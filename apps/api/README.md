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
- reference catalog and Freqtrade-backed NFI backtest delegation

Not implemented yet:

- live trading adapters
- alerting and operator event storage
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
- `GET /api/runs/{run_id}/orders`
- `GET /api/runs/{run_id}/positions`
- `GET /api/runs/{run_id}/metrics`
- `GET /api/market-data/status`

## Runtime Notes

- backtests run to completion and are persisted immediately
- native candle-backed runs persist dataset identity fingerprints for the exact candles used
- stored rerun boundaries can launch explicit backtest, sandbox, and paper reruns with
  match-or-drift notes
- sandbox worker sessions and paper sessions now persist as separate modes, so history and filters no
  longer share the same storage bucket
- sandbox runs now start as native worker sessions with persisted heartbeat and recovery state
- paper runs now start from the latest simulated market snapshot instead of sharing the sandbox
  worker-session path
- reference strategies are supported for backtest delegation only
- the app lifespan starts sandbox worker maintenance jobs, and adds market-data sync jobs when the
  Binance provider is active

## Test

```bash
pytest
```
