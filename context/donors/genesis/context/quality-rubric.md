---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Scoring Dimensions

source: genesis/SKILL.md#quality-rubric

Score the session output on 4 dimensions (1-5 each) at the end of Phase 4. Minimum passing score: 3 on all 4 dimensions. Score < 3 on any dimension: report as DONE_WITH_CONCERNS and name the failing dimension.

### Dimension 1: Divergence Depth
**5 — Excellent:** 20+ ideas generated; 3+ labeled uncomfortable or absurd; role-shifting ran with a distinct (non-restatement) insight per role.
**3 — Acceptable:** 15-19 ideas; 1-2 uncomfortable ones; one divergence technique used.
**1 — Fail:** < 15 ideas; no uncomfortable ideas; no divergence techniques applied.

**When to rerun:** Score = 1 or 2 on this dimension means the synthesis is built on obvious-space selection. Return to EXPLODE and enforce the 20-idea minimum before STRUCTURE.

---

### Dimension 2: ULTRATHINK Rigor
**5 — Excellent:** U names a hidden problem distinct from the stated problem; T names a specific named capability users gain that they cannot do today; N is ONE concrete action with a named artifact (file, tool, command).
**3 — Acceptable:** U, T, N all answered but answers are generic or could apply to any problem in the domain.
**1 — Fail:** Any of U, T, N is vague ("improve performance"), restated (U = stated problem), or absent.

**When to rerun:** Score = 1 or 2 means DEEPEN gate was bypassed or not genuinely passed. Return to Phase 3 before delivering.

---

### Dimension 3: Emergence Quality
**5 — Excellent:** Z enables something neither A nor B can do; stakeholder check ran from 3 distinct positions; Z sentence is complete and specific.
**3 — Acceptable:** Z is plausible but untested; stakeholder check was skipped; Z sentence is vague but names something.
**1 — Fail:** Z = A+B stacked (concatenation); no new capability named; output organized by source (From A: ... From B: ...).

**When to rerun:** Score = 1 or 2 means SYNTHESIZE did not produce emergence. Restart SYNTHESIZE and ask "what is impossible with only A and impossible with only B but possible with both?"

---

### Dimension 4: Evolution Capture
**5 — Excellent:** worked + failed + pattern + hypothesis all written; mind_remember called with salience >= 0.75; UUID 550e8400 confirmed.
**3 — Acceptable:** worked + failed captured in EVOLVE; pattern or hypothesis is absent or weak.
**1 — Fail:** Nothing captured; EVOLVE was skipped entirely; session ended without mind_remember or learnings.jsonl write.

**When to rerun:** Score = 1 on this dimension means the session did not compound. Run EVOLVE-ONLY MODE immediately before closing. The mind_remember write with UUID 550e8400-e29b-41d4-a716-446655440000 is the gate.
