---
name: vague-to-system
preamble-tier: 1
version: 1.2.0
description: |
  Transforms any vague input into a grounded System Card that builder skills can execute.
  CLASSIFY (clarity + stuck-loop signal) → INTERROGATE (capped; one-at-a-time if stuck) → FORGE →
  ROUTE (incl. synthesis-forge for full-arc intents). Fast path: one pass, one card.
---

<!-- TFC:PREAMBLE-HOOK START -->
## TFC Runtime Hook (managed — do not edit; tfc_install regenerates this block)

Run this first. It surfaces prior learnings, records the invocation, and exposes
`tfc_learn <type> <note>` (type: operational | sharp_edge | routing | timing) so a
genuine learning is one reliable call — never a hand-built JSON line.

```bash
_TFC_RT="${TFC_HOME:-$HOME/.future-code}/mcp/tfc-builder/runtime"
[ -f "$_TFC_RT/preamble.sh" ] && source "$_TFC_RT/preamble.sh" "pattern" "vague-to-system"
```
<!-- TFC:PREAMBLE-HOOK END -->

## Preamble (run first)

```bash
# TFC Preamble v1
_TFC_HOME="${TFC_HOME:-$HOME/.future-code}"
_SKILL_ID="vague-to-system"
_SKILL_CAT="pattern"
_SESSION_ID="$$-$(date +%s)"
_TEL_START=$(date +%s)
_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
_PROJECT=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")

echo "BRANCH: $_BRANCH | PROJECT: $_PROJECT | SESSION: $_SESSION_ID"

_MODEL_TIER=$(grep '^model_tier:' "$_TFC_HOME/skills/$_SKILL_CAT/$_SKILL_ID/spec.yaml" 2>/dev/null | awk '{print $2}' | tr -d '"' || echo "sonnet")
echo "MODEL_TIER: $_MODEL_TIER"

_LEARN_FILE="$_TFC_HOME/skills/$_SKILL_CAT/$_SKILL_ID/learnings.jsonl"
if [ -f "$_LEARN_FILE" ]; then
  _LC=$(wc -l < "$_LEARN_FILE" 2>/dev/null | tr -d ' ')
  echo "LEARNINGS: $_LC entries loaded"
  [ "${_LC:-0}" -gt 0 ] && tail -5 "$_LEARN_FILE" 2>/dev/null | python3 -c "
import sys, json
for line in sys.stdin:
    line = line.strip()
    if line:
        try:
            d = json.loads(line)
            print('  •', d.get('insight','')[:120])
        except: pass
" 2>/dev/null | head -3 || true
else
  echo "LEARNINGS: 0"
fi

_SPEC_VER=$(grep '^version:' "$_TFC_HOME/skills/$_SKILL_CAT/$_SKILL_ID/spec.yaml" 2>/dev/null | awk '{print $2}')
echo "SKILL_VERSION: ${_SPEC_VER:-unknown}"
```

Pull past context before forging:

```python
mind_retrieve(
  user_id="550e8400-e29b-41d4-a716-446655440000",
  query="<paste 3-5 keywords from the vague input>",
  limit=3,
  min_salience=0.4
)
```

If mind_retrieve returns a prior System Card or decision on this topic, surface it before
proceeding. The user may be iterating, not starting fresh.

**Front-door precedence:** vague-to-system is the card door; an intent that scores higher for
apex (multi-leaf routing), ultraflow (blab-to-skill), omni-forge (arc), or kraken-flow (spine)
is handed off, not absorbed. Table: `~/.future-code/skills/pattern/apex/context/knowledge/front-door-precedence.md`.

---

## Phase 1 — CLASSIFY

Read the raw input. Do not rewrite it. Do not summarize it yet. Run these five checks:

**Intent class detection** (pick one):

| Class | Signal | Builder skill |
|-------|--------|---------------|
| BUILD | "make", "build", "create", "write", "generate", artifact noun | autovibe |
| DECIDE | "should I", "which", "best way to", "compare", "strategy" | think-pipeline |
| DEBUG | "broken", "failing", "error", "wrong", "fix", "why is" | realthink |
| EXPLORE | "what is", "how does", "explain", "understand", "learn" | think-pipeline --gap |
| SPEC | "design", "plan", "spec out", "architect", "define" | think-pipeline --build |

