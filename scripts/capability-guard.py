#!/usr/bin/env python3
"""
Capability guard for APEX spawns (W1/item 47).

Least privilege: every routed leaf declares a capability envelope
(read-only | write | exec) plus the dirs it may touch. Defaults live in
context/knowledge/capability-envelopes.json and are the floor: a leaf may
narrow, never widen without an explicit HYBRID acceptance.

Rule:
    read  - open
    write - requires cap write|exec AND the path under a declared write dir
    exec  - requires cap exec AND the path under a declared exec dir

Usage:
    python3 capability-guard.py --envelope <TYPE>
    python3 capability-guard.py --can <TYPE> <read|write|exec> <path> [--repo DIR]
    python3 capability-guard.py --breach-sim
Exit: 0 allowed / sim as expected · 1 blocked / breach detected · 2 usage.
"""

import json
import sys
from pathlib import Path

TABLE = Path(__file__).parent.parent / "context" / "knowledge" / "capability-envelopes.json"
SIM_ROOTS = {"$OUT": "/tmp/opencode", "$REPO": "/tmp/opencode/apex-repo"}

BREACHES = [
    ("RESEARCH", "exec", "$OUT/tool.sh", "research leaf may not exec"),
    ("LEARN", "write", "$OUT/notes.md", "learn leaf may not write"),
    ("BUILD", "write", "/etc/passwd", "write outside declared dirs"),
    ("DECIDE", "exec", "$REPO/run.sh", "decide leaf may not exec"),
    ("GENERATE", "exec", "$OUT/build.sh", "generate leaf may not exec"),
]

CONTROLS = [
    ("BUILD", "write", "$OUT/out.md", "build write inside $OUT"),
    ("BUILD", "exec", "$REPO/run.sh", "build exec inside $REPO"),
]


def load_table() -> dict:
    with open(TABLE) as f:
        return json.load(f)


def expand(path: str, roots: dict) -> str:
    for token, val in roots.items():
        if path.startswith(token):
            return val + path[len(token):]
    return path


def under(path: str, dirs: list[str]) -> bool:
    p = str(Path(path))
    return any(p == d or p.startswith(d.rstrip("/") + "/") for d in dirs)


def decide(table: dict, leaf_type: str, action: str, path: str, roots: dict) -> tuple[bool, str]:
    env = table["envelopes"].get(leaf_type.upper())
    if env is None:
        return False, f"unknown leaf TYPE {leaf_type!r} (fail-closed)"
    if action == "read":
        return True, "read is open"
    real = expand(path, roots)
    if action == "write":
        if env["cap"] not in ("write", "exec"):
            return False, f"{leaf_type} is {env['cap']}: no write capability"
        if not under(real, [expand(d, roots) for d in env["write_dirs"]]):
            return False, f"write outside declared dirs for {leaf_type}: {real}"
        return True, "write allowed under declared dirs"
    if action == "exec":
        if env["cap"] != "exec":
            return False, f"{leaf_type} cap is {env['cap']}: no exec capability"
        if not under(real, [expand(d, roots) for d in env["exec_dirs"]]):
            return False, f"exec outside declared dirs for {leaf_type}: {real}"
        return True, "exec allowed under declared dirs"
    return False, f"unknown action {action!r} (fail-closed)"


def breach_sim(table: dict) -> int:
    b_ok = 0
    print("  breach simulations (must all be blocked):")
    for leaf, action, path, why in BREACHES:
        allowed, reason = decide(table, leaf, action, path, SIM_ROOTS)
        if allowed:
            print(f"    [BREACH ] {leaf} {action} {path} ({why}): {reason}")
        else:
            b_ok += 1
            print(f"    [BLOCKED] {leaf} {action} {path} ({why}): {reason}")
    c_ok = 0
    print("  positive controls (must all be allowed):")
    for leaf, action, path, why in CONTROLS:
        allowed, reason = decide(table, leaf, action, path, SIM_ROOTS)
        if allowed:
            c_ok += 1
            print(f"    [ALLOWED] {leaf} {action} {path} ({why})")
        else:
            print(f"    [DENIED ] {leaf} {action} {path} ({why}): {reason}")
    readonly = [t for t, e in table["envelopes"].items() if e["cap"] == "read-only"]
    leaked = [t for t, e in table["envelopes"].items()
              if e["cap"] == "read-only" and (e["write_dirs"] or e["exec_dirs"])]
    if not leaked:
        print(f"AUDIT: 0 research leaves with write tools (read-only set checked: {', '.join(sorted(readonly))})")
    else:
        print(f"AUDIT FAIL: read-only types carrying dirs: {leaked}")
    print(f"CAPABILITY GUARD: {b_ok}/{len(BREACHES)} breaches blocked, "
          f"{c_ok}/{len(CONTROLS)} controls allowed")
    return 0 if b_ok == len(BREACHES) and c_ok == len(CONTROLS) and not leaked else 1


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    table = load_table()

    if sys.argv[1] == "--breach-sim":
        return breach_sim(table)

    if sys.argv[1] == "--envelope" and len(sys.argv) >= 3:
        env = table["envelopes"].get(sys.argv[2].upper())
        if env is None:
            print(f"unknown leaf TYPE {sys.argv[2]!r} (fail-closed)")
            return 2
        print(json.dumps({"type": sys.argv[2].upper(), **env}, indent=2))
        return 0

    if sys.argv[1] == "--can" and len(sys.argv) >= 5:
        roots = dict(SIM_ROOTS)
        if "--repo" in sys.argv:
            roots["$REPO"] = sys.argv[sys.argv.index("--repo") + 1]
        allowed, reason = decide(table, sys.argv[2], sys.argv[3].lower(), sys.argv[4], roots)
        print(f"{'ALLOW' if allowed else 'BLOCK'}: {sys.argv[2]} {sys.argv[3]} {sys.argv[4]} - {reason}")
        return 0 if allowed else 1

    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
