from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from akra_trader.domain.models import OperatorAuditEvent
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync

def _pull_sync_guarded_live_provider_recovery(
  app,
  *,
  incident_events: tuple[OperatorIncidentEvent, ...],
  delivery_history: tuple[OperatorIncidentDelivery, ...],
  current_time: datetime,
) -> tuple[
  tuple[OperatorIncidentEvent, ...],
  tuple[OperatorIncidentDelivery, ...],
  tuple[OperatorAuditEvent, ...],
  bool,
]:
  updated_incidents = incident_events
  effective_delivery_history = delivery_history
  audit_events: list[OperatorAuditEvent] = []
  local_remediation_executed = False

  for incident in tuple(updated_incidents):
    if incident.kind not in {"incident_opened", "incident_resolved"}:
      continue
    provider = app._normalize_paging_provider(
      incident.remediation.provider or incident.paging_provider or incident.external_provider
    )
    if provider is None:
      continue
    if not any((
      incident.provider_workflow_reference,
      incident.external_reference,
      incident.remediation.reference,
    )):
      continue
    try:
      pull_sync = app._operator_alert_delivery.pull_incident_workflow_state(
        incident=incident,
        provider=provider,
      )
    except Exception as exc:
      audit_events.append(
        OperatorAuditEvent(
          event_id=f"guarded-live-incident-provider-pull-sync-failed:{incident.event_id}:{current_time.isoformat()}",
          timestamp=current_time,
          actor="system",
          kind="guarded_live_incident_provider_pull_sync_failed",
          summary=f"Guarded-live provider pull-sync failed for {incident.alert_id}.",
          detail=(
            f"Provider-authoritative pull-sync failed via {provider}. "
            f"Reference: {incident.provider_workflow_reference or incident.external_reference or incident.alert_id}. "
            f"Error: {exc}."
          ),
          run_id=incident.run_id,
          session_id=incident.session_id,
          source="guarded_live",
        )
      )
      continue
    if pull_sync is None:
      continue
    previous_incident = incident
    previous_history = effective_delivery_history
    updated_incident, effective_delivery_history, executed = app._apply_provider_pull_sync(
      incident=incident,
      pull_sync=pull_sync,
      delivery_history=effective_delivery_history,
      current_time=current_time,
    )
    if updated_incident == previous_incident and effective_delivery_history == previous_history:
      continue
    updated_incidents = app._replace_incident_event(
      incident_events=updated_incidents,
      updated_incident=updated_incident,
    )
    local_remediation_executed = local_remediation_executed or executed
    audit_events.append(
      OperatorAuditEvent(
        event_id=f"guarded-live-incident-provider-pull-sync:{updated_incident.event_id}:{pull_sync.synced_at.isoformat()}",
        timestamp=pull_sync.synced_at,
        actor=f"{provider}:pull_sync",
        kind="guarded_live_incident_provider_pull_synced",
        summary=f"Guarded-live provider recovery reconciled for {updated_incident.alert_id}.",
        detail=(
          f"Provider-authoritative pull-sync via {provider}. "
          f"Workflow state: {pull_sync.workflow_state}. "
          f"Recovery state: {pull_sync.remediation_state or 'n/a'}. "
          f"Reference: {pull_sync.workflow_reference or updated_incident.provider_workflow_reference or updated_incident.external_reference or updated_incident.alert_id}. "
          f"Local remediation: {'executed' if executed else 'not_executed'}."
        ),
        run_id=updated_incident.run_id,
        session_id=updated_incident.session_id,
        source="guarded_live",
      )
    )

  return updated_incidents, effective_delivery_history, tuple(audit_events), local_remediation_executed

