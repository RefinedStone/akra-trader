from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from numbers import Number
from uuid import uuid4

from akra_trader.domain.models import RunComparison
from akra_trader.domain.models import RunComparisonNarrative
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
from akra_trader.lineage import build_rerun_boundary_identity
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

COMPARISON_INTENT_DEFAULT = "benchmark_validation"
COMPARISON_INTENT_WEIGHTS: dict[str, dict[str, float]] = {
  "benchmark_validation": {
    "return": 0.8,
    "drawdown": 1.5,
    "win_rate": 0.7,
    "trade_count": 0.12,
    "native_reference_bonus": 8.0,
    "reference_bonus": 3.0,
    "status_bonus": 1.5,
    "benchmark_story_bonus": 1.5,
    "reference_floor": 1.0,
  },
  "execution_regression": {
    "return": 0.9,
    "drawdown": 1.9,
    "win_rate": 1.0,
    "trade_count": 0.4,
    "native_reference_bonus": 3.0,
    "reference_bonus": 1.0,
    "status_bonus": 3.0,
    "benchmark_story_bonus": 0.8,
    "reference_floor": 1.0,
  },
  "strategy_tuning": {
    "return": 2.0,
    "drawdown": 0.7,
    "win_rate": 1.3,
    "trade_count": 0.35,
    "native_reference_bonus": 1.5,
    "reference_bonus": 0.5,
    "status_bonus": 0.8,
    "benchmark_story_bonus": 0.4,
    "reference_floor": 0.5,
  },
}

COMPARISON_INTENT_COPY: dict[str, dict[str, str]] = {
  "benchmark_validation": {
    "title_prefix": "Benchmark validation",
    "summary_prefix": "Validation view",
    "partial_summary": (
      "Benchmark validation falls back to persisted reference provenance because direct metric "
      "deltas are partial."
    ),
    "lane_prefix": "Validation context",
    "activity_prefix": "Validation signal",
    "reference_prefix": "Benchmark evidence",
  },
  "execution_regression": {
    "title_prefix": "Execution regression",
    "summary_prefix": "Regression view",
    "partial_summary": (
      "Execution regression falls back to persisted reference provenance because direct execution "
      "deltas are partial."
    ),
    "lane_prefix": "Regression context",
    "activity_prefix": "Execution signal",
    "reference_prefix": "Reference baseline",
  },
  "strategy_tuning": {
    "title_prefix": "Strategy tuning",
    "summary_prefix": "Tuning view",
    "partial_summary": (
      "Strategy tuning falls back to benchmark provenance because direct optimization deltas are partial."
    ),
    "lane_prefix": "Tuning context",
    "activity_prefix": "Tuning signal",
    "reference_prefix": "Benchmark backdrop",
  },
}

