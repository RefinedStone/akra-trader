from __future__ import annotations

from dataclasses import dataclass


def _parse_csv_env(value: str) -> tuple[str, ...]:
  return tuple(item.strip() for item in value.split(",") if item.strip())


def _parse_bool_env(value: str) -> bool:
  return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
  app_name: str = "Akra Trader API"
  api_prefix: str = "/api"
  cors_origin: str = "http://localhost:5173"
  runs_database_url: str | None = None
  market_data_database_url: str | None = None
  market_data_provider: str = "binance"
  market_data_symbols: tuple[str, ...] = ("BTC/USDT", "ETH/USDT", "SOL/USDT")
  market_data_sync_timeframes: tuple[str, ...] = ("5m",)
  market_data_sync_interval_seconds: int = 60
  market_data_default_candle_limit: int = 500
  market_data_historical_candle_limit: int = 2_000
  sandbox_worker_heartbeat_interval_seconds: int = 15
  sandbox_worker_heartbeat_timeout_seconds: int = 45
  guarded_live_execution_enabled: bool = False
  guarded_live_venue: str | None = None
  guarded_live_worker_heartbeat_interval_seconds: int = 15
  guarded_live_worker_heartbeat_timeout_seconds: int = 45
  guarded_live_api_key: str | None = None
  guarded_live_api_secret: str | None = None
  binance_api_key: str | None = None
  binance_api_secret: str | None = None


from akra_trader.config_loader import load_settings
