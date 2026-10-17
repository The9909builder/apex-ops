#!/usr/bin/env python3
"""
System Card checker for APEX (W1/item 45).

One schema, two styles. vague-to-system emits a System Card; APEX Stage 0
DECODE consumes it. Both styles parse into the same canonical object:

    apex style: 'KEY : value' lines (INTENT/MODE/RISK/DRYRUN/ROOT TYPE plus context fields)
    v2s style:  '## SYSTEM CARD' header, then 'KEY: value' lines (ACTOR/GOAL/... plus MODE/RISK/DRYRUN/ROOT TYPE)

Schema: context/knowledge/system-card.schema.json v1.0
Required: intent, mode, risk, root_type. Enums are closed sets. Unknown fields are
rejected fail-closed (a typo'd key must not degrade to a missing field).

Usage:
    python3 check-system-card.py --check <file>       # validate one card
    python3 check-system-card.py --roundtrip <file>   # validate + cross-style roundtrip
    python3 check-system-card.py --fixtures <dir>     # all *.txt; '# EXPECT: accept|reject'
Exit: 0 all as expected · 1 mismatch/reject · 2 unparseable/missing (fail-closed).
"""

import json
import re
import sys
from pathlib import Path

SCHEMA_VERSION = "1.0"
MODES = {"EXPLORATION", "HYBRID", "EXECUTION"}
ROOT_TYPES = {"LEARN", "DECIDE", "GENERATE", "RESEARCH", "BUILD", "SHIP", "LEVERAGE"}
EXTRACTION = {"clean", "interrogated", "rabbit-hole"}
DRYRUN = {"yes", "no"}
REQUIRED = ("intent", "mode", "risk", "root_type")
CANON = ("intent", "mode", "risk", "dryrun", "root_type",
         "actor", "domain", "output", "constraints", "success", "extraction_method")

KEY_RE = re.compile(r"^\s*([A-Za-z][A-Za-z _-]*?)\s*:\s*(.*?)\s*$")
ALIASES = {
    "INTENT": "intent", "GOAL": "intent",
    "MODE": "mode",
    "RISK": "risk",
    "DRYRUN": "dryrun",
    "ROOT TYPE": "root_type", "NODE TYPE": "root_type",
    "ACTOR": "actor",
    "DOMAIN": "domain",
    "OUTPUT": "output",
    "CONSTRAINTS": "constraints",
    "SUCCESS": "success",
    "EXTRACTION METHOD": "extraction_method",
}


def parse_card(text: str) -> tuple[dict, list[str]]:
    """Parse either style into the canonical object. Errors never abort the parse."""
    canon = {k: "" for k in CANON}
    errors = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = KEY_RE.match(line)
        if not m:
            errors.append(f"unparseable line: {line.strip()!r}")
            continue
        key = " ".join(m.group(1).upper().replace("_", " ").split())
        target = ALIASES.get(key)
        if target is None:
            errors.append(f"unknown field {m.group(1)!r} (fail-closed)")
            continue
        if canon[target]:
            errors.append(f"duplicate field {target}")
            continue
        canon[target] = m.group(2).strip()
    return canon, errors


def judge(canon: dict, errors: list[str]) -> tuple[bool, list[str]]:
    """Return (accepted, reasons). accepted=True means the card is schema-clean."""
    reasons = list(errors)
    for field in REQUIRED:
        if not canon[field]:
            reasons.append(f"missing required field {field.upper()}")
    mode = canon["mode"].upper()
    if mode and mode not in MODES:
        reasons.append(f"MODE must be exactly one of {sorted(MODES)}, got {canon['mode']!r}")
    risk = canon["risk"]
    if risk and not re.fullmatch(r"\d+", risk):
        reasons.append(f"RISK must be an integer 0-10, got {risk!r}")
    elif risk and not 0 <= int(risk) <= 10:
        reasons.append(f"RISK out of the 0-10 range: {risk!r}")
    rt = canon["root_type"].upper()
    if rt and rt not in ROOT_TYPES:
        reasons.append(f"ROOT TYPE must be exactly one of {sorted(ROOT_TYPES)}, got {canon['root_type']!r}")
    em = canon["extraction_method"].lower()
    if em and em not in EXTRACTION:
        reasons.append(f"EXTRACTION_METHOD must be one of {sorted(EXTRACTION)}, got {canon['extraction_method']!r}")
    dr = canon["dryrun"].lower()
    if dr and dr not in DRYRUN:
        reasons.append(f"DRYRUN must be yes|no, got {canon['dryrun']!r}")
    return not reasons, reasons


def style_of(text: str) -> str:
    return "v2s" if "## SYSTEM CARD" in text.upper() else "apex"


