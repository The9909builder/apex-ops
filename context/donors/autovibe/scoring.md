# PACK SCORING — autovibe's self-evaluation rubric

> **NEW in v0.4.0.** autovibe doesn't ship a pack until it scores itself.
> The rubric below is run as the final step before reporting SHIP to the user.
> Threshold: 80/100. Below threshold → re-run affected passes.

---

## WHEN TO SCORE

After P5 QUALITY-WRAP completes, before SHIP batch fires. Score is appended to `RUN-ORDER.md` as a section:

```markdown
## PACK QUALITY SCORE
Score: 87/100
Threshold: 80
Status: ✅ SHIPPED
```

If score < 80, autovibe re-runs the weakest pass(es) and re-scores. Max 2 re-runs per pack. Beyond that → surface to user with the score + gap analysis.

---

## THE 100-POINT RUBRIC

| Category | Max | Description |
|---|---|---|
| Groundedness | 10 | Did PASS 0.0 run AND return grounded verdict? Reads CRUX header + ground-verdicts.jsonl. |
| Decomposition Depth | 20 | Is P1 thorough? Who/JTBDs/capabilities/via-negativa each concrete? |
| Differentiation Strength | 20 | If P1.5 ran, does the charter pass specific/defensible/user-cares? Are design vectors propagated? |
| Domain Coverage | 15 | Does P2 matrix cover all capabilities from P1 without gaps? |
| CATCQ Quality | 15 | Are ACTIONs precise (vocabulary verbs)? TARGETs concrete? CONSTRAINTS quote skills/charters? |
| Quality Wrap Integrity | 10 | Every file has QUALITY WRAP + VERIFY? Anti-pattern guards selected, not generic? |
| Run Order Coherence | 5 | RUN-ORDER.md has explicit deps + parallelizable pairs marked? |
| Security Discipline | 5 | If security-adjacent → scanner gate in RUN-ORDER? |

Total = 100.

---

## SCORING ALGORITHM

```python
def score_pack(pack_dir: Path) -> PackScore:
    pack = load_pack(pack_dir)
    s = PackScore()

    # ── Decomposition Depth (25) ─────────────────────────────────
    proj = pack.read("00-PROJECT.md")
    if has_concrete_persona(proj):           s.add("decomp.persona", 5)
    if jtbds_count(proj) in range(3, 8):     s.add("decomp.jtbds", 7)
    if capabilities_match_jtbds(proj):       s.add("decomp.capabilities", 7)
    if has_via_negativa_list(proj):          s.add("decomp.not_now", 6)

    # ── Differentiation Strength (20, optional) ──────────────────
    if pack.exists("00-TRANSCEND.md"):
        t = pack.read("00-TRANSCEND.md")
        if charter_passes_3_tests(t):        s.add("transcend.charter", 6)
        if superpowers_count(t) >= 3:        s.add("transcend.superpowers", 5)
        if removals_count(t) >= 3:           s.add("transcend.removals", 4)
        vectors = parse_design_vectors(t)
        if vectors_propagated_to_p3(vectors, pack): s.add("transcend.propagation", 5)
    else:
        # No transcend = full 20 prorated as not-applicable bonus
        s.add("transcend.na_bonus", 10)

    # ── Domain Coverage (15) ─────────────────────────────────────
    matrix = parse_domain_matrix(proj)
    capabilities = parse_capabilities(proj)
    if every_capability_has_domain(capabilities, matrix): s.add("domain.coverage", 8)
    if cross_cutting_list_non_empty(proj):                s.add("domain.cross_cutting", 4)
    if stack_picks_have_rationale(matrix):                s.add("domain.rationale", 3)

    # ── CATCQ Quality (20) ───────────────────────────────────────
    catcq_files = pack.glob("0[2-9]-*.md") + pack.glob("1[0-9]-*.md")
    for f in catcq_files:
        if action_uses_vocab_verb(f):     s.add(f"catcq.{f.stem}.action", 5/len(catcq_files))
        if target_lists_concrete_paths(f):s.add(f"catcq.{f.stem}.target", 5/len(catcq_files))
        if constraints_quote_skill(f):    s.add(f"catcq.{f.stem}.skill_quote", 5/len(catcq_files))
        if constraints_quote_charter(f):  s.add(f"catcq.{f.stem}.charter_quote", 5/len(catcq_files))

    # ── Quality Wrap Integrity (10) ──────────────────────────────
    for f in pack.glob("*.md"):
        if f.name == "RUN-ORDER.md": continue
        if has_quality_wrap_section(f):  s.add(f"qw.{f.stem}", 5/n)
        if has_verify_section(f):        s.add(f"verify.{f.stem}", 5/n)

    # ── Run Order Coherence (5) ──────────────────────────────────
    ro = pack.read("RUN-ORDER.md")
    if has_explicit_deps(ro):            s.add("run_order.deps", 3)
    if has_parallelizable_markers(ro):   s.add("run_order.parallel", 2)

    # ── Security Discipline (5) ──────────────────────────────────
    if has_security_adjacent_domain(matrix):
        if scanner_gate_in_run_order(ro):     s.add("security.gate", 5)
        # else: 0 — security-adjacent without gate = critical fail
    else:
        s.add("security.na_bonus", 5)

    # ── Groundedness (10) ────────────────────────────────────────
    if pack.has_flag("--no-ground"):
        s.add("ground.na_bonus", 10)          # prorated as N/A bonus
    else:
        crux = extract_crux_header(pack.read("00-PROJECT.md"))
        verdict = ground_verdict_for_pack(pack_dir)  # reads ~/.kraken/outcomes/ground-verdicts.jsonl
        if verdict == "grounded":             s.add("ground.real", 10)
        # else: 0 — ungrounded or skipped without --no-ground = critical miss

    return s
```

