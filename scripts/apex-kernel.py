#!/usr/bin/env python3
"""
APEX sealed-kernel seed (W3 items 8-12, W3b sealed depth).

Seeds the sealed_substrate Kernel under APEX so every stage of an APEX run is a
typed, gated, ledgered call:

  item 8  Kernel + CheckpointedPersistentLedger at ~/.apex/ledger/apex.jsonl,
          key at ~/.apex/ledger/kernel.key (0600, never committed), and
          restore_revocations() at boot so a revocation survives a restart.
  item 9  Seven typed stage contracts: SystemCard, GroundVerdict, TreeNode,
          RouteReceipt, FuseReport, WavePlan, CloseBlock. Malformed input
          raises SealError.
  item 10 GROUND precondition: a NO verdict blocks every downstream stage with
          zero downstream ledger rows. Two layers: this wrapper refuses before
          seal(), and the kernel itself carries a registered "ground_yes"
          invariant on every downstream contract (defense in depth).
  item 11 Donor calls run under attenuated capabilities (holder invoke:<donor>,
          ttl = run deadline), never the run's own stage capability.
  item 12 ApexRoutingGate: a route row is certified (cert_hash present) or
          BLOCKED. Forged gate evidence is refused; a cert signed with a
          foreign key fails closed inside seal() (CertInvalid).
  W3b-1   Signed checkpoints: the ledger commits an HMAC checkpoint every 256
          appends into <ledger>.checkpoints (substrate checkpoint discipline);
          boot fails closed on a log truncated below a signed commitment.
  W3b-2   Item 14 ContextEnvelope + donor hash pinning: every donor route seals
          the sha256 of the donor's SKILL.md; pins land beside the ledger in
          <ledger>.pins.jsonl bound to the sealed row's result_hash, and
          verify-pins turns a mutated donor into a DRIFT receipt in one run.

The substrate itself stays untouched; this module imports it (system python3;
the substrate venv python cannot see it) and seeds APEX on top.

Commands:
    python3 apex-kernel.py seed          [--ledger P] [--key P]
    python3 apex-kernel.py status        [--ledger P] [--key P]
    python3 apex-kernel.py smoke         [--ledger P] [--key P] [--run-id S] [--now TS] [--out J]
    python3 apex-kernel.py verify-routes [--ledger P]
    python3 apex-kernel.py verify-pins   [--pins P] [--donors-dir D] [--receipts-dir R]

Fail-open defaults: status, verify-routes and verify-pins exit 0 with a terse
"not seeded" / "none" verdict when their store is absent. A contract refusal
exits 1.
"""

import argparse
import hashlib
import importlib.util
import json
import os
import re
import secrets
import sys
import threading
import time
from pathlib import Path
from typing import Literal, Optional

SUBSTRATE_SRC = os.environ.get(
    "APEX_SUBSTRATE_SRC",
    os.path.expanduser("~/prompt-packs/sealed-substrate/src"),
)
if SUBSTRATE_SRC not in sys.path:
    sys.path.insert(0, SUBSTRATE_SRC)

from pydantic import BaseModel, ConfigDict, Field  # noqa: E402
from sealed_substrate.kernel import errors as E  # noqa: E402
from sealed_substrate.kernel.cert import ValidatorVerdict, cert_manifest_binding  # noqa: E402
from sealed_substrate.kernel.checkpoint import (  # noqa: E402
    CheckpointedPersistentLedger,
    checkpoint_key,
)
from sealed_substrate.kernel.primitives import canonical_bytes, content_hash_of  # noqa: E402
from sealed_substrate.kernel.result import Err, Ok  # noqa: E402
from sealed_substrate.kernel.seal import Call, ContractImpl, Kernel  # noqa: E402
from sealed_substrate.kernel.types import (  # noqa: E402
    EvidenceLane,
    Kind,
    RiskClass,
    SemVer,
    TypeSchema,
    Verdict,
    make_contract,
)
from sealed_substrate.gate.certs import emit_cert  # noqa: E402

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
DEFAULT_LEDGER = Path.home() / ".apex" / "ledger" / "apex.jsonl"
DEFAULT_KEY = Path.home() / ".apex" / "ledger" / "kernel.key"


