from __future__ import annotations

import json
from typing import Any
from urllib import error as urllib_error

from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync




class OperatorDeliverySquadcastWorkflowMixin:
  def _deliver_squadcast(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._squadcast_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:squadcast_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="squadcast_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="squadcast_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="squadcast",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_squadcast_delivery_request(incident=incident, reference=reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:squadcast_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="squadcast_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"squadcast_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="squadcast",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:squadcast_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="squadcast_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"squadcast_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="squadcast",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_squadcast_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    attempt_number: int,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    target = "squadcast_workflow"
    if not self._squadcast_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="squadcast_workflow_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="squadcast",
        external_reference=reference,
        source=incident.source,
      )
    if not reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="squadcast_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="squadcast",
        external_reference=None,
        source=incident.source,
      )
    request = self._build_squadcast_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="squadcast",
      request=request,
      payload=payload,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="delivered",
        attempted_at=attempted_at,
        detail=f"squadcast_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="squadcast",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail=f"squadcast_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="squadcast",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_squadcast_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._squadcast_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_squadcast_pull_request(reference=reference, reference_type=reference_type)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      incident_payload.get("attributes"),
      incident_payload.get("incident"),
      incident_payload,
    )
    metadata_payload = self._extract_mapping(
      incident_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      incident_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "severity": self._first_non_empty_string(
        incident_payload.get("severity"),
        incident_payload.get("priority"),
        attributes.get("severity"),
      ),
      "assignee": self._first_non_empty_string(
        incident_payload.get("assignee"),
        attributes.get("assignee"),
        self._extract_mapping(incident_payload.get("assignee")).get("name"),
      ),
      "escalation_policy": self._first_non_empty_string(
        incident_payload.get("escalation_policy"),
        incident_payload.get("escalation_policy_name"),
        attributes.get("escalation_policy"),
      ),
      "url": self._first_non_empty_string(
        incident_payload.get("url"),
        attributes.get("url"),
        incident_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        incident_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="squadcast",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("incident_id"),
        incident_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        incident_payload.get("incident_status"),
        incident_payload.get("status"),
        incident_payload.get("state"),
        attributes.get("incident_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        incident_payload.get("summary"),
        incident_payload.get("short_description"),
        attributes.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        incident_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )
