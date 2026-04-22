from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from datetime import timedelta
from numbers import Number
from typing import Any

from akra_trader.domain.models import GuardedLiveRuntimeRecovery
from akra_trader.domain.models import GuardedLiveState
from akra_trader.domain.models import GuardedLiveStatus
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import OperatorAlert
from akra_trader.domain.models import OperatorAuditEvent
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync
from akra_trader.domain.models import OrderStatus
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.application_support.guarded_live_external_sync_orchestration import (
  sync_guarded_live_incident_from_external,
)
from akra_trader.application_support.guarded_live_pull_sync_orchestration import (
  _apply_provider_pull_sync,
)
from akra_trader.application_support.guarded_live_pull_sync_orchestration import (
  _pull_sync_guarded_live_provider_recovery,
)

def get_guarded_live_status(app: Any) -> GuardedLiveStatus:
  current_time = app._clock()
  sandbox_alerts, _ = app._collect_sandbox_operator_visibility(current_time=current_time)
  state, live_alerts = app._refresh_guarded_live_alert_state(current_time=current_time)
  runtime_alerts = [*sandbox_alerts, *live_alerts]
  running_sandbox_count = app._count_running_runs(RunMode.SANDBOX)
  running_paper_count = app._count_running_runs(RunMode.PAPER)
  running_live_count = app._count_running_runs(RunMode.LIVE)
  venue_execution_ready, venue_execution_issues = app._venue_execution.describe_capability()

  blockers: list[str] = []
  if not app._guarded_live_execution_enabled:
    blockers.append("Guarded-live venue execution is disabled in configuration.")
  if state.kill_switch.state == "engaged":
    blockers.append("Kill switch is engaged for operator-controlled runtime sessions.")
  if state.reconciliation.state != "clear":
    blockers.append("Guarded-live reconciliation has not been cleared.")
  if state.recovery.state not in {"recovered", "recovered_with_warnings"}:
    blockers.append("Guarded-live runtime recovery has not been recorded from venue snapshots.")
  if state.recovery.state == "failed":
    blockers.append("Guarded-live runtime recovery failed after the latest restart or fault drill.")
  if not venue_execution_ready:
    blockers.append(
      "Venue order execution is unavailable: "
      + (", ".join(venue_execution_issues) if venue_execution_issues else "adapter not ready")
      + "."
    )
  if state.ownership.state in {"owned", "orphaned"} and state.ownership.owner_run_id is not None:
    blockers.append(
      "Guarded-live session ownership is still held by "
      f"{state.ownership.owner_run_id}. Resume or release it before launching a new live worker."
    )
  if runtime_alerts:
    blockers.append("Unresolved operator alerts remain in runtime operations.")

  audit_events = tuple(
    sorted(state.audit_events, key=lambda event: event.timestamp, reverse=True)
  )
  incident_events = tuple(
    sorted(state.incident_events, key=lambda event: event.timestamp, reverse=True)
  )
  delivery_history = tuple(
    sorted(state.delivery_history, key=lambda record: record.attempted_at, reverse=True)
  )
  return GuardedLiveStatus(
    generated_at=current_time,
    candidacy_status="blocked" if blockers else "candidate",
    blockers=tuple(dict.fromkeys(blockers)),
    active_alerts=tuple(live_alerts),
    alert_history=state.alert_history,
    incident_events=incident_events,
    delivery_history=delivery_history,
    kill_switch=state.kill_switch,
    reconciliation=state.reconciliation,
    recovery=state.recovery,
    ownership=state.ownership,
    order_book=state.order_book,
    session_restore=state.session_restore,
    session_handoff=state.session_handoff,
    audit_events=audit_events,
    active_runtime_alert_count=len(runtime_alerts),
    running_sandbox_count=running_sandbox_count,
    running_paper_count=running_paper_count,
    running_live_count=running_live_count,
  )

