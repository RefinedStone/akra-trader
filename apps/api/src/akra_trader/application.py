from __future__ import annotations

from dataclasses import asdict
from datetime import UTC
from datetime import datetime
from uuid import uuid4

from akra_trader.adapters.in_memory import candles_to_frame
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import Position
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import StrategyExecutionState
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import StrategyRegistration
from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter
from akra_trader.domain.services import apply_signal
from akra_trader.domain.services import build_equity_point
from akra_trader.domain.services import summarize_performance
from akra_trader.ports import MarketDataPort
from akra_trader.ports import RunRepositoryPort
from akra_trader.ports import StrategyCatalogPort


class TradingApplication:
  def __init__(
    self,
    *,
    market_data: MarketDataPort,
    strategies: StrategyCatalogPort,
    runs: RunRepositoryPort,
    freqtrade_reference: FreqtradeReferenceAdapter | None = None,
  ) -> None:
    self._market_data = market_data
    self._strategies = strategies
    self._runs = runs
    self._freqtrade_reference = freqtrade_reference

  def list_strategies(self) -> list[StrategyMetadata]:
    return self._strategies.list_strategies()

  def register_strategy(self, *, strategy_id: str, module_path: str, class_name: str) -> StrategyMetadata:
    registration = StrategyRegistration(
      strategy_id=strategy_id,
      module_path=module_path,
      class_name=class_name,
      registered_at=datetime.now(UTC),
    )
    return self._strategies.register(registration)

  def list_runs(self, mode: str | None = None) -> list[RunRecord]:
    return self._runs.list_runs(mode=mode)

  def get_run(self, run_id: str) -> RunRecord | None:
    return self._runs.get_run(run_id)

  def get_market_data_status(self, timeframe: str) -> MarketDataStatus:
    return self._market_data.get_status(timeframe)

  def run_backtest(
    self,
    *,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
  ) -> RunRecord:
    strategy = self._strategies.load(strategy_id)
    metadata = strategy.describe()
    config = RunConfig(
      run_id=str(uuid4()),
      mode=RunMode.BACKTEST,
      strategy_id=metadata.strategy_id,
      strategy_version=metadata.version,
      venue="binance",
      symbols=(symbol,),
      timeframe=timeframe,
      parameters=parameters,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      start_at=start_at,
      end_at=end_at,
    )
    if metadata.runtime == "freqtrade_reference":
      run = RunRecord(config=config, status=RunStatus.PENDING)
      if self._freqtrade_reference is None:
        run.status = RunStatus.FAILED
        run.notes.append("Freqtrade reference adapter is not configured.")
      else:
        run = self._freqtrade_reference.execute_backtest(run, metadata)
      return self._runs.save_run(run)
    run = self._simulate_run(config=config, active_bars=None)
    run.status = RunStatus.COMPLETED
    run.ended_at = datetime.now(UTC)
    return self._runs.save_run(run)

  def start_paper_run(
    self,
    *,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict,
    replay_bars: int = 96,
  ) -> RunRecord:
    strategy = self._strategies.load(strategy_id)
    metadata = strategy.describe()
    config = RunConfig(
      run_id=str(uuid4()),
      mode=RunMode.PAPER,
      strategy_id=metadata.strategy_id,
      strategy_version=metadata.version,
      venue="binance",
      symbols=(symbol,),
      timeframe=timeframe,
      parameters=parameters,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
    )
    if metadata.runtime == "freqtrade_reference":
      run = RunRecord(config=config, status=RunStatus.FAILED)
      run.notes.append(
        "Reference Freqtrade strategies are exposed for cataloging and backtest delegation. "
        "Paper trading remains on the native engine for now."
      )
      return self._runs.save_run(run)
    run = self._simulate_run(config=config, active_bars=replay_bars)
    run.status = RunStatus.RUNNING
    run.notes.append(
      "Paper run replays the most recent candles through the shared engine. "
      "Hook a live scheduler/stream adapter into the same use case for continuous trading."
    )
    return self._runs.save_run(run)

  def stop_paper_run(self, run_id: str) -> RunRecord | None:
    run = self._runs.update_status(run_id, RunStatus.STOPPED)
    if run is not None:
      run.notes.append("Paper run stopped by operator.")
    return run

  def _simulate_run(self, *, config: RunConfig, active_bars: int | None) -> RunRecord:
    candles = self._market_data.get_candles(
      symbol=config.symbols[0],
      timeframe=config.timeframe,
      start_at=config.start_at,
      end_at=config.end_at,
      limit=active_bars,
    )
    strategy = self._strategies.load(config.strategy_id)
    data = candles_to_frame(candles)
    if data.empty:
      run = RunRecord(config=config, status=RunStatus.FAILED)
      run.notes.append("No candles available for the requested range.")
      return run

    enriched = strategy.build_feature_frame(data, config.parameters)
    run = RunRecord(config=config, status=RunStatus.RUNNING)
    warmup = strategy.warmup_spec().required_bars
    cash = config.initial_cash
    position: Position | None = None

    for index in range(max(warmup, 2), len(enriched)):
      history = enriched.iloc[: index + 1]
      latest_row = history.iloc[-1]
      state = StrategyExecutionState(
        timestamp=latest_row["timestamp"].to_pydatetime(),
        instrument_id=f"{config.venue}:{config.symbols[0]}",
        has_position=position is not None and position.is_open,
        cash=cash,
        position_size=position.quantity if position else 0.0,
        parameters=config.parameters,
      )
      decision = strategy.evaluate(history, config.parameters, state)
      latest_row = history.iloc[-1]
      cash, position, order, fill, closed_trade = apply_signal(
        run_id=config.run_id,
        instrument_id=f"{config.venue}:{config.symbols[0]}",
        signal=decision.signal,
        market_price=float(latest_row["close"]),
        position=position,
        cash=cash,
        fee_rate=config.fee_rate,
        slippage_bps=config.slippage_bps,
      )
      if order is not None:
        run.orders.append(order)
      if fill is not None:
        run.fills.append(fill)
      if position is not None:
        run.positions[position.instrument_id] = position
      if closed_trade is not None:
        run.closed_trades.append(closed_trade)

      run.equity_curve.append(
        build_equity_point(
          timestamp=decision.signal.timestamp,
          cash=cash,
          position=position if position and position.is_open else None,
          market_price=float(latest_row["close"]),
        )
      )
      run.notes.append(f"{decision.context.timestamp.isoformat()} | {decision.signal.action.value} | {decision.rationale}")

    run.metrics = summarize_performance(
      initial_cash=config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    if active_bars is not None:
      run.notes.append(f"Paper preview replayed {active_bars} most recent bars.")
    return run


def serialize_run(run: RunRecord) -> dict:
  payload = asdict(run)
  payload["config"]["mode"] = run.config.mode.value
  payload["status"] = run.status.value
  return payload
