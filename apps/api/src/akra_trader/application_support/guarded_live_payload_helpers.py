from __future__ import annotations

from datetime import datetime
from numbers import Number
from typing import Any

from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync

def _normalize_external_incident_event_kind(event_kind: str) -> str:
  normalized = event_kind.strip().lower().replace("-", "_")
  mapping = {
    "recovery_requested": "remediation_requested",
    "recovery_started": "remediation_started",
    "recovered": "remediation_completed",
    "recovery_completed": "remediation_completed",
    "recovery_failed": "remediation_failed",
  }
  return mapping.get(normalized, normalized)

def _first_non_empty_string(*values: Any) -> str | None:
  for value in values:
    if not isinstance(value, str):
      continue
    stripped = value.strip()
    if stripped:
      return stripped
  return None

def _extract_payload_mapping(value: Any) -> dict[str, Any]:
  if isinstance(value, dict):
    return value
  return {}

def _merge_payload_mappings(app: Any, *values: Any) -> dict[str, Any]:
  merged: dict[str, Any] = {}
  for value in values:
    if isinstance(value, dict):
      merged.update(app._extract_payload_mapping(value))
  return merged

def _extract_string_tuple(app: Any, *values: Any) -> tuple[str, ...]:
  items: list[str] = []
  for value in values:
    if isinstance(value, str):
      stripped = value.strip()
      if stripped and stripped not in items:
        items.append(stripped)
      continue
    if isinstance(value, (list, tuple, set)):
      for item in value:
        if not isinstance(item, str):
          continue
        stripped = item.strip()
        if stripped and stripped not in items:
          items.append(stripped)
  return tuple(items)

def _parse_payload_datetime(app: Any, value: Any) -> datetime | None:
  if isinstance(value, datetime):
    return value
  if not isinstance(value, str):
    return None
  candidate = value.strip()
  if not candidate:
    return None
  if candidate.endswith("Z"):
    candidate = f"{candidate[:-1]}+00:00"
  try:
    return datetime.fromisoformat(candidate)
  except ValueError:
    return None

def _parse_payload_int(*values: Any) -> int | None:
  for value in values:
    if isinstance(value, bool):
      continue
    if isinstance(value, int):
      return value
    if isinstance(value, float) and value.is_integer():
      return int(value)
    if not isinstance(value, str):
      continue
    candidate = value.strip()
    if not candidate:
      continue
    try:
      return int(candidate)
    except ValueError:
      continue
  return None

def _normalize_incident_workflow_payload_value(app: Any, value: Any) -> Any:
  if value is None or isinstance(value, (str, bool)):
    return value
  if isinstance(value, datetime):
    return value.isoformat()
  if isinstance(value, int):
    return value
  if isinstance(value, float):
    return value
  if isinstance(value, Number):
    return float(value)
  if isinstance(value, dict):
    normalized: dict[str, Any] = {}
    for key, nested_value in value.items():
      key_copy = str(key).strip()
      if not key_copy:
        continue
      normalized[key_copy] = app._normalize_incident_workflow_payload_value(nested_value)
    return normalized
  if isinstance(value, (list, tuple, set)):
    return [app._normalize_incident_workflow_payload_value(item) for item in value]
  return str(value)

def _normalize_incident_workflow_payload(
  app: Any,
  payload: dict[str, Any] | None,
) -> dict[str, Any]:
  if not payload:
    return {}
  return {
    key_copy: app._normalize_incident_workflow_payload_value(value)
    for key, value in payload.items()
    if (key_copy := str(key).strip())
  }

def _merge_incident_workflow_payload(
  *,
  existing: dict[str, Any],
  incoming: dict[str, Any],
) -> dict[str, Any]:
  if not existing:
    return dict(incoming)
  if not incoming:
    return dict(existing)
  merged = dict(existing)
  merged.update(incoming)
  return merged

def _extract_incident_payload_reference(app: Any, payload: dict[str, Any]) -> str | None:
  return app._first_non_empty_string(
    payload.get("workflow_reference"),
    payload.get("provider_workflow_reference"),
    payload.get("reference"),
    payload.get("job_reference"),
    payload.get("job_id"),
    payload.get("execution_id"),
    payload.get("recovery_id"),
  )

def _resolve_provider_pull_sync_event_kind(
  app: Any,
  *,
  incident: OperatorIncidentEvent,
  pull_sync: OperatorIncidentProviderPullSync,
  payload: dict[str, Any],
) -> str | None:
  explicit_event = app._first_non_empty_string(
    payload.get("event_kind"),
    payload.get("recovery_event_kind"),
    payload.get("last_event_kind"),
    app._extract_payload_mapping(payload.get("status_machine")).get("last_event_kind"),
  )
  if explicit_event is not None:
    return app._normalize_external_incident_event_kind(explicit_event)

  remediation_state = app._first_non_empty_string(
    pull_sync.remediation_state,
    payload.get("recovery_state"),
    payload.get("status"),
  )
  if remediation_state is not None:
    normalized_state = remediation_state.strip().lower().replace("-", "_")
    remediation_mapping = {
      "requested": "remediation_requested",
      "provider_requested": "remediation_requested",
      "recovering": "remediation_started",
      "running": "remediation_started",
      "in_progress": "remediation_started",
      "provider_recovering": "remediation_started",
      "recovered": "remediation_completed",
      "provider_recovered": "remediation_completed",
      "completed": "remediation_completed",
      "verified": "remediation_completed",
      "resolved": "resolved",
      "failed": "remediation_failed",
      "provider_failed": "remediation_failed",
    }
    if normalized_state in remediation_mapping:
      return remediation_mapping[normalized_state]

  workflow_state = app._first_non_empty_string(
    pull_sync.workflow_state,
    payload.get("workflow_state"),
  )
  if workflow_state is None:
    return None
  normalized_workflow_state = workflow_state.strip().lower().replace("-", "_")
  workflow_mapping = {
    "triggered": "triggered",
    "open": "triggered",
    "active": "triggered",
    "acknowledged": "acknowledged",
    "escalated": "escalated",
    "resolved": "resolved",
    "closed": "resolved",
  }
  resolved = workflow_mapping.get(normalized_workflow_state)
  if resolved == "resolved" and incident.kind == "incident_opened" and incident.remediation.state != "not_applicable":
    return None
  return resolved
