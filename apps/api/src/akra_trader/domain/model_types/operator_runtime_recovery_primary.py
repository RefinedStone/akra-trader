from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from akra_trader.domain.model_types.provider_provenance import ProviderProvenanceSchedulerHealth

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
