#!/usr/bin/env python3
"""
GROUND evidence checker for APEX (W1/item 6).

Rule: a GROUNDED block with Verdict YES requires
  (1) a NAMED actor — never 'we'/'the team'/empty, and
  (2) an OBSERVED artifact in EVIDENCE — a path, URL, measurement, ticket id,
      or quoted words.

'flag set'-class evidence (assertions that a check happened, with no artifact)
is rejected: an assertion of a check is not the check.

Usage:
    python3 check-ground-evidence.py --check <file>       # one GROUNDED block
    python3 check-ground-evidence.py --fixtures <dir>     # all *.txt in dir;
                                                          # '# EXPECT: accept|reject'
Exit: 0 all as expected · 1 mismatch · 2 unparseable block (fail-closed).
"""

import re
import sys
from pathlib import Path

WEAK_PATTERNS = [
    "flag set", "flags set", "we checked", "we validated", "we verified",
    "we believe", "should be", "should work", "should pass", "seems",
    "looks fine", "looks good", "assume", "assumed", "predicted", "predict",
    "expected to", "believed", "attributed to", "per engineering", "per the team",
    "no reason to doubt", "tests pass", "ci is green", "ci green",
]

UNNAMED_ACTORS = {"", "we", "us", "team", "the team", "ourselves", "everyone"}

ARTIFACT_PATTERNS = [
    re.compile(r"https?://\S+"),                              # URL
    re.compile(r"(?:~|/)[\w./-]{3,}"),                        # path
    re.compile(r"\b[\w-]+\.(?:py|sh|md|json|yaml|txt|log|db)\b"),  # filename
    re.compile(r"\b\d+(?:\.\d+)?\s*(?:ms|s|m|h|runs?|bytes?|kb|mb|gb|%|x)\b", re.I),  # measurement
    re.compile(r"\b[A-Z]{2,}-\d+\b"),                          # ticket id
    re.compile(r"\b[0-9a-f]{7,40}\b"),                         # commit sha
    re.compile(r"['\"][^'\"]{4,}['\"]"),                       # quoted words
    re.compile(r"\b\d+/\d+\b"),                                # ratio e.g. 5/5
]

FIELD_RE = {
    "actor": re.compile(r"^\s*ACTOR\s*:\s*(.+)$", re.I),
    "evidence": re.compile(r"^\s*EVIDENCE\s*:\s*(.+)$", re.I),
    "verdict": re.compile(r"^\s*Verdict\s*:\s*(\S+)", re.I),
}


def parse_block(text: str) -> dict:
    """Extract ACTOR/EVIDENCE/Verdict from the first GROUNDED-style block.

    None values mean the field is absent; the caller decides if that fails.
    """
    out = {"actor": None, "evidence": None, "verdict": None}
    for line in text.splitlines():
        for field, rx in FIELD_RE.items():
            if out[field] is None:
                m = rx.match(line)
                if m:
                    out[field] = m.group(1).strip()
    return out


def judge(text: str) -> tuple[bool, list[str]]:
    """Return (accepted, reasons). accepted=True means the GROUNDED block is honest."""
    fields = parse_block(text)
    reasons = []

    if fields["verdict"] is None or fields["actor"] is None or fields["evidence"] is None:
        return False, ["BLOCKED: block missing ACTOR/EVIDENCE/Verdict — fail-closed"]

    verdict = fields["verdict"].strip().lower()
    if verdict not in ("yes", "no"):
        return False, [f"BLOCKED: unparseable Verdict '{fields['verdict']}'"]

    if verdict == "no":
        return True, ["Verdict NO — honest halt, nothing to accept or reject"]

    actor = fields["actor"].strip().strip('"').strip("'")
    if actor.lower().rstrip(":. ") in UNNAMED_ACTORS:
        reasons.append(f"unnamed actor: {actor!r} — require a named actor, never 'we'")

    evidence = fields["evidence"]
    low = evidence.lower()
    for pat in WEAK_PATTERNS:
        if pat in low:
            reasons.append(f"mock evidence: '{pat}' — an assertion of a check is not the check")
    if not any(rx.search(evidence) for rx in ARTIFACT_PATTERNS):
        reasons.append("no observed artifact in EVIDENCE (path/URL/measurement/ticket/quote)")

    return not reasons, reasons


def expect_of(text: str, path: Path) -> str:
    for line in text.splitlines():
        m = re.match(r"^#?\s*EXPECT:\s*(accept|reject)\b", line, re.I)
        if m:
            return m.group(1).lower()
    return "reject"  # adversarial by default


def check_one(path: Path) -> int:
    text = path.read_text(errors="replace")
    accepted, reasons = judge(text)
    expected = expect_of(text, path)
    ok = (accepted and expected == "accept") or (not accepted and expected == "reject")
    mark = "OK  " if ok else "MISMATCH"
    print(f"  [{mark}] {path.name}: expected {expected}, got "
          f"{'accept' if accepted else 'reject'}")
    for r in reasons:
        print(f"           - {r}")
    return 0 if ok else 1


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] not in ("--check", "--fixtures"):
        print(__doc__)
        return 1
    target = Path(sys.argv[2])
    if sys.argv[1] == "--check":
        if not target.is_file():
            print(f"not a file: {target}")
            return 2
        accepted, reasons = judge(target.read_text(errors="replace"))
        print(f"{'ACCEPT' if accepted else 'REJECT'}: {target}")
        for r in reasons:
            print(f"  - {r}")
        return 0 if accepted else 1
    files = sorted(target.glob("*.txt"))
    if not files:
        print(f"no fixtures in {target}")
        return 2
    fails = sum(check_one(f) for f in files)
    print(f"GROUND EVIDENCE: {len(files) - fails}/{len(files)} fixtures behaved as expected")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
