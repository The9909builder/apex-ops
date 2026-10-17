# TOURNAMENT — autovibe v2.0 multi-candidate compile backend

> One compile is an opinion. A tournament is a verdict.
> The fusion of "1000x better" + "optimized" + "more capable" into ONE mechanism.

This is the third compiler backend, beside `pack` (greenfield directory) and `ultra`
(single ULTRA-PROMPT.md). Tournament does not replace ultra — it wraps it: each
candidate IS a full §0–§10 ULTRA prompt, and the winner ships as `ULTRA-PROMPT.md`.
Single-pass ultra stays the default fallback (`--single` forces it). Everything is additive.

---

## WHY THIS EXISTS — THE CRUX IT BREAKS

autovibe v1.0 compiles ONCE, self-scores against a STATIC rubric (scoring.md, SHIP ≥ 80),
re-runs the weakest pass at most twice. The quality signal is the compiler grading its own
opinion. That is a structural ceiling: **no single generation out-thinks a panel built to
refute it.** "1000x better" is not a bigger rubric or more passes — it is breaking that ceiling.

One mechanism delivers all three of the user's axes at once:

| Axis | How the tournament delivers it |
|------|--------------------------------|
| **1000x better** | adversarial judges score candidates against the REAL downstream signal (would a `/ship` + `scanner` actually pass), not against the self-score rubric |
| **optimized** | the K candidates generate IN PARALLEL — wall-clock ≈ one candidate, not K. More quality at the SAME latency |
| **more capable** | each candidate is compiled under a DIFFERENT lens, so the tournament explores the option space instead of committing blind to one |

---

## WHEN IT FIRES

Auto-on when ALL hold: ultra backend selected AND (route is L4 OR `--ambitious`/`--10x` OR
the intent is a transformation-class ask carrying a magnitude word — "1000x", "next level",
"world-class", "overhaul"). Explicit: `--tournament` / `--tourney`. Force off: `--single`
(restores v1.0 single-pass ultra verbatim). Greenfield pack intent + `--tournament` →
ask which backend; a pack tournament is a separate future surface, not this one.

`--max` raises K from 3 to 5 and J from 3 to 5 (deeper search, more cost).

---

## THE PROTOCOL — 5 STAGES (each names its gate)

### T0 — LENS-CAST
From the GROUND crux (PASS 0.0) + TRANSCEND design vectors, cast **K diverse lenses**
(K = 3 default, 5 with `--max`). Lenses MUST differ in KIND, not in parameter. The canonical set:

- **MVP-first** — the smallest thing that ships and proves the crux. Ruthless via-negativa.
- **Ceiling-first** — maximum defensible ambition; what the system could be if nothing were cut.
- **Risk-first** — design from the failure modes backward; the prompt that hardens what breaks.
- **Simplicity-first** — fewest moving parts; delete before add; the elegant minimal frame.
- **Domain-expert** — go deep on the single highest-leverage domain instead of broad.

Pick K lenses that genuinely conflict with each other (MVP-first vs Ceiling-first is a real
tension, not a rephrase). Print the cast: `LENS-CAST: [MVP-first, Ceiling-first, Risk-first]`.

**GATE:** K ≥ 3 lenses, each with a distinct `Lens:` label. Two lenses that would produce the
same candidate = not a cast. Recast.

### T1 — PARALLEL GENERATE
Generate **K candidate ULTRA prompts in parallel** — each a full §0–§10 ULTRA prompt compiled
under its lens, written to `candidate-<lens>.md`. Each candidate's §0 grounds in the SAME real
cracks (from SYSTEM-RECON) but its §5 ambition floor/ceiling and §7 wave contract reflect its lens.

- **Workflow-capable harness:** emit a `parallel()` of K agents, one per lens (see § WORKFLOW EMISSION).
  Wall-clock = slowest candidate. This is where "optimized" is literally true.
- **Pure markdown / no infra:** Claude generates K candidates in one turn, each genuinely distinct
  because the lens constrains it. Still cheaper than K separate manual runs, and the diversity is real.

**GATE:** K candidate files exist; no two are near-duplicates (distinct §5 CEILING + §7 wave sets).

### T2 — ADVERSARIAL JUDGE (the ceiling-breaker)
**J judges** (J = 3 default, 5 with `--max`), each a DIFFERENT refutation lens, score EVERY
candidate against the **reality rubric** below — not the self-score rubric. Judges default to
**REFUTED when uncertain** (anti-theater). A candidate passes an axis only on ≥ majority of judges.

THE REALITY RUBRIC (each axis 0–25, judged adversarially, total 100):

| Axis | The judge asks | Refute-default failure |
|------|----------------|------------------------|
| **SHIP-PASS** (25) | if an LLM executed this prompt, would the system it forces pass a `/ship` gate? | forces vapor / unbounded scope / no working slice |
| **SCANNER-PASS** (25) | would `scanner_scan` find criticals in what this prompt forces? | ignores auth/secrets/inputs in a security-adjacent build |
| **WAVE-REAL** (25) | does it force 3–7 genuinely shippable waves + a delete list + a risk map + per-wave verify? | "waves" are phases-on-paper with no shippable slice |
| **GROUND-REAL** (25) | does §0 ground in REAL cracks (file/metric/incident), not generic ambition? | §0 is filler; recommendations unanchored |

