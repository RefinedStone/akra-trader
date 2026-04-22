from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from datetime import timedelta
from typing import Any

from akra_trader.domain.models import GuardedLiveState
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentRemediation

def _collect_due_incident_retries(
  app: Any,
  *,
  incident_events: tuple[OperatorIncidentEvent, ...],
  delivery_history: tuple[OperatorIncidentDelivery, ...],
  current_time: datetime,
) -> tuple[tuple[str, str, int], ...]:
  due_retries: list[tuple[str, str, int]] = []
  incidents_by_id = {incident.event_id: incident for incident in incident_events}
  latest_by_key = app._latest_delivery_records_by_key(delivery_history=delivery_history)

  for latest in latest_by_key.values():
    incident = incidents_by_id.get(latest.incident_event_id)
    if incident is None:
      continue
    if incident.kind == "incident_opened" and not app._incident_is_still_active(
      incident=incident,
      incident_events=incident_events,
    ):
      continue
    if (
      incident.kind == "incident_opened"
      and incident.acknowledgment_state == "acknowledged"
      and not latest.phase.startswith("provider_")
    ):
      continue
    if latest.status != "retry_scheduled" or latest.next_retry_at is None:
      continue
    if latest.next_retry_at > current_time:
      continue
    if latest.attempt_number >= app._operator_alert_delivery_max_attempts:
      continue
    due_retries.append((latest.incident_event_id, latest.target, latest.attempt_number + 1))
  due_retries.sort()
  return tuple(due_retries)

def _apply_incident_delivery_state(
  app: Any,
  *,
  incident_events: tuple[OperatorIncidentEvent, ...],
  delivery_history: tuple[OperatorIncidentDelivery, ...],
) -> tuple[OperatorIncidentEvent, ...]:
  latest_by_key = app._latest_delivery_records_by_key(delivery_history=delivery_history)

  refreshed: list[OperatorIncidentEvent] = []
  for incident in incident_events:
    delivery_records = tuple(
      record
      for key, record in latest_by_key.items()
      if key[0] == incident.event_id
      and not key[2].startswith("provider_")
    )
    provider_records = tuple(
      record
      for key, record in latest_by_key.items()
      if key[0] == incident.event_id
      and key[2].startswith("provider_")
    )
    latest_provider_record = app._latest_provider_workflow_record(records=provider_records)
    prefer_provider_authoritative = (
      incident.external_last_synced_at is not None
      and (
        latest_provider_record is None
        or latest_provider_record.attempted_at <= incident.external_last_synced_at
      )
    )
    refreshed.append(
      replace(
        incident,
        delivery_state=app._resolve_incident_delivery_state(records=delivery_records),
        provider_workflow_state=(
          incident.provider_workflow_state
          if prefer_provider_authoritative
          else (
            app._resolve_incident_delivery_state(records=provider_records)
            if provider_records
            else incident.provider_workflow_state
          )
        ),
        provider_workflow_action=(
          incident.provider_workflow_action
          if prefer_provider_authoritative
          else (
            latest_provider_record.provider_action
            if latest_provider_record is not None
            else incident.provider_workflow_action
          )
        ),
        provider_workflow_last_attempted_at=(
          incident.provider_workflow_last_attempted_at
          if prefer_provider_authoritative
          else (
            latest_provider_record.attempted_at
            if latest_provider_record is not None
            else incident.provider_workflow_last_attempted_at
          )
        ),
        provider_workflow_reference=(
          incident.provider_workflow_reference
          if prefer_provider_authoritative
          else (
            latest_provider_record.external_reference
            if latest_provider_record is not None and latest_provider_record.external_reference is not None
            else incident.provider_workflow_reference
          )
        ),
        remediation=app._refresh_incident_remediation_state(
          incident=incident,
          latest_by_key=latest_by_key,
        ),
      )
    )
  refreshed.sort(key=lambda event: event.timestamp, reverse=True)
  return tuple(refreshed)

