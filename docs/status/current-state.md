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

- ccxt-backed `MarketDataPort` adapter for Binance, Coinbase, and Kraken
- tracked-symbol sync and historical backfill
- duplicate avoidance, lag tracking, and gap reporting
- background sync job started from the app lifespan when a supported ccxt provider is active
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
  venue-push multi-stream websocket transport for that handoff
- Binance push-session supervision now performs automatic listen-key failover and records broader
  account-position, balance-update, order-list, trade-tick, aggregate-trade, book-ticker,
  mini-ticker, depth, and kline coverage alongside execution events, full depth snapshot rebuilds,
  order-book resync state, rebuild counts, full recovered bid/ask levels, channel-restore
  timing/counts, channel-continuation timing/counts, persisted trade/aggregate-trade/book-ticker/
  mini-ticker/kline snapshots, and top-of-book levels. Durable incidents now split generic ladder
  gap/rebuild faults from venue-native ladder snapshot integrity faults such as crossed snapshots,
  missing sides, and non-monotonic snapshot ladders
- guarded-live handoff can now widen beyond Binance-native continuation into push-native multi-venue
  market transports, using Binance public market websockets, Coinbase Advanced Trade authenticated
  user/account order transport plus public heartbeats/ticker/trade/level2/candle channels, and
  Kraken spot public heartbeat/ticker/trade/book/ohlc channels while preserving continuation state
  and transport ownership metadata
- guarded-live reconciliation, recovery, and live launch now use a dedicated configured live venue
  instead of assuming the market-data provider, so supported venue-state and order-session wiring
  can target Binance, Coinbase, or Kraken independently of candle sourcing

### Control room

- strategy catalog grouped by runtime lane
- reference catalog panel
- market-data status with backfill, contiguous-gap, sync checkpoint, and recent failure summaries
- launch forms for backtests and native sandbox worker sessions
- launch form for guarded-live workers once live gates are clear
- separate sandbox worker sessions and paper sessions with their own filters, stop controls, and rerun-boundary actions
- separate guarded-live run history with stop controls
- runtime alert and audit panel for stale sandbox heartbeats, worker failures, guarded-live
  live-path alerts, persisted live-path alert history, durable incident events, outbound delivery
  history, and recent merged runtime/guarded-live events
- guarded-live panel with persisted kill-switch state, candidacy blockers, active guarded-live
  alerts, guarded-live alert history, durable incident events, outbound delivery history,
  reconciliation findings,
  venue-state verification snapshots, runtime recovery state restored from verified venue snapshots,
  live-owner visibility, venue-native session-restore state, durable order-book visibility,
  venue session handoff supervision/failover coverage plus market/depth/kline event visibility,
  order-book resync state, snapshot rebuild visibility, recovered bid/ask ladders, deeper channel
  restore visibility, persisted market-channel continuation visibility, top-of-book visibility,
  guarded-live resume controls, and guarded-live audit history
- outbound incident delivery can now fan out to console, generic webhook, Slack webhook,
  PagerDuty, and Opsgenie targets with persisted delivery-attempt history, attempt counts, and
  retry timing
- durable guarded-live incidents now persist acknowledgment state, escalation state, next
  escalation timing, operator actions for acknowledge/escalate workflows, and paging policy
  identity/provider selection
- durable guarded-live incidents now also persist external provider/reference state, provider
  workflow state/reference, external sync timestamps, and paging status from external callbacks
  plus local provider-native workflow actions
- durable guarded-live incident workflow now covers worker failure/staleness, risk breaches,
  repeated live recovery loops, stale active-order sync faults, and market-data freshness policy
  breaches such as stale sync, richer backfill-quality semantics, repeated sync failures, and
  venue-specific upstream fault classifications, plus guarded-live venue-session channel
  consistency, restore degradation, venue-specific book/kline consistency faults, exchange-specific
  ladder integrity faults, deeper depth-ladder/candle-sequence semantics, and multi-candle
  continuity faults, instead of only generic runtime control faults
- side-by-side backtest comparison with narratives

## Partial or Fragile Areas

- sandbox runs are now supervised worker sessions that keep processing newly arrived candles with persisted heartbeat and restart recovery, while paper runs remain snapshot-primed sessions
- operator visibility now persists guarded-live live-path alert history, durable incident events,
  and outbound delivery attempts with bounded retry/backoff state, but it is not yet a full
  external incident-management system
- incident workflow now includes operator acknowledgment, retry suppression, manual escalation, and
  auto escalation after ack-timeout or retry exhaustion, and incidents now carry a persisted paging
  policy id/provider plus provider-workflow state, but provider-managed policy ownership is still
  limited
- external paging workflows can now sync `triggered`, `acknowledged`, `escalated`, and `resolved`
  events back into local incident state, and local acknowledge/escalate actions can now push
  provider-native workflow updates back out, but the integration is still not a full
  provider-managed ownership workflow
- guarded-live reconciliation and runtime recovery now depend on configured venue credentials, and
  recovery/live resume currently restores tracked venue order lifecycle state before falling back to
  persisted control-plane state, but it still does not revive broader venue-native stream or market
  session coverage beyond Binance multi-stream
  account/order/trade/aggregate-trade/book-ticker/mini-ticker/depth/kline events plus exchange-backed
  ticker/trade/ohlcv restore, persisted market-channel continuation, and the current Binance/
  Coinbase authenticated user-plus-market continuation and Kraken push-market continuation layer
- guarded-live order sync now persists lifecycle progression, a durable open-order snapshot, and
  session ownership for resume, but it still does not restore a full exchange session lifecycle
- custom strategy registration exists, but registration metadata is process-local rather than durable
- run persistence is durable, but the schema is still payload-centric and not yet optimized for rich experiment querying
- native run provenance now pins dataset identity and supports explicit rerun, but deterministic
  promotion gates and normalized rerun queries are not complete
- decision-engine support exists only as an interface and template strategy, not as a production research lane

## Not Implemented Yet

- full external incident-management workflow such as provider-managed ownership beyond the current
  PagerDuty/Opsgenie-native bidirectional paths, richer escalation ladders, richer destinations,
  and more advanced retry policies
- operator alerts for wider market-data freshness policies and broader risk surfaces beyond the
  current guarded-live worker-failure, stale-runtime, market-data-freshness, risk-breach,
  recovery-loop, and stale order-sync coverage
- full live order lifecycle management beyond cancel/replace, including venue-native amend flows
- broader venue-native session continuation beyond Binance multi-stream
  account/order/trade/aggregate-trade/book-ticker/mini-ticker/depth/kline streaming and
  exchange-backed ticker/trade/ohlcv restore plus persisted market-channel continuation
- live-worker restart recovery that resumes an actual venue-backed execution session lifecycle
- prompt versioning, raw trace persistence, and replay harness for LLM decisions

## Immediate Next Priorities

1. Harden reproducibility and dataset lineage so repeated runs can be proven equivalent.
2. Finish Stage 2 experiment workflow features such as durable strategy lifecycle, tags, presets, and richer exports.
3. Expand operator delivery from the current console/webhook/Slack/PagerDuty/Opsgenie plus bidirectional provider workflow sync into richer multi-provider incident-management and wider audit coverage.
4. Expand guarded-live controls from the current Binance-plus-Coinbase-authenticated-plus-Kraken push-native session supervision into wider live-path audit coverage and broader venue-native session management.
5. Keep the LLM lane isolated until trace storage, fallback, and replay tooling exist.
