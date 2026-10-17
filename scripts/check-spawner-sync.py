#!/usr/bin/env python3
"""
Spawner-sync checker for APEX.

Skills dual-published to the spawner registry carry a "spawner dialect" view:
  - skill.yaml        (identity: id/name/version)
  - collaboration.yaml (mirrors spec.yaml pairs_with, adds delegation triggers)
  - sharp-edges.yaml   (mirrors spec.yaml sharp_edges into the spawner dialect)

The dialect headers say "keep in sync with spec.yaml by hand" — this checker
turns that manual promise into a machine-checkable invariant.

Invariants per dual-registered skill (spec.yaml = TFC source of truth):
  1. identity: skill.yaml id/name match spec.yaml id/name.
     Version drift is REPORTED as a note (published-vs-canon is a decision).
  2. collaboration.complementary_skills {(skill, direction)} == spec.pairs_with
     {(skill, direction)} as SETS (reasons may differ; the dialect translates).
  3. sharp-edges.yaml sharp_edges ids == spec.yaml sharp_edges ids as SETS.

Exit 0 = no drift. Exit 1 = drift found (dialect views need sync).

Usage:
    python3 scripts/check-spawner-sync.py [--skills-root DIR]
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required (pip install pyyaml)")
    sys.exit(2)

HERE = Path(__file__).resolve().parent.parent   # skill dir
DEFAULT_SKILLS_ROOT = HERE.parent.parent        # skills/


def load(p: Path):
    with open(p) as f:
        return yaml.safe_load(f) or {}


def check_skill(sdir: Path):
    """Return (problems, notes) for one dual-registered skill dir."""
    problems, notes = [], []
    spec_p = sdir / "spec.yaml"
    sk_p = sdir / "skill.yaml"
    if not spec_p.exists():
        return ["skill.yaml present but spec.yaml missing"], notes

    spec = load(spec_p)
    sk = load(sk_p)

    # 1. identity
    if sk.get("id") != spec.get("id"):
        problems.append(f"id: skill.yaml={sk.get('id')!r} != spec.yaml={spec.get('id')!r}")
    if sk.get("name") != spec.get("name"):
        problems.append(f"name: skill.yaml={sk.get('name')!r} != spec.yaml={spec.get('name')!r}")
    sv, pv = sk.get("version"), spec.get("version")
    if sv != pv:
        notes.append(f"version drift: skill.yaml={sv} spec.yaml={pv}")

    # 2. collaboration.yaml <-> spec.pairs_with
    col_p = sdir / "collaboration.yaml"
    if col_p.exists():
        col = load(col_p)
        pairs_spec = {(x.get("skill"), x.get("direction")) for x in (spec.get("pairs_with") or [])}
        pairs_col = {(x.get("skill"), x.get("direction")) for x in (col.get("complementary_skills") or [])}
        missing, extra = pairs_spec - pairs_col, pairs_col - pairs_spec
        if missing:
            problems.append(f"collaboration.yaml missing pairs: {sorted(missing)}")
        if extra:
            problems.append(f"collaboration.yaml extra pairs: {sorted(extra)}")
    elif spec.get("pairs_with"):
        notes.append("no collaboration.yaml (dialect partial — identity only)")

    # 3. sharp-edges.yaml <-> spec.sharp_edges
    se_p = sdir / "sharp-edges.yaml"
    if se_p.exists():
        se = load(se_p)
        ids_spec = {x.get("id") for x in (spec.get("sharp_edges") or []) if isinstance(x, dict)}
        ids_se = {x.get("id") for x in (se.get("sharp_edges") or []) if isinstance(x, dict)}
        if ids_spec - ids_se:
            problems.append(f"sharp-edges.yaml missing ids: {sorted(ids_spec - ids_se)}")
        if ids_se - ids_spec:
            problems.append(f"sharp-edges.yaml extra ids: {sorted(ids_se - ids_spec)}")
    elif spec.get("sharp_edges"):
        notes.append("no sharp-edges.yaml (dialect partial)")

    return problems, notes


def main():
    args = sys.argv[1:]
    root = DEFAULT_SKILLS_ROOT
    if "--skills-root" in args:
        root = Path(args[args.index("--skills-root") + 1])

    files = sorted(root.glob("*/*/skill.yaml"))
    print(f"spawner-sync check — root: {root}")
    print(f"dual-registered skills found: {len(files)}\n")
    if not files:
        print("RESULT: no skill.yaml found — nothing to sync")
        sys.exit(0)

    drift = 0
    for f in files:
        sdir = f.parent
        problems, notes = check_skill(sdir)
        label = f"{sdir.parent.name}/{sdir.name}"
        if problems:
            drift += 1
            print(f"[DRIFT] {label}")
            for p in problems:
                print(f"    x {p}")
            for n in notes:
                print(f"    . {n}")
        else:
            suffix = f"  ({'; '.join(notes)})" if notes else ""
            print(f"[ok]    {label}{suffix}")

    print()
    if drift:
        print(f"RESULT: {drift} skill(s) drifted — dialect views need sync (republish vs pin is a human call)")
        sys.exit(1)
    print("RESULT: all dual-registered skills in sync")
    sys.exit(0)


if __name__ == "__main__":
    main()
