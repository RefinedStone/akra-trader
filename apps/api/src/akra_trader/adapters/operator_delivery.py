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
from akra_trader.domain.models import OperatorIncidentProviderPullSync
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
  if normalized in {"incidentio", "incident_io", "incidentio_incidents", "operator_incidentio"}:
    return "incidentio_incidents"
  if normalized in {"firehydrant", "fire_hydrant", "firehydrant_incidents", "operator_firehydrant"}:
    return "firehydrant_incidents"
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
    pagerduty_recovery_engine_url_template: str | None = None,
    pagerduty_recovery_engine_token: str | None = None,
    incidentio_api_token: str | None = None,
    incidentio_api_url: str = "https://api.incident.io",
    incidentio_recovery_engine_url_template: str | None = None,
    incidentio_recovery_engine_token: str | None = None,
    firehydrant_api_token: str | None = None,
    firehydrant_api_url: str = "https://api.firehydrant.io",
    firehydrant_recovery_engine_url_template: str | None = None,
    firehydrant_recovery_engine_token: str | None = None,
    opsgenie_api_key: str | None = None,
    opsgenie_api_url: str = "https://api.opsgenie.com",
    opsgenie_recovery_engine_url_template: str | None = None,
    opsgenie_recovery_engine_api_key: str | None = None,
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
    self._pagerduty_recovery_engine_url_template = pagerduty_recovery_engine_url_template
    self._pagerduty_recovery_engine_token = pagerduty_recovery_engine_token
    self._incidentio_api_token = incidentio_api_token
    self._incidentio_api_url = incidentio_api_url.rstrip("/")
    self._incidentio_recovery_engine_url_template = incidentio_recovery_engine_url_template
    self._incidentio_recovery_engine_token = incidentio_recovery_engine_token
    self._firehydrant_api_token = firehydrant_api_token
    self._firehydrant_api_url = firehydrant_api_url.rstrip("/")
    self._firehydrant_recovery_engine_url_template = firehydrant_recovery_engine_url_template
    self._firehydrant_recovery_engine_token = firehydrant_recovery_engine_token
    self._opsgenie_api_key = opsgenie_api_key
    self._opsgenie_api_url = opsgenie_api_url.rstrip("/")
    self._opsgenie_recovery_engine_url_template = opsgenie_recovery_engine_url_template
    self._opsgenie_recovery_engine_api_key = opsgenie_recovery_engine_api_key
    self._webhook_timeout_seconds = webhook_timeout_seconds
    self._clock = clock or (lambda: datetime.now(UTC))
    self._urlopen = urlopen or urllib_request.urlopen

  def list_targets(self) -> tuple[str, ...]:
    return self._targets

  def list_supported_workflow_providers(self) -> tuple[str, ...]:
    providers: list[str] = []
    if self._pagerduty_api_token and self._pagerduty_from_email:
      providers.append("pagerduty")
    if self._incidentio_api_token:
      providers.append("incidentio")
    if self._firehydrant_api_token:
      providers.append("firehydrant")
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
      if target == "incidentio_incidents":
        records.append(self._deliver_incidentio(incident=incident, attempt_number=attempt_number, phase=phase))
        continue
      if target == "firehydrant_incidents":
        records.append(self._deliver_firehydrant(incident=incident, attempt_number=attempt_number, phase=phase))
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
    if normalized_provider == "incidentio":
      return (
        self._sync_incidentio_workflow(
          incident=incident,
          action=normalized_action,
          actor=actor,
          detail=detail,
          payload=payload,
          attempt_number=attempt_number,
        ),
      )
    if normalized_provider == "firehydrant":
      return (
        self._sync_firehydrant_workflow(
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

  def pull_incident_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
    provider: str,
  ) -> OperatorIncidentProviderPullSync | None:
    normalized_provider = provider.strip().lower().replace("-", "_")
    if normalized_provider == "pagerduty":
      return self._pull_pagerduty_workflow_state(incident=incident)
    if normalized_provider == "incidentio":
      return self._pull_incidentio_workflow_state(incident=incident)
    if normalized_provider == "firehydrant":
      return self._pull_firehydrant_workflow_state(incident=incident)
    if normalized_provider == "opsgenie":
      return self._pull_opsgenie_workflow_state(incident=incident)
    return None

  @staticmethod
  def _build_recovery_engine_template_context(
    *,
    workflow_reference: str | None,
    external_reference: str | None,
    job_id: str | None,
  ) -> dict[str, str]:
    context: dict[str, str] = {}
    for key, value in {
      "workflow_reference": workflow_reference,
      "reference": external_reference,
      "external_reference": external_reference,
      "job_id": job_id,
    }.items():
      if not value:
        continue
      context[key] = value
      context[f"{key}_urlencoded"] = urllib_parse.quote(value, safe="")
    return context

  @staticmethod
  def _format_recovery_engine_url(
    *,
    url_template: str | None,
    direct_url: str | None,
    workflow_reference: str | None,
    external_reference: str | None,
    job_id: str | None,
  ) -> str | None:
    if direct_url:
      return direct_url
    if not url_template:
      return None
    context = OperatorAlertDeliveryAdapter._build_recovery_engine_template_context(
      workflow_reference=workflow_reference,
      external_reference=external_reference,
      job_id=job_id,
    )
    try:
      return url_template.format_map(context)
    except KeyError:
      return None

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

  def _normalize_recovery_engine_payload(
    self,
    *,
    payload: dict[str, Any],
    provider: str,
  ) -> dict[str, Any]:
    body = self._extract_mapping(
      payload.get("data"),
      payload.get("job"),
      payload.get("telemetry"),
      payload,
    )
    telemetry = self._extract_mapping(
      body.get("telemetry"),
      body.get("status"),
      body.get("progress"),
    )
    merged = {**body, **telemetry}
    state = self._first_non_empty_string(
      merged.get("state"),
      merged.get("status"),
      merged.get("phase"),
    )
    progress = (
      merged.get("progress_percent")
      if isinstance(merged.get("progress_percent"), int)
      else (
        merged.get("progressPercent")
        if isinstance(merged.get("progressPercent"), int)
        else (
          merged.get("completion_percent")
          if isinstance(merged.get("completion_percent"), int)
          else merged.get("percent_complete")
        )
      )
    )
    attempt_count = (
      merged.get("attempt_count")
      if isinstance(merged.get("attempt_count"), int)
      else (
        merged.get("attempts")
        if isinstance(merged.get("attempts"), int)
        else merged.get("retry_count")
      )
    )
    return {
      "source": "provider_engine",
      "state": state,
      "progress_percent": progress,
      "attempt_count": attempt_count,
      "current_step": self._first_non_empty_string(
        merged.get("current_step"),
        merged.get("step"),
        merged.get("stage"),
        merged.get("phase"),
      ),
      "last_message": self._first_non_empty_string(
        merged.get("last_message"),
        merged.get("message"),
        merged.get("summary"),
        merged.get("detail"),
      ),
      "last_error": self._first_non_empty_string(
        merged.get("last_error"),
        merged.get("error"),
      ),
      "external_run_id": self._first_non_empty_string(
        merged.get("external_run_id"),
        merged.get("run_id"),
        merged.get("execution_id"),
        merged.get("job_id"),
        merged.get("id"),
      ),
      "job_url": self._first_non_empty_string(
        merged.get("job_url"),
        merged.get("url"),
        merged.get("html_url"),
      ),
      "started_at": self._parse_provider_datetime(
        merged.get("started_at"),
        merged.get("created_at"),
        merged.get("createdAt"),
      ),
      "finished_at": self._parse_provider_datetime(
        merged.get("finished_at"),
        merged.get("completed_at"),
        merged.get("completedAt"),
        merged.get("finishedAt"),
      ),
      "updated_at": self._parse_provider_datetime(
        merged.get("updated_at"),
        merged.get("updatedAt"),
        merged.get("last_update_at"),
        merged.get("lastUpdateAt"),
      ),
      "provider": provider,
    }

  def _poll_recovery_engine_payload(
    self,
    *,
    provider: str,
    workflow_reference: str | None,
    external_reference: str | None,
    direct_url: str | None,
    job_id: str | None,
  ) -> dict[str, Any]:
    if provider == "pagerduty":
      url = self._format_recovery_engine_url(
        url_template=self._pagerduty_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_pagerduty_recovery_engine_request(url=url)
    elif provider == "incidentio":
      url = self._format_recovery_engine_url(
        url_template=self._incidentio_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_incidentio_recovery_engine_request(url=url)
    elif provider == "firehydrant":
      url = self._format_recovery_engine_url(
        url_template=self._firehydrant_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_firehydrant_recovery_engine_request(url=url)
    elif provider == "opsgenie":
      url = self._format_recovery_engine_url(
        url_template=self._opsgenie_recovery_engine_url_template,
        direct_url=direct_url,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        job_id=job_id,
      )
      if not url:
        return {}
      request = self._build_opsgenie_recovery_engine_request(url=url)
    else:
      return {}
    try:
      with self._urlopen(request, timeout=self._webhook_timeout_seconds) as response:
        payload = self._read_json_response(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
      return {}
    return self._normalize_recovery_engine_payload(payload=payload, provider=provider)

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

  @staticmethod
  def _resolve_pagerduty_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {"triggered", "acknowledged", "resolved"}:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_pagerduty_responder_phase(incident_phase: str) -> str:
    if incident_phase == "triggered":
      return "awaiting_acknowledgment"
    if incident_phase == "acknowledged":
      return "engaged"
    if incident_phase == "resolved":
      return "resolved"
    return "unknown"

  @staticmethod
  def _resolve_pagerduty_urgency_phase(urgency: str | None) -> str:
    normalized = (urgency or "").strip().lower().replace(" ", "_")
    if normalized == "high":
      return "high_urgency"
    if normalized == "low":
      return "low_urgency"
    return "unknown"

  @staticmethod
  def _resolve_pagerduty_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state == "resolved":
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    return "idle"

  @staticmethod
  def _resolve_opsgenie_alert_phase(status: str | None, acknowledged: bool | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {"open", "acknowledged", "closed"}:
      return normalized
    if acknowledged is True:
      return "acknowledged"
    return "unknown"

  @staticmethod
  def _resolve_opsgenie_acknowledgment_phase(alert_phase: str, acknowledged: bool | None) -> str:
    if alert_phase == "closed":
      return "closed"
    if acknowledged is True or alert_phase == "acknowledged":
      return "acknowledged"
    if alert_phase == "open":
      return "pending_acknowledgment"
    return "unknown"

  @staticmethod
  def _resolve_opsgenie_ownership_phase(owner: str | None, teams: list[str]) -> str:
    if owner:
      return "assigned"
    if teams:
      return "team_routed"
    return "unknown"

  @staticmethod
  def _resolve_opsgenie_visibility_phase(seen: bool | None) -> str:
    if seen is True:
      return "seen"
    if seen is False:
      return "unseen"
    return "unknown"

  @staticmethod
  def _resolve_opsgenie_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state == "closed":
      return "closed_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_close"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "recovery_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "alert_acknowledged"
    return "idle"

  @staticmethod
  def _resolve_incidentio_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {"active", "acknowledged", "resolved", "closed"}:
      return normalized
    if normalized in {"triaged"}:
      return "acknowledged"
    return "unknown"

  @staticmethod
  def _resolve_incidentio_assignment_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_incidentio_visibility_phase(visibility: str | None) -> str:
    normalized = (visibility or "").strip().lower().replace(" ", "_")
    if normalized in {"public", "private"}:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_incidentio_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized in {"critical", "high", "warning", "medium", "low"}:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_incidentio_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"closed", "resolved"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    return "idle"

  @staticmethod
  def _resolve_firehydrant_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {"open", "investigating", "mitigating", "monitoring", "resolved", "closed"}:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_firehydrant_ownership_phase(team: str | None) -> str:
    if team:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_firehydrant_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized in {"sev1", "critical"}:
      return "critical"
    if normalized in {"sev2", "high"}:
      return "high"
    if normalized in {"sev3", "medium"}:
      return "medium"
    if normalized in {"sev4", "low"}:
      return "low"
    return "unknown"

  @staticmethod
  def _resolve_firehydrant_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized in {"p1", "critical"}:
      return "critical"
    if normalized in {"p2", "high"}:
      return "high"
    if normalized in {"p3", "medium"}:
      return "medium"
    if normalized in {"p4", "low"}:
      return "low"
    return "unknown"

  @staticmethod
  def _resolve_firehydrant_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"closed", "resolved"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"investigating", "mitigating", "monitoring"}:
      return "incident_active"
    return "idle"

  def _build_provider_pull_sync(
    self,
    *,
    provider: str,
    workflow_reference: str | None,
    external_reference: str | None,
    workflow_state: str,
    detail: str | None,
    provider_payload: dict[str, Any],
    updated_at: datetime | None,
  ) -> OperatorIncidentProviderPullSync:
    remediation_payload = self._extract_mapping(
      provider_payload.get("remediation_provider_payload"),
      provider_payload.get("provider_payload"),
      provider_payload.get("remediation_payload"),
      provider_payload.get("payload"),
    )
    provider_recovery = self._extract_mapping(
      provider_payload.get("remediation_provider_recovery"),
      provider_payload.get("provider_recovery"),
      provider_payload.get("recovery"),
    )
    provider_telemetry = self._extract_mapping(
      provider_payload.get("remediation_provider_telemetry"),
      provider_payload.get("provider_telemetry"),
      provider_payload.get("telemetry"),
      provider_recovery.get("telemetry"),
    )
    provider_specific_recovery = self._extract_mapping(provider_recovery.get(provider))
    status_machine_payload = self._extract_mapping(
      provider_recovery.get("status_machine"),
      provider_payload.get("status_machine"),
    )
    job_id = self._first_non_empty_string(
      provider_recovery.get("job_id"),
      provider_payload.get("job_id"),
    )
    direct_telemetry_url = self._first_non_empty_string(
      provider_payload.get("remediation_provider_telemetry_url"),
      provider_payload.get("provider_telemetry_url"),
      provider_payload.get("telemetry_url"),
      self._extract_mapping(provider_recovery.get("telemetry")).get("job_url"),
    )
    engine_telemetry = self._poll_recovery_engine_payload(
      provider=provider,
      workflow_reference=workflow_reference,
      external_reference=external_reference,
      direct_url=direct_telemetry_url,
      job_id=job_id,
    )
    provider_schema_payload: dict[str, Any] = {}
    if provider == "pagerduty":
      pagerduty_urgency = self._first_non_empty_string(
        provider_specific_recovery.get("urgency"),
        provider_payload.get("urgency"),
        self._extract_mapping(provider_payload.get("incident")).get("urgency"),
      )
      pagerduty_incident_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("incident_phase"),
        self._resolve_pagerduty_incident_phase(workflow_state),
      ) or "unknown"
      provider_schema_payload = {
        "kind": "pagerduty",
        "pagerduty": {
          "incident_id": workflow_reference,
          "incident_key": external_reference,
          "incident_status": workflow_state,
          "urgency": self._first_non_empty_string(
            provider_payload.get("urgency"),
            self._extract_mapping(provider_payload.get("incident")).get("urgency"),
          ),
          "service_id": self._first_non_empty_string(
            provider_payload.get("service_id"),
            self._extract_mapping(provider_payload.get("service")).get("id"),
          ),
          "service_summary": self._first_non_empty_string(
            provider_payload.get("service_summary"),
            self._extract_mapping(provider_payload.get("service")).get("summary"),
            self._extract_mapping(provider_payload.get("service")).get("name"),
          ),
          "escalation_policy_id": self._first_non_empty_string(
            provider_payload.get("escalation_policy_id"),
            self._extract_mapping(provider_payload.get("escalation_policy")).get("id"),
          ),
          "escalation_policy_summary": self._first_non_empty_string(
            provider_payload.get("escalation_policy_summary"),
            self._extract_mapping(provider_payload.get("escalation_policy")).get("summary"),
            self._extract_mapping(provider_payload.get("escalation_policy")).get("name"),
          ),
          "html_url": self._first_non_empty_string(
            provider_payload.get("html_url"),
          ),
          "last_status_change_at": (
            self._parse_provider_datetime(
              provider_payload.get("last_status_change_at"),
            ).isoformat()
            if self._parse_provider_datetime(provider_payload.get("last_status_change_at")) is not None
            else None
          ),
          "phase_graph": {
            "incident_phase": pagerduty_incident_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_pagerduty_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=workflow_state,
            ),
            "responder_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("responder_phase"),
            ) or self._resolve_pagerduty_responder_phase(pagerduty_incident_phase),
            "urgency_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("urgency_phase"),
            ) or self._resolve_pagerduty_urgency_phase(pagerduty_urgency),
            "last_transition_at": (
              self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("last_status_change_at"),
              ).isoformat()
              if self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("last_status_change_at"),
              ) is not None
              else None
            ),
          },
        },
      }
      provider_telemetry = {
        **provider_telemetry,
        "state": self._first_non_empty_string(
          provider_telemetry.get("state"),
          provider_recovery.get("job_state"),
          provider_payload.get("remediation_state"),
        ),
        "job_url": self._first_non_empty_string(
          provider_telemetry.get("job_url"),
          provider_payload.get("html_url"),
        ),
        "updated_at": self._first_non_empty_string(
          provider_telemetry.get("updated_at"),
          provider_payload.get("last_status_change_at"),
        ),
      }
    elif provider == "incidentio":
      incidentio_severity = self._first_non_empty_string(
        provider_payload.get("severity"),
        self._extract_mapping(provider_payload.get("incident")).get("severity"),
      )
      incidentio_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("status"),
      ) or "unknown"
      incidentio_assignee = self._first_non_empty_string(
        provider_payload.get("assignee"),
        self._extract_mapping(provider_payload.get("assignee")).get("name"),
        self._extract_mapping(provider_payload.get("assignee")).get("email"),
      )
      incidentio_visibility = self._first_non_empty_string(
        provider_payload.get("visibility"),
        self._extract_mapping(provider_payload.get("incident")).get("visibility"),
      )
      provider_schema_payload = {
        "kind": "incidentio",
        "incidentio": {
          "incident_id": workflow_reference,
          "external_reference": external_reference,
          "incident_status": incidentio_status,
          "severity": incidentio_severity,
          "mode": self._first_non_empty_string(
            provider_payload.get("mode"),
            self._extract_mapping(provider_payload.get("incident")).get("mode"),
          ),
          "visibility": incidentio_visibility,
          "assignee": incidentio_assignee,
          "url": self._first_non_empty_string(
            provider_payload.get("url"),
            provider_payload.get("html_url"),
            self._extract_mapping(provider_payload.get("incident")).get("url"),
          ),
          "updated_at": self._parse_provider_datetime(
            provider_payload.get("updated_at"),
            self._extract_mapping(provider_payload.get("incident")).get("updated_at"),
            updated_at,
          ),
          "phase_graph": {
            "incident_phase": self._resolve_incidentio_incident_phase(incidentio_status),
            "workflow_phase": self._resolve_incidentio_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=incidentio_status,
            ),
            "assignment_phase": self._resolve_incidentio_assignment_phase(incidentio_assignee),
            "visibility_phase": self._resolve_incidentio_visibility_phase(incidentio_visibility),
            "severity_phase": self._resolve_incidentio_severity_phase(incidentio_severity),
            "last_transition_at": self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ),
          },
        },
      }
      provider_telemetry = {
        **provider_telemetry,
        "state": self._first_non_empty_string(
          provider_telemetry.get("state"),
          provider_recovery.get("job_state"),
          incidentio_status,
        ),
        "job_url": self._first_non_empty_string(
          provider_telemetry.get("job_url"),
          provider_payload.get("url"),
        ),
        "updated_at": self._parse_provider_datetime(
          provider_telemetry.get("updated_at"),
          provider_payload.get("updated_at"),
          updated_at,
        ),
      }
    elif provider == "firehydrant":
      firehydrant_severity = self._first_non_empty_string(
        provider_payload.get("severity"),
        self._extract_mapping(provider_payload.get("incident")).get("severity"),
      )
      firehydrant_priority = self._first_non_empty_string(
        provider_payload.get("priority"),
        self._extract_mapping(provider_payload.get("incident")).get("priority"),
      )
      firehydrant_team = self._first_non_empty_string(
        provider_payload.get("team"),
        self._extract_mapping(provider_payload.get("team")).get("name"),
        self._extract_mapping(provider_payload.get("incident")).get("team"),
      )
      firehydrant_status = self._first_non_empty_string(
        workflow_state,
        provider_payload.get("status"),
      ) or "unknown"
      provider_schema_payload = {
        "kind": "firehydrant",
        "firehydrant": {
          "incident_id": workflow_reference,
          "external_reference": external_reference,
          "incident_status": firehydrant_status,
          "severity": firehydrant_severity,
          "priority": firehydrant_priority,
          "team": firehydrant_team,
          "runbook": self._first_non_empty_string(
            provider_payload.get("runbook"),
            self._extract_mapping(provider_payload.get("runbook")).get("name"),
          ),
          "url": self._first_non_empty_string(
            provider_payload.get("url"),
            provider_payload.get("html_url"),
            self._extract_mapping(provider_payload.get("incident")).get("url"),
          ),
          "updated_at": self._parse_provider_datetime(
            provider_payload.get("updated_at"),
            self._extract_mapping(provider_payload.get("incident")).get("updated_at"),
            updated_at,
          ),
          "phase_graph": {
            "incident_phase": self._resolve_firehydrant_incident_phase(firehydrant_status),
            "workflow_phase": self._resolve_firehydrant_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=firehydrant_status,
            ),
            "ownership_phase": self._resolve_firehydrant_ownership_phase(firehydrant_team),
            "severity_phase": self._resolve_firehydrant_severity_phase(firehydrant_severity),
            "priority_phase": self._resolve_firehydrant_priority_phase(firehydrant_priority),
            "last_transition_at": self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              updated_at,
            ),
          },
        },
      }
      provider_telemetry = {
        **provider_telemetry,
        "state": self._first_non_empty_string(
          provider_telemetry.get("state"),
          provider_recovery.get("job_state"),
          firehydrant_status,
        ),
        "job_url": self._first_non_empty_string(
          provider_telemetry.get("job_url"),
          provider_payload.get("url"),
        ),
        "updated_at": self._parse_provider_datetime(
          provider_telemetry.get("updated_at"),
          provider_payload.get("updated_at"),
          updated_at,
        ),
      }
    elif provider == "opsgenie":
      opsgenie_owner = self._first_non_empty_string(
        provider_specific_recovery.get("owner"),
        provider_payload.get("owner"),
        self._extract_mapping(provider_payload.get("owner_user")).get("username"),
      )
      opsgenie_acknowledged = (
        provider_specific_recovery.get("acknowledged")
        if isinstance(provider_specific_recovery.get("acknowledged"), bool)
        else (
          provider_payload.get("acknowledged")
          if isinstance(provider_payload.get("acknowledged"), bool)
          else None
        )
      )
      opsgenie_seen = (
        provider_specific_recovery.get("seen")
        if isinstance(provider_specific_recovery.get("seen"), bool)
        else (
          provider_payload.get("seen")
          if isinstance(provider_payload.get("seen"), bool)
          else None
        )
      )
      opsgenie_teams = self._extract_string_list(
        provider_specific_recovery.get("teams"),
        provider_payload.get("teams"),
        provider_payload.get("team"),
      )
      opsgenie_alert_phase = self._first_non_empty_string(
        self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("alert_phase"),
        self._resolve_opsgenie_alert_phase(workflow_state, opsgenie_acknowledged),
      ) or "unknown"
      provider_schema_payload = {
        "kind": "opsgenie",
        "opsgenie": {
          "alert_id": workflow_reference,
          "alias": external_reference,
          "alert_status": workflow_state,
          "priority": self._first_non_empty_string(provider_payload.get("priority")),
          "owner": self._first_non_empty_string(
            provider_payload.get("owner"),
            self._extract_mapping(provider_payload.get("owner_user")).get("username"),
          ),
          "acknowledged": (
            provider_payload.get("acknowledged")
            if isinstance(provider_payload.get("acknowledged"), bool)
            else None
          ),
          "seen": (
            provider_payload.get("seen")
            if isinstance(provider_payload.get("seen"), bool)
            else None
          ),
          "tiny_id": self._first_non_empty_string(
            provider_payload.get("tiny_id"),
            provider_payload.get("tinyId"),
          ),
          "teams": self._extract_string_list(
            provider_payload.get("teams"),
            provider_payload.get("team"),
          ),
          "updated_at": (
            self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              provider_payload.get("updatedAt"),
            ).isoformat()
            if self._parse_provider_datetime(
              provider_payload.get("updated_at"),
              provider_payload.get("updatedAt"),
            ) is not None
            else None
          ),
          "phase_graph": {
            "alert_phase": opsgenie_alert_phase,
            "workflow_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("workflow_phase"),
            ) or self._resolve_opsgenie_workflow_phase(
              lifecycle_state=self._first_non_empty_string(
                provider_recovery.get("lifecycle_state"),
                provider_payload.get("recovery_state"),
              ),
              workflow_state=workflow_state,
            ),
            "acknowledgment_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("acknowledgment_phase"),
            ) or self._resolve_opsgenie_acknowledgment_phase(opsgenie_alert_phase, opsgenie_acknowledged),
            "ownership_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("ownership_phase"),
            ) or self._resolve_opsgenie_ownership_phase(opsgenie_owner, opsgenie_teams),
            "visibility_phase": self._first_non_empty_string(
              self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("visibility_phase"),
            ) or self._resolve_opsgenie_visibility_phase(opsgenie_seen),
            "last_transition_at": (
              self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                provider_payload.get("updatedAt"),
              ).isoformat()
              if self._parse_provider_datetime(
                self._extract_mapping(provider_specific_recovery.get("phase_graph")).get("last_transition_at"),
                provider_payload.get("updated_at"),
                provider_payload.get("updatedAt"),
              ) is not None
              else None
            ),
          },
        },
      }
      provider_telemetry = {
        **provider_telemetry,
        "state": self._first_non_empty_string(
          provider_telemetry.get("state"),
          provider_recovery.get("job_state"),
          provider_payload.get("remediation_state"),
        ),
        "updated_at": self._first_non_empty_string(
          provider_telemetry.get("updated_at"),
          provider_payload.get("updated_at"),
          provider_payload.get("updatedAt"),
        ),
      }
    merged_telemetry = {
      **provider_telemetry,
      **{key: value for key, value in engine_telemetry.items() if value is not None},
    }
    merged_payload: dict[str, Any] = dict(remediation_payload)
    merged_payload.update({
      "workflow_reference": workflow_reference,
      "workflow_state": workflow_state,
      "status": self._first_non_empty_string(
        provider_recovery.get("job_state"),
        provider_payload.get("remediation_state"),
        merged_telemetry.get("state"),
      ),
      "recovery_state": self._first_non_empty_string(
        provider_recovery.get("lifecycle_state"),
        provider_payload.get("recovery_state"),
      ),
      "job_id": self._first_non_empty_string(
        provider_recovery.get("job_id"),
        provider_payload.get("job_id"),
      ),
      "summary": self._first_non_empty_string(
        provider_payload.get("remediation_summary"),
        provider_recovery.get("summary"),
      ),
      "detail": self._first_non_empty_string(
        provider_payload.get("remediation_detail"),
        provider_recovery.get("detail"),
        detail,
      ),
      "channels": self._extract_string_list(
        provider_recovery.get("channels"),
        provider_payload.get("channels"),
      ),
      "targets": {
        "symbols": self._extract_string_list(
          provider_recovery.get("symbols"),
          provider_payload.get("symbols"),
        ),
        "timeframe": self._first_non_empty_string(
          provider_recovery.get("timeframe"),
          provider_payload.get("timeframe"),
        ),
      },
      "verification": {
        "state": self._first_non_empty_string(
          provider_recovery.get("verification_state"),
          self._extract_mapping(provider_recovery.get("verification")).get("state"),
          self._extract_mapping(provider_payload.get("verification")).get("state"),
        ),
      },
      "telemetry": {
        "source": self._first_non_empty_string(
          merged_telemetry.get("source"),
        ),
        "state": self._first_non_empty_string(
          merged_telemetry.get("state"),
          provider_recovery.get("job_state"),
          provider_payload.get("remediation_state"),
        ),
        "progress_percent": (
          merged_telemetry.get("progress_percent")
          if isinstance(merged_telemetry.get("progress_percent"), int)
          else merged_telemetry.get("progressPercent")
        ),
        "attempt_count": (
          merged_telemetry.get("attempt_count")
          if isinstance(merged_telemetry.get("attempt_count"), int)
          else (
            merged_telemetry.get("attempts")
            if isinstance(merged_telemetry.get("attempts"), int)
            else status_machine_payload.get("attempt_number")
          )
        ),
        "current_step": self._first_non_empty_string(
          merged_telemetry.get("current_step"),
          merged_telemetry.get("step"),
          merged_telemetry.get("phase"),
        ),
        "last_message": self._first_non_empty_string(
          merged_telemetry.get("last_message"),
          merged_telemetry.get("message"),
          merged_telemetry.get("summary"),
          provider_recovery.get("detail"),
          detail,
        ),
        "last_error": self._first_non_empty_string(
          merged_telemetry.get("last_error"),
          merged_telemetry.get("error"),
        ),
        "external_run_id": self._first_non_empty_string(
          merged_telemetry.get("external_run_id"),
          merged_telemetry.get("run_id"),
          merged_telemetry.get("execution_id"),
          provider_recovery.get("job_id"),
          provider_payload.get("job_id"),
        ),
        "job_url": self._first_non_empty_string(
          merged_telemetry.get("job_url"),
          merged_telemetry.get("url"),
        ),
        "started_at": self._parse_provider_datetime(
          merged_telemetry.get("started_at"),
          merged_telemetry.get("created_at"),
        ),
        "finished_at": self._parse_provider_datetime(
          merged_telemetry.get("finished_at"),
          merged_telemetry.get("completed_at"),
        ),
        "updated_at": self._parse_provider_datetime(
          merged_telemetry.get("updated_at"),
          merged_telemetry.get("last_update_at"),
          updated_at,
        ),
      },
      "status_machine": {
        "state": self._first_non_empty_string(
          provider_recovery.get("status_machine_state"),
          status_machine_payload.get("state"),
        ),
        "workflow_state": self._first_non_empty_string(
          provider_recovery.get("status_machine_workflow_state"),
          status_machine_payload.get("workflow_state"),
          workflow_state,
        ),
        "workflow_action": self._first_non_empty_string(
          provider_recovery.get("status_machine_workflow_action"),
          status_machine_payload.get("workflow_action"),
        ),
        "job_state": self._first_non_empty_string(
          provider_recovery.get("status_machine_job_state"),
          status_machine_payload.get("job_state"),
          provider_recovery.get("job_state"),
        ),
        "sync_state": (
          self._first_non_empty_string(
            provider_recovery.get("status_machine_sync_state"),
            status_machine_payload.get("sync_state"),
          )
          or "provider_authoritative"
        ),
        "last_event_kind": self._first_non_empty_string(
          status_machine_payload.get("last_event_kind"),
        ),
        "last_event_at": (
          self._parse_provider_datetime(status_machine_payload.get("last_event_at")) or updated_at
        ),
        "last_detail": self._first_non_empty_string(
          provider_recovery.get("detail"),
          status_machine_payload.get("last_detail"),
          detail,
        ),
        "attempt_number": (
          int(status_machine_payload.get("attempt_number"))
          if isinstance(status_machine_payload.get("attempt_number"), int)
          else 0
        ),
      },
      "provider_schema": provider_schema_payload,
    })
    remediation_state = self._first_non_empty_string(
      provider_payload.get("remediation_state"),
      provider_recovery.get("lifecycle_state"),
      provider_recovery.get("job_state"),
      merged_payload.get("status"),
    )
    return OperatorIncidentProviderPullSync(
      provider=provider,
      workflow_reference=workflow_reference,
      external_reference=external_reference,
      workflow_state=workflow_state,
      remediation_state=remediation_state,
      detail=detail,
      payload=merged_payload,
      synced_at=updated_at or self._clock(),
    )

  @staticmethod
  def _build_provider_recovery_payload(incident: OperatorIncidentEvent) -> dict[str, Any]:
    provider_recovery = incident.remediation.provider_recovery
    return {
      "lifecycle_state": provider_recovery.lifecycle_state,
      "provider": provider_recovery.provider,
      "job_id": provider_recovery.job_id,
      "reference": provider_recovery.reference,
      "workflow_reference": provider_recovery.workflow_reference,
      "summary": provider_recovery.summary,
      "detail": provider_recovery.detail,
      "channels": provider_recovery.channels,
      "symbols": provider_recovery.symbols,
      "timeframe": provider_recovery.timeframe,
      "updated_at": (
        provider_recovery.updated_at.isoformat()
        if provider_recovery.updated_at is not None
        else None
      ),
      "verification": {
        "state": provider_recovery.verification.state,
        "checked_at": (
          provider_recovery.verification.checked_at.isoformat()
          if provider_recovery.verification.checked_at is not None
          else None
        ),
        "summary": provider_recovery.verification.summary,
        "issues": provider_recovery.verification.issues,
      },
      "telemetry": {
        "source": provider_recovery.telemetry.source,
        "state": provider_recovery.telemetry.state,
        "progress_percent": provider_recovery.telemetry.progress_percent,
        "attempt_count": provider_recovery.telemetry.attempt_count,
        "current_step": provider_recovery.telemetry.current_step,
        "last_message": provider_recovery.telemetry.last_message,
        "last_error": provider_recovery.telemetry.last_error,
        "external_run_id": provider_recovery.telemetry.external_run_id,
        "job_url": provider_recovery.telemetry.job_url,
        "started_at": (
          provider_recovery.telemetry.started_at.isoformat()
          if provider_recovery.telemetry.started_at is not None
          else None
        ),
        "finished_at": (
          provider_recovery.telemetry.finished_at.isoformat()
          if provider_recovery.telemetry.finished_at is not None
          else None
        ),
        "updated_at": (
          provider_recovery.telemetry.updated_at.isoformat()
          if provider_recovery.telemetry.updated_at is not None
          else None
        ),
      },
      "status_machine": {
        "state": provider_recovery.status_machine.state,
        "workflow_state": provider_recovery.status_machine.workflow_state,
        "workflow_action": provider_recovery.status_machine.workflow_action,
        "job_state": provider_recovery.status_machine.job_state,
        "sync_state": provider_recovery.status_machine.sync_state,
        "last_event_kind": provider_recovery.status_machine.last_event_kind,
        "last_event_at": (
          provider_recovery.status_machine.last_event_at.isoformat()
          if provider_recovery.status_machine.last_event_at is not None
          else None
        ),
        "last_detail": provider_recovery.status_machine.last_detail,
        "attempt_number": provider_recovery.status_machine.attempt_number,
      },
      "provider_schema_kind": provider_recovery.provider_schema_kind,
      "pagerduty": {
        "incident_id": provider_recovery.pagerduty.incident_id,
        "incident_key": provider_recovery.pagerduty.incident_key,
        "incident_status": provider_recovery.pagerduty.incident_status,
        "urgency": provider_recovery.pagerduty.urgency,
        "service_id": provider_recovery.pagerduty.service_id,
        "service_summary": provider_recovery.pagerduty.service_summary,
        "escalation_policy_id": provider_recovery.pagerduty.escalation_policy_id,
        "escalation_policy_summary": provider_recovery.pagerduty.escalation_policy_summary,
        "html_url": provider_recovery.pagerduty.html_url,
        "last_status_change_at": (
          provider_recovery.pagerduty.last_status_change_at.isoformat()
          if provider_recovery.pagerduty.last_status_change_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.pagerduty.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.pagerduty.phase_graph.workflow_phase,
          "responder_phase": provider_recovery.pagerduty.phase_graph.responder_phase,
          "urgency_phase": provider_recovery.pagerduty.phase_graph.urgency_phase,
          "last_transition_at": (
            provider_recovery.pagerduty.phase_graph.last_transition_at.isoformat()
            if provider_recovery.pagerduty.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "opsgenie": {
        "alert_id": provider_recovery.opsgenie.alert_id,
        "alias": provider_recovery.opsgenie.alias,
        "alert_status": provider_recovery.opsgenie.alert_status,
        "priority": provider_recovery.opsgenie.priority,
        "owner": provider_recovery.opsgenie.owner,
        "acknowledged": provider_recovery.opsgenie.acknowledged,
        "seen": provider_recovery.opsgenie.seen,
        "tiny_id": provider_recovery.opsgenie.tiny_id,
        "teams": provider_recovery.opsgenie.teams,
        "updated_at": (
          provider_recovery.opsgenie.updated_at.isoformat()
          if provider_recovery.opsgenie.updated_at is not None
          else None
        ),
        "phase_graph": {
          "alert_phase": provider_recovery.opsgenie.phase_graph.alert_phase,
          "workflow_phase": provider_recovery.opsgenie.phase_graph.workflow_phase,
          "acknowledgment_phase": provider_recovery.opsgenie.phase_graph.acknowledgment_phase,
          "ownership_phase": provider_recovery.opsgenie.phase_graph.ownership_phase,
          "visibility_phase": provider_recovery.opsgenie.phase_graph.visibility_phase,
          "last_transition_at": (
            provider_recovery.opsgenie.phase_graph.last_transition_at.isoformat()
            if provider_recovery.opsgenie.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "incidentio": {
        "incident_id": provider_recovery.incidentio.incident_id,
        "external_reference": provider_recovery.incidentio.external_reference,
        "incident_status": provider_recovery.incidentio.incident_status,
        "severity": provider_recovery.incidentio.severity,
        "mode": provider_recovery.incidentio.mode,
        "visibility": provider_recovery.incidentio.visibility,
        "assignee": provider_recovery.incidentio.assignee,
        "url": provider_recovery.incidentio.url,
        "updated_at": (
          provider_recovery.incidentio.updated_at.isoformat()
          if provider_recovery.incidentio.updated_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.incidentio.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.incidentio.phase_graph.workflow_phase,
          "assignment_phase": provider_recovery.incidentio.phase_graph.assignment_phase,
          "visibility_phase": provider_recovery.incidentio.phase_graph.visibility_phase,
          "severity_phase": provider_recovery.incidentio.phase_graph.severity_phase,
          "last_transition_at": (
            provider_recovery.incidentio.phase_graph.last_transition_at.isoformat()
            if provider_recovery.incidentio.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
      "firehydrant": {
        "incident_id": provider_recovery.firehydrant.incident_id,
        "external_reference": provider_recovery.firehydrant.external_reference,
        "incident_status": provider_recovery.firehydrant.incident_status,
        "severity": provider_recovery.firehydrant.severity,
        "priority": provider_recovery.firehydrant.priority,
        "team": provider_recovery.firehydrant.team,
        "runbook": provider_recovery.firehydrant.runbook,
        "url": provider_recovery.firehydrant.url,
        "updated_at": (
          provider_recovery.firehydrant.updated_at.isoformat()
          if provider_recovery.firehydrant.updated_at is not None
          else None
        ),
        "phase_graph": {
          "incident_phase": provider_recovery.firehydrant.phase_graph.incident_phase,
          "workflow_phase": provider_recovery.firehydrant.phase_graph.workflow_phase,
          "ownership_phase": provider_recovery.firehydrant.phase_graph.ownership_phase,
          "severity_phase": provider_recovery.firehydrant.phase_graph.severity_phase,
          "priority_phase": provider_recovery.firehydrant.phase_graph.priority_phase,
          "last_transition_at": (
            provider_recovery.firehydrant.phase_graph.last_transition_at.isoformat()
            if provider_recovery.firehydrant.phase_graph.last_transition_at is not None
            else None
          ),
        },
      },
    }

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
          "provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
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
            "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
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
            "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
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
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
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
              "remediation_provider_recovery": OperatorAlertDeliveryAdapter._build_provider_recovery_payload(incident),
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
  def _read_json_response(response: object) -> dict[str, Any]:
    if not hasattr(response, "read"):
      return {}
    raw = response.read()
    if isinstance(raw, bytes):
      body = raw.decode("utf-8")
    elif isinstance(raw, str):
      body = raw
    else:
      body = ""
    if not body:
      return {}
    parsed = json.loads(body)
    return parsed if isinstance(parsed, dict) else {}

  @staticmethod
  def _extract_mapping(*candidates: Any) -> dict[str, Any]:
    for candidate in candidates:
      if isinstance(candidate, dict):
        return candidate
    return {}

  @staticmethod
  def _extract_string_list(*candidates: Any) -> list[str]:
    for candidate in candidates:
      if isinstance(candidate, str):
        value = candidate.strip()
        if value:
          return [value]
      elif isinstance(candidate, (list, tuple)):
        values = [
          str(item).strip()
          for item in candidate
          if isinstance(item, str) and item.strip()
        ]
        if values:
          return values
    return []

  @staticmethod
  def _first_non_empty_string(*candidates: Any) -> str | None:
    for candidate in candidates:
      if isinstance(candidate, str):
        value = candidate.strip()
        if value:
          return value
    return None

  @staticmethod
  def _parse_provider_datetime(*candidates: Any) -> datetime | None:
    for candidate in candidates:
      if isinstance(candidate, datetime):
        return candidate.astimezone(UTC) if candidate.tzinfo is not None else candidate.replace(tzinfo=UTC)
      if not isinstance(candidate, str):
        continue
      value = candidate.strip()
      if not value:
        continue
      normalized = value.replace("Z", "+00:00")
      try:
        parsed = datetime.fromisoformat(normalized)
      except ValueError:
        continue
      return parsed.astimezone(UTC) if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)
    return None

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
