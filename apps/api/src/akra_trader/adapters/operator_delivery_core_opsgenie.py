from __future__ import annotations

import json
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync


class CoreOpsgenieWorkflowProviderMixin:
  def _build_opsgenie_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    api_key = self._opsgenie_recovery_engine_api_key or self._opsgenie_api_key
    headers = {
      "Accept": "application/json",
    }
    if api_key:
      headers["Authorization"] = f"GenieKey {api_key}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _deliver_opsgenie(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    alias = incident.external_reference or incident.alert_id
    if not self._opsgenie_api_key:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:opsgenie_alerts:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="opsgenie_alerts",
        status="failed",
        attempted_at=attempted_at,
        detail="opsgenie_api_key_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="opsgenie",
        external_reference=alias,
        source=incident.source,
      )
    request = self._build_opsgenie_delivery_request(incident=incident, alias=alias)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:opsgenie_alerts:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="opsgenie_alerts",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"opsgenie_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="opsgenie",
        external_reference=alias,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:opsgenie_alerts:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="opsgenie_alerts",
        status="failed",
        attempted_at=attempted_at,
        detail=f"opsgenie_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="opsgenie",
        external_reference=alias,
        source=incident.source,
      )

  def _sync_opsgenie_workflow(
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
    reference_type = "id" if incident.provider_workflow_reference else "alias"
    target = "opsgenie_workflow"
    if not self._opsgenie_api_key:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="opsgenie_workflow_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="opsgenie",
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
        detail="opsgenie_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="opsgenie",
        external_reference=None,
        source=incident.source,
      )
    request = self._build_opsgenie_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="opsgenie",
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
        detail=f"opsgenie_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="opsgenie",
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
        detail=f"opsgenie_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="opsgenie",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_opsgenie_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._opsgenie_api_key or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "alias"
    request = self._build_opsgenie_pull_request(
      reference=reference,
      reference_type=reference_type,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    alert_payload = self._extract_mapping(payload.get("data"), payload)
    details_payload = self._extract_mapping(
      alert_payload.get("details"),
      alert_payload.get("detail"),
    )
    provider_payload = dict(details_payload)
    provider_payload.update({
      "priority": alert_payload.get("priority"),
      "owner": self._extract_mapping(alert_payload.get("owner")),
      "acknowledged": alert_payload.get("acknowledged"),
      "seen": alert_payload.get("isSeen"),
      "tinyId": alert_payload.get("tinyId"),
      "teams": [
        team.get("name")
        for team in alert_payload.get("teams", [])
        if isinstance(team, dict) and isinstance(team.get("name"), str)
      ] if isinstance(alert_payload.get("teams"), list) else details_payload.get("teams"),
      "updatedAt": alert_payload.get("updatedAt"),
    })
    workflow_state = self._first_non_empty_string(alert_payload.get("status"))
    acknowledged = alert_payload.get("acknowledged")
    if workflow_state is None and isinstance(acknowledged, bool):
      workflow_state = "acknowledged" if acknowledged else "triggered"
    return self._build_provider_pull_sync(
      provider="opsgenie",
      workflow_reference=self._first_non_empty_string(
        alert_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        alert_payload.get("alias"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=workflow_state or "unknown",
      detail=self._first_non_empty_string(
        alert_payload.get("message"),
        alert_payload.get("description"),
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        alert_payload.get("updatedAt"),
        alert_payload.get("updated_at"),
        alert_payload.get("createdAt"),
      ),
    )

  def _build_opsgenie_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    alias: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"GenieKey {self._opsgenie_api_key}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_alias = urllib_parse.quote(alias, safe="")
      return urllib_request.Request(
        f"{self._opsgenie_api_url}/v2/alerts/{encoded_alias}/close?identifierType=alias",
        data=json.dumps(
          {
            "user": "Akra Trader",
            "source": incident.source,
            "note": incident.detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    return urllib_request.Request(
      f"{self._opsgenie_api_url}/v2/alerts",
      data=json.dumps(
        {
          "message": incident.summary[:130],
          "alias": alias,
          "description": incident.detail,
          "source": incident.source,
          "priority": self._map_opsgenie_priority(incident.severity),
          "details": {
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
          "tags": ["akra", incident.source, incident.severity.lower()],
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_opsgenie_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._opsgenie_api_url}/v2/alerts/{encoded_reference}?identifierType={reference_type}",
      headers={
        "Authorization": f"GenieKey {self._opsgenie_api_key}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_opsgenie_workflow_request(
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
    suffix = f"?identifierType={reference_type}"
    headers = {
      "Authorization": f"GenieKey {self._opsgenie_api_key}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._opsgenie_api_url}/v2/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "user": actor,
            "source": incident.source,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._opsgenie_api_url}/v2/alerts/{encoded_reference}/close{suffix}",
        data=json.dumps(
          {
            "user": actor,
            "source": incident.source,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._opsgenie_api_url}/v2/alerts/{encoded_reference}/notes{suffix}",
        data=json.dumps(
          {
            "user": actor,
            "source": incident.source,
            "note": (
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
        f"{self._opsgenie_api_url}/v2/alerts/{encoded_reference}/notes{suffix}",
        data=json.dumps(
          {
            "user": actor,
            "source": incident.source,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    raise ValueError(f"unsupported opsgenie workflow action: {action}")

  @staticmethod
  def _map_opsgenie_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "P1"
    if normalized in {"warning", "warn"}:
      return "P3"
    return "P5"
