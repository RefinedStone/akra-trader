from __future__ import annotations

from akra_trader.application_context import *  # noqa: F403
from akra_trader import application_context as _application_context

globals().update({
  name: getattr(_application_context, name)
  for name in dir(_application_context)
  if name.startswith("_") and not name.startswith("__")
})

class TradingApplicationSimulationRerunMixin:
  @staticmethod
  def _merge_operator_alert_history(
    *,
    existing: tuple[OperatorAlert, ...],
    active_alerts: list[OperatorAlert],
    current_time: datetime,
  ) -> tuple[OperatorAlert, ...]:
    history_by_id = {alert.alert_id: alert for alert in existing}
    active_ids = {alert.alert_id for alert in active_alerts}

    for alert in active_alerts:
      previous = history_by_id.get(alert.alert_id)
      detected_at = (
        previous.detected_at
        if previous is not None and previous.status == "active"
        else alert.detected_at
      )
      history_by_id[alert.alert_id] = replace(
        alert,
        detected_at=detected_at,
        status="active",
        resolved_at=None,
        delivery_targets=alert.delivery_targets or (previous.delivery_targets if previous is not None else ()),
      )

    for alert_id, previous in tuple(history_by_id.items()):
      if alert_id in active_ids or previous.status != "active":
        continue
      history_by_id[alert_id] = replace(
        previous,
        status="resolved",
        resolved_at=current_time,
      )

    merged = sorted(
      history_by_id.values(),
      key=lambda alert: (alert.resolved_at or alert.detected_at, alert.detected_at),
      reverse=True,
    )
    return tuple(merged)
  @staticmethod
  def _build_operator_alert_occurrence_id(
    *,
    alert_id: str,
    detected_at: datetime,
    resolved_at: datetime | None,
  ) -> str:
    resolved_marker = resolved_at.isoformat() if resolved_at is not None else "active"
    return f"{alert_id}:{detected_at.isoformat()}:{resolved_marker}"
  def _build_operator_alerts_for_run(
    self,
    *,
    run: RunRecord,
    current_time: datetime,
  ) -> list[OperatorAlert]:
    session = run.provenance.runtime_session
    if session is None:
      return []

    alerts: list[OperatorAlert] = []
    symbol = run.config.symbols[0] if run.config.symbols else run.config.run_id
    market_context = self._build_operator_alert_market_context(
      symbol=symbol,
      symbols=list(run.config.symbols),
      timeframe=run.config.timeframe,
    )
    failed_event = self._latest_runtime_note_event(run=run, kind="sandbox_worker_failed")
    if failed_event is not None or session.lifecycle_state == "failed" or run.status == RunStatus.FAILED:
      detected_at = (
        failed_event["timestamp"]
        or run.ended_at
        or session.last_heartbeat_at
        or run.started_at
      )
      detail = failed_event["detail"] if failed_event is not None else (
        run.notes[-1] if run.notes else "Sandbox worker entered a failed runtime state."
      )
      alerts.append(
        OperatorAlert(
          alert_id=f"runtime-failed:{run.config.run_id}:{detected_at.isoformat()}",
          severity="critical",
          category="worker_failure",
          summary=f"Sandbox worker failed for {symbol}.",
          detail=detail,
          detected_at=detected_at,
          run_id=run.config.run_id,
          session_id=session.session_id,
          **market_context,
        )
      )

    heartbeat_at = session.last_heartbeat_at or session.started_at
    heartbeat_age_seconds = (current_time - heartbeat_at).total_seconds()
    if (
      run.status == RunStatus.RUNNING
      and session.lifecycle_state == "active"
      and heartbeat_age_seconds > session.heartbeat_timeout_seconds
    ):
      alerts.append(
        OperatorAlert(
          alert_id=f"runtime-stale:{run.config.run_id}:{current_time.isoformat()}",
          severity="warning",
          category="stale_runtime",
          summary=f"Sandbox worker heartbeat is stale for {symbol}.",
          detail=(
            f"Last heartbeat at {heartbeat_at.isoformat()} exceeded the "
            f"{session.heartbeat_timeout_seconds}s timeout while the run remains active."
          ),
          detected_at=current_time,
          run_id=run.config.run_id,
          session_id=session.session_id,
          **market_context,
        )
      )
    return alerts
  def _build_operator_audit_events_for_run(
    self,
    *,
    run: RunRecord,
    current_time: datetime,
  ) -> list[OperatorAuditEvent]:
    session = run.provenance.runtime_session
    if session is None:
      return []

    events: list[OperatorAuditEvent] = [
      OperatorAuditEvent(
        event_id=f"runtime-started:{run.config.run_id}:{session.started_at.isoformat()}",
        timestamp=session.started_at,
        actor="system",
        kind="sandbox_worker_started",
        summary=f"Sandbox worker started for {run.config.symbols[0]}.",
        detail=(
          f"Session {session.session_id} started with {session.primed_candle_count} primed candles "
          f"and {session.processed_tick_count} processed ticks."
        ),
        run_id=run.config.run_id,
        session_id=session.session_id,
      )
    ]

    for note in run.notes:
      if note == "Sandbox run stopped by operator.":
        timestamp = run.ended_at or current_time
        events.append(
          OperatorAuditEvent(
            event_id=f"audit:sandbox_worker_stopped:{run.config.run_id}:{timestamp.isoformat()}",
            timestamp=timestamp,
            actor="operator",
            kind="sandbox_worker_stopped",
            summary=self._build_runtime_audit_summary(run=run, kind="sandbox_worker_stopped"),
            detail=note,
            run_id=run.config.run_id,
            session_id=session.session_id,
          )
        )
        continue
      if parsed := self._parse_runtime_note_event(note):
        events.append(
          OperatorAuditEvent(
            event_id=f"audit:{parsed['kind']}:{run.config.run_id}:{parsed['timestamp'].isoformat()}",
            timestamp=parsed["timestamp"],
            actor="system",
            kind=parsed["kind"],
            summary=self._build_runtime_audit_summary(run=run, kind=parsed["kind"]),
            detail=parsed["detail"],
            run_id=run.config.run_id,
            session_id=session.session_id,
          )
        )

    heartbeat_at = session.last_heartbeat_at or session.started_at
    if (
      run.status == RunStatus.RUNNING
      and session.lifecycle_state == "active"
      and (current_time - heartbeat_at).total_seconds() > session.heartbeat_timeout_seconds
    ):
      events.append(
        OperatorAuditEvent(
          event_id=f"audit:sandbox_worker_stale:{run.config.run_id}:{current_time.isoformat()}",
          timestamp=current_time,
          actor="system",
          kind="sandbox_worker_stale",
          summary=f"Sandbox worker stale state detected for {run.config.symbols[0]}.",
          detail=(
            f"Heartbeat timeout exceeded after {session.heartbeat_timeout_seconds}s without an update."
          ),
          run_id=run.config.run_id,
          session_id=session.session_id,
        )
      )
    return events
  def _latest_runtime_note_event(
    self,
    *,
    run: RunRecord,
    kind: str,
  ) -> dict[str, datetime | str] | None:
    for note in reversed(run.notes):
      parsed = self._parse_runtime_note_event(note)
      if parsed is not None and parsed["kind"] == kind:
        return parsed
    return None
  def _parse_runtime_note_event(self, note: str) -> dict[str, datetime | str] | None:
    parts = note.split(" | ", 2)
    if len(parts) == 3:
      timestamp_raw, kind, detail = parts
      if kind.startswith("sandbox_worker_") or kind.startswith("guarded_live_worker_"):
        return {
          "timestamp": datetime.fromisoformat(timestamp_raw),
          "kind": kind,
          "detail": detail,
        }
    return None
  @staticmethod
  def _build_runtime_audit_summary(*, run: RunRecord, kind: str) -> str:
    symbol = run.config.symbols[0] if run.config.symbols else run.config.run_id
    summary_by_kind = {
      "guarded_live_worker_failed": f"Guarded-live worker failed for {symbol}.",
      "guarded_live_worker_recovered": f"Guarded-live worker recovered for {symbol}.",
      "sandbox_worker_recovered": f"Sandbox worker recovered for {symbol}.",
      "sandbox_worker_failed": f"Sandbox worker failed for {symbol}.",
      "sandbox_worker_stopped": f"Sandbox worker stopped by operator for {symbol}.",
    }
    return summary_by_kind.get(kind, f"Sandbox worker runtime event for {symbol}.")
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
    metadata = _apply_registration_snapshot_metadata(
      metadata=metadata,
      registration=registration,
    )
    schema = deepcopy(metadata.parameter_schema)
    requested = deepcopy(parameters)
    resolved = self._resolve_parameters(schema=schema, requested=requested)
    return StrategySnapshot(
      strategy_id=metadata.strategy_id,
      name=metadata.name,
      version=metadata.version,
      runtime=metadata.runtime,
      lifecycle=metadata.lifecycle,
      catalog_semantics=deepcopy(metadata.catalog_semantics),
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
