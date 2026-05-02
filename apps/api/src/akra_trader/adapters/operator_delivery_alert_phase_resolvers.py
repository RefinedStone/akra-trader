from __future__ import annotations



class OperatorDeliveryAlertPhaseResolverMixin:
  @staticmethod
  def _resolve_signl4_alert_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "in_progress",
      "investigating",
      "monitoring",
      "escalated",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_signl4_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_signl4_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_signl4_team_phase(team: str | None) -> str:
    if team:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_signl4_workflow_phase(
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
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "in_progress", "investigating", "monitoring", "escalated"}:
      return "alert_active"
    return "idle"

  @staticmethod
  def _resolve_ilert_alert_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "escalated",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_ilert_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_ilert_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_ilert_escalation_phase(escalation_policy: str | None) -> str:
    if escalation_policy:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_ilert_workflow_phase(
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
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  @staticmethod
  def _resolve_betterstack_alert_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "escalated",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_betterstack_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_betterstack_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_betterstack_escalation_phase(escalation_policy: str | None) -> str:
    if escalation_policy:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_betterstack_workflow_phase(
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
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  @staticmethod
  def _resolve_onpage_alert_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "escalated",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_onpage_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_onpage_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_onpage_escalation_phase(escalation_policy: str | None) -> str:
    if escalation_policy:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_onpage_workflow_phase(
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
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  @staticmethod
  def _resolve_allquiet_alert_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "escalated",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_allquiet_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_allquiet_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_allquiet_escalation_phase(escalation_policy: str | None) -> str:
    if escalation_policy:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_allquiet_workflow_phase(
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
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  @staticmethod
  def _resolve_moogsoft_alert_phase(status: str | None) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "escalated",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_moogsoft_ownership_phase(assignee: str | None) -> str:
    if assignee:
      return "assigned"
    return "unassigned"

  @staticmethod
  def _resolve_moogsoft_priority_phase(priority: str | None) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return "unknown"

  @staticmethod
  def _resolve_moogsoft_escalation_phase(escalation_policy: str | None) -> str:
    if escalation_policy:
      return "configured"
    return "unconfigured"

  @staticmethod
  def _resolve_moogsoft_workflow_phase(
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
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"
