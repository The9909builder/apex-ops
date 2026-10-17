#!/usr/bin/env python3
"""
W3b gate battery: deterministic acceptance for the sealed-depth tranche
(checkpointed ledger + item 14 donor pinning), hermetic (tmp ledgers only, never
~/.apex/ledger) and offline.

    1  checkpointed boot: 260 appends commit a signed checkpoint; reopen with the
       key verifies it; a log truncated BELOW the committed checkpoint refuses to
       boot (LedgerLoadError, fail-closed), and a sidecar without a key refuses too
    2  donor pins: one pin per sealed route, each bound to the exact ledger row
       (row_hash = sha256 of the raw line, result_hash matched); verify_pins OK
    3  donor drift in one run: a mutated donor SKILL.md after routing turns
       verify_pins into DRIFT and writes a pin-drift receipt
    4  broken binding: a pin claiming a row the ledger does not hold is FAIL and
       the verify-pins CLI exits 1
    5  unpinnable donor: a route to a donor with no SKILL.md is refused BEFORE any
       kernel call — zero route rows, ops side unchanged
    6  W3 gate (which re-runs W1+W2) still green (no regression by W3b)

Prints one line per sub-check then `W3b GATE: PASS n/n`; exit 0 only if all pass.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
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

from sealed_substrate.kernel.persistent_ledger import LedgerLoadError  # noqa: E402
from sealed_substrate.kernel.types import CallVerdict  # noqa: E402

CHECKPOINT_INTERVAL = 256


def fresh_root(tag: str) -> Path:
    return Path(tempfile.mkdtemp(prefix=f"apex-w3b-{tag}-"))


def three_donors() -> list:
    allow = sorted(AK.default_allowlist())
    if not allow:
        raise AssertionError("context/donors allowlist is empty")
    return allow[:3]


def routes_for(donors: list) -> list:
    return [{
        "node_id": f"leaf-{i}", "node_type": "BUILD", "donor": donor,
        "envelope": "read-only",
        "gate_evidence": f"gate: w3b battery route {i}, donor skill file observed",
    } for i, donor in enumerate(donors)]


def append_rows(kernel, contracts, n: int, offset: int = 0) -> None:
    caller = hashlib.sha256(b"w3b-caller").digest()
    for i in range(offset, offset + n):
        kernel.ledger.append_deriving_call_id(
            ts=1000 + i,
            derive_call_id=(lambda prev, i=i:
                            hashlib.sha256(prev + b"w3b" + str(i).encode()).digest()),
            caller_cap_hash=caller, target=contracts["DONOR_ROUTE"].id,
            args_hash=hashlib.sha256(str(i).encode()).digest(),
            cert_hash=None, verdict=CallVerdict.EXECUTED, result_hash=None)


def check_1_checkpoints(results: list) -> None:
    root = fresh_root("cp")
    ledger, key = root / "apex.jsonl", root / "kernel.key"
    kernel, contracts, _ = AK.boot_kernel(ledger, key)
    append_rows(kernel, contracts, CHECKPOINT_INTERVAL + 4)
    kernel.ledger.close()
    sidecar = ledger.with_name(ledger.name + ".checkpoints")
    sidecar_ok = sidecar.exists() and len(sidecar.read_text().splitlines()) == 1

    kernel2, _contracts2, _ = AK.boot_kernel(ledger, key)  # signed checkpoint verifies
    reopened = len(kernel2.ledger) == CHECKPOINT_INTERVAL + 4
    kernel2.ledger.close()

    trunc_root = fresh_root("trunc")
    trunc_ledger = trunc_root / "apex.jsonl"
    lines = ledger.read_bytes().split(b"\n")
    trunc_ledger.write_bytes(b"\n".join(lines[:CHECKPOINT_INTERVAL - 6]) + b"\n")
    (trunc_root / "apex.jsonl.checkpoints").write_bytes(sidecar.read_bytes())
    try:
        AK.boot_kernel(trunc_ledger, key)
        trunc_refused = False
    except LedgerLoadError:
        trunc_refused = True

    try:
        AK.CheckpointedPersistentLedger(ledger)  # sidecar present, no key
        nokey_refused = False
    except LedgerLoadError:
        nokey_refused = True

    ok = sidecar_ok and reopened and trunc_refused and nokey_refused
    results.append(("1/6 checkpointed boot", ok,
                    f"sidecar={sidecar_ok} reopened={reopened} "
                    f"truncation_refused={trunc_refused} nokey_refused={nokey_refused}"))


def check_2_pins_bound(results: list) -> None:
    root = fresh_root("pins")
    ledger, key = root / "apex.jsonl", root / "kernel.key"
    pins = root / "apex.pins.jsonl"
    now = int(time.time())
    kernel, contracts, _ = AK.boot_kernel(ledger, key)
    summary = AK.run_pipeline(kernel, contracts, run_id="w3b-pins", now=now,
                              deadline=now + 86400, routes=routes_for(three_donors()),
                              pins_path=pins)
    kernel.ledger.close()
    lines = [ln for ln in pins.read_text().splitlines() if ln.strip()]
    reported = AK.verify_pins(pins, ledger_path=ledger)
    ok = (summary["pins"] == 3 and len(lines) == 3
          and reported["status"] == "ok" and reported["bound"] == 3
          and reported["drift"] == 0 and reported["failed"] == 0
          and reported["receipts"] == [])
    results.append(("2/6 donor pins bound", ok,
                    f"pins={summary['pins']} bound={reported['bound']} "
                    f"status={reported['status']}"))


def check_3_drift_receipt(results: list) -> None:
    root = fresh_root("drift")
    donors = root / "donors"
    (donors / "fixture-donor").mkdir(parents=True)
    skill_md = donors / "fixture-donor" / "SKILL.md"
    skill_md.write_text("# fixture donor v1\n")
    ledger, key = root / "apex.jsonl", root / "kernel.key"
    pins = root / "apex.pins.jsonl"
    receipts = root / "receipts"
    now = 1000
    kernel, contracts, _ = AK.boot_kernel(ledger, key, allowlist={"fixture-donor"})
    AK.run_pipeline(kernel, contracts, run_id="w3b-drift", now=now,
                    deadline=now + 86400,
                    routes=[{"node_id": "n1", "node_type": "BUILD",
                             "donor": "fixture-donor", "envelope": "read-only",
                             "gate_evidence": "gate: fixture donor observed"}],
                    pins_path=pins, donors_dir=donors)
    kernel.ledger.close()
    clean = AK.verify_pins(pins, ledger_path=ledger, donors_dir=donors)
    skill_md.write_text("# fixture donor v2 (mutated after routing)\n")
    drifted = AK.verify_pins(pins, ledger_path=ledger, donors_dir=donors,
                             receipts_dir=receipts, now=now + 60)
    receipt = (receipts / drifted["receipts"][0]) if drifted["receipts"] else None
    receipt_ok = bool(receipt and receipt.exists()
                      and json.loads(receipt.read_text())["kind"] == "pin-drift")
    with contextlib.redirect_stdout(io.StringIO()):
        cli_exit = AK.cmd_verify_pins(SimpleNamespace(
            pins=str(pins), ledger=str(ledger), donors_dir=str(donors),
            receipts_dir=str(receipts), now=str(now + 60)))
    ok = (clean["status"] == "ok" and drifted["status"] == "drift"
          and drifted["drift"] == 1 and drifted["failed"] == 0
          and receipt_ok and cli_exit == 0)
    results.append(("3/6 drift -> receipt", ok,
                    f"clean={clean['status']} drifted={drifted['status']} "
                    f"receipt={receipt_ok} cli_exit={cli_exit}"))


def check_4_broken_binding(results: list) -> None:
    root = fresh_root("broken")
    ledger, key = root / "apex.jsonl", root / "kernel.key"
    kernel, contracts, _ = AK.boot_kernel(ledger, key)
    append_rows(kernel, contracts, 1)
    kernel.ledger.close()
    pins = root / "apex.pins.jsonl"
    pins.write_text(json.dumps({
        "ts": 1, "node_id": "forged", "donor": "ghost",
        "donor_hash": "ab" * 32, "result_hash": "cd" * 32, "row_hash": "ef" * 32,
        "length": 1,
    }) + "\n")
    reported = AK.verify_pins(pins, ledger_path=ledger)
    with contextlib.redirect_stdout(io.StringIO()):
        cli_exit = AK.cmd_verify_pins(SimpleNamespace(
            pins=str(pins), ledger=str(ledger), donors_dir=None,
            receipts_dir=str(root / "receipts"), now=None))
    ok = (reported["status"] == "failed" and reported["failed"] == 1
          and reported["bound"] == 0 and cli_exit == 1)
    results.append(("4/6 broken binding FAIL", ok,
                    f"status={reported['status']} failed={reported['failed']} "
                    f"cli_exit={cli_exit}"))


def check_5_unpinnable_donor(results: list) -> None:
    root = fresh_root("ghost")
    donors = root / "donors"  # empty: ghost-donor has no SKILL.md
    donors.mkdir()
    ledger, key = root / "apex.jsonl", root / "kernel.key"
    now = 2000
    kernel, contracts, _ = AK.boot_kernel(ledger, key, allowlist={"ghost-donor"})
    try:
        AK.run_pipeline(kernel, contracts, run_id="w3b-ghost", now=now,
                        deadline=now + 86400,
                        routes=[{"node_id": "n1", "node_type": "BUILD",
                                 "donor": "ghost-donor", "envelope": "read-only",
                                 "gate_evidence": "gate: ghost observed"}],
                        pins_path=root / "apex.pins.jsonl", donors_dir=donors)
        refused = False
        input_rejected = False
    except AK.SealError as exc:
        refused = True
        input_rejected = isinstance(exc.error, AK.E.InputRejected)
    routes = AK.verify_routes(ledger)
    zero_route_rows = routes["total"] == 0 and routes["forged"] == 0
    pin_file_absent = not (root / "apex.pins.jsonl").exists()
    kernel.ledger.close()
    ok = refused and input_rejected and zero_route_rows and pin_file_absent
    results.append(("5/6 unpinnable donor refused", ok,
                    f"refused={refused} input_rejected={input_rejected} "
                    f"zero_route_rows={zero_route_rows} pins_absent={pin_file_absent}"))


def check_6_w3_gate(results: list) -> None:
    proc = subprocess.run([sys.executable, str(HERE / "check-w3-gate.py")],
                          capture_output=True, text=True)
    ok = proc.returncode == 0 and "W3 GATE: PASS 6/6" in proc.stdout
    results.append(("6/6 W3 gate (incl. W1+W2)", ok, f"exit={proc.returncode}"))


def main() -> int:
    results = []
    check_1_checkpoints(results)
    check_2_pins_bound(results)
    check_3_drift_receipt(results)
    check_4_broken_binding(results)
    check_5_unpinnable_donor(results)
    check_6_w3_gate(results)
    passed = sum(1 for _, ok, _ in results if ok)
    for label, ok, detail in results:
        print(f"W3b GATE {label}: {'PASS' if ok else 'FAIL'} {detail}")
    total = len(results)
    print(f"W3b GATE: {'PASS' if passed == total else 'FAIL'} {passed}/{total}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
