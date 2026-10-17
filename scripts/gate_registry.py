#!/usr/bin/env python3
"""
Single source of donor gate keywords for the APEX verifier family (W1/B1.2).

context/knowledge/gates.json is the single manifest. Any script that needs
gate keywords loads them through this module — never from a local copy (the
three divergent GATE_KEYWORDS dicts this replaced were the F2 finding).

Semantics:
  keywords        any-of markers expected in the donor's own SKILL.md
                  (consumers: donor-health, check-donor-sync)
  route_evidence  any-of markers expected in a run's ROUTE block for this
                  donor (consumer: check-receipts); falls back to keywords.

Usage:
    from gate_registry import load_gates
    gates = load_gates()   # {"donor": {"kind", "keywords", "route_evidence"}}
"""

import json
from pathlib import Path

GATES_FILE = Path(__file__).resolve().parent.parent / "context" / "knowledge" / "gates.json"


def load_gates() -> dict:
    """Load gates.json into a normalized {donor: entry} dict (lowercased lists)."""
    data = json.loads(GATES_FILE.read_text())
    donors = {}
    for name, spec in (data.get("donors") or {}).items():
        entry = dict(spec)
        entry.setdefault("kind", "curated")
        keywords = [str(k).lower() for k in entry.get("keywords", [])]
        entry["keywords"] = keywords
        route = entry.get("route_evidence")
        entry["route_evidence"] = [str(k).lower() for k in route] if route else keywords
        donors[name] = entry
    return donors


if __name__ == "__main__":
    gates = load_gates()
    for name, e in sorted(gates.items()):
        print(f"{name:28s} {e['kind']:8s} keywords={e['keywords']}")
