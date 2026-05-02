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

def _normalize_pagerduty_incident_phase(
  incident_status: str | None,
  existing_phase: str,
) -> str:
  normalized = (incident_status or "").strip().lower().replace(" ", "_")
  if normalized in {"triggered", "acknowledged", "resolved"}:
    return normalized
  return existing_phase

def _resolve_pagerduty_responder_phase(incident_phase: str) -> str:
  if incident_phase == "triggered":
    return "awaiting_acknowledgment"
  if incident_phase == "acknowledged":
    return "engaged"
  if incident_phase == "resolved":
    return "resolved"
  return "unknown"

def _resolve_pagerduty_urgency_phase(urgency: str | None, existing_phase: str) -> str:
  normalized = (urgency or "").strip().lower().replace(" ", "_")
  if normalized in {"high"}:
    return "high_urgency"
  if normalized in {"low"}:
    return "low_urgency"
  return existing_phase

def _resolve_pagerduty_workflow_phase(
  *,
  lifecycle_state: str,
  workflow_action: str | None,
  incident_phase: str,
  existing_phase: str,
) -> str:
  if workflow_action == "resolve" or incident_phase == "resolved" or lifecycle_state == "resolved":
    return "resolved_back_synced"
  if lifecycle_state == "verified":
    return "verified_pending_resolve"
  if lifecycle_state == "recovered":
    return "awaiting_local_verification"
  if lifecycle_state == "recovering":
    return "provider_recovering"
  if lifecycle_state == "requested" or workflow_action == "remediate":
    return "remediation_requested"
  if lifecycle_state == "failed":
    return "recovery_failed"
  if workflow_action == "acknowledge" or incident_phase == "acknowledged":
    return "incident_acknowledged"
  if existing_phase != "unknown":
    return existing_phase
  return "idle"

def _build_pagerduty_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  incident_status: str,
  urgency: str | None,
  lifecycle_state: str,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentPagerDutyRecoveryState,
) -> OperatorIncidentPagerDutyRecoveryPhaseGraph:
  phase_payload = self._extract_payload_mapping(payload.get("phase_graph"))
  incident_phase = self._first_non_empty_string(
    phase_payload.get("incident_phase"),
    self._normalize_pagerduty_incident_phase(incident_status, existing.phase_graph.incident_phase),
    existing.phase_graph.incident_phase,
  ) or "unknown"
  workflow_phase = self._first_non_empty_string(
    phase_payload.get("workflow_phase"),
    self._resolve_pagerduty_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_action=status_machine.workflow_action,
      incident_phase=incident_phase,
      existing_phase=existing.phase_graph.workflow_phase,
    ),
    existing.phase_graph.workflow_phase,
  ) or "unknown"
  responder_phase = self._first_non_empty_string(
    phase_payload.get("responder_phase"),
    self._resolve_pagerduty_responder_phase(incident_phase),
    existing.phase_graph.responder_phase,
  ) or "unknown"
  urgency_phase = self._first_non_empty_string(
    phase_payload.get("urgency_phase"),
    self._resolve_pagerduty_urgency_phase(urgency, existing.phase_graph.urgency_phase),
    existing.phase_graph.urgency_phase,
  ) or "unknown"
  last_transition_at = (
    self._parse_payload_datetime(phase_payload.get("last_transition_at"))
    or self._parse_payload_datetime(payload.get("last_status_change_at"))
    or existing.phase_graph.last_transition_at
    or synced_at
  )
  return OperatorIncidentPagerDutyRecoveryPhaseGraph(
    incident_phase=incident_phase,
    workflow_phase=workflow_phase,
    responder_phase=responder_phase,
    urgency_phase=urgency_phase,
    last_transition_at=last_transition_at,
  )

def _normalize_opsgenie_alert_phase(
  alert_status: str | None,
  acknowledged: bool | None,
  existing_phase: str,
) -> str:
  normalized = (alert_status or "").strip().lower().replace(" ", "_")
  if normalized in {"open", "acknowledged", "closed"}:
    return normalized
  if acknowledged is True:
    return "acknowledged"
  return existing_phase

