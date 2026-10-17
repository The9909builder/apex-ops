#!/usr/bin/env python3
"""
W3 gate battery: the deterministic acceptance check for the seeded kernel
(items 8-12), hermetic (tmp ledgers only, never ~/.apex/ledger) and offline.

    1  sealed pipeline smoke: one full run, ledger rows == typed calls (19 == 19)
    2  malformed input raises SealError 7/7 stages (wrapper + kernel InputRejected)
    3  GROUND:NO on 10 fresh fixtures -> zero downstream ledger rows, plus the
       kernel-invariant bypass refusal (layer 2)
    4  revocation continuity: revoke, reboot on the same ledger, the revocation
       is restored and the capability is refused
    5  route certs: 100% certified after a smoke run; a forged pass (no gate
       evidence) is BLOCKED, and a hand-forged EXECUTED route row (cert_hash
       None) is caught by verify-routes (exit 1)
    6  W1 + W2 gate scripts still green (no regression by the W3 seed)

Prints one line per sub-check then `W3 GATE: PASS n/n`; exit 0 only if all pass.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent


def load_apex_kernel():
    spec = importlib.util.spec_from_file_location("apex_kernel", HERE / "apex-kernel.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AK = load_apex_kernel()

from sealed_substrate.kernel.primitives import content_hash_of  # noqa: E402
from sealed_substrate.kernel.types import CallVerdict  # noqa: E402


def fresh_root(tag: str) -> Path:
    return Path(tempfile.mkdtemp(prefix=f"apex-w3-{tag}-"))


def three_donors() -> list:
    allow = sorted(AK.default_allowlist())
    if not allow:
        raise AssertionError("context/donors allowlist is empty")
    return allow[:3]


def routes_for(donors: list) -> list:
    return [{
        "node_id": f"leaf-{i}", "node_type": "BUILD", "donor": donor,
        "envelope": "read-only",
        "gate_evidence": f"gate: w3 battery route {i}, donor skill file observed",
    } for i, donor in enumerate(donors)]


def check_1_sealed_pipeline(results: list) -> None:
    root = fresh_root("pipe")
    kernel, contracts, _ = AK.boot_kernel(root / "apex.jsonl", root / "kernel.key")
    now = int(time.time())
    summary = AK.run_pipeline(kernel, contracts, run_id="w3-gate", now=now,
                              deadline=now + 86400, routes=routes_for(three_donors()))
    kernel.ledger.close()
    expected = 7 + 6 + 2 * len(summary["donors"])  # mints + stage records + (attenuate, seal)
    ok = summary["ops"] == summary["rows"] == expected
    results.append(("1/6 sealed pipeline", ok,
                    f"calls={summary['ops']} rows={summary['rows']} expected={expected}"))
    return root


def check_2_malformed(results: list) -> None:
    root = fresh_root("malformed")
    kernel, contracts, _ = AK.boot_kernel(root / "apex.jsonl", root / "kernel.key")
    now = int(time.time())
    run = AK.ApexRun(kernel, contracts, run_id="malformed", now=now, deadline=now + 86400)
    run.open()
    stages = ("DECODE", "GROUND", "DECOMPOSE", "ROUTE", "FUSE", "PLAN", "CLOSE")
    passed = 0
    for stage in stages:
        cap_key = "DONOR_ROUTE" if stage == "ROUTE" else stage
        target = contracts[cap_key].id
        result = kernel.seal(AK.Call(capability=run._stage_caps[cap_key], target=target,
                                     raw_input={"garbage": 1}, now=now))
        kernel_rejected = (
            isinstance(result, AK.Err) and isinstance(result.error, AK.E.InputRejected))
        try:
            AK.validate_stage(stage, {"garbage": 1})
            wrapper_rejected = False
        except AK.SealError:
            wrapper_rejected = True
        if kernel_rejected and wrapper_rejected:
            passed += 1
    kernel.ledger.close()
    results.append(("2/6 malformed SealError", passed == 7, f"{passed}/7 stages"))


def check_3_ground_no(results: list) -> None:
    passed = 0
    bypass_ok = False
    now = int(time.time())
    for i in range(10):
        root = fresh_root(f"groundno-{i}")
        kernel, contracts, _ = AK.boot_kernel(root / "apex.jsonl", root / "kernel.key")
        stage = rows = None
        try:
            AK.run_pipeline(kernel, contracts, run_id=f"no-{i}", now=now + i,
                            deadline=now + i + 86400,
                            routes=routes_for(three_donors()[:1]), ground="NO")
        except AK.SealError as exc:
            stage = exc.stage
            rows = len(kernel.ledger)
        if stage == "DECOMPOSE" and rows == 9:  # 7 mints + DECODE + GROUND, zero downstream
            passed += 1
        if i == 0:  # layer 2: a direct seal() below a NO verdict is refused by the kernel
            run = AK.ApexRun(kernel, contracts, run_id="no-bypass", now=now,
                             deadline=now + 86400)
            run.open()
            raw = AK.DonorRouteInput(
                node_id="x", node_type="BUILD", donor=three_donors()[0],
                gate_evidence="gate: observed", envelope="read-only", ground_verdict="NO",
                donor_hash=AK.donor_skill_hash(three_donors()[0]))
            result = kernel.seal(AK.Call(
                capability=run._stage_caps["DONOR_ROUTE"],
                target=contracts["DONOR_ROUTE"].id, raw_input=raw, now=now))
            bypass_ok = (
                isinstance(result, AK.Err)
                and isinstance(result.error, AK.E.InvariantViolated))
        kernel.ledger.close()
    ok = passed == 10 and bypass_ok
    results.append(("3/6 GROUND:NO x10", ok,
                    f"{passed}/10 zero-downstream, kernel bypass refused={bypass_ok}"))


def check_4_revocation(results: list) -> None:
    root = fresh_root("revoke")
    ledger, key = root / "apex.jsonl", root / "kernel.key"
    now = int(time.time())
    kernel, contracts, _ = AK.boot_kernel(ledger, key)
    run = AK.ApexRun(kernel, contracts, run_id="revoke", now=now, deadline=now + 86400)
    run.open()
    doomed = run._stage_caps["CLOSE"]
    revoked = kernel.revoke(doomed, now=now)
    kernel.ledger.close()
    assert isinstance(revoked, AK.Ok), "revoke was itself refused"
    kernel2, contracts2, restored = AK.boot_kernel(ledger, key)
    close_block = AK.CloseBlock(gates_fired=[], skipped=[], blackboard="x",
                                handoffs=[], status="DONE", ground_verdict="YES")
    result = kernel2.seal(AK.Call(capability=doomed, target=contracts2["CLOSE"].id,
                                  raw_input=close_block, now=now + 1))
    kernel2.ledger.close()
    refused = (isinstance(result, AK.Err)
               and isinstance(result.error, AK.E.CapabilityRevoked))
    ok = restored >= 1 and refused
    results.append(("4/6 revocation continuity", ok,
                    f"restored={restored} refused={refused}"))


def check_5_certs_and_forgery(results: list) -> None:
    root = fresh_root("certs")
    ledger, key = root / "apex.jsonl", root / "kernel.key"
    now = int(time.time())
    kernel, contracts, _ = AK.boot_kernel(ledger, key)
    AK.run_pipeline(kernel, contracts, run_id="certs", now=now, deadline=now + 86400,
                    routes=routes_for(three_donors()))
    reported = AK.verify_routes(ledger)
    certified_ok = (reported["status"] == "ok" and reported["forged"] == 0
                    and reported["certified"] == reported["total"] == 3)

    run = AK.ApexRun(kernel, contracts, run_id="certs2", now=now, deadline=now + 86400)
    run.open()
    run.seal_stage("DECODE", AK.SystemCard(
        intent="second run", mode="EXECUTION", risk=1, root_type="BUILD",
        assumptions=["battery"]))
    run.seal_stage("GROUND", AK.GroundVerdict(
        verdict="YES", actor="battery", cost="one seal", evidence="fixture",
        crux="cert check"))
    try:
        run.invoke_donor(node_id="forged", node_type="BUILD", donor=three_donors()[0],
                         gate_evidence="just trust me", envelope="read-only")
        gate_refused = False
    except AK.SealError as exc:
        gate_refused = isinstance(exc.error, AK.E.GateBlocked)

    forged_target = contracts["DONOR_ROUTE"].id
    kernel.ledger.append_deriving_call_id(
        ts=now,
        derive_call_id=lambda prev: hashlib.sha256(prev + b"forged").digest(),
        caller_cap_hash=run._stage_caps["DONOR_ROUTE"].safe_content_hash(),
        target=forged_target, args_hash=content_hash_of({"op": "forged"}),
        cert_hash=None, verdict=CallVerdict.EXECUTED, result_hash=None)
    tampered = AK.verify_routes(ledger)
    caught = tampered["status"] == "forged" and tampered["forged"] == 1
    with contextlib.redirect_stdout(io.StringIO()):
        cli_exit = AK.cmd_verify_routes(SimpleNamespace(ledger=str(ledger)))
    kernel.ledger.close()
    ok = certified_ok and gate_refused and caught and cli_exit == 1
    results.append(("5/6 certs 100% + forged blocked", ok,
                    f"certified={reported['certified']}/{reported['total']} "
                    f"gate_refused={gate_refused} forged_caught={caught} "
                    f"cli_exit={cli_exit}"))


def check_6_w1_w2(results: list) -> None:
    outcomes = {}
    for name in ("check-w1-gate.py", "check-w2-gate.py"):
        proc = subprocess.run([sys.executable, str(HERE / name)],
                              capture_output=True, text=True)
        outcomes[name] = proc.returncode
    ok = all(code == 0 for code in outcomes.values())
    detail = " ".join(f"{n.split('-')[1]}={code}" for n, code in outcomes.items())
    results.append(("6/6 W1+W2 gates", ok, detail))


def main() -> int:
    results = []
    check_1_sealed_pipeline(results)
    check_2_malformed(results)
    check_3_ground_no(results)
    check_4_revocation(results)
    check_5_certs_and_forgery(results)
    check_6_w1_w2(results)
    passed = sum(1 for _, ok, _ in results if ok)
    for label, ok, detail in results:
        print(f"W3 GATE {label}: {'PASS' if ok else 'FAIL'} {detail}")
    total = len(results)
    print(f"W3 GATE: {'PASS' if passed == total else 'FAIL'} {passed}/{total}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