def _refresh_incident_remediation_state(
  app: Any,
  *,
  incident: OperatorIncidentEvent,
  latest_by_key: dict[tuple[str, str, str], OperatorIncidentDelivery],
) -> OperatorIncidentRemediation:
  remediation = incident.remediation
  if remediation.state == "not_applicable":
    return remediation
  remediation_records = tuple(
    record
    for key, record in latest_by_key.items()
    if key[0] == incident.event_id and key[2] == "provider_remediate"
  )
  if not remediation_records:
    return remediation
  latest_record = app._latest_provider_workflow_record(records=remediation_records)
  prefer_provider_authoritative = (
    incident.external_last_synced_at is not None
    and (
      latest_record is None
      or latest_record.attempted_at <= incident.external_last_synced_at
    )
  )
  if prefer_provider_authoritative:
    return remediation
  next_state = app._resolve_remediation_delivery_state(
    records=remediation_records,
    current_state=remediation.state,
  )
  return replace(
    remediation,
    state=next_state,
    last_attempted_at=(
      latest_record.attempted_at if latest_record is not None else remediation.last_attempted_at
    ),
    provider=(
      latest_record.external_provider
      if latest_record is not None and latest_record.external_provider is not None
      else remediation.provider
    ),
    reference=(
      latest_record.external_reference
      if latest_record is not None and latest_record.external_reference is not None
      else remediation.reference
    ),
    provider_recovery=app._refresh_provider_recovery_phase_graphs(
      provider_recovery=replace(
        remediation.provider_recovery,
        status_machine=app._build_provider_recovery_status_machine(
          existing=remediation.provider_recovery.status_machine,
          remediation_state=next_state,
          event_kind=remediation.provider_recovery.status_machine.last_event_kind,
          workflow_state=app._resolve_incident_delivery_state(records=remediation_records),
          workflow_action=(
            latest_record.provider_action if latest_record is not None else remediation.provider_recovery.status_machine.workflow_action
          ),
          attempt_number=latest_record.attempt_number if latest_record is not None else remediation.provider_recovery.status_machine.attempt_number,
          detail=latest_record.detail if latest_record is not None else remediation.provider_recovery.status_machine.last_detail,
          event_at=latest_record.attempted_at if latest_record is not None else remediation.provider_recovery.status_machine.last_event_at,
        ),
      ),
      synced_at=latest_record.attempted_at if latest_record is not None else app._clock(),
    ),
  )

def _resolve_remediation_delivery_state(
  app: Any,
  *,
  records: tuple[OperatorIncidentDelivery, ...],
  current_state: str,
) -> str:
  if current_state in {
    "executed",
    "partial",
    "failed",
    "skipped",
    "completed",
    "provider_recovering",
    "provider_recovered",
  }:
    return current_state
  delivery_state = app._resolve_incident_delivery_state(records=records)
  mapping = {
    "delivered": "requested",
    "partial": "requested",
    "retrying": "retrying",
    "failed": "failed",
    "suppressed": "suppressed",
    "not_configured": current_state,
  }
  return mapping.get(delivery_state, current_state)

def _apply_delivery_retry_policy(
  app: Any,
  *,
  records: tuple[OperatorIncidentDelivery, ...],
  current_time: datetime,
) -> tuple[OperatorIncidentDelivery, ...]:
  updated: list[OperatorIncidentDelivery] = []
  for record in records:
    if record.status != "failed":
      updated.append(record)
      continue
    if record.attempt_number >= app._operator_alert_delivery_max_attempts:
      updated.append(record)
      continue
    updated.append(
      replace(
        record,
        status="retry_scheduled",
        next_retry_at=current_time + timedelta(
          seconds=app._resolve_delivery_backoff_seconds(record.attempt_number)
        ),
      )
    )
  return tuple(updated)

def _resolve_delivery_backoff_seconds(app: Any, attempt_number: int) -> int:
  multiplier = app._operator_alert_delivery_backoff_multiplier ** max(attempt_number - 1, 0)
  backoff = int(app._operator_alert_delivery_initial_backoff_seconds * multiplier)
  return min(backoff, app._operator_alert_delivery_max_backoff_seconds)

def _resolve_incident_delivery_state(
  *,
  records: tuple[OperatorIncidentDelivery, ...],
) -> str:
  if not records:
    return "not_configured"
  statuses = {record.status for record in records}
  if statuses <= {"delivered", "retry_suppressed"} and "delivered" in statuses:
    return "delivered"
  if "retry_scheduled" in statuses:
    return "retrying"
  if statuses == {"retry_suppressed"}:
    return "suppressed"
  if "delivered" in statuses:
    return "partial"
  return "failed"

