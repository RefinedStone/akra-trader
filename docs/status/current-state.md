# Current State

Canonical status snapshot for the repository as of April 17, 2026.

Use this document as the source of truth for "what exists now" before reading roadmap or architecture docs.

Forward-looking planning lives under [Blueprint](../blueprint/README.md).

## Stage Summary

- Stage 0: complete
- Stage 1: largely complete
- Stage 2: partially complete
- Stage 3: early groundwork only
- Stage 4: not started in practice
- Stage 5: interface skeleton only

## Implemented Now

### Backend platform

- FastAPI backend with explicit domain, application, adapter, and runtime layers
- durable run storage through `SqlAlchemyRunRepository`
- repo-local SQLite defaults, with Postgres support through configuration
- run persistence for config, metrics, orders, fills, positions, notes, equity curve, and provenance payloads

### Market data

- Binance-backed `MarketDataPort` adapter
- tracked-symbol sync and historical backfill
- duplicate avoidance, lag tracking, and gap reporting
- background sync job started from the app lifespan when Binance is active
- seeded market-data adapter still available for tests and fixture-driven flows

### Strategy and execution

- native runtime lane
- Freqtrade reference runtime lane for NostalgiaForInfinity backtests
- decision-engine lane contract through `DecisionEnginePort`
- runtime decomposition into `DataEngine`, `ExecutionEngine`, `RiskEngine`, `StateCache`, `RunSupervisor`, and `ExecutionModeService`
- strategy snapshots and parameter snapshots stored in run provenance

### Research workflow

- backtest execution with durable run lookup
- supervised sandbox worker sessions and paper-session priming for native strategies
- run history listing and filtering by mode, strategy id, and strategy version
- run comparison API and control-room comparison UI
- native vs reference benchmark provenance and artifact display
- native run provenance carries dataset identity fingerprints for candle-backed inputs
- run provenance now links native runs to sync checkpoints and rerun boundary identities
- explicit rerun from stored rerun boundaries into backtest, sandbox, or paper execution with
  match-or-drift tracking
- guarded-live worker launch behind reconciliation, recovery, and configuration gates
- venue-backed guarded-live order submission with persisted live run history
- guarded-live worker order lifecycle sync for recovered/open venue orders, including partial-fill
  and fill progression in local run state
- guarded-live operator cancel/replace controls for active venue orders from the control room and API
- guarded-live control state now persists live session ownership and a durable open-order snapshot,
  and guarded-live resume now restores tracked venue order lifecycle state before falling back to
  the persisted snapshot after restart or fault drills
- guarded-live runtime now persists a venue session handoff with transport/session metadata so
  maintenance keeps following the same venue-owned lifecycle after resume, and Binance now uses a
  venue-push user-data websocket stream for that handoff

### Control room

- strategy catalog grouped by runtime lane
- reference catalog panel
- market-data status with backfill, contiguous-gap, sync checkpoint, and recent failure summaries
- launch forms for backtests and native sandbox worker sessions
- launch form for guarded-live workers once live gates are clear
- separate sandbox worker sessions and paper sessions with their own filters, stop controls, and rerun-boundary actions
- separate guarded-live run history with stop controls
- runtime alert and audit panel for stale sandbox heartbeats, worker failures, and recent runtime
  events
- guarded-live panel with persisted kill-switch state, candidacy blockers, reconciliation findings,
  venue-state verification snapshots, runtime recovery state restored from verified venue snapshots,
  live-owner visibility, venue-native session-restore state, durable order-book visibility,
  venue session handoff visibility, guarded-live resume controls, and guarded-live audit history
- side-by-side backtest comparison with narratives

## Partial or Fragile Areas

- sandbox runs are now supervised worker sessions that keep processing newly arrived candles with persisted heartbeat and restart recovery, while paper runs remain snapshot-primed sessions
- operator visibility is derived from runtime session state and run notes, but it is not yet a
  durable event store or notification channel
- guarded-live reconciliation and runtime recovery now depend on configured venue credentials, and
  recovery/live resume currently restores tracked venue order lifecycle state before falling back to
  persisted control-plane state, but it still does not revive broader venue-native stream or market
  session coverage beyond Binance user-data order events
- guarded-live order sync now persists lifecycle progression, a durable open-order snapshot, and
  session ownership for resume, but it still does not restore a full exchange session lifecycle
- custom strategy registration exists, but registration metadata is process-local rather than durable
- run persistence is durable, but the schema is still payload-centric and not yet optimized for rich experiment querying
- native run provenance now pins dataset identity and supports explicit rerun, but deterministic
  promotion gates and normalized rerun queries are not complete
- decision-engine support exists only as an interface and template strategy, not as a production research lane

## Not Implemented Yet

- durable operator event storage and external alert delivery
- operator alerts for risk breaches, live-path faults, and wider market-data freshness policies
- full live order lifecycle management beyond cancel/replace, including venue-native amend flows
- broader venue-native session continuation beyond Binance user-data order-event streaming
- live-worker restart recovery that resumes an actual venue-backed execution session lifecycle
- prompt versioning, raw trace persistence, and replay harness for LLM decisions

## Immediate Next Priorities

1. Harden reproducibility and dataset lineage so repeated runs can be proven equivalent.
2. Finish Stage 2 experiment workflow features such as durable strategy lifecycle, tags, presets, and richer exports.
3. Turn runtime-derived operator visibility into durable alert delivery and audit storage.
4. Expand guarded-live controls from Binance user-data stream continuation into wider live-path audit coverage and broader venue-native session management.
5. Keep the LLM lane isolated until trace storage, fallback, and replay tooling exist.
