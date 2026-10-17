---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Documented Failures

source: genesis/SKILL.md#battle-scars

Three documented, non-obvious failures that appear to succeed. Read before every session.

### Scar 1: Stale UUID 477b8a03 — Silent mind_remember Failure
**Failure:** mind_remember is called. No error is returned. The call appears to succeed. But nothing is written — the evolution log is permanently lost. The practitioner believes EVOLVE ran; it did not.
**Why non-obvious:** The old UUID (`477b8a03-d6f3-54e0-902f-c543549dccc5`) fails UUID validation silently. The Mind API returns no error — it accepts the call and drops the write. `mind_retrieve` next session returns zero results and the practitioner assumes the session log was just not relevant, not that it was never stored.
**Exact fix:** Always use `550e8400-e29b-41d4-a716-446655440000` for all mind_* calls. Run before any session: `grep -n "477b8a03" ~/.future-code/skills/pattern/genesis/SKILL.md` — if results appear, the stale UUID is present and must be replaced.

---

### Scar 2: Early Candidate Selection Picks from Obvious-Space Only
**Failure:** EXPLODE generates 8-10 ideas. The top-2 feel strong. Candidate selection happens at idea 8. STRUCTURE produces solid-looking candidates. SYNTHESIZE runs. The final synthesis is competent but not differentiated — the exact result the team could have named without running GENESIS.
**Why non-obvious:** The ideas at positions 1-10 are the ones the practitioner already had walking in — they are the obvious solution space. They look like good ideas because they are familiar and plausible. They are not the best ideas; they are the best obvious ideas. The non-obvious insight that drives real differentiation is in ideas 11-20, in the ideas that require divergence techniques to reach. Selecting at idea 8 feels like efficiency; it is actually anchoring.
**Exact fix:** Enforce the 20-idea minimum as a structural constraint before any evaluation step. Name the anti-pattern aloud when the user pushes for early convergence: "We are in premature-convergence. We need 20 ideas before evaluation starts."

---

### Scar 3: Output Organized by Source = Summarization, Not Synthesis
**Failure:** SYNTHESIZE produces a section titled "From Approach A: ..." followed by "From Approach B: ..." The output looks thorough. The practitioner delivers it as the synthesis result. Reviewers nod. The document is filed. Two weeks later the same problem is reopened because no new capability was actually created — only a summary of the existing approaches.
**Why non-obvious:** Organizing output by source looks like synthesis because it is systematic and comprehensive. It represents good work. The failure is not visible at delivery time — it is visible two weeks later when no new capability was added. The tell is structural: if the section headers are named after input sources, not after capabilities, the output is summarization.
**Exact fix:** Before delivering any SYNTHESIZE output, apply the emergence test: fill in "A+B enables ___ which neither alone can do because ___." If the blank is empty or vague, rewrite the output organized by capability (what Z makes possible) rather than by source. The output should be impossible to interpret as "From A: ... From B: ..." after the rewrite.
