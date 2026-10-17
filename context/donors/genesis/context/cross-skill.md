---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Handoffs Out

source: genesis/SKILL.md#cross-skill-invocation-protocol

GENESIS does not own: problem-identification, prd-generation, execution-waves, research-gathering. On any handoff trigger, STATE "SCOPE: out of bounds — [condition]; routing to [target]" before stopping.

### To realthink
**Trigger:** Real problem statement is still unclear after Phase 1 completes; U answer cannot be distinguished from the stated problem.
**What to pass:** `idea_list` (all 20+ ideas), `top_candidates` (top 3 with partial ULTRATHINK), `stated_problem`.
**What to receive:** `one_lever` (the real problem realthink identified).
**Resume:** Enter Phase 3 DEEPEN with realthink's lever as the U answer. Do NOT re-run Phases 1-2.

### To think-pipeline
**Trigger:** Emergence Z is named and now needs a 7-slot executable plan.
**What to pass:** `emergence_Z` (the named new capability), `first_action`, `problem context`.
**What to receive:** Filled 7-slot schema.
**Resume:** Do not re-run GENESIS after. think-pipeline output is the plan. GENESIS has completed.

### To vague-to-system
**Trigger:** Synthesis produces a new framework that needs formalization as a system.
**What to pass:** Synthesis result, framework name, extracted principles, evolution log.
**Resume:** Do not re-run GENESIS. vague-to-system formalizes; GENESIS does not.

### Scope guard (boundary contract)
Does not own: problem-identification (route to realthink), prd-generation (route to idearalph_prd), execution-waves (route to vague-to-system or build skill), research-gathering (route to spawner_analyze or Agent tool).

NEVER attempt in-scope emulation of an out-of-bounds task. If research is needed, stop and route before EXPLODE starts.

---

## Handoffs In

source: genesis/SKILL.md#provides-to-receives-from

### From realthink
**When:** ONE leverage move has been identified; creative solution space exploration is needed.
**What arrives:** The ONE lever realthink identified with its root cause.
**What GENESIS does with it:** Enters Phase 1 EXPLODE (FULL mode) or Phase 3 DEEPEN (EXPRESS mode) with the lever as the starting U answer.

### From think-pipeline
**When:** 7-slot schema is filled and synthesis is needed before execution.
**What arrives:** Filled 7-slot schema as synthesis inputs.
**What GENESIS does with it:** Enters Phase 4 SYNTHESIZE treating the filled schema as the candidate set.

### From kraken-flow
**When:** GENESIS is called as the Phase 2 PLAN gate in an L4 kraken-flow pipeline.
**What arrives:** Problem statement + research phase outputs.
**What GENESIS returns:** Synthesis result Z + completed Concrete Build table (from Output Template).
