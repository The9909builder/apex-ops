# apex-ops mirror design (W4 item 31)

## Repo

`Cyperphycho/apex-ops` (public; scheduled Actions minutes are free on public
repos). Built by the agent with `rsync -rL` from
`~/.future-code/skills/pattern/apex/` so donor symlinks become real dirs:

- include: `SKILL.md spec.yaml protocol.yaml quality.yaml evals.yaml
  scripts/ context/ learnings.jsonl CHANGELOG.jsonl` (when present)
- exclude: `receipts/ __pycache__/ .blackboard-* analytics/`

Nothing secret ever lands here: no `cloud.json`, no `notify.json`, no `state.db`,
no keys. Path names inside scripts are fine (public by design).

## Artifact flow

1. Each scheduled workflow runs its check against the checkout.
2. It writes one JSON row and pushes it to the orphan branch `ops-artifacts`
   (`ops-artifacts/<workflow>.json`), serialized by `concurrency: ops-artifacts`.
3. Local pull (built at window time): `apex-cloud-pull` fetches
   `https://raw.githubusercontent.com/Cyperphycho/apex-ops/ops-artifacts/ops-artifacts/<name>.json`
   into `~/.apex/journal/ops-artifacts/`; run at wake + hourly via pulse.
4. Cockpit: mission-control gains an `OPS` source (mtime + freshest row age,
   STALE >24h) in the execution phase after the window. That is the W4 gate leg
   "GH Action row in cockpit <=24h".

## Honest boundary

The weekly fold needs the local agent (skill eval + CHANGELOG write), so CI only
produces a readiness row (counts, last-changelog ts). The regression suite of
evals stays local. What CI gives us: donor drift detection between sessions,
catalog hygiene, and a heartbeat proving the mirror repo is alive.

## Rows

| workflow | cadence | row | meaning |
|---|---|---|---|
| nightly-donor-health | daily 18:47Z | donors map + PASS/FAIL | donor reachability + drift |
| weekly-fold-readiness | Sun 18:23Z | unconsumed_est, changelog_last | fold queue size |
| catalog-freshness | Sun 18:11Z | entries, dups, junk | catalog hygiene (item 46) |
