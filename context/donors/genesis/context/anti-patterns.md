---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Failure Modes

source: genesis/SKILL.md#anti-patterns

### 1. Summarizing Instead of Synthesizing
**Pattern:** SYNTHESIZE output is organized by source: "From Approach A: ... From Approach B: ..." with sections labeled by input origin.
**Why it fails:** Summarization preserves existing knowledge organized by where it came from. SYNTHESIZE must create new knowledge organized by a new capability. Output organized by source means Phase 4 was skipped — you named the inputs, not the emergence. Z is empty.
**Corrected version:** Ask "What does A+B make possible that neither A nor B can do alone?" and answer it in ONE sentence before writing any output. Reorganize the output around the new capability Z, not around A and B.

### 2. Premature Convergence
**Pattern:** A candidate is selected or an obvious direction is named before 15+ ideas are generated. User says "we already know the direction" after 3 ideas.
**Why it fails:** The first 10 ideas are the ones the builder already had walking in — they are the obvious solution space. The non-obvious insight that drives differentiation is statistically in ideas 11-20. Selecting from the first pool produces the best bad idea, not the best idea. The team then executes with high confidence on a locally-optimal but globally-mediocre direction.
**Corrected version:** STATE "STOP: premature convergence" aloud. Enforce the 20-idea minimum as a structural constraint, not a guideline. Apply CROSS-Domain Stealing or Absurd Amplification to reach ideas 11-20. Evaluate only after 20.

### 3. Vague ULTRATHINK Answers
**Pattern:** U, T, or N answers are one vague sentence: "to improve performance", "to build something useful", "figure out the next step". The gate is considered passed.
**Why it fails:** A vague U answer means the real problem has not been named. The plan then optimizes for the stated problem, which is rarely the real one. DEEPEN with a vague U produces a confident wrong synthesis. The gate is not advisory — vague means the gate did not pass.
**Corrected version:** U must name ONE hidden problem distinct from the stated problem. T must name ONE new capability users gain (not "improvement" — a named capability). N must be ONE concrete action with a named file, tool, or command. If any are vague, return to Phase 1 before proceeding.

### 4. Skipping EVOLVE
**Pattern:** SYNTHESIZE output is delivered and the session closes without a mind_remember write or a learnings.jsonl entry. "We ran out of time."
**Why it fails:** Every session either compounds the next one or resets it. Without EVOLVE, the same ineffective techniques repeat in the next session because nothing was captured. The PROTOCOL is a ONE-time protocol without EVOLVE; it becomes a compounding system only when EVOLVE runs. UUID 550e8400... is the write target — old UUID 477b8a03 fails silently.
**Corrected version:** Before closing any session, answer three questions: what technique produced a breakthrough? what felt forced? what is ONE hypothesis for next time? Write to learnings.jsonl or call mind_remember with salience >= 0.75. EVOLVE-ONLY MODE exists precisely for this situation — switch to it instead of skipping.

### 5. Role-Shifting Without Distinct Insight
**Pattern:** Role-Shifting runs three roles but each produces a restatement of the same framing. "The criminal would also want a fast search." "The child would also ask for better search." The roles are named but produce no divergence.
**Why it fails:** Role-Shifting is designed to force frame breaks — views from positions that have fundamentally different constraints than the builder. A restatement means the builder interpreted each role through their own frame, which defeats the mechanism. The technique produced noise, not divergence.
**Corrected version:** For each role, ask "what would make this person REJECT the current direction entirely?" The child asks "why does it have to work that way at all?" — not "how do we make it better." The criminal asks "how would I exploit this to harm the system?" The competitor asks "where is this plan weakest and how would I attack it?" Document the divergent insight from each role before proceeding.

### 6. Treating EXPRESS as a Skip Permit
**Pattern:** User has ONE direction and invokes EXPRESS MODE, then skips Phase 3 DEEPEN because "we have a direction." ULTRATHINK is not applied. EVOLVE is also skipped because "it was EXPRESS."
**Why it fails:** EXPRESS reduces the idea-generation floor from 20 to 15 and compresses Phases 2 and 4 into Phase 3. It does NOT skip ULTRATHINK and it does NOT skip EVOLVE. A direction that has not passed ULTRATHINK U+T+N has not been stress-tested — executing on it is executing on an assumption. EVOLVE is never optional in any MODE.
**Corrected version:** In EXPRESS MODE, still apply the ULTRATHINK gate to the ONE candidate. U, T, N must each be answered in one specific sentence. And EVOLVE still runs at the close. EXPRESS saves time on idea generation, not on quality gates.

### 7. Z Sentence with Empty Blank
**Pattern:** After SYNTHESIZE, the emergence sentence is filled with a placeholder: "A+B enables ___ which neither alone can do because ___." The blank is left empty or filled with "more value" or "better outcomes."
**Why it fails:** An empty Z means SYNTHESIZE did not run — it was declared without producing the emergence. The output is concatenation organized by source. The mechanism that GENESIS STRUCTURE is built on is emergence testing; if Z is empty, the phase 4 gate has not passed.
**Corrected version:** Ask "what task is impossible with only A, impossible with only B, but becomes possible with both?" The answer to that question is Z. If no such task can be named, the two approaches do not synthesize — acknowledge this and restart from Phase 1 with the constraint that synthesis must be possible.
