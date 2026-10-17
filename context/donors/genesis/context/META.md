---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Glossary

source: genesis/SKILL.md

| Term | Definition |
|------|-----------|
| **EXPLODE** | Phase 1: generate 20+ raw ideas including 3+ uncomfortable or absurd ones before any evaluation; the structural constraint that forces divergence past obvious-space |
| **STRUCTURE** | Phase 2: filter ideas to the top 20-30% using the Goldilocks filter (specific enough to act on AND flexible enough to adapt); each survivor needs a `first_action` naming a file, tool, or command |
| **DEEPEN** | Phase 3: apply the ULTRATHINK 10-letter gate to top candidates; U/T/N are the three hard gates; the other 7 letters deepen quality |
| **SYNTHESIZE** | Phase 4: combine best elements across candidates and test emergence; the output must name Z — a capability that A+B produces but neither A nor B can alone |
| **EVOLVE** | Phase 5: capture what worked, what failed, ONE reusable pattern, ONE hypothesis; write to mind_remember or learnings.jsonl; the mechanism that makes sessions compound |
| **ULTRATHINK** | The 10-letter gate (U through K): U=real problem, L=depth needed, T=new capability, R=plan survives its own logic, A=operational wisdom, T=value proof, H=meta-patterns, I=system connections, N=minimal next action, K=most intelligent version |
| **Emergence** | The property of synthesis where A+B produces Z and Z exceeds X+Y; Z names a capability neither A nor B can produce alone; synthesis without emergence is concatenation |
| **MODE** | The execution path selected for a session: FULL (phases 1-5), EXPRESS (phases 1,3,5), REVIEW (phases 3-4), EVOLVE-ONLY (phase 5) |
| **UUID** | The canonical Mind API user identifier: `550e8400-e29b-41d4-a716-446655440000`; old UUID `477b8a03` fails silently with no error |
| **PROTOCOL** | The full GENESIS system including all five phases, gates, recovery paths, and EVOLVE hook; not just the divergence step; applies to its own output as a self-consistency check |

---

## Reading Order

source: genesis/SKILL.md

Read in this order to build a working mental model before running a session:

1. **taxonomy.md** — understand the 8 categories and when each fires; lets you select MODE correctly before opening SKILL.md
2. **principles.md** — the 5 grounded rules; memorize the falsification conditions; these are what the gates enforce
3. **mechanisms.md** — understand the cause->effect chains; mechanisms are what you apply when a gate fails
4. **anti-patterns.md** — the 7 failure modes; read before Phase 1 to know what to catch in yourself during the session
5. **few-shots.md** — 3 worked examples; read to calibrate what "good" looks like in each phase before touching a live problem
6. **edge-cases.md** — read only when a principle appears to break; not needed for standard runs

**Never read** edge-cases before principles — edge cases require the baseline to be meaningful.

---

## Bootstrap Recipe

source: genesis/SKILL.md (PROTOCOL-agnostic; replace domain-specific words with your domain)

A domain-agnostic 5-step recipe for bootstrapping GENESIS context in any new domain:

1. **List the fundamental categories of this domain.** Name 5-8 categories with a definition and a "when to use" condition for each. If a category cannot answer "when to use," it is not a category — it is an abstraction.

2. **Identify the compounding mechanism.** Every domain has ONE mechanism that makes sessions compound instead of reset. Find it, name it, and make it non-optional. In this domain it is EVOLVE. In your domain: what must run at the close of every session for the next session to be better?

3. **Name the primary divergence gate.** What is the structural constraint that forces the practitioner to go beyond the obvious before selecting? In this domain it is the 20-idea minimum before evaluation. In your domain: what count, check, or step must complete before any selection is allowed?

4. **Define the emergence test.** Every synthesis domain has a test for whether output is new knowledge or reorganized existing knowledge. In this domain: "A+B enables Z which neither alone can do." Define the equivalent sentence for your domain before any synthesis step is allowed.

5. **Write the EVOLVE fallback path.** When the primary capture mechanism (mind_remember) is unavailable, what is the fallback that prevents zero capture? In this domain: learnings.jsonl with `"pending_mind_sync": true`. In your domain: define the fallback before the first session runs, not after the first session fails.
