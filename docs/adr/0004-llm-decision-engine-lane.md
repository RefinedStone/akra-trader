# ADR 0004: LLM Decision Engine Lane

## Status

Accepted

## Context

The strategy abstraction was intentionally designed so that decision making can be split from feature generation. This creates a path for LLM-guided strategies, but only if that path is controlled and traceable.

## Decision

LLM-based strategies will be modeled as a `decision_engine` runtime lane behind `DecisionEnginePort`.

The platform will not allow direct provider-specific logic to leak into domain or application code. All LLM usage must be adapter-driven and must emit a standard decision envelope plus trace metadata.

Initial rollout rules:

- allowed in backtest and paper modes
- recorded with prompt/version/response metadata
- paired with deterministic fallback or operator review path
- not promoted to unattended live trading until replay and audit criteria are met

## Consequences

Positive:

- LLM research becomes a first-class but isolated lane
- deterministic and prompt-driven policies can be compared using the same orchestration

Negative:

- trace storage and replay tooling become mandatory
- provider latency and nondeterminism require additional evaluation tooling

## Implementation notes

- prompt templates should be versioned like strategy code
- decision traces should be stored as part of experiment history
- any live usage should start in operator-reviewed mode
