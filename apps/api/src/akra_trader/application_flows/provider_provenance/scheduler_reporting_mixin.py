from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any
from typing import Iterable
import json
from numbers import Number
from uuid import uuid4

from akra_trader.domain.models import *  # noqa: F403
from akra_trader.application_flows.provider_provenance.scheduler_reporting_exports_mixin import ProviderProvenanceSchedulerReportingExportsMixin


class ProviderProvenanceSchedulerReportingMixin(ProviderProvenanceSchedulerReportingExportsMixin):
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
