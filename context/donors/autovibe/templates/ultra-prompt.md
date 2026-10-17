# ULTRA-PROMPT TEMPLATE (v1.0.0 — fill every {{slot}}; delete no section)

> Compiler notes (strip from final output): §0–§10 map to ultra.md grammar. Budget:
> capsule ≤ ~2k tokens, whole doc ≤ ~5k. The FIVE load-bearing sections that must never
> be thinned: §0 pre-generation ground form, §5 floor, §6 stage artifacts, §7 contract,
> §9 gate. §0 MUST be emitted before §1 — that ordering is the v1.0 anti-anchoring mechanism
> (the gate's check 8 BLOCKS when §0 is absent, thin, or positioned after §1).

# ULTRA PROMPT — {{system_name}} → {{v_next_name}}

## §0 — PRE-GENERATION GROUND FORM
*(Complete ALL fields before reading §1. The ordering is the mechanism — causal attention is
directional: constraints placed here shape what gets generated; the same constraints placed
after §1–§4 fight a residual stream already committed to a direction. Skip this and every
recommendation is first-draft anchored.)*

**VIA-NEGATIVA — complete first (honesty decays after direction-commit):**
1. [ ] This change CANNOT {{cannot_1 — a hard boundary / invariant it must not break}}
2. [ ] This change CANNOT {{cannot_2}}
3. [ ] This change CANNOT {{cannot_3}}
4. [ ] "{{plausible_move_1}}" LOOKS right but is a TRAP because {{why_it_is_a_trap}}
5. [ ] "{{plausible_move_2}}" LOOKS right but is a TRAP because {{why}}
6. [ ] "{{plausible_move_3}}" LOOKS right but is a TRAP because {{why}}
7. [ ] Assumption that BREAKS the approach: "{{load_bearing_assumption}}" — {{why it is false}}
8. [ ] Strongest adversarial OBJECTION: "{{best_counter_argument}}". Rebuttal: {{rebuttal}}

**POSITIVE-GROUND — complete second (constrained by the via-negativa above):**
1. Evidence: {{file_or_metric_or_incident_1}} — {{what it shows}}
2. Evidence: {{file_or_metric_or_incident_2}} — {{what it shows}}
3. First principle: {{the irreducible truth this rests on}}
4. Measurable success: {{the falsifiable check that proves it landed}}
5. Scope: {{the exact files/systems in bounds — and what is explicitly out}}

## 1 — ROLE & STAKES
You are the principal architect of {{system_name}}, with full authority to make breaking
changes. Your mandate: design the next whole version, not improvements to this one.
"Great" for this system means: {{one_sentence_definition_of_great}}.
**Anti-goal:** proposals at the level of renames, lint fixes, config flags, or single-file
refactors are failures. The smallest acceptable unit of change is architectural.

## 2 — CONTEXT CAPSULE (current state — compressed, ≤2k tokens)
**Components & jobs:** {{component_list_one_line_each}}
**Data/control flows:** {{flows}}
**INVARIANTS (must survive the transformation):** {{strengths_as_invariants ≥3}}
**CRACKS (with evidence):** {{cracks_with_evidence ≥3}}
**Constraints:** REAL: {{real_constraints}} · ASSUMED (challengeable): {{assumed_constraints}}
Deeper detail lives at: {{file_paths_links}} — read on demand, do not guess.

## 3 — CRUX
{{one_sentence_grounded_bottleneck}}
Evidence: {{crux_evidence_line}}
Every wave you propose must help dissolve this. Changes that don't touch the crux are out of scope.

## 4 — NORTH-STAR CHARTER + DESIGN VECTORS
Charter: **{{differentiation_charter_one_sentence}}**
Vectors (verbatim — these outrank every existing convention of the current system):
{{#each design_vectors}}V{{n}}. {{vector_one_line}}
{{/each}}
Every wave must cite the vector it serves.

## 5 — AMBITION CALIBRATION
**FLOOR (reject below):** if your full proposal could be executed in under a day, it is
below the floor — discard it and restart at Stage A. Below-floor examples for this system:
{{below_floor_examples e.g. "adding a flag to X", "wrapping Y in a helper"}}.
**CEILING (aim at):** {{v_current}} → {{v_next_name}}. State the capability delta in user terms.
**DELETE LIST (seed — you must extend it):**
{{transcend_removals_list}}
Deletion before addition: what does {{v_next_name}} refuse to carry forward?

## 6 — THINKING PROTOCOL (run all stages; emit each artifact BEFORE your answer)
- **Stage A — First-principles teardown.** The system's irreducible job in one sentence;
  then list every current structure NOT entailed by that job. *Artifact: teardown list.*
- **Stage B — 5-step on each crack** (Question → Delete → Simplify → Accelerate → Automate).
  *Artifact: crack × 5-step table.*
- **Stage C — Second-order ripple.** For each candidate change: what becomes possible that
  wasn't before? *Artifact: ripple list.*
- **Stage D — Three tiers.** T1 conservative / T2 structural / T3 reimagined — one-paragraph
  sketch + one risk line each. *Artifact: three sketches.*
- **Stage E — Forced selection.** Choose the HIGHEST tier that survives the risk map and the
  INVARIANTS. Choosing below T3 requires written proof the higher tiers break a named
  invariant — "safer" is not an argument. *Artifact: selection + proof.*
A stage without its artifact = skipped = invalid response.

## 7 — OUTPUT CONTRACT (your answer must contain ALL of these)
a. **Target architecture** of {{v_next_name}} + capability delta ({{v_current}} → {{v_next_name}}) in user terms.
   Each line: `[file:section] — [what changes] (grounded in: [§0 evidence item or design vector])`
b. **Migration waves** (3–7) — each independently shippable, each citing its design vector
c. **Completed DELETE LIST** (seed from §5, extended)
d. **Risk map** — each wave's hurdle + mitigate/accept decision
e. **Per-wave VERIFY** — one concrete check proving the wave landed
**CLAIM-LEVEL GROUNDING:** every recommendation cites ≥1 §0 evidence item or design vector
as `grounded in: …`. A recommendation you cannot anchor is not yet knowledge — convert it to
`EXPERIMENT: [hypothesis] | TEST: [check] | SIGNAL: [observable]` before the answer is complete.
An answer missing any of a–e, or carrying an unanchored recommendation, is incomplete. Do not present it.

## 8 — QUALITY WRAP
- Do not preserve existing structure out of politeness — preserve only the INVARIANTS in §2.
- Breaking an invariant requires naming it and justifying against the charter. No silent breakage.
- No rewrite-for-rewrite's-sake: every wave cites a crack (§2) or a vector (§4).
- No big-bang wave: each wave must ship and verify alone.
- Anti-slop: no god-modules; no premature abstraction; no vague names ({{banned_names e.g. data/helper/manager/util}}); errors surface, never swallowed.
{{stack_specific_guards_optional}}

## 9 — SELF-SCORE GATE (apply before presenting; any "no" → return to Stage A)
1. Did you complete §0 (via-negativa + positive-ground) BEFORE reading §1 — or did the answer anchor first and rationalize §0 after?
2. Does the proposal dissolve the CRUX (§3)?
3. Is the selected tier the highest viable (proof present if below T3)?
4. Does every wave cite a vector AND ship independently?
5. Is the DELETE LIST extended beyond the seed?
6. Is every INVARIANT intact or explicitly traded with justification?
7. Is every recommendation anchored (`grounded in: …`) or framed as an `EXPERIMENT:`?

## 10 — VERIFY (for the human reading the answer)
The answer must contain ≥3 deletions, ≥1 second-order capability, and a stated
{{v_current}} → {{v_next_name}} delta. If it reads like a code-review comment list,
the prompt failed — refine via `/autovibe --refine {{slug}}`.
