# PASS Ω — ULTRA-COMPILE  (the single-document backend — NEW in v0.6.0)

> **autovibe is a compiler: front-end (analysis) + back-end (emitter).** v0.1–v0.5 had ONE
> back-end — the multi-file prompt-pack. PASS Ω is the SECOND back-end: it takes the exact
> same IR (GROUND crux + DECOMPOSE lists + TRANSCEND charter/vectors) and compiles DOWN
> into **one self-contained ULTRA-PROMPT.md** that any LLM can be handed to produce a
> system-level, next-version transformation — not minor tweaks.
>
> Pack mode answers: *"build X from scratch"* → 10–15 files executed in order.
> Ultra mode answers: *"enhance/transcend EXISTING system X"* → 1 file pasted once.
>
> **The engineering claim:** what makes an LLM return architecture-scale change instead of
> polite polish is **contractual, not rhetorical**. You don't ask harder — you (1) set an
> ambition FLOOR that rejects sub-architectural output, (2) embed a thinking protocol with
> visible stage artifacts the model cannot skip, (3) demand an output contract of migration
> waves + a delete list, and (4) close with a self-score gate that forces a redo below
> threshold. The grammar below exists to encode those four mechanisms.

---

## TRIGGER

Fire ULTRA mode when ANY of:

- User passes `--ultra` or `--one` flag
- Intent verb-class is **transformation of an existing system**: "enhance", "upgrade",
  "modernize", "overhaul", "rearchitect", "make X great", "next level", "next version",
  "10x/100x/1000x", "transform" — AND the intent names a system that already exists
  (a repo, a product, "this codebase", "the system", "Kraken OS")
- An upstream skill requests a single-document compile (kraken-flow node 7 with
  `backend: ultra`, realthink `--build` on an enhancement move)

Stay in PACK mode when:

- Intent is greenfield ("build me a health app") — nothing exists to transform;
  ultra-on-greenfield is a sharp edge (see `sharp-edges.yaml#ultra-on-greenfield-intent`)
- User explicitly asks for a pack / multiple prompts / a run order

Ambiguous (enhancement verb but no existing system named, or "rebuild X from scratch") →
ask one question: *"Transform the existing system (1 ULTRA prompt) or compile a fresh
build pack (N prompts)?"* Never guess on this fork — the two artifacts are not interchangeable.

---

## MODE FORK — which passes run

| Pass | Pack mode | Ultra mode |
|---|---|---|
| PRE (mind_retrieve + spawner_orchestrate) | ✅ | ✅ unchanged |
| PASS 0.0 GROUND | ✅ | ✅ unchanged — an ungrounded "make it great" is the costliest ultra input; HALT applies identically |
| P0 RECONNAISSANCE | references = competitor products | **SYSTEM-RECON**: the "reference product" is the TARGET SYSTEM ITSELF (see below) |
| P1 DECOMPOSE | user × JTBD × capabilities × via-negativa | ✅ same shape, applied to the current system's users and jobs |
| P1.5 TRANSCEND | conditional | **ALWAYS fires** — it is the engine; ultra without a charter is a tweak-generator |
| P2 DOMAIN-MAP | ✅ | ⛔ folded into Ω (the executing LLM picks structure; the prompt constrains it with vectors + invariants) |
| P3 CATCQ-FILL | ✅ | ⛔ folded into Ω (CATCQ generalizes to the 11-section §0–§10 grammar) |
| P4 COMBO-ASSEMBLE | ✅ | ⛔ N/A — there is exactly one document; no RUN-ORDER |
| P5 QUALITY-WRAP | ✅ | folded into Ω §8 (inverted scope limiters — see grammar) |
| SCORE | pack rubric | **ULTRA rubric** (`scoring.md` § ULTRA) — SHIP ≥ 80/100 |

### SYSTEM-RECON (P0 variant in ultra mode)

The product being researched is the system to be transformed. Do this:

