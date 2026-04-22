from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from akra_trader.domain.model_types.provider_provenance import ProviderProvenanceSchedulerHealth

@dataclass(frozen=True)
class OperatorAlertPrimaryFocus:
  symbol: str | None = None
  timeframe: str | None = None
  candidate_symbols: tuple[str, ...] = ()
  candidate_count: int = 0
  policy: str = "none"
  reason: str | None = None


@dataclass(frozen=True)
class OperatorAlertMarketContextFieldProvenance:
  scope: str | None = None
  path: str | None = None


@dataclass(frozen=True)
class OperatorAlertMarketContextProvenance:
  provider: str | None = None
  vendor_field: str | None = None
  symbol: OperatorAlertMarketContextFieldProvenance | None = None
  symbols: OperatorAlertMarketContextFieldProvenance | None = None
  timeframe: OperatorAlertMarketContextFieldProvenance | None = None
  primary_focus: OperatorAlertMarketContextFieldProvenance | None = None


@dataclass(frozen=True)
class OperatorAlert:
  alert_id: str
  severity: str
  category: str
  summary: str
  detail: str
  detected_at: datetime
  run_id: str | None = None
  session_id: str | None = None
  symbol: str | None = None
  symbols: tuple[str, ...] = ()
  timeframe: str | None = None
  primary_focus: OperatorAlertPrimaryFocus | None = None
  occurrence_id: str | None = None
  timeline_key: str | None = None
  timeline_position: int | None = None
  timeline_total: int | None = None
  status: str = "active"
  resolved_at: datetime | None = None
  source: str = "runtime"
  delivery_targets: tuple[str, ...] = ()


@dataclass(frozen=True)
class OperatorAuditEvent:
  event_id: str
  timestamp: datetime
  actor: str
  kind: str
  summary: str
  detail: str
  run_id: str | None = None
  session_id: str | None = None
  source: str = "runtime"


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
class OperatorIncidentProviderRecoveryVerification:
  state: str = "unknown"
  checked_at: datetime | None = None
  summary: str | None = None
  issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class OperatorIncidentProviderRecoveryStatusMachine:
  state: str = "not_requested"
  workflow_state: str = "idle"
  workflow_action: str | None = None
  job_state: str = "not_started"
  sync_state: str = "not_synced"
  last_event_kind: str | None = None
  last_event_at: datetime | None = None
  last_detail: str | None = None
  attempt_number: int = 0