def _refresh_guarded_live_alert_state(
  app,
  *,
  current_time: datetime,
  allow_post_remediation_recompute: bool = True,
) -> tuple[GuardedLiveState, list[OperatorAlert]]:
  state = app._guarded_live_state.load_state()
  active_alerts = app._build_guarded_live_operator_alerts(
    state=state,
    current_time=current_time,
  )
  merged_history = app._merge_operator_alert_history(
    existing=state.alert_history,
    active_alerts=active_alerts,
    current_time=current_time,
  )
  incident_events = app._build_guarded_live_incident_events(
    previous_history=state.alert_history,
    merged_history=merged_history,
    current_time=current_time,
  )
  delivery_records = state.delivery_history
  new_incident_events, new_delivery_records, auto_remediation_executed = app._deliver_guarded_live_incident_events(
    incident_events=incident_events,
    current_time=current_time,
  )
  delivery_records = tuple((*new_delivery_records, *delivery_records))
  provider_synced_incident_events, provider_synced_delivery_history, provider_pull_audit_events, provider_pull_executed = (
    app._pull_sync_guarded_live_provider_recovery(
      incident_events=tuple((*new_incident_events, *state.incident_events)),
      delivery_history=delivery_records,
      current_time=current_time,
    )
  )
  delivery_records = provider_synced_delivery_history
  workflow_incident_events, workflow_delivery_history, workflow_audit_events = (
    app._refresh_guarded_live_incident_workflow(
      incident_events=provider_synced_incident_events,
      delivery_history=delivery_records,
      current_time=current_time,
    )
  )
  delivery_records = workflow_delivery_history
  refreshed_incident_events = app._apply_incident_delivery_state(
    incident_events=workflow_incident_events,
    delivery_history=delivery_records,
  )
  retry_delivery_records = app._retry_guarded_live_incident_deliveries(
    incident_events=refreshed_incident_events,
    delivery_history=delivery_records,
    current_time=current_time,
  )
  if retry_delivery_records:
    delivery_records = tuple((*retry_delivery_records, *delivery_records))
    refreshed_incident_events = app._apply_incident_delivery_state(
      incident_events=refreshed_incident_events,
      delivery_history=delivery_records,
    )
  if (
    merged_history != state.alert_history
    or refreshed_incident_events != state.incident_events
    or delivery_records != state.delivery_history
    or bool(provider_pull_audit_events)
    or bool(workflow_audit_events)
  ):
    latest_state = app._guarded_live_state.load_state()
    state = app._persist_guarded_live_state(
      replace(
        latest_state,
        alert_history=merged_history,
        incident_events=refreshed_incident_events,
        delivery_history=delivery_records,
        audit_events=tuple((*provider_pull_audit_events, *workflow_audit_events, *latest_state.audit_events)),
      )
    )
  if (auto_remediation_executed or provider_pull_executed) and allow_post_remediation_recompute:
    return app._refresh_guarded_live_alert_state(
      current_time=current_time,
      allow_post_remediation_recompute=False,
    )
  return state, active_alerts

def recover_guarded_live_runtime_state(
  app,
  *,
  actor: str,
  reason: str,
) -> GuardedLiveStatus:
  current_time = app._clock()
  state = app._guarded_live_state.load_state()
  snapshot = app._select_guarded_live_recovery_snapshot(state)
  recovered_exposures, recovery_issues = app._recover_exposures_from_venue_snapshot(snapshot)
  recovered_open_orders = snapshot.open_orders or state.order_book.open_orders
  if not snapshot.open_orders and state.order_book.open_orders:
    recovery_issues = (*recovery_issues, "using_durable_order_book_sync")

  if snapshot.verification_state == "unavailable":
    recovery_state = GuardedLiveRuntimeRecovery(
      state="failed",
      recovered_at=current_time,
      recovered_by=actor,
      reason=reason,
      source_snapshot_at=snapshot.captured_at,
      source_verification_state=snapshot.verification_state,
      summary="Guarded-live runtime recovery failed because no usable venue snapshot was available.",
      exposures=(),
      open_orders=(),
      issues=tuple(snapshot.issues),
    )
  else:
    recovered_with_warnings = bool(recovery_issues) or snapshot.verification_state != "verified"
    recovery_state = GuardedLiveRuntimeRecovery(
      state="recovered_with_warnings" if recovered_with_warnings else "recovered",
      recovered_at=current_time,
      recovered_by=actor,
      reason=reason,
      source_snapshot_at=snapshot.captured_at,
      source_verification_state=snapshot.verification_state,
      summary=(
        "Guarded-live runtime state recovered from the latest verified venue snapshot."
        if not recovered_with_warnings
        else "Guarded-live runtime state recovered from venue data with follow-up issues to review."
      ),
      exposures=recovered_exposures,
      open_orders=recovered_open_orders,
      issues=tuple(dict.fromkeys((*snapshot.issues, *recovery_issues))),
    )
  projected_state = replace(state, recovery=recovery_state)
  refreshed_reconciliation = app._build_guarded_live_reconciliation(
    state=projected_state,
    checked_at=current_time,
    checked_by=actor,
  )

  event = OperatorAuditEvent(
    event_id=f"guarded-live-runtime-recovered:{current_time.isoformat()}",
    timestamp=current_time,
    actor=actor,
    kind="guarded_live_runtime_recovered",
    summary="Guarded-live runtime recovery recorded.",
    detail=(
      f"Reason: {reason}. {recovery_state.summary} "
      f"Recovered {len(recovery_state.exposures)} exposure(s) and {len(recovery_state.open_orders)} open order(s)."
    ),
    source="guarded_live",
  )
  app._persist_guarded_live_state(
    replace(
      projected_state,
      reconciliation=refreshed_reconciliation,
      recovery=recovery_state,
      audit_events=(event, *state.audit_events),
    )
  )
  return app.get_guarded_live_status()

