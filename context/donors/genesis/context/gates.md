---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Evidence Gates

source: genesis/SKILL.md#evidence-gates

All gates are hard blocks. Do not proceed to the next phase until the gate passes. A skipped gate must be logged in STATE.

### Phase 1 EXPLODE Gate
**Condition:** 20+ ideas generated; 3+ labeled uncomfortable or absurd.
**Fail signal:** Count < 15; all ideas feel similar in angle; no idea makes the practitioner uncomfortable.
**Recovery:** Apply CROSS-Domain Stealing (name the core pattern; find an unrelated field that solved it; steal the mechanism) and Absurd Amplification (take constraints to 1000x; extract the 1% genius). Do NOT advance until count is at 20.

---

### Phase 2 STRUCTURE Gate
**Condition:** 5+ candidates survive; each has a `first_action` that names a specific file, tool, or command.
**Fail signal:** Fewer than 5 candidates; any first_action is vague ("research," "think about it," "explore").
**Recovery:** For each candidate with a vague first_action, ask: what is the FIRST file to edit, command to run, or tool to call? Replace the vague action with that specific artifact. If fewer than 5 candidates survive, return to EXPLODE with the Goldilocks constraint explicit.

---

### Phase 3 DEEPEN Gate
**Condition:** U, T, N each answered in ONE specific sentence for at least the top candidate.
**Fail signal:** U = restatement of stated problem ("the real problem is that search is slow"); T = "improvement" not a named capability; N is multi-step or uses vague verbs.
**Recovery:** U: ask "what breaks in the system if we solve the stated problem but the hidden one remains?" T: ask "what can users do after this ships that they literally cannot do today — name it." N: ask "what is one named command, file, or deliverable?" Return to Phase 1 if U cannot be distinguished from the stated problem.

---

### Phase 4 SYNTHESIZE Gate
**Condition:** Z named: "A+B enables [Z] which neither alone can do because [reason]" — blank is filled with a specific capability.
**Fail signal:** Z sentence has an empty blank; output is organized by source (From A: ... From B: ...); Z = "more value" or "better outcomes."
**Recovery:** Restart SYNTHESIZE. Ask "what task is impossible with only A, impossible with only B, but possible with both?" That task is Z. If no such task can be named, acknowledge no synthesis is available and route to selection instead.

---

### Phase 5 EVOLVE Gate
**Condition:** mind_remember written (UUID 550e8400-e29b-41d4-a716-446655440000) OR learnings.jsonl entry added; all four fields present: worked, failed, pattern, hypothesis.
**Fail signal:** Session ends without capture; mind_remember not called; no learnings.jsonl entry; only 1-2 of the four fields filled.
**Recovery:** Switch to EVOLVE-ONLY MODE immediately. Write to learnings.jsonl with `"pending_mind_sync": true` as fallback if Mind API (port 8000) is down. Never mark a session complete without the EVOLVE write — absence resets the compounding mechanism to zero.
