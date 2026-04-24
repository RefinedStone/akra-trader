from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from datetime import timedelta
from typing import Any

from akra_trader.domain.models import OperatorAuditEvent
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent

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
  lineage_evidence_pack_id: str | None = None,
  lineage_evidence_retention_expires_at: datetime | None = None,
  lineage_evidence_summary: str | None = None,
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
    lineage_evidence_pack_id=(
      lineage_evidence_pack_id.strip()
      if isinstance(lineage_evidence_pack_id, str) and lineage_evidence_pack_id.strip()
      else incident.lineage_evidence_pack_id
    ),
    lineage_evidence_retention_expires_at=(
      lineage_evidence_retention_expires_at
      if lineage_evidence_retention_expires_at is not None
      else incident.lineage_evidence_retention_expires_at
    ),
    lineage_evidence_summary=(
      lineage_evidence_summary.strip()
      if isinstance(lineage_evidence_summary, str) and lineage_evidence_summary.strip()
      else incident.lineage_evidence_summary
    ),
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
      f"{_format_lineage_evidence_pack_audit_detail(updated_incident)}"
      f"Provider workflow: {updated_incident.provider_workflow_state}."
    ),
    run_id=incident.run_id,
    session_id=incident.session_id,
    source="guarded_live",
  )
  return updated_incident, updated_delivery_history, audit_event


def _format_lineage_evidence_pack_audit_detail(incident: OperatorIncidentEvent) -> str:
  if not incident.lineage_evidence_pack_id:
    return ""
  retention = (
    incident.lineage_evidence_retention_expires_at.isoformat()
    if incident.lineage_evidence_retention_expires_at is not None
    else "unknown"
  )
  summary = (
    f" Summary: {incident.lineage_evidence_summary}."
    if incident.lineage_evidence_summary
    else ""
  )
  return (
    f"Lineage evidence pack {incident.lineage_evidence_pack_id} "
    f"retained until {retention}.{summary} "
  )