def acknowledge_guarded_live_incident(
  app,
  *,
  event_id: str,
  actor: str,
  reason: str,
) -> GuardedLiveStatus:
  current_time = app._clock()
  state, _ = app._refresh_guarded_live_alert_state(current_time=current_time)
  incident = app._require_active_guarded_live_incident(state=state, event_id=event_id)
  if incident.acknowledgment_state == "acknowledged":
    return app.get_guarded_live_status()

  updated_incident = replace(
    incident,
    acknowledgment_state="acknowledged",
    acknowledged_at=current_time,
    acknowledged_by=actor,
    acknowledgment_reason=reason,
    next_escalation_at=None,
  )
  incident_events = app._replace_incident_event(
    incident_events=state.incident_events,
    updated_incident=updated_incident,
  )
  delivery_history = app._suppress_pending_incident_retries(
    delivery_history=state.delivery_history,
    incident_event_id=event_id,
    reason="acknowledged_by_operator",
  )
  updated_incident, delivery_history = app._sync_incident_provider_workflow(
    incident=updated_incident,
    delivery_history=delivery_history,
    current_time=current_time,
    action="acknowledge",
    actor=actor,
    detail=reason,
  )
  incident_events = app._replace_incident_event(
    incident_events=incident_events,
    updated_incident=updated_incident,
  )
  incident_events = app._apply_incident_delivery_state(
    incident_events=incident_events,
    delivery_history=delivery_history,
  )
  audit_event = OperatorAuditEvent(
    event_id=f"guarded-live-incident-acknowledged:{event_id}:{current_time.isoformat()}",
    timestamp=current_time,
    actor=actor,
    kind="guarded_live_incident_acknowledged",
    summary=f"Guarded-live incident acknowledged for {incident.alert_id}.",
    detail=(
      f"Reason: {reason}. Incident {event_id} acknowledged and pending retries suppressed. "
      f"Provider workflow: {updated_incident.provider_workflow_state}."
    ),
    run_id=incident.run_id,
    session_id=incident.session_id,
    source="guarded_live",
  )
  app._persist_guarded_live_state(
    replace(
      state,
      incident_events=incident_events,
      delivery_history=delivery_history,
      audit_events=(audit_event, *state.audit_events),
    )
  )
  return app.get_guarded_live_status()

def remediate_guarded_live_incident(
  app,
  *,
  event_id: str,
  actor: str,
  reason: str,
) -> GuardedLiveStatus:
  current_time = app._clock()
  state, _ = app._refresh_guarded_live_alert_state(current_time=current_time)
  incident = app._require_active_guarded_live_incident(state=state, event_id=event_id)
  if incident.remediation.state == "not_applicable":
    raise ValueError("Guarded-live incident does not expose a remediation workflow")

  incident, local_results = app._execute_local_incident_remediation(
    incident=incident,
    actor=actor,
    current_time=current_time,
  )

  delivery_history = app._suppress_pending_incident_retries(
    delivery_history=state.delivery_history,
    incident_event_id=event_id,
    reason="manual_remediation_requested",
    phase="provider_remediate",
  )
  updated_incident, remediation_records = app._request_incident_remediation(
    incident=incident,
    delivery_history=delivery_history,
    current_time=current_time,
    actor=actor,
    detail=reason,
  )
  delivery_history = tuple((*remediation_records, *delivery_history))
  incident_events = app._replace_incident_event(
    incident_events=state.incident_events,
    updated_incident=updated_incident,
  )
  incident_events = app._apply_incident_delivery_state(
    incident_events=incident_events,
    delivery_history=delivery_history,
  )
  audit_event = OperatorAuditEvent(
    event_id=f"guarded-live-incident-remediation-requested:{event_id}:{current_time.isoformat()}",
    timestamp=current_time,
    actor=actor,
    kind="guarded_live_incident_remediation_requested",
    summary=f"Guarded-live remediation requested for {incident.alert_id}.",
    detail=(
      f"Reason: {reason}. Remediation state: {updated_incident.remediation.state}. "
      f"Provider workflow: {updated_incident.provider_workflow_state}. "
      f"Local execution: {app._summarize_local_remediation_results(local_results)}."
    ),
    run_id=incident.run_id,
    session_id=incident.session_id,
    source="guarded_live",
  )
  latest_state = app._guarded_live_state.load_state()
  app._persist_guarded_live_state(
    replace(
      latest_state,
      incident_events=incident_events,
      delivery_history=delivery_history,
      audit_events=(audit_event, *latest_state.audit_events),
    )
  )
  return app.get_guarded_live_status()