1. **Read the actual system — MANDATORY, not "if a repo".** `Read` the entry docs /
   CLAUDE.md / README / architecture files (and `spawner_analyze(path)` when it is a repo),
   AND `mind_retrieve` past decisions/outcomes about it (V4 outcome-informed recon — the
   priors keep cracks from going stale; see edge `stale-mind-retrieve-misleads-pre-pipeline`).
   NEVER compile an ultra prompt for a system you haven't looked at — that is fluent
   fabrication at the compiler level. `COMPILE-REPORT.md` MUST list the files read + the
   `mind_retrieve` priors; `bin/precompile-gate.sh --report` BLOCKS when that provenance is
   absent. The optional-read branch is deleted as of v0.7.0 — reading is the floor of RECON.
2. **Name strengths** (≥3) — what the transformation must NOT lose. These become INVARIANTS.
3. **Name cracks** (≥3) — concrete weaknesses with evidence (a file, a metric, an incident,
   a user complaint). These feed TRANSCEND's 5-step teardown.
4. **Name accepted costs** — what everyone treats as "just how it is". The crux usually
   hides here (realthink CRUX rule).
5. Optional: `scanner_scan` if the system is security-adjacent; cracks found become evidence.

Output: the recon IR is folded into the CONTEXT CAPSULE (§2) and kept verbatim in
`COMPILE-REPORT.md` for traceability.

---

## THE GRAMMAR — 11 sections (§0–§10), every ULTRA-PROMPT.md has all of them

> CATCQ scales to single-shot transformation as: CONTEXT→§2, ACTION→§1+§5, TARGET→§2+§7,
> CONSTRAINTS→§0+§4+§8, QUALITY→§8+§9. Fill `templates/ultra-prompt.md`; specs below.