def pins_path_for(ledger_path) -> Path:
    """The pins sidecar lives beside its ledger, mirroring <ledger>.checkpoints —
    so a hermetic tmp ledger keeps every test artifact in its own sandbox."""
    p = Path(ledger_path)
    stem = p.name[:-6] if p.name.endswith(".jsonl") else p.name
    return p.with_name(stem + ".pins.jsonl")


DEFAULT_PINS = pins_path_for(DEFAULT_LEDGER)

NODE_TYPES = ("LEARN", "DECIDE", "GENERATE", "RESEARCH", "BUILD", "SHIP", "LEVERAGE")
STAGE_ORDER = ("DECODE", "GROUND", "DECOMPOSE", "ROUTE", "FUSE", "PLAN", "CLOSE")
DOWNSTREAM_STAGES = ("DECOMPOSE", "ROUTE", "FUSE", "PLAN", "CLOSE")


class SealError(Exception):
    """Raised form of a typed contract refusal.

    `.error` carries the substrate SealError value (InputRejected, GateBlocked,
    CapabilityRevoked, InvariantViolated, ...); `.stage` names the APEX stage that
    refused. This is the exception the item-9 metric names ("malformed input
    raises SealError")."""

    def __init__(self, error, *, stage: Optional[str] = None) -> None:
        self.error = error
        self.stage = stage
        prefix = f"[{stage}] " if stage else ""
        super().__init__(f"{prefix}{error}")


# --------------------------------------------------------------------------
# Seven typed stage contracts (item 9)
# --------------------------------------------------------------------------

class SystemCard(BaseModel):
    model_config = ConfigDict(extra="forbid")
    intent: str
    mode: Literal["EXPLORATION", "HYBRID", "EXECUTION"]
    risk: int = Field(ge=0, le=10)
    root_type: Literal[NODE_TYPES]
    assumptions: list[str] = Field(min_length=1)


class GroundVerdict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    verdict: Literal["YES", "NO"]
    actor: str
    cost: str
    evidence: str
    crux: str


class TreeNode(BaseModel):
    model_config = ConfigDict(extra="forbid")
    node_id: str
    node_type: Literal[NODE_TYPES]
    item: str
    what: str
    deliverable: str
    done: bool
    ground_verdict: str


class RouteReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")
    node_id: str
    donor: str
    gate_line: str
    envelope: Literal["read-only", "write", "exec"]
    ground_verdict: str
    donor_hash: str = Field(pattern=r"^[0-9a-f]{64}$")


class FuseReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    node_id: str
    contradictions_found: int = Field(ge=0)
    resolved: int = Field(ge=0)
    synthesis: str
    ground_verdict: str


class WaveEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    wave: str
    goal: str
    accept: str


class WavePlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    waves: list[WaveEntry] = Field(min_length=1)
    ground_verdict: str


class CloseBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    gates_fired: list[str]
    skipped: list[str]
    blackboard: str
    handoffs: list[str]
    status: Literal["DONE", "DONE_WITH_CONCERNS", "BLOCKED", "NEEDS_CONTEXT"]
    ground_verdict: str


class DonorRouteInput(BaseModel):
    """Input to the gated donor-route call. `ground_verdict` is kernel-checked by the
    registered ground_yes invariant, so even a direct seal() bypass of the wrapper
    cannot execute a route below a NO verdict. `donor_hash` is the ContextEnvelope:
    the sha256 of the donor's SKILL.md as observed at handoff time, so the sealed
    row commits (via args_hash) to the exact donor version that was routed to."""
    model_config = ConfigDict(extra="forbid")
    node_id: str
    node_type: Literal[NODE_TYPES]
    donor: str
    gate_evidence: str
    envelope: Literal["read-only", "write", "exec"]
    ground_verdict: str
    donor_hash: str = Field(pattern=r"^[0-9a-f]{64}$")


# The seven named stage artifact classes, plus the route-request plumbing.
STAGE_MODELS = {
    "DECODE": SystemCard,
    "GROUND": GroundVerdict,
    "DECOMPOSE": TreeNode,
    "ROUTE": RouteReceipt,
    "FUSE": FuseReport,
    "PLAN": WavePlan,
    "CLOSE": CloseBlock,
}
SEALED_STAGE_MODELS = {k: v for k, v in STAGE_MODELS.items() if k != "ROUTE"}
STAGE_MODELS_SIZE = len(STAGE_MODELS)


