# BACKEND: ULTRA-PACK — the reasoning-first compiler  (NEW in v2.1.0)

> **The fourth emitter.** `pack` builds greenfield from prescribed domain files. `ultra`
> transforms an existing system in one contractual prompt. `tournament` races K ultras.
> **`ultra-pack` compiles a REASONING MACHINE** — one prompt that makes the executing LLM
> *derive* the genius build plan (what to build, how, the smartest way), prove it is genius
> rather than merely adequate, then emit the full research→deploy execution prompts FROM its
> own derived plan. A prompt that makes a prompt. One shot, anything, end to end.

---

## THE ENGINEERING CLAIM

autovibe cannot know the smartest stack/architecture for an arbitrary intent. But it CAN
compile a prompt that **forces the executing LLM to find it and prove it.** This is the same
contractual-not-rhetorical thesis as `ultra` (§5 floor + §6 staged protocol + §9 self-score
gate already make an LLM reason instead of polish). ULTRA-PACK does ONE thing differently:

- `ultra` runs §6's reasoning at **transform-an-existing-system** orientation and the answer
  is a migration plan for that system.
- `ultra-pack` re-points §6 to **derive a build from the job-to-be-done** (greenfield-capable,
  existing-capable), and the §7 output contract demands the LLM then **emit the lifecycle
  execution prompts** (research → setup → build → deploy → verify) from the plan it just derived.

**The crux this dissolves:** genius-finding moves from *compile-time-baked* (autovibe guesses
the plan) to *run-time-forced* (the prompt makes any LLM reason to the genius plan with full
fresh context). The compiler ships the reasoning, not the answer.

---

## TRIGGER

Fire ULTRA-PACK mode when ANY of:

- User passes `--ultra-pack` or `--reason` flag
- Intent asks for a *plan/approach derivation across the whole lifecycle*: "one shot from
  research to deploy", "figure out what and how to build", "the smartest way to build X",
  "ultra pack", "reason out the whole build", "research → plan → build → deploy in one prompt"
- An upstream skill requests a reason-then-execute single artifact (kraken-flow node 7 with
  `backend: ultra-pack`)

Distinguish from the neighbours:

| You want… | Backend |
|---|---|
| Build a known greenfield system; you'll execute domain prompts in order | `pack` |
| Transform a *specific existing system* to its next version | `ultra` |
| Same as ultra but high-stakes, race K candidates | `tournament` |
| **Make the LLM reason out WHAT+HOW+smartest-way, then emit the whole research→deploy run** | **`ultra-pack`** |

Ambiguous between `pack` and `ultra-pack`: ask one question — *"Do you already know the build
(I compile execution prompts → `pack`), or should the prompt reason out the smartest build
first (→ `ultra-pack`)?"* The two are not interchangeable: `pack` prescribes, `ultra-pack` derives.

---

## MODE FORK — which passes run

| Pass | ultra-pack behaviour |
|---|---|
| PRE (mind_retrieve + spawner_orchestrate) | ✅ unchanged |
| PASS 0.0 GROUND | ✅ unchanged — an ungrounded "build something genius" is the costliest input; HALT applies |
| P0 RECONNAISSANCE | **PRIOR-ART RECON** (greenfield) OR **SYSTEM-RECON** (if an existing system is named). Greenfield = research the closest existing products + the white space, like pack-mode P0 — NOT "the target system itself" |
| P1 DECOMPOSE | ✅ user × JTBD × capabilities × via-negativa |
| P1.5 TRANSCEND | **ALWAYS fires** — supplies the charter + design vectors the reasoning §4 quotes |
| P2–P5 | ⛔ folded into Ω-PACK — the EXECUTING LLM derives structure; the prompt constrains it |
| PΩ-PACK COMPILE | fill `templates/ultra-pack-reason.md` → `REASON.md` + `RUN-ORDER.md` |
| SCORE | **ULTRA-PACK rubric** (`scoring.md § ULTRA-PACK`) — SHIP ≥ 80/100 |

### PRIOR-ART RECON (greenfield P0 variant)

When nothing exists to transform, RECON researches the *solution space*, not a target system:

1. **Read the adjacent art — MANDATORY.** `WebSearch`/`WebFetch` (or `mind_retrieve` priors) the
   2–3 closest existing products/approaches. NEVER compile a reasoning prompt blind — name what
   already exists so the derived plan has to beat it, not reinvent it. `COMPILE-REPORT.md` lists
   the sources + priors read.
2. **Name the white space** (≥2) — what the closest art does badly or not at all. These become
   the genius-opportunity seeds the reasoning §6 Stage B diverges into.
3. **Name the irreducible job** (1 sentence) — what the user actually needs done. This anchors §6 Stage A.
4. **Name the accepted costs** — what everyone treats as "just how you build this". The genius
   move usually hides in refusing one (realthink CRUX / via-negativa).

When an existing system IS named, fall back to ultra.md's SYSTEM-RECON instead.

---

## THE §-GRAMMAR, RE-POINTED FOR DERIVATION

`REASON.md` reuses the §0–§10 ULTRA grammar (see `ultra.md`) with three sections re-aimed.
Everything not listed here is filled exactly as ultra.md specifies.

### §5 AMBITION FLOOR — greenfield variant
- **FLOOR (reject below):** *"If your plan is the obvious build any competent dev would
  produce — the standard CRUD app, the textbook stack, the first architecture that comes to
  mind — it is below the floor. Discard and restart at Stage A. The genius move is the
  non-obvious architecture that makes the hard thing trivial or deletes a whole problem class."*
  Plus 2 named below-floor examples for THIS intent.
