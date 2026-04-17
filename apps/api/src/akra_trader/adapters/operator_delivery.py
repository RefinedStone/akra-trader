from __future__ import annotations

import json
import logging
from datetime import UTC
from datetime import datetime
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
    self._webhook_timeout_seconds = webhook_timeout_seconds
    self._clock = clock or (lambda: datetime.now(UTC))
    self._urlopen = urlopen or urllib_request.urlopen

  def list_targets(self) -> tuple[str, ...]:
    return self._targets

  def list_supported_workflow_providers(self) -> tuple[str, ...]:
    if self._pagerduty_api_token and self._pagerduty_from_email:
      return ("pagerduty",)
    return ()

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
    return tuple(records)

  def sync_incident_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    provider: str,
    action: str,
    actor: str,
    detail: str,
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
          },
        },
      }
    ).encode("utf-8")

  def _build_pagerduty_workflow_request(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
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
    raise ValueError(f"unsupported pagerduty workflow action: {action}")

  @staticmethod
  def _map_pagerduty_severity(severity: str) -> str:
    normalized = severity.lower()
    if normalized in {"critical", "error"}:
      return "critical"
    if normalized in {"warning", "warn"}:
      return "warning"
    return "info"
