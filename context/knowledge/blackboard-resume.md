# Blackboard resume

What failure this prevents: re-deriving an already-grounded crux on resume and producing a
different tree than the original run.

Schema (one JSON object persisted next to the target work):

```json
{
  "session": "<id>",
  "system_card": { "intent": "", "mode": "", "risk": 0, "root_type": "" },
  "grounded": { "verdict": "", "actor": "", "cost": "", "evidence": "" },
  "nodes": {
    "<id>": { "type": "", "parent": "", "delta": "", "donor": "",
              "status": "pending|done|skipped|ungrounded", "output_ref": "" }
  },
  "dependencies": ["A->B"],
  "contradictions": [],
  "plan": []
}
```

Rules:
- Persist after every stage, not at end.
- On resume: reload the blackboard, continue from last completed stage.
- Never re-run DECODE/GROUND from scratch; the grounded crux is the most expensive output
  and re-deriving it invalidates everything downstream.
