---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Mode Decision Tree

source: genesis/SKILL.md#mode-declaration

Run this decision tree before Phase 1. STATE "MODE: [mode]" as first output line. STATE "PRESET: [signal matched]" before starting.

```
START
  |
  Does the problem have any committed direction?
  |
  NO → How many candidate directions exist?
       |
       ZERO → MODE: FULL | Entry: Phase 1 EXPLODE
       |
       1-4 (uncommitted) → MODE: FULL | Entry: Phase 2 STRUCTURE (keep 20-idea minimum)
  |
  YES → Is the direction already stress-tested by ULTRATHINK?
        |
        NO → Is it ONE direction or TWO+ directions to combine?
             |
             ONE → MODE: EXPRESS | Entry: Phase 3 DEEPEN
             |
             TWO+ → MODE: EXPRESS | Entry: Phase 4 SYNTHESIZE
        |
        YES → Does a synthesis output (Z sentence) already exist?
              |
              YES → MODE: REVIEW | Entry: Phase 3 DEEPEN + Phase 4 emergence test
              |
              NO → Is the session ending without any capture?
                   |
                   YES → MODE: EVOLVE-ONLY | Entry: Phase 5 EVOLVE
                   |
                   NO → MODE: EXPRESS | Entry: Phase 3 DEEPEN
```

### MODE Summaries

| MODE | Phases | Idea minimum | EVOLVE required |
|------|--------|-------------|----------------|
| FULL | 1→2→3→4→5 | 20 ideas before Phase 2 | Yes |
| EXPRESS | 1→3→5 (2+4 compressed into 3) | 15 ideas in Phase 1 | Yes |
| REVIEW | 3→4 only | None (no idea generation) | Yes |
| EVOLVE-ONLY | 5 only | None | The entire session IS EVOLVE |

**EVOLVE is never optional.** STATE "MODE: [mode] + EVOLVE" — not "EVOLVE optional." A mode declaration without EVOLVE is not a valid mode.

### Quick pre-session STATE declarations

```
# No direction, open problem
STATE "MODE: FULL" | STATE "PRESET: no existing direction — running all 5 phases; 20-idea minimum"

# One direction to validate
STATE "MODE: EXPRESS" | STATE "PRESET: ONE direction exists but unvalidated — entering at Phase 3 DEEPEN"

# Two approaches to merge
STATE "MODE: EXPRESS" | STATE "PRESET: two committed approaches — entering at Phase 4 SYNTHESIZE"

# Plan exists, needs quality gate
STATE "MODE: REVIEW" | STATE "PRESET: plan exists — applying ULTRATHINK + emergence test only"

# Session ending, no capture yet
STATE "MODE: EVOLVE-ONLY" | STATE "PRESET: session closing — EVOLVE is the only required output"
```
