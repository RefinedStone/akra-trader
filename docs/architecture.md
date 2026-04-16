# Architecture

## Core Rule

Domain and application code do not know about FastAPI, SQLAlchemy, ccxt, or Freqtrade internals.

## Current System Shape

The repository is organized around a small set of stable boundaries:

- domain models and pure services
- application orchestration
- ports for external systems
- adapters for storage, market data, references, and external runtimes
- runtime services for execution flow and mode handling

## Layers

### Domain

- market models such as instrument, candle, order, fill, position, trade, and run config
- strategy models such as metadata, lifecycle, decision context, execution plan, and decision envelope
- pure services for order application, equity generation, and performance summaries

### Application

- strategy listing and registration
- backtest orchestration
- supervised sandbox worker-session orchestration
- guarded-live worker orchestration behind kill-switch, reconciliation, and recovery gates
- run lookup, listing, filtering, and comparison
- market-data status queries
- operator visibility queries for runtime alerts and audit events
- guarded-live kill-switch, reconciliation, recovery, and live execution orchestration

### Ports

- `MarketDataPort`
- `RunRepositoryPort`
- `GuardedLiveStatePort`
- `VenueStatePort`
- `StrategyCatalogPort`
- `DecisionEnginePort`
- `ReferenceCatalogPort`

## Runtime Core

The native runtime is already split into explicit services:

- `DataEngine`
  - loads candles through `MarketDataPort`
  - builds aggregated market-data lineage for the run
- `ExecutionEngine`
  - applies reviewed decisions to orders, fills, positions, and equity
- `RiskEngine`
  - normalizes execution intent and blocks invalid actions
- `StateCache`
  - tracks current cash, position, and marked price within the run
- `RunSupervisor`
  - owns run status transitions and mode notes
- `ExecutionModeService`
  - normalizes user-facing mode names and keeps shared lifecycle notes around execution modes

## Strategy Abstraction

The strategy boundary is split on purpose.

Canonical flow:

1. `build_feature_frame`
2. `build_decision_context`
3. signal policy
4. execution policy
5. `StrategyDecisionEnvelope`

This keeps feature engineering, decision logic, execution intent, and provenance aligned across lanes.

## Strategy Lanes

### Native

- executed fully by the platform runtime
- current built-in example: `ma_cross_v1`

### Freqtrade reference

- catalog entries point at files under `reference/NostalgiaForInfinity`
- backtest execution is delegated through a Freqtrade command
- run provenance stores reference metadata, command, and benchmark artifacts
- sandbox and live execution are intentionally unsupported for this lane today

### Decision engine

- modeled behind `DecisionEnginePort`
- intended for future LLM-assisted or external policy research
- current repository state includes the contract and a template strategy, but not the full traceable research stack

## Persistence and Provenance

Run persistence is durable today.

- `SqlAlchemyRunRepository` stores run payloads in a relational table
- every persisted run carries config, status, metrics, orders, fills, positions, equity, notes, and provenance
- provenance can include:
  - strategy snapshot and parameter snapshot
  - market-data lineage with dataset identity, sync checkpoint links, and reproducibility state
  - rerun boundary identity for the exact execution input bundle
  - reference id and integration mode
  - external command and artifact paths
  - benchmark artifact summaries

This is enough for restart-safe history, comparison, and stable dataset-boundary inspection, but not
yet the final analytics-friendly schema.

Stored rerun boundaries can also be used to launch explicit backtest reruns or sandbox/paper
execution. Sandbox and paper now persist as separate execution modes. Sandbox reruns restore a
supervised worker session with the stored priming window, while paper sessions remain snapshot
priming flows. The rerun records the source run, the target boundary, and whether the new
execution still matched that boundary.

## Market Data

Two adapters exist today:

- `SeededMarketDataAdapter`
  - used for tests and deterministic fixture flows
- `BinanceMarketDataAdapter`
  - backed by ccxt and local SQL storage
  - tracks sync status, lag, backfill progress, gap windows, last successful sync checkpoint,
    and recent sync failure history

The API app lifespan always starts a sandbox worker maintenance job that heartbeats running worker
sessions and applies restart recovery. When Binance is enabled, the app also starts a
`MarketDataSyncJob` that periodically refreshes tracked symbols.

The application also derives operator visibility from sandbox runtime state. Failed worker sessions
and stale heartbeats surface as control-room alerts, and worker lifecycle notes are normalized into
recent audit events for operator review.

Guarded-live control state is persisted separately from run history. That state currently tracks a
kill switch for operator-controlled runtime sessions, reconciliation results that now include
internal runtime exposure plus venue balance/open-order snapshots, persisted runtime recovery
projections rebuilt from verified venue snapshots, and a guarded-live audit log of operator
actions. A separate venue execution adapter now submits guarded-live market orders once those gates
are clear, and the guarded-live worker now syncs tracked venue order lifecycle changes back into
local orders, fills, positions, and audit notes. Operator controls can now cancel active venue
orders or replace them with repriced limit orders from persisted live run state.

## Modes

### Backtest

- full native run to completion
- persisted as a completed run

### Sandbox

- current implementation starts a native worker session from a bounded priming window
- native-only today
- worker cycles keep consuming new candle closes after priming and persist processed-tick progress
- persisted runtime session state includes heartbeat cadence, last heartbeat, processed candle state,
  and recovery history
- stoppable through the API and control room

### Live

- guarded-live worker sessions are now available for native strategies
- launch is blocked until kill switch, reconciliation, recovery, and venue-execution gates are clear
- the current live order path submits venue market orders, then keeps syncing open and partially
  filled venue orders into persisted run/session history
- operator controls can cancel active venue orders and replace them with repriced limit orders

## Control Room

The web app currently surfaces:

- strategy catalog by runtime lane
- reference catalog
- market-data health and backfill quality
- backtest launch
- sandbox worker launch, stop, and rerun restore
- guarded-live worker launch, stop, and run history
- guarded-live order cancel/replace controls for active venue orders
- runtime alerts and audit visibility for sandbox worker failures and stale sessions
- guarded-live kill switch, candidacy blockers, venue-state verification snapshots, reconciliation findings, and guarded-live audit history
- run history
- run comparison and benchmark narratives

The UI is already useful for research inspection, but not yet an operator-grade surface for live or continuous execution.

## Known Limits

- guarded-live worker execution exists, but it is still limited to a narrow market-entry path
- runtime alerts and audit visibility exist only for sandbox worker failures and stale sessions, and
  guarded-live recovery/live launch still stop short of a full venue order-book restore or durable
  live worker resume
- the system still lacks durable alert delivery and wider operator event coverage
- venue order lifecycle management is still limited beyond cancel/replace: no durable venue-order-book sync
- no durable custom strategy registration history
- no provider-backed LLM decision lane yet