def escalate_guarded_live_incident(
  app,
  *,
  event_id: str,
  actor: str,
  reason: str,
) -> GuardedLiveStatus:
  current_time = app._clock()
  state, _ = app._refresh_guarded_live_alert_state(current_time=current_time)
  incident = app._require_active_guarded_live_incident(state=state, event_id=event_id)
  if incident.escalation_level >= app._operator_alert_incident_max_escalations:
    raise ValueError("incident escalation limit reached")

  (
    updated_incident,
    delivery_history,
    escalation_audit_event,
  ) = app._escalate_incident_event(
    incident=incident,
    delivery_history=state.delivery_history,
    current_time=current_time,
    actor=actor,
    reason=reason,
    trigger="manual_operator_escalation",
  )
  incident_events = app._replace_incident_event(
    incident_events=state.incident_events,
    updated_incident=updated_incident,
  )
  incident_events = app._apply_incident_delivery_state(
    incident_events=incident_events,
    delivery_history=delivery_history,
  )
  app._persist_guarded_live_state(
    replace(
      state,
      incident_events=incident_events,
      delivery_history=delivery_history,
      audit_events=(escalation_audit_event, *state.audit_events),
    )
  )
  return app.get_guarded_live_status()


def _build_guarded_live_incident_events(
  app,
  *,
  previous_history: tuple[OperatorAlert, ...],
  merged_history: tuple[OperatorAlert, ...],
  current_time: datetime,
) -> tuple[OperatorIncidentEvent, ...]:
  previous_by_id = {alert.alert_id: alert for alert in previous_history}
  incident_events: list[OperatorIncidentEvent] = []

  for alert in merged_history:
    policy = app._resolve_incident_paging_policy(alert=alert)
    remediation = app._build_incident_remediation(alert=alert, policy=policy)
    previous = previous_by_id.get(alert.alert_id)
    if alert.status == "active" and (previous is None or previous.status != "active"):
      incident_events.append(
        OperatorIncidentEvent(
          event_id=f"incident_opened:{alert.alert_id}:{alert.detected_at.isoformat()}",
          alert_id=alert.alert_id,
          timestamp=alert.detected_at,
          kind="incident_opened",
          severity=alert.severity,
          summary=alert.summary,
          detail=alert.detail,
          run_id=alert.run_id,
          session_id=alert.session_id,
          symbol=alert.symbol,
          symbols=alert.symbols,
          timeframe=alert.timeframe,
          primary_focus=alert.primary_focus,
          source=alert.source,
          paging_policy_id=policy.policy_id,
          paging_provider=policy.provider,
          delivery_targets=policy.initial_targets,
          escalation_targets=policy.escalation_targets,
          acknowledgment_state="unacknowledged",
          escalation_state=(
            "pending" if policy.escalation_targets else "not_configured"
          ),
          next_escalation_at=(
            alert.detected_at + timedelta(seconds=app._operator_alert_incident_ack_timeout_seconds)
            if policy.escalation_targets
            else None
          ),
          paging_status="pending" if policy.provider else "not_configured",
          provider_workflow_state="idle" if policy.provider else "not_configured",
          remediation=remediation,
        )
      )
      continue
    if alert.status == "resolved" and previous is not None and previous.status == "active":
      resolved_at = alert.resolved_at or current_time
      incident_events.append(
        OperatorIncidentEvent(
          event_id=f"incident_resolved:{alert.alert_id}:{resolved_at.isoformat()}",
          alert_id=alert.alert_id,
          timestamp=resolved_at,
          kind="incident_resolved",
          severity=alert.severity,
          summary=f"Resolved: {alert.summary}",
          detail=alert.detail,
          run_id=alert.run_id,
          session_id=alert.session_id,
          symbol=alert.symbol,
          symbols=alert.symbols,
          timeframe=alert.timeframe,
          primary_focus=alert.primary_focus,
          source=alert.source,
          paging_policy_id=policy.policy_id,
          paging_provider=policy.provider,
          delivery_targets=policy.resolution_targets,
          acknowledgment_state="not_applicable",
          escalation_state="not_applicable",
          paging_status="pending" if policy.provider else "not_configured",
          remediation=remediation,
        )
      )

  incident_events.sort(key=lambda event: event.timestamp, reverse=True)
  return tuple(incident_events)

