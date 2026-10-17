---
name: think-pipeline
description: Meta-pattern reasoning engine — fills the 7-slot schema for any vague problem in a single chain. CAPTURE → LENS → SLOT-FILL → IDEARALPH → RECURSIVE TEST → SAVE. Default uses Mind+Spawner+IdeaRalph (always-on tier). Add --deep to also write Kraken vault + entity graph.
trigger: /think-pipeline
---

# /think-pipeline

Executable wrapper around the meta-pattern in `/home/roshish/vibeship-x-kraken/think.md`.

Turns a vague problem into a filled 7-slot schema (mindset shift, core loop, engine, artifact types, patterns, anti-patterns, axiom) plus optional PRD/architecture/checklist.

**Identity move:** curator of constraint, not author of instruction. Stack references; do not write paragraphs. The form IS the function.

## Usage

```
/think-pipeline "<vague problem>"            # default chain (~10 min, mind+spawner+idearalph)
/think-pipeline "<problem>" --build          # also run prd → architecture → checklist
/think-pipeline "<problem>" --deep           # also write Kraken vault + entity graph (opt-in)
/think-pipeline "<problem>" --gap            # if a lens reveals a prereq gap, branch into /deep-understanding --gap
/think-pipeline --recursive                  # run pipeline on itself (validates the mechanism)
```

## Execution — DO THESE IN ORDER

### Step 0 — Read the meta-pattern source of truth

Always read first:
- `/home/roshish/vibeship-x-kraken/think.md` — the 540-line spec (Part 1 Lens 7 = the schema; Part 2 = the formula; Part 9 = tool contracts; Part 10 = the 7-checkbox recursive test)

If user passed `--recursive`, the problem IS the pipeline itself. Use Part 8 (Worked Example: Kraken OS) as the seed.

### Step 1 — CAPTURE (memory pull, ~30 sec)

```python
mind_retrieve(query="<problem keywords>", limit=5, min_salience=0.5)
spawner_remember(action="recall", query="<problem keywords>")
```

Resolve the user UUID once per session (sharp edge: Mind takes UUID, not email).
Read `~/.kraken/think-pipeline/learnings.jsonl` tail — last 5 rows give domain priors.

### Step 2 — LENS (3 reasoning frames in parallel, ~2 min)

Default tier (always-on): apply manually using the templates in `think.md` Part 1, Lenses 1-7. Don't skip.

For each of these three, write 2-4 sentences of output:
1. **First Principles** — what is the irreducible truth under the surface advice?
2. **Via Negativa** — what is being destroyed / left out / made obsolete?
3. **Second Order** — if everyone adopts this, what new bottleneck emerges? Where does it break?

Optional `--deep` tier (Kraken opt-in):
```python
mcp__kraken__think_start(topic="<problem>")
mcp__kraken__think_framework(framework="first-principles")
mcp__kraken__think_framework(framework="via-negativa")
mcp__kraken__think_framework(framework="5-whys")
mcp__kraken__think_complete()
```

### Step 3 — GAP CHECK (only if a lens flagged a prereq, ~1 min)

If any lens output contains "I don't actually understand X well enough":
→ Stop the chain. Branch into `/deep-understanding --gap "<X>"`. Resume after.

### Step 4 — SLOT-FILL (~5 min — the core deliverable)

Open the schema from think.md Part 1, Lens 7. Fill all 7 slots for THIS problem:

```
1. MINDSET SHIFT     — FROM "<verbal-instruct frame>" TO "<artifact-curate frame>"
2. CORE LOOP         — 4 verbs: SHOW → PRODUCE → TEST → REFINE (one variable)
3. ENGINE            — name the generative engine (LLM / market / runtime / time / your brain)
4. ARTIFACT TYPES    — exactly 5, each carrying distinct signal
5. PATTERNS          — exactly 5 interaction verbs with examples
6. ANTI-PATTERNS     — exactly 6 traps, each = one principle inverted
7. AXIOM             — one line that re-anchors identity (curator > author)
```

Stuck on a slot? Pull the closest-matching domain from `think.md` Part 3 (Business / Systems / Content / Personal / Learning) and edit it.

### Step 5 — IDEARALPH CHAIN (~3 min default; ~10 min with --build)

```python
# Default: validate the schema as an idea
idearalph_brainstorm(topic="<filled schema as one paragraph>")
idearalph_validate(idea="<top candidate>")
idearalph_refine(idea="<top>", mode="single", maxIterations=1)

# --build only:
idearalph_prd(idea="<refined>", level="napkin")
idearalph_architecture(idea="<refined>")
idearalph_checklist(idea="<refined>", projectName="<slug>")
```

These tools return prompt templates — Claude executes them and generates the actual content.

### Step 6 — RECURSIVE TEST (~2 min — the gate)

Apply the 7 checkboxes from `think.md` Part 10 to your filled schema:

1. ☐ Mindset shift (FROM → TO) in first 3 lines
2. ☐ 4-step loop (verbs only, all action)
3. ☐ Exactly 5 input types, each distinct signal
4. ☐ 5 interaction patterns (verbs, with examples)
5. ☐ 6 anti-patterns (each principle inverted)
6. ☐ 1-line axiom that re-anchors identity
7. ☐ Cuts everything that isn't the mechanism

