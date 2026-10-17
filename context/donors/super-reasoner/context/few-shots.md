---
last_verified: 2026-07-10
freshness_clock: 2026-07-10
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.5"
forge_domain: "super-reasoner"
fill_hint: "3 worked examples (input task -> good output -> annotation that explains WHY via a domain MECHANISM, using the word 'because')."
---

## Example 1
source: super-reasoner/SKILL.md#Patterns (TIER S)

Input: "What's the capital of France?"

Good output: `MODE: EXECUTION`, `TIER (if EXECUTION): S`, then a direct answer plus one
falsifiability condition ("this would be wrong if the question meant a historical capital, not
the current one").

Annotation: this stays TIER S because the satisficing risk score is genuinely near zero: no
domain expert would pause at the answer, nothing about it is contested, and getting it wrong
would be immediately obvious. Running full multi-lens synthesis here would be Depth Theater,
because the machinery exists to catch a plausible-but-wrong answer, and there is no plausible
wrong answer to catch.

## Example 2
source: super-reasoner/SKILL.md#Patterns (EXPLORATION)

Input: "Is remote work good or bad for company culture?"

Good output: `MODE: EXPLORATION`, malformation signature "false dichotomy" named explicitly,
then exactly 5 incompatible reformulations, zero answer given.

Annotation: this cannot go to EXECUTION at all, because the question assumes a binary
(good/bad) that the real answer is context-dependent on. Answering it directly, even with
nuance, would be Coherent Malpractice: it would launder the false dichotomy instead of
surfacing it. The 5 reformulations exist specifically to expose which hidden assumption the
user actually means.

## Example 3
source: super-reasoner/SKILL.md#Patterns (TIER D)

Input: "Is centralized or decentralized governance more resilient to systemic shocks?"

Good output: `MODE: EXECUTION`, `TIER (if EXECUTION): D`, four ontologically distinct lenses
(e.g. physical/biological/social/computational), a DNA check-equivalent destruction checklist,
and a one-sentence falsifiable meta-precondition before the final verdict.

Annotation: this routes to TIER D and not TIER S, because it is well-formed (no malformation
signature fires) but scores high satisficing risk: it is contested, it has a textbook-sounding
"decentralization is more resilient" consensus answer practitioners privately doubt, and
getting it wrong in a real system-design decision would be expensive. Malformation and risk are
independent here: a perfectly parseable question still earns the deepest tier.
