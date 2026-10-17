---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Signal to Mode

source: genesis/SKILL.md#selector-logic

The SELECTOR LOGIC table maps input signal to MODE and entry point. STATE "PRESET: [signal matched]" before starting.

| Signal | MODE | Entry point |
|--------|------|------------|
| No existing direction; problem is open | FULL | Phase 1 EXPLODE (20-idea minimum) |
| 1-4 directions exist but none committed | FULL | Phase 2 STRUCTURE (still enforce 20+ ideas minimum; do not skip EXPLODE) |
| Plan or approach exists; needs stress-test | EXPRESS | Phase 3 DEEPEN (ULTRATHINK only) |
| Two specific approaches exist; need merge | EXPRESS | Phase 4 SYNTHESIZE |
| Session is ending; nothing captured yet | EVOLVE-ONLY | Phase 5 EVOLVE |
| Output already delivered; quality check needed | REVIEW | Phase 3 DEEPEN + Phase 4 emergence test |

### How to apply SELECTOR LOGIC

1. Read the input. Identify which row the signal matches.
2. STATE "PRESET: [signal matched]" — e.g., "PRESET: two specific approaches exist; running EXPRESS from Phase 4."
3. Enter at the indicated phase. Do not revisit phases earlier in the dependency graph unless a gate fails and sends you back.
4. EVOLVE always runs regardless of which entry point was used.

### Common misroutes

**Misroute 1:** Using FULL when the problem already has 1-4 candidates. This wastes time re-generating ideas that already exist. Correct route: FULL starting at Phase 2 STRUCTURE (keeping the 20-idea minimum but using existing ideas as the seed).

**Misroute 2:** Using EXPRESS for "no existing direction." EXPRESS with no prior direction skips the idea generation that breaks out of the first framing. Correct route: FULL from Phase 1.

**Misroute 3:** Using REVIEW on a problem that has not yet passed ULTRATHINK. REVIEW applies DEEPEN + emergence test to an existing plan. If the plan was never stress-tested, it needs EXPRESS, not REVIEW.

**Misroute 4:** Running any MODE without EVOLVE. EVOLVE is not a MODE option — it is mandatory in every MODE. STATE "MODE: FULL + EVOLVE" not "MODE: FULL (EVOLVE optional)."
