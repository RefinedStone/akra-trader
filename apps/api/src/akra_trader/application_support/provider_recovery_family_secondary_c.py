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
  "_normalize_openduty_alert_phase",
  "_resolve_openduty_ownership_phase",
  "_resolve_openduty_priority_phase",
  "_resolve_openduty_escalation_phase",
  "_resolve_openduty_workflow_phase",
  "_build_openduty_recovery_phase_graph",
  "_normalize_cabot_alert_phase",
  "_resolve_cabot_ownership_phase",
  "_resolve_cabot_priority_phase",
  "_resolve_cabot_escalation_phase",
  "_resolve_cabot_workflow_phase",
  "_build_cabot_recovery_phase_graph",
  "_normalize_haloitsm_alert_phase",
  "_resolve_haloitsm_ownership_phase",
  "_resolve_haloitsm_priority_phase",
  "_resolve_haloitsm_escalation_phase",
  "_resolve_haloitsm_workflow_phase",
  "_build_haloitsm_recovery_phase_graph",
  "_normalize_incidentmanagerio_alert_phase",
  "_resolve_incidentmanagerio_ownership_phase",
  "_resolve_incidentmanagerio_priority_phase",
  "_resolve_incidentmanagerio_escalation_phase",
  "_resolve_incidentmanagerio_workflow_phase",
  "_build_incidentmanagerio_recovery_phase_graph",
  "_normalize_oneuptime_alert_phase",
  "_resolve_oneuptime_ownership_phase",
  "_resolve_oneuptime_priority_phase",
  "_resolve_oneuptime_escalation_phase",
  "_resolve_oneuptime_workflow_phase",
  "_build_oneuptime_recovery_phase_graph",
  "_normalize_squzy_alert_phase",
  "_resolve_squzy_ownership_phase",
  "_resolve_squzy_priority_phase",
  "_resolve_squzy_escalation_phase",
  "_resolve_squzy_workflow_phase",
  "_build_squzy_recovery_phase_graph",
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
