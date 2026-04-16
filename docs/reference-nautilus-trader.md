# NautilusTrader Reference Notes

## Summary

- Source checkout: `reference/nautilus_trader/nautilus_trader`
- License: `LGPL-3.0`
- Role in `akra-trader`: architecture and runtime-boundary reference, not an immediate core dependency

NautilusTrader is useful to us mainly because it keeps research, simulation, and live execution inside
one event-driven system while still separating strategy logic from execution, risk, and data engines.
That separation matches the direction we want for `akra-trader`, especially once sandbox/live execution
and reconciliation become first-class.

## What To Borrow

### Environment contexts

The most immediately reusable idea is the explicit runtime split:

- `backtest`
- `sandbox`
- `live`

Our native engine now exposes `sandbox` as the primary simulated real-time mode, with `paper` retained
only as a legacy alias. The Nautilus model is still the better long-term shape because it keeps
real-time simulated execution and real live execution as separate environments with a shared core.

### Engine boundaries

Nautilus makes the following components explicit:

- `MessageBus`
- `Cache`
- `DataEngine`
- `ExecutionEngine`
- `RiskEngine`
- `Kernel`

We should not copy these classes, but we should mirror the decomposition. For `akra-trader`, the
practical mapping is:

- `MarketDataPort` + ingestion/replay workers -> `DataEngine`
- order application + fill handling -> `ExecutionEngine`
- risk checks and exposure caps -> `RiskEngine`
- run state / positions / latest market snapshot -> `StateCache`
- application bootstrap -> `Kernel`

### Reconciliation and restart

Nautilus is strong on fail-fast behavior, externalized state, restartability, and reconciliation with
venue state. These are relevant once we add continuous sandbox/live workers. The main idea to adopt is
that open orders, positions, and account state should be recoverable and comparable against external
truth after restart.

### Strategy/event model

Nautilus strategies are event-driven and can react to market data, orders, positions, timers, and state
transitions. We do not need that exact actor model today, but it is a useful target when our native
strategies move beyond bar-based replay into live streams and operator-controlled execution.

## What To Use Carefully

### Execution algorithms

Nautilus has a distinct execution-algorithm layer such as TWAP. That is a good model for us, but not a
first implementation target. The useful abstraction is "signal generation is not the same thing as order
execution policy." We have started reflecting that by separating `SignalPolicy` and `ExecutionPlan`.

### OMS and reconciliation

Nautilus explicitly models `NETTING` vs `HEDGING` OMS behavior. We should adopt that concept before
adding multi-position or futures support, but we do not need the full matrix yet. Our current native
engine is effectively a simple netting model.

## What Not To Do

- Do not vendor Nautilus core code into `akra-trader`.
- Do not let Nautilus types leak into our domain models.
- Do not adopt the Rust/Cython runtime just because it is more advanced; only use it if we have a clear
  sidecar or dependency boundary.
- Do not skip our own `StrategyRuntime`, `DecisionEnginePort`, and repository ports in favor of direct
  framework coupling.

## Acceptable Integration Paths

### Ideas only

This is the current default. We inspect the local checkout and copy architectural decisions:

- environment naming
- engine decomposition
- reconciliation patterns
- restart behavior
- risk placement

### Experimental sidecar

If we later want to compare execution semantics or live runtime behavior, Nautilus should be isolated as
an experimental lane or sidecar process. `akra-trader` remains the owner of domain types, run metadata,
and operator-facing APIs.

### Direct dependency

This should be treated as a later-stage option only after we prove an actual need. The burden is not
just technical; it would also change how we package, test, and reason about the runtime.

## Immediate Actions For `akra-trader`

- Keep Nautilus in the `reference` catalog as `ideas_only`.
- Continue refactoring our native engine toward `DataEngine`, `ExecutionEngine`, `RiskEngine`, and
  `StateCache`.
- Keep `sandbox` as the primary simulated execution mode and retire `paper` as a user-facing term over time.
- Add reconciliation and restart semantics before enabling guarded live trading.