def _resolve_opsgenie_acknowledgment_phase(
  alert_phase: str,
  acknowledged: bool | None,
) -> str:
  if alert_phase == "closed":
    return "closed"
  if acknowledged is True or alert_phase == "acknowledged":
    return "acknowledged"
  if alert_phase == "open":
    return "pending_acknowledgment"
  return "unknown"

def _resolve_opsgenie_ownership_phase(
  owner: str | None,
  teams: tuple[str, ...],
  existing_phase: str,
) -> str:
  if owner:
    return "assigned"
  if teams:
    return "team_routed"
  return existing_phase

def _resolve_opsgenie_visibility_phase(seen: bool | None, existing_phase: str) -> str:
  if seen is True:
    return "seen"
  if seen is False:
    return "unseen"
  return existing_phase

def _resolve_opsgenie_workflow_phase(
  *,
  lifecycle_state: str,
  workflow_action: str | None,
  alert_phase: str,
  existing_phase: str,
) -> str:
  if workflow_action == "resolve" or alert_phase == "closed" or lifecycle_state == "resolved":
    return "closed_back_synced"
  if lifecycle_state == "verified":
    return "verified_pending_close"
  if lifecycle_state == "recovered":
    return "awaiting_local_verification"
  if lifecycle_state == "recovering":
    return "provider_recovering"
  if lifecycle_state == "requested" or workflow_action == "remediate":
    return "recovery_requested"
  if lifecycle_state == "failed":
    return "recovery_failed"
  if alert_phase == "acknowledged":
    return "alert_acknowledged"
  if existing_phase != "unknown":
    return existing_phase
  return "idle"

def _build_opsgenie_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  owner: str | None,
  acknowledged: bool | None,
  seen: bool | None,
  teams: tuple[str, ...],
  lifecycle_state: str,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentOpsgenieRecoveryState,
) -> OperatorIncidentOpsgenieRecoveryPhaseGraph:
  phase_payload = self._extract_payload_mapping(payload.get("phase_graph"))
  alert_phase = self._first_non_empty_string(
    phase_payload.get("alert_phase"),
    self._normalize_opsgenie_alert_phase(alert_status, acknowledged, existing.phase_graph.alert_phase),
    existing.phase_graph.alert_phase,
  ) or "unknown"
  workflow_phase = self._first_non_empty_string(
    phase_payload.get("workflow_phase"),
    self._resolve_opsgenie_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_action=status_machine.workflow_action,
      alert_phase=alert_phase,
      existing_phase=existing.phase_graph.workflow_phase,
    ),
    existing.phase_graph.workflow_phase,
  ) or "unknown"
  acknowledgment_phase = self._first_non_empty_string(
    phase_payload.get("acknowledgment_phase"),
    self._resolve_opsgenie_acknowledgment_phase(alert_phase, acknowledged),
    existing.phase_graph.acknowledgment_phase,
  ) or "unknown"
  ownership_phase = self._first_non_empty_string(
    phase_payload.get("ownership_phase"),
    self._resolve_opsgenie_ownership_phase(owner, teams, existing.phase_graph.ownership_phase),
    existing.phase_graph.ownership_phase,
  ) or "unknown"
  visibility_phase = self._first_non_empty_string(
    phase_payload.get("visibility_phase"),
    self._resolve_opsgenie_visibility_phase(seen, existing.phase_graph.visibility_phase),
    existing.phase_graph.visibility_phase,
  ) or "unknown"
  last_transition_at = (
    self._parse_payload_datetime(phase_payload.get("last_transition_at"))
    or self._parse_payload_datetime(payload.get("updated_at"))
    or self._parse_payload_datetime(payload.get("updatedAt"))
    or existing.phase_graph.last_transition_at
    or synced_at
  )
  return OperatorIncidentOpsgenieRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    acknowledgment_phase=acknowledgment_phase,
    ownership_phase=ownership_phase,
    visibility_phase=visibility_phase,
    last_transition_at=last_transition_at,
  )

def _normalize_incidentio_incident_phase(
  incident_status: str | None,
  existing_phase: str,
) -> str:
  normalized = (incident_status or "").strip().lower().replace(" ", "_")
  if normalized in {"active", "acknowledged", "resolved", "closed"}:
    return normalized
  if normalized in {"triaged"}:
    return "acknowledged"
  return existing_phase

