from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
  app_name: str = "Akra Trader API"
  api_prefix: str = "/api"
  cors_origin: str = os.getenv("AKRA_TRADER_CORS_ORIGIN", "http://localhost:5173")
  market_data_provider: str = os.getenv("AKRA_TRADER_MARKET_DATA_PROVIDER", "seeded")
  default_quote_currency: str = os.getenv("AKRA_TRADER_DEFAULT_QUOTE", "USDT")


def load_settings() -> Settings:
  return Settings()
