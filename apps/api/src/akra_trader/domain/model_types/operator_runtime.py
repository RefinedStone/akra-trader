from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from akra_trader.domain.model_types.provider_provenance import ProviderProvenanceSchedulerHealth

from akra_trader.domain.model_types.operator_runtime_common import *
from akra_trader.domain.model_types.operator_runtime_recovery_primary import *
from akra_trader.domain.model_types.operator_runtime_recovery_secondary import *

@dataclass(frozen=True)
class OperatorIncidentRemediation:
  state: str = "not_applicable"
  kind: str | None = None
  owner: str | None = None
  summary: str | None = None
  detail: str | None = None
  runbook: str | None = None
  requested_at: datetime | None = None
  requested_by: str | None = None
  last_attempted_at: datetime | None = None
  provider: str | None = None
  reference: str | None = None
  provider_payload: dict[str, Any] = field(default_factory=dict)
  provider_payload_updated_at: datetime | None = None
  provider_recovery: "OperatorIncidentProviderRecoveryState" = field(
    default_factory=lambda: OperatorIncidentProviderRecoveryState()
  )



@dataclass(frozen=True)
class OperatorIncidentProviderRecoveryState:
  lifecycle_state: str = "not_synced"
  provider: str | None = None
  job_id: str | None = None
  reference: str | None = None
  workflow_reference: str | None = None
  summary: str | None = None
  detail: str | None = None
  channels: tuple[str, ...] = ()
  symbols: tuple[str, ...] = ()
  timeframe: str | None = None
  primary_focus: OperatorAlertPrimaryFocus | None = None
  market_context_provenance: OperatorAlertMarketContextProvenance | None = None
  verification: OperatorIncidentProviderRecoveryVerification = field(
    default_factory=OperatorIncidentProviderRecoveryVerification
  )
  telemetry: OperatorIncidentProviderRecoveryTelemetry = field(
    default_factory=OperatorIncidentProviderRecoveryTelemetry
  )
  status_machine: OperatorIncidentProviderRecoveryStatusMachine = field(
    default_factory=OperatorIncidentProviderRecoveryStatusMachine
  )
  provider_schema_kind: str | None = None
  pagerduty: OperatorIncidentPagerDutyRecoveryState = field(
    default_factory=OperatorIncidentPagerDutyRecoveryState
  )
  opsgenie: OperatorIncidentOpsgenieRecoveryState = field(
    default_factory=OperatorIncidentOpsgenieRecoveryState
  )
  incidentio: OperatorIncidentIncidentIoRecoveryState = field(
    default_factory=OperatorIncidentIncidentIoRecoveryState
  )
  firehydrant: OperatorIncidentFireHydrantRecoveryState = field(
    default_factory=OperatorIncidentFireHydrantRecoveryState
  )
  rootly: OperatorIncidentRootlyRecoveryState = field(
    default_factory=OperatorIncidentRootlyRecoveryState
  )
  blameless: OperatorIncidentBlamelessRecoveryState = field(
    default_factory=OperatorIncidentBlamelessRecoveryState
  )
  xmatters: OperatorIncidentXmattersRecoveryState = field(
    default_factory=OperatorIncidentXmattersRecoveryState
  )
  servicenow: OperatorIncidentServicenowRecoveryState = field(
    default_factory=OperatorIncidentServicenowRecoveryState
  )
  squadcast: OperatorIncidentSquadcastRecoveryState = field(
    default_factory=OperatorIncidentSquadcastRecoveryState
  )
  bigpanda: OperatorIncidentBigPandaRecoveryState = field(
    default_factory=OperatorIncidentBigPandaRecoveryState
  )
  grafana_oncall: OperatorIncidentGrafanaOnCallRecoveryState = field(
    default_factory=OperatorIncidentGrafanaOnCallRecoveryState
  )
  zenduty: OperatorIncidentZendutyRecoveryState = field(
    default_factory=OperatorIncidentZendutyRecoveryState
  )
  splunk_oncall: OperatorIncidentSplunkOnCallRecoveryState = field(
    default_factory=OperatorIncidentSplunkOnCallRecoveryState
  )
  jira_service_management: OperatorIncidentJiraServiceManagementRecoveryState = field(
    default_factory=OperatorIncidentJiraServiceManagementRecoveryState
  )
  pagertree: OperatorIncidentPagerTreeRecoveryState = field(
    default_factory=OperatorIncidentPagerTreeRecoveryState
  )
  alertops: OperatorIncidentAlertOpsRecoveryState = field(
    default_factory=OperatorIncidentAlertOpsRecoveryState
  )
  signl4: OperatorIncidentSignl4RecoveryState = field(
    default_factory=OperatorIncidentSignl4RecoveryState
  )
  ilert: OperatorIncidentIlertRecoveryState = field(
    default_factory=OperatorIncidentIlertRecoveryState
  )
  betterstack: OperatorIncidentBetterstackRecoveryState = field(
    default_factory=OperatorIncidentBetterstackRecoveryState
  )
  onpage: OperatorIncidentOnpageRecoveryState = field(
    default_factory=OperatorIncidentOnpageRecoveryState
  )
  allquiet: OperatorIncidentAllquietRecoveryState = field(
    default_factory=OperatorIncidentAllquietRecoveryState
  )
  moogsoft: OperatorIncidentMoogsoftRecoveryState = field(
    default_factory=OperatorIncidentMoogsoftRecoveryState
  )
  spikesh: OperatorIncidentSpikeshRecoveryState = field(
    default_factory=OperatorIncidentSpikeshRecoveryState
  )
  dutycalls: OperatorIncidentDutyCallsRecoveryState = field(
    default_factory=OperatorIncidentDutyCallsRecoveryState
  )
  incidenthub: OperatorIncidentIncidentHubRecoveryState = field(
    default_factory=OperatorIncidentIncidentHubRecoveryState
  )
  resolver: OperatorIncidentResolverRecoveryState = field(
    default_factory=OperatorIncidentResolverRecoveryState
  )
  openduty: OperatorIncidentOpenDutyRecoveryState = field(
    default_factory=OperatorIncidentOpenDutyRecoveryState
  )
  cabot: OperatorIncidentCabotRecoveryState = field(
    default_factory=OperatorIncidentCabotRecoveryState
  )
  haloitsm: OperatorIncidentHaloItsmRecoveryState = field(
    default_factory=OperatorIncidentHaloItsmRecoveryState
  )
  incidentmanagerio: OperatorIncidentIncidentManagerIoRecoveryState = field(
    default_factory=OperatorIncidentIncidentManagerIoRecoveryState
  )
  oneuptime: OperatorIncidentOneUptimeRecoveryState = field(
    default_factory=OperatorIncidentOneUptimeRecoveryState
  )
  squzy: OperatorIncidentSquzyRecoveryState = field(
    default_factory=OperatorIncidentSquzyRecoveryState
  )
  crisescontrol: OperatorIncidentCrisesControlRecoveryState = field(
    default_factory=OperatorIncidentCrisesControlRecoveryState
  )
  freshservice: OperatorIncidentFreshserviceRecoveryState = field(
    default_factory=OperatorIncidentFreshserviceRecoveryState
  )
  freshdesk: OperatorIncidentFreshdeskRecoveryState = field(
    default_factory=OperatorIncidentFreshdeskRecoveryState
  )
  happyfox: OperatorIncidentHappyfoxRecoveryState = field(
    default_factory=OperatorIncidentHappyfoxRecoveryState
  )
  zendesk: OperatorIncidentZendeskRecoveryState = field(
    default_factory=OperatorIncidentZendeskRecoveryState
  )
  zohodesk: OperatorIncidentZohoDeskRecoveryState = field(
    default_factory=OperatorIncidentZohoDeskRecoveryState
  )
  helpscout: OperatorIncidentHelpScoutRecoveryState = field(
    default_factory=OperatorIncidentHelpScoutRecoveryState
  )
  kayako: OperatorIncidentKayakoRecoveryState = field(
    default_factory=OperatorIncidentKayakoRecoveryState
  )
  intercom: OperatorIncidentIntercomRecoveryState = field(
    default_factory=OperatorIncidentIntercomRecoveryState
  )
  front: OperatorIncidentFrontRecoveryState = field(
    default_factory=OperatorIncidentFrontRecoveryState
  )
  servicedeskplus: OperatorIncidentServiceDeskPlusRecoveryState = field(
    default_factory=OperatorIncidentServiceDeskPlusRecoveryState
  )
  sysaid: OperatorIncidentSysAidRecoveryState = field(
    default_factory=OperatorIncidentSysAidRecoveryState
  )
  bmchelix: OperatorIncidentBmcHelixRecoveryState = field(
    default_factory=OperatorIncidentBmcHelixRecoveryState
  )
  solarwindsservicedesk: OperatorIncidentSolarWindsServiceDeskRecoveryState = field(
    default_factory=OperatorIncidentSolarWindsServiceDeskRecoveryState
  )
  topdesk: OperatorIncidentTopdeskRecoveryState = field(
    default_factory=OperatorIncidentTopdeskRecoveryState
  )
  invgateservicedesk: OperatorIncidentInvGateServiceDeskRecoveryState = field(
    default_factory=OperatorIncidentInvGateServiceDeskRecoveryState
  )
  opsramp: OperatorIncidentOpsRampRecoveryState = field(
    default_factory=OperatorIncidentOpsRampRecoveryState
  )
  updated_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentProviderPullSync:
  provider: str
  workflow_reference: str | None = None
  external_reference: str | None = None
  workflow_state: str = "unknown"
  remediation_state: str | None = None
  detail: str | None = None
  payload: dict[str, Any] = field(default_factory=dict)
  synced_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class OperatorIncidentEvent:
  event_id: str
  alert_id: str
  timestamp: datetime
  kind: str
  severity: str
  summary: str
  detail: str
  run_id: str | None = None
  session_id: str | None = None
  symbol: str | None = None
  symbols: tuple[str, ...] = ()
  timeframe: str | None = None
  primary_focus: OperatorAlertPrimaryFocus | None = None
  source: str = "guarded_live"
  paging_policy_id: str = "default"
  paging_provider: str | None = None
  delivery_targets: tuple[str, ...] = ()
  escalation_targets: tuple[str, ...] = ()
  delivery_state: str = "pending"
  acknowledgment_state: str = "not_applicable"
  acknowledged_at: datetime | None = None
  acknowledged_by: str | None = None
  acknowledgment_reason: str | None = None
  escalation_level: int = 0
  escalation_state: str = "not_applicable"
  last_escalated_at: datetime | None = None
  last_escalated_by: str | None = None
  escalation_reason: str | None = None
  lineage_evidence_pack_id: str | None = None
  lineage_evidence_retention_expires_at: datetime | None = None
  lineage_evidence_summary: str | None = None
  next_escalation_at: datetime | None = None
  external_provider: str | None = None
  external_reference: str | None = None
  provider_workflow_reference: str | None = None
  external_status: str = "not_synced"
  external_last_synced_at: datetime | None = None
  paging_status: str = "not_configured"
  provider_workflow_state: str = "not_configured"
  provider_workflow_action: str | None = None
  provider_workflow_last_attempted_at: datetime | None = None
  remediation: OperatorIncidentRemediation = field(default_factory=OperatorIncidentRemediation)


@dataclass(frozen=True)
class OperatorIncidentDelivery:
  delivery_id: str
  incident_event_id: str
  alert_id: str
  incident_kind: str
  target: str
  status: str
  attempted_at: datetime
  detail: str
  attempt_number: int = 1
  next_retry_at: datetime | None = None
  phase: str = "initial"
  provider_action: str | None = None
  external_provider: str | None = None
  external_reference: str | None = None
  source: str = "guarded_live"


@dataclass(frozen=True)
class OperatorVisibility:
  generated_at: datetime
  alerts: tuple[OperatorAlert, ...] = ()
  alert_history: tuple[OperatorAlert, ...] = ()
  incident_events: tuple[OperatorIncidentEvent, ...] = ()
  delivery_history: tuple[OperatorIncidentDelivery, ...] = ()
  audit_events: tuple[OperatorAuditEvent, ...] = ()
  provider_provenance_scheduler: ProviderProvenanceSchedulerHealth | None = None
