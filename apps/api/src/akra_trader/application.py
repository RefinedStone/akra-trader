from __future__ import annotations

from dataclasses import replace
from datetime import UTC
from datetime import datetime
from typing import Any
from typing import Callable
from uuid import uuid4

import pandas as pd

from akra_trader.domain.models import OperationLog
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunProvenance
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import RuntimeSessionState
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.models import StrategyDecisionContext
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import StrategyLifecycle
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import StrategyParameterSnapshot
from akra_trader.domain.models import StrategySnapshot
from akra_trader.domain.models import WarmupSpec
from akra_trader.domain.services import summarize_performance
from akra_trader.ports import DecisionEnginePort
from akra_trader.ports import MarketDataPort
from akra_trader.ports import StrategyCatalogPort
from akra_trader.ports import VenueExecutionPort
from akra_trader.runtime import DataEngine
from akra_trader.runtime import ExecutionEngine
from akra_trader.runtime import ExecutionModeService
from akra_trader.runtime import RunSupervisor
from akra_trader.runtime import StateCache
from akra_trader.strategies.llm import ExternalDecisionStrategy


class HoldDecisionEngine(DecisionEnginePort):
  def decide(self, context: StrategyDecisionContext) -> StrategyDecisionEnvelope:
    signal = SignalDecision(
      timestamp=context.timestamp,
      action=SignalAction.HOLD,
      size_fraction=0.0,
      confidence=0.0,
      tags=("isolated_llm_interface",),
      reason="external_decision_engine_not_configured",
    )
    return StrategyDecisionEnvelope(
      signal=signal,
      rationale="LLM provider adapters are intentionally isolated from the core runtime.",
      context=context,
      trace={
        "provider": None,
        "boundary": "DecisionEnginePort",
        "isolation_state": "interface_only",
      },
    )


