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

def _build_provider_recovery_state_secondary_group_five(
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
  bmchelix_schema = existing.bmchelix
  bmchelix_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("bmchelix"),
    payload.get("bmchelix"),
    payload.get("bmchelix_alert"),
  )
  if normalized_provider == "bmchelix" or bmchelix_payload:
    bmchelix_status = self._first_non_empty_string(
      bmchelix_payload.get("alert_status"),
      bmchelix_payload.get("status"),
      bmchelix_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.bmchelix.alert_status,
    ) or "unknown"
    bmchelix_schema = OperatorIncidentBmcHelixRecoveryState(
      alert_id=self._first_non_empty_string(
        bmchelix_payload.get("alert_id"),
        bmchelix_payload.get("id"),
        bmchelix_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.bmchelix.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        bmchelix_payload.get("external_reference"),
        bmchelix_payload.get("reference"),
        reference,
        existing.bmchelix.external_reference,
      ),
      alert_status=bmchelix_status,
      priority=self._first_non_empty_string(
        bmchelix_payload.get("priority"),
        bmchelix_payload.get("severity"),
        bmchelix_payload.get("urgency"),
        existing.bmchelix.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        bmchelix_payload.get("escalation_policy"),
        bmchelix_payload.get("escalationPolicy"),
        bmchelix_payload.get("policy"),
        bmchelix_payload.get("source"),
        existing.bmchelix.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        bmchelix_payload.get("assignee"),
        bmchelix_payload.get("owner"),
        bmchelix_payload.get("assigned_to"),
        existing.bmchelix.assignee,
      ),
      url=self._first_non_empty_string(
        bmchelix_payload.get("url"),
        bmchelix_payload.get("html_url"),
        bmchelix_payload.get("link"),
        existing.bmchelix.url,
      ),
      updated_at=(
        self._parse_payload_datetime(bmchelix_payload.get("updated_at"))
        or existing.bmchelix.updated_at
      ),
      phase_graph=self._build_bmchelix_recovery_phase_graph(
        payload=bmchelix_payload,
        alert_status=bmchelix_status,
        priority=self._first_non_empty_string(
          bmchelix_payload.get("priority"),
          bmchelix_payload.get("severity"),
          bmchelix_payload.get("urgency"),
          existing.bmchelix.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          bmchelix_payload.get("escalation_policy"),
          bmchelix_payload.get("escalationPolicy"),
          bmchelix_payload.get("policy"),
          bmchelix_payload.get("source"),
          existing.bmchelix.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          bmchelix_payload.get("assignee"),
          bmchelix_payload.get("owner"),
          bmchelix_payload.get("assigned_to"),
          existing.bmchelix.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.bmchelix,
      ),
    )
    provider_schema_kind = "bmchelix"
  solarwindsservicedesk_schema = existing.solarwindsservicedesk
  solarwindsservicedesk_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("solarwindsservicedesk"),
    payload.get("solarwindsservicedesk"),
    payload.get("solarwindsservicedesk_alert"),
  )
  if normalized_provider == "solarwindsservicedesk" or solarwindsservicedesk_payload:
    solarwindsservicedesk_status = self._first_non_empty_string(
      solarwindsservicedesk_payload.get("alert_status"),
      solarwindsservicedesk_payload.get("status"),
      solarwindsservicedesk_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.solarwindsservicedesk.alert_status,
    ) or "unknown"
    solarwindsservicedesk_schema = OperatorIncidentSolarWindsServiceDeskRecoveryState(
      alert_id=self._first_non_empty_string(
        solarwindsservicedesk_payload.get("alert_id"),
        solarwindsservicedesk_payload.get("id"),
        solarwindsservicedesk_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.solarwindsservicedesk.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        solarwindsservicedesk_payload.get("external_reference"),
        solarwindsservicedesk_payload.get("reference"),
        reference,
        existing.solarwindsservicedesk.external_reference,
      ),
      alert_status=solarwindsservicedesk_status,
      priority=self._first_non_empty_string(
        solarwindsservicedesk_payload.get("priority"),
        solarwindsservicedesk_payload.get("severity"),
        solarwindsservicedesk_payload.get("urgency"),
        existing.solarwindsservicedesk.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        solarwindsservicedesk_payload.get("escalation_policy"),
        solarwindsservicedesk_payload.get("escalationPolicy"),
        solarwindsservicedesk_payload.get("policy"),
        solarwindsservicedesk_payload.get("source"),
        existing.solarwindsservicedesk.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        solarwindsservicedesk_payload.get("assignee"),
        solarwindsservicedesk_payload.get("owner"),
        solarwindsservicedesk_payload.get("assigned_to"),
        existing.solarwindsservicedesk.assignee,
      ),
      url=self._first_non_empty_string(
        solarwindsservicedesk_payload.get("url"),
        solarwindsservicedesk_payload.get("html_url"),
        solarwindsservicedesk_payload.get("link"),
        existing.solarwindsservicedesk.url,
      ),
      updated_at=(
        self._parse_payload_datetime(solarwindsservicedesk_payload.get("updated_at"))
        or existing.solarwindsservicedesk.updated_at
      ),
      phase_graph=self._build_solarwindsservicedesk_recovery_phase_graph(
        payload=solarwindsservicedesk_payload,
        alert_status=solarwindsservicedesk_status,
        priority=self._first_non_empty_string(
          solarwindsservicedesk_payload.get("priority"),
          solarwindsservicedesk_payload.get("severity"),
          solarwindsservicedesk_payload.get("urgency"),
          existing.solarwindsservicedesk.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          solarwindsservicedesk_payload.get("escalation_policy"),
          solarwindsservicedesk_payload.get("escalationPolicy"),
          solarwindsservicedesk_payload.get("policy"),
          solarwindsservicedesk_payload.get("source"),
          existing.solarwindsservicedesk.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          solarwindsservicedesk_payload.get("assignee"),
          solarwindsservicedesk_payload.get("owner"),
          solarwindsservicedesk_payload.get("assigned_to"),
          existing.solarwindsservicedesk.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.solarwindsservicedesk,
      ),
    )
    provider_schema_kind = "solarwindsservicedesk"
  topdesk_schema = existing.topdesk
  topdesk_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("topdesk"),
    payload.get("topdesk"),
    payload.get("topdesk_alert"),
  )
  if normalized_provider == "topdesk" or topdesk_payload:
    topdesk_status = self._first_non_empty_string(
      topdesk_payload.get("alert_status"),
      topdesk_payload.get("status"),
      topdesk_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.topdesk.alert_status,
    ) or "unknown"
    topdesk_schema = OperatorIncidentTopdeskRecoveryState(
      alert_id=self._first_non_empty_string(
        topdesk_payload.get("alert_id"),
        topdesk_payload.get("id"),
        topdesk_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.topdesk.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        topdesk_payload.get("external_reference"),
        topdesk_payload.get("reference"),
        reference,
        existing.topdesk.external_reference,
      ),
      alert_status=topdesk_status,
      priority=self._first_non_empty_string(
        topdesk_payload.get("priority"),
        topdesk_payload.get("severity"),
        topdesk_payload.get("urgency"),
        existing.topdesk.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        topdesk_payload.get("escalation_policy"),
        topdesk_payload.get("escalationPolicy"),
        topdesk_payload.get("policy"),
        topdesk_payload.get("source"),
        existing.topdesk.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        topdesk_payload.get("assignee"),
        topdesk_payload.get("owner"),
        topdesk_payload.get("assigned_to"),
        existing.topdesk.assignee,
      ),
      url=self._first_non_empty_string(
        topdesk_payload.get("url"),
        topdesk_payload.get("html_url"),
        topdesk_payload.get("link"),
        existing.topdesk.url,
      ),
      updated_at=(
        self._parse_payload_datetime(topdesk_payload.get("updated_at"))
        or existing.topdesk.updated_at
      ),
      phase_graph=self._build_topdesk_recovery_phase_graph(
        payload=topdesk_payload,
        alert_status=topdesk_status,
        priority=self._first_non_empty_string(
          topdesk_payload.get("priority"),
          topdesk_payload.get("severity"),
          topdesk_payload.get("urgency"),
          existing.topdesk.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          topdesk_payload.get("escalation_policy"),
          topdesk_payload.get("escalationPolicy"),
          topdesk_payload.get("policy"),
          topdesk_payload.get("source"),
          existing.topdesk.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          topdesk_payload.get("assignee"),
          topdesk_payload.get("owner"),
          topdesk_payload.get("assigned_to"),
          existing.topdesk.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.topdesk,
      ),
    )
    provider_schema_kind = "topdesk"
  invgateservicedesk_schema = existing.invgateservicedesk
  invgateservicedesk_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("invgateservicedesk"),
    payload.get("invgateservicedesk"),
    payload.get("invgateservicedesk_alert"),
  )
  if normalized_provider == "invgateservicedesk" or invgateservicedesk_payload:
    invgateservicedesk_status = self._first_non_empty_string(
      invgateservicedesk_payload.get("alert_status"),
      invgateservicedesk_payload.get("status"),
      invgateservicedesk_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.invgateservicedesk.alert_status,
    ) or "unknown"
    invgateservicedesk_schema = OperatorIncidentInvGateServiceDeskRecoveryState(
      alert_id=self._first_non_empty_string(
        invgateservicedesk_payload.get("alert_id"),
        invgateservicedesk_payload.get("id"),
        invgateservicedesk_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.invgateservicedesk.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        invgateservicedesk_payload.get("external_reference"),
        invgateservicedesk_payload.get("reference"),
        reference,
        existing.invgateservicedesk.external_reference,
      ),
      alert_status=invgateservicedesk_status,
      priority=self._first_non_empty_string(
        invgateservicedesk_payload.get("priority"),
        invgateservicedesk_payload.get("severity"),
        invgateservicedesk_payload.get("urgency"),
        existing.invgateservicedesk.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        invgateservicedesk_payload.get("escalation_policy"),
        invgateservicedesk_payload.get("escalationPolicy"),
        invgateservicedesk_payload.get("policy"),
        invgateservicedesk_payload.get("source"),
        existing.invgateservicedesk.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        invgateservicedesk_payload.get("assignee"),
        invgateservicedesk_payload.get("owner"),
        invgateservicedesk_payload.get("assigned_to"),
        existing.invgateservicedesk.assignee,
      ),
      url=self._first_non_empty_string(
        invgateservicedesk_payload.get("url"),
        invgateservicedesk_payload.get("html_url"),
        invgateservicedesk_payload.get("link"),
        existing.invgateservicedesk.url,
      ),
      updated_at=(
        self._parse_payload_datetime(invgateservicedesk_payload.get("updated_at"))
        or existing.invgateservicedesk.updated_at
      ),
      phase_graph=self._build_invgateservicedesk_recovery_phase_graph(
        payload=invgateservicedesk_payload,
        alert_status=invgateservicedesk_status,
        priority=self._first_non_empty_string(
          invgateservicedesk_payload.get("priority"),
          invgateservicedesk_payload.get("severity"),
          invgateservicedesk_payload.get("urgency"),
          existing.invgateservicedesk.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          invgateservicedesk_payload.get("escalation_policy"),
          invgateservicedesk_payload.get("escalationPolicy"),
          invgateservicedesk_payload.get("policy"),
          invgateservicedesk_payload.get("source"),
          existing.invgateservicedesk.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          invgateservicedesk_payload.get("assignee"),
          invgateservicedesk_payload.get("owner"),
          invgateservicedesk_payload.get("assigned_to"),
          existing.invgateservicedesk.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.invgateservicedesk,
      ),
    )
    provider_schema_kind = "invgateservicedesk"
  opsramp_schema = existing.opsramp
  opsramp_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("opsramp"),
    payload.get("opsramp"),
    payload.get("opsramp_alert"),
  )
  if normalized_provider == "opsramp" or opsramp_payload:
    opsramp_status = self._first_non_empty_string(
      opsramp_payload.get("alert_status"),
      opsramp_payload.get("status"),
      opsramp_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.opsramp.alert_status,
    ) or "unknown"
    opsramp_schema = OperatorIncidentOpsRampRecoveryState(
      alert_id=self._first_non_empty_string(
        opsramp_payload.get("alert_id"),
        opsramp_payload.get("id"),
        opsramp_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.opsramp.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        opsramp_payload.get("external_reference"),
        opsramp_payload.get("reference"),
        reference,
        existing.opsramp.external_reference,
      ),
      alert_status=opsramp_status,
      priority=self._first_non_empty_string(
        opsramp_payload.get("priority"),
        opsramp_payload.get("severity"),
        opsramp_payload.get("urgency"),
        existing.opsramp.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        opsramp_payload.get("escalation_policy"),
        opsramp_payload.get("escalationPolicy"),
        opsramp_payload.get("policy"),
        opsramp_payload.get("source"),
        existing.opsramp.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        opsramp_payload.get("assignee"),
        opsramp_payload.get("owner"),
        opsramp_payload.get("assigned_to"),
        existing.opsramp.assignee,
      ),
      url=self._first_non_empty_string(
        opsramp_payload.get("url"),
        opsramp_payload.get("html_url"),
        opsramp_payload.get("link"),
        existing.opsramp.url,
      ),
      updated_at=(
        self._parse_payload_datetime(opsramp_payload.get("updated_at"))
        or existing.opsramp.updated_at
      ),
      phase_graph=self._build_opsramp_recovery_phase_graph(
        payload=opsramp_payload,
        alert_status=opsramp_status,
        priority=self._first_non_empty_string(
          opsramp_payload.get("priority"),
          opsramp_payload.get("severity"),
          opsramp_payload.get("urgency"),
          existing.opsramp.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          opsramp_payload.get("escalation_policy"),
          opsramp_payload.get("escalationPolicy"),
          opsramp_payload.get("policy"),
          opsramp_payload.get("source"),
          existing.opsramp.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          opsramp_payload.get("assignee"),
          opsramp_payload.get("owner"),
          opsramp_payload.get("assigned_to"),
          existing.opsramp.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.opsramp,
      ),
    )
    provider_schema_kind = "opsramp"
  return (
    provider_schema_kind,
    bmchelix_schema,
    solarwindsservicedesk_schema,
    topdesk_schema,
    invgateservicedesk_schema,
    opsramp_schema,
  )
