from __future__ import annotations

import json
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync


class CoreIncidentioWorkflowProviderMixin:
  def _build_incidentio_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    token = self._incidentio_recovery_engine_token or self._incidentio_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _deliver_incidentio(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._incidentio_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidentio_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidentio_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="incidentio_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidentio",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_incidentio_delivery_request(incident=incident, reference=reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidentio_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidentio_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"incidentio_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidentio",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidentio_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidentio_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"incidentio_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidentio",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_incidentio_workflow(
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
    target = "incidentio_workflow"
    if not self._incidentio_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="incidentio_workflow_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidentio",
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
        detail="incidentio_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidentio",
        external_reference=None,
        source=incident.source,
      )
    request = self._build_incidentio_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="incidentio",
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
        detail=f"incidentio_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidentio",
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
        detail=f"incidentio_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidentio",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_incidentio_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._incidentio_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_incidentio_pull_request(reference=reference, reference_type=reference_type)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(payload.get("incident"), payload.get("data"), payload)
    metadata_payload = self._extract_mapping(
      incident_payload.get("metadata"),
      incident_payload.get("custom_fields"),
      incident_payload.get("details"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "severity": incident_payload.get("severity"),
      "mode": incident_payload.get("mode"),
      "visibility": incident_payload.get("visibility"),
      "url": incident_payload.get("url"),
      "updated_at": incident_payload.get("updated_at"),
      "assignee": self._first_non_empty_string(
        self._extract_mapping(incident_payload.get("assignee")).get("name"),
        self._extract_mapping(incident_payload.get("assignee")).get("email"),
        incident_payload.get("assignee"),
      ),
    })
    return self._build_provider_pull_sync(
      provider="incidentio",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        incident_payload.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        incident_payload.get("status"),
        payload.get("status"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        incident_payload.get("name"),
        incident_payload.get("summary"),
        incident_payload.get("description"),
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        incident_payload.get("updated_at"),
        incident_payload.get("created_at"),
      ),
    )

  def _build_incidentio_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._incidentio_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._incidentio_api_url}/v2/incidents/{encoded_reference}/actions/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": {"type": "application", "name": "Akra Trader"},
            "message": incident.detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._incidentio_api_url}/v2/incidents",
      data=json.dumps(
        {
          "incident": {
            "name": incident.summary[:255],
            "summary": incident.detail,
            "status": "active",
            "severity": self._map_incidentio_severity(incident.severity),
            "visibility": "public",
            "external_reference": reference,
            "metadata": {
              "alert_id": incident.alert_id,
              "event_id": incident.event_id,
              "incident_kind": incident.kind,
              "run_id": incident.run_id,
              "session_id": incident.session_id,
              "remediation_state": incident.remediation.state,
              "remediation_kind": incident.remediation.kind,
              "remediation_runbook": incident.remediation.runbook,
              "remediation_summary": incident.remediation.summary,
              "remediation_provider_payload": incident.remediation.provider_payload,
              "remediation_provider_recovery": self._build_provider_recovery_payload(incident),
            },
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_incidentio_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._incidentio_api_url}/v2/incidents/{encoded_reference}?identifier_type={reference_type}",
      headers={
        "Authorization": f"Bearer {self._incidentio_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_incidentio_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    suffix = f"?identifier_type={reference_type}"
    headers = {
      "Authorization": f"Bearer {self._incidentio_api_token}",
      "Content-Type": "application/json",
    }
    base_payload = {
      "actor": {"type": "application", "name": actor},
      "message": detail,
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._incidentio_api_url}/v2/incidents/{encoded_reference}/actions/acknowledge{suffix}",
        data=json.dumps(base_payload).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._incidentio_api_url}/v2/incidents/{encoded_reference}/actions/resolve{suffix}",
        data=json.dumps(
          {
            **base_payload,
            "message": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._incidentio_api_url}/v2/incidents/{encoded_reference}/actions/escalate{suffix}",
        data=json.dumps(
          {
            **base_payload,
            "message": (
              f"Akra escalated incident to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._incidentio_api_url}/v2/incidents/{encoded_reference}/actions/remediate{suffix}",
        data=json.dumps(
          {
            **base_payload,
            "message": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported incidentio workflow action: {action}")

  @staticmethod
  def _map_incidentio_severity(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "critical"
    if normalized in {"warning", "warn"}:
      return "warning"
    return "info"
