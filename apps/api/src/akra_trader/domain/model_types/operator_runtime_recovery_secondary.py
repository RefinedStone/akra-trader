from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from akra_trader.domain.model_types.provider_provenance import ProviderProvenanceSchedulerHealth

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