def validate_stage(stage: str, raw):
    """Parse-don't-validate for stage artifacts. Returns the model instance or raises
    SealError(InputRejected). One entry point shared by the wrapper, the gate battery,
    and any future resume path, so the malformed-input contract has exactly one home."""
    model = STAGE_MODELS.get(stage)
    if model is None:
        raise SealError(E.InputRejected(f"unknown stage {stage!r}"), stage=stage)
    if isinstance(raw, model):
        return raw
    try:
        if isinstance(raw, dict):
            return model.model_validate(raw, strict=True)
        return model.model_validate(raw)
    except Exception as exc:
        raise SealError(E.InputRejected(f"{stage}: {exc}"), stage=stage) from None


def ground_yes(value) -> bool:
    """Kernel-registered invariant on every downstream contract: no descent below a
    non-YES ground verdict, enforced at seal() step 4/6, not only by the wrapper."""
    return getattr(value, "ground_verdict", None) == "YES"


# --------------------------------------------------------------------------
# Contract construction, kernel boot, key management
# --------------------------------------------------------------------------

def _stage_contract(model, invariants: tuple = ()):
    return make_contract(
        kind=Kind.MESSAGE,
        version=SemVer(1, 0, 0),
        risk_class=RiskClass.R0,
        evidence_lane=EvidenceLane.EXPLORATORY,
        input_schema=TypeSchema(model),
        output_schema=TypeSchema(model),
        invariants=invariants,
    )


def make_apex_contracts() -> dict:
    """The 7 registered contracts: 6 stage records (R0) and 1 donor-route surface
    (R1, so the gate fires and the ledger row carries a cert_hash)."""
    contracts = {
        name: _stage_contract(model, ("ground_yes",) if name in DOWNSTREAM_STAGES else ())
        for name, model in SEALED_STAGE_MODELS.items()
    }
    contracts["DONOR_ROUTE"] = make_contract(
        kind=Kind.TOOL,
        version=SemVer(1, 1, 0),  # 1.1.0: donor_hash pinning (item 14)
        risk_class=RiskClass.R1,
        evidence_lane=EvidenceLane.RESEARCH,
        input_schema=TypeSchema(DonorRouteInput),
        output_schema=TypeSchema(RouteReceipt),
        invariants=("ground_yes",),
    )
    return contracts


def _identity_body(parsed, proof):
    return parsed


def _route_body(parsed, proof):
    return RouteReceipt(
        node_id=parsed.node_id,
        donor=parsed.donor,
        gate_line=parsed.gate_evidence,
        envelope=parsed.envelope,
        ground_verdict=parsed.ground_verdict,
        donor_hash=parsed.donor_hash,
    )


def register_apex_contracts(kernel: Kernel) -> dict:
    """Register the ground_yes invariant and the 7 contracts into a kernel."""
    kernel.register_invariant("ground_yes", ground_yes)
    contracts = make_apex_contracts()
    for name, contract in contracts.items():
        body = _route_body if name == "DONOR_ROUTE" else _identity_body
        kernel.register_contract(ContractImpl(contract=contract, body=body))
    return contracts


def ensure_key(key_path: Path) -> bytes:
    """0600 key file, created once with O_EXCL. The key is never printed or logged."""
    if key_path.exists():
        return key_path.read_bytes()
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key = secrets.token_bytes(32)
    fd = os.open(key_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(fd, key)
    finally:
        os.close(fd)
    return key


DONOR_ALLOWLIST_DIR = SKILL_DIR / "context" / "donors"


def default_allowlist() -> frozenset:
    """Curated donor names, read live from context/donors/ (the symlinked donor set).
    No hardcoded donor list: adding a curated donor is adding a link."""
    if DONOR_ALLOWLIST_DIR.is_dir():
        return frozenset(
            p.name for p in DONOR_ALLOWLIST_DIR.iterdir() if (p / "SKILL.md").exists()
        )
    return frozenset()


def donor_skill_hash(donor: str, donors_dir=None) -> Optional[str]:
    """sha256 of a donor's SKILL.md as observed NOW — the ContextEnvelope pin (W3b
    item 14). None when the donor has no SKILL.md the kernel could observe (the
    caller decides whether that refusal is fatal)."""
    base = Path(donors_dir) if donors_dir else DONOR_ALLOWLIST_DIR
    p = base / donor / "SKILL.md"
    if not p.is_file():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _write_pin(pins_path: Path, pin: dict) -> None:
    """Append one canonical pin line, fsync'd — the same byte discipline as the
    checkpoint sidecar (one canonical JSON object per line + record terminator)."""
    pins_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pins_path, "ab") as f:
        f.write(canonical_bytes(pin) + b"\n")
        f.flush()
        os.fsync(f.fileno())