def _deliver_guarded_live_incident_events(
  app,
  *,
  incident_events: tuple[OperatorIncidentEvent, ...],
  current_time: datetime,
) -> tuple[
  tuple[OperatorIncidentEvent, ...],
  tuple[OperatorIncidentDelivery, ...],
  bool,
]:
  persisted_events: list[OperatorIncidentEvent] = []
  delivery_records: list[OperatorIncidentDelivery] = []
  auto_remediation_executed = False
  for incident in incident_events:
    records = app._operator_alert_delivery.deliver(
      incident=incident,
      targets=incident.delivery_targets,
      attempt_number=1,
      phase="initial",
    )
    records = app._apply_delivery_retry_policy(
      records=records,
      current_time=current_time,
    )
    delivery_state = app._resolve_incident_delivery_state(records=records)
    external_record = next((record for record in records if record.external_provider is not None), None)
    paging_status = incident.paging_status
    external_status = incident.external_status
    if external_record is not None and delivery_state in {"delivered", "partial"}:
      if incident.kind == "incident_opened":
        paging_status = "triggered"
        external_status = "triggered"
      elif incident.kind == "incident_resolved":
        paging_status = "resolved"
        external_status = "resolved"
    persisted_events.append(
      replace(
        incident,
        delivery_state=delivery_state,
        delivery_targets=incident.delivery_targets or app._operator_alert_delivery.list_targets(),
        paging_provider=(
          external_record.external_provider if external_record is not None else incident.paging_provider
        ),
        external_provider=(
          external_record.external_provider if external_record is not None else incident.external_provider
        ),
        external_reference=(
          external_record.external_reference if external_record is not None else incident.external_reference
        ),
        external_status=external_status,
        paging_status=paging_status,
      )
    )
    delivery_records.extend(records)
    if incident.kind == "incident_opened":
      persisted_events[-1], auto_results = app._execute_local_incident_remediation(
        incident=persisted_events[-1],
        actor="system",
        current_time=current_time,
      )
      auto_remediation_executed = auto_remediation_executed or bool(auto_results)
      persisted_events[-1], remediation_records = app._request_incident_remediation(
        incident=persisted_events[-1],
        delivery_history=tuple(delivery_records),
        current_time=current_time,
        actor="system",
        detail="incident_opened",
      )
      if remediation_records:
        delivery_records.extend(remediation_records)
  return tuple(persisted_events), tuple(delivery_records), auto_remediation_executed

def _retry_guarded_live_incident_deliveries(
  app,
  *,
  incident_events: tuple[OperatorIncidentEvent, ...],
  delivery_history: tuple[OperatorIncidentDelivery, ...],
  current_time: datetime,
) -> tuple[OperatorIncidentDelivery, ...]:
  retries: list[OperatorIncidentDelivery] = []
  incidents_by_id = {incident.event_id: incident for incident in incident_events}
  for incident_event_id, target, attempt_number in app._collect_due_incident_retries(
    incident_events=incident_events,
    delivery_history=delivery_history,
    current_time=current_time,
  ):
    incident = incidents_by_id.get(incident_event_id)
    if incident is None:
      continue
    latest = app._latest_incident_delivery_record(
      delivery_history=delivery_history,
      incident_event_id=incident_event_id,
      target=target,
    )
    if latest is None:
      continue
    if latest.phase.startswith("provider_"):
      provider = latest.external_provider or incident.paging_provider or incident.external_provider
      action = latest.provider_action or latest.phase.removeprefix("provider_")
      if provider is None:
        continue
      records = app._operator_alert_delivery.sync_incident_workflow(
        incident=incident,
        provider=provider,
        action=action,
        actor="system",
        detail=f"retry:{latest.phase}",
        payload=app._build_incident_provider_workflow_payload(
          incident=incident,
          action=action,
          actor="system",
          detail=f"retry:{latest.phase}",
        ),
        attempt_number=attempt_number,
      )
    else:
      records = app._operator_alert_delivery.deliver(
        incident=incident,
        targets=(target,),
        attempt_number=attempt_number,
        phase=latest.phase,
      )
    retries.extend(
      app._apply_delivery_retry_policy(
        records=records,
        current_time=current_time,
      )
    )
  return tuple(retries)

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



