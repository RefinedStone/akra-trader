from __future__ import annotations


from akra_trader.adapters.operator_delivery_alert_phase_resolvers import OperatorDeliveryAlertPhaseResolverMixin


class OperatorDeliveryPhaseResolverMixin(OperatorDeliveryAlertPhaseResolverMixin):
  @staticmethod
  def _resolve_pagerduty_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {"triggered", "acknowledged", "resolved"}:
      return normalized
    return "unknown"
  def _resolve_pagerduty_responder_phase(incident_phase: str) -> str:
    if incident_phase == "triggered":
      return "awaiting_acknowledgment"
    if incident_phase == "acknowledged":
      return "engaged"
    if incident_phase == "resolved":
      return "resolved"
    return "unknown"

  @staticmethod
  def _resolve_pagerduty_urgency_phase(urgency: str | None) -> str:
    normalized = (urgency or "").strip().lower().replace(" ", "_")
    if normalized == "high":
      return "high_urgency"
    if normalized == "low":
      return "low_urgency"
    return "unknown"

  @staticmethod
  def _resolve_pagerduty_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state == "resolved":
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    return "idle"

  @staticmethod
  def _resolve_opsgenie_alert_phase(status: str | None, acknowledged: bool | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {"open", "acknowledged", "closed"}:
      return normalized
    if acknowledged is True:
      return "acknowledged"
    return "unknown"

  @staticmethod
  def _resolve_opsgenie_acknowledgment_phase(alert_phase: str, acknowledged: bool | None) -> str:
    if alert_phase == "closed":
      return "closed"
    if acknowledged is True or alert_phase == "acknowledged":
      return "acknowledged"
    if alert_phase == "open":
      return "pending_acknowledgment"
    return "unknown"

  @staticmethod
  def _resolve_opsgenie_ownership_phase(owner: str | None, teams: list[str]) -> str:
    if owner:
      return "assigned"
    if teams:
      return "team_routed"
    return "unknown"

  @staticmethod
  def _resolve_opsgenie_visibility_phase(seen: bool | None) -> str:
    if seen is True:
      return "seen"
    if seen is False:
      return "unseen"
    return "unknown"

  @staticmethod
  def _resolve_opsgenie_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state == "closed":
      return "closed_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_close"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "recovery_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "alert_acknowledged"
    return "idle"

  @staticmethod
  def _resolve_incidentio_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {"active", "acknowledged", "resolved", "closed"}:
      return normalized
    if normalized in {"triaged"}:
      return "acknowledged"
    return "unknown"

  @staticmethod
  def _resolve_incidentio_assignment_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_incidentio_visibility_phase(visibility: str | None) -> str:
    normalized = (visibility or "").strip().lower().replace(" ", "_")
    if normalized in {"public", "private"}:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_incidentio_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized in {"critical", "high", "warning", "medium", "low"}:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_incidentio_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"closed", "resolved"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    return "idle"

  @staticmethod
  def _resolve_firehydrant_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {"open", "investigating", "mitigating", "monitoring", "resolved", "closed"}:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_firehydrant_ownership_phase(team: str | None) -> str:
    if team:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_firehydrant_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized in {"sev1", "critical"}:
      return "critical"
    if normalized in {"sev2", "high"}:
      return "high"
    if normalized in {"sev3", "medium"}:
      return "medium"
    if normalized in {"sev4", "low"}:
      return "low"
    return "unknown"

  @staticmethod
  def _resolve_firehydrant_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized in {"p1", "critical"}:
      return "critical"
    if normalized in {"p2", "high"}:
      return "high"
    if normalized in {"p3", "medium"}:
      return "medium"
    if normalized in {"p4", "low"}:
      return "low"
    return "unknown"

  @staticmethod
  def _resolve_firehydrant_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"closed", "resolved"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"investigating", "mitigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_rootly_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "open",
      "started",
      "acknowledged",
      "investigating",
      "mitigating",
      "monitoring",
      "resolved",
      "closed",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_rootly_acknowledgment_phase(
    *,
    incident_phase: str,
    acknowledged_at: str | None,
  ) -> str:
    if incident_phase in {"resolved", "closed"}:
      return "closed"
    if acknowledged_at:
      return "acknowledged"
    if incident_phase == "acknowledged":
      return "acknowledged"
    if incident_phase in {"open", "started", "investigating", "mitigating", "monitoring"}:
      return "pending_acknowledgment"
    return "unknown"

  @staticmethod
  def _resolve_rootly_visibility_phase(private: bool | None) -> str:
    if private is True:
      return "private"
    if private is False:
      return "public"
    return "unknown"

  @staticmethod
  def _resolve_rootly_severity_phase(severity_id: str | None) -> str:
    normalized = (severity_id or "").strip().lower().replace(" ", "_")
    return normalized or "unknown"

  @staticmethod
  def _resolve_rootly_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"open", "started", "investigating", "mitigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_blameless_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "open",
      "started",
      "acknowledged",
      "investigating",
      "mitigating",
      "monitoring",
      "resolved",
      "closed",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_blameless_command_phase(commander: str | None) -> str:
    return "assigned" if commander else "unassigned"

  @staticmethod
  def _resolve_blameless_visibility_phase(visibility: str | None) -> str:
    normalized = (visibility or "").strip().lower().replace(" ", "_")
    if normalized in {"public", "private", "internal"}:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_blameless_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    return normalized or "unknown"

  @staticmethod
  def _resolve_blameless_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"open", "started", "investigating", "mitigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_xmatters_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "open",
      "started",
      "acknowledged",
      "investigating",
      "mitigating",
      "monitoring",
      "resolved",
      "closed",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_xmatters_ownership_phase(assignee: str | None) -> str:
    return "assigned" if assignee else "unassigned"

  @staticmethod
  def _resolve_xmatters_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    return normalized or "unknown"

  @staticmethod
  def _resolve_xmatters_response_plan_phase(response_plan: str | None) -> str:
    return "configured" if response_plan else "unconfigured"

  @staticmethod
  def _resolve_xmatters_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"open", "started", "investigating", "mitigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_servicenow_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "new",
      "open",
      "acknowledged",
      "in_progress",
      "on_hold",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_servicenow_assignment_phase(
    *,
    assigned_to: str | None,
    assignment_group: str | None,
  ) -> str:
    if assigned_to:
      return "assigned_to_user"
    if assignment_group:
      return "assigned_to_group"
    return "unassigned"

  @staticmethod
  def _resolve_servicenow_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    return normalized or "unknown"

  @staticmethod
  def _resolve_servicenow_group_phase(assignment_group: str | None) -> str:
    return "group_configured" if assignment_group else "group_unconfigured"

  @staticmethod
  def _resolve_servicenow_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"new", "open", "in_progress", "on_hold"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_squadcast_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "investigating",
      "on_hold",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_squadcast_ownership_phase(assignee: str | None) -> str:
    return "assigned" if assignee else "unassigned"

  @staticmethod
  def _resolve_squadcast_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    return normalized or "unknown"

  @staticmethod
  def _resolve_squadcast_escalation_phase(escalation_policy: str | None) -> str:
    return "configured" if escalation_policy else "unconfigured"

  @staticmethod
  def _resolve_squadcast_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "investigating", "on_hold"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_bigpanda_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_bigpanda_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_bigpanda_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_bigpanda_team_phase(team: str | None) -> str:
    if team:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_bigpanda_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_grafana_oncall_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_grafana_oncall_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_grafana_oncall_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_grafana_oncall_escalation_phase(escalation_chain: str | None) -> str:
    if escalation_chain:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_grafana_oncall_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_zenduty_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_zenduty_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_zenduty_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_zenduty_service_phase(service: str | None) -> str:
    if service:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_zenduty_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_splunk_oncall_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_splunk_oncall_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_splunk_oncall_severity_phase(severity: str | None) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_splunk_oncall_routing_phase(routing_key: str | None) -> str:
    if routing_key:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_splunk_oncall_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_jira_service_management_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "in_progress",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_jira_service_management_assignment_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_jira_service_management_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_jira_service_management_project_phase(service_project: str | None) -> str:
    if service_project:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_jira_service_management_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "in_progress", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_pagertree_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "in_progress",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_pagertree_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_pagertree_urgency_phase(urgency: str | None) -> str:
    normalized = (urgency or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_pagertree_team_phase(team: str | None) -> str:
    if team:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_pagertree_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "in_progress", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  @staticmethod
  def _resolve_alertops_incident_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "in_progress",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
      "escalated",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_alertops_ownership_phase(owner: str | None) -> str:
    if owner:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_alertops_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_alertops_service_phase(service: str | None) -> str:
    if service:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_alertops_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "in_progress", "investigating", "monitoring", "escalated"}:
      return "incident_active"
    return "idle"
