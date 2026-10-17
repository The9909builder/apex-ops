---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Principles

source: genesis/SKILL.md#behavioral-constraints

### 1. EXPLODE Before Compressing
Generate at least 20 raw ideas including 3+ uncomfortable ones before evaluating any candidate.

**Why it is true:** Intuition anchors to the first framing and stops diverging after idea 3. The non-obvious insight is statistically in ideas 11-20, after the obvious solution space is exhausted. Builders who select from the first 5 ideas get the best bad idea, not the best idea (source: six-week rebuild story in EXPERT PERSONA).

**Falsifiable:** Apply this principle to a new case by counting ideas before selection. If the top candidate could have been named in the first session minute, the principle was violated. If the winning idea required reaching idea 14+, the principle was honored.

**Concrete change when applied:** Before the first STRUCTURE step, count the idea list. If count < 20, apply CROSS-Domain Stealing or Absurd Amplification and continue generating. Do not open the filter until count is at 20.

---

### 2. ULTRATHINK U+T+N is a Hard Gate, Not a Checklist
DEEPEN must produce one specific sentence each for U (real problem), T (new capability created), N (minimal next action). Vague answers mean the gate is not passed.

**Why it is true:** A vague U means the plan optimizes for the stated problem, which is rarely the real one. A plan that cannot name the new capability it creates (T) is building infrastructure with no user-visible outcome. A vague N generates ambiguous handoffs that stall execution. The ULTRATHINK gate exists because builders consistently produce confident wrong results by passing gates they have not actually answered (source: BEHAVIORAL CONSTRAINTS #2, EVIDENCE GATES table).

**Falsifiable:** For any new GENESIS session, check U, T, N after DEEPEN. If any answer uses "improve," "better," "explore," or "figure out" — gate has not passed. A passing T answer names a capability in the form "users can now do X that they could not do before."

**Concrete change when applied:** After writing U, T, N draft answers, replace any vague word with a proper noun (a file name, a command, a named capability). If you cannot, return to Phase 1 before proceeding.

---

### 3. Synthesis Creates New Capability; Combination Produces Stacks
A+B must produce Z where Z enables something neither A nor B can do alone. If Z = A+B stacked, restart SYNTHESIZE.

**Why it is true:** Genuine synthesis multiplies (creates new capability). Concatenation adds (organizes existing capability by source). The mechanism that distinguishes them is the emergence test — naming Z in ONE sentence. If output is organized by source (From A: ... From B: ...), the synthesis phase was skipped. Builders who mistake concatenation for synthesis deliver a plan that neither input approach could improve on (source: KNOWN-GOOD RECIPES / Emergence Test, BATTLE SCARS).

**Falsifiable:** For any proposed synthesis, apply: "What task is impossible with only A, impossible with only B, but possible with both?" If no such task can be named, Z is empty and the emergence test fails.

**Concrete change when applied:** After writing the synthesis output, reorganize it by capability (what users can now do) rather than by source. Then fill in: "A+B enables ___ which neither alone can do because ___." If the blank cannot be filled, rewrite the output around the new capability.

---

### 4. EVOLVE is the Compounding Mechanism — Not Optional in Any MODE
Every session must close with a mind_remember write capturing what worked, what failed, ONE reusable pattern, and ONE hypothesis. UUID 550e8400-e29b-41d4-a716-446655440000 is the write target.

**Why it is true:** A session without EVOLVE produces one synthesis result. A session with EVOLVE produces one result plus one improvement to the PROTOCOL for every future session. The team that skipped EVOLVE ran the same wrong techniques next session because nothing was captured (source: EXPERT PERSONA final lesson, SELF-IMPROVEMENT HOOK, EVIDENCE GATES Phase 5 row).

**Falsifiable:** For any closed session, check learnings.jsonl or mind_retrieve. If EVOLVE ran, there is an entry with worked+failed+pattern+hypothesis. If EVOLVE was skipped, the entry is absent and the session contributed zero to the compounding ledger.

**Concrete change when applied:** Before closing, write EVOLVE-ONLY output even if only 2 minutes remain. If Mind API (port 8000) is down, write directly to learnings.jsonl with `"pending_mind_sync": true`. Never mark a session complete without the EVOLVE write.

---

### 5. PROTOCOL Applies Itself — a Synthesis Method That Cannot Synthesize Its Own Output is Broken
GENESIS is applied to its own output before delivery: run the emergence test on the synthesis, run the ULTRATHINK N check on the next action, run EVOLVE on the session before closing.

**Why it is true:** A synthesis PROTOCOL that exempts itself from the synthesis gate will drift. If GENESIS cannot name what the combination of its phases produces that no single phase produces alone, the PROTOCOL is concatenation not synthesis. The behavioral constraint "apply the PROTOCOL to itself before delivering" exists because GENESIS is also a candidate for the emergence test (source: BEHAVIORAL CONSTRAINTS #4).

**Falsifiable:** After any GENESIS session, apply the emergence test to the session itself: "What does EXPLODE + STRUCTURE + DEEPEN + SYNTHESIZE + EVOLVE produce that no single phase produces alone?" If the answer is only "a structured output," the session was concatenation. A passing answer names a capability the phases create together that none produces individually (e.g., "a synthesis that compounds across sessions via EVOLVE memory").

**Concrete change when applied:** After Phase 4, run one self-check: does the delivery output name Z, state the U answer, and name N? If any are absent, fill them before delivering. This takes under 2 minutes and is the gate that proves the PROTOCOL ran, not just the phases.
