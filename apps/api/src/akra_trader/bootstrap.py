from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter
from akra_trader.adapters.in_memory import InMemoryRunRepository
from akra_trader.adapters.in_memory import LocalStrategyCatalog
from akra_trader.adapters.in_memory import SeededMarketDataAdapter
from akra_trader.application import TradingApplication
from akra_trader.config import Settings


@dataclass
class Container:
  app: TradingApplication


def build_container(settings: Settings) -> Container:
  market_data = SeededMarketDataAdapter()
  strategies = LocalStrategyCatalog()
  runs = InMemoryRunRepository()
  application = TradingApplication(
    market_data=market_data,
    strategies=strategies,
    runs=runs,
    freqtrade_reference=FreqtradeReferenceAdapter(Path(__file__).resolve().parents[4]),
  )
  return Container(app=application)
