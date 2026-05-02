from __future__ import annotations

from akra_trader.application_context import *  # noqa: F403
from akra_trader import application_context as _application_context

globals().update({
  name: getattr(_application_context, name)
  for name in dir(_application_context)
  if name.startswith("_") and not name.startswith("__")
})

class TradingApplicationGuardedLiveSessionMixin:
  def prune_operator_lineage_evidence_retention(
    self,
    *,
    dry_run: bool = False,
    lineage_history_days: int | None = None,
    lineage_issue_history_days: int | None = None,
    ingestion_job_days: int | None = None,
    ingestion_issue_job_days: int | None = None,
    protected_history_ids: tuple[str, ...] = (),
    protected_job_ids: tuple[str, ...] = (),
  ):
    current_time = self._clock()
    policy = build_operator_lineage_evidence_retention_policy(
      lineage_history_days=lineage_history_days,
      lineage_issue_history_days=lineage_issue_history_days,
      ingestion_job_days=ingestion_job_days,
      ingestion_issue_job_days=ingestion_issue_job_days,
    )
    result = build_operator_lineage_evidence_retention_result(
      lineage_history=self.list_market_data_lineage_history(),
      ingestion_jobs=self.list_market_data_ingestion_jobs(),
      current_time=current_time,
      policy=policy,
      dry_run=dry_run,
      protected_history_ids=protected_history_ids,
      protected_job_ids=protected_job_ids,
    )
    deleted_lineage_history_count = 0
    deleted_ingestion_job_count = 0
    if not dry_run:
      if result.eligible_ingestion_job_ids:
        delete_ingestion_jobs = getattr(
          self._market_data,
          "delete_market_data_ingestion_jobs",
          None,
        )
        if not callable(delete_ingestion_jobs):
          raise RuntimeError("Market-data adapter does not support ingestion-job TTL deletion.")
        deleted_ingestion_job_count = int(delete_ingestion_jobs(result.eligible_ingestion_job_ids))
      if result.eligible_lineage_history_ids:
        delete_lineage_history = getattr(
          self._market_data,
          "delete_market_data_lineage_history_records",
          None,
        )
        if not callable(delete_lineage_history):
          raise RuntimeError("Market-data adapter does not support lineage-history TTL deletion.")
        deleted_lineage_history_count = int(delete_lineage_history(result.eligible_lineage_history_ids))
    return apply_operator_lineage_evidence_retention_deletion_counts(
      result,
      deleted_lineage_history_count=deleted_lineage_history_count,
      deleted_ingestion_job_count=deleted_ingestion_job_count,
    )
  def export_operator_lineage_drill_evidence_pack(
    self,
    *,
    scenario_key: str | None = None,
    scenario_label: str | None = None,
    incident_id: str | None = None,
    operator_decision: str = "reviewed",
    final_posture: str = "unresolved",
    venue: str | None = None,
    symbol: str | None = None,
    timeframe: str | None = None,
    sync_status: str | None = None,
    validation_claim: str | None = None,
    operation: str | None = None,
    status: str | None = None,
    source_run_id: str | None = None,
    rerun_id: str | None = None,
    dataset_identity: str | None = None,
    sync_checkpoint_id: str | None = None,
    rerun_boundary_id: str | None = None,
    rerun_validation_category: str | None = None,
    generated_by: str = "operator",
    export_format: str = "json",
    lineage_history_limit: int | None = 100,
    ingestion_job_limit: int | None = 100,
  ):
    current_time = self._clock()
    return build_operator_lineage_drill_evidence_pack(
      lineage_history=self.list_market_data_lineage_history(
        timeframe=timeframe,
        symbol=symbol,
        sync_status=sync_status,
        validation_claim=validation_claim,
        limit=lineage_history_limit,
      ),
      ingestion_jobs=self.list_market_data_ingestion_jobs(
        timeframe=timeframe,
        symbol=symbol,
        operation=operation,
        status=status,
        limit=ingestion_job_limit,
      ),
      generated_at=current_time,
      pack_id=f"operator-lineage-drill-pack:{uuid4()}",
      generated_by=generated_by,
      export_format=export_format,
      scenario_key=scenario_key,
      scenario_label=scenario_label,
      incident_id=incident_id,
      operator_decision=operator_decision,
      final_posture=final_posture,
      venue=venue,
      symbol=symbol,
      timeframe=timeframe,
      source_run_id=source_run_id,
      rerun_id=rerun_id,
      dataset_identity=dataset_identity,
      sync_checkpoint_id=sync_checkpoint_id,
      rerun_boundary_id=rerun_boundary_id,
      validation_claim=validation_claim,
      rerun_validation_category=rerun_validation_category,
      sync_status=sync_status,
      operation=operation,
      status=status,
      lineage_history_limit=lineage_history_limit,
      ingestion_job_limit=ingestion_job_limit,
    )
  def get_operator_visibility(self) -> OperatorVisibility:
    current_time = self._clock()
    sandbox_alerts, sandbox_audit_events = self._collect_sandbox_operator_visibility(
      current_time=current_time
    )
    scheduler_health, scheduler_alerts, scheduler_audit_events = (
      self._collect_provider_provenance_scheduler_operator_visibility(current_time=current_time)
    )
    guarded_live_state, live_alerts = self._refresh_guarded_live_alert_state(
      current_time=current_time
    )
    alerts = [*sandbox_alerts, *live_alerts, *scheduler_alerts]
    audit_events = [*sandbox_audit_events, *guarded_live_state.audit_events, *scheduler_audit_events]
    incident_events = tuple(
      sorted(guarded_live_state.incident_events, key=lambda event: event.timestamp, reverse=True)
    )
    delivery_history = tuple(
      sorted(
        guarded_live_state.delivery_history,
        key=lambda record: record.attempted_at,
        reverse=True,
      )
    )
    alerts.sort(key=lambda alert: alert.detected_at, reverse=True)
    audit_events.sort(key=lambda event: event.timestamp, reverse=True)
    scheduler_alert_history = self._build_provider_provenance_scheduler_alert_history(
      current_time=current_time,
    )
    merged_alert_history = tuple(
      sorted(
        (*guarded_live_state.alert_history, *scheduler_alert_history),
        key=lambda alert: (alert.resolved_at or alert.detected_at, alert.detected_at),
        reverse=True,
      )
    )
    return OperatorVisibility(
      generated_at=current_time,
      alerts=tuple(alerts),
      alert_history=merged_alert_history,
      incident_events=incident_events,
      delivery_history=delivery_history,
      audit_events=tuple(audit_events),
      provider_provenance_scheduler=scheduler_health,
    )
  def get_guarded_live_status(self) -> GuardedLiveStatus:
    return guarded_live_alert_state_refresh_support.get_guarded_live_status(self)
  def _refresh_guarded_live_alert_state(
    self,
    *,
    current_time: datetime,
    allow_post_remediation_recompute: bool = True,
  ) -> tuple[GuardedLiveState, list[OperatorAlert]]:
    return guarded_live_alert_state_refresh_support._refresh_guarded_live_alert_state(
      self,
      current_time=current_time,
      allow_post_remediation_recompute=allow_post_remediation_recompute,
    )
  def engage_guarded_live_kill_switch(
    self,
    *,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    stopped_runs = self._stop_runs_for_kill_switch(actor=actor, reason=reason)
    activation_count = state.kill_switch.activation_count
    if state.kill_switch.state != "engaged":
      activation_count += 1
    kill_switch = GuardedLiveKillSwitch(
      state="engaged",
      reason=reason,
      updated_at=current_time,
      updated_by=actor,
      activation_count=activation_count,
      last_engaged_at=current_time,
      last_released_at=state.kill_switch.last_released_at,
    )
    event = OperatorAuditEvent(
      event_id=f"guarded-live-kill-switch-engaged:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_kill_switch_engaged",
      summary="Guarded-live kill switch engaged.",
      detail=(
        f"Reason: {reason}. Stopped {len(stopped_runs)} operator-controlled runtime "
        f"session(s): {', '.join(stopped_runs) if stopped_runs else 'none'}."
      ),
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        state,
        kill_switch=kill_switch,
        audit_events=(event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()
  def release_guarded_live_kill_switch(
    self,
    *,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    kill_switch = GuardedLiveKillSwitch(
      state="released",
      reason=reason,
      updated_at=current_time,
      updated_by=actor,
      activation_count=state.kill_switch.activation_count,
      last_engaged_at=state.kill_switch.last_engaged_at,
      last_released_at=current_time,
    )
    event = OperatorAuditEvent(
      event_id=f"guarded-live-kill-switch-released:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_kill_switch_released",
      summary="Guarded-live kill switch released.",
      detail=f"Reason: {reason}. Operator-controlled runtime sessions may start again.",
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        state,
        kill_switch=kill_switch,
        audit_events=(event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()
  def run_guarded_live_reconciliation(
    self,
    *,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    reconciliation = self._build_guarded_live_reconciliation(
      state=state,
      checked_at=current_time,
      checked_by=actor,
    )
    event = OperatorAuditEvent(
      event_id=f"guarded-live-reconciliation-ran:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_reconciliation_ran",
      summary="Guarded-live reconciliation recorded.",
      detail=f"Reason: {reason}. {reconciliation.summary}",
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        state,
        reconciliation=reconciliation,
        audit_events=(event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()
  def recover_guarded_live_runtime_state(
    self,
    *,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    return guarded_live_alert_workflows_support.recover_guarded_live_runtime_state(
      self,
      actor=actor,
      reason=reason,
    )
  def _collect_sandbox_operator_visibility(
    self,
    *,
    current_time: datetime,
  ) -> tuple[list[OperatorAlert], list[OperatorAuditEvent]]:
    alerts: list[OperatorAlert] = []
    audit_events: list[OperatorAuditEvent] = []
    for run in self._runs.list_runs(mode=RunMode.SANDBOX.value):
      alerts.extend(self._build_operator_alerts_for_run(run=run, current_time=current_time))
      audit_events.extend(self._build_operator_audit_events_for_run(run=run, current_time=current_time))
    return alerts, audit_events
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
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    return self._run_execution_flow.run_backtest(
      strategy_id=strategy_id,
      timeframe=timeframe,
      symbol=symbol,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      start_at=start_at,
      end_at=end_at,
      tags=tags,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
    )
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
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    return self._run_execution_flow.start_sandbox_run(
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
      tags=tags,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
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
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    return self._run_execution_flow.start_paper_run(
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
      tags=tags,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
    )
  def start_live_run(
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
    operator_reason: str = "guarded_live_launch",
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    return self._run_execution_flow.start_live_run(
      strategy_id=strategy_id,
      symbol=symbol,
      timeframe=timeframe,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      replay_bars=replay_bars,
      operator_reason=operator_reason,
      start_at=start_at,
      end_at=end_at,
      tags=tags,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
    )
  def _start_sandbox_session(
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
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    return self._run_execution_flow.start_sandbox_session(
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
      tags=tags,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
    )
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
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    return self._run_execution_flow.start_paper_session(
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
      tags=tags,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
    )
  def _start_live_session(
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
    operator_reason: str,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    return self._run_execution_flow.start_live_session(
      strategy_id=strategy_id,
      timeframe=timeframe,
      symbol=symbol,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      replay_bars=replay_bars,
      operator_reason=operator_reason,
      start_at=start_at,
      end_at=end_at,
      tags=tags,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
    )
  def _start_native_session(
    self,
    *,
    target_mode: RunMode,
    reference_failure_copy: str,
    primed_note_prefix: str,
    insufficient_candles_copy: str,
    attach_runtime_session: bool,
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
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    return self._run_execution_flow.start_native_session(
      target_mode=target_mode,
      reference_failure_copy=reference_failure_copy,
      primed_note_prefix=primed_note_prefix,
      insufficient_candles_copy=insufficient_candles_copy,
      attach_runtime_session=attach_runtime_session,
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
      tags=tags,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
    )
  def stop_sandbox_run(self, run_id: str) -> RunRecord | None:
    run = self._runs.get_run(run_id)
    if run is None:
      return None
    _ensure_run_action_allowed(
      run=run,
      capabilities=self.get_run_surface_capabilities(),
      action_key="stop_run",
    )
    self._run_supervisor.stop(run, reason="Sandbox run stopped by operator.")
    return self._runs.save_run(run)
  def stop_paper_run(self, run_id: str) -> RunRecord | None:
    run = self._runs.get_run(run_id)
    if run is None:
      return None
    _ensure_run_action_allowed(
      run=run,
      capabilities=self.get_run_surface_capabilities(),
      action_key="stop_run",
    )
    self._run_supervisor.stop(run, reason="Paper run stopped by operator.")
    return self._runs.save_run(run)
  def stop_live_run(self, run_id: str) -> RunRecord | None:
    return self._run_execution_flow.stop_live_run(run_id)
  def resume_guarded_live_run(
    self,
    *,
    actor: str,
    reason: str,
  ) -> RunRecord:
    return self._run_execution_flow.resume_guarded_live_run(
      actor=actor,
      reason=reason,
    )
  def cancel_live_order(
    self,
    *,
    run_id: str,
    order_id: str,
    actor: str,
    reason: str,
  ) -> RunRecord:
    return self._run_execution_flow.cancel_live_order(
      run_id=run_id,
      order_id=order_id,
      actor=actor,
      reason=reason,
    )
  def replace_live_order(
    self,
    *,
    run_id: str,
    order_id: str,
    price: float,
    quantity: float | None,
    actor: str,
    reason: str,
  ) -> RunRecord:
    return self._run_execution_flow.replace_live_order(
      run_id=run_id,
      order_id=order_id,
      price=price,
      quantity=quantity,
      actor=actor,
      reason=reason,
    )
  def _ensure_operator_control_runtime_allowed(self, mode: RunMode) -> None:
    self._run_execution_flow.ensure_operator_control_runtime_allowed(mode)
  def _ensure_guarded_live_worker_start_allowed(self) -> None:
    self._run_execution_flow.ensure_guarded_live_worker_start_allowed()
