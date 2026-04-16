# ADR 0005: Native Runtime Decomposition

## Status

Accepted

## Context

The initial native engine proved the strategy boundary and simulation loop, but too much orchestration
responsibility sat inside one application flow. At the same time, the long-term platform goals require:

- one shared execution model across backtest, sandbox, and live
- explicit risk review before execution
- restart-safe state and reconciliation
- adapter-level mode differences instead of domain-level forks

The NautilusTrader reference notes reinforce this direction by emphasizing a separated runtime made of
data, execution, risk, cache, and lifecycle concerns.

## Decision

The native runtime will be decomposed into explicit services with clear responsibilities:

- `DataEngine`
- `ExecutionEngine`
- `RiskEngine`
- `StateCache`
- `RunSupervisor`
- `ExecutionModeService`

The application layer remains the orchestrator, but it should delegate runtime responsibilities to these
services rather than owning the full simulation loop inline.

This decomposition is a platform-owned design. It is inspired by external references, but it does not
adopt external runtime types or framework internals.

## Consequences

Positive:

- runtime evolution toward sandbox and live becomes clearer
- risk and execution behavior can be tested independently
- state and reconciliation concerns gain a natural home
- future worker and stream adapters can plug into a more stable runtime core

Negative:

- more internal interfaces exist earlier than a minimal demo would require
- some logic moves out of a simple call stack into collaborating runtime services

## Implementation notes

- `RiskEngine` must review execution intent before order application
- `StateCache` owns current cash, position, and latest market snapshot within a run
- `RunSupervisor` owns status transitions and mode-specific lifecycle notes
- adapter differences belong around the runtime core, not inside domain models
