---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Required Sections

source: genesis/SKILL.md#output-template

The required sections must appear verbatim in every GENESIS synthesis delivery. Missing sections mean Phase 4 output is not accepted.

```markdown
## SYNTHESIS RESULTS

### Core Insights
- **Shared DNA:** [pattern connecting the sources — what all candidates have in common]
- **Gaps Filled:** [what each source adds that others lack — organized by contribution, not by source name]
- **Emergence:** [new capability that exists only in combination — the Z sentence: "A+B enables Z which neither alone can do because [reason]"]

### Concrete Build
| Attribute | Detail |
|-----------|--------|
| **Name** | [name of the synthesis output] |
| **Type** | Tool / Protocol / System / Framework |
| **Description** | [one paragraph; what it does; for whom] |
| **First Action** | [ONE specific command, file edit, or tool call to start] |

### Next Actions
1. [Action 1 — specific artifact named]
2. [Action 2 — specific artifact named]
3. [Action 3 — specific artifact named]
```

---

## Delivery Format

source: genesis/SKILL.md#completion-status-protocol

Every GENESIS session closes with ONE of these status lines:

- **DONE:** completed with evidence. Include: Z sentence, quality rubric scores, EVOLVE confirmation.
- **DONE_WITH_CONCERNS:** completed; list concerns. Name the rubric dimension that scored < 3 and why.
- **BLOCKED:** cannot proceed. State: what phases ran, what techniques were tried, what gate blocked each candidate.
- **NEEDS_CONTEXT:** missing information. State exactly what is needed before GENESIS can continue.

Format: `STATUS | REASON | ATTEMPTED | RECOMMENDATION`

**Example DONE delivery:**
```
DONE | Z: "EXPLODE + STRUCTURE enables non-obvious candidate selection which intuition alone cannot do because intuition stops diverging after idea 3" | rubric: divergence=5, ultrathink=4, emergence=5, evolve=5 | EVOLVE written to mind_remember UUID 550e8400
```

**Example DONE_WITH_CONCERNS:**
```
DONE_WITH_CONCERNS | EVOLVE: Mind API down, wrote to learnings.jsonl with pending_mind_sync=true | phases 1-4 complete | recommend: restart Mind API and sync pending entry before next session
```
