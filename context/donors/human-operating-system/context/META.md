---
last_verified: 2026-09-20
freshness_clock: 2026-09-20
synthesized: true
source_basis: "HOS Comprehensive Reference Manual (operator-provided) full structure; retrieval order mirrors the 5-loop pipeline"
confidence: "0.9"
forge_domain: "human-operating-system"
fill_hint: "Index of context files and the retrieval order by task intent."
---

## File Index

| File | Contents | Read when |
|---|---|---|
| foundations.md | Four roots (FEP/autopoiesis, Alexander, Meadows, Burkeman/Ellis), synthesis matrix, claims ledger | The run needs theoretical grounding or a claim needs its provisionality checked |
| ten-volumes.md | The 10 data libraries with failure modes and diagnostic routing table | Diagnosing which lens a symptom needs |
| eleven-engines.md | The 11 runtime processors, failure signatures, fixes, loop-to-engine map | A loop's marker line cannot be emitted honestly |
| fifteen-properties.md | The 15 properties with operational tests, application moves, pipeline mapping | Loop 4: choosing the property an intervention applies |
| five-loop-pipeline.md | The 5 loops in depth, marker lines, five-check gate, engine map | Running or auditing the pipeline itself |
| principles.md | Eight domain invariants with resolution order | Two principles collide, or the mandate needs operationalizing |
| few-shots.md | Three worked examples with marker lines | Calibrating output shape before a run |
| anti-patterns.md | Eight failure modes with corrections | A run smells wrong; matching the smell to a named failure |

## Retrieval Order by Intent

- "Diagnose this system": anti-patterns.md (smell match) -> ten-volumes.md
  (diagnostic routing) -> five-loop-pipeline.md (run Loop 1).
- "Design an intervention": fifteen-properties.md (choose property) ->
  principles.md (resolution order) -> few-shots.md Example 1 (output shape).
- "Why do I keep oscillating": anti-patterns.md failures 1 and 6 ->
  eleven-engines.md Integration row -> foundations.md Middle Way root.
- "Audit my efficiency": ten-volumes.md Volume IX -> principles.md Principle 6 ->
  anti-patterns.md failure 5.
- "Explain the theory": foundations.md, then ten-volumes.md for the specific
  volume; claims ledger governs what is held provisionally.
- "Run the full pipeline": five-loop-pipeline.md is the single required file;
  all others load on demand by loop.

## Freshness

All files synthesized 2026-09-20 from the operator-provided HOS manual. The
manual is the source of truth; these files are its operational distillation.
When the manual changes, re-forge this context layer.
