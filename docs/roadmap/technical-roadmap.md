# Technical Roadmap

## Goal

The technical roadmap turns the current architecture into a durable platform without breaking the core boundary rule:

- domain and application code stay independent from frameworks, exchanges, storage engines, and LLM providers

## Current system baseline

The current implementation already fixes several important design choices:

- `StrategyRuntime` is split into feature-building, context-building, and decision steps
- `DecisionEnginePort` exists for external decision systems
- `MarketDataPort`, `RunRepositoryPort`, and `StrategyCatalogPort` define the main seams
- the application already supports native and reference runtime lanes

The main weaknesses are:

- in-memory persistence
- seeded data instead of venue-backed ingestion
- replay-only paper execution
- no long-running worker model
- no live execution adapter or safety controls
- no structured experiment metadata beyond the current run record

## Track A: Data Platform

### Target state

- market data is venue-backed, versionable, and auditable
- every run knows which data slice it used
- the platform can distinguish between data freshness problems and strategy problems

### Milestones

- Replace seeded market data with a Binance adapter behind `MarketDataPort`
- Store instruments, candle batches, ingestion jobs, and freshness metadata in Postgres
- Define resync, deduplication, and gap-detection rules
- Add data quality checks for empty series, broken timestamps, and missing bars
- Add background ingestion jobs for historical catch-up and recent updates

### Interface additions

- `MarketDataPort` should expand to cover write-side synchronization or a companion ingestion port
- API should expose ingestion lag, sync status, and recent failures

### Technical decisions to preserve

- execution services read via ports only
- strategies do not read raw exchange clients directly

## Track B: Experiment and Persistence Platform

### Target state

- all runs are durable
- all inputs are reproducible
- comparison across strategies and parameter sets is straightforward

### Milestones

- Replace `InMemoryRunRepository` with a Postgres-backed adapter
- Persist run config, metrics, notes, orders, fills, positions, and equity curve snapshots
- Add strategy version records and parameter snapshots
- Add run tags, scenario presets, and comparison queries
- Add artifact storage references for logs and serialized outputs

### Interface additions

- `RunRepositoryPort` will need query methods for comparisons, filtering, and strategy-version history
- API will need endpoints for run comparison, run tags, and result exports

### Technical decisions to preserve

- run storage remains an adapter concern
- run reproducibility metadata is stored at run creation time, not reconstructed later

## Track C: Strategy Platform

### Target state

- strategy runtime lanes are explicit and extensible
- native rules, NFI references, and LLM decision engines use one shared orchestration model

### Milestones

- Formalize strategy version lifecycle: draft, active, archived
- Normalize metadata between native and reference strategies
- Add trace schema for `StrategyDecisionEnvelope`
- Add scenario-aware context builders for multi-timeframe and venue-aware features
- Add prompt-driven decision engine research harness behind `DecisionEnginePort`

### Interface additions

- `StrategyMetadata` should gain lifecycle and promotion status
- `StrategyDecisionEnvelope` should gain normalized trace metadata for human and machine decisions
- `DecisionEnginePort` should support audit-friendly invocation metadata

### Technical decisions to preserve

- feature building and decision making remain separable
- LLM decisions do not bypass the shared execution pipeline
- reference strategies remain a distinct lane, not a hidden special case

## Track D: Real-Time Execution Platform

### Target state

- backtest, paper, and live modes share the same orchestration and state transition model
- differences between modes are adapter-level, not domain-level

### Milestones

- move from replay-only paper mode to long-running worker execution
- add market stream or timed polling infrastructure
- add order state machine support for real exchange responses
- add exchange reconciliation on startup and after failures
- add live execution adapter and safe promotion flow

### Interface additions

- execution mode separation should be represented in application services or new execution ports
- API should expose live account status, open orders, reconciliation state, and emergency stop actions

### Technical decisions to preserve

- live trading must use the same decision envelope and risk checks as paper mode
- operators can always force a safe stop

## Track E: Safety, Observability, and Operations

### Target state

- the operator can trust the system enough to diagnose issues without shelling into containers first

### Milestones

- structured logs for ingestion, execution, and strategy decisions
- alerts for stale data, worker failure, rejected orders, and risk breaches
- audit log for operator actions
- single-host deployment recipe with service healthchecks and restart policies
- runbook for incident response and daily operations

### Interface additions

- add operator event storage and alert endpoints
- expose health, lag, and status summary APIs for the control room

### Technical decisions to preserve

- observability data is part of the product, not an afterthought
- every live-affecting operator action is logged

## 6-Month technical exit criteria

At the end of the roadmap, the codebase should meet these technical checks:

- no core user flow depends on in-memory-only state
- real market data powers backtest, paper, and live lanes
- native, reference, and decision-engine strategies all fit the same strategy contract
- one exchange supports a guarded live path with reconciliation and auditability
- operational health and recent failures are visible through the platform UI and API
