---
name: reason
description: >-
  The GROUND-Recursive Reasoning Engine — the outer loop all other tools lack.
  Applies GROUND to the OUTPUT, wrapping kraken-flow in a recursive verification
  loop that runs until the answer itself passes GROUND.
---

# /reason — The GROUND-Recursive Reasoning Engine

**The outer loop all other tools lack.** Every Kraken OS reasoning tool
(realthink, think-pipeline, kraken-flow) applies GROUND once to the INPUT.
None apply GROUND to the OUTPUT. /reason wraps kraken-flow in a recursive
verification loop that runs until the ANSWER itself passes GROUND.

> The engine bottoms out when the ANSWER passes GROUND — not when the loop runs out.

This is the NATIVE entry point. The deep substrate lives at:
`~/.spawner/skills/pattern/reason/`

---

## STEP 0 — LOAD THE SUBSTRATE

Read before executing:
```
Read ~/.spawner/skills/pattern/reason/SKILL.md    # full spec + chain contract
Read ~/.spawner/skills/pattern/reason/flow.yaml   # the GROUND-recursive loop
Read ~/.spawner/skills/pattern/reason/skill.yaml  # metadata + pairs_with
```

---

## WHAT /reason IS

```
kraken-flow = the inner engine (DECODE + DEEPEN + REALTHINK + DIVERGE + REFLECT)
/reason     = the outer GROUND-recursive loop around kraken-flow

/reason(input):
  depth = 0
  loop:
    output = kraken-flow(input, --ground)    ← inner engine: TYPE-DETECT + GROUND
    if GROUND-CHECK(output): break            ← OUTPUT grounded: done
    if depth >= max_depth: emit "frame-broken"; break
    input = ungrounded_claim(output)          ← output becomes new input
    depth++
  evidence_grade(output)                      ← chip model tiers
  compress_to_axiom(output)                   ← 1-line falsifiable claim
  mind_remember(output, salience=0.85)        ← persist
```

The critical distinction from kraken-flow:
- kraken-flow GROUND checks: "is the PROBLEM real?"
- /reason GROUND-CHECK asks: "is the ANSWER real?"
A grounded problem can still produce an ungrounded answer.

---

## WHEN TO USE

| Use /reason when...                             | Use /kraken-flow when...                  |
|-------------------------------------------------|-------------------------------------------|
| You want depth — don't know how many passes     | You want the full speak→done spine        |
| kraken-flow output feels shallow                | You have a multi-domain vague intent      |
| You want the engine to self-verify its answers  | You want DIVERGE + REFLECT + AUTOVIBE     |
| "I want to understand this to its core"         | "I want this turned into a build"         |

---

## MODES

```
/reason "<question>"              # full recursive → stops when grounded (default)
/reason "<question>" --depth 3    # max_depth override (default: 5)
/reason "<question>" --once       # single-pass (equivalent to /kraken-flow --ground)
/reason "<question>" --build      # after grounding, pass to autovibe for build plan
/reason "<question>" --deep       # opt into Kraken vault writes (off by default)
```

---

## OUTPUT CONTRACT

```
═══════════════ KRAKEN-REASON ═══════════════
Input      : <the original question>
Depth      : L<n>  (iterations to grounded output)
Grounded ⛔ : ✅ OUTPUT grounded  |  ⚠️ FRAME-BROKEN (real question surfaced at L<n>)
Crux       : <the grounded crux — passes GROUND on its own>
Evidence   : research_grounded | benchmark_grounded | exploratory | realworld
Axiom      : <one-line falsifiable claim — the core answer>
THE ANSWER : <grounded · evidence-tagged · axiom-compressed>
Memory     : ~/.mind/ (salience=0.85)
═════════════════════════════════════════════
```

---

## AXIOM
> **The engine bottoms out when the ANSWER passes GROUND — not when the loop runs out.**

## Status
`instrumented, not yet champion` — needs 3+ grounded runs + quality_rubric >= 60 before promotion.

## Substrate
`~/.spawner/skills/pattern/reason/` →
`SKILL.md` (full spec) · `flow.yaml` (recursive loop) · `skill.yaml` (metadata)

SKILL_COMPLETE
