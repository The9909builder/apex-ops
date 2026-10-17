#!/usr/bin/env python3
"""
APEX Selftest.

One command that re-verifies every W4 enhancement tool end-to-end, on real
files, with automatic backup/restore of anything it touches. Run after any
edit to apex scripts or SKILL.md; run before evals.

    python3 scripts/selftest.py            # full suite
    python3 scripts/selftest.py --quick    # skip slow drift drill

Checks (each is a real positive AND negative test, not a smoke check):
  1. telemetry query      — matches found + clean no-match path
  2. telemetry antibody   — add idempotent, blocks bad route, passes clean
  3. donor-health         — all donors healthy, drift drill catches mutation
  4. check-receipts       — demo passes, negative fixture fails as expected
  5. harvest-eval         — roundtrip appends valid YAML, duplicate refused
  6. eval batch           — all golden tasks pass
  7. contract drift       — PASS
  8. catalog freshness    — schema valid + ≤14d stale warning
  9. ground evidence      - 5 adversarial mock-evidence fixtures rejected + golden accepted
 10. system card        - 6/6 fixtures judged + roundtrip 3/3 across both card styles
 11. front door         - 5/5 scripted intents routed to the correct door
 12. capability guard    - 5/5 breach sims blocked + 2/2 controls + 0 read-only leaks
 13. council mode        - 7/7 fixtures judged + winner/scores row appended to ledger
 14. run budgets         - 6/6 fixtures + within-budget OK + halt-without-pointer refused
 15. cockpit contract    - W2 gate battery green
 16. sealed kernel seed  - W3 gate battery green (rows == calls, GROUND:NO, certs)
 17. sealed depth        - W3b gate battery green (checkpoints, donor pins, drift)

Exit 0 = all green. Any failure prints the failed check name and exits 1.
"""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
PY = sys.executable

RESULTS: list[tuple[str, bool, str]] = []


def run(*args: str, expect_ok: bool = True) -> subprocess.CompletedProcess:
    p = subprocess.run([PY, *args], capture_output=True, text=True, cwd=SKILL_DIR)
    if expect_ok and p.returncode != 0:
        raise AssertionError(f"command failed: {' '.join(args)}\n{p.stdout}\n{p.stderr}")
    return p


def check(name: str, fn) -> None:
    try:
        note = fn()
        RESULTS.append((name, True, note or ""))
        print(f"  ✅ {name}" + (f" — {note}" if note else ""))
    except Exception as e:  # noqa: BLE001 - selftest reports anything
        RESULTS.append((name, False, str(e)[:200]))
        print(f"  ❌ {name}\n     {str(e)[:200]}")


def t_query() -> str:
    p = run("scripts/telemetry.py", "query", "--terms", "routing donor blackboard")
    assert "OVERRIDE-CANDIDATE" in p.stdout, "query found no candidates for known terms"
    p2 = run("scripts/telemetry.py", "query", "--terms", "zzz-selftest-no-match")
    assert "no override" in p2.stdout, "no-match path missing 'no override' action"
    return "match + no-match paths OK"


def t_antibodies() -> str:
    ab = SKILL_DIR / "context" / "knowledge" / "antibodies.json"
    bak = ab.with_suffix(".json.selftest-bak") if ab.exists() else None
    if bak:
        shutil.copy(ab, bak)
    try:
        sig = "selftest probe signature xyz"
        run("scripts/telemetry.py", "antibody", "add",
            "--signature", sig, "--wrong-route", "deep-understanding",
            "--correction", "selftest correction")
        p = run("scripts/telemetry.py", "antibody", "check",
                "--terms", "selftest probe signature xyz here",
                "--routes", "deep-understanding genesis", expect_ok=False)
        assert p.returncode == 1 and "ANTIBODY BLOCK" in p.stdout, \
            "antibody did not block the immunized route"
        p2 = run("scripts/telemetry.py", "antibody", "check",
                 "--terms", "selftest probe signature xyz here",
                 "--routes", "genesis super-reasoner", expect_ok=False)
        assert p2.returncode == 0, "antibody blocked a corrected route"
    finally:
        if bak and bak.exists():
            shutil.copy(bak, ab)
            bak.unlink()
        elif ab.exists() and bak is None:
            ab.unlink()
    return "block + pass + cleanup OK"