def _latest_delivery_records_by_key(
  *,
  delivery_history: tuple[OperatorIncidentDelivery, ...],
) -> dict[tuple[str, str, str], OperatorIncidentDelivery]:
  latest_by_key: dict[tuple[str, str, str], OperatorIncidentDelivery] = {}
  for record in delivery_history:
    key = (record.incident_event_id, record.target, record.phase)
    existing = latest_by_key.get(key)
    if existing is None or record.attempt_number > existing.attempt_number:
      latest_by_key[key] = record
  return latest_by_key

def _latest_incident_delivery_record(
  app: Any,
  *,
  delivery_history: tuple[OperatorIncidentDelivery, ...],
  incident_event_id: str,
  target: str,
) -> OperatorIncidentDelivery | None:
  latest_by_key = app._latest_delivery_records_by_key(delivery_history=delivery_history)
  candidates = [
    record
    for key, record in latest_by_key.items()
    if key[0] == incident_event_id and key[1] == target
  ]
  if not candidates:
    return None
  candidates.sort(key=lambda record: (record.phase == "escalation", record.attempt_number), reverse=True)
  return candidates[0]

def _latest_provider_workflow_record(
  *,
  records: tuple[OperatorIncidentDelivery, ...],
) -> OperatorIncidentDelivery | None:
  if not records:
    return None
  return max(
    records,
    key=lambda record: (
      record.attempted_at,
      record.attempt_number,
    ),
  )

def _replace_incident_event(
  *,
  incident_events: tuple[OperatorIncidentEvent, ...],
  updated_incident: OperatorIncidentEvent,
) -> tuple[OperatorIncidentEvent, ...]:
  replaced = [
    updated_incident if incident.event_id == updated_incident.event_id else incident
    for incident in incident_events
  ]
  replaced.sort(key=lambda event: event.timestamp, reverse=True)
  return tuple(replaced)

def _incident_is_still_active(
  *,
  incident: OperatorIncidentEvent,
  incident_events: tuple[OperatorIncidentEvent, ...],
) -> bool:
  if incident.kind != "incident_opened":
    return False
  for candidate in incident_events:
    if candidate.alert_id != incident.alert_id or candidate.kind != "incident_resolved":
      continue
    if candidate.timestamp >= incident.timestamp:
      return False
  return True

def _find_latest_open_incident_for_alert(
  *,
  incident_events: tuple[OperatorIncidentEvent, ...],
  alert_id: str,
  resolved_at: datetime,
) -> OperatorIncidentEvent | None:
  candidates = [
    incident
    for incident in incident_events
    if incident.kind == "incident_opened"
    and incident.alert_id == alert_id
    and incident.timestamp <= resolved_at
  ]
  if not candidates:
    return None
  candidates.sort(key=lambda incident: incident.timestamp, reverse=True)
  return candidates[0]

def _incident_has_provider_workflow_phase(
  *,
  incident_event_id: str,
  delivery_history: tuple[OperatorIncidentDelivery, ...],
  phase: str,
) -> bool:
  latest_by_key = _latest_delivery_records_by_key(
    delivery_history=delivery_history,
  )
  return any(key[0] == incident_event_id and key[2] == phase for key in latest_by_key)

def _require_active_guarded_live_incident(
  app: Any,
  *,
  state: GuardedLiveState,
  event_id: str,
) -> OperatorIncidentEvent:
  incident = next((event for event in state.incident_events if event.event_id == event_id), None)
  if incident is None:
    raise LookupError("Guarded-live incident not found")
  if incident.kind != "incident_opened":
    raise ValueError("Only active incident_opened records can be acknowledged or escalated")
  if not app._incident_is_still_active(incident=incident, incident_events=state.incident_events):
    raise ValueError("Guarded-live incident is no longer active")
  return incident

