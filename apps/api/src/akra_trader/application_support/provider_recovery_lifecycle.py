from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any

from akra_trader.domain.models import (
  OperatorIncidentAlertOpsRecoveryPhaseGraph,
  OperatorIncidentAlertOpsRecoveryState,
  OperatorIncidentAllquietRecoveryPhaseGraph,
  OperatorIncidentAllquietRecoveryState,
  OperatorIncidentBetterstackRecoveryPhaseGraph,
  OperatorIncidentBetterstackRecoveryState,
  OperatorIncidentBigPandaRecoveryPhaseGraph,
  OperatorIncidentBigPandaRecoveryState,
  OperatorIncidentBlamelessRecoveryPhaseGraph,
  OperatorIncidentBlamelessRecoveryState,
  OperatorIncidentBmcHelixRecoveryPhaseGraph,
  OperatorIncidentBmcHelixRecoveryState,
  OperatorIncidentCabotRecoveryPhaseGraph,
  OperatorIncidentCabotRecoveryState,
  OperatorIncidentCrisesControlRecoveryPhaseGraph,
  OperatorIncidentCrisesControlRecoveryState,
  OperatorIncidentDutyCallsRecoveryPhaseGraph,
  OperatorIncidentDutyCallsRecoveryState,
  OperatorIncidentFireHydrantRecoveryPhaseGraph,
  OperatorIncidentFireHydrantRecoveryState,
  OperatorIncidentFreshdeskRecoveryPhaseGraph,
  OperatorIncidentFreshdeskRecoveryState,
  OperatorIncidentFreshserviceRecoveryPhaseGraph,
  OperatorIncidentFreshserviceRecoveryState,
  OperatorIncidentFrontRecoveryPhaseGraph,
  OperatorIncidentFrontRecoveryState,
  OperatorIncidentGrafanaOnCallRecoveryPhaseGraph,
  OperatorIncidentGrafanaOnCallRecoveryState,
  OperatorIncidentHaloItsmRecoveryPhaseGraph,
  OperatorIncidentHaloItsmRecoveryState,
  OperatorIncidentHappyfoxRecoveryPhaseGraph,
  OperatorIncidentHappyfoxRecoveryState,
  OperatorIncidentHelpScoutRecoveryPhaseGraph,
  OperatorIncidentHelpScoutRecoveryState,
  OperatorIncidentIlertRecoveryPhaseGraph,
  OperatorIncidentIlertRecoveryState,
  OperatorIncidentIncidentHubRecoveryPhaseGraph,
  OperatorIncidentIncidentHubRecoveryState,
  OperatorIncidentIncidentIoRecoveryPhaseGraph,
  OperatorIncidentIncidentIoRecoveryState,
  OperatorIncidentIncidentManagerIoRecoveryPhaseGraph,
  OperatorIncidentIncidentManagerIoRecoveryState,
  OperatorIncidentIntercomRecoveryPhaseGraph,
  OperatorIncidentIntercomRecoveryState,
  OperatorIncidentInvGateServiceDeskRecoveryPhaseGraph,
  OperatorIncidentInvGateServiceDeskRecoveryState,
  OperatorIncidentJiraServiceManagementRecoveryPhaseGraph,
  OperatorIncidentJiraServiceManagementRecoveryState,
  OperatorIncidentKayakoRecoveryPhaseGraph,
  OperatorIncidentKayakoRecoveryState,
  OperatorIncidentMoogsoftRecoveryPhaseGraph,
  OperatorIncidentMoogsoftRecoveryState,
  OperatorIncidentOneUptimeRecoveryPhaseGraph,
  OperatorIncidentOneUptimeRecoveryState,
  OperatorIncidentOnpageRecoveryPhaseGraph,
  OperatorIncidentOnpageRecoveryState,
  OperatorIncidentOpenDutyRecoveryPhaseGraph,
  OperatorIncidentOpenDutyRecoveryState,
  OperatorIncidentOpsRampRecoveryPhaseGraph,
  OperatorIncidentOpsRampRecoveryState,
  OperatorIncidentOpsgenieRecoveryPhaseGraph,
  OperatorIncidentOpsgenieRecoveryState,
  OperatorIncidentPagerDutyRecoveryPhaseGraph,
  OperatorIncidentPagerDutyRecoveryState,
  OperatorIncidentPagerTreeRecoveryPhaseGraph,
  OperatorIncidentPagerTreeRecoveryState,
  OperatorIncidentProviderRecoveryState,
  OperatorIncidentProviderRecoveryStatusMachine,
  OperatorIncidentProviderRecoveryTelemetry,
  OperatorIncidentProviderRecoveryVerification,
  OperatorIncidentRemediation,
  OperatorIncidentResolverRecoveryPhaseGraph,
  OperatorIncidentResolverRecoveryState,
  OperatorIncidentRootlyRecoveryPhaseGraph,
  OperatorIncidentRootlyRecoveryState,
  OperatorIncidentServiceDeskPlusRecoveryPhaseGraph,
  OperatorIncidentServiceDeskPlusRecoveryState,
  OperatorIncidentServicenowRecoveryPhaseGraph,
  OperatorIncidentServicenowRecoveryState,
  OperatorIncidentSignl4RecoveryPhaseGraph,
  OperatorIncidentSignl4RecoveryState,
  OperatorIncidentSolarWindsServiceDeskRecoveryPhaseGraph,
  OperatorIncidentSolarWindsServiceDeskRecoveryState,
  OperatorIncidentSpikeshRecoveryPhaseGraph,
  OperatorIncidentSpikeshRecoveryState,
  OperatorIncidentSplunkOnCallRecoveryPhaseGraph,
  OperatorIncidentSplunkOnCallRecoveryState,
  OperatorIncidentSquadcastRecoveryPhaseGraph,
  OperatorIncidentSquadcastRecoveryState,
  OperatorIncidentSquzyRecoveryPhaseGraph,
  OperatorIncidentSquzyRecoveryState,
  OperatorIncidentSysAidRecoveryPhaseGraph,
  OperatorIncidentSysAidRecoveryState,
  OperatorIncidentTopdeskRecoveryPhaseGraph,
  OperatorIncidentTopdeskRecoveryState,
  OperatorIncidentXmattersRecoveryPhaseGraph,
  OperatorIncidentXmattersRecoveryState,
  OperatorIncidentZendeskRecoveryPhaseGraph,
  OperatorIncidentZendeskRecoveryState,
  OperatorIncidentZendutyRecoveryPhaseGraph,
  OperatorIncidentZendutyRecoveryState,
  OperatorIncidentZohoDeskRecoveryPhaseGraph,
  OperatorIncidentZohoDeskRecoveryState,
)

