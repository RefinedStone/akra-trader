# Architecture

Updated for the repository state as of April 21, 2026.

## Core Rule

Domain and application code do not know about FastAPI, SQLAlchemy, ccxt, Freqtrade, or any
incident-delivery provider internals.

## Current System Shape

The repository is organized around a small set of stable boundaries:

- domain models and pure services
- application orchestration
- ports for external systems
- adapters for storage, market data, references, venue state, and operator delivery
- runtime services for execution flow, supervision, and mode handling

## Layers

### Domain

- market models such as candle, order, fill, position, trade, and run config
- strategy models such as metadata, lifecycle, decision context, execution plan, and decision
  envelope
- pure services for order application, equity generation, and performance summaries

### Application

- strategy listing and registration
- preset, comparison, rerun, and run-query orchestration
- sandbox worker supervision
- guarded-live kill switch, reconciliation, recovery, and incident orchestration
- operator visibility and delivery coordination

### Ports

- `MarketDataPort`
- `RunRepositoryPort`
- `GuardedLiveStatePort`
- `VenueStatePort`
- `StrategyCatalogPort`
- `DecisionEnginePort`
- `ReferenceCatalogPort`

## Runtime Core

The native runtime is already decomposed into explicit services:

- `DataEngine`
  - loads candles and market lineage through `MarketDataPort`
- `ExecutionEngine`
  - applies reviewed decisions to orders, fills, positions, and equity
- `RiskEngine`
  - validates execution intent and blocks invalid actions
- `StateCache`
  - tracks current cash, position, and marked price within a run
- `RunSupervisor`
  - owns run status transitions and mode notes
- `ExecutionModeService`
  - normalizes mode names and lifecycle notes across backtest, sandbox, paper, and live concepts

## Strategy Lanes

### Native lane

- executed fully by the platform runtime

### Reference lane

- catalog entries point at third-party strategy files under `reference/NostalgiaForInfinity`
- execution is delegated through an external Freqtrade command
- benchmark provenance is stored alongside native runs

### Decision-engine lane

- modeled behind `DecisionEnginePort`
- intentionally kept isolated until trace, replay, and fallback infrastructure exists

## Persistence And Provenance

Run persistence already stores:

- config and status
- metrics
- orders, fills, positions, and equity
- notes and audit-oriented provenance
- strategy snapshots and parameter snapshots
- market-data lineage, dataset identity fingerprints, and rerun boundaries

This is enough for durable research history and guarded-live control-plane state, but it is not yet
the final normalized experiment model.

## Execution Modes

### Backtest

- completes immediately and persists as a historical run

### Sandbox

- native worker session seeded from a priming window
- continues processing new candle closes
- persists heartbeat, processed-candle progress, and recovery history

### Paper

- separate mode and history bucket
- kept distinct from sandbox worker semantics

### Guarded live

- launch is blocked behind kill switch, reconciliation, recovery, and venue configuration gates
- venue-backed order submission exists
- cancel and replace controls exist
- live-session ownership, open-order snapshots, incidents, and audit-oriented control state are
  persisted separately from ordinary run history

## Market Data And Operator Surfaces

- ccxt-backed market-data adapters support Binance, Coinbase, and Kraken
- status surfaces already expose checkpoints, gaps, lag, backfill, and failure history
- operator visibility merges sandbox runtime health and guarded-live incident state
- incident delivery supports console, webhooks, Slack, and a large provider matrix

The detailed provider matrix lives outside this architecture document:

- [Operator Delivery Matrix](reference/operator-delivery-matrix.md)

## Main Architectural Pressure Points

- run persistence is still too payload-centric for some experiment and export paths
- custom strategy registration is not yet a durable registry
- the web control room is feature-rich but monolithic
- guarded-live venue lifecycle handling is partial rather than complete
- the intelligence lane is still only a contract and template layer
