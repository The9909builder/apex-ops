---
name: realthink
description: "The Real-Problem Lens — takes a messy real-world situation (spoken blab, avoided decision, someone's plan) and finds the ONE leverage move, refusing to proceed on ungrounded claims. GROUND → CRUX → RIPPLE → CUT. Solver's twin of /think-pipeline (which designs mechanisms; this one finds leverage). Signature = the grounding gate: beautiful + ungrounded is rejected."
trigger: /realthink
---

# /realthink — the Real-Problem Lens

**FROM** answering the question that was asked
**TO** finding the *constraint the question is hiding* — then cutting to one move.

Real problems are never the question on the surface. They're the bottleneck underneath.
This skill is the track an LLM can't be shallow on: it **refuses to output leverage
until the truth is grounded**, then runs a fixed loop to the single move that matters.

> Companion, not duplicate. `/think-pipeline` designs *mechanisms* (vague → 7-slot schema).
> `/realthink` finds *leverage* (real situation → the one move). Use think-pipeline to
> build the thing; use realthink to decide what's worth building and where the crux is.

## Usage

```
/realthink "<messy real situation, said however it comes out>"   # the core case
/realthink "<vague problem>" --deepen # 5-layer Socratic descent to atomic, THEN the loop (see spawner deepen.yaml)
/realthink "<plan/doc>" --audit      # find the load-bearing omission in someone's plan
/realthink "<situation>" --ground    # stop at the grounding gate; just expose what's unknown
/realthink "<situation>" --build      # after the move is found, hand off to autovibe/think-pipeline --build
/realthink --recursive               # run the lens on itself (validates the mechanism)
```

---

## THE LOOP — run in order, no skipping

### ① GROUND  *(the gate — nothing proceeds until this passes)*

The #1 failure of any thinking system is **fluent fabrication**: gorgeous analysis
built on an actor and cost that were never real. So before anything else, force three
facts into the open:

```
ACTOR    — exactly WHO is stuck? (a person, not a market. "a solo dev at 11pm", not "users")
COST     — what do they pay TODAY to cope? (time / money / pain / a manual grind)
EVIDENCE — how do we KNOW? (lived it / saw it / a quote / a number) — or mark it UNKNOWN
```

**Gate rule:** if ACTOR or COST is unnamed, or EVIDENCE is invented, you do **not** get
to output a leverage move. You output: *"UNGROUNDED — here is exactly what I'd need to
find out first: …"* Then stop, or pull memory (`mind_retrieve`) to ground it.

> Pull past reasoning to ground, don't fabricate it:
> `mind_retrieve(user_id=<UUID>, query="<situation keywords>", min_salience=0.5)`
> (Mind already holds deep findings from past sessions — use them as evidence, not your imagination.)

### ② CRUX  *(find the one constraint — leverage lives only here)*

Every system moves only as fast as its single tightest bottleneck. Find it:

- *"What's the ONE thing that, if it vanished, makes everything else easy?"*
- *"What does everyone here just accept as the unavoidable price of doing this?"*

That accepted cost is usually the crux. Name it in one sentence. Tuning anything that
isn't the crux is motion, not progress.

### ③ RIPPLE  *(trace the loops + the second-order)*

- **Reinforcing loop** — what snowball makes this stronger as it grows?
- **Balancing loop** — what thermostat fights back / caps it?
- **Second-order** — once the crux is cracked, what *new* thing becomes possible that
  wasn't before? (Uber's driver network → Uber Eats: same network, new payload.)

The second-order answer is usually where the real value hides.

### ④ CUT  *(one move out — via negativa)*

End with **exactly one** leverage move — not a menu of five. State:

- **THE MOVE** — the single highest-leverage action (changes the *unit/goal*, not a knob).
- **THE DELETE** — what this refuses or removes. The "no" that defines the shape.
- **THE TELL** — the one concrete signal that proves it worked.

If the move requires building, hand off: `/think-pipeline "<move>" --build` or `autovibe`.

---

## 5 INPUT TYPES (what you can feed it)

1. **The messy blab** — "I want X but it's all tangled" (the primary case; say it however).
2. **The avoided decision** — a fork you keep circling; the crux is the hidden constraint.
3. **The product/system idea** — find its deleted cost and its reusable network.
4. **The recurring grind** — the thing you do by hand that shouldn't need you.
5. **Someone else's plan/doc** (`--audit`) — find the load-bearing omission (the FEIMS move).

