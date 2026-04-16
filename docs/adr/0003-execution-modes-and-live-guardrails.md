# ADR 0003: Execution Modes, Sandbox Semantics, and Live Guardrails

## Status

Accepted

## Context

The roadmap includes backtest, sandbox, and controlled live trading. If these modes diverge too early,
the system becomes difficult to reason about and risky to operate.

## Decision

The platform will keep a shared execution model across:

- backtest
- sandbox
- live

The differences between modes should be expressed in adapters and operational policies, not in separate domain models.

`paper` remains a legacy alias for compatibility, but the platform's primary term for simulated
real-time execution is `sandbox`.

Live trading will be introduced only with mandatory guardrails:

- explicit account configuration
- exposure limits
- loss limits where available
- operator kill switch
- audit logging for all operator and system actions
- reconciliation on startup and after execution faults

## Consequences

Positive:

- behavior learned in backtest and sandbox can be promoted with less surprise
- live rollout is constrained and observable

Negative:

- live support requires more plumbing before the first order is sent
- sandbox mode must become more operationally serious

## Implementation notes

- live mode is not a free-form extension of sandbox mode
- every live order must pass through shared checks before adapter dispatch
- control-room surfaces must expose safety state, not just trading state
- reconciliation and restart behavior must be visible to operators before unattended live execution is
  considered
