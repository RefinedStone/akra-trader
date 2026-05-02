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


class OperatorDeliveryWorkflowRequestGroupFourMixin:
  def _build_dutycalls_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._dutycalls_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._dutycalls_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_dutycalls_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._dutycalls_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._dutycalls_api_url}/alerts/{encoded_reference}/resolve"
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
      f"{self._dutycalls_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_dutycalls_priority(incident.severity),
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
  def _build_dutycalls_workflow_request(
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
      "Authorization": f"Bearer {self._dutycalls_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._dutycalls_api_url}/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps({"actor": actor, "note": detail}).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._dutycalls_api_url}/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {"actor": actor, "note": f"{detail}{self._format_workflow_payload_context(payload)}"}
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._dutycalls_api_url}/alerts/{encoded_reference}/escalate{suffix}",
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
        f"{self._dutycalls_api_url}/alerts/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported dutycalls workflow action: {action}")
  def _build_incidenthub_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._incidenthub_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._incidenthub_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_opsramp_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._opsramp_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._opsramp_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_resolver_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._resolver_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._resolver_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_openduty_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._openduty_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._openduty_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_cabot_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._cabot_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._cabot_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_haloitsm_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._haloitsm_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._haloitsm_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_incidentmanagerio_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._incidentmanagerio_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._incidentmanagerio_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_oneuptime_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._oneuptime_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._oneuptime_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_squzy_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._squzy_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._squzy_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_crisescontrol_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._crisescontrol_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._crisescontrol_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_freshservice_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._freshservice_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._freshservice_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_freshdesk_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._freshdesk_api_url}/tickets/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._freshdesk_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_happyfox_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._happyfox_api_url}/tickets/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._happyfox_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_zendesk_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._zendesk_api_url}/tickets/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._zendesk_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_zohodesk_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._zohodesk_api_url}/tickets/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._zohodesk_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_helpscout_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._helpscout_api_url}/conversations/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._helpscout_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_kayako_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._kayako_api_url}/cases/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._kayako_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_intercom_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._intercom_api_url}/conversations/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._intercom_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_front_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._front_api_url}/conversations/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._front_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_servicedeskplus_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._servicedeskplus_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._servicedeskplus_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_sysaid_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._sysaid_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._sysaid_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_bmchelix_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._bmchelix_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._bmchelix_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_solarwindsservicedesk_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._solarwindsservicedesk_api_url}/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._solarwindsservicedesk_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_topdesk_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._topdesk_api_url}/incidents/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._topdesk_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_invgateservicedesk_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._invgateservicedesk_api_url}/incidents/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._invgateservicedesk_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