def _resolve_incidentio_assignment_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  if existing_phase != "unknown":
    return existing_phase
  return "unassigned"

def _resolve_incidentio_visibility_phase(
  visibility: str | None,
  existing_phase: str,
) -> str:
  normalized = (visibility or "").strip().lower().replace(" ", "_")
  if normalized in {"public", "private", "internal"}:
    return normalized
  return existing_phase

def _resolve_incidentio_severity_phase(
  severity: str | None,
  existing_phase: str,
) -> str:
  normalized = (severity or "").strip().lower().replace(" ", "_")
  if normalized in {"critical", "high", "warning", "medium", "low", "info"}:
    return normalized
  return existing_phase

def _resolve_incidentio_workflow_phase(
  *,
  lifecycle_state: str,
  workflow_action: str | None,
  incident_phase: str,
  existing_phase: str,
) -> str:
  if workflow_action == "resolve" or incident_phase in {"resolved", "closed"} or lifecycle_state == "resolved":
    return "resolved_back_synced"
  if lifecycle_state == "verified":
    return "verified_pending_resolve"
  if lifecycle_state == "recovered":
    return "awaiting_local_verification"
  if lifecycle_state == "recovering":
    return "provider_recovering"
  if lifecycle_state == "requested" or workflow_action == "remediate":
    return "remediation_requested"
  if lifecycle_state == "failed":
    return "recovery_failed"
  if workflow_action == "acknowledge" or incident_phase == "acknowledged":
    return "incident_acknowledged"
  if existing_phase != "unknown":
    return existing_phase
  return "idle"

def _build_incidentio_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  incident_status: str,
  severity: str | None,
  mode: str | None,
  visibility: str | None,
  assignee: str | None,
  lifecycle_state: str,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentIncidentIoRecoveryState,
) -> OperatorIncidentIncidentIoRecoveryPhaseGraph:
  phase_payload = self._extract_payload_mapping(payload.get("phase_graph"))
  incident_phase = self._first_non_empty_string(
    phase_payload.get("incident_phase"),
    self._normalize_incidentio_incident_phase(incident_status, existing.phase_graph.incident_phase),
    existing.phase_graph.incident_phase,
  ) or "unknown"
  workflow_phase = self._first_non_empty_string(
    phase_payload.get("workflow_phase"),
    self._resolve_incidentio_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_action=status_machine.workflow_action,
      incident_phase=incident_phase,
      existing_phase=existing.phase_graph.workflow_phase,
    ),
    existing.phase_graph.workflow_phase,
  ) or "unknown"
  assignment_phase = self._first_non_empty_string(
    phase_payload.get("assignment_phase"),
    self._resolve_incidentio_assignment_phase(assignee, existing.phase_graph.assignment_phase),
    existing.phase_graph.assignment_phase,
  ) or "unknown"
  visibility_phase = self._first_non_empty_string(
    phase_payload.get("visibility_phase"),
    self._resolve_incidentio_visibility_phase(visibility, existing.phase_graph.visibility_phase),
    existing.phase_graph.visibility_phase,
  ) or "unknown"
  severity_phase = self._first_non_empty_string(
    phase_payload.get("severity_phase"),
    self._resolve_incidentio_severity_phase(severity, existing.phase_graph.severity_phase),
    mode,
    existing.phase_graph.severity_phase,
  ) or "unknown"
  last_transition_at = (
    self._parse_payload_datetime(phase_payload.get("last_transition_at"))
    or self._parse_payload_datetime(payload.get("updated_at"))
    or existing.phase_graph.last_transition_at
    or synced_at
  )
  return OperatorIncidentIncidentIoRecoveryPhaseGraph(
    incident_phase=incident_phase,
    workflow_phase=workflow_phase,
    assignment_phase=assignment_phase,
    visibility_phase=visibility_phase,
    severity_phase=severity_phase,
    last_transition_at=last_transition_at,
  )

def _normalize_firehydrant_incident_phase(
  incident_status: str | None,
  existing_phase: str,
) -> str:
  normalized = (incident_status or "").strip().lower().replace(" ", "_")
  if normalized in {"open", "investigating", "mitigating", "monitoring", "resolved", "closed"}:
    return normalized
  return existing_phase

