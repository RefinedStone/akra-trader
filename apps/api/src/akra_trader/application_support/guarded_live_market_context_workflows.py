from __future__ import annotations

from dataclasses import asdict
from dataclasses import replace
from datetime import datetime
from typing import Any

from akra_trader.domain.models import OperatorIncidentEvent


def _apply_external_remediation_sync(
  app: Any,
  *,
  incident: OperatorIncidentEvent,
  next_state: str,
  event_kind: str,
  provider: str,
  actor: str,
  detail: str,
  synced_at: datetime,
  workflow_reference: str | None,
  payload: dict[str, Any],
) -> OperatorIncidentEvent:
  remediation = incident.remediation
  merged_payload = app._merge_incident_workflow_payload(
    existing=remediation.provider_payload,
    incoming=payload,
  )
  payload_reference = app._extract_incident_payload_reference(payload)
  provider_recovery = app._build_provider_recovery_state(
    remediation=remediation,
    next_state=next_state,
    provider=provider,
    detail=detail,
    synced_at=synced_at,
    workflow_reference=workflow_reference,
    payload=merged_payload,
    event_kind=event_kind,
  )
  next_remediation = replace(
    remediation,
    state=next_state,
    kind=app._first_non_empty_string(
      payload.get("remediation_kind"),
      payload.get("kind"),
    ) or remediation.kind,
    owner=app._first_non_empty_string(
      payload.get("remediation_owner"),
      payload.get("owner"),
    ) or remediation.owner,
    summary=app._first_non_empty_string(
      payload.get("remediation_summary"),
      payload.get("summary"),
      payload.get("message"),
    ) or remediation.summary,
    detail=app._first_non_empty_string(
      payload.get("remediation_detail"),
      payload.get("detail"),
      payload.get("status_detail"),
      payload.get("result_detail"),
      payload.get("message"),
    ) or detail,
    runbook=app._first_non_empty_string(
      payload.get("remediation_runbook"),
      payload.get("runbook"),
    ) or remediation.runbook,
    requested_at=remediation.requested_at or synced_at,
    requested_by=f"{provider}:{actor}",
    last_attempted_at=synced_at,
    provider=provider or remediation.provider,
    reference=workflow_reference or payload_reference or remediation.reference,
    provider_payload=merged_payload,
    provider_payload_updated_at=(
      synced_at if merged_payload != remediation.provider_payload else remediation.provider_payload_updated_at
    ),
    provider_recovery=provider_recovery,
  )
  incident_market_context = app._extract_operator_alert_market_context_from_workflow_payload(
    payload=merged_payload,
    existing_symbol=incident.symbol,
    existing_symbols=incident.symbols,
    existing_timeframe=incident.timeframe,
    existing_primary_focus=incident.primary_focus,
  )
  return replace(
    incident,
    symbol=incident_market_context["symbol"],
    symbols=incident_market_context["symbols"],
    timeframe=incident_market_context["timeframe"],
    primary_focus=incident_market_context["primary_focus"],
    remediation=next_remediation,
  )


def _build_incident_provider_workflow_payload(
  app: Any,
  *,
  incident: OperatorIncidentEvent,
  action: str,
  actor: str,
  detail: str,
  payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
  remediation = incident.remediation
  payload_context = app._normalize_incident_workflow_payload(payload)
  payload_market_context = app._extract_operator_alert_market_context_from_workflow_payload(
    payload=payload_context,
    existing_symbol=(
      incident.symbol
      or (
        remediation.provider_recovery.primary_focus.symbol
        if remediation.provider_recovery.primary_focus is not None
        else None
      )
    ),
    existing_symbols=incident.symbols or remediation.provider_recovery.symbols,
    existing_timeframe=(
      incident.timeframe
      or (
        remediation.provider_recovery.primary_focus.timeframe
        if remediation.provider_recovery.primary_focus is not None
        else remediation.provider_recovery.timeframe
      )
    ),
    existing_primary_focus=incident.primary_focus or remediation.provider_recovery.primary_focus,
  )
  workflow_payload: dict[str, Any] = {
    "action": action,
    "actor": actor,
    "detail": detail,
    "alert": {
      "alert_id": incident.alert_id,
      "event_id": incident.event_id,
      "kind": incident.kind,
      "severity": incident.severity,
      "source": incident.source,
      "summary": incident.summary,
      "run_id": incident.run_id,
      "session_id": incident.session_id,
    },
    "market_context": app._serialize_operator_alert_market_context_payload(
      symbol=payload_market_context["symbol"],
      symbols=payload_market_context["symbols"],
      timeframe=payload_market_context["timeframe"],
      primary_focus=payload_market_context["primary_focus"],
    ),
  }
  if remediation.state != "not_applicable":
    workflow_payload["remediation"] = {
      "state": remediation.state,
      "kind": remediation.kind,
      "owner": remediation.owner,
      "summary": remediation.summary,
      "detail": remediation.detail,
      "runbook": remediation.runbook,
      "requested_at": remediation.requested_at.isoformat() if remediation.requested_at is not None else None,
      "requested_by": remediation.requested_by,
      "last_attempted_at": (
        remediation.last_attempted_at.isoformat()
        if remediation.last_attempted_at is not None
        else None
      ),
      "provider": remediation.provider,
      "reference": remediation.reference,
      "provider_payload": remediation.provider_payload,
      "provider_payload_updated_at": (
        remediation.provider_payload_updated_at.isoformat()
        if remediation.provider_payload_updated_at is not None
        else None
      ),
      "provider_recovery": asdict(remediation.provider_recovery),
    }
  if payload_context:
    workflow_payload["provider_context"] = payload_context
  return workflow_payload
