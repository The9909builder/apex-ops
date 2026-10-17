#!/usr/bin/env python3
"""
Contract drift checker for APEX.

Golden-task data is duplicated across three contract files. When they drift,
the eval lane and the quality contract silently disagree. This compares:

  1. Golden task IDs across evals.yaml, quality.yaml, spec.yaml
  2. Required sections across spec.yaml and protocol.yaml
  3. pass_threshold across evals.yaml, quality.yaml, spec.yaml

Exit 0 = no drift. Exit 1 = drift found, with each mismatch printed.

Usage:
    python3 scripts/check-contract-drift.py
"""

import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent.parent


def load_yaml(name: str) -> dict:
    path = HERE / name
    if not path.exists():
        print(f"ERROR: contract file missing: {path}")
        sys.exit(1)
    with open(path) as f:
        return yaml.safe_load(f) or {}


def task_ids(data: dict) -> set:
    return {t.get("id") for t in data.get("golden_tasks", [])}


def main():
    evals = load_yaml("evals.yaml")
    quality = load_yaml("quality.yaml")
    spec = load_yaml("spec.yaml")
    protocol = load_yaml("protocol.yaml")

    drift = []

    # 1. Golden task IDs: evals.yaml and quality.yaml must match exactly.
    #    spec.yaml is a compiled view and may carry no golden tasks at all;
    #    if it carries some, they must be a subset of evals.yaml.
    e_ids, q_ids, s_ids = task_ids(evals), task_ids(quality), task_ids(spec)
    if e_ids != q_ids:
        drift.append(f"golden task IDs evals.yaml vs quality.yaml: only-evals={sorted(e_ids - q_ids)} only-quality={sorted(q_ids - e_ids)}")
    if s_ids and not s_ids.issubset(e_ids):
        drift.append(f"golden task IDs spec.yaml (compiled) not a subset of evals.yaml: unknown={sorted(s_ids - e_ids)}")
    if not s_ids:
        print(f"  note: spec.yaml (compiled) carries no golden tasks — evals.yaml is the eval source of truth ({len(e_ids)} tasks)")

    # 2. Required sections must match between spec.yaml and protocol.yaml.
    spec_sections = set(spec.get("required_sections", []))
    proto_sections = set(protocol.get("required_sections", []))
    if spec_sections != proto_sections:
        drift.append(f"required_sections spec.yaml vs protocol.yaml: only-spec={sorted(spec_sections - proto_sections)} only-protocol={sorted(proto_sections - spec_sections)}")

    # 3. pass_threshold must agree everywhere it appears.
    thresholds = {
        "evals.yaml": evals.get("pass_threshold"),
        "quality.yaml": quality.get("pass_threshold"),
        "spec.yaml": spec.get("pass_threshold"),
    }
    present = {k: v for k, v in thresholds.items() if v is not None}
    if present and len(set(present.values())) > 1:
        drift.append(f"pass_threshold mismatch: {present}")

    if drift:
        print("CONTRACT DRIFT CHECK: FAIL")
        for d in drift:
            print(f"  - {d}")
        sys.exit(1)
    print(f"CONTRACT DRIFT CHECK: PASS "
          f"({len(e_ids)} golden tasks aligned, "
          f"{len(spec_sections)} required sections aligned, "
          f"threshold={next(iter(present.values())) if present else 'n/a'})")
    sys.exit(0)


if __name__ == "__main__":
    main()