def _resolve_firehydrant_ownership_phase(
  team: str | None,
  existing_phase: str,
) -> str:
  if team:
    return "assigned"
  if existing_phase != "unknown":
    return existing_phase
  return "unassigned"

def _resolve_firehydrant_severity_phase(
  severity: str | None,
  existing_phase: str,
) -> str:
  normalized = (severity or "").strip().lower().replace(" ", "_")
  if normalized in {"sev1", "critical"}:
    return "critical"
  if normalized in {"sev2", "high"}:
    return "high"
  if normalized in {"sev3", "medium"}:
    return "medium"
  if normalized in {"sev4", "low"}:
    return "low"
  return existing_phase

def _resolve_firehydrant_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized in {"p1", "critical"}:
    return "critical"
  if normalized in {"p2", "high"}:
    return "high"
  if normalized in {"p3", "medium"}:
    return "medium"
  if normalized in {"p4", "low"}:
    return "low"
  return existing_phase

def _resolve_firehydrant_workflow_phase(
  *,
  lifecycle_state: str,
  workflow_action: str | None,
  incident_phase: str,
  existing_phase: str,
) -> str:
  if workflow_action == "resolve" or incident_phase in {"resolved", "closed"} or lifecycle_state == "resolved":
    return "resolved_back_synced"
  if lifecycle_state == "verified":
    return "verified_pending_resolve"
  if lifecycle_state == "recovered":
    return "awaiting_local_verification"
  if lifecycle_state == "recovering":
    return "provider_recovering"
  if lifecycle_state == "requested" or workflow_action == "remediate":
    return "remediation_requested"
  if lifecycle_state == "failed":
    return "recovery_failed"
  if incident_phase in {"investigating", "mitigating", "monitoring"}:
    return "incident_active"
  if existing_phase != "unknown":
    return existing_phase
  return "idle"

def _build_firehydrant_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  incident_status: str,
  severity: str | None,
  priority: str | None,
  team: str | None,
  lifecycle_state: str,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentFireHydrantRecoveryState,
) -> OperatorIncidentFireHydrantRecoveryPhaseGraph:
  phase_payload = self._extract_payload_mapping(payload.get("phase_graph"))
  incident_phase = self._first_non_empty_string(
    phase_payload.get("incident_phase"),
    self._normalize_firehydrant_incident_phase(incident_status, existing.phase_graph.incident_phase),
    existing.phase_graph.incident_phase,
  ) or "unknown"
  workflow_phase = self._first_non_empty_string(
    phase_payload.get("workflow_phase"),
    self._resolve_firehydrant_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_action=status_machine.workflow_action,
      incident_phase=incident_phase,
      existing_phase=existing.phase_graph.workflow_phase,
    ),
    existing.phase_graph.workflow_phase,
  ) or "unknown"
  ownership_phase = self._first_non_empty_string(
    phase_payload.get("ownership_phase"),
    self._resolve_firehydrant_ownership_phase(team, existing.phase_graph.ownership_phase),
    existing.phase_graph.ownership_phase,
  ) or "unknown"
  severity_phase = self._first_non_empty_string(
    phase_payload.get("severity_phase"),
    self._resolve_firehydrant_severity_phase(severity, existing.phase_graph.severity_phase),
    existing.phase_graph.severity_phase,
  ) or "unknown"
  priority_phase = self._first_non_empty_string(
    phase_payload.get("priority_phase"),
    self._resolve_firehydrant_priority_phase(priority, existing.phase_graph.priority_phase),
    existing.phase_graph.priority_phase,
  ) or "unknown"
  last_transition_at = (
    self._parse_payload_datetime(phase_payload.get("last_transition_at"))
    or self._parse_payload_datetime(payload.get("updated_at"))
    or existing.phase_graph.last_transition_at
    or synced_at
  )
  return OperatorIncidentFireHydrantRecoveryPhaseGraph(
    incident_phase=incident_phase,
    workflow_phase=workflow_phase,
    ownership_phase=ownership_phase,
    severity_phase=severity_phase,
    priority_phase=priority_phase,
    last_transition_at=last_transition_at,
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
