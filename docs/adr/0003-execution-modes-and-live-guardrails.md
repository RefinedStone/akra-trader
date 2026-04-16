# ADR 0003: Execution Modes and Live Guardrails

## Status

Accepted

## Context

The roadmap includes backtest, paper, and controlled live trading. If these modes diverge too early, the system becomes difficult to reason about and risky to operate.

## Decision

The platform will keep a shared execution model across:

- backtest
- paper
- live

The differences between modes should be expressed in adapters and operational policies, not in separate domain models.

Live trading will be introduced only with mandatory guardrails:

- explicit account configuration
- exposure limits
- loss limits where available
- operator kill switch
- audit logging for all operator and system actions
- reconciliation on startup and after execution faults

## Consequences

Positive:

- behavior learned in backtest and paper can be promoted with less surprise
- live rollout is constrained and observable

Negative:

- live support requires more plumbing before the first order is sent
- paper mode must become more operationally serious

## Implementation notes

- live mode is not a free-form extension of paper mode
- every live order must pass through shared checks before adapter dispatch
- control-room surfaces must expose safety state, not just trading state