COMPARISON_METRIC_COPY: dict[str, dict[str, dict[str, str]]] = {
  "benchmark_validation": {
    "total_return_pct": {
      "annotation": "Validation read: return drift versus the selected benchmark baseline.",
      "positive_delta": "above benchmark",
      "negative_delta": "below benchmark",
      "baseline": "benchmark baseline",
      "missing": "benchmark delta unavailable",
    },
    "max_drawdown_pct": {
      "annotation": "Validation read: downside drift versus the benchmark risk envelope.",
      "positive_delta": "deeper than benchmark",
      "negative_delta": "tighter than benchmark",
      "baseline": "benchmark baseline",
      "missing": "benchmark drawdown delta unavailable",
    },
    "win_rate_pct": {
      "annotation": "Validation read: hit-rate drift versus the benchmark baseline.",
      "positive_delta": "above benchmark",
      "negative_delta": "below benchmark",
      "baseline": "benchmark baseline",
      "missing": "benchmark hit-rate delta unavailable",
    },
    "trade_count": {
      "annotation": "Validation read: participation and pacing drift versus the benchmark.",
      "positive_delta": "above benchmark",
      "negative_delta": "below benchmark",
      "baseline": "benchmark baseline",
      "missing": "benchmark activity delta unavailable",
    },
  },
  "execution_regression": {
    "total_return_pct": {
      "annotation": "Regression read: return movement is treated as execution drift.",
      "positive_delta": "return lift",
      "negative_delta": "return regression",
      "baseline": "regression baseline",
      "missing": "return regression unavailable",
    },
    "max_drawdown_pct": {
      "annotation": "Regression read: higher drawdown is treated as risk regression.",
      "positive_delta": "extra drawdown",
      "negative_delta": "risk improvement",
      "baseline": "regression baseline",
      "missing": "drawdown regression unavailable",
    },
    "win_rate_pct": {
      "annotation": "Regression read: hit-rate movement is treated as execution drift.",
      "positive_delta": "hit-rate lift",
      "negative_delta": "hit-rate regression",
      "baseline": "regression baseline",
      "missing": "hit-rate regression unavailable",
    },
    "trade_count": {
      "annotation": "Regression read: trade-flow changes point to execution behavior drift.",
      "positive_delta": "extra activity",
      "negative_delta": "reduced activity",
      "baseline": "regression baseline",
      "missing": "activity regression unavailable",
    },
  },
  "strategy_tuning": {
    "total_return_pct": {
      "annotation": "Tuning read: return deltas show optimization edge versus the baseline.",
      "positive_delta": "tuning edge",
      "negative_delta": "tuning gap",
      "baseline": "tuning baseline",
      "missing": "tuning delta unavailable",
    },
    "max_drawdown_pct": {
      "annotation": "Tuning read: lower drawdown marks a cleaner optimization tradeoff.",
      "positive_delta": "drawdown penalty",
      "negative_delta": "drawdown improvement",
      "baseline": "tuning baseline",
      "missing": "drawdown tuning delta unavailable",
    },
    "win_rate_pct": {
      "annotation": "Tuning read: hit-rate deltas show signal-quality tradeoffs.",
      "positive_delta": "hit-rate edge",
      "negative_delta": "hit-rate gap",
      "baseline": "tuning baseline",
      "missing": "hit-rate tuning delta unavailable",
    },
    "trade_count": {
      "annotation": "Tuning read: trade-count changes expose activity tradeoffs in the variant.",
      "positive_delta": "activity expansion",
      "negative_delta": "activity reduction",
      "baseline": "tuning baseline",
      "missing": "activity tuning delta unavailable",
    },
  },
}


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
    rerun_boundary_id: str | None = None,
  ) -> list[RunRecord]:
    return self._runs.list_runs(
      mode=self._mode_service.normalize(mode),
      strategy_id=strategy_id,
      strategy_version=strategy_version,
      rerun_boundary_id=rerun_boundary_id,
    )

  def get_run(self, run_id: str) -> RunRecord | None:
    return self._runs.get_run(run_id)

  def rerun_backtest_from_boundary(self, *, rerun_boundary_id: str) -> RunRecord:
    return self._rerun_from_boundary(
      rerun_boundary_id=rerun_boundary_id,
      target_mode=RunMode.BACKTEST,
      requested_mode_label=RunMode.BACKTEST.value,
    )

  def rerun_sandbox_from_boundary(self, *, rerun_boundary_id: str) -> RunRecord:
    return self._rerun_from_boundary(
      rerun_boundary_id=rerun_boundary_id,
      target_mode=RunMode.SANDBOX,
      requested_mode_label=RunMode.SANDBOX.value,
    )

  def rerun_paper_from_boundary(self, *, rerun_boundary_id: str) -> RunRecord:
    return self._rerun_from_boundary(
      rerun_boundary_id=rerun_boundary_id,
      target_mode=RunMode.PAPER,
      requested_mode_label=RunMode.PAPER.value,
    )

  def compare_runs(self, *, run_ids: list[str], intent: str | None = None) -> RunComparison:
    normalized_run_ids = _normalize_run_ids(run_ids)
    if len(normalized_run_ids) < 2:
      raise ValueError("Run comparison requires at least two unique run IDs.")
    resolved_intent = _normalize_comparison_intent(intent)

    runs = self._runs.compare_runs(normalized_run_ids)
    run_by_id = {run.config.run_id: run for run in runs}
    missing_run_ids = [run_id for run_id in normalized_run_ids if run_id not in run_by_id]
    if missing_run_ids:
      raise LookupError(f"Run not found: {', '.join(missing_run_ids)}")

    ordered_runs = [run_by_id[run_id] for run_id in normalized_run_ids]
    baseline_run = ordered_runs[0]
    metric_rows = tuple(
      _build_comparison_metric_row(
        runs=ordered_runs,
        baseline_run=baseline_run,
        intent=resolved_intent,
        key=key,
        label=label,
        unit=unit,
        higher_is_better=higher_is_better,
      )
      for key, label, unit, higher_is_better in COMPARISON_METRICS
    )
    metric_row_by_key = {row.key: row for row in metric_rows}
    ranked_narratives = _rank_comparison_narratives([
      narrative
      for run in ordered_runs[1:]
      if (
        narrative := _build_comparison_narrative(
          baseline_run=baseline_run,
          run=run,
          intent=resolved_intent,
          metric_row_by_key=metric_row_by_key,
        )
      ) is not None
    ])
    return RunComparison(
      requested_run_ids=tuple(normalized_run_ids),
      intent=resolved_intent,
      baseline_run_id=baseline_run.config.run_id,
      runs=tuple(_serialize_comparison_run(run) for run in ordered_runs),
      metric_rows=metric_rows,
      narratives=tuple(ranked_narratives),
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
      self._attach_rerun_boundary(run)
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
    replay_bars: int | None = 96,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
  ) -> RunRecord:
    return self._start_preview_run(
      target_mode=RunMode.SANDBOX,
      strategy_id=strategy_id,
      symbol=symbol,
      timeframe=timeframe,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      replay_bars=replay_bars,
      start_at=start_at,
      end_at=end_at,
    )

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
    replay_bars: int | None = 96,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
  ) -> RunRecord:
    return self._start_paper_session(
      strategy_id=strategy_id,
      symbol=symbol,
      timeframe=timeframe,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      replay_bars=replay_bars,
      start_at=start_at,
      end_at=end_at,
    )

  def _start_preview_run(
    self,
    *,
    target_mode: RunMode,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict,
    replay_bars: int | None = 96,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
  ) -> RunRecord:
    strategy, metadata, strategy_snapshot = self._prepare_strategy(strategy_id=strategy_id, parameters=parameters)
    config = RunConfig(
      run_id=str(uuid4()),
      mode=target_mode,
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
        status=RunStatus.FAILED,
        provenance=RunProvenance(lane="reference", strategy=strategy_snapshot),
      )
      run.notes.append(
        "Reference Freqtrade strategies are exposed for cataloging and backtest delegation. "
        f"{target_mode.value.capitalize()} trading remains on the native engine for now."
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
        mode=target_mode,
        mode_service=self._mode_service,
        replay_bars=replay_bars,
      )
    return self._runs.save_run(run)

  def _start_paper_session(
    self,
    *,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict,
    replay_bars: int | None = 96,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
  ) -> RunRecord:
    strategy, metadata, strategy_snapshot = self._prepare_strategy(strategy_id=strategy_id, parameters=parameters)
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
      start_at=start_at,
      end_at=end_at,
    )
    if metadata.runtime == "freqtrade_reference":
      run = RunRecord(
        config=config,
        status=RunStatus.FAILED,
        provenance=RunProvenance(lane="reference", strategy=strategy_snapshot),
      )
      run.notes.append(
        "Reference Freqtrade strategies are exposed for cataloging and backtest delegation. "
        "Paper trading remains on the native engine for now."
      )
      return self._runs.save_run(run)

    loaded = self._data_engine.load_frame(config=config, active_bars=replay_bars)
    run = self._run_supervisor.create_native_run(config=config, strategy=strategy_snapshot)
    run.provenance.market_data = loaded.lineage
    run.provenance.market_data_by_symbol = loaded.lineage_by_symbol
    self._attach_rerun_boundary(run)
    data = loaded.frame
    if data.empty:
      run.notes.append("No candles available for the requested range.")
      run.status = RunStatus.FAILED
      return self._runs.save_run(run)

    enriched = strategy.build_feature_frame(data, config.parameters)
    required_bars = max(strategy.warmup_spec().required_bars, 2)
    if len(enriched) < required_bars:
      run.status = RunStatus.FAILED
      run.notes.append(
        f"Paper session requires at least {required_bars} candles to prime the current strategy state."
      )
      return self._runs.save_run(run)

    cache = StateCache(
      instrument_id=f"{config.venue}:{config.symbols[0]}",
      cash=config.initial_cash,
    )
    history = enriched.iloc[:]
    latest_row = history.iloc[-1]
    state = cache.snapshot(
      timestamp=latest_row["timestamp"].to_pydatetime(),
      parameters=config.parameters,
    )
    decision = strategy.evaluate(history, config.parameters, state)
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
    self._run_supervisor.start_mode(
      run=run,
      mode=RunMode.PAPER,
      mode_service=self._mode_service,
    )
    primed_candle_count = run.provenance.market_data.candle_count if run.provenance.market_data is not None else 0
    run.notes.insert(
      0,
      f"Paper session primed from the latest market snapshot using {primed_candle_count} candles.",
    )
    return self._runs.save_run(run)

  def stop_sandbox_run(self, run_id: str) -> RunRecord | None:
    run = self._runs.get_run(run_id)
    if run is None:
      return None
    self._run_supervisor.stop(run, reason="Sandbox run stopped by operator.")
    return self._runs.save_run(run)

  def stop_paper_run(self, run_id: str) -> RunRecord | None:
    run = self._runs.get_run(run_id)
    if run is None:
      return None
    self._run_supervisor.stop(run, reason="Paper run stopped by operator.")
    return self._runs.save_run(run)

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
    self._attach_rerun_boundary(run)
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

  def _attach_rerun_boundary(self, run: RunRecord) -> None:
    market_data = run.provenance.market_data
    if market_data is None:
      run.provenance.rerun_boundary_id = None
      run.provenance.rerun_boundary_state = "range_only"
      return

    strategy = run.provenance.strategy
    symbol_checkpoint_ids = {
      symbol: lineage.sync_checkpoint_id
      for symbol, lineage in sorted(run.provenance.market_data_by_symbol.items())
      if lineage.sync_checkpoint_id is not None
    }
    resolved_parameters = (
      deepcopy(strategy.parameter_snapshot.resolved)
      if strategy is not None
      else deepcopy(run.config.parameters)
    )
    run.provenance.rerun_boundary_id = build_rerun_boundary_identity(
      lane=run.provenance.lane,
      mode=run.config.mode.value,
      strategy_id=run.config.strategy_id,
      strategy_version=run.config.strategy_version,
      resolved_parameters=resolved_parameters,
      venue=run.config.venue,
      symbols=run.config.symbols,
      timeframe=run.config.timeframe,
      initial_cash=run.config.initial_cash,
      fee_rate=run.config.fee_rate,
      slippage_bps=run.config.slippage_bps,
      market_data_reproducibility_state=market_data.reproducibility_state,
      market_data_dataset_identity=market_data.dataset_identity,
      market_data_sync_checkpoint_id=market_data.sync_checkpoint_id,
      market_data_symbol_checkpoint_ids=symbol_checkpoint_ids,
      requested_start_at=market_data.requested_start_at,
      requested_end_at=market_data.requested_end_at,
      effective_start_at=market_data.effective_start_at,
      effective_end_at=market_data.effective_end_at,
      candle_count=market_data.candle_count,
      reference_id=run.provenance.reference_id,
      reference_version=run.provenance.reference_version,
      integration_mode=run.provenance.integration_mode,
      external_command=run.provenance.external_command,
    )
    run.provenance.rerun_boundary_state = market_data.reproducibility_state

  def _resolve_rerun_source(self, *, rerun_boundary_id: str) -> RunRecord:
    candidates = self._runs.list_runs(rerun_boundary_id=rerun_boundary_id)
    if not candidates:
      raise LookupError(f"Rerun boundary not found: {rerun_boundary_id}")
    completed = [run for run in candidates if run.status == RunStatus.COMPLETED]
    return completed[0] if completed else candidates[0]

  def _rerun_from_boundary(
    self,
    *,
    rerun_boundary_id: str,
    target_mode: RunMode,
    requested_mode_label: str,
  ) -> RunRecord:
    source_run = self._resolve_rerun_source(rerun_boundary_id=rerun_boundary_id)
    if len(source_run.config.symbols) != 1:
      raise ValueError(f"Explicit rerun currently supports only single-symbol {requested_mode_label} runs.")

    rerun_start_at = self._resolve_rerun_start_at(source_run)
    rerun_end_at = self._resolve_rerun_end_at(source_run)
    rerun_parameters = self._resolve_rerun_parameters(source_run)
    symbol = source_run.config.symbols[0]
    preview_window_note: str | None = None

    if target_mode == RunMode.BACKTEST:
      rerun = self.run_backtest(
        strategy_id=source_run.config.strategy_id,
        symbol=symbol,
        timeframe=source_run.config.timeframe,
        initial_cash=source_run.config.initial_cash,
        fee_rate=source_run.config.fee_rate,
        slippage_bps=source_run.config.slippage_bps,
        parameters=rerun_parameters,
        start_at=rerun_start_at,
        end_at=rerun_end_at,
      )
    elif target_mode in {RunMode.SANDBOX, RunMode.PAPER}:
      preview_start_at, preview_end_at, preview_replay_bars = self._resolve_preview_rerun_window(source_run)
      preview_label = target_mode.value.capitalize()
      if target_mode == RunMode.SANDBOX:
        if preview_replay_bars is None:
          preview_window_note = f"{preview_label} rerun locked execution to the stored effective market-data window."
        else:
          preview_window_note = (
            f"{preview_label} rerun replay preserved the stored {source_run.config.mode.value} bar window."
          )
        rerun = self._start_preview_run(
          target_mode=target_mode,
          strategy_id=source_run.config.strategy_id,
          symbol=symbol,
          timeframe=source_run.config.timeframe,
          initial_cash=source_run.config.initial_cash,
          fee_rate=source_run.config.fee_rate,
          slippage_bps=source_run.config.slippage_bps,
          parameters=rerun_parameters,
          replay_bars=preview_replay_bars,
          start_at=preview_start_at,
          end_at=preview_end_at,
        )
      else:
        if preview_replay_bars is None:
          preview_window_note = "Paper rerun seeded the current paper session from the stored effective market-data window."
        else:
          preview_window_note = "Paper rerun seeded the current paper session from the stored priming window."
        rerun = self._start_paper_session(
          strategy_id=source_run.config.strategy_id,
          symbol=symbol,
          timeframe=source_run.config.timeframe,
          initial_cash=source_run.config.initial_cash,
          fee_rate=source_run.config.fee_rate,
          slippage_bps=source_run.config.slippage_bps,
          parameters=rerun_parameters,
          replay_bars=preview_replay_bars,
          start_at=preview_start_at,
          end_at=preview_end_at,
        )
    else:
      raise ValueError(f"Unsupported rerun target mode: {target_mode.value}")

    return self._persist_explicit_rerun(
      rerun=rerun,
      source_run=source_run,
      rerun_boundary_id=rerun_boundary_id,
      requested_mode_label=requested_mode_label,
      preview_window_note=preview_window_note,
    )

  def _persist_explicit_rerun(
    self,
    *,
    rerun: RunRecord,
    source_run: RunRecord,
    rerun_boundary_id: str,
    requested_mode_label: str,
    preview_window_note: str | None = None,
  ) -> RunRecord:
    rerun.provenance.rerun_source_run_id = source_run.config.run_id
    rerun.provenance.rerun_target_boundary_id = rerun_boundary_id
    rerun.provenance.rerun_match_status = (
      "matched"
      if rerun.provenance.rerun_boundary_id == rerun_boundary_id
      else "drifted"
    )
    rerun.notes.insert(
      0,
      f"Explicit {requested_mode_label} rerun from boundary {rerun_boundary_id} using source run {source_run.config.run_id}.",
    )
    if rerun.config.mode in {RunMode.SANDBOX, RunMode.PAPER} and preview_window_note is not None:
      rerun.notes.insert(
        1,
        preview_window_note,
      )
    if rerun.provenance.rerun_match_status == "matched":
      rerun.notes.append("Explicit rerun matched the stored rerun boundary.")
    else:
      rerun.notes.append(
        "Explicit rerun drifted from the stored rerun boundary. "
        f"Expected {rerun_boundary_id}, got {rerun.provenance.rerun_boundary_id or 'unavailable'}."
      )
      if source_run.config.mode != rerun.config.mode:
        rerun.notes.append(
          "Mode-specific rerun boundary drift is expected when replaying a stored boundary into a different execution mode."
        )
    return self._runs.save_run(rerun)

  def _resolve_rerun_parameters(self, run: RunRecord) -> dict:
    strategy = run.provenance.strategy
    if strategy is not None:
      return deepcopy(strategy.parameter_snapshot.resolved)
    return deepcopy(run.config.parameters)

  @staticmethod
  def _resolve_rerun_start_at(run: RunRecord) -> datetime | None:
    market_data = run.provenance.market_data
    if market_data is None:
      return run.config.start_at
    return (
      market_data.effective_start_at
      or market_data.requested_start_at
      or run.config.start_at
    )

  @staticmethod
  def _resolve_rerun_end_at(run: RunRecord) -> datetime | None:
    market_data = run.provenance.market_data
    if market_data is None:
      return run.config.end_at
    return (
      market_data.effective_end_at
      or market_data.requested_end_at
      or run.config.end_at
    )

  @staticmethod
  def _resolve_preview_rerun_window(run: RunRecord) -> tuple[datetime | None, datetime | None, int | None]:
    market_data = run.provenance.market_data
    if (
      run.config.mode in {RunMode.SANDBOX, RunMode.PAPER}
      and run.config.start_at is None
      and run.config.end_at is None
      and market_data is not None
      and market_data.candle_count > 0
    ):
      return None, None, market_data.candle_count
    return (
      TradingApplication._resolve_rerun_start_at(run),
      TradingApplication._resolve_rerun_end_at(run),
      None,
    )


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
    rerun_boundary_id=run.provenance.rerun_boundary_id,
    rerun_boundary_state=run.provenance.rerun_boundary_state,
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
  intent: str,
  key: str,
  label: str,
  unit: str,
  higher_is_better: bool,
) -> RunComparisonMetricRow:
  baseline_value = _resolve_run_metric_value(baseline_run, key)
  values = {
    run.config.run_id: _resolve_run_metric_value(run, key)
    for run in runs
  }
  deltas_vs_baseline = {
    run_id: _calculate_metric_delta(value, baseline_value)
    for run_id, value in values.items()
  }
  delta_annotations = {
    run_id: _build_metric_delta_annotation(
      intent=intent,
      key=key,
      unit=unit,
      is_baseline=run_id == baseline_run.config.run_id,
      higher_is_better=higher_is_better,
      delta=deltas_vs_baseline[run_id],
      value=values[run_id],
    )
    for run_id in values
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
    delta_annotations=delta_annotations,
    annotation=_build_metric_annotation(intent=intent, key=key),
    best_run_id=best_run_id,
  )


