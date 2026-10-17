---
last_verified: 2026-09-20
freshness_clock: 2026-09-20
synthesized: true
source_basis: "HOS Comprehensive Reference Manual (operator-provided): section 4, the 5-Loop Execution Pipeline and Execution Checklist"
confidence: "0.9"
forge_domain: "human-operating-system"
fill_hint: "The runtime pipeline: each loop's question, method, marker line, and the five-check gate."
---

## The 5-Loop Execution Pipeline

The runtime where strategy meets action. Each loop answers one question, uses one
method, and emits one marker line. Marker lines make the run machine-checkable;
a loop that cannot emit its marker honestly is a failed loop, and the run stops.

### Loop 1: Observation (The Friston Loop)

- **Question:** what is actually true of the system right now?
- **Method:** minimize prediction error by updating the internal model through
  sensory states. Observe the environment as it is, not as the model expects.
- **Method detail:** stocks before stories. Calendar, ledger, health data, repo
  activity, throughput. Interview states (when energy rises and drains, what
  inputs arrived), not narratives (what it all means).
- **Emits:** `Evidence:` line, at least two observed states with sources.
- **Fails to:** every later loop; an unobserved system produces fiction.

### Loop 2: Orientation (The Alexander Loop)

- **Question:** where is the potential life?
- **Method:** identify the Centers of highest potential. Locate the localized
  zone of coherence that requires intensification, reading field effects
  (strengthens or depletes surroundings) rather than loudness.
- **Emits:** `Centers:` line naming the center(s) and their field effect.
- **Fails to:** aiming at symptoms instead of structures.

### Loop 3: Decision (The Meadows Loop)

- **Question:** where is the leverage, and at what level?
- **Method:** determine whether the intervention requires a change in numbers
  (stocks), a change in information flow, a change in rules, or a change in
  paradigm. Weakest to strongest; match level to loop type.
- **Emits:** `Leverage:` line naming loop type and intervention level.
- **Fails to:** the pesticide trap (see anti-patterns.md, linear-fix-trap).

### Loop 4: Action (The Craft Loop)

- **Question:** what gets made, with which property?
- **Method:** engage structural coupling through precise technê. Perform the
  intervention using the 15 properties so the result is a living structure the
  system can run without you.
- **Emits:** `Intervention:` block naming the property applied and the center
  intensified.
- **Fails to:** advice-giving; ungrounded recommendations are not action.

### Loop 5: Integration (The Middle Way Loop)

- **Question:** what did making this teach the model?
- **Method:** assess the roughness of the result. Acknowledge irregularities,
  update the internal model, and remain provisional: belief, evidence, revision
  condition, all in one line.
- **Emits:** `Provisional:` line with one model update and one revision condition.
- **Fails to:** oscillation on the next cycle; dogma re-forms silently.

## The Execution Checklist (Five-Check Gate)

Run before closing any intervention:

- [ ] **FEP Check:** does this action minimize systemic surprise, or create a
      reinforcing loop of uncertainty?
- [ ] **Meadows Check:** am I applying a linear fix (pesticide) to a non-linear
      problem (predator-prey balance)?
- [ ] **Alexander Check:** does this intervention create a thick boundary, or
      cause boundary thinning?
- [ ] **Burkeman Check:** is this a high-value use of the remaining 4,000 weeks,
      or an efficiency-paradox trap?
- [ ] **Ellis Check:** am I holding this decision provisionally, or have I
      absolutised my current belief?

## Loop-to-Engine Map

| Loop | Primary engines | Note |
|---|---|---|
| 1 Observation | Perception, Inference | Model update before anything |
| 2 Orientation | Valuation, Scale-Mapping | Potential life, not loudness |
| 3 Decision | Feedback | Loop type and leverage level |
| 4 Action | Repetition, Contrast, Coupling | Technê on real material |
| 5 Integration | Integration | Provisionality institutionalized |
