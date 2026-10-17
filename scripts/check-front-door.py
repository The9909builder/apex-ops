#!/usr/bin/env python3
"""
Front-door precedence checker for APEX (W1/item 44).

Routes a raw user intent to the correct entry door using the ordered table in
context/knowledge/front-door-precedence.json. Score = number of a door's
patterns that appear in the intent (case-insensitive); highest score wins;
ties resolve by precedence_order; no match falls back to the table's fallback.

Usage:
    python3 check-front-door.py --intent "<raw intent text>"
    python3 check-front-door.py --fixtures <dir>   # *.txt: '# EXPECT: <door>' + '# INTENT: <text>'
Exit: 0 all as expected · 1 mismatch · 2 usage/missing fixture (fail-closed).
"""

import json
import re
import sys
from pathlib import Path

TABLE = Path(__file__).parent.parent / "context" / "knowledge" / "front-door-precedence.json"


def load_table() -> dict:
    with open(TABLE) as f:
        return json.load(f)


def route(text: str, table: dict) -> tuple[str, dict]:
    """Return (winning door id, per-door scores). Ties resolve by precedence order."""
    low = text.lower()
    scores = {}
    for door in table["doors"]:
        scores[door["id"]] = sum(1 for p in door["patterns"] if re.search(p, low))
    winner, best = table["fallback"], 0
    for door_id in table["precedence_order"]:
        if scores.get(door_id, 0) > best:
            best = scores[door_id]
            winner = door_id
    return winner, scores


def expect_of(text: str) -> str | None:
    for line in text.splitlines():
        m = re.match(r"^#?\s*EXPECT:\s*(\S+)\s*$", line, re.I)
        if m:
            return m.group(1)
    return None


def intent_of(text: str) -> str | None:
    for line in text.splitlines():
        m = re.match(r"^#?\s*INTENT:\s*(.+)$", line, re.I)
        if m:
            return m.group(1).strip()
    body = " ".join(l.strip() for l in text.splitlines()
                    if l.strip() and not l.lstrip().startswith("#"))
    return body or None


def check_one(path: Path, table: dict) -> int:
    text = path.read_text(errors="replace")
    expected = expect_of(text)
    intent = intent_of(text)
    if expected is None or intent is None:
        print(f"  [MISMATCH] {path.name}: fixture must carry '# EXPECT: <door>' and '# INTENT: <text>'")
        return 1
    winner, scores = route(intent, table)
    ok = winner == expected
    mark = "OK  " if ok else "MISMATCH"
    detail = " ".join(f"{k}={v}" for k, v in scores.items() if v)
    print(f"  [{mark}] {path.name}: expected {expected}, got {winner}"
          f"{' (' + detail + ')' if detail else ''}")
    return 0 if ok else 1


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] not in ("--intent", "--fixtures"):
        print(__doc__)
        return 1
    table = load_table()

    if sys.argv[1] == "--intent":
        winner, scores = route(sys.argv[2], table)
        detail = " ".join(f"{k}={v}" for k, v in scores.items() if v)
        print(f"DOOR: {winner}" + (f"  ({detail})" if detail else ""))
        return 0

    target = Path(sys.argv[2])
    if not target.is_dir():
        print(f"not a dir: {target}")
        return 2
    files = sorted(target.glob("*.txt"))
    if not files:
        print(f"no fixtures in {target}")
        return 2
    fails = sum(check_one(f, table) for f in files)
    print(f"FRONT DOOR: {len(files) - fails}/{len(files)} intents routed to the correct door")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
