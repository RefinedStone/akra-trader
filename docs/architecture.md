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
- replay-based sandbox orchestration
- run lookup, listing, filtering, and comparison
- market-data status queries

### Ports

- `MarketDataPort`
- `RunRepositoryPort`
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
  - normalizes mode naming such as the `paper` alias for `sandbox`

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

Stored rerun boundaries can also be used to launch explicit backtest reruns. The rerun records the
source run, the target boundary, and whether the new execution still matched that boundary.

## Market Data

Two adapters exist today:

- `SeededMarketDataAdapter`
  - used for tests and deterministic fixture flows
- `BinanceMarketDataAdapter`
  - backed by ccxt and local SQL storage
  - tracks sync status, lag, backfill progress, gap windows, last successful sync checkpoint,
    and recent sync failure history

When Binance is enabled, the API app lifespan starts a `MarketDataSyncJob` that periodically refreshes tracked symbols.

## Modes

### Backtest

- full native run to completion
- persisted as a completed run

### Sandbox

- current implementation is a replay-based preview of recent bars
- native-only today
- marked as `running` for compatibility with a future long-running worker model
- stoppable through the API and control room

### Live

- represented in the domain model
- reserved for guarded future implementation

## Control Room

The web app currently surfaces:

- strategy catalog by runtime lane
- reference catalog
- market-data health and backfill quality
- backtest launch
- sandbox launch and stop
- run history
- run comparison and benchmark narratives

The UI is already useful for research inspection, but not yet an operator-grade surface for live or continuous execution.

## Known Limits

- no continuous execution worker yet
- no alerts, audit trail, or reconciliation flows
- no durable custom strategy registration history
- no provider-backed LLM decision lane yet
