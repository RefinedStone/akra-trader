# Intelligence research lane

- Direction id: `intelligence-research-lane`

## Goal

Evolve `DecisionEnginePort` into a traceable intelligence research lane with prompt registry, trace
storage, replay harnesses, evaluation, and mandatory fallback or review so LLM work stays isolated
from deterministic execution guarantees.

## Current status on April 21, 2026

- the lane still stops at the port, template strategy, and trace-capable envelope level
- none of the required research infrastructure is implemented yet

## Immediate gaps

- prompt version registry
- raw trace storage
- replay harness
- evaluation workflow
- fallback or review enforcement

## Linked docs

- `docs/status/current-state.md`
- `docs/roadmap/product-roadmap.md`
- `docs/blueprint/llm-lane.md`

## Success criteria

- every intelligence run captures prompt version, raw response, normalized decision, and post-risk
  trace metadata
- replay and evaluation flows can benchmark intelligence-assisted decisions against deterministic
  baselines
- no sandbox or live promotion path exists without deterministic fallback or human review
