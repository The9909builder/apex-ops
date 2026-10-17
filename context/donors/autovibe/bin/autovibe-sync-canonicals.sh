#!/usr/bin/env bash
# autovibe — autovibe-sync-canonicals.sh  (v0.8.0 Wave 7, V4 — VERIFIED DISCOVERY)
# ─────────────────────────────────────────────────────────────────────────────
# Regenerate collaboration.yaml's canonical truth FROM DISK.
#
# v0.4.1 marked the whole canonical map `aspirational` (4/114 verified, hand-curated,
# silently drifting). This script makes the map a CACHE OF DISK TRUTH:
#   1. parse every `canonical:` skill name out of collaboration.yaml
#   2. check each against ~/.spawner/skills/ on disk (a dir named exactly that)
#   3. write a verified-map sidecar: name  verified  path  checked_at
#   4. update ONLY the 3 unique header lines (status, verified list, generated_against)
#      — never touches the curated 38K body (risk mitigation: additive, no mass-rewrite)
#
# WARN-ONLY by default (V4 phasing): prints the unverified list, does not delete entries.
# P3 skill-load reads the sidecar to WARN before injecting an unverified canonical.
#
# Usage:  autovibe-sync-canonicals.sh [--skill-dir <dir>] [--skills-root <dir>]
# Pure bash + find + sed + awk. No python, no node (INVARIANT 2).
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_ROOT="${HOME}/.spawner/skills"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --skill-dir)   SKILL_DIR="$2"; shift 2;;
    --skills-root) SKILLS_ROOT="$2"; shift 2;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0;;
    *) echo "unknown arg: $1" >&2; exit 64;;
  esac
done

COLLAB="$SKILL_DIR/collaboration.yaml"
MAP="$SKILL_DIR/collaboration.verified.tsv"
[[ -f "$COLLAB" ]] || { echo "no collaboration.yaml at $COLLAB" >&2; exit 1; }
[[ -d "$SKILLS_ROOT" ]] || { echo "no skills root at $SKILLS_ROOT" >&2; exit 1; }

SKV="$(grep -oE 'version:[[:space:]]*"[0-9.]+"' "$SKILL_DIR/skill.yaml" 2>/dev/null \
        | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "0.0.0")"
NOW="$(date -Iseconds 2>/dev/null || date)"

# 1. Extract canonical names (indented YAML list under a `canonical:` key).
mapfile -t NAMES < <(awk '
  /^[[:space:]]*canonical:[[:space:]]*$/ { inc=1; next }
  inc==1 {
    if ($0 ~ /^[[:space:]]*-[[:space:]]+[A-Za-z0-9._-]+[[:space:]]*$/) {
      gsub(/^[[:space:]]*-[[:space:]]+/,""); gsub(/[[:space:]]+$/,""); print; next
    } else { inc=0 }
  }' "$COLLAB" | sort -u)

total=${#NAMES[@]}
[[ "$total" -eq 0 ]] && { echo "no canonical: entries found" >&2; exit 1; }

# 2. Check each against disk → 3. write the verified map.
printf '# name\tverified\tpath\tchecked_at\t(skill %s)\n' "$SKV" > "$MAP"
verified=0 ; verified_names=()
for n in "${NAMES[@]}"; do
  path="$(find "$SKILLS_ROOT" -maxdepth 4 -type d -name "$n" -print -quit 2>/dev/null || true)"
  if [[ -n "$path" ]]; then
    printf '%s\ttrue\t%s\t%s\n' "$n" "${path#"$HOME"/}" "$NOW" >> "$MAP"
    verified=$((verified+1)); verified_names+=("$n")
  else
    printf '%s\tfalse\t-\t%s\n' "$n" "$NOW" >> "$MAP"
  fi
done

# 4. Update ONLY the 3 unique header lines in collaboration.yaml (targeted, safe).
# 4a. canonical_field_status: aspirational -> disk-verified (<v>/<t>)
sed -i -E "s|^canonical_field_status:.*|canonical_field_status: \"disk-verified\"  # ${verified}/${total} verified on disk by autovibe-sync-canonicals.sh @ ${NOW}|" "$COLLAB"
# 4b. verified_canonicals_on_disk: [...] -> the real list (truncated display, full truth in the .tsv map)
VLIST="$(printf '"%s", ' "${verified_names[@]}" | sed 's/, $//')"
sed -i -E "s|^verified_canonicals_on_disk:.*|verified_canonicals_on_disk: [${VLIST}]   # source of truth: collaboration.verified.tsv|" "$COLLAB"
# 4c. generated_against -> current skill version (content now reflects a disk-verified pass)
SKV_MM="$(printf '%s' "$SKV" | grep -oE '^[0-9]+\.[0-9]+')"
sed -i -E "s|^generated_against:.*|generated_against: \"${SKV_MM}\"   # v0.8.0 Wave 7: canonical map regenerated from disk @ ${NOW}|" "$COLLAB"

echo "── autovibe-sync-canonicals ── skill $SKV"
echo "✅ canonicals verified from disk: ${verified}/${total}"
echo "📝 verified map → ${MAP#"$HOME"/}"
echo "📝 collaboration.yaml header updated (status + verified list + generated_against → ${SKV_MM})"
if [[ "$verified" -lt "$total" ]]; then
  echo "⚠️  $((total - verified)) canonical(s) NOT on disk (HINTS only — P3 must WARN before injecting):"
  awk -F'\t' '$2=="false"{print "     - "$1}' "$MAP" | head -20
  rest=$(( $(awk -F'\t' '$2=="false"' "$MAP" | wc -l) - 20 ))
  [[ "$rest" -gt 0 ]] && echo "     … and $rest more (see $MAP)"
fi
exit 0