GATE_EVIDENCE_RE = re.compile(r"gate\s*:\s*\S", re.IGNORECASE)


class ApexRoutingGate:
    """GateProvider for donor routes (item 12).

    Certifies a route call only when (a) the donor is in the routing allowlist and
    (b) the gate evidence is mechanical: a "gate: <observed check>" line, not a bare
    assertion. Anything else returns Err(GateBlocked), which seal() records as a
    BLOCKED row with no cert_hash. Because certs are HMAC-signed under the kernel's
    cert key and verify_cert runs inside seal(), a gate that returns a forged or
    mis-bound cert still fails closed (CertInvalid)."""

    def __init__(self, *, cert_key: bytes, allowlist: frozenset) -> None:
        self._cert_key = cert_key
        self._allowlist = frozenset(allowlist)
        self._prev_cert_hash = None
        self._lock = threading.Lock()
        self.emitted = 0

    def certify(self, *, contract, parsed_input, args_hash, now):
        donor = getattr(parsed_input, "donor", "")
        if donor not in self._allowlist:
            return Err(E.GateBlocked(f"donor {donor!r} not in routing allowlist"))
        evidence = getattr(parsed_input, "gate_evidence", "") or ""
        if not GATE_EVIDENCE_RE.search(evidence):
            return Err(E.GateBlocked(
                "forged pass: no gate evidence (expected 'gate: <observed check>')"))
        with self._lock:
            cert = emit_cert(
                cert_key=self._cert_key,
                manifest_hash=cert_manifest_binding(contract.id, args_hash),
                validators=(ValidatorVerdict(validator="apex-routing", verdict=Verdict.PASS),),
                quorum_verdict=Verdict.PASS,
                ap_access=(),
                ap_phenomenal=(),
                now=now,
                prev_cert_hash=self._prev_cert_hash,
            )
            self._prev_cert_hash = cert.content_hash()
            self.emitted += 1
        return Ok(cert)


def boot_kernel(ledger_path=None, key_path=None, allowlist=None):
    """Boot the sealed kernel: key (0600), CheckpointedPersistentLedger (loads and
    re-verifies the chain; signed checkpoints fail closed on a log truncated below a
    committed checkpoint, on tip-tamper and on re-chain), contracts + invariant
    registered, gate installed, revocations restored.
    Returns (kernel, contracts, restored_count)."""
    lp = Path(ledger_path) if ledger_path else DEFAULT_LEDGER
    kp = Path(key_path) if key_path else DEFAULT_KEY
    lp.parent.mkdir(parents=True, exist_ok=True)
    key = ensure_key(kp)
    kernel = Kernel(key)
    kernel.ledger = CheckpointedPersistentLedger(lp, key=checkpoint_key(key))
    contracts = register_apex_contracts(kernel)
    gate = ApexRoutingGate(
        cert_key=kernel.cert_key,
        allowlist=allowlist if allowlist is not None else default_allowlist(),
    )
    kernel.install_gate(gate)
    restored = kernel.restore_revocations()
    return kernel, contracts, restored


# --------------------------------------------------------------------------
# One APEX run as typed, ledgered calls
# --------------------------------------------------------------------------

