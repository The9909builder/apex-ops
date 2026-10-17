#!/usr/bin/env python3
"""
W2 gate battery (vision: "two runs byte-identical · backdated source -> STALE ·
every INBOX item carries a one-line remedy" plus the item contracts: 7 declared
views, progressive disclosure, trust ladder, plain-language errors, pulse wire).

One command, nine verdicts, each from the mechanical checker that owns it.
Exit 0 = all hold; 1 = any fails. Prints one line per check plus a final
W2 GATE line for the journal receipt.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
PY = sys.executable
BIN = Path(os.path.expanduser(os.environ.get("APEX_BIN", "~/.apex/bin")))
MC = BIN / "mission-control.py"
LADDER = BIN / "apex-ladder.py"
ERROR = BIN / "apex-error"

RESULTS: list[tuple[str, bool, str]] = []
VIEW_NAMES = ["NOW", "WALL", "LEDGER", "INBOX", "LEARNED", "NEXT", "COST"]


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([PY, *args], capture_output=True, text=True, cwd=SKILL_DIR)


def gate(name: str, ok: bool, detail: str) -> None:
    RESULTS.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")


def iso(ago_h: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=ago_h)).isoformat()


def utfy(path: Path, ago_h: float) -> None:
    t = (datetime.now(timezone.utc) - timedelta(hours=ago_h)).timestamp()
    os.utime(path, (t, t))


def make_home(root: Path, name: str, stale: bool = False,
              tasks=None, errors=None, quiet: bool = False) -> Path:
    home = root / name
    j = home / "journal"
    j.mkdir(parents=True)
    beats_ts = iso(30.0) if stale else iso(0.05)
    (j / "beats.jsonl").write_text(json.dumps(
        {"ts": beats_ts, "ok": True, "api": "up", "mcp": "ok"}) + "\n")
    (j / "scan-latest.json").write_text(json.dumps({
        "ts": beats_ts, "mind": {"api": "up", "memories": 2, "events": 1,
                                 "decision_traces": 1},
        "substrate": {"head": "abc123", "dirty": 0},
        "learnings": {"total": 1, "unconsumed": 0}}))
    if stale:
        utfy(j / "beats.jsonl", 30.0)
        utfy(j / "scan-latest.json", 30.0)
    if tasks is None:
        tasks = [
            {"id": "t1", "title": "fix widget", "status": "blocked",
             "detail": "blocked: waits for CI", "acceptance": "gate green"},
            {"id": "t2", "title": "build thing", "status": "queued",
             "acceptance": "thing built"},
            {"id": "t3", "title": "keep watch", "status": "standing",
             "acceptance": "weekly"},
            {"id": "t9", "title": "done thing", "status": "done"},
        ]
        if quiet:
            tasks = [{"id": "t9", "title": "done thing", "status": "done"}]
    (home / "tasks.jsonl").write_text(
        "\n".join(json.dumps(t) for t in tasks) + "\n")
    (home / "NEXT.md").write_text(
        "# NEXT\n\n- [ ] open box one\n- [ ] open box two\n\n"
        "| metric | value |\n|---|---|\n| gates | 2 |\n")
    (home / "learnings.jsonl").write_text(json.dumps(
        {"ts": iso(0.1), "type": "operational",
         "insight": "fixture learning"}) + "\n")
    if errors:
        (j / "errors.jsonl").write_text("\n".join(json.dumps(e) for e in errors) + "\n")
    return home


def mc(home: Path, *args: str) -> subprocess.CompletedProcess:
    return run(str(MC), "--home", str(home), *args)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section(out: str, name: str) -> list:
    res, inn = [], False
    for line in out.splitlines():
        if line.startswith("## "):
            inn = line.startswith(f"## {name} ·")
            continue
        if inn:
            res.append(line)
    return res


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="apex-w2-gate-"))

    # 1 + 6. byte-identical double-run, then refresh short-circuit / regen
    home_a = make_home(tmp, "fresh", errors=[{
        "ts": iso(0.2), "source": "apex-scan", "cause": "ci timeout",
        "blast": "none", "remedy": "rerun scan", "continued": "yes"}])
    out = home_a / "MISSION-CONTROL.md"
    r1 = mc(home_a)
    sha1 = sha(out)
    r2 = mc(home_a)
    sha2 = sha(out)
    gate("double-run byte-identical",
         r1.returncode == 0 and r2.returncode == 0
         and "changed=true" in r1.stdout and "changed=false" in r2.stdout
         and sha1 == sha2,
         f"changed=false on rerun, sha {sha1[:12]} == {sha2[:12]}")

    with open(home_a / "learnings.jsonl", "a") as f:
        f.write(json.dumps({"ts": iso(0.0), "type": "operational",
                            "insight": "second fixture learning"}) + "\n")
    m1 = out.stat().st_mtime_ns
    rf1 = mc(home_a, "--refresh")
    m2 = out.stat().st_mtime_ns
    rf2 = mc(home_a, "--refresh")
    m3 = out.stat().st_mtime_ns
    gate("refresh short-circuit",
         "regenerated" in rf1.stdout and m1 != m2 and m2 == m3
         and "unchanged" in rf2.stdout,
         "changed source -> regenerated + rewritten; rerun -> unchanged, no rewrite")

    # 5. progressive disclosure: --status <=3 lines, expansions logged, bad view rc=2
    exp = home_a / "journal" / "expansions.jsonl"
    before = len(exp.read_text().splitlines()) if exp.exists() else 0
    rs = mc(home_a, "--status")
    rv = mc(home_a, "--view", "NOW")
    rb = mc(home_a, "--view", "BOGUS")
    after = len(exp.read_text().splitlines()) if exp.exists() else 0
    gate("progressive disclosure",
         len(rs.stdout.splitlines()) == 3 and rv.returncode == 0
         and after > before and rb.returncode == 2,
         f"--status {len(rs.stdout.splitlines())} lines, "
         f"--view logged ({after - before} row), unknown view rc=2")

    # 4. seven views present, each declared source/trigger/action, <=40 lines
    doc = out.read_text()
    comments = re.findall(r"<!-- view: (\w+) \| source: ([^|]+)\| trigger: "
                          r"([^|]+)\| action: ([^|]+)\|", doc)
    names = [c[0] for c in comments if c[1].strip() and c[2].strip()
             and c[3].strip()]
    blocks = re.split(r"(?=<!-- view: )", doc)
    oversized = []
    for b in blocks:
        m = re.match(r"<!-- view: (\w+)", b)
        if not m:
            continue
        n = len([l for l in b.splitlines() if not l.startswith("<!-- view:")])
        if n > 40:
            oversized.append(f"{m.group(1)}={n}")
    gate("7 declared views <=40 lines",
         names == VIEW_NAMES and not oversized,
         f"{len(names)}/7 views with source+trigger+action, "
         f"{len(oversized)} oversized")

    # 2 + 3. backdated source -> STALE chip; INBOX 100% remedy on that home
    home_b = make_home(tmp, "stale", stale=True, errors=[{
        "ts": iso(0.2), "source": "apex-scan", "cause": "ci timeout",
        "blast": "none", "remedy": "rerun scan", "continued": "yes"}])
    mb = mc(home_b)
    docb = (home_b / "MISSION-CONTROL.md").read_text()
    stale_now = re.search(r"## NOW · STALE · as of \d{4}-\d{2}-\d{2}", docb)
    gate("backdated source -> STALE",
         mb.returncode == 0 and bool(stale_now),
         f"NOW chip: {stale_now.group(0) if stale_now else 'missing'}")

    ib = section(docb, "INBOX")
    bullets = [l for l in ib if l.startswith("- ")]
    missing = [l for l in bullets if "remedy:" not in l]
    gate("INBOX 100% remedy (stale home)",
         bullets and not missing and len(bullets) >= 5,
         f"{len(bullets)} items, {len(missing)} without remedy")

    # 3b. quiet home -> silence line, no bullets
    home_c = make_home(tmp, "quiet", quiet=True)
    mc(home_c)
    ic = section((home_c / "MISSION-CONTROL.md").read_text(), "INBOX")
    gate("INBOX empty -> silence",
         any("(silence - nothing needs you)" in l for l in ic)
         and not [l for l in ic if l.startswith("- ")],
         "empty home renders silence, 0 bullets")

    # 7. trust ladder: 9 -> propose-only, 10 -> auto, 1 fail -> demote, forged blocked
    home_l = tmp / "ladder"
    home_l.mkdir()
    ok_l = run(str(LADDER), "propose", "x", "--home", str(home_l)).returncode == 0
    for i in range(9):
        run(str(LADDER), "record", "x", "pass", "--receipt", f"r{i}",
            "--home", str(home_l))
    nine = run(str(LADDER), "list", "--home", str(home_l)).stdout
    ten = run(str(LADDER), "record", "x", "pass", "--receipt", "r10",
              "--home", str(home_l)).stdout
    check1 = run(str(LADDER), "check", "--home", str(home_l))
    demote = run(str(LADDER), "record", "x", "fail", "--home", str(home_l)).stdout
    noreceipt = run(str(LADDER), "record", "x", "pass", "--home", str(home_l))
    with open(home_l / "automations.jsonl", "a") as f:
        f.write(json.dumps({"ts": iso(0.0), "id": "ghost", "mode": "auto",
                            "streak": 2, "last": "pass"}) + "\n")
    check2 = run(str(LADDER), "check", "--home", str(home_l))
    gate("trust ladder contract",
         ok_l and "[propose-only] streak=9" in nine and "PROMOTED to auto" in ten
         and check1.returncode == 0 and "DEMOTED" in demote
         and noreceipt.returncode == 2 and check2.returncode == 1,
         "9 stays propose-only, 10 promotes, 1 fail demotes, forged auto refused")

    # 8. error contract: 4 fields, missing refused + not logged, audit honesty
    home_e = tmp / "errhome"
    home_e.mkdir()
    full = run(str(ERROR), "--cause", "bridge down", "--blast", "emails paused",
               "--remedy", "rerun wake", "--continued", "yes", "--home", str(home_e))
    ledger = home_e / "journal" / "errors.jsonl"
    n_before = len(ledger.read_text().splitlines())
    bad = run(str(ERROR), "--cause", "no remedy", "--home", str(home_e))
    n_after = len(ledger.read_text().splitlines())
    audit1 = run(str(ERROR), "--audit", "--home", str(home_e))
    with open(ledger, "a") as f:
        f.write(json.dumps({"ts": iso(0.0), "source": "x", "cause": "partial",
                            "blast": "", "remedy": "", "continued": "weird"}) + "\n")
    audit2 = run(str(ERROR), "--audit", "--home", str(home_e))
    fields = all(k in full.stdout for k in
                 ("WHAT:", "BLAST:", "FIX:", "WORK CONTINUED:"))
    gate("plain-language error contract",
         full.returncode == 0 and fields and bad.returncode == 2
         and n_after == n_before and "1/1 complete" in audit1.stdout
         and audit1.returncode == 0 and audit2.returncode == 1,
         "4 fields rendered, incomplete refused + unlogged, audit flags forged row")

    # 9. pulse wire: heartbeat refreshes the cockpit (item 22 `pulse-refreshed`)
    pulse = (BIN / "apex-pulse").read_text()
    gate("pulse -> cockpit refresh wired",
         "mission-control.py" in pulse and "--refresh" in pulse,
         "apex-pulse invokes mission-control.py --refresh (fail-open)")

    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"W2 GATE: {'PASS' if not failed else 'FAIL ' + ','.join(failed)} "
          f"({len(RESULTS) - len(failed)}/{len(RESULTS)})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