def _refresh_guarded_live_incident_workflow(
  app,
  *,
  incident_events: tuple[OperatorIncidentEvent, ...],
  delivery_history: tuple[OperatorIncidentDelivery, ...],
  current_time: datetime,
) -> tuple[
  tuple[OperatorIncidentEvent, ...],
  tuple[OperatorIncidentDelivery, ...],
  tuple[OperatorAuditEvent, ...],
]:
  updated_incidents = incident_events
  effective_delivery_history = delivery_history
  audit_events: list[OperatorAuditEvent] = []

  for incident in incident_events:
    if incident.kind != "incident_opened":
      continue
    if (
      not app._incident_is_still_active(
        incident=incident,
        incident_events=updated_incidents,
      )
      or incident.acknowledgment_state == "acknowledged"
    ):
      continue
    if incident.escalation_level >= app._operator_alert_incident_max_escalations:
      continue

    trigger: str | None = None
    reason: str | None = None
    if app._incident_has_exhausted_initial_delivery(
      incident=incident,
      delivery_history=effective_delivery_history,
    ):
      trigger = "delivery_exhausted"
      reason = "retry_budget_exhausted"
    elif incident.next_escalation_at is not None and incident.next_escalation_at <= current_time:
      trigger = "ack_timeout"
      reason = "ack_timeout_elapsed"
    if trigger is None or reason is None:
      continue

    updated_incident, effective_delivery_history, audit_event = app._escalate_incident_event(
      incident=incident,
      delivery_history=effective_delivery_history,
      current_time=current_time,
      actor="system",
      reason=reason,
      trigger=trigger,
    )
    updated_incidents = app._replace_incident_event(
      incident_events=updated_incidents,
      updated_incident=updated_incident,
    )
    audit_events.append(audit_event)

  for incident in tuple(updated_incidents):
    if incident.kind != "incident_resolved":
      continue
    source_incident = app._find_latest_open_incident_for_alert(
      incident_events=updated_incidents,
      alert_id=incident.alert_id,
      resolved_at=incident.timestamp,
    )
    if source_incident is None:
      continue
    resolved_incident = replace(
      incident,
      paging_provider=source_incident.paging_provider or incident.paging_provider,
      external_provider=source_incident.external_provider or incident.external_provider,
      external_reference=source_incident.external_reference or incident.external_reference,
      provider_workflow_reference=(
        source_incident.provider_workflow_reference or incident.provider_workflow_reference
      ),
      external_status=(
        source_incident.external_status
        if source_incident.external_status != "not_synced"
        else incident.external_status
      ),
      paging_status=(
        source_incident.paging_status
        if source_incident.paging_status != "not_configured"
        else incident.paging_status
      ),
      remediation=source_incident.remediation,
    )
    if resolved_incident != incident:
      updated_incidents = app._replace_incident_event(
        incident_events=updated_incidents,
        updated_incident=resolved_incident,
      )
    if source_incident.external_status == "resolved" or source_incident.paging_status == "resolved":
      continue
    if app._incident_has_provider_workflow_phase(
      incident_event_id=resolved_incident.event_id,
      delivery_history=effective_delivery_history,
      phase="provider_resolve",
    ):
      continue
    resolve_detail = resolved_incident.detail
    remediation_detail = (
      resolved_incident.remediation.detail
      or resolved_incident.remediation.summary
    )
    if remediation_detail:
      resolve_detail = f"{resolve_detail}. Remediation: {remediation_detail}"
    resolved_incident, effective_delivery_history = app._sync_incident_provider_workflow(
      incident=resolved_incident,
      delivery_history=effective_delivery_history,
      current_time=current_time,
      action="resolve",
      actor="system",
      detail=resolve_detail,
      payload=resolved_incident.remediation.provider_payload,
    )
    resolved_incident = replace(
      resolved_incident,
      remediation=replace(
        resolved_incident.remediation,
        provider_recovery=replace(
          resolved_incident.remediation.provider_recovery,
          lifecycle_state="resolved",
          status_machine=app._build_provider_recovery_status_machine(
            existing=resolved_incident.remediation.provider_recovery.status_machine,
            remediation_state="completed",
            event_kind="provider_resolve_requested",
            workflow_state=resolved_incident.provider_workflow_state,
            workflow_action="resolve",
            job_state="resolved",
            sync_state="bidirectional_synced",
            detail=resolve_detail,
            event_at=current_time,
            attempt_number=resolved_incident.remediation.provider_recovery.status_machine.attempt_number,
          ),
          updated_at=current_time,
        ),
      ),
    )
    updated_incidents = app._replace_incident_event(
      incident_events=updated_incidents,
      updated_incident=resolved_incident,
    )
    audit_events.append(
      OperatorAuditEvent(
        event_id=(
          f"guarded-live-incident-provider-resolve:{resolved_incident.event_id}:{current_time.isoformat()}"
        ),
        timestamp=current_time,
        actor="system",
        kind="guarded_live_incident_provider_resolved",
        summary=f"Guarded-live provider workflow resolve synced for {resolved_incident.alert_id}.",
        detail=(
          f"Provider workflow resolve synced via "
          f"{resolved_incident.paging_provider or resolved_incident.external_provider or 'unknown'}. "
          f"Reference: {resolved_incident.provider_workflow_reference or resolved_incident.external_reference or 'n/a'}. "
          f"State: {resolved_incident.provider_workflow_state}."
        ),
        run_id=resolved_incident.run_id,
        session_id=resolved_incident.session_id,
        source="guarded_live",
      )
    )
  return updated_incidents, effective_delivery_history, tuple(audit_events)

def _sync_incident_provider_workflow(
  app,
  *,
  incident: OperatorIncidentEvent,
  delivery_history: tuple[OperatorIncidentDelivery, ...],
  current_time: datetime,
  action: str,
  actor: str,
  detail: str,
  payload: dict[str, Any] | None = None,
) -> tuple[OperatorIncidentEvent, tuple[OperatorIncidentDelivery, ...]]:
  provider = incident.paging_provider or incident.external_provider
  if provider is None:
    return (
      replace(
        incident,
        provider_workflow_state="not_configured",
        provider_workflow_action=action,
      ),
      delivery_history,
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
        paging_provider=normalized_provider,
        provider_workflow_state="not_supported",
        provider_workflow_action=action,
        provider_workflow_last_attempted_at=current_time,
      ),
      delivery_history,
    )

  records = app._operator_alert_delivery.sync_incident_workflow(
    incident=incident,
    provider=normalized_provider or provider,
    action=action,
    actor=actor,
    detail=detail,
    payload=app._build_incident_provider_workflow_payload(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
    ),
    attempt_number=1,
  )
  records = app._apply_delivery_retry_policy(
    records=records,
    current_time=current_time,
  )
  latest = app._latest_provider_workflow_record(records=records)
  updated_incident = replace(
    incident,
    paging_provider=normalized_provider,
    external_provider=normalized_provider or incident.external_provider,
    provider_workflow_action=action,
    provider_workflow_last_attempted_at=(
      latest.attempted_at if latest is not None else current_time
    ),
    provider_workflow_reference=(
      latest.external_reference
      if latest is not None and latest.external_reference is not None
      else incident.provider_workflow_reference
    ),
  )
  return updated_incident, tuple((*records, *delivery_history))

