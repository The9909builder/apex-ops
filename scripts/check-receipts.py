#!/usr/bin/env python3
"""
APEX Live Routing Receipt Checker.

Verifies every NODE routing line in an APEX run output carries machine-checkable
evidence, so a route is a receipt and not prose (INV-7).

Parsed line forms (W1/B1.1 — fail-closed):
    NODE <id> [<TYPE>] -> <donor>: gate = ...                curated donor
    NODE <id> [<TYPE>] -> <donor> (catalog): gate = ...      catalog-resolved donor
    NODE <id> [<TYPE>] -> <d1> then <d2>: gate ...           chain (every donor checked)
    NODE <id> [<TYPE>] -> <d1> (curated) -> <d2> (catalog): arrow chain
    NODE <id> [<TYPE>] -> direct: <reason>                   declared direct skip
    NODE <id> [<TYPE>] -> direct execution (<note>): ...     declared direct skip
    ... (predicted) anywhere on the line = dry-run (reachability only)

Per donor: node type is in the closed set; the donor is reachable (curated:
context/donors/<d>/SKILL.md; catalog: donor-catalog.json entry whose path
contains SKILL.md); the donor's route_evidence from gates.json appears in the
line (fallback: the ROUTE block) — skipped for (predicted) lines.

Fail-closed guarantees:
  * a NODE-prefixed line that does not parse is a failure (never silently skipped);
  * a ROUTE block with no parseable lines BLOCKS (exit 2) — never "0/0 PASS";
  * PASS requires at least one verified route.

Usage:
    python3 check-receipts.py --check <run_output.txt>
    python3 check-receipts.py --demo

Exit codes: 0 = all receipts verified, 1 = failures found, 2 = blocked/usage.
"""

import json
import re
import sys
from pathlib import Path

from gate_registry import load_gates

SKILL_DIR = Path(__file__).parent.parent
DONOR_DIR = SKILL_DIR / "context" / "donors"
CATALOG_FILE = SKILL_DIR / "context" / "knowledge" / "donor-catalog.json"

NODE_TYPES = {"LEARN", "DECIDE", "GENERATE", "RESEARCH", "BUILD", "SHIP", "LEVERAGE"}
KNOWN_DECORATORS = {"catalog", "curated", "predicted", "dry-run"}
DIRECT_TOKENS = {"direct", "direct execution"}

NODE_PREFIX_RE = re.compile(r"^\s*NODE\b")
ROUTE_LINE_RE = re.compile(r"^\s*NODE\s+(\S+)\s+\[([A-Z]+)\]\s*->\s*(.*)$")
CHAIN_SPLIT_RE = re.compile(r"\s+then\s+|\s*->\s*")
TOKEN_RE = re.compile(r"^\s*([\w-]+(?:\s+execution)?)\s*(?:\(([^()]*)\))?\s*$")
PREDICTED_RE = re.compile(r"\(predicted\)|\(dry-run\)", re.IGNORECASE)


def load_catalog_index() -> dict:
    """{name: [entry, ...]} from donor-catalog.json, or {} if missing."""
    if not CATALOG_FILE.exists():
        return {}
    try:
        data = json.loads(CATALOG_FILE.read_text())
    except json.JSONDecodeError:
        return {}
    index: dict[str, list] = {}
    for entry in data.get("skills", []):
        index.setdefault(str(entry.get("name", "")).lower(), []).append(entry)
    return index


def split_launcher(remainder: str) -> tuple[str, str] | tuple[None, None]:
    """Split 'donor-part: rest' at the first colon outside parentheses."""
    depth = 0
    for i, ch in enumerate(remainder):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif ch == ":" and depth == 0:
            return remainder[:i], remainder[i + 1:]
    return None, None


def parse_launcher(launcher: str) -> list[tuple[str, str]] | None:
    """Tokenize 'd1 (dec) -> d2 then d3' into [(name, decorator), ...] or None."""
    parts = [p for p in CHAIN_SPLIT_RE.split(launcher) if p.strip()]
    if not parts:
        return None
    tokens = []
    for part in parts:
        m = TOKEN_RE.fullmatch(part)
        if not m:
            return None
        tokens.append((m.group(1).strip(), (m.group(2) or "").strip().lower()))
    return tokens


def parse_route_lines(text: str) -> tuple[list[dict], list[str]]:
    """Return (parsed routes, unparseable NODE-prefixed lines)."""
    routes, unparsed = [], []
    for ln in text.splitlines():
        if not NODE_PREFIX_RE.match(ln):
            continue
        m = ROUTE_LINE_RE.match(ln)
        if not m:
            unparsed.append(ln.strip())
            continue
        launcher, rest = split_launcher(m.group(3))
        tokens = parse_launcher(launcher) if launcher is not None else None
        if tokens is None:
            unparsed.append(ln.strip())
            continue
        token_names = [t[0].lower() for t in tokens]
        routes.append({
            "node_id": m.group(1),
            "node_type": m.group(2),
            "tokens": tokens,
            "direct": len(tokens) == 1 and token_names[0] in DIRECT_TOKENS,
            "rest": rest,
            "line": ln.strip(),
        })
    return routes, unparsed


def resolve_catalog_donor(name: str, catalog_index: dict) -> Path | None:
    """First catalog entry for `name` whose path holds a SKILL.md."""
    for entry in catalog_index.get(name.lower(), []):
        p = Path(str(entry.get("path", "")))
        if p.is_dir() and (p / "SKILL.md").is_file():
            return p
    return None


