---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## High-ROI Moves

source: genesis/SKILL.md#quick-wins

Six moves applicable without running a full GENESIS session. Each takes under 5 minutes and targets a specific known failure mode.

### 1. Load Past Evolution Logs Before Starting
```bash
# Call before Phase 1 of any session
mind_retrieve(user_id="550e8400-e29b-41d4-a716-446655440000", query="genesis synthesis patterns", limit=5)
```
**What it does:** Surfaces which divergence techniques worked and which failed in past sessions. Prevents repeating the same ineffective technique twice. If Mind API is down, read the last 5 lines of `~/.future-code/skills/pattern/genesis/learnings.jsonl` instead.

---

### 2. ULTRATHINK U+T+N Check on Any Existing Plan
Apply to any plan in PLAN.md or CLAUDE.md right now:
1. U: "What is the real problem beneath the stated problem?" — ONE sentence, must differ from the stated problem.
2. T: "What new capability do users gain that they cannot do today?" — ONE named capability.
3. N: "What is the ONE minimal next action?" — ONE named command, file, or tool.
If any answer is vague, the plan is not ready to execute.

---

### 3. Role-Shifting on Fast Agreement
When a team agrees on an approach in under 5 minutes for an L3+ problem, run:
- Child: "Why does it have to work that way?"
- Criminal: "How would someone exploit this?"
- Competitor: "Where is this plan weakest and how would I attack it?"
Write the divergent insight from each role before continuing. One insight must make the room uncomfortable — if none do, the roles were not genuinely adopted.

---

### 4. Emergence Test on Any Proposed Synthesis
Before delivering any synthesis output, fill in:
> "A+B enables ___ which neither alone can do because ___."

If the blank is empty, vague ("more value"), or a restatement of A and B, the output is concatenation. Rewrite it organized by the capability Z before delivering.

---

### 5. Stale UUID Check
```bash
grep -n "477b8a03" ~/.future-code/skills/pattern/genesis/SKILL.md
```
If this returns results, the stale UUID is present and mind_* calls will fail silently with no error. Replace every instance with `550e8400-e29b-41d4-a716-446655440000` before the next session.

---

### 6. Cross-Domain Steal When Stuck at Idea 10-12
When EXPLODE stalls:
1. Name the CORE PATTERN of the problem (not its surface feature).
2. Identify an unrelated field that solved the same core pattern.
3. Steal the mechanism and translate it to the current domain.

Aviation, medicine, manufacturing, and urban planning each contain solutions most software problems have not borrowed. A translated mechanism from an unrelated field consistently produces the idea that breaks the anchor.
