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
- `CcxtMarketDataAdapter` for Binance, Coinbase, and Kraken
  - backed by ccxt and local SQL storage
  - tracks sync status, lag, backfill progress, gap windows, last successful sync checkpoint,
    and recent sync failure history

The API app lifespan always starts a sandbox worker maintenance job that heartbeats running worker
sessions and applies restart recovery. When a supported ccxt market-data provider is enabled, the
app also starts a `MarketDataSyncJob` that periodically refreshes tracked symbols.

The application also derives operator visibility from runtime state across sandbox and guarded-live
flows. Failed worker sessions and stale heartbeats surface as control-room alerts, guarded-live
control/session faults plus guarded-live risk breaches, repeated recovery loops, stale order
sync, and market-data freshness faults from stale sync, richer backfill-quality semantics, gap
windows, repeated sync failures, and venue-specific upstream fault classifications now persist as
live-path alert history with active/resolved lifecycle state and delivery targets. Guarded-live
venue-session coverage now also promotes channel-level depth/order-book continuity gaps, stale
market-channel timestamps, channel-restore failures, and venue-specific book/kline consistency
faults, exchange-specific ladder gap/rebuild faults, venue-native ladder snapshot integrity
faults, deeper depth-ladder/candle-sequence semantics, and multi-candle continuity faults into the
same durable incident surface. Alert transitions now emit durable incident-opened/resolved events
plus outbound delivery attempt history, failed deliveries now carry retry scheduling state through
attempt numbers plus bounded exponential backoff timestamps, durable incidents now also carry
acknowledgment, escalation, and external paging-sync state, and worker lifecycle notes plus
guarded-live control events are normalized into recent audit events for operator review.

Guarded-live control state is persisted separately from run history. That state currently tracks a
kill switch for operator-controlled runtime sessions, reconciliation results that now include
internal runtime exposure plus venue balance/open-order snapshots, persisted runtime recovery
projections rebuilt from verified venue snapshots, and a guarded-live audit log of operator
actions. It also keeps durable guarded-live session ownership plus a persisted open-order snapshot
for the current live owner. A separate venue execution adapter now submits guarded-live market
orders once those gates are clear, and the guarded-live worker now syncs tracked venue order
lifecycle changes back into local orders, fills, positions, and audit notes. Operator controls can
cancel active venue orders or replace them with repriced limit orders from persisted live run
state, and the guarded-live resume flow now restores tracked venue order lifecycle state before it
falls back to the persisted snapshot after restart or fault drills. The live worker also persists a
venue session handoff backed by the Binance multi-stream websocket transport so subsequent
maintenance cycles can continue against the same venue-owned session lifecycle instead of dropping
back to a one-shot restore. That handoff is now supervised: if the stream drops, the adapter
rotates to a fresh listen key and keeps session metadata on failover count plus observed
account/balance/order-list/trade/aggregate-trade/book-ticker/mini-ticker/depth/kline coverage,
order-book resync state, full depth snapshot rebuilds, full recovered bid/ask levels, deeper
channel restore state from exchange ticker/trade/ohlcv snapshots, persisted market-channel
continuation snapshots for trade/aggregate-trade/book-ticker/mini-ticker/kline state, and
top-of-book levels. When Binance user-data streaming is unavailable, the guarded-live adapter can
  continue on Binance's public market websocket, and the same handoff model now supports Coinbase
  Advanced Trade authenticated user/account order transport plus public market channels, alongside
  Kraken spot public market channels, so multi-venue push-native continuation persists with
  explicit transport ownership metadata.
  Guarded-live reconciliation, recovery, and launch wiring also now resolve a dedicated configured
  live venue instead of inheriting the market-data provider, which lets supported venue-state and
  order-session adapters run against Binance, Coinbase, or Kraken while candle reads stay on a
  separate market-data source.
  Incident delivery is handled behind a dedicated delivery port that can currently fan out to
  console logging, generic webhooks, Slack incoming webhooks, PagerDuty Events API targets, and
  Opsgenie Alert API targets, while the application layer owns acknowledgment, escalation timing, retry suppression, and
  phase-aware retry/backoff rules. Durable incidents now also persist paging policy identity plus
  provider workflow state/action/reference. External incident-management systems can sync paging
  events back through a guarded API endpoint, and local acknowledge/escalate actions can push
  provider-native workflow updates back out when the selected provider supports them, so durable
  incidents track a bidirectional paging workflow without handing local alert truth over to the
  external system.

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
- guarded-live control state persists live session ownership and a durable open-order snapshot so a
  guarded-live resume action can recover the owned live session from venue-native order lifecycle
  state after restart or fault drills