def check_line(route: dict, route_block_lower: str, catalog_index: dict, gates: dict) -> list[str]:
    """Return failure strings for one NODE line (empty = fully verified)."""
    failures = []
    node_type = route["node_type"]
    if node_type not in NODE_TYPES:
        failures.append(f"unknown node type [{node_type}] (closed set: "
                        f"{', '.join(sorted(NODE_TYPES))})")

    if route["direct"]:
        return failures  # declared direct skip — accounted as skip, not a failure

    if any(t[0].lower().startswith("direct") for t in route["tokens"]):
        failures.append("'direct' cannot be part of a donor chain — declare a direct "
                        "skip on its own line (-> direct: <reason>)")
        return failures

    predicted = bool(PREDICTED_RE.search(route["rest"]))
    line_lower = route["line"].lower()

    for name, dec_raw in route["tokens"]:
        if dec_raw and dec_raw in ("predicted", "dry-run"):
            decorator, predicted = None, True
        elif dec_raw and dec_raw in ("catalog", "curated"):
            decorator = dec_raw
        elif dec_raw:
            failures.append(f"unknown decorator '({dec_raw})' on '{name}' — known: "
                            f"{', '.join(sorted(KNOWN_DECORATORS))}")
            continue
        else:
            decorator = None

        if decorator == "catalog":
            root = resolve_catalog_donor(name, catalog_index)
            if root is None:
                failures.append(f"catalog donor unreachable: no donor-catalog.json entry "
                                f"for '{name}' with a SKILL.md on disk "
                                f"(run scripts/donor-catalog.py refresh)")
                continue
        else:
            skill = DONOR_DIR / name / "SKILL.md"
            if name.lower() in DIRECT_TOKENS or not skill.exists():
                failures.append(f"donor unreachable: context/donors/{name}/SKILL.md "
                                f"missing (if it is a catalog donor, decorate the line "
                                f"with (catalog))")
                continue

        if predicted:
            continue

        entry = gates.get(name)
        if entry is None:
            failures.append(f"no gate registered for donor '{name}' "
                            f"(add it to context/knowledge/gates.json)")
            continue
        evidence = entry["route_evidence"]
        if not any(k in line_lower or k in route_block_lower for k in evidence):
            failures.append(f"gate evidence for '{name}' not found in line or ROUTE "
                            f"block (any of: {', '.join(evidence)})")
    return failures


def check_text(text: str) -> dict:
    """Check all route lines. Returns dict with verified/total/skips/failures/has_block."""
    routes, unparsed = parse_route_lines(text)

    route_block = ""
    in_block = False
    for ln in text.splitlines():
        if re.match(r"^ROUTE\b", ln.strip()):
            in_block = True
            continue
        if in_block and re.match(r"^(FUSE|CLOSE|PLAN)\b", ln.strip()):
            break
        if in_block:
            route_block += ln + "\n"
    route_block_lower = route_block.lower()

    catalog_index = load_catalog_index()
    gates = load_gates()

    failures = [f"unparseable NODE line (fail-closed): {u[:140]}" for u in unparsed]
    verified = 0
    skips = 0
    for r in routes:
        f = check_line(r, route_block_lower, catalog_index, gates)
        if f:
            failures.extend(f"NODE {r['node_id']}: {msg}" for msg in f)
        elif r["direct"]:
            skips += 1
        else:
            verified += 1

    return {
        "verified": verified,
        "total": len(routes) + len(unparsed),
        "skips": skips,
        "failures": failures,
        "has_block": bool(route_block.strip()),
    }


def emit(result: dict, label: str = "RECEIPT CHECK") -> int:
    line = (f"{label}: {result['verified']}/{result['total']} route lines verified")
    if result["skips"]:
        line += f" ({result['skips']} declared direct skips)"
    print(line)
    for f in result["failures"]:
        print(f"  ❌ {f}")
    if not result["has_block"]:
        print("BLOCKED: no ROUTE block found — cannot verify receipts (fail-closed)")
        return 2
    if result["failures"]:
        print("STATUS: FAIL")
        return 1
    if result["verified"] == 0:
        print("BLOCKED: ROUTE block present but 0 verified routes — fail-closed "
              "(declare at least one verifiable donor route, or fix the line format)")
        return 2
    print("STATUS: PASS")
    return 0


DEMO = (
    "ROUTE\n"
    "NODE A [LEARN] -> deep-understanding: gate gap named = MECHANISM\n"
    "NODE B [DECIDE] -> super-reasoner: falsifiability conditions present\n"
    "NODE C [BUILD] -> think-pipeline then autovibe: W1 slot exists, compiled\n"
    "NODE D [GENERATE] -> reel-forge (catalog): gate = film-ready script with delivery notes\n"
    "NODE E [BUILD] -> direct: single-file change, no donor fit\n"
    "NODE F [BUILD] -> think-pipeline (curated) -> autovibe (curated): chain, W1 slot exists and compiled\n"
)


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ("--check", "--demo"):
        print(__doc__)
        sys.exit(2)

    if sys.argv[1] == "--demo" or (len(sys.argv) > 2 and sys.argv[2] == "--demo"):
        sys.exit(emit(check_text(DEMO), label="DEMO"))

    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)

    path = Path(sys.argv[2])
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(2)

    sys.exit(emit(check_text(path.read_text())))


if __name__ == "__main__":
    main()
