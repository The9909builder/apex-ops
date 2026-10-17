---
last_verified: 2026-07-10
freshness_clock: 2026-07-10
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.5"
forge_domain: "super-reasoner"
fill_hint: "List the 5-8 fundamental categories/types in this domain; each: name, definition, and a 'when to use' condition."
---

## Categories
source: super-reasoner/SKILL.md#Patterns

- **EXPLORATION**: the MODE fired when Phase 0's malformation count is 2 or more, or a single
  malformation has no salvageable core. Produces exactly 5 incompatible reformulations, never
  an answer.
- **HYBRID**: the MODE fired when malformation count is exactly 1 and a well-formed question
  survives underneath. Extracts the salvageable core, discloses the assumptions needed to
  answer it, then re-scores risk before routing to a TIER.
- **TIER S** (fast path): the EXECUTION tier for risk score <=2. Direct answer plus one
  falsifiability condition, no adversarial machinery.
- **TIER M** (standard adversarial): the EXECUTION tier for risk score 3-6, where most
  well-formed questions land. Baseline, precondition attack, synthesis, a DNA check against the
  baseline, then falsifiability.
- **TIER D** (deep multi-lens synthesis): the EXECUTION tier for risk score >=7. Four
  ontologically distinct lenses, precondition-level contradiction mining, one falsifiable
  meta-precondition, and a 7-item destruction checklist before delivery.

## When To Use
source: super-reasoner/SKILL.md#Workflow

- Use EXPLORATION when the question itself cannot be correctly answered as asked (a false
  dichotomy, a category error, an unestablished presupposition).
- Use HYBRID when only part of the question is confused and the rest is genuinely answerable.
- Use TIER S only when the risk score is genuinely low: textbook-safe, non-contested,
  low-stakes. Escalate mid-answer if a satisficing symptom surfaces that Phase 0 missed.
- Use TIER M for the ordinary case: a real, well-formed question with moderate stakes or mild
  contestedness, where an unverified "I tested this adversarially" claim would be unconvincing
  without a written baseline.
- Use TIER D only when risk is genuinely high, or when TIER M's precondition survival drops
  below 80%, or the DNA check shows the answer never actually left the Obvious Answer.
