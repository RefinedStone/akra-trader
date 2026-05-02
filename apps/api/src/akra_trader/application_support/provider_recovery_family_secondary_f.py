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
  "_normalize_intercom_alert_phase",
  "_resolve_intercom_ownership_phase",
  "_resolve_intercom_priority_phase",
  "_resolve_intercom_escalation_phase",
  "_resolve_intercom_workflow_phase",
  "_build_intercom_recovery_phase_graph",
  "_normalize_front_alert_phase",
  "_resolve_front_ownership_phase",
  "_resolve_front_priority_phase",
  "_resolve_front_escalation_phase",
  "_resolve_front_workflow_phase",
  "_build_front_recovery_phase_graph",
  "_normalize_servicedeskplus_alert_phase",
  "_resolve_servicedeskplus_ownership_phase",
  "_resolve_servicedeskplus_priority_phase",
  "_resolve_servicedeskplus_escalation_phase",
  "_resolve_servicedeskplus_workflow_phase",
  "_build_servicedeskplus_recovery_phase_graph",
  "_normalize_sysaid_alert_phase",
  "_resolve_sysaid_ownership_phase",
  "_resolve_sysaid_priority_phase",
  "_resolve_sysaid_escalation_phase",
  "_resolve_sysaid_workflow_phase",
  "_build_sysaid_recovery_phase_graph",
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