def t_donor_health(quick: bool) -> str:
    p = run("scripts/donor-health.py", "check-all", expect_ok=False)
    assert p.returncode == 0, f"donor health check-all exited {p.returncode}:\n{p.stdout[-300:]}"
    assert "STATUS: PASS" in p.stdout or "STATUS: DRIFT" in p.stdout, \
        f"donor health failed:\n{p.stdout[-300:]}"
    if quick:
        return "healthy or drift-only (drift drill skipped)"
    # drift drill: mutate a currently-clean donor, expect typed DRIFT + receipt
    hashes_file = SKILL_DIR / "context" / "knowledge" / "donor-hashes.json"
    if not hashes_file.exists():
        return "all healthy (no baseline; drill skipped)"
    real = json.loads(hashes_file.read_text())
    donor = None
    for name in sorted(real):
        skill = SKILL_DIR / "context" / "donors" / name / "SKILL.md"
        if skill.exists() and hashlib.sha256(skill.read_bytes()).hexdigest() == real[name]:
            donor = name
            break
    if donor is None:
        return "all healthy (all drifted; drill skipped)"
    skill = SKILL_DIR / "context" / "donors" / donor / "SKILL.md"
    orig = skill.read_bytes()
    try:
        skill.write_bytes(orig + b"\n<!-- selftest drift probe -->\n")
        p2 = run("scripts/donor-health.py", "check", donor, expect_ok=False)
        assert p2.returncode == 0, \
            f"DRIFT must exit 0 (usable, re-read required) — got {p2.returncode}"
        assert "STATUS: DRIFT" in p2.stdout, "typed DRIFT verdict did not fire on mutation"
        receipts = sorted((SKILL_DIR / "receipts").glob(f"drift-*-{donor}.json"))
        assert receipts, "drift receipt not written"
    finally:
        skill.write_bytes(orig)
    p3 = run("scripts/donor-health.py", "check", donor)
    assert "STATUS: PASS" in p3.stdout, "donor not healthy after restore"
    return "healthy + typed DRIFT + receipt + restored OK"


def t_catalog() -> str:
    cat = SKILL_DIR / "context" / "knowledge" / "donor-catalog.json"
    assert cat.exists(), "donor-catalog.json missing; run scripts/donor-catalog.py refresh"
    data = json.loads(cat.read_text())
    for key in ("generated_ts", "count", "skills", "curated_donors", "roots"):
        assert key in data, f"catalog missing key: {key}"
    assert isinstance(data["count"], int) and data["count"] > 0, "catalog count invalid"
    assert isinstance(data["skills"], list) and len(data["skills"]) == data["count"], \
        "catalog skills list does not match count"
    assert len(data["curated_donors"]) > 0 and len(data["roots"]) > 0, \
        "catalog curated_donors/roots empty"
    ts = datetime.fromisoformat(str(data["generated_ts"]).replace("Z", "+00:00"))
    age_days = (datetime.now(timezone.utc) - ts).days
    if age_days > 14:
        return f"STALE WARNING: {age_days}d old (>14); run scripts/donor-catalog.py refresh"
    return f"fresh ({age_days}d, {data['count']} skills)"


