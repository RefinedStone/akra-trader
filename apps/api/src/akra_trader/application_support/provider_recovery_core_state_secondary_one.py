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

def _build_provider_recovery_state_secondary_group_one(
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
  betterstack_schema = existing.betterstack
  betterstack_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("betterstack"),
    self._extract_payload_mapping(payload.get("provider_schema")).get("better_stack"),
    payload.get("betterstack"),
    payload.get("betterstack_alert"),
    payload.get("better_stack"),
  )
  if normalized_provider == "betterstack" or betterstack_payload:
    betterstack_status = self._first_non_empty_string(
      betterstack_payload.get("alert_status"),
      betterstack_payload.get("status"),
      betterstack_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.betterstack.alert_status,
    ) or "unknown"
    betterstack_schema = OperatorIncidentBetterstackRecoveryState(
      alert_id=self._first_non_empty_string(
        betterstack_payload.get("alert_id"),
        betterstack_payload.get("id"),
        betterstack_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.betterstack.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        betterstack_payload.get("external_reference"),
        betterstack_payload.get("reference"),
        reference,
        existing.betterstack.external_reference,
      ),
      alert_status=betterstack_status,
      priority=self._first_non_empty_string(
        betterstack_payload.get("priority"),
        betterstack_payload.get("severity"),
        betterstack_payload.get("urgency"),
        existing.betterstack.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        betterstack_payload.get("escalation_policy"),
        betterstack_payload.get("escalationPolicy"),
        betterstack_payload.get("policy"),
        betterstack_payload.get("source"),
        existing.betterstack.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        betterstack_payload.get("assignee"),
        betterstack_payload.get("owner"),
        betterstack_payload.get("assigned_to"),
        existing.betterstack.assignee,
      ),
      url=self._first_non_empty_string(
        betterstack_payload.get("url"),
        betterstack_payload.get("html_url"),
        betterstack_payload.get("link"),
        existing.betterstack.url,
      ),
      updated_at=(
        self._parse_payload_datetime(betterstack_payload.get("updated_at"))
        or existing.betterstack.updated_at
      ),
      phase_graph=self._build_betterstack_recovery_phase_graph(
        payload=betterstack_payload,
        alert_status=betterstack_status,
        priority=self._first_non_empty_string(
          betterstack_payload.get("priority"),
          betterstack_payload.get("severity"),
          betterstack_payload.get("urgency"),
          existing.betterstack.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          betterstack_payload.get("escalation_policy"),
          betterstack_payload.get("escalationPolicy"),
          betterstack_payload.get("policy"),
          betterstack_payload.get("source"),
          existing.betterstack.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          betterstack_payload.get("assignee"),
          betterstack_payload.get("owner"),
          betterstack_payload.get("assigned_to"),
          existing.betterstack.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.betterstack,
      ),
    )
    provider_schema_kind = "betterstack"
  onpage_schema = existing.onpage
  onpage_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("onpage"),
    self._extract_payload_mapping(payload.get("provider_schema")).get("on_page"),
    payload.get("onpage"),
    payload.get("onpage_alert"),
    payload.get("on_page"),
  )
  if normalized_provider == "onpage" or onpage_payload:
    onpage_status = self._first_non_empty_string(
      onpage_payload.get("alert_status"),
      onpage_payload.get("status"),
      onpage_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.onpage.alert_status,
    ) or "unknown"
    onpage_schema = OperatorIncidentOnpageRecoveryState(
      alert_id=self._first_non_empty_string(
        onpage_payload.get("alert_id"),
        onpage_payload.get("id"),
        onpage_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.onpage.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        onpage_payload.get("external_reference"),
        onpage_payload.get("reference"),
        reference,
        existing.onpage.external_reference,
      ),
      alert_status=onpage_status,
      priority=self._first_non_empty_string(
        onpage_payload.get("priority"),
        onpage_payload.get("severity"),
        onpage_payload.get("urgency"),
        existing.onpage.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        onpage_payload.get("escalation_policy"),
        onpage_payload.get("escalationPolicy"),
        onpage_payload.get("policy"),
        onpage_payload.get("source"),
        existing.onpage.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        onpage_payload.get("assignee"),
        onpage_payload.get("owner"),
        onpage_payload.get("assigned_to"),
        existing.onpage.assignee,
      ),
      url=self._first_non_empty_string(
        onpage_payload.get("url"),
        onpage_payload.get("html_url"),
        onpage_payload.get("link"),
        existing.onpage.url,
      ),
      updated_at=(
        self._parse_payload_datetime(onpage_payload.get("updated_at"))
        or existing.onpage.updated_at
      ),
      phase_graph=self._build_onpage_recovery_phase_graph(
        payload=onpage_payload,
        alert_status=onpage_status,
        priority=self._first_non_empty_string(
          onpage_payload.get("priority"),
          onpage_payload.get("severity"),
          onpage_payload.get("urgency"),
          existing.onpage.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          onpage_payload.get("escalation_policy"),
          onpage_payload.get("escalationPolicy"),
          onpage_payload.get("policy"),
          onpage_payload.get("source"),
          existing.onpage.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          onpage_payload.get("assignee"),
          onpage_payload.get("owner"),
          onpage_payload.get("assigned_to"),
          existing.onpage.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.onpage,
      ),
    )
    provider_schema_kind = "onpage"
  allquiet_schema = existing.allquiet
  allquiet_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("allquiet"),
    self._extract_payload_mapping(payload.get("provider_schema")).get("all_quiet"),
    payload.get("allquiet"),
    payload.get("allquiet_alert"),
    payload.get("all_quiet"),
  )
  if normalized_provider == "allquiet" or allquiet_payload:
    allquiet_status = self._first_non_empty_string(
      allquiet_payload.get("alert_status"),
      allquiet_payload.get("status"),
      allquiet_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.allquiet.alert_status,
    ) or "unknown"
    allquiet_schema = OperatorIncidentAllquietRecoveryState(
      alert_id=self._first_non_empty_string(
        allquiet_payload.get("alert_id"),
        allquiet_payload.get("id"),
        allquiet_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.allquiet.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        allquiet_payload.get("external_reference"),
        allquiet_payload.get("reference"),
        reference,
        existing.allquiet.external_reference,
      ),
      alert_status=allquiet_status,
      priority=self._first_non_empty_string(
        allquiet_payload.get("priority"),
        allquiet_payload.get("severity"),
        allquiet_payload.get("urgency"),
        existing.allquiet.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        allquiet_payload.get("escalation_policy"),
        allquiet_payload.get("escalationPolicy"),
        allquiet_payload.get("policy"),
        allquiet_payload.get("source"),
        existing.allquiet.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        allquiet_payload.get("assignee"),
        allquiet_payload.get("owner"),
        allquiet_payload.get("assigned_to"),
        existing.allquiet.assignee,
      ),
      url=self._first_non_empty_string(
        allquiet_payload.get("url"),
        allquiet_payload.get("html_url"),
        allquiet_payload.get("link"),
        existing.allquiet.url,
      ),
      updated_at=(
        self._parse_payload_datetime(allquiet_payload.get("updated_at"))
        or existing.allquiet.updated_at
      ),
      phase_graph=self._build_allquiet_recovery_phase_graph(
        payload=allquiet_payload,
        alert_status=allquiet_status,
        priority=self._first_non_empty_string(
          allquiet_payload.get("priority"),
          allquiet_payload.get("severity"),
          allquiet_payload.get("urgency"),
          existing.allquiet.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          allquiet_payload.get("escalation_policy"),
          allquiet_payload.get("escalationPolicy"),
          allquiet_payload.get("policy"),
          allquiet_payload.get("source"),
          existing.allquiet.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          allquiet_payload.get("assignee"),
          allquiet_payload.get("owner"),
          allquiet_payload.get("assigned_to"),
          existing.allquiet.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.allquiet,
      ),
    )
    provider_schema_kind = "allquiet"
  moogsoft_schema = existing.moogsoft
  moogsoft_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("moogsoft"),
    payload.get("moogsoft"),
    payload.get("moogsoft_alert"),
  )
  if normalized_provider == "moogsoft" or moogsoft_payload:
    moogsoft_status = self._first_non_empty_string(
      moogsoft_payload.get("alert_status"),
      moogsoft_payload.get("status"),
      moogsoft_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.moogsoft.alert_status,
    ) or "unknown"
    moogsoft_schema = OperatorIncidentMoogsoftRecoveryState(
      alert_id=self._first_non_empty_string(
        moogsoft_payload.get("alert_id"),
        moogsoft_payload.get("id"),
        moogsoft_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.moogsoft.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        moogsoft_payload.get("external_reference"),
        moogsoft_payload.get("reference"),
        reference,
        existing.moogsoft.external_reference,
      ),
      alert_status=moogsoft_status,
      priority=self._first_non_empty_string(
        moogsoft_payload.get("priority"),
        moogsoft_payload.get("severity"),
        moogsoft_payload.get("urgency"),
        existing.moogsoft.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        moogsoft_payload.get("escalation_policy"),
        moogsoft_payload.get("escalationPolicy"),
        moogsoft_payload.get("policy"),
        moogsoft_payload.get("source"),
        existing.moogsoft.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        moogsoft_payload.get("assignee"),
        moogsoft_payload.get("owner"),
        moogsoft_payload.get("assigned_to"),
        existing.moogsoft.assignee,
      ),
      url=self._first_non_empty_string(
        moogsoft_payload.get("url"),
        moogsoft_payload.get("html_url"),
        moogsoft_payload.get("link"),
        existing.moogsoft.url,
      ),
      updated_at=(
        self._parse_payload_datetime(moogsoft_payload.get("updated_at"))
        or existing.moogsoft.updated_at
      ),
      phase_graph=self._build_moogsoft_recovery_phase_graph(
        payload=moogsoft_payload,
        alert_status=moogsoft_status,
        priority=self._first_non_empty_string(
          moogsoft_payload.get("priority"),
          moogsoft_payload.get("severity"),
          moogsoft_payload.get("urgency"),
          existing.moogsoft.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          moogsoft_payload.get("escalation_policy"),
          moogsoft_payload.get("escalationPolicy"),
          moogsoft_payload.get("policy"),
          moogsoft_payload.get("source"),
          existing.moogsoft.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          moogsoft_payload.get("assignee"),
          moogsoft_payload.get("owner"),
          moogsoft_payload.get("assigned_to"),
          existing.moogsoft.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.moogsoft,
      ),
    )
    provider_schema_kind = "moogsoft"
  spikesh_schema = existing.spikesh
  spikesh_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("spikesh"),
    payload.get("spikesh"),
    payload.get("spikesh_alert"),
  )
  if normalized_provider == "spikesh" or spikesh_payload:
    spikesh_status = self._first_non_empty_string(
      spikesh_payload.get("alert_status"),
      spikesh_payload.get("status"),
      spikesh_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.spikesh.alert_status,
    ) or "unknown"
    spikesh_schema = OperatorIncidentSpikeshRecoveryState(
      alert_id=self._first_non_empty_string(
        spikesh_payload.get("alert_id"),
        spikesh_payload.get("id"),
        spikesh_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.spikesh.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        spikesh_payload.get("external_reference"),
        spikesh_payload.get("reference"),
        reference,
        existing.spikesh.external_reference,
      ),
      alert_status=spikesh_status,
      priority=self._first_non_empty_string(
        spikesh_payload.get("priority"),
        spikesh_payload.get("severity"),
        spikesh_payload.get("urgency"),
        existing.spikesh.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        spikesh_payload.get("escalation_policy"),
        spikesh_payload.get("escalationPolicy"),
        spikesh_payload.get("policy"),
        spikesh_payload.get("source"),
        existing.spikesh.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        spikesh_payload.get("assignee"),
        spikesh_payload.get("owner"),
        spikesh_payload.get("assigned_to"),
        existing.spikesh.assignee,
      ),
      url=self._first_non_empty_string(
        spikesh_payload.get("url"),
        spikesh_payload.get("html_url"),
        spikesh_payload.get("link"),
        existing.spikesh.url,
      ),
      updated_at=(
        self._parse_payload_datetime(spikesh_payload.get("updated_at"))
        or existing.spikesh.updated_at
      ),
      phase_graph=self._build_spikesh_recovery_phase_graph(
        payload=spikesh_payload,
        alert_status=spikesh_status,
        priority=self._first_non_empty_string(
          spikesh_payload.get("priority"),
          spikesh_payload.get("severity"),
          spikesh_payload.get("urgency"),
          existing.spikesh.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          spikesh_payload.get("escalation_policy"),
          spikesh_payload.get("escalationPolicy"),
          spikesh_payload.get("policy"),
          spikesh_payload.get("source"),
          existing.spikesh.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          spikesh_payload.get("assignee"),
          spikesh_payload.get("owner"),
          spikesh_payload.get("assigned_to"),
          existing.spikesh.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.spikesh,
      ),
    )
    provider_schema_kind = "spikesh"
  dutycalls_schema = existing.dutycalls
  dutycalls_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("dutycalls"),
    payload.get("dutycalls"),
    payload.get("dutycalls_alert"),
  )
  if normalized_provider == "dutycalls" or dutycalls_payload:
    dutycalls_status = self._first_non_empty_string(
      dutycalls_payload.get("alert_status"),
      dutycalls_payload.get("status"),
      dutycalls_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.dutycalls.alert_status,
    ) or "unknown"
    dutycalls_schema = OperatorIncidentDutyCallsRecoveryState(
      alert_id=self._first_non_empty_string(
        dutycalls_payload.get("alert_id"),
        dutycalls_payload.get("id"),
        dutycalls_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.dutycalls.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        dutycalls_payload.get("external_reference"),
        dutycalls_payload.get("reference"),
        reference,
        existing.dutycalls.external_reference,
      ),
      alert_status=dutycalls_status,
      priority=self._first_non_empty_string(
        dutycalls_payload.get("priority"),
        dutycalls_payload.get("severity"),
        dutycalls_payload.get("urgency"),
        existing.dutycalls.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        dutycalls_payload.get("escalation_policy"),
        dutycalls_payload.get("escalationPolicy"),
        dutycalls_payload.get("policy"),
        dutycalls_payload.get("source"),
        existing.dutycalls.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        dutycalls_payload.get("assignee"),
        dutycalls_payload.get("owner"),
        dutycalls_payload.get("assigned_to"),
        existing.dutycalls.assignee,
      ),
      url=self._first_non_empty_string(
        dutycalls_payload.get("url"),
        dutycalls_payload.get("html_url"),
        dutycalls_payload.get("link"),
        existing.dutycalls.url,
      ),
      updated_at=(
        self._parse_payload_datetime(dutycalls_payload.get("updated_at"))
        or existing.dutycalls.updated_at
      ),
      phase_graph=self._build_dutycalls_recovery_phase_graph(
        payload=dutycalls_payload,
        alert_status=dutycalls_status,
        priority=self._first_non_empty_string(
          dutycalls_payload.get("priority"),
          dutycalls_payload.get("severity"),
          dutycalls_payload.get("urgency"),
          existing.dutycalls.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          dutycalls_payload.get("escalation_policy"),
          dutycalls_payload.get("escalationPolicy"),
          dutycalls_payload.get("policy"),
          dutycalls_payload.get("source"),
          existing.dutycalls.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          dutycalls_payload.get("assignee"),
          dutycalls_payload.get("owner"),
          dutycalls_payload.get("assigned_to"),
          existing.dutycalls.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.dutycalls,
      ),
    )
    provider_schema_kind = "dutycalls"
  incidenthub_schema = existing.incidenthub
  incidenthub_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("incidenthub"),
    payload.get("incidenthub"),
    payload.get("incidenthub_alert"),
  )
  if normalized_provider == "incidenthub" or incidenthub_payload:
    incidenthub_status = self._first_non_empty_string(
      incidenthub_payload.get("alert_status"),
      incidenthub_payload.get("status"),
      incidenthub_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.incidenthub.alert_status,
    ) or "unknown"
    incidenthub_schema = OperatorIncidentIncidentHubRecoveryState(
      alert_id=self._first_non_empty_string(
        incidenthub_payload.get("alert_id"),
        incidenthub_payload.get("id"),
        incidenthub_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.incidenthub.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        incidenthub_payload.get("external_reference"),
        incidenthub_payload.get("reference"),
        reference,
        existing.incidenthub.external_reference,
      ),
      alert_status=incidenthub_status,
      priority=self._first_non_empty_string(
        incidenthub_payload.get("priority"),
        incidenthub_payload.get("severity"),
        incidenthub_payload.get("urgency"),
        existing.incidenthub.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        incidenthub_payload.get("escalation_policy"),
        incidenthub_payload.get("escalationPolicy"),
        incidenthub_payload.get("policy"),
        incidenthub_payload.get("source"),
        existing.incidenthub.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        incidenthub_payload.get("assignee"),
        incidenthub_payload.get("owner"),
        incidenthub_payload.get("assigned_to"),
        existing.incidenthub.assignee,
      ),
      url=self._first_non_empty_string(
        incidenthub_payload.get("url"),
        incidenthub_payload.get("html_url"),
        incidenthub_payload.get("link"),
        existing.incidenthub.url,
      ),
      updated_at=(
        self._parse_payload_datetime(incidenthub_payload.get("updated_at"))
        or existing.incidenthub.updated_at
      ),
      phase_graph=self._build_incidenthub_recovery_phase_graph(
        payload=incidenthub_payload,
        alert_status=incidenthub_status,
        priority=self._first_non_empty_string(
          incidenthub_payload.get("priority"),
          incidenthub_payload.get("severity"),
          incidenthub_payload.get("urgency"),
          existing.incidenthub.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          incidenthub_payload.get("escalation_policy"),
          incidenthub_payload.get("escalationPolicy"),
          incidenthub_payload.get("policy"),
          incidenthub_payload.get("source"),
          existing.incidenthub.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          incidenthub_payload.get("assignee"),
          incidenthub_payload.get("owner"),
          incidenthub_payload.get("assigned_to"),
          existing.incidenthub.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.incidenthub,
      ),
    )
    provider_schema_kind = "incidenthub"
  return (
    provider_schema_kind,
    betterstack_schema,
    onpage_schema,
    allquiet_schema,
    moogsoft_schema,
    spikesh_schema,
    dutycalls_schema,
    incidenthub_schema,
  )
