---
last_verified: 2026-10-15
freshness_clock: 2026-10-15
synthesized: true
source_basis: "SKILL.md (tfc:v0.10 CONTEXT PACKET phase, apex-v1.3 handoff contract)"
confidence: "0.9"
forge_domain: "autovibe"
---

## Packet Sources

source: autovibe/SKILL.md #CONTEXT PACKET (table)

Six named sources, assembled in one batch before BACKEND selects. Every source either
contributes a finding or prints its degrade label; a skipped source is visible, never silent.

- ENV: working directory stack manifest (package.json, pyproject.toml, Cargo.toml, go.mod),
  README first line, file count. Empty dir -> `greenfield`. Degrades to `na`.
- MEMORY: `mind_retrieve(query=<intent>)` top hits with salience. Degrades to `na, no mind MCP`.
- VAULT: kraken vault search on the domain terms. Degrades to `na, no kraken MCP`.
- PRIOR-ART: slugs in `~/prompt-packs/` matching the intent terms, plus the last outcome row
  per match in `~/.kraken/outcomes/decisions.jsonl` and `build-receipts.jsonl`. Degrades to `empty`.
- ANCESTRY: the CONTEXT ENVELOPE a caller passed. Degrades to `none, standalone`.
- USER: at most ONE question, only when grade >= L3 AND a named hole blocks the compile.
  Degrades to `not-needed`.

Because the primary failure this section exists to fix is compiling from the bare sentence while
ground truth sat one read away (the 2026-10-15 split-brain: a canonical SKILL.md referencing
files that existed only in a deployed copy), the emit contract forces one visible line per
source: an empty source must be seen as empty, not forgotten.

## Source Tags

source: autovibe/SKILL.md #GROUND + #BACKEND evidence

Every GROUND field (actor, cost, evidence) carries `source: env|memory|vault|prior|ancestry|user`.
The tag chains the claim to the packet finding; a GROUND field with no tag is a contextual claim
with no evidence, which the sharp edge `context-free-compile` names as a failure.

Why: GROUND is falsifiable only if its inputs are inspectable. A verdict of "grounded" whose
evidence line cannot be traced to ENV or MEMORY is a taste judgment wearing a verdict's clothes.
The source tag makes the trace mechanical.

## Hole Detection

source: autovibe/SKILL.md #CONTEXT PACKET (USER row + evidence line)

A HOLE is a named fact the compile cannot proceed without (target stack for an existing-system
transform when ENV shows two conflicting manifests; the deployment target for a lifecycle
clarification). Rules:

- Zero findings from ENV+MEMORY+PRIOR-ART on an intent that names an EXISTING project is a failed
  packet: re-read before GROUND, do not ask the user to re-state what is on disk.
- The USER question fires only when grade >= L3 AND a named hole blocks the compile. One question,
  then STOP and wait; never a questionnaire.
- `HOLES: none` is the common case and must still be written; its absence reads as a skipped step.

## Handoff Envelope

source: apex/SKILL.md #HANDOFFS (v1.3) + autovibe/SKILL.md ANCESTRY row

When apex routes a BUILD leaf to autovibe, it passes a CONTEXT ENVELOPE; autovibe consumes it as
the ANCESTRY packet source. The shape is the binding contract between the two skills:

- root intent: the verbatim root ask (never paraphrased)
- crux: the grounded root crux sentence
- deltas: the DELTA lines from ancestor nodes
- artifacts: names of upstream outputs the compile builds on
- constraints: user constraints gathered upstream

A standalone `/autovibe` run prints `ANCESTRY none, standalone`: the envelope is additive, never
required. A run that receives an envelope but prints none has silently dropped its ancestry, which
reads as a context-free compile even though the caller did the grounding work.
