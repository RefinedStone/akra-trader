# Akra Trader API

FastAPI backend for strategy cataloging, market-data access, durable run storage, native backtests, supervised sandbox worker sessions, paper-session priming, and external reference backtest delegation.

## Current Scope

Implemented now:

- strategy catalog with native and reference lanes
- in-process custom strategy registration endpoint
- durable run storage through SQLAlchemy
- backtest execution and run lookup
- supervised sandbox worker sessions and paper-session priming for native strategies
- native vs reference run comparison API
- dataset identity and reproducibility state recorded in run market-data provenance
- ccxt-backed market data for Binance, Coinbase, and Kraken with sync, backfill, gap detection,
  sync checkpoints, failure history, and status reporting
- run provenance exposes rerun boundary identities, supports rerun-boundary filtering, and can
  relaunch stored boundaries into backtest, sandbox, or paper flows
- operator visibility endpoint exposes sandbox worker failure alerts, stale runtime alerts,
  guarded-live live-path alerts including risk breaches, repeated runtime recovery loops, stale
  live order sync, market-data freshness/quality/venue-policy breaches, persisted live-path alert
  history, durable incident events, outbound delivery history, and merged runtime plus
  guarded-live audit events
- guarded-live state endpoints persist kill-switch state, reconciliation status, live-path alert
  history, durable incident events, outbound delivery history, and guarded-live audit events in the
  control plane
- guarded-live reconciliation records venue-state snapshots and compares them against local runtime
  exposure before live candidacy discussion
- guarded-live runtime recovery can rebuild persisted runtime exposure and open-order state from the
  latest verified venue snapshot after a restart or fault drill
- guarded-live live-worker sessions can start behind reconciliation, recovery, and configuration
  gates, then submit venue market orders through a dedicated execution adapter
- guarded-live workers now sync tracked venue order lifecycle state back into persisted orders,
  fills, positions, and audit notes
- guarded-live operator actions can now cancel active venue orders or replace them with repriced
  limit orders from stored live run state
- guarded-live control state now persists live session ownership and a durable open-order snapshot,
  and guarded-live resume now restores the owned live run from venue-native order lifecycle state
  before falling back to the persisted snapshot
- guarded-live live workers now keep an explicit venue session handoff backed by the Binance
  multi-stream websocket session so maintenance can continue through the same venue-owned lifecycle
  after resume
- Binance guarded-live session supervision now fails over to a fresh listen-key stream when the
  venue session drops, and the control plane tracks broader stream coverage across execution,
  account-position, balance-update, order-list, trade-tick, aggregate-trade, book-ticker,
  mini-ticker, depth, and kline events while rebuilding a local book from full depth snapshots and
  recording order-book resync state, rebuild counts, full recovered bid/ask levels, and
  deeper-channel restore state from exchange ticker/trade/ohlcv snapshots plus persisted channel
  continuation snapshots for trade, aggregate-trade, book-ticker, mini-ticker, and kline state
- guarded-live session handoff can now widen beyond Binance-native continuation into push-native
  market transports: Binance falls back to its public market websocket when user-data auth is not
  available, Coinbase Advanced Trade can now supply authenticated user/account order transport plus
  public heartbeat/ticker/trade/level2/candle continuation, and Kraken spot can supply public
  heartbeat/ticker/trade/book/ohlc continuation through the same handoff surface
- guarded-live incident delivery now supports console, generic webhook, Slack webhook, PagerDuty
  Events API, and Opsgenie Alert API targets with persisted attempt history, operator
  acknowledgment, manual/automatic escalation, and retry/backoff scheduling
- durable incidents now persist paging policy selection, provider workflow state/reference, and
  can sync provider callbacks plus local provider-native workflow actions bidirectionally through
  the operator incident sync endpoint and guarded-live acknowledge/escalate actions
- guarded-live launch wiring and venue-state reconciliation can now target a configured supported
  venue independently from the market-data provider, while seeded fixture flows still default to a
  Binance-shaped live venue in tests
- reference catalog and Freqtrade-backed NFI backtest delegation

Not implemented yet:

- richer venue order management beyond cancel/replace, including venue-native amend flows
- full external incident-management workflow such as provider-managed incident ownership beyond the
  current PagerDuty/Opsgenie-native bidirectional paths, richer escalation ladders, and broader
  paging policy management
- durable custom strategy registration lifecycle
- concrete LLM provider adapters

## Run

```bash
python3 -m pip install -e ".[dev]"
uvicorn akra_trader.main:app --reload
```

Useful environment variables:

- `AKRA_TRADER_CORS_ORIGIN`
- `AKRA_TRADER_MARKET_DATA_PROVIDER`
- `AKRA_TRADER_RUNS_DATABASE_URL`
- `AKRA_TRADER_MARKET_DATA_DATABASE_URL`
- `AKRA_TRADER_MARKET_DATA_SYMBOLS`
- `AKRA_TRADER_MARKET_DATA_SYNC_TIMEFRAMES`
- `AKRA_TRADER_MARKET_DATA_SYNC_INTERVAL_SECONDS`
- `AKRA_TRADER_SANDBOX_WORKER_HEARTBEAT_INTERVAL_SECONDS`
- `AKRA_TRADER_SANDBOX_WORKER_HEARTBEAT_TIMEOUT_SECONDS`
- `AKRA_TRADER_GUARDED_LIVE_EXECUTION_ENABLED`
- `AKRA_TRADER_GUARDED_LIVE_VENUE`
- `AKRA_TRADER_GUARDED_LIVE_WORKER_HEARTBEAT_INTERVAL_SECONDS`
- `AKRA_TRADER_GUARDED_LIVE_WORKER_HEARTBEAT_TIMEOUT_SECONDS`
- `AKRA_TRADER_OPERATOR_ALERT_DELIVERY_TARGETS`
- `AKRA_TRADER_OPERATOR_ALERT_WEBHOOK_URL`
- `AKRA_TRADER_OPERATOR_ALERT_WEBHOOK_TIMEOUT_SECONDS`
- `AKRA_TRADER_OPERATOR_ALERT_SLACK_WEBHOOK_URL`
- `AKRA_TRADER_OPERATOR_ALERT_PAGERDUTY_INTEGRATION_KEY`
- `AKRA_TRADER_OPERATOR_ALERT_PAGERDUTY_API_TOKEN`
- `AKRA_TRADER_OPERATOR_ALERT_PAGERDUTY_FROM_EMAIL`
- `AKRA_TRADER_OPERATOR_ALERT_OPSGENIE_API_KEY`
- `AKRA_TRADER_OPERATOR_ALERT_OPSGENIE_API_URL`
- `AKRA_TRADER_OPERATOR_ALERT_DELIVERY_MAX_ATTEMPTS`
- `AKRA_TRADER_OPERATOR_ALERT_DELIVERY_INITIAL_BACKOFF_SECONDS`
- `AKRA_TRADER_OPERATOR_ALERT_DELIVERY_MAX_BACKOFF_SECONDS`
- `AKRA_TRADER_OPERATOR_ALERT_DELIVERY_BACKOFF_MULTIPLIER`
- `AKRA_TRADER_OPERATOR_ALERT_PAGING_POLICY_DEFAULT_PROVIDER`
- `AKRA_TRADER_OPERATOR_ALERT_PAGING_POLICY_WARNING_TARGETS`
- `AKRA_TRADER_OPERATOR_ALERT_PAGING_POLICY_CRITICAL_TARGETS`
- `AKRA_TRADER_OPERATOR_ALERT_PAGING_POLICY_WARNING_ESCALATION_TARGETS`
- `AKRA_TRADER_OPERATOR_ALERT_PAGING_POLICY_CRITICAL_ESCALATION_TARGETS`
- `AKRA_TRADER_OPERATOR_ALERT_EXTERNAL_SYNC_TOKEN`
- `AKRA_TRADER_OPERATOR_ALERT_ESCALATION_TARGETS`
- `AKRA_TRADER_OPERATOR_ALERT_INCIDENT_ACK_TIMEOUT_SECONDS`
- `AKRA_TRADER_OPERATOR_ALERT_INCIDENT_MAX_ESCALATIONS`
- `AKRA_TRADER_OPERATOR_ALERT_INCIDENT_ESCALATION_BACKOFF_MULTIPLIER`
- `AKRA_TRADER_GUARDED_LIVE_API_KEY`
- `AKRA_TRADER_GUARDED_LIVE_API_SECRET`
- `AKRA_TRADER_BINANCE_API_KEY`
- `AKRA_TRADER_BINANCE_API_SECRET`

Defaults:

- market-data provider: `binance`
- run database: repo-local SQLite if not overridden
- market-data database: repo-local SQLite if not overridden

## Main Endpoints

- `GET /api/health`
- `GET /api/strategies`
- `POST /api/strategies/register`
- `GET /api/references`
- `GET /api/runs`
- `GET /api/runs/compare`
- `POST /api/runs/backtests`
- `GET /api/runs/backtests/{run_id}`
- `POST /api/runs/rerun-boundaries/{rerun_boundary_id}/backtests`
- `POST /api/runs/rerun-boundaries/{rerun_boundary_id}/sandbox`
- `POST /api/runs/rerun-boundaries/{rerun_boundary_id}/paper`
- `POST /api/runs/sandbox`
- `POST /api/runs/sandbox/{run_id}/stop`
- `POST /api/runs/paper`
- `POST /api/runs/paper/{run_id}/stop`
- `POST /api/runs/live`
- `POST /api/runs/live/{run_id}/stop`
- `POST /api/runs/live/{run_id}/orders/{order_id}/cancel`
- `POST /api/runs/live/{run_id}/orders/{order_id}/replace`
- `GET /api/runs/{run_id}/orders`
- `GET /api/runs/{run_id}/positions`
- `GET /api/runs/{run_id}/metrics`
- `GET /api/market-data/status`
- `GET /api/operator/visibility`
- `POST /api/operator/incidents/external-sync`
- `GET /api/guarded-live`
- `POST /api/guarded-live/kill-switch/engage`
- `POST /api/guarded-live/kill-switch/release`
- `POST /api/guarded-live/reconciliation`
- `POST /api/guarded-live/recovery`
- `POST /api/guarded-live/incidents/{event_id}/acknowledge`
- `POST /api/guarded-live/incidents/{event_id}/escalate`
- `POST /api/guarded-live/resume`