@dataclass(frozen=True)
class OperatorIncidentProviderRecoveryTelemetry:
  source: str = "unknown"
  state: str = "unknown"
  progress_percent: int | None = None
  attempt_count: int = 0
  current_step: str | None = None
  last_message: str | None = None
  last_error: str | None = None
  external_run_id: str | None = None
  job_url: str | None = None
  started_at: datetime | None = None
  finished_at: datetime | None = None
  updated_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentPagerDutyRecoveryState:
  incident_id: str | None = None
  incident_key: str | None = None
  incident_status: str = "unknown"
  urgency: str | None = None
  service_id: str | None = None
  service_summary: str | None = None
  escalation_policy_id: str | None = None
  escalation_policy_summary: str | None = None
  html_url: str | None = None
  last_status_change_at: datetime | None = None
  phase_graph: "OperatorIncidentPagerDutyRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentPagerDutyRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentPagerDutyRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  responder_phase: str = "unknown"
  urgency_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentOpsgenieRecoveryState:
  alert_id: str | None = None
  alias: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  owner: str | None = None
  acknowledged: bool | None = None
  seen: bool | None = None
  tiny_id: str | None = None
  teams: tuple[str, ...] = ()
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentOpsgenieRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentOpsgenieRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentOpsgenieRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  acknowledgment_phase: str = "unknown"
  ownership_phase: str = "unknown"
  visibility_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentIncidentIoRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity: str | None = None
  mode: str | None = None
  visibility: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentIncidentIoRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentIncidentIoRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentIncidentIoRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  assignment_phase: str = "unknown"
  visibility_phase: str = "unknown"
  severity_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentFireHydrantRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity: str | None = None
  priority: str | None = None
  team: str | None = None
  runbook: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentFireHydrantRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentFireHydrantRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentFireHydrantRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  severity_phase: str = "unknown"
  priority_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentRootlyRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity_id: str | None = None
  private: bool | None = None
  slug: str | None = None
  url: str | None = None
  acknowledged_at: datetime | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentRootlyRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentRootlyRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentRootlyRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  acknowledgment_phase: str = "unknown"
  visibility_phase: str = "unknown"
  severity_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentBlamelessRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity: str | None = None
  commander: str | None = None
  visibility: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentBlamelessRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentBlamelessRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentBlamelessRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  command_phase: str = "unknown"
  visibility_phase: str = "unknown"
  severity_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentXmattersRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  priority: str | None = None
  assignee: str | None = None
  response_plan: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentXmattersRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentXmattersRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentXmattersRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  response_plan_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentServicenowRecoveryState:
  incident_number: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  priority: str | None = None
  assigned_to: str | None = None
  assignment_group: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentServicenowRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentServicenowRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentServicenowRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  assignment_phase: str = "unknown"
  priority_phase: str = "unknown"
  group_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentSquadcastRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity: str | None = None
  assignee: str | None = None
  escalation_policy: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentSquadcastRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentSquadcastRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentSquadcastRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  severity_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentBigPandaRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity: str | None = None
  assignee: str | None = None
  team: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentBigPandaRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentBigPandaRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentBigPandaRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  severity_phase: str = "unknown"
  team_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentGrafanaOnCallRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity: str | None = None
  assignee: str | None = None
  escalation_chain: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentGrafanaOnCallRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentGrafanaOnCallRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentGrafanaOnCallRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  severity_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentZendutyRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity: str | None = None
  assignee: str | None = None
  service: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentZendutyRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentZendutyRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentZendutyRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  severity_phase: str = "unknown"
  service_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentSplunkOnCallRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  severity: str | None = None
  assignee: str | None = None
  routing_key: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentSplunkOnCallRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentSplunkOnCallRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentSplunkOnCallRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  severity_phase: str = "unknown"
  routing_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentJiraServiceManagementRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  priority: str | None = None
  assignee: str | None = None
  service_project: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentJiraServiceManagementRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentJiraServiceManagementRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentJiraServiceManagementRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  assignment_phase: str = "unknown"
  priority_phase: str = "unknown"
  project_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentPagerTreeRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  urgency: str | None = None
  assignee: str | None = None
  team: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentPagerTreeRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentPagerTreeRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentPagerTreeRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  urgency_phase: str = "unknown"
  team_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentAlertOpsRecoveryState:
  incident_id: str | None = None
  external_reference: str | None = None
  incident_status: str = "unknown"
  priority: str | None = None
  owner: str | None = None
  service: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentAlertOpsRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentAlertOpsRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentAlertOpsRecoveryPhaseGraph:
  incident_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  service_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentSignl4RecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  team: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentSignl4RecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentSignl4RecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentSignl4RecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  team_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentIlertRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentIlertRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentIlertRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentIlertRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentBetterstackRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentBetterstackRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentBetterstackRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentBetterstackRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentOnpageRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentOnpageRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentOnpageRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentOnpageRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentAllquietRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentAllquietRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentAllquietRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentAllquietRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentMoogsoftRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentMoogsoftRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentMoogsoftRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentMoogsoftRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentSpikeshRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentSpikeshRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentSpikeshRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentSpikeshRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentDutyCallsRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentDutyCallsRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentDutyCallsRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentDutyCallsRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentIncidentHubRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentIncidentHubRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentIncidentHubRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentIncidentHubRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentResolverRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentResolverRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentResolverRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentResolverRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentOpenDutyRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentOpenDutyRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentOpenDutyRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentOpenDutyRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentCabotRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentCabotRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentCabotRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentCabotRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentHaloItsmRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentHaloItsmRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentHaloItsmRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentHaloItsmRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentIncidentManagerIoRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentIncidentManagerIoRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentIncidentManagerIoRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentIncidentManagerIoRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentOneUptimeRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentOneUptimeRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentOneUptimeRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentOneUptimeRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentSquzyRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentSquzyRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentSquzyRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentSquzyRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentCrisesControlRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentCrisesControlRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentCrisesControlRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentCrisesControlRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentFreshserviceRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentFreshserviceRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentFreshserviceRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentFreshserviceRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentFreshdeskRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentFreshdeskRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentFreshdeskRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentFreshdeskRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentHappyfoxRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentHappyfoxRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentHappyfoxRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentHappyfoxRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentZendeskRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentZendeskRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentZendeskRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentZendeskRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentZohoDeskRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentZohoDeskRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentZohoDeskRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentZohoDeskRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentHelpScoutRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentHelpScoutRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentHelpScoutRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentHelpScoutRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentKayakoRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentKayakoRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentKayakoRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentKayakoRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentIntercomRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentIntercomRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentIntercomRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentIntercomRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentFrontRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentFrontRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentFrontRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentFrontRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentServiceDeskPlusRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentServiceDeskPlusRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentServiceDeskPlusRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentServiceDeskPlusRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentSysAidRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentSysAidRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentSysAidRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentSysAidRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentBmcHelixRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentBmcHelixRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentBmcHelixRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentBmcHelixRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentSolarWindsServiceDeskRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentSolarWindsServiceDeskRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentSolarWindsServiceDeskRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentSolarWindsServiceDeskRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentTopdeskRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentTopdeskRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentTopdeskRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentTopdeskRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentInvGateServiceDeskRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentInvGateServiceDeskRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentInvGateServiceDeskRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentInvGateServiceDeskRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


@dataclass(frozen=True)
class OperatorIncidentOpsRampRecoveryState:
  alert_id: str | None = None
  external_reference: str | None = None
  alert_status: str = "unknown"
  priority: str | None = None
  escalation_policy: str | None = None
  assignee: str | None = None
  url: str | None = None
  updated_at: datetime | None = None
  phase_graph: "OperatorIncidentOpsRampRecoveryPhaseGraph" = field(
    default_factory=lambda: OperatorIncidentOpsRampRecoveryPhaseGraph()
  )


@dataclass(frozen=True)
class OperatorIncidentOpsRampRecoveryPhaseGraph:
  alert_phase: str = "unknown"
  workflow_phase: str = "unknown"
  ownership_phase: str = "unknown"
  priority_phase: str = "unknown"
  escalation_phase: str = "unknown"
  last_transition_at: datetime | None = None


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
