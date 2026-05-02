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

def _build_provider_recovery_state_secondary_group_two(
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
  resolver_schema = existing.resolver
  resolver_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("resolver"),
    payload.get("resolver"),
    payload.get("resolver_alert"),
  )
  if normalized_provider == "resolver" or resolver_payload:
    resolver_status = self._first_non_empty_string(
      resolver_payload.get("alert_status"),
      resolver_payload.get("status"),
      resolver_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.resolver.alert_status,
    ) or "unknown"
    resolver_schema = OperatorIncidentResolverRecoveryState(
      alert_id=self._first_non_empty_string(
        resolver_payload.get("alert_id"),
        resolver_payload.get("id"),
        resolver_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.resolver.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        resolver_payload.get("external_reference"),
        resolver_payload.get("reference"),
        reference,
        existing.resolver.external_reference,
      ),
      alert_status=resolver_status,
      priority=self._first_non_empty_string(
        resolver_payload.get("priority"),
        resolver_payload.get("severity"),
        resolver_payload.get("urgency"),
        existing.resolver.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        resolver_payload.get("escalation_policy"),
        resolver_payload.get("escalationPolicy"),
        resolver_payload.get("policy"),
        resolver_payload.get("source"),
        existing.resolver.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        resolver_payload.get("assignee"),
        resolver_payload.get("owner"),
        resolver_payload.get("assigned_to"),
        existing.resolver.assignee,
      ),
      url=self._first_non_empty_string(
        resolver_payload.get("url"),
        resolver_payload.get("html_url"),
        resolver_payload.get("link"),
        existing.resolver.url,
      ),
      updated_at=(
        self._parse_payload_datetime(resolver_payload.get("updated_at"))
        or existing.resolver.updated_at
      ),
      phase_graph=self._build_resolver_recovery_phase_graph(
        payload=resolver_payload,
        alert_status=resolver_status,
        priority=self._first_non_empty_string(
          resolver_payload.get("priority"),
          resolver_payload.get("severity"),
          resolver_payload.get("urgency"),
          existing.resolver.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          resolver_payload.get("escalation_policy"),
          resolver_payload.get("escalationPolicy"),
          resolver_payload.get("policy"),
          resolver_payload.get("source"),
          existing.resolver.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          resolver_payload.get("assignee"),
          resolver_payload.get("owner"),
          resolver_payload.get("assigned_to"),
          existing.resolver.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.resolver,
      ),
    )
    provider_schema_kind = "resolver"
  openduty_schema = existing.openduty
  openduty_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("openduty"),
    payload.get("openduty"),
    payload.get("openduty_alert"),
  )
  if normalized_provider == "openduty" or openduty_payload:
    openduty_status = self._first_non_empty_string(
      openduty_payload.get("alert_status"),
      openduty_payload.get("status"),
      openduty_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.openduty.alert_status,
    ) or "unknown"
    openduty_schema = OperatorIncidentOpenDutyRecoveryState(
      alert_id=self._first_non_empty_string(
        openduty_payload.get("alert_id"),
        openduty_payload.get("id"),
        openduty_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.openduty.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        openduty_payload.get("external_reference"),
        openduty_payload.get("reference"),
        reference,
        existing.openduty.external_reference,
      ),
      alert_status=openduty_status,
      priority=self._first_non_empty_string(
        openduty_payload.get("priority"),
        openduty_payload.get("severity"),
        openduty_payload.get("urgency"),
        existing.openduty.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        openduty_payload.get("escalation_policy"),
        openduty_payload.get("escalationPolicy"),
        openduty_payload.get("policy"),
        openduty_payload.get("source"),
        existing.openduty.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        openduty_payload.get("assignee"),
        openduty_payload.get("owner"),
        openduty_payload.get("assigned_to"),
        existing.openduty.assignee,
      ),
      url=self._first_non_empty_string(
        openduty_payload.get("url"),
        openduty_payload.get("html_url"),
        openduty_payload.get("link"),
        existing.openduty.url,
      ),
      updated_at=(
        self._parse_payload_datetime(openduty_payload.get("updated_at"))
        or existing.openduty.updated_at
      ),
      phase_graph=self._build_openduty_recovery_phase_graph(
        payload=openduty_payload,
        alert_status=openduty_status,
        priority=self._first_non_empty_string(
          openduty_payload.get("priority"),
          openduty_payload.get("severity"),
          openduty_payload.get("urgency"),
          existing.openduty.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          openduty_payload.get("escalation_policy"),
          openduty_payload.get("escalationPolicy"),
          openduty_payload.get("policy"),
          openduty_payload.get("source"),
          existing.openduty.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          openduty_payload.get("assignee"),
          openduty_payload.get("owner"),
          openduty_payload.get("assigned_to"),
          existing.openduty.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.openduty,
      ),
    )
    provider_schema_kind = "openduty"
  cabot_schema = existing.cabot
  cabot_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("cabot"),
    payload.get("cabot"),
    payload.get("cabot_alert"),
  )
  if normalized_provider == "cabot" or cabot_payload:
    cabot_status = self._first_non_empty_string(
      cabot_payload.get("alert_status"),
      cabot_payload.get("status"),
      cabot_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.cabot.alert_status,
    ) or "unknown"
    cabot_schema = OperatorIncidentCabotRecoveryState(
      alert_id=self._first_non_empty_string(
        cabot_payload.get("alert_id"),
        cabot_payload.get("id"),
        cabot_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.cabot.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        cabot_payload.get("external_reference"),
        cabot_payload.get("reference"),
        reference,
        existing.cabot.external_reference,
      ),
      alert_status=cabot_status,
      priority=self._first_non_empty_string(
        cabot_payload.get("priority"),
        cabot_payload.get("severity"),
        cabot_payload.get("urgency"),
        existing.cabot.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        cabot_payload.get("escalation_policy"),
        cabot_payload.get("escalationPolicy"),
        cabot_payload.get("policy"),
        cabot_payload.get("source"),
        existing.cabot.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        cabot_payload.get("assignee"),
        cabot_payload.get("owner"),
        cabot_payload.get("assigned_to"),
        existing.cabot.assignee,
      ),
      url=self._first_non_empty_string(
        cabot_payload.get("url"),
        cabot_payload.get("html_url"),
        cabot_payload.get("link"),
        existing.cabot.url,
      ),
      updated_at=(
        self._parse_payload_datetime(cabot_payload.get("updated_at"))
        or existing.cabot.updated_at
      ),
      phase_graph=self._build_cabot_recovery_phase_graph(
        payload=cabot_payload,
        alert_status=cabot_status,
        priority=self._first_non_empty_string(
          cabot_payload.get("priority"),
          cabot_payload.get("severity"),
          cabot_payload.get("urgency"),
          existing.cabot.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          cabot_payload.get("escalation_policy"),
          cabot_payload.get("escalationPolicy"),
          cabot_payload.get("policy"),
          cabot_payload.get("source"),
          existing.cabot.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          cabot_payload.get("assignee"),
          cabot_payload.get("owner"),
          cabot_payload.get("assigned_to"),
          existing.cabot.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.cabot,
      ),
    )
    provider_schema_kind = "cabot"
  haloitsm_schema = existing.haloitsm
  haloitsm_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("haloitsm"),
    payload.get("haloitsm"),
    payload.get("haloitsm_alert"),
  )
  if normalized_provider == "haloitsm" or haloitsm_payload:
    haloitsm_status = self._first_non_empty_string(
      haloitsm_payload.get("alert_status"),
      haloitsm_payload.get("status"),
      haloitsm_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.haloitsm.alert_status,
    ) or "unknown"
    haloitsm_schema = OperatorIncidentHaloItsmRecoveryState(
      alert_id=self._first_non_empty_string(
        haloitsm_payload.get("alert_id"),
        haloitsm_payload.get("id"),
        haloitsm_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.haloitsm.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        haloitsm_payload.get("external_reference"),
        haloitsm_payload.get("reference"),
        reference,
        existing.haloitsm.external_reference,
      ),
      alert_status=haloitsm_status,
      priority=self._first_non_empty_string(
        haloitsm_payload.get("priority"),
        haloitsm_payload.get("severity"),
        haloitsm_payload.get("urgency"),
        existing.haloitsm.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        haloitsm_payload.get("escalation_policy"),
        haloitsm_payload.get("escalationPolicy"),
        haloitsm_payload.get("policy"),
        haloitsm_payload.get("source"),
        existing.haloitsm.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        haloitsm_payload.get("assignee"),
        haloitsm_payload.get("owner"),
        haloitsm_payload.get("assigned_to"),
        existing.haloitsm.assignee,
      ),
      url=self._first_non_empty_string(
        haloitsm_payload.get("url"),
        haloitsm_payload.get("html_url"),
        haloitsm_payload.get("link"),
        existing.haloitsm.url,
      ),
      updated_at=(
        self._parse_payload_datetime(haloitsm_payload.get("updated_at"))
        or existing.haloitsm.updated_at
      ),
      phase_graph=self._build_haloitsm_recovery_phase_graph(
        payload=haloitsm_payload,
        alert_status=haloitsm_status,
        priority=self._first_non_empty_string(
          haloitsm_payload.get("priority"),
          haloitsm_payload.get("severity"),
          haloitsm_payload.get("urgency"),
          existing.haloitsm.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          haloitsm_payload.get("escalation_policy"),
          haloitsm_payload.get("escalationPolicy"),
          haloitsm_payload.get("policy"),
          haloitsm_payload.get("source"),
          existing.haloitsm.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          haloitsm_payload.get("assignee"),
          haloitsm_payload.get("owner"),
          haloitsm_payload.get("assigned_to"),
          existing.haloitsm.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.haloitsm,
      ),
    )
    provider_schema_kind = "haloitsm"
  incidentmanagerio_schema = existing.incidentmanagerio
  incidentmanagerio_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("incidentmanagerio"),
    payload.get("incidentmanagerio"),
    payload.get("incidentmanagerio_alert"),
  )
  if normalized_provider == "incidentmanagerio" or incidentmanagerio_payload:
    incidentmanagerio_status = self._first_non_empty_string(
      incidentmanagerio_payload.get("alert_status"),
      incidentmanagerio_payload.get("status"),
      incidentmanagerio_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.incidentmanagerio.alert_status,
    ) or "unknown"
    incidentmanagerio_schema = OperatorIncidentIncidentManagerIoRecoveryState(
      alert_id=self._first_non_empty_string(
        incidentmanagerio_payload.get("alert_id"),
        incidentmanagerio_payload.get("id"),
        incidentmanagerio_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.incidentmanagerio.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        incidentmanagerio_payload.get("external_reference"),
        incidentmanagerio_payload.get("reference"),
        reference,
        existing.incidentmanagerio.external_reference,
      ),
      alert_status=incidentmanagerio_status,
      priority=self._first_non_empty_string(
        incidentmanagerio_payload.get("priority"),
        incidentmanagerio_payload.get("severity"),
        incidentmanagerio_payload.get("urgency"),
        existing.incidentmanagerio.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        incidentmanagerio_payload.get("escalation_policy"),
        incidentmanagerio_payload.get("escalationPolicy"),
        incidentmanagerio_payload.get("policy"),
        incidentmanagerio_payload.get("source"),
        existing.incidentmanagerio.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        incidentmanagerio_payload.get("assignee"),
        incidentmanagerio_payload.get("owner"),
        incidentmanagerio_payload.get("assigned_to"),
        existing.incidentmanagerio.assignee,
      ),
      url=self._first_non_empty_string(
        incidentmanagerio_payload.get("url"),
        incidentmanagerio_payload.get("html_url"),
        incidentmanagerio_payload.get("link"),
        existing.incidentmanagerio.url,
      ),
      updated_at=(
        self._parse_payload_datetime(incidentmanagerio_payload.get("updated_at"))
        or existing.incidentmanagerio.updated_at
      ),
      phase_graph=self._build_incidentmanagerio_recovery_phase_graph(
        payload=incidentmanagerio_payload,
        alert_status=incidentmanagerio_status,
        priority=self._first_non_empty_string(
          incidentmanagerio_payload.get("priority"),
          incidentmanagerio_payload.get("severity"),
          incidentmanagerio_payload.get("urgency"),
          existing.incidentmanagerio.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          incidentmanagerio_payload.get("escalation_policy"),
          incidentmanagerio_payload.get("escalationPolicy"),
          incidentmanagerio_payload.get("policy"),
          incidentmanagerio_payload.get("source"),
          existing.incidentmanagerio.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          incidentmanagerio_payload.get("assignee"),
          incidentmanagerio_payload.get("owner"),
          incidentmanagerio_payload.get("assigned_to"),
          existing.incidentmanagerio.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.incidentmanagerio,
      ),
    )
    provider_schema_kind = "incidentmanagerio"
  oneuptime_schema = existing.oneuptime
  oneuptime_payload = self._merge_payload_mappings(
    self._extract_payload_mapping(payload.get("provider_schema")).get("oneuptime"),
    payload.get("oneuptime"),
    payload.get("oneuptime_alert"),
  )
  if normalized_provider == "oneuptime" or oneuptime_payload:
    oneuptime_status = self._first_non_empty_string(
      oneuptime_payload.get("alert_status"),
      oneuptime_payload.get("status"),
      oneuptime_payload.get("state"),
      status_machine.workflow_state,
      payload.get("workflow_state"),
      existing.oneuptime.alert_status,
    ) or "unknown"
    oneuptime_schema = OperatorIncidentOneUptimeRecoveryState(
      alert_id=self._first_non_empty_string(
        oneuptime_payload.get("alert_id"),
        oneuptime_payload.get("id"),
        oneuptime_payload.get("alertId"),
        self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        existing.oneuptime.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        oneuptime_payload.get("external_reference"),
        oneuptime_payload.get("reference"),
        reference,
        existing.oneuptime.external_reference,
      ),
      alert_status=oneuptime_status,
      priority=self._first_non_empty_string(
        oneuptime_payload.get("priority"),
        oneuptime_payload.get("severity"),
        oneuptime_payload.get("urgency"),
        existing.oneuptime.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        oneuptime_payload.get("escalation_policy"),
        oneuptime_payload.get("escalationPolicy"),
        oneuptime_payload.get("policy"),
        oneuptime_payload.get("source"),
        existing.oneuptime.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        oneuptime_payload.get("assignee"),
        oneuptime_payload.get("owner"),
        oneuptime_payload.get("assigned_to"),
        existing.oneuptime.assignee,
      ),
      url=self._first_non_empty_string(
        oneuptime_payload.get("url"),
        oneuptime_payload.get("html_url"),
        oneuptime_payload.get("link"),
        existing.oneuptime.url,
      ),
      updated_at=(
        self._parse_payload_datetime(oneuptime_payload.get("updated_at"))
        or existing.oneuptime.updated_at
      ),
      phase_graph=self._build_oneuptime_recovery_phase_graph(
        payload=oneuptime_payload,
        alert_status=oneuptime_status,
        priority=self._first_non_empty_string(
          oneuptime_payload.get("priority"),
          oneuptime_payload.get("severity"),
          oneuptime_payload.get("urgency"),
          existing.oneuptime.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          oneuptime_payload.get("escalation_policy"),
          oneuptime_payload.get("escalationPolicy"),
          oneuptime_payload.get("policy"),
          oneuptime_payload.get("source"),
          existing.oneuptime.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          oneuptime_payload.get("assignee"),
          oneuptime_payload.get("owner"),
          oneuptime_payload.get("assigned_to"),
          existing.oneuptime.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.oneuptime,
      ),
    )
    provider_schema_kind = "oneuptime"
  return (
    provider_schema_kind,
    resolver_schema,
    openduty_schema,
    cabot_schema,
    haloitsm_schema,
    incidentmanagerio_schema,
    oneuptime_schema,
  )
