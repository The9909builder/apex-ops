#!/usr/bin/env bash
# autovibe — autovibe-gate.sh  (v0.8.0 — the closed-loop compiler)
# ─────────────────────────────────────────────────────────────────────────────
# THE ONE GATE ENGINE.  Mode-dispatched, bash-native, zero external infra.
#
#   autovibe-gate.sh ultra      --ultra <ULTRA-PROMPT.md> [--report <path>]
#   autovibe-gate.sh tournament <tournament-dir>          # v2.0 multi-candidate floor
#   autovibe-gate.sh pack      <pack-dir>                [--report <path>]
#   autovibe-gate.sh transcend <00-TRANSCEND.md | charter-file>
#   autovibe-gate.sh substrate [<skill-dir>]      # WARN-only freshness check
#   autovibe-gate.sh ground    <pack-dir | file>  # ground-verdict presence
#
# v0.7.0 shipped a machine gate for ULTRA only (precompile-gate.sh --ultra).
# v0.8.0 makes the gate the architecture, not a flag: PACK gets the same
# blocking floor, TRANSCEND gets a machine charter-floor, and EVERY run writes
# a COMPILE-REPORT.md (both backends) as the gate's exit artifact.
# v1.0.0 adds the Phase-0 ORDERING invariant to ULTRA mode (checks 8-10): §0
# PRE-GENERATION GROUND FORM must PRECEDE §1 ROLE, carry a non-thin via-negativa
# (>=3 CANNOT + >=3 TRAP/BREAKS + >=1 OBJECTION) + positive-ground (>=2 Evidence +
# first-principle + scope), and every recommendation must be claim-anchored
# ('grounded in:' or EXPERIMENT:). Checks 1-7 stay VERBATIM; 8-10 are additive.
#
# Exit 0 = PASS (the emitter may ship).  Exit 2 = BLOCK (do NOT emit; fix first).
# substrate mode is WARN-only (exit 0 always) — staleness nags, never walls.
# Every BLOCK prints the failing check + the matching sharp-edges.yaml id + fix.
#
# INVARIANT: the 7 ULTRA checks below are preserved VERBATIM from
# precompile-gate.sh v0.7.0 — Wave 1 EXTRACTS, it does not rewrite them.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

OUTCOMES="${AUTOVIBE_OUTCOMES_DIR:-$HOME/.kraken/outcomes}"
LEDGER="$OUTCOMES/decisions.jsonl"
GROUND_VERDICTS="$OUTCOMES/ground-verdicts.jsonl"
SKILL_DIR_DEFAULT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

fail=0 ; warns=0
block() { printf '🚫 BLOCK [%s]: %s\n   ↳ fix (sharp-edge %s): %s\n' "$1" "$2" "$3" "$4"; fail=1; }
warn()  { printf '⚠️  WARN [%s]: %s\n' "$1" "$2"; warns=$((warns+1)); }
ok()    { printf '✅ %s\n' "$1"; }

# W4 (LEARN GRAMMAR) — when a W3 grammar-profile exists, the gate enforces the PIN
# invariant via grammar-guide.sh (exit 2 = a pinned safety floor was marked for
# prune). No profile => frozen hand-authored grammar (W4 off, the safe default).
check_grammar_profile_pin() {
  local gg="$HOME/.kraken/outcomes/grammar-guide.sh"
  local prof="$HOME/.kraken/outcomes/grammar-profile.jsonl"
  [[ -x "$gg" && -s "$prof" ]] || return 0
  if "$gg" --json >/dev/null 2>&1; then
    ok "profile-guided generation available (W4; pinned GROUND/ambition/scanner floors held)"
  else
    block "pin-violated" "grammar-profile would down-weight a pinned safety floor (GROUND/ambition/scanner)" \
      "w4-pin-invariant" "pinned safety/quality floors are not learnable — never emit them for prune"
  fi
}