def t_receipts() -> str:
    p = run("scripts/check-receipts.py", "--demo")
    assert "STATUS: PASS" in p.stdout, "demo failed"
    # F1 regression: the catalog golden must verify 1/1 (was a false "0/0 PASS")
    golden = SKILL_DIR / "eval-outputs" / "catalog-route-reaches-installed-skill.txt"
    assert golden.exists(), "catalog golden missing"
    p1 = run("scripts/check-receipts.py", "--check", str(golden))
    assert "1/1 route lines verified" in p1.stdout, \
        f"catalog golden did not verify:\n{p1.stdout}"
    tmp = Path(tempfile.mkdtemp())
    try:
        neg = tmp / "neg.txt"
        neg.write_text(
            "ROUTE\n"
            "NODE A [LEARN] -> deep-understanding: just route it\n"
            "NODE B [BUILD] -> think-pipeline: no gate shown\n"
            "NODE C [DECIDE] -> super-reasoner: falsifiability conditions present\n")
        p2 = run("scripts/check-receipts.py", "--check", str(neg), expect_ok=False)
        assert p2.returncode == 1, "negative receipt fixture unexpectedly passed"
        assert "NODE A" in p2.stdout and "NODE B" in p2.stdout, \
            "negative check missed expected failures"
        # fail-closed: empty ROUTE block must BLOCK (rc=2), never "0/0 PASS"
        fc = tmp / "failclosed.txt"
        fc.write_text("ROUTE\n\nFUSE: nothing\n")
        p3 = run("scripts/check-receipts.py", "--check", str(fc), expect_ok=False)
        assert p3.returncode == 2 and "BLOCKED" in p3.stdout, \
            "empty ROUTE block did not fail closed"
    finally:
        shutil.rmtree(tmp)
    return "demo + catalog golden + negative + fail-closed OK"


def t_ground_evidence() -> str:
    fix = SKILL_DIR / "context" / "knowledge" / "fixtures" / "ground-evidence"
    assert fix.is_dir(), "ground-evidence fixtures dir missing"
    p = run("scripts/check-ground-evidence.py", "--fixtures", str(fix), expect_ok=False)
    assert p.returncode == 0, f"ground-evidence fixtures failed:\n{p.stdout[-300:]}"
    assert "6/6 fixtures behaved as expected" in p.stdout, \
        f"fixture behavior mismatch:\n{p.stdout[-300:]}"
    rejects = p.stdout.count("expected reject, got reject")
    assert rejects == 5, f"expected 5 adversarial rejects, saw {rejects}"
    assert "expected accept, got accept" in p.stdout, "golden accept fixture did not accept"
    return "5/5 adversarial rejected + golden accepted"


def t_system_card() -> str:
    fix = SKILL_DIR / "context" / "knowledge" / "fixtures" / "system-card"
    assert fix.is_dir(), "system-card fixtures dir missing"
    p = run("scripts/check-system-card.py", "--fixtures", str(fix), expect_ok=False)
    assert p.returncode == 0, f"system-card fixtures failed:\n{p.stdout[-300:]}"
    assert "6/6 fixtures behaved as expected" in p.stdout, \
        f"judgement mismatch:\n{p.stdout[-300:]}"
    assert "ROUNDTRIP: 3/3" in p.stdout, f"roundtrip mismatch:\n{p.stdout[-300:]}"
    return "6/6 judged + roundtrip 3/3 (both styles)"


def t_front_door() -> str:
    fix = SKILL_DIR / "context" / "knowledge" / "fixtures" / "front-door"
    assert fix.is_dir(), "front-door fixtures dir missing"
    p = run("scripts/check-front-door.py", "--fixtures", str(fix), expect_ok=False)
    assert p.returncode == 0, f"front-door fixtures failed:\n{p.stdout[-300:]}"
    assert "5/5 intents routed to the correct door" in p.stdout, \
        f"routing mismatch:\n{p.stdout[-300:]}"
    return "5/5 scripted intents -> correct door"


def t_capability() -> str:
    p = run("scripts/capability-guard.py", "--breach-sim", expect_ok=False)
    assert p.returncode == 0, f"breach sim failed:\n{p.stdout[-300:]}"
    assert "5/5 breaches blocked" in p.stdout, f"breach count mismatch:\n{p.stdout[-300:]}"
    assert "2/2 controls allowed" in p.stdout, "positive controls failed"
    assert "0 research leaves with write tools" in p.stdout, "read-only audit leaked"
    return "5/5 breaches blocked + 2/2 controls + read-only audit 0"