def _escalate_incident_event(
  app,
  *,
  incident: OperatorIncidentEvent,
  delivery_history: tuple[OperatorIncidentDelivery, ...],
  current_time: datetime,
  actor: str,
  reason: str,
  trigger: str,
) -> tuple[OperatorIncidentEvent, tuple[OperatorIncidentDelivery, ...], OperatorAuditEvent]:
  escalation_targets = incident.escalation_targets or incident.delivery_targets
  if not escalation_targets:
    raise ValueError("incident escalation has no configured delivery targets")

  updated_delivery_history = app._suppress_pending_incident_retries(
    delivery_history=delivery_history,
    incident_event_id=incident.event_id,
    reason=f"escalated:{trigger}",
    phase="initial",
  )
  next_level = incident.escalation_level + 1
  next_escalation_at = None
  if (
    incident.acknowledgment_state != "acknowledged"
    and next_level < app._operator_alert_incident_max_escalations
  ):
    next_escalation_at = current_time + timedelta(
      seconds=app._resolve_incident_escalation_backoff_seconds(next_level)
    )

  updated_incident = replace(
    incident,
    escalation_level=next_level,
    escalation_state="escalated",
    last_escalated_at=current_time,
    last_escalated_by=actor,
    escalation_reason=reason,
    next_escalation_at=next_escalation_at,
  )
  escalation_deliveries = app._operator_alert_delivery.deliver(
    incident=updated_incident,
    targets=escalation_targets,
    attempt_number=1,
    phase="escalation",
  )
  escalation_deliveries = app._apply_delivery_retry_policy(
    records=escalation_deliveries,
    current_time=current_time,
  )
  updated_delivery_history = tuple((*escalation_deliveries, *updated_delivery_history))
  updated_incident, updated_delivery_history = app._sync_incident_provider_workflow(
    incident=updated_incident,
    delivery_history=updated_delivery_history,
    current_time=current_time,
    action="escalate",
    actor=actor,
    detail=reason,
  )
  audit_event = OperatorAuditEvent(
    event_id=f"guarded-live-incident-escalated:{incident.event_id}:{current_time.isoformat()}",
    timestamp=current_time,
    actor=actor,
    kind="guarded_live_incident_escalated",
    summary=f"Guarded-live incident escalated for {incident.alert_id}.",
    detail=(
      f"Trigger: {trigger}. Reason: {reason}. Escalation level {next_level} "
      f"sent via {', '.join(escalation_targets)}. "
      f"Provider workflow: {updated_incident.provider_workflow_state}."
    ),
    run_id=incident.run_id,
    session_id=incident.session_id,
    source="guarded_live",
  )
  return updated_incident, updated_delivery_history, audit_event