def _apply_provider_pull_sync(
  app,
  *,
  incident: OperatorIncidentEvent,
  pull_sync: OperatorIncidentProviderPullSync,
  delivery_history: tuple[OperatorIncidentDelivery, ...],
  current_time: datetime,
) -> tuple[OperatorIncidentEvent, tuple[OperatorIncidentDelivery, ...], bool]:
  provider = app._normalize_paging_provider(pull_sync.provider) or pull_sync.provider
  synced_at = pull_sync.synced_at or current_time
  payload = app._normalize_incident_workflow_payload(pull_sync.payload)
  detail_copy = (
    pull_sync.detail
    or app._first_non_empty_string(
      payload.get("detail"),
      payload.get("remediation_detail"),
      payload.get("status_detail"),
      payload.get("summary"),
      payload.get("message"),
    )
    or f"{provider}_pull_synced"
  )
  workflow_reference = (
    pull_sync.workflow_reference
    or app._first_non_empty_string(
      payload.get("workflow_reference"),
      payload.get("provider_workflow_reference"),
    )
    or incident.provider_workflow_reference
    or incident.remediation.provider_recovery.workflow_reference
    or incident.external_reference
  )
  external_reference = (
    pull_sync.external_reference
    or incident.external_reference
    or incident.remediation.reference
    or incident.alert_id
  )
  event_kind = app._resolve_provider_pull_sync_event_kind(
    incident=incident,
    pull_sync=pull_sync,
    payload=payload,
  )
  provider_action = (
    app._provider_phase_for_event_kind(event_kind).removeprefix("provider_")
    if event_kind is not None and app._provider_phase_for_event_kind(event_kind) is not None
    else incident.provider_workflow_action
  )
  updated_incident = replace(
    incident,
    paging_provider=provider or incident.paging_provider,
    external_provider=provider or incident.external_provider,
    external_reference=external_reference,
    provider_workflow_reference=workflow_reference,
    external_last_synced_at=synced_at,
    provider_workflow_state=pull_sync.workflow_state or incident.provider_workflow_state,
    provider_workflow_action=provider_action,
    provider_workflow_last_attempted_at=synced_at,
  )
  incident_market_context = app._extract_operator_alert_market_context_from_workflow_payload(
    payload=payload,
    existing_symbol=updated_incident.symbol,
    existing_symbols=updated_incident.symbols,
    existing_timeframe=updated_incident.timeframe,
    existing_primary_focus=updated_incident.primary_focus,
  )
  updated_incident = replace(
    updated_incident,
    symbol=incident_market_context["symbol"],
    symbols=incident_market_context["symbols"],
    timeframe=incident_market_context["timeframe"],
    primary_focus=incident_market_context["primary_focus"],
  )
  effective_delivery_history = delivery_history
  executed = False
  incident_changed = updated_incident != incident

  if event_kind == "triggered":
    updated_incident = replace(
      updated_incident,
      external_status="triggered",
      paging_status="triggered",
    )
    incident_changed = updated_incident != incident
  elif event_kind == "acknowledged":
    updated_incident = replace(
      updated_incident,
      acknowledgment_state="acknowledged",
      acknowledged_at=synced_at,
      acknowledged_by=f"{provider}:pull_sync",
      acknowledgment_reason=detail_copy,
      next_escalation_at=None,
      external_status="acknowledged",
      paging_status="acknowledged",
    )
    effective_delivery_history = app._suppress_pending_incident_retries(
      delivery_history=effective_delivery_history,
      incident_event_id=incident.event_id,
      reason=f"provider_pull_synced:{provider}:{event_kind}",
    )
    incident_changed = updated_incident != incident or effective_delivery_history != delivery_history
  elif event_kind == "escalated":
    updated_incident = replace(
      updated_incident,
      escalation_state="escalated",
      last_escalated_at=synced_at,
      last_escalated_by=f"{provider}:pull_sync",
      escalation_reason=detail_copy,
      external_status="escalated",
      paging_status="escalated",
    )
    incident_changed = updated_incident != incident
  elif event_kind == "resolved":
    updated_incident = replace(
      updated_incident,
      external_status="resolved",
      paging_status="resolved",
      next_escalation_at=None,
    )
    effective_delivery_history = app._suppress_pending_incident_retries(
      delivery_history=effective_delivery_history,
      incident_event_id=incident.event_id,
      reason=f"provider_pull_synced:{provider}:{event_kind}",
    )
    incident_changed = updated_incident != incident or effective_delivery_history != delivery_history
  elif event_kind in {
    "remediation_requested",
    "remediation_started",
    "remediation_completed",
    "remediation_failed",
  }:
    next_state = {
      "remediation_requested": "requested",
      "remediation_started": "provider_recovering",
      "remediation_completed": "provider_recovered",
      "remediation_failed": "failed",
    }[event_kind]
    status_machine_payload = app._extract_payload_mapping(payload.get("status_machine"))
    provider_payload = dict(payload)
    provider_payload["status_machine"] = {
      **status_machine_payload,
      "workflow_state": app._first_non_empty_string(
        status_machine_payload.get("workflow_state"),
        pull_sync.workflow_state,
      ),
      "workflow_action": app._first_non_empty_string(
        status_machine_payload.get("workflow_action"),
        "remediate",
      ),
      "sync_state": app._first_non_empty_string(
        status_machine_payload.get("sync_state"),
        "provider_authoritative",
      ),
    }
    updated_incident = app._apply_external_remediation_sync(
      incident=updated_incident,
      next_state=next_state,
      event_kind=event_kind,
      provider=provider,
      actor="pull_sync",
      detail=detail_copy,
      synced_at=synced_at,
      workflow_reference=workflow_reference,
      payload=provider_payload,
    )
    effective_delivery_history = app._suppress_pending_incident_retries(
      delivery_history=effective_delivery_history,
      incident_event_id=incident.event_id,
      reason=f"provider_pull_synced:{provider}:{event_kind}",
      phase="provider_remediate",
    )
    if (
      event_kind == "remediation_completed"
      and incident.remediation.state not in {"executed", "completed", "partial", "failed"}
    ):
      updated_incident, local_results = app._execute_local_incident_remediation(
        incident=updated_incident,
        actor=f"{provider}:pull_sync",
        current_time=synced_at,
      )
      executed = bool(local_results)
    incident_changed = (
      updated_incident != incident
      or effective_delivery_history != delivery_history
      or executed
    )

  if incident_changed and event_kind is not None:
    effective_delivery_history = app._confirm_external_provider_workflow(
      delivery_history=effective_delivery_history,
      incident=incident,
      provider=provider,
      event_kind=event_kind,
      detail=detail_copy,
      occurred_at=synced_at,
      external_reference=workflow_reference or external_reference,
    )

  return updated_incident, effective_delivery_history, executed
