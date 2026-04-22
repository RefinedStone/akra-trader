from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent

def _request_incident_remediation(
  app,
  *,
  incident: OperatorIncidentEvent,
  delivery_history: tuple[OperatorIncidentDelivery, ...],
  current_time: datetime,
  actor: str,
  detail: str,
) -> tuple[OperatorIncidentEvent, tuple[OperatorIncidentDelivery, ...]]:
  remediation = incident.remediation
  if incident.kind != "incident_opened" or remediation.state in {"not_applicable", "completed"}:
    return incident, ()

  detail_copy = detail.strip() or remediation.detail or remediation.summary or "remediation_requested"
  requested_remediation = replace(
    remediation,
    requested_at=current_time,
    requested_by=actor,
    last_attempted_at=current_time,
  )
  if remediation.owner != "provider":
    return replace(incident, remediation=requested_remediation), ()

  provider = requested_remediation.provider or incident.paging_provider or incident.external_provider
  if provider is None:
    return (
      replace(
        incident,
        remediation=replace(
          requested_remediation,
          state="not_configured",
        ),
      ),
      (),
    )
  normalized_provider = app._normalize_paging_provider(provider)
  supported_providers = {
    app._normalize_paging_provider(candidate)
    for candidate in app._operator_alert_delivery.list_supported_workflow_providers()
  }
  if normalized_provider not in supported_providers:
    return (
      replace(
        incident,
        remediation=replace(
          requested_remediation,
          state="not_supported",
          provider=normalized_provider,
        ),
      ),
      (),
    )

  requested_incident = replace(incident, remediation=requested_remediation)
  records = app._operator_alert_delivery.sync_incident_workflow(
    incident=requested_incident,
    provider=normalized_provider or provider,
    action="remediate",
    actor=actor,
    detail=detail_copy,
    payload=app._build_incident_provider_workflow_payload(
      incident=requested_incident,
      action="remediate",
      actor=actor,
      detail=detail_copy,
    ),
    attempt_number=1,
  )
  records = app._apply_delivery_retry_policy(
    records=records,
    current_time=current_time,
  )
  latest = app._latest_provider_workflow_record(records=records)
  requested_provider_recovery = app._build_provider_recovery_state(
    remediation=requested_remediation,
    next_state=requested_remediation.state,
    provider=normalized_provider or provider,
    detail=detail_copy,
    synced_at=current_time,
    workflow_reference=(
      latest.external_reference
      if latest is not None and latest.external_reference is not None
      else requested_remediation.reference
    ),
    payload={},
    event_kind="local_remediation_requested",
  )
  requested_provider_recovery = replace(
    requested_provider_recovery,
    status_machine=app._build_provider_recovery_status_machine(
      existing=requested_provider_recovery.status_machine,
      remediation_state=requested_remediation.state,
      event_kind="local_remediation_requested",
      workflow_state=(
        app._resolve_incident_delivery_state(records=records)
        if records
        else requested_provider_recovery.status_machine.workflow_state
      ),
      workflow_action="remediate",
      attempt_number=latest.attempt_number if latest is not None else 1,
      detail=detail_copy,
      event_at=latest.attempted_at if latest is not None else current_time,
    ),
  )
  updated_incident = replace(
    incident,
    remediation=replace(
      requested_remediation,
      state=app._resolve_remediation_delivery_state(
        records=records,
        current_state=requested_remediation.state,
      ),
      provider=normalized_provider,
      reference=(
        latest.external_reference
        if latest is not None and latest.external_reference is not None
        else requested_remediation.reference
      ),
      provider_recovery=requested_provider_recovery,
    ),
  )
  return updated_incident, records

