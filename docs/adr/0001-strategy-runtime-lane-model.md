# ADR 0001: Strategy Runtime Lane Model

## Status

Accepted

## Context

The project already supports multiple strategy families:

- native strategies executed by the platform's own simulation flow
- NostalgiaForInfinity reference strategies delegated to Freqtrade
- external decision strategies that defer the final decision to `DecisionEnginePort`

Without an explicit model, these lanes could drift into ad hoc special cases.

## Decision

The platform will formalize three strategy runtime lanes:

1. `native`
2. `freqtrade_reference`
3. `decision_engine`

All lanes must still produce or map into the same decision-oriented abstractions:

- feature frame
- decision context
- decision envelope

Reference and decision-engine strategies may add adapter-specific behavior, but they must not bypass the shared execution orchestration or run metadata model.

## Consequences

Positive:

- strategy families remain comparable
- NFI integration stays explicit
- LLM research can mature without breaking deterministic strategies

Negative:

- metadata normalization work increases
- some reference strategies will require adapter shims instead of direct reuse

## Implementation notes

- `StrategyMetadata.runtime` is the control field for lane selection
- reference strategies remain benchmark lanes, not the main execution contract
- future work should avoid adding hidden runtime branches outside the strategy catalog or application layer
