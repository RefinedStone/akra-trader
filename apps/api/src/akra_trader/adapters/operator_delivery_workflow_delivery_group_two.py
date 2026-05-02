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


class OperatorDeliveryWorkflowDeliveryGroupTwoMixin:
  def _build_zohodesk_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._zohodesk_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._zohodesk_api_url}/tickets/{encoded_reference}/resolve"
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
      f"{self._zohodesk_api_url}/tickets",
      data=json.dumps(
        {
          "ticket": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_zohodesk_priority(incident.severity),
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
  def _build_helpscout_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._helpscout_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._helpscout_api_url}/conversations/{encoded_reference}/resolve"
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
      f"{self._helpscout_api_url}/conversations",
      data=json.dumps(
        {
          "conversation": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_helpscout_priority(incident.severity),
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
  def _build_kayako_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._kayako_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._kayako_api_url}/cases/{encoded_reference}/resolve"
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
      f"{self._kayako_api_url}/cases",
      data=json.dumps(
        {
          "case": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_kayako_priority(incident.severity),
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
  def _build_intercom_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._intercom_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._intercom_api_url}/conversations/{encoded_reference}/resolve"
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
      f"{self._intercom_api_url}/conversations",
      data=json.dumps(
        {
          "conversation": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_intercom_priority(incident.severity),
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
  def _build_front_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._front_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._front_api_url}/conversations/{encoded_reference}/resolve"
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
      f"{self._front_api_url}/conversations",
      data=json.dumps(
        {
          "conversation": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_front_priority(incident.severity),
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
  def _build_servicedeskplus_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._servicedeskplus_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._servicedeskplus_api_url}/alerts/{encoded_reference}/resolve"
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
      f"{self._servicedeskplus_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_servicedeskplus_priority(incident.severity),
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
  def _build_sysaid_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._sysaid_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._sysaid_api_url}/alerts/{encoded_reference}/resolve"
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
      f"{self._sysaid_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_sysaid_priority(incident.severity),
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
  def _build_bmchelix_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._bmchelix_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._bmchelix_api_url}/alerts/{encoded_reference}/resolve"
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
      f"{self._bmchelix_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_bmchelix_priority(incident.severity),
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
  def _build_solarwindsservicedesk_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._solarwindsservicedesk_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._solarwindsservicedesk_api_url}/alerts/{encoded_reference}/resolve"
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
      f"{self._solarwindsservicedesk_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_solarwindsservicedesk_priority(incident.severity),
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
  def _build_topdesk_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._topdesk_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._topdesk_api_url}/incidents/{encoded_reference}/resolve"
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
      f"{self._topdesk_api_url}/incidents",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_topdesk_priority(incident.severity),
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
  def _build_invgateservicedesk_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._invgateservicedesk_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._invgateservicedesk_api_url}/incidents/{encoded_reference}/resolve"
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
      f"{self._invgateservicedesk_api_url}/incidents",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_invgateservicedesk_priority(incident.severity),
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
  def _build_opsramp_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._opsramp_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._opsramp_api_url}/alerts/{encoded_reference}/resolve"
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
      f"{self._opsramp_api_url}/alerts",
      data=json.dumps(
        {
          "alert": {
            "summary": incident.summary[:255],
            "description": incident.detail,
            "status": "pending",
            "priority": self._map_opsramp_priority(incident.severity),
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