from akra_trader.application_support import provider_recovery_family_primary as _provider_recovery_family_primary
from akra_trader.application_support import provider_recovery_family_secondary as _provider_recovery_family_secondary

globals().update(
  {
    name: getattr(_provider_recovery_family_primary, name)
    for name in dir(_provider_recovery_family_primary)
    if name.startswith("_") and not name.startswith("__")
  }
)
globals().update(
  {
    name: getattr(_provider_recovery_family_secondary, name)
    for name in dir(_provider_recovery_family_secondary)
    if name.startswith("_") and not name.startswith("__")
  }
)

def _provider_recovery_lifecycle_for_remediation_state(remediation_state: str) -> str:
  mapping = {
    "requested": "requested",
    "provider_recovering": "recovering",
    "provider_recovered": "recovered",
    "executed": "verified",
    "completed": "verified",
    "partial": "partially_verified",
    "failed": "failed",
  }
  return mapping.get(remediation_state, remediation_state or "not_synced")

def _provider_recovery_lifecycle_for_event(
  *,
  remediation_state: str,
  event_kind: str | None,
) -> str:
  event_mapping = {
    "remediation_requested": "requested",
    "remediation_started": "recovering",
    "remediation_completed": "recovered",
    "remediation_failed": "failed",
    "local_remediation_requested": "requested",
    "local_verification_executed": "verified",
    "local_verification_failed": "failed",
    "provider_resolve_requested": "resolved",
    "provider_resolve_confirmed": "resolved",
  }
  if event_kind is not None and event_kind in event_mapping:
    return event_mapping[event_kind]
  return _provider_recovery_lifecycle_for_remediation_state(remediation_state)

