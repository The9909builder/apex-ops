#!/usr/bin/env python3
"""
W1 gate battery (vision: "goldens 1/1 PASS · forged fixture BLOCKED · 0 catalog
dups · precedence test 5/5 · breach simulation blocked").

One command, five verdicts, each from the mechanical checker that owns it.
Exit 0 = all five hold; 1 = any fails. Prints one line per check plus a final
W1 GATE line for the journal receipt.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
PY = sys.executable

RESULTS: list[tuple[str, bool, str]] = []


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([PY, *args], capture_output=True, text=True, cwd=SKILL_DIR)


def gate(name: str, ok: bool, detail: str) -> None:
    RESULTS.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")


def main() -> int:
    # 1. goldens 1/1 PASS
    golden = SKILL_DIR / "eval-outputs" / "catalog-route-reaches-installed-skill.txt"
    p = run("scripts/check-receipts.py", "--check", str(golden))
    gate("goldens 1/1", p.returncode == 0 and "1/1 route lines verified" in p.stdout,
         " ".join(p.stdout.strip().splitlines()[:1]))

    # 2. forged fixture BLOCKED (a gate claim with no evidence is refused)
    tmp = Path(tempfile.mkdtemp())
    forged = tmp / "forged.txt"
    forged.write_text(
        "ROUTE\nNODE F [BUILD] -> sealed-substrate-architect: gate = trust me\n")
    p = run("scripts/check-receipts.py", "--check", str(forged))
    gate("forged fixture BLOCKED", p.returncode != 0 and "STATUS: FAIL" in p.stdout,
         f"rc={p.returncode}, not a PASS")

    # 3. 0 catalog dups
    cat = json.loads((SKILL_DIR / "context" / "knowledge" / "donor-catalog.json").read_text())
    names = [s["name"] for s in cat["skills"]]
    dups = sorted({n for n in names if names.count(n) > 1})
    junk = [s["id"] for s in cat["skills"]
            if "_template" in s["id"] or s["id"].endswith(".bak")]
    gate("0 catalog dups", not dups and not junk,
         f"{len(names)} entries, {len(dups)} dups, {len(junk)} bak/_template")

    # 4. precedence test 5/5
    p = run("scripts/check-front-door.py", "--fixtures",
            str(SKILL_DIR / "context" / "knowledge" / "fixtures" / "front-door"))
    gate("precedence test 5/5",
         p.returncode == 0 and "5/5 intents routed to the correct door" in p.stdout,
         " ".join(p.stdout.strip().splitlines()[-1:]))

    # 5. breach simulation blocked
    p = run("scripts/capability-guard.py", "--breach-sim")
    gate("breach simulation blocked",
         p.returncode == 0 and "5/5 breaches blocked" in p.stdout,
         " ".join(p.stdout.strip().splitlines()[-1:]))

    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"W1 GATE: {'PASS' if not failed else 'FAIL ' + ','.join(failed)} "
          f"({len(RESULTS) - len(failed)}/{len(RESULTS)})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
