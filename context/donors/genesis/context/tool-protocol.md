---
last_verified: 2026-06-28
freshness_clock: 2026-06-28
synthesized: true
source_basis: "SKILL.md (tfc_context_forge)"
confidence: "0.9"
forge_domain: "genesis"
---

## Tool Usage

source: genesis/SKILL.md#tool-availability-check

Run TOOL AVAILABILITY CHECK before Phase 1. Emit "TOOLS: mind=[OK/DOWN] spawner=[OK/DOWN] idearalph=[OK/SKIP]".

```bash
curl -sf http://127.0.0.1:8000/health && echo "mind:OK" || echo "mind:DOWN"
```

### mind_retrieve
**Phase:** Session start, before Phase 1 EXPLODE.
**Required:** Preferred (not blocking).
**Call:** `mind_retrieve(user_id="550e8400-e29b-41d4-a716-446655440000", query="genesis synthesis [domain] patterns", limit=5)`
**Purpose:** Surfaces past evolution logs; skips techniques that previously failed; prioritizes working patterns.
**On unavailable (port 8000 down):** Skip past-learning load. Read the last 5 lines of `learnings.jsonl` manually instead. Proceed without halting.

---

### mind_remember
**Phase:** After Phase 4 (high-confidence synthesis result) and Phase 5 EVOLVE.
**Required:** Preferred (blocking substitute = learnings.jsonl write).
**UUID:** Always `550e8400-e29b-41d4-a716-446655440000`. Old UUID `477b8a03` fails silently with no error returned.
**After Phase 4:** `mind_remember(..., content="GENESIS synthesis: [Z sentence]", temporal_level=2, salience=0.8)`
**After Phase 5:** `mind_remember(..., content="GENESIS evolution: worked=[X] | failed=[Y] | pattern=[Z] | next=[hypothesis]", temporal_level=2, salience=0.75)`
**On unavailable:** Write to learnings.jsonl with `"pending_mind_sync": true`. Mark STATE `MIND_API_AVAILABLE=false`. Do NOT skip EVOLVE — switch to fallback path instead.

---

### spawner_emit
**Phase:** Phase 5 end.
**Required:** Optional.
**Call:** `spawner_emit(type="progress", message="GENESIS synthesis complete | evolution logged")`
**Purpose:** Signals orchestrators that GENESIS synthesis track is complete; used by kraken-flow and spawner_orchestrate to coordinate parallel tracks.
**On unavailable:** Skip emit. Proceed normally.

---

### idearalph_brainstorm
**Phase:** Phase 1 EXPLODE, when idea generation stalls past idea 12.
**Required:** Optional.
**Purpose:** Returns a prompt template — Claude executes the template and generates the actual ideas; the tool does not generate ideas itself.
**On unavailable:** Use manual divergence techniques (CROSS-Domain Stealing, Absurd Amplification). Do NOT halt.

---

### spawner_remember
**Phase:** After Phase 4, when project-level context should persist beyond the session.
**Required:** Optional.
**Purpose:** Stores the synthesis approach and emergence result Z for spawner-scoped memory, available in future sessions via spawner_analyze.
**Note:** Use ONLY for project-level synthesis results, not for session-level evolution logs (those go to mind_remember).
