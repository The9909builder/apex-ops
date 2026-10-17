<!--
TEMPLATE: ultra-pack-reason.md  →  fill into ~/prompt-packs/<slug>/REASON.md
This is the REASONING MACHINE. The compiler fills the {{...}} slots from the IR
(GROUND crux + PRIOR-ART/SYSTEM RECON + DECOMPOSE lists + TRANSCEND charter/vectors).
It is NOT a plan. It is a prompt that makes the executing LLM DERIVE the genius plan,
prove it, then emit the research→deploy execution prompts. Keep ≤ ~6k tokens.
Section order is load-bearing: §0 MUST precede §1 (anti-anchoring). Gate: autovibe-gate.sh ultra-pack
-->

# REASON: {{intent_title}}

> Paste this entire file into a strong reasoning LLM. It will reason out WHAT to build, HOW,
> and the smartest/genius way — prove the choice — then emit the full research→deploy prompts.
> Do not answer the sections in your own voice; you ARE the executing LLM the moment you read §1.

---

## §0 — GROUND FORM (complete this FIRST, before reading §1)

**VIA-NEGATIVA (complete first):**
- CANNOT: {{≥3 hard boundary lines — what this build must never do/assume}}
- TRAP / BREAKS: {{≥3 plausible-looking moves that look smart but break this — the obvious wrong turns}}
- OBJECTION + rebuttal: {{≥1 adversarial objection to the whole premise, and the rebuttal}}

**POSITIVE-GROUND (complete second, constrained by the above):**
- Evidence: {{≥2 grounded facts — a real user need, a market signal, a constraint, a prior-art gap}}
- First principle: {{the irreducible truth this build rests on}}
- Measurable success: {{the one number/observable that says "this worked"}}
- Scope: {{what is in, what is explicitly out, for v1}}

---

## §1 — ROLE & STAKES

You are a **principal architect with full authority to choose the architecture, stack, and
shape of this system from scratch** (or to rearchitect what exists). "Great" for THIS build
means: {{one-sentence definition of great for this intent}}.

**Anti-goal:** a plan that just names the obvious stack and CRUD screens is a failure. The
smallest acceptable unit of thinking is *architectural* — you are choosing the bet the whole
system rides on, not picking a framework.

---

## §2 — CONTEXT CAPSULE  (≤ ~2,000 tokens)

- **The job-to-be-done:** {{from RECON step 3 — one sentence}}
- **User × jobs:** {{P1 DECOMPOSE — who, and the top 3 jobs}}
- **Prior art + white space:** {{RECON — closest existing approaches, and the ≥2 gaps the smart build exploits}}
- **INVARIANTS (must hold):** {{≥3 things the build cannot violate — perf, trust, a core UX truth}}
- **Real constraints vs assumed:** {{label which constraints are real (budget, platform, time) vs assumed (everyone-uses-X)}}

Link out to sources/paths instead of pasting bulk.

---

## §3 — CRUX

The one constraint the whole build must dissolve: **{{grounded crux from PASS 0.0, one sentence}}**.
Evidence: {{the line that grounds it}}. Any plan that doesn't move THIS is rejected at §9.

---

## §4 — NORTH-STAR CHARTER + DESIGN VECTORS

Charter (specific / defensible / user-cares): **{{TRANSCEND charter, one sentence}}**.
Design vectors (quote verbatim, every wave must cite one):
- {{vector 1}}
- {{vector 2}}
- {{vector 3}}

These vectors outrank any default convention or "best practice" — if a convention fights a
vector, the vector wins; say so.

---

## §5 — AMBITION FLOOR

- **FLOOR (reject below):** If your plan is the obvious build any competent dev would produce —
  the standard CRUD app, the textbook stack, the first architecture that comes to mind — it is
  BELOW THE FLOOR. Discard and restart at Stage A. The genius move is the non-obvious
  architecture that makes the hard thing trivial or deletes a whole problem class.
  Below-floor for THIS intent looks like: {{example 1}}; {{example 2}}.
- **CEILING (aim at):** {{the "how is this even possible" capability — the genius delta, one line}}.
- **DELETE-LIST seed (extend this):** the smart build refuses to carry: {{≥2 things the obvious
  build would include but this one deletes}}. Deletion before addition.

---

## §6 — THINKING PROTOCOL  (staged, visible, unskippable — emit each artifact BEFORE the plan)

A stage with no emitted artifact counts as skipped → restart.

