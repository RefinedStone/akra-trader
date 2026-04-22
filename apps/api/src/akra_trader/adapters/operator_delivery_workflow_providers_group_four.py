from __future__ import annotations

import json
from typing import Any
from urllib import error as urllib_error

from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync


class OperatorDeliveryWorkflowProvidersGroupFourMixin:
  def _deliver_oneuptime(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._oneuptime_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:oneuptime_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="oneuptime_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="oneuptime_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="oneuptime",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_oneuptime_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:oneuptime_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="oneuptime_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"oneuptime_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="oneuptime",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:oneuptime_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="oneuptime_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"oneuptime_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="oneuptime",
        external_reference=reference,
        source=incident.source,
      )

  def _deliver_squzy(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._squzy_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:squzy_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="squzy_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="squzy_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="squzy",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_squzy_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:squzy_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="squzy_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"squzy_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="squzy",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:squzy_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="squzy_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"squzy_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="squzy",
        external_reference=reference,
        source=incident.source,
      )

  def _deliver_crisescontrol(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._crisescontrol_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:crisescontrol_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="crisescontrol_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="crisescontrol_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="crisescontrol",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_crisescontrol_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:crisescontrol_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="crisescontrol_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"crisescontrol_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="crisescontrol",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:crisescontrol_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="crisescontrol_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"crisescontrol_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="crisescontrol",
        external_reference=reference,
        source=incident.source,
      )

  def _deliver_freshservice(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._freshservice_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:freshservice_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="freshservice_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="freshservice_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="freshservice",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_freshservice_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:freshservice_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="freshservice_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"freshservice_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="freshservice",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:freshservice_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="freshservice_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"freshservice_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="freshservice",
        external_reference=reference,
        source=incident.source,
      )

  def _deliver_freshdesk(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._freshdesk_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:freshdesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="freshdesk_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="freshdesk_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="freshdesk",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_freshdesk_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:freshdesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="freshdesk_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"freshdesk_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="freshdesk",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:freshdesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="freshdesk_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"freshdesk_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="freshdesk",
        external_reference=reference,
        source=incident.source,
      )

  def _deliver_happyfox(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._happyfox_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:happyfox_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="happyfox_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="happyfox_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="happyfox",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_happyfox_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:happyfox_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="happyfox_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"happyfox_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="happyfox",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:happyfox_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="happyfox_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"happyfox_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="happyfox",
        external_reference=reference,
        source=incident.source,
      )

  def _deliver_zendesk(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._zendesk_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:zendesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="zendesk_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="zendesk_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="zendesk",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_zendesk_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:zendesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="zendesk_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"zendesk_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="zendesk",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:zendesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="zendesk_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"zendesk_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="zendesk",
        external_reference=reference,
        source=incident.source,
      )

  def _deliver_zohodesk(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._zohodesk_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:zohodesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="zohodesk_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="zohodesk_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="zohodesk",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_zohodesk_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:zohodesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="zohodesk_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"zohodesk_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="zohodesk",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:zohodesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="zohodesk_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"zohodesk_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="zohodesk",
        external_reference=reference,
        source=incident.source,
      )

  def _deliver_servicedeskplus(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._servicedeskplus_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:servicedeskplus_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="servicedeskplus_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="servicedeskplus_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="servicedeskplus",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_servicedeskplus_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:servicedeskplus_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="servicedeskplus_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"servicedeskplus_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="servicedeskplus",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:servicedeskplus_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="servicedeskplus_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"servicedeskplus_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="servicedeskplus",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_oneuptime_workflow(
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
    target = "oneuptime_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._oneuptime_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="oneuptime_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="oneuptime",
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
        detail="oneuptime_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="oneuptime",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_oneuptime_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="oneuptime",
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
        detail=f"oneuptime_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="oneuptime",
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
        detail=f"oneuptime_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="oneuptime",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_squzy_workflow(
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
    target = "squzy_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._squzy_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="squzy_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="squzy",
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
        detail="squzy_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="squzy",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_squzy_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="squzy",
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
        detail=f"squzy_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="squzy",
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
        detail=f"squzy_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="squzy",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_crisescontrol_workflow(
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
    target = "crisescontrol_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._crisescontrol_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="crisescontrol_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="crisescontrol",
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
        detail="crisescontrol_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="crisescontrol",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_crisescontrol_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="crisescontrol",
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
        detail=f"crisescontrol_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="crisescontrol",
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
        detail=f"crisescontrol_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="crisescontrol",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_freshservice_workflow(
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
    target = "freshservice_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._freshservice_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="freshservice_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="freshservice",
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
        detail="freshservice_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="freshservice",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_freshservice_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="freshservice",
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
        detail=f"freshservice_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="freshservice",
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
        detail=f"freshservice_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="freshservice",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_freshdesk_workflow(
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
    target = "freshdesk_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._freshdesk_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="freshdesk_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="freshdesk",
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
        detail="freshdesk_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="freshdesk",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_freshdesk_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="freshdesk",
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
        detail=f"freshdesk_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="freshdesk",
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
        detail=f"freshdesk_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="freshdesk",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_happyfox_workflow(
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
    target = "happyfox_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._happyfox_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="happyfox_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="happyfox",
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
        detail="happyfox_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="happyfox",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_happyfox_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="happyfox",
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
        detail=f"happyfox_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="happyfox",
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
        detail=f"happyfox_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="happyfox",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_zendesk_workflow(
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
    target = "zendesk_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._zendesk_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="zendesk_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="zendesk",
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
        detail="zendesk_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="zendesk",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_zendesk_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="zendesk",
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
        detail=f"zendesk_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="zendesk",
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
        detail=f"zendesk_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="zendesk",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_zohodesk_workflow(
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
    target = "zohodesk_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._zohodesk_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="zohodesk_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="zohodesk",
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
        detail="zohodesk_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="zohodesk",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_zohodesk_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="zohodesk",
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
        detail=f"zohodesk_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="zohodesk",
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
        detail=f"zohodesk_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="zohodesk",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_servicedeskplus_workflow(
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
    target = "servicedeskplus_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._servicedeskplus_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="servicedeskplus_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="servicedeskplus",
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
        detail="servicedeskplus_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="servicedeskplus",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_servicedeskplus_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="servicedeskplus",
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
        detail=f"servicedeskplus_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="servicedeskplus",
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
        detail=f"servicedeskplus_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="servicedeskplus",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_oneuptime_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._oneuptime_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_oneuptime_pull_request(
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
      provider="oneuptime",
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

  def _pull_squzy_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._squzy_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_squzy_pull_request(
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
      provider="squzy",
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

  def _pull_crisescontrol_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._crisescontrol_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_crisescontrol_pull_request(
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
      provider="crisescontrol",
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

  def _pull_freshservice_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._freshservice_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_freshservice_pull_request(
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
      provider="freshservice",
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

  def _pull_freshdesk_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._freshdesk_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_freshdesk_pull_request(
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
      payload.get("ticket"),
      payload.get("alert"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("ticket"),
      alert_payload.get("alert"),
      alert_payload.get("incident"),
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
      provider="freshdesk",
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

  def _pull_happyfox_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._happyfox_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_happyfox_pull_request(
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
      payload.get("ticket"),
      payload.get("alert"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("ticket"),
      alert_payload.get("alert"),
      alert_payload.get("incident"),
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
      provider="happyfox",
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
        "unknown",
      )
      or "unknown",
      detail=self._first_non_empty_string(
        provider_payload.get("detail"),
        provider_payload.get("summary"),
        alert_payload.get("summary"),
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _pull_zendesk_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._zendesk_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_zendesk_pull_request(
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
      payload.get("ticket"),
      payload.get("alert"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("ticket"),
      alert_payload.get("alert"),
      alert_payload.get("incident"),
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
      provider="zendesk",
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
        "unknown",
      )
      or "unknown",
      detail=self._first_non_empty_string(
        provider_payload.get("detail"),
        provider_payload.get("summary"),
        alert_payload.get("summary"),
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _pull_zohodesk_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._zohodesk_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_zohodesk_pull_request(
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
      payload.get("ticket"),
      payload.get("alert"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("ticket"),
      alert_payload.get("alert"),
      alert_payload.get("incident"),
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
      provider="zohodesk",
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

  def _deliver_helpscout(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._helpscout_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:helpscout_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="helpscout_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="helpscout_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="helpscout",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_helpscout_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:helpscout_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="helpscout_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"helpscout_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="helpscout",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:helpscout_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="helpscout_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"helpscout_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="helpscout",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_helpscout_workflow(
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
    target = "helpscout_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._helpscout_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="helpscout_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="helpscout",
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
        detail="helpscout_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="helpscout",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_helpscout_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="helpscout",
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
        detail=f"helpscout_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="helpscout",
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
        detail=f"helpscout_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="helpscout",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_helpscout_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._helpscout_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_helpscout_pull_request(
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
      payload.get("conversation"),
      payload.get("alert"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("conversation"),
      alert_payload.get("alert"),
      alert_payload.get("incident"),
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
      provider="helpscout",
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
        alert_payload.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_kayako(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._kayako_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:kayako_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="kayako_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="kayako_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="kayako",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_kayako_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:kayako_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="kayako_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"kayako_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="kayako",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:kayako_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="kayako_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"kayako_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="kayako",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_kayako_workflow(
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
    target = "kayako_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._kayako_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="kayako_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="kayako",
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
        detail="kayako_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="kayako",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_kayako_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="kayako",
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
        detail=f"kayako_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="kayako",
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
        detail=f"kayako_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="kayako",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_kayako_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._kayako_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_kayako_pull_request(
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
      payload.get("case"),
      payload.get("alert"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("case"),
      alert_payload.get("alert"),
      alert_payload.get("incident"),
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
      provider="kayako",
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
        alert_payload.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_intercom(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._intercom_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:intercom_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="intercom_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="intercom_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="intercom",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_intercom_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:intercom_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="intercom_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"intercom_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="intercom",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:intercom_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="intercom_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"intercom_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="intercom",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_intercom_workflow(
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
    target = "intercom_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._intercom_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="intercom_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="intercom",
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
        detail="intercom_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="intercom",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_intercom_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="intercom",
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
        detail=f"intercom_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="intercom",
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
        detail=f"intercom_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="intercom",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_intercom_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._intercom_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_intercom_pull_request(
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
      payload.get("conversation"),
      payload.get("alert"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("conversation"),
      alert_payload.get("alert"),
      alert_payload.get("incident"),
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
      provider="intercom",
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
        alert_payload.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _deliver_front(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._front_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:front_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="front_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="front_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="front",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_front_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:front_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="front_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"front_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="front",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:front_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="front_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"front_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="front",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_front_workflow(
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
    target = "front_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._front_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="front_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="front",
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
        detail="front_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="front",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_front_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="front",
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
        detail=f"front_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="front",
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
        detail=f"front_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="front",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_front_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._front_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_front_pull_request(
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
      payload.get("conversation"),
      payload.get("alert"),
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("conversation"),
      alert_payload.get("alert"),
      alert_payload.get("incident"),
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
      provider="front",
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
        alert_payload.get("summary"),
        incident.summary,
      ),
      provider_payload=provider_payload,
      updated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )

  def _pull_servicedeskplus_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._servicedeskplus_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_servicedeskplus_pull_request(
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
      provider="servicedeskplus",
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

  def _deliver_sysaid(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._sysaid_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:sysaid_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="sysaid_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="sysaid_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="sysaid",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_sysaid_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:sysaid_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="sysaid_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"sysaid_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="sysaid",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:sysaid_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="sysaid_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"sysaid_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="sysaid",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_sysaid_workflow(
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
    target = "sysaid_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._sysaid_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="sysaid_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="sysaid",
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
        detail="sysaid_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="sysaid",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_sysaid_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="sysaid",
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
        detail=f"sysaid_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="sysaid",
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
        detail=f"sysaid_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="sysaid",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_sysaid_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._sysaid_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_sysaid_pull_request(
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
      provider="sysaid",
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

  def _deliver_bmchelix(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._bmchelix_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:bmchelix_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="bmchelix_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="bmchelix_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="bmchelix",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_bmchelix_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:bmchelix_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="bmchelix_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"bmchelix_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="bmchelix",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:bmchelix_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="bmchelix_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"bmchelix_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="bmchelix",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_bmchelix_workflow(
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
    target = "bmchelix_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._bmchelix_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="bmchelix_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="bmchelix",
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
        detail="bmchelix_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="bmchelix",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_bmchelix_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="bmchelix",
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
        detail=f"bmchelix_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="bmchelix",
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
        detail=f"bmchelix_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="bmchelix",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_bmchelix_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._bmchelix_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_bmchelix_pull_request(
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
      provider="bmchelix",
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

  def _deliver_solarwindsservicedesk(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._solarwindsservicedesk_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:solarwindsservicedesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="solarwindsservicedesk_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="solarwindsservicedesk_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="solarwindsservicedesk",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_solarwindsservicedesk_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:solarwindsservicedesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="solarwindsservicedesk_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"solarwindsservicedesk_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="solarwindsservicedesk",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:solarwindsservicedesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="solarwindsservicedesk_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"solarwindsservicedesk_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="solarwindsservicedesk",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_solarwindsservicedesk_workflow(
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
    target = "solarwindsservicedesk_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._solarwindsservicedesk_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="solarwindsservicedesk_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="solarwindsservicedesk",
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
        detail="solarwindsservicedesk_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="solarwindsservicedesk",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_solarwindsservicedesk_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="solarwindsservicedesk",
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
        detail=f"solarwindsservicedesk_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="solarwindsservicedesk",
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
        detail=f"solarwindsservicedesk_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="solarwindsservicedesk",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_solarwindsservicedesk_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._solarwindsservicedesk_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_solarwindsservicedesk_pull_request(
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
      provider="solarwindsservicedesk",
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

  def _deliver_topdesk(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._topdesk_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:topdesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="topdesk_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="topdesk_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="topdesk",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_topdesk_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:topdesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="topdesk_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"topdesk_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="topdesk",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:topdesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="topdesk_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"topdesk_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="topdesk",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_topdesk_workflow(
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
    target = "topdesk_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._topdesk_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="topdesk_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="topdesk",
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
        detail="topdesk_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="topdesk",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_topdesk_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="topdesk",
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
        detail=f"topdesk_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="topdesk",
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
        detail=f"topdesk_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="topdesk",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_topdesk_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._topdesk_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_topdesk_pull_request(
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
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload.get("incident"),
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
      provider="topdesk",
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

  def _deliver_invgateservicedesk(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._invgateservicedesk_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:invgateservicedesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="invgateservicedesk_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="invgateservicedesk_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="invgateservicedesk",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_invgateservicedesk_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:invgateservicedesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="invgateservicedesk_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"invgateservicedesk_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="invgateservicedesk",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:invgateservicedesk_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="invgateservicedesk_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"invgateservicedesk_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="invgateservicedesk",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_invgateservicedesk_workflow(
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
    target = "invgateservicedesk_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._invgateservicedesk_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="invgateservicedesk_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="invgateservicedesk",
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
        detail="invgateservicedesk_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="invgateservicedesk",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_invgateservicedesk_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="invgateservicedesk",
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
        detail=f"invgateservicedesk_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="invgateservicedesk",
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
        detail=f"invgateservicedesk_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="invgateservicedesk",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_invgateservicedesk_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._invgateservicedesk_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_invgateservicedesk_pull_request(
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
      payload.get("incident"),
      payload,
    )
    attributes = self._extract_mapping(
      alert_payload.get("attributes"),
      alert_payload.get("alert"),
      alert_payload.get("incident"),
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
      provider="invgateservicedesk",
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

  def _deliver_opsramp(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    reference = incident.external_reference or incident.alert_id
    if not self._opsramp_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:opsramp_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="opsramp_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail="opsramp_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="opsramp",
        external_reference=reference,
        source=incident.source,
      )
    request = self._build_opsramp_delivery_request(
      incident=incident,
      reference=reference,
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 202)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:opsramp_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="opsramp_incidents",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"opsramp_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="opsramp",
        external_reference=reference,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:opsramp_incidents:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="opsramp_incidents",
        status="failed",
        attempted_at=attempted_at,
        detail=f"opsramp_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        external_provider="opsramp",
        external_reference=reference,
        source=incident.source,
      )

  def _sync_opsramp_workflow(
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
    target = "opsramp_workflow"
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._opsramp_api_token:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed",
        attempted_at=attempted_at,
        detail="opsramp_api_token_unconfigured",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="opsramp",
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
        detail="opsramp_workflow_reference_unavailable",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="opsramp",
        external_reference=None,
        source=incident.source,
      )
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_opsramp_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
      reference=reference,
      reference_type=reference_type,
    )
    request = self._project_workflow_market_context_into_request(
      provider="opsramp",
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
        detail=f"opsramp_workflow_status:{status_code}:{action}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="opsramp",
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
        detail=f"opsramp_workflow_failed:{action}:{exc}",
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider="opsramp",
        external_reference=reference,
        source=incident.source,
      )

  def _pull_opsramp_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference or incident.alert_id
    if not self._opsramp_api_token or not reference:
      return None
    reference_type = "id" if incident.provider_workflow_reference else "external_reference"
    request = self._build_opsramp_pull_request(
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
      provider="opsramp",
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