### §0 PRE-GENERATION GROUND FORM — ordering is the anti-anchoring mechanism (NEW v1.0)
The first section the executing LLM completes, **before §1 ROLE**. Two forms:
- **VIA-NEGATIVA** (complete first): ≥3 `CANNOT` boundary lines, ≥3 `TRAP`/`BREAKS` lines
  (plausible moves that look right but aren't), ≥1 adversarial `OBJECTION` + rebuttal.
- **POSITIVE-GROUND** (complete second, constrained by the above): ≥2 `Evidence:` items
  (file/metric/incident), ≥1 `First principle`, a measurable-success line, and a `Scope:` line.
**Why §0 and not §5:** causal attention is directional — tokens generated early become context
for later tokens. Constraints placed *before* any positive-direction section shape what gets
generated; the same constraints placed at §5/§6 (after ROLE+CONTEXT+CRUX+CHARTER) fight a
residual stream already committed to a direction. A §6 Stage-A "teardown" that runs after §1–§4
is post-commitment rationalization, not genuine teardown. §0 moves the constraint map ahead of
the commitment. The gate (`autovibe-gate.sh ultra` check 8) BLOCKS when §0 is absent, thin, or
positioned after §1 — the ordering is enforced at compile time, not requested in prose.

### §1 ROLE & STAKES — permission removes conservatism
Who the executing LLM is and what authority it holds. Must include: a principal-architect
role WITH explicit breaking-change authority, what "great" means for THIS system in one
sentence, and the anti-goal: *"Proposals at the level of renames, lint fixes, or single-file
refactors are failures. The smallest acceptable unit of change is architectural."*
LLMs default to safe edits because nobody granted them authority; this section grants it.

### §2 CONTEXT CAPSULE — compressed truth beats pasted bulk
The current-state map from SYSTEM-RECON, compressed to **≤ ~2,000 tokens**: components and
their one-line jobs, data flows, the strengths-as-INVARIANTS list (must not be lost), the
cracks list WITH evidence, real constraints vs assumed constraints (label which is which).
Budget is a gate (`context_capsule_token_budget`) — a bloated capsule buries the signal and
dilutes every section after it. Link out (file paths) instead of inlining code.

### §3 CRUX — the one constraint
The grounded bottleneck from PASS 0.0, one sentence, plus its evidence line. The entire
transformation must dissolve THIS — any proposal that doesn't touch the crux is rejected by
§9. (This is what stops the LLM from "improving" twelve random corners.)

### §4 NORTH-STAR CHARTER + DESIGN VECTORS — the constitution
TRANSCEND's differentiation charter (one sentence: specific / defensible / user-cares) and
3–5 design vectors, quoted verbatim. Every wave the LLM proposes must cite which vector it
serves. Vectors outrank any existing convention of the current system — say so explicitly.

### §5 AMBITION CALIBRATION — the floor is the mechanism
The section that deletes minor-tweak responses. Three parts:
- **FLOOR** (reject below): *"If your full proposal could be executed in under a day, it is
  below the floor — discard and restart at Stage A."* Plus named examples of below-floor
  output for this system ("adding a config flag", "wrapping X in a helper").
- **CEILING** (aim at): the next whole version — name it (`v_current → v_next`) and require
  the proposal to state the capability delta in user terms.
- **DELETE LIST seed** (via-negativa): TRANSCEND's removals. Require the LLM to EXTEND this
  list — what the next version refuses to carry forward. Deletion before addition.

### §6 THINKING PROTOCOL — staged, visible, unskippable
The mechanism that makes the model actually think. The prompt REQUIRES these stages, each
with a visible artifact emitted before the answer (a stage without an artifact = skipped):
- **Stage A — First-principles teardown:** restate the system's irreducible job in one
  sentence; list every current structure that is NOT entailed by that job.
- **Stage B — 5-step algorithm on each crack:** Question (is it a hidden feature?) → Delete
  (the assumption creating it) → Simplify → Accelerate → Automate. Artifact: a crack × 5-step table.
- **Stage C — Second-order ripple:** for each candidate change, what becomes possible that
  wasn't before? The highest-value moves are usually second-order (realthink RIPPLE).
- **Stage D — Three-tier options:** propose THREE transformations: T1 conservative,
  T2 structural, T3 reimagined. Artifact: one-paragraph sketch + risk line each.
- **Stage E — Forced selection:** select the HIGHEST tier that survives the risk map and
  the INVARIANTS. Selecting T1 requires written proof that T2 and T3 break an invariant —
  "T1 is safer" is not an argument, it is the anchoring bias this protocol exists to defeat.

### §7 OUTPUT CONTRACT — the shape forces the scale
Exact deliverable: **(a)** Target architecture of the next version (capability delta stated
as `v_current → v_next`); **(b)** Migration WAVES — 3–7, each independently shippable and
verifiable, each citing the design vector it serves; **(c)** the completed DELETE LIST;
**(d)** Risk map — every wave's hurdle + mitigation/accept; **(e)** per-wave VERIFY — a
concrete check proving the wave landed. An answer missing any of (a)–(e) is incomplete:
say so in the contract.

### §8 QUALITY WRAP — inverted for transformation
Pack-mode limiters protect existing structure; ultra-mode limiters protect only what was
DECLARED worth protecting: *"Do not preserve existing structure out of politeness — preserve
only the named INVARIANTS (§2)."* Keep the classic anti-slop guards (no god-modules, no
premature abstraction, no vague names) and add transformation guards: no rewrite-for-rewrite's-sake
(every wave cites a crack or vector), no big-bang wave (each wave shippable alone), no silent
invariant breakage (breaking one requires naming it + justifying against the charter).

### §9 SELF-SCORE GATE — the discipline travels with the prompt
Embed a 5-line rubric the EXECUTING LLM applies to its own proposal before presenting:
crux dissolved? / highest viable tier chosen (with proof if not T3)? / every wave vector-cited
+ independently shippable? / delete list extended beyond the seed? / all invariants intact or
explicitly traded? **Any "no" → return to Stage A; do not present.** This is autovibe's own
SHIP-gate discipline, recursed into the artifact.

### §10 VERIFY — the tell
One falsifiable check the USER runs on the LLM's answer to know the prompt worked, e.g.:
*"The proposal names ≥3 deletions, ≥1 second-order capability, and a v_next capability delta;
if it reads like a code-review comment list, the prompt failed — refine via
`/autovibe --refine <slug>`."*

