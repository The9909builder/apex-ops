---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Variables

source: genesis/SKILL.md#state-tracker

Emit on each phase transition: "STATE: phase=[N] | ideas=[count] | candidates=[count] | ultrathink=[pass/fail] | emergence=[named/null] | evolve=[done/pending] | blocked=[null/reason]"

| Variable | Initial | What updates it |
|----------|---------|----------------|
| `CURRENT_PHASE` | 0 | Set to 1-5 on phase entry |
| `IDEAS_GENERATED` | 0 | Increment per idea; must reach 20 before Phase 2 gate passes |
| `CANDIDATES_SELECTED` | 0 | Set after Phase 2 Goldilocks filter; must be 5+ |
| `ULTRATHINK_PASSED` | false | Set to true when U+T+N answered in ONE specific sentence for top candidate |
| `EMERGENCE_NAMED` | false | Set to true when Z sentence is complete and non-vague |
| `EVOLVE_WRITTEN` | false | Set to true after mind_remember confirmed OR learnings.jsonl entry confirmed |
| `MODE` | FULL | Set in MODE DECLARATION before Phase 1 |
| `BLOCKED_AT` | null | Set to "Phase [N]: [reason]" when recovery is needed |
| `MIND_API_AVAILABLE` | unknown | Set to true/false after TOOL AVAILABILITY CHECK |

---

## Transitions

source: genesis/SKILL.md#state-tracker

Emit STATE on every transition. A transition without a STATE emission means the phase was silently skipped — this is the anti-pattern the STATE tracker exists to prevent.

| Transition | Required STATE content |
|-----------|----------------------|
| Entering Phase 1 EXPLODE | phase=1, ideas=0, mode=[set mode] |
| Exiting Phase 1 (gate passed) | phase=1->2, ideas=[count >=20], 3+ labeled uncomfortable |
| Entering Phase 2 STRUCTURE | phase=2, ideas=[final count] |
| Exiting Phase 2 (gate passed) | phase=2->3, candidates=[count >=5], all have specific first_action |
| Entering Phase 3 DEEPEN | phase=3, candidates=[count], ultrathink=pending |
| Exiting Phase 3 (gate passed) | phase=3->4, ultrathink=pass, U=[one sentence], T=[one sentence], N=[one sentence] |
| Entering Phase 4 SYNTHESIZE | phase=4, ultrathink=pass |
| Exiting Phase 4 (gate passed) | phase=4->5, emergence=named, Z=[Z sentence] |
| Entering Phase 5 EVOLVE | phase=5, emergence=[named/null], evolve=pending |
| Exiting Phase 5 (complete) | phase=5, evolve=done, mind_remember=[UUID confirmed] OR evolve=learnings.jsonl |
| Any gate failure | blocked=[Phase N: reason], CURRENT_PHASE stays at N |
| Escalation to L2 | blocked=[Phase N: twice], routing=realthink, handoff=[what was passed] |
