---
last_verified: 2026-07-10
freshness_clock: 2026-07-10
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.5"
forge_domain: "super-reasoner"
fill_hint: "10-term domain glossary, recommended reading order of the artifacts, and a DOMAIN-AGNOSTIC 5-step bootstrap recipe."
---

## Glossary
source: super-reasoner/SKILL.md#Workflow + #Patterns

- **MODE**: the top-level routing decision from Phase 0: EXPLORATION, HYBRID, or EXECUTION.
- **TIER**: the depth level within MODE: EXECUTION only: S, M, or D.
- **EXPLORATION**: the MODE for malformed questions; produces reformulations, never an answer.
- **HYBRID**: the MODE for a partially malformed question with a salvageable well-formed core.
- **EXECUTION**: the MODE for well-formed questions; always carries a TIER.
- **well-formed**: a question free of malformation signatures (no false dichotomy, category
  error, presupposition failure, infinite regress, underdetermination, or premature
  optimization).
- **PHASE**: a numbered gated step within the workflow (Phase 0 Classify, Phase 1 Route and
  Execute, Phase 2 Verify) or within TIER D (D-0 through D-8).
- **DNA check** (or **zero-DNA check**): the TIER M/D gate asking whether the derived answer
  shares intellectual DNA with the Obvious Answer baseline; sharing DNA means the adversarial
  testing did not actually move the answer.
- **mode-detection-fails**: the sharp edge covering the case where Phase 0 cannot confidently
  classify MODE; resolved by defaulting to EXPLORATION.
- **DONE / BLOCKED**: completion-status values. DONE requires all phase gates passed with
  evidence; BLOCKED means a gate could not be satisfied and the reason is stated.

## Reading Order
source: super-reasoner/SKILL.md (structural)

1. SKILL.md Identity + Principles: why the two-axis (malformation x risk) design exists.
2. SKILL.md Workflow: the 3 gated phases (Classify, Route and Execute, Verify).
3. context/taxonomy.md: the 5 named modes/tiers and when each applies.
4. SKILL.md Patterns (or context/few-shots.md): the full worked protocol for each mode/tier.
5. context/anti-patterns.md: the failure modes to recognize and correct in real time.
6. SKILL.md Sharp Edges: the recovery procedures for stuck states (loops, unfalsifiable
   synthesis, recursive malformation).

## Bootstrap Recipe
source: super-reasoner/SKILL.md (derived, domain-agnostic)

1. Decompose the input into its explicit ask, implicit assumptions, and category.
2. Scan for the domain's known malformation signatures; count them.
3. Independently scan for the domain's own satisficing-risk symptoms, even if step 2 found
   nothing: the two counts are separate axes, never assume one predicts the other.
4. Classify into the domain's named modes/tiers from the two counts, using the lowest tier that
   the risk score actually justifies, never the highest "to be safe."
5. Execute exactly the matched mode/tier's own protocol, and close every output with a
   falsifiability statement, at a depth proportional to that mode/tier, not the depth of the
   most demanding one.
