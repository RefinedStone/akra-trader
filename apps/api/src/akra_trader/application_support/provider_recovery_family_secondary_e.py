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
  "_normalize_zendesk_alert_phase",
  "_resolve_zendesk_ownership_phase",
  "_resolve_zendesk_priority_phase",
  "_resolve_zendesk_escalation_phase",
  "_resolve_zendesk_workflow_phase",
  "_build_zendesk_recovery_phase_graph",
  "_normalize_zohodesk_alert_phase",
  "_resolve_zohodesk_ownership_phase",
  "_resolve_zohodesk_priority_phase",
  "_resolve_zohodesk_escalation_phase",
  "_resolve_zohodesk_workflow_phase",
  "_build_zohodesk_recovery_phase_graph",
  "_normalize_helpscout_alert_phase",
  "_resolve_helpscout_ownership_phase",
  "_resolve_helpscout_priority_phase",
  "_resolve_helpscout_escalation_phase",
  "_resolve_helpscout_workflow_phase",
  "_build_helpscout_recovery_phase_graph",
  "_normalize_kayako_alert_phase",
  "_resolve_kayako_ownership_phase",
  "_resolve_kayako_priority_phase",
  "_resolve_kayako_escalation_phase",
  "_resolve_kayako_workflow_phase",
  "_build_kayako_recovery_phase_graph",
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