class ApexRun:
    """A run = a sequence of kernel-mediated ops. Every op increments `ops` so callers
    can assert the item-8 equality: ledger rows == typed calls.

    `now` is the run clock, supplied by the caller (S16: no wall clock in-core);
    `deadline` is the run deadline and becomes the ttl of every capability, stage and
    attenuated alike (item 11)."""

    def __init__(self, kernel: Kernel, contracts: dict, *, run_id: str,
                 now: int, deadline: int, pins_path=None, donors_dir=None) -> None:
        self.kernel = kernel
        self.contracts = contracts
        self.run_id = run_id
        self.now = int(now)
        self.deadline = int(deadline)
        self.ops = 0
        self.ground_verdict: Optional[str] = None
        self._stage_caps: dict = {}
        self._donor_caps: dict = {}
        self.pins_path = Path(pins_path) if pins_path else None
        self.donors_dir = Path(donors_dir) if donors_dir else None
        self.pins_emitted = 0

    def open(self) -> None:
        """Mint one capability per contract (7 admin rows). The only root-mint path:
        kernel.mint under the kernel's root admin capability, ledgered either way."""
        holder = f"apex-run:{self.run_id}"
        for name, contract in self.contracts.items():
            result = self.kernel.mint(
                self.kernel.root_admin_capability, holder=holder, target=contract.id,
                rights=frozenset({"invoke"}), ttl=self.deadline, now=self.now,
            )
            self.ops += 1
            if isinstance(result, Err):
                raise SealError(result.error, stage=f"open:{name}")
            self._stage_caps[name] = result.value

    def _require_ground(self, stage: str) -> None:
        if self.ground_verdict != "YES":
            raise SealError(
                E.GateBlocked(
                    f"GROUND:{self.ground_verdict or 'unset'} blocks {stage}; "
                    "zero downstream ledger rows"),
                stage=stage,
            )

    def seal_stage(self, stage: str, artifact):
        """Seal one stage record. Downstream stages refuse before any kernel call when
        the ground verdict is not YES (layer 1 of item 10)."""
        if stage == "ROUTE":
            raise SealError(
                E.InputRejected("ROUTE artifacts are sealed via invoke_donor()"),
                stage=stage)
        art = validate_stage(stage, artifact)
        if stage in DOWNSTREAM_STAGES:
            self._require_ground(stage)
        result = self.kernel.seal(Call(
            capability=self._stage_caps[stage], target=self.contracts[stage].id,
            raw_input=art, now=self.now,
        ))
        self.ops += 1
        if isinstance(result, Err):
            raise SealError(result.error, stage=stage)
        if stage == "GROUND":
            self.ground_verdict = art.verdict
        return result.value

    def invoke_donor(self, *, node_id: str, node_type: str, donor: str,
                     gate_evidence: str, envelope: str = "read-only"):
        """One donor call under an attenuated capability (item 11): holder
        invoke:<donor>, ttl = run deadline, derived from the run's donor-route
        capability. The gated R1 seal appends the route row; on PASS it carries the
        cert_hash (item 12)."""
        self._require_ground("ROUTE")
        donor_hash = donor_skill_hash(donor, self.donors_dir)
        if donor_hash is None:
            raise SealError(  # pre-kernel: an unpinnable donor never reaches seal()
                E.InputRejected(
                    f"donor {donor}: SKILL.md not found under "
                    f"{self.donors_dir or DONOR_ALLOWLIST_DIR} — the ContextEnvelope "
                    "cannot be pinned; refusing the route"),
                stage="ROUTE",
            )
        cap = self._donor_caps.get(donor)
        if cap is None:
            result = self.kernel.attenuate(
                self._stage_caps["DONOR_ROUTE"], holder=f"invoke:{donor}",
                rights=frozenset({"invoke"}), ttl=self.deadline, now=self.now,
            )
            self.ops += 1
            if isinstance(result, Err):
                raise SealError(result.error, stage="ROUTE")
            cap = self._donor_caps[donor] = result.value
        raw = DonorRouteInput(
            node_id=node_id, node_type=node_type, donor=donor,
            gate_evidence=gate_evidence, envelope=envelope,
            ground_verdict=self.ground_verdict, donor_hash=donor_hash,
        )
        result = self.kernel.seal(Call(
            capability=cap, target=self.contracts["DONOR_ROUTE"].id,
            raw_input=raw, now=self.now,
        ))
        self.ops += 1
        if isinstance(result, Err):
            raise SealError(result.error, stage="ROUTE")
        receipt = result.value
        if self.pins_path is not None:
            _write_pin(Path(self.pins_path), {
                "ts": self.now,
                "node_id": node_id,
                "donor": donor,
                "donor_hash": receipt.donor_hash,
                "result_hash": content_hash_of(receipt).hex(),
                "row_hash": self.kernel.ledger.last_entry_hash().hex(),
                "length": len(self.kernel.ledger),
            })
            self.pins_emitted += 1
        return receipt