**Compound intent** (two classes in one input, e.g. "decide X then build Y"): do NOT collapse to
one class. Record both in order (e.g. `DECIDE → BUILD`). Phase 4 sequences a route per class.

**Domain detection** (pick one or "unclear"):

`ai` / `backend` / `frontend` / `devops` / `data` / `mobile` / `design` / `finance` / `content` / `unclear`

**Clarity score**:
- Score 3: action verb present, domain clear, output type inferrable. Skip to Phase 3.
- Score 2: one of the three is missing. One question resolves it. Ask it, then skip to Phase 3.
- Score 1 or 0: two or more missing. Run Phase 2 (INTERROGATE).

**Stuck-loop signal** (independent of clarity — a rambling input can be clear-but-sparse OR
genuinely stuck, and they need different handling in Phase 2):
- Self-referential confusion markers: the input comments on its own inability to articulate
  ("I don't know how to say this," "it's hard to put into words," "I keep going in circles,"
  "this is all jumbled").
- Restatement without new information: the same underlying point re-asserted 2+ times in
  different words, with no added specifics each pass.
- Unresolved-thread density: many clauses opened ("also," "another thing is," "like") with none
  closed or connected back to a single throughline.

If 2 or more of these are present, set `Stuck: true`. This does not change the Clarity score —
it changes which question style Phase 2 uses.

**Output this block:**

```
## CLASSIFY

Intent class: [BUILD | DECIDE | DEBUG | EXPLORE | SPEC]
Domain: [detected domain or "unclear"]
Clarity: [3=forge-direct | 2=one-question | 1=interrogate]
Stuck: [true | false]
Missing: [what is unknown — actor / output-type / domain / constraints / "nothing"]
```

If Clarity is 3, skip to Phase 3 now.

---

## Phase 2 — INTERROGATE

Only runs when Clarity score is 1 or 0. Two modes, chosen by the Stuck signal from Phase 1.

### Mode A — sparse (Stuck: false)

Hard cap: 3 questions maximum.

Before asking, rank unknowns by impact:
1. Who is the actor? (most load-bearing — wrong actor = wrong everything)
2. What is the concrete output? (second most — defines the builder skill)
3. What is the hardest constraint? (time / tech stack / scope)

Ask only the top unknowns (up to 3). Ask them all at once in a single message, not sequentially.

Format:
```
To build your System Card, I need three things:
1. [Question about actor or context]
2. [Question about concrete output]
3. [Question about constraint]
```

**STOP.** Wait for user to answer. Do not proceed to Phase 3 until answers arrive.

When answers arrive, re-run Phase 1 classify. Clarity should now be 3. If not, pick the
single most important remaining unknown, ask it once more, then proceed regardless.

### Mode B — stuck (Stuck: true)

A batch of 3 questions compounds the problem — a stuck user answering all 3 at once tends to
spiral further instead of converge. Ask ONE question at a time instead.

1. Find the single most concrete, least-abstract fragment already in their input (a specific
   noun, action, or complaint — not the vaguest sentence, the sharpest one).
2. Reflect it back in one plain-language sentence: "It sounds like the core of this is ___ — is
   that right?" This gives the user something to confirm or correct instead of generating more
   raw material from a blank state.
