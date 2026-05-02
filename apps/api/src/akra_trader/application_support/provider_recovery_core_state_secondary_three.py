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

def _build_provider_recovery_state_secondary_group_three(
  self,
  *,
  existing: OperatorIncidentProviderRecoveryState,
  payload: dict[str, Any],
  normalized_provider: str,
  lifecycle_state: str,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  provider_schema_kind: str | None,
  workflow_reference: str | None,
  reference: str | None,
) -> tuple[Any, ...]:
  squzy_schema = existing.squzy
  squzy_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("squzy"),
    payload.get("squzy"),
    payload.get("squzy_alert"),
  )
  if normalized_provider == "squzy" or squzy_payload:
    squzy_status = self._first_non_empty_string(
      squzy_payload.get("alert_status"),
      squzy_payload.get("status"),
      squzy_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.squzy.alert_status,
    ) or "unknown"
    squzy_schema = OperatorIncidentSquzyRecoveryState(
      alert_id=self._first_non_empty_string(
        squzy_payload.get("alert_id"),
        squzy_payload.get("id"),
        squzy_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.squzy.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        squzy_payload.get("external_reference"),
        squzy_payload.get("reference"),
        reference,
        existing.squzy.external_reference,
      ),
      alert_status=squzy_status,
      priority=self._first_non_empty_string(
        squzy_payload.get("priority"),
        squzy_payload.get("severity"),
        squzy_payload.get("urgency"),
        existing.squzy.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        squzy_payload.get("escalation_policy"),
        squzy_payload.get("escalationPolicy"),
        squzy_payload.get("policy"),
        squzy_payload.get("source"),
        existing.squzy.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        squzy_payload.get("assignee"),
        squzy_payload.get("owner"),
        squzy_payload.get("assigned_to"),
        existing.squzy.assignee,
      ),
      url=self._first_non_empty_string(
        squzy_payload.get("url"),
        squzy_payload.get("html_url"),
        squzy_payload.get("link"),
        existing.squzy.url,
      ),
      updated_at=(
        self._parse_payload_datetime(squzy_payload.get("updated_at"))
        or existing.squzy.updated_at
      ),
      phase_graph=self._build_squzy_recovery_phase_graph(
        payload=squzy_payload,
        alert_status=squzy_status,
        priority=self._first_non_empty_string(
          squzy_payload.get("priority"),
          squzy_payload.get("severity"),
          squzy_payload.get("urgency"),
          existing.squzy.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          squzy_payload.get("escalation_policy"),
          squzy_payload.get("escalationPolicy"),
          squzy_payload.get("policy"),
          squzy_payload.get("source"),
          existing.squzy.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          squzy_payload.get("assignee"),
          squzy_payload.get("owner"),
          squzy_payload.get("assigned_to"),
          existing.squzy.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.squzy,
      ),
    )
    provider_schema_kind = "squzy"
  crisescontrol_schema = existing.crisescontrol
  crisescontrol_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("crisescontrol"),
    payload.get("crisescontrol"),
    payload.get("crisescontrol_alert"),
  )
  if normalized_provider == "crisescontrol" or crisescontrol_payload:
    crisescontrol_status = self._first_non_empty_string(
      crisescontrol_payload.get("alert_status"),
      crisescontrol_payload.get("status"),
      crisescontrol_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.crisescontrol.alert_status,
    ) or "unknown"
    crisescontrol_schema = OperatorIncidentCrisesControlRecoveryState(
      alert_id=self._first_non_empty_string(
        crisescontrol_payload.get("alert_id"),
        crisescontrol_payload.get("id"),
        crisescontrol_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.crisescontrol.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        crisescontrol_payload.get("external_reference"),
        crisescontrol_payload.get("reference"),
        reference,
        existing.crisescontrol.external_reference,
      ),
      alert_status=crisescontrol_status,
      priority=self._first_non_empty_string(
        crisescontrol_payload.get("priority"),
        crisescontrol_payload.get("severity"),
        crisescontrol_payload.get("urgency"),
        existing.crisescontrol.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        crisescontrol_payload.get("escalation_policy"),
        crisescontrol_payload.get("escalationPolicy"),
        crisescontrol_payload.get("policy"),
        crisescontrol_payload.get("source"),
        existing.crisescontrol.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        crisescontrol_payload.get("assignee"),
        crisescontrol_payload.get("owner"),
        crisescontrol_payload.get("assigned_to"),
        existing.crisescontrol.assignee,
      ),
      url=self._first_non_empty_string(
        crisescontrol_payload.get("url"),
        crisescontrol_payload.get("html_url"),
        crisescontrol_payload.get("link"),
        existing.crisescontrol.url,
      ),
      updated_at=(
        self._parse_payload_datetime(crisescontrol_payload.get("updated_at"))
        or existing.crisescontrol.updated_at
      ),
      phase_graph=self._build_crisescontrol_recovery_phase_graph(
        payload=crisescontrol_payload,
        alert_status=crisescontrol_status,
        priority=self._first_non_empty_string(
          crisescontrol_payload.get("priority"),
          crisescontrol_payload.get("severity"),
          crisescontrol_payload.get("urgency"),
          existing.crisescontrol.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          crisescontrol_payload.get("escalation_policy"),
          crisescontrol_payload.get("escalationPolicy"),
          crisescontrol_payload.get("policy"),
          crisescontrol_payload.get("source"),
          existing.crisescontrol.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          crisescontrol_payload.get("assignee"),
          crisescontrol_payload.get("owner"),
          crisescontrol_payload.get("assigned_to"),
          existing.crisescontrol.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.crisescontrol,
      ),
    )
    provider_schema_kind = "crisescontrol"
  freshservice_schema = existing.freshservice
  freshservice_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("freshservice"),
    payload.get("freshservice"),
    payload.get("freshservice_alert"),
  )
  if normalized_provider == "freshservice" or freshservice_payload:
    freshservice_status = self._first_non_empty_string(
      freshservice_payload.get("alert_status"),
      freshservice_payload.get("status"),
      freshservice_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.freshservice.alert_status,
    ) or "unknown"
    freshservice_schema = OperatorIncidentFreshserviceRecoveryState(
      alert_id=self._first_non_empty_string(
        freshservice_payload.get("alert_id"),
        freshservice_payload.get("id"),
        freshservice_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.freshservice.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        freshservice_payload.get("external_reference"),
        freshservice_payload.get("reference"),
        reference,
        existing.freshservice.external_reference,
      ),
      alert_status=freshservice_status,
      priority=self._first_non_empty_string(
        freshservice_payload.get("priority"),
        freshservice_payload.get("severity"),
        freshservice_payload.get("urgency"),
        existing.freshservice.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        freshservice_payload.get("escalation_policy"),
        freshservice_payload.get("escalationPolicy"),
        freshservice_payload.get("policy"),
        freshservice_payload.get("source"),
        existing.freshservice.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        freshservice_payload.get("assignee"),
        freshservice_payload.get("owner"),
        freshservice_payload.get("assigned_to"),
        existing.freshservice.assignee,
      ),
      url=self._first_non_empty_string(
        freshservice_payload.get("url"),
        freshservice_payload.get("html_url"),
        freshservice_payload.get("link"),
        existing.freshservice.url,
      ),
      updated_at=(
        self._parse_payload_datetime(freshservice_payload.get("updated_at"))
        or existing.freshservice.updated_at
      ),
      phase_graph=self._build_freshservice_recovery_phase_graph(
        payload=freshservice_payload,
        alert_status=freshservice_status,
        priority=self._first_non_empty_string(
          freshservice_payload.get("priority"),
          freshservice_payload.get("severity"),
          freshservice_payload.get("urgency"),
          existing.freshservice.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          freshservice_payload.get("escalation_policy"),
          freshservice_payload.get("escalationPolicy"),
          freshservice_payload.get("policy"),
          freshservice_payload.get("source"),
          existing.freshservice.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          freshservice_payload.get("assignee"),
          freshservice_payload.get("owner"),
          freshservice_payload.get("assigned_to"),
          existing.freshservice.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.freshservice,
      ),
    )
    provider_schema_kind = "freshservice"
  freshdesk_schema = existing.freshdesk
  freshdesk_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("freshdesk"),
    payload.get("freshdesk"),
    payload.get("freshdesk_alert"),
  )
  if normalized_provider == "freshdesk" or freshdesk_payload:
    freshdesk_status = self._first_non_empty_string(
      freshdesk_payload.get("alert_status"),
      freshdesk_payload.get("status"),
      freshdesk_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.freshdesk.alert_status,
    ) or "unknown"
    freshdesk_schema = OperatorIncidentFreshdeskRecoveryState(
      alert_id=self._first_non_empty_string(
        freshdesk_payload.get("alert_id"),
        freshdesk_payload.get("id"),
        freshdesk_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.freshdesk.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        freshdesk_payload.get("external_reference"),
        freshdesk_payload.get("reference"),
        reference,
        existing.freshdesk.external_reference,
      ),
      alert_status=freshdesk_status,
      priority=self._first_non_empty_string(
        freshdesk_payload.get("priority"),
        freshdesk_payload.get("severity"),
        freshdesk_payload.get("urgency"),
        existing.freshdesk.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        freshdesk_payload.get("escalation_policy"),
        freshdesk_payload.get("escalationPolicy"),
        freshdesk_payload.get("policy"),
        freshdesk_payload.get("source"),
        existing.freshdesk.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        freshdesk_payload.get("assignee"),
        freshdesk_payload.get("owner"),
        freshdesk_payload.get("assigned_to"),
        existing.freshdesk.assignee,
      ),
      url=self._first_non_empty_string(
        freshdesk_payload.get("url"),
        freshdesk_payload.get("html_url"),
        freshdesk_payload.get("link"),
        existing.freshdesk.url,
      ),
      updated_at=(
        self._parse_payload_datetime(freshdesk_payload.get("updated_at"))
        or existing.freshdesk.updated_at
      ),
      phase_graph=self._build_freshdesk_recovery_phase_graph(
        payload=freshdesk_payload,
        alert_status=freshdesk_status,
        priority=self._first_non_empty_string(
          freshdesk_payload.get("priority"),
          freshdesk_payload.get("severity"),
          freshdesk_payload.get("urgency"),
          existing.freshdesk.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          freshdesk_payload.get("escalation_policy"),
          freshdesk_payload.get("escalationPolicy"),
          freshdesk_payload.get("policy"),
          freshdesk_payload.get("source"),
          existing.freshdesk.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          freshdesk_payload.get("assignee"),
          freshdesk_payload.get("owner"),
          freshdesk_payload.get("assigned_to"),
          existing.freshdesk.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.freshdesk,
      ),
    )
    provider_schema_kind = "freshdesk"
  happyfox_schema = existing.happyfox
  happyfox_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("happyfox"),
    payload.get("happyfox"),
    payload.get("happyfox_alert"),
    payload.get("happyfox_ticket"),
  )
  if normalized_provider == "happyfox" or happyfox_payload:
    happyfox_status = self._first_non_empty_string(
      happyfox_payload.get("alert_status"),
      happyfox_payload.get("status"),
      happyfox_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.happyfox.alert_status,
    ) or "unknown"
    happyfox_schema = OperatorIncidentHappyfoxRecoveryState(
      alert_id=self._first_non_empty_string(
        happyfox_payload.get("alert_id"),
        happyfox_payload.get("id"),
        happyfox_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.happyfox.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        happyfox_payload.get("external_reference"),
        happyfox_payload.get("reference"),
        reference,
        existing.happyfox.external_reference,
      ),
      alert_status=happyfox_status,
      priority=self._first_non_empty_string(
        happyfox_payload.get("priority"),
        happyfox_payload.get("severity"),
        happyfox_payload.get("urgency"),
        existing.happyfox.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        happyfox_payload.get("escalation_policy"),
        happyfox_payload.get("escalationPolicy"),
        happyfox_payload.get("policy"),
        happyfox_payload.get("source"),
        existing.happyfox.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        happyfox_payload.get("assignee"),
        happyfox_payload.get("owner"),
        happyfox_payload.get("assigned_to"),
        existing.happyfox.assignee,
      ),
      url=self._first_non_empty_string(
        happyfox_payload.get("url"),
        happyfox_payload.get("html_url"),
        happyfox_payload.get("link"),
        existing.happyfox.url,
      ),
      updated_at=(
        self._parse_payload_datetime(happyfox_payload.get("updated_at"))
        or existing.happyfox.updated_at
      ),
      phase_graph=self._build_happyfox_recovery_phase_graph(
        payload=happyfox_payload,
        alert_status=happyfox_status,
        priority=self._first_non_empty_string(
          happyfox_payload.get("priority"),
          happyfox_payload.get("severity"),
          happyfox_payload.get("urgency"),
          existing.happyfox.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          happyfox_payload.get("escalation_policy"),
          happyfox_payload.get("escalationPolicy"),
          happyfox_payload.get("policy"),
          happyfox_payload.get("source"),
          existing.happyfox.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          happyfox_payload.get("assignee"),
          happyfox_payload.get("owner"),
          happyfox_payload.get("assigned_to"),
          existing.happyfox.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.happyfox,
      ),
    )
    provider_schema_kind = "happyfox"
  zendesk_schema = existing.zendesk
  zendesk_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("zendesk"),
    payload.get("zendesk"),
    payload.get("zendesk_alert"),
    payload.get("zendesk_ticket"),
  )
  if normalized_provider == "zendesk" or zendesk_payload:
    zendesk_status = self._first_non_empty_string(
      zendesk_payload.get("alert_status"),
      zendesk_payload.get("status"),
      zendesk_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.zendesk.alert_status,
    ) or "unknown"
    zendesk_schema = OperatorIncidentZendeskRecoveryState(
      alert_id=self._first_non_empty_string(
        zendesk_payload.get("alert_id"),
        zendesk_payload.get("id"),
        zendesk_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.zendesk.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        zendesk_payload.get("external_reference"),
        zendesk_payload.get("reference"),
        reference,
        existing.zendesk.external_reference,
      ),
      alert_status=zendesk_status,
      priority=self._first_non_empty_string(
        zendesk_payload.get("priority"),
        zendesk_payload.get("severity"),
        zendesk_payload.get("urgency"),
        existing.zendesk.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        zendesk_payload.get("escalation_policy"),
        zendesk_payload.get("escalationPolicy"),
        zendesk_payload.get("policy"),
        zendesk_payload.get("source"),
        existing.zendesk.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        zendesk_payload.get("assignee"),
        zendesk_payload.get("owner"),
        zendesk_payload.get("assigned_to"),
        existing.zendesk.assignee,
      ),
      url=self._first_non_empty_string(
        zendesk_payload.get("url"),
        zendesk_payload.get("html_url"),
        zendesk_payload.get("link"),
        existing.zendesk.url,
      ),
      updated_at=(
        self._parse_payload_datetime(zendesk_payload.get("updated_at"))
        or existing.zendesk.updated_at
      ),
      phase_graph=self._build_zendesk_recovery_phase_graph(
        payload=zendesk_payload,
        alert_status=zendesk_status,
        priority=self._first_non_empty_string(
          zendesk_payload.get("priority"),
          zendesk_payload.get("severity"),
          zendesk_payload.get("urgency"),
          existing.zendesk.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          zendesk_payload.get("escalation_policy"),
          zendesk_payload.get("escalationPolicy"),
          zendesk_payload.get("policy"),
          zendesk_payload.get("source"),
          existing.zendesk.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          zendesk_payload.get("assignee"),
          zendesk_payload.get("owner"),
          zendesk_payload.get("assigned_to"),
          existing.zendesk.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.zendesk,
      ),
    )
    provider_schema_kind = "zendesk"
  return (
    provider_schema_kind,
    squzy_schema,
    crisescontrol_schema,
    freshservice_schema,
    freshdesk_schema,
    happyfox_schema,
    zendesk_schema,
  )
