from __future__ import annotations

from dataclasses import dataclass
import os


def _parse_csv_env(value: str) -> tuple[str, ...]:
  return tuple(item.strip() for item in value.split(",") if item.strip())


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
  market_data_default_candle_limit: int = 500


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
    market_data_default_candle_limit=int(
      os.getenv("AKRA_TRADER_MARKET_DATA_DEFAULT_CANDLE_LIMIT", "500")
    ),
  )
