from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any
from typing import Iterable
import json
from numbers import Number
from uuid import uuid4

from akra_trader.domain.models import *  # noqa: F403


class ProviderProvenanceSchedulerReportingMixin:
  def create_provider_provenance_scheduled_report(
    self,
    *,
    name: str,
    description: str = "",
    query: dict[str, Any] | None = None,
    layout: dict[str, Any] | None = None,
    preset_id: str | None = None,
    view_id: str | None = None,
    cadence: str = "daily",
    status: str = "scheduled",
    created_by_tab_id: str | None = None,
    created_by_tab_label: str | None = None,
  ) -> ProviderProvenanceScheduledReportRecord:
    now = self._clock()
    normalized_preset_id = (
      preset_id.strip()
      if isinstance(preset_id, str) and preset_id.strip()
      else None
    )
    normalized_view_id = (
      view_id.strip()
      if isinstance(view_id, str) and view_id.strip()
      else None
    )
    preset_record = (
      self.get_provider_provenance_analytics_preset(normalized_preset_id)
      if normalized_preset_id is not None
      else None
    )
    view_record = (
      self.get_provider_provenance_dashboard_view(normalized_view_id)
      if normalized_view_id is not None
      else None
    )
    resolved_query = (
      query
      if isinstance(query, dict) and query
      else view_record.query if view_record is not None
      else preset_record.query if preset_record is not None
      else None
    )
    resolved_layout = (
      layout
      if isinstance(layout, dict) and layout
      else view_record.layout if view_record is not None
      else None
    )
    normalized_status = self._normalize_provider_provenance_scheduled_report_status(status)
    normalized_cadence = self._normalize_provider_provenance_scheduled_report_cadence(cadence)
    record = ProviderProvenanceScheduledReportRecord(
      report_id=uuid4().hex[:12],
      name=self._normalize_provider_provenance_workspace_name(name, field_name="scheduled report name"),
      description=description.strip() if isinstance(description, str) else "",
      query=self._normalize_provider_provenance_analytics_query_payload(resolved_query),
      layout=self._normalize_provider_provenance_dashboard_layout_payload(resolved_layout),
      preset_id=(view_record.preset_id if view_record is not None and view_record.preset_id else normalized_preset_id),
      view_id=normalized_view_id,
      cadence=normalized_cadence,
      status=normalized_status,
      created_at=now,
      updated_at=now,
      next_run_at=self._calculate_provider_provenance_scheduled_report_next_run(
        reference_time=now,
        cadence=normalized_cadence,
        status=normalized_status,
      ),
      last_run_at=None,
      last_export_job_id=None,
      created_by_tab_id=(
        created_by_tab_id.strip()
        if isinstance(created_by_tab_id, str) and created_by_tab_id.strip()
        else None
      ),
      created_by_tab_label=(
        created_by_tab_label.strip()
        if isinstance(created_by_tab_label, str) and created_by_tab_label.strip()
        else None
      ),
    )
    saved_record = self._save_provider_provenance_scheduled_report_record(record)
    self._record_provider_provenance_scheduled_report_event(
      record=saved_record,
      action="created",
      source_tab_id=saved_record.created_by_tab_id,
      source_tab_label=saved_record.created_by_tab_label,
      detail="Provider provenance scheduled report created.",
    )
    return saved_record

  def list_provider_provenance_scheduled_reports(
    self,
    *,
    status: str | None = None,
    cadence: str | None = None,
    preset_id: str | None = None,
    view_id: str | None = None,
    created_by_tab_id: str | None = None,
    focus_scope: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceScheduledReportRecord, ...]:
    normalized_status = (
      status.strip()
      if isinstance(status, str) and status.strip() in {"scheduled", "paused"}
      else None
    )
    normalized_cadence = (
      cadence.strip()
      if isinstance(cadence, str) and cadence.strip() in {"daily", "weekly"}
      else None
    )
    normalized_preset_id = (
      preset_id.strip()
      if isinstance(preset_id, str) and preset_id.strip()
      else None
    )
    normalized_view_id = (
      view_id.strip()
      if isinstance(view_id, str) and view_id.strip()
      else None
    )
    normalized_creator = (
      created_by_tab_id.strip()
      if isinstance(created_by_tab_id, str) and created_by_tab_id.strip()
      else None
    )
    normalized_focus_scope = (
      focus_scope.strip()
      if isinstance(focus_scope, str) and focus_scope.strip() in {"current_focus", "all_focuses"}
      else None
    )
    normalized_limit = max(1, min(limit, 200))
    filtered: list[ProviderProvenanceScheduledReportRecord] = []
    for record in self._list_provider_provenance_scheduled_report_records():
      normalized_query = self._normalize_provider_provenance_analytics_query_payload(record.query)
      normalized_layout = self._normalize_provider_provenance_dashboard_layout_payload(record.layout)
      if normalized_status is not None and record.status != normalized_status:
        continue
      if normalized_cadence is not None and record.cadence != normalized_cadence:
        continue
      if normalized_preset_id is not None and record.preset_id != normalized_preset_id:
        continue
      if normalized_view_id is not None and record.view_id != normalized_view_id:
        continue
      if normalized_creator is not None and record.created_by_tab_id != normalized_creator:
        continue
      if normalized_focus_scope is not None and normalized_query["focus_scope"] != normalized_focus_scope:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.report_id,
          record.name,
          record.description,
          record.preset_id,
          record.view_id,
          record.created_by_tab_id,
          record.created_by_tab_label,
          record.status,
          record.cadence,
          normalized_query.get("focus_key"),
          normalized_query.get("symbol"),
          normalized_query.get("timeframe"),
          normalized_query.get("provider_label"),
          normalized_query.get("vendor_field"),
          normalized_query.get("market_data_provider"),
          normalized_query.get("requested_by_tab_id"),
          normalized_query.get("scheduler_alert_category"),
          normalized_query.get("scheduler_alert_status"),
          normalized_query.get("scheduler_alert_narrative_facet"),
          normalized_query.get("search"),
          normalized_layout.get("highlight_panel"),
        ),
        search=search,
      ):
        continue
      filtered.append(
        replace(record, query=normalized_query, layout=normalized_layout)
      )
    return tuple(filtered[:normalized_limit])

  def get_provider_provenance_scheduled_report(
    self,
    report_id: str,
  ) -> ProviderProvenanceScheduledReportRecord:
    normalized_report_id = report_id.strip()
    if not normalized_report_id:
      raise LookupError("Provider provenance scheduled report not found.")
    record = self._load_provider_provenance_scheduled_report_record(normalized_report_id)
    if record is None:
      raise LookupError("Provider provenance scheduled report not found.")
    return replace(
      record,
      query=self._normalize_provider_provenance_analytics_query_payload(record.query),
      layout=self._normalize_provider_provenance_dashboard_layout_payload(record.layout),
    )

  def run_provider_provenance_scheduled_report(
    self,
    report_id: str,
    *,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
    detail: str | None = None,
  ) -> dict[str, Any]:
    record = self.get_provider_provenance_scheduled_report(report_id)
    preset_record = (
      self.get_provider_provenance_analytics_preset(record.preset_id)
      if record.preset_id is not None
      else None
    )
    view_record = (
      self.get_provider_provenance_dashboard_view(record.view_id)
      if record.view_id is not None
      else None
    )
    normalized_query = self._normalize_provider_provenance_analytics_query_payload(record.query)
    exported_at = self._clock()
    analytics = self.get_provider_provenance_export_analytics(
      focus_key=normalized_query.get("focus_key"),
      symbol=normalized_query.get("symbol"),
      timeframe=normalized_query.get("timeframe"),
      provider_label=normalized_query.get("provider_label"),
      vendor_field=normalized_query.get("vendor_field"),
      market_data_provider=normalized_query.get("market_data_provider"),
      venue=normalized_query.get("venue"),
      requested_by_tab_id=normalized_query.get("requested_by_tab_id"),
      status=normalized_query.get("status"),
      search=normalized_query.get("search"),
      result_limit=int(normalized_query.get("result_limit", 12)),
      window_days=int(normalized_query.get("window_days", 14)),
    )
    report_payload = self._build_provider_provenance_analytics_report_payload(
      report=record,
      analytics=analytics,
      preset=preset_record,
      view=view_record,
      exported_at=exported_at,
    )
    export_job = self.create_provider_provenance_export_job(
      content=json.dumps(report_payload, indent=2, sort_keys=True),
      requested_by_tab_id=(
        source_tab_id.strip()
        if isinstance(source_tab_id, str) and source_tab_id.strip()
        else record.created_by_tab_id
      ),
      requested_by_tab_label=(
        source_tab_label.strip()
        if isinstance(source_tab_label, str) and source_tab_label.strip()
        else record.created_by_tab_label
      ),
    )
    updated_record = replace(
      record,
      query=normalized_query,
      layout=self._normalize_provider_provenance_dashboard_layout_payload(record.layout),
      updated_at=exported_at,
      next_run_at=self._calculate_provider_provenance_scheduled_report_next_run(
        reference_time=exported_at,
        cadence=record.cadence,
        status=record.status,
      ),
      last_run_at=exported_at,
      last_export_job_id=export_job.job_id,
    )
    saved_record = self._save_provider_provenance_scheduled_report_record(updated_record)
    self._record_provider_provenance_scheduled_report_event(
      record=saved_record,
      action="ran",
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
      export_job_id=export_job.job_id,
      detail=detail or "Provider provenance scheduled report run completed.",
    )
    return {
      "report": saved_record,
      "export_job": export_job,
    }

  def run_due_provider_provenance_scheduled_reports(
    self,
    *,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
    due_before: datetime | None = None,
    limit: int = 25,
  ) -> dict[str, Any]:
    reference_time = due_before or self._clock()
    normalized_limit = max(1, min(limit, 100))
    candidate_records = [
      record
      for record in self.list_provider_provenance_scheduled_reports(
        status="scheduled",
        limit=500,
      )
      if record.next_run_at is not None and record.next_run_at <= reference_time
    ]
    candidate_records.sort(
      key=lambda record: (
        record.next_run_at or record.updated_at,
        record.updated_at,
        record.report_id,
      )
    )
    results = [
      self.run_provider_provenance_scheduled_report(
        record.report_id,
        source_tab_id=source_tab_id,
        source_tab_label=source_tab_label,
        detail="Due provider provenance scheduled report run completed.",
      )
      for record in candidate_records[:normalized_limit]
    ]
    return {
      "generated_at": self._clock().isoformat(),
      "due_before": reference_time.isoformat(),
      "executed_count": len(results),
      "items": results,
    }

  def execute_provider_provenance_scheduler_cycle(
    self,
    *,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
    limit: int | None = None,
  ) -> dict[str, Any]:
    started_at = self._clock()
    normalized_limit = max(
      1,
      min(
        limit if isinstance(limit, int) and limit > 0 else self._provider_provenance_report_scheduler_batch_limit,
        100,
      ),
    )
    with self._provider_provenance_scheduler_health_lock:
      self._provider_provenance_scheduler_health = replace(
        self._provider_provenance_scheduler_health,
        generated_at=started_at,
        last_cycle_started_at=started_at,
      )
    try:
      result = self.run_due_provider_provenance_scheduled_reports(
        source_tab_id=source_tab_id,
        source_tab_label=source_tab_label,
        limit=normalized_limit,
      )
    except Exception as exc:
      finished_at = self._clock()
      due_report_count, oldest_due_at, max_due_lag_seconds = (
        self._summarize_provider_provenance_scheduler_due_reports(reference_time=finished_at)
      )
      with self._provider_provenance_scheduler_health_lock:
        snapshot = self._provider_provenance_scheduler_health
        updated_snapshot = replace(
          snapshot,
          generated_at=finished_at,
          status="failed",
          summary="Background scheduler failed while executing due provider provenance reports.",
          last_cycle_finished_at=finished_at,
          last_failure_at=finished_at,
          last_error=str(exc),
          cycle_count=snapshot.cycle_count + 1,
          failure_count=snapshot.failure_count + 1,
          consecutive_failure_count=snapshot.consecutive_failure_count + 1,
          last_executed_count=0,
          due_report_count=due_report_count,
          oldest_due_at=oldest_due_at,
          max_due_lag_seconds=max_due_lag_seconds,
          issues=("Scheduler cycle raised an exception before due reports completed.",),
        )
        self._provider_provenance_scheduler_health = updated_snapshot
      updated_snapshot = self._run_provider_provenance_scheduler_alert_workflow(
        snapshot=updated_snapshot,
        previous_snapshot=snapshot,
        source_tab_id=source_tab_id,
        source_tab_label=source_tab_label,
      )
      with self._provider_provenance_scheduler_health_lock:
        self._provider_provenance_scheduler_health = updated_snapshot
      self._record_provider_provenance_scheduler_health(
        snapshot=updated_snapshot,
        source_tab_id=source_tab_id,
        source_tab_label=source_tab_label,
      )
      raise

    finished_at = self._clock()
    due_report_count, oldest_due_at, max_due_lag_seconds = (
      self._summarize_provider_provenance_scheduler_due_reports(reference_time=finished_at)
    )
    with self._provider_provenance_scheduler_health_lock:
      snapshot = self._provider_provenance_scheduler_health
      issues: list[str] = []
      status = "healthy"
      summary = "Background scheduler is healthy for provider provenance automation."
      if (
        due_report_count > 0
        and max_due_lag_seconds >= self._provider_provenance_scheduler_warning_lag_seconds()
      ):
        status = "lagging"
        summary = "Background scheduler is lagging on due provider provenance reports."
        issues.append(
          f"{due_report_count} due report(s) remain after the latest cycle; oldest due lag is {max_due_lag_seconds}s."
        )
      executed_count = int(result.get("executed_count", 0))
      updated_snapshot = replace(
        snapshot,
        generated_at=finished_at,
        status=status,
        summary=summary,
        last_cycle_started_at=started_at,
        last_cycle_finished_at=finished_at,
        last_success_at=finished_at,
        last_error=None,
        cycle_count=snapshot.cycle_count + 1,
        success_count=snapshot.success_count + 1,
        consecutive_failure_count=0,
        last_executed_count=executed_count,
        total_executed_count=snapshot.total_executed_count + executed_count,
        due_report_count=due_report_count,
        oldest_due_at=oldest_due_at,
        max_due_lag_seconds=max_due_lag_seconds,
        issues=tuple(issues),
      )
      self._provider_provenance_scheduler_health = updated_snapshot
    updated_snapshot = self._run_provider_provenance_scheduler_alert_workflow(
      snapshot=updated_snapshot,
      previous_snapshot=snapshot,
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
    )
    with self._provider_provenance_scheduler_health_lock:
      self._provider_provenance_scheduler_health = updated_snapshot
    self._record_provider_provenance_scheduler_health(
      snapshot=updated_snapshot,
      source_tab_id=source_tab_id,
      source_tab_label=source_tab_label,
    )
    return result

  def list_provider_provenance_scheduled_report_history(
    self,
    report_id: str,
  ) -> tuple[ProviderProvenanceScheduledReportAuditRecord, ...]:
    record = self.get_provider_provenance_scheduled_report(report_id)
    self._prune_provider_provenance_scheduled_report_audit_records()
    return self._list_provider_provenance_scheduled_report_audit_records(record.report_id)

  def get_provider_provenance_export_job(
    self,
    job_id: str,
  ) -> ProviderProvenanceExportJobRecord:
    self._prune_provider_provenance_export_artifact_records()
    self._prune_provider_provenance_export_job_records()
    normalized_job_id = job_id.strip()
    if not normalized_job_id:
      raise LookupError("Provider provenance export job not found.")
    record = self._load_provider_provenance_export_job_record(normalized_job_id)
    if record is None:
      raise LookupError("Provider provenance export job not found.")
    if record.expires_at is not None and record.expires_at <= self._clock():
      raise LookupError("Provider provenance export job has expired.")
    return self._ensure_provider_provenance_scheduler_export_policy(record)

  def get_provider_provenance_export_artifact(
    self,
    artifact_id: str,
  ) -> ProviderProvenanceExportArtifactRecord:
    self._prune_provider_provenance_export_artifact_records()
    normalized_artifact_id = artifact_id.strip()
    if not normalized_artifact_id:
      raise LookupError("Provider provenance export artifact not found.")
    record = self._load_provider_provenance_export_artifact_record(normalized_artifact_id)
    if record is None:
      raise LookupError("Provider provenance export artifact not found.")
    if record.expires_at is not None and record.expires_at <= self._clock():
      raise LookupError("Provider provenance export artifact has expired.")
    return record

  def list_provider_provenance_export_job_history(
    self,
    job_id: str,
  ) -> tuple[ProviderProvenanceExportJobAuditRecord, ...]:
    record = self.get_provider_provenance_export_job(job_id)
    self._prune_provider_provenance_export_job_audit_records()
    return self._list_provider_provenance_export_job_audit_records(record.job_id)

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
