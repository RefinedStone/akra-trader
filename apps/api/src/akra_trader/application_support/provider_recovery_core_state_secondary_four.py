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

def _build_provider_recovery_state_secondary_group_four(
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
  zohodesk_schema = existing.zohodesk
  zohodesk_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("zohodesk"),
    payload.get("zohodesk"),
    payload.get("zohodesk_alert"),
    payload.get("zohodesk_ticket"),
  )
  if normalized_provider == "zohodesk" or zohodesk_payload:
    zohodesk_status = self._first_non_empty_string(
      zohodesk_payload.get("alert_status"),
      zohodesk_payload.get("status"),
      zohodesk_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.zohodesk.alert_status,
    ) or "unknown"
    zohodesk_schema = OperatorIncidentZohoDeskRecoveryState(
      alert_id=self._first_non_empty_string(
        zohodesk_payload.get("alert_id"),
        zohodesk_payload.get("id"),
        zohodesk_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.zohodesk.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        zohodesk_payload.get("external_reference"),
        zohodesk_payload.get("reference"),
        reference,
        existing.zohodesk.external_reference,
      ),
      alert_status=zohodesk_status,
      priority=self._first_non_empty_string(
        zohodesk_payload.get("priority"),
        zohodesk_payload.get("severity"),
        zohodesk_payload.get("urgency"),
        existing.zohodesk.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        zohodesk_payload.get("escalation_policy"),
        zohodesk_payload.get("escalationPolicy"),
        zohodesk_payload.get("policy"),
        zohodesk_payload.get("source"),
        existing.zohodesk.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        zohodesk_payload.get("assignee"),
        zohodesk_payload.get("owner"),
        zohodesk_payload.get("assigned_to"),
        existing.zohodesk.assignee,
      ),
      url=self._first_non_empty_string(
        zohodesk_payload.get("url"),
        zohodesk_payload.get("html_url"),
        zohodesk_payload.get("link"),
        existing.zohodesk.url,
      ),
      updated_at=(
        self._parse_payload_datetime(zohodesk_payload.get("updated_at"))
        or existing.zohodesk.updated_at
      ),
      phase_graph=self._build_zohodesk_recovery_phase_graph(
        payload=zohodesk_payload,
        alert_status=zohodesk_status,
        priority=self._first_non_empty_string(
          zohodesk_payload.get("priority"),
          zohodesk_payload.get("severity"),
          zohodesk_payload.get("urgency"),
          existing.zohodesk.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          zohodesk_payload.get("escalation_policy"),
          zohodesk_payload.get("escalationPolicy"),
          zohodesk_payload.get("policy"),
          zohodesk_payload.get("source"),
          existing.zohodesk.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          zohodesk_payload.get("assignee"),
          zohodesk_payload.get("owner"),
          zohodesk_payload.get("assigned_to"),
          existing.zohodesk.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.zohodesk,
      ),
    )
    provider_schema_kind = "zohodesk"
  helpscout_schema = existing.helpscout
  helpscout_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("helpscout"),
    payload.get("helpscout"),
    payload.get("helpscout_alert"),
    payload.get("helpscout_conversation"),
  )
  if normalized_provider == "helpscout" or helpscout_payload:
    helpscout_status = self._first_non_empty_string(
      helpscout_payload.get("alert_status"),
      helpscout_payload.get("status"),
      helpscout_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.helpscout.alert_status,
    ) or "unknown"
    helpscout_schema = OperatorIncidentHelpScoutRecoveryState(
      alert_id=self._first_non_empty_string(
        helpscout_payload.get("alert_id"),
        helpscout_payload.get("id"),
        helpscout_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.helpscout.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        helpscout_payload.get("external_reference"),
        helpscout_payload.get("reference"),
        reference,
        existing.helpscout.external_reference,
      ),
      alert_status=helpscout_status,
      priority=self._first_non_empty_string(
        helpscout_payload.get("priority"),
        helpscout_payload.get("severity"),
        helpscout_payload.get("urgency"),
        existing.helpscout.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        helpscout_payload.get("escalation_policy"),
        helpscout_payload.get("escalationPolicy"),
        helpscout_payload.get("policy"),
        helpscout_payload.get("source"),
        existing.helpscout.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        helpscout_payload.get("assignee"),
        helpscout_payload.get("owner"),
        helpscout_payload.get("assigned_to"),
        existing.helpscout.assignee,
      ),
      url=self._first_non_empty_string(
        helpscout_payload.get("url"),
        helpscout_payload.get("html_url"),
        helpscout_payload.get("link"),
        existing.helpscout.url,
      ),
      updated_at=(
        self._parse_payload_datetime(helpscout_payload.get("updated_at"))
        or existing.helpscout.updated_at
      ),
      phase_graph=self._build_helpscout_recovery_phase_graph(
        payload=helpscout_payload,
        alert_status=helpscout_status,
        priority=self._first_non_empty_string(
          helpscout_payload.get("priority"),
          helpscout_payload.get("severity"),
          helpscout_payload.get("urgency"),
          existing.helpscout.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          helpscout_payload.get("escalation_policy"),
          helpscout_payload.get("escalationPolicy"),
          helpscout_payload.get("policy"),
          helpscout_payload.get("source"),
          existing.helpscout.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          helpscout_payload.get("assignee"),
          helpscout_payload.get("owner"),
          helpscout_payload.get("assigned_to"),
          existing.helpscout.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.helpscout,
      ),
    )
    provider_schema_kind = "helpscout"
  kayako_schema = existing.kayako
  kayako_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("kayako"),
    payload.get("kayako"),
    payload.get("kayako_alert"),
    payload.get("kayako_case"),
  )
  if normalized_provider == "kayako" or kayako_payload:
    kayako_status = self._first_non_empty_string(
      kayako_payload.get("alert_status"),
      kayako_payload.get("status"),
      kayako_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.kayako.alert_status,
    ) or "unknown"
    kayako_schema = OperatorIncidentKayakoRecoveryState(
      alert_id=self._first_non_empty_string(
        kayako_payload.get("alert_id"),
        kayako_payload.get("id"),
        kayako_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.kayako.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        kayako_payload.get("external_reference"),
        kayako_payload.get("reference"),
        reference,
        existing.kayako.external_reference,
      ),
      alert_status=kayako_status,
      priority=self._first_non_empty_string(
        kayako_payload.get("priority"),
        kayako_payload.get("severity"),
        kayako_payload.get("urgency"),
        existing.kayako.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        kayako_payload.get("escalation_policy"),
        kayako_payload.get("escalationPolicy"),
        kayako_payload.get("policy"),
        kayako_payload.get("source"),
        existing.kayako.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        kayako_payload.get("assignee"),
        kayako_payload.get("owner"),
        kayako_payload.get("assigned_to"),
        existing.kayako.assignee,
      ),
      url=self._first_non_empty_string(
        kayako_payload.get("url"),
        kayako_payload.get("html_url"),
        kayako_payload.get("link"),
        existing.kayako.url,
      ),
      updated_at=(
        self._parse_payload_datetime(kayako_payload.get("updated_at"))
        or existing.kayako.updated_at
      ),
      phase_graph=self._build_kayako_recovery_phase_graph(
        payload=kayako_payload,
        alert_status=kayako_status,
        priority=self._first_non_empty_string(
          kayako_payload.get("priority"),
          kayako_payload.get("severity"),
          kayako_payload.get("urgency"),
          existing.kayako.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          kayako_payload.get("escalation_policy"),
          kayako_payload.get("escalationPolicy"),
          kayako_payload.get("policy"),
          kayako_payload.get("source"),
          existing.kayako.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          kayako_payload.get("assignee"),
          kayako_payload.get("owner"),
          kayako_payload.get("assigned_to"),
          existing.kayako.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.kayako,
      ),
    )
    provider_schema_kind = "kayako"
  intercom_schema = existing.intercom
  intercom_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("intercom"),
    payload.get("intercom"),
    payload.get("intercom_alert"),
    payload.get("intercom_conversation"),
  )
  if normalized_provider == "intercom" or intercom_payload:
    intercom_status = self._first_non_empty_string(
      intercom_payload.get("alert_status"),
      intercom_payload.get("status"),
      intercom_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.intercom.alert_status,
    ) or "unknown"
    intercom_schema = OperatorIncidentIntercomRecoveryState(
      alert_id=self._first_non_empty_string(
        intercom_payload.get("alert_id"),
        intercom_payload.get("id"),
        intercom_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.intercom.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        intercom_payload.get("external_reference"),
        intercom_payload.get("reference"),
        reference,
        existing.intercom.external_reference,
      ),
      alert_status=intercom_status,
      priority=self._first_non_empty_string(
        intercom_payload.get("priority"),
        intercom_payload.get("severity"),
        intercom_payload.get("urgency"),
        existing.intercom.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        intercom_payload.get("escalation_policy"),
        intercom_payload.get("escalationPolicy"),
        intercom_payload.get("policy"),
        intercom_payload.get("source"),
        existing.intercom.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        intercom_payload.get("assignee"),
        intercom_payload.get("owner"),
        intercom_payload.get("assigned_to"),
        existing.intercom.assignee,
      ),
      url=self._first_non_empty_string(
        intercom_payload.get("url"),
        intercom_payload.get("html_url"),
        intercom_payload.get("link"),
        existing.intercom.url,
      ),
      updated_at=(
        self._parse_payload_datetime(intercom_payload.get("updated_at"))
        or existing.intercom.updated_at
      ),
      phase_graph=self._build_intercom_recovery_phase_graph(
        payload=intercom_payload,
        alert_status=intercom_status,
        priority=self._first_non_empty_string(
          intercom_payload.get("priority"),
          intercom_payload.get("severity"),
          intercom_payload.get("urgency"),
          existing.intercom.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          intercom_payload.get("escalation_policy"),
          intercom_payload.get("escalationPolicy"),
          intercom_payload.get("policy"),
          intercom_payload.get("source"),
          existing.intercom.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          intercom_payload.get("assignee"),
          intercom_payload.get("owner"),
          intercom_payload.get("assigned_to"),
          existing.intercom.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.intercom,
      ),
    )
    provider_schema_kind = "intercom"
  front_schema = existing.front
  front_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("front"),
    payload.get("front"),
    payload.get("front_alert"),
    payload.get("front_conversation"),
  )
  if normalized_provider == "front" or front_payload:
    front_status = self._first_non_empty_string(
      front_payload.get("alert_status"),
      front_payload.get("status"),
      front_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.front.alert_status,
    ) or "unknown"
    front_schema = OperatorIncidentFrontRecoveryState(
      alert_id=self._first_non_empty_string(
        front_payload.get("alert_id"),
        front_payload.get("id"),
        front_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.front.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        front_payload.get("external_reference"),
        front_payload.get("reference"),
        reference,
        existing.front.external_reference,
      ),
      alert_status=front_status,
      priority=self._first_non_empty_string(
        front_payload.get("priority"),
        front_payload.get("severity"),
        front_payload.get("urgency"),
        existing.front.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        front_payload.get("escalation_policy"),
        front_payload.get("escalationPolicy"),
        front_payload.get("policy"),
        front_payload.get("source"),
        existing.front.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        front_payload.get("assignee"),
        front_payload.get("owner"),
        front_payload.get("assigned_to"),
        existing.front.assignee,
      ),
      url=self._first_non_empty_string(
        front_payload.get("url"),
        front_payload.get("html_url"),
        front_payload.get("link"),
        existing.front.url,
      ),
      updated_at=(
        self._parse_payload_datetime(front_payload.get("updated_at"))
        or existing.front.updated_at
      ),
      phase_graph=self._build_front_recovery_phase_graph(
        payload=front_payload,
        alert_status=front_status,
        priority=self._first_non_empty_string(
          front_payload.get("priority"),
          front_payload.get("severity"),
          front_payload.get("urgency"),
          existing.front.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          front_payload.get("escalation_policy"),
          front_payload.get("escalationPolicy"),
          front_payload.get("policy"),
          front_payload.get("source"),
          existing.front.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          front_payload.get("assignee"),
          front_payload.get("owner"),
          front_payload.get("assigned_to"),
          existing.front.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.front,
      ),
    )
    provider_schema_kind = "front"
  servicedeskplus_schema = existing.servicedeskplus
  servicedeskplus_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("servicedeskplus"),
    payload.get("servicedeskplus"),
    payload.get("servicedeskplus_alert"),
  )
  if normalized_provider == "servicedeskplus" or servicedeskplus_payload:
    servicedeskplus_status = self._first_non_empty_string(
      servicedeskplus_payload.get("alert_status"),
      servicedeskplus_payload.get("status"),
      servicedeskplus_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.servicedeskplus.alert_status,
    ) or "unknown"
    servicedeskplus_schema = OperatorIncidentServiceDeskPlusRecoveryState(
      alert_id=self._first_non_empty_string(
        servicedeskplus_payload.get("alert_id"),
        servicedeskplus_payload.get("id"),
        servicedeskplus_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.servicedeskplus.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        servicedeskplus_payload.get("external_reference"),
        servicedeskplus_payload.get("reference"),
        reference,
        existing.servicedeskplus.external_reference,
      ),
      alert_status=servicedeskplus_status,
      priority=self._first_non_empty_string(
        servicedeskplus_payload.get("priority"),
        servicedeskplus_payload.get("severity"),
        servicedeskplus_payload.get("urgency"),
        existing.servicedeskplus.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        servicedeskplus_payload.get("escalation_policy"),
        servicedeskplus_payload.get("escalationPolicy"),
        servicedeskplus_payload.get("policy"),
        servicedeskplus_payload.get("source"),
        existing.servicedeskplus.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        servicedeskplus_payload.get("assignee"),
        servicedeskplus_payload.get("owner"),
        servicedeskplus_payload.get("assigned_to"),
        existing.servicedeskplus.assignee,
      ),
      url=self._first_non_empty_string(
        servicedeskplus_payload.get("url"),
        servicedeskplus_payload.get("html_url"),
        servicedeskplus_payload.get("link"),
        existing.servicedeskplus.url,
      ),
      updated_at=(
        self._parse_payload_datetime(servicedeskplus_payload.get("updated_at"))
        or existing.servicedeskplus.updated_at
      ),
      phase_graph=self._build_servicedeskplus_recovery_phase_graph(
        payload=servicedeskplus_payload,
        alert_status=servicedeskplus_status,
        priority=self._first_non_empty_string(
          servicedeskplus_payload.get("priority"),
          servicedeskplus_payload.get("severity"),
          servicedeskplus_payload.get("urgency"),
          existing.servicedeskplus.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          servicedeskplus_payload.get("escalation_policy"),
          servicedeskplus_payload.get("escalationPolicy"),
          servicedeskplus_payload.get("policy"),
          servicedeskplus_payload.get("source"),
          existing.servicedeskplus.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          servicedeskplus_payload.get("assignee"),
          servicedeskplus_payload.get("owner"),
          servicedeskplus_payload.get("assigned_to"),
          existing.servicedeskplus.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.servicedeskplus,
      ),
    )
    provider_schema_kind = "servicedeskplus"
  sysaid_schema = existing.sysaid
  sysaid_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("sysaid"),
    payload.get("sysaid"),
    payload.get("sysaid_alert"),
  )
  if normalized_provider == "sysaid" or sysaid_payload:
    sysaid_status = self._first_non_empty_string(
      sysaid_payload.get("alert_status"),
      sysaid_payload.get("status"),
      sysaid_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.sysaid.alert_status,
    ) or "unknown"
    sysaid_schema = OperatorIncidentSysAidRecoveryState(
      alert_id=self._first_non_empty_string(
        sysaid_payload.get("alert_id"),
        sysaid_payload.get("id"),
        sysaid_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.sysaid.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        sysaid_payload.get("external_reference"),
        sysaid_payload.get("reference"),
        reference,
        existing.sysaid.external_reference,
      ),
      alert_status=sysaid_status,
      priority=self._first_non_empty_string(
        sysaid_payload.get("priority"),
        sysaid_payload.get("severity"),
        sysaid_payload.get("urgency"),
        existing.sysaid.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        sysaid_payload.get("escalation_policy"),
        sysaid_payload.get("escalationPolicy"),
        sysaid_payload.get("policy"),
        sysaid_payload.get("source"),
        existing.sysaid.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        sysaid_payload.get("assignee"),
        sysaid_payload.get("owner"),
        sysaid_payload.get("assigned_to"),
        existing.sysaid.assignee,
      ),
      url=self._first_non_empty_string(
        sysaid_payload.get("url"),
        sysaid_payload.get("html_url"),
        sysaid_payload.get("link"),
        existing.sysaid.url,
      ),
      updated_at=(
        self._parse_payload_datetime(sysaid_payload.get("updated_at"))
        or existing.sysaid.updated_at
      ),
      phase_graph=self._build_sysaid_recovery_phase_graph(
        payload=sysaid_payload,
        alert_status=sysaid_status,
        priority=self._first_non_empty_string(
          sysaid_payload.get("priority"),
          sysaid_payload.get("severity"),
          sysaid_payload.get("urgency"),
          existing.sysaid.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          sysaid_payload.get("escalation_policy"),
          sysaid_payload.get("escalationPolicy"),
          sysaid_payload.get("policy"),
          sysaid_payload.get("source"),
          existing.sysaid.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          sysaid_payload.get("assignee"),
          sysaid_payload.get("owner"),
          sysaid_payload.get("assigned_to"),
          existing.sysaid.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.sysaid,
      ),
    )
    provider_schema_kind = "sysaid"
  return (
    provider_schema_kind,
    zohodesk_schema,
    helpscout_schema,
    kayako_schema,
    intercom_schema,
    front_schema,
    servicedeskplus_schema,
    sysaid_schema,
  )