def _smoke_artifacts(ground: str) -> list:
    return [
        ("DECODE", SystemCard(
            intent="sealed-kernel smoke: seal one run through the typed stage contracts",
            mode="EXECUTION", risk=2, root_type="BUILD",
            assumptions=["smoke run on a fixture or seeded ledger"])),
        ("GROUND", GroundVerdict(
            verdict=ground, actor="apex-kernel smoke",
            cost="one smoke run", evidence="scripts/apex-kernel.py probe run",
            crux="kernel seams hold end to end")),
        ("DECOMPOSE", TreeNode(
            node_id="ROOT", node_type="BUILD", item="smoke",
            what="seal one typed run", deliverable="ledger rows",
            done=False, ground_verdict=ground)),
        ("FUSE", FuseReport(
            node_id="ROOT", contradictions_found=0, resolved=0,
            synthesis="no contradictions in a smoke run",
            ground_verdict=ground)),
        ("PLAN", WavePlan(
            waves=[WaveEntry(wave="SMOKE", goal="prove rows == calls",
                             accept="python3 scripts/check-w3-gate.py")],
            ground_verdict=ground)),
        ("CLOSE", CloseBlock(
            gates_fired=["kernel-smoke"], skipped=[], blackboard="n/a",
            handoffs=[], status="DONE", ground_verdict=ground)),
    ]


def run_pipeline(kernel: Kernel, contracts: dict, *, run_id: str, now: int,
                 deadline: int, routes: list, ground: str = "YES",
                 pins_path=None, donors_dir=None) -> dict:
    """Seal one full run: 6 stage records + N donor routes, emitting one donor pin
    per sealed route when `pins_path` is set. Returns the run summary; `ops` must
    equal the ledger row delta (item 8). On ground == "NO" the pipeline raises
    SealError at the first downstream stage with zero downstream rows written
    (item 10)."""
    run = ApexRun(kernel, contracts, run_id=run_id, now=now, deadline=deadline,
                  pins_path=pins_path, donors_dir=donors_dir)
    rows_before = len(kernel.ledger)
    run.open()
    for stage, artifact in _smoke_artifacts(ground):
        if stage == "FUSE":  # donor routes land between DECOMPOSE and FUSE
            for r in routes:
                run.invoke_donor(**r)
        run.seal_stage(stage, artifact)
    rows_after = len(kernel.ledger)
    return {
        "run_id": run_id,
        "ops": run.ops,
        "rows": rows_after - rows_before,
        "rows_total": rows_after,
        "donors": [r["donor"] for r in routes],
        "pins": run.pins_emitted,
    }


# --------------------------------------------------------------------------
# Route verification (item 12 CLI): every EXECUTED route row must carry a cert_hash
# --------------------------------------------------------------------------

def verify_routes(ledger_path=None, route_contract_id=None) -> dict:
    """Read-only scan of the persisted ledger: an EXECUTED row targeting the
    donor-route contract without a cert_hash is a forged/uncertified route and is
    reported as such. BLOCKED rows are counted separately (refusals are receipts).
    Raw line parse, no flock: the ledger is append-only and this never writes."""
    lp = Path(ledger_path) if ledger_path else DEFAULT_LEDGER
    if not lp.exists():
        return {"status": "none", "certified": 0, "total": 0, "forged": 0, "blocked": 0}
    rid = route_contract_id or make_apex_contracts()["DONOR_ROUTE"].id
    rid_hex = rid.hex() if isinstance(rid, bytes) else rid
    certified = total = forged = blocked = 0
    for line in lp.read_text().splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("target") != rid_hex:
            continue
        if payload.get("verdict") == "EXECUTED":
            total += 1
            if payload.get("cert_hash"):
                certified += 1
            else:
                forged += 1
        elif payload.get("verdict") == "BLOCKED":
            blocked += 1
    status = "forged" if forged else ("ok" if total else "none")
    return {"status": status, "certified": certified, "total": total,
            "forged": forged, "blocked": blocked}