## 5 INTERACTION PATTERNS (verbs, with examples)

1. **GROUND-OR-DIE** — "You said 'users want this' — which user, doing what, costing what? Name it or it's UNKNOWN."
2. **HUNT-THE-CONSTRAINT** — "What's the one bottleneck rate-limiting the whole thing?" (recruitment → FEIMS is a manual govt portal).
3. **NAME-THE-DELETE** — "Uber deleted 'you must own a car.' What does yours delete?"
4. **FOLLOW-THE-RIPPLE** — "Once the crux is solved, what becomes possible?" (network → new payload).
5. **ONE-MOVE-OUT** — "The move: make the books record what's defensible, not what's real — that's the whole design decision."

## 6 ANTI-PATTERNS (each = one principle inverted)

1. ❌ **Fluent fabrication** — beautiful analysis on an ungrounded actor/cost. *(inverts GROUND)*
2. ❌ **Symptom-chasing** — tuning a knob instead of finding the constraint. *(inverts CRUX)*
3. ❌ **First-order blindness** — stopping at the immediate effect, missing the ripple. *(inverts RIPPLE)*
4. ❌ **The menu** — handing over 5 options instead of the 1 move. *(inverts CUT)*
5. ❌ **Feature-piling** — adding capability instead of deleting a cost. *(inverts via-negativa)*
6. ❌ **Answering the question asked** — solving the surface ask, not the constraint underneath. *(inverts the mindset shift)*

## AXIOM

> **The question is never the problem. Ground the truth, find the crux, cut to one move.**
> Beautiful + ungrounded is the enemy.

---

## Auto-trigger (Claude self-applies — no explicit command needed)

Fire this lens when the situation is **"find leverage on a real thing,"** specifically:

- User describes a real problem/frustration and wants insight, not code.
- User is weighing a decision with a tangled constraint.
- `spawner_orchestrate` grades L2+ AND verb-class = `decide / strategize / find-leverage`.
- Reviewing someone's plan/blueprint for what's missing (`--audit`).

**Do NOT auto-fire for:** build/fix/verify execution, status checks, or when the output
is a file diff rather than a decision. (Those go to think-pipeline `--build` or straight to work.)

## Sharp edges (memorize)

1. **The gate is non-negotiable** — no leverage move ships while ACTOR/COST/EVIDENCE is ungrounded.
2. **UUID not email** — `mind_retrieve(user_id=UUID)`; email crashes with a hex error.
3. **Kraken is opt-in** — never call `mcp__kraken__*` without `--deep` or explicit ask.
4. **TLB is banned** — never call any TLB tool. Ever. (Standing user rule.)
5. **One move, not a menu** — if you wrote 5 options, you skipped CUT. Pick the leverage one.
6. **Memory grounds, imagination fabricates** — pull `mind_retrieve` before inventing evidence.
7. **Rate-limit aware** — if the model is rate-capped, run the loop mentally; tools are optional, the gate is not.

## Output contract

End every run with this block:

```
══════════════ REALTHINK ══════════════
Situation   : <one line, as the user meant it>
GROUNDED    : ✅ actor+cost+evidence  |  ⚠️ UNGROUNDED (what's needed: …)
CRUX        : <the one constraint, one sentence>
RIPPLE      : <reinforcing loop> ↑ / <2nd-order opening>
THE MOVE    : <single highest-leverage action>
THE DELETE  : <what it refuses / removes>
THE TELL    : <the one signal it worked>
Next        : <one concrete step in <15 min, or the --build handoff>
═══════════════════════════════════════
```

## Save (close the loop — depth compounds only if you keep it)

```python
mind_remember(content="<CRUX + THE MOVE + path>", salience=0.85, temporal_level=3, content_type="insight")
```
Append one row to the ledger (`~/.kraken/realthink/learnings.jsonl`, created on first run):
```bash
echo '{"ts":"<ISO8601>","situation":"<one line>","grounded":true,"crux":"<…>","move":"<…>","tell":"<…>"}' \
  >> ~/.kraken/realthink/learnings.jsonl
```