---

## COMPRESSION DISCIPLINE

The whole document targets **≤ ~5,000 tokens** (capsule ≤ ~2,000). It must travel: pasteable
into any LLM with room left for the answer. When over budget, cut in this order:
example bulk in §5 → capsule detail (link out to paths) → §6 stage prose (keep the artifacts
list). NEVER cut: the pre-generation ground form (§0), the floor (§5), the stage-artifact
requirement (§6), the output contract (§7), the self-score gate (§9) — those five ARE the
mechanism. §0 in particular is non-negotiable: thinning it past ≥3 CANNOT + ≥3 TRAP + ≥1
OBJECTION + ≥2 Evidence re-opens the first-draft-anchoring hole v1.0 closed.

---

## QUALITY GATES (ultra mode — replace pack-mode gates)

| Gate | Severity |
|---|---|
| `ultra_all_sections_present` — all 11 sections (§0–§10), none empty | blocker |
| `phase0_present` — §0 has ≥3 CANNOT + ≥3 TRAP/BREAKS + ≥1 OBJECTION + ≥2 Evidence + first-principle + scope | blocker (NEW v1.0.0, V1) |
| `phase0_precedes_role` — §0's line number is BEFORE §1 ROLE (the anti-anchoring ordering invariant) | blocker (NEW v1.0.0, V2) |
| `claim_level_grounding` — every recommendation carries `grounded in:` or an `EXPERIMENT:` framing | blocker (NEW v1.0.0, V3) |
| `ambition_floor_stated` — §5 has explicit floor with below-floor examples | blocker |
| `crux_grounded` — §3 traces to PASS 0.0 verdict (or `--no-ground` logged) | blocker |
| `thinking_protocol_has_artifacts` — every §6 stage names its visible artifact | blocker |
| `output_contract_forces_waves` — §7 demands waves + delete list + risk map + verify | blocker |
| `recon_baseline_met` — §2 carries ≥3 `Evidence:`-backed cracks AND ≥3 named INVARIANTS | blocker (NEW v0.7.0) |
| `version_delta_declared` — §5 names `v_current → v_next` with a capability-delta sentence | blocker (NEW v0.7.0) |
| `recon_provenance_listed` — `COMPILE-REPORT.md` lists files read + `mind_retrieve` priors | blocker (NEW v0.7.0, V4) |
| `context_capsule_token_budget` — capsule ≤ ~2k tokens | warn |
| `vectors_quoted_verbatim` — §4 quotes TRANSCEND vectors, not paraphrases | warn |
| `doc_token_budget` — whole doc ≤ ~5k tokens | warn |

`file_count_floor` does NOT apply in ultra mode (pack-mode-only as of v0.6.0).

---

## PRE-EMIT GATE — the harness that makes the gates BLOCK  (NEW v0.7.0)

The table above lists blockers. v0.6 enforced them by PROSE — the compiling LLM was
asked to self-check AFTER writing, and `quick_detection_recipes` in `sharp-edges.yaml`
ran post-hoc on the finished file. v0.7 makes them EXECUTABLE and PRE-EMIT:

```
bin/precompile-gate.sh --ultra <draft ULTRA-PROMPT.md> [--report <COMPILE-REPORT.md>]
```

**PΩ is NOT complete until this gate exits 0.** Run it on the draft BEFORE presenting
the ULTRA-PROMPT as final. The gate greps the draft for the blocker conditions
(11 sections §0–§10 · ambition floor WITH below-floor examples · ≥5 stage artifacts · output
contract forces waves+delete+risk+verify · ≥3 evidence-backed cracks · ≥3 INVARIANTS ·
a `v_current → v_next` delta · **§0 present + BEFORE §1 with a non-thin via-negativa +
positive-ground (checks 8-9)** · **every recommendation claim-anchored (check 10)**).
**Exit 2 = BLOCK**: do NOT emit — the user sees
`compile blocked: RECON thin` with the matching `sharp-edges.yaml` id + fix BEFORE
pasting anything into a second LLM. **Exit 0 = PASS**: ship.