3. Ask exactly one narrow question that expands only that fragment.
4. **STOP.** Wait for the answer. Repeat the reflect-then-ask step on the new answer.
5. Cap at 5 rounds (looser than Mode A's 3 — extraction is genuinely harder here). After 5
   rounds, or as soon as ACTOR + OUTPUT are both nameable, forge the card with whatever is
   confirmed. Do not chase full certainty on every field.

A card built via Mode B is tagged `EXTRACTION_METHOD: rabbit-hole` in Phase 3.

---

## Phase 3 — FORGE

Build the System Card. Every field is ONE LINE. Max 15 words per field.

```
## SYSTEM CARD

ACTOR:       [who is doing this — specific person/role, not "users"]
GOAL:        [what they want to achieve — one action + one outcome]
DOMAIN:      [single domain from the detection table]
OUTPUT:      [the concrete thing that gets built, decided, or fixed]
CONSTRAINTS: [the binding limits — time, tech, scope, or "none stated"]
SUCCESS:     [the one observable signal that this worked]
EXTRACTION_METHOD: [clean | interrogated | rabbit-hole]
MODE:        [EXECUTION | HYBRID | EXPLORATION, from Clarity: 3=EXECUTION, 2=HYBRID, 1/0=EXPLORATION]
RISK:        [0-10, scope plus blast radius; never blank]
ROOT TYPE:   [LEARN | DECIDE | GENERATE | RESEARCH | BUILD | SHIP | LEVERAGE, mapped from the CLASSIFY class: EXPLORE→LEARN, DECIDE→DECIDE, BUILD/DEBUG→BUILD, SPEC→GENERATE]
```

These last three lines (plus DRYRUN when set) are governance: APEX Stage 0 DECODE consumes this
card verbatim. One shared schema: `context/knowledge/system-card.schema.json` v1.0 (apex skill);
mechanical check: `python3 scripts/check-system-card.py --check <card>`.

Rules for forging each field:

**ACTOR**: Start with "A solo" / "A team of N" / "The user building" — never just "the user" or "developers."
Name the real situation, not an abstract role.

**GOAL**: One sentence: "[ACTOR] wants to [action] so that [outcome]." Delete "in order to."

**OUTPUT**: Name the artifact. Not "a solution" or "a system." Name it: "a CLI tool," "an API endpoint,"
"a Next.js page," "a decision between X and Y," "a debugged auth flow."

**CONSTRAINTS**: If the user named a stack, put it here. If they named a deadline, put it here.
If they named nothing, write "none stated." Never invent constraints.

**SUCCESS**: Complete this sentence: "I'll know it worked when ___." Should be observable in
under 60 seconds by the user. Not a metric. A moment.

**EXTRACTION_METHOD**: Set from how this card was built — `clean` (Clarity was 3, no questions
asked), `interrogated` (Phase 2 Mode A), or `rabbit-hole` (Phase 2 Mode B). Downstream skills use
this to gauge confidence: a rabbit-hole card warrants a lighter-touch re-confirmation rather than
treating every field as fully solid.

After writing the System Card, pause for 3 seconds of internal validation:
- Could autovibe execute the OUTPUT field directly? If yes, card is good.
- Is any field a paragraph? If yes, rewrite it to one line.
- Is ACTOR "users" or "developers"? If yes, get more specific.

---

## Phase 4 — ROUTE

Pick the builder skill based on the CLASSIFY intent class and OUTPUT field:

| Intent class | OUTPUT is an artifact | OUTPUT is a decision/insight | OUTPUT is a broken thing |
|---|---|---|---|
| BUILD | `→ /autovibe` | `→ /think-pipeline` | `→ /realthink --build` |
| DECIDE | `→ /think-pipeline` | `→ /think-pipeline` | `→ /realthink` |
| DEBUG | `→ /realthink --build` | `→ /realthink` | `→ /realthink` |
| EXPLORE | `→ /think-pipeline --gap` | `→ /think-pipeline` | `→ /realthink --ground` |
| SPEC | `→ /think-pipeline --build` | `→ /think-pipeline` | `→ /autovibe` |

**Compound intent:** if CLASSIFY recorded two classes (e.g. `DECIDE → BUILD`), emit ONE route
line per class in order, joined by `then` — the first resolves the decision, the second builds
on it. Example: `→ /think-pipeline "..." then → /autovibe "..."`.

**Full-pipeline override:** if CLASSIFY recorded a compound intent of 3+ chained classes (e.g.
`EXPLORE → DECIDE → BUILD`), or the System Card is tagged `EXTRACTION_METHOD: rabbit-hole` and
OUTPUT is broad rather than one well-scoped artifact, or the input explicitly asks for the whole
arc ("idea to shipped," "figure out what to build and build it") — do not hand-chain 3+ separate
skill calls. Route to `/synthesis-forge` instead: it already runs brainstorm → vision → ground →
synthesis → compile as one gated pipeline with shared state, which a hand-chained sequence of
single-purpose skills does not have.

Emit the route as:

```
## ROUTE

→ /[skill] "[one-sentence summary of the System Card]"

Reason: [one line — why this skill and not the alternatives]
Handoff: Paste the System Card above into the skill invocation as context.
```

Then ask: "Ready to route to [skill]? Type 'go' to proceed or adjust any System Card field first."

**STOP.** Wait for user confirmation before invoking the next skill.

When user confirms (any affirmative), invoke:
```
Skill(skill:"[skill-name]", args:"[paste System Card]")
```

---

## Sharp Edges (from spec.yaml)

- **interrogate-overrun:** Never ask more than 3 questions. Pick the top 3 unknowns only. Watch for: 4th bullet point in INTERROGATE, second round of questions before Phase 3.
- **system-card-bloat:** Every field is one line. Watch for: fields longer than 20 words, nested bullets inside the card.
- **route-to-wrong-skill:** BUILD + artifact = autovibe. DECIDE/EXPLORE = think-pipeline. Broken thing = realthink. Watch for: routing autovibe at a decision, routing think-pipeline at a build.
- **stuck-mode-batch-questions:** Never batch 3 questions when Stuck: true. A stuck user answering all 3 at once tends to spiral further, not converge. Watch for: Mode B asking more than one question per turn.

---

## Voice

Direct, concrete, builder-to-builder. Name the artifact. Name the actor. Name the skill.

No filler. No "I'll help you." No "Let's explore." Start with the action.

No em dashes. No AI vocabulary: delve, crucial, robust, comprehensive, nuanced, multifaceted.

Short paragraphs. End with what to do next.

The user has context you do not. The System Card is a handoff, not a decision. The user decides.

---

## Completion Status Protocol

Report using exactly one of:

- **DONE** — System Card forged, route identified, user confirmed. Evidence: [card summary].
- **DONE_WITH_CONCERNS** — Card forged, but [specific concern about a field or route].
- **BLOCKED** — Cannot proceed. Blocker: [what is missing]. Tried: [what was attempted]. Recommendation: [what user needs to provide].
- **NEEDS_CONTEXT** — Input too sparse to classify. Need: [exactly what is missing]. Ask: [the one highest-leverage question].

Format: `STATUS | REASON | ATTEMPTED | RECOMMENDATION`

---

## Operational Self-Improvement

Before completing: if you found a pattern where CLASSIFY misfired, a question that resolved
ambiguity especially well, or a routing rule that needed an exception, log it.

Do not log: obvious facts, one-time errors, anything the user told you explicitly.

```bash
_TFC_HOME="${TFC_HOME:-$HOME/.future-code}"
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"vague-to-system","type":"operational","key":"SHORT_KEY","insight":"DESCRIPTION — include what was vague, how it resolved, what the card said","confidence":0.8,"source":"observed","project":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo unknown)'"}' \
  >> "$_TFC_HOME/skills/pattern/vague-to-system/learnings.jsonl"
```

Replace `SHORT_KEY` with a slug (e.g., `build-vs-spec-collision`, `actor-missing-from-short-input`).

---

## Telemetry (run last)

```bash
_TEL_END=$(date +%s)
_TEL_DUR=$(( _TEL_END - _TEL_START ))
_TFC_HOME="${TFC_HOME:-$HOME/.future-code}"
mkdir -p "$_TFC_HOME/analytics"
echo '{"skill":"vague-to-system","duration_s":"'"$_TEL_DUR"'","outcome":"OUTCOME","session":"'"$_SESSION_ID"'","project":"'"$_PROJECT"'","branch":"'"$_BRANCH"'","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' \
  >> "$_TFC_HOME/analytics/skill-usage.jsonl" 2>/dev/null || true
```

Replace `OUTCOME` with: `success`, `error`, `blocked`, `needs_context`.