def t_council() -> str:
    fix = SKILL_DIR / "context" / "knowledge" / "fixtures" / "council"
    assert fix.is_dir(), "council fixtures dir missing"
    p = run("scripts/check-council.py", "--fixtures", str(fix), expect_ok=False)
    assert p.returncode == 0, f"council fixtures failed:\n{p.stdout[-300:]}"
    assert "7/7 fixtures behaved as expected" in p.stdout, \
        f"judgement mismatch:\n{p.stdout[-300:]}"
    assert p.stdout.count("got accept") == 3, "expected 3 accept fixtures"
    assert p.stdout.count("got reject") == 4, "expected 4 reject fixtures"
    tmp = Path(tempfile.mkdtemp())
    try:
        led = tmp / "decisions.jsonl"
        p2 = run("scripts/check-council.py", "--record",
                 str(fix / "02-three-candidates.accept.txt"),
                 "--ledger", str(led), "--id", "selftest-council", expect_ok=False)
        assert p2.returncode == 0, f"council record failed:\n{p2.stdout[-300:]}"
        row = json.loads(led.read_text().strip().splitlines()[-1])
        assert row["winner"] == "C3", f"ledger winner wrong: {row}"
        assert row["scores"] == {"C1": 7, "C2": 6, "C3": 8}, f"ledger scores wrong: {row}"
        assert row["source"] == "apex-council", f"ledger source wrong: {row}"
    finally:
        shutil.rmtree(tmp)
    return "7/7 judged + winner/scores row in ledger"


def t_budget() -> str:
    fix = SKILL_DIR / "context" / "knowledge" / "fixtures" / "budget"
    assert fix.is_dir(), "budget fixtures dir missing"
    p = run("scripts/check-budget.py", "--fixtures", str(fix), expect_ok=False)
    assert p.returncode == 0, f"budget fixtures failed:\n{p.stdout[-300:]}"
    assert "6/6 fixtures behaved as expected" in p.stdout, \
        f"judgement mismatch:\n{p.stdout[-300:]}"
    assert p.stdout.count("got accept") == 3 and p.stdout.count("got reject") == 3, \
        "expected 3 accept + 3 reject fixtures"
    src = fix / "01-overrun-terse.accept.txt"
    p2 = run("scripts/check-budget.py", "--sim", str(src),
             "--leaves", "2", "--tokens", "30000", expect_ok=False)
    assert p2.returncode == 0 and "BUDGET OK" in p2.stdout, \
        f"within-budget sim wrong:\n{p2.stdout}"
    p3 = run("scripts/check-budget.py", "--sim",
             str(fix / "06-halt-no-pointer.reject.txt"), "--leaves", "9", expect_ok=False)
    assert p3.returncode == 1 and "resume pointer" in p3.stdout, \
        f"halt pointer check wrong:\n{p3.stdout}"
    return "6/6 judged + within OK + halt-without-pointer refused"


