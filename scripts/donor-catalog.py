#!/usr/bin/env python3
"""
Donor catalog for APEX.

The routing table's symlinked donors are the curated core (11 skills). The catalog
widens reach to every skill installed on this machine: TFC skills, Claude skills,
spawner skills, agents skills. Refresh scans the roots and writes
context/knowledge/donor-catalog.json plus a small .md summary. Query ranks catalog
entries against free terms so ROUTE can reach past the curated set without
absorbing any donor.

Roots (scanned in order, deduped by realpath):
  1. --root PATH (repeatable)
  2. APEX_CATALOG_ROOTS env var (colon-separated)
  3. defaults: the skills root apex itself is installed in, plus
     ~/.claude/skills, ~/.spawner/skills, ~/.agents/skills

Exit 0 on success, 1 on failure.

Usage:
    python3 donor-catalog.py refresh [--quiet]
    python3 donor-catalog.py query --terms "video reel prompt" [--top 5] [--json]
    python3 donor-catalog.py stats
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

APEX_DIR = Path(__file__).resolve().parent.parent
CATALOG_JSON = APEX_DIR / "context" / "knowledge" / "donor-catalog.json"
CATALOG_MD = APEX_DIR / "context" / "knowledge" / "donor-catalog.md"
DONORS_DIR = APEX_DIR / "context" / "donors"

MAX_DEPTH = 3
MAX_DIRS = 25000

TOKEN_RE = re.compile(r"[a-z0-9]+")
SKILL_MD = "SKILL.md"


def default_roots():
    roots = [APEX_DIR.parent.parent]
    home = Path.home()
    for rel in (".claude/skills", ".spawner/skills", ".agents/skills"):
        roots.append(home / rel)
    return roots


def resolve_roots(cli_roots):
    roots = []
    env = os.environ.get("APEX_CATALOG_ROOTS", "")
    for raw in list(cli_roots) + [p for p in env.split(":") if p] + [str(r) for r in default_roots()]:
        p = Path(raw).expanduser()
        if p.is_dir():
            rp = p.resolve()
            if rp not in roots:
                roots.append(rp)
    return roots


def siblings(path, depth, budget):
    """Bounded walk that follows dir symlinks but never exceeds MAX_DEPTH/MAX_DIRS."""
    stack = [(path, 0)]
    while stack and budget[0] > 0:
        d, dd = stack.pop()
        budget[0] -= 1
        if dd >= depth:
            continue
        try:
            entries = sorted(os.scandir(d), key=lambda e: e.name)
        except OSError:
            continue
        for e in entries:
            try:
                if e.is_dir(follow_symlinks=True) and not e.name.startswith("."):
                    stack.append((Path(e.path), dd + 1))
            except OSError:
                continue


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = text[3:end]
    out = {"name": "", "description": ""}
    lines = fm.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^name:\s*(.+?)\s*$", line)
        if m:
            out["name"] = m.group(1).strip().strip('"').strip("'")
        m = re.match(r"^description:\s*(.*)$", line)
        if m:
            rest = m.group(1).strip()
            if rest in (">", "|", ">-", "|-", ""):
                parts = []
                j = i + 1
                while j < len(lines) and (lines[j].startswith(" ") or lines[j].strip() == ""):
                    parts.append(lines[j].strip())
                    j += 1
                out["description"] = " ".join(p for p in parts if p)
                i = j
                continue
            out["description"] = rest.strip('"').strip("'")
        i += 1
    return out


def parse_spec(spec_path):
    info = {"version": "", "lane": "", "triggers": []}
    try:
        text = spec_path.read_text()
    except OSError:
        return info
    for key in ("version", "lane"):
        m = re.search(rf"^{key}:\s*[\"']?([A-Za-z0-9_.-]+)", text, re.M)
        if m:
            info[key] = m.group(1)
    m = re.search(r"^triggers:\s*$", text, re.M)
    if m:
        tail = text[m.end():]
        for tm in re.finditer(r"^\s+-\s*[\"']?(.+?)[\"']?\s*$", tail, re.M):
            trig = tm.group(1).strip()
            if re.match(r"^[a-z_]+:", trig):
                break
            info["triggers"].append(trig)
            if len(info["triggers"]) >= 20:
                break
    return info


def curated_donors():
    """Map donor name -> resolved target path for the curated symlinked donors."""
    out = {}
    if not DONORS_DIR.is_dir():
        return out
    for link in DONORS_DIR.iterdir():
        if link.is_symlink():
            target = link.resolve()
            out[link.name] = target
    return out


def is_junk_dir(name: str) -> bool:
    """Backups and templates are not skills (W1/item 46 metric: 0 bak/_template)."""
    return name.startswith("_") or ".bak" in name


def dedupe_by_name(skills):
    """One entry per skill name. Prefer the richest copy: curated-donor flag,
    then version/lane metadata (TFC spec'd), then first-scan order (the apex
    tree root is scanned first, so the real tree beats thin mirrors)."""
    best = {}
    for s in skills:
        n = s["name"]
        if n not in best:
            best[n] = s
            continue
        score_new = (bool(s["donor"]), bool(s["version"]), bool(s["lane"]))
        score_cur = (bool(best[n]["donor"]), bool(best[n]["version"]), bool(best[n]["lane"]))
        if score_new > score_cur:
            best[n] = s
    return list(best.values())


def scan(roots):
    skills = {}
    budget = [MAX_DIRS]
    curated = curated_donors()
    for root in roots:
        candidates = [root]
        candidates.extend([Path(e.path) for e in os.scandir(root) if e.is_dir(follow_symlinks=True) and not e.name.startswith(".") and not is_junk_dir(e.name)] if root.is_dir() else [])
        seen_dirs = set()
        stack = [(c, 1) for c in candidates]
        while stack and budget[0] > 0:
            d, depth = stack.pop()
            rp = str(d.resolve()) if d.exists() else None
            if rp is None or rp in seen_dirs:
                continue
            seen_dirs.add(rp)
            budget[0] -= 1
            md = d / SKILL_MD
            if md.is_file():
                real = str(d.resolve())
                if real not in skills:
                    try:
                        text = md.read_text(errors="replace")[:6000]
                    except OSError:
                        text = ""
                    fm = parse_frontmatter(text)
                    spec = parse_spec(d / "spec.yaml")
                    donor_name = None
                    for name, target in curated.items():
                        if real == str(target):
                            donor_name = name
                            break
                    skills[real] = {
                        "id": str(d.relative_to(root)) if str(d).startswith(str(root)) else str(d),
                        "root": str(root),
                        "path": real,
                        "name": fm.get("name") or d.name,
                        "description": (fm.get("description") or "")[:300],
                        "version": spec["version"],
                        "lane": spec["lane"],
                        "triggers": spec["triggers"][:12],
                        "donor": donor_name or "",
                    }
            if depth < MAX_DEPTH:
                try:
                    for e in sorted(os.scandir(d), key=lambda e: e.name):
                        if e.is_dir(follow_symlinks=True) and not e.name.startswith(".") \
                                and not is_junk_dir(e.name):
                            stack.append((Path(e.path), depth + 1))
                except OSError:
                    continue
    return dedupe_by_name(list(skills.values()))


def tilde(path):
    home = str(Path.home())
    return "~" + path[len(home):] if path.startswith(home) else path


def cmd_refresh(args):
    roots = resolve_roots(args.root)
    skills = scan(roots)
    skills.sort(key=lambda s: (s["root"], s["id"]))
    payload = {
        "generated_ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "scripts/donor-catalog.py",
        "roots": [str(r) for r in roots],
        "count": len(skills),
        "curated_donors": sorted(curated_donors().keys()),
        "skills": skills,
    }
    CATALOG_JSON.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_JSON.write_text(json.dumps(payload, indent=1) + "\n")
    by_root = {}
    for s in skills:
        by_root.setdefault(s["root"], []).append(s)
    lines = [
        "# Donor catalog (generated; do not hand-edit)",
        "",
        f"Generated: {payload['generated_ts']} by `scripts/donor-catalog.py refresh`.",
        f"Scanned skills: {len(skills)} across {len(by_root)} root(s).",
        "",
        f"Curated symlinked donors: {', '.join(payload['curated_donors'])}.",
        "",
        "## Roots",
        "",
    ]
    for root, group in sorted(by_root.items()):
        lines.append(f"- `{tilde(root)}` — {len(group)} skill(s)")
    lines += ["", "## Pattern-category skills (route candidates)", ""]
    for s in skills:
        if "/pattern/" in s["path"]:
            lane = f" lane={s['lane']}" if s["lane"] else ""
            ver = f" v{s['version']}" if s["version"] else ""
            donor = " [curated donor]" if s["donor"] else ""
            desc = s["description"][:90]
            lines.append(f"- `{s['id']}`{ver}{lane}{donor}: {desc}")
    lines += [
        "",
        "Query at route time: `python3 scripts/donor-catalog.py query --terms \"...\" --top 5`.",
        "",
    ]
    CATALOG_MD.write_text("\n".join(lines))
    if not args.quiet:
        print(f"catalog: {len(skills)} skills from {len(roots)} root(s) -> {CATALOG_JSON}")
    return 0


def score_entry(entry, terms):
    tokens = set()
    for t in terms:
        tokens.update(TOKEN_RE.findall(t.lower()))
    if not tokens:
        return 0, []
    name = entry["name"].lower()
    desc = entry["description"].lower()
    trigs = " | ".join(entry["triggers"]).lower()
    hay = f"{name} {' '.join(TOKEN_RE.findall(name))} | {trigs} | {desc}"
    why, score = [], 0
    joined = " ".join(terms).lower()
    if joined and joined in hay:
        score += 4
        why.append(f"phrase '{joined}'")
    for tok in sorted(tokens):
        if tok in TOKEN_RE.findall(name):
            score += 3
            why.append(f"name:{tok}")
        elif tok in trigs:
            score += 2
            why.append(f"trigger:{tok}")
        elif tok in desc:
            score += 1
            why.append(f"desc:{tok}")
    return score, why


def cmd_query(args):
    if not CATALOG_JSON.is_file():
        print("no catalog; run: python3 donor-catalog.py refresh", file=sys.stderr)
        return 1
    payload = json.loads(CATALOG_JSON.read_text())
    terms = args.terms or []
    ranked = []
    for entry in payload["skills"]:
        s, why = score_entry(entry, terms)
        if s > 0:
            ranked.append((s, entry, why))
    ranked.sort(key=lambda r: (-r[0], r[1]["donor"] == "", r[1]["path"]))
    top = ranked[: args.top]
    if args.json:
        print(json.dumps([{"score": s, "entry": e, "why": w} for s, e, w in top], indent=1))
        return 0
    if not top:
        print("no catalog match; route from the curated donor table")
        return 0
    for s, e, w in top:
        lane = f" lane={e['lane']}" if e["lane"] else ""
        donor = " [curated]" if e["donor"] else ""
        print(f"{s:>3}  {e['path']}{donor}{lane}")
        print(f"     {e['name']}: {e['description'][:110]}")
        print(f"     why: {', '.join(w[:6])}")
    return 0


def cmd_stats(args):
    if not CATALOG_JSON.is_file():
        print("no catalog; run: python3 donor-catalog.py refresh", file=sys.stderr)
        return 1
    payload = json.loads(CATALOG_JSON.read_text())
    print(f"generated: {payload['generated_ts']}")
    print(f"skills: {payload['count']}  roots: {len(payload['roots'])}")
    print(f"curated donors present in catalog: "
          f"{sum(1 for s in payload['skills'] if s['donor'])}/{len(payload['curated_donors'])}")
    by_root = {}
    for s in payload["skills"]:
        by_root[s["root"]] = by_root.get(s["root"], 0) + 1
    for root, n in sorted(by_root.items()):
        print(f"  {root}: {n}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="APEX donor catalog")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_ref = sub.add_parser("refresh", help="rescan roots and rewrite the catalog")
    p_ref.add_argument("--root", action="append", default=[], help="extra root (repeatable)")
    p_ref.add_argument("--quiet", action="store_true")
    p_ref.set_defaults(fn=cmd_refresh)

    p_q = sub.add_parser("query", help="rank catalog skills against terms")
    p_q.add_argument("--terms", nargs="+", required=True)
    p_q.add_argument("--top", type=int, default=5)
    p_q.add_argument("--json", action="store_true")
    p_q.set_defaults(fn=cmd_query)

    p_s = sub.add_parser("stats", help="catalog summary")
    p_s.set_defaults(fn=cmd_stats)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
