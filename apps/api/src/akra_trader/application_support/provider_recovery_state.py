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
from akra_trader.application_support.provider_recovery_core_state_secondary_one import _build_provider_recovery_state_secondary_group_one
from akra_trader.application_support.provider_recovery_core_state_secondary_two import _build_provider_recovery_state_secondary_group_two
from akra_trader.application_support.provider_recovery_core_state_secondary_three import _build_provider_recovery_state_secondary_group_three
from akra_trader.application_support.provider_recovery_core_state_secondary_four import _build_provider_recovery_state_secondary_group_four
from akra_trader.application_support.provider_recovery_core_state_secondary_five import _build_provider_recovery_state_secondary_group_five

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

def _build_provider_recovery_state(
  self,
  *,
  remediation: OperatorIncidentRemediation,
  next_state: str,
  provider: str,
  detail: str,
  synced_at: datetime,
  workflow_reference: str | None,
  payload: dict[str, Any],
  event_kind: str | None = None,
) -> OperatorIncidentProviderRecoveryState:
  existing = remediation.provider_recovery
  market_context = self._extract_operator_alert_market_context_from_workflow_payload(
    payload=payload,
    existing_symbols=existing.symbols,
    existing_timeframe=existing.timeframe,
    existing_primary_focus=existing.primary_focus,
  )
  market_context_provenance = self._extract_operator_alert_market_context_provenance_from_workflow_payload(
    payload=payload,
    existing=existing.market_context_provenance,
  )
  verification_payload = self._extract_payload_mapping(payload.get("verification"))
  target_payload = self._extract_payload_mapping(payload.get("target"))
  targets_payload = self._extract_payload_mapping(payload.get("targets"))
  lifecycle_state = self._first_non_empty_string(
    payload.get("recovery_state"),
    payload.get("recovery_phase"),
    payload.get("job_state"),
    payload.get("status"),
  ) or self._provider_recovery_lifecycle_for_event(
    remediation_state=next_state,
    event_kind=event_kind,
  )
  verification = OperatorIncidentProviderRecoveryVerification(
    state=self._first_non_empty_string(
      verification_payload.get("state"),
      payload.get("verification_state"),
      existing.verification.state,
    ) or "unknown",
    checked_at=(
      self._parse_payload_datetime(verification_payload.get("checked_at"))
      or self._parse_payload_datetime(payload.get("verified_at"))
      or self._parse_payload_datetime(payload.get("checked_at"))
      or existing.verification.checked_at
    ),
    summary=self._first_non_empty_string(
      verification_payload.get("summary"),
      verification_payload.get("message"),
      payload.get("verification_summary"),
      existing.verification.summary,
    ),
    issues=self._extract_string_tuple(
      verification_payload.get("issues"),
      payload.get("verification_issues"),
      existing.verification.issues,
    ),
  )
  status_machine = self._build_provider_recovery_status_machine(
    existing=existing.status_machine,
    remediation_state=next_state,
    event_kind=event_kind,
    workflow_state=existing.status_machine.workflow_state,
    workflow_action=existing.status_machine.workflow_action,
    detail=detail,
    event_at=synced_at,
    payload=payload,
  )
  telemetry = self._build_provider_recovery_telemetry(
    payload=payload,
    synced_at=synced_at,
    status_machine=status_machine,
    existing=existing.telemetry,
  )
  reference = self._first_non_empty_string(
    payload.get("reference"),
    payload.get("job_reference"),
    payload.get("recovery_reference"),
    existing.reference,
    remediation.reference,
  )
  normalized_provider = self._normalize_paging_provider(
    provider or existing.provider or remediation.provider or ""
  )
  (
    provider_schema_kind,
    pagerduty_schema,
    opsgenie_schema,
    incidentio_schema,
    firehydrant_schema,
    rootly_schema,
    blameless_schema,
    xmatters_schema,
    servicenow_schema,
    squadcast_schema,
    bigpanda_schema,
    grafana_oncall_schema,
    zenduty_schema,
    splunk_oncall_schema,
    jira_service_management_schema,
    pagertree_schema,
    alertops_schema,
    signl4_schema,
    ilert_schema,
  ) = (
    self._build_provider_recovery_provider_schema(
      provider=provider or existing.provider or remediation.provider or "",
      payload=payload,
      lifecycle_state=lifecycle_state,
      status_machine=status_machine,
      synced_at=synced_at,
      workflow_state=status_machine.workflow_state,
      workflow_reference=self._first_non_empty_string(
        workflow_reference,
        payload.get("workflow_reference"),
        payload.get("provider_workflow_reference"),
        existing.workflow_reference,
      ),
      reference=reference,
      existing=existing,
    )
  )
  (
    provider_schema_kind,
    betterstack_schema,
    onpage_schema,
    allquiet_schema,
    moogsoft_schema,
    spikesh_schema,
    dutycalls_schema,
    incidenthub_schema,
  ) = _build_provider_recovery_state_secondary_group_one(
    self,
    existing=existing,
    payload=payload,
    normalized_provider=normalized_provider,
    lifecycle_state=lifecycle_state,
    status_machine=status_machine,
    synced_at=synced_at,
    provider_schema_kind=provider_schema_kind,
    workflow_reference=workflow_reference,
    reference=reference,
  )
  (
    provider_schema_kind,
    resolver_schema,
    openduty_schema,
    cabot_schema,
    haloitsm_schema,
    incidentmanagerio_schema,
    oneuptime_schema,
  ) = _build_provider_recovery_state_secondary_group_two(
    self,
    existing=existing,
    payload=payload,
    normalized_provider=normalized_provider,
    lifecycle_state=lifecycle_state,
    status_machine=status_machine,
    synced_at=synced_at,
    provider_schema_kind=provider_schema_kind,
    workflow_reference=workflow_reference,
    reference=reference,
  )
  (
    provider_schema_kind,
    squzy_schema,
    crisescontrol_schema,
    freshservice_schema,
    freshdesk_schema,
    happyfox_schema,
    zendesk_schema,
  ) = _build_provider_recovery_state_secondary_group_three(
    self,
    existing=existing,
    payload=payload,
    normalized_provider=normalized_provider,
    lifecycle_state=lifecycle_state,
    status_machine=status_machine,
    synced_at=synced_at,
    provider_schema_kind=provider_schema_kind,
    workflow_reference=workflow_reference,
    reference=reference,
  )
  (
    provider_schema_kind,
    zohodesk_schema,
    helpscout_schema,
    kayako_schema,
    intercom_schema,
    front_schema,
    servicedeskplus_schema,
    sysaid_schema,
  ) = _build_provider_recovery_state_secondary_group_four(
    self,
    existing=existing,
    payload=payload,
    normalized_provider=normalized_provider,
    lifecycle_state=lifecycle_state,
    status_machine=status_machine,
    synced_at=synced_at,
    provider_schema_kind=provider_schema_kind,
    workflow_reference=workflow_reference,
    reference=reference,
  )
  (
    provider_schema_kind,
    bmchelix_schema,
    solarwindsservicedesk_schema,
    topdesk_schema,
    invgateservicedesk_schema,
    opsramp_schema,
  ) = _build_provider_recovery_state_secondary_group_five(
    self,
    existing=existing,
    payload=payload,
    normalized_provider=normalized_provider,
    lifecycle_state=lifecycle_state,
    status_machine=status_machine,
    synced_at=synced_at,
    provider_schema_kind=provider_schema_kind,
    workflow_reference=workflow_reference,
    reference=reference,
  )
  return OperatorIncidentProviderRecoveryState(
    lifecycle_state=lifecycle_state,
    provider=provider or existing.provider or remediation.provider,
    job_id=self._first_non_empty_string(
      payload.get("job_id"),
      payload.get("recovery_id"),
      payload.get("execution_id"),
      existing.job_id,
    ),
    reference=reference,
    workflow_reference=self._first_non_empty_string(
      workflow_reference,
      payload.get("workflow_reference"),
      payload.get("provider_workflow_reference"),
      existing.workflow_reference,
    ),
    summary=self._first_non_empty_string(
      payload.get("summary"),
      payload.get("remediation_summary"),
      payload.get("message"),
      existing.summary,
      remediation.summary,
    ),
    detail=self._first_non_empty_string(
      payload.get("detail"),
      payload.get("remediation_detail"),
      payload.get("status_detail"),
      payload.get("result_detail"),
      existing.detail,
      detail,
    ),
    channels=self._extract_string_tuple(
      payload.get("channels"),
      payload.get("channel"),
      target_payload.get("channels"),
      existing.channels,
    ),
    symbols=market_context["symbols"],
    timeframe=market_context["timeframe"],
    primary_focus=market_context["primary_focus"],
    market_context_provenance=market_context_provenance,
    verification=verification,
    telemetry=telemetry,
    status_machine=status_machine,
    provider_schema_kind=provider_schema_kind,
    pagerduty=pagerduty_schema,
    opsgenie=opsgenie_schema,
    incidentio=incidentio_schema,
    firehydrant=firehydrant_schema,
    rootly=rootly_schema,
    blameless=blameless_schema,
    xmatters=xmatters_schema,
    servicenow=servicenow_schema,
    squadcast=squadcast_schema,
    bigpanda=bigpanda_schema,
    grafana_oncall=grafana_oncall_schema,
    zenduty=zenduty_schema,
    splunk_oncall=splunk_oncall_schema,
    jira_service_management=jira_service_management_schema,
    pagertree=pagertree_schema,
    alertops=alertops_schema,
    signl4=signl4_schema,
    ilert=ilert_schema,
    betterstack=betterstack_schema,
    onpage=onpage_schema,
    allquiet=allquiet_schema,
    moogsoft=moogsoft_schema,
    spikesh=spikesh_schema,
    dutycalls=dutycalls_schema,
    incidenthub=incidenthub_schema,
    resolver=resolver_schema,
    openduty=openduty_schema,
    cabot=cabot_schema,
    haloitsm=haloitsm_schema,
    incidentmanagerio=incidentmanagerio_schema,
    oneuptime=oneuptime_schema,
    squzy=squzy_schema,
    crisescontrol=crisescontrol_schema,
    freshservice=freshservice_schema,
    freshdesk=freshdesk_schema,
    happyfox=happyfox_schema,
    zendesk=zendesk_schema,
    zohodesk=zohodesk_schema,
    helpscout=helpscout_schema,
    kayako=kayako_schema,
    intercom=intercom_schema,
    front=front_schema,
    servicedeskplus=servicedeskplus_schema,
    sysaid=sysaid_schema,
    bmchelix=bmchelix_schema,
    solarwindsservicedesk=solarwindsservicedesk_schema,
    topdesk=topdesk_schema,
    invgateservicedesk=invgateservicedesk_schema,
    opsramp=opsramp_schema,
    updated_at=synced_at,
  )
