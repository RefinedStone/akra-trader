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

def _normalize_bigpanda_incident_phase(status: str | None, existing_phase: str) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "acknowledged",
    "investigating",
    "monitoring",
    "resolved",
    "closed",
    "canceled",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_bigpanda_ownership_phase(assignee: str | None, existing_phase: str) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_bigpanda_severity_phase(severity: str | None, existing_phase: str) -> str:
  normalized = (severity or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_bigpanda_team_phase(team: str | None, existing_phase: str) -> str:
  if team:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_bigpanda_workflow_phase(
  *,
  lifecycle_state: str | None,
  workflow_state: str,
) -> str:
  normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
  if workflow_state in {"resolved", "closed", "canceled"}:
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
  if workflow_state in {"triggered", "open", "investigating", "monitoring"}:
    return "incident_active"
  return "idle"

def _build_bigpanda_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  incident_status: str,
  severity: str | None,
  assignee: str | None,
  team: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentBigPandaRecoveryState,
) -> OperatorIncidentBigPandaRecoveryPhaseGraph:
  incident_phase = self._first_non_empty_string(
    payload.get("incident_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
  ) or self._normalize_bigpanda_incident_phase(
    incident_status,
    existing.phase_graph.incident_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_bigpanda_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=incident_status,
  )
  return OperatorIncidentBigPandaRecoveryPhaseGraph(
    incident_phase=incident_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_bigpanda_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    severity_phase=self._first_non_empty_string(
      payload.get("severity_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("severity_phase"),
    ) or self._resolve_bigpanda_severity_phase(
      severity,
      existing.phase_graph.severity_phase,
    ),
    team_phase=self._first_non_empty_string(
      payload.get("team_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("team_phase"),
    ) or self._resolve_bigpanda_team_phase(
      team,
      existing.phase_graph.team_phase,
    ),
    last_transition_at=(
      self._parse_payload_datetime(payload.get("updated_at"))
      or self._parse_payload_datetime(
        self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
      )
      or synced_at
    ),
  )

def _normalize_grafana_oncall_incident_phase(status: str | None, existing_phase: str) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "acknowledged",
    "investigating",
    "monitoring",
    "resolved",
    "closed",
    "canceled",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_grafana_oncall_ownership_phase(assignee: str | None, existing_phase: str) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_grafana_oncall_severity_phase(severity: str | None, existing_phase: str) -> str:
  normalized = (severity or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_grafana_oncall_escalation_phase(
  escalation_chain: str | None,
  existing_phase: str,
) -> str:
  if escalation_chain:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_grafana_oncall_workflow_phase(
  *,
  lifecycle_state: str | None,
  workflow_state: str,
) -> str:
  normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
  if workflow_state in {"resolved", "closed", "canceled"}:
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
  if workflow_state in {"triggered", "open", "investigating", "monitoring"}:
    return "incident_active"
  return "idle"

def _build_grafana_oncall_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  incident_status: str,
  severity: str | None,
  assignee: str | None,
  escalation_chain: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentGrafanaOnCallRecoveryState,
) -> OperatorIncidentGrafanaOnCallRecoveryPhaseGraph:
  incident_phase = self._first_non_empty_string(
    payload.get("incident_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
  ) or self._normalize_grafana_oncall_incident_phase(
    incident_status,
    existing.phase_graph.incident_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_grafana_oncall_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=incident_status,
  )
  return OperatorIncidentGrafanaOnCallRecoveryPhaseGraph(
    incident_phase=incident_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_grafana_oncall_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    severity_phase=self._first_non_empty_string(
      payload.get("severity_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("severity_phase"),
    ) or self._resolve_grafana_oncall_severity_phase(
      severity,
      existing.phase_graph.severity_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_grafana_oncall_escalation_phase(
      escalation_chain,
      existing.phase_graph.escalation_phase,
    ),
    last_transition_at=(
      self._parse_payload_datetime(payload.get("updated_at"))
      or self._parse_payload_datetime(
        self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
      )
      or synced_at
    ),
  )

def _normalize_zenduty_incident_phase(status: str | None, existing_phase: str) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "acknowledged",
    "investigating",
    "monitoring",
    "resolved",
    "closed",
    "canceled",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_zenduty_ownership_phase(assignee: str | None, existing_phase: str) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_zenduty_severity_phase(severity: str | None, existing_phase: str) -> str:
  normalized = (severity or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_zenduty_service_phase(service: str | None, existing_phase: str) -> str:
  if service:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_zenduty_workflow_phase(
  *,
  lifecycle_state: str | None,
  workflow_state: str,
) -> str:
  normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
  if workflow_state in {"resolved", "closed", "canceled"}:
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
  if workflow_state in {"triggered", "open", "investigating", "monitoring"}:
    return "incident_active"
  return "idle"

def _build_zenduty_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  incident_status: str,
  severity: str | None,
  assignee: str | None,
  service: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentZendutyRecoveryState,
) -> OperatorIncidentZendutyRecoveryPhaseGraph:
  incident_phase = self._first_non_empty_string(
    payload.get("incident_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
  ) or self._normalize_zenduty_incident_phase(
    incident_status,
    existing.phase_graph.incident_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_zenduty_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=incident_status,
  )
  return OperatorIncidentZendutyRecoveryPhaseGraph(
    incident_phase=incident_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_zenduty_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    severity_phase=self._first_non_empty_string(
      payload.get("severity_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("severity_phase"),
    ) or self._resolve_zenduty_severity_phase(
      severity,
      existing.phase_graph.severity_phase,
    ),
    service_phase=self._first_non_empty_string(
      payload.get("service_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("service_phase"),
    ) or self._resolve_zenduty_service_phase(
      service,
      existing.phase_graph.service_phase,
    ),
    last_transition_at=(
      self._parse_payload_datetime(payload.get("updated_at"))
      or self._parse_payload_datetime(
        self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
      )
      or synced_at
    ),
  )

def _normalize_splunk_oncall_incident_phase(status: str | None, existing_phase: str) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "acknowledged",
    "investigating",
    "monitoring",
    "resolved",
    "closed",
    "canceled",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_splunk_oncall_ownership_phase(assignee: str | None, existing_phase: str) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_splunk_oncall_severity_phase(severity: str | None, existing_phase: str) -> str:
  normalized = (severity or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_splunk_oncall_routing_phase(routing_key: str | None, existing_phase: str) -> str:
  if routing_key:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_splunk_oncall_workflow_phase(
  *,
  lifecycle_state: str | None,
  workflow_state: str,
) -> str:
  normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
  if workflow_state in {"resolved", "closed", "canceled"}:
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
  if workflow_state in {"triggered", "open", "investigating", "monitoring"}:
    return "incident_active"
  return "idle"

def _build_splunk_oncall_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  incident_status: str,
  severity: str | None,
  assignee: str | None,
  routing_key: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentSplunkOnCallRecoveryState,
) -> OperatorIncidentSplunkOnCallRecoveryPhaseGraph:
  incident_phase = self._first_non_empty_string(
    payload.get("incident_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
  ) or self._normalize_splunk_oncall_incident_phase(
    incident_status,
    existing.phase_graph.incident_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_splunk_oncall_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=incident_status,
  )
  return OperatorIncidentSplunkOnCallRecoveryPhaseGraph(
    incident_phase=incident_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_splunk_oncall_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    severity_phase=self._first_non_empty_string(
      payload.get("severity_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("severity_phase"),
    ) or self._resolve_splunk_oncall_severity_phase(
      severity,
      existing.phase_graph.severity_phase,
    ),
    routing_phase=self._first_non_empty_string(
      payload.get("routing_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("routing_phase"),
    ) or self._resolve_splunk_oncall_routing_phase(
      routing_key,
      existing.phase_graph.routing_phase,
    ),
    last_transition_at=(
      self._parse_payload_datetime(payload.get("updated_at"))
      or self._parse_payload_datetime(
        self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
      )
      or synced_at
    ),
  )

def _normalize_jira_service_management_incident_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "acknowledged",
    "in_progress",
    "investigating",
    "monitoring",
    "resolved",
    "closed",
    "canceled",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_jira_service_management_assignment_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_jira_service_management_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_jira_service_management_project_phase(
  service_project: str | None,
  existing_phase: str,
) -> str:
  if service_project:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_jira_service_management_workflow_phase(
  *,
  lifecycle_state: str | None,
  workflow_state: str,
) -> str:
  normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
  if workflow_state in {"resolved", "closed", "canceled"}:
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
  if workflow_state in {"triggered", "open", "in_progress", "investigating", "monitoring"}:
    return "incident_active"
  return "idle"

def _build_jira_service_management_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  incident_status: str,
  priority: str | None,
  assignee: str | None,
  service_project: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentJiraServiceManagementRecoveryState,
) -> OperatorIncidentJiraServiceManagementRecoveryPhaseGraph:
  incident_phase = self._first_non_empty_string(
    payload.get("incident_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
  ) or self._normalize_jira_service_management_incident_phase(
    incident_status,
    existing.phase_graph.incident_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_jira_service_management_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=incident_status,
  )
  return OperatorIncidentJiraServiceManagementRecoveryPhaseGraph(
    incident_phase=incident_phase,
    workflow_phase=workflow_phase,
    assignment_phase=self._first_non_empty_string(
      payload.get("assignment_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("assignment_phase"),
    ) or self._resolve_jira_service_management_assignment_phase(
      assignee,
      existing.phase_graph.assignment_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_jira_service_management_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    project_phase=self._first_non_empty_string(
      payload.get("project_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("project_phase"),
    ) or self._resolve_jira_service_management_project_phase(
      service_project,
      existing.phase_graph.project_phase,
    ),
    last_transition_at=(
      self._parse_payload_datetime(payload.get("updated_at"))
      or self._parse_payload_datetime(
        self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
      )
      or synced_at
    ),
  )