def _provider_recovery_machine_defaults_for_event(
  *,
  remediation_state: str,
  event_kind: str | None = None,
) -> tuple[str, str, str]:
  event_mapping = {
    "remediation_requested": ("provider_requested", "requested", "provider_confirmed"),
    "remediation_started": ("provider_running", "running", "provider_confirmed"),
    "remediation_completed": ("local_verification_pending", "completed", "provider_confirmed"),
    "remediation_failed": ("provider_failed", "failed", "provider_confirmed"),
    "local_remediation_requested": ("provider_requested", "requested", "local_dispatched"),
    "local_verification_executed": ("verified", "verified", "bidirectional_synced"),
    "local_verification_failed": ("verification_failed", "failed", "local_failed"),
    "provider_resolve_requested": ("resolved", "resolved", "bidirectional_synced"),
    "provider_resolve_confirmed": ("resolved", "resolved", "provider_confirmed"),
  }
  if event_kind is not None and event_kind in event_mapping:
    return event_mapping[event_kind]
  remediation_mapping = {
    "requested": ("provider_requested", "requested", "local_dispatched"),
    "provider_recovering": ("provider_running", "running", "provider_confirmed"),
    "provider_recovered": ("local_verification_pending", "completed", "provider_confirmed"),
    "executed": ("verified", "verified", "bidirectional_synced"),
    "completed": ("verified", "verified", "bidirectional_synced"),
    "partial": ("partially_verified", "partial", "partially_synced"),
    "failed": ("provider_failed", "failed", "provider_failed"),
    "skipped": ("verification_skipped", "skipped", "local_only"),
    "retrying": ("provider_requested", "requested", "local_retrying"),
    "suppressed": ("provider_requested", "requested", "suppressed"),
    "not_supported": ("provider_unavailable", "not_supported", "not_supported"),
    "not_configured": ("provider_unavailable", "not_configured", "not_configured"),
    "suggested": ("not_requested", "not_started", "not_synced"),
    "operator_review": ("not_requested", "not_started", "not_synced"),
    "not_applicable": ("not_requested", "not_started", "not_synced"),
  }
  return remediation_mapping.get(remediation_state, ("not_requested", "not_started", "not_synced"))

def _build_provider_recovery_status_machine(
  self,
  *,
  existing: OperatorIncidentProviderRecoveryStatusMachine,
  remediation_state: str,
  event_kind: str | None,
  workflow_state: str | None = None,
  workflow_action: str | None = None,
  job_state: str | None = None,
  sync_state: str | None = None,
  detail: str | None = None,
  event_at: datetime | None = None,
  attempt_number: int | None = None,
  payload: dict[str, Any] | None = None,
) -> OperatorIncidentProviderRecoveryStatusMachine:
  payload = payload or {}
  status_payload = self._extract_payload_mapping(payload.get("status_machine"))
  default_state, default_job_state, default_sync_state = self._provider_recovery_machine_defaults_for_event(
    remediation_state=remediation_state,
    event_kind=event_kind,
  )
  return OperatorIncidentProviderRecoveryStatusMachine(
    state=self._first_non_empty_string(
      status_payload.get("state"),
      payload.get("recovery_machine_state"),
      payload.get("machine_state"),
    ) or default_state,
    workflow_state=self._first_non_empty_string(
      status_payload.get("workflow_state"),
      payload.get("workflow_state"),
      workflow_state,
      existing.workflow_state,
    ) or "idle",
    workflow_action=self._first_non_empty_string(
      status_payload.get("workflow_action"),
      payload.get("workflow_action"),
      workflow_action,
      existing.workflow_action,
    ),
    job_state=self._first_non_empty_string(
      status_payload.get("job_state"),
      payload.get("job_state"),
      payload.get("status"),
      job_state,
    ) or default_job_state,
    sync_state=self._first_non_empty_string(
      status_payload.get("sync_state"),
      payload.get("sync_state"),
      sync_state,
    ) or default_sync_state,
    last_event_kind=self._first_non_empty_string(
      status_payload.get("last_event_kind"),
      payload.get("last_event_kind"),
      event_kind,
      existing.last_event_kind,
    ),
    last_event_at=(
      self._parse_payload_datetime(status_payload.get("last_event_at"))
      or self._parse_payload_datetime(payload.get("last_event_at"))
      or event_at
      or existing.last_event_at
    ),
    last_detail=self._first_non_empty_string(
      status_payload.get("last_detail"),
      payload.get("last_detail"),
      payload.get("status_detail"),
      detail,
      existing.last_detail,
    ),
    attempt_number=(
      int(status_payload.get("attempt_number"))
      if isinstance(status_payload.get("attempt_number"), int)
      else (
        int(payload.get("attempt_number"))
        if isinstance(payload.get("attempt_number"), int)
        else (
          attempt_number
          if attempt_number is not None
          else existing.attempt_number
        )
      )
    ),
  )