- **CEILING (aim at):** the version a world-class team would ship — name the capability that
  makes users say "how is this even possible". State it as a one-line `genius delta`.
- **DELETE-LIST seed:** what the smart build REFUSES to include that the obvious build would.
  Deletion before addition — require the LLM to extend it.

### §6 THINKING PROTOCOL — re-aimed at "what + how + smartest way" (the reasoning engine)
Each stage emits a visible artifact BEFORE the plan (a stage without an artifact = skipped):
- **Stage A — Irreducible job (first principles):** state the job-to-be-done in one sentence;
  list the minimum capability set that satisfies it. Everything else is a candidate for deletion.
- **Stage B — Solution-space divergence:** generate ≥3 genuinely different architectures /
  approaches that satisfy the job — not variations of one. Artifact: an approach × core-bet table.
  The genius move is rarely the first approach; this stage forbids converging early.
- **Stage C — Second-order ripple:** for each approach, what becomes *possible* that wasn't,
  and what whole problem class does it *delete*? Highest-value builds are second-order.
- **Stage D — Three-tier framing:** label the approaches T1 obvious/safe · T2 smart · T3 genius/
  reimagined. Artifact: one-paragraph sketch + the core bet + the risk line for each.
- **Stage E — Forced selection:** select the HIGHEST tier that survives the constraints and the
  job. Selecting T1 or T2 requires WRITTEN PROOF that T3 breaks a real constraint — *"the obvious
  approach is safer"* is not an argument, it is the anchoring bias this protocol exists to defeat.
  Artifact: the chosen approach + the proof line.

### §7 OUTPUT CONTRACT — reason-THEN-emit (the "prompt that makes a prompt")
The executing LLM must output, in order:
- **(a) THE DERIVED PLAN** — *what* to build (the selected approach), *how* (the architecture +
  stack with the rationale, NOT defaults), and *why this is the genius way* (the §6 Stage E proof).
- **(b) THE LIFECYCLE EXECUTION PROMPTS** — generated FROM (a), one self-contained prompt per
  stage, each carrying its own ACTION + TARGET + CONSTRAINTS + QUALITY-WRAP + VERIFY:
  1. `RESEARCH` — validate the riskiest assumption in the plan before building (kill-criteria).
  2. `SETUP` — scaffold, repo, env, the chosen stack wired to "hello world runs".
  3. `BUILD` — the capabilities in dependency order, each independently shippable + verifiable.
  4. `DEPLOY` — ship it live (the deploy target, the pipeline, the rollback).
  5. `VERIFY` — the falsifiable checks proving each stage landed + the BUILD RECEIPT line.
- **(c) RUN-ORDER** — the exact paste order + what each stage hands the next (outputs→inputs).

An answer missing (a), (b), or (c) is incomplete — say so in the contract. The plan without the
emitted prompts is just an opinion; the prompts without the derived plan are pack-mode.

§0 (ground form), §1–§4 (role/capsule/crux/charter), §8 (quality wrap), §9 (self-score gate),
§10 (verify) — fill per ultra.md. §9's rubric gains one line: *"is the plan DERIVED (Stage E
proof present) rather than asserted? any 'no' → return to Stage A."*

---

## OUTPUT CONTRACT (what autovibe writes)

Write to `~/prompt-packs/<slug>/`:
- `REASON.md` — the reasoning machine (§0–§10, derivation-aimed, ≤ ~6k tokens — slightly above
  ultra's 5k because §7 carries the lifecycle emit contract).
- `RUN-ORDER.md` — paste `REASON.md` once → the LLM reasons → emits the staged prompts → run them.
- `COMPILE-REPORT.md` — IR traceability: RECON sources/priors read, the crux, the charter
  vectors, the ULTRA-PACK rubric score breakdown.

`bin/autovibe-gate.sh ultra-pack <dir>` must exit 0 before SHIP. Report to user: path + score +
crux + *"paste REASON.md into any strong LLM — it must reason out the plan, prove the genius
tier, then emit research→deploy prompts. If it hands back a plain plan with no emitted prompts,
the contract failed — `/autovibe --refine <slug>`."*

The BUILD RECEIPT block (return edge, all backends) appends to `RUN-ORDER.md`: the executor runs
`receipt-ingest.sh --slug <slug> --result pass|fail|partial --sections "<§ids the verify exercised>"`.

---

## QUALITY GATES (ultra-pack mode — replace pack-mode + ultra-mode gates)

| Gate | Severity |
|---|---|
| `up_all_sections_present` — §0–§10 present, none empty | blocker |
| `up_phase0_present` + `up_phase0_precedes_role` — §0 ground form, before §1 (anti-anchoring) | blocker |
| `up_floor_greenfield` — §5 floor rejects the obvious build + names ≥2 below-floor examples | blocker |
| `up_stage_E_forced` — §6 Stage E requires written proof when a tier below T3 is chosen | blocker |
| `up_reason_then_emit` — §7 demands (a) derived plan AND (b) emitted lifecycle prompts AND (c) run-order | blocker |
| `up_lifecycle_complete` — §7 (b) names all of research/setup/build/deploy/verify | blocker |
| `up_recon_provenance` — `COMPILE-REPORT.md` lists prior-art sources (or SYSTEM-RECON files) read | blocker |
| `up_self_score_derived` — §9 rubric includes the "plan derived not asserted" line | blocker |
| `up_doc_budget` — `REASON.md` ≤ ~6k tokens | warn |

`file_count_floor` does NOT apply (ultra-pack writes 3 files by design — the reasoning machine,
not a directory of prescriptions).