def _build_metric_annotation(*, intent: str, key: str) -> str | None:
  return COMPARISON_METRIC_COPY.get(intent, {}).get(key, {}).get("annotation")


def _build_metric_delta_annotation(
  *,
  intent: str,
  key: str,
  unit: str,
  is_baseline: bool,
  higher_is_better: bool,
  delta: float | int | None,
  value: float | int | None,
) -> str:
  copy = COMPARISON_METRIC_COPY.get(intent, {}).get(key, {})
  if is_baseline:
    return copy.get("baseline", "baseline")
  if value is None or delta is None:
    return copy.get("missing", "delta unavailable")
  if delta == 0:
    return "aligned with baseline"

  magnitude = _format_metric_delta_magnitude(delta=delta, unit=unit)
  positive_phrase = copy.get("positive_delta", "above baseline")
  negative_phrase = copy.get("negative_delta", "below baseline")

  if higher_is_better:
    phrase = positive_phrase if delta > 0 else negative_phrase
  else:
    phrase = positive_phrase if delta > 0 else negative_phrase
  return f"{magnitude} {phrase}"


def _format_metric_delta_magnitude(
  *,
  delta: float | int,
  unit: str,
) -> str:
  magnitude = abs(float(delta))
  if unit == "pct":
    rounded = round(magnitude, 2)
    return f"{rounded:g} pts"
  rounded = round(magnitude, 2)
  if rounded.is_integer():
    return str(int(rounded))
  return f"{rounded:g}"


