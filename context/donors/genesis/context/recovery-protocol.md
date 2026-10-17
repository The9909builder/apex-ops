---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Recovery Actions

source: genesis/SKILL.md#recovery-protocol

One action per failure. Apply the action, then retry the gate once before escalating to the next ESCALATION LADDER level.

| Failure | Recovery action |
|---------|----------------|
| Phase 1: < 15 ideas | Apply CROSS-Domain Stealing first: name the core pattern of the problem, find an unrelated field that solved it, steal the mechanism. Do not advance. |
| Phase 1: all ideas feel like the same idea | Apply Role-Shifting: run Child, Criminal, Competitor. Extract the uncomfortable insight from each role. That insight is your divergence. |
| Phase 2: vague first_actions | For each candidate, name the specific file to edit, command to run, or tool to call. "Think about" and "explore" are not first_actions. |
| Phase 3: U = restatement of stated problem | Ask: "what breaks in the system if we solve the stated problem but this hidden one remains?" That answer is U. |
| Phase 3: T = improvement not capability | Ask: "what can users do after this ships that they literally cannot do today?" Name it specifically. That is T. |
| Phase 3: N is vague or multi-step | Ask: "what is ONE named command, file, or tool to call right now?" If multi-step, name only the FIRST step. |
| Phase 4: Z = weighted average | Restart SYNTHESIZE. Ask: "what task is impossible with only A, impossible with only B, but possible with both?" That task is Z. |
| Phase 4: output organized by source | Restart SYNTHESIZE. Reorganize output by the new capability (Z), not by input source. Do not name sections by input origin. |
| Phase 5: Mind API (port 8000) down | Write to learnings.jsonl directly with `"pending_mind_sync": true`. Do not skip EVOLVE — switch to fallback path. |
| Any phase: user pushes to skip gate | Name the anti-pattern aloud ("This is premature convergence" or "This is skipping EVOLVE"). State the risk in ONE sentence. Proceed only with explicit user consent, and log the bypass in EVOLVE. |
| Any phase: blocked twice in same phase | Escalate to L2: hand off to realthink with current STATE, all generated ideas, top candidates, and partial ULTRATHINK answers. Resume GENESIS at Phase 3 with realthink's lever as U. |
