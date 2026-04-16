from __future__ import annotations

from dataclasses import asdict
from datetime import UTC
from datetime import datetime
from uuid import uuid4

from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import ReferenceSource
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import StrategyRegistration
from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter
from akra_trader.domain.services import summarize_performance
from akra_trader.ports import MarketDataPort
from akra_trader.ports import ReferenceCatalogPort
from akra_trader.ports import RunRepositoryPort
from akra_trader.ports import StrategyCatalogPort
from akra_trader.runtime import DataEngine
from akra_trader.runtime import ExecutionEngine
from akra_trader.runtime import ExecutionModeService
from akra_trader.runtime import RunSupervisor
from akra_trader.runtime import StateCache


class TradingApplication:
  def __init__(
    self,
    *,
    market_data: MarketDataPort,
    strategies: StrategyCatalogPort,
    references: ReferenceCatalogPort,
    runs: RunRepositoryPort,
    freqtrade_reference: FreqtradeReferenceAdapter | None = None,
    mode_service: ExecutionModeService | None = None,
    data_engine: DataEngine | None = None,
    execution_engine: ExecutionEngine | None = None,
    run_supervisor: RunSupervisor | None = None,
  ) -> None:
    self._market_data = market_data
    self._strategies = strategies
    self._references = references
    self._runs = runs
    self._freqtrade_reference = freqtrade_reference
    self._mode_service = mode_service or ExecutionModeService()
    self._data_engine = data_engine or DataEngine(market_data)
    self._execution_engine = execution_engine or ExecutionEngine()
    self._run_supervisor = run_supervisor or RunSupervisor()

  def list_strategies(self) -> list[StrategyMetadata]:
    return self._strategies.list_strategies()

  def list_references(self) -> list[ReferenceSource]:
    return self._references.list_entries()

  def register_strategy(self, *, strategy_id: str, module_path: str, class_name: str) -> StrategyMetadata:
    registration = StrategyRegistration(
      strategy_id=strategy_id,
      module_path=module_path,
      class_name=class_name,
      registered_at=datetime.now(UTC),
    )
    return self._strategies.register(registration)

  def list_runs(self, mode: str | None = None) -> list[RunRecord]:
    return self._runs.list_runs(mode=self._mode_service.normalize(mode))

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
    if run.status != RunStatus.FAILED:
      self._run_supervisor.complete(run)
    return self._runs.save_run(run)

  def start_sandbox_run(
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
      mode=RunMode.SANDBOX,
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
        "Sandbox trading remains on the native engine for now."
      )
      return self._runs.save_run(run)
    run = self._simulate_run(config=config, active_bars=replay_bars)
    if run.status != RunStatus.FAILED:
      self._run_supervisor.start_mode(
        run=run,
        mode=RunMode.SANDBOX,
        mode_service=self._mode_service,
        replay_bars=replay_bars,
      )
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
    return self.start_sandbox_run(
      strategy_id=strategy_id,
      symbol=symbol,
      timeframe=timeframe,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      replay_bars=replay_bars,
    )

  def stop_sandbox_run(self, run_id: str) -> RunRecord | None:
    run = self._runs.get_run(run_id)
    if run is None:
      return None
    self._run_supervisor.stop(run, reason="Sandbox run stopped by operator.")
    return self._runs.save_run(run)

  def stop_paper_run(self, run_id: str) -> RunRecord | None:
    return self.stop_sandbox_run(run_id)

  def _simulate_run(self, *, config: RunConfig, active_bars: int | None) -> RunRecord:
    strategy = self._strategies.load(config.strategy_id)
    loaded = self._data_engine.load_frame(config=config, active_bars=active_bars)
    run = self._run_supervisor.create_native_run(config=config)
    run.provenance.market_data = loaded.lineage
    data = loaded.frame
    if data.empty:
      run.notes.append("No candles available for the requested range.")
      run.status = RunStatus.FAILED
      return run

    enriched = strategy.build_feature_frame(data, config.parameters)
    warmup = strategy.warmup_spec().required_bars
    cache = StateCache(
      instrument_id=f"{config.venue}:{config.symbols[0]}",
      cash=config.initial_cash,
    )

    for index in range(max(warmup, 2), len(enriched)):
      history = enriched.iloc[: index + 1]
      latest_row = history.iloc[-1]
      state = cache.snapshot(
        timestamp=latest_row["timestamp"].to_pydatetime(),
        parameters=config.parameters,
      )
      decision = strategy.evaluate(history, config.parameters, state)
      latest_row = history.iloc[-1]
      self._execution_engine.apply_decision(
        run=run,
        config=config,
        decision=decision,
        cache=cache,
        market_price=float(latest_row["close"]),
      )

    run.metrics = summarize_performance(
      initial_cash=config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    if active_bars is not None:
      run.notes.append(f"Sandbox preview replayed {active_bars} most recent bars.")
    return run


def serialize_run(run: RunRecord) -> dict:
  payload = asdict(run)
  payload["config"]["mode"] = run.config.mode.value
  payload["status"] = run.status.value
  payload["provenance"]["external_command"] = list(run.provenance.external_command)
  payload["provenance"]["artifact_paths"] = list(run.provenance.artifact_paths)
  return payload
