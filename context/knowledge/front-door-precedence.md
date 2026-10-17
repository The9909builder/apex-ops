# Front-door precedence (W1 item 44)

One table that decides which door a raw user intent enters through. The machine
copy is `front-door-precedence.json` (one source, loaded by
`scripts/check-front-door.py`); this file is the agent-facing prose.

| Door | Role | Enters when | First move |
|------|------|-------------|------------|
| apex | multi-leaf routing | the goal decomposes into several typed leaves (learn/decide/build) across donors | decode, ground, decompose to a typed pyramid, route leaves |
| ultraflow | blab to skill | a messy intent should become a reusable, self-improving skill | ground + frame, then forge/evolve a skill package |
| omni-forge | arc | the intent spans a full arc (research, idea, decision, plan, build, meta) | run the adaptive-depth pipeline on the whole arc |
| kraken-flow | spine | decide + design + build in one messy-to-executed pass | run the 8-node reasoning spine |
| vague-to-system | card | the intent needs one System Card forged and routed onward | classify, forge the card, route it |

## Rules

- Score = how many of a door's patterns appear in the intent; highest score wins.
- Ties resolve by precedence order: apex, ultraflow, omni-forge, kraken-flow, vague-to-system.
- No pattern matches: the fallback door is vague-to-system (a card is the cheapest correct first step).
- A door that receives an intent scoring higher for another door names that door and hands
  off. Never absorb another door's job (monolith-drift).

## Mutual refs

Every door's SKILL.md carries one line naming its role in this table; that line is the
mutual reference. The apex copy of the line: apex is the multi-leaf routing door; intents
that score higher for another door are handed off with the door named, not absorbed.

Mechanical check:

```bash
python3 scripts/check-front-door.py --fixtures context/knowledge/fixtures/front-door/
python3 scripts/check-front-door.py --intent "<raw intent text>"
```
