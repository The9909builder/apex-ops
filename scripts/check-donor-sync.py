#!/usr/bin/env python3
"""
Donor-sync checker for APEX.

Cross-references the routing table in context/knowledge/donor-routing.md
against installed SKILL.md files.

Skills-root resolution order:
  1. --skills-dir CLI flag
  2. APEX_SKILLS_DIR env var
  3. Sibling resolution: the tree apex itself is installed in
     (<skills-root>/<category>/apex -> <skills-root>)
  4. Legacy fallback: ~/.claude/skills

Donor names are derived from the routing table itself, so a donor added to
the table is always checked. Gate keywords are a separate map; a table donor
with no keyword entry prints an UNVERIFIED-GATE warning instead of being
silently skipped.

Exit 0 if all donors present and gates verified. Exit 1 otherwise.

Usage:
    python3 check-donor-sync.py [--skills-dir /path/to/skills]
"""

import os
import re
import sys
from pathlib import Path

from gate_registry import load_gates

ROUTING_FILE = Path(__file__).resolve().parent.parent / "context" / "knowledge" / "donor-routing.md"

# Gate keywords that must appear in each donor's SKILL.md (lowercased match).
# Single source: context/knowledge/gates.json via scripts/gate_registry.py (W1/B1.2).
# Insertion order = catalog order; values are all read-only views of the manifest.
gates = load_gates()
gate_keywords = {name: e["keywords"] for name, e in gates.items()}


def resolve_skills_root(explicit: str | None) -> Path:
    """Resolve the skills root from flag, env, sibling tree, or legacy default."""
    if explicit:
        return Path(explicit).resolve()
    env = os.environ.get("APEX_SKILLS_DIR")
    if env:
        return Path(env).resolve()
    # <skills-root>/<category>/apex/scripts/check-donor-sync.py
    apex_dir = Path(__file__).resolve().parent.parent
    sibling_root = apex_dir.parent.parent
    if (sibling_root / "pattern" / "apex").exists() or sibling_root.name == "skills":
        return sibling_root
    return Path.home() / ".claude" / "skills"


def parse_routing_table(routing_path: Path) -> dict[str, dict]:
    """Extract node-type -> {donor, gate} mapping from donor-routing.md."""
    if not routing_path.exists():
        print(f"ERROR: Routing file not found: {routing_path}")
        return {}
    content = routing_path.read_text()
    table = {}
    for line in content.split("\n"):
        if line.startswith("|") and "Node type" not in line and "---" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                node_type = parts[0]
                table[node_type] = {
                    "donor": parts[1],
                    "gate": parts[2] if len(parts) > 2 else "",
                }
    return table


def donor_candidates(donor_name: str, skills_dir: Path) -> list[Path]:
    """Candidate SKILL.md paths: local donor link first, then skills root."""
    donor_link = Path(__file__).resolve().parent.parent / "context" / "donors" / donor_name
    return [donor_link / "SKILL.md", skills_dir / donor_name / "SKILL.md"]


def check_donor_exists(donor_name: str, skills_dir: Path) -> tuple[bool, Path | None, int]:
    """Check if a donor's SKILL.md exists. Returns (exists, resolved_path, size)."""
    for candidate in donor_candidates(donor_name, skills_dir):
        if candidate.exists():
            return True, candidate, candidate.stat().st_size
    return False, None, 0


def check_gate_match(donor_name: str, gate_keywords: list[str], skills_dir: Path) -> list[str]:
    """Check the donor's SKILL.md contains at least one gate keyword (any-of,
    matching donor-health semantics — W1/B1.2 single-manifest reconciliation)."""
    if not gate_keywords:
        return []
    for candidate in donor_candidates(donor_name, skills_dir):
        if candidate.exists():
            content = candidate.read_text().lower()
            return [] if any(kw in content for kw in gate_keywords) else gate_keywords
    return ["SKILL.md not found"]


def main():
    skills_dir = resolve_skills_root(sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--skills-dir" else None)

    print("=== APEX DONOR SYNC CHECK ===")
    print(f"Skills root: {skills_dir}\n")

    routing = parse_routing_table(ROUTING_FILE)
    if not routing:
        print("FAIL: Could not parse routing table")
        sys.exit(1)

    errors = []
    # Derive the donor set from the table: a donor counts if its canonical
    # name appears in any Invoke cell (cells may be prose, e.g.
    # "hand off to ship / land-and-deploy" or "think-pipeline slots, then autovibe").
    known_donors = set(gate_keywords)
    donors = set()
    for entry in routing.values():
        cell = entry["donor"].lower()
        # Word-boundary match: "reason" must not match inside "super-reasoner".
        mentioned = [name for name in known_donors
                     if re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", cell)]
        if mentioned:
            donors.update(mentioned)
        else:
            errors.append(f"routing table Invoke cell names no known donor: '{entry['donor']}'")
    donors = sorted(donors)

    warnings = []
    checked = 0

    for donor_name in donors:
        keywords = gate_keywords.get(donor_name)
        if keywords is None:
            warnings.append(f"{donor_name}: in routing table but has no gate-keyword entry — gate UNVERIFIED")
            keywords = []

        exists, resolved, size = check_donor_exists(donor_name, skills_dir)
        gate_missing = check_gate_match(donor_name, keywords, skills_dir)

        if exists and not gate_missing:
            print(f"  ✅ {donor_name} — {size}B — gate keywords present")
            checked += 1
        elif not exists:
            print(f"  ❌ {donor_name} — SKILL.md MISSING")
            errors.append(f"{donor_name}: SKILL.md not found (tried {[str(c) for c in donor_candidates(donor_name, skills_dir)]})")
        else:
            print(f"  ⚠️  {donor_name} — {size}B — missing gate keywords: {gate_missing}")
            errors.append(f"{donor_name}: gate keywords missing: {gate_missing}")
            checked += 1  # Donor exists, just gate partial

    print(f"\n--- RESULT ---")
    print(f"Checked: {checked}/{len(donors)} donors from routing table")
    for w in warnings:
        print(f"  WARNING: {w}")
    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors:
            print(f"  - {e}")
        print("\nSTATUS: FAIL")
        sys.exit(1)
    print("All donors present, all gates verified.")
    print("\nSTATUS: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