def _build_live_operator_alerts_for_run(
  app,
  *,
  run: RunRecord,
  current_time: datetime,
) -> list[OperatorAlert]:
  session = run.provenance.runtime_session
  if session is None:
    return []

  alerts: list[OperatorAlert] = []
  symbol = run.config.symbols[0] if run.config.symbols else run.config.run_id
  delivery_targets = app._guarded_live_delivery_targets()
  market_context = app._build_operator_alert_market_context(
    symbol=symbol,
    symbols=list(run.config.symbols),
    timeframe=run.config.timeframe,
  )
  failed_event = app._latest_runtime_note_event(run=run, kind="guarded_live_worker_failed")
  if failed_event is not None or session.lifecycle_state == "failed" or run.status == RunStatus.FAILED:
    detected_at = (
      failed_event["timestamp"]
      or run.ended_at
      or session.last_heartbeat_at
      or run.started_at
    )
    detail = failed_event["detail"] if failed_event is not None else (
      run.notes[-1] if run.notes else "Guarded-live worker entered a failed runtime state."
    )
    alerts.append(
      OperatorAlert(
        alert_id=f"guarded-live:worker-failed:{run.config.run_id}:{session.session_id}",
        severity="critical",
        category="worker_failure",
        summary=f"Guarded-live worker failed for {symbol}.",
        detail=detail,
        detected_at=detected_at,
        run_id=run.config.run_id,
        session_id=session.session_id,
        **market_context,
        source="guarded_live",
        delivery_targets=delivery_targets,
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
        alert_id=f"guarded-live:worker-stale:{run.config.run_id}:{session.session_id}",
        severity="warning",
        category="stale_runtime",
        summary=f"Guarded-live worker heartbeat is stale for {symbol}.",
        detail=(
          f"Last heartbeat at {heartbeat_at.isoformat()} exceeded the "
          f"{session.heartbeat_timeout_seconds}s timeout while the live run remains active."
        ),
        detected_at=heartbeat_at,
        run_id=run.config.run_id,
        session_id=session.session_id,
        **market_context,
        source="guarded_live",
        delivery_targets=delivery_targets,
      )
    )

  risk_issues: list[str] = []
  latest_equity = run.equity_curve[-1] if run.equity_curve else None
  max_drawdown_pct = run.metrics.get("max_drawdown_pct")
  if isinstance(max_drawdown_pct, Number) and float(max_drawdown_pct) >= app._guarded_live_drawdown_breach_pct:
    risk_issues.append(
      f"max drawdown {float(max_drawdown_pct):.2f}% breached the "
      f"{app._guarded_live_drawdown_breach_pct:.2f}% guardrail"
    )
  total_return_pct = run.metrics.get("total_return_pct")
  if isinstance(total_return_pct, Number) and float(total_return_pct) <= -app._guarded_live_loss_breach_pct:
    risk_issues.append(
      f"total return {float(total_return_pct):.2f}% breached the "
      f"-{app._guarded_live_loss_breach_pct:.2f}% loss guardrail"
    )
  if latest_equity is not None and latest_equity.cash < -app._guarded_live_balance_tolerance:
    risk_issues.append(
      f"cash balance fell below zero to {latest_equity.cash:.2f}"
    )
  if latest_equity is not None and latest_equity.equity > app._guarded_live_balance_tolerance:
    pending_buy_notional = app._estimate_guarded_live_open_buy_notional(run)
    gross_open_risk = max(latest_equity.exposure, 0.0) + pending_buy_notional
    gross_open_risk_ratio = gross_open_risk / latest_equity.equity
    if gross_open_risk_ratio > app._guarded_live_gross_open_risk_ratio:
      risk_issues.append(
        f"gross open risk reached {gross_open_risk_ratio:.2f}x equity "
        f"({gross_open_risk:.2f} notional including {pending_buy_notional:.2f} pending buy notional)"
      )
  if risk_issues:
    alerts.append(
      OperatorAlert(
        alert_id=f"guarded-live:risk-breach:{run.config.run_id}:{session.session_id}",
        severity="critical",
        category="risk_breach",
        summary=f"Guarded-live risk guardrail breached for {symbol}.",
        detail=(
          "; ".join(risk_issues)
          + (
            f". Latest equity {latest_equity.equity:.2f}."
            if latest_equity is not None
            else ""
          )
        ),
        detected_at=(
          latest_equity.timestamp
          if latest_equity is not None
          else heartbeat_at
        ),
        run_id=run.config.run_id,
        session_id=session.session_id,
        **market_context,
        source="guarded_live",
        delivery_targets=delivery_targets,
      )
    )

  if run.status == RunStatus.RUNNING and session.recovery_count >= app._guarded_live_recovery_alert_threshold:
    alerts.append(
      OperatorAlert(
        alert_id=f"guarded-live:recovery-loop:{run.config.run_id}:{session.session_id}",
        severity="critical" if session.recovery_count >= app._guarded_live_recovery_alert_threshold + 1 else "warning",
        category="runtime_recovery",
        summary=f"Guarded-live worker recovery loop detected for {symbol}.",
        detail=(
          f"Runtime session recovered {session.recovery_count} times. "
          f"Last recovery: {session.last_recovery_reason or 'unknown'} at "
          f"{session.last_recovered_at.isoformat() if session.last_recovered_at is not None else 'n/a'}."
        ),
        detected_at=session.last_recovered_at or heartbeat_at,
        run_id=run.config.run_id,
        session_id=session.session_id,
        **market_context,
        source="guarded_live",
        delivery_targets=delivery_targets,
      )
    )

  if run.status == RunStatus.RUNNING:
    stale_orders = []
    for order in run.orders:
      if order.status not in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}:
        continue
      synced_at = order.last_synced_at or order.updated_at or order.created_at
      if (current_time - synced_at).total_seconds() <= session.heartbeat_timeout_seconds:
        continue
      stale_orders.append((order, synced_at))
    if stale_orders:
      stale_order_ids = ", ".join(order.order_id for order, _ in stale_orders[:3])
      oldest_sync_at = min(synced_at for _, synced_at in stale_orders)
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:order-sync:{run.config.run_id}:{session.session_id}",
          severity="warning",
          category="order_sync",
          summary=f"Guarded-live venue order sync is stale for {symbol}.",
          detail=(
            f"{len(stale_orders)} active order(s) have not synced within "
            f"{session.heartbeat_timeout_seconds}s. Orders: {stale_order_ids}."
          ),
          detected_at=oldest_sync_at,
          run_id=run.config.run_id,
          session_id=session.session_id,
          **market_context,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )
  return alerts
