from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from datetime import UTC
from datetime import datetime
from numbers import Number
from uuid import uuid4

from akra_trader.domain.models import RunComparison
from akra_trader.domain.models import RunComparisonMetricRow
from akra_trader.domain.models import RunComparisonRun
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import ReferenceSource
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunProvenance
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import StrategyLifecycle
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import StrategyParameterSnapshot
from akra_trader.domain.models import StrategyRegistration
from akra_trader.domain.models import StrategySnapshot
from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter
from akra_trader.domain.services import summarize_performance
from akra_trader.ports import MarketDataPort
from akra_trader.ports import ReferenceCatalogPort
from akra_trader.ports import RunRepositoryPort
from akra_trader.ports import StrategyCatalogPort
from akra_trader.ports import StrategyRuntime
from akra_trader.runtime import DataEngine
from akra_trader.runtime import ExecutionEngine
from akra_trader.runtime import ExecutionModeService
from akra_trader.runtime import RunSupervisor
from akra_trader.runtime import StateCache


COMPARISON_METRICS: tuple[tuple[str, str, str, bool], ...] = (
  ("total_return_pct", "Total return", "pct", True),
  ("max_drawdown_pct", "Max drawdown", "pct", False),
  ("win_rate_pct", "Win rate", "pct", True),
  ("trade_count", "Trades", "count", True),
)


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

  def list_strategies(
    self,
    *,
    lane: str | None = None,
    lifecycle_stage: str | None = None,
    version: str | None = None,
  ) -> list[StrategyMetadata]:
    return self._strategies.list_strategies(
      runtime=lane,
      lifecycle_stage=lifecycle_stage,
      version=version,
    )

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

  def list_runs(
    self,
    mode: str | None = None,
    *,
    strategy_id: str | None = None,
    strategy_version: str | None = None,
  ) -> list[RunRecord]:
    return self._runs.list_runs(
      mode=self._mode_service.normalize(mode),
      strategy_id=strategy_id,
      strategy_version=strategy_version,
    )

  def get_run(self, run_id: str) -> RunRecord | None:
    return self._runs.get_run(run_id)

  def compare_runs(self, *, run_ids: list[str]) -> RunComparison:
    normalized_run_ids = _normalize_run_ids(run_ids)
    if len(normalized_run_ids) < 2:
      raise ValueError("Run comparison requires at least two unique run IDs.")

    runs = self._runs.compare_runs(normalized_run_ids)
    run_by_id = {run.config.run_id: run for run in runs}
    missing_run_ids = [run_id for run_id in normalized_run_ids if run_id not in run_by_id]
    if missing_run_ids:
      raise LookupError(f"Run not found: {', '.join(missing_run_ids)}")

    ordered_runs = [run_by_id[run_id] for run_id in normalized_run_ids]
    baseline_run = ordered_runs[0]
    return RunComparison(
      requested_run_ids=tuple(normalized_run_ids),
      baseline_run_id=baseline_run.config.run_id,
      runs=tuple(_serialize_comparison_run(run) for run in ordered_runs),
      metric_rows=tuple(
        _build_comparison_metric_row(
          runs=ordered_runs,
          baseline_run=baseline_run,
          key=key,
          label=label,
          unit=unit,
          higher_is_better=higher_is_better,
        )
        for key, label, unit, higher_is_better in COMPARISON_METRICS
      ),
    )

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
    strategy, metadata, strategy_snapshot = self._prepare_strategy(strategy_id=strategy_id, parameters=parameters)
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
      run = RunRecord(
        config=config,
        status=RunStatus.PENDING,
        provenance=RunProvenance(lane="reference", strategy=strategy_snapshot),
      )
      if self._freqtrade_reference is None:
        run.status = RunStatus.FAILED
        run.notes.append("Freqtrade reference adapter is not configured.")
      else:
        run = self._freqtrade_reference.execute_backtest(run, metadata)
      return self._runs.save_run(run)
    run = self._simulate_run(
      config=config,
      strategy=strategy,
      strategy_snapshot=strategy_snapshot,
      active_bars=None,
    )
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
    strategy, metadata, strategy_snapshot = self._prepare_strategy(strategy_id=strategy_id, parameters=parameters)
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
      run = RunRecord(
        config=config,
        status=RunStatus.FAILED,
        provenance=RunProvenance(lane="reference", strategy=strategy_snapshot),
      )
      run.notes.append(
        "Reference Freqtrade strategies are exposed for cataloging and backtest delegation. "
        "Sandbox trading remains on the native engine for now."
      )
      return self._runs.save_run(run)
    run = self._simulate_run(
      config=config,
      strategy=strategy,
      strategy_snapshot=strategy_snapshot,
      active_bars=replay_bars,
    )
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

  def _simulate_run(
    self,
    *,
    config: RunConfig,
    active_bars: int | None,
    strategy: StrategyRuntime | None = None,
    strategy_snapshot: StrategySnapshot | None = None,
  ) -> RunRecord:
    if strategy is None:
      strategy, _, strategy_snapshot = self._prepare_strategy(
        strategy_id=config.strategy_id,
        parameters=config.parameters,
      )
    loaded = self._data_engine.load_frame(config=config, active_bars=active_bars)
    run = self._run_supervisor.create_native_run(config=config, strategy=strategy_snapshot)
    run.provenance.market_data = loaded.lineage
    run.provenance.market_data_by_symbol = loaded.lineage_by_symbol
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

  def _prepare_strategy(
    self,
    *,
    strategy_id: str,
    parameters: dict,
  ) -> tuple[StrategyRuntime, StrategyMetadata, StrategySnapshot]:
    strategy = self._strategies.load(strategy_id)
    metadata = strategy.describe()
    registration = self._strategies.get_registration(metadata.strategy_id)
    return strategy, metadata, self._build_strategy_snapshot(
      strategy=strategy,
      metadata=metadata,
      parameters=parameters,
      registration=registration,
    )

  def _build_strategy_snapshot(
    self,
    *,
    strategy: StrategyRuntime,
    metadata: StrategyMetadata,
    parameters: dict,
    registration: StrategyRegistration | None,
  ) -> StrategySnapshot:
    schema = deepcopy(metadata.parameter_schema)
    requested = deepcopy(parameters)
    resolved = self._resolve_parameters(schema=schema, requested=requested)
    lifecycle = metadata.lifecycle
    if registration is not None and lifecycle.registered_at is None:
      lifecycle = StrategyLifecycle(
        stage=lifecycle.stage,
        registered_at=registration.registered_at,
      )
    return StrategySnapshot(
      strategy_id=metadata.strategy_id,
      name=metadata.name,
      version=metadata.version,
      runtime=metadata.runtime,
      lifecycle=lifecycle,
      version_lineage=metadata.version_lineage or (metadata.version,),
      parameter_snapshot=StrategyParameterSnapshot(
        requested=requested,
        resolved=resolved,
        schema=schema,
      ),
      supported_timeframes=metadata.supported_timeframes,
      warmup=strategy.warmup_spec(),
      reference_id=metadata.reference_id,
      reference_path=metadata.reference_path,
      entrypoint=metadata.entrypoint,
    )

  @staticmethod
  def _resolve_parameters(*, schema: dict, requested: dict) -> dict:
    resolved: dict = {}
    for name, definition in schema.items():
      if isinstance(definition, dict) and "default" in definition:
        resolved[name] = deepcopy(definition["default"])
    for name, value in requested.items():
      resolved[name] = deepcopy(value)
    return resolved


