---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Escalation Levels

source: genesis/SKILL.md#escalation-ladder

Never jump from L0 directly to L3. Work through levels in order. Each level must be attempted before the next.

### L0 — Self-Resolve
**Trigger:** Gate not passed on first attempt.
**Action:** Apply RECOVERY PROTOCOL for that specific phase. Do not skip the gate. Retry once using the technique listed in RECOVERY PROTOCOL for the specific failure type.
**What to pass to next level:** N/A — L0 is self-contained.

---

### L1 — Retry
**Trigger:** Gate fails twice in the same phase.
**Action:** STATE the block explicitly: "BLOCKED at Phase [N]: [reason]". Switch the divergence technique (e.g., if CROSS-Domain failed, switch to Role-Shifting). Retry once more.
**What to pass to next level:** Current STATE tracker values, failed technique names, both gate failure reasons.

---

### L2 — Skill Handoff (realthink)
**Trigger:** Problem statement is still unclear after Phase 1 completes; practitioner cannot name a U answer that differs from the stated problem.
**Action:** Hand off to `realthink`. Pass: all 20+ ideas generated, top-3 candidates with partial ULTRATHINK answers, stated problem. Resume GENESIS at Phase 3 with realthink's lever as the U answer. Do NOT re-run Phases 1-2.
**What to pass:** idea_list (all 20+ ideas), top_candidates (top 3), stated_problem, partial ULTRATHINK answers if any.

---

### L3 — Orchestration (spawner_orchestrate)
**Trigger:** Multiple parallel synthesis tracks are needed simultaneously; ONE synthesis track cannot hold all the problem dimensions.
**Action:** Call `spawner_orchestrate`. GENESIS handles ONE synthesis track. Coordinate tracks via spawner_emit. Each track runs GENESIS independently and passes its Z sentence to a final merge step.
**What to pass:** Per-track problem framing, synthesis target for each track, coordination protocol via spawner_emit event names.

---

### L4 — Abort
**Trigger:** User rejects all Phase 3 candidates; no new direction is extractable after L0-L2 recovery attempts.
**Action:** Emit BLOCKED. STATE exactly: what phases ran, what techniques were tried, what gate killed each candidate. Recommend: restart from realthink to reframe the problem before attempting GENESIS again.
**What to pass:** Full STATE tracker dump, list of failed candidates with the ULTRATHINK answer that blocked each, the reframe question for realthink.
