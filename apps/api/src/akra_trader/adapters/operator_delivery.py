from __future__ import annotations

import json
import logging
from datetime import UTC
from datetime import datetime
from typing import Any
from typing import Callable
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.ports import OperatorAlertDeliveryPort


LOGGER = logging.getLogger("akra_trader.operator_delivery")


def _normalize_target(target: str) -> str | None:
  normalized = target.strip().lower().replace("-", "_")
  if not normalized:
    return None
  if normalized in {"console", "operator_console"}:
    return "operator_console"
  if normalized in {"webhook", "operator_webhook"}:
    return "operator_webhook"
  if normalized in {"slack", "slack_webhook", "operator_slack"}:
    return "slack_webhook"
  if normalized in {"pagerduty", "pagerduty_events", "operator_pagerduty"}:
    return "pagerduty_events"
  if normalized in {"opsgenie", "opsgenie_alerts", "operator_opsgenie"}:
    return "opsgenie_alerts"
  return None


class OperatorAlertDeliveryAdapter(OperatorAlertDeliveryPort):
  def __init__(
    self,
    *,
    targets: tuple[str, ...] = ("console",),
    webhook_url: str | None = None,
    slack_webhook_url: str | None = None,
    pagerduty_integration_key: str | None = None,
    pagerduty_api_token: str | None = None,
    pagerduty_from_email: str | None = None,
    opsgenie_api_key: str | None = None,
    opsgenie_api_url: str = "https://api.opsgenie.com",
    webhook_timeout_seconds: int = 5,
    clock: Callable[[], datetime] | None = None,
    urlopen: Callable[..., object] | None = None,
  ) -> None:
    normalized_targets = []
    for target in targets:
      normalized = _normalize_target(target)
      if normalized is not None and normalized not in normalized_targets:
        normalized_targets.append(normalized)
    self._targets = tuple(normalized_targets)
    self._webhook_url = webhook_url
    self._slack_webhook_url = slack_webhook_url
    self._pagerduty_integration_key = pagerduty_integration_key
    self._pagerduty_api_token = pagerduty_api_token
    self._pagerduty_from_email = pagerduty_from_email
    self._opsgenie_api_key = opsgenie_api_key
    self._opsgenie_api_url = opsgenie_api_url.rstrip("/")
    self._webhook_timeout_seconds = webhook_timeout_seconds
    self._clock = clock or (lambda: datetime.now(UTC))
    self._urlopen = urlopen or urllib_request.urlopen

  def list_targets(self) -> tuple[str, ...]:
    return self._targets

  def list_supported_workflow_providers(self) -> tuple[str, ...]:
    providers: list[str] = []
    if self._pagerduty_api_token and self._pagerduty_from_email:
      providers.append("pagerduty")
    if self._opsgenie_api_key:
      providers.append("opsgenie")
    return tuple(providers)

  def deliver(
    self,
    *,
    incident: OperatorIncidentEvent,
    targets: tuple[str, ...] | None = None,
    attempt_number: int = 1,
    phase: str = "initial",
  ) -> tuple[OperatorIncidentDelivery, ...]:
    records: list[OperatorIncidentDelivery] = []
    resolved_targets = targets or self._targets
    for target in resolved_targets:
      if target == "operator_console":
        records.append(self._deliver_console(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "operator_webhook":
        records.append(self._deliver_webhook(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "slack_webhook":
        records.append(self._deliver_slack(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "pagerduty_events":
        records.append(self._deliver_pagerduty(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "opsgenie_alerts":
        records.append(self._deliver_opsgenie(incident=incident, attempt_number=attempt_number, phase=phase))
    return tuple(records)

  def sync_incident_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    provider: str,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None = None,
    attempt_number: int = 1,
  ) -> tuple[OperatorIncidentDelivery, ...]:
    normalized_provider = provider.strip().lower().replace("-", "_")
    normalized_action = action.strip().lower().replace("-", "_")
    if normalized_provider == "pagerduty":
      return (
        self._sync_pagerduty_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "opsgenie":
      return (
        self._sync_opsgenie_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    attempted_at = self._clock()
    return (
      OperatorIncidentDelivery(
        delivery_id=(
          f"{incident.event_id}:{normalized_provider}_workflow:{normalized_action}:attempt-{attempt_number}"
        ),
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=f"{normalized_provider}_workflow",
        status="failed",
        attempted_at=attempted_at,
        detail=f"provider_workflow_unsupported:{normalized_provider}:{normalized_action}",
        attempt_number=attempt_number,
        phase=f"provider_{normalized_action}",
        provider_action=normalized_action,
        external_provider=normalized_provider,
        external_reference=incident.provider_workflow_reference or incident.external_reference,
        source=incident.source,
      ),
    )

  def _deliver_console(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    LOGGER.warning(
      "operator-incident %s",
      json.dumps(
        {
          "event_id": incident.event_id,
          "alert_id": incident.alert_id,
          "kind": incident.kind,
          "severity": incident.severity,
          "summary": incident.summary,
          "detail": incident.detail,
          "run_id": incident.run_id,
          "session_id": incident.session_id,
          "source": incident.source,
          "delivery_targets": incident.delivery_targets,
        },
        default=str,
        sort_keys=True,
      ),
    )
    return OperatorIncidentDelivery(
      delivery_id=f"{incident.event_id}:operator_console:attempt-{attempt_number}",
      incident_event_id=incident.event_id,
      alert_id=incident.alert_id,
      incident_kind=incident.kind,
      target="operator_console",
      status="delivered",
      attempted_at=attempted_at,
      detail="logged_to_operator_console",
      attempt_number=attempt_number,
      phase=phase,
      source=incident.source,
    )

  def _deliver_webhook(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    if not self._webhook_url:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:operator_webhook:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="operator_webhook",
        status="failed",
        attempted_at=attempted_at,
        detail="webhook_url_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        source=incident.source,
      )

    request = urllib_request.Request(
      self._webhook_url,
      data=self._build_generic_webhook_payload(incident=incident),
      headers={"Content-Type": "application/json"},
      method="POST",
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 200)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:operator_webhook:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="operator_webhook",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"webhook_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:operator_webhook:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="operator_webhook",
        status="failed",
        attempted_at=attempted_at,
        detail=f"webhook_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        source=incident.source,
      )

  def _deliver_slack(
    self,
    *,
    incident: OperatorIncidentEvent,
    attempt_number: int,
    phase: str,
  ) -> OperatorIncidentDelivery:
    attempted_at = self._clock()
    if not self._slack_webhook_url:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:slack_webhook:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="slack_webhook",
        status="failed",
        attempted_at=attempted_at,
        detail="slack_webhook_url_unconfigured",
        attempt_number=attempt_number,
        phase=phase,
        source=incident.source,
      )
    request = urllib_request.Request(
      self._slack_webhook_url,
      data=self._build_slack_payload(incident=incident),
      headers={"Content-Type": "application/json"},
      method="POST",
    )
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        status_code = getattr(response, "status", 200)
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:slack_webhook:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="slack_webhook",
        status="delivered",
        attempted_at=attempted_at,
        detail=f"slack_status:{status_code}",
        attempt_number=attempt_number,
        phase=phase,
        source=incident.source,
      )
    except (urllib_error.URLError, TimeoutError, ValueError) as exc:
      return OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:slack_webhook:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target="slack_webhook",
        status="failed",
        attempted_at=attempted_at,
        detail=f"slack_delivery_failed:{exc}",
        attempt_number=attempt_number,
        phase=phase,
        source=incident.source,
      )

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

    request = self._build_pagerduty_workflow_request(
      incident=incident,
      action=action,
      actor=actor,
      detail=detail,
      workflow_reference=workflow_reference,
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

  @staticmethod
  def _build_generic_webhook_payload(*, incident: OperatorIncidentEvent) -> bytes:
    return json.dumps(
      {
        "event_id": incident.event_id,
        "alert_id": incident.alert_id,
        "kind": incident.kind,
        "timestamp": incident.timestamp.isoformat(),
        "severity": incident.severity,
        "summary": incident.summary,
        "detail": incident.detail,
        "run_id": incident.run_id,
        "session_id": incident.session_id,
        "source": incident.source,
        "remediation": {
          "state": incident.remediation.state,
          "kind": incident.remediation.kind,
          "owner": incident.remediation.owner,
          "summary": incident.remediation.summary,
          "detail": incident.remediation.detail,
          "runbook": incident.remediation.runbook,
          "provider": incident.remediation.provider,
          "reference": incident.remediation.reference,
          "provider_payload": incident.remediation.provider_payload,
          "provider_payload_updated_at": (
            incident.remediation.provider_payload_updated_at.isoformat()
            if incident.remediation.provider_payload_updated_at is not None
            else None
          ),
          "provider_recovery": {
            "lifecycle_state": incident.remediation.provider_recovery.lifecycle_state,
            "provider": incident.remediation.provider_recovery.provider,
            "job_id": incident.remediation.provider_recovery.job_id,
            "reference": incident.remediation.provider_recovery.reference,
            "workflow_reference": incident.remediation.provider_recovery.workflow_reference,
            "summary": incident.remediation.provider_recovery.summary,
            "detail": incident.remediation.provider_recovery.detail,
            "channels": incident.remediation.provider_recovery.channels,
            "symbols": incident.remediation.provider_recovery.symbols,
            "timeframe": incident.remediation.provider_recovery.timeframe,
            "updated_at": (
              incident.remediation.provider_recovery.updated_at.isoformat()
              if incident.remediation.provider_recovery.updated_at is not None
              else None
            ),
            "verification": {
              "state": incident.remediation.provider_recovery.verification.state,
              "checked_at": (
                incident.remediation.provider_recovery.verification.checked_at.isoformat()
                if incident.remediation.provider_recovery.verification.checked_at is not None
                else None
              ),
              "summary": incident.remediation.provider_recovery.verification.summary,
              "issues": incident.remediation.provider_recovery.verification.issues,
            },
            "status_machine": {
              "state": incident.remediation.provider_recovery.status_machine.state,
              "workflow_state": incident.remediation.provider_recovery.status_machine.workflow_state,
              "workflow_action": incident.remediation.provider_recovery.status_machine.workflow_action,
              "job_state": incident.remediation.provider_recovery.status_machine.job_state,
              "sync_state": incident.remediation.provider_recovery.status_machine.sync_state,
              "last_event_kind": incident.remediation.provider_recovery.status_machine.last_event_kind,
              "last_event_at": (
                incident.remediation.provider_recovery.status_machine.last_event_at.isoformat()
                if incident.remediation.provider_recovery.status_machine.last_event_at is not None
                else None
              ),
              "last_detail": incident.remediation.provider_recovery.status_machine.last_detail,
              "attempt_number": incident.remediation.provider_recovery.status_machine.attempt_number,
            },
          },
        },
      }
    ).encode("utf-8")

  @staticmethod
  def _build_slack_payload(*, incident: OperatorIncidentEvent) -> bytes:
    return json.dumps(
      {
        "text": f"[{incident.severity.upper()}] {incident.summary}",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": (
                f"*{incident.summary}*\n"
                f"{incident.detail}\n"
                f"`{incident.kind}` • `{incident.alert_id}` • `{incident.source}`"
                + (
                  f"\nRemediation: {incident.remediation.summary} "
                  f"(`{incident.remediation.runbook or 'n/a'}`)"
                  if incident.remediation.state != "not_applicable" and incident.remediation.summary
                  else ""
                )
              ),
            },
          }
        ],
      }
    ).encode("utf-8")

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
            "remediation_provider_recovery": {
              "lifecycle_state": incident.remediation.provider_recovery.lifecycle_state,
              "job_id": incident.remediation.provider_recovery.job_id,
              "channels": incident.remediation.provider_recovery.channels,
              "symbols": incident.remediation.provider_recovery.symbols,
              "timeframe": incident.remediation.provider_recovery.timeframe,
              "verification_state": incident.remediation.provider_recovery.verification.state,
              "status_machine_state": incident.remediation.provider_recovery.status_machine.state,
              "status_machine_workflow_state": incident.remediation.provider_recovery.status_machine.workflow_state,
              "status_machine_job_state": incident.remediation.provider_recovery.status_machine.job_state,
              "status_machine_sync_state": incident.remediation.provider_recovery.status_machine.sync_state,
            },
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
            "remediation_provider_recovery": {
              "lifecycle_state": incident.remediation.provider_recovery.lifecycle_state,
              "job_id": incident.remediation.provider_recovery.job_id,
              "channels": incident.remediation.provider_recovery.channels,
              "symbols": incident.remediation.provider_recovery.symbols,
              "timeframe": incident.remediation.provider_recovery.timeframe,
              "verification_state": incident.remediation.provider_recovery.verification.state,
              "status_machine_state": incident.remediation.provider_recovery.status_machine.state,
              "status_machine_workflow_state": incident.remediation.provider_recovery.status_machine.workflow_state,
              "status_machine_job_state": incident.remediation.provider_recovery.status_machine.job_state,
              "status_machine_sync_state": incident.remediation.provider_recovery.status_machine.sync_state,
            },
          },
          "tags": ["akra", incident.source, incident.severity.lower()],
        }
      ).encode("utf-8"),
      headers=headers,
      method="POST",
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
  def _format_workflow_payload_context(payload: dict[str, Any] | None) -> str:
    if not payload:
      return ""
    return f" Context: {json.dumps(payload, default=str, sort_keys=True)}"

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