def _execute_local_incident_remediation(
  app,
  *,
  incident: OperatorIncidentEvent,
  actor: str,
  current_time: datetime,
) -> tuple[OperatorIncidentEvent, tuple[MarketDataRemediationResult, ...]]:
  remediation = incident.remediation
  if remediation.kind in {
    "recent_sync",
    "historical_backfill",
    "candle_repair",
    "venue_fault_review",
    "market_data_review",
  }:
    timeframe, symbols = app._resolve_market_data_remediation_targets(incident=incident)
    if timeframe is None or not symbols:
      return incident, ()

    results_list: list[MarketDataRemediationResult] = []
    for symbol in symbols:
      try:
        results_list.append(
          app._market_data.remediate(
            kind=remediation.kind,
            symbol=symbol,
            timeframe=timeframe,
          )
        )
      except Exception as exc:
        results_list.append(
          MarketDataRemediationResult(
            kind=remediation.kind,
            symbol=symbol,
            timeframe=timeframe,
            status="failed",
            started_at=current_time,
            finished_at=current_time,
            detail=f"market_data_remediation_failed:{exc}",
          )
        )
    results = tuple(results_list)
  elif remediation.kind in {"channel_restore", "order_book_rebuild"}:
    results = app._execute_local_guarded_live_session_remediation(
      incident=incident,
      actor=actor,
      current_time=current_time,
    )
  else:
    return incident, ()
  if not results:
    return incident, ()

  last_attempted_at = max((result.finished_at for result in results), default=current_time)
  local_state = app._resolve_local_remediation_state(results=results)
  local_detail = app._summarize_local_remediation_results(results)
  updated_remediation = replace(
    remediation,
    state=local_state,
    requested_at=current_time,
    requested_by=actor,
    last_attempted_at=last_attempted_at,
    detail=local_detail,
    provider_recovery=app._refresh_provider_recovery_phase_graphs(
      provider_recovery=replace(
        remediation.provider_recovery,
        lifecycle_state=app._provider_recovery_lifecycle_for_remediation_state(local_state),
        detail=local_detail,
        status_machine=app._build_provider_recovery_status_machine(
          existing=remediation.provider_recovery.status_machine,
          remediation_state=local_state,
          event_kind=(
            "local_verification_executed"
            if local_state in {"executed", "completed", "partial", "skipped"}
            else "local_verification_failed"
          ),
          workflow_state=remediation.provider_recovery.status_machine.workflow_state,
          workflow_action=remediation.provider_recovery.status_machine.workflow_action,
          job_state=(
            "verified"
            if local_state in {"executed", "completed"}
            else ("partial" if local_state == "partial" else ("skipped" if local_state == "skipped" else "failed"))
          ),
          sync_state=(
            "bidirectional_synced"
            if remediation.provider_recovery.provider is not None
            and local_state in {"executed", "completed", "partial", "skipped"}
            else ("local_failed" if local_state == "failed" else "local_only")
          ),
          detail=local_detail,
          event_at=last_attempted_at,
          attempt_number=remediation.provider_recovery.status_machine.attempt_number,
        ),
        updated_at=last_attempted_at,
      ),
      synced_at=last_attempted_at,
    ),
  )
  return replace(incident, remediation=updated_remediation), results

def _execute_local_guarded_live_session_remediation(
  app,
  *,
  incident: OperatorIncidentEvent,
  actor: str,
  current_time: datetime,
) -> tuple[MarketDataRemediationResult, ...]:
  state = app._guarded_live_state.load_state()
  run = app._resolve_guarded_live_remediation_run(incident=incident, state=state)
  symbol, timeframe = app._resolve_guarded_live_remediation_identity(
    run=run,
    state=state,
  )
  remediation_kind = incident.remediation.kind
  if run is None:
    return (
      MarketDataRemediationResult(
        kind=remediation_kind,
        symbol=symbol,
        timeframe=timeframe,
        status="failed",
        started_at=current_time,
        finished_at=current_time,
        detail=f"{remediation_kind}:{symbol}:{timeframe}:guarded_live_run_unavailable",
      ),
    )

  session = run.provenance.runtime_session
  remediation_reason = f"incident_remediation:{remediation_kind}"
  try:
    handoff = app._activate_guarded_live_venue_session(
      run=run,
      reason=remediation_reason,
    )
    session_sync = app._sync_guarded_live_session(run=run, handoff=handoff)
    next_handoff = session_sync["handoff"]
    run = app._runs.save_run(run)
    refreshed_state = app._build_guarded_live_state_for_local_session_remediation(
      state=app._guarded_live_state.load_state(),
      run=run,
      actor=actor,
      reason=remediation_reason,
      session_handoff=next_handoff,
    )
    app._persist_guarded_live_state(refreshed_state)
    detail = app._summarize_guarded_live_session_remediation_result(
      remediation_kind=remediation_kind,
      handoff=next_handoff,
    )
    app._append_guarded_live_audit_event(
      kind="guarded_live_incident_local_remediation_executed",
      actor=actor,
      summary=f"Guarded-live local remediation executed for {incident.alert_id}.",
      detail=detail,
      run_id=run.config.run_id,
      session_id=session.session_id if session is not None else None,
    )
    return (
      MarketDataRemediationResult(
        kind=remediation_kind,
        symbol=symbol,
        timeframe=timeframe,
        status="executed",
        started_at=current_time,
        finished_at=app._clock(),
        detail=detail,
      ),
    )
  except Exception as exc:
    detail = f"{remediation_kind}:{symbol}:{timeframe}:guarded_live_session_remediation_failed:{exc}"
    app._append_guarded_live_audit_event(
      kind="guarded_live_incident_local_remediation_failed",
      actor=actor,
      summary=f"Guarded-live local remediation failed for {incident.alert_id}.",
      detail=detail,
      run_id=run.config.run_id,
      session_id=session.session_id if session is not None else None,
    )
    return (
      MarketDataRemediationResult(
        kind=remediation_kind,
        symbol=symbol,
        timeframe=timeframe,
        status="failed",
        started_at=current_time,
        finished_at=app._clock(),
        detail=detail,
      ),
    )