def _build_comparison_narrative(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
  intent: str,
  metric_row_by_key: dict[str, RunComparisonMetricRow],
) -> RunComparisonNarrative | None:
  comparison_type = _classify_comparison_type(baseline_run, run)
  target_label = _comparison_run_label(run)
  baseline_label = _comparison_run_label(baseline_run)
  target_subject = _comparison_subject_label(run)

  total_return_delta = _metric_row_delta(metric_row_by_key, "total_return_pct", run.config.run_id)
  max_drawdown_delta = _metric_row_delta(metric_row_by_key, "max_drawdown_pct", run.config.run_id)
  win_rate_delta = _metric_row_delta(metric_row_by_key, "win_rate_pct", run.config.run_id)
  trade_count_delta = _metric_row_delta(metric_row_by_key, "trade_count", run.config.run_id)

  title = _build_comparison_narrative_title(
    intent=intent,
    comparison_type=comparison_type,
    target_subject=target_subject,
    baseline_label=baseline_label,
    total_return_delta=total_return_delta,
    max_drawdown_delta=max_drawdown_delta,
  )
  summary = _build_comparison_narrative_summary(
    intent=intent,
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
    baseline_label=baseline_label,
    total_return_delta=total_return_delta,
    max_drawdown_delta=max_drawdown_delta,
    win_rate_delta=win_rate_delta,
    trade_count_delta=trade_count_delta,
  )
  bullets = _build_comparison_narrative_bullets(
    intent=intent,
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
    target_label=target_label,
    baseline_label=baseline_label,
    win_rate_delta=win_rate_delta,
    trade_count_delta=trade_count_delta,
  )

  if not title and not summary and not bullets:
    return None

  insight_score = _score_comparison_narrative(
    intent=intent,
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
    total_return_delta=total_return_delta,
    max_drawdown_delta=max_drawdown_delta,
    win_rate_delta=win_rate_delta,
    trade_count_delta=trade_count_delta,
  )

  return RunComparisonNarrative(
    run_id=run.config.run_id,
    baseline_run_id=baseline_run.config.run_id,
    comparison_type=comparison_type,
    title=title or f"{target_subject} diverged from {baseline_label}.",
    summary=summary or f"{target_label} is being compared against {baseline_label}.",
    bullets=tuple(bullets),
    insight_score=insight_score,
  )


