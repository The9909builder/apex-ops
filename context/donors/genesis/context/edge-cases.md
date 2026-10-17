---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Edge Cases

source: genesis/SKILL.md#escalation-ladder

### 1. Problem Statement Is Still Unclear After Phase 1 Completes
**Case:** EXPLODE generates 20+ ideas, but the ideas reveal that the practitioner was solving the wrong problem all along. The top candidates disagree on what the problem even is.
**Why default fails:** The standard path enters STRUCTURE and filters 20 ideas down to 5-8 candidates — but if the ideas disagree on the problem definition, the Goldilocks filter cannot distinguish between them on quality; it will select on surface plausibility. SYNTHESIZE then attempts to combine candidates that are solving different problems.
**Adjustment:** This is the ESCALATION LADDER L2 trigger: "problem statement is still unclear after Phase 1 completes." Hand off to realthink. Pass all 20+ ideas, the top-3 candidates, and the stated problem. Resume GENESIS at Phase 3 (DEEPEN) after realthink returns ONE lever. Enter Phase 3 with realthink's lever as the U answer. Do NOT re-run Phases 1-2.

---

### 2. Two Approaches That Do Not Synthesize (No Valid Z Exists)
**Case:** SYNTHESIZE runs. The emergence test is applied. "What task is impossible with only A, impossible with only B, but possible with both?" — and the honest answer is "nothing." The approaches are genuinely orthogonal or competing, not combinable.
**Why default fails:** The default principle (synthesis creates new capability) assumes the inputs can combine. If they cannot, forcing a Z sentence produces a false emergence claim — a sentence that sounds like synthesis but describes concatenation. Delivering a false Z is worse than acknowledging no synthesis exists.
**Adjustment:** STATE "SYNTHESIZE: no valid Z — approaches are not combinable." Report which approach passes ULTRATHINK U+T+N with stronger answers. Recommend selecting the better candidate rather than synthesizing. Hand the selection and rationale to think-pipeline for the 7-slot executable plan. Do not manufacture a Z that cannot be defended.

---

### 3. Mind API Down During EVOLVE (EVOLVE-ONLY Mode)
**Case:** Phase 5 EVOLVE fires. mind_remember is called. Port 8000 is not responding. `curl -sf http://127.0.0.1:8000/health` returns nothing.
**Why default fails:** The default EVOLVE protocol calls mind_remember as the write target. If the API (port 8000) is down, the call appears to succeed silently (no error raised) but nothing is written — identical to the silent UUID failure. A practitioner who believes EVOLVE ran successfully will not run it again next session, permanently losing the evolution log.
**Adjustment:** Check Mind API health BEFORE Phase 5 begins (TOOL AVAILABILITY CHECK). If down: write evolution log directly to `$TFC_HOME/skills/pattern/genesis/learnings.jsonl` with `"pending_mind_sync": true`. Do not mark EVOLVE as complete without a confirmed write to at least one of these targets. The STATE tracker entry for Phase 5 must show `evolve=[learnings.jsonl]` not `evolve=[done]` until mind_remember is confirmed written.

---

### 4. User Pushes to Skip a Gate Under Time Pressure
**Case:** Any phase gate (especially the 20-idea minimum or ULTRATHINK U+T+N). User says "we know the answer, skip the gate." The default principle says gates are hard blocks.
**Why default fails:** "Hard block" creates a conflict when the user has explicit authority over the session. Blocking the user causes them to lose trust in the PROTOCOL and disable it. But proceeding without the gate produces a synthesis that optimizes for the stated problem (not the real one) or misses the non-obvious insight.
**Adjustment:** Name the anti-pattern aloud: "This is premature convergence" or "This is ULTRATHINK gate bypass." State the specific risk in one sentence (e.g., "Skipping the 20-idea minimum means we are selecting from obvious-space only"). Then defer explicitly to the user: "Proceeding only with your explicit consent." If user confirms, proceed but STATE "GATE BYPASSED: [phase] — user consent given." Log in EVOLVE that a gate was bypassed and what the consequence was, so the next session has data.

---

### 5. Single Source — Synthesis Target Is One Input, Not Two
**Case:** SYNTHESIZE receives only ONE candidate (not two approaches to combine). User wants "synthesis" of a single approach. There is no A+B, only A.
**Why default fails:** The emergence test formula (A+B produces Z) requires two inputs. With only ONE input, the test cannot be applied, and the practitioner either fakes a second input or mistakes DEEPEN (validating ONE approach) for SYNTHESIZE (combining multiple approaches).
**Adjustment:** Route to REVIEW mode instead: apply ULTRATHINK to the single candidate, then apply the emergence test to the candidate vs. its OWN phases (does Phase 1 + Phase 3 + Phase 5 produce something no single phase produces alone?). If genuine synthesis is needed, return to EXPLODE and generate 5+ alternative approaches to combine with the single candidate before entering SYNTHESIZE. STATE "SYNTHESIZE: only ONE candidate — routed to REVIEW; returning to EXPLODE to generate synthesis partner."

---

### 6. GENESIS Called on a Problem realthink Already Solved
**Case:** realthink has identified the ONE lever. The user calls GENESIS to "synthesize a solution." But realthink's lever is already the specific next action — there is no synthesis target, only an execution target.
**Why default fails:** GENESIS does not own execution-waves (boundary contract: does_not_own). Running FULL mode on an already-solved problem produces 20 ideas and 5 candidates when ONE concrete implementation plan is what is needed. The phases add latency without adding capability.
**Adjustment:** STATE "SCOPE: realthink lever already identified — GENESIS out of bounds; routing to vague-to-system or build skill." Pass realthink's lever as the first_action in N. Do not re-run Phases 1-2. If the lever is a framework (not a direct action), GENESIS can run SYNTHESIZE in EXPRESS mode treating the lever as the ONE candidate to stress-test via ULTRATHINK before formalization.
