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

def _normalize_rootly_incident_phase(status: str | None, existing_phase: str) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "open",
    "started",
    "acknowledged",
    "investigating",
    "mitigating",
    "monitoring",
    "resolved",
    "closed",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_rootly_acknowledgment_phase(
  incident_phase: str,
  acknowledged_at: datetime | None,
  existing_phase: str,
) -> str:
  if incident_phase in {"resolved", "closed"}:
    return "closed"
  if acknowledged_at is not None or incident_phase == "acknowledged":
    return "acknowledged"
  if incident_phase in {"open", "started", "investigating", "mitigating", "monitoring"}:
    return "pending_acknowledgment"
  return existing_phase or "unknown"

def _resolve_rootly_visibility_phase(private: bool | None, existing_phase: str) -> str:
  if private is True:
    return "private"
  if private is False:
    return "public"
  return existing_phase or "unknown"

def _resolve_rootly_severity_phase(severity_id: str | None, existing_phase: str) -> str:
  normalized = (severity_id or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_rootly_workflow_phase(
  *,
  lifecycle_state: str | None,
  workflow_state: str,
) -> str:
  normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
  if workflow_state in {"resolved", "closed"}:
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
  if workflow_state in {"open", "started", "investigating", "mitigating", "monitoring"}:
    return "incident_active"
  return "idle"

def _build_rootly_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  incident_status: str,
  severity_id: str | None,
  private: bool | None,
  acknowledged_at: datetime | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentRootlyRecoveryState,
) -> OperatorIncidentRootlyRecoveryPhaseGraph:
  incident_phase = self._first_non_empty_string(
    payload.get("incident_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
  ) or self._normalize_rootly_incident_phase(
    incident_status,
    existing.phase_graph.incident_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    status_machine.workflow_state,
  ) or self._resolve_rootly_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=incident_status,
  )
  return OperatorIncidentRootlyRecoveryPhaseGraph(
    incident_phase=incident_phase,
    workflow_phase=workflow_phase,
    acknowledgment_phase=self._first_non_empty_string(
      payload.get("acknowledgment_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("acknowledgment_phase"),
    ) or self._resolve_rootly_acknowledgment_phase(
      incident_phase,
      acknowledged_at,
      existing.phase_graph.acknowledgment_phase,
    ),
    visibility_phase=self._first_non_empty_string(
      payload.get("visibility_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("visibility_phase"),
    ) or self._resolve_rootly_visibility_phase(
      private,
      existing.phase_graph.visibility_phase,
    ),
    severity_phase=self._first_non_empty_string(
      payload.get("severity_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("severity_phase"),
    ) or self._resolve_rootly_severity_phase(
      severity_id,
      existing.phase_graph.severity_phase,
    ),
    last_transition_at=(
      self._parse_payload_datetime(payload.get("updated_at"))
      or self._parse_payload_datetime(
        self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
      )
      or synced_at
    ),
  )

def _normalize_blameless_incident_phase(status: str | None, existing_phase: str) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "open",
    "started",
    "acknowledged",
    "investigating",
    "mitigating",
    "monitoring",
    "resolved",
    "closed",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_blameless_command_phase(commander: str | None, existing_phase: str) -> str:
  if commander:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_blameless_visibility_phase(visibility: str | None, existing_phase: str) -> str:
  normalized = (visibility or "").strip().lower().replace(" ", "_")
  if normalized in {"public", "private", "internal"}:
    return normalized
  return existing_phase or "unknown"

def _resolve_blameless_severity_phase(severity: str | None, existing_phase: str) -> str:
  normalized = (severity or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_blameless_workflow_phase(
  *,
  lifecycle_state: str | None,
  workflow_state: str,
) -> str:
  normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
  if workflow_state in {"resolved", "closed"}:
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
  if workflow_state in {"open", "started", "investigating", "mitigating", "monitoring"}:
    return "incident_active"
  return "idle"

def _build_blameless_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  incident_status: str,
  severity: str | None,
  commander: str | None,
  visibility: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentBlamelessRecoveryState,
) -> OperatorIncidentBlamelessRecoveryPhaseGraph:
  incident_phase = self._first_non_empty_string(
    payload.get("incident_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
  ) or self._normalize_blameless_incident_phase(
    incident_status,
    existing.phase_graph.incident_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_blameless_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=incident_status,
  )
  return OperatorIncidentBlamelessRecoveryPhaseGraph(
    incident_phase=incident_phase,
    workflow_phase=workflow_phase,
    command_phase=self._first_non_empty_string(
      payload.get("command_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("command_phase"),
    ) or self._resolve_blameless_command_phase(
      commander,
      existing.phase_graph.command_phase,
    ),
    visibility_phase=self._first_non_empty_string(
      payload.get("visibility_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("visibility_phase"),
    ) or self._resolve_blameless_visibility_phase(
      visibility,
      existing.phase_graph.visibility_phase,
    ),
    severity_phase=self._first_non_empty_string(
      payload.get("severity_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("severity_phase"),
    ) or self._resolve_blameless_severity_phase(
      severity,
      existing.phase_graph.severity_phase,
    ),
    last_transition_at=(
      self._parse_payload_datetime(payload.get("updated_at"))
      or self._parse_payload_datetime(
        self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
      )
      or synced_at
    ),
  )

def _normalize_xmatters_incident_phase(status: str | None, existing_phase: str) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "open",
    "started",
    "acknowledged",
    "investigating",
    "mitigating",
    "monitoring",
    "resolved",
    "closed",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_xmatters_ownership_phase(assignee: str | None, existing_phase: str) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_xmatters_priority_phase(priority: str | None, existing_phase: str) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_xmatters_response_plan_phase(response_plan: str | None, existing_phase: str) -> str:
  if response_plan:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_xmatters_workflow_phase(
  *,
  lifecycle_state: str | None,
  workflow_state: str,
) -> str:
  normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
  if workflow_state in {"resolved", "closed"}:
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
  if workflow_state in {"open", "started", "investigating", "mitigating", "monitoring"}:
    return "incident_active"
  return "idle"

def _build_xmatters_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  incident_status: str,
  priority: str | None,
  assignee: str | None,
  response_plan: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentXmattersRecoveryState,
) -> OperatorIncidentXmattersRecoveryPhaseGraph:
  incident_phase = self._first_non_empty_string(
    payload.get("incident_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
  ) or self._normalize_xmatters_incident_phase(
    incident_status,
    existing.phase_graph.incident_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_xmatters_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=incident_status,
  )
  return OperatorIncidentXmattersRecoveryPhaseGraph(
    incident_phase=incident_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_xmatters_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_xmatters_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    response_plan_phase=self._first_non_empty_string(
      payload.get("response_plan_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("response_plan_phase"),
    ) or self._resolve_xmatters_response_plan_phase(
      response_plan,
      existing.phase_graph.response_plan_phase,
    ),
    last_transition_at=(
      self._parse_payload_datetime(payload.get("updated_at"))
      or self._parse_payload_datetime(
        self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
      )
      or synced_at
    ),
  )

def _normalize_servicenow_incident_phase(status: str | None, existing_phase: str) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "new",
    "open",
    "acknowledged",
    "in_progress",
    "on_hold",
    "resolved",
    "closed",
    "canceled",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_servicenow_assignment_phase(
  assigned_to: str | None,
  assignment_group: str | None,
  existing_phase: str,
) -> str:
  if assigned_to:
    return "assigned_to_user"
  if assignment_group:
    return "assigned_to_group"
  return existing_phase or "unassigned"

def _resolve_servicenow_priority_phase(priority: str | None, existing_phase: str) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_servicenow_group_phase(assignment_group: str | None, existing_phase: str) -> str:
  if assignment_group:
    return "group_configured"
  return existing_phase or "group_unconfigured"

def _resolve_servicenow_workflow_phase(
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
  if workflow_state in {"new", "open", "in_progress", "on_hold"}:
    return "incident_active"
  return "idle"

def _build_servicenow_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  incident_status: str,
  priority: str | None,
  assigned_to: str | None,
  assignment_group: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentServicenowRecoveryState,
) -> OperatorIncidentServicenowRecoveryPhaseGraph:
  incident_phase = self._first_non_empty_string(
    payload.get("incident_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
  ) or self._normalize_servicenow_incident_phase(
    incident_status,
    existing.phase_graph.incident_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_servicenow_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=incident_status,
  )
  return OperatorIncidentServicenowRecoveryPhaseGraph(
    incident_phase=incident_phase,
    workflow_phase=workflow_phase,
    assignment_phase=self._first_non_empty_string(
      payload.get("assignment_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("assignment_phase"),
    ) or self._resolve_servicenow_assignment_phase(
      assigned_to,
      assignment_group,
      existing.phase_graph.assignment_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_servicenow_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    group_phase=self._first_non_empty_string(
      payload.get("group_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("group_phase"),
    ) or self._resolve_servicenow_group_phase(
      assignment_group,
      existing.phase_graph.group_phase,
    ),
    last_transition_at=(
      self._parse_payload_datetime(payload.get("updated_at"))
      or self._parse_payload_datetime(
        self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
      )
      or synced_at
    ),
  )

def _normalize_squadcast_incident_phase(status: str | None, existing_phase: str) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "acknowledged",
    "investigating",
    "on_hold",
    "resolved",
    "closed",
    "canceled",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_squadcast_ownership_phase(assignee: str | None, existing_phase: str) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_squadcast_severity_phase(severity: str | None, existing_phase: str) -> str:
  normalized = (severity or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_squadcast_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_squadcast_workflow_phase(
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
  if workflow_state in {"triggered", "open", "investigating", "on_hold"}:
    return "incident_active"
  return "idle"

def _build_squadcast_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  incident_status: str,
  severity: str | None,
  assignee: str | None,
  escalation_policy: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentSquadcastRecoveryState,
) -> OperatorIncidentSquadcastRecoveryPhaseGraph:
  incident_phase = self._first_non_empty_string(
    payload.get("incident_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
  ) or self._normalize_squadcast_incident_phase(
    incident_status,
    existing.phase_graph.incident_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_squadcast_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=incident_status,
  )
  return OperatorIncidentSquadcastRecoveryPhaseGraph(
    incident_phase=incident_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_squadcast_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    severity_phase=self._first_non_empty_string(
      payload.get("severity_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("severity_phase"),
    ) or self._resolve_squadcast_severity_phase(
      severity,
      existing.phase_graph.severity_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_squadcast_escalation_phase(
      escalation_policy,
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
