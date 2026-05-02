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


class OperatorDeliveryWorkflowRunGroupTwoMixin:
  def _build_zohodesk_workflow_request(
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
      "Authorization": f"Bearer {self._zohodesk_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._zohodesk_api_url}/tickets/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._zohodesk_api_url}/tickets/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._zohodesk_api_url}/tickets/{encoded_reference}/escalate{suffix}",
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
        f"{self._zohodesk_api_url}/tickets/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported zohodesk workflow action: {action}")
  def _build_helpscout_workflow_request(
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
      "Authorization": f"Bearer {self._helpscout_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._helpscout_api_url}/conversations/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._helpscout_api_url}/conversations/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._helpscout_api_url}/conversations/{encoded_reference}/escalate{suffix}",
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
        f"{self._helpscout_api_url}/conversations/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported helpscout workflow action: {action}")
  def _build_kayako_workflow_request(
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
      "Authorization": f"Bearer {self._kayako_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._kayako_api_url}/cases/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._kayako_api_url}/cases/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._kayako_api_url}/cases/{encoded_reference}/escalate{suffix}",
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
        f"{self._kayako_api_url}/cases/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported kayako workflow action: {action}")
  def _build_intercom_workflow_request(
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
      "Authorization": f"Bearer {self._intercom_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._intercom_api_url}/conversations/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._intercom_api_url}/conversations/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._intercom_api_url}/conversations/{encoded_reference}/escalate{suffix}",
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
        f"{self._intercom_api_url}/conversations/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported intercom workflow action: {action}")
  def _build_front_workflow_request(
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
      "Authorization": f"Bearer {self._front_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._front_api_url}/conversations/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._front_api_url}/conversations/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._front_api_url}/conversations/{encoded_reference}/escalate{suffix}",
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
        f"{self._front_api_url}/conversations/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported front workflow action: {action}")
  def _build_servicedeskplus_workflow_request(
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
      "Authorization": f"Bearer {self._servicedeskplus_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._servicedeskplus_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._servicedeskplus_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._servicedeskplus_api_url}/alerts/{encoded_reference}/escalate{suffix}",
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
        f"{self._servicedeskplus_api_url}/alerts/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported servicedeskplus workflow action: {action}")
  def _build_sysaid_workflow_request(
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
      "Authorization": f"Bearer {self._sysaid_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._sysaid_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._sysaid_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._sysaid_api_url}/alerts/{encoded_reference}/escalate{suffix}",
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
        f"{self._sysaid_api_url}/alerts/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported sysaid workflow action: {action}")
  def _build_bmchelix_workflow_request(
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
      "Authorization": f"Bearer {self._bmchelix_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._bmchelix_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._bmchelix_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._bmchelix_api_url}/alerts/{encoded_reference}/escalate{suffix}",
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
        f"{self._bmchelix_api_url}/alerts/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported bmchelix workflow action: {action}")
  def _build_solarwindsservicedesk_workflow_request(
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
      "Authorization": f"Bearer {self._solarwindsservicedesk_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        (
          f"{self._solarwindsservicedesk_api_url}/alerts/"
          f"{encoded_reference}/acknowledge{suffix}"
        ),
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        (
          f"{self._solarwindsservicedesk_api_url}/alerts/"
          f"{encoded_reference}/resolve{suffix}"
        ),
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        (
          f"{self._solarwindsservicedesk_api_url}/alerts/"
          f"{encoded_reference}/escalate{suffix}"
        ),
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
        (
          f"{self._solarwindsservicedesk_api_url}/alerts/"
          f"{encoded_reference}/remediate{suffix}"
        ),
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
    raise ValueError(f"unsupported solarwindsservicedesk workflow action: {action}")
  def _build_topdesk_workflow_request(
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
      "Authorization": f"Bearer {self._topdesk_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._topdesk_api_url}/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._topdesk_api_url}/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._topdesk_api_url}/incidents/{encoded_reference}/escalate{suffix}",
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
        f"{self._topdesk_api_url}/incidents/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported topdesk workflow action: {action}")
  def _build_invgateservicedesk_workflow_request(
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
      "Authorization": f"Bearer {self._invgateservicedesk_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._invgateservicedesk_api_url}/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._invgateservicedesk_api_url}/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._invgateservicedesk_api_url}/incidents/{encoded_reference}/escalate{suffix}",
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
        f"{self._invgateservicedesk_api_url}/incidents/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported invgateservicedesk workflow action: {action}")
  def _build_opsramp_workflow_request(
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
      "Authorization": f"Bearer {self._opsramp_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._opsramp_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._opsramp_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._opsramp_api_url}/alerts/{encoded_reference}/escalate{suffix}",
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
        f"{self._opsramp_api_url}/alerts/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported opsramp workflow action: {action}")