---

## RE-RUN POLICY

| Failed category | Re-run pass | Max retries |
|---|---|---|
| Groundedness | P0.0 (re-check ground-verdicts.jsonl; halt if still ungrounded) | 1 |
| Decomposition Depth | P1 (with /decode if 2nd retry) | 2 |
| Differentiation Strength | P1.5 (with `oracle` persona forced) | 1 |
| Domain Coverage | P2 (re-derive from capabilities) | 1 |
| CATCQ Quality | P3 (per affected file) | 2 |
| Quality Wrap Integrity | P5 (per affected file) | 2 |
| Run Order Coherence | P4 (re-assemble) | 1 |
| Security Discipline | P5 (force scanner gate) | 1 |

Above retry caps → surface to user with score + gaps. Never silent-fail.

---

## OUTPUT FORMAT (appended to RUN-ORDER.md)

```markdown
---

## PACK QUALITY SCORE

**Score:** 87/100
**Threshold:** 80
**Status:** ✅ SHIPPED

### Category breakdown
| Category | Earned | Max |
|---|---|---|
| Groundedness | 10 | 10 |
| Decomposition Depth | 20 | 20 |
| Differentiation Strength | 18 | 20 |
| Domain Coverage | 13 | 15 |
| CATCQ Quality | 12 | 15 |
| Quality Wrap Integrity | 9 | 10 |
| Run Order Coherence | 5 | 5 |
| Security Discipline | 0 | 5 ⚠️ (auth domain present, scanner gate missing — appended automatically)

### Gaps addressed
- Auth domain detected → scanner_scan step appended to step 9

### Next
Open `01-architecture.md`. Begin with step 1 of RUN-ORDER.
```

---

## INTEGRATION WITH `spawner_skill_score`

`spawner_skill_score` evaluates the **skill itself** (autovibe).
`scoring.md` evaluates **a pack autovibe just built**.

The two are independent:
- skill score → "is autovibe a good skill?" → ran by maintainer (you)
- pack score → "is THIS pack ship-ready?" → ran by autovibe at end of every run

Both threshold at 80/100. Both surface gaps with suggestions.

---

## v0.5 — EMPIRICAL FEEDBACK LOOP  (WIRED in v0.5.0 — instrumented, not yet champion)

