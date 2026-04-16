from __future__ import annotations

from dataclasses import dataclass
import os


def _parse_csv_env(value: str) -> tuple[str, ...]:
  return tuple(item.strip() for item in value.split(",") if item.strip())


def _parse_bool_env(value: str) -> bool:
  return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
  app_name: str = "Akra Trader API"
  api_prefix: str = "/api"
  cors_origin: str = "http://localhost:5173"
  market_data_provider: str = "binance"
  default_quote_currency: str = "USDT"
  runs_database_url: str | None = None
  market_data_database_url: str | None = None
  market_data_symbols: tuple[str, ...] = ("BTC/USDT", "ETH/USDT", "SOL/USDT")
  market_data_sync_timeframes: tuple[str, ...] = ("5m",)
  market_data_sync_interval_seconds: int = 60
  market_data_default_candle_limit: int = 500
  market_data_historical_candle_limit: int = 2_000
  sandbox_worker_heartbeat_interval_seconds: int = 15
  sandbox_worker_heartbeat_timeout_seconds: int = 45
  guarded_live_execution_enabled: bool = False
  guarded_live_worker_heartbeat_interval_seconds: int = 15
  guarded_live_worker_heartbeat_timeout_seconds: int = 45
  binance_api_key: str | None = None
  binance_api_secret: str | None = None


def load_settings() -> Settings:
  return Settings(
    cors_origin=os.getenv("AKRA_TRADER_CORS_ORIGIN", "http://localhost:5173"),
    market_data_provider=os.getenv("AKRA_TRADER_MARKET_DATA_PROVIDER", "binance"),
    default_quote_currency=os.getenv("AKRA_TRADER_DEFAULT_QUOTE", "USDT"),
    runs_database_url=os.getenv("AKRA_TRADER_RUNS_DATABASE_URL") or None,
    market_data_database_url=os.getenv("AKRA_TRADER_MARKET_DATA_DATABASE_URL") or None,
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
    guarded_live_worker_heartbeat_interval_seconds=int(
      os.getenv("AKRA_TRADER_GUARDED_LIVE_WORKER_HEARTBEAT_INTERVAL_SECONDS", "15")
    ),
    guarded_live_worker_heartbeat_timeout_seconds=int(
      os.getenv("AKRA_TRADER_GUARDED_LIVE_WORKER_HEARTBEAT_TIMEOUT_SECONDS", "45")
    ),
    binance_api_key=os.getenv("AKRA_TRADER_BINANCE_API_KEY") or None,
    binance_api_secret=os.getenv("AKRA_TRADER_BINANCE_API_SECRET") or None,
  )
