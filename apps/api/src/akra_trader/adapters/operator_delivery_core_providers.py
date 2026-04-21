from __future__ import annotations

import json
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync


class CoreWorkflowProviderMixin:
  def _build_pagerduty_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    headers = {
      "Accept": "application/json",
    }
    if self._pagerduty_recovery_engine_token:
      headers["Authorization"] = f"Bearer {self._pagerduty_recovery_engine_token}"
    elif self._pagerduty_api_token:
      headers["Authorization"] = f"Token token={self._pagerduty_api_token}"
      headers["Accept"] = "application/vnd.pagerduty+json;version=2"
      if self._pagerduty_from_email:
        headers["From"] = self._pagerduty_from_email
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_opsgenie_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    api_key = self._opsgenie_recovery_engine_api_key or self._opsgenie_api_key
    headers = {
      "Accept": "application/json",
    }
    if api_key:
      headers["Authorization"] = f"GenieKey {api_key}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_incidentio_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    token = self._incidentio_recovery_engine_token or self._incidentio_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_firehydrant_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    token = self._firehydrant_recovery_engine_token or self._firehydrant_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _build_rootly_recovery_engine_request(self, *, url: str) -> urllib_request.Request:
    token = self._rootly_recovery_engine_token or self._rootly_api_token
    headers = {
      "Accept": "application/json",
    }
    if token:
      headers["Authorization"] = f"Bearer {token}"
    return urllib_request.Request(url, headers=headers, method="GET")

  def _deliver_pagerduty(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    if not self._pagerduty_integration_key:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:pagerduty_events:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="pagerduty_events",
        status="failed",
        attempted_at=attempted_at,
        detail="pagerduty_integration_key_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="pagerduty",
        external_reference=incident.external_reference or incident.alert_id,
        source=incident.source,
      )
    request = urllib_request.Request(
      "https://events.pagerduty.com/v2/enqueue",
      data=self._build_pagerduty_payload(incident=incident),
      headers={"Content-Type": "application/json"},
      method="POST",
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:pagerduty_events:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="pagerduty_events",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"pagerduty_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="pagerduty",
        external_reference=incident.external_reference or incident.alert_id,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:pagerduty_events:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="pagerduty_events",
        status="failed",
        attempted_at=attempted_at,
        detail=f"pagerduty_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="pagerduty",
        external_reference=incident.external_reference or incident.alert_id,
        source=incident.source,
      )

  def _sync_pagerduty_workflow(
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
    workflow_reference = incident.provider_workflow_reference or incident.external_reference
    target = "pagerduty_workflow"
    if not self._pagerduty_api_token or not self._pagerduty_from_email:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="pagerduty_workflow_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="pagerduty",
        external_reference=workflow_reference,
        source=incident.source,
      )
    if not workflow_reference:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="pagerduty_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="pagerduty",
        external_reference=None,
        source=incident.source,
      )

    request = self._build_pagerduty_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      workflow_reference=workflow_reference,
    )
    request = self._project_workflow_market_context_into_request(
      provider="pagerduty",
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
        detail=f"pagerduty_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="pagerduty",
        external_reference=workflow_reference,
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
        detail=f"pagerduty_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="pagerduty",
        external_reference=workflow_reference,
        source=incident.source,
      )

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

  def _deliver_firehydrant(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._firehydrant_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:firehydrant_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="firehydrant_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="firehydrant_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="firehydrant",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_firehydrant_delivery_request(incident=incident, reference=reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:firehydrant_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="firehydrant_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"firehydrant_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="firehydrant",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:firehydrant_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="firehydrant_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"firehydrant_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="firehydrant",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_firehydrant_workflow(
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
    target = "firehydrant_workflow"
    if not self._firehydrant_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="firehydrant_workflow_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="firehydrant",
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
        detail="firehydrant_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="firehydrant",
        external_reference=None,
        source=incident.source,
      )
    request = self._build_firehydrant_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="firehydrant",
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
        detail=f"firehydrant_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="firehydrant",
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
        detail=f"firehydrant_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="firehydrant",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_firehydrant_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._firehydrant_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_firehydrant_pull_request(reference=reference, reference_type=reference_type)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(payload.get("incident"), payload.get("data"), payload)
    details_payload = self._extract_mapping(
      incident_payload.get("details"),
      incident_payload.get("custom_fields"),
      incident_payload.get("metadata"),
    )
    provider_payload = dict(details_payload)
    provider_payload.update({
      "severity": incident_payload.get("severity"),
      "priority": incident_payload.get("priority"),
      "team": self._first_non_empty_string(
        self._extract_mapping(incident_payload.get("team")).get("name"),
        incident_payload.get("team"),
      ),
      "runbook": self._first_non_empty_string(
        self._extract_mapping(incident_payload.get("runbook")).get("name"),
        incident_payload.get("runbook"),
      ),
      "url": self._first_non_empty_string(
        incident_payload.get("url"),
        incident_payload.get("incident_url"),
        incident_payload.get("html_url"),
      ),
      "updated_at": incident_payload.get("updated_at"),
      "external_reference": incident_payload.get("external_reference"),
    })
    return self._build_provider_pull_sync(
      provider="firehydrant",
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

  def _deliver_rootly(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._rootly_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:rootly_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="rootly_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="rootly_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="rootly",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_rootly_delivery_request(incident=incident, reference=reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:rootly_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="rootly_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"rootly_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="rootly",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:rootly_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="rootly_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"rootly_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="rootly",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_rootly_workflow(
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
    target = "rootly_workflow"
    if not self._rootly_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="rootly_workflow_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="rootly",
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
        detail="rootly_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="rootly",
        external_reference=None,
        source=incident.source,
      )
    request = self._build_rootly_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="rootly",
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
        detail=f"rootly_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="rootly",
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
        detail=f"rootly_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="rootly",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_rootly_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._rootly_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_rootly_pull_request(reference=reference, reference_type=reference_type)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(
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
      attributes.get("metadata"),
      attributes.get("details"),
      attributes.get("custom_fields"),
    )
    provider_payload = dict(metadata_payload)
    provider_payload.update({
      "severity_id": self._first_non_empty_string(
        attributes.get("severity_id"),
        self._extract_mapping(attributes.get("severity")).get("id"),
      ),
      "private": attributes.get("private") if isinstance(attributes.get("private"), bool) else None,
      "slug": self._first_non_empty_string(
        attributes.get("slug"),
        attributes.get("short_id"),
      ),
      "url": self._first_non_empty_string(
        attributes.get("url"),
        attributes.get("html_url"),
      ),
      "acknowledged_at": attributes.get("acknowledged_at"),
      "updated_at": attributes.get("updated_at"),
      "external_reference": self._first_non_empty_string(
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
    })
    return self._build_provider_pull_sync(
      provider="rootly",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("id"),
        incident.provider_workflow_reference,
        reference if reference_type == "id" else None,
      ),
      external_reference=self._first_non_empty_string(
        attributes.get("external_reference"),
        incident.external_reference,
        incident.alert_id,
      ),
      workflow_state=self._first_non_empty_string(
        attributes.get("status"),
        payload.get("status"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        attributes.get("title"),
        attributes.get("summary"),
        attributes.get("description"),
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        attributes.get("updated_at"),
        attributes.get("created_at"),
      ),
    )

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

  def _pull_pagerduty_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    workflow_reference = incident.provider_workflow_reference or incident.external_reference
    if not self._pagerduty_api_token or not self._pagerduty_from_email or not workflow_reference:
      return None
    request = self._build_pagerduty_pull_request(workflow_reference=workflow_reference)
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return None
    incident_payload = self._extract_mapping(payload.get("incident"), payload)
    body_payload = self._extract_mapping(
      incident_payload.get("body"),
      incident_payload.get("custom_details"),
      incident_payload.get("details"),
    )
    custom_details = self._extract_mapping(
      incident_payload.get("custom_details"),
      body_payload.get("details"),
      body_payload,
    )
    provider_payload = dict(custom_details)
    provider_payload.update({
      "urgency": incident_payload.get("urgency"),
      "html_url": incident_payload.get("html_url"),
      "last_status_change_at": incident_payload.get("last_status_change_at"),
      "service": self._extract_mapping(incident_payload.get("service")),
      "escalation_policy": self._extract_mapping(incident_payload.get("escalation_policy")),
    })
    return self._build_provider_pull_sync(
      provider="pagerduty",
      workflow_reference=self._first_non_empty_string(
        incident_payload.get("id"),
        workflow_reference,
      ),
      external_reference=self._first_non_empty_string(
        incident_payload.get("incident_key"),
        incident.alert_id,
        workflow_reference,
      ),
      workflow_state=self._first_non_empty_string(
        incident_payload.get("status"),
        payload.get("status"),
      ) or "unknown",
      detail=self._first_non_empty_string(
        incident_payload.get("title"),
        incident_payload.get("summary"),
        incident_payload.get("description"),
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        incident_payload.get("last_status_change_at"),
        incident_payload.get("updated_at"),
        payload.get("updated_at"),
      ),
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

  def _build_pagerduty_payload(self, *, incident: OperatorIncidentEvent) -> bytes:
    event_action = "resolve" if incident.kind == "incident_resolved" else "trigger"
    return json.dumps(
      {
        "routing_key": self._pagerduty_integration_key,
        "event_action": event_action,
        "dedup_key": incident.alert_id,
        "payload": {
          "summary": incident.summary,
          "source": incident.source,
          "severity": self._map_pagerduty_severity(incident.severity),
          "timestamp": incident.timestamp.isoformat(),
          "custom_details": {
            "detail": incident.detail,
            "kind": incident.kind,
            "run_id": incident.run_id,
            "session_id": incident.session_id,
            "event_id": incident.event_id,
            "remediation_state": incident.remediation.state,
            "remediation_kind": incident.remediation.kind,
            "remediation_runbook": incident.remediation.runbook,
            "remediation_summary": incident.remediation.summary,
            "remediation_provider_payload": incident.remediation.provider_payload,
            "remediation_provider_recovery": self._build_provider_recovery_payload(incident),
          },
        },
      }
    ).encode("utf-8")

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

  def _build_firehydrant_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._firehydrant_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._firehydrant_api_url}/v1/incidents/{encoded_reference}/resolve"
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
      f"{self._firehydrant_api_url}/v1/incidents",
      data=json.dumps(
        {
          "incident": {
            "name": incident.summary[:255],
            "summary": incident.detail,
            "status": "open",
            "severity": self._map_firehydrant_severity(incident.severity),
            "priority": self._map_firehydrant_priority(incident.severity),
            "external_reference": reference,
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
          }
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
    )

  def _build_rootly_delivery_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    reference: str,
  ) -> urllib_request.Request:
    headers = {
      "Authorization": f"Bearer {self._rootly_api_token}",
      "Content-Type": "application/json",
    }
    if incident.kind == "incident_resolved":
      encoded_reference = urllib_parse.quote(reference, safe="")
      return urllib_request.Request(
        (
          f"{self._rootly_api_url}/v1/incidents/{encoded_reference}/resolve"
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
      f"{self._rootly_api_url}/v1/incidents",
      data=json.dumps(
        {
          "incident": {
            "title": incident.summary[:255],
            "summary": incident.detail,
            "status": "open",
            "severity_id": self._map_rootly_severity(incident.severity),
            "private": False,
            "slug": reference,
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

  def _build_pagerduty_pull_request(
    self,
    *,
    workflow_reference: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(workflow_reference, safe="")
    return urllib_request.Request(
      f"https://api.pagerduty.com/incidents/{encoded_reference}",
      headers={
        "Accept": "application/vnd.pagerduty+json;version=2",
        "Authorization": f"Token token={self._pagerduty_api_token}",
        "From": self._pagerduty_from_email or "",
      },
      method="GET",
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

  def _build_firehydrant_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._firehydrant_api_url}/v1/incidents/{encoded_reference}?identifier_type={reference_type}",
      headers={
        "Authorization": f"Bearer {self._firehydrant_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_rootly_pull_request(
    self,
    *,
    reference: str,
    reference_type: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(reference, safe="")
    return urllib_request.Request(
      f"{self._rootly_api_url}/v1/incidents/{encoded_reference}?identifier_type={reference_type}",
      headers={
        "Authorization": f"Bearer {self._rootly_api_token}",
        "Content-Type": "application/json",
      },
      method="GET",
    )

  def _build_pagerduty_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None,
    workflow_reference: str,
  ) -> urllib_request.Request:
    encoded_reference = urllib_parse.quote(workflow_reference, safe="")
    headers = {
      "Accept": "application/vnd.pagerduty+json;version=2",
      "Authorization": f"Token token={self._pagerduty_api_token}",
      "Content-Type": "application/json",
      "From": self._pagerduty_from_email or "",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"https://api.pagerduty.com/incidents/{encoded_reference}",
        data=json.dumps(
          {
            "incident": {
              "type": "incident_reference",
              "status": "acknowledged",
            }
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "resolve":
      return urllib_request.Request(
        f"https://api.pagerduty.com/incidents/{encoded_reference}",
        data=json.dumps(
          {
            "incident": {
              "type": "incident_reference",
              "status": "resolved",
            }
          }
        ).encode("utf-8"),
        headers=headers,
        method="PUT",
      )
    if action == "escalate":
      return urllib_request.Request(
        f"https://api.pagerduty.com/incidents/{encoded_reference}/notes",
        data=json.dumps(
          {
            "note": {
              "content": (
                f"Akra escalated incident to level {incident.escalation_level}. "
                f"Actor: {actor}. Detail: {detail}."
              ),
            }
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
      )
    if action == "remediate":
      return urllib_request.Request(
        f"https://api.pagerduty.com/incidents/{encoded_reference}/notes",
        data=json.dumps(
          {
            "note": {
              "content": (
                f"Akra requested remediation. Actor: {actor}. "
                f"Summary: {incident.remediation.summary or incident.summary}. "
                f"Runbook: {incident.remediation.runbook or 'n/a'}. Detail: {detail}."
                f"{self._format_workflow_payload_context(payload)}"
              ),
            }
          }
        ).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    raise ValueError(f"unsupported pagerduty workflow action: {action}")

  def _build_firehydrant_workflow_request(
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
      "Authorization": f"Bearer {self._firehydrant_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._firehydrant_api_url}/v1/incidents/{encoded_reference}/acknowledge{suffix}",
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
        f"{self._firehydrant_api_url}/v1/incidents/{encoded_reference}/resolve{suffix}",
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
        f"{self._firehydrant_api_url}/v1/incidents/{encoded_reference}/escalate{suffix}",
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
        f"{self._firehydrant_api_url}/v1/incidents/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported firehydrant workflow action: {action}")

  def _build_rootly_workflow_request(
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
      "Authorization": f"Bearer {self._rootly_api_token}",
      "Content-Type": "application/json",
    }
    if action == "acknowledge":
      return urllib_request.Request(
        f"{self._rootly_api_url}/v1/incidents/{encoded_reference}/acknowledge{suffix}",
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
        f"{self._rootly_api_url}/v1/incidents/{encoded_reference}/resolve{suffix}",
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
        f"{self._rootly_api_url}/v1/incidents/{encoded_reference}/escalate{suffix}",
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
        f"{self._rootly_api_url}/v1/incidents/{encoded_reference}/remediate{suffix}",
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
    raise ValueError(f"unsupported rootly workflow action: {action}")

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
  def _map_pagerduty_severity(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "critical"
    if normalized in {"warning", "warn"}:
      return "warning"
    return "info"

  @staticmethod
  def _map_opsgenie_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "P1"
    if normalized in {"warning", "warn"}:
      return "P3"
    return "P5"

  @staticmethod
  def _map_incidentio_severity(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "critical"
    if normalized in {"warning", "warn"}:
      return "warning"
    return "info"

  @staticmethod
  def _map_firehydrant_severity(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "SEV1"
    if normalized in {"warning", "warn"}:
      return "SEV3"
    return "SEV4"

  @staticmethod
  def _map_firehydrant_priority(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "P1"
    if normalized in {"warning", "warn"}:
      return "P2"
    return "P3"

  @staticmethod
  def _map_rootly_severity(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "sev_critical"
    if normalized in {"warning", "warn"}:
      return "sev_warning"
    return "sev_info"
