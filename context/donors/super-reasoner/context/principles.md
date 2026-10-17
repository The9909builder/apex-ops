---
last_verified: 2026-07-10
freshness_clock: 2026-07-10
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.5"
forge_domain: "super-reasoner"
fill_hint: "5 grounded principles; each cites a reason it is true (not 'best practice'), is falsifiable on a new case, and produces a concrete change when applied."
---

## Principles
source: super-reasoner/SKILL.md#Principles

1. **Malformed questions get transformation, never answer synthesis.** True because a malformed
   question (false dichotomy, category error, unestablished presupposition) cannot be correctly
   answered as stated; any fluent EXECUTION answer to it launders the confusion. Falsifiable: if
   a question with 2+ malformation signatures were correctly answerable directly, this
   principle would be wrong. Applied: routes straight to MODE: EXPLORATION, never EXECUTION.

2. **Satisficing risk is scored independently of malformation, always.** True because
   well-formed and low-risk are not the same property; a contested normative question can parse
   perfectly and still be a trap. Falsifiable: if risk score always tracked malformation count
   1:1 across real questions, TIER D would be dead code (see `axes-collapse-invalidates-tier-d`
   in spec.yaml). Applied: the risk scan runs even when malformation count is 0.

3. **Phase 0 runs on every input, unconditionally.** True because it costs only a few sentences
   and skipping it is the exact mechanism by which a high-risk question sneaks through the fast
   path. Falsifiable: any DONE output that never shows a `MODE:` line violates it and should be
   treated as BLOCKED, not DONE. Applied: no answer is produced before classification.

4. **Depth is earned by the risk score, never defaulted to "more is safer."** True because
   forcing TIER D onto a low-risk question wastes effort without reducing error, since there is
   no plausible wrong answer to catch at TIER S. Falsifiable: if TIER D output on a TIER
   S-scored question produced a measurably better answer than TIER S alone, this principle
   would be wrong. Applied: TIER S self-corrects only on a missed symptom, never on suspicion.

5. **Every EXECUTION answer ends with a falsifiability statement.** True because an answer that
   cannot state what would prove it wrong is unfalsifiable speculation, not reasoning, and
   cannot be checked later against reality. Falsifiable: an output marked DONE with no
   falsifiability conditions listed is not actually done. Applied: TIER S needs 1 condition,
   TIER M needs 3, TIER D needs the full destruction checklist before delivery.
