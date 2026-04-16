from __future__ import annotations

from collections import OrderedDict
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from importlib import import_module
from typing import Iterable

import pandas as pd

from akra_trader.domain.models import AssetType
from akra_trader.domain.models import Candle
from akra_trader.domain.models import Instrument
from akra_trader.domain.models import InstrumentStatus
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import MarketType
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import StrategyRegistration
from akra_trader.ports import MarketDataPort
from akra_trader.ports import RunRepositoryPort
from akra_trader.ports import StrategyCatalogPort
from akra_trader.strategies.base import Strategy
from akra_trader.strategies.examples import MovingAverageCrossStrategy
from akra_trader.strategies.reference import build_reference_strategies


def build_seeded_market_data() -> dict[str, list[Candle]]:
  instruments = ("BTC/USDT", "ETH/USDT", "SOL/USDT")
  start = datetime(2025, 1, 1, tzinfo=UTC)
  series: dict[str, list[Candle]] = {}
  for offset, symbol in enumerate(instruments):
    candles: list[Candle] = []
    price = 40_000.0 / (offset + 1)
    for index in range(240):
      timestamp = start + timedelta(minutes=5 * index)
      drift = 1 + (0.0008 * (index / 8))
      cycle = ((index % 24) - 12) / 280
      open_price = price
      close_price = price * drift + price * cycle
      high_price = max(open_price, close_price) * 1.004
      low_price = min(open_price, close_price) * 0.996
      volume = 500 + (index * 3) + (offset * 15)
      candles.append(
        Candle(
          timestamp=timestamp,
          open=round(open_price, 2),
          high=round(high_price, 2),
          low=round(low_price, 2),
          close=round(close_price, 2),
          volume=round(volume, 2),
        )
      )
      price = close_price
    series[symbol] = candles
  return series


class SeededMarketDataAdapter(MarketDataPort):
  def __init__(self, venue: str = "binance") -> None:
    self._venue = venue
    self._candles = build_seeded_market_data()
    self._instruments = [
      Instrument(
        symbol=symbol,
        venue=venue,
        base_currency=symbol.split("/")[0],
        quote_currency=symbol.split("/")[1],
        asset_type=AssetType.CRYPTO,
        market_type=MarketType.SPOT,
      )
      for symbol in self._candles
    ]

  def list_instruments(self) -> list[Instrument]:
    return list(self._instruments)

  def get_candles(
    self,
    *,
    symbol: str,
    timeframe: str,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int | None = None,
  ) -> list[Candle]:
    candles = list(self._candles.get(symbol, ()))
    if start_at is not None:
      candles = [candle for candle in candles if candle.timestamp >= start_at]
    if end_at is not None:
      candles = [candle for candle in candles if candle.timestamp <= end_at]
    if limit is not None:
      candles = candles[-limit:]
    return candles

  def get_status(self, timeframe: str) -> MarketDataStatus:
    instruments = []
    for symbol, candles in self._candles.items():
      first = candles[0].timestamp if candles else None
      last = candles[-1].timestamp if candles else None
      instruments.append(
        InstrumentStatus(
          instrument_id=f"{self._venue}:{symbol}",
          timeframe=timeframe,
          candle_count=len(candles),
          first_timestamp=first,
          last_timestamp=last,
        )
      )
    return MarketDataStatus(provider="seeded", venue=self._venue, instruments=instruments)


class InMemoryRunRepository(RunRepositoryPort):
  def __init__(self) -> None:
    self._runs: OrderedDict[str, RunRecord] = OrderedDict()

  def save_run(self, run: RunRecord) -> RunRecord:
    self._runs[run.config.run_id] = run
    return run

  def get_run(self, run_id: str) -> RunRecord | None:
    return self._runs.get(run_id)

  def list_runs(self, mode: str | None = None) -> list[RunRecord]:
    values = list(self._runs.values())
    if mode is None:
      return list(reversed(values))
    return [run for run in reversed(values) if run.config.mode.value == mode]

  def update_status(self, run_id: str, status: RunStatus) -> RunRecord | None:
    run = self._runs.get(run_id)
    if run is None:
      return None
    run.status = status
    if status in {RunStatus.COMPLETED, RunStatus.STOPPED, RunStatus.FAILED}:
      run.ended_at = datetime.now(UTC)
    return run


class LocalStrategyCatalog(StrategyCatalogPort):
  def __init__(self, builtins: Iterable[type[Strategy]] | None = None) -> None:
    builtin_factories: dict[str, callable] = {}
    for strategy in (builtins or (MovingAverageCrossStrategy,)):
      metadata = strategy().describe()
      builtin_factories[metadata.strategy_id] = strategy
    for strategy in build_reference_strategies():
      builtin_factories[strategy.describe().strategy_id] = strategy.__class__
    self._builtins = builtin_factories
    self._references = {strategy.describe().strategy_id: strategy for strategy in build_reference_strategies()}
    self._registrations: dict[str, StrategyRegistration] = {}

  def list_strategies(self) -> list[StrategyMetadata]:
    metadata = []
    for strategy_id, strategy in self._builtins.items():
      if strategy_id in self._references:
        metadata.append(self._references[strategy_id].describe())
      else:
        metadata.append(strategy().describe())
    for registration in self._registrations.values():
      metadata.append(self.load(registration.strategy_id).describe())
    return sorted(metadata, key=lambda item: item.strategy_id)

  def load(self, strategy_id: str) -> Strategy:
    if strategy_id in self._references:
      return self._references[strategy_id]
    if strategy_id in self._builtins:
      return self._builtins[strategy_id]()
    registration = self._registrations[strategy_id]
    module = import_module(registration.module_path)
    strategy_cls = getattr(module, registration.class_name)
    return strategy_cls()

  def register(self, registration: StrategyRegistration) -> StrategyMetadata:
    module = import_module(registration.module_path)
    strategy_cls = getattr(module, registration.class_name)
    strategy = strategy_cls()
    self._registrations[registration.strategy_id] = registration
    return strategy.describe()


def candles_to_frame(candles: list[Candle]) -> pd.DataFrame:
  return pd.DataFrame(
    [
      {
        "timestamp": candle.timestamp,
        "open": candle.open,
        "high": candle.high,
        "low": candle.low,
        "close": candle.close,
        "volume": candle.volume,
      }
      for candle in candles
    ]
  )
