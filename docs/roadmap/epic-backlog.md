# Epic Backlog

This backlog starts after the foundations already present in the repository as of April 17, 2026.

Already in place:

- durable run storage
- Binance market-data ingestion baseline
- native vs reference comparison baseline

## Epic 1: Reproducibility and Dataset Lineage Hardening

Priority:

- P0

Goal:

- make every run point to a stable, auditable data identity instead of a best-effort lineage snapshot

Why now:

- Stage 1 is mostly complete, but reproducibility claims are still softer than the docs should allow

Acceptance criteria:

- runs store a stable dataset or sync-checkpoint identity
- repeated runs with identical inputs can be validated against the same data boundary
- lineage gaps are surfaced clearly when deterministic rerun guarantees cannot be made

## Epic 2: Experiment Metadata Completion

Priority:

- P0

Goal:

- finish the missing Stage 2 experiment workflow pieces

Why now:

- comparison exists, but experiment management is still incomplete

Acceptance criteria:

- run tags and scenario presets are durable
- core experiment filters do not require scanning full payloads for common queries
- exports or artifact references are consistent across native and reference runs

## Epic 3: Durable Strategy Lifecycle and Registration

Priority:

- P0

Goal:

- move strategy lifecycle and registration beyond the current process-local catalog behavior

Why now:

- strategy version metadata exists, but user-driven registration and promotion are not durable workflows yet

Acceptance criteria:

- strategy registrations survive restart
- lifecycle stages such as `draft`, `active`, and `archived` are queryable and enforceable
- control-room filtering can reflect durable lifecycle state

## Epic 4: Continuous Sandbox Worker

Priority:

- P1

Goal:

- replace replay-style sandbox semantics with a real continuous execution worker

Why now:

- the current sandbox label suggests a stronger operational mode than the implementation actually delivers

Acceptance criteria:

- workers can start, stop, recover, and report heartbeat
- worker state is stored separately from preview results
- positions, orders, fills, and recent decisions update through an active runtime path

## Epic 5: Alerts and Operator Events

Priority:

- P1

Goal:

- introduce the first operational surfaces required for trustworthy sandbox and live work

Why now:

- continuous operation is not credible without alerting and operator-visible failure state

Acceptance criteria:

- stale data, sync failures, and worker crashes generate visible alerts
- operator actions are stored as explicit events
- the UI can surface recent failures and acknowledgement state

## Epic 6: Live Execution Guardrails

Priority:

- P1

Goal:

- add a constrained live lane only after operator safety primitives exist

Why now:

- live execution is still entirely absent, but its prerequisites must be implemented in order

Acceptance criteria:

- live trading is blocked unless safety configuration exists
- kill-switch behavior is explicit
- risk limits are enforced before adapter dispatch

## Epic 7: Reconciliation and Audit Trail

Priority:

- P1

Goal:

- make sandbox and future live execution restart-safe and diagnosable

Why now:

- worker-based operation and live execution both depend on trustworthy restart behavior

Acceptance criteria:

- open orders and positions can be reloaded after restart
- mismatches between internal and exchange state are surfaced
- audit views exist for operator and system actions

## Epic 8: LLM Decision Research Lane

Priority:

- P1

Goal:

- turn the existing decision-engine contract into a traceable research lane

Why now:

- the abstraction is in place, but the research controls are not

Acceptance criteria:

- prompt versions, raw responses, and normalized traces are stored
- historical replay can evaluate decision-engine behavior
- fallback or operator review is mandatory before any promotion

## Epic 9: Control Room Operations Upgrade

Priority:

- P2

Goal:

- turn the current research UI into an operator-grade operations surface

Why now:

- the current control room is useful, but it still centers on inspection over operations

Acceptance criteria:

- worker health, alerts, lag, and recent decisions are visible together
- positions, orders, and fills are easier to inspect during active execution
- live safety state can share the same control room without ambiguity

## Epic 10: Documentation and Runbooks

Priority:

- P2

Goal:

- keep docs aligned with implementation and make daily operation explicit

Why now:

- stale docs already distorted the perceived progress of the project once

Acceptance criteria:

- current-state docs stay aligned with implementation
- setup guides cover data sync, persistence, and reference runtime handling
- operator runbooks cover sandbox incidents, stale data, and reconciliation issues
