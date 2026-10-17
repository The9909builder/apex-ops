#!/usr/bin/env python3
"""
Council checker for APEX DECIDE leaves (W1/item 48).

Validates a COUNCIL block (rules: context/knowledge/council-rules.md):
2-3 candidates, each `- C<n> [<lens>] score <0-10>`, a named winner, and a
RULED: line whenever the winner is not the top score.

Usage:
    python3 check-council.py --check <run-output>
    python3 check-council.py --record <run-output> --ledger <path> [--id <slug>]
    python3 check-council.py --fixtures <dir>
Exit: 0 OK / fixture as expected · 1 reject / mismatch · 2 usage.
"""

import json
import re
import sys
import time
from pathlib import Path

COUNCIL_RE = re.compile(r"^COUNCIL:.*\((\d+) candidates?\)")
CAND_RE = re.compile(r"^- C(\d+) \[([^\]]+)\] score (\d{1,2})\b")
WINNER_RE = re.compile(r"^WINNER: C(\d+)\b")
RULED_RE = re.compile(r"^RULED:\s*\S")


def judge(text: str) -> tuple[bool, str, dict]:
    council = None
    cands: dict[int, dict] = {}
    winner = None
    ruled = False
    for raw in text.splitlines():
        ln = raw.strip()
        m = COUNCIL_RE.match(ln)
        if m:
            council = int(m.group(1))
            continue
        m = CAND_RE.match(ln)
        if m:
            cands[int(m.group(1))] = {"lens": m.group(2).strip(), "score": int(m.group(3))}
            continue
        m = WINNER_RE.match(ln)
        if m:
            winner = int(m.group(1))
            continue
        if RULED_RE.match(ln):
            ruled = True

    if council is None and not cands:
        return False, "no COUNCIL block found", {}
    if not cands:
        return False, "COUNCIL header present but no candidate line parses " \
                      "(need `- C<n> [<lens>] score <0-10>`)", {}
    n = len(cands)
    if council is not None and council != n:
        return False, f"header declares {council} candidates, found {n}", {}
    if n < 2:
        return False, f"single candidate (C{next(iter(cands))}): not a council; " \
                      "re-route or state the skip reason", {}
    if n > 3:
        return False, f"{n} candidates: over the 3 cap; split the leaf", {}
    over = [c for c, v in cands.items() if v["score"] > 10]
    if over:
        return False, f"score out of range 0-10 on C{over[0]}", {}
    if winner is None:
        return False, "no WINNER line", {}
    if winner not in cands:
        return False, f"winner C{winner} is not among candidates {sorted(cands)}", {}
    top = max(v["score"] for v in cands.values())
    if cands[winner]["score"] < top and not ruled:
        return False, f"winner C{winner} (score {cands[winner]['score']}) below " \
                      f"top ({top}) with no RULED: reason", {}
    note = "" if cands[winner]["score"] == top else " (non-top winner, ruled)"
    data = {
        "candidates": n,
        "winner": f"C{winner}",
        "scores": {f"C{c}": cands[c]["score"] for c in sorted(cands)},
        "lenses": {f"C{c}": cands[c]["lens"] for c in sorted(cands)},
    }
    return True, f"winner C{winner} {data['scores']}{note}", data


def record(path: str, ledger: str, slug: str) -> int:
    ok, detail, data = judge(Path(path).read_text())
    if not ok:
        print(f"REJECT: {detail}")
        return 1
    row = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "id": f"apex-council:{slug}",
        "source": "apex-council",
        "slug": slug,
        "winner": data["winner"],
        "scores": data["scores"],
        "lenses": data["lenses"],
        "status": "decided",
    }
    with open(ledger, "a") as f:
        f.write(json.dumps(row) + "\n")
    print(f"RECORDED: {data['winner']} {data['scores']} -> {ledger}")
    return 0


def fixtures(d: str) -> int:
    files = sorted(Path(d).glob("*.txt"))
    assert files, f"no fixtures in {d}"
    ok_n = 0
    for f in files:
        text = f.read_text()
        expect = "accept" if "accept" in text.splitlines()[0] else "reject"
        ok, detail, _ = judge(text)
        got = "accept" if ok else "reject"
        mark = "OK  " if got == expect else "MISMATCH"
        if got == expect:
            ok_n += 1
        print(f"  [{mark}] {f.name}: expected {expect}, got {got} - {detail}")
    print(f"COUNCIL: {ok_n}/{len(files)} fixtures behaved as expected")
    return 0 if ok_n == len(files) else 1


def main() -> int:
    a = sys.argv
    if len(a) >= 3 and a[1] == "--check":
        ok, detail, _ = judge(Path(a[2]).read_text())
        print(f"{'ACCEPT' if ok else 'REJECT'}: {detail}")
        return 0 if ok else 1
    if len(a) >= 4 and a[1] == "--record":
        slug = a[a.index("--id") + 1] if "--id" in a else Path(a[2]).stem
        return record(a[2], a[a.index("--ledger") + 1] if "--ledger" in a else
                      str(Path.home() / ".kraken" / "outcomes" / "decisions.jsonl"), slug)
    if len(a) >= 3 and a[1] == "--fixtures":
        return fixtures(a[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