def serialize_run(run: RunRecord) -> dict:
  payload = asdict(run)
  payload["config"]["mode"] = run.config.mode.value
  payload["status"] = run.status.value
  payload["provenance"]["external_command"] = list(run.provenance.external_command)
  payload["provenance"]["artifact_paths"] = list(run.provenance.artifact_paths)
  payload["provenance"]["benchmark_artifacts"] = [
    asdict(artifact)
    for artifact in run.provenance.benchmark_artifacts
  ]
  strategy_snapshot = payload["provenance"].get("strategy")
  if strategy_snapshot is not None:
    strategy_snapshot["version_lineage"] = list(
      run.provenance.strategy.version_lineage or (run.provenance.strategy.version,)
    )
    strategy_snapshot["supported_timeframes"] = list(run.provenance.strategy.supported_timeframes)
    strategy_snapshot["warmup"]["timeframes"] = list(run.provenance.strategy.warmup.timeframes)
  return payload


def serialize_strategy(strategy: StrategyMetadata) -> dict:
  payload = asdict(strategy)
  payload["asset_types"] = [asset_type.value for asset_type in strategy.asset_types]
  payload["supported_timeframes"] = list(strategy.supported_timeframes)
  payload["version_lineage"] = list(strategy.version_lineage or (strategy.version,))
  return payload