def _rank_comparison_narratives(
  narratives: list[RunComparisonNarrative],
) -> list[RunComparisonNarrative]:
  ordered = sorted(
    narratives,
    key=lambda narrative: (-narrative.insight_score, narrative.run_id),
  )
  return [
    replace(
      narrative,
      rank=index + 1,
      is_primary=index == 0,
    )
    for index, narrative in enumerate(ordered)
  ]


def _score_comparison_narrative(
  *,
  intent: str,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
  total_return_delta: float | int | None,
  max_drawdown_delta: float | int | None,
  win_rate_delta: float | int | None,
  trade_count_delta: float | int | None,
) -> float:
  weights = COMPARISON_INTENT_WEIGHTS[intent]
  score = 0.0
  score += abs(float(total_return_delta or 0.0)) * weights["return"]
  score += abs(float(max_drawdown_delta or 0.0)) * weights["drawdown"]
  score += abs(float(win_rate_delta or 0.0)) * weights["win_rate"]
  score += min(abs(float(trade_count_delta or 0.0)), 50.0) * weights["trade_count"]

  if comparison_type == "native_vs_reference":
    score += weights["native_reference_bonus"]
  elif comparison_type == "reference_vs_reference":
    score += weights["reference_bonus"]

  if run.status != baseline_run.status:
    score += weights["status_bonus"]
  if _extract_benchmark_story(run) or _extract_benchmark_story(baseline_run):
    score += weights["benchmark_story_bonus"]
  if score == 0.0 and _has_reference_context(run, baseline_run):
    score = weights["reference_floor"]
  return round(score, 2)


