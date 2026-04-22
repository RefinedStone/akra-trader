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

def _normalize_pagertree_incident_phase(
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

def _resolve_pagertree_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_pagertree_urgency_phase(
  urgency: str | None,
  existing_phase: str,
) -> str:
  normalized = (urgency or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_pagertree_team_phase(
  team: str | None,
  existing_phase: str,
) -> str:
  if team:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_pagertree_workflow_phase(
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

def _build_pagertree_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  incident_status: str,
  urgency: str | None,
  assignee: str | None,
  team: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentPagerTreeRecoveryState,
) -> OperatorIncidentPagerTreeRecoveryPhaseGraph:
  incident_phase = self._first_non_empty_string(
    payload.get("incident_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
  ) or self._normalize_pagertree_incident_phase(
    incident_status,
    existing.phase_graph.incident_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_pagertree_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=incident_status,
  )
  return OperatorIncidentPagerTreeRecoveryPhaseGraph(
    incident_phase=incident_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_pagertree_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    urgency_phase=self._first_non_empty_string(
      payload.get("urgency_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("urgency_phase"),
    ) or self._resolve_pagertree_urgency_phase(
      urgency,
      existing.phase_graph.urgency_phase,
    ),
    team_phase=self._first_non_empty_string(
      payload.get("team_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("team_phase"),
    ) or self._resolve_pagertree_team_phase(
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

def _normalize_alertops_incident_phase(
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
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_alertops_ownership_phase(
  owner: str | None,
  existing_phase: str,
) -> str:
  if owner:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_alertops_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_alertops_service_phase(
  service: str | None,
  existing_phase: str,
) -> str:
  if service:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_alertops_workflow_phase(
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
  if workflow_state in {"triggered", "open", "in_progress", "investigating", "monitoring", "escalated"}:
    return "incident_active"
  return "idle"

def _build_alertops_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  incident_status: str,
  priority: str | None,
  owner: str | None,
  service: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentAlertOpsRecoveryState,
) -> OperatorIncidentAlertOpsRecoveryPhaseGraph:
  incident_phase = self._first_non_empty_string(
    payload.get("incident_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
  ) or self._normalize_alertops_incident_phase(
    incident_status,
    existing.phase_graph.incident_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_alertops_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=incident_status,
  )
  return OperatorIncidentAlertOpsRecoveryPhaseGraph(
    incident_phase=incident_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_alertops_ownership_phase(
      owner,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_alertops_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    service_phase=self._first_non_empty_string(
      payload.get("service_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("service_phase"),
    ) or self._resolve_alertops_service_phase(
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

def _normalize_signl4_alert_phase(
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
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_signl4_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_signl4_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_signl4_team_phase(
  team: str | None,
  existing_phase: str,
) -> str:
  if team:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_signl4_workflow_phase(
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
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "in_progress", "investigating", "monitoring", "escalated"}:
    return "alert_active"
  return "idle"

def _build_signl4_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  team: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentSignl4RecoveryState,
) -> OperatorIncidentSignl4RecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_signl4_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_signl4_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentSignl4RecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_signl4_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_signl4_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    team_phase=self._first_non_empty_string(
      payload.get("team_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("team_phase"),
    ) or self._resolve_signl4_team_phase(
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

def _normalize_ilert_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_ilert_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_ilert_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_ilert_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_ilert_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_ilert_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentIlertRecoveryState,
) -> OperatorIncidentIlertRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_ilert_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_ilert_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentIlertRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_ilert_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_ilert_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_ilert_escalation_phase(
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

def _normalize_betterstack_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_betterstack_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_betterstack_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_betterstack_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_betterstack_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_betterstack_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentBetterstackRecoveryState,
) -> OperatorIncidentBetterstackRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_betterstack_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_betterstack_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentBetterstackRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_betterstack_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_betterstack_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_betterstack_escalation_phase(
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

def _normalize_onpage_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_onpage_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_onpage_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_onpage_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_onpage_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_onpage_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentOnpageRecoveryState,
) -> OperatorIncidentOnpageRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_onpage_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_onpage_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentOnpageRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_onpage_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_onpage_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_onpage_escalation_phase(
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

def _normalize_allquiet_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_allquiet_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_allquiet_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_allquiet_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_allquiet_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_allquiet_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentAllquietRecoveryState,
) -> OperatorIncidentAllquietRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_allquiet_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_allquiet_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentAllquietRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_allquiet_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_allquiet_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_allquiet_escalation_phase(
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

def _normalize_moogsoft_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_moogsoft_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_moogsoft_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_moogsoft_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_moogsoft_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_moogsoft_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentMoogsoftRecoveryState,
) -> OperatorIncidentMoogsoftRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_moogsoft_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_moogsoft_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentMoogsoftRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_moogsoft_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_moogsoft_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_moogsoft_escalation_phase(
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

def _normalize_spikesh_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_spikesh_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_spikesh_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_spikesh_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_spikesh_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_spikesh_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentSpikeshRecoveryState,
) -> OperatorIncidentSpikeshRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_spikesh_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_spikesh_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentSpikeshRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_spikesh_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_spikesh_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_spikesh_escalation_phase(
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

def _normalize_dutycalls_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_dutycalls_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_dutycalls_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_dutycalls_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_dutycalls_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_dutycalls_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentDutyCallsRecoveryState,
) -> OperatorIncidentDutyCallsRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_dutycalls_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_dutycalls_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentDutyCallsRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_dutycalls_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_dutycalls_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_dutycalls_escalation_phase(
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

def _normalize_incidenthub_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_incidenthub_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_incidenthub_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_incidenthub_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_incidenthub_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_incidenthub_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentIncidentHubRecoveryState,
) -> OperatorIncidentIncidentHubRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_incidenthub_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_incidenthub_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentIncidentHubRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_incidenthub_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_incidenthub_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_incidenthub_escalation_phase(
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

def _normalize_resolver_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_resolver_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_resolver_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_resolver_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_resolver_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_resolver_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentResolverRecoveryState,
) -> OperatorIncidentResolverRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_resolver_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_resolver_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentResolverRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_resolver_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_resolver_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_resolver_escalation_phase(
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

def _normalize_openduty_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_openduty_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_openduty_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_openduty_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_openduty_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_openduty_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentOpenDutyRecoveryState,
) -> OperatorIncidentOpenDutyRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_openduty_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_openduty_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentOpenDutyRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_openduty_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_openduty_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_openduty_escalation_phase(
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

def _normalize_cabot_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_cabot_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_cabot_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_cabot_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_cabot_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_cabot_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentCabotRecoveryState,
) -> OperatorIncidentCabotRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_cabot_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_cabot_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentCabotRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_cabot_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_cabot_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_cabot_escalation_phase(
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

def _normalize_haloitsm_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_haloitsm_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_haloitsm_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_haloitsm_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_haloitsm_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_haloitsm_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentHaloItsmRecoveryState,
) -> OperatorIncidentHaloItsmRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_haloitsm_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_haloitsm_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentHaloItsmRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_haloitsm_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_haloitsm_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_haloitsm_escalation_phase(
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

def _normalize_incidentmanagerio_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_incidentmanagerio_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_incidentmanagerio_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_incidentmanagerio_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_incidentmanagerio_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_incidentmanagerio_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentIncidentManagerIoRecoveryState,
) -> OperatorIncidentIncidentManagerIoRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_incidentmanagerio_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_incidentmanagerio_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentIncidentManagerIoRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_incidentmanagerio_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_incidentmanagerio_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_incidentmanagerio_escalation_phase(
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

def _normalize_oneuptime_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_oneuptime_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_oneuptime_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_oneuptime_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_oneuptime_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_oneuptime_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentOneUptimeRecoveryState,
) -> OperatorIncidentOneUptimeRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_oneuptime_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_oneuptime_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentOneUptimeRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_oneuptime_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_oneuptime_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_oneuptime_escalation_phase(
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

def _normalize_squzy_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_squzy_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_squzy_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_squzy_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_squzy_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_squzy_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentSquzyRecoveryState,
) -> OperatorIncidentSquzyRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_squzy_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_squzy_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentSquzyRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_squzy_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_squzy_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_squzy_escalation_phase(
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

def _normalize_crisescontrol_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_crisescontrol_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_crisescontrol_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_crisescontrol_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_crisescontrol_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_crisescontrol_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentCrisesControlRecoveryState,
) -> OperatorIncidentCrisesControlRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_crisescontrol_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_crisescontrol_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentCrisesControlRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_crisescontrol_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_crisescontrol_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_crisescontrol_escalation_phase(
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

def _normalize_freshservice_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_freshservice_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_freshservice_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_freshservice_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_freshservice_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_freshservice_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentFreshserviceRecoveryState,
) -> OperatorIncidentFreshserviceRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_freshservice_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_freshservice_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentFreshserviceRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_freshservice_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_freshservice_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_freshservice_escalation_phase(
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

def _normalize_freshdesk_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_freshdesk_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_freshdesk_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_freshdesk_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_freshdesk_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_freshdesk_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentFreshdeskRecoveryState,
) -> OperatorIncidentFreshdeskRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_freshdesk_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_freshdesk_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentFreshdeskRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_freshdesk_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_freshdesk_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_freshdesk_escalation_phase(
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

def _normalize_happyfox_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  return _normalize_freshdesk_alert_phase(status, existing_phase)

def _resolve_happyfox_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_ownership_phase(assignee, existing_phase)

def _resolve_happyfox_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_priority_phase(priority, existing_phase)

def _resolve_happyfox_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_escalation_phase(
    escalation_policy,
    existing_phase,
  )

def _resolve_happyfox_workflow_phase(
  *,
  lifecycle_state: str | None,
  workflow_state: str,
) -> str:
  return _resolve_freshdesk_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=workflow_state,
  )

def _build_happyfox_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentHappyfoxRecoveryState,
) -> OperatorIncidentHappyfoxRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_happyfox_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_happyfox_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentHappyfoxRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_happyfox_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_happyfox_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_happyfox_escalation_phase(
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

def _normalize_zendesk_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  return _normalize_freshdesk_alert_phase(status, existing_phase)

def _resolve_zendesk_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_ownership_phase(assignee, existing_phase)

def _resolve_zendesk_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_priority_phase(priority, existing_phase)

def _resolve_zendesk_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_escalation_phase(
    escalation_policy,
    existing_phase,
  )

def _resolve_zendesk_workflow_phase(
  *,
  lifecycle_state: str | None,
  workflow_state: str,
) -> str:
  return _resolve_freshdesk_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=workflow_state,
  )

def _build_zendesk_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentZendeskRecoveryState,
) -> OperatorIncidentZendeskRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_zendesk_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_zendesk_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentZendeskRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_zendesk_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_zendesk_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_zendesk_escalation_phase(
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

def _normalize_zohodesk_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  return _normalize_freshdesk_alert_phase(status, existing_phase)

def _resolve_zohodesk_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_ownership_phase(assignee, existing_phase)

def _resolve_zohodesk_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_priority_phase(priority, existing_phase)

def _resolve_zohodesk_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_escalation_phase(
    escalation_policy,
    existing_phase,
  )

def _resolve_zohodesk_workflow_phase(
  *,
  lifecycle_state: str | None,
  workflow_state: str,
) -> str:
  return _resolve_freshdesk_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=workflow_state,
  )

def _build_zohodesk_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentZohoDeskRecoveryState,
) -> OperatorIncidentZohoDeskRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_zohodesk_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_zohodesk_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentZohoDeskRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_zohodesk_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_zohodesk_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_zohodesk_escalation_phase(
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

def _normalize_helpscout_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  return _normalize_freshdesk_alert_phase(status, existing_phase)

def _resolve_helpscout_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_ownership_phase(assignee, existing_phase)

def _resolve_helpscout_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_priority_phase(priority, existing_phase)

def _resolve_helpscout_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_escalation_phase(
    escalation_policy,
    existing_phase,
  )

def _resolve_helpscout_workflow_phase(
  *,
  lifecycle_state: str | None,
  workflow_state: str,
) -> str:
  return _resolve_freshdesk_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=workflow_state,
  )

def _build_helpscout_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentHelpScoutRecoveryState,
) -> OperatorIncidentHelpScoutRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_helpscout_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_helpscout_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentHelpScoutRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_helpscout_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_helpscout_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_helpscout_escalation_phase(
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

def _normalize_kayako_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  return _normalize_freshdesk_alert_phase(status, existing_phase)

def _resolve_kayako_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_ownership_phase(assignee, existing_phase)

def _resolve_kayako_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_priority_phase(priority, existing_phase)

def _resolve_kayako_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_escalation_phase(
    escalation_policy,
    existing_phase,
  )

def _resolve_kayako_workflow_phase(
  *,
  lifecycle_state: str | None,
  workflow_state: str,
) -> str:
  return _resolve_freshdesk_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=workflow_state,
  )

def _build_kayako_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentKayakoRecoveryState,
) -> OperatorIncidentKayakoRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_kayako_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_kayako_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentKayakoRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_kayako_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_kayako_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_kayako_escalation_phase(
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

def _normalize_intercom_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  return _normalize_freshdesk_alert_phase(status, existing_phase)

def _resolve_intercom_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_ownership_phase(assignee, existing_phase)

def _resolve_intercom_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_priority_phase(priority, existing_phase)

def _resolve_intercom_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_escalation_phase(
    escalation_policy,
    existing_phase,
  )

def _resolve_intercom_workflow_phase(
  *,
  lifecycle_state: str | None,
  workflow_state: str,
) -> str:
  return _resolve_freshdesk_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=workflow_state,
  )

def _build_intercom_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentIntercomRecoveryState,
) -> OperatorIncidentIntercomRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_intercom_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_intercom_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentIntercomRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_intercom_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_intercom_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_intercom_escalation_phase(
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

def _normalize_front_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  return _normalize_freshdesk_alert_phase(status, existing_phase)

def _resolve_front_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_ownership_phase(assignee, existing_phase)

def _resolve_front_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_priority_phase(priority, existing_phase)

def _resolve_front_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  return _resolve_freshdesk_escalation_phase(
    escalation_policy,
    existing_phase,
  )

def _resolve_front_workflow_phase(
  *,
  lifecycle_state: str | None,
  workflow_state: str,
) -> str:
  return _resolve_freshdesk_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=workflow_state,
  )

def _build_front_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentFrontRecoveryState,
) -> OperatorIncidentFrontRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_front_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_front_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentFrontRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_front_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_front_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_front_escalation_phase(
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

def _normalize_servicedeskplus_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_servicedeskplus_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_servicedeskplus_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_servicedeskplus_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_servicedeskplus_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_servicedeskplus_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentServiceDeskPlusRecoveryState,
) -> OperatorIncidentServiceDeskPlusRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_servicedeskplus_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_servicedeskplus_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentServiceDeskPlusRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_servicedeskplus_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_servicedeskplus_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_servicedeskplus_escalation_phase(
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

def _normalize_sysaid_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_sysaid_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_sysaid_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_sysaid_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_sysaid_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_sysaid_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentSysAidRecoveryState,
) -> OperatorIncidentSysAidRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_sysaid_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_sysaid_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentSysAidRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_sysaid_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_sysaid_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_sysaid_escalation_phase(
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

def _normalize_bmchelix_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_bmchelix_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_bmchelix_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_bmchelix_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_bmchelix_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_bmchelix_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentBmcHelixRecoveryState,
) -> OperatorIncidentBmcHelixRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_bmchelix_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_bmchelix_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentBmcHelixRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_bmchelix_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_bmchelix_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_bmchelix_escalation_phase(
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

def _normalize_solarwindsservicedesk_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_solarwindsservicedesk_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_solarwindsservicedesk_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_solarwindsservicedesk_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_solarwindsservicedesk_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_solarwindsservicedesk_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentSolarWindsServiceDeskRecoveryState,
) -> OperatorIncidentSolarWindsServiceDeskRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_solarwindsservicedesk_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_solarwindsservicedesk_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentSolarWindsServiceDeskRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_solarwindsservicedesk_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_solarwindsservicedesk_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_solarwindsservicedesk_escalation_phase(
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

def _normalize_topdesk_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_topdesk_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_topdesk_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_topdesk_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_topdesk_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_topdesk_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentTopdeskRecoveryState,
) -> OperatorIncidentTopdeskRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_topdesk_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_topdesk_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentTopdeskRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_topdesk_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_topdesk_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_topdesk_escalation_phase(
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

def _normalize_invgateservicedesk_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_invgateservicedesk_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_invgateservicedesk_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_invgateservicedesk_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_invgateservicedesk_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_invgateservicedesk_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentInvGateServiceDeskRecoveryState,
) -> OperatorIncidentInvGateServiceDeskRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_invgateservicedesk_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_invgateservicedesk_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentInvGateServiceDeskRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_invgateservicedesk_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_invgateservicedesk_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_invgateservicedesk_escalation_phase(
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

def _normalize_opsramp_alert_phase(
  status: str | None,
  existing_phase: str,
) -> str:
  normalized = (status or "").strip().lower().replace(" ", "_")
  if normalized in {
    "triggered",
    "open",
    "pending",
    "accepted",
    "acknowledged",
    "in_progress",
    "resolved",
    "closed",
    "escalated",
  }:
    return normalized
  return existing_phase or "unknown"

def _resolve_opsramp_ownership_phase(
  assignee: str | None,
  existing_phase: str,
) -> str:
  if assignee:
    return "assigned"
  return existing_phase or "unassigned"

def _resolve_opsramp_priority_phase(
  priority: str | None,
  existing_phase: str,
) -> str:
  normalized = (priority or "").strip().lower().replace(" ", "_")
  if normalized:
    return normalized
  return existing_phase or "unknown"

def _resolve_opsramp_escalation_phase(
  escalation_policy: str | None,
  existing_phase: str,
) -> str:
  if escalation_policy:
    return "configured"
  return existing_phase or "unconfigured"

def _resolve_opsramp_workflow_phase(
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
  if workflow_state in {"accepted", "acknowledged"}:
    return "alert_acknowledged"
  if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
    return "alert_active"
  return "idle"

def _build_opsramp_recovery_phase_graph(
  self,
  *,
  payload: dict[str, Any],
  alert_status: str,
  priority: str | None,
  escalation_policy: str | None,
  assignee: str | None,
  lifecycle_state: str | None,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  existing: OperatorIncidentOpsRampRecoveryState,
) -> OperatorIncidentOpsRampRecoveryPhaseGraph:
  alert_phase = self._first_non_empty_string(
    payload.get("alert_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
  ) or self._normalize_opsramp_alert_phase(
    alert_status,
    existing.phase_graph.alert_phase,
  )
  workflow_phase = self._first_non_empty_string(
    payload.get("workflow_phase"),
    self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
  ) or self._resolve_opsramp_workflow_phase(
    lifecycle_state=lifecycle_state,
    workflow_state=alert_status,
  )
  return OperatorIncidentOpsRampRecoveryPhaseGraph(
    alert_phase=alert_phase,
    workflow_phase=workflow_phase,
    ownership_phase=self._first_non_empty_string(
      payload.get("ownership_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
    ) or self._resolve_opsramp_ownership_phase(
      assignee,
      existing.phase_graph.ownership_phase,
    ),
    priority_phase=self._first_non_empty_string(
      payload.get("priority_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
    ) or self._resolve_opsramp_priority_phase(
      priority,
      existing.phase_graph.priority_phase,
    ),
    escalation_phase=self._first_non_empty_string(
      payload.get("escalation_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
    ) or self._resolve_opsramp_escalation_phase(
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

