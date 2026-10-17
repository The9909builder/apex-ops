#!/usr/bin/env python3
"""
APEX Auto-Eval Harvest.

Converts a REAL failed or concerning APEX run output into a golden task,
so the eval suite grows from reality instead of authoring. This is the
immunization loop: a failure that taught the router something becomes a
regression test.

Usage:
    python3 harvest-eval.py --from <run_output.txt> --outcome blocked|done_with_concerns \
                            --id <task-slug> [--prompt "original intent"]

What gets harvested from the output (heuristics, printed for review):
  - must:   the exact STATUS token line, GROUNDED verdict if present,
            every donor named in NODE route lines, gates from GATES FIRED
  - must_not (blocked): TREE:, ROUTE, FUSE  (a blocked run must emit none)
  - must_not (done_with_concerns): 'STATUS: DONE' exact-token trap

The task is appended to evals.yaml golden_tasks. quality.yaml is synced
automatically to keep check-contract-drift.py green.

Exit codes: 0 = task appended, 1 = nothing harvested / duplicate, 2 = usage.
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

SKILL_DIR = Path(__file__).parent.parent
EVALS_FILE = SKILL_DIR / "evals.yaml"
QUALITY_FILE = SKILL_DIR / "quality.yaml"

STATUS_LINE_RE = re.compile(r"^STATUS:\s*([A-Z_]+)\s*$", re.MULTILINE)
GROUNDED_NO_RE = re.compile(r"^GROUNDED\s*:\s*NO", re.MULTILINE)
NODE_LINE_RE = re.compile(r"^\s*NODE\s+\S+\s+\[([A-Z]+)\]\s*->\s*([\w-]+)", re.MULTILINE)
INTENT_RE = re.compile(r"^INTENT\s*:\s*(.+)$", re.MULTILINE)


def harvest(output_text: str, outcome: str) -> dict:
    """Extract must/must_not criteria from a real run output."""
    must: list[str] = []
    must_not: list[str] = []

    status = STATUS_LINE_RE.search(output_text)
    if status:
        must.append(f"STATUS: {status.group(1)}")
    else:
        print("HARVEST WARNING: no exact 'STATUS: <TOKEN>' line found")

    if outcome == "blocked":
        if GROUNDED_NO_RE.search(output_text):
            must.append("GROUNDED   : NO")
        must_not += ["TREE:", "ROUTE", "FUSE"]
    elif outcome == "done_with_concerns":
        must.append("SKIPPED")
        must_not.append("STATUS: DONE")  # exact-token trap, no false positive
    else:
        print(f"Unsupported outcome: {outcome} (use blocked|done_with_concerns)")
        sys.exit(2)

    donors: list[str] = []
    for m in NODE_LINE_RE.finditer(output_text):
        donor = m.group(2)
        if donor not in donors:
            donors.append(donor)
    for d in donors:
        if d not in must:
            must.append(d)

    return {"must": must, "must_not": must_not, "donors": donors}


def append_task(task: dict) -> None:
    """Append a golden task to evals.yaml and quality.yaml golden_tasks.

    The block is inserted INSIDE golden_tasks: for evals.yaml (tasks are the
    last key) it is appended at EOF; for quality.yaml it is inserted before
    the next top-level key (freshness_horizon:) if present. Block is emitted
    with 2-space list indentation matching the existing file style.
    """
    inner = yaml.safe_dump(task, sort_keys=False, allow_unicode=True, width=100)
    # indent every line by 4, then turn the first into a '- ' list item
    lines = ["    " + ln for ln in inner.splitlines()]
    lines[0] = "  - " + lines[0].strip()
    block = "\n".join(lines) + "\n"

    for f in (EVALS_FILE, QUALITY_FILE):
        text = f.read_text()
        if not text.endswith("\n"):
            text += "\n"
        # find end of the golden_tasks list: next top-level key after 'golden_tasks:'
        m = re.search(r"^golden_tasks:\s*$(?:(?!^\S).)*", text, re.DOTALL | re.MULTILINE)
        if m:
            insert_at = m.end()
            text = text[:insert_at] + block + text[insert_at:]
        else:
            text += "\ngolden_tasks:\n" + block
        f.write_text(text)


def main() -> None:
    args = sys.argv[1:]
    src = outcome = task_id = prompt = None
    i = 0
    while i < len(args):
        if args[i] == "--from" and i + 1 < len(args):
            src = Path(args[i + 1]); i += 2
        elif args[i] == "--outcome" and i + 1 < len(args):
            outcome = args[i + 1]; i += 2
        elif args[i] == "--id" and i + 1 < len(args):
            task_id = args[i + 1]; i += 2
        elif args[i] == "--prompt" and i + 1 < len(args):
            prompt = args[i + 1]; i += 2
        else:
            i += 1

    if not (src and outcome and task_id and src.exists()):
        print(__doc__)
        sys.exit(2)

    evals = yaml.safe_load(EVALS_FILE.read_text())
    existing = {t["id"] for t in evals.get("golden_tasks", [])}
    if task_id in existing:
        print(f"REFUSED: task id '{task_id}' already exists — failures append, they don't overwrite")
        sys.exit(1)

    output_text = src.read_text()
    harvested = harvest(output_text, outcome)
    if not harvested["must"]:
        print("NOTHING HARVESTED: no usable criteria found in output")
        sys.exit(1)

    if prompt is None:
        m = INTENT_RE.search(output_text)
        prompt = m.group(1).strip() if m else f"replay harvested failure {task_id}"

    task = {
        "id": task_id,
        "prompt": prompt,
        "must": harvested["must"],
        "must_not": harvested["must_not"],
    }
    append_task(task)

    print(f"HARVESTED: {task_id} ({outcome}) -> evals.yaml + quality.yaml")
    print(f"  donors in route: {harvested['donors'] or 'none'}")
    print(f"  must[{len(task['must'])}] must_not[{len(task['must_not'])}]")
    for m_ in task["must"]:
        print(f"    + '{m_}'")
    for m_ in task["must_not"]:
        print(f"    - '{m_}'")
    print(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} "
          f"— next full eval run must include this task")
    sys.exit(0)


if __name__ == "__main__":
    main()