def _normalize_comparison_intent(intent: str | None) -> str:
  if intent in (None, ""):
    return COMPARISON_INTENT_DEFAULT
  if intent not in COMPARISON_INTENT_WEIGHTS:
    supported = ", ".join(sorted(COMPARISON_INTENT_WEIGHTS))
    raise ValueError(f"Unsupported comparison intent: {intent}. Expected one of: {supported}.")
  return intent


def _build_comparison_narrative_title(
  *,
  intent: str,
  comparison_type: str,
  target_subject: str,
  baseline_label: str,
  total_return_delta: float | int | None,
  max_drawdown_delta: float | int | None,
) -> str | None:
  copy = COMPARISON_INTENT_COPY[intent]
  versus_baseline = "the baseline" if comparison_type != "native_vs_reference" else f"the native/reference baseline {baseline_label}"
  if total_return_delta is not None and max_drawdown_delta is not None:
    if intent == "benchmark_validation":
      if total_return_delta > 0 and max_drawdown_delta <= 0:
        return f"{copy['title_prefix']} favors {target_subject}: higher return without extra drawdown versus {versus_baseline}."
      if total_return_delta > 0 and max_drawdown_delta > 0:
        return f"{copy['title_prefix']} shows {target_subject} running hotter than {versus_baseline}: more return, but deeper drawdown."
      if total_return_delta < 0 and max_drawdown_delta <= 0:
        return f"{copy['title_prefix']} shows {target_subject} staying safer than {versus_baseline}, but giving up return."
      if total_return_delta < 0 and max_drawdown_delta > 0:
        return f"{copy['title_prefix']} flags {target_subject} as off-benchmark versus {versus_baseline}."
      return f"{copy['title_prefix']} shows {target_subject} holding close to {versus_baseline}."
    if intent == "execution_regression":
      if total_return_delta > 0 and max_drawdown_delta <= 0:
        return f"{copy['title_prefix']} sees {target_subject} diverging from {versus_baseline}, but not as a degradation."
      if total_return_delta > 0 and max_drawdown_delta > 0:
        return f"{copy['title_prefix']} shows {target_subject} changing risk behavior versus {versus_baseline}."
      if total_return_delta < 0 and max_drawdown_delta <= 0:
        return f"{copy['title_prefix']} shows {target_subject} throttling risk versus {versus_baseline}."
      if total_return_delta < 0 and max_drawdown_delta > 0:
        return f"{copy['title_prefix']} flags {target_subject} as a clear degradation versus {versus_baseline}."
      return f"{copy['title_prefix']} sees only limited drift in {target_subject} versus {versus_baseline}."
    if total_return_delta > 0 and max_drawdown_delta <= 0:
      return f"{copy['title_prefix']} clearly prefers {target_subject} over {versus_baseline}."
    if total_return_delta > 0 and max_drawdown_delta > 0:
      return f"{copy['title_prefix']} treats {target_subject} as the higher-upside variant versus {versus_baseline}, with a drawdown tradeoff."
    if total_return_delta < 0 and max_drawdown_delta <= 0:
      return f"{copy['title_prefix']} treats {target_subject} as the more defensive variant versus {versus_baseline}."
    if total_return_delta < 0 and max_drawdown_delta > 0:
      return f"{copy['title_prefix']} finds little upside in {target_subject} versus {versus_baseline}."
    return f"{copy['title_prefix']} keeps {target_subject} near-neutral against {versus_baseline}."
  if total_return_delta is not None:
    if intent == "strategy_tuning":
      if total_return_delta > 0:
        return f"{copy['title_prefix']} prefers {target_subject} for return potential versus {versus_baseline}."
      if total_return_delta < 0:
        return f"{copy['title_prefix']} sees {target_subject} as lower-upside than {versus_baseline}."
      return f"{copy['title_prefix']} sees no return edge between {target_subject} and {versus_baseline}."
    if total_return_delta > 0:
      return f"{copy['title_prefix']} shows {target_subject} ahead of {versus_baseline} on total return."
    if total_return_delta < 0:
      return f"{copy['title_prefix']} shows {target_subject} trailing {versus_baseline} on total return."
    return f"{copy['title_prefix']} shows {target_subject} matching {versus_baseline} on total return."
  if max_drawdown_delta is not None:
    if max_drawdown_delta < 0:
      return f"{copy['title_prefix']} shows {target_subject} containing drawdown better than {versus_baseline}."
    if max_drawdown_delta > 0:
      return f"{copy['title_prefix']} shows {target_subject} running with deeper drawdown than {versus_baseline}."
    return f"{copy['title_prefix']} shows {target_subject} matching {versus_baseline} on drawdown."
  if comparison_type == "native_vs_reference":
    return f"{copy['title_prefix']} frames {target_subject} as the comparison counterpart to {baseline_label}."
  return f"{copy['title_prefix']} reads {target_subject} against {baseline_label}."


