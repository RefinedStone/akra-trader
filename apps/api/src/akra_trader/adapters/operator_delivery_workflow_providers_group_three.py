from __future__ import annotations

import json
from typing import Any
from urllib import error as urllib_error

from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync


class OperatorDeliveryWorkflowProvidersGroupThreeMixin:
  def _deliver_onpage(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._onpage_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:onpage_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="onpage_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="onpage_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="onpage",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_onpage_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:onpage_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="onpage_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"onpage_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="onpage",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:onpage_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="onpage_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"onpage_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="onpage",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_onpage_workflow(
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
    target = "onpage_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._onpage_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="onpage_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="onpage",
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
        detail="onpage_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="onpage",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_onpage_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="onpage",
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
        detail=f"onpage_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="onpage",
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
        detail=f"onpage_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="onpage",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_onpage_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._onpage_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_onpage_pull_request(
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
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
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
      provider="onpage",
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
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_allquiet(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._allquiet_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:allquiet_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="allquiet_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="allquiet_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="allquiet",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_allquiet_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:allquiet_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="allquiet_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"allquiet_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="allquiet",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:allquiet_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="allquiet_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"allquiet_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="allquiet",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_allquiet_workflow(
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
    target = "allquiet_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._allquiet_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="allquiet_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="allquiet",
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
        detail="allquiet_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="allquiet",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_allquiet_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="allquiet",
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
        detail=f"allquiet_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="allquiet",
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
        detail=f"allquiet_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="allquiet",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_allquiet_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._allquiet_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_allquiet_pull_request(
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
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
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
      provider="allquiet",
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
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_moogsoft(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._moogsoft_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:moogsoft_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="moogsoft_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="moogsoft_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="moogsoft",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_moogsoft_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:moogsoft_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="moogsoft_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"moogsoft_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="moogsoft",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:moogsoft_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="moogsoft_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"moogsoft_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="moogsoft",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_moogsoft_workflow(
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
    target = "moogsoft_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._moogsoft_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="moogsoft_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="moogsoft",
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
        detail="moogsoft_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="moogsoft",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_moogsoft_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="moogsoft",
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
        detail=f"moogsoft_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="moogsoft",
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
        detail=f"moogsoft_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="moogsoft",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_moogsoft_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._moogsoft_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_moogsoft_pull_request(
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
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
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
      provider="moogsoft",
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
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_spikesh(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._spikesh_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:spikesh_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="spikesh_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="spikesh_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="spikesh",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_spikesh_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:spikesh_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="spikesh_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"spikesh_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="spikesh",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:spikesh_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="spikesh_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"spikesh_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="spikesh",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_spikesh_workflow(
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
    target = "spikesh_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._spikesh_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="spikesh_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="spikesh",
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
        detail="spikesh_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="spikesh",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_spikesh_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="spikesh",
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
        detail=f"spikesh_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="spikesh",
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
        detail=f"spikesh_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="spikesh",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_spikesh_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._spikesh_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_spikesh_pull_request(
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
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
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
      provider="spikesh",
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
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_dutycalls(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._dutycalls_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:dutycalls_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="dutycalls_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="dutycalls_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="dutycalls",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_dutycalls_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:dutycalls_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="dutycalls_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"dutycalls_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="dutycalls",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:dutycalls_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="dutycalls_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"dutycalls_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="dutycalls",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_dutycalls_workflow(
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
    target = "dutycalls_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._dutycalls_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="dutycalls_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="dutycalls",
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
        detail="dutycalls_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="dutycalls",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_dutycalls_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="dutycalls",
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
        detail=f"dutycalls_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="dutycalls",
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
        detail=f"dutycalls_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="dutycalls",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_dutycalls_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._dutycalls_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_dutycalls_pull_request(
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
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
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
      provider="dutycalls",
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
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_incidenthub(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._incidenthub_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidenthub_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidenthub_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="incidenthub_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidenthub",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_incidenthub_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidenthub_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidenthub_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"incidenthub_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidenthub",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidenthub_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidenthub_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"incidenthub_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidenthub",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_incidenthub_workflow(
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
    target = "incidenthub_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._incidenthub_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="incidenthub_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidenthub",
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
        detail="incidenthub_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidenthub",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_incidenthub_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="incidenthub",
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
        detail=f"incidenthub_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidenthub",
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
        detail=f"incidenthub_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidenthub",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_incidenthub_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._incidenthub_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_incidenthub_pull_request(
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
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
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
      provider="incidenthub",
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
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_resolver(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._resolver_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:resolver_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="resolver_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="resolver_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="resolver",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_resolver_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:resolver_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="resolver_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"resolver_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="resolver",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:resolver_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="resolver_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"resolver_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="resolver",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_resolver_workflow(
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
    target = "resolver_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._resolver_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="resolver_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="resolver",
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
        detail="resolver_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="resolver",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_resolver_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="resolver",
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
        detail=f"resolver_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="resolver",
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
        detail=f"resolver_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="resolver",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_resolver_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._resolver_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_resolver_pull_request(
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
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
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
      provider="resolver",
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
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_openduty(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._openduty_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:openduty_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="openduty_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="openduty_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="openduty",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_openduty_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:openduty_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="openduty_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"openduty_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="openduty",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:openduty_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="openduty_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"openduty_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="openduty",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_openduty_workflow(
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
    target = "openduty_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._openduty_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="openduty_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="openduty",
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
        detail="openduty_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="openduty",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_openduty_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="openduty",
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
        detail=f"openduty_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="openduty",
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
        detail=f"openduty_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="openduty",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_openduty_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._openduty_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_openduty_pull_request(
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
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
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
      provider="openduty",
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
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_cabot(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._cabot_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:cabot_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="cabot_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="cabot_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="cabot",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_cabot_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:cabot_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="cabot_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"cabot_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="cabot",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:cabot_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="cabot_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"cabot_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="cabot",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_cabot_workflow(
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
    target = "cabot_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._cabot_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="cabot_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="cabot",
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
        detail="cabot_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="cabot",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_cabot_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="cabot",
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
        detail=f"cabot_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="cabot",
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
        detail=f"cabot_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="cabot",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_cabot_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._cabot_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_cabot_pull_request(
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
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
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
      provider="cabot",
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
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_haloitsm(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._haloitsm_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:haloitsm_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="haloitsm_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="haloitsm_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="haloitsm",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_haloitsm_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:haloitsm_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="haloitsm_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"haloitsm_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="haloitsm",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:haloitsm_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="haloitsm_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"haloitsm_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="haloitsm",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_haloitsm_workflow(
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
    target = "haloitsm_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._haloitsm_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="haloitsm_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="haloitsm",
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
        detail="haloitsm_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="haloitsm",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_haloitsm_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="haloitsm",
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
        detail=f"haloitsm_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="haloitsm",
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
        detail=f"haloitsm_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="haloitsm",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_haloitsm_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._haloitsm_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_haloitsm_pull_request(
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
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
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
      provider="haloitsm",
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
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_incidentmanagerio(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._incidentmanagerio_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidentmanagerio_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidentmanagerio_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="incidentmanagerio_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidentmanagerio",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_incidentmanagerio_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidentmanagerio_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidentmanagerio_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"incidentmanagerio_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidentmanagerio",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:incidentmanagerio_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="incidentmanagerio_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"incidentmanagerio_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="incidentmanagerio",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_incidentmanagerio_workflow(
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
    target = "incidentmanagerio_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._incidentmanagerio_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="incidentmanagerio_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidentmanagerio",
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
        detail="incidentmanagerio_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidentmanagerio",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_incidentmanagerio_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="incidentmanagerio",
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
        detail=f"incidentmanagerio_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidentmanagerio",
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
        detail=f"incidentmanagerio_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="incidentmanagerio",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_incidentmanagerio_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._incidentmanagerio_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_incidentmanagerio_pull_request(
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
      payload.get("alert"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
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
      provider="incidentmanagerio",
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
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

