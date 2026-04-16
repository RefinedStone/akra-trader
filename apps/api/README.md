# Akra Trader API

FastAPI backend for strategy cataloging, market-data access, durable run storage, native backtests, replay-based sandbox runs, and external reference backtest delegation.

## Current Scope

Implemented now:

- strategy catalog with native and reference lanes
- in-process custom strategy registration endpoint
- durable run storage through SQLAlchemy
- backtest execution and run lookup
- replay-based sandbox preview flow for native strategies
- native vs reference run comparison API
- Binance-backed market data with sync, backfill, gap detection, and status reporting
- reference catalog and Freqtrade-backed NFI backtest delegation

Not implemented yet:

- continuous sandbox workers
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
- `POST /api/runs/sandbox`
- `POST /api/runs/sandbox/{run_id}/stop`
- `GET /api/runs/{run_id}/orders`
- `GET /api/runs/{run_id}/positions`
- `GET /api/runs/{run_id}/metrics`
- `GET /api/market-data/status`

## Runtime Notes

- backtests run to completion and are persisted immediately
- sandbox runs currently replay the most recent bars and are then marked `running` for forward compatibility with a future worker model
- reference strategies are supported for backtest delegation only
- the app lifespan starts background market-data sync jobs when the Binance provider is active

## Test

```bash
pytest
```