Judge lenses (assign one per judge): **Shipper** (SHIP-PASS focus), **Security** (SCANNER-PASS
focus), **Skeptic** (WAVE-REAL / "where is the vapor"), **Grounder** (GROUND-REAL / "what is
unanchored"). With J = 3 use Shipper + Security + Skeptic; `--max` adds Grounder + a second Skeptic.

Write each verdict: `candidate-<lens> | judge=<lens> | ship=NN scan=NN wave=NN ground=NN | total=NN | refutes: <one line>`.

**GATE:** every candidate carries ≥ J verdicts; verdicts cite the reality axes (not the self-score
rubric); a candidate's total is the median across judges (robust to one outlier judge).

### T3 — SYNTHESIZE WINNER
Rank candidates by median reality score. The winner is the top candidate. If the top two are
within the **delta threshold** (default 6 pts), do not just pick — **SYNTHESIZE**: graft the
runner-up's highest-scoring section into the winner (e.g. winner's §7 wave contract + runner-up's
§2 risk map). The synthesized artifact is the shipped `ULTRA-PROMPT.md`.

Record: `WINNER: candidate-<lens> | median=NN | delta-over-runner-up=NN | grafted: <section> from <lens> | none`.

**GATE:** a winner is named with `delta-over-runner-up ≥ 3` (after any graft). Delta ≈ 0 means the
tournament did not discriminate — candidates too similar (recast T0) or judging too coarse (sharpen
the refute prompts). The shipped winner MUST itself pass `autovibe-gate.sh ultra` (the v1.0 floor
is a subset of the tournament floor — a tournament winner is never below a single-pass ship).

### T4 — RUBRIC FEEDBACK (the closed reality loop)
Record WHAT made the winner win into `~/.kraken/outcomes/autovibe-rubric-weights.json`:
the winning lens, the axes it dominated, the sections that scored highest. The NEXT compile's
scoring reads these weights — the rubric becomes **reality-tuned, not static**. This is the loop
that v1.0 only closed MANUALLY via `/autovibe --outcome`; the tournament closes it AUTOMATICALLY
every run (and `--outcome good|bad` still reconciles the PREDICTED signal against the ACTUAL ship).

Weights record shape (append one object):
```json
{"ts":"<iso>","slug":"<slug>","winner_lens":"Risk-first","dominated_axes":["scan","ground"],
 "delta":11,"top_sections":["§0","§7"],"k":3,"j":3,"mode":"tournament"}
```

**GATE:** the weights file gained a row this run. No row = a one-off bake-off, not a learning
tournament — the loop did not close.

---

## OUTPUT CONTRACT

Write to `~/prompt-packs/<slug>/`:
1. `ULTRA-PROMPT.md` — the winner (or synthesized winner), a full §0–§10 ULTRA prompt.
2. `TOURNAMENT.md` — LENS-CAST · K candidate scores · all judge verdicts · WINNER + delta + graft · rubric-update record.
3. `COMPILE-REPORT.md` — IR traceability (written by the gate).
4. `candidate-<lens>.md` × K — the candidates (kept; refine mode reads them).

Then: `autovibe-gate.sh tournament ~/prompt-packs/<slug>/` must exit 0 before SHIP.
Report: path · winner lens · median reality score · delta · "the winner survived J adversarial
judges on the real ship signal — paste ULTRA-PROMPT.md into any LLM."

---

## WORKFLOW EMISSION (optional accelerator, harness-gated)

When the executing harness exposes a Workflow/parallel-agent tool, the tournament is not just
"more quality" — it is genuinely parallel and so genuinely faster. Emit (do not run it yourself):

```js
// T1 parallel generate + T2 pipeline judge — candidates judged as each finishes
const winners = await pipeline(
  LENSES,                                              // T0 cast
  lens => agent(genPrompt(lens), {schema: ULTRA, phase:'Generate'}),     // T1
  cand => parallel(JUDGES.map(j => () =>                                  // T2
    agent(`Refute as ${j} vs the reality rubric. Default REFUTED if unsure.`,
          {schema: VERDICT, phase:'Judge'}).then(v => ({...cand, j, v})))))
// T3 synthesize + T4 feedback in plain code
```

Pure-markdown fallback ALWAYS works — every layer is additive (the autovibe invariant). The
Workflow path is the speed dividend, not a dependency.

---

## SHARP EDGES (tournament-specific; gate IDs match autovibe-gate.sh)

- **tournament-candidates-collapse:** K candidates share one lens → not a tournament, a copy.
  Watch for: identical §5 CEILING across candidates. Gate: distinct `Lens:` + non-duplicate sections.
- **judge-grades-selfscore:** judges score the v1.0 self-rubric instead of the reality axes → the
  old ceiling in disguise. Watch for: verdicts with no ship/scan/wave/ground breakdown.
- **winner-no-delta:** winner declared with delta ≈ 0 → the tournament didn't discriminate.
  Watch for: `delta-over-runner-up < 3`. Recast lenses or sharpen the refute prompts.
- **rubric-feedback-skipped:** no row appended to autovibe-rubric-weights.json → a bake-off, not a
  learning tournament; the reality loop never closed.
- **parallel-is-sequential-theater:** claiming K candidates but generating one and paraphrasing it.
  Watch for: candidates that differ only in wording. The lens must change the SHAPE (§5/§7), not prose.
- **judge-is-yes-man:** judges that pass every candidate on every axis → refute-default not applied.
  Watch for: all-candidates-pass-all-axes. A real panel kills weak candidates.

---

## INVARIANTS PRESERVED (what v2.0 must not lose)

1. Pure markdown + Claude — no API keys, no infra. The Workflow path is optional, never required.
2. Single-pass ultra is the verbatim fallback (`--single`). Every v1.0 path still works.
3. The gate is the architecture: a tournament is real only if it passes `autovibe-gate.sh tournament`.
4. The winner is never below the v1.0 ship floor — `check_ultra` runs on the winner inside the gate.
5. No synthetic learnings: the rubric-weights row records what was OBSERVED in this run, not invented.
