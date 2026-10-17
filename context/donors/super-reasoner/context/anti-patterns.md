---
last_verified: 2026-07-10
freshness_clock: 2026-07-10
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.5"
forge_domain: "super-reasoner"
fill_hint: "The 5-8 most common domain failures; each: the failure pattern -> why it fails -> the corrected version."
---

## Failure Modes
source: super-reasoner/SKILL.md#Anti-Patterns

- **Coherent Malpractice**: answering a malformed question smoothly, no reformulation offered.
  Fails because a malformed question cannot be correctly answered by construction; a fluent
  answer launders the confusion instead of exposing it. Corrected: route to MODE: EXPLORATION,
  return exactly 5 incompatible reformulations, give no answer.

- **Premature Synthesis**: satisficing symptoms fire (textbook-safe tone, urge to conclude) and
  the response still jumps straight to a tidy answer. Fails because a well-formed question is
  not automatically a safe one; skipping the risk scan when malformation is zero is exactly how
  a hard question sneaks through the easy door. Corrected: always run the risk scan, route by
  score, not by malformation alone.

- **Depth Theater**: running full TIER D multi-lens machinery on a question that scored risk
  <=2, "to be safe." Fails because more depth is not always safer; it burns the user's patience
  on a problem that never existed. Corrected: trust TIER S when risk is genuinely low; use the
  inline self-correction check (stop and escalate only if a missed symptom actually surfaces)
  as the safety valve instead of blanket over-depth.

- **Baseline-Last Adversarial Testing**: writing the "Obvious Answer" baseline after the
  precondition attack instead of before, in TIER M or TIER D. Fails because it lets the
  "adversarial testing" quietly converge back onto the baseline instead of independently
  attacking it; the DNA check becomes meaningless if the baseline was written to already match
  the answer. Corrected: baseline first, always, before any precondition is attacked.

- **Guessing EXECUTION on an Ambiguous MODE**: forcing a MODE: EXECUTION classification when
  Phase 0's malformation and risk scores are both genuinely uncertain. Fails because EXECUTION
  on a secretly-malformed question produces confident garbage that reads as reasoned (see
  `mode-detection-fails`). Corrected: default to EXPLORATION when uncertain; it is always the
  safe fallback and forces user clarity instead of a guess.

- **Unbounded Recursive Reformulation**: letting an EXPLORATION reformulation that is itself
  malformed recurse without a depth cap. Fails because it never returns control to the user.
  Corrected: recurse at most to depth 3, then state `EMPIRICAL FLOOR REACHED` and hand the
  normative commitment back to the user.
