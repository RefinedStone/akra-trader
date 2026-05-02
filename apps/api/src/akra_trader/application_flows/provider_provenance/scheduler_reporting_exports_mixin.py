from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any
from typing import Iterable
import json
from numbers import Number
from uuid import uuid4

from akra_trader.domain.models import *  # noqa: F403


class ProviderProvenanceSchedulerReportingExportsMixin:
  def _available_provider_provenance_export_delivery_targets(self) -> tuple[str, ...]:
    return self._normalize_targets(self._operator_alert_delivery.list_targets())

  def _classify_provider_provenance_export_delivery_targets(
    self,
    available_targets: tuple[str, ...],
  ) -> tuple[tuple[str, ...], tuple[str, ...]]:
    chatops_targets: list[str] = []
    paging_targets: list[str] = []
    for target in available_targets:
      normalized_target = target.strip().lower().replace("-", "_")
      inferred_provider = self._infer_paging_provider(
        initial_targets=(target,),
        escalation_targets=(),
      )
      if (
        inferred_provider is not None
        or normalized_target.endswith("_incidents")
        or normalized_target.endswith("_alerts")
        or normalized_target == "pagerduty_events"
      ):
        paging_targets.append(target)
      else:
        chatops_targets.append(target)
    return tuple(chatops_targets), tuple(paging_targets)

  def _extract_provider_provenance_scheduler_export_context(
    self,
    *,
    content: str,
  ) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    try:
      decoded = json.loads(content)
    except json.JSONDecodeError:
      decoded = {}
    if isinstance(decoded, dict):
      payload = decoded
    current_payload = payload.get("current") if isinstance(payload.get("current"), dict) else {}
    history_payload = payload.get("history_page") if isinstance(payload.get("history_page"), dict) else {}
    scheduler_status = (
      current_payload.get("status").strip().lower()
      if isinstance(current_payload.get("status"), str) and current_payload.get("status").strip()
      else "unknown"
    )
    summary_text = (
      current_payload.get("summary").strip()
      if isinstance(current_payload.get("summary"), str) and current_payload.get("summary").strip()
      else ""
    )
    max_due_lag_seconds = (
      int(current_payload["max_due_lag_seconds"])
      if isinstance(current_payload.get("max_due_lag_seconds"), Number)
      else 0
    )
    due_report_count = (
      int(current_payload["due_report_count"])
      if isinstance(current_payload.get("due_report_count"), Number)
      else 0
    )
    history_total = (
      int(history_payload["total"])
      if isinstance(history_payload.get("total"), Number)
      else 0
    )
    return {
      "status": scheduler_status,
      "summary": summary_text,
      "max_due_lag_seconds": max_due_lag_seconds,
      "due_report_count": due_report_count,
      "history_total": history_total,
    }

  def _provider_provenance_scheduler_export_is_critical(
    self,
    *,
    scheduler_status: str,
    max_due_lag_seconds: int,
  ) -> bool:
    return (
      scheduler_status in {"failed", "failure", "error"}
      or max_due_lag_seconds >= self._provider_provenance_scheduler_critical_lag_seconds()
    )

  def _build_provider_provenance_scheduler_export_policy(
    self,
    *,
    content: str,
    routing_policy_id: str | None = None,
    delivery_targets: Iterable[str] | None = None,
    approval_policy_id: str | None = None,
    current_time: datetime,
    preserve_approval: ProviderProvenanceExportJobRecord | None = None,
  ) -> dict[str, Any]:
    available_targets = self._available_provider_provenance_export_delivery_targets()
    context = self._extract_provider_provenance_scheduler_export_context(content=content)
    critical_export = self._provider_provenance_scheduler_export_is_critical(
      scheduler_status=context["status"],
      max_due_lag_seconds=context["max_due_lag_seconds"],
    )
    if not available_targets:
      return {
        "available_delivery_targets": (),
        "routing_policy_id": "unconfigured",
        "routing_policy_summary": (
          "No operator delivery targets are configured for scheduler export escalation."
        ),
        "routing_targets": (),
        "approval_policy_id": "auto",
        "approval_required": False,
        "approval_state": "not_required",
        "approval_summary": "No delivery targets are configured for scheduler export escalation.",
        "approved_at": None,
        "approved_by": None,
        "approval_note": None,
        "paging_targets": (),
        "chatops_targets": (),
        "critical_export": critical_export,
        "context": context,
      }
    chatops_targets, paging_targets = self._classify_provider_provenance_export_delivery_targets(available_targets)
    resolved_routing_policy_id = (
      routing_policy_id.strip().lower()
      if isinstance(routing_policy_id, str) and routing_policy_id.strip()
      else "default"
    )
    if resolved_routing_policy_id == "default":
      if critical_export:
        selected_targets = available_targets
        resolved_routing_policy_id = "default_critical"
        routing_policy_summary = "Critical scheduler exports route to all configured delivery targets."
      elif chatops_targets:
        selected_targets = chatops_targets
        resolved_routing_policy_id = "chatops_only"
        routing_policy_summary = "Non-critical scheduler exports default to chatops/non-paging review targets."
      else:
        selected_targets = available_targets
        resolved_routing_policy_id = "all_targets"
        routing_policy_summary = "No dedicated chatops targets are configured, so the export routes to all targets."
    elif resolved_routing_policy_id == "all_targets":
      selected_targets = available_targets
      routing_policy_summary = "Route the scheduler export to all configured delivery targets."
    elif resolved_routing_policy_id == "chatops_only":
      if not chatops_targets:
        raise ValueError("No chatops/non-paging delivery targets are configured for scheduler export routing.")
      selected_targets = chatops_targets
      routing_policy_summary = "Route the scheduler export to chatops/non-paging review targets only."
    elif resolved_routing_policy_id == "paging_only":
      if not paging_targets:
        raise ValueError("No paging delivery targets are configured for scheduler export routing.")
      selected_targets = paging_targets
      routing_policy_summary = "Route the scheduler export directly to paging/incident delivery targets."
    elif resolved_routing_policy_id == "custom":
      if delivery_targets is None or not any(
        isinstance(target, str) and target.strip()
        for target in delivery_targets
      ):
        raise ValueError("Custom scheduler export routing requires at least one explicit delivery target.")
      selected_targets = self._resolve_provider_provenance_export_delivery_targets(
        delivery_targets=delivery_targets,
      )
      routing_policy_summary = "Route the scheduler export to the operator-selected delivery targets."
    else:
      raise ValueError(f"Unsupported scheduler export routing policy: {resolved_routing_policy_id}")
    selected_targets = self._normalize_targets(selected_targets)
    selected_target_set = set(selected_targets)
    selected_paging_targets = tuple(target for target in paging_targets if target in selected_target_set)
    selected_chatops_targets = tuple(target for target in chatops_targets if target in selected_target_set)
    resolved_approval_policy_id = (
      approval_policy_id.strip().lower()
      if isinstance(approval_policy_id, str) and approval_policy_id.strip()
      else "auto"
    )
    if resolved_approval_policy_id == "auto":
      if critical_export:
        approval_required = False
        approval_state = "approved"
        approval_summary = "Critical scheduler exports are auto-approved for immediate escalation."
        approved_at = current_time
        approved_by = "system:auto_policy"
        approval_note = "critical_scheduler_auto_approval"
      elif selected_paging_targets:
        approval_required = True
        approval_state = "pending"
        approval_summary = "Paging delivery targets require explicit operator approval before escalation."
        approved_at = None
        approved_by = None
        approval_note = None
      else:
        approval_required = False
        approval_state = "not_required"
        approval_summary = "Chatops-only scheduler routing does not require approval."
        approved_at = None
        approved_by = None
        approval_note = None
    elif resolved_approval_policy_id == "manual_required":
      approval_required = True
      approval_state = "pending"
      approval_summary = "Manual operator approval is required before the scheduler export can be escalated."
      approved_at = None
      approved_by = None
      approval_note = None
    else:
      raise ValueError(f"Unsupported scheduler export approval policy: {resolved_approval_policy_id}")
    if (
      preserve_approval is not None
      and preserve_approval.routing_policy_id == resolved_routing_policy_id
      and preserve_approval.routing_targets == selected_targets
      and preserve_approval.approval_policy_id == resolved_approval_policy_id
      and preserve_approval.approval_state == "approved"
    ):
      approval_required = preserve_approval.approval_required
      approval_state = preserve_approval.approval_state
      approval_summary = preserve_approval.approval_summary or approval_summary
      approved_at = preserve_approval.approved_at
      approved_by = preserve_approval.approved_by
      approval_note = preserve_approval.approval_note
    return {
      "available_delivery_targets": available_targets,
      "routing_policy_id": resolved_routing_policy_id,
      "routing_policy_summary": routing_policy_summary,
      "routing_targets": selected_targets,
      "approval_policy_id": resolved_approval_policy_id,
      "approval_required": approval_required,
      "approval_state": approval_state,
      "approval_summary": approval_summary,
      "approved_at": approved_at,
      "approved_by": approved_by,
      "approval_note": approval_note,
      "paging_targets": selected_paging_targets,
      "chatops_targets": selected_chatops_targets,
      "critical_export": critical_export,
      "context": context,
    }

  def _ensure_provider_provenance_scheduler_export_policy(
    self,
    record: ProviderProvenanceExportJobRecord,
  ) -> ProviderProvenanceExportJobRecord:
    if record.export_scope != "provider_provenance_scheduler_health":
      return record
    if record.available_delivery_targets and record.routing_policy_id and record.routing_targets:
      return record
    artifact_content = record.content
    if record.artifact_id:
      artifact_content = self.get_provider_provenance_export_artifact(record.artifact_id).content
    policy = self._build_provider_provenance_scheduler_export_policy(
      content=artifact_content,
      current_time=self._clock(),
    )
    return self._save_provider_provenance_export_job_record(
      replace(
        record,
        available_delivery_targets=policy["available_delivery_targets"],
        routing_policy_id=policy["routing_policy_id"],
        routing_policy_summary=policy["routing_policy_summary"],
        routing_targets=policy["routing_targets"],
        approval_policy_id=policy["approval_policy_id"],
        approval_required=policy["approval_required"],
        approval_state=policy["approval_state"],
        approval_summary=policy["approval_summary"],
        approved_at=policy["approved_at"],
        approved_by=policy["approved_by"],
        approval_note=policy["approval_note"],
      )
    )

  def _resolve_provider_provenance_export_delivery_targets(
    self,
    *,
    delivery_targets: Iterable[str] | None = None,
  ) -> tuple[str, ...]:
    available_targets = tuple(
      target.strip()
      for target in self._operator_alert_delivery.list_targets()
      if isinstance(target, str) and target.strip()
    )
    if delivery_targets is None:
      if not available_targets:
        raise RuntimeError("No operator delivery targets are configured for provider provenance export escalation.")
      return available_targets
    provided_targets = tuple(delivery_targets)
    normalized_targets: list[str] = []
    invalid_targets: list[str] = []
    available_target_set = set(available_targets)
    for target in provided_targets:
      if not isinstance(target, str) or not target.strip():
        continue
      candidate = target.strip()
      if candidate not in available_target_set:
        invalid_targets.append(candidate)
        continue
      if candidate not in normalized_targets:
        normalized_targets.append(candidate)
    if invalid_targets:
      raise ValueError(f"Unsupported provider provenance export delivery targets: {', '.join(sorted(set(invalid_targets)))}")
    if not normalized_targets:
      if available_targets:
        return available_targets
      raise RuntimeError("No operator delivery targets are configured for provider provenance export escalation.")
    return tuple(normalized_targets)

  def _build_provider_provenance_scheduler_export_incident(
    self,
    *,
    record: ProviderProvenanceExportJobRecord,
    content: str,
    actor: str,
    reason: str,
    current_time: datetime,
    delivery_targets: tuple[str, ...],
  ) -> OperatorIncidentEvent:
    context = self._extract_provider_provenance_scheduler_export_context(content=content)
    scheduler_status = context["status"]
    summary_text = (
      context["summary"]
      or (
        record.filter_summary.strip()
        if isinstance(record.filter_summary, str) and record.filter_summary.strip()
        else "Scheduler health export requires operator review."
      )
    )
    max_due_lag_seconds = context["max_due_lag_seconds"]
    due_report_count = context["due_report_count"]
    history_total = context["history_total"] or record.result_count
    severity = (
      "critical"
      if self._provider_provenance_scheduler_export_is_critical(
        scheduler_status=scheduler_status,
        max_due_lag_seconds=max_due_lag_seconds,
      )
      else "warning"
    )
    return OperatorIncidentEvent(
      event_id=f"provider-provenance-scheduler-export:{record.job_id}:{current_time.isoformat()}",
      alert_id=f"provider-provenance:scheduler-export:{record.job_id}",
      timestamp=current_time,
      kind="incident_opened",
      severity=severity,
      summary=f"Provider provenance scheduler {scheduler_status.replace('_', ' ')} export escalated.",
      detail=(
        f"{summary_text} Escalation reason: {reason}. "
        f"Captured {history_total} scheduler record(s) with {due_report_count} due report(s) "
        f"and {max_due_lag_seconds}s peak lag. Requested by {actor}."
      ),
      source="runtime",
      delivery_targets=delivery_targets,
      escalation_targets=delivery_targets,
      external_reference=record.job_id,
    )

  def update_provider_provenance_export_job_routing_policy(
    self,
    job_id: str,
    *,
    actor: str = "operator",
    routing_policy_id: str = "default",
    approval_policy_id: str = "auto",
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
    delivery_targets: Iterable[str] | None = None,
  ) -> dict[str, Any]:
    record = self.get_provider_provenance_export_job(job_id)
    if record.export_scope != "provider_provenance_scheduler_health":
      raise ValueError("Only scheduler health export jobs support routing policy updates.")
    actor_value = actor.strip() if isinstance(actor, str) and actor.strip() else "operator"
    artifact_content = record.content
    if record.artifact_id:
      artifact_content = self.get_provider_provenance_export_artifact(record.artifact_id).content
    current_time = self._clock()
    policy = self._build_provider_provenance_scheduler_export_policy(
      content=artifact_content,
      routing_policy_id=routing_policy_id,
      delivery_targets=delivery_targets,
      approval_policy_id=approval_policy_id,
      current_time=current_time,
      preserve_approval=record,
    )
    updated_record = self._save_provider_provenance_export_job_record(
      replace(
        record,
        available_delivery_targets=policy["available_delivery_targets"],
        routing_policy_id=policy["routing_policy_id"],
        routing_policy_summary=policy["routing_policy_summary"],
        routing_targets=policy["routing_targets"],
        approval_policy_id=policy["approval_policy_id"],
        approval_required=policy["approval_required"],
        approval_state=policy["approval_state"],
        approval_summary=policy["approval_summary"],
        approved_at=policy["approved_at"],
        approved_by=policy["approved_by"],
        approval_note=policy["approval_note"],
      )
    )
    audit_record = self._record_provider_provenance_export_job_event(
      record=updated_record,
      action="policy_updated",
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
      detail=(
        f"Scheduler export routing policy set to {policy['routing_policy_id']} "
        f"with targets {', '.join(policy['routing_targets']) or 'none'}."
      ),
      routing_policy_id=policy["routing_policy_id"],
      routing_targets=policy["routing_targets"],
      approval_policy_id=policy["approval_policy_id"],
      approval_required=policy["approval_required"],
      approval_state=policy["approval_state"],
      approval_summary=policy["approval_summary"],
      approved_by=actor_value if policy["approval_state"] == "approved" else policy["approved_by"],
    )
    return {
      "export_job": updated_record,
      "audit_record": audit_record,
    }

  def approve_provider_provenance_export_job(
    self,
    job_id: str,
    *,
    actor: str = "operator",
    note: str | None = None,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> dict[str, Any]:
    record = self.get_provider_provenance_export_job(job_id)
    if record.export_scope != "provider_provenance_scheduler_health":
      raise ValueError("Only scheduler health export jobs support approval actions.")
    if not record.routing_targets:
      raise ValueError("Configure a scheduler export routing policy before requesting approval.")
    if not record.approval_required and record.approval_state != "pending":
      raise ValueError("The current scheduler export routing policy does not require approval.")
    actor_value = actor.strip() if isinstance(actor, str) and actor.strip() else "operator"
    note_value = note.strip() if isinstance(note, str) and note.strip() else "manual_operator_approval"
    current_time = self._clock()
    approval_summary = f"Approved by {actor_value} for delivery to {', '.join(record.routing_targets)}."
    updated_record = self._save_provider_provenance_export_job_record(
      replace(
        record,
        approval_state="approved",
        approval_summary=approval_summary,
        approved_at=current_time,
        approved_by=actor_value,
        approval_note=note_value,
      )
    )
    audit_record = self._record_provider_provenance_export_job_event(
      record=updated_record,
      action="approved",
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
      detail=approval_summary,
      routing_policy_id=updated_record.routing_policy_id,
      routing_targets=updated_record.routing_targets,
      approval_policy_id=updated_record.approval_policy_id,
      approval_required=updated_record.approval_required,
      approval_state=updated_record.approval_state,
      approval_summary=updated_record.approval_summary,
      approved_by=updated_record.approved_by,
    )
    return {
      "export_job": updated_record,
      "audit_record": audit_record,
    }

  def escalate_provider_provenance_export_job(
    self,
    job_id: str,
    *,
    actor: str = "operator",
    reason: str = "scheduler_health_review",
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
    delivery_targets: Iterable[str] | None = None,
  ) -> dict[str, Any]:
    record = self.get_provider_provenance_export_job(job_id)
    if record.export_scope != "provider_provenance_scheduler_health":
      raise ValueError("Only scheduler health export jobs support escalation.")
    actor_value = actor.strip() if isinstance(actor, str) and actor.strip() else "operator"
    reason_value = reason.strip() if isinstance(reason, str) and reason.strip() else "scheduler_health_review"
    artifact_content = record.content
    if record.artifact_id:
      artifact_content = self.get_provider_provenance_export_artifact(record.artifact_id).content
    if delivery_targets is not None and any(
      isinstance(target, str) and target.strip()
      for target in delivery_targets
    ):
      explicit_targets = self._normalize_targets(tuple(target for target in delivery_targets if isinstance(target, str)))
      if explicit_targets != record.routing_targets:
        raise ValueError("Update the scheduler export routing policy before using custom escalation targets.")
    resolved_targets = record.routing_targets
    if not resolved_targets:
      policy = self._build_provider_provenance_scheduler_export_policy(
        content=artifact_content,
        current_time=self._clock(),
        preserve_approval=record,
      )
      record = self._save_provider_provenance_export_job_record(
        replace(
          record,
          available_delivery_targets=policy["available_delivery_targets"],
          routing_policy_id=policy["routing_policy_id"],
          routing_policy_summary=policy["routing_policy_summary"],
          routing_targets=policy["routing_targets"],
          approval_policy_id=policy["approval_policy_id"],
          approval_required=policy["approval_required"],
          approval_state=policy["approval_state"],
          approval_summary=policy["approval_summary"],
          approved_at=policy["approved_at"],
          approved_by=policy["approved_by"],
          approval_note=policy["approval_note"],
        )
      )
      resolved_targets = record.routing_targets
    if not resolved_targets:
      raise RuntimeError("No scheduler export routing targets are configured for escalation.")
    if record.approval_required and record.approval_state != "approved":
      raise ValueError("Scheduler health export escalation requires approval before delivery.")
    current_time = self._clock()
    incident = self._build_provider_provenance_scheduler_export_incident(
      record=record,
      content=artifact_content,
      actor=actor_value,
      reason=reason_value,
      current_time=current_time,
      delivery_targets=resolved_targets,
    )
    delivery_history = self._operator_alert_delivery.deliver(
      incident=incident,
      targets=resolved_targets,
      phase="scheduler_export_escalation",
    )
    delivered_count = sum(1 for delivery in delivery_history if delivery.status == "delivered")
    failed_count = sum(1 for delivery in delivery_history if delivery.status != "delivered")
    delivery_status = (
      "delivered"
      if delivered_count and failed_count == 0
      else ("failed" if delivered_count == 0 else "partial_failure")
    )
    delivery_summary = (
      f"Scheduler health export escalated via {record.routing_policy_id or 'unconfigured_route'} to {', '.join(resolved_targets)} "
      f"({delivered_count} delivered, {failed_count} failed)."
    )
    updated_record = self._save_provider_provenance_export_job_record(
      replace(
        record,
        escalation_count=record.escalation_count + 1,
        last_escalated_at=current_time,
        last_escalated_by=actor_value,
        last_escalation_reason=reason_value,
        last_delivery_targets=resolved_targets,
        last_delivery_status=delivery_status,
        last_delivery_summary=delivery_summary,
      )
    )
    audit_record = self._record_provider_provenance_export_job_event(
      record=updated_record,
      action="escalated",
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
      detail=delivery_summary,
      routing_policy_id=updated_record.routing_policy_id,
      routing_targets=updated_record.routing_targets,
      approval_policy_id=updated_record.approval_policy_id,
      approval_required=updated_record.approval_required,
      approval_state=updated_record.approval_state,
      approval_summary=updated_record.approval_summary,
      approved_by=updated_record.approved_by,
      delivery_targets=resolved_targets,
      delivery_status=delivery_status,
      delivery_summary=delivery_summary,
    )
    return {
      "export_job": updated_record,
      "audit_record": audit_record,
      "delivery_history": delivery_history,
    }