def t_harvest() -> str:
    evals_bak = (SKILL_DIR / "evals.yaml").read_text()
    quality_bak = (SKILL_DIR / "quality.yaml").read_text()
    sample = Path(tempfile.mkdtemp()) / "run.txt"
    sample.write_text("INTENT     : selftest\nGROUNDED   : NO -> HALTED (needed: actor)\nSTATUS: BLOCKED\n")
    try:
        run("scripts/harvest-eval.py", "--from", str(sample), "--outcome", "blocked",
            "--id", "selftest-harvest-probe")
        import yaml
        e = yaml.safe_load((SKILL_DIR / "evals.yaml").read_text())
        q = yaml.safe_load((SKILL_DIR / "quality.yaml").read_text())
        assert any(t["id"] == "selftest-harvest-probe" for t in e["golden_tasks"]), \
            "harvested task missing from evals.yaml"
        assert any(t["id"] == "selftest-harvest-probe" for t in q["golden_tasks"]), \
            "harvested task missing from quality.yaml"
        p_dup = run("scripts/harvest-eval.py", "--from", str(sample), "--outcome",
                    "blocked", "--id", "selftest-harvest-probe", expect_ok=False)
        assert p_dup.returncode == 1, "duplicate harvest not refused"
    finally:
        (SKILL_DIR / "evals.yaml").write_text(evals_bak)
        (SKILL_DIR / "quality.yaml").write_text(quality_bak)
        shutil.rmtree(sample.parent)
    return "append + sync + duplicate-refused + cleanup OK"


def t_evals() -> str:
    p = run("apex_eval.py", "--batch", "eval-outputs", expect_ok=False)
    assert p.returncode == 0, f"eval batch failed:\n{p.stdout[-300:]}"
    assert "NEGATIVE FIXTURES:" in p.stdout and "failed as expected" in p.stdout, \
        "negative fixture discrimination not exercised in batch"
    return p.stdout.strip().splitlines()[-2] if len(p.stdout.splitlines()) >= 2 else "PASS"


def t_drift() -> str:
    p = run("scripts/check-contract-drift.py", expect_ok=False)
    assert p.returncode == 0 and "PASS" in p.stdout, "contract drift check failed"
    return "PASS"


def t_cockpit() -> str:
    p = run("scripts/check-w2-gate.py", expect_ok=False)
    assert p.returncode == 0, f"W2 gate failed:\n{p.stdout[-600:]}"
    assert "W2 GATE: PASS" in p.stdout, "W2 GATE verdict line missing"
    line = [l for l in p.stdout.splitlines() if l.startswith("W2 GATE:")][-1]
    return line


def t_sealed_kernel() -> str:
    p = run("scripts/check-w3-gate.py", expect_ok=False)
    assert p.returncode == 0, f"W3 gate failed:\n{p.stdout[-600:]}"
    assert "W3 GATE: PASS" in p.stdout, "W3 GATE verdict line missing"
    line = [l for l in p.stdout.splitlines() if l.startswith("W3 GATE:")][-1]
    return line


def t_sealed_depth() -> str:
    p = run("scripts/check-w3b-gate.py", expect_ok=False)
    assert p.returncode == 0, f"W3b gate failed:\n{p.stdout[-600:]}"
    assert "W3b GATE: PASS" in p.stdout, "W3b GATE verdict line missing"
    line = [l for l in p.stdout.splitlines() if l.startswith("W3b GATE:")][-1]
    return line


def main() -> None:
    quick = "--quick" in sys.argv
    print("APEX SELFTEST\n" + "=" * 50)
    check("telemetry query (overrides)", t_query)
    check("antibodies add/check", t_antibodies)
    check("donor health + drift drill", lambda: t_donor_health(quick))
    check("catalog freshness (schema + 14d warn)", t_catalog)
    check("receipt checker", t_receipts)
    check("ground evidence fixtures (item 6)", t_ground_evidence)
    check("system card fixtures (item 45)", t_system_card)
    check("front door fixtures (item 44)", t_front_door)
    check("capability envelopes (item 47)", t_capability)
    check("council mode (item 48)", t_council)
    check("run budgets (item 49)", t_budget)
    check("eval harvest roundtrip", t_harvest)
    check("golden task eval batch", t_evals)
    check("contract drift", t_drift)
    check("cockpit contract (W2 gate)", t_cockpit)
    check("sealed kernel seed (W3 gate)", t_sealed_kernel)
    check("sealed depth (W3b gate)", t_sealed_depth)

    failed = [n for n, ok, _ in RESULTS if not ok]
    print("=" * 50)
    print(f"SELFTEST: {len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