v0.4 scored against a rubric (analytical, one pass). v0.5 adds the loop that was missing: the
pack's **real outcome** feeds back into the priors that built it, via `mind_decide`.

**Outcome signals** (recorded as `outcome_signal` by `ledger-decide.sh`):
- **executed** — did the pack get fully executed by an LLM? → `shipped_and_used`
- **re-run rate** — how often did the user `/autovibe --refine <slug>`? → `refined_Nx`
- **survival** — does the shipped code still exist 7 days later? → `alive_7d` vs `code_gone_7d`
- **natural recall** — does the pack surface in `mind_retrieve` on its own?

**How it closes (shipped Wave 2):** every SHIP appends a *pending* row to the shared
`~/.kraken/outcomes/decisions.jsonl`, carrying the PRE `mind_retrieve` `memory_ids` (the priors).
`/autovibe --outcome <slug> good|bad` closes it via `mind_decide`, grading those priors by the
real result — so the next pack's PRE retrieval is weighted by what actually shipped.

**Bootstrap trigger (RE-POINTED).** Auto-tuning mode selection + pass-weights begins when the
shared ledger holds **≥ 20 `decided` rows across BOTH sources** (autovibe SHIP + kraken-flow node 8)
— *not* the old "30+ solo packs shipped". autovibe ships ~4 packs; that gate was unreachable.
kraken-flow runs far more often; **co-writing one ledger reaches critical mass at combined volume.**
Check: `grep -c '"status":"decided"' ~/.kraken/outcomes/decisions.jsonl`. Contract: `~/.kraken/outcomes/LEDGER.md`.

---

## ULTRA RUBRIC (v0.6.0 — scores `ULTRA-PROMPT.md`; the pack rubric above does NOT apply in ultra mode)

Runs after PASS Ω, before SHIP. Score appended to `COMPILE-REPORT.md`. Threshold: **80/100**.
Below threshold → re-emit the weakest SECTION(S) from the IR held in `COMPILE-REPORT.md`
(max 2 re-emits) — the front-end passes only re-run if Groundedness or Context Fidelity fail.

| Category | Max | What earns it |
|---|---|---|
| Groundedness | 10 | PASS 0.0 ran and returned grounded; §3 CRUX traces to the verdict (`--no-ground` → prorated N/A, logged) |
| Context Fidelity | 15 | §2 capsule built from a REAL SYSTEM-RECON (files actually read); ≥3 invariants; ≥3 cracks each with evidence; real-vs-assumed constraints labeled; ≤ ~2k tokens |
| Crux Sharpness | 10 | One sentence; names an accepted-cost constraint, not a symptom; evidence line present |
| Charter & Vectors | 15 | Charter passes specific/defensible/user-cares; 3–5 vectors quoted VERBATIM from TRANSCEND; §5 and §7 reference them |
| Ambition Calibration | 15 | Floor stated with system-specific below-floor examples; ceiling names `v_current → v_next`; delete-list seed ≥3 with extension demanded |
| Thinking Protocol | 15 | All 5 stages (A teardown / B crack×5-step / C ripple / D three tiers / E forced selection) each with a NAMED visible artifact; Stage E carries the "below-T3 requires proof" rule |
| Output Contract | 10 | All of a–e demanded (architecture+delta / 3–7 shippable waves / delete list / risk map / per-wave verify); "incomplete → do not present" clause present |
| Quality Wrap & Gates | 10 | Inverted limiters (preserve only INVARIANTS) + anti-slop guards + embedded §9 self-score gate + §10 verify tell |

Total = 100.

### Re-emit policy (ultra)

| Failed category | Re-emit | Max |
|---|---|---|
| Groundedness | re-run PASS 0.0; halt if still ungrounded | 1 |
| Context Fidelity | re-run SYSTEM-RECON (read more of the actual system), recompress §2 | 1 |
| Crux Sharpness | §3 from ground verdict | 2 |
| Charter & Vectors | re-run P1.5 with `oracle` persona forced | 1 |
| Ambition Calibration / Thinking Protocol / Output Contract / Quality Wrap | re-emit that section from template + IR | 2 |