def _build_comparison_narrative_summary(
  *,
  intent: str,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
  baseline_label: str,
  total_return_delta: float | int | None,
  max_drawdown_delta: float | int | None,
  win_rate_delta: float | int | None,
  trade_count_delta: float | int | None,
) -> str | None:
  copy = COMPARISON_INTENT_COPY[intent]
  metric_shifts: list[str] = []
  if total_return_delta is not None:
    metric_shifts.append(f"return {_format_metric_delta(total_return_delta, 'pct_points')}")
  if max_drawdown_delta is not None:
    metric_shifts.append(f"drawdown {_format_metric_delta(max_drawdown_delta, 'pct_points')}")
  if win_rate_delta is not None:
    metric_shifts.append(f"win rate {_format_metric_delta(win_rate_delta, 'pct_points')}")
  if trade_count_delta is not None:
    metric_shifts.append(f"trades {_format_metric_delta(trade_count_delta, 'count')}")
  if metric_shifts:
    if intent == "benchmark_validation":
      return f"{copy['summary_prefix']} treats these shifts as benchmark drift against {baseline_label}: {', '.join(metric_shifts)}."
    if intent == "execution_regression":
      return f"{copy['summary_prefix']} interprets these changes as execution drift against {baseline_label}: {', '.join(metric_shifts)}."
    return f"{copy['summary_prefix']} reads these changes as optimization tradeoffs against {baseline_label}: {', '.join(metric_shifts)}."

  if comparison_type == "native_vs_reference" and _has_reference_context(run, baseline_run):
    return copy["partial_summary"]
  if run.status != baseline_run.status:
    return f"{copy['summary_prefix']} also notes a status split: {run.status} versus {baseline_run.status}."
  return None


def _build_comparison_narrative_bullets(
  *,
  intent: str,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
  target_label: str,
  baseline_label: str,
  win_rate_delta: float | int | None,
  trade_count_delta: float | int | None,
) -> list[str]:
  bullets: list[str] = []

  lane_context = _build_lane_context_bullet(
    intent=intent,
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
  )
  if lane_context is not None:
    bullets.append(lane_context)

  activity_context = _build_activity_context_bullet(
    intent=intent,
    run=run,
    trade_count_delta=trade_count_delta,
    win_rate_delta=win_rate_delta,
  )
  if activity_context is not None:
    bullets.append(activity_context)

  reference_story = _build_reference_story_bullet(intent=intent, baseline_run=baseline_run, run=run)
  if reference_story is not None:
    bullets.append(reference_story)

  if not bullets and comparison_type == "native_vs_reference":
    bullets.append(f"{COMPARISON_INTENT_COPY[intent]['lane_prefix']}: {target_label} is the reference/native counterpart to {baseline_label}.")
  return bullets[:3]


def _build_lane_context_bullet(
  *,
  intent: str,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
) -> str | None:
  if comparison_type != "native_vs_reference":
    return None
  copy = COMPARISON_INTENT_COPY[intent]
  reference_run = run if run.provenance.lane == "reference" else baseline_run
  native_run = baseline_run if reference_run is run else run
  reference_label = _comparison_run_label(reference_run)
  integration_mode = reference_run.provenance.integration_mode or "external_runtime"
  return (
    f"{copy['lane_prefix']}: native engine {_comparison_run_label(native_run)} is being read against "
    f"reference benchmark {reference_label} via {integration_mode}."
  )


def _build_activity_context_bullet(
  *,
  intent: str,
  run: RunRecord,
  trade_count_delta: float | int | None,
  win_rate_delta: float | int | None,
) -> str | None:
  copy = COMPARISON_INTENT_COPY[intent]
  trade_count = _resolve_run_metric_value(run, "trade_count")
  win_rate = _resolve_run_metric_value(run, "win_rate_pct")
  segments: list[str] = []
  if trade_count is not None:
    segment = f"trade flow landed at {trade_count}"
    if trade_count_delta is not None:
      segment += f" ({_format_metric_delta(trade_count_delta, 'count')} vs baseline)"
    segments.append(segment)
  if win_rate is not None:
    segment = f"win rate closed at {win_rate}%"
    if win_rate_delta is not None:
      segment += f" ({_format_metric_delta(win_rate_delta, 'pct_points')} vs baseline)"
    segments.append(segment)
  if not segments:
    return None
  return f"{copy['activity_prefix']}: " + "; ".join(segments) + "."