class TradingApplication:
  def __init__(
    self,
    *,
    market_data: MarketDataPort,
    strategies: StrategyCatalogPort,
    runs: Any,
    venue_execution: VenueExecutionPort | None = None,
    decision_engine: DecisionEnginePort | None = None,
    guarded_live_venue: str = "binance",
    guarded_live_execution_enabled: bool = False,
    sandbox_worker_heartbeat_interval_seconds: int = 15,
    sandbox_worker_heartbeat_timeout_seconds: int = 45,
    guarded_live_worker_heartbeat_interval_seconds: int = 15,
    guarded_live_worker_heartbeat_timeout_seconds: int = 45,
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    self._clock = clock or (lambda: datetime.now(UTC))
    self._market_data = market_data
    self._strategies = strategies
    self._runs = runs
    self._venue_execution = venue_execution
    self._decision_engine = decision_engine or HoldDecisionEngine()
    self._mode_service = ExecutionModeService()
    self._data_engine = DataEngine(market_data)
    self._execution_engine = ExecutionEngine()
    self._run_supervisor = RunSupervisor()
    self._guarded_live_venue = guarded_live_venue
    self._guarded_live_execution_enabled = guarded_live_execution_enabled
    self._sandbox_worker_kind = "sandbox_native_worker"
    self._guarded_live_worker_kind = "guarded_live_native_worker"
    self._sandbox_worker_heartbeat_interval_seconds = sandbox_worker_heartbeat_interval_seconds
    self._sandbox_worker_heartbeat_timeout_seconds = sandbox_worker_heartbeat_timeout_seconds
    self._guarded_live_worker_heartbeat_interval_seconds = (
      guarded_live_worker_heartbeat_interval_seconds
    )
    self._guarded_live_worker_heartbeat_timeout_seconds = (
      guarded_live_worker_heartbeat_timeout_seconds
    )

    self._llm_strategy = ExternalDecisionStrategy(self._decision_engine)
    self._record_log(
      layer="log",
      event_type="runtime_initialized",
      message="Core trading runtime initialized with backtest, sandbox, data, live, logs, and LLM strategy layers.",
    )

  def health(self) -> dict[str, Any]:
    return {
      "status": "ok",
      "layers": ("backtest", "sandbox", "data", "live", "logs", "llm_strategy"),
      "market_data_provider": self.get_market_data_status().provider,
      "guarded_live": {
        "venue": self._guarded_live_venue,
        "enabled": self._guarded_live_execution_enabled,
      },
    }

  def list_strategies(self) -> list[StrategyMetadata]:
    metadata = self._strategies.list_strategies()
    llm_metadata = self._llm_strategy.describe()
    return sorted([*metadata, llm_metadata], key=lambda item: item.strategy_id)

  def get_llm_strategy_interface(self) -> dict[str, Any]:
    metadata = self._llm_strategy.describe()
    return {
      "strategy_id": metadata.strategy_id,
      "name": metadata.name,
      "runtime": metadata.runtime,
      "lifecycle": metadata.lifecycle.stage,
      "decision_port": "DecisionEnginePort",
      "provider_adapter": None,
      "isolation_state": "interface_only",
      "trace_envelope": {
        "signal": "SignalDecision",
        "rationale": "string",
        "context": "StrategyDecisionContext",
        "execution": "ExecutionPlan",
        "trace": "provider-neutral dict",
      },
    }

  def run_backtest(
    self,
    *,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict[str, Any],
    start_at: datetime | None = None,
    end_at: datetime | None = None,
  ) -> RunRecord:
    run = self._create_simulated_run(
      mode=RunMode.BACKTEST,
      strategy_id=strategy_id,
      symbol=symbol,
      timeframe=timeframe,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      active_bars=None,
      start_at=start_at,
      end_at=end_at,
    )
    if run.status != RunStatus.FAILED:
      self._run_supervisor.complete(run)
    self._runs.save_run(run)
    self._append_run_note(
      run,
      layer="backtest",
      event_type="backtest_completed" if run.status == RunStatus.COMPLETED else "backtest_failed",
      message=f"Backtest {run.status.value} for {symbol} on {timeframe}.",
      severity="info" if run.status == RunStatus.COMPLETED else "error",
    )
    self._runs.save_run(run)
    return run

  def start_sandbox_run(
    self,
    *,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict[str, Any],
    replay_bars: int | None = 96,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
  ) -> RunRecord:
    run = self._create_simulated_run(
      mode=RunMode.SANDBOX,
      strategy_id=strategy_id,
      symbol=symbol,
      timeframe=timeframe,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      active_bars=replay_bars,
      start_at=start_at,
      end_at=end_at,
    )
    if run.status != RunStatus.FAILED:
      self._run_supervisor.start_mode(
        run=run,
        mode=RunMode.SANDBOX,
        mode_service=self._mode_service,
        replay_bars=replay_bars,
      )
      self._start_runtime_session(run, mode=RunMode.SANDBOX)
    self._runs.save_run(run)
    self._append_run_note(
      run,
      layer="sandbox",
      event_type="sandbox_started" if run.status == RunStatus.RUNNING else "sandbox_failed",
      message=f"Sandbox run {run.status.value} for {symbol} on {timeframe}.",
      severity="info" if run.status == RunStatus.RUNNING else "error",
    )
    self._runs.save_run(run)
    return run

  def start_live_run(
    self,
    *,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict[str, Any],
    replay_bars: int | None = 96,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
  ) -> RunRecord:
    self._ensure_live_launch_allowed()
    run = self._create_simulated_run(
      mode=RunMode.LIVE,
      strategy_id=strategy_id,
      symbol=symbol,
      timeframe=timeframe,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      active_bars=replay_bars,
      start_at=start_at,
      end_at=end_at,
    )
    if run.status != RunStatus.FAILED:
      self._run_supervisor.start_mode(
        run=run,
        mode=RunMode.LIVE,
        mode_service=self._mode_service,
        replay_bars=replay_bars,
      )
      self._start_runtime_session(run, mode=RunMode.LIVE)
    self._runs.save_run(run)
    self._append_run_note(
      run,
      layer="live",
      event_type="live_started" if run.status == RunStatus.RUNNING else "live_failed",
      message=f"Guarded-live run {run.status.value} for {symbol} on {self._guarded_live_venue}.",
      severity="info" if run.status == RunStatus.RUNNING else "error",
    )
    self._runs.save_run(run)
    return run

  def stop_run(self, run_id: str) -> RunRecord:
    run = self._require_run(run_id)
    if run.status == RunStatus.RUNNING:
      self._run_supervisor.stop(run, reason="Stopped by operator.")
      self._runs.save_run(run)
      self._append_run_note(
        run,
        layer=run.config.mode.value,
        event_type="run_stopped",
        message=f"{run.config.mode.value} run stopped by operator.",
      )
      self._runs.save_run(run)
    return run

  def list_runs(self, mode: str | None = None) -> list[RunRecord]:
    normalized_mode = self._mode_service.normalize(mode)
    return self._runs.list_runs(normalized_mode)

  def get_run(self, run_id: str) -> RunRecord | None:
    return self._runs.get_run(run_id)

  def get_run_orders(self, run_id: str):
    return list(self._require_run(run_id).orders)

  def get_run_positions(self, run_id: str):
    return list(self._require_run(run_id).positions.values())

  def get_run_metrics(self, run_id: str) -> dict[str, Any]:
    return dict(self._require_run(run_id).metrics)

  def get_run_logs(self, run_id: str) -> list[OperationLog]:
    self._require_run(run_id)
    return self.list_operation_logs(run_id=run_id)

  def list_operation_logs(
    self,
    *,
    run_id: str | None = None,
    mode: str | None = None,
    severity: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = 200,
  ) -> list[OperationLog]:
    return self._runs.list_logs(
      run_id=run_id,
      mode=mode,
      severity=severity,
      since=since,
      until=until,
      limit=limit,
    )

  def get_market_data_status(self, timeframe: str = "5m"):
    return self._market_data.get_status(timeframe)

  def get_market_data_candles(
    self,
    *,
    symbol: str,
    timeframe: str,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int | None = None,
  ):
    candles = self._market_data.get_candles(
      symbol=symbol,
      timeframe=timeframe,
      start_at=start_at,
      end_at=end_at,
      limit=limit,
    )
    self._record_log(
      layer="data",
      event_type="candles_read",
      message=f"Read {len(candles)} candles for {symbol} on {timeframe}.",
      payload={"symbol": symbol, "timeframe": timeframe, "count": len(candles)},
    )
    return candles

  def maintain_sandbox_worker_sessions(
    self,
    *,
    force_recovery: bool = False,
    recovery_reason: str = "heartbeat_timeout",
  ) -> dict[str, int]:
    return self._maintain_worker_sessions(
      mode=RunMode.SANDBOX,
      worker_kind=self._sandbox_worker_kind,
      heartbeat_interval_seconds=self._sandbox_worker_heartbeat_interval_seconds,
      heartbeat_timeout_seconds=self._sandbox_worker_heartbeat_timeout_seconds,
      force_recovery=force_recovery,
      recovery_reason=recovery_reason,
    )

  def maintain_guarded_live_worker_sessions(
    self,
    *,
    force_recovery: bool = False,
    recovery_reason: str = "heartbeat_timeout",
  ) -> dict[str, int]:
    return self._maintain_worker_sessions(
      mode=RunMode.LIVE,
      worker_kind=self._guarded_live_worker_kind,
      heartbeat_interval_seconds=self._guarded_live_worker_heartbeat_interval_seconds,
      heartbeat_timeout_seconds=self._guarded_live_worker_heartbeat_timeout_seconds,
      force_recovery=force_recovery,
      recovery_reason=recovery_reason,
    )

  def _create_simulated_run(
    self,
    *,
    mode: RunMode,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict[str, Any],
    active_bars: int | None,
    start_at: datetime | None,
    end_at: datetime | None,
  ) -> RunRecord:
    strategy, metadata, strategy_snapshot, resolved_parameters = self._prepare_strategy(
      strategy_id=strategy_id,
      parameters=parameters,
    )
    config = RunConfig(
      run_id=str(uuid4()),
      mode=mode,
      strategy_id=metadata.strategy_id,
      strategy_version=metadata.version,
      venue=self._guarded_live_venue,
      symbols=(symbol,),
      timeframe=timeframe,
      parameters=resolved_parameters,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      start_at=start_at,
      end_at=end_at,
    )
    loaded = self._data_engine.load_frame(config=config, active_bars=active_bars)
    run = RunRecord(
      config=config,
      status=RunStatus.RUNNING,
      provenance=RunProvenance(
        lane="core",
        strategy=strategy_snapshot,
        market_data=loaded.lineage,
        market_data_by_symbol=loaded.lineage_by_symbol,
      ),
    )
    data = loaded.frame
    if data.empty:
      self._fail_run(run, "No candles available for the requested range.")
      return run

    enriched = strategy.build_feature_frame(data, config.parameters)
    required_bars = max(strategy.warmup_spec().required_bars, 2)
    if len(enriched) < required_bars:
      self._fail_run(
        run,
        f"Strategy requires at least {required_bars} candles; received {len(enriched)}.",
      )
      return run

    cache = StateCache(
      instrument_id=f"{config.venue}:{config.symbols[0]}",
      cash=config.initial_cash,
    )
    for index in range(required_bars - 1, len(enriched)):
      history = enriched.iloc[: index + 1]
      latest = history.iloc[-1]
      if pd.isna(latest["close"]):
        continue
      timestamp = _row_timestamp(latest["timestamp"])
      state = cache.snapshot(timestamp=timestamp, parameters=config.parameters)
      decision = strategy.evaluate(history, config.parameters, state)
      self._execution_engine.apply_decision(
        run=run,
        config=config,
        decision=decision,
        cache=cache,
        market_price=float(latest["close"]),
      )

    run.metrics = summarize_performance(
      initial_cash=config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    return run

  def _prepare_strategy(
    self,
    *,
    strategy_id: str,
    parameters: dict[str, Any],
  ):
    if strategy_id == self._llm_strategy.describe().strategy_id:
      raise ValueError("LLM strategy execution is interface-only in this runtime.")
    strategy = self._strategies.load(strategy_id)
    metadata = strategy.describe()
    resolved_parameters = _resolve_parameters(metadata, parameters)
    metadata = replace(
      metadata,
      parameter_schema=metadata.parameter_schema,
    )
    strategy_snapshot = StrategySnapshot(
      strategy_id=metadata.strategy_id,
      name=metadata.name,
      version=metadata.version,
      runtime=metadata.runtime,
      lifecycle=metadata.lifecycle,
      catalog_semantics=metadata.catalog_semantics,
      version_lineage=metadata.version_lineage,
      parameter_snapshot=StrategyParameterSnapshot(
        requested=dict(parameters),
        resolved=resolved_parameters,
        schema=metadata.parameter_schema,
      ),
      supported_timeframes=metadata.supported_timeframes,
      warmup=strategy.warmup_spec(),
      entrypoint=metadata.entrypoint,
    )
    return strategy, metadata, strategy_snapshot, resolved_parameters

  def _ensure_live_launch_allowed(self) -> None:
    if not self._guarded_live_execution_enabled:
      raise PermissionError("Guarded-live execution is disabled.")
    if self._guarded_live_venue != "binance":
      raise PermissionError("Only Binance guarded-live execution is supported.")
    if self._venue_execution is not None:
      supported, issues = self._venue_execution.describe_capability()
      if not supported:
        raise PermissionError("; ".join(issues) or "Venue execution is unavailable.")

  def _start_runtime_session(self, run: RunRecord, *, mode: RunMode) -> None:
    now = self._clock()
    worker_kind = (
      self._guarded_live_worker_kind if mode == RunMode.LIVE else self._sandbox_worker_kind
    )
    heartbeat_interval = (
      self._guarded_live_worker_heartbeat_interval_seconds
      if mode == RunMode.LIVE
      else self._sandbox_worker_heartbeat_interval_seconds
    )
    heartbeat_timeout = (
      self._guarded_live_worker_heartbeat_timeout_seconds
      if mode == RunMode.LIVE
      else self._sandbox_worker_heartbeat_timeout_seconds
    )
    last_point = run.equity_curve[-1].timestamp if run.equity_curve else now
    run.provenance.runtime_session = RuntimeSessionState(
      worker_kind=worker_kind,
      lifecycle_state="active",
      started_at=now,
      primed_candle_count=(
        run.provenance.market_data.candle_count
        if run.provenance.market_data is not None
        else 0
      ),
      processed_tick_count=len(run.equity_curve),
      last_heartbeat_at=now,
      last_processed_candle_at=last_point,
      last_seen_candle_at=last_point,
      heartbeat_interval_seconds=heartbeat_interval,
      heartbeat_timeout_seconds=heartbeat_timeout,
    )

  def _maintain_worker_sessions(
    self,
    *,
    mode: RunMode,
    worker_kind: str,
    heartbeat_interval_seconds: int,
    heartbeat_timeout_seconds: int,
    force_recovery: bool,
    recovery_reason: str,
  ) -> dict[str, int]:
    current_time = self._clock()
    heartbeated = 0
    recovered = 0
    for run in self._runs.list_runs(mode.value):
      if run.status != RunStatus.RUNNING:
        continue
      if force_recovery or self._run_supervisor.needs_worker_recovery(run=run, now=current_time):
        self._run_supervisor.recover_worker_session(
          run=run,
          worker_kind=worker_kind,
          heartbeat_interval_seconds=heartbeat_interval_seconds,
          heartbeat_timeout_seconds=heartbeat_timeout_seconds,
          reason=recovery_reason,
          now=current_time,
          primed_candle_count=(
            run.provenance.market_data.candle_count
            if run.provenance.market_data is not None
            else 0
          ),
          processed_tick_count=len(run.equity_curve),
          last_processed_candle_at=run.equity_curve[-1].timestamp if run.equity_curve else None,
          last_seen_candle_at=run.equity_curve[-1].timestamp if run.equity_curve else None,
        )
        recovered += 1
        self._append_run_note(
          run,
          layer=mode.value,
          event_type="worker_recovered",
          message=f"{mode.value} worker session recovered: {recovery_reason}.",
        )
      else:
        self._run_supervisor.heartbeat_worker_session(run=run, now=current_time)
        heartbeated += 1
      self._runs.save_run(run)
    return {"heartbeated": heartbeated, "recovered": recovered}

  def _fail_run(self, run: RunRecord, message: str) -> None:
    run.status = RunStatus.FAILED
    run.ended_at = self._clock()
    run.notes.append(message)
    self._record_log(
      layer=run.config.mode.value,
      event_type="run_failed",
      message=message,
      severity="error",
      run_id=run.config.run_id,
      mode=run.config.mode,
    )

  def _append_run_note(
    self,
    run: RunRecord,
    *,
    layer: str,
    event_type: str,
    message: str,
    severity: str = "info",
    payload: dict[str, Any] | None = None,
  ) -> None:
    run.notes.append(f"{self._clock().isoformat()} | {event_type} | {message}")
    self._record_log(
      layer=layer,
      event_type=event_type,
      message=message,
      severity=severity,
      run_id=run.config.run_id,
      mode=run.config.mode,
      payload=payload or {},
    )

  def _record_log(
    self,
    *,
    layer: str,
    event_type: str,
    message: str,
    severity: str = "info",
    run_id: str | None = None,
    mode: RunMode | None = None,
    payload: dict[str, Any] | None = None,
  ) -> OperationLog:
    timestamp = self._clock()
    log = OperationLog(
      log_id=f"{timestamp.isoformat()}:{event_type}:{uuid4()}",
      recorded_at=timestamp,
      layer=layer,
      event_type=event_type,
      message=message,
      severity=severity,
      run_id=run_id,
      mode=mode,
      payload=payload or {},
    )
    return self._runs.save_log(log)

  def _require_run(self, run_id: str) -> RunRecord:
    run = self._runs.get_run(run_id)
    if run is None:
      raise LookupError(f"Run not found: {run_id}")
    return run


def _resolve_parameters(metadata: StrategyMetadata, requested: dict[str, Any]) -> dict[str, Any]:
  resolved: dict[str, Any] = {}
  for key, spec in metadata.parameter_schema.items():
    if isinstance(spec, dict) and "default" in spec:
      resolved[key] = spec["default"]
  resolved.update(requested)
  return resolved


def _row_timestamp(value: Any) -> datetime:
  if hasattr(value, "to_pydatetime"):
    return value.to_pydatetime()
  if isinstance(value, datetime):
    return value
  return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