**If any fail → loop back to Step 4 with refined input.** No exceptions.

### Step 7 — SAVE (~1 min — close the loop)

Write the run output:
```
~/.kraken/think-pipeline/runs/<domain-slug>-<YYYYMMDD>.md
```

Append one row to the ledger:
```bash
echo '{"ts":"<ISO8601>","domain":"<slug>","input":"<problem>","slots_filled":7,"recursive_test":"PASS|FAIL","axiom":"<one line>","time_min":<N>,"output":"<path>","mode":"default|build|deep"}' \
  >> ~/.kraken/think-pipeline/learnings.jsonl
```

Persist the axiom (default tier):
```python
mind_remember(content="<axiom + path>", salience=0.9, temporal_level=4, content_type="insight")
spawner_remember(content="<schema path + axiom>", scope="project")
```

Optional `--deep` tier (Kraken opt-in):
```python
mcp__kraken__memory_remember(content="<full schema>", type="insight")
mcp__kraken__create_note(vault="Kraken Starting", path="11-Deep-Understanding/<slug>.md", content=<full schema>)
```

## Kraken OS Wiring — Auto-trigger Conditions

This skill fires automatically (without explicit `/think-pipeline` command) in three situations:

**Situation 1 — BLOCK 1.5 of the self-audit** (`KRAKEN_SELF_AUDIT_PROMPT.md`)
When BLOCK 1 names verb-class = `decide / synthesize / strategy` AND task spans 3+ domains:
→ Run Step 2 (LENS) + abbreviated Step 4 (mindset shift + core loop only).
→ Time budget: 2-3 minutes. Skip Steps 1, 5, 6, 7.
→ Paste the lens output into BLOCK 1.5, let it inform BLOCK 3 (Orchestration Choice).

**Situation 2 — L3/L4 complexity grade in kraken-os**
When `spawner_orchestrate` routes to L3 (multi-domain, auth/schema, new domain) or L4:
→ Before Phase 2 PLAN fires: run Steps 1-4 (CAPTURE → LENS → GAP CHECK → SLOT-FILL).
→ The filled 7-slot schema becomes the PLAN.md seed.
→ Skip IDEARALPH and RECURSIVE TEST for speed on L3; run full chain on L4.

**Situation 3 — Before /plan-eng-review or /plan-ceo-review**
These plan review skills evaluate structure. Without a filled schema, they review symptoms.
→ think-pipeline must run first. The schema IS the plan. The review tests whether the schema holds.

**Quick mode (Situation 1 only):**
```
Steps to run:  2 (LENS) + 4 (abbreviated)
Steps to skip: 1 (memory pull), 3 (gap check), 5 (idearalph), 6 (recursive test), 7 (save)
Output format: 3 × 2-sentence lens outputs + mindset shift (FROM→TO) + core loop (4 verbs)
Time budget:   2-3 minutes
```

**Do NOT auto-trigger for:**
- L1/L2 tasks (single file, clear bug fix, status check)
- Tasks where verb-class = build / fix / verify (execution, not thinking)
- Any task where the output is a file diff, not a decision

---

## Sharp edges (memorize before running)

1. **UUID not email** — `mind_retrieve(user_id=UUID)`. Email crashes with hex error.
2. **Kraken is opt-in** — never call `mcp__kraken__*` without `--deep` flag or explicit user request.
3. **TLB is banned** — never call any TLB tool. Never. (User feedback memory.)
4. **5/5/6 counts are exact** — schema fails the recursive test if you write 4 artifact types or 7 anti-patterns.
5. **Refine ONE thing** — between iterations, change exactly one variable. "Random iteration" kills the loop.
6. **Show, don't describe** — if you find yourself writing a paragraph, stop and pull a reference instead.
7. **Time bound the chain** — default: 10 min. --build: 25 min. --deep: 35 min. If you exceed, you're in monolithic-spec-dump anti-pattern.
8. **Recursive test is a HARD gate** — no save unless 7/7 pass.

## Anti-patterns the skill itself avoids

- ❌ Calling Kraken tools by default (violates CLAUDE.md governance)
- ❌ Replacing the user's reasoning with a tool wrapper (the lenses are mental, not API calls)
- ❌ Saving to learnings.jsonl without recursive test passing (corrupts the dataset)
- ❌ Skipping mind_retrieve at start (loses cross-session context)
- ❌ Writing prose summaries instead of filled schemas (defeats the form-is-function principle)

## Output contract

End every run with this block, copy-paste ready:

```
═══════════════ THINK-PIPELINE RUN COMPLETE ═══════════════
Domain        : <slug>
Mode          : default | build | deep
Time          : <N> min
Recursive     : PASS (7/7) | FAIL (n/7) [+ which slot failed]
Schema path   : ~/.kraken/think-pipeline/runs/<file>.md
Axiom         : <one line>
Next action   : <one concrete step the user can take in <15 min>
═════════════════════════════════════════════════════════════
```
