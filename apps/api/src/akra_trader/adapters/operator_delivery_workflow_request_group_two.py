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


class OperatorDeliveryWorkflowRequestGroupTwoMixin:
  def _build_zenduty_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._zenduty_api_url}/api/v1/incidents/{encoded_reference}?identifier_type={reference_type}",
      headers={
        "Authorization": f"Bearer {self._zenduty_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_zenduty_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._zenduty_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._zenduty_api_url}/api/v1/incidents/{encoded_reference}/resolve"
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
        method="POST",
      )
    return urllib_request.Request(
      f"{self._zenduty_api_url}/api/v1/incidents",
      data=json.dumps(
        {
          "incident": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "triggered",
            "severity": self._map_zenduty_severity(incident.severity),
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
  def _build_zenduty_workflow_request(
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
      "Authorization": f"Bearer {self._zenduty_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._zenduty_api_url}/api/v1/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._zenduty_api_url}/api/v1/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._zenduty_api_url}/api/v1/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
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
        f"{self._zenduty_api_url}/api/v1/incidents/{encoded_reference}/remediate{suffix}",
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
        method="POST",
      )
    raise ValueError(f"unsupported zenduty workflow action: {action}")
  def _build_splunk_oncall_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._splunk_oncall_api_url}/api/v3/incidents/{encoded_reference}?identifier_type={reference_type}",
      headers={
        "Authorization": f"Bearer {self._splunk_oncall_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_splunk_oncall_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._splunk_oncall_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._splunk_oncall_api_url}/api/v3/incidents/{encoded_reference}/resolve"
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
        method="POST",
      )
    return urllib_request.Request(
      f"{self._splunk_oncall_api_url}/api/v3/incidents",
      data=json.dumps(
        {
          "incident": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "triggered",
            "severity": self._map_splunk_oncall_severity(incident.severity),
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
  def _build_splunk_oncall_workflow_request(
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
      "Authorization": f"Bearer {self._splunk_oncall_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._splunk_oncall_api_url}/api/v3/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._splunk_oncall_api_url}/api/v3/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._splunk_oncall_api_url}/api/v3/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
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
        f"{self._splunk_oncall_api_url}/api/v3/incidents/{encoded_reference}/remediate{suffix}",
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
        method="POST",
      )
    raise ValueError(f"unsupported splunk_oncall workflow action: {action}")
  def _build_jira_service_management_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._jira_service_management_api_url}/v1/incidents/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._jira_service_management_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_jira_service_management_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._jira_service_management_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._jira_service_management_api_url}/v1/incidents/{encoded_reference}/resolve"
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
        method="POST",
      )
    return urllib_request.Request(
      f"{self._jira_service_management_api_url}/v1/incidents",
      data=json.dumps(
        {
          "incident": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "triggered",
            "priority": self._map_jira_service_management_priority(incident.severity),
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
  def _build_jira_service_management_workflow_request(
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
      "Authorization": f"Bearer {self._jira_service_management_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._jira_service_management_api_url}/v1/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._jira_service_management_api_url}/v1/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._jira_service_management_api_url}/v1/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
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
        f"{self._jira_service_management_api_url}/v1/incidents/{encoded_reference}/remediate{suffix}",
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
        method="POST",
      )
    raise ValueError(f"unsupported jira_service_management workflow action: {action}")
  def _build_pagertree_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._pagertree_api_url}/api/v1/incidents/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._pagertree_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_pagertree_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._pagertree_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._pagertree_api_url}/api/v1/incidents/{encoded_reference}/resolve"
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
        method="POST",
      )
    return urllib_request.Request(
      f"{self._pagertree_api_url}/api/v1/incidents",
      data=json.dumps(
        {
          "incident": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "triggered",
            "urgency": self._map_pagertree_urgency(incident.severity),
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
  def _build_pagertree_workflow_request(
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
      "Authorization": f"Bearer {self._pagertree_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._pagertree_api_url}/api/v1/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._pagertree_api_url}/api/v1/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._pagertree_api_url}/api/v1/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
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
        f"{self._pagertree_api_url}/api/v1/incidents/{encoded_reference}/remediate{suffix}",
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
        method="POST",
      )
    raise ValueError(f"unsupported pagertree workflow action: {action}")
  def _build_alertops_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._alertops_api_url}/api/v2/incidents/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._alertops_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_alertops_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._alertops_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._alertops_api_url}/api/v2/incidents/{encoded_reference}/resolve"
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
        method="POST",
      )
    return urllib_request.Request(
      f"{self._alertops_api_url}/api/v2/incidents",
      data=json.dumps(
        {
          "incident": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "triggered",
            "priority": self._map_alertops_priority(incident.severity),
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
  def _build_alertops_workflow_request(
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
      "Authorization": f"Bearer {self._alertops_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._alertops_api_url}/api/v2/incidents/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._alertops_api_url}/api/v2/incidents/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._alertops_api_url}/api/v2/incidents/{encoded_reference}/escalate{suffix}",
        data=json.dumps(
          {
            "actor": actor,
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
        f"{self._alertops_api_url}/api/v2/incidents/{encoded_reference}/remediate{suffix}",
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
        method="POST",
      )
    raise ValueError(f"unsupported alertops workflow action: {action}")
  def _build_signl4_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      (
        f"{self._signl4_api_url}/api/v1/alerts/{encoded_reference}"
        f"?identifier_type={reference_type}"
      ),
      headers={
        "Authorization": f"Bearer {self._signl4_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )
  def _build_signl4_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._signl4_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._signl4_api_url}/api/v1/alerts/{encoded_reference}/resolve"
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
        method="POST",
      )
    return urllib_request.Request(
      f"{self._signl4_api_url}/api/v1/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "triggered",
            "priority": self._map_signl4_priority(incident.severity),
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
  def _build_signl4_workflow_request(
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
      "Authorization": f"Bearer {self._signl4_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._signl4_api_url}/api/v1/alerts/{encoded_reference}/acknowledge{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": detail,
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"{self._signl4_api_url}/api/v1/alerts/{encoded_reference}/resolve{suffix}",
        data=json.dumps(
          {
            "actor": actor,
            "note": f"{detail}{self._format_workflow_payload_context(payload)}",
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"{self._signl4_api_url}/api/v1/alerts/{encoded_reference}/escalate{suffix}",
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
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"{self._signl4_api_url}/api/v1/alerts/{encoded_reference}/remediate{suffix}",
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
        method="POST",
      )
    raise ValueError(f"unsupported signl4 workflow action: {action}")