def serialize_run_comparison(comparison: RunComparison) -> dict:
  payload = asdict(comparison)
  payload["requested_run_ids"] = list(comparison.requested_run_ids)
  payload["runs"] = [
    {
      **run_payload,
      "symbols": list(run.symbols),
      "external_command": list(run.external_command),
      "artifact_paths": list(run.artifact_paths),
      "benchmark_artifacts": [asdict(artifact) for artifact in run.benchmark_artifacts],
      "notes": list(run.notes),
    }
    for run_payload, run in zip(payload["runs"], comparison.runs, strict=True)
  ]
  return payload


def _normalize_run_ids(run_ids: list[str]) -> list[str]:
  normalized_run_ids: list[str] = []
  seen_run_ids: set[str] = set()
  for run_id in run_ids:
    if run_id in seen_run_ids:
      continue
    seen_run_ids.add(run_id)
    normalized_run_ids.append(run_id)
  return normalized_run_ids


def _serialize_comparison_run(run: RunRecord) -> RunComparisonRun:
  return RunComparisonRun(
    run_id=run.config.run_id,
    mode=run.config.mode.value,
    status=run.status.value,
    lane=run.provenance.lane,
    strategy_id=run.config.strategy_id,
    strategy_name=run.provenance.strategy.name if run.provenance.strategy is not None else None,
    strategy_version=run.config.strategy_version,
    symbols=run.config.symbols,
    timeframe=run.config.timeframe,
    started_at=run.started_at,
    ended_at=run.ended_at,
    reference_id=run.provenance.reference_id,
    reference_version=run.provenance.reference_version,
    integration_mode=run.provenance.integration_mode,
    reference=deepcopy(run.provenance.reference),
    working_directory=run.provenance.working_directory,
    external_command=tuple(run.provenance.external_command),
    artifact_paths=tuple(run.provenance.artifact_paths),
    benchmark_artifacts=tuple(run.provenance.benchmark_artifacts),
    metrics=deepcopy(run.metrics),
    notes=tuple(run.notes),
  )


def _build_comparison_metric_row(
  *,
  runs: list[RunRecord],
  baseline_run: RunRecord,
  key: str,
  label: str,
  unit: str,
  higher_is_better: bool,
) -> RunComparisonMetricRow:
  baseline_value = _coerce_metric_value(baseline_run.metrics.get(key))
  values = {
    run.config.run_id: _coerce_metric_value(run.metrics.get(key))
    for run in runs
  }
  deltas_vs_baseline = {
    run_id: _calculate_metric_delta(value, baseline_value)
    for run_id, value in values.items()
  }
  comparable_values = {
    run_id: value
    for run_id, value in values.items()
    if value is not None
  }
  best_run_id: str | None = None
  if comparable_values:
    best_run_id = (
      max(comparable_values, key=comparable_values.get)
      if higher_is_better
      else min(comparable_values, key=comparable_values.get)
    )
  return RunComparisonMetricRow(
    key=key,
    label=label,
    unit=unit,
    higher_is_better=higher_is_better,
    values=values,
    deltas_vs_baseline=deltas_vs_baseline,
    best_run_id=best_run_id,
  )


def _coerce_metric_value(value: object) -> float | int | None:
  if isinstance(value, bool) or not isinstance(value, Number):
    return None
  if isinstance(value, int):
    return value
  return round(float(value), 2)


def _calculate_metric_delta(
  value: float | int | None,
  baseline_value: float | int | None,
) -> float | int | None:
  if value is None or baseline_value is None:
    return None
  delta = value - baseline_value
  if isinstance(value, int) and isinstance(baseline_value, int):
    return int(delta)
  return round(float(delta), 2)
