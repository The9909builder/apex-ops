---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Core Mechanisms

source: genesis/SKILL.md#genesis-workflow

### 1. Idea Count Gate (EXPLODE Divergence Mechanism)
**Trigger:** EXPLODE phase is running; practitioner reaches idea 5-7 and the count feels like "enough."
**Mechanism:** The 20-idea minimum creates structural pressure beyond the obvious solution space. Ideas 1-10 exhaust the approaches the practitioner already knew. Ideas 11-20 require applying divergence techniques (CROSS-Domain, Role-Shifting, Absurd Amplification) that access non-obvious frames. The gate does not evaluate quality — it enforces quantity to force the divergence that breaks out of the first framing.
**Observable result:** After idea 20, the top candidate is measurably different from the candidate that would have been selected at idea 5. The 1% genius from the absurd ideas surfaces as a constraint, edge case, or mechanism that changes the direction of the synthesis.

---

### 2. Role-Shifting Frame Break
**Trigger:** All generated ideas feel like variations of the same framing; the team or model converges on ONE direction without discomfort.
**Mechanism:** Role-Shifting forces the practitioner to adopt positions with structurally different constraints: Child (no assumptions, asks "why does it have to work this way?"), Criminal (how to exploit or harm), Competitor (where is this weakest?), Artist (emotion/aesthetics), Scientist (how to falsify). Each role breaks the shared frame by introducing a constraint the practitioner's own frame makes invisible. The divergent insight from each role must be distinct — not a restatement.
**Observable result:** At least ONE idea emerges that makes the room uncomfortable. That idea contains the hidden constraint or attack vector that the original framing was blind to. The ULTRATHINK U answer often comes from this discomfort.

---

### 3. Goldilocks Filter (STRUCTURE Signal Extraction)
**Trigger:** EXPLODE is complete with 20+ ideas; the practitioner needs to reduce to 5-8 actionable candidates.
**Mechanism:** Each idea is tested against two constraints simultaneously: (a) specific enough to act on — has a named first_action identifying a file, tool, or command; (b) flexible enough to adapt — not so locked to one implementation that a new constraint kills it. Ideas that fail either test are removed. Vague first_actions ("think about it," "research") are not actionable and fail gate (a). Overly specific implementations that cannot adapt fail gate (b).
**Observable result:** 5-8 candidates remain, each with a `first_action` that names a specific artifact. The filter simultaneously removes noise (too vague) and brittle premature implementation (too rigid), producing a candidate set that can survive DEEPEN.

---

### 4. ULTRATHINK U+T+N Hard Block
**Trigger:** Top candidates have been selected; practitioner is about to commit to execution or synthesis.
**Mechanism:** Three questions must be answered with ONE specific sentence each before any forward motion: U (what is the real problem beneath the stated problem — not a restatement), T (what new capability users gain that they literally cannot do today — a named capability, not "improvement"), N (what is the minimal specific next action — one named file, tool, or command). These three cannot be vague. If any answer is vague, the gate sends the practitioner back to Phase 1. The block prevents executing on an assumption masquerading as an answer.
**Observable result:** The U answer reveals a hidden problem that changes either the direction or the synthesis target. The T answer names something the product cannot do today, converting abstract improvement into a concrete capability. The N answer produces a handoff that can be acted on without a follow-up question.

---

### 5. Emergence Test (SYNTHESIZE Quality Gate)
**Trigger:** Two or more candidates are being combined; output feels like a "weighted average" or is organized by source.
**Mechanism:** The emergence test asks: "What task is impossible with only A, impossible with only B, but possible with both A and B?" The answer is Z. Z must be a named capability — not an abstraction or a restatement of A and B. If Z cannot be named, the combination is concatenation (addition) not synthesis (multiplication). The test structurally requires naming the new capability before the output is accepted, preventing the common failure of delivering a summary organized by source.
**Observable result:** Z is named in ONE sentence: "A+B enables [Z] which neither alone can do because [reason]." The delivery output is organized around Z, not around A and B. Reviewers can identify what is NEW that neither approach could produce independently.

---

### 6. EVOLVE Compounding Loop
**Trigger:** Any GENESIS session is ending; output has been delivered; practitioner is about to close.
**Mechanism:** Four questions must be answered before close: (1) what ONE technique produced a breakthrough this session? (2) what ONE technique felt forced or produced noise? (3) what ONE reusable pattern generalizes beyond this problem? (4) what ONE hypothesis should the next session test? Answers are written to mind_remember (UUID 550e8400-e29b-41d4-a716-446655440000, salience=0.75) or to learnings.jsonl as fallback. The next session's EXPLODE phase begins by loading these learnings, which prevents repeating failed techniques and prioritizes working patterns.
**Observable result:** After 3+ sessions with EVOLVE, mind_retrieve returns past patterns that change the Phase 1 divergence technique selection. Failed techniques are skipped. Working patterns are prioritized. The quality of synthesis improves measurably across sessions without the practitioner consciously choosing to improve.

---

### 7. STATE Tracker Phase-Lock
**Trigger:** Any phase transition in a GENESIS session.
**Mechanism:** The STATE tracker is emitted on every phase entry and exit: "STATE: phase=[N] | ideas=[count] | candidates=[count] | ultrathink=[pass/fail] | emergence=[named/null] | evolve=[done/pending] | blocked=[null/reason]". This makes the current PROTOCOL state observable and prevents silent phase skipping. A phase cannot be exited without emitting STATE, which forces the practitioner to acknowledge whether the gate for that phase was passed or not.
**Observable result:** Phase skipping becomes visible — a STATE emission that shows `ultrathink=pending` at the transition from Phase 3 to Phase 4 is an explicit record that the gate was bypassed. The STATE tracker turns invisible skips into auditable decisions, enabling the ESCALATION LADDER to apply the correct recovery.