def _build_reference_story_bullet(
  *,
  intent: str,
  baseline_run: RunRecord,
  run: RunRecord,
) -> str | None:
  copy = COMPARISON_INTENT_COPY[intent]
  reference_run = None
  if run.provenance.lane == "reference":
    reference_run = run
  elif baseline_run.provenance.lane == "reference":
    reference_run = baseline_run
  if reference_run is None:
    return None
  benchmark_story = _extract_benchmark_story(reference_run)
  if not benchmark_story:
    return None
  for key in ("headline", "signal_context", "exit_context", "market_context", "pair_context", "portfolio_context"):
    value = benchmark_story.get(key)
    if isinstance(value, str) and value:
      return f"{copy['reference_prefix']}: {value}"
  return None


def _classify_comparison_type(baseline_run: RunRecord, run: RunRecord) -> str:
  lanes = {baseline_run.provenance.lane, run.provenance.lane}
  if lanes == {"native", "reference"}:
    return "native_vs_reference"
  if lanes == {"reference"}:
    return "reference_vs_reference"
  if lanes == {"native"}:
    return "native_vs_native"
  return "run_vs_baseline"


def _comparison_run_label(run: RunRecord) -> str:
  if run.provenance.reference is not None and run.provenance.reference.title:
    return run.provenance.reference.title
  if run.provenance.strategy is not None and run.provenance.strategy.name:
    return run.provenance.strategy.name
  return run.config.strategy_id


def _comparison_subject_label(run: RunRecord) -> str:
  label = _comparison_run_label(run)
  if run.provenance.lane == "reference":
    return f"Reference benchmark {label}"
  if run.provenance.lane == "native":
    return f"Native run {label}"
  return label


def _has_reference_context(run: RunRecord, baseline_run: RunRecord) -> bool:
  return any(candidate.provenance.lane == "reference" for candidate in (run, baseline_run))


def _metric_row_delta(
  metric_row_by_key: dict[str, RunComparisonMetricRow],
  key: str,
  run_id: str,
) -> float | int | None:
  metric_row = metric_row_by_key.get(key)
  if metric_row is None:
    return None
  return metric_row.deltas_vs_baseline.get(run_id)


def _resolve_run_metric_value(run: RunRecord, key: str) -> float | int | None:
  direct_value = _coerce_metric_value(run.metrics.get(key))
  if direct_value is not None:
    return direct_value
  return _extract_benchmark_metric_value(run, key)


def _extract_benchmark_metric_value(run: RunRecord, key: str) -> float | int | None:
  summary_key_map = {
    "total_return_pct": "profit_total_pct",
    "max_drawdown_pct": "max_drawdown_pct",
    "trade_count": "trade_count",
    "win_rate_pct": "win_rate_pct",
  }
  summary_key = summary_key_map.get(key)
  if summary_key is None:
    return None

  artifacts = sorted(
    run.provenance.benchmark_artifacts,
    key=lambda artifact: _benchmark_artifact_priority(artifact.kind),
  )
  for artifact in artifacts:
    value = _coerce_metric_value(artifact.summary.get(summary_key))
    if value is not None:
      return value
    if key == "win_rate_pct":
      for section_name, row_key in (
        ("strategy_comparison", "best"),
        ("pair_metrics", "total"),
      ):
        section = artifact.sections.get(section_name)
        if not isinstance(section, dict):
          continue
        candidate_row = section.get(row_key)
        if isinstance(candidate_row, dict):
          value = _coerce_metric_value(candidate_row.get(summary_key))
          if value is not None:
            return value
        preview = section.get("preview")
        if isinstance(preview, list) and preview:
          first_row = preview[0]
          if isinstance(first_row, dict):
            value = _coerce_metric_value(first_row.get(summary_key))
            if value is not None:
              return value
  return None


def _extract_benchmark_story(run: RunRecord) -> dict[str, str]:
  artifacts = sorted(
    run.provenance.benchmark_artifacts,
    key=lambda artifact: _benchmark_artifact_priority(artifact.kind),
  )
  for artifact in artifacts:
    story = artifact.sections.get("benchmark_story")
    if not isinstance(story, dict):
      continue
    normalized_story = {
      key: value
      for key, value in story.items()
      if isinstance(value, str) and value
    }
    if normalized_story:
      return normalized_story
  return {}


def _benchmark_artifact_priority(kind: str) -> int:
  priorities = {
    "result_snapshot": 0,
    "result_snapshot_root": 1,
    "result_manifest": 2,
  }
  return priorities.get(kind, 100)


def _format_metric_delta(value: float | int | None, unit: str) -> str:
  if value is None:
    return "n/a"
  prefix = "+" if value > 0 else ""
  if unit == "pct_points":
    return f"{prefix}{value} pts"
  if unit == "count":
    suffix = "trade" if value in {-1, 1} else "trades"
    return f"{prefix}{value} {suffix}"
  return f"{prefix}{value}"


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