- guarded-live maintenance now follows a persisted venue session handoff with transport/session
  metadata once a live session has been resumed or relaunched, and Binance uses a multi-stream
  websocket transport instead of the earlier restore-and-poll bridge
- Binance push-session supervision now covers execution, account-position, balance-update, and
  order-list events plus trade/aggregate-trade/book-ticker/mini-ticker/depth/kline market
  transport, with automatic listen-key failover when the websocket drops, full depth snapshot
  rebuilds when order-book continuity breaks, persisted recovered bid/ask levels for restart
  recovery, exchange-snapshot channel restore for ticker/trade/ohlcv state, and persisted market
  channel continuation snapshots for broader restart continuity
- guarded-live can now widen beyond the Binance-native stream into push-native market transports,
  using Binance public market websockets, Coinbase Advanced Trade authenticated user/order
  websockets plus public heartbeats/ticker/trade/level2/candles, or Kraken spot public
  heartbeat/ticker/trade/book/ohlc streams while preserving venue transport ownership and
  continuation state across handoff and sync
- guarded-live reconciliation and live launch now follow a dedicated configured venue so supported
  venue-state/account session transport no longer has to match the market-data provider

## Control Room

The web app currently surfaces:

- strategy catalog by runtime lane
- reference catalog
- market-data health and backfill quality
- backtest launch
- sandbox worker launch, stop, and rerun restore
- guarded-live worker launch, stop, and run history
- guarded-live order cancel/replace controls for active venue orders
- guarded-live live-owner visibility, durable order-book state, and explicit resume control
- guarded-live venue session handoff state, websocket transport, cursor, failover health, and
  last account/balance/order-list/market/depth/kline event visibility plus order-book resync,
  rebuild, recovered bid/ask ladders, channel-restore visibility, persisted market-channel
  continuation visibility, and top-of-book supervision
- runtime alerts and audit visibility for sandbox worker failures, stale sessions, guarded-live
  live-path alerts, persisted live-path alert history, durable incident events, and outbound
  delivery history
- guarded-live kill switch, candidacy blockers, guarded-live alert history, venue-state
  verification snapshots, reconciliation findings, durable incident events, outbound delivery
  history, guarded-live incident acknowledgment/escalation actions, external paging-sync state,
  and guarded-live audit history
- run history
- run comparison and benchmark narratives

The UI is already useful for research inspection and early incident operations, but not yet a full
operator-grade surface for live or continuous execution.

## Known Limits

- guarded-live worker execution exists, but it is still limited to a narrow market-entry path
- runtime alerts and audit visibility exist only for sandbox worker failures and stale sessions, and
  guarded-live recovery/live resume still stop short of broader venue-native stream coverage beyond
  Binance multi-stream account/order/trade/aggregate-trade/book-ticker/mini-ticker/depth/kline
  session coverage plus exchange-backed ticker/trade/ohlcv restore, persisted market-channel
  continuation, Binance/Coinbase push-market continuation, and order lifecycle supervision
- the system still lacks richer provider-native incident-management coverage, richer escalation
  ladders, and wider operator event coverage
- venue order lifecycle management is still limited beyond cancel/replace: no venue-native amend
  flow and no full exchange-order restore
- no durable custom strategy registration history
- no provider-backed LLM decision lane yet
