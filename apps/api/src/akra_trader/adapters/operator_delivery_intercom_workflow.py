from __future__ import annotations

import json
from typing import Any
from urllib import error as urllib_error

from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync


class OperatorDeliveryIntercomWorkflowMixin:
  def _deliver_intercom(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._intercom_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:intercom_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="intercom_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="intercom_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="intercom",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_intercom_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:intercom_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="intercom_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"intercom_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="intercom",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:intercom_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="intercom_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"intercom_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="intercom",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_intercom_workflow(
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
    target = "intercom_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._intercom_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="intercom_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="intercom",
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
        detail="intercom_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="intercom",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_intercom_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="intercom",
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
        detail=f"intercom_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="intercom",
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
        detail=f"intercom_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="intercom",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_intercom_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._intercom_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_intercom_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(
      payload.get("result"),
      payload.get("data"),
      payload.get("conversation"),
      payload.get("alert"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("conversation"),
      alert_payload.get("alert"),
      alert_payload.get("incident"),
      alert_payload,
    )
    metadata_payload = self._extract_mapping(
      alert_payload.get("metadata"),
      attributes.get("metadata"),
      attributes.get("details"),
      alert_payload.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "priority": self._first_non_empty_string(
        alert_payload.get("priority"),
        alert_payload.get("severity"),
        attributes.get("priority"),
      ),
      "escalation_policy": self._first_non_empty_string(
        alert_payload.get("escalation_policy"),
        alert_payload.get("escalationPolicy"),
        alert_payload.get("policy"),
        alert_payload.get("source"),
        attributes.get("source"),
      ),
      "assignee": self._first_non_empty_string(
        alert_payload.get("assignee"),
        alert_payload.get("owner"),
        attributes.get("assignee"),
        self._extract_mapping(alert_payload.get("owner")).get("display_name"),
        self._extract_mapping(alert_payload.get("owner")).get("name"),
      ),
      "url": self._first_non_empty_string(
        alert_payload.get("url"),
        attributes.get("url"),
        alert_payload.get("html_url"),
      ),
      "updated_at": self._first_non_empty_string(
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
      "external_reference": self._first_non_empty_string(
        alert_payload.get("external_reference"),
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="intercom",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("alert_id"),
        alert_payload.get("id"),
        alert_payload.get("alertId"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        provider_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        alert_payload.get("alert_status"),
        alert_payload.get("status"),
        alert_payload.get("state"),
        attributes.get("alert_status"),
        attributes.get("status"),
        attributes.get("state"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("summary"),
        alert_payload.get("subject"),
        attributes.get("summary"),
        alert_payload.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )
