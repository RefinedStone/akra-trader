# ADR 0001: Strategy Runtime and Policy Model

## Status

Accepted

## Context

The project already supports multiple strategy families:

- native strategies executed by the platform's own simulation flow
- NostalgiaForInfinity reference strategies delegated to Freqtrade
- external decision strategies that defer the final decision to `DecisionEnginePort`

The strategy surface has also grown beyond a single "decide buy or sell" hook. The platform now needs a
clear model for:

- runtime lane selection
- feature and context construction
- signal generation
- execution intent generation
- comparable run metadata across native and external lanes

Without an explicit model, these lanes could drift into ad hoc special cases.

## Decision

The platform will formalize three strategy runtime lanes:

1. `native`
2. `freqtrade_reference`
3. `decision_engine`

All lanes must still produce or map into the same decision-oriented abstractions:

- feature frame
- decision context
- signal policy
- execution policy
- decision envelope

The canonical flow is:

1. `build_feature_frame`
2. `build_decision_context`
3. `SignalPolicy`
4. `ExecutionPolicy`
5. `StrategyDecisionEnvelope`

Reference and decision-engine strategies may add adapter-specific behavior, but they must not bypass the
shared execution orchestration, risk checks, or run metadata model.

## Consequences

Positive:

- strategy families remain comparable
- NFI integration stays explicit
- LLM research can mature without breaking deterministic strategies
- execution sizing and exit behavior can evolve independently from signal logic

Negative:

- metadata normalization work increases
- some reference strategies will require adapter shims instead of direct reuse
- strategy implementations need a slightly richer contract than a typical single-method bot interface

## Implementation notes

- `StrategyMetadata.runtime` is the control field for lane selection
- `StrategyDecisionEnvelope` is expected to carry both signal and execution intent
- reference strategies remain benchmark lanes, not the main execution contract
- future work should avoid adding hidden runtime branches outside the strategy catalog or application layer
