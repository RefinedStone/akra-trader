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


class OperatorDeliveryWorkflowRunGroupOneMixin:
  def _build_incidenthub_workflow_request(
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
      "Authorization": f"Bearer {self._incidenthub_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._incidenthub_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._incidenthub_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._incidenthub_api_url}/alerts/{encoded_reference}/escalate{suffix}",
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
        f"{self._incidenthub_api_url}/alerts/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported incidenthub workflow action: {action}")
  def _build_resolver_workflow_request(
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
      "Authorization": f"Bearer {self._resolver_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._resolver_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._resolver_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._resolver_api_url}/alerts/{encoded_reference}/escalate{suffix}",
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
        f"{self._resolver_api_url}/alerts/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported resolver workflow action: {action}")
  def _build_openduty_workflow_request(
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
      "Authorization": f"Bearer {self._openduty_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._openduty_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._openduty_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._openduty_api_url}/alerts/{encoded_reference}/escalate{suffix}",
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
        f"{self._openduty_api_url}/alerts/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported openduty workflow action: {action}")
  def _build_cabot_workflow_request(
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
      "Authorization": f"Bearer {self._cabot_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._cabot_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._cabot_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._cabot_api_url}/alerts/{encoded_reference}/escalate{suffix}",
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
        f"{self._cabot_api_url}/alerts/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported cabot workflow action: {action}")
  def _build_haloitsm_workflow_request(
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
      "Authorization": f"Bearer {self._haloitsm_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._haloitsm_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._haloitsm_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._haloitsm_api_url}/alerts/{encoded_reference}/escalate{suffix}",
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
        f"{self._haloitsm_api_url}/alerts/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported haloitsm workflow action: {action}")
  def _build_incidentmanagerio_workflow_request(
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
      "Authorization": f"Bearer {self._incidentmanagerio_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._incidentmanagerio_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._incidentmanagerio_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._incidentmanagerio_api_url}/alerts/{encoded_reference}/escalate{suffix}",
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
        f"{self._incidentmanagerio_api_url}/alerts/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported incidentmanagerio workflow action: {action}")
  def _build_oneuptime_workflow_request(
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
      "Authorization": f"Bearer {self._oneuptime_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._oneuptime_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._oneuptime_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._oneuptime_api_url}/alerts/{encoded_reference}/escalate{suffix}",
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
        f"{self._oneuptime_api_url}/alerts/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported oneuptime workflow action: {action}")
  def _build_squzy_workflow_request(
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
      "Authorization": f"Bearer {self._squzy_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._squzy_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._squzy_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._squzy_api_url}/alerts/{encoded_reference}/escalate{suffix}",
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
        f"{self._squzy_api_url}/alerts/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported squzy workflow action: {action}")
  def _build_crisescontrol_workflow_request(
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
      "Authorization": f"Bearer {self._crisescontrol_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._crisescontrol_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._crisescontrol_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._crisescontrol_api_url}/alerts/{encoded_reference}/escalate{suffix}",
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
        f"{self._crisescontrol_api_url}/alerts/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported crisescontrol workflow action: {action}")
  def _build_freshservice_workflow_request(
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
      "Authorization": f"Bearer {self._freshservice_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._freshservice_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._freshservice_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._freshservice_api_url}/alerts/{encoded_reference}/escalate{suffix}",
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
        f"{self._freshservice_api_url}/alerts/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported freshservice workflow action: {action}")
  def _build_freshdesk_workflow_request(
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
      "Authorization": f"Bearer {self._freshdesk_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._freshdesk_api_url}/tickets/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._freshdesk_api_url}/tickets/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._freshdesk_api_url}/tickets/{encoded_reference}/escalate{suffix}",
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
        f"{self._freshdesk_api_url}/tickets/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported freshdesk workflow action: {action}")
  def _build_happyfox_workflow_request(
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
      "Authorization": f"Bearer {self._happyfox_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._happyfox_api_url}/tickets/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._happyfox_api_url}/tickets/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._happyfox_api_url}/tickets/{encoded_reference}/escalate{suffix}",
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
        f"{self._happyfox_api_url}/tickets/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported happyfox workflow action: {action}")
  def _build_zendesk_workflow_request(
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
      "Authorization": f"Bearer {self._zendesk_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._zendesk_api_url}/tickets/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._zendesk_api_url}/tickets/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._zendesk_api_url}/tickets/{encoded_reference}/escalate{suffix}",
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
        f"{self._zendesk_api_url}/tickets/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported zendesk workflow action: {action}")