# ── COMPILE-REPORT writer (Wave 4, V5) — gate's exit artifact for BOTH backends ─
# Provenance: files read · ground verdict · charter grade · gate mode+result ·
# outcome_row_id (most-recent OPEN row — what `--outcome <slug>` would close).
write_report() {
  local mode="$1" result="$2" target="$3" charter="${4:-n/a}"
  local rdir rpath files ground rowid
  if [[ -d "$target" ]]; then rdir="$target"; else rdir="$(dirname "$target")"; fi
  rpath="${REPORT:-$rdir/COMPILE-REPORT.md}"
  if [[ -d "$target" ]]; then
    files="$(find "$target" -maxdepth 1 -type f -name '*.md' -printf '%f ' 2>/dev/null || true)"
  else
    files="$(basename "$target")"
  fi
  [[ -z "$files" ]] && files="(none)"
  ground="$(grep -hoiE '"verdict":"[a-z]+"|grounded|ungrounded' "$GROUND_VERDICTS" 2>/dev/null | tail -1 || true)"
  [[ -z "$ground" ]] && ground="n/a (no ground-verdicts.jsonl entry)"
  rowid="$(grep '"status":"pending"' "$LEDGER" 2>/dev/null | tail -1 \
            | grep -oE '"slug":"[^"]*"' | head -1 | cut -d'"' -f4 || true)"
  [[ -z "$rowid" ]] && rowid="none-open"
  cat > "$rpath" <<EOF
# COMPILE-REPORT — autovibe gate (v1.0.0)

generated:        $(date -Iseconds 2>/dev/null || date)
mode:             $mode
result:           $result
target:           $target
files read:       $files
ground verdict:   $ground
charter grade:    $charter
outcome_row_id:   $rowid   # close with: /autovibe --outcome $rowid good|bad

> Provenance record written by autovibe-gate.sh. refine mode reads this to
> re-emit targeted sections instead of recompiling the whole artifact.
EOF
  echo "📝 COMPILE-REPORT → $rpath"
}

# ── TRANSCEND machine-floor (Wave 3, V1 — strengthens INV3) ────────────────────
# Standalone mode AND invoked inside check_pack. Charter present, >=2 vectors,
# charter is not a generic clone. Sets `fail`; caller decides exit.
GENERIC_RE='modern|scalable|user-friendly|seamless|cutting-edge|robust|powerful|intuitive|world-class|next-gen|state-of-the-art|best-in-class'
check_transcend_file() {
  local T="$1"
  [[ -f "$T" ]] || { block "transcend-missing" "no such charter file: $T" \
        "transcend-generic-charter" "P1.5 TRANSCEND must emit a 00-TRANSCEND.md with a charter + vectors"; return; }
  if grep -qiE 'charter' "$T"; then ok "charter present ($(basename "$T"))"
  else block "charter-missing" "$(basename "$T"): no charter line" \
        "transcend-generic-charter" "name a one-sentence charter — the specific capability this system gives a user"; fi
  local vec
  vec=$(grep -ciE 'vector|^[[:space:]]*[-*][[:space:]]*V[0-9]' "$T" 2>/dev/null || true)
  if [[ "${vec:-0}" -ge 2 ]]; then ok "design vectors present ($vec)"
  else block "vectors" "$(basename "$T"): fewer than 2 design vectors ($vec)" \
        "transcend-generic-charter" "TRANSCEND emits >=2 design vectors that outrank conventions where they conflict"; fi
  local gw
  gw=$(grep -iE 'charter' "$T" 2>/dev/null | grep -oiE "$GENERIC_RE" | wc -l | tr -d ' ' || true)
  if [[ "${gw:-0}" -ge 2 ]]; then
    block "generic-charter" "$(basename "$T"): charter reads as a generic clone ($gw filler words)" \
      "transcend-generic-charter" \
      "charter names a SPECIFIC defensible capability a user cares about — not modern/scalable/seamless filler"
  else ok "charter is specific (not a generic clone)"; fi
}

# ── PACK gate (Wave 2, V1) — the floor ULTRA always had, now for pack mode ─────
check_pack() {
  local PACK="$1"
  [[ -d "$PACK" ]] || { echo "BLOCK: not a pack dir: $PACK" >&2; exit 2; }
  echo "── autovibe-gate pack ── $PACK"
  local catcq=()
  while IFS= read -r f; do catcq+=("$f"); done < <(
    find "$PACK" -maxdepth 1 -type f \( -name '0[2-9]-*.md' -o -name '1[0-9]-*.md' \) | sort)
  if [[ ${#catcq[@]} -eq 0 ]]; then
    block "no-catcq" "no CATCQ files (02-..19-*.md) in pack" \
      "pack-empty-catcq" "P3 CATCQ-FILL must emit numbered domain prompts; an empty pack ships nothing"
  fi
  local b
  for f in "${catcq[@]}"; do
    b="$(basename "$f")"
    grep -qiE '##[[:space:]]*VERIFY|^[[:space:]]*VERIFY|\*\*VERIFY' "$f" \
      || block "no-verify" "$b: no VERIFY block" \
           "pack-catcq-without-verify" "every CATCQ file ends with a ## VERIFY block — one concrete check the executor runs"
    grep -qiE 'QUALITY[[:space:] _-]*WRAP' "$f" \
      || block "no-qwrap" "$b: no QUALITY WRAP section" \
           "pack-catcq-without-qwrap" "P5 wraps every file with QUALITY WRAP (anti-pattern guards, not generic boilerplate)"
    if grep -qiE 'ACTION' "$f"; then
      if grep -iE 'ACTION' "$f" | grep -qiE '\b(handle|manage|process|deal with|support|work with|take care of|do the)\b'; then
        block "vague-action" "$b: ACTION uses a vague catch-all verb (handle/manage/process/...)" \
          "pack-vague-action-verb" "ACTION uses a concrete vocabulary.md verb (build/emit/validate/render/parse/route...), never a catch-all"
      fi
    fi
  done
  local RO="$PACK/RUN-ORDER.md"
  if [[ -f "$RO" ]]; then
    grep -qiE 'depend|dep:|after step|requires|→|->' "$RO" \
      || block "ro-deps" "RUN-ORDER.md has no explicit dependencies" \
           "pack-run-order-no-deps" "RUN-ORDER states explicit deps + marks parallelizable pairs"
  else
    block "no-run-order" "no RUN-ORDER.md" \
      "pack-no-run-order" "P4 assembles RUN-ORDER.md — the execution spine; a pack without it has no order"
  fi
  # Security discipline — auth/payment domain demands a scanner gate
  if grep -rqiE 'auth|login|password|oauth|[^a-z]token|session|payment|credit card|api[_ ]key|secret' "$PACK" 2>/dev/null; then
    if grep -rqiE 'scanner_scan|scanner gate|/cso|security gate' "$PACK" 2>/dev/null; then
      ok "security-adjacent: scanner gate present"
    else
      block "no-scanner" "security-adjacent pack (auth/payment/secrets) with no scanner gate" \
        "pack-security-without-scanner" "add a scanner_scan gate row to RUN-ORDER before ship — security-adjacent without a gate is a critical miss"
    fi
  fi
  # TRANSCEND floor if a charter was emitted
  local T="$PACK/00-TRANSCEND.md"
  [[ -f "$T" ]] && check_transcend_file "$T"

  # BUILD RECEIPT contract (W1 — WARN, the return edge). Some file must carry the
  # ## BUILD RECEIPT block calling receipt-ingest.sh, or the pack ships write-only.
  if grep -rqiE 'BUILD RECEIPT|receipt-ingest' "$PACK" 2>/dev/null; then
    ok "build-receipt contract present (return edge wired)"
  else
    warn "no-receipt" "no ## BUILD RECEIPT block — pack ships with the loop's return edge cut (W1: becomes a blocker once emission is reliable)"
  fi

  # SIMULATE contract (W2 — WARN, the pre-ship dry run). Some file must carry the
  # ## SIMULATE / --kind sim block, or the pack ships with no calibratable prediction.
  if grep -rqiE 'SIMULATE|--kind sim|kind:"?sim' "$PACK" 2>/dev/null; then
    ok "simulate contract present (pre-ship dry run wired)"
  else
    warn "no-simulate" "no ## SIMULATE / --kind sim block — pack ships with no predicted receipt to calibrate (W2: becomes a blocker once calibration is trusted)"
  fi
  check_grammar_profile_pin

  echo "────────────────────────────────────────"
  if [[ "$fail" -eq 0 ]]; then
    ok "PACK PASS — pack may ship."
    write_report "pack" "PASS" "$PACK" "$([[ -f "$T" ]] && echo "checked" || echo "n/a (no transcend)")"
    exit 0
  else
    echo "🚫 PACK BLOCK — fix the above BEFORE reporting SHIP. ship aborted."
    write_report "pack" "BLOCK" "$PACK" "$([[ -f "$T" ]] && echo "checked" || echo "n/a")"
    exit 2
  fi
}

# ── ULTRA gate (checks 1-7 v0.7.0 VERBATIM · checks 8-10 v1.0 Phase-0 ordering) ─
check_ultra() {
  local ULTRA="" ; REPORT="${REPORT:-}"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --ultra)  ULTRA="${2:-}"; shift 2;;
      --report) REPORT="${2:-}"; shift 2;;
      *) echo "ultra: unknown arg: $1" >&2; exit 64;;
    esac
  done
  [[ -z "$ULTRA" ]] && { echo "BLOCK: --ultra <path> required" >&2; exit 64; }
  [[ -f "$ULTRA" ]] || { echo "BLOCK: no such file: $ULTRA" >&2; exit 2; }
  echo "── autovibe-gate ultra ── $ULTRA"

  # Check 1 — core grammar sections present (§1–§10 floor of 10; §0 enforced by check 8)
  local sections; sections=$(grep -cE '^##[[:space:]]+§?[0-9]+' "$ULTRA" || true)
  if [[ "$sections" -ge 10 ]]; then ok "grammar sections present ($sections; §0–§10)"
  else block "sections" "only $sections grammar sections (need the full §0–§10)" \
        "ultra_all_sections_present" "emit the full §0–§10 grammar; none empty"; fi

  # Check 2 — ambition floor WITH below-floor examples
  if grep -qE 'FLOOR' "$ULTRA" \
     && grep -qiE 'below[- ]floor|under a day|config flag|helper|rename|yaml key|adding .* prose' "$ULTRA"; then
    ok "ambition floor stated with below-floor examples"
  else block "floor" "§5 floor missing or generic (no system-specific below-floor examples)" \
        "ultra-ambition-floor-missing-or-generic" \
        "FLOOR = executable-in-<1-day test + >=2 below-floor examples naming this system + 'discard, restart at Stage A'"; fi

  # Check 3 — thinking protocol names >=5 visible stage artifacts
  local arts; arts=$(grep -c 'Artifact:' "$ULTRA" || true)
  if [[ "$arts" -ge 5 ]]; then ok "thinking-protocol artifacts ($arts)"
  else block "artifacts" "§6 names only $arts/5 stage artifacts" \
        "ultra-thinking-protocol-without-artifacts" \
        "each stage A-E names its artifact; 'a stage without its artifact = skipped = invalid'"; fi

  # Check 4 — output contract forces waves + delete list + risk map + verify
  local miss=""
  grep -qiE 'wave'        "$ULTRA" || miss+="waves "
  grep -qiE 'delete list' "$ULTRA" || miss+="delete-list "
  grep -qiE 'risk'        "$ULTRA" || miss+="risk-map "
  grep -qiE 'verify'      "$ULTRA" || miss+="verify "
  if [[ -z "$miss" ]]; then ok "output contract forces waves+delete+risk+verify"
  else block "contract" "§7 missing: $miss" \
        "ultra_output_contract_forces_waves" \
        "demand architecture+delta, 3-7 shippable waves, delete list, risk map, per-wave verify"; fi

  # Check 5 — crux grounded: >=3 cracks carry an Evidence line
  local ev; ev=$(grep -c 'Evidence:' "$ULTRA" || true)
  if [[ "$ev" -ge 3 ]]; then ok "RECON baseline: $ev evidence-backed cracks"
  else block "recon-thin" "only $ev/3 cracks carry an Evidence: line — RECON thin" \
        "ultra-system-recon-skipped" \
        "SYSTEM-RECON reads the actual system; every crack carries a file/metric/incident as evidence"; fi

  # Check 6 — >=3 named INVARIANTS
  local inv; inv=$(grep -ciE 'invariant' "$ULTRA" || true)
  if [[ "$inv" -ge 3 ]]; then ok "INVARIANTS named ($inv references)"
  else block "invariants" "fewer than 3 INVARIANT references ($inv)" \
        "ultra-system-recon-skipped" \
        "name >=3 strengths-as-INVARIANTS the transformation must not lose"; fi

  # Check 7 — version delta declared
  if grep -qiE 'v[0-9][^[:space:]]*[[:space:]]*(→|->|to)[[:space:]]*v?[0-9]|v_current.*v_next' "$ULTRA"; then
    ok "version delta declared (v_current → v_next)"
  else block "delta" "no v_current → v_next capability delta" \
        "ultra-ambition-floor-missing-or-generic" \
        "§5 CEILING must name v_current → v_next and state the capability delta in user terms"; fi

  # ── checks 8-10 (v1.0 — Phase 0 ordering invariant; checks 1-7 above are VERBATIM) ──
  # The novel unit of v1.0: not a keyword count but an ORDERING invariant — §0 must precede
  # §1, so the constraint map is attended-to before any positive-direction section is read.

  # Check 8 — §0 present, BEFORE §1 ROLE, with a non-thin via-negativa form
  local p0 s1
  p0=$(grep -niE 'PRE-GENERATION GROUND|VIA-NEGATIVA' "$ULTRA" | head -1 | cut -d: -f1 || true)
  s1=$(grep -niE '^##[[:space:]]+§?1[[:space:]]|ROLE & STAKES' "$ULTRA" | head -1 | cut -d: -f1 || true)
  if [[ -z "$p0" ]]; then
    block "phase0" "no §0 PRE-GENERATION GROUND FORM (Phase 0 missing)" \
      "ultra-phase0-missing-or-thin" \
      "emit §0 with a VIA-NEGATIVA form (>=3 CANNOT + >=3 TRAP/BREAKS + >=1 OBJECTION) + a POSITIVE-GROUND form, BEFORE §1"
  elif [[ -z "$s1" || "$p0" -ge "$s1" ]]; then
    block "phase0-order" "§0 present but not before §1 ROLE (ordering invariant violated)" \
      "ultra-phase0-after-positive-sections" \
      "§0 must precede §1 — grounding before any positive-direction section is the v1.0 anti-anchoring mechanism"
  else
    local block0 cannots traps obj p_ev p_fp p_scope
    block0="$(sed -n "${p0},$((s1-1))p" "$ULTRA")"
    cannots=$(printf '%s\n' "$block0" | grep -ciE 'CANNOT'    || true)
    traps=$(printf '%s\n'   "$block0" | grep -ciE 'TRAP|BREAKS' || true)
    obj=$(printf '%s\n'     "$block0" | grep -ciE 'OBJECTION'  || true)
    if [[ "${cannots:-0}" -ge 3 && "${traps:-0}" -ge 3 && "${obj:-0}" -ge 1 ]]; then
      ok "Phase 0 present, before §1, via-negativa complete ($cannots CANNOT / $traps TRAP-BREAKS / $obj OBJECTION)"
    else
      block "phase0-thin" "§0 via-negativa thin ($cannots CANNOT, $traps TRAP/BREAKS, $obj OBJECTION; need >=3/>=3/>=1)" \
        "ultra-phase0-missing-or-thin" \
        "VIA-NEGATIVA needs >=3 CANNOT boundary lines + >=3 TRAP/BREAKS lines + >=1 adversarial OBJECTION"
    fi
    # Check 9 — §0 POSITIVE-GROUND carries its OWN evidence (scoped to the §0 block)
    p_ev=$(printf '%s\n'    "$block0" | grep -ciE 'Evidence:'       || true)
    p_fp=$(printf '%s\n'    "$block0" | grep -ciE 'first principle' || true)
    p_scope=$(printf '%s\n' "$block0" | grep -ciE 'scope'           || true)
    if [[ "${p_ev:-0}" -ge 2 && "${p_fp:-0}" -ge 1 && "${p_scope:-0}" -ge 1 ]]; then
      ok "Phase 0 positive-ground grounded ($p_ev Evidence / first-principle / scope)"
    else
      block "phase0-ground" "§0 positive-ground thin ($p_ev Evidence, fp=$p_fp, scope=$p_scope; need >=2/>=1/>=1)" \
        "ultra-phase0-missing-or-thin" \
        "POSITIVE-GROUND needs >=2 Evidence: items + >=1 'First principle' + a 'Scope:' line"
    fi
  fi

  # Check 10 — claim-level grounding: recommendations cite a source OR are framed as experiments
  local gi exp
  gi=$(grep -ciE 'grounded in:' "$ULTRA"  || true)
  exp=$(grep -ciE 'EXPERIMENT:'  "$ULTRA" || true)
  if [[ "$(( ${gi:-0} + ${exp:-0} ))" -ge 1 ]]; then
    ok "claim-level grounding present (grounded-in: $gi · EXPERIMENT: $exp)"
  else
    block "unanchored" "no recommendation carries a 'grounded in:' citation or an EXPERIMENT: framing" \
      "ultra-recommendation-unanchored" \
      "every recommendation cites >=1 §0/§2 evidence item as 'grounded in: ...', or converts to 'EXPERIMENT: [hyp] | TEST: [check] | SIGNAL: [observable]'"
  fi

  # Check 11 (W1 — WARN, additive; checks 1-7 stay VERBATIM, 8-10 unchanged) — BUILD RECEIPT return edge
  if grep -qiE 'BUILD RECEIPT|receipt-ingest' "$ULTRA"; then
    ok "build-receipt contract present (return edge wired)"
  else
    warn "no-receipt" "no ## BUILD RECEIPT block — ULTRA ships with the loop's return edge cut (W1: becomes a blocker once emission is reliable)"
  fi

  # Check 12 (W2 — WARN, additive) — SIMULATE pre-ship dry run
  if grep -qiE 'SIMULATE|--kind sim|kind:"?sim' "$ULTRA"; then
    ok "simulate contract present (pre-ship dry run wired)"
  else
    warn "no-simulate" "no ## SIMULATE / --kind sim block — ULTRA ships with no predicted receipt to calibrate (W2: becomes a blocker once calibration is trusted)"
  fi
  check_grammar_profile_pin

  echo "────────────────────────────────────────"
  if [[ "$fail" -eq 0 ]]; then
    echo "✅ PRECOMPILE PASS — ULTRA-PROMPT.md may ship."
    # Wave 4: the gate WRITES provenance (v0.7 expected the model to pre-write it).
    write_report "ultra" "PASS" "$ULTRA" "checked-by-ultra-rubric"
    exit 0
  else
    echo "🚫 PRECOMPILE BLOCK — fix the above BEFORE emitting. compile aborted."
    write_report "ultra" "BLOCK" "$ULTRA" "n/a"
    exit 2
  fi
}

# ── TOURNAMENT gate (v2.0) — a tournament is real only if it clears this floor ──
# Verifies: >=K diverse candidates · adversarial verdicts on the REALITY axes ·
# a winner with a discriminating delta · a closed rubric-feedback loop · and the
# winner itself clears the v1.0 ultra floor (check_ultra in a subshell). The gate
# IS the architecture: --tournament without these artifacts is single-pass in a costume.
TOURNEY_MIN_CANDIDATES="${AUTOVIBE_TOURNEY_MIN_CANDIDATES:-3}"
TOURNEY_MIN_VERDICTS="${AUTOVIBE_TOURNEY_MIN_VERDICTS:-3}"
TOURNEY_MIN_DELTA="${AUTOVIBE_TOURNEY_MIN_DELTA:-3}"
WEIGHTS="$OUTCOMES/autovibe-rubric-weights.json"
check_tournament() {
  local DIR="$1"
  [[ -d "$DIR" ]] || { echo "BLOCK: not a tournament dir: $DIR" >&2; exit 2; }
  echo "── autovibe-gate tournament ── $DIR"
  local slug; slug="$(basename "$DIR")"

  # 1 — >=K candidate files
  local cands=() ; while IFS= read -r f; do cands+=("$f"); done < <(
    find "$DIR" -maxdepth 1 -type f -name 'candidate-*.md' | sort)
  if [[ ${#cands[@]} -ge "$TOURNEY_MIN_CANDIDATES" ]]; then
    ok "candidates present (${#cands[@]} >= $TOURNEY_MIN_CANDIDATES)"
  else
    block "tournament-too-few" "only ${#cands[@]} candidate-*.md (need >=$TOURNEY_MIN_CANDIDATES)" \
      "tournament-candidates-collapse" "T1 emits >=$TOURNEY_MIN_CANDIDATES candidates, one per lens"
  fi

  # 2 — distinct lenses (no candidate collapse): unique Lens: labels across candidates,
  #     or a LENS-CAST line in TOURNAMENT.md naming >=K lenses.
  local T="$DIR/TOURNAMENT.md" lenses
  lenses=$(grep -hoiE 'Lens:[[:space:]]*[A-Za-z0-9_-]+' "${cands[@]}" 2>/dev/null \
            | sort -u | wc -l | tr -d ' ' || echo 0)
  if [[ "${lenses:-0}" -lt "$TOURNEY_MIN_CANDIDATES" && -f "$T" ]]; then
    lenses=$(grep -iE 'LENS-CAST' "$T" 2>/dev/null | head -1 | grep -oE ',' | wc -l | tr -d ' ' || echo 0)
    lenses=$(( lenses + 1 ))   # N commas => N+1 items
  fi
  if [[ "${lenses:-0}" -ge "$TOURNEY_MIN_CANDIDATES" ]]; then
    ok "lenses are distinct ($lenses >= $TOURNEY_MIN_CANDIDATES)"
  else
    block "tournament-collapse" "fewer than $TOURNEY_MIN_CANDIDATES distinct lenses ($lenses) — candidates collapsed" \
      "tournament-candidates-collapse" "each candidate carries a distinct 'Lens:' label; lenses differ in KIND not wording"
  fi

  # 3 — TOURNAMENT.md present
  if [[ -f "$T" ]]; then ok "TOURNAMENT.md present"
  else block "tournament-no-record" "no TOURNAMENT.md (judge verdicts + winner record missing)" \
        "judge-grades-selfscore" "T2/T3 write TOURNAMENT.md: lens cast, every judge verdict, winner+delta, rubric-update"; fi

  if [[ -f "$T" ]]; then
    # 4 — adversarial verdicts cite the REALITY axes, not the self-score rubric
    local verdicts axes_ok=1 ax
    verdicts=$(grep -ciE 'judge[[:space:]]*=' "$T" 2>/dev/null || echo 0)
    for ax in 'ship' 'scan' 'wave' 'ground'; do
      grep -qiE "$ax" "$T" || { axes_ok=0; }
    done
    if [[ "${verdicts:-0}" -ge "$TOURNEY_MIN_VERDICTS" && "$axes_ok" -eq 1 ]]; then
      ok "adversarial verdicts on reality axes ($verdicts verdicts; ship/scan/wave/ground cited)"
    else
      block "judge-thin" "verdicts=$verdicts (need >=$TOURNEY_MIN_VERDICTS) or reality axes not cited (ship/scan/wave/ground)" \
        "judge-grades-selfscore" "J judges score each candidate on SHIP-PASS/SCANNER-PASS/WAVE-REAL/GROUND-REAL, refute-default if unsure"
    fi

    # 5 — winner named with a DISCRIMINATING delta
    local delta
    # extract the number that FOLLOWS the delta token (not the first number on the WINNER line,
    # which may be median=NN). Canonical form: delta-over-runner-up=NN; fallback delta=NN / delta: NN.
    delta=$(grep -hoiE 'delta[- ]?over[- ]?runner[- ]?up[=:]?[[:space:]]*[0-9]+|delta[=:][[:space:]]*[0-9]+' "$T" 2>/dev/null \
             | grep -oE '[0-9]+' | head -1 || echo 0)
    [[ -z "$delta" ]] && delta=0
    if grep -qiE 'WINNER:' "$T" && [[ "${delta:-0}" -ge "$TOURNEY_MIN_DELTA" ]]; then
      ok "winner discriminated (delta=$delta >= $TOURNEY_MIN_DELTA)"
    else
      block "winner-no-delta" "no WINNER line or delta=$delta < $TOURNEY_MIN_DELTA — tournament didn't discriminate" \
        "winner-no-delta" "recast lenses (too similar) or sharpen refute prompts (judging too coarse); winner needs delta>=$TOURNEY_MIN_DELTA"
    fi
  fi

  # 6 — rubric-feedback loop closed THIS run (slug appears in the weights file)
  if [[ -f "$WEIGHTS" ]] && grep -q "\"$slug\"" "$WEIGHTS" 2>/dev/null; then
    ok "rubric-feedback loop closed (slug in autovibe-rubric-weights.json)"
  else
    block "rubric-feedback-skipped" "no row for '$slug' in $WEIGHTS — reality loop did not close" \
      "rubric-feedback-skipped" "T4 appends {slug,winner_lens,dominated_axes,delta,...} so the next compile's rubric is reality-tuned"
  fi

  # 7 — the winner itself clears the v1.0 ultra floor (subshell: its exit doesn't end us)
  local WINNER="$DIR/ULTRA-PROMPT.md"
  if [[ -f "$WINNER" ]]; then
    if ( check_ultra --ultra "$WINNER" >/dev/null 2>&1 ); then
      ok "winner clears the v1.0 ULTRA floor (check_ultra PASS)"
    else
      block "winner-below-floor" "winner ULTRA-PROMPT.md fails the v1.0 ultra gate" \
        "winner-no-delta" "a tournament winner is never below a single-pass ship; run: autovibe-gate.sh ultra --ultra $WINNER"
    fi
  else
    block "no-winner-file" "no ULTRA-PROMPT.md (the winner must ship as a §0–§10 ULTRA prompt)" \
      "winner-no-delta" "T3 writes the winner (or synthesized winner) to ULTRA-PROMPT.md"
  fi

  echo "────────────────────────────────────────"
  if [[ "$fail" -eq 0 ]]; then
    ok "TOURNAMENT PASS — winner survived $TOURNEY_MIN_VERDICTS+ adversarial judges; may ship."
    write_report "tournament" "PASS" "$DIR" "tournament-winner"
    exit 0
  else
    echo "🚫 TOURNAMENT BLOCK — fix the above BEFORE reporting SHIP. ship aborted."
    write_report "tournament" "BLOCK" "$DIR" "n/a"
    exit 2
  fi
}

# ── SUBSTRATE freshness (Wave 6, V3) — WARN-only, never walls ──────────────────
check_substrate() {
  local SKILL_DIR="${1:-$SKILL_DIR_DEFAULT}"
  echo "── autovibe-gate substrate ── $SKILL_DIR"
  local skv; skv=$(grep -oE 'version:[[:space:]]*"[0-9.]+"' "$SKILL_DIR/skill.yaml" 2>/dev/null \
                    | head -1 | grep -oE '[0-9]+\.[0-9]+' | head -1 || true)
  [[ -z "$skv" ]] && { warn "substrate" "cannot read skill.yaml version"; echo "(skipped)"; return; }
  local sk_major sk_minor; sk_major="${skv%%.*}"; sk_minor="${skv##*.}"
  ok "skill version: $skv"
  local f ga ga_major ga_minor
  for f in collaboration.yaml integrations.md kraken-os-bridge.md validations.yaml; do
    [[ -f "$SKILL_DIR/$f" ]] || { warn "substrate" "$f: missing"; continue; }
    ga=$(grep -oE 'generated_against:[[:space:]]*"?[0-9]+\.[0-9]+' "$SKILL_DIR/$f" 2>/dev/null \
          | head -1 | grep -oE '[0-9]+\.[0-9]+' | head -1 || true)
    if [[ -z "$ga" ]]; then warn "substrate" "$f: no generated_against stamp (run a sync)"; continue; fi
    ga_major="${ga%%.*}"; ga_minor="${ga##*.}"
    if [[ "$ga_major" -lt "$sk_major" ]] || { [[ "$ga_major" -eq "$sk_major" ]] && [[ $((sk_minor - ga_minor)) -ge 1 ]]; }; then
      warn "substrate" "$f generated_against $ga but skill is $skv — substrate is stale (regenerate)"
    else
      ok "$f current ($ga)"
    fi
  done
  echo "────────────────────────────────────────"
  echo "ℹ️  substrate check is WARN-only ($warns warning(s)) — never blocks a build."
  exit 0
}

# ── GROUND presence (lightweight) ──────────────────────────────────────────────
check_ground() {
  echo "── autovibe-gate ground ──"
  if [[ -f "$GROUND_VERDICTS" ]] && grep -qiE 'grounded' "$GROUND_VERDICTS" 2>/dev/null; then
    ok "ground-verdicts.jsonl has a grounded verdict"; exit 0
  else
    warn "ground" "no grounded verdict in $GROUND_VERDICTS — PASS 0.0 may not have run"; exit 0
  fi
}

# ── ULTRA-PACK gate (v2.1) — the reasoning-machine floor ──────────────────────
# REASON.md is real only if it makes the LLM DERIVE the plan (not assert it) and
# then EMIT the lifecycle prompts. Validates the derivation-aimed §-grammar + the
# reason-THEN-emit §7 contract + recon provenance. Takes a pack dir holding REASON.md.
check_ultra_pack() {
  local DIR="${1:?ultra-pack dir required}"
  [[ -d "$DIR" ]] || { echo "BLOCK: not an ultra-pack dir: $DIR" >&2; exit 2; }
  local R="$DIR/REASON.md"
  [[ -f "$R" ]] || { echo "BLOCK: no REASON.md in $DIR" >&2; exit 2; }
  echo "── autovibe-gate ultra-pack ── $R"

  # 1 — full §0–§10 grammar present
  local sections; sections=$(grep -cE '^##[[:space:]]+§?[0-9]+' "$R" || true)
  if [[ "$sections" -ge 10 ]]; then ok "grammar sections present ($sections; §0–§10)"
  else block "sections" "only $sections grammar sections (need §0–§10)" \
        "up_all_sections_present" "emit the full §0–§10 derivation grammar; none empty"; fi

  # 2 — §0 GROUND FORM precedes §1 ROLE (anti-anchoring ordering invariant)
  local l0 l1; l0=$( { grep -nE '^##[[:space:]]+§?0\b' "$R" || true; } | head -1 | cut -d: -f1)
  l1=$( { grep -nE '^##[[:space:]]+§?1\b' "$R" || true; } | head -1 | cut -d: -f1)
  if [[ -n "$l0" && -n "$l1" && "$l0" -lt "$l1" ]]; then ok "§0 ground form precedes §1 role (anti-anchoring)"
  else block "phase0-order" "§0 missing or positioned after §1 (l0=$l0 l1=$l1)" \
        "up_phase0_precedes_role" "§0 GROUND FORM must be the first section, before §1 ROLE"; fi

  # 3 — greenfield ambition floor: rejects the obvious build + >=2 below-floor examples
  if grep -qE 'FLOOR' "$R" \
     && grep -qiE 'obvious build|standard CRUD|textbook stack|first architecture|below[- ]floor' "$R"; then
    ok "greenfield ambition floor rejects the obvious build"
  else block "floor" "§5 floor missing or generic (no 'obvious build' rejection + examples)" \
        "up_floor_greenfield" "FLOOR = reject the obvious build + >=2 below-floor examples + 'restart at Stage A'"; fi

  # 4 — §6 Stage E forced selection with written proof (the genius-tier mechanism)
  if grep -qiE 'Stage E' "$R" && grep -qiE 'highest.*tier|written proof|anchoring bias' "$R"; then
    ok "§6 Stage E forced-selection present (highest viable tier + proof)"
  else block "stage-E" "§6 Stage E forced selection missing or lacks the proof requirement" \
        "up_stage_E_forced" "Stage E selects highest viable tier; choosing below T3 requires WRITTEN PROOF it breaks a constraint"; fi

  # 5 — §6 names >=5 visible stage artifacts (A–E unskippable)
  local arts; arts=$(grep -c 'Artifact:' "$R" || true)
  if [[ "$arts" -ge 5 ]]; then ok "thinking-protocol artifacts ($arts; Stages A–E)"
  else block "artifacts" "§6 names only $arts/5 stage artifacts" \
        "up_stage_E_forced" "each Stage A–E names its visible artifact; a stage without one = skipped"; fi

  # 6 — §7 reason-THEN-emit contract: derived plan AND emitted lifecycle prompts AND run-order
  local miss=""
  grep -qiE 'derived plan|THE DERIVED PLAN'      "$R" || miss+="derived-plan "
  grep -qiE 'execution prompts|lifecycle.*prompt|emit' "$R" || miss+="emitted-prompts "
  grep -qiE 'run.?order'                          "$R" || miss+="run-order "
  if [[ -z "$miss" ]]; then ok "§7 reason-THEN-emit contract complete (plan + emitted prompts + run-order)"
  else block "reason-emit" "§7 missing: $miss" \
        "up_reason_then_emit" "§7 must demand (a) derived plan, (b) emitted lifecycle prompts FROM it, (c) run-order"; fi

  # 7 — lifecycle complete: research/setup/build/deploy/verify all named in §7
  local lmiss=""
  for stage in research setup build deploy verify; do
    grep -qiE "$stage" "$R" || lmiss+="$stage "
  done
  if [[ -z "$lmiss" ]]; then ok "lifecycle complete (research·setup·build·deploy·verify)"
  else block "lifecycle" "§7 missing lifecycle stages: $lmiss" \
        "up_lifecycle_complete" "§7 (b) must emit a prompt for each of research/setup/build/deploy/verify"; fi

  # 8 — RECON provenance: COMPILE-REPORT.md lists sources/priors read
  local CR="$DIR/COMPILE-REPORT.md"
  if [[ -f "$CR" ]] && grep -qiE 'source|prior|recon|read|http|mind_retrieve|file' "$CR"; then
    ok "RECON provenance listed in COMPILE-REPORT.md"
  else block "provenance" "COMPILE-REPORT.md absent or lists no prior-art/system sources read" \
        "up_recon_provenance" "list the prior-art sources (or SYSTEM-RECON files) + mind_retrieve priors read"; fi

  # 9 — §9 self-score gate includes the 'plan derived not asserted' line
  if grep -qiE 'derived.*not.*assert|assert.*not.*derived|DERIVED.*Stage E|plan.*DERIVED' "$R"; then
    ok "§9 self-score gate checks plan-derived-not-asserted"
  else block "self-score" "§9 missing the 'plan derived not asserted' check" \
        "up_self_score_derived" "§9 must include: 'is the plan DERIVED (Stage E proof) not merely asserted? any no → Stage A'"; fi

  # 10 — doc budget (warn)
  local words; words=$(wc -w < "$R")
  if [[ "$words" -le 4500 ]]; then ok "REASON.md within budget (~$words words ≈ ≤6k tok)"
  else warn "budget" "REASON.md ~$words words may exceed ~6k tokens — trim §5 examples / §2 capsule"; fi

  echo "────────────────────────────────────────"
  if [[ "$fail" -eq 0 ]]; then
    echo "✅ ULTRA-PACK PASS — REASON.md may ship."
    write_report "ultra-pack" "PASS" "$R" "checked-by-ultra-pack-rubric"
    exit 0
  else
    echo "🚫 ULTRA-PACK BLOCK — fix the above BEFORE shipping. compile aborted."
    write_report "ultra-pack" "BLOCK" "$R" "n/a"
    exit 2
  fi
}

# ── DISPATCH ───────────────────────────────────────────────────────────────────
MODE="${1:-}"; shift || true
REPORT="${REPORT:-}"
# pull a --report out of the remaining args for pack mode
ARGS=(); while [[ $# -gt 0 ]]; do
  case "$1" in --report) REPORT="${2:-}"; shift 2;; *) ARGS+=("$1"); shift;; esac
done
set -- "${ARGS[@]:-}"

case "$MODE" in
  ultra)      check_ultra "$@";;
  ultra-pack) check_ultra_pack "${1:?ultra-pack dir required}";;
  tournament) check_tournament "${1:?tournament dir required}";;
  pack)      check_pack "${1:?pack dir required}";;
  transcend) check_transcend_file "${1:?transcend file required}"
             echo "────────────────────────────────────────"
             [[ "$fail" -eq 0 ]] && { ok "TRANSCEND PASS"; exit 0; } || { echo "🚫 TRANSCEND BLOCK"; exit 2; };;
  substrate) check_substrate "${1:-}";;
  ground)    check_ground;;
  -h|--help|"") grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0;;
  *) echo "unknown mode: $MODE (use ultra|ultra-pack|tournament|pack|transcend|substrate|ground)" >&2; exit 64;;
esac