## Runtime Notes

- backtests run to completion and are persisted immediately
- native candle-backed runs persist dataset identity fingerprints for the exact candles used
- stored rerun boundaries can launch explicit backtest, sandbox, and paper reruns with
  match-or-drift notes
- sandbox worker sessions and paper sessions now persist as separate modes, so history and filters no
  longer share the same storage bucket
- sandbox runs now start as native worker sessions, then continuously apply new candle ticks with
  persisted heartbeat and recovery state
- operator visibility now surfaces stale sandbox heartbeats, worker failures, guarded-live
  live-path alerts, persisted live-path alert history, durable incident events, outbound delivery
  history, and merged runtime plus guarded-live audit entries directly in the control room
- guarded-live controls now persist kill-switch state, can stop running sandbox/paper sessions, and
  record operator reconciliation drills before any live candidacy discussion
- guarded-live reconciliation now stores internal exposure snapshots, venue balance/open-order
  snapshots, and mismatch findings when external venue state does not line up with local runtime
- guarded-live recovery can reuse the last verified venue snapshot to rebuild persisted runtime
  exposures and open orders after restart-or-fault drills, while still recording recovery issues
- guarded-live workers now start only after reconciliation, recovery, and config gates are clear,
  then keep a venue-backed worker session alive and submit market orders through the live execution
  adapter
- guarded-live worker maintenance now syncs open and partially-filled venue orders back into local
  order status, fill history, position state, and runtime audit trails
- guarded-live operator controls can now cancel active venue orders or replace them with repriced
  limit orders while keeping local order history and audit state aligned
- guarded-live control state now tracks owned live session identity plus a durable open-order
  snapshot, and the explicit resume action now restores tracked venue order lifecycle state before
  falling back to the persisted snapshot after restart or fault drills
- guarded-live live-path alerting now covers worker failure/staleness, risk guardrail breaches,
  repeated live-session recovery loops, stale active-order sync, and market-data freshness faults
  such as stale sync, richer backfill-quality semantics, repeated sync failures, and venue-specific
  upstream fault classifications so those faults flow into the same durable incident and delivery
  history
- guarded-live alert transitions now emit durable incident-opened/resolved events and outbound
  delivery attempts through configured operator delivery targets such as console logging, generic
  webhook delivery, Slack webhook delivery, PagerDuty Events API delivery, or Opsgenie Alert API
  delivery, while persisting the attempt history for operator review
- failed outbound incident deliveries now persist `attempt_number` and `next_retry_at`, and the
  application applies bounded exponential backoff before retrying due targets on subsequent
  guarded-live state refreshes
- guarded-live incident records now persist acknowledgment and escalation state, support operator
  `acknowledge` and `escalate` actions, suppress pending retries after acknowledgment, and can
  auto-escalate to configured escalation targets after retry exhaustion or ack-timeout windows
- severity-aware paging policy orchestration can now choose initial and escalation targets plus a
  native paging provider, and guarded-live incident records persist the selected policy id,
  provider workflow state/action, and provider workflow reference
- external paging systems can now push `triggered`, `acknowledged`, `escalated`, or `resolved`
  incident sync events into the durable guarded-live incident history, including provider workflow
  references, while local acknowledge/escalate actions can also push provider-native workflow
  actions back out when the provider supports them across PagerDuty and Opsgenie
- guarded-live maintenance now keeps a persisted venue session handoff with transport/session
  metadata so the resumed worker can continue through the Binance multi-stream websocket transport
  and the same venue-owned lifecycle
- guarded-live reconciliation, recovery, and live launch now use the configured guarded-live venue
  instead of inheriting market-data provider wiring, so supported live venues can diverge from the
  candle source when operators need that split
- guarded-live session handoff state now tracks supervision health, failover count, and the latest
  market, depth, kline, aggregate-trade, mini-ticker, account-position, balance-update,
  order-list, trade-tick, and book-ticker event timestamps from the Binance push session, along
  with order-book state, depth sequence, snapshot rebuild timing/counts, full recovered bid/ask
  levels, channel-restore timing/counts, channel-continuation timing/counts, persisted market
  channel snapshots, and top-of-book levels
- if Binance-native user-data streaming is unavailable, guarded-live can now continue on the
  Binance public market websocket, and the same handoff model also supports Coinbase Advanced
  Trade authenticated user/account order transport plus public market channels, alongside Kraken
  spot public market channels for heartbeat/ticker/trade plus level2/book and candle/ohlc
  continuation
- paper runs now start from the latest simulated market snapshot instead of sharing the sandbox
  worker-session path
- reference strategies are supported for backtest delegation only
- the app lifespan starts sandbox worker maintenance jobs, and adds market-data sync jobs when a
  supported ccxt market-data provider is active

## Test

```bash
pytest
```
