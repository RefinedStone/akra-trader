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

def _build_provider_recovery_provider_schema_group_primary(
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
  pagerduty_payload = self._merge_payload_mappings(
    schema_payload.get("pagerduty"),
    payload.get("pagerduty"),
    payload.get("pagerduty_incident"),
  )
  pagerduty_status = self._first_non_empty_string(
    pagerduty_payload.get("incident_status"),
    pagerduty_payload.get("status"),
    workflow_state,
    payload.get("workflow_state"),
    existing.pagerduty.incident_status,
  ) or "unknown"
  pagerduty = OperatorIncidentPagerDutyRecoveryState(
    incident_id=self._first_non_empty_string(
      pagerduty_payload.get("incident_id"),
      pagerduty_payload.get("id"),
      workflow_reference,
      existing.pagerduty.incident_id,
    ),
    incident_key=self._first_non_empty_string(
      pagerduty_payload.get("incident_key"),
      pagerduty_payload.get("dedup_key"),
      reference,
      existing.pagerduty.incident_key,
    ),
    incident_status=pagerduty_status,
    urgency=self._first_non_empty_string(
      pagerduty_payload.get("urgency"),
      existing.pagerduty.urgency,
    ),
    service_id=self._first_non_empty_string(
      pagerduty_payload.get("service_id"),
      existing.pagerduty.service_id,
    ),
    service_summary=self._first_non_empty_string(
      pagerduty_payload.get("service_summary"),
      pagerduty_payload.get("service_name"),
      existing.pagerduty.service_summary,
    ),
    escalation_policy_id=self._first_non_empty_string(
      pagerduty_payload.get("escalation_policy_id"),
      existing.pagerduty.escalation_policy_id,
    ),
    escalation_policy_summary=self._first_non_empty_string(
      pagerduty_payload.get("escalation_policy_summary"),
      pagerduty_payload.get("escalation_policy_name"),
      existing.pagerduty.escalation_policy_summary,
    ),
    html_url=self._first_non_empty_string(
      pagerduty_payload.get("html_url"),
      existing.pagerduty.html_url,
    ),
    last_status_change_at=(
      self._parse_payload_datetime(pagerduty_payload.get("last_status_change_at"))
      or existing.pagerduty.last_status_change_at
    ),
    phase_graph=self._build_pagerduty_recovery_phase_graph(
      payload=pagerduty_payload,
      incident_status=pagerduty_status,
      urgency=self._first_non_empty_string(
        pagerduty_payload.get("urgency"),
        existing.pagerduty.urgency,
      ),
      lifecycle_state=lifecycle_state,
      status_machine=status_machine,
      synced_at=synced_at,
      existing=existing.pagerduty,
    ),
  )

  opsgenie_payload = self._merge_payload_mappings(
    schema_payload.get("opsgenie"),
    payload.get("opsgenie"),
    payload.get("opsgenie_alert"),
  )
  opsgenie_status = self._first_non_empty_string(
    opsgenie_payload.get("alert_status"),
    opsgenie_payload.get("status"),
    workflow_state,
    payload.get("workflow_state"),
    existing.opsgenie.alert_status,
  ) or "unknown"
  opsgenie = OperatorIncidentOpsgenieRecoveryState(
    alert_id=self._first_non_empty_string(
      opsgenie_payload.get("alert_id"),
      opsgenie_payload.get("id"),
      workflow_reference,
      existing.opsgenie.alert_id,
    ),
    alias=self._first_non_empty_string(
      opsgenie_payload.get("alias"),
      reference,
      existing.opsgenie.alias,
    ),
    alert_status=opsgenie_status,
    priority=self._first_non_empty_string(
      opsgenie_payload.get("priority"),
      existing.opsgenie.priority,
    ),
    owner=self._first_non_empty_string(
      opsgenie_payload.get("owner"),
      existing.opsgenie.owner,
    ),
    acknowledged=(
      opsgenie_payload.get("acknowledged")
      if isinstance(opsgenie_payload.get("acknowledged"), bool)
      else existing.opsgenie.acknowledged
    ),
    seen=(
      opsgenie_payload.get("seen")
      if isinstance(opsgenie_payload.get("seen"), bool)
      else existing.opsgenie.seen
    ),
    tiny_id=self._first_non_empty_string(
      opsgenie_payload.get("tiny_id"),
      opsgenie_payload.get("tinyId"),
      existing.opsgenie.tiny_id,
    ),
    teams=self._extract_string_tuple(
      opsgenie_payload.get("teams"),
      opsgenie_payload.get("team"),
      existing.opsgenie.teams,
    ),
    updated_at=(
      self._parse_payload_datetime(opsgenie_payload.get("updated_at"))
      or self._parse_payload_datetime(opsgenie_payload.get("updatedAt"))
      or existing.opsgenie.updated_at
    ),
    phase_graph=self._build_opsgenie_recovery_phase_graph(
      payload=opsgenie_payload,
      alert_status=opsgenie_status,
      owner=self._first_non_empty_string(
        opsgenie_payload.get("owner"),
        existing.opsgenie.owner,
      ),
      acknowledged=(
        opsgenie_payload.get("acknowledged")
        if isinstance(opsgenie_payload.get("acknowledged"), bool)
        else existing.opsgenie.acknowledged
      ),
      seen=(
        opsgenie_payload.get("seen")
        if isinstance(opsgenie_payload.get("seen"), bool)
        else existing.opsgenie.seen
      ),
      teams=self._extract_string_tuple(
        opsgenie_payload.get("teams"),
        opsgenie_payload.get("team"),
        existing.opsgenie.teams,
      ),
      lifecycle_state=lifecycle_state,
      status_machine=status_machine,
      synced_at=synced_at,
      existing=existing.opsgenie,
    ),
  )

  incidentio_payload = self._merge_payload_mappings(
    schema_payload.get("incidentio"),
    schema_payload.get("incident_io"),
    payload.get("incidentio"),
    payload.get("incidentio_incident"),
    payload.get("incident_io"),
  )
  incidentio_status = self._first_non_empty_string(
    incidentio_payload.get("incident_status"),
    incidentio_payload.get("status"),
    workflow_state,
    payload.get("workflow_state"),
    existing.incidentio.incident_status,
  ) or "unknown"
  incidentio = OperatorIncidentIncidentIoRecoveryState(
    incident_id=self._first_non_empty_string(
      incidentio_payload.get("incident_id"),
      incidentio_payload.get("id"),
      workflow_reference,
      existing.incidentio.incident_id,
    ),
    external_reference=self._first_non_empty_string(
      incidentio_payload.get("external_reference"),
      incidentio_payload.get("reference"),
      reference,
      existing.incidentio.external_reference,
    ),
    incident_status=incidentio_status,
    severity=self._first_non_empty_string(
      incidentio_payload.get("severity"),
      existing.incidentio.severity,
    ),
    mode=self._first_non_empty_string(
      incidentio_payload.get("mode"),
      existing.incidentio.mode,
    ),
    visibility=self._first_non_empty_string(
      incidentio_payload.get("visibility"),
      existing.incidentio.visibility,
    ),
    assignee=self._first_non_empty_string(
      incidentio_payload.get("assignee"),
      incidentio_payload.get("owner"),
      existing.incidentio.assignee,
    ),
    url=self._first_non_empty_string(
      incidentio_payload.get("url"),
      incidentio_payload.get("html_url"),
      existing.incidentio.url,
    ),
    updated_at=(
      self._parse_payload_datetime(incidentio_payload.get("updated_at"))
      or existing.incidentio.updated_at
    ),
    phase_graph=self._build_incidentio_recovery_phase_graph(
      payload=incidentio_payload,
      incident_status=incidentio_status,
      severity=self._first_non_empty_string(
        incidentio_payload.get("severity"),
        existing.incidentio.severity,
      ),
      mode=self._first_non_empty_string(
        incidentio_payload.get("mode"),
        existing.incidentio.mode,
      ),
      visibility=self._first_non_empty_string(
        incidentio_payload.get("visibility"),
        existing.incidentio.visibility,
      ),
      assignee=self._first_non_empty_string(
        incidentio_payload.get("assignee"),
        incidentio_payload.get("owner"),
        existing.incidentio.assignee,
      ),
      lifecycle_state=lifecycle_state,
      status_machine=status_machine,
      synced_at=synced_at,
      existing=existing.incidentio,
    ),
  )

  firehydrant_payload = self._merge_payload_mappings(
    schema_payload.get("firehydrant"),
    schema_payload.get("fire_hydrant"),
    payload.get("firehydrant"),
    payload.get("firehydrant_incident"),
    payload.get("fire_hydrant"),
  )
  firehydrant_status = self._first_non_empty_string(
    firehydrant_payload.get("incident_status"),
    firehydrant_payload.get("status"),
    workflow_state,
    payload.get("workflow_state"),
    existing.firehydrant.incident_status,
  ) or "unknown"
  firehydrant = OperatorIncidentFireHydrantRecoveryState(
    incident_id=self._first_non_empty_string(
      firehydrant_payload.get("incident_id"),
      firehydrant_payload.get("id"),
      workflow_reference,
      existing.firehydrant.incident_id,
    ),
    external_reference=self._first_non_empty_string(
      firehydrant_payload.get("external_reference"),
      firehydrant_payload.get("reference"),
      reference,
      existing.firehydrant.external_reference,
    ),
    incident_status=firehydrant_status,
    severity=self._first_non_empty_string(
      firehydrant_payload.get("severity"),
      existing.firehydrant.severity,
    ),
    priority=self._first_non_empty_string(
      firehydrant_payload.get("priority"),
      existing.firehydrant.priority,
    ),
    team=self._first_non_empty_string(
      firehydrant_payload.get("team"),
      firehydrant_payload.get("owner"),
      existing.firehydrant.team,
    ),
    runbook=self._first_non_empty_string(
      firehydrant_payload.get("runbook"),
      firehydrant_payload.get("runbook_name"),
      existing.firehydrant.runbook,
    ),
    url=self._first_non_empty_string(
      firehydrant_payload.get("url"),
      firehydrant_payload.get("html_url"),
      existing.firehydrant.url,
    ),
    updated_at=(
      self._parse_payload_datetime(firehydrant_payload.get("updated_at"))
      or existing.firehydrant.updated_at
    ),
    phase_graph=self._build_firehydrant_recovery_phase_graph(
      payload=firehydrant_payload,
      incident_status=firehydrant_status,
      severity=self._first_non_empty_string(
        firehydrant_payload.get("severity"),
        existing.firehydrant.severity,
      ),
      priority=self._first_non_empty_string(
        firehydrant_payload.get("priority"),
        existing.firehydrant.priority,
      ),
      team=self._first_non_empty_string(
        firehydrant_payload.get("team"),
        firehydrant_payload.get("owner"),
        existing.firehydrant.team,
      ),
      lifecycle_state=lifecycle_state,
      status_machine=status_machine,
      synced_at=synced_at,
      existing=existing.firehydrant,
    ),
  )

  return (
    pagerduty,
    opsgenie,
    incidentio,
    firehydrant,
  )