- **Stage A — Irreducible job (first principles).** State the job in one sentence. List the
  MINIMUM capability set that satisfies it. Artifact: the minimum-set list. Everything outside it
  is a deletion candidate.
- **Stage B — Solution-space divergence.** Generate **≥3 genuinely different architectures** that
  satisfy the job — different core bets, not variations of one. Artifact: an `approach × core-bet ×
  what-it-makes-trivial` table. Converging to one approach here is forbidden.
- **Stage C — Second-order ripple.** For each approach: what becomes POSSIBLE that wasn't, and
  what whole problem class does it DELETE? Artifact: ripple line per approach. The best builds win
  on second-order effects.
- **Stage D — Three-tier framing.** Label them **T1 obvious/safe · T2 smart · T3 genius/reimagined**.
  Artifact: one-paragraph sketch + the core bet + the risk line for each tier.
- **Stage E — Forced selection.** Select the HIGHEST tier that survives the INVARIANTS (§2) and the
  real constraints. Choosing T1 or T2 requires WRITTEN PROOF that T3 breaks a real constraint —
  *"the obvious approach is safer"* is not an argument, it is the anchoring bias this protocol
  defeats. Artifact: chosen approach + the proof line.

---

## §7 — OUTPUT CONTRACT  (reason, THEN emit the prompts — both, in order)

Produce, in this order:

**(a) THE DERIVED PLAN**
- WHAT: the selected approach (§6 Stage E) in plain terms.
- HOW: the architecture + stack, each choice with its one-line rationale (NOT "because it's
  popular" — because it serves a vector or dissolves the crux).
- WHY GENIUS: the Stage E proof — why this beats the obvious build, restated for the user.

**(b) THE LIFECYCLE EXECUTION PROMPTS** — generate one self-contained prompt per stage FROM plan (a).
Each prompt carries its own CONTEXT · ACTION · TARGET · CONSTRAINTS · QUALITY-WRAP · VERIFY:
1. **RESEARCH** — validate the single riskiest assumption in the plan before any code. State the
   kill-criteria: what result means "stop, the plan is wrong".
2. **SETUP** — scaffold + repo + env + the chosen stack wired until "hello world runs end-to-end".
3. **BUILD** — the capabilities in dependency order; each capability is independently shippable and
   has its own VERIFY. Cite the design vector each one serves.
4. **DEPLOY** — ship it live: the deploy target, the pipeline, the rollback plan.
5. **VERIFY** — the falsifiable checks proving each stage landed, plus the BUILD RECEIPT line below.

**(c) RUN-ORDER** — the exact order to paste the (b) prompts, and what each stage hands the next
(its outputs become the next stage's inputs).

An answer missing (a), (b), or (c) is incomplete — say so and complete it. The plan alone is an
opinion; the prompts alone are a prescription with no reasoning behind them.

---

## §8 — QUALITY WRAP

- Preserve only the named INVARIANTS (§2) — do not gold-plate or add structure out of habit.
- Anti-slop: no god-modules, no premature abstraction, no vague names, no framework cargo-cult.
- Every BUILD capability cites a crack/vector; no capability exists "because apps usually have it".
- No big-bang: every BUILD step ships and verifies alone.

---

## §9 — SELF-SCORE GATE  (apply to your OWN output before presenting)

- Crux (§3) dissolved by the plan? 
- Highest viable tier chosen, with written proof if below T3?
- Plan **DERIVED** (Stage E proof present) and not merely asserted?
- §7 emitted (a) plan AND (b) all five lifecycle prompts AND (c) run-order?
- All INVARIANTS intact or explicitly traded with justification?

**Any "no" → return to Stage A. Do not present.**

---

## §10 — VERIFY (the user runs this on your answer)

The prompt worked if your answer: derives ≥3 distinct approaches, proves the chosen tier, names
≥2 deletions, and emits 5 self-contained lifecycle prompts with their own VERIFY checks. If it
reads like a single generic "here's how I'd build it" plan with no emitted prompts, the contract
failed — refine via `/autovibe --refine {{slug}}`.

---

## BUILD RECEIPT (close autovibe's loop with a REAL outcome)
After you (or a downstream executor) run the emitted prompts and the VERIFY checks, report back so
autovibe learns from what actually built:

  ~/.kraken/outcomes/receipt-ingest.sh --slug {{slug}} --result pass|fail|partial \
    --probe "<the VERIFY check you ran>" --sections "§5,§6,§7"

If you cannot run it, paste the result and a human fires `/autovibe --outcome {{slug}} good|bad`.
