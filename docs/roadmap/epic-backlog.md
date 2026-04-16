# Epic Backlog

This backlog is ordered by product leverage rather than implementation convenience.

## Epic 1: Persistent Run Repository

Priority:

- P0

Goal:

- replace the in-memory run repository with durable Postgres-backed storage

Why now:

- every other workflow depends on run history, reproducibility, and restart-safe state

Dependencies:

- database schema definition
- repository adapter design

Acceptance criteria:

- backtest and paper runs survive process restart
- run config, metrics, orders, fills, positions, and notes are persisted
- API endpoints continue to work without semantic regression

## Epic 2: Binance Market Data Ingestion

Priority:

- P0

Goal:

- replace seeded candles with real Binance data behind `MarketDataPort`

Why now:

- all meaningful backtesting and paper execution depends on real venue data

Dependencies:

- instrument metadata schema
- ingestion job model

Acceptance criteria:

- historical candles can be downloaded and incrementally refreshed
- duplicate and gap conditions are detected
- market-data status surfaces lag and sync failures

## Epic 3: Strategy Versioning and Experiment Metadata

Priority:

- P0

Goal:

- treat strategy runs as experiments with durable versioned inputs

Why now:

- comparison and LLM research become noisy without version discipline

Dependencies:

- persistent run storage

Acceptance criteria:

- every run stores strategy version, parameter snapshot, timeframe, venue, and symbol set
- strategies can be listed by version and lifecycle state
- UI and API can filter runs by strategy version

## Epic 4: Backtest Comparison Workflow

Priority:

- P1

Goal:

- add run comparison and benchmark workflows for native and NFI reference strategies

Why now:

- the platform must become better than one-off shell commands for research work

Dependencies:

- persistent run storage
- experiment metadata

Acceptance criteria:

- at least two runs can be compared side by side
- comparison includes total return, drawdown, win rate, trade count, and notes
- NFI reference runs appear as a separate runtime lane

## Epic 5: Continuous Paper Execution Worker

Priority:

- P1

Goal:

- convert the current replay-based paper mode into a continuous real-time worker system

Why now:

- paper mode is the bridge between research and guarded live trading

Dependencies:

- real market data ingestion
- persistent run storage

Acceptance criteria:

- paper workers can start, stop, recover, and report heartbeat
- positions, orders, fills, and recent decisions are visible in the UI
- stale data and worker failure trigger alerts

## Epic 6: Live Execution Guardrails

Priority:

- P1

Goal:

- enable first-exchange live execution with hard risk controls

Why now:

- live trading is a roadmap commitment, but it must arrive as a constrained lane

Dependencies:

- continuous paper worker
- secrets management
- account synchronization

Acceptance criteria:

- max exposure, kill switch, and operator stop actions are enforced
- live trading cannot be enabled without configured guardrails
- audit records exist for all live order attempts and operator actions

## Epic 7: Exchange Reconciliation and Audit Trail

Priority:

- P1

Goal:

- make live and paper operation restart-safe and diagnosable

Why now:

- without reconciliation, live trading becomes operationally brittle

Dependencies:

- live execution support
- durable storage

Acceptance criteria:

- the platform can reload open orders and positions after restart
- mismatches between local and exchange state are surfaced
- audit views exist for operator and system actions

## Epic 8: LLM Decision Engine Research Lane

Priority:

- P1

Goal:

- introduce a controlled path for LLM-based strategy decisions without weakening deterministic execution boundaries

Why now:

- strategy abstraction already supports this lane and the research value is high

Dependencies:

- strategy versioning
- trace storage
- reproducible historical context replay

Acceptance criteria:

- `DecisionEnginePort` calls can be recorded with prompt and response metadata
- LLM decisions can run in backtest and paper modes
- human-review or fallback behavior exists before any live promotion

## Epic 9: Control Room Upgrade

Priority:

- P2

Goal:

- turn the current dashboard into an operator-grade control room

Why now:

- the platform needs a single place to observe runs, alerts, lag, and strategy state

Dependencies:

- persistent run data
- paper worker
- alerting and health data

Acceptance criteria:

- the UI can show run health, recent alerts, ingestion lag, and decision traces
- the operator can inspect why a strategy acted, not just that it acted
- live safety state is visible from the same control room

## Epic 10: Documentation and Runbooks

Priority:

- P2

Goal:

- make system setup, operation, and incident handling explicit and repeatable

Why now:

- operational maturity and research repeatability both depend on documentation quality

Dependencies:

- stable service boundaries

Acceptance criteria:

- setup guide covers initial bootstrap and reference repo handling
- operator runbook covers paper and live procedures
- incident notes cover stale data, worker crash, and exchange mismatch scenarios