# --------------------------------------------------------------------------
# Donor-pin verification (W3b item 14 CLI): each pin must bind to the exact sealed
# route row it claims, and the donor's SKILL.md must still hash to the pinned value
# --------------------------------------------------------------------------

def verify_pins(pins_path=None, *, ledger_path=None, donors_dir=None,
                receipts_dir=None, now=None) -> dict:
    """Read-only donor-pin audit. Binding: a pin's `row_hash` (sha256 of the raw
    ledger line) must exist among EXECUTED DONOR_ROUTE rows and its `result_hash`
    must match that row — a pin claiming a row the ledger does not hold is FAIL.
    Drift: the donor's SKILL.md no longer hashes to the pinned value — a DRIFT
    receipt is written when `receipts_dir` is given. Raw-line reads, no flock, the
    ledger is never written."""
    pp = Path(pins_path) if pins_path else DEFAULT_PINS
    lp = Path(ledger_path) if ledger_path else DEFAULT_LEDGER
    out = {"status": "none", "pins": 0, "bound": 0, "drift": 0, "failed": 0,
           "receipts": [], "drifts": []}
    if not pp.exists():
        return out
    rid = make_apex_contracts()["DONOR_ROUTE"].id
    rid_hex = rid.hex() if isinstance(rid, bytes) else rid
    rows: dict = {}
    if lp.exists():
        for raw in lp.read_bytes().split(b"\n"):
            if not raw:
                continue
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if payload.get("target") != rid_hex or payload.get("verdict") != "EXECUTED":
                continue
            rows[hashlib.sha256(raw).hexdigest()] = payload
    for line in pp.read_text().splitlines():
        if not line.strip():
            continue
        out["pins"] += 1
        try:
            pin = json.loads(line)
        except json.JSONDecodeError:
            out["failed"] += 1
            continue
        row = rows.get(pin.get("row_hash"))
        if row is None or row.get("result_hash") != pin.get("result_hash"):
            out["failed"] += 1
            continue
        observed = donor_skill_hash(pin.get("donor", ""), donors_dir)
        if observed != pin.get("donor_hash"):
            out["drift"] += 1
            out["drifts"].append({
                "donor": pin.get("donor"), "node_id": pin.get("node_id"),
                "pinned_hash": pin.get("donor_hash"), "observed_hash": observed,
                "result_hash": pin.get("result_hash"),
            })
        else:
            out["bound"] += 1
    if out["failed"]:
        out["status"] = "failed"
    elif out["drift"]:
        out["status"] = "drift"
    else:
        out["status"] = "ok"
    if out["drift"] and receipts_dir:
        rd = Path(receipts_dir)
        rd.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime(
            now if now is not None else int(time.time())))
        for d in out["drifts"]:
            receipt = {
                "kind": "pin-drift", "ts": stamp, "donor": d["donor"],
                "node_id": d["node_id"], "pinned_hash": d["pinned_hash"],
                "observed_hash": d["observed_hash"],
                "result_hash": d["result_hash"],
                "action": "re-read the donor SKILL.md before re-invoking; the sealed "
                          "route pinned a different version",
            }
            path = rd / f"pin-drift-{stamp}-{d['donor']}.json"
            path.write_text(json.dumps(receipt, indent=2) + "\n")
            out["receipts"].append(path.name)
    return out


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def cmd_seed(args) -> int:
    kernel, _contracts, restored = boot_kernel(args.ledger, args.key)
    n = len(kernel.ledger)
    lp = Path(args.ledger) if args.ledger else DEFAULT_LEDGER
    if not lp.exists():  # 0-row seed still materializes the store (append is lazy)
        lp.touch(mode=0o600)
    print(f"KERNEL SEEDED rows={n} restored_revocations={restored} "
          f"tip={kernel.ledger.last_entry_hash().hex()[:12]}")
    kernel.ledger.close()
    return 0


def cmd_status(args) -> int:
    lp = Path(args.ledger) if args.ledger else DEFAULT_LEDGER
    kp = Path(args.key) if args.key else DEFAULT_KEY
    if not lp.exists() or not kp.exists():
        print("KERNEL: not seeded (run: python3 scripts/apex-kernel.py seed)")
        return 0
    try:
        kernel, _contracts, restored = boot_kernel(args.ledger, args.key)
    except Exception as exc:  # chain broken / unreadable: honest refusal, terse
        print(f"KERNEL: BROKEN {type(exc).__name__}: {str(exc)[:120]}")
        return 1
    n = len(kernel.ledger)
    print(f"KERNEL: OK rows={n} revoked_restored={restored} "
          f"tip={kernel.ledger.last_entry_hash().hex()[:12]}")
    kernel.ledger.close()
    return 0


