from __future__ import annotations

import json
import logging
from datetime import UTC
from datetime import datetime
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from akra_trader.domain.models import OperatorAlertPrimaryFocus
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync


LOGGER = logging.getLogger("akra_trader.operator_delivery")


class OperatorDeliveryWorkflowRequestGroupThreeMixin:
  def _build_ilert_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._ilert_api_url}/api/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._ilert_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_ilert_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._ilert_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._ilert_api_url}/api/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._ilert_api_url}/api/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_ilert_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
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
  def _build_ilert_workflow_request(
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
      "Authorization": f"Bearer {self._ilert_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._ilert_api_url}/api/alerts/{encoded_reference}/accept{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._ilert_api_url}/api/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._ilert_api_url}/api/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._ilert_api_url}/api/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
      method="PUT",
      )
    raise ValueError(f"unsupported ilert workflow action: {action}")
  def _build_betterstack_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._betterstack_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._betterstack_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_betterstack_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._betterstack_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._betterstack_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._betterstack_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_betterstack_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
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
  def _build_betterstack_workflow_request(
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
      "Authorization": f"Bearer {self._betterstack_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._betterstack_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._betterstack_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._betterstack_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._betterstack_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    raise ValueError(f"unsupported betterstack workflow action: {action}")
  def _build_onpage_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._onpage_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._onpage_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_onpage_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._onpage_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._onpage_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._onpage_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_onpage_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
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
  def _build_onpage_workflow_request(
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
      "Authorization": f"Bearer {self._onpage_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._onpage_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._onpage_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._onpage_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._onpage_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
      method="PUT",
      )
    raise ValueError(f"unsupported onpage workflow action: {action}")
  def _build_allquiet_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._allquiet_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._allquiet_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_allquiet_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._allquiet_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._allquiet_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._allquiet_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_allquiet_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
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
  def _build_allquiet_workflow_request(
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
      "Authorization": f"Bearer {self._allquiet_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._allquiet_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._allquiet_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._allquiet_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._allquiet_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    raise ValueError(f"unsupported allquiet workflow action: {action}")
  def _build_moogsoft_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._moogsoft_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._moogsoft_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_moogsoft_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._moogsoft_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._moogsoft_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._moogsoft_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_moogsoft_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
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
  def _build_moogsoft_workflow_request(
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
      "Authorization": f"Bearer {self._moogsoft_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._moogsoft_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._moogsoft_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._moogsoft_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._moogsoft_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    raise ValueError(f"unsupported moogsoft workflow action: {action}")
  def _build_spikesh_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._spikesh_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._spikesh_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_spikesh_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._spikesh_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._spikesh_api_url}/alerts/{encoded_reference}/resolve"
          "?identifier_type=external_reference"
        ),
        data=json.dumps(
          {
            "actor": "Akra Trader",
            "note": incident.detail,
            "source": incident.source,
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    return urllib_request.Request(
      f"{self._spikesh_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_spikesh_priority(incident.severity),
            "external_reference": reference,
            "source": "akra_trader",
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
  def _build_spikesh_workflow_request(
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
      "Authorization": f"Bearer {self._spikesh_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._spikesh_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._spikesh_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._spikesh_api_url}/alerts/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra escalated alert to level {incident.escalation_level}. "
              f"Actor: {actor}. Detail: {detail}."
            ),
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._spikesh_api_url}/alerts/{encoded_reference}/remediate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": (
              f"Akra requested remediation. Summary: {incident.remediation.summary or incident.summary}. "
              f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
              f"{self._format_workflow_payload_context(payload)}"
            ),
          }
        ).encode("utf-8"),
      headers=headers,
      method="PUT",
    )
    raise ValueError(f"unsupported spikesh workflow action: {action}")
