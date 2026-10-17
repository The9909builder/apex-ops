#!/usr/bin/env python3
"""
APEX Telemetry Logger.

Appends structured run data to learnings.jsonl for routing analysis.

Usage:
    python3 telemetry.py log --type <type> --insight "<text>" [--confidence <0-1>]
    python3 telemetry.py log --type routing --insight "routed LEARN to deep-understanding" --confidence 0.9
    python3 telemetry.py log --type operational --insight "blackboard persisted after FUSE" --confidence 0.8
    python3 telemetry.py stats                        # Show learning stats
    python3 telemetry.py tail [N]                     # Show last N entries
    python3 telemetry.py query --terms "bt mic dictation" [--limit 5]
                                                      # Search learnings for override
                                                      # candidates at DECODE time
    python3 telemetry.py antibody add --signature "..." --wrong-route "..."
                                      --correction "..."   # immunize a bad route
    python3 telemetry.py antibody check --terms "..." --routes "d1 d2"
                                                      # screen planned route (exit 1 = block)

Types: operational | sharp_edge | routing | timing
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LEARNINGS_FILE = Path(__file__).parent.parent / "learnings.jsonl"
ANTIBODIES_FILE = Path(__file__).parent.parent / "context" / "knowledge" / "antibodies.json"


def log_entry(entry_type: str, insight: str, confidence: float = 0.8, source: str = "observed") -> dict:
    """Create and append a learning entry."""
    entry = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "skill": "apex",
        "type": entry_type,
        "insight": insight,
        "confidence": confidence,
        "source": source,
    }

    with open(LEARNINGS_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return entry


def log_run(session_id: str, stages_completed: list[str], gates_fired: list[str],
            stages_skipped: list[str], routes: list[dict], contradictions: int) -> dict:
    """Log a complete APEX run summary."""
    insight = (
        f"session={session_id} "
        f"stages={','.join(stages_completed)} "
        f"gates={','.join(gates_fired)} "
        f"skipped={','.join(stages_skipped) if stages_skipped else 'none'} "
        f"routes={len(routes)} "
        f"contradictions={contradictions}"
    )

    return log_entry("routing", insight, confidence=0.9, source="execution")


def show_stats() -> None:
    """Show statistics from learnings.jsonl."""
    if not LEARNINGS_FILE.exists():
        print("No learnings yet.")
        return

    entries = []
    with open(LEARNINGS_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if not entries:
        print("No valid entries.")
        return

    by_type = {}
    for e in entries:
        t = e.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

    print(f"Total entries: {len(entries)}")
    print(f"By type:")
    for t, count in sorted(by_type.items()):
        print(f"  {t}: {count}")
    print(f"Date range: {entries[0].get('ts', '?')} to {entries[-1].get('ts', '?')}")


def tail_entries(n: int = 5) -> None:
    """Show last N entries."""
    if not LEARNINGS_FILE.exists():
        print("No learnings yet.")
        return

    entries = []
    with open(LEARNINGS_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    for e in entries[-n:]:
        print(f"[{e.get('ts', '?')}] {e.get('type', '?')}: {e.get('insight', '?')[:100]}")


def query_entries(terms: list[str], limit: int = 5) -> list[dict]:
    """Search learnings.jsonl for entries matching intent terms.

    Scoring: each term present in the entry's insight (case-insensitive)
    adds 1; type='routing' and type='sharp_edge' entries get a +1 relevance
    bump because they carry routing corrections. Returns top `limit` by
    (score, recency). Empty list when nothing matches — the caller proceeds
    with the default routing table, no override.
    """
    if not LEARNINGS_FILE.exists():
        return []

    terms_lower = [t.lower() for t in terms if t.strip()]
    if not terms_lower:
        return []

    scored = []
    with open(LEARNINGS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            insight = str(e.get("insight", "")).lower()
            score = sum(1 for t in terms_lower if t in insight)
            if score == 0:
                continue
            if e.get("type") in ("routing", "sharp_edge"):
                score += 1
            scored.append((score, e))

    scored.sort(key=lambda pair: (pair[0], pair[1].get("ts", "")), reverse=True)
    return [e for _, e in scored[:limit]]


def run_query(terms: list[str], limit: int = 5) -> int:
    """Print override candidates in a greppable format. Returns match count."""
    matches = query_entries(terms, limit)
    print(f"LEARNINGS QUERY: terms={terms} matches={len(matches)}")
    for e in matches:
        print(f"  OVERRIDE-CANDIDATE [{e.get('ts', '?')}] "
              f"({e.get('type', '?')}): {str(e.get('insight', ''))[:160]}")
    if matches:
        print("ACTION: fire LEARNING OVERRIDE: lines in ROUTE for matched leaves; "
              "cite the entry ts.")
    else:
        print("ACTION: no override: route from the default donor table.")
    return len(matches)


# --- Route antibodies: each bad route immunizes future runs -----------------

def load_antibodies() -> list[dict]:
    """Load antibody entries; corrupt file or missing file = empty list."""
    if not ANTIBODIES_FILE.exists():
        return []
    try:
        data = json.loads(ANTIBODIES_FILE.read_text())
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_antibodies(entries: list[dict]) -> None:
    ANTIBODIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    ANTIBODIES_FILE.write_text(json.dumps(entries, indent=2) + "\n")


def add_antibody(signature: str, wrong_route: str, correction: str) -> dict:
    """Record a bad-route signature so the same malformation is caught next time."""
    entry = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "signature": signature.lower(),
        "wrong_route": wrong_route,
        "correction": correction,
    }
    entries = load_antibodies()
    if any(e.get("signature") == entry["signature"] and
           e.get("wrong_route") == wrong_route for e in entries):
        print(f"ANTIBODY EXISTS: '{signature}' -> '{wrong_route}' already immunized")
        return entry
    entries.append(entry)
    save_antibodies(entries)
    print(f"ANTIBODY ADDED: '{signature}' must not route to '{wrong_route}'; "
          f"correction: {correction}")
    return entry


def check_antibodies(terms: list[str], proposed_routes: list[str]) -> int:
    """Screen a planned route against known bad-route signatures.

    Prints ANTIBODY BLOCK lines for any signature that matches the intent
    terms AND names a proposed donor as its wrong_route. Returns block count.
    """
    entries = load_antibodies()
    if not entries:
        print("ANTIBODY CHECK: no antibodies on file — route unscreened")
        return 0

    terms_joined = " ".join(t.lower() for t in terms if t.strip())
    routes_lower = [r.lower() for r in proposed_routes]
    blocks = 0
    for e in entries:
        sig_terms = e.get("signature", "").split()
        # any signature term present in the intent = candidate match;
        # the wrong_route must ALSO be among the proposed routes to block
        sig_matches = bool(sig_terms) and any(t in terms_joined for t in sig_terms)
        wrong = e.get("wrong_route", "").lower()
        route_hit = bool(wrong) and any(wrong in r for r in routes_lower)
        if sig_matches and route_hit:
            blocks += 1
            print(f"ANTIBODY BLOCK: signature '{e['signature']}' routes to "
                  f"'{wrong}' — known bad. Correction: {e.get('correction', '?')}")
    if blocks == 0:
        print(f"ANTIBODY CHECK: {len(entries)} antibody(ies) on file, 0 blocks")
    return blocks


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "log":
        entry_type = None
        insight = None
        confidence = 0.8

        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--type" and i + 1 < len(sys.argv):
                entry_type = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--insight" and i + 1 < len(sys.argv):
                insight = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--confidence" and i + 1 < len(sys.argv):
                confidence = float(sys.argv[i + 1])
                i += 2
            else:
                i += 1

        if not entry_type or not insight:
            print("Usage: telemetry.py log --type <type> --insight '<text>'")
            sys.exit(1)

        entry = log_entry(entry_type, insight, confidence)
        print(f"Logged: {entry['type']}: {entry['insight'][:80]}")

    elif cmd == "query":
        terms: list[str] = []
        limit = 5

        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--terms" and i + 1 < len(sys.argv):
                terms = sys.argv[i + 1].split()
                i += 2
            elif sys.argv[i] == "--limit" and i + 1 < len(sys.argv):
                limit = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1

        if not terms:
            print("Usage: telemetry.py query --terms '<word1 word2 ...>' [--limit N]")
            sys.exit(1)

        run_query(terms, limit)

    elif cmd == "antibody":
        if len(sys.argv) > 2 and sys.argv[2] == "add":
            # antibody add --signature "..." --wrong-route "..." --correction "..."
            vals = {"signature": None, "wrong-route": None, "correction": None}
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] == "--signature" and i + 1 < len(sys.argv):
                    vals["signature"] = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--wrong-route" and i + 1 < len(sys.argv):
                    vals["wrong-route"] = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--correction" and i + 1 < len(sys.argv):
                    vals["correction"] = sys.argv[i + 1]
                    i += 2
                else:
                    i += 1
            if not all(vals.values()):
                print("Usage: telemetry.py antibody add --signature '<terms>' "
                      "--wrong-route '<donor>' --correction '<what to do instead>'")
                sys.exit(1)
            add_antibody(vals["signature"], vals["wrong-route"], vals["correction"])
        elif len(sys.argv) > 2 and sys.argv[2] == "check":
            # antibody check --terms "..." --routes "donor1 donor2"
            terms: list[str] = []
            routes: list[str] = []
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] == "--terms" and i + 1 < len(sys.argv):
                    terms = sys.argv[i + 1].split()
                    i += 2
                elif sys.argv[i] == "--routes" and i + 1 < len(sys.argv):
                    routes = sys.argv[i + 1].split()
                    i += 2
                else:
                    i += 1
            if not terms or not routes:
                print("Usage: telemetry.py antibody check --terms '<words>' "
                      "--routes '<donor1 donor2 ...>'")
                sys.exit(1)
            blocks = check_antibodies(terms, routes)
            sys.exit(1 if blocks else 0)
        else:
            print("Usage: telemetry.py antibody add|check ...")
            sys.exit(1)

    elif cmd == "stats":
        show_stats()

    elif cmd == "tail":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        tail_entries(n)

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
