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
- Binance-backed market data with sync, backfill, gap detection, sync checkpoints, failure history,
  and status reporting
- run provenance exposes rerun boundary identities, supports rerun-boundary filtering, and can
  relaunch stored boundaries into backtest, sandbox, or paper flows
- operator visibility endpoint exposes sandbox worker failure alerts, stale runtime alerts, and
  runtime audit events
- guarded-live state endpoints persist kill-switch state, reconciliation status, and guarded-live
  audit events in the control plane
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
  available, and Coinbase Advanced Trade can supply public heartbeat/ticker/trade/level2/candle
  continuation through the same handoff surface
- reference catalog and Freqtrade-backed NFI backtest delegation

Not implemented yet:

- richer venue order management beyond cancel/replace, including venue-native amend flows
- external alert delivery and wider operator event storage
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
- `AKRA_TRADER_GUARDED_LIVE_WORKER_HEARTBEAT_INTERVAL_SECONDS`
- `AKRA_TRADER_GUARDED_LIVE_WORKER_HEARTBEAT_TIMEOUT_SECONDS`
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
- `GET /api/guarded-live`
- `POST /api/guarded-live/kill-switch/engage`
- `POST /api/guarded-live/kill-switch/release`
- `POST /api/guarded-live/reconciliation`
- `POST /api/guarded-live/recovery`
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
- operator visibility now surfaces stale sandbox heartbeats, worker failures, and runtime audit
  entries directly in the control room
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
- guarded-live maintenance now keeps a persisted venue session handoff with transport/session
  metadata so the resumed worker can continue through the Binance multi-stream websocket transport
  and the same venue-owned lifecycle
- guarded-live session handoff state now tracks supervision health, failover count, and the latest
  market, depth, kline, aggregate-trade, mini-ticker, account-position, balance-update,
  order-list, trade-tick, and book-ticker event timestamps from the Binance push session, along
  with order-book state, depth sequence, snapshot rebuild timing/counts, full recovered bid/ask
  levels, channel-restore timing/counts, channel-continuation timing/counts, persisted market
  channel snapshots, and top-of-book levels
- if Binance-native user-data streaming is unavailable, guarded-live can now continue on the
  Binance public market websocket, and the same handoff model also supports Coinbase Advanced
  Trade public market channels for heartbeat/ticker/trade/level2/candle continuation
- paper runs now start from the latest simulated market snapshot instead of sharing the sandbox
  worker-session path
- reference strategies are supported for backtest delegation only
- the app lifespan starts sandbox worker maintenance jobs, and adds market-data sync jobs when the
  Binance provider is active

## Test

```bash
pytest
```
