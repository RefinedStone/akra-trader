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

__all__ = (
  "_normalize_bmchelix_alert_phase",
  "_resolve_bmchelix_ownership_phase",
  "_resolve_bmchelix_priority_phase",
  "_resolve_bmchelix_escalation_phase",
  "_resolve_bmchelix_workflow_phase",
  "_build_bmchelix_recovery_phase_graph",
  "_normalize_solarwindsservicedesk_alert_phase",
  "_resolve_solarwindsservicedesk_ownership_phase",
  "_resolve_solarwindsservicedesk_priority_phase",
  "_resolve_solarwindsservicedesk_escalation_phase",
  "_resolve_solarwindsservicedesk_workflow_phase",
  "_build_solarwindsservicedesk_recovery_phase_graph",
  "_normalize_topdesk_alert_phase",
  "_resolve_topdesk_ownership_phase",
  "_resolve_topdesk_priority_phase",
  "_resolve_topdesk_escalation_phase",
  "_resolve_topdesk_workflow_phase",
  "_build_topdesk_recovery_phase_graph",
  "_normalize_invgateservicedesk_alert_phase",
  "_resolve_invgateservicedesk_ownership_phase",
  "_resolve_invgateservicedesk_priority_phase",
  "_resolve_invgateservicedesk_escalation_phase",
  "_resolve_invgateservicedesk_workflow_phase",
  "_build_invgateservicedesk_recovery_phase_graph",
  "_normalize_opsramp_alert_phase",
  "_resolve_opsramp_ownership_phase",
  "_resolve_opsramp_priority_phase",
  "_resolve_opsramp_escalation_phase",
  "_resolve_opsramp_workflow_phase",
  "_build_opsramp_recovery_phase_graph",
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