This is the crux of v0.7: it converts the post-hoc `quick_detection_recipes` into a
compile-time blocker. Each crack the gate names carries an `Evidence:` line, so the
22 sharp edges auto-surface at failure time (V3) instead of being read manually. The
gate is pure bash — markdown is the artifact format; bash is the gate (the "no external
infra" constraint applied only to the artifact, never the harness).

---

## OUTPUT & SHIP

Write to `~/prompt-packs/<slug>/` (path discipline unchanged):
- `ULTRA-PROMPT.md` — the artifact; the only file the user needs
- `COMPILE-REPORT.md` — IR traceability: GROUND verdict + crux, SYSTEM-RECON
  (strengths/cracks/accepted-costs), TRANSCEND charter + vectors, ULTRA score breakdown,
  compile decisions (what was cut for budget)

Score per `scoring.md` § ULTRA RUBRIC; SHIP ≥ 80/100, re-run weakest section (max 2), else
surface gaps. SHIP batch identical to pack mode (`mind_remember` + `spawner_remember` +
ledger-append with `--mode ultra`), so the v0.5 outcome loop covers both backends —
`/autovibe --outcome <slug> good|bad` works unchanged.

Report to user:
```
✅ ULTRA prompt compiled: ~/prompt-packs/<slug>/ULTRA-PROMPT.md
Mode: ultra   Score: <N>/100   Crux: <one line>
Paste the whole file into Claude/Cursor/any LLM. One shot.
The answer must contain: waves + delete list + risk map + v_next delta (§7 contract).
To refine: /autovibe --refine <slug>   Outcome: /autovibe --outcome <slug> good|bad
```

---

## MICRO-EXAMPLE (compressed skeleton — "make Kraken OS great")

```markdown
# ULTRA PROMPT — Kraken OS → next version
## 0 PRE-GENERATION GROUND FORM — VIA-NEGATIVA (≥3 CANNOT + ≥3 TRAP + ≥1 OBJECTION)
THEN POSITIVE-GROUND (≥2 Evidence + first principle + scope). Completed BEFORE §1.
## 1 ROLE & STAKES
You are the principal architect of Kraken OS with full breaking-change authority…
Failure mode to avoid: a list of hook tweaks. Smallest acceptable change: architectural.
## 2 CONTEXT CAPSULE
Components: tier-0/1 hooks (routing), 24 packs (method), 6 MCP servers (tools), Mind
(salience memory)… INVARIANTS: pack method-discipline; Mind outcome loop; kill-switches.
CRACKS: routing is regex-first (evidence: P18-on-refactor misfire 2026-06-12); execution
contract enforced by prose, not state machine; …
## 3 CRUX
Orchestration intelligence lives in bash regex while the model that could route by meaning
is told to obey the regex — evidence: 30-case pack-test needed to patch misfires one by one.
## 4 CHARTER + VECTORS
"The first self-routing OS where the model IS the router and hooks only verify."
V1 meaning-over-regex… V2 state-machine gates… V3 every directive machine-checkable…
## 5 AMBITION — FLOOR: executable <1 day = restart. CEILING: v7 "verifier OS".
DELETE seed: banner prose directives; per-pack regex triggers; …extend this list.
## 6 THINKING PROTOCOL — Stages A–E with artifacts (teardown table, crack×5-step
table, ripple list, T1/T2/T3 sketches, forced selection w/ proof).
## 7 OUTPUT CONTRACT — target architecture + 3–7 shippable waves + delete list
+ risk map + per-wave VERIFY. ## 8 QUALITY WRAP … ## 9 SELF-SCORE … ## 10 VERIFY …
```

---

## NEXT

Ω done → SCORE (ultra rubric) → SHIP batch → report. No RUN-ORDER, no P2–P5.
Refine mode: `--refine <slug>` re-runs only the weakest SECTION(S) of the grammar, not
whole passes — read the score breakdown in `COMPILE-REPORT.md` to pick them.
