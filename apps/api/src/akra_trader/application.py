from __future__ import annotations

import calendar
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
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
from akra_trader.ports import LlmJudgementPort
from akra_trader.ports import MarketDataPort
from akra_trader.ports import StrategyCatalogPort
from akra_trader.ports import VenueExecutionPort
from akra_trader.runtime import DataEngine
from akra_trader.runtime import ExecutionEngine
from akra_trader.runtime import ExecutionModeService
from akra_trader.runtime import RunSupervisor
from akra_trader.runtime import StateCache
from akra_trader.runtime import candles_to_frame
from akra_trader.strategies.llm import ExternalDecisionStrategy
from akra_trader.strategies.llm import LlmJudgementVetoStrategy


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
    llm_judgement: LlmJudgementPort | None = None,
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
    self._llm_judgement = llm_judgement
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
      "judgement_port": "LlmJudgementPort",
      "provider_adapter": None,
      "isolation_state": "interface_only",
      "judgement_state": "available" if self._llm_judgement is not None else "not_configured",
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
      payload=self._build_run_completion_payload(run),
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

  def get_run_llm_judgements(self, run_id: str) -> list[dict[str, Any]]:
    self._require_run(run_id)
    judgements: list[dict[str, Any]] = []
    for log in self.list_operation_logs(run_id=run_id, limit=1_000):
      if log.event_type != "llm_judgement_recorded":
        continue
      judgements.append(
        {
          "log_id": log.log_id,
          "recorded_at": log.recorded_at,
          "message": log.message,
          "severity": log.severity,
          **log.payload,
        }
      )
    return judgements

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

  def sync_market_data(
    self,
    *,
    symbol: str,
    timeframe: str,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int | None = None,
  ):
    result = self._market_data.ensure_candles(
      symbol=symbol,
      timeframe=timeframe,
      start_at=start_at,
      end_at=end_at,
      limit=limit,
    )
    self._record_log(
      layer="data",
      event_type="market_data_sync_requested",
      message=f"Market data sync {result.status} for {symbol} on {timeframe}.",
      severity="info" if result.status in {"synced", "fixture"} else "warning",
      payload={
        "symbol": symbol,
        "timeframe": timeframe,
        "status": result.status,
        "candle_count": result.candle_count,
        "issues": list(result.issues),
      },
    )
    return result

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
    required_bars = max(strategy.warmup_spec().required_bars, 2)
    ensure_limit = self._resolve_run_ensure_limit(
      active_bars=active_bars,
      required_bars=required_bars,
      start_at=start_at,
      end_at=end_at,
    )
    ensure_result = self._market_data.ensure_candles(
      symbol=symbol,
      timeframe=timeframe,
      start_at=start_at,
      end_at=end_at,
      limit=ensure_limit,
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
    data_issue = self._validate_loaded_market_data(
      data=data,
      config=config,
      required_bars=required_bars,
    )
    self._record_backtest_window_validation(
      run=run,
      data=data,
      required_bars=required_bars,
      data_issue=data_issue,
    )
    if data_issue is not None:
      self._fail_run(run, data_issue)
      if ensure_result.status == "failed":
        run.notes.append(
          f"Market data sync failed before execution: {', '.join(ensure_result.issues) or 'unknown'}."
        )
      return run

    enriched = strategy.build_feature_frame(data, config.parameters)
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
      reviewed = self._execution_engine.apply_decision(
        run=run,
        config=config,
        decision=decision,
        cache=cache,
        market_price=float(latest["close"]),
      )
      self._record_llm_judgement_trace(run=run, decision=reviewed)

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
    if self._llm_judgement is not None and resolved_parameters.get("use_llm_judgement") is True:
      strategy = LlmJudgementVetoStrategy(strategy, self._llm_judgement)
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
      processed_candles = 0
      try:
        processed_candles = self._poll_worker_market_data(run=run, mode=mode)
      except Exception as exc:
        self._append_run_note(
          run,
          layer=mode.value,
          event_type="worker_market_data_poll_failed",
          message=f"{mode.value} worker market-data polling failed: {exc}",
          severity="warning",
        )
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
      if processed_candles > 0:
        self._append_run_note(
          run,
          layer=mode.value,
          event_type="worker_candles_processed",
          message=f"{mode.value} worker processed {processed_candles} closed candles.",
          payload={"processed_candles": processed_candles},
        )
      self._runs.save_run(run)
    return {"heartbeated": heartbeated, "recovered": recovered}

  def _resolve_run_ensure_limit(
    self,
    *,
    active_bars: int | None,
    required_bars: int,
    start_at: datetime | None,
    end_at: datetime | None,
  ) -> int | None:
    if active_bars is not None:
      return max(active_bars, required_bars)
    if start_at is not None or end_at is not None:
      return required_bars
    return None

  def _validate_loaded_market_data(
    self,
    *,
    data: pd.DataFrame,
    config: RunConfig,
    required_bars: int,
  ) -> str | None:
    if data.empty:
      return "No candles available for the requested range."
    if len(data) < required_bars:
      return f"Strategy requires at least {required_bars} candles; received {len(data)}."

    timestamps = sorted(
      _ensure_utc_datetime(_row_timestamp(value))
      for value in data["timestamp"].tolist()
    )
    requested_start_at = _ensure_utc_datetime(config.start_at) if config.start_at is not None else None
    requested_end_at = _ensure_utc_datetime(config.end_at) if config.end_at is not None else None
    if requested_start_at is not None and timestamps[0] > requested_start_at:
      return (
        "Market data does not cover the requested start: "
        f"{timestamps[0].isoformat()} > {requested_start_at.isoformat()}."
      )
    if requested_end_at is not None and _shift_timeframe_timestamp(timestamps[-1], config.timeframe, 1) <= requested_end_at:
      return (
        "Market data does not cover the requested end: "
        f"{timestamps[-1].isoformat()} < {requested_end_at.isoformat()}."
      )
    for previous, current in zip(timestamps, timestamps[1:]):
      expected = _shift_timeframe_timestamp(previous, config.timeframe, 1)
      if current > expected:
        timeframe_delta = _timeframe_delta(config.timeframe)
        missing = max(int((current - previous).total_seconds() // timeframe_delta.total_seconds()) - 1, 1)
        return (
          "Market data has a gap in the requested range: "
          f"{previous.isoformat()} to {current.isoformat()} ({missing} missing candles)."
        )
    return None

  def _poll_worker_market_data(self, *, run: RunRecord, mode: RunMode) -> int:
    if not run.config.symbols:
      return 0
    session = run.provenance.runtime_session
    if session is None:
      return 0
    symbol = run.config.symbols[0]
    timeframe = run.config.timeframe
    timeframe_delta = _timeframe_delta(timeframe)
    closed_until = _latest_closed_candle_at(self._clock(), timeframe)
    requested_end_at = (
      _ensure_utc_datetime(run.config.end_at) if run.config.end_at is not None else None
    )
    if requested_end_at is not None and requested_end_at < closed_until:
      closed_until = requested_end_at
    last_processed_at = session.last_processed_candle_at
    if last_processed_at is None and run.equity_curve:
      last_processed_at = run.equity_curve[-1].timestamp
    if last_processed_at is not None:
      last_processed_at = (
        last_processed_at.astimezone(UTC)
        if last_processed_at.tzinfo
        else last_processed_at.replace(tzinfo=UTC)
      )
    if last_processed_at is not None and closed_until <= last_processed_at:
      return 0

    start_at = last_processed_at + timeframe_delta if last_processed_at is not None else None
    self._market_data.ensure_candles(
      symbol=symbol,
      timeframe=timeframe,
      start_at=start_at,
      end_at=closed_until,
      limit=None,
    )
    candles = self._market_data.get_candles(
      symbol=symbol,
      timeframe=timeframe,
      start_at=start_at,
      end_at=closed_until,
      limit=None,
    )
    new_candles = [
      candle
      for candle in candles
      if last_processed_at is None or candle.timestamp > last_processed_at
    ]
    if not new_candles:
      return 0

    strategy = self._strategies.load(run.config.strategy_id)
    required_bars = max(strategy.warmup_spec().required_bars, 2)
    cache = self._restore_state_cache(run)
    processed = 0
    last_processed_candle_at = None
    for candle in sorted(new_candles, key=lambda item: item.timestamp):
      history_candles = self._market_data.get_candles(
        symbol=symbol,
        timeframe=timeframe,
        end_at=candle.timestamp,
        limit=required_bars,
      )
      if len(history_candles) < required_bars:
        continue
      history = strategy.build_feature_frame(
        candles_to_frame(history_candles),
        run.config.parameters,
      )
      if len(history) < required_bars:
        continue
      latest = history.iloc[-1]
      if pd.isna(latest["close"]):
        continue
      timestamp = _row_timestamp(latest["timestamp"])
      state = cache.snapshot(timestamp=timestamp, parameters=run.config.parameters)
      decision = strategy.evaluate(history, run.config.parameters, state)
      reviewed = self._execution_engine.apply_decision(
        run=run,
        config=run.config,
        decision=decision,
        cache=cache,
        market_price=float(latest["close"]),
      )
      self._record_llm_judgement_trace(run=run, decision=reviewed)
      processed += 1
      last_processed_candle_at = candle.timestamp

    if processed == 0:
      return 0

    run.metrics = summarize_performance(
      initial_cash=run.config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    self._run_supervisor.record_worker_market_progress(
      run=run,
      last_seen_candle_at=new_candles[-1].timestamp,
      last_processed_candle_at=last_processed_candle_at,
      processed_tick_count_increment=processed,
    )
    lineage_candles = self._market_data.get_candles(
      symbol=symbol,
      timeframe=timeframe,
      limit=max(session.primed_candle_count, required_bars, processed),
    )
    lineage = self._market_data.describe_lineage(
      symbol=symbol,
      timeframe=timeframe,
      candles=lineage_candles,
      limit=len(lineage_candles),
    )
    run.provenance.market_data = lineage
    run.provenance.market_data_by_symbol = {symbol: lineage}
    if mode == RunMode.LIVE:
      run.notes.append(
        f"{self._clock().isoformat()} | live_data_poll | evaluated closed candles without venue order submission."
      )
    return processed

  def _restore_state_cache(self, run: RunRecord) -> StateCache:
    instrument_id = f"{run.config.venue}:{run.config.symbols[0]}"
    cash = run.equity_curve[-1].cash if run.equity_curve else run.config.initial_cash
    cache = StateCache(instrument_id=instrument_id, cash=cash)
    cache.apply(cash=cash, position=run.positions.get(instrument_id))
    return cache

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

  def _record_llm_judgement_trace(
    self,
    *,
    run: RunRecord,
    decision: StrategyDecisionEnvelope,
  ) -> None:
    judgement_trace = decision.trace.get("llm_judgement")
    if not isinstance(judgement_trace, dict):
      return
    if judgement_trace.get("request") is None and judgement_trace.get("response") is None:
      return

    status = str(judgement_trace.get("status") or "recorded")
    payload = {
      "timestamp": decision.context.timestamp.isoformat(),
      "instrument_id": decision.context.instrument_id,
      "strategy_id": run.config.strategy_id,
      "candidate": judgement_trace.get("candidate"),
      "request": judgement_trace.get("request"),
      "response": judgement_trace.get("response"),
      "fallback": bool(judgement_trace.get("fallback")),
      "veto_reason": judgement_trace.get("veto_reason"),
      "final_action": decision.signal.action.value,
      "min_confidence": judgement_trace.get("min_confidence"),
      "status": status,
    }
    self._record_log(
      layer="llm_judgement",
      event_type="llm_judgement_recorded",
      message=(
        f"LLM judgement {status} for {decision.context.instrument_id}; "
        f"final action {decision.signal.action.value}."
      ),
      severity="info",
      run_id=run.config.run_id,
      mode=run.config.mode,
      payload=payload,
    )

  def _record_backtest_window_validation(
    self,
    *,
    run: RunRecord,
    data: pd.DataFrame,
    required_bars: int,
    data_issue: str | None,
  ) -> None:
    if run.config.mode != RunMode.BACKTEST:
      return

    payload = _build_window_payload(
      run=run,
      data=data,
      required_bars=required_bars,
      validation_status="failed" if data_issue else "valid",
      validation_message=data_issue,
    )
    event_type = (
      "backtest_window_validation_failed"
      if data_issue
      else "backtest_window_validated"
    )
    self._record_log(
      layer="backtest",
      event_type=event_type,
      message=_backtest_window_message(run=run, payload=payload, data_issue=data_issue),
      severity="error" if data_issue else "info",
      run_id=run.config.run_id,
      mode=run.config.mode,
      payload=payload,
    )

  def _build_run_completion_payload(self, run: RunRecord) -> dict[str, Any]:
    return {
      "status": run.status.value,
      "metrics": dict(run.metrics),
      "orders_count": len(run.orders),
      "fills_count": len(run.fills),
      "positions_count": len(run.positions),
      "closed_trades_count": len(run.closed_trades),
      "market_data": _lineage_payload(run),
    }

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


def _build_window_payload(
  *,
  run: RunRecord,
  data: pd.DataFrame,
  required_bars: int,
  validation_status: str,
  validation_message: str | None,
) -> dict[str, Any]:
  expected_candle_count = _expected_candle_count(
    start_at=run.config.start_at,
    end_at=run.config.end_at,
    timeframe=run.config.timeframe,
  )
  candle_count = len(data)
  return {
    "validation_status": validation_status,
    "validation_message": validation_message,
    "symbol": run.config.symbols[0] if run.config.symbols else None,
    "timeframe": run.config.timeframe,
    "requested_start_at": _serialize_optional_datetime(run.config.start_at),
    "requested_end_at": _serialize_optional_datetime(run.config.end_at),
    "effective_start_at": _effective_start_at(run=run, data=data),
    "effective_end_at": _effective_end_at(run=run, data=data),
    "candle_count": candle_count,
    "expected_candle_count": expected_candle_count,
    "candle_count_matches_expected": (
      candle_count == expected_candle_count
      if expected_candle_count is not None
      else None
    ),
    "required_bars": required_bars,
    "first_strategy_evaluation_at": _frame_timestamp_at(data, required_bars - 1),
    "last_strategy_evaluation_at": _frame_timestamp_at(data, candle_count - 1),
    "expected_evaluated_bars": max(candle_count - required_bars + 1, 0),
    "market_data": _lineage_payload(run),
  }


def _lineage_payload(run: RunRecord) -> dict[str, Any] | None:
  lineage = run.provenance.market_data
  if lineage is None:
    return None
  return {
    "provider": lineage.provider,
    "venue": lineage.venue,
    "symbols": list(lineage.symbols),
    "timeframe": lineage.timeframe,
    "requested_start_at": _serialize_optional_datetime(lineage.requested_start_at),
    "requested_end_at": _serialize_optional_datetime(lineage.requested_end_at),
    "effective_start_at": _serialize_optional_datetime(lineage.effective_start_at),
    "effective_end_at": _serialize_optional_datetime(lineage.effective_end_at),
    "candle_count": lineage.candle_count,
    "sync_status": lineage.sync_status,
    "reproducibility_state": lineage.reproducibility_state,
    "dataset_identity": lineage.dataset_identity,
    "sync_checkpoint_id": lineage.sync_checkpoint_id,
    "issues": list(lineage.issues),
  }


def _backtest_window_message(
  *,
  run: RunRecord,
  payload: dict[str, Any],
  data_issue: str | None,
) -> str:
  symbol = run.config.symbols[0] if run.config.symbols else "unknown"
  if data_issue:
    return (
      f"Backtest data window validation failed for {symbol} "
      f"on {run.config.timeframe}: {data_issue}"
    )
  return (
    f"Backtest data window validated for {symbol} on {run.config.timeframe}: "
    f"{payload['candle_count']} candles from {payload['effective_start_at']} "
    f"to {payload['effective_end_at']}."
  )


def _expected_candle_count(
  *,
  start_at: datetime | None,
  end_at: datetime | None,
  timeframe: str,
) -> int | None:
  if start_at is None or end_at is None or timeframe.endswith("M"):
    return None
  start = _ensure_utc_datetime(start_at)
  end = _ensure_utc_datetime(end_at)
  if end < start:
    return 0
  timeframe_seconds = _timeframe_seconds(timeframe)
  return int((end - start).total_seconds() // timeframe_seconds) + 1


def _effective_start_at(*, run: RunRecord, data: pd.DataFrame) -> str | None:
  lineage = run.provenance.market_data
  if lineage is not None and lineage.effective_start_at is not None:
    return _serialize_optional_datetime(lineage.effective_start_at)
  return _frame_timestamp_at(data, 0)


def _effective_end_at(*, run: RunRecord, data: pd.DataFrame) -> str | None:
  lineage = run.provenance.market_data
  if lineage is not None and lineage.effective_end_at is not None:
    return _serialize_optional_datetime(lineage.effective_end_at)
  return _frame_timestamp_at(data, len(data) - 1)


def _frame_timestamp_at(data: pd.DataFrame, index: int) -> str | None:
  if data.empty or index < 0 or index >= len(data):
    return None
  return _serialize_optional_datetime(_row_timestamp(data.iloc[index]["timestamp"]))


def _serialize_optional_datetime(value: datetime | None) -> str | None:
  if value is None:
    return None
  return _ensure_utc_datetime(value).isoformat().replace("+00:00", "Z")


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


def _ensure_utc_datetime(value: datetime) -> datetime:
  if value.tzinfo is None:
    return value.replace(tzinfo=UTC)
  return value.astimezone(UTC)


def _latest_closed_candle_at(now: datetime, timeframe: str) -> datetime:
  current = now.astimezone(UTC) if now.tzinfo else now.replace(tzinfo=UTC)
  seconds = _timeframe_seconds(timeframe)
  epoch_seconds = int(current.timestamp())
  floor_seconds = epoch_seconds - (epoch_seconds % seconds)
  return datetime.fromtimestamp(floor_seconds, tz=UTC) - timedelta(seconds=seconds)


def _timeframe_delta(timeframe: str) -> timedelta:
  return timedelta(seconds=_timeframe_seconds(timeframe))


def _shift_timeframe_timestamp(timestamp: datetime, timeframe: str, steps: int) -> datetime:
  if timeframe.endswith("M"):
    amount = int(timeframe[:-1])
    return _add_months(timestamp, amount * steps)
  return timestamp + _timeframe_delta(timeframe) * steps


def _add_months(value: datetime, months: int) -> datetime:
  month_index = value.year * 12 + value.month - 1 + months
  year = month_index // 12
  month = month_index % 12 + 1
  day = min(value.day, calendar.monthrange(year, month)[1])
  return value.replace(year=year, month=month, day=day)


def _timeframe_seconds(timeframe: str) -> int:
  if not timeframe:
    raise ValueError("Timeframe is required.")
  amount = int(timeframe[:-1])
  unit = timeframe[-1]
  if unit == "m":
    return amount * 60
  if unit == "h":
    return amount * 60 * 60
  if unit == "d":
    return amount * 24 * 60 * 60
  if unit == "w":
    return amount * 7 * 24 * 60 * 60
  if unit == "M":
    return amount * 30 * 24 * 60 * 60
  raise ValueError(f"Unsupported timeframe: {timeframe}")