def _find_guarded_live_incident_for_external_sync(
  app: Any,
  *,
  state: GuardedLiveState,
  alert_id: str | None,
  external_reference: str | None,
) -> OperatorIncidentEvent:
  candidates = [
    incident
    for incident in state.incident_events
    if incident.kind == "incident_opened"
    and (
      (alert_id is not None and incident.alert_id == alert_id)
      or (
        external_reference is not None
        and (
          incident.external_reference == external_reference
          or incident.provider_workflow_reference == external_reference
          or incident.alert_id == external_reference
        )
      )
    )
  ]
  if not candidates:
    raise LookupError("Guarded-live incident not found for external sync")
  candidates.sort(
    key=lambda incident: (
      app._incident_is_still_active(incident=incident, incident_events=state.incident_events),
      incident.timestamp,
    ),
    reverse=True,
  )
  return candidates[0]

def _suppress_pending_incident_retries(
  *,
  delivery_history: tuple[OperatorIncidentDelivery, ...],
  incident_event_id: str,
  reason: str,
  phase: str | None = None,
) -> tuple[OperatorIncidentDelivery, ...]:
  updated: list[OperatorIncidentDelivery] = []
  for record in delivery_history:
    if record.incident_event_id != incident_event_id:
      updated.append(record)
      continue
    if phase is not None and record.phase != phase:
      updated.append(record)
      continue
    if record.status != "retry_scheduled":
      updated.append(record)
      continue
    updated.append(
      replace(
        record,
        status="retry_suppressed",
        next_retry_at=None,
        detail=f"{record.detail}; retry_suppressed:{reason}",
      )
    )
  return tuple(updated)

def _confirm_external_provider_workflow(
  app: Any,
  *,
  delivery_history: tuple[OperatorIncidentDelivery, ...],
  incident: OperatorIncidentEvent,
  provider: str,
  event_kind: str,
  detail: str,
  occurred_at: datetime,
  external_reference: str | None,
) -> tuple[OperatorIncidentDelivery, ...]:
  phase = app._provider_phase_for_event_kind(event_kind)
  if phase is None:
    return delivery_history
  provider_prefix = app._normalize_paging_provider(provider) or provider
  updated_history = app._suppress_pending_incident_retries(
    delivery_history=delivery_history,
    incident_event_id=incident.event_id,
    reason=f"external_confirmed:{provider_prefix}:{event_kind}",
    phase=phase,
  )
  confirmation = OperatorIncidentDelivery(
    delivery_id=f"{incident.event_id}:{provider_prefix}_external:{event_kind}:{occurred_at.isoformat()}",
    incident_event_id=incident.event_id,
    alert_id=incident.alert_id,
    incident_kind=incident.kind,
    target=f"{provider_prefix}_external_sync",
    status="delivered",
    attempted_at=occurred_at,
    detail=f"external_provider_confirmed:{event_kind}:{detail}",
    phase=phase,
    provider_action=phase.removeprefix("provider_"),
    external_provider=provider_prefix,
    external_reference=external_reference,
    source=incident.source,
  )
  return (confirmation, *updated_history)

def _provider_phase_for_event_kind(event_kind: str) -> str | None:
  mapping = {
    "triggered": "provider_trigger",
    "acknowledged": "provider_acknowledge",
    "escalated": "provider_escalate",
    "resolved": "provider_resolve",
    "remediation_requested": "provider_remediate",
    "remediation_started": "provider_remediate",
    "remediation_completed": "provider_remediate",
    "remediation_failed": "provider_remediate",
  }
  return mapping.get(event_kind)

def _incident_has_exhausted_initial_delivery(
  app: Any,
  *,
  incident: OperatorIncidentEvent,
  delivery_history: tuple[OperatorIncidentDelivery, ...],
) -> bool:
  latest_by_key = app._latest_delivery_records_by_key(delivery_history=delivery_history)
  initial_records = [
    record
    for key, record in latest_by_key.items()
    if key[0] == incident.event_id and key[2] == "initial"
  ]
  return any(record.status == "failed" for record in initial_records)

def _resolve_incident_escalation_backoff_seconds(app: Any, escalation_level: int) -> int:
  multiplier = app._operator_alert_incident_escalation_backoff_multiplier ** max(escalation_level - 1, 0)
  backoff = int(app._operator_alert_incident_ack_timeout_seconds * multiplier)
  return min(backoff, app._operator_alert_delivery_max_backoff_seconds)
