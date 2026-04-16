from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from akra_trader.adapters.binance import BinanceMarketDataAdapter
from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter
from akra_trader.adapters.in_memory import LocalStrategyCatalog
from akra_trader.adapters.references import load_reference_catalog
from akra_trader.adapters.in_memory import SeededMarketDataAdapter
from akra_trader.adapters.sqlalchemy import SqlAlchemyRunRepository
from akra_trader.application import TradingApplication
from akra_trader.config import Settings


@dataclass
class Container:
  app: TradingApplication


def build_default_runs_database_url(repo_root: Path) -> str:
  database_path = (repo_root / ".local" / "state" / "runs.sqlite3").resolve()
  return f"sqlite:///{database_path}"


def build_default_market_data_database_url(repo_root: Path) -> str:
  database_path = (repo_root / ".local" / "state" / "market-data.sqlite3").resolve()
  return f"sqlite:///{database_path}"


def build_market_data_adapter(settings: Settings, repo_root: Path):
  if settings.market_data_provider == "seeded":
    return SeededMarketDataAdapter()
  if settings.market_data_provider == "binance":
    return BinanceMarketDataAdapter(
      database_url=(
        settings.market_data_database_url
        or settings.runs_database_url
        or build_default_market_data_database_url(repo_root)
      ),
      tracked_symbols=settings.market_data_symbols,
      default_candle_limit=settings.market_data_default_candle_limit,
    )
  raise ValueError(f"Unsupported market data provider: {settings.market_data_provider}")


def build_container(settings: Settings) -> Container:
  repo_root = Path(__file__).resolve().parents[4]
  market_data = build_market_data_adapter(settings, repo_root)
  strategies = LocalStrategyCatalog()
  references = load_reference_catalog(repo_root / "reference" / "catalog.toml")
  runs = SqlAlchemyRunRepository(
    settings.runs_database_url or build_default_runs_database_url(repo_root)
  )
  application = TradingApplication(
    market_data=market_data,
    strategies=strategies,
    references=references,
    runs=runs,
    freqtrade_reference=FreqtradeReferenceAdapter(repo_root, references),
  )
  return Container(app=application)
