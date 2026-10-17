#!/usr/bin/env python3
"""
APEX Per-Leaf Donor Health Gate.

Route-time health check for a donor, cheap enough to call per leaf:
  1. Reachability: context/donors/<donor>/SKILL.md resolves and is non-empty.
  2. Frontmatter: parseable YAML with name + description (the slash-menu
     discovery contract — a missing frontmatter made apex invisible once).
  3. Gate keywords: donor's markers from context/knowledge/gates.json
     (single manifest, loaded via scripts/gate_registry.py) present in SKILL.md.
  4. Drift detection: sha256 of SKILL.md vs context/knowledge/donor-hashes.json.

Typed verdicts (W1/B1.3):
  OK    — healthy; no action.
  DRIFT — SKILL.md changed since baseline: still usable, but re-read the donor
          before invoke; a json receipt is written to receipts/drift-*.json.
  FAIL  — unreachable / broken frontmatter / gate keywords absent: do not invoke.

Exit codes: FAIL anywhere -> 1; DRIFT or OK only -> 0; usage error -> 2.

Usage:
    python3 donor-health.py check <donor> [<donor> ...]
    python3 donor-health.py check-all
    python3 donor-health.py baseline            # record current hashes
    python3 donor-health.py --json check <donor>  # machine-readable
"""

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from gate_registry import load_gates

SKILL_DIR = Path(__file__).parent.parent
DONOR_DIR = SKILL_DIR / "context" / "donors"
HASHES_FILE = SKILL_DIR / "context" / "knowledge" / "donor-hashes.json"
RECEIPTS_DIR = SKILL_DIR / "receipts"

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_donor(donor: str, gates: dict) -> dict:
    """Full health check for one donor. Returns report dict with verdict."""
    report = {"donor": donor, "healthy": True, "verdict": "OK", "problems": [],
              "hash": None, "drift": None}
    hard_fail = False

    skill = DONOR_DIR / donor / "SKILL.md"

    # 1. Reachability
    if not skill.exists():
        report["healthy"] = False
        report["verdict"] = "FAIL"
        report["problems"].append("unreachable: context/donors/"
                                  f"{donor}/SKILL.md missing (broken symlink?)")
        return report

    text = skill.read_text(errors="replace")

    # 2. Frontmatter contract
    m = FRONTMATTER_RE.match(text)
    if not m:
        hard_fail = True
        report["problems"].append("frontmatter: no parseable --- YAML block at top")
    else:
        fm = m.group(1)
        if not re.search(r"^name:", fm, re.MULTILINE):
            hard_fail = True
            report["problems"].append("frontmatter: missing 'name:'")
        if not re.search(r"^description:", fm, re.MULTILINE):
            hard_fail = True
            report["problems"].append("frontmatter: missing 'description:'")

    # 3. Gate keywords (single manifest: context/knowledge/gates.json)
    entry = gates.get(donor)
    if entry is None:
        report["problems"].append(f"NOTE: no gate keywords registered for '{donor}' "
                                  f"(not in gates.json — direct-execution donor?)")
    elif not any(k in text.lower() for k in entry["keywords"]):
        hard_fail = True
        report["problems"].append(f"gate keywords absent from SKILL.md "
                                  f"(any of: {', '.join(entry['keywords'])})")

    # 4. Drift vs baseline
    digest = sha256_of(skill)
    report["hash"] = digest[:12]
    if HASHES_FILE.exists():
        try:
            known = json.loads(HASHES_FILE.read_text())
        except json.JSONDecodeError:
            known = {}
        if donor in known and known[donor] != digest:
            report["drift"] = {"old": known[donor][:12], "new": digest[:12]}
            report["problems"].append(
                f"DRIFT: SKILL.md changed since baseline "
                f"({known[donor][:12]} -> {digest[:12]}) — re-read donor before invoke")

    if hard_fail:
        report["healthy"] = False
        report["verdict"] = "FAIL"
    elif report["drift"]:
        report["healthy"] = False
        report["verdict"] = "DRIFT"
    return report


def check_all(gates: dict) -> list[dict]:
    donors = sorted(p.name for p in DONOR_DIR.iterdir() if p.is_dir())
    return [check_donor(d, gates) for d in donors]


def baseline() -> None:
    """Record current hashes as the drift baseline."""
    hashes = {}
    for skill in DONOR_DIR.glob("*/SKILL.md"):
        hashes[skill.parent.name] = sha256_of(skill)
    HASHES_FILE.parent.mkdir(parents=True, exist_ok=True)
    HASHES_FILE.write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n")
    print(f"BASELINE RECORDED: {len(hashes)} donors -> {HASHES_FILE.relative_to(SKILL_DIR)}")


def write_drift_receipts(reports: list[dict]) -> list[str]:
    """Write one receipt per drifted donor (dedupe by donor + new hash)."""
    written = []
    drifted = [r for r in reports if r["verdict"] == "DRIFT"]
    if not drifted:
        return written
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    for r in drifted:
        new_hash = r["drift"]["new"]
        dup = False
        for p in RECEIPTS_DIR.glob(f"drift-*-{r['donor']}.json"):
            try:
                if json.loads(p.read_text()).get("new_hash", "")[:12] == new_hash:
                    dup = True
                    break
            except (json.JSONDecodeError, OSError):
                continue
        if dup:
            continue
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
        receipt = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "kind": "drift",
            "donor": r["donor"],
            "old_hash": r["drift"]["old"],
            "new_hash": new_hash,
            "action": "re-read donor SKILL.md before invoke (drifted since baseline)",
            "source": "scripts/donor-health.py",
        }
        path = RECEIPTS_DIR / f"drift-{stamp}-{r['donor']}.json"
        path.write_text(json.dumps(receipt, indent=2) + "\n")
        written.append(path.name)
    return written


def print_report(reports: list[dict], as_json: bool = False) -> int:
    failed = [r for r in reports if r["verdict"] == "FAIL"]
    drifted = [r for r in reports if r["verdict"] == "DRIFT"]
    ok = len(reports) - len(failed) - len(drifted)

    receipts = write_drift_receipts(reports)
    if as_json:
        print(json.dumps(reports, indent=2))
    else:
        for r in reports:
            mark = {"OK": "✅", "DRIFT": "⚠️ ", "FAIL": "❌"}[r["verdict"]]
            print(f"  {mark} {r['donor']} (hash {r.get('hash') or '-'}) [{r['verdict']}]")
            for p in r["problems"]:
                print(f"     - {p}")
        for name in receipts:
            print(f"     → drift receipt written: receipts/{name}")
        if failed:
            print(f"STATUS: FAIL ({ok}/{len(reports)} ok; {len(failed)} failed, "
                  f"{len(drifted)} drifted)")
            return 1
        if drifted:
            print(f"STATUS: DRIFT ({ok}/{len(reports)} ok; {len(drifted)} drifted — "
                  f"re-read donor(s) before invoke)")
            return 0
        print(f"STATUS: PASS ({ok}/{len(reports)} healthy)")
    if failed:
        return 1
    return 0


def main() -> None:
    args = sys.argv[1:]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]

    if not args:
        print(__doc__)
        sys.exit(2)

    cmd = args[0]

    if cmd == "baseline":
        baseline()
        sys.exit(0)

    gates = load_gates()

    if cmd == "check-all":
        sys.exit(print_report(check_all(gates), as_json))

    if cmd == "check" and len(args) >= 2:
        reports = [check_donor(d, gates) for d in args[1:]]
        sys.exit(print_report(reports, as_json))

    print(__doc__)
    sys.exit(2)


if __name__ == "__main__":
    main()
