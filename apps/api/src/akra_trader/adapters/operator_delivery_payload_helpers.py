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


class OperatorDeliveryPayloadHelpersMixin:
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
      ated_at=self._parse_provider_datetime(
        provider_payload.get("updated_at"),
        alert_payload.get("updated_at"),
        attributes.get("updated_at"),
      ),
    )
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
    market_context = self._build_provider_pull_market_context_payload(
      provider=provider,
      remediation_payload=remediation_payload,
      provider_payload=provider_payload,
      provider_recovery=provider_recovery,
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
    provider_schema_payload = (
      self._build_provider_pull_sync_schema_payload(
        provider=provider,
        workflow_reference=workflow_reference,
        external_reference=external_reference,
        workflow_state=workflow_state,
        detail=detail,
        provider_payload=provider_payload,
        remediation_payload=remediation_payload,
        provider_recovery=provider_recovery,
        provider_telemetry=provider_telemetry,
        market_context=market_context,
        provider_specific_recovery=provider_specific_recovery,
        status_machine_payload=status_machine_payload,
        engine_telemetry=engine_telemetry,
        job_id=job_id,
        updated_at=updated_at,
      )
      or {}
    )
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
      "symbol": market_context["symbol"],
      "symbols": market_context["symbols"],
      "timeframe": market_context["timeframe"],
      "primary_focus": market_context["primary_focus"],
      "market_context_provenance": market_context["market_context_provenance"],
      "targets": {
        "symbol": market_context["symbol"],
        "symbols": market_context["symbols"],
        "timeframe": market_context["timeframe"],
        "primary_focus": market_context["primary_focus"],
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
  @classmethod
  def _build_provider_recovery_payload(cls, incident: OperatorIncidentEvent) -> dict[str, Any]:
    provider_recovery = incident.remediation.provider_recovery
    market_context = cls._build_incident_market_context_payload(incident)
    return {
      "lifecycle_state": provider_recovery.lifecycle_state,
      "provider": provider_recovery.provider,
      "job_id": provider_recovery.job_id,
      "reference": provider_recovery.reference,
      "workflow_reference": provider_recovery.workflow_reference,
      "summary": provider_recovery.summary,
      "detail": provider_recovery.detail,
      "channels": provider_recovery.channels,
      "symbol": market_context["symbol"],
      "symbols": provider_recovery.symbols,
      "timeframe": provider_recovery.timeframe,
      "primary_focus": market_context["primary_focus"],
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
      **cls._build_provider_recovery_payload_schema(provider_recovery),
    }
