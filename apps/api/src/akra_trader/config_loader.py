from __future__ import annotations

import os

from akra_trader.config import Settings
from akra_trader.config import _parse_bool_env
from akra_trader.config import _parse_csv_env


def load_settings() -> Settings:
  return Settings(
    api_prefix=os.getenv("AKRA_TRADER_API_PREFIX", "/api"),
    cors_origin=os.getenv("AKRA_TRADER_CORS_ORIGIN", "http://localhost:5173"),
    runs_database_url=os.getenv("AKRA_TRADER_RUNS_DATABASE_URL") or None,
    market_data_database_url=os.getenv("AKRA_TRADER_MARKET_DATA_DATABASE_URL") or None,
    market_data_provider=os.getenv("AKRA_TRADER_MARKET_DATA_PROVIDER", "binance"),
    market_data_symbols=_parse_csv_env(
      os.getenv("AKRA_TRADER_MARKET_DATA_SYMBOLS", "BTC/USDT,ETH/USDT,SOL/USDT")
    ),
    market_data_sync_timeframes=_parse_csv_env(
      os.getenv("AKRA_TRADER_MARKET_DATA_SYNC_TIMEFRAMES", "5m")
    ),
    market_data_sync_interval_seconds=int(
      os.getenv("AKRA_TRADER_MARKET_DATA_SYNC_INTERVAL_SECONDS", "60")
    ),
    market_data_default_candle_limit=int(
      os.getenv("AKRA_TRADER_MARKET_DATA_DEFAULT_CANDLE_LIMIT", "500")
    ),
    market_data_historical_candle_limit=int(
      os.getenv("AKRA_TRADER_MARKET_DATA_HISTORICAL_CANDLE_LIMIT", "2000")
    ),
    sandbox_worker_heartbeat_interval_seconds=int(
      os.getenv("AKRA_TRADER_SANDBOX_WORKER_HEARTBEAT_INTERVAL_SECONDS", "15")
    ),
    sandbox_worker_heartbeat_timeout_seconds=int(
      os.getenv("AKRA_TRADER_SANDBOX_WORKER_HEARTBEAT_TIMEOUT_SECONDS", "45")
    ),
    guarded_live_execution_enabled=_parse_bool_env(
      os.getenv("AKRA_TRADER_GUARDED_LIVE_EXECUTION_ENABLED", "false")
    ),
    guarded_live_venue=os.getenv("AKRA_TRADER_GUARDED_LIVE_VENUE") or None,
    guarded_live_worker_heartbeat_interval_seconds=int(
      os.getenv("AKRA_TRADER_GUARDED_LIVE_WORKER_HEARTBEAT_INTERVAL_SECONDS", "15")
    ),
    guarded_live_worker_heartbeat_timeout_seconds=int(
      os.getenv("AKRA_TRADER_GUARDED_LIVE_WORKER_HEARTBEAT_TIMEOUT_SECONDS", "45")
    ),
    guarded_live_api_key=os.getenv("AKRA_TRADER_GUARDED_LIVE_API_KEY") or None,
    guarded_live_api_secret=os.getenv("AKRA_TRADER_GUARDED_LIVE_API_SECRET") or None,
    binance_api_key=os.getenv("AKRA_TRADER_BINANCE_API_KEY") or None,
    binance_api_secret=os.getenv("AKRA_TRADER_BINANCE_API_SECRET") or None,
  )
