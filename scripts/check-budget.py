#!/usr/bin/env python3
"""
Run budget checker for APEX (W1/item 49).

Every run declares token/leaf caps at DECODE:
    BUDGET: leaves<=<N> tokens<=<T> overrun: terse|halt
Overrun -> terse (compress, no new leaves) or halt (STOP with a resume pointer
taken from the BLACKBOARD or RESUME line). Rules: SKILL.md Stage 0 + protocol.yaml
decode gate.

Usage:
    python3 check-budget.py --check <run-output>          # declaration valid
    python3 check-budget.py --sim <run-output> --leaves N [--tokens T]
    python3 check-budget.py --fixtures <dir>
Exit: 0 OK / expected · 1 reject / halt without resume pointer · 2 usage.
"""

import re
import sys
from pathlib import Path

BUDGET_RE = re.compile(r"^BUDGET\s*:\s*leaves<=(\d+)\s+tokens<=(\d+)\s+overrun:\s*(\w+)\s*$")
RESUME_RE = re.compile(r"^(?:RESUME|BLACKBOARD)\s*:\s*(\S.*)$")
POLICIES = ("terse", "halt")


def declaration(text: str) -> tuple[dict | None, str]:
    for raw in text.splitlines():
        m = BUDGET_RE.match(raw.strip())
        if m:
            policy = m.group(3)
            if policy not in POLICIES:
                return None, f"overrun policy {policy!r} not in {POLICIES}"
            return {"leaf_cap": int(m.group(1)), "token_cap": int(m.group(2)),
                    "policy": policy}, "declared"
    return None, "no BUDGET line (need `BUDGET: leaves<=<N> tokens<=<T> overrun: terse|halt`)"


def sim(text: str, leaves: int, tokens: int | None = None) -> tuple[int, str]:
    d, why = declaration(text)
    if d is None:
        return 1, f"REJECT: {why}"
    if leaves <= d["leaf_cap"] and (tokens is None or tokens <= d["token_cap"]):
        used = f"leaves {leaves}/{d['leaf_cap']}" + (
            f", tokens {tokens}/{d['token_cap']}" if tokens is not None else "")
        return 0, f"BUDGET OK: {used}"
    if d["policy"] == "terse":
        return 0, (f"OVERRUN -> TERSE: finish the current leaf compressed, spawn no new "
                   f"leaves (leaves {leaves}/{d['leaf_cap']})")
    pointer = None
    for raw in text.splitlines():
        m = RESUME_RE.match(raw.strip())
        if m:
            pointer = m.group(1).strip()
            break
    if pointer is None:
        return 1, "OVERRUN -> HALT: no resume pointer in run output (BLACKBOARD or RESUME line required)"
    return 0, f"OVERRUN -> HALT: STOP; resume at {pointer}"


def fixtures(d: str) -> int:
    files = sorted(Path(d).glob("*.txt"))
    assert files, f"no fixtures in {d}"
    ok_n = 0
    for f in files:
        text = f.read_text()
        expect = "accept" if "accept" in text.splitlines()[0] else "reject"
        dcl, _ = declaration(text)
        leaves = dcl["leaf_cap"] + 1 if dcl else 1
        rc, detail = sim(text, leaves)
        got = "accept" if rc == 0 else "reject"
        mark = "OK  " if got == expect else "MISMATCH"
        if got == expect:
            ok_n += 1
        print(f"  [{mark}] {f.name}: expected {expect}, got {got} - {detail}")
    print(f"BUDGET: {ok_n}/{len(files)} fixtures behaved as expected")
    return 0 if ok_n == len(files) else 1


def main() -> int:
    a = sys.argv
    if len(a) >= 3 and a[1] == "--check":
        d, why = declaration(Path(a[2]).read_text())
        if d is None:
            print(f"REJECT: {why}")
            return 1
        print(f"ACCEPT: caps leaves<={d['leaf_cap']} tokens<={d['token_cap']} overrun: {d['policy']}")
        return 0
    if len(a) >= 3 and a[1] == "--sim":
        leaves = int(a[a.index("--leaves") + 1]) if "--leaves" in a else 0
        tokens = int(a[a.index("--tokens") + 1]) if "--tokens" in a else None
        rc, detail = sim(Path(a[2]).read_text(), leaves, tokens)
        print(detail)
        return rc
    if len(a) >= 3 and a[1] == "--fixtures":
        return fixtures(a[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