def _build_provider_recovery_telemetry(
  self,
  *,
  payload: dict[str, Any],
  synced_at: datetime,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  existing: OperatorIncidentProviderRecoveryTelemetry,
) -> OperatorIncidentProviderRecoveryTelemetry:
  telemetry_payload = self._merge_payload_mappings(
    payload.get("telemetry"),
    payload.get("provider_telemetry"),
    payload.get("remediation_telemetry"),
    payload.get("job_telemetry"),
  )
  return OperatorIncidentProviderRecoveryTelemetry(
    source=self._first_non_empty_string(
      telemetry_payload.get("source"),
      payload.get("telemetry_source"),
      existing.source,
    ) or "unknown",
    state=self._first_non_empty_string(
      telemetry_payload.get("state"),
      telemetry_payload.get("job_state"),
      payload.get("telemetry_state"),
      payload.get("job_state"),
      existing.state,
      status_machine.job_state,
    ) or "unknown",
    progress_percent=self._parse_payload_int(
      telemetry_payload.get("progress_percent"),
      telemetry_payload.get("progressPercent"),
      telemetry_payload.get("percent_complete"),
      telemetry_payload.get("completion_percent"),
      telemetry_payload.get("completionPercent"),
      existing.progress_percent,
    ),
    attempt_count=(
      self._parse_payload_int(
        telemetry_payload.get("attempt_count"),
        telemetry_payload.get("attempts"),
        telemetry_payload.get("retry_count"),
        payload.get("attempt_number"),
        existing.attempt_count,
        status_machine.attempt_number,
      )
      or 0
    ),
    current_step=self._first_non_empty_string(
      telemetry_payload.get("current_step"),
      telemetry_payload.get("step"),
      telemetry_payload.get("phase"),
      payload.get("telemetry_step"),
      existing.current_step,
    ),
    last_message=self._first_non_empty_string(
      telemetry_payload.get("last_message"),
      telemetry_payload.get("message"),
      telemetry_payload.get("summary"),
      existing.last_message,
    ),
    last_error=self._first_non_empty_string(
      telemetry_payload.get("last_error"),
      telemetry_payload.get("error"),
      payload.get("telemetry_error"),
      existing.last_error,
    ),
    external_run_id=self._first_non_empty_string(
      telemetry_payload.get("external_run_id"),
      telemetry_payload.get("run_id"),
      telemetry_payload.get("execution_id"),
      telemetry_payload.get("job_id"),
      payload.get("job_id"),
      existing.external_run_id,
    ),
    job_url=self._first_non_empty_string(
      telemetry_payload.get("job_url"),
      telemetry_payload.get("url"),
      payload.get("job_url"),
      existing.job_url,
    ),
    started_at=(
      self._parse_payload_datetime(telemetry_payload.get("started_at"))
      or self._parse_payload_datetime(telemetry_payload.get("created_at"))
      or existing.started_at
    ),
    finished_at=(
      self._parse_payload_datetime(telemetry_payload.get("finished_at"))
      or self._parse_payload_datetime(telemetry_payload.get("completed_at"))
      or existing.finished_at
    ),
    updated_at=(
      self._parse_payload_datetime(telemetry_payload.get("updated_at"))
      or self._parse_payload_datetime(telemetry_payload.get("last_update_at"))
      or existing.updated_at
      or synced_at
    ),
  )
