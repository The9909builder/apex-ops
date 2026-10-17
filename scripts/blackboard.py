#!/usr/bin/env python3
"""
Blackboard persistence for APEX.

Manages the JSON state file that enables resume without re-derivation.

Usage:
    python3 blackboard.py init <session_id> [path]   # Create new blackboard (writes file when path given)
    python3 blackboard.py write <bb_path> <stage>    # Mark stage complete
    python3 blackboard.py read <bb_path>             # Dump current state
    python3 blackboard.py resume <bb_path>           # Show last completed stage
"""

import copy
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = {
    "session": "",
    "system_card": {
        "intent": "",
        "mode": "",
        "risk": 0,
        "root_type": "",
    },
    "grounded": {
        "verdict": "",
        "actor": "",
        "cost": "",
        "evidence": "",
    },
    "nodes": {},
    "dependencies": [],
    "contradictions": [],
    "plan": [],
    "stages_completed": [],
}

STAGES = ["DECODE", "GROUND", "DECOMPOSE", "ROUTE", "FUSE", "PLAN", "CLOSE"]


def init_blackboard(session_id: str) -> dict:
    """Create a new blackboard with the schema.

    Deep-copies SCHEMA: a shallow .copy() shares the nested dicts/lists
    between sessions, so stages completed in one session leak into another.
    """
    bb = copy.deepcopy(SCHEMA)
    bb["session"] = session_id
    bb["stages_completed"] = []
    return bb


def load_blackboard(path: Path) -> dict | None:
    """Load blackboard from disk."""
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def save_blackboard(bb: dict, path: Path) -> None:
    """Persist blackboard to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(bb, f, indent=2)


def mark_stage(bb: dict, stage: str) -> dict:
    """Mark a stage as completed."""
    if stage not in STAGES:
        print(f"WARNING: Unknown stage '{stage}'. Valid: {STAGES}")
    if stage not in bb["stages_completed"]:
        bb["stages_completed"].append(stage)
    return bb


def resume_point(bb: dict) -> str | None:
    """Return the last completed stage, or None if empty."""
    if not bb["stages_completed"]:
        return None
    return bb["stages_completed"][-1]


def next_stage(bb: dict) -> str | None:
    """Return the next stage to run, or None if all done."""
    completed = set(bb["stages_completed"])
    for stage in STAGES:
        if stage not in completed:
            return stage
    return None


def selftest() -> int:
    """Roundtrip test: schema isolation, write, save, load, resume.

    Exits 0 on pass, 1 on any failure.
    """
    failures = []

    # Schema isolation: two sessions must not share nested state.
    bb1 = init_blackboard("s1")
    bb2 = init_blackboard("s2")
    if bb1["stages_completed"] is bb2["stages_completed"]:
        failures.append("stages_completed shared between sessions (shallow copy)")
    if bb1["system_card"] is bb2["system_card"]:
        failures.append("system_card shared between sessions (shallow copy)")

    # Roundtrip: mark stages, save, load, resume.
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "bb.json"
        bb = init_blackboard("roundtrip")
        save_blackboard(mark_stage(bb, "DECODE"), path)
        bb = load_blackboard(path)
        mark_stage(bb, "GROUND")
        save_blackboard(bb, path)
        bb = load_blackboard(path)
        if resume_point(bb) != "GROUND":
            failures.append(f"resume_point={resume_point(bb)!r}, expected GROUND")
        if next_stage(bb) != "DECOMPOSE":
            failures.append(f"next_stage={next_stage(bb)!r}, expected DECOMPOSE")
        if load_blackboard(Path(td) / "missing.json") is not None:
            failures.append("missing blackboard should load as None")

    if failures:
        print("SELFTEST: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("SELFTEST: PASS (schema isolated, roundtrip ok)")
    return 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""

    if cmd == "selftest":
        sys.exit(selftest())

    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    if cmd == "init":
        session_id = sys.argv[2] if len(sys.argv) > 2 else f"session-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
        bb = init_blackboard(session_id)
        print(json.dumps(bb, indent=2))
        if len(sys.argv) > 3:
            bb_path = Path(sys.argv[3])
            save_blackboard(bb, bb_path)
            print(f"Blackboard written: {bb_path}", file=sys.stderr)

    elif cmd == "write":
        if len(sys.argv) < 4:
            print("Usage: blackboard.py write <bb_path> <stage>")
            sys.exit(1)
        bb_path = Path(sys.argv[2])
        stage = sys.argv[3]
        bb = load_blackboard(bb_path)
        if bb is None:
            print(f"ERROR: No blackboard at {bb_path}. Run 'init' first.")
            sys.exit(1)
        bb = mark_stage(bb, stage)
        save_blackboard(bb, bb_path)
        nxt = next_stage(bb)
        print(f"Stage {stage} marked complete. Next: {nxt or 'ALL DONE'}")

    elif cmd == "read":
        bb_path = Path(sys.argv[2])
        bb = load_blackboard(bb_path)
        if bb is None:
            print(f"ERROR: No blackboard at {bb_path}")
            sys.exit(1)
        print(json.dumps(bb, indent=2))

    elif cmd == "resume":
        bb_path = Path(sys.argv[2])
        bb = load_blackboard(bb_path)
        if bb is None:
            print(f"ERROR: No blackboard at {bb_path}")
            sys.exit(1)
        last = resume_point(bb)
        nxt = next_stage(bb)
        print(f"Last completed: {last or 'none'}")
        print(f"Next stage: {nxt or 'ALL DONE'}")
        print(f"Stages completed: {bb['stages_completed']}")
        print(f"Resume from: {nxt or 'CLOSE (all stages done)'}")

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
