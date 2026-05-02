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

def _build_provider_recovery_provider_schema_group_mid(
  self,
  *,
  schema_payload: dict[str, Any],
  payload: dict[str, Any],
  lifecycle_state: str,
  status_machine: OperatorIncidentProviderRecoveryStatusMachine,
  synced_at: datetime,
  workflow_state: str | None,
  workflow_reference: str | None,
  reference: str | None,
  existing: OperatorIncidentProviderRecoveryState,
) -> tuple[Any, ...]:
  rootly_payload = self._merge_payload_mappings(
    schema_payload.get("rootly"),
    schema_payload.get("root_ly"),
    payload.get("rootly"),
    payload.get("rootly_incident"),
    payload.get("root_ly"),
  )
  rootly_status = self._first_non_empty_string(
    rootly_payload.get("incident_status"),
    rootly_payload.get("status"),
    workflow_state,
    payload.get("workflow_state"),
    existing.rootly.incident_status,
  ) or "unknown"
  rootly_private = (
    rootly_payload.get("private")
    if isinstance(rootly_payload.get("private"), bool)
    else existing.rootly.private
  )
  rootly_acknowledged_at = (
    self._parse_payload_datetime(rootly_payload.get("acknowledged_at"))
    or existing.rootly.acknowledged_at
  )
  rootly = OperatorIncidentRootlyRecoveryState(
    incident_id=self._first_non_empty_string(
      rootly_payload.get("incident_id"),
      rootly_payload.get("id"),
      workflow_reference,
      existing.rootly.incident_id,
    ),
    external_reference=self._first_non_empty_string(
      rootly_payload.get("external_reference"),
      rootly_payload.get("reference"),
      reference,
      existing.rootly.external_reference,
    ),
    incident_status=rootly_status,
    severity_id=self._first_non_empty_string(
      rootly_payload.get("severity_id"),
      existing.rootly.severity_id,
    ),
    private=rootly_private,
    slug=self._first_non_empty_string(
      rootly_payload.get("slug"),
      rootly_payload.get("short_id"),
      existing.rootly.slug,
    ),
    url=self._first_non_empty_string(
      rootly_payload.get("url"),
      rootly_payload.get("html_url"),
      existing.rootly.url,
    ),
    acknowledged_at=rootly_acknowledged_at,
    updated_at=(
      self._parse_payload_datetime(rootly_payload.get("updated_at"))
      or existing.rootly.updated_at
    ),
    phase_graph=self._build_rootly_recovery_phase_graph(
      payload=rootly_payload,
      incident_status=rootly_status,
      severity_id=self._first_non_empty_string(
        rootly_payload.get("severity_id"),
        existing.rootly.severity_id,
      ),
      private=rootly_private,
      acknowledged_at=rootly_acknowledged_at,
      lifecycle_state=lifecycle_state,
      status_machine=status_machine,
      synced_at=synced_at,
      existing=existing.rootly,
    ),
  )

  blameless_payload = self._merge_payload_mappings(
    schema_payload.get("blameless"),
    schema_payload.get("blame_less"),
    payload.get("blameless"),
    payload.get("blameless_incident"),
    payload.get("blame_less"),
  )
  blameless_status = self._first_non_empty_string(
    blameless_payload.get("incident_status"),
    blameless_payload.get("status"),
    workflow_state,
    payload.get("workflow_state"),
    existing.blameless.incident_status,
  ) or "unknown"
  blameless = OperatorIncidentBlamelessRecoveryState(
    incident_id=self._first_non_empty_string(
      blameless_payload.get("incident_id"),
      blameless_payload.get("id"),
      workflow_reference,
      existing.blameless.incident_id,
    ),
    external_reference=self._first_non_empty_string(
      blameless_payload.get("external_reference"),
      blameless_payload.get("reference"),
      reference,
      existing.blameless.external_reference,
    ),
    incident_status=blameless_status,
    severity=self._first_non_empty_string(
      blameless_payload.get("severity"),
      existing.blameless.severity,
    ),
    commander=self._first_non_empty_string(
      blameless_payload.get("commander"),
      blameless_payload.get("owner"),
      existing.blameless.commander,
    ),
    visibility=self._first_non_empty_string(
      blameless_payload.get("visibility"),
      blameless_payload.get("visibility_mode"),
      existing.blameless.visibility,
    ),
    url=self._first_non_empty_string(
      blameless_payload.get("url"),
      blameless_payload.get("html_url"),
      existing.blameless.url,
    ),
    updated_at=(
      self._parse_payload_datetime(blameless_payload.get("updated_at"))
      or existing.blameless.updated_at
    ),
    phase_graph=self._build_blameless_recovery_phase_graph(
      payload=blameless_payload,
      incident_status=blameless_status,
      severity=self._first_non_empty_string(
        blameless_payload.get("severity"),
        existing.blameless.severity,
      ),
      commander=self._first_non_empty_string(
        blameless_payload.get("commander"),
        blameless_payload.get("owner"),
        existing.blameless.commander,
      ),
      visibility=self._first_non_empty_string(
        blameless_payload.get("visibility"),
        blameless_payload.get("visibility_mode"),
        existing.blameless.visibility,
      ),
      lifecycle_state=lifecycle_state,
      status_machine=status_machine,
      synced_at=synced_at,
      existing=existing.blameless,
    ),
  )

  xmatters_payload = self._merge_payload_mappings(
    schema_payload.get("xmatters"),
    schema_payload.get("x_matters"),
    payload.get("xmatters"),
    payload.get("xmatters_incident"),
    payload.get("x_matters"),
  )
  xmatters_status = self._first_non_empty_string(
    xmatters_payload.get("incident_status"),
    xmatters_payload.get("status"),
    workflow_state,
    payload.get("workflow_state"),
    existing.xmatters.incident_status,
  ) or "unknown"
  xmatters = OperatorIncidentXmattersRecoveryState(
    incident_id=self._first_non_empty_string(
      xmatters_payload.get("incident_id"),
      xmatters_payload.get("id"),
      workflow_reference,
      existing.xmatters.incident_id,
    ),
    external_reference=self._first_non_empty_string(
      xmatters_payload.get("external_reference"),
      xmatters_payload.get("reference"),
      reference,
      existing.xmatters.external_reference,
    ),
    incident_status=xmatters_status,
    priority=self._first_non_empty_string(
      xmatters_payload.get("priority"),
      existing.xmatters.priority,
    ),
    assignee=self._first_non_empty_string(
      xmatters_payload.get("assignee"),
      xmatters_payload.get("owner"),
      existing.xmatters.assignee,
    ),
    response_plan=self._first_non_empty_string(
      xmatters_payload.get("response_plan"),
      xmatters_payload.get("plan"),
      existing.xmatters.response_plan,
    ),
    url=self._first_non_empty_string(
      xmatters_payload.get("url"),
      xmatters_payload.get("html_url"),
      existing.xmatters.url,
    ),
    updated_at=(
      self._parse_payload_datetime(xmatters_payload.get("updated_at"))
      or existing.xmatters.updated_at
    ),
    phase_graph=self._build_xmatters_recovery_phase_graph(
      payload=xmatters_payload,
      incident_status=xmatters_status,
      priority=self._first_non_empty_string(
        xmatters_payload.get("priority"),
        existing.xmatters.priority,
      ),
      assignee=self._first_non_empty_string(
        xmatters_payload.get("assignee"),
        xmatters_payload.get("owner"),
        existing.xmatters.assignee,
      ),
      response_plan=self._first_non_empty_string(
        xmatters_payload.get("response_plan"),
        xmatters_payload.get("plan"),
        existing.xmatters.response_plan,
      ),
      lifecycle_state=lifecycle_state,
      status_machine=status_machine,
      synced_at=synced_at,
      existing=existing.xmatters,
    ),
  )

  servicenow_payload = self._merge_payload_mappings(
    schema_payload.get("servicenow"),
    schema_payload.get("service_now"),
    payload.get("servicenow"),
    payload.get("servicenow_incident"),
    payload.get("service_now"),
  )
  servicenow_status = self._first_non_empty_string(
    servicenow_payload.get("incident_status"),
    servicenow_payload.get("status"),
    servicenow_payload.get("state"),
    workflow_state,
    payload.get("workflow_state"),
    existing.servicenow.incident_status,
  ) or "unknown"
  servicenow = OperatorIncidentServicenowRecoveryState(
    incident_number=self._first_non_empty_string(
      servicenow_payload.get("incident_number"),
      servicenow_payload.get("number"),
      workflow_reference,
      existing.servicenow.incident_number,
    ),
    external_reference=self._first_non_empty_string(
      servicenow_payload.get("external_reference"),
      servicenow_payload.get("reference"),
      reference,
      existing.servicenow.external_reference,
    ),
    incident_status=servicenow_status,
    priority=self._first_non_empty_string(
      servicenow_payload.get("priority"),
      existing.servicenow.priority,
    ),
    assigned_to=self._first_non_empty_string(
      servicenow_payload.get("assigned_to"),
      servicenow_payload.get("owner"),
      existing.servicenow.assigned_to,
    ),
    assignment_group=self._first_non_empty_string(
      servicenow_payload.get("assignment_group"),
      servicenow_payload.get("group"),
      existing.servicenow.assignment_group,
    ),
    url=self._first_non_empty_string(
      servicenow_payload.get("url"),
      servicenow_payload.get("html_url"),
      existing.servicenow.url,
    ),
    updated_at=(
      self._parse_payload_datetime(servicenow_payload.get("updated_at"))
      or existing.servicenow.updated_at
    ),
    phase_graph=self._build_servicenow_recovery_phase_graph(
      payload=servicenow_payload,
      incident_status=servicenow_status,
      priority=self._first_non_empty_string(
        servicenow_payload.get("priority"),
        existing.servicenow.priority,
      ),
      assigned_to=self._first_non_empty_string(
        servicenow_payload.get("assigned_to"),
        servicenow_payload.get("owner"),
        existing.servicenow.assigned_to,
      ),
      assignment_group=self._first_non_empty_string(
        servicenow_payload.get("assignment_group"),
        servicenow_payload.get("group"),
        existing.servicenow.assignment_group,
      ),
      lifecycle_state=lifecycle_state,
      status_machine=status_machine,
      synced_at=synced_at,
      existing=existing.servicenow,
    ),
  )

  squadcast_payload = self._merge_payload_mappings(
    schema_payload.get("squadcast"),
    schema_payload.get("squad_cast"),
    payload.get("squadcast"),
    payload.get("squadcast_incident"),
    payload.get("squad_cast"),
  )
  squadcast_status = self._first_non_empty_string(
    squadcast_payload.get("incident_status"),
    squadcast_payload.get("status"),
    squadcast_payload.get("state"),
    workflow_state,
    payload.get("workflow_state"),
    existing.squadcast.incident_status,
  ) or "unknown"
  squadcast = OperatorIncidentSquadcastRecoveryState(
    incident_id=self._first_non_empty_string(
      squadcast_payload.get("incident_id"),
      squadcast_payload.get("id"),
      workflow_reference,
      existing.squadcast.incident_id,
    ),
    external_reference=self._first_non_empty_string(
      squadcast_payload.get("external_reference"),
      squadcast_payload.get("reference"),
      reference,
      existing.squadcast.external_reference,
    ),
    incident_status=squadcast_status,
    severity=self._first_non_empty_string(
      squadcast_payload.get("severity"),
      squadcast_payload.get("priority"),
      existing.squadcast.severity,
    ),
    assignee=self._first_non_empty_string(
      squadcast_payload.get("assignee"),
      squadcast_payload.get("owner"),
      existing.squadcast.assignee,
    ),
    escalation_policy=self._first_non_empty_string(
      squadcast_payload.get("escalation_policy"),
      squadcast_payload.get("escalation_policy_name"),
      squadcast_payload.get("policy"),
      existing.squadcast.escalation_policy,
    ),
    url=self._first_non_empty_string(
      squadcast_payload.get("url"),
      squadcast_payload.get("html_url"),
      existing.squadcast.url,
    ),
    updated_at=(
      self._parse_payload_datetime(squadcast_payload.get("updated_at"))
      or existing.squadcast.updated_at
    ),
    phase_graph=self._build_squadcast_recovery_phase_graph(
      payload=squadcast_payload,
      incident_status=squadcast_status,
      severity=self._first_non_empty_string(
        squadcast_payload.get("severity"),
        squadcast_payload.get("priority"),
        existing.squadcast.severity,
      ),
      assignee=self._first_non_empty_string(
        squadcast_payload.get("assignee"),
        squadcast_payload.get("owner"),
        existing.squadcast.assignee,
      ),
      escalation_policy=self._first_non_empty_string(
        squadcast_payload.get("escalation_policy"),
        squadcast_payload.get("escalation_policy_name"),
        squadcast_payload.get("policy"),
        existing.squadcast.escalation_policy,
      ),
      lifecycle_state=lifecycle_state,
      status_machine=status_machine,
      synced_at=synced_at,
      existing=existing.squadcast,
    ),
  )

  return (
    rootly,
    blameless,
    xmatters,
    servicenow,
    squadcast,
  )
