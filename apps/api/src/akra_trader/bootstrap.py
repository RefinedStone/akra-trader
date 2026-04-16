from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter
from akra_trader.adapters.in_memory import InMemoryRunRepository
from akra_trader.adapters.in_memory import LocalStrategyCatalog
from akra_trader.adapters.references import load_reference_catalog
from akra_trader.adapters.in_memory import SeededMarketDataAdapter
from akra_trader.application import TradingApplication
from akra_trader.config import Settings


@dataclass
class Container:
  app: TradingApplication


def build_container(settings: Settings) -> Container:
  repo_root = Path(__file__).resolve().parents[4]
  market_data = SeededMarketDataAdapter()
  strategies = LocalStrategyCatalog()
  references = load_reference_catalog(repo_root / "reference" / "catalog.toml")
  runs = InMemoryRunRepository()
  application = TradingApplication(
    market_data=market_data,
    strategies=strategies,
    references=references,
    runs=runs,
    freqtrade_reference=FreqtradeReferenceAdapter(repo_root, references),
  )
  return Container(app=application)
