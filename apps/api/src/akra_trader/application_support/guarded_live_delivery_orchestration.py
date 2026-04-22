from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent

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
