---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Categories

source: genesis/SKILL.md

### 1. FULL Mode
All five phases in sequence: EXPLODE -> STRUCTURE -> DEEPEN -> SYNTHESIZE -> EVOLVE. The STATE tracker starts at phase 0 and advances only when the gate for each phase passes. Use when no clear direction exists and the problem is open.

### 2. EXPRESS Mode
Compressed path: Phase 1 (min 15 ideas) -> Phase 3 DEEPEN -> Phase 5 EVOLVE. Phase 2 and 4 are folded into DEEPEN. GENESIS runs EXPRESS when ONE direction exists but has not been validated by ULTRATHINK. STOP: EVOLVE is never skipped even in EXPRESS.

### 3. REVIEW Mode
Phases 3 and 4 only: ULTRATHINK gate on an existing plan + emergence test on a proposed synthesis. No idea generation. GENESIS runs REVIEW when a plan already exists and needs a quality gate before execution starts.

### 4. EVOLVE-ONLY Mode
Phase 5 only. mind_remember is the ONE required output. Runs when a session is ending without captured evolution. The PROTOCOL treats a session without EVOLVE as a reset to zero.

### 5. Divergence Techniques (EXPLODE)
The four techniques that break out of the first framing: Absurd Amplification (take constraints to 1000x), Role Shifting (Child/Criminal/Competitor/Artist/Scientist), CROSS-Domain Stealing (borrow a mechanism from an unrelated field), Constraint Explosion (invert or remove the main constraint). Each must produce a distinct idea, not a restatement.

### 6. STRUCTURE / Signal Filtering
Goldilocks filter applied after EXPLODE: keep the top 20-30% of ideas; each surviving candidate must be specific enough to act on AND flexible enough to adapt. Each candidate needs a `first_action` naming a specific file, tool, or command — vague first_actions fail the gate.

### 7. DEEPEN / ULTRATHINK Gate
The 10-letter gate (U through K) applied to the top 3 candidates. U = real problem beneath the stated problem. T = new capability created. N = minimal specific next action. These three are the hard gate; the other 7 letters deepen quality but do not block progression.

### 8. SYNTHESIZE / Emergence
Phase 4: combine best elements across candidates and test emergence. The emergence test: "A+B enables Z which neither A nor B can do because [reason]." If Z cannot be named, the output is concatenation and SYNTHESIZE must restart.

## When To Use

source: genesis/spec.yaml

| Category | When to invoke |
|----------|----------------|
| FULL | No existing direction; problem has too many or zero viable paths |
| EXPRESS | ONE direction exists but has not passed ULTRATHINK; direction needs stress-test before commitment |
| REVIEW | A plan exists in PLAN.md or conversation; apply ULTRATHINK + emergence test before first wave starts |
| EVOLVE-ONLY | Session ending; no evolution log written yet; cannot extend session |
| Divergence Techniques | Any time EXPLODE generates < 15 ideas or all ideas feel like the same idea from the same angle |
| STRUCTURE | After EXPLODE generates 20+ ideas; must gate on 5+ candidates with specific first_actions |
| DEEPEN | After STRUCTURE produces candidates; must gate on U+T+N answers before SYNTHESIZE |
| SYNTHESIZE | After top candidates pass ULTRATHINK; combining approaches; output must name Z explicitly |
