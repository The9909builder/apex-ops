# Council Rules (W1 item 48)

Council mode is how a DECIDE leaf resolves a decision with more than one
viable option. It exists to make the winning case inspectable, not to slow
the router.

## When council fires

- DECIDE leaf with 2 or 3 viable candidates, none eliminated by GROUND.
- Skipped, with the reason in CLOSE, when: a single candidate survives
  grounding, the decision is owner-gated (Law 7: the user decides), or the
  leaf is a pure lookup.

## Candidates and lenses

- 2-3 candidates, each argued under a distinct lens:
  `reversibility-first | cost-first | speed-first | risk-first`.
- Each candidate gate-scored 0-10 against the leaf's own acceptance
  criterion.

## Winner

- Winner = highest score.
- A non-top winner is allowed only with a `RULED:` line giving the reason
  (usually a gate violation in the top candidate). The reason is part of
  the record.

## Recording (metric: winner + scores in the outcomes ledger)

- Emit the COUNCIL block in the run output.
- Append the row:
  `python3 scripts/check-council.py --record <run-output> --ledger ~/.kraken/outcomes/decisions.jsonl`
  (`source: apex-council`; carries winner, every score, and every lens).
- Budget: decision time <= 2x single-candidate. The 3-candidate cap is the
  mechanical expression of that budget; a 4th candidate means the leaf was
  under-decomposed, split it instead.

## Guard

- `python3 scripts/check-council.py --fixtures context/knowledge/fixtures/council`
  (7/7 fixtures: 3 accept, 4 reject).
- `--check <run-output>` on any run that ran a council.
- selftest check 13 keeps it live.