def cmd_smoke(args) -> int:
    kernel, contracts, restored = boot_kernel(args.ledger, args.key)
    now = int(args.now) if args.now else int(time.time())
    deadline = now + 86400
    allow = sorted(default_allowlist())
    donors = args.donors.split(",") if args.donors else allow[:3]
    if not donors:
        print("SMOKE: BLOCKED no donors in allowlist (context/donors empty)")
        return 1
    lp = Path(args.ledger) if args.ledger else DEFAULT_LEDGER
    routes = [{
        "node_id": f"leaf-{i}", "node_type": "BUILD", "donor": d, "envelope": "read-only",
        "gate_evidence": f"gate: smoke route {i}, donor skill file observed",
    } for i, d in enumerate(donors)]
    try:
        summary = run_pipeline(kernel, contracts, run_id=args.run_id, now=now,
                               deadline=deadline, routes=routes,
                               pins_path=pins_path_for(lp))
    except SealError as exc:
        print(f"SMOKE: BLOCKED [{exc.stage}] {exc.error}")
        kernel.ledger.close()
        return 1
    equal = "yes" if summary["ops"] == summary["rows"] else "NO"
    print(f"SMOKE: calls={summary['ops']} rows={summary['rows']} equal={equal} "
          f"pins={summary['pins']} restored={restored} "
          f"donors={','.join(summary['donors'])}")
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2))
    kernel.ledger.close()
    return 0 if equal == "yes" else 1


def cmd_verify_routes(args) -> int:
    report = verify_routes(args.ledger)
    if report["status"] == "forged":
        print(f"ROUTES: BLOCKED forged uncertified EXECUTED rows: {report['forged']}")
        return 1
    if report["status"] == "none":
        print("ROUTES: none (no certified route rows yet)")
        return 0
    pct = 100 if report["total"] else 0
    print(f"ROUTES CERTIFIED: {report['certified']}/{report['total']} ({pct}%) "
          f"blocked={report['blocked']}")
    return 0


def cmd_verify_pins(args) -> int:
    report = verify_pins(
        args.pins, ledger_path=args.ledger, donors_dir=args.donors_dir,
        receipts_dir=(Path(args.receipts_dir) if args.receipts_dir
                      else SKILL_DIR / "receipts"),
        now=int(args.now) if args.now else None)
    if report["status"] == "none":
        print("PINS: none (no sealed donor routes yet)")
        return 0
    if report["status"] == "failed":
        print(f"PINS: BLOCKED {report['failed']} broken binding(s) — a pin claims a "
              "ledger row the ledger does not hold")
        return 1
    if report["status"] == "drift":
        print(f"PINS: DRIFT {report['drift']} donor(s) changed since routing "
              f"(bound={report['bound']}/{report['pins']}, "
              f"receipts={len(report['receipts'])})")
        return 0
    print(f"PINS OK: {report['bound']}/{report['pins']} bound, drift=0")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="APEX sealed-kernel seed (W3/W3b)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, fn in (("seed", cmd_seed), ("status", cmd_status), ("smoke", cmd_smoke),
                     ("verify-routes", cmd_verify_routes), ("verify-pins", cmd_verify_pins)):
        p = sub.add_parser(name)
        p.add_argument("--ledger", default=None)
        if name not in ("verify-routes", "verify-pins"):
            p.add_argument("--key", default=None)
        if name == "smoke":
            p.add_argument("--run-id", default="smoke")
            p.add_argument("--now", default=None)
            p.add_argument("--out", default=None)
            p.add_argument("--donors", default=None, help="comma-separated donor names")
        if name == "verify-pins":
            p.add_argument("--pins", default=None)
            p.add_argument("--donors-dir", default=None)
            p.add_argument("--receipts-dir", default=None)
            p.add_argument("--now", default=None)
        p.set_defaults(fn=fn)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
