# Intelligence research lane

- Direction id: `intelligence-research-lane`

## Goal

Evolve DecisionEnginePort into a traceable intelligence research lane with prompt registry, trace storage, replay harnesses, evaluation, and mandatory fallback or review so LLM work stays isolated from deterministic execution guarantees.

## Success criteria

- Every intelligence run captures prompt version, raw response, normalized decision, and post-risk trace metadata.
- Replay and evaluation flows can benchmark intelligence-assisted decisions against deterministic baselines.
- No sandbox or live promotion path exists without deterministic fallback or human review.

## Scope hints

- Use docs/blueprint/llm-lane.md, docs/blueprint/platform-program.md Workstream E, and docs/blueprint/metrics-and-gates.md Gate 4 as the target shape.
- Treat trace, replay, fallback, and evaluation as mandatory infrastructure rather than optional research tooling.
- Keep intelligence-assisted strategies isolated from deterministic core behavior and forbid unattended live promotion.
