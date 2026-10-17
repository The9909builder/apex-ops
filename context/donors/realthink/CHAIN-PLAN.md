# The Kraken Deep-Chain — Architecture Blueprint

> Captured 2026-06-01. Blueprint for: (1) realthink as a full YAML spawner skill,
> (2) the speak-to-done chain with two NEW reasoning moves the user asked for.
> Build-ready; each node maps to an existing Kraken asset or is flagged NEW.

## What the user actually wants (verbatim intent, decoded)

1. **Speak messy → everything gets done.** One chain from raw speech to executed output.
2. **DEEPEN** — the chain asks questions "deeper into deeper into deeper," *from scratch*,
   until a vague thing ("fix a person's life") is drilled down to something atomic and
   groundable. Progressive Socratic descent, not one-shot.
3. **DIVERGE → REFLECT** — somewhere the system "gives answer with different options,"
   then has "a place where it feels its own way from reading the options so it has a
   better idea." = generate options, then self-critique/synthesize a sharper frame
   before committing. (This is the reflexion / tree-of-thoughts pattern.)
4. **realthink built in depth** as a proper spawner skill with full YAML (not one .md).

## The chain — DESCEND → DIVERGE → CONVERGE → EXECUTE

```
  SPEAK (messy, however it comes out)
    │
    ▼
  ① DECODE        messy intent ──► structured spec            [/decode — EXISTS]
    │
    ▼
  ② DEEPEN  🌀     recursive Socratic descent, layer by layer  [NEW — move A]
    │             stops at ATOMIC: 1 actor · 1 cost · 1 action
    ▼
  ③ REALTHINK     grounding gate → crux → ripple → cut         [/realthink — JUST BUILT]
    │
    ▼
  ④ DIVERGE  🔀    generate 3-5 GENUINELY distinct options      [idearalph_brainstorm — EXISTS]
    │
    ▼
  ⑤ REFLECT  🪞     read own options as a critic, score,        [NEW — move B]
    │             synthesize a BETTER frame ("feel its way")
    ▼
  ⑥ THINK-PIPELINE fill the 7-slot mechanism schema            [/think-pipeline — EXISTS]
    │
    ▼
  ⑦ AUTOVIBE      compile to executable prompt-pack            [autovibe — EXISTS]
    │             ("everything gets done")
    ▼
  ⑧ MIND          remember crux + move; depth COMPOUNDS        [mind_remember — EXISTS]
```

**Shape insight:** a linear pipe can't think. This shape can — it goes DOWN (deepen to
the atom), FANS OUT (options), pulls BACK IN (reflect to one frame), then BUILDS. That
descend-diverge-converge motion is how good reasoning actually works.

## Node specs

| # | Node | Input | Mechanism | Output | Asset | New? |
|---|------|-------|-----------|--------|-------|------|
| 1 | DECODE | raw speech | intent → fields | structured spec | /decode | — |
| 2 | DEEPEN | spec | recursive WHY descent, ≤5 layers | atomic groundable problem | — | 🆕 A |
| 3 | REALTHINK | atomic problem | gate → crux → ripple → cut | the one leverage move | /realthink | — |
| 4 | DIVERGE | the move | 3-5 distinct paths | option set | idearalph_brainstorm | — |
| 5 | REFLECT | option set | self-critique + synthesize | sharper frame + pick | — | 🆕 B |
| 6 | THINK-PIPELINE | frame | 7-slot schema | mechanism design | /think-pipeline | — |
| 7 | AUTOVIBE | schema | CATCQ prompt-pack | executable prompts | autovibe | — |
| 8 | MIND | crux+move | salience write | persistent memory | mind_remember | — |

## The two NEW mechanisms (the real work)

### 🌀 A. DEEPEN — recursive Socratic descent
- **Depth budget:** 5 layers max (anti-infinite-loop).
- **Each layer:** exactly ONE question that *narrows* (WHY/WHO/WHICH-specifically).
- **Stop condition (ATOMIC):** reached when problem = 1 real actor · 1 measured cost ·
  1 next action. Reuse /decode's atomic principle (1 file/1 function) but for life-problems.
- **Hands off to:** REALTHINK's GROUND gate (which then refuses if still ungrounded).
- **Anti-pattern it kills:** answering a vague question at the vague altitude it was asked.

### 🪞 B. DIVERGE → REFLECT — generate then feel its own way
- **DIVERGE:** 3-5 options that differ *in kind*, not in wording. (idearalph_brainstorm.)
- **REFLECT:** the model re-reads its OWN options as an adversarial critic — scores each
  on leverage/feasibility/groundedness, names what each option reveals, then SYNTHESIZES
  a frame better than any single option. Output is a sharper *understanding*, not just a vote.
- **Why it matters:** this is the "feel its own way from reading options" the user described.
  Divergence without reflection is a menu; reflection is where the better idea is born.

## Build waves (small, capacity-safe)

- **Wave 1 — DONE:** this blueprint + Mind save.
- **Wave 2 — realthink full YAML** (`spawner_skill_new`): skill.yaml manifest + SKILL.md
  (router) + `deepen.yaml` (the 5-layer descent spec) + register in registry.yaml.
  Needs fresh context — run after /compact.
- **Wave 3 — the spine orchestrator skill** that runs nodes ①–⑧ in order, with DEEPEN
  and REFLECT wired in. Name TBD (user decides).
- **Wave 4 — wire + test** DEEPEN + REFLECT on one real problem end to end.

## Open decisions (user's call)
1. **Name** of the spine command (`/deepchain`? `/spine`? `/kraken-flow`?).
2. Is **DEEPEN** a *mode of realthink* (`/realthink --deepen`) or its **own skill**?
3. Default **depth** (layers) and **option count** — 5 / 4? user-tunable?
4. Does REFLECT run **once** or **loop** until the frame stops improving (reflexion loop)?
