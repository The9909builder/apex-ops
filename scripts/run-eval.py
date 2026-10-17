#!/usr/bin/env python3
"""
Eval runner for APEX golden tasks.

apex_eval.py is a checker: it scores saved output files. This runner closes
the loop honestly — it prepares per-task prompt files and reports which
outputs are missing, then delegates all scoring to apex_eval.py. It never
fabricates outputs: a task whose output file does not exist is reported as
MISSING, never invented.

Usage:
    python3 scripts/run-eval.py --prepare [outdir]   # write <id>.prompt.txt + status
    python3 scripts/run-eval.py --check   [outdir]   # run apex_eval.py --batch (exit 0 = pass)
    python3 scripts/run-eval.py --status  [outdir]   # show per-task output presence

Workflow:
    1. --prepare               creates eval-outputs/<id>.prompt.txt
    2. run apex on each prompt, save output as eval-outputs/<id>.txt
    3. --check                 scores everything present via apex_eval.py
"""

import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent.parent
DEFAULT_OUTDIR = HERE / "eval-outputs"


def load_tasks() -> list[dict]:
    with open(HERE / "evals.yaml") as f:
        return yaml.safe_load(f).get("golden_tasks", [])


def load_negative_fixtures() -> list[dict]:
    with open(HERE / "evals.yaml") as f:
        return yaml.safe_load(f).get("negative_fixtures", [])


def outdir_from(argv: list[str], start: int) -> Path:
    return Path(argv[start]) if len(argv) > start else DEFAULT_OUTDIR


def prepare(outdir: Path, tasks: list[dict]) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    for t in tasks:
        prompt_file = outdir / f"{t['id']}.prompt.txt"
        prompt_file.write_text(t["prompt"])
        print(f"  wrote {prompt_file.relative_to(HERE.parent.parent)}")
    for fx in load_negative_fixtures():
        prompt_file = outdir / f"{fx['id']}.prompt.txt"
        prompt_file.write_text(fx.get("prompt", "") + "\n# must-fail fixture: a bad output the scorer must reject")
        print(f"  wrote {prompt_file.relative_to(HERE.parent.parent)} (negative fixture)")
    print(f"\nNext: run apex on each prompt and save the output as {outdir}/<task-id>.txt, then run --check")


def status(outdir: Path, tasks: list[dict]) -> int:
    missing = 0
    print(f"Output dir: {outdir}\n")
    for t in tasks:
        output_file = outdir / f"{t['id']}.txt"
        if output_file.exists():
            print(f"  READY    {t['id']}")
        else:
            print(f"  MISSING  {t['id']}")
            missing += 1
    neg = load_negative_fixtures()
    if neg:
        print()
        for fx in neg:
            output_file = outdir / f"{fx['id']}.txt"
            state = "READY  " if output_file.exists() else "MISSING"
            print(f"  {state} {fx['id']} (negative fixture — must FAIL its contract)")
    print(f"\n{len(tasks) - missing}/{len(tasks)} outputs present")
    return 1 if missing else 0


def check(outdir: Path) -> int:
    if not outdir.exists():
        print(f"No output dir at {outdir}. Run --prepare first, then produce outputs.")
        return 1
    result = subprocess.run(
        [sys.executable, str(HERE / "apex_eval.py"), "--batch", str(outdir)],
    )
    return result.returncode


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("--prepare", "--check", "--status"):
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    outdir = outdir_from(sys.argv, 2)
    tasks = load_tasks()

    if cmd == "--prepare":
        prepare(outdir, tasks)
        sys.exit(0)
    elif cmd == "--status":
        sys.exit(status(outdir, tasks))
    elif cmd == "--check":
        sys.exit(check(outdir))


if __name__ == "__main__":
    main()