def emit_apex(canon: dict) -> str:
    lines = [
        f"INTENT     : {canon['intent']}",
        f"MODE       : {canon['mode']}",
        f"RISK       : {canon['risk']}",
    ]
    if canon["dryrun"]:
        lines.append(f"DRYRUN     : {canon['dryrun']}")
    lines.append(f"ROOT TYPE  : {canon['root_type']}")
    for key, label in (("actor", "ACTOR"), ("domain", "DOMAIN"), ("output", "OUTPUT"),
                       ("constraints", "CONSTRAINTS"), ("success", "SUCCESS"),
                       ("extraction_method", "EXTRACTION METHOD")):
        if canon[key]:
            lines.append(f"{label:<11}: {canon[key]}")
    return "\n".join(lines) + "\n"


def emit_v2s(canon: dict) -> str:
    lines = ["## SYSTEM CARD", ""]
    for key, label in (("actor", "ACTOR"), ("intent", "GOAL"), ("domain", "DOMAIN"),
                       ("output", "OUTPUT"), ("constraints", "CONSTRAINTS"),
                       ("success", "SUCCESS"), ("extraction_method", "EXTRACTION_METHOD")):
        if canon[key]:
            lines.append(f"{label}: {canon[key]}")
    for key, label in (("mode", "MODE"), ("risk", "RISK"), ("dryrun", "DRYRUN"), ("root_type", "ROOT TYPE")):
        if canon[key]:
            lines.append(f"{label}: {canon[key]}")
    return "\n".join(lines) + "\n"


def roundtrip(text: str) -> tuple[bool, list[str], dict]:
    """Parse, re-emit in the other style, re-parse; canon must be identical."""
    canon1, errs1 = parse_card(text)
    other = emit_v2s(canon1) if style_of(text) == "apex" else emit_apex(canon1)
    canon2, errs2 = parse_card(other)
    problems = errs1 + errs2
    for key in CANON:
        if canon1[key] != canon2[key]:
            problems.append(f"roundtrip mismatch on {key}: {canon1[key]!r} != {canon2[key]!r}")
    return not problems, problems, canon1


def expect_of(text: str) -> str:
    for line in text.splitlines():
        m = re.match(r"^#?\s*EXPECT:\s*(accept|reject)\b", line, re.I)
        if m:
            return m.group(1).lower()
    return "reject"  # adversarial by default


def check_one(path: Path) -> tuple[int, bool, bool]:
    """Returns (failed, is_accept_fixture, roundtrip_passed). Accept fixtures must roundtrip."""
    text = path.read_text(errors="replace")
    canon, perr = parse_card(text)
    accepted, reasons = judge(canon, perr)
    expected = expect_of(text)
    ok = (accepted and expected == "accept") or (not accepted and expected == "reject")
    rt_pass = False
    if expected == "accept":
        rt_pass, rt_reasons, _ = roundtrip(text)
        if not rt_pass:
            ok = False
            reasons = rt_reasons
    mark = "OK  " if ok else "MISMATCH"
    rt_note = f" · roundtrip {'OK' if rt_pass else 'FAIL'}" if expected == "accept" else ""
    print(f"  [{mark}] {path.name}: expected {expected}, got "
          f"{'accept' if accepted else 'reject'}{rt_note}")
    for r in reasons:
        print(f"           - {r}")
    return (0 if ok else 1), expected == "accept", rt_pass


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] not in ("--check", "--roundtrip", "--fixtures"):
        print(__doc__)
        return 1
    target = Path(sys.argv[2])

    if sys.argv[1] in ("--check", "--roundtrip"):
        if not target.is_file():
            print(f"not a file: {target}")
            return 2
        text = target.read_text(errors="replace")
        canon, perr = parse_card(text)
        accepted, reasons = judge(canon, perr)
        rt_pass = True
        if accepted and sys.argv[1] == "--roundtrip":
            rt_pass, rt_reasons, canon = roundtrip(text)
            reasons = rt_reasons
        verdict = accepted and rt_pass
        print(f"{'ACCEPT' if verdict else 'REJECT'}: {target} (schema v{SCHEMA_VERSION})")
        if verdict:
            print(json.dumps(canon, indent=2))
        for r in reasons:
            print(f"  - {r}")
        return 0 if verdict else 1

    if not target.is_dir():
        print(f"not a dir: {target}")
        return 2
    files = sorted(target.glob("*.txt"))
    if not files:
        print(f"no fixtures in {target}")
        return 2
    fails = accepts = rt_ok = 0
    for f in files:
        failed, is_accept, rt_pass = check_one(f)
        fails += failed
        accepts += is_accept
        rt_ok += rt_pass
    print(f"SYSTEM CARD: {len(files) - fails}/{len(files)} fixtures behaved as expected")
    print(f"ROUNDTRIP: {rt_ok}/{accepts} accept fixtures survived a style roundtrip")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
