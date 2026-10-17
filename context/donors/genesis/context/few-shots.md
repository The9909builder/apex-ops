---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Example 1

source: genesis/SKILL.md#known-good-recipes

**Task:** Team needs to decide how to architect a new notification system. Three early ideas all look like variations of "add a pub/sub queue." The tech lead wants to pick the best of the three and build.

**GENESIS run (FULL mode):**
- PRESET: no committed direction; 3 ideas that feel identical in angle
- EXPLODE: enforced 20 ideas including uncomfortable ones (#14: "let users write their own notification rules in a DSL", #17: "charge per notification so senders self-regulate volume")
- STRUCTURE: filtered to 6 candidates; #14 became "user-configurable delivery contracts" with first_action: `edit src/notifications/schema.ts to add DeliveryContract type`
- DEEPEN U: "real problem is senders have no cost signal so they flood every channel" (not "build a queue")
- DEEPEN T: "users gain the ability to define exactly which events reach which surface, creating a private API for their own attention"
- SYNTHESIZE Z: "pub/sub queue + user delivery contracts enables demand-driven notification routing which neither alone can do because neither alone knows what the recipient values"
- EVOLVE: `mind_remember(user_id="550e8400-e29b-41d4-a716-446655440000", content="GENESIS: worked=role-shift-criminal revealed sender-flooding; failed=early convergence pressure; pattern=framing-as-sender-cost-problem; next=test delivery-contract DSL for complexity threshold", salience=0.75)`

**Annotation:** This works because EXPLODE's 20-idea constraint forces divergence past the obvious pub/sub space. The Criminal role (how would a spammer exploit this system?) revealed the sender-flooding insight at idea 14. Without the count constraint, the team would have selected from ideas 1-3 and built a standard queue without the delivery-contract layer. The ULTRATHINK T answer named a capability (user-controlled attention routing) that the original three ideas could not produce alone. because the 20-idea minimum structurally prevents anchoring to the first framing, which would have produced the best bad idea, not the best idea.

---

## Example 2

source: genesis/SKILL.md#battle-scars

**Task:** Two synthesis candidates exist for a search ranking improvement: (A) BM25 keyword scoring, (B) semantic embedding similarity. Team wants to ship whichever is better.

**GENESIS run (EXPRESS mode):**
- PRESET: two committed directions, no synthesis yet
- Entry point: Phase 3 DEEPEN + Phase 4 SYNTHESIZE (EXPRESS path)
- DEEPEN U: "real problem is that keyword search misses intent and semantic search misses exact terms — each fails where the other succeeds"
- DEEPEN T: "A+B would let the engine answer 'find invoices mentioning Q3' (keyword) AND 'find documents similar in meaning to this contract' (semantic) with ONE query path"
- ULTRATHINK passed; proceed to SYNTHESIZE
- Emergence test: "BM25 + semantic enables hybrid intent-and-term ranking which neither alone can do because BM25 cannot generalize across synonyms and embedding alone misses exact-match anchors"
- Z named: "hybrid ranking that resolves ambiguity by weighting term salience against semantic distance"
- EVOLVE: logged worked=ultrathink-caught-the-either-or-trap; failed=N/A (EXPRESS was fast); pattern=when-two-approaches-each-fail-where-the-other-succeeds-synthesis-is-always-available; next=test fusion weight parameter

**Annotation:** This works because EXPRESS mode does not skip ULTRATHINK — it only skips re-generating 20 ideas. The DEEPEN U answer identified that both approaches fail on orthogonal input types, which is the structural signal that synthesis is available. Synthesis here is not "use A for X and B for Y" (that is routing, not synthesis). The emergence test forced naming the mechanism (intent-and-term ranking in ONE path) because the forge PROTOCOL requires Z to be a new capability, not a weighted average. because the emergence test demands the output name something impossible with only one approach, it converts an either-or choice into an AND capability.

---

## Example 3

source: genesis/SKILL.md#phase-5-evolve

**Task:** A GENESIS session just delivered a synthesis result for a product architecture decision. No evolution log has been written. Session is about to close.

**GENESIS run (EVOLVE-ONLY mode):**
- PRESET: session ending, EVOLVE not yet written
- Entry point: Phase 5 EVOLVE only
- Answered four questions:
  - Technique that produced breakthrough: Role-Shifting (Competitor role identified the defensive moat the obvious architecture lacked)
  - Technique that felt forced: Constraint Explosion (inverting the main constraint produced noise; team was already past the constraint)
  - Reusable pattern: "when a competitor framing changes the architecture decision, the real problem was defensibility, not functionality"
  - Hypothesis for next session: "Competitor role should run before any architecture gate, not as a divergence technique inside EXPLODE"
- Wrote to learnings.jsonl with key `competitor-role-before-architecture-gate`
- Called `mind_remember(user_id="550e8400-e29b-41d4-a716-446655440000", content="GENESIS evolution: worked=competitor-role-surfaced-defensibility | failed=constraint-explosion-noise | pattern=defensibility-as-real-problem | next=run-competitor-before-arch-gate", temporal_level=2, salience=0.75)`

**Annotation:** This works because EVOLVE is the mechanism that makes sessions compound. A session without EVOLVE produces ONE synthesis result. A session with EVOLVE produces ONE result PLUS one improvement to every future session. The pattern captured (competitor-role-before-architecture-gate) changes how Phase 1 is run next time, before the builder even realizes they made a choice. because mind_remember with salience=0.75 persists the pattern across sessions (not just within the conversation), it converts a one-time insight into a structural improvement to the GENESIS PROTOCOL itself.
