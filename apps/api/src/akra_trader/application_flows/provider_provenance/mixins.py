from __future__ import annotations

import csv
from copy import deepcopy
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
import hashlib
import io
import json
import math
from numbers import Number
import re
from typing import Any
from typing import Mapping
from uuid import uuid4

from akra_trader.application_support.provider_governance_catalog_plan_workflows import (
  apply_provider_provenance_scheduler_search_moderation_catalog_governance_plan as apply_provider_provenance_scheduler_search_moderation_catalog_governance_plan_support,
)
from akra_trader.application_support.provider_governance_catalog_plan_workflows import (
  approve_provider_provenance_scheduler_search_moderation_catalog_governance_plan as approve_provider_provenance_scheduler_search_moderation_catalog_governance_plan_support,
)
from akra_trader.application_support.provider_governance_meta_workflows import (
  apply_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan as apply_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_support,
)
from akra_trader.application_support.provider_governance_meta_workflows import (
  approve_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan as approve_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_support,
)
from akra_trader.application_support.provider_governance_bulk_policy_orchestration import (
  bulk_govern_provider_provenance_scheduler_search_moderation_catalog_governance_policies as bulk_govern_provider_provenance_scheduler_search_moderation_catalog_governance_policies_support,
)
from akra_trader.application_support.provider_governance_catalog_plan_workflows import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_plans as list_provider_provenance_scheduler_search_moderation_catalog_governance_plans_support,
)
from akra_trader.application_support.provider_governance_catalog_plan_workflows import (
  stage_provider_provenance_scheduler_search_moderation_catalog_governance_plan as stage_provider_provenance_scheduler_search_moderation_catalog_governance_plan_support,
)
from akra_trader.application_support.provider_governance_meta_workflows import (
  create_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy as create_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_support,
)
from akra_trader.application_support.provider_governance_meta_workflows import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans as list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans_support,
)
from akra_trader.application_support.provider_governance_meta_workflows import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies as list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies_support,
)
from akra_trader.application_support.provider_governance_meta_workflows import (
  stage_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan as stage_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_support,
)
from akra_trader.application_support.provider_governance_persistence import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_records as list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_records_support,
)
from akra_trader.application_support.provider_governance_persistence import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records as list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records_support,
)
from akra_trader.application_support.provider_governance_persistence import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records as list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records_support,
)
from akra_trader.application_support.provider_governance_persistence import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records as list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records_support,
)
from akra_trader.application_support.provider_governance_persistence import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records as list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records_support,
)
from akra_trader.application_support.provider_governance_persistence import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records as list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records_support,
)
from akra_trader.application_support.provider_governance_persistence import (
  save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record as save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record_support,
)
from akra_trader.application_support.provider_governance_persistence import (
  save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record as save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record_support,
)
from akra_trader.application_support.provider_governance_persistence import (
  save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record as save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record_support,
)
from akra_trader.application_support.provider_governance_persistence import (
  save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record as save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record_support,
)
from akra_trader.application_support.provider_governance_persistence import (
  save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record as save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record_support,
)
from akra_trader.application_support.provider_governance_persistence import (
  save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record as save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record_support,
)
from akra_trader.application_support.provider_governance_policy_history import (
  build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_detail as build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_detail_support,
)
from akra_trader.application_support.provider_governance_policy_history import (
  build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision as build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_support,
)
from akra_trader.application_support.provider_governance_policy_history import (
  normalize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_status as normalize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_status_support,
)
from akra_trader.application_support.provider_governance_policy_history import (
  record_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision as record_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_support,
)
from akra_trader.application_support.provider_governance_policy_mutations import (
  create_provider_provenance_scheduler_search_moderation_catalog_governance_policy as create_provider_provenance_scheduler_search_moderation_catalog_governance_policy_support,
)
from akra_trader.application_support.provider_governance_policy_mutations import (
  delete_provider_provenance_scheduler_search_moderation_catalog_governance_policy as delete_provider_provenance_scheduler_search_moderation_catalog_governance_policy_support,
)
from akra_trader.application_support.provider_governance_policy_mutations import (
  restore_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision as restore_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_support,
)
from akra_trader.application_support.provider_governance_policy_mutations import (
  update_provider_provenance_scheduler_search_moderation_catalog_governance_policy as update_provider_provenance_scheduler_search_moderation_catalog_governance_policy_support,
)
from akra_trader.application_support.provider_governance_policy_reads import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_policies as list_provider_provenance_scheduler_search_moderation_catalog_governance_policies_support,
)
from akra_trader.application_support.provider_governance_policy_reads import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits as list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_support,
)
from akra_trader.application_support.provider_governance_policy_reads import (
  list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions as list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions_support,
)
from akra_trader.application_support.provider_governance_records import (
  get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record as get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record as get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  get_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record as get_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  get_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record as get_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  load_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record as load_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_preview_item as serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_preview_item_support,
)
from akra_trader.application_support.provider_governance_records import (
  serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record as serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record as serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_preview_item as serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_preview_item_support,
)
from akra_trader.application_support.provider_governance_records import (
  serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record as serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record as serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record as serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record_support,
)
from akra_trader.application_support.provider_governance_records import (
  serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record as serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record_support,
)
from akra_trader.application_flows.provider_provenance.replay_alias_mixin import ReplayIntentAliasMixin
from akra_trader.application_flows.provider_provenance.scheduler_health_mixin import ProviderProvenanceSchedulerHealthMixin
from akra_trader.application_flows.provider_provenance.scheduler_reporting_mixin import ProviderProvenanceSchedulerReportingMixin
from akra_trader.application_flows.provider_provenance.search_moderation_mixin import ProviderProvenanceSearchModerationMixin
from akra_trader.domain.models import *  # noqa: F403

PROVIDER_PROVENANCE_SCHEDULER_ALERT_AUTOMATION_TAB_ID = (
  "system:provider-provenance-scheduler-alerts"
)
PROVIDER_PROVENANCE_SCHEDULER_ALERT_AUTOMATION_TAB_LABEL = (
  "Scheduler alert automation"
)


class ProviderProvenanceCompatibilityMixin(
  ReplayIntentAliasMixin,
  ProviderProvenanceSearchModerationMixin,
  ProviderProvenanceSchedulerHealthMixin,
  ProviderProvenanceSchedulerReportingMixin,
):
  @staticmethod
  def _serialize_operator_alert_primary_focus_payload(
    primary_focus: OperatorAlertPrimaryFocus | None,
  ) -> dict[str, Any] | None:
    if primary_focus is None:
      return None
    return {
      "symbol": primary_focus.symbol,
      "timeframe": primary_focus.timeframe,
      "candidate_symbols": list(primary_focus.candidate_symbols),
      "candidate_count": primary_focus.candidate_count,
      "policy": primary_focus.policy,
      "reason": primary_focus.reason,
    }


  def _save_provider_provenance_export_artifact_record(
    self,
    record: ProviderProvenanceExportArtifactRecord,
  ) -> ProviderProvenanceExportArtifactRecord:
    save_artifact = getattr(self._runs, "save_provider_provenance_export_artifact", None)
    if callable(save_artifact):
      return save_artifact(record)
    self._provider_provenance_export_artifacts[record.artifact_id] = record
    return record

  def _load_provider_provenance_export_artifact_record(
    self,
    artifact_id: str,
  ) -> ProviderProvenanceExportArtifactRecord | None:
    get_artifact = getattr(self._runs, "get_provider_provenance_export_artifact", None)
    if callable(get_artifact):
      return get_artifact(artifact_id)
    return self._provider_provenance_export_artifacts.get(artifact_id)

  def _delete_provider_provenance_export_artifact_records(self, artifact_ids: tuple[str, ...]) -> int:
    delete_artifacts = getattr(self._runs, "delete_provider_provenance_export_artifacts", None)
    if callable(delete_artifacts):
      return int(delete_artifacts(artifact_ids))
    deleted_count = 0
    for artifact_id in artifact_ids:
      if artifact_id in self._provider_provenance_export_artifacts:
        deleted_count += 1
        del self._provider_provenance_export_artifacts[artifact_id]
    return deleted_count

  def _prune_provider_provenance_export_artifact_records(self) -> int:
    current_time = self._clock()
    prune_artifacts = getattr(self._runs, "prune_provider_provenance_export_artifacts", None)
    if callable(prune_artifacts):
      return int(prune_artifacts(current_time))
    original_count = len(self._provider_provenance_export_artifacts)
    self._provider_provenance_export_artifacts = {
      artifact_id: record
      for artifact_id, record in self._provider_provenance_export_artifacts.items()
      if record.expires_at is None or record.expires_at > current_time
    }
    return original_count - len(self._provider_provenance_export_artifacts)

  def _save_provider_provenance_export_job_record(
    self,
    record: ProviderProvenanceExportJobRecord,
  ) -> ProviderProvenanceExportJobRecord:
    save_job = getattr(self._runs, "save_provider_provenance_export_job", None)
    if callable(save_job):
      return save_job(record)
    self._provider_provenance_export_jobs[record.job_id] = record
    return record

  def _load_provider_provenance_export_job_record(
    self,
    job_id: str,
  ) -> ProviderProvenanceExportJobRecord | None:
    get_job = getattr(self._runs, "get_provider_provenance_export_job", None)
    if callable(get_job):
      return get_job(job_id)
    return self._provider_provenance_export_jobs.get(job_id)

  def _list_provider_provenance_export_job_records(
    self,
  ) -> tuple[ProviderProvenanceExportJobRecord, ...]:
    list_jobs = getattr(self._runs, "list_provider_provenance_export_jobs", None)
    if callable(list_jobs):
      return tuple(list_jobs())
    return tuple(
      sorted(
        self._provider_provenance_export_jobs.values(),
        key=lambda record: (record.exported_at or record.created_at, record.job_id),
        reverse=True,
      )
    )

  def _prune_provider_provenance_export_job_records(self) -> int:
    current_time = self._clock()
    prune_jobs = getattr(self._runs, "prune_provider_provenance_export_jobs", None)
    if callable(prune_jobs):
      return int(prune_jobs(current_time))
    original_count = len(self._provider_provenance_export_jobs)
    self._provider_provenance_export_jobs = {
      job_id: record
      for job_id, record in self._provider_provenance_export_jobs.items()
      if record.expires_at is None or record.expires_at > current_time
    }
    return original_count - len(self._provider_provenance_export_jobs)

  def _delete_provider_provenance_export_job_records(self, job_ids: tuple[str, ...]) -> int:
    delete_jobs = getattr(self._runs, "delete_provider_provenance_export_jobs", None)
    if callable(delete_jobs):
      return int(delete_jobs(job_ids))
    deleted_count = 0
    for job_id in job_ids:
      if job_id in self._provider_provenance_export_jobs:
        deleted_count += 1
        del self._provider_provenance_export_jobs[job_id]
    return deleted_count

  def _save_provider_provenance_export_job_audit_record(
    self,
    record: ProviderProvenanceExportJobAuditRecord,
  ) -> ProviderProvenanceExportJobAuditRecord:
    save_audit = getattr(self._runs, "save_provider_provenance_export_job_audit_record", None)
    if callable(save_audit):
      return save_audit(record)
    self._provider_provenance_export_job_audit_records[record.audit_id] = record
    return record

  def _list_provider_provenance_export_job_audit_records(
    self,
    job_id: str | None = None,
  ) -> tuple[ProviderProvenanceExportJobAuditRecord, ...]:
    list_audits = getattr(self._runs, "list_provider_provenance_export_job_audit_records", None)
    if callable(list_audits):
      return tuple(list_audits(job_id))
    records = [
      record
      for record in self._provider_provenance_export_job_audit_records.values()
      if job_id is None or record.job_id == job_id
    ]
    return tuple(
      sorted(
        records,
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def _delete_provider_provenance_export_job_audit_records(self, audit_ids: tuple[str, ...]) -> int:
    delete_audits = getattr(self._runs, "delete_provider_provenance_export_job_audit_records", None)
    if callable(delete_audits):
      return int(delete_audits(audit_ids))
    deleted_count = 0
    for audit_id in audit_ids:
      if audit_id in self._provider_provenance_export_job_audit_records:
        deleted_count += 1
        del self._provider_provenance_export_job_audit_records[audit_id]
    return deleted_count

  def _prune_provider_provenance_export_job_audit_records(self) -> int:
    current_time = self._clock()
    prune_audits = getattr(self._runs, "prune_provider_provenance_export_job_audit_records", None)
    if callable(prune_audits):
      return int(prune_audits(current_time))
    original_count = len(self._provider_provenance_export_job_audit_records)
    self._provider_provenance_export_job_audit_records = {
      audit_id: record
      for audit_id, record in self._provider_provenance_export_job_audit_records.items()
      if record.expires_at is None or record.expires_at > current_time
    }
    return original_count - len(self._provider_provenance_export_job_audit_records)

  def _record_provider_provenance_export_job_event(
    self,
    *,
    record: ProviderProvenanceExportJobRecord,
    action: str,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
    detail: str | None = None,
    routing_policy_id: str | None = None,
    routing_targets: tuple[str, ...] = (),
    approval_policy_id: str | None = None,
    approval_required: bool | None = None,
    approval_state: str | None = None,
    approval_summary: str | None = None,
    approved_by: str | None = None,
    delivery_targets: tuple[str, ...] = (),
    delivery_status: str | None = None,
    delivery_summary: str | None = None,
  ) -> ProviderProvenanceExportJobAuditRecord:
    self._prune_provider_provenance_export_job_audit_records()
    recorded_at = self._clock()
    latest_recorded_at = next(
      (
        existing.recorded_at
        for existing in self._list_provider_provenance_export_job_audit_records(record.job_id)
      ),
      None,
    )
    if latest_recorded_at is not None and latest_recorded_at >= recorded_at:
      recorded_at = latest_recorded_at + timedelta(microseconds=1)
    audit_record = ProviderProvenanceExportJobAuditRecord(
      audit_id=uuid4().hex[:12],
      job_id=record.job_id,
      action=action,
      recorded_at=recorded_at,
      expires_at=self._build_replay_intent_alias_audit_expiry(
        retention_policy="30d",
        recorded_at=recorded_at,
      ),
      export_scope=record.export_scope,
      export_format=record.export_format,
      focus_key=record.focus_key,
      focus_label=record.focus_label,
      symbol=record.symbol,
      timeframe=record.timeframe,
      market_data_provider=record.market_data_provider,
      requested_by_tab_id=record.requested_by_tab_id,
      requested_by_tab_label=record.requested_by_tab_label,
      source_tab_id=source_tab_id.strip() if isinstance(source_tab_id, str) and source_tab_id.strip() else None,
      source_tab_label=(
        source_tab_label.strip()
        if isinstance(source_tab_label, str) and source_tab_label.strip()
        else None
      ),
      routing_policy_id=(
        routing_policy_id.strip()
        if isinstance(routing_policy_id, str) and routing_policy_id.strip()
        else record.routing_policy_id
      ),
      routing_targets=tuple(routing_targets or record.routing_targets),
      approval_policy_id=(
        approval_policy_id.strip()
        if isinstance(approval_policy_id, str) and approval_policy_id.strip()
        else record.approval_policy_id
      ),
      approval_required=record.approval_required if approval_required is None else bool(approval_required),
      approval_state=(
        approval_state.strip()
        if isinstance(approval_state, str) and approval_state.strip()
        else record.approval_state
      ),
      approval_summary=(
        approval_summary.strip()
        if isinstance(approval_summary, str) and approval_summary.strip()
        else record.approval_summary
      ),
      approved_by=(
        approved_by.strip()
        if isinstance(approved_by, str) and approved_by.strip()
        else record.approved_by
      ),
      delivery_targets=tuple(delivery_targets),
      delivery_status=delivery_status.strip() if isinstance(delivery_status, str) and delivery_status.strip() else None,
      delivery_summary=(
        delivery_summary.strip()
        if isinstance(delivery_summary, str) and delivery_summary.strip()
        else None
      ),
      detail=(
        detail.strip()
        if isinstance(detail, str) and detail.strip()
        else (
          "Provider provenance export created."
          if action == "created"
          else (
            "Provider provenance export downloaded."
            if action == "downloaded"
            else "Provider provenance export updated."
          )
        )
      ),
    )
    return self._save_provider_provenance_export_job_audit_record(audit_record)

  def _save_provider_provenance_analytics_preset_record(
    self,
    record: ProviderProvenanceAnalyticsPresetRecord,
  ) -> ProviderProvenanceAnalyticsPresetRecord:
    save_preset = getattr(self._runs, "save_provider_provenance_analytics_preset", None)
    if callable(save_preset):
      return save_preset(record)
    self._provider_provenance_analytics_presets[record.preset_id] = record
    return record

  def _load_provider_provenance_analytics_preset_record(
    self,
    preset_id: str,
  ) -> ProviderProvenanceAnalyticsPresetRecord | None:
    get_preset = getattr(self._runs, "get_provider_provenance_analytics_preset", None)
    if callable(get_preset):
      return get_preset(preset_id)
    return self._provider_provenance_analytics_presets.get(preset_id)

  def _list_provider_provenance_analytics_preset_records(
    self,
  ) -> tuple[ProviderProvenanceAnalyticsPresetRecord, ...]:
    list_presets = getattr(self._runs, "list_provider_provenance_analytics_presets", None)
    if callable(list_presets):
      return tuple(list_presets())
    return tuple(
      sorted(
        self._provider_provenance_analytics_presets.values(),
        key=lambda record: (record.updated_at, record.preset_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_dashboard_view_record(
    self,
    record: ProviderProvenanceDashboardViewRecord,
  ) -> ProviderProvenanceDashboardViewRecord:
    save_view = getattr(self._runs, "save_provider_provenance_dashboard_view", None)
    if callable(save_view):
      return save_view(record)
    self._provider_provenance_dashboard_views[record.view_id] = record
    return record

  def _load_provider_provenance_dashboard_view_record(
    self,
    view_id: str,
  ) -> ProviderProvenanceDashboardViewRecord | None:
    get_view = getattr(self._runs, "get_provider_provenance_dashboard_view", None)
    if callable(get_view):
      return get_view(view_id)
    return self._provider_provenance_dashboard_views.get(view_id)

  def _list_provider_provenance_dashboard_view_records(
    self,
  ) -> tuple[ProviderProvenanceDashboardViewRecord, ...]:
    list_views = getattr(self._runs, "list_provider_provenance_dashboard_views", None)
    if callable(list_views):
      return tuple(list_views())
    return tuple(
      sorted(
        self._provider_provenance_dashboard_views.values(),
        key=lambda record: (record.updated_at, record.view_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_stitched_report_view_record(
    self,
    record: ProviderProvenanceSchedulerStitchedReportViewRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRecord:
    save_view = getattr(self._runs, "save_provider_provenance_scheduler_stitched_report_view", None)
    if callable(save_view):
      return save_view(record)
    self._provider_provenance_scheduler_stitched_report_views[record.view_id] = record
    return record

  def _load_provider_provenance_scheduler_stitched_report_view_record(
    self,
    view_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRecord | None:
    get_view = getattr(self._runs, "get_provider_provenance_scheduler_stitched_report_view", None)
    if callable(get_view):
      return get_view(view_id)
    return self._provider_provenance_scheduler_stitched_report_views.get(view_id)

  def _list_provider_provenance_scheduler_stitched_report_view_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportViewRecord, ...]:
    list_views = getattr(self._runs, "list_provider_provenance_scheduler_stitched_report_views", None)
    if callable(list_views):
      return tuple(list_views())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_views.values(),
        key=lambda record: (record.updated_at, record.view_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_stitched_report_view_revision_record(
    self,
    record: ProviderProvenanceSchedulerStitchedReportViewRevisionRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRevisionRecord:
    save_revision = getattr(self._runs, "save_provider_provenance_scheduler_stitched_report_view_revision", None)
    if callable(save_revision):
      return save_revision(record)
    self._provider_provenance_scheduler_stitched_report_view_revisions[record.revision_id] = record
    return record

  def _load_provider_provenance_scheduler_stitched_report_view_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRevisionRecord | None:
    get_revision = getattr(self._runs, "get_provider_provenance_scheduler_stitched_report_view_revision", None)
    if callable(get_revision):
      return get_revision(revision_id)
    return self._provider_provenance_scheduler_stitched_report_view_revisions.get(revision_id)

  def _list_provider_provenance_scheduler_stitched_report_view_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportViewRevisionRecord, ...]:
    list_revisions = getattr(self._runs, "list_provider_provenance_scheduler_stitched_report_view_revisions", None)
    if callable(list_revisions):
      return tuple(list_revisions())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_view_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_stitched_report_view_audit_record(
    self,
    record: ProviderProvenanceSchedulerStitchedReportViewAuditRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportViewAuditRecord:
    save_audit = getattr(self._runs, "save_provider_provenance_scheduler_stitched_report_view_audit_record", None)
    if callable(save_audit):
      return save_audit(record)
    self._provider_provenance_scheduler_stitched_report_view_audit_records[record.audit_id] = record
    return record

  def _list_provider_provenance_scheduler_stitched_report_view_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportViewAuditRecord, ...]:
    list_audits = getattr(self._runs, "list_provider_provenance_scheduler_stitched_report_view_audit_records", None)
    if callable(list_audits):
      return tuple(list_audits())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_view_audit_records.values(),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_stitched_report_governance_registry_record(
    self,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord:
    save_registry = getattr(
      self._runs,
      "save_provider_provenance_scheduler_stitched_report_governance_registry",
      None,
    )
    if callable(save_registry):
      return save_registry(record)
    self._provider_provenance_scheduler_stitched_report_governance_registries[record.registry_id] = record
    return record

  def _load_provider_provenance_scheduler_stitched_report_governance_registry_record(
    self,
    registry_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord | None:
    get_registry = getattr(
      self._runs,
      "get_provider_provenance_scheduler_stitched_report_governance_registry",
      None,
    )
    if callable(get_registry):
      return get_registry(registry_id)
    return self._provider_provenance_scheduler_stitched_report_governance_registries.get(registry_id)

  def _list_provider_provenance_scheduler_stitched_report_governance_registry_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord, ...]:
    list_registries = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_registries",
      None,
    )
    if callable(list_registries):
      return tuple(list_registries())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_governance_registries.values(),
        key=lambda record: (record.updated_at, record.registry_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_stitched_report_governance_registry_audit_record(
    self,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord:
    save_audit = getattr(
      self._runs,
      "save_provider_provenance_scheduler_stitched_report_governance_registry_audit_record",
      None,
    )
    if callable(save_audit):
      return save_audit(record)
    self._provider_provenance_scheduler_stitched_report_governance_registry_audit_records[record.audit_id] = record
    return record

  def _list_provider_provenance_scheduler_stitched_report_governance_registry_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord, ...]:
    list_audits = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_registry_audit_records",
      None,
    )
    if callable(list_audits):
      return tuple(list_audits())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_governance_registry_audit_records.values(),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_stitched_report_governance_registry_revision_record(
    self,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord:
    save_revision = getattr(
      self._runs,
      "save_provider_provenance_scheduler_stitched_report_governance_registry_revision",
      None,
    )
    if callable(save_revision):
      return save_revision(record)
    self._provider_provenance_scheduler_stitched_report_governance_registry_revisions[record.revision_id] = record
    return record

  def _load_provider_provenance_scheduler_stitched_report_governance_registry_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord | None:
    get_revision = getattr(
      self._runs,
      "get_provider_provenance_scheduler_stitched_report_governance_registry_revision",
      None,
    )
    if callable(get_revision):
      return get_revision(revision_id)
    return self._provider_provenance_scheduler_stitched_report_governance_registry_revisions.get(
      revision_id
    )

  def _list_provider_provenance_scheduler_stitched_report_governance_registry_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord, ...]:
    list_revisions = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_registry_revisions",
      None,
    )
    if callable(list_revisions):
      return tuple(list_revisions())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_governance_registry_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduled_report_record(
    self,
    record: ProviderProvenanceScheduledReportRecord,
  ) -> ProviderProvenanceScheduledReportRecord:
    save_report = getattr(self._runs, "save_provider_provenance_scheduled_report", None)
    if callable(save_report):
      return save_report(record)
    self._provider_provenance_scheduled_reports[record.report_id] = record
    return record

  def _load_provider_provenance_scheduled_report_record(
    self,
    report_id: str,
  ) -> ProviderProvenanceScheduledReportRecord | None:
    get_report = getattr(self._runs, "get_provider_provenance_scheduled_report", None)
    if callable(get_report):
      return get_report(report_id)
    return self._provider_provenance_scheduled_reports.get(report_id)

  def _list_provider_provenance_scheduled_report_records(
    self,
  ) -> tuple[ProviderProvenanceScheduledReportRecord, ...]:
    list_reports = getattr(self._runs, "list_provider_provenance_scheduled_reports", None)
    if callable(list_reports):
      return tuple(list_reports())
    return tuple(
      sorted(
        self._provider_provenance_scheduled_reports.values(),
        key=lambda record: (record.updated_at, record.report_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_narrative_template_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeTemplateRecord,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRecord:
    save_template = getattr(self._runs, "save_provider_provenance_scheduler_narrative_template", None)
    if callable(save_template):
      return save_template(record)
    self._provider_provenance_scheduler_narrative_templates[record.template_id] = record
    return record

  def _load_provider_provenance_scheduler_narrative_template_record(
    self,
    template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRecord | None:
    get_template = getattr(self._runs, "get_provider_provenance_scheduler_narrative_template", None)
    if callable(get_template):
      return get_template(template_id)
    return self._provider_provenance_scheduler_narrative_templates.get(template_id)

  def _list_provider_provenance_scheduler_narrative_template_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeTemplateRecord, ...]:
    list_templates = getattr(self._runs, "list_provider_provenance_scheduler_narrative_templates", None)
    if callable(list_templates):
      return tuple(list_templates())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_templates.values(),
        key=lambda record: (record.updated_at, record.template_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_narrative_template_revision_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord:
    save_revision = getattr(self._runs, "save_provider_provenance_scheduler_narrative_template_revision", None)
    if callable(save_revision):
      return save_revision(record)
    self._provider_provenance_scheduler_narrative_template_revisions[record.revision_id] = record
    return record

  def _load_provider_provenance_scheduler_narrative_template_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord | None:
    get_revision = getattr(self._runs, "get_provider_provenance_scheduler_narrative_template_revision", None)
    if callable(get_revision):
      return get_revision(revision_id)
    return self._provider_provenance_scheduler_narrative_template_revisions.get(revision_id)

  def _list_provider_provenance_scheduler_narrative_template_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord, ...]:
    list_revisions = getattr(self._runs, "list_provider_provenance_scheduler_narrative_template_revisions", None)
    if callable(list_revisions):
      return tuple(list_revisions())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_template_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_narrative_registry_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeRegistryRecord,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRecord:
    save_registry_entry = getattr(self._runs, "save_provider_provenance_scheduler_narrative_registry_entry", None)
    if callable(save_registry_entry):
      return save_registry_entry(record)
    self._provider_provenance_scheduler_narrative_registry[record.registry_id] = record
    return record

  def _load_provider_provenance_scheduler_narrative_registry_record(
    self,
    registry_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRecord | None:
    get_registry_entry = getattr(self._runs, "get_provider_provenance_scheduler_narrative_registry_entry", None)
    if callable(get_registry_entry):
      return get_registry_entry(registry_id)
    return self._provider_provenance_scheduler_narrative_registry.get(registry_id)

  def _list_provider_provenance_scheduler_narrative_registry_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeRegistryRecord, ...]:
    list_registry = getattr(self._runs, "list_provider_provenance_scheduler_narrative_registry_entries", None)
    if callable(list_registry):
      return tuple(list_registry())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_registry.values(),
        key=lambda record: (record.updated_at, record.registry_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_narrative_registry_revision_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord:
    save_revision = getattr(self._runs, "save_provider_provenance_scheduler_narrative_registry_revision", None)
    if callable(save_revision):
      return save_revision(record)
    self._provider_provenance_scheduler_narrative_registry_revisions[record.revision_id] = record
    return record

  def _load_provider_provenance_scheduler_narrative_registry_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord | None:
    get_revision = getattr(self._runs, "get_provider_provenance_scheduler_narrative_registry_revision", None)
    if callable(get_revision):
      return get_revision(revision_id)
    return self._provider_provenance_scheduler_narrative_registry_revisions.get(revision_id)

  def _list_provider_provenance_scheduler_narrative_registry_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord, ...]:
    list_revisions = getattr(self._runs, "list_provider_provenance_scheduler_narrative_registry_revisions", None)
    if callable(list_revisions):
      return tuple(list_revisions())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_registry_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  @staticmethod
  def _uses_provider_provenance_scheduler_stitched_report_governance_policy_store(
    item_type_scope: str | None,
  ) -> bool:
    return item_type_scope == "stitched_report_governance_registry"

  @staticmethod
  def _uses_provider_provenance_scheduler_stitched_report_governance_plan_store(
    item_type: str | None,
  ) -> bool:
    return item_type == "stitched_report_governance_registry"

  def _save_provider_provenance_scheduler_narrative_governance_policy_template_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    if self._uses_provider_provenance_scheduler_stitched_report_governance_policy_store(
      record.item_type_scope
    ):
      save_record = getattr(
        self._runs,
        "save_provider_provenance_scheduler_stitched_report_governance_policy_template",
        None,
      )
      if callable(save_record):
        return save_record(record)
      self._provider_provenance_scheduler_stitched_report_governance_policy_templates[
        record.policy_template_id
      ] = record
      return record
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_policy_template",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_policy_templates[record.policy_template_id] = record
    return record

  def _load_provider_provenance_scheduler_narrative_governance_policy_template_record(
    self,
    policy_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord | None:
    get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_narrative_governance_policy_template",
      None,
    )
    if callable(get_record):
      record = get_record(policy_template_id)
      if record is not None:
        return record
    else:
      record = self._provider_provenance_scheduler_narrative_governance_policy_templates.get(policy_template_id)
      if record is not None:
        return record
    stitched_get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_stitched_report_governance_policy_template",
      None,
    )
    if callable(stitched_get_record):
      return stitched_get_record(policy_template_id)
    return self._provider_provenance_scheduler_stitched_report_governance_policy_templates.get(
      policy_template_id
    )

  def _list_provider_provenance_scheduler_narrative_governance_policy_template_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_policy_templates",
      None,
    )
    shared_records = (
      tuple(list_records())
      if callable(list_records)
      else tuple(self._provider_provenance_scheduler_narrative_governance_policy_templates.values())
    )
    stitched_list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_policy_templates",
      None,
    )
    stitched_records = (
      tuple(stitched_list_records())
      if callable(stitched_list_records)
      else tuple(self._provider_provenance_scheduler_stitched_report_governance_policy_templates.values())
    )
    return tuple(
      sorted(
        (*shared_records, *stitched_records),
        key=lambda record: (record.updated_at, record.policy_template_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_narrative_governance_policy_template_revision_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord:
    if self._uses_provider_provenance_scheduler_stitched_report_governance_policy_store(
      record.item_type_scope
    ):
      save_record = getattr(
        self._runs,
        "save_provider_provenance_scheduler_stitched_report_governance_policy_template_revision",
        None,
      )
      if callable(save_record):
        return save_record(record)
      self._provider_provenance_scheduler_stitched_report_governance_policy_template_revisions[
        record.revision_id
      ] = record
      return record
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_policy_template_revision",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_policy_template_revisions[record.revision_id] = record
    return record

  def _load_provider_provenance_scheduler_narrative_governance_policy_template_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord | None:
    get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_narrative_governance_policy_template_revision",
      None,
    )
    if callable(get_record):
      record = get_record(revision_id)
      if record is not None:
        return record
    else:
      record = self._provider_provenance_scheduler_narrative_governance_policy_template_revisions.get(
        revision_id
      )
      if record is not None:
        return record
    stitched_get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_stitched_report_governance_policy_template_revision",
      None,
    )
    if callable(stitched_get_record):
      return stitched_get_record(revision_id)
    return self._provider_provenance_scheduler_stitched_report_governance_policy_template_revisions.get(
      revision_id
    )

  def _list_provider_provenance_scheduler_narrative_governance_policy_template_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_policy_template_revisions",
      None,
    )
    shared_records = (
      tuple(list_records())
      if callable(list_records)
      else tuple(self._provider_provenance_scheduler_narrative_governance_policy_template_revisions.values())
    )
    stitched_list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_policy_template_revisions",
      None,
    )
    stitched_records = (
      tuple(stitched_list_records())
      if callable(stitched_list_records)
      else tuple(self._provider_provenance_scheduler_stitched_report_governance_policy_template_revisions.values())
    )
    return tuple(
      sorted(
        (*shared_records, *stitched_records),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_narrative_governance_policy_template_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord:
    if self._uses_provider_provenance_scheduler_stitched_report_governance_policy_store(
      record.item_type_scope
    ):
      save_record = getattr(
        self._runs,
        "save_provider_provenance_scheduler_stitched_report_governance_policy_template_audit_record",
        None,
      )
      if callable(save_record):
        return save_record(record)
      self._provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records[
        record.audit_id
      ] = record
      return record
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_policy_template_audit_record",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_policy_template_audit_records[record.audit_id] = record
    return record

  def _list_provider_provenance_scheduler_narrative_governance_policy_template_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_policy_template_audit_records",
      None,
    )
    shared_records = (
      tuple(list_records())
      if callable(list_records)
      else tuple(self._provider_provenance_scheduler_narrative_governance_policy_template_audit_records.values())
    )
    stitched_list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records",
      None,
    )
    stitched_records = (
      tuple(stitched_list_records())
      if callable(stitched_list_records)
      else tuple(self._provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records.values())
    )
    return tuple(
      sorted(
        (*shared_records, *stitched_records),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_hierarchy_step_templates[
      record.hierarchy_step_template_id
    ] = record
    return record

  def _load_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record(
    self,
    hierarchy_step_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord | None:
    get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template",
      None,
    )
    if callable(get_record):
      return get_record(hierarchy_step_template_id)
    return self._provider_provenance_scheduler_narrative_governance_hierarchy_step_templates.get(
      hierarchy_step_template_id
    )

  def _list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_hierarchy_step_templates",
      None,
    )
    if callable(list_records):
      return tuple(list_records())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_governance_hierarchy_step_templates.values(),
        key=lambda record: (record.updated_at, record.hierarchy_step_template_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord:
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions[
      record.revision_id
    ] = record
    return record

  def _load_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord | None:
    get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision",
      None,
    )
    if callable(get_record):
      return get_record(revision_id)
    return self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions.get(
      revision_id
    )

  def _list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions",
      None,
    )
    if callable(list_records):
      return tuple(list_records())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord:
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_record",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records[
      record.audit_id
    ] = record
    return record

  def _list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records",
      None,
    )
    if callable(list_records):
      return tuple(list_records())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records.values(),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    if self._uses_provider_provenance_scheduler_stitched_report_governance_policy_store(
      record.item_type_scope
    ):
      save_record = getattr(
        self._runs,
        "save_provider_provenance_scheduler_stitched_report_governance_policy_catalog",
        None,
      )
      if callable(save_record):
        return save_record(record)
      self._provider_provenance_scheduler_stitched_report_governance_policy_catalogs[
        record.catalog_id
      ] = record
      return record
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_policy_catalog",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_policy_catalogs[record.catalog_id] = record
    return record

  def _load_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
    self,
    catalog_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord | None:
    get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_narrative_governance_policy_catalog",
      None,
    )
    if callable(get_record):
      record = get_record(catalog_id)
      if record is not None:
        return record
    else:
      record = self._provider_provenance_scheduler_narrative_governance_policy_catalogs.get(catalog_id)
      if record is not None:
        return record
    stitched_get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_stitched_report_governance_policy_catalog",
      None,
    )
    if callable(stitched_get_record):
      return stitched_get_record(catalog_id)
    return self._provider_provenance_scheduler_stitched_report_governance_policy_catalogs.get(catalog_id)

  def _list_provider_provenance_scheduler_narrative_governance_policy_catalog_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_policy_catalogs",
      None,
    )
    shared_records = (
      tuple(list_records())
      if callable(list_records)
      else tuple(self._provider_provenance_scheduler_narrative_governance_policy_catalogs.values())
    )
    stitched_list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_policy_catalogs",
      None,
    )
    stitched_records = (
      tuple(stitched_list_records())
      if callable(stitched_list_records)
      else tuple(self._provider_provenance_scheduler_stitched_report_governance_policy_catalogs.values())
    )
    return tuple(
      sorted(
        (*shared_records, *stitched_records),
        key=lambda record: (record.updated_at, record.catalog_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord:
    if self._uses_provider_provenance_scheduler_stitched_report_governance_policy_store(
      record.item_type_scope
    ):
      save_record = getattr(
        self._runs,
        "save_provider_provenance_scheduler_stitched_report_governance_policy_catalog_revision",
        None,
      )
      if callable(save_record):
        return save_record(record)
      self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions[
        record.revision_id
      ] = record
      return record
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_policy_catalog_revision",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_policy_catalog_revisions[record.revision_id] = record
    return record

  def _load_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord | None:
    get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_narrative_governance_policy_catalog_revision",
      None,
    )
    if callable(get_record):
      record = get_record(revision_id)
      if record is not None:
        return record
    else:
      record = self._provider_provenance_scheduler_narrative_governance_policy_catalog_revisions.get(
        revision_id
      )
      if record is not None:
        return record
    stitched_get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_stitched_report_governance_policy_catalog_revision",
      None,
    )
    if callable(stitched_get_record):
      return stitched_get_record(revision_id)
    return self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions.get(
      revision_id
    )

  def _list_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_policy_catalog_revisions",
      None,
    )
    shared_records = (
      tuple(list_records())
      if callable(list_records)
      else tuple(self._provider_provenance_scheduler_narrative_governance_policy_catalog_revisions.values())
    )
    stitched_list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions",
      None,
    )
    stitched_records = (
      tuple(stitched_list_records())
      if callable(stitched_list_records)
      else tuple(self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions.values())
    )
    return tuple(
      sorted(
        (*shared_records, *stitched_records),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord:
    if self._uses_provider_provenance_scheduler_stitched_report_governance_policy_store(
      record.item_type_scope
    ):
      save_record = getattr(
        self._runs,
        "save_provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_record",
        None,
      )
      if callable(save_record):
        return save_record(record)
      self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records[
        record.audit_id
      ] = record
      return record
    save_record = getattr(
      self._runs,
      "save_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record",
      None,
    )
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records[record.audit_id] = (
      record
    )
    return record

  def _list_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord, ...]:
    list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records",
      None,
    )
    shared_records = (
      tuple(list_records())
      if callable(list_records)
      else tuple(self._provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records.values())
    )
    stitched_list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records",
      None,
    )
    stitched_records = (
      tuple(stitched_list_records())
      if callable(stitched_list_records)
      else tuple(self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records.values())
    )
    return tuple(
      sorted(
        (*shared_records, *stitched_records),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_narrative_governance_plan_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePlanRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    if self._uses_provider_provenance_scheduler_stitched_report_governance_plan_store(record.item_type):
      save_record = getattr(
        self._runs,
        "save_provider_provenance_scheduler_stitched_report_governance_plan",
        None,
      )
      if callable(save_record):
        return save_record(record)
      self._provider_provenance_scheduler_stitched_report_governance_plans[record.plan_id] = record
      return record
    save_record = getattr(self._runs, "save_provider_provenance_scheduler_narrative_governance_plan", None)
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_narrative_governance_plans[record.plan_id] = record
    return record

  def _load_provider_provenance_scheduler_narrative_governance_plan_record(
    self,
    plan_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord | None:
    get_record = getattr(self._runs, "get_provider_provenance_scheduler_narrative_governance_plan", None)
    if callable(get_record):
      record = get_record(plan_id)
      if record is not None:
        return record
    else:
      record = self._provider_provenance_scheduler_narrative_governance_plans.get(plan_id)
      if record is not None:
        return record
    stitched_get_record = getattr(
      self._runs,
      "get_provider_provenance_scheduler_stitched_report_governance_plan",
      None,
    )
    if callable(stitched_get_record):
      return stitched_get_record(plan_id)
    return self._provider_provenance_scheduler_stitched_report_governance_plans.get(plan_id)

  def _list_provider_provenance_scheduler_narrative_governance_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePlanRecord, ...]:
    list_records = getattr(self._runs, "list_provider_provenance_scheduler_narrative_governance_plans", None)
    shared_records = (
      tuple(list_records())
      if callable(list_records)
      else tuple(self._provider_provenance_scheduler_narrative_governance_plans.values())
    )
    stitched_list_records = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_plans",
      None,
    )
    stitched_records = (
      tuple(stitched_list_records())
      if callable(stitched_list_records)
      else tuple(self._provider_provenance_scheduler_stitched_report_governance_plans.values())
    )
    return tuple(
      sorted(
        (*shared_records, *stitched_records),
        key=lambda record: (record.updated_at, record.plan_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduled_report_audit_record(
    self,
    record: ProviderProvenanceScheduledReportAuditRecord,
  ) -> ProviderProvenanceScheduledReportAuditRecord:
    save_audit = getattr(self._runs, "save_provider_provenance_scheduled_report_audit_record", None)
    if callable(save_audit):
      return save_audit(record)
    self._provider_provenance_scheduled_report_audit_records[record.audit_id] = record
    return record

  def _list_provider_provenance_scheduled_report_audit_records(
    self,
    report_id: str | None = None,
  ) -> tuple[ProviderProvenanceScheduledReportAuditRecord, ...]:
    list_audits = getattr(self._runs, "list_provider_provenance_scheduled_report_audit_records", None)
    if callable(list_audits):
      return tuple(list_audits(report_id))
    records = [
      record
      for record in self._provider_provenance_scheduled_report_audit_records.values()
      if report_id is None or record.report_id == report_id
    ]
    return tuple(
      sorted(
        records,
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def _prune_provider_provenance_scheduled_report_audit_records(self) -> int:
    current_time = self._clock()
    prune_audits = getattr(self._runs, "prune_provider_provenance_scheduled_report_audit_records", None)
    if callable(prune_audits):
      return int(prune_audits(current_time))
    original_count = len(self._provider_provenance_scheduled_report_audit_records)
    self._provider_provenance_scheduled_report_audit_records = {
      audit_id: record
      for audit_id, record in self._provider_provenance_scheduled_report_audit_records.items()
      if record.expires_at is None or record.expires_at > current_time
    }
    return original_count - len(self._provider_provenance_scheduled_report_audit_records)

  def _save_provider_provenance_scheduler_health_record(
    self,
    record: ProviderProvenanceSchedulerHealthRecord,
  ) -> ProviderProvenanceSchedulerHealthRecord:
    save_record = getattr(self._runs, "save_provider_provenance_scheduler_health_record", None)
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_health_records[record.record_id] = record
    return record

  def _list_provider_provenance_scheduler_health_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerHealthRecord, ...]:
    list_records = getattr(self._runs, "list_provider_provenance_scheduler_health_records", None)
    if callable(list_records):
      return tuple(list_records())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_health_records.values(),
        key=lambda record: (record.recorded_at, record.record_id),
        reverse=True,
      )
    )

  def _prune_provider_provenance_scheduler_health_records(self) -> int:
    current_time = self._clock()
    prune_records = getattr(self._runs, "prune_provider_provenance_scheduler_health_records", None)
    if callable(prune_records):
      pruned_count = int(prune_records(current_time))
      self._prune_provider_provenance_scheduler_search_document_records()
      self._prune_provider_provenance_scheduler_search_query_analytics_records()
      self._prune_provider_provenance_scheduler_search_feedback_records()
      return pruned_count
    original_count = len(self._provider_provenance_scheduler_health_records)
    self._provider_provenance_scheduler_health_records = {
      record_id: record
      for record_id, record in self._provider_provenance_scheduler_health_records.items()
      if record.expires_at is None or record.expires_at > current_time
    }
    self._prune_provider_provenance_scheduler_search_document_records()
    self._prune_provider_provenance_scheduler_search_query_analytics_records()
    self._prune_provider_provenance_scheduler_search_feedback_records()
    return original_count - len(self._provider_provenance_scheduler_health_records)

  def _save_provider_provenance_scheduler_search_document_record(
    self,
    record: ProviderProvenanceSchedulerSearchDocumentRecord,
  ) -> ProviderProvenanceSchedulerSearchDocumentRecord:
    return self._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_document_record(
      record
    )

  def _list_provider_provenance_scheduler_search_document_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchDocumentRecord, ...]:
    return tuple(
      self._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_document_records()
    )

  def _prune_provider_provenance_scheduler_search_document_records(self) -> int:
    current_time = self._clock()
    return int(
      self._provider_provenance_scheduler_search_backend.prune_provider_provenance_scheduler_search_document_records(
        current_time
      )
    )

  def _save_provider_provenance_scheduler_search_query_analytics_record(
    self,
    record: ProviderProvenanceSchedulerSearchQueryAnalyticsRecord,
  ) -> ProviderProvenanceSchedulerSearchQueryAnalyticsRecord:
    return self._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_query_analytics_record(
      record
    )

  def _list_provider_provenance_scheduler_search_query_analytics_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchQueryAnalyticsRecord, ...]:
    return tuple(
      self._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_query_analytics_records()
    )

  def _prune_provider_provenance_scheduler_search_query_analytics_records(self) -> int:
    current_time = self._clock()
    return int(
      self._provider_provenance_scheduler_search_backend.prune_provider_provenance_scheduler_search_query_analytics_records(
        current_time
      )
    )

  def _save_provider_provenance_scheduler_search_feedback_record(
    self,
    record: ProviderProvenanceSchedulerSearchFeedbackRecord,
  ) -> ProviderProvenanceSchedulerSearchFeedbackRecord:
    return self._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_feedback_record(
      record
    )

  def _list_provider_provenance_scheduler_search_feedback_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchFeedbackRecord, ...]:
    return tuple(
      self._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_feedback_records()
    )

  def _prune_provider_provenance_scheduler_search_feedback_records(self) -> int:
    current_time = self._clock()
    return int(
      self._provider_provenance_scheduler_search_backend.prune_provider_provenance_scheduler_search_feedback_records(
        current_time
      )
    )

  def _save_provider_provenance_scheduler_search_moderation_policy_catalog_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord:
    return (
      self._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_moderation_policy_catalog_record(
        record
      )
    )

  def _list_provider_provenance_scheduler_search_moderation_policy_catalog_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord, ...]:
    return tuple(
      self._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_moderation_policy_catalog_records()
    )

  def _save_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord:
    return (
      self._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
        record
      )
    )

  def _list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord, ...]:
    return tuple(
      self._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records()
    )

  def _save_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord:
    return (
      self._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
        record
      )
    )

  def _list_provider_provenance_scheduler_search_moderation_policy_catalog_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord, ...]:
    return tuple(
      self._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_moderation_policy_catalog_audit_records()
    )

  def _save_provider_provenance_scheduler_search_moderation_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPlanRecord:
    return (
      self._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_moderation_plan_record(
        record
      )
    )

  def _list_provider_provenance_scheduler_search_moderation_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPlanRecord, ...]:
    return tuple(
      self._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_moderation_plan_records()
    )

  def _save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
    return save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record_support(
      self,
      record,
    )

  def _list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord, ...]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records_support(
      self
    )

  def _save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord:
    return save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record_support(
      self,
      record,
    )

  def _list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord, ...]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records_support(
      self
    )

  def _save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord:
    return save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record_support(
      self,
      record,
    )

  def _list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord, ...]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records_support(
      self
    )

  def _save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord:
    return save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record_support(
      self,
      record,
    )

  def _list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord, ...]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records_support(
      self
    )

  def _save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord:
    return save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record_support(
      self,
      record,
    )

  def _list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord, ...]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records_support(
      self
    )

  def _save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord:
    return save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record_support(
      self,
      record,
    )

  def _list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord, ...]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_records_support(
      self
    )

  def _provider_provenance_scheduler_search_persistence_mode(self) -> str:
    persistence_mode = getattr(
      self._provider_provenance_scheduler_search_backend,
      "persistence_mode",
      None,
    )
    if isinstance(persistence_mode, str) and persistence_mode.strip():
      return persistence_mode.strip()
    return "embedded_scheduler_search_service"

  @staticmethod
  def _build_provider_provenance_scheduler_search_document_record(
    *,
    record: ProviderProvenanceSchedulerHealthRecord,
    search_projection: Mapping[str, Any],
  ) -> ProviderProvenanceSchedulerSearchDocumentRecord:
    normalized_fields = {
      key: tuple(
        value
        for value in values
        if isinstance(value, str) and value.strip()
      )
      for key, values in (search_projection.get("fields", {}) or {}).items()
      if isinstance(key, str)
    }
    return ProviderProvenanceSchedulerSearchDocumentRecord(
      record_id=record.record_id,
      recorded_at=record.recorded_at,
      scheduler_key=record.scheduler_key,
      expires_at=record.expires_at,
      index_version=(
        search_projection.get("index_version")
        if isinstance(search_projection.get("index_version"), str)
        and search_projection.get("index_version").strip()
        else "scheduler-search-store.v1"
      ),
      lexical_terms=tuple(
        token
        for token in (search_projection.get("lexical_terms", ()) or ())
        if isinstance(token, str) and token.strip()
      ),
      semantic_concepts=tuple(
        concept
        for concept in (search_projection.get("semantic_concepts", ()) or ())
        if isinstance(concept, str) and concept.strip()
      ),
      fields=normalized_fields,
    )

  def _record_provider_provenance_scheduler_health(
    self,
    *,
    snapshot: ProviderProvenanceSchedulerHealth,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerHealthRecord:
    self._prune_provider_provenance_scheduler_health_records()
    search_projection = self._build_provider_provenance_scheduler_health_search_projection(
      snapshot=snapshot
    )
    record = ProviderProvenanceSchedulerHealthRecord(
      record_id=uuid4().hex[:12],
      recorded_at=snapshot.generated_at,
      expires_at=self._build_replay_intent_alias_audit_expiry(
        retention_policy="90d",
        recorded_at=snapshot.generated_at,
      ),
      enabled=snapshot.enabled,
      status=snapshot.status,
      summary=snapshot.summary,
      interval_seconds=snapshot.interval_seconds,
      batch_limit=snapshot.batch_limit,
      last_cycle_started_at=snapshot.last_cycle_started_at,
      last_cycle_finished_at=snapshot.last_cycle_finished_at,
      last_success_at=snapshot.last_success_at,
      last_failure_at=snapshot.last_failure_at,
      last_error=snapshot.last_error,
      cycle_count=snapshot.cycle_count,
      success_count=snapshot.success_count,
      failure_count=snapshot.failure_count,
      consecutive_failure_count=snapshot.consecutive_failure_count,
      last_executed_count=snapshot.last_executed_count,
      total_executed_count=snapshot.total_executed_count,
      due_report_count=snapshot.due_report_count,
      oldest_due_at=snapshot.oldest_due_at,
      max_due_lag_seconds=snapshot.max_due_lag_seconds,
      active_alert_key=snapshot.active_alert_key,
      alert_workflow_job_id=snapshot.alert_workflow_job_id,
      alert_workflow_triggered_at=snapshot.alert_workflow_triggered_at,
      alert_workflow_state=snapshot.alert_workflow_state,
      alert_workflow_summary=snapshot.alert_workflow_summary,
      source_tab_id=source_tab_id.strip() if isinstance(source_tab_id, str) and source_tab_id.strip() else None,
      source_tab_label=(
        source_tab_label.strip()
        if isinstance(source_tab_label, str) and source_tab_label.strip()
        else None
      ),
      issues=tuple(snapshot.issues),
    )
    saved_record = self._save_provider_provenance_scheduler_health_record(record)
    self._save_provider_provenance_scheduler_search_document_record(
      self._build_provider_provenance_scheduler_search_document_record(
        record=saved_record,
        search_projection=search_projection,
      )
    )
    return saved_record

  @staticmethod
  def _build_provider_provenance_scheduler_alert_workflow_reason(status: str) -> str:
    if status == "failed":
      return "scheduler_failure_auto_export"
    return "scheduler_lag_auto_export"

  def _build_provider_provenance_scheduler_alert_key(
    self,
    *,
    current: ProviderProvenanceSchedulerHealth,
    previous: ProviderProvenanceSchedulerHealth | None = None,
  ) -> str | None:
    if current.status not in {"lagging", "failed"}:
      return None
    if (
      previous is not None
      and previous.status == current.status
      and isinstance(previous.active_alert_key, str)
      and previous.active_alert_key.strip()
    ):
      return previous.active_alert_key
    if current.status == "failed":
      anchor = (
        current.last_success_at
        or current.last_failure_at
        or current.last_cycle_started_at
        or current.generated_at
      )
    else:
      anchor = current.oldest_due_at or current.last_success_at or current.generated_at
    return f"{current.status}:{anchor.isoformat()}"

  def _get_provider_provenance_export_job_content(
    self,
    record: ProviderProvenanceExportJobRecord,
  ) -> str:
    if record.artifact_id:
      artifact_record = self.get_provider_provenance_export_artifact(record.artifact_id)
      return artifact_record.content
    return record.content

  def _find_provider_provenance_scheduler_alert_export_job(
    self,
    *,
    alert_key: str,
  ) -> ProviderProvenanceExportJobRecord | None:
    if not isinstance(alert_key, str) or not alert_key.strip():
      return None
    for record in self.list_provider_provenance_export_jobs(
      export_scope="provider_provenance_scheduler_health",
      requested_by_tab_id=PROVIDER_PROVENANCE_SCHEDULER_ALERT_AUTOMATION_TAB_ID,
      limit=200,
    ):
      try:
        payload = json.loads(self._get_provider_provenance_export_job_content(record))
      except (TypeError, ValueError, json.JSONDecodeError):
        continue
      if not isinstance(payload, dict):
        continue
      automation_payload = payload.get("automation")
      if not isinstance(automation_payload, dict):
        continue
      candidate_alert_key = automation_payload.get("alert_key")
      if isinstance(candidate_alert_key, str) and candidate_alert_key.strip() == alert_key:
        return record
    return None

  @staticmethod
  def _build_provider_provenance_scheduler_alert_workflow_state(
    record: ProviderProvenanceExportJobRecord,
  ) -> tuple[str, str]:
    if record.escalation_count > 0:
      delivery_status = record.last_delivery_status or "delivered"
      return (
        f"escalated_{delivery_status}",
        record.last_delivery_summary or "Scheduler alert export workflow escalated.",
      )
    if not record.routing_targets:
      return (
        "route_unconfigured",
        "Scheduler alert export was created but routing targets are not configured.",
      )
    if record.approval_required and record.approval_state != "approved":
      return (
        "approval_pending",
        record.approval_summary
        or "Scheduler alert export workflow is waiting for operator approval.",
      )
    return (
      "created",
      record.routing_policy_summary
      or "Scheduler alert export workflow was created and is ready for delivery.",
    )

  def _run_provider_provenance_scheduler_alert_workflow(
    self,
    *,
    snapshot: ProviderProvenanceSchedulerHealth,
    previous_snapshot: ProviderProvenanceSchedulerHealth | None = None,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerHealth:
    alert_key = self._build_provider_provenance_scheduler_alert_key(
      current=snapshot,
      previous=previous_snapshot,
    )
    if alert_key is None:
      return replace(
        snapshot,
        active_alert_key=None,
        alert_workflow_job_id=None,
        alert_workflow_triggered_at=None,
        alert_workflow_state=None,
        alert_workflow_summary=None,
      )
    existing_job = self._find_provider_provenance_scheduler_alert_export_job(alert_key=alert_key)
    reason = self._build_provider_provenance_scheduler_alert_workflow_reason(snapshot.status)
    try:
      job = existing_job
      if job is None:
        export_payload = self.export_provider_provenance_scheduler_health(
          export_format="json",
          status=snapshot.status,
          window_days=14,
          history_limit=12,
          limit=25,
          offset=0,
        )
        content_payload = json.loads(export_payload["content"])
        if not isinstance(content_payload, dict):
          raise ValueError("Scheduler alert export content must be a JSON object.")
        content_payload["automation"] = {
          "kind": "scheduler_alert_workflow",
          "alert_key": alert_key,
          "alert_status": snapshot.status,
          "trigger": "automatic",
          "reason": reason,
          "generated_at": snapshot.generated_at.isoformat(),
          "detected_at": (
            snapshot.last_failure_at.isoformat()
            if snapshot.status == "failed" and snapshot.last_failure_at is not None
            else (
              snapshot.oldest_due_at.isoformat()
              if snapshot.status == "lagging" and snapshot.oldest_due_at is not None
              else snapshot.generated_at.isoformat()
            )
          ),
        }
        job = self.create_provider_provenance_export_job(
          content=json.dumps(content_payload, indent=2, sort_keys=True),
          requested_by_tab_id=PROVIDER_PROVENANCE_SCHEDULER_ALERT_AUTOMATION_TAB_ID,
          requested_by_tab_label=PROVIDER_PROVENANCE_SCHEDULER_ALERT_AUTOMATION_TAB_LABEL,
        )
        self._record_provider_provenance_export_job_event(
          record=job,
          action="automation_triggered",
          source_tab_id=source_tab_id or PROVIDER_PROVENANCE_SCHEDULER_ALERT_AUTOMATION_TAB_ID,
          source_tab_label=source_tab_label or PROVIDER_PROVENANCE_SCHEDULER_ALERT_AUTOMATION_TAB_LABEL,
          detail=(
            f"Scheduler {snapshot.status} alert opened automatic export workflow "
            f"for alert key {alert_key}."
          ),
          routing_policy_id=job.routing_policy_id,
          routing_targets=job.routing_targets,
          approval_policy_id=job.approval_policy_id,
          approval_required=job.approval_required,
          approval_state=job.approval_state,
          approval_summary=job.approval_summary,
          approved_by=job.approved_by,
        )
      if (
        job.escalation_count == 0
        and job.routing_targets
        and (not job.approval_required or job.approval_state == "approved")
      ):
        escalation_result = self.escalate_provider_provenance_export_job(
          job.job_id,
          actor="system",
          reason=reason,
          source_tab_id=source_tab_id or PROVIDER_PROVENANCE_SCHEDULER_ALERT_AUTOMATION_TAB_ID,
          source_tab_label=(
            source_tab_label or PROVIDER_PROVENANCE_SCHEDULER_ALERT_AUTOMATION_TAB_LABEL
          ),
        )
        job = escalation_result["export_job"]
      workflow_state, workflow_summary = (
        self._build_provider_provenance_scheduler_alert_workflow_state(job)
      )
      return replace(
        snapshot,
        active_alert_key=alert_key,
        alert_workflow_job_id=job.job_id,
        alert_workflow_triggered_at=job.created_at,
        alert_workflow_state=workflow_state,
        alert_workflow_summary=workflow_summary,
      )
    except Exception as exc:
      return replace(
        snapshot,
        active_alert_key=alert_key,
        alert_workflow_job_id=(
          existing_job.job_id if existing_job is not None else snapshot.alert_workflow_job_id
        ),
        alert_workflow_triggered_at=(
          existing_job.created_at
          if existing_job is not None
          else snapshot.alert_workflow_triggered_at
        ),
        alert_workflow_state="automation_failed",
        alert_workflow_summary=(
          f"Scheduler {snapshot.status} alert automation failed: {exc}"
        ),
      )

  def _record_provider_provenance_scheduled_report_event(
    self,
    *,
    record: ProviderProvenanceScheduledReportRecord,
    action: str,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
    export_job_id: str | None = None,
    detail: str | None = None,
  ) -> ProviderProvenanceScheduledReportAuditRecord:
    self._prune_provider_provenance_scheduled_report_audit_records()
    recorded_at = self._clock()
    audit_record = ProviderProvenanceScheduledReportAuditRecord(
      audit_id=uuid4().hex[:12],
      report_id=record.report_id,
      action=action,
      recorded_at=recorded_at,
      expires_at=self._build_replay_intent_alias_audit_expiry(
        retention_policy="30d",
        recorded_at=recorded_at,
      ),
      source_tab_id=source_tab_id.strip() if isinstance(source_tab_id, str) and source_tab_id.strip() else None,
      source_tab_label=(
        source_tab_label.strip()
        if isinstance(source_tab_label, str) and source_tab_label.strip()
        else None
      ),
      export_job_id=export_job_id.strip() if isinstance(export_job_id, str) and export_job_id.strip() else None,
      detail=detail or f"Provider provenance scheduled report {action}.",
    )
    return self._save_provider_provenance_scheduled_report_audit_record(audit_record)

  @staticmethod
  def _calculate_provider_provenance_scheduled_report_next_run(
    *,
    reference_time: datetime,
    cadence: str,
    status: str,
  ) -> datetime | None:
    if status != "scheduled":
      return None
    if cadence == "weekly":
      return reference_time + timedelta(days=7)
    return reference_time + timedelta(days=1)

  @staticmethod
  def _normalize_provider_provenance_export_strings(values: Iterable[Any]) -> tuple[str, ...]:
    normalized_values: list[str] = []
    for value in values:
      if not isinstance(value, str):
        continue
      candidate = value.strip()
      if candidate and candidate not in normalized_values:
        normalized_values.append(candidate)
    return tuple(normalized_values)

  @staticmethod
  def _build_provider_provenance_export_filename(
    *,
    export_scope: str,
    symbol: str | None,
    timeframe: str | None,
    exported_at: datetime | None,
    fallback_time: datetime,
  ) -> str:
    if export_scope == "provider_provenance_scheduler_health":
      timestamp = (exported_at or fallback_time).astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
      return f"provider-provenance-scheduler-health-{timestamp}.json"
    safe_symbol = re.sub(r"[^a-z0-9]+", "-", (symbol or "market").lower()).strip("-") or "market"
    safe_timeframe = re.sub(r"[^a-z0-9]+", "-", (timeframe or "window").lower()).strip("-") or "window"
    timestamp = (exported_at or fallback_time).astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"provider-provenance-{safe_symbol}-{safe_timeframe}-{timestamp}.json"

  @classmethod
  def _extract_provider_provenance_export_metadata(
    cls,
    payload: dict[str, Any],
  ) -> dict[str, Any]:
    export_scope = (
      payload.get("export_scope").strip()
      if isinstance(payload.get("export_scope"), str) and payload.get("export_scope").strip()
      else "provider_market_context_provenance"
    )
    focus = payload.get("focus") if isinstance(payload.get("focus"), dict) else {}
    instrument_id = (
      focus.get("instrument_id").strip()
      if isinstance(focus.get("instrument_id"), str) and focus.get("instrument_id").strip()
      else None
    )
    symbol = (
      focus.get("symbol").strip()
      if isinstance(focus.get("symbol"), str) and focus.get("symbol").strip()
      else None
    )
    if symbol is None and instrument_id is not None:
      separator_index = instrument_id.find(":")
      symbol = instrument_id[separator_index + 1:] if separator_index >= 0 else instrument_id
    timeframe = (
      focus.get("timeframe").strip()
      if isinstance(focus.get("timeframe"), str) and focus.get("timeframe").strip()
      else None
    )
    focus_key = f"{instrument_id}|{timeframe}" if instrument_id and timeframe else None
    focus_label = f"{symbol} · {timeframe}" if symbol and timeframe else symbol or timeframe
    export_filters = deepcopy(payload.get("export_filter")) if isinstance(payload.get("export_filter"), dict) else {}
    if export_scope == "provider_provenance_scheduler_health":
      query_payload = payload.get("query") if isinstance(payload.get("query"), dict) else {}
      current_payload = payload.get("current") if isinstance(payload.get("current"), dict) else {}
      history_payload = payload.get("history_page") if isinstance(payload.get("history_page"), dict) else {}
      result_count = (
        int(history_payload["total"])
        if isinstance(history_payload.get("total"), Number)
        else (
          int(payload["total_count"])
          if isinstance(payload.get("total_count"), Number)
          else 0
        )
      )
      window_days = (
        int(query_payload["window_days"])
        if isinstance(query_payload.get("window_days"), Number)
        else None
      )
      filter_tokens: list[str] = []
      if isinstance(query_payload.get("status"), str) and query_payload.get("status").strip():
        filter_tokens.append(f"status {query_payload['status'].strip()}")
      else:
        filter_tokens.append("all statuses")
      if window_days is not None:
        filter_tokens.append(f"{window_days}d window")
      if isinstance(query_payload.get("drilldown_bucket_key"), str) and query_payload.get("drilldown_bucket_key").strip():
        filter_tokens.append(f"hour drill-down {query_payload['drilldown_bucket_key'].strip()}")
      if (
        isinstance(query_payload.get("reconstruction_mode"), str)
        and query_payload.get("reconstruction_mode").strip() == "resolved_alert_row"
      ):
        filter_tokens.append("resolved alert reconstruction")
      if (
        isinstance(query_payload.get("reconstruction_mode"), str)
        and query_payload.get("reconstruction_mode").strip() == "stitched_occurrence_report"
      ):
        filter_tokens.append("stitched occurrence report")
      if (
        isinstance(query_payload.get("narrative_mode"), str)
        and query_payload.get("narrative_mode").strip() == "mixed_status_post_resolution"
      ):
        filter_tokens.append("mixed-status narrative")
      if (
        isinstance(query_payload.get("narrative_mode"), str)
        and query_payload.get("narrative_mode").strip() == "stitched_multi_occurrence"
      ):
        filter_tokens.append("stitched multi-occurrence narrative")
      if (
        isinstance(query_payload.get("alert_category"), str)
        and query_payload.get("alert_category").strip()
      ):
        filter_tokens.append(query_payload["alert_category"].strip())
      if (
        isinstance(query_payload.get("narrative_facet"), str)
        and query_payload.get("narrative_facet").strip()
      ):
        filter_tokens.append(query_payload["narrative_facet"].strip())
      if isinstance(query_payload.get("occurrence_limit"), Number):
        filter_tokens.append(f"{int(query_payload['occurrence_limit'])} occurrence(s)")
      filter_summary = " / ".join(filter_tokens)
      if not export_filters:
        export_filters = {
          key: value
          for key, value in query_payload.items()
          if value is not None and value != ""
        }
      return {
        "export_scope": export_scope,
        "exported_at": cls._parse_optional_iso_datetime(payload.get("exported_at")),
        "focus_key": "provider-provenance-scheduler-health",
        "focus_label": "Scheduler automation",
        "market_data_provider": "provider_provenance_scheduler",
        "venue": None,
        "symbol": None,
        "timeframe": None,
        "result_count": max(result_count, 0),
        "provider_provenance_count": 0,
        "provider_labels": (),
        "vendor_fields": (),
        "filter_summary": (
          filter_summary
          if filter_summary
          else (
            current_payload.get("summary").strip()
            if isinstance(current_payload.get("summary"), str) and current_payload.get("summary").strip()
            else None
          )
        ),
        "filters": export_filters,
      }
    if export_scope == "provider_provenance_analytics_report":
      analytics_payload = payload.get("analytics") if isinstance(payload.get("analytics"), dict) else {}
      totals_payload = analytics_payload.get("totals") if isinstance(analytics_payload.get("totals"), dict) else {}
      available_filters_payload = (
        analytics_payload.get("available_filters")
        if isinstance(analytics_payload.get("available_filters"), dict)
        else {}
      )
      provider_labels = cls._normalize_provider_provenance_export_strings(
        available_filters_payload.get("provider_labels")
        if isinstance(available_filters_payload.get("provider_labels"), list)
        else ()
      )
      vendor_fields = cls._normalize_provider_provenance_export_strings(
        available_filters_payload.get("vendor_fields")
        if isinstance(available_filters_payload.get("vendor_fields"), list)
        else ()
      )
      result_count = (
        int(totals_payload["result_count"])
        if isinstance(totals_payload.get("result_count"), Number)
        else 0
      )
      provider_provenance_count = (
        int(totals_payload["provider_provenance_count"])
        if isinstance(totals_payload.get("provider_provenance_count"), Number)
        else (
          int(focus["provider_provenance_incident_count"])
          if isinstance(focus.get("provider_provenance_incident_count"), Number)
          else 0
        )
      )
    else:
      provider_incidents = (
        payload.get("provider_provenance_incidents")
        if isinstance(payload.get("provider_provenance_incidents"), list)
        else []
      )
      provider_labels = cls._normalize_provider_provenance_export_strings(
        incident.get("provider")
        for incident in provider_incidents
        if isinstance(incident, dict)
      )
      vendor_fields = cls._normalize_provider_provenance_export_strings(
        incident.get("vendor_field")
        for incident in provider_incidents
        if isinstance(incident, dict)
      )
      result_count = (
        int(payload["export_result_count"])
        if isinstance(payload.get("export_result_count"), Number)
        else len(provider_incidents)
      )
      provider_provenance_count = (
        int(focus["provider_provenance_incident_count"])
        if isinstance(focus.get("provider_provenance_incident_count"), Number)
        else len(provider_incidents)
      )
    return {
      "export_scope": export_scope,
      "exported_at": cls._parse_optional_iso_datetime(payload.get("exported_at")),
      "focus_key": focus_key,
      "focus_label": focus_label,
      "market_data_provider": (
        focus.get("provider").strip()
        if isinstance(focus.get("provider"), str) and focus.get("provider").strip()
        else None
      ),
      "venue": (
        focus.get("venue").strip()
        if isinstance(focus.get("venue"), str) and focus.get("venue").strip()
        else None
      ),
      "symbol": symbol,
      "timeframe": timeframe,
      "result_count": max(result_count, 0),
      "provider_provenance_count": max(provider_provenance_count, 0),
      "provider_labels": provider_labels,
      "vendor_fields": vendor_fields,
      "filter_summary": (
        payload.get("export_filter_summary").strip()
        if isinstance(payload.get("export_filter_summary"), str) and payload.get("export_filter_summary").strip()
        else None
      ),
      "filters": export_filters,
    }

  @classmethod
  def _normalize_provider_provenance_export_content(
    cls,
    content: str,
  ) -> tuple[str, dict[str, Any], dict[str, Any]]:
    normalized_content = content.strip() if isinstance(content, str) else ""
    if not normalized_content:
      raise ValueError("Provider provenance export content is required.")
    try:
      payload = json.loads(normalized_content)
    except json.JSONDecodeError as exc:
      raise ValueError("Provider provenance export content must be valid JSON.") from exc
    if not isinstance(payload, dict):
      raise ValueError("Provider provenance export content must be a JSON object.")
    metadata = cls._extract_provider_provenance_export_metadata(payload)
    if metadata["export_scope"] not in {
      "provider_market_context_provenance",
      "provider_provenance_analytics_report",
      "provider_provenance_scheduler_health",
    }:
      raise ValueError("Unsupported provider provenance export scope.")
    if (
      metadata["export_scope"] == "provider_market_context_provenance"
      and (metadata["focus_key"] is None or metadata["symbol"] is None or metadata["timeframe"] is None)
    ):
      raise ValueError("Provider provenance export content must include focus instrument_id, symbol, and timeframe.")
    return normalized_content, payload, metadata


  def create_provider_provenance_export_job(
    self,
    *,
    content: str,
    requested_by_tab_id: str | None = None,
    requested_by_tab_label: str | None = None,
  ) -> ProviderProvenanceExportJobRecord:
    self._prune_provider_provenance_export_artifact_records()
    self._prune_provider_provenance_export_job_records()
    self._prune_provider_provenance_export_job_audit_records()
    normalized_content, _, metadata = self._normalize_provider_provenance_export_content(content)
    created_at = self._clock()
    artifact_id = uuid4().hex[:12]
    job_id = uuid4().hex[:12]
    scheduler_policy = None
    if metadata["export_scope"] == "provider_provenance_scheduler_health":
      scheduler_policy = self._build_provider_provenance_scheduler_export_policy(
        content=normalized_content,
        current_time=created_at,
      )
    artifact_record = ProviderProvenanceExportArtifactRecord(
      artifact_id=artifact_id,
      job_id=job_id,
      filename=self._build_provider_provenance_export_filename(
        export_scope=metadata["export_scope"],
        symbol=metadata["symbol"],
        timeframe=metadata["timeframe"],
        exported_at=metadata["exported_at"],
        fallback_time=created_at,
      ),
      content_type="application/json; charset=utf-8",
      content=normalized_content,
      created_at=created_at,
      expires_at=self._build_replay_intent_alias_audit_expiry(
        retention_policy="30d",
        recorded_at=created_at,
      ),
      byte_length=len(normalized_content.encode("utf-8")),
    )
    saved_artifact = self._save_provider_provenance_export_artifact_record(artifact_record)
    record = ProviderProvenanceExportJobRecord(
      job_id=job_id,
      export_scope=metadata["export_scope"],
      export_format="json",
      filename=saved_artifact.filename,
      content_type=saved_artifact.content_type,
      status="completed",
      created_at=created_at,
      completed_at=created_at,
      exported_at=metadata["exported_at"] or created_at,
      expires_at=self._build_replay_intent_alias_audit_expiry(
        retention_policy="30d",
        recorded_at=created_at,
      ),
      focus_key=metadata["focus_key"],
      focus_label=metadata["focus_label"],
      market_data_provider=metadata["market_data_provider"],
      venue=metadata["venue"],
      symbol=metadata["symbol"],
      timeframe=metadata["timeframe"],
      result_count=metadata["result_count"],
      provider_provenance_count=metadata["provider_provenance_count"],
      provider_labels=metadata["provider_labels"],
      vendor_fields=metadata["vendor_fields"],
      filter_summary=metadata["filter_summary"],
      filters=metadata["filters"],
      requested_by_tab_id=(
        requested_by_tab_id.strip()
        if isinstance(requested_by_tab_id, str) and requested_by_tab_id.strip()
        else None
      ),
      requested_by_tab_label=(
        requested_by_tab_label.strip()
        if isinstance(requested_by_tab_label, str) and requested_by_tab_label.strip()
        else None
      ),
      available_delivery_targets=(
        scheduler_policy["available_delivery_targets"] if scheduler_policy is not None else ()
      ),
      routing_policy_id=(
        scheduler_policy["routing_policy_id"] if scheduler_policy is not None else None
      ),
      routing_policy_summary=(
        scheduler_policy["routing_policy_summary"] if scheduler_policy is not None else None
      ),
      routing_targets=(
        scheduler_policy["routing_targets"] if scheduler_policy is not None else ()
      ),
      approval_policy_id=(
        scheduler_policy["approval_policy_id"] if scheduler_policy is not None else None
      ),
      approval_required=(
        scheduler_policy["approval_required"] if scheduler_policy is not None else False
      ),
      approval_state=(
        scheduler_policy["approval_state"] if scheduler_policy is not None else "not_required"
      ),
      approval_summary=(
        scheduler_policy["approval_summary"] if scheduler_policy is not None else None
      ),
      approved_at=(
        scheduler_policy["approved_at"] if scheduler_policy is not None else None
      ),
      approved_by=(
        scheduler_policy["approved_by"] if scheduler_policy is not None else None
      ),
      approval_note=(
        scheduler_policy["approval_note"] if scheduler_policy is not None else None
      ),
      escalation_count=0,
      artifact_id=saved_artifact.artifact_id,
      content_length=saved_artifact.byte_length,
    )
    saved_record = self._save_provider_provenance_export_job_record(record)
    self._record_provider_provenance_export_job_event(
      record=saved_record,
      action="created",
      source_tab_id=requested_by_tab_id,
      source_tab_label=requested_by_tab_label,
    )
    return saved_record

  @classmethod
  def _matches_provider_provenance_export_job_search(
    cls,
    record: ProviderProvenanceExportJobRecord,
    search: str | None,
  ) -> bool:
    if not isinstance(search, str) or not search.strip():
      return True
    needle = search.strip().lower()
    haystacks = (
      record.job_id,
      record.export_scope,
      record.filename,
      record.status,
      record.focus_key or "",
      record.focus_label or "",
      record.market_data_provider or "",
      record.venue or "",
      record.symbol or "",
      record.timeframe or "",
      record.requested_by_tab_id or "",
      record.requested_by_tab_label or "",
      record.filter_summary or "",
      *record.provider_labels,
      *record.vendor_fields,
    )
    return any(needle in value.lower() for value in haystacks if value)

  def _filter_provider_provenance_export_job_records(
    self,
    *,
    export_scope: str | None = None,
    focus_key: str | None = None,
    symbol: str | None = None,
    timeframe: str | None = None,
    provider_label: str | None = None,
    vendor_field: str | None = None,
    market_data_provider: str | None = None,
    venue: str | None = None,
    requested_by_tab_id: str | None = None,
    status: str | None = None,
    search: str | None = None,
  ) -> tuple[ProviderProvenanceExportJobRecord, ...]:
    normalized_export_scope = (
      export_scope.strip()
      if isinstance(export_scope, str) and export_scope.strip()
      else "provider_market_context_provenance"
    )
    normalized_focus_key = focus_key.strip() if isinstance(focus_key, str) and focus_key.strip() else None
    normalized_symbol = symbol.strip() if isinstance(symbol, str) and symbol.strip() else None
    normalized_timeframe = timeframe.strip() if isinstance(timeframe, str) and timeframe.strip() else None
    normalized_provider_label = (
      provider_label.strip()
      if isinstance(provider_label, str) and provider_label.strip()
      else None
    )
    normalized_vendor_field = (
      vendor_field.strip()
      if isinstance(vendor_field, str) and vendor_field.strip()
      else None
    )
    normalized_market_data_provider = (
      market_data_provider.strip()
      if isinstance(market_data_provider, str) and market_data_provider.strip()
      else None
    )
    normalized_venue = venue.strip() if isinstance(venue, str) and venue.strip() else None
    normalized_requested_by_tab_id = (
      requested_by_tab_id.strip()
      if isinstance(requested_by_tab_id, str) and requested_by_tab_id.strip()
      else None
    )
    normalized_status = status.strip().lower() if isinstance(status, str) and status.strip() else None
    search_value = search.strip().lower() if isinstance(search, str) and search.strip() else None
    filtered = [
      record
      for record in self._list_provider_provenance_export_job_records()
      if record.export_scope == normalized_export_scope
      and (normalized_focus_key is None or record.focus_key == normalized_focus_key)
      and (normalized_symbol is None or record.symbol == normalized_symbol)
      and (normalized_timeframe is None or record.timeframe == normalized_timeframe)
      and (normalized_provider_label is None or normalized_provider_label in record.provider_labels)
      and (normalized_vendor_field is None or normalized_vendor_field in record.vendor_fields)
      and (
        normalized_market_data_provider is None
        or record.market_data_provider == normalized_market_data_provider
      )
      and (normalized_venue is None or record.venue == normalized_venue)
      and (
        normalized_requested_by_tab_id is None
        or record.requested_by_tab_id == normalized_requested_by_tab_id
      )
      and (normalized_status is None or record.status == normalized_status)
      and self._matches_provider_provenance_export_job_search(record, search_value)
    ]
    return tuple(filtered)

  def list_provider_provenance_export_jobs(
    self,
    *,
    export_scope: str | None = None,
    focus_key: str | None = None,
    symbol: str | None = None,
    timeframe: str | None = None,
    provider_label: str | None = None,
    vendor_field: str | None = None,
    market_data_provider: str | None = None,
    venue: str | None = None,
    requested_by_tab_id: str | None = None,
    status: str | None = None,
    search: str | None = None,
    limit: int = 100,
  ) -> tuple[ProviderProvenanceExportJobRecord, ...]:
    self._prune_provider_provenance_export_artifact_records()
    self._prune_provider_provenance_export_job_records()
    self._prune_provider_provenance_export_job_audit_records()
    normalized_limit = max(1, min(limit, 500))
    filtered = self._filter_provider_provenance_export_job_records(
      export_scope=export_scope,
      focus_key=focus_key,
      symbol=symbol,
      timeframe=timeframe,
      provider_label=provider_label,
      vendor_field=vendor_field,
      market_data_provider=market_data_provider,
      venue=venue,
      requested_by_tab_id=requested_by_tab_id,
      status=status,
      search=search,
    )
    return tuple(
      self._ensure_provider_provenance_scheduler_export_policy(record)
      for record in filtered[:normalized_limit]
    )

  @staticmethod
  def _normalize_provider_provenance_export_bucket_start(value: datetime) -> datetime:
    normalized_value = value.astimezone(UTC) if value.tzinfo is not None else value.replace(tzinfo=UTC)
    return normalized_value.replace(hour=0, minute=0, second=0, microsecond=0)

  @classmethod
  def _build_provider_provenance_export_time_series(
    cls,
    *,
    records: tuple[ProviderProvenanceExportJobRecord, ...],
    audit_records: tuple[ProviderProvenanceExportJobAuditRecord, ...],
    window_days: int,
    now: datetime,
  ) -> dict[str, Any]:
    normalized_window_days = max(3, min(window_days, 90))
    anchor_candidates = [now]
    anchor_candidates.extend(record.exported_at or record.created_at for record in records)
    anchor_candidates.extend(
      audit_record.recorded_at
      for audit_record in audit_records
      if audit_record.action == "downloaded"
    )
    window_anchor = cls._normalize_provider_provenance_export_bucket_start(max(anchor_candidates))
    window_started_at = window_anchor - timedelta(days=normalized_window_days - 1)
    window_ended_at = window_anchor + timedelta(days=1)

    record_buckets: dict[datetime, list[ProviderProvenanceExportJobRecord]] = {}
    download_counts_by_bucket: dict[datetime, int] = {}
    for record in records:
      bucket_start = cls._normalize_provider_provenance_export_bucket_start(
        record.exported_at or record.created_at
      )
      if not (window_started_at <= bucket_start < window_ended_at):
        continue
      record_buckets.setdefault(bucket_start, []).append(record)
    for audit_record in audit_records:
      if audit_record.action != "downloaded":
        continue
      bucket_start = cls._normalize_provider_provenance_export_bucket_start(audit_record.recorded_at)
      if not (window_started_at <= bucket_start < window_ended_at):
        continue
      download_counts_by_bucket[bucket_start] = download_counts_by_bucket.get(bucket_start, 0) + 1

    provider_drift_series: list[dict[str, Any]] = []
    export_burn_up_series: list[dict[str, Any]] = []
    cumulative_exports = 0
    cumulative_results = 0
    cumulative_provider_provenance = 0
    cumulative_downloads = 0

    for offset in range(normalized_window_days):
      bucket_start = window_started_at + timedelta(days=offset)
      bucket_end = bucket_start + timedelta(days=1)
      bucket_records = record_buckets.get(bucket_start, [])
      export_count = len(bucket_records)
      result_count = sum(record.result_count for record in bucket_records)
      provider_provenance_count = sum(
        record.provider_provenance_count
        for record in bucket_records
      )
      download_count = download_counts_by_bucket.get(bucket_start, 0)
      provider_labels = cls._normalize_provider_provenance_export_strings(
        provider
        for record in bucket_records
        for provider in record.provider_labels
      )
      vendor_fields = cls._normalize_provider_provenance_export_strings(
        field
        for record in bucket_records
        for field in record.vendor_fields
      )
      focus_count = len({
        record.focus_key
        for record in bucket_records
        if isinstance(record.focus_key, str) and record.focus_key
      })
      provider_label_count = len(provider_labels)
      drift_intensity = round(
        provider_provenance_count / export_count,
        2,
      ) if export_count else 0.0
      bucket_key = bucket_start.date().isoformat()
      bucket_label = bucket_start.strftime("%b %d")
      provider_drift_series.append(
        {
          "bucket_key": bucket_key,
          "bucket_label": bucket_label,
          "started_at": bucket_start.isoformat(),
          "ended_at": bucket_end.isoformat(),
          "export_count": export_count,
          "result_count": result_count,
          "provider_provenance_count": provider_provenance_count,
          "focus_count": focus_count,
          "provider_label_count": provider_label_count,
          "provider_labels": list(provider_labels),
          "vendor_fields": list(vendor_fields),
          "drift_intensity": drift_intensity,
        }
      )

      cumulative_exports += export_count
      cumulative_results += result_count
      cumulative_provider_provenance += provider_provenance_count
      cumulative_downloads += download_count
      export_burn_up_series.append(
        {
          "bucket_key": bucket_key,
          "bucket_label": bucket_label,
          "started_at": bucket_start.isoformat(),
          "ended_at": bucket_end.isoformat(),
          "export_count": export_count,
          "result_count": result_count,
          "provider_provenance_count": provider_provenance_count,
          "download_count": download_count,
          "cumulative_export_count": cumulative_exports,
          "cumulative_result_count": cumulative_results,
          "cumulative_provider_provenance_count": cumulative_provider_provenance,
          "cumulative_download_count": cumulative_downloads,
        }
      )

    provider_drift_peak = max(
      provider_drift_series,
      key=lambda item: (
        int(item["provider_provenance_count"]),
        int(item["export_count"]),
        item["bucket_key"],
      ),
      default=None,
    )
    burn_up_latest = export_burn_up_series[-1] if export_burn_up_series else None

    return {
      "bucket_size": "day",
      "window_days": normalized_window_days,
      "window_started_at": window_started_at.isoformat(),
      "window_ended_at": window_ended_at.isoformat(),
      "provider_drift": {
        "series": provider_drift_series,
        "summary": {
          "peak_bucket_key": (
            provider_drift_peak["bucket_key"]
            if provider_drift_peak is not None
            else None
          ),
          "peak_bucket_label": (
            provider_drift_peak["bucket_label"]
            if provider_drift_peak is not None
            else None
          ),
          "peak_export_count": (
            int(provider_drift_peak["export_count"])
            if provider_drift_peak is not None
            else 0
          ),
          "peak_provider_provenance_count": (
            int(provider_drift_peak["provider_provenance_count"])
            if provider_drift_peak is not None
            else 0
          ),
          "latest_bucket_key": (
            provider_drift_series[-1]["bucket_key"]
            if provider_drift_series
            else None
          ),
          "latest_bucket_label": (
            provider_drift_series[-1]["bucket_label"]
            if provider_drift_series
            else None
          ),
          "latest_export_count": (
            int(provider_drift_series[-1]["export_count"])
            if provider_drift_series
            else 0
          ),
          "latest_provider_provenance_count": (
            int(provider_drift_series[-1]["provider_provenance_count"])
            if provider_drift_series
            else 0
          ),
        },
      },
      "export_burn_up": {
        "series": export_burn_up_series,
        "summary": {
          "latest_bucket_key": (
            burn_up_latest["bucket_key"]
            if burn_up_latest is not None
            else None
          ),
          "latest_bucket_label": (
            burn_up_latest["bucket_label"]
            if burn_up_latest is not None
            else None
          ),
          "cumulative_export_count": (
            int(burn_up_latest["cumulative_export_count"])
            if burn_up_latest is not None
            else 0
          ),
          "cumulative_result_count": (
            int(burn_up_latest["cumulative_result_count"])
            if burn_up_latest is not None
            else 0
          ),
          "cumulative_provider_provenance_count": (
            int(burn_up_latest["cumulative_provider_provenance_count"])
            if burn_up_latest is not None
            else 0
          ),
          "cumulative_download_count": (
            int(burn_up_latest["cumulative_download_count"])
            if burn_up_latest is not None
            else 0
          ),
        },
      },
    }

  @staticmethod
  def _normalize_provider_provenance_workspace_name(
    value: str | None,
    *,
    field_name: str,
  ) -> str:
    normalized_value = value.strip() if isinstance(value, str) else ""
    if not normalized_value:
      raise ValueError(f"Provider provenance {field_name} is required.")
    return normalized_value

  @classmethod
  def _normalize_provider_provenance_analytics_query_payload(
    cls,
    payload: dict[str, Any] | None,
  ) -> dict[str, Any]:
    query = deepcopy(payload) if isinstance(payload, dict) else {}
    focus_scope = query.get("focus_scope")
    normalized_focus_scope = (
      focus_scope.strip()
      if isinstance(focus_scope, str) and focus_scope.strip() in {"current_focus", "all_focuses"}
      else "all_focuses"
    )
    normalized_query = {
      "focus_scope": normalized_focus_scope,
      "focus_key": (
        query.get("focus_key").strip()
        if isinstance(query.get("focus_key"), str) and query.get("focus_key").strip()
        else None
      ),
      "symbol": (
        query.get("symbol").strip()
        if isinstance(query.get("symbol"), str) and query.get("symbol").strip()
        else None
      ),
      "timeframe": (
        query.get("timeframe").strip()
        if isinstance(query.get("timeframe"), str) and query.get("timeframe").strip()
        else None
      ),
      "provider_label": (
        query.get("provider_label").strip()
        if isinstance(query.get("provider_label"), str) and query.get("provider_label").strip()
        else None
      ),
      "vendor_field": (
        query.get("vendor_field").strip()
        if isinstance(query.get("vendor_field"), str) and query.get("vendor_field").strip()
        else None
      ),
      "market_data_provider": (
        query.get("market_data_provider").strip()
        if isinstance(query.get("market_data_provider"), str) and query.get("market_data_provider").strip()
        else None
      ),
      "venue": (
        query.get("venue").strip()
        if isinstance(query.get("venue"), str) and query.get("venue").strip()
        else None
      ),
      "requested_by_tab_id": (
        query.get("requested_by_tab_id").strip()
        if isinstance(query.get("requested_by_tab_id"), str) and query.get("requested_by_tab_id").strip()
        else None
      ),
      "status": (
        query.get("status").strip()
        if isinstance(query.get("status"), str) and query.get("status").strip()
        else None
      ),
      "scheduler_alert_category": cls._normalize_provider_provenance_scheduler_alert_history_category(
        query.get("scheduler_alert_category")
      ),
      "scheduler_alert_status": cls._normalize_provider_provenance_scheduler_alert_history_status(
        query.get("scheduler_alert_status")
      ),
      "scheduler_alert_narrative_facet": (
        cls._normalize_provider_provenance_scheduler_alert_history_narrative_facet(
          query.get("scheduler_alert_narrative_facet")
        )
        or "all_occurrences"
      ),
      "search": (
        query.get("search").strip()
        if isinstance(query.get("search"), str) and query.get("search").strip()
        else None
      ),
      "result_limit": (
        max(1, min(int(query.get("result_limit")), 50))
        if isinstance(query.get("result_limit"), Number)
        else 12
      ),
      "window_days": (
        max(3, min(int(query.get("window_days")), 90))
        if isinstance(query.get("window_days"), Number)
        else 14
      ),
    }
    if normalized_focus_scope == "current_focus" and (
      normalized_query["focus_key"] is None
      or normalized_query["symbol"] is None
      or normalized_query["timeframe"] is None
    ):
      raise ValueError(
        "Current-focus provider provenance workspace entries require focus_key, symbol, and timeframe."
      )
    return normalized_query

  @staticmethod
  def _normalize_provider_provenance_dashboard_layout_payload(
    payload: dict[str, Any] | None,
  ) -> dict[str, Any]:
    layout = deepcopy(payload) if isinstance(payload, dict) else {}
    highlight_panel = layout.get("highlight_panel")
    normalized_highlight_panel = (
      highlight_panel.strip()
      if isinstance(highlight_panel, str)
      and highlight_panel.strip() in {
        "overview",
        "drift",
        "burn_up",
        "rollups",
        "recent_exports",
        "scheduler_alerts",
      }
      else "overview"
    )
    normalized_layout = {
      "highlight_panel": normalized_highlight_panel,
      "show_rollups": bool(layout.get("show_rollups", True)),
      "show_time_series": bool(layout.get("show_time_series", True)),
      "show_recent_exports": bool(layout.get("show_recent_exports", True)),
    }
    normalized_governance_queue_view = (
      ProviderProvenanceCompatibilityMixin._normalize_provider_provenance_scheduler_narrative_governance_queue_view_payload(
        layout.get("governance_queue_view")
      )
    )
    if normalized_governance_queue_view is not None:
      normalized_layout["governance_queue_view"] = normalized_governance_queue_view
    return normalized_layout

  @classmethod
  def _normalize_provider_provenance_scheduler_narrative_registry_layout_payload(
    cls,
    payload: dict[str, Any] | None,
  ) -> dict[str, Any]:
    normalized_layout = cls._normalize_provider_provenance_dashboard_layout_payload(payload)
    return {
      **normalized_layout,
      "highlight_panel": "scheduler_alerts",
    }

  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_record_status(
    value: str | None,
  ) -> str:
    normalized_value = value.strip() if isinstance(value, str) else ""
    return "deleted" if normalized_value == "deleted" else "active"

  def _build_provider_provenance_scheduler_stitched_report_view_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerStitchedReportViewRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRevisionRecord:
    revision_count = sum(
      1
      for revision in self._list_provider_provenance_scheduler_stitched_report_view_revision_records()
      if revision.view_id == record.view_id
    )
    return ProviderProvenanceSchedulerStitchedReportViewRevisionRecord(
      revision_id=f"{record.view_id}:r{revision_count + 1:04d}",
      view_id=record.view_id,
      action=action,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      name=record.name,
      description=record.description,
      query=deepcopy(record.query),
      occurrence_limit=int(record.occurrence_limit),
      history_limit=int(record.history_limit),
      drilldown_history_limit=int(record.drilldown_history_limit),
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
      recorded_at=recorded_at,
      source_revision_id=source_revision_id,
      recorded_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      recorded_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )

  def _find_latest_active_provider_provenance_scheduler_stitched_report_view_revision(
    self,
    view_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRevisionRecord | None:
    for revision in self._list_provider_provenance_scheduler_stitched_report_view_revision_records():
      if revision.view_id != view_id:
        continue
      if self._normalize_provider_provenance_scheduler_narrative_record_status(revision.status) != "active":
        continue
      return revision
    return None

  def _build_provider_provenance_scheduler_stitched_report_view_bulk_query(
    self,
    current_query: dict[str, Any],
    query_patch: dict[str, Any] | None,
  ) -> dict[str, Any]:
    candidate = deepcopy(current_query)
    if isinstance(query_patch, dict):
      for key, value in query_patch.items():
        candidate[key] = deepcopy(value)
    return self._normalize_provider_provenance_analytics_query_payload(candidate)

  @staticmethod
  def _build_provider_provenance_scheduler_stitched_report_view_audit_detail(
    *,
    record: ProviderProvenanceSchedulerStitchedReportViewRecord,
    action: str,
  ) -> str:
    lens = f"{record.occurrence_limit} occurrences / {record.history_limit} history / {record.drilldown_history_limit} drill-down"
    if action == "created":
      return f"Created stitched report view {record.name} with {lens}."
    if action == "updated":
      return f"Updated stitched report view {record.name} with {lens}."
    if action == "deleted":
      return f"Deleted stitched report view {record.name}."
    if action == "restored":
      return f"Restored stitched report view {record.name}."
    return f"Recorded stitched report view action {action} for {record.name}."

  def _record_provider_provenance_scheduler_stitched_report_view_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerStitchedReportViewRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRecord:
    revision = self._save_provider_provenance_scheduler_stitched_report_view_revision_record(
      self._build_provider_provenance_scheduler_stitched_report_view_revision(
        record=record,
        action=action,
        reason=reason,
        recorded_at=recorded_at,
        source_revision_id=source_revision_id,
        actor_tab_id=actor_tab_id,
        actor_tab_label=actor_tab_label,
      )
    )
    updated = self._save_provider_provenance_scheduler_stitched_report_view_record(
      replace(
        record,
        current_revision_id=revision.revision_id,
        revision_count=int(record.revision_count or 0) + 1,
      )
    )
    normalized_query = self._normalize_provider_provenance_analytics_query_payload(updated.query)
    self._save_provider_provenance_scheduler_stitched_report_view_audit_record(
      ProviderProvenanceSchedulerStitchedReportViewAuditRecord(
        audit_id=f"{updated.view_id}:{revision.revision_id}:{action}",
        view_id=updated.view_id,
        action=action,
        recorded_at=recorded_at,
        reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
        detail=self._build_provider_provenance_scheduler_stitched_report_view_audit_detail(
          record=updated,
          action=action,
        ),
        revision_id=revision.revision_id,
        source_revision_id=source_revision_id,
        name=updated.name,
        status=updated.status,
        occurrence_limit=int(updated.occurrence_limit),
        history_limit=int(updated.history_limit),
        drilldown_history_limit=int(updated.drilldown_history_limit),
        filter_summary=self._build_provider_provenance_analytics_filter_summary(normalized_query),
        actor_tab_id=revision.recorded_by_tab_id,
        actor_tab_label=revision.recorded_by_tab_label,
      )
    )
    return updated

  def _normalize_provider_provenance_scheduler_stitched_report_governance_registry_queue_view(
    self,
    queue_view: dict[str, Any] | None,
  ) -> dict[str, Any]:
    normalized = self._normalize_provider_provenance_scheduler_narrative_governance_queue_view_payload(
      queue_view
    )
    if not isinstance(normalized, dict):
      return {}
    normalized["item_type"] = "stitched_report_view"
    return normalized

  def _build_provider_provenance_scheduler_stitched_report_governance_registry_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord:
    revision_count = sum(
      1
      for revision in self._list_provider_provenance_scheduler_stitched_report_governance_registry_revision_records()
      if revision.registry_id == record.registry_id
    )
    return ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord(
      revision_id=f"{record.registry_id}:r{revision_count + 1:04d}",
      registry_id=record.registry_id,
      action=action,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      name=record.name,
      description=record.description,
      queue_view=deepcopy(record.queue_view),
      default_policy_template_id=record.default_policy_template_id,
      default_policy_template_name=record.default_policy_template_name,
      default_policy_catalog_id=record.default_policy_catalog_id,
      default_policy_catalog_name=record.default_policy_catalog_name,
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
      recorded_at=recorded_at,
      source_revision_id=source_revision_id,
      recorded_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      recorded_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )

  @staticmethod
  def _build_provider_provenance_scheduler_stitched_report_governance_registry_audit_detail(
    *,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord,
    action: str,
  ) -> str:
    queue_view = record.queue_view if isinstance(record.queue_view, dict) else {}
    queue_tokens: list[str] = []
    if isinstance(queue_view.get("queue_state"), str) and queue_view["queue_state"]:
      queue_tokens.append(f"queue {queue_view['queue_state']}")
    if isinstance(queue_view.get("approval_lane"), str) and queue_view["approval_lane"]:
      queue_tokens.append(f"lane {queue_view['approval_lane']}")
    if isinstance(queue_view.get("approval_priority"), str) and queue_view["approval_priority"]:
      queue_tokens.append(f"priority {queue_view['approval_priority']}")
    if isinstance(queue_view.get("search"), str) and queue_view["search"]:
      queue_tokens.append(f"search \"{queue_view['search']}\"")
    if isinstance(queue_view.get("sort"), str) and queue_view["sort"]:
      queue_tokens.append(f"sort {queue_view['sort']}")
    queue_summary = " / ".join(queue_tokens) if queue_tokens else "default stitched-report queue"
    policy_tokens = [
      value
      for value in (
        record.default_policy_template_name or record.default_policy_template_id,
        record.default_policy_catalog_name or record.default_policy_catalog_id,
      )
      if isinstance(value, str) and value
    ]
    policy_summary = " / ".join(policy_tokens) if policy_tokens else "no default policy bundle"
    if action == "created":
      return f"Created stitched governance registry {record.name} on {queue_summary}. {policy_summary}."
    if action == "updated":
      return f"Updated stitched governance registry {record.name} on {queue_summary}. {policy_summary}."
    if action == "deleted":
      return f"Deleted stitched governance registry {record.name}."
    if action == "restored":
      return f"Restored stitched governance registry {record.name} on {queue_summary}. {policy_summary}."
    return f"Recorded stitched governance registry action {action} for {record.name}. {queue_summary}."

  def _record_provider_provenance_scheduler_stitched_report_governance_registry_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord:
    revision = self._save_provider_provenance_scheduler_stitched_report_governance_registry_revision_record(
      self._build_provider_provenance_scheduler_stitched_report_governance_registry_revision(
        record=record,
        action=action,
        reason=reason,
        recorded_at=recorded_at,
        source_revision_id=source_revision_id,
        actor_tab_id=actor_tab_id,
        actor_tab_label=actor_tab_label,
      )
    )
    updated = self._save_provider_provenance_scheduler_stitched_report_governance_registry_record(
      replace(
        record,
        current_revision_id=revision.revision_id,
        revision_count=int(record.revision_count or 0) + 1,
      )
    )
    normalized_queue_view = self._normalize_provider_provenance_scheduler_stitched_report_governance_registry_queue_view(
      updated.queue_view
    )
    self._save_provider_provenance_scheduler_stitched_report_governance_registry_audit_record(
      ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord(
        audit_id=f"{updated.registry_id}:{revision.revision_id}:{action}",
        registry_id=updated.registry_id,
        action=action,
        recorded_at=recorded_at,
        reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
        detail=self._build_provider_provenance_scheduler_stitched_report_governance_registry_audit_detail(
          record=replace(updated, queue_view=normalized_queue_view),
          action=action,
        ),
        revision_id=revision.revision_id,
        source_revision_id=source_revision_id,
        name=updated.name,
        description=updated.description,
        queue_view=deepcopy(normalized_queue_view) if normalized_queue_view is not None else {},
        default_policy_template_id=updated.default_policy_template_id,
        default_policy_template_name=updated.default_policy_template_name,
        default_policy_catalog_id=updated.default_policy_catalog_id,
        default_policy_catalog_name=updated.default_policy_catalog_name,
        status=updated.status,
        actor_tab_id=revision.recorded_by_tab_id,
        actor_tab_label=revision.recorded_by_tab_label,
      )
    )
    return updated

  def _find_latest_active_provider_provenance_scheduler_stitched_report_governance_registry_revision(
    self,
    registry_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord | None:
    for revision in self._list_provider_provenance_scheduler_stitched_report_governance_registry_revision_records():
      if revision.registry_id != registry_id:
        continue
      if self._normalize_provider_provenance_scheduler_narrative_record_status(revision.status) != "active":
        continue
      return revision
    return None

  def _build_provider_provenance_scheduler_narrative_template_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeTemplateRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord:
    revision_count = sum(
      1
      for revision in self._list_provider_provenance_scheduler_narrative_template_revision_records()
      if revision.template_id == record.template_id
    )
    return ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord(
      revision_id=f"{record.template_id}:r{revision_count + 1:04d}",
      template_id=record.template_id,
      action=action,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      name=record.name,
      description=record.description,
      query=deepcopy(record.query),
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
      recorded_at=recorded_at,
      source_revision_id=source_revision_id,
      recorded_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      recorded_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )

  def _record_provider_provenance_scheduler_narrative_template_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeTemplateRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRecord:
    revision = self._save_provider_provenance_scheduler_narrative_template_revision_record(
      self._build_provider_provenance_scheduler_narrative_template_revision(
        record=record,
        action=action,
        reason=reason,
        recorded_at=recorded_at,
        source_revision_id=source_revision_id,
        actor_tab_id=actor_tab_id,
        actor_tab_label=actor_tab_label,
      )
    )
    return self._save_provider_provenance_scheduler_narrative_template_record(
      replace(
        record,
        current_revision_id=revision.revision_id,
        revision_count=int(record.revision_count or 0) + 1,
      )
    )

  def _build_provider_provenance_scheduler_narrative_registry_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeRegistryRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord:
    revision_count = sum(
      1
      for revision in self._list_provider_provenance_scheduler_narrative_registry_revision_records()
      if revision.registry_id == record.registry_id
    )
    return ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord(
      revision_id=f"{record.registry_id}:r{revision_count + 1:04d}",
      registry_id=record.registry_id,
      action=action,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      name=record.name,
      description=record.description,
      query=deepcopy(record.query),
      layout=deepcopy(record.layout),
      template_id=record.template_id,
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
      recorded_at=recorded_at,
      source_revision_id=source_revision_id,
      recorded_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      recorded_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )

  def _record_provider_provenance_scheduler_narrative_registry_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeRegistryRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRecord:
    revision = self._save_provider_provenance_scheduler_narrative_registry_revision_record(
      self._build_provider_provenance_scheduler_narrative_registry_revision(
        record=record,
        action=action,
        reason=reason,
        recorded_at=recorded_at,
        source_revision_id=source_revision_id,
        actor_tab_id=actor_tab_id,
        actor_tab_label=actor_tab_label,
      )
    )
    return self._save_provider_provenance_scheduler_narrative_registry_record(
      replace(
        record,
        current_revision_id=revision.revision_id,
        revision_count=int(record.revision_count or 0) + 1,
      )
    )

  def _build_provider_provenance_scheduler_narrative_governance_policy_template_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord:
    revision_count = sum(
      1
      for revision in self._list_provider_provenance_scheduler_narrative_governance_policy_template_revision_records()
      if revision.policy_template_id == record.policy_template_id
    )
    return ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord(
      revision_id=f"{record.policy_template_id}:r{revision_count + 1:04d}",
      policy_template_id=record.policy_template_id,
      action=action,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      name=record.name,
      description=record.description,
      item_type_scope=record.item_type_scope,
      action_scope=record.action_scope,
      approval_lane=record.approval_lane,
      approval_priority=record.approval_priority,
      guidance=record.guidance,
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
      recorded_at=recorded_at,
      source_revision_id=source_revision_id,
      recorded_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      recorded_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )

  @staticmethod
  def _build_provider_provenance_scheduler_narrative_governance_policy_template_audit_detail(
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
    action: str,
  ) -> str:
    scope = f"{record.item_type_scope}/{record.action_scope}"
    lane = f"{record.approval_lane}/{record.approval_priority}"
    if action == "created":
      return f"Created governance policy template {record.name} for {scope} on {lane}."
    if action == "updated":
      return f"Updated governance policy template {record.name} for {scope} on {lane}."
    if action == "deleted":
      return f"Deleted governance policy template {record.name}."
    if action == "restored":
      return f"Restored governance policy template {record.name}."
    return f"Recorded governance policy template action {action} for {record.name}."

  def _record_provider_provenance_scheduler_narrative_governance_policy_template_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    revision = self._save_provider_provenance_scheduler_narrative_governance_policy_template_revision_record(
      self._build_provider_provenance_scheduler_narrative_governance_policy_template_revision(
        record=record,
        action=action,
        reason=reason,
        recorded_at=recorded_at,
        source_revision_id=source_revision_id,
        actor_tab_id=actor_tab_id,
        actor_tab_label=actor_tab_label,
      )
    )
    updated = self._save_provider_provenance_scheduler_narrative_governance_policy_template_record(
      replace(
        record,
        current_revision_id=revision.revision_id,
        revision_count=int(record.revision_count or 0) + 1,
      )
    )
    self._save_provider_provenance_scheduler_narrative_governance_policy_template_audit_record(
      ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord(
        audit_id=f"{updated.policy_template_id}:{revision.revision_id}:{action}",
        policy_template_id=updated.policy_template_id,
        action=action,
        recorded_at=recorded_at,
        reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
        detail=self._build_provider_provenance_scheduler_narrative_governance_policy_template_audit_detail(
          record=updated,
          action=action,
        ),
        revision_id=revision.revision_id,
        source_revision_id=source_revision_id,
        name=updated.name,
        status=updated.status,
        item_type_scope=updated.item_type_scope,
        action_scope=updated.action_scope,
        approval_lane=updated.approval_lane,
        approval_priority=updated.approval_priority,
        guidance=updated.guidance,
        actor_tab_id=revision.recorded_by_tab_id,
        actor_tab_label=revision.recorded_by_tab_label,
      )
    )
    return updated

  def _build_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord:
    record = self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(record)
    revision_count = sum(
      1
      for revision in self._list_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_records()
      if revision.catalog_id == record.catalog_id
    )
    return ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord(
      revision_id=f"{record.catalog_id}:r{revision_count + 1:04d}",
      catalog_id=record.catalog_id,
      action=action,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      name=record.name,
      description=record.description,
      policy_template_ids=tuple(record.policy_template_ids),
      policy_template_names=tuple(record.policy_template_names),
      default_policy_template_id=record.default_policy_template_id,
      default_policy_template_name=record.default_policy_template_name,
      item_type_scope=record.item_type_scope,
      action_scope=record.action_scope,
      approval_lane=record.approval_lane,
      approval_priority=record.approval_priority,
      guidance=record.guidance,
      hierarchy_steps=tuple(record.hierarchy_steps),
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
      recorded_at=recorded_at,
      source_revision_id=source_revision_id,
      recorded_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      recorded_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )

  @staticmethod
  def _build_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_detail(
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
    action: str,
  ) -> str:
    template_summary = ", ".join(record.policy_template_names) if record.policy_template_names else "no templates"
    default_summary = record.default_policy_template_name or "no default"
    lane = f"{record.approval_lane}/{record.approval_priority}"
    hierarchy_summary = ProviderProvenanceCompatibilityMixin._summarize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
      record.hierarchy_steps
    )
    if action == "created":
      return (
        f"Created governance policy catalog {record.name} with default {default_summary} and linked templates "
        f"{template_summary} on {lane}. {hierarchy_summary}"
      )
    if action == "updated":
      return (
        f"Updated governance policy catalog {record.name}; default {default_summary}, linked templates "
        f"{template_summary}. {hierarchy_summary}"
      )
    if action == "hierarchy_captured":
      return f"Captured reusable governance hierarchy for policy catalog {record.name}. {hierarchy_summary}"
    if action == "staged":
      return f"Staged reusable governance hierarchy for policy catalog {record.name}. {hierarchy_summary}"
    if action == "hierarchy_step_updated":
      return f"Updated one hierarchy step on policy catalog {record.name}. {hierarchy_summary}"
    if action == "hierarchy_step_restored":
      return f"Restored one hierarchy step from revision history on policy catalog {record.name}. {hierarchy_summary}"
    if action == "hierarchy_steps_bulk_updated":
      return f"Applied bulk hierarchy step updates on policy catalog {record.name}. {hierarchy_summary}"
    if action == "hierarchy_steps_bulk_deleted":
      return f"Deleted one or more hierarchy steps from policy catalog {record.name}. {hierarchy_summary}"
    if action == "deleted":
      return f"Deleted governance policy catalog {record.name}."
    if action == "restored":
      return f"Restored governance policy catalog {record.name}."
    return f"Recorded governance policy catalog action {action} for {record.name}."

  def _record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    record = self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(record)
    revision = self._save_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
      self._build_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
        record=record,
        action=action,
        reason=reason,
        recorded_at=recorded_at,
        source_revision_id=source_revision_id,
        actor_tab_id=actor_tab_id,
        actor_tab_label=actor_tab_label,
      )
    )
    updated = self._save_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
      replace(
        record,
        current_revision_id=revision.revision_id,
        revision_count=int(record.revision_count or 0) + 1,
      )
    )
    self._save_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record(
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord(
        audit_id=f"{updated.catalog_id}:{revision.revision_id}:{action}",
        catalog_id=updated.catalog_id,
        action=action,
        recorded_at=recorded_at,
        reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
        detail=self._build_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_detail(
          record=updated,
          action=action,
        ),
        revision_id=revision.revision_id,
        source_revision_id=source_revision_id,
        name=updated.name,
        status=updated.status,
        default_policy_template_id=updated.default_policy_template_id,
        default_policy_template_name=updated.default_policy_template_name,
        policy_template_ids=tuple(updated.policy_template_ids),
        policy_template_names=tuple(updated.policy_template_names),
        item_type_scope=updated.item_type_scope,
        action_scope=updated.action_scope,
        approval_lane=updated.approval_lane,
        approval_priority=updated.approval_priority,
        guidance=updated.guidance,
        hierarchy_steps=tuple(updated.hierarchy_steps),
        actor_tab_id=revision.recorded_by_tab_id,
        actor_tab_label=revision.recorded_by_tab_label,
      )
    )
    return updated

  def _build_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord:
    revision_count = sum(
      1
      for revision in self._list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_records()
      if revision.hierarchy_step_template_id == record.hierarchy_step_template_id
    )
    return ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord(
      revision_id=f"{record.hierarchy_step_template_id}:r{revision_count + 1:04d}",
      hierarchy_step_template_id=record.hierarchy_step_template_id,
      action=action,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      name=record.name,
      description=record.description,
      item_type=record.item_type,
      step=record.step,
      origin_catalog_id=record.origin_catalog_id,
      origin_catalog_name=record.origin_catalog_name,
      origin_step_id=record.origin_step_id,
      governance_policy_template_id=record.governance_policy_template_id,
      governance_policy_template_name=record.governance_policy_template_name,
      governance_policy_catalog_id=record.governance_policy_catalog_id,
      governance_policy_catalog_name=record.governance_policy_catalog_name,
      governance_approval_lane=record.governance_approval_lane,
      governance_approval_priority=record.governance_approval_priority,
      governance_policy_guidance=record.governance_policy_guidance,
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
      recorded_at=recorded_at,
      source_revision_id=source_revision_id,
      recorded_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      recorded_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )

  @staticmethod
  def _build_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_detail(
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord,
    action: str,
  ) -> str:
    summary = ProviderProvenanceCompatibilityMixin.format_provider_provenance_scheduler_narrative_governance_hierarchy_step_summary(
      record.step
    )
    origin = record.origin_catalog_name or "ad hoc source"
    policy = (
      record.governance_policy_template_name
      or record.governance_policy_catalog_name
      or f"{record.governance_approval_lane}/{record.governance_approval_priority}"
    )
    if action == "created":
      return f"Created hierarchy step template {record.name} from {origin} on {policy}. {summary}"
    if action == "updated":
      return f"Updated hierarchy step template {record.name} on {policy}. {summary}"
    if action == "deleted":
      return f"Deleted hierarchy step template {record.name}."
    if action == "restored":
      return f"Restored hierarchy step template {record.name} on {policy}. {summary}"
    if action == "staged":
      return f"Staged hierarchy step template {record.name} into the approval queue on {policy}. {summary}"
    return f"Recorded hierarchy step template action {action} for {record.name}. {summary}"

  def _record_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
    revision = self._save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_record(
      self._build_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
        record=record,
        action=action,
        reason=reason,
        recorded_at=recorded_at,
        source_revision_id=source_revision_id,
        actor_tab_id=actor_tab_id,
        actor_tab_label=actor_tab_label,
      )
    )
    updated = self._save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record(
      replace(
        record,
        current_revision_id=revision.revision_id,
        revision_count=int(record.revision_count or 0) + 1,
      )
    )
    self._save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_record(
      ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord(
        audit_id=f"{updated.hierarchy_step_template_id}:{revision.revision_id}:{action}",
        hierarchy_step_template_id=updated.hierarchy_step_template_id,
        action=action,
        recorded_at=recorded_at,
        reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
        detail=self._build_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_detail(
          record=updated,
          action=action,
        ),
        revision_id=revision.revision_id,
        source_revision_id=source_revision_id,
        name=updated.name,
        description=updated.description,
        item_type=updated.item_type,
        step=updated.step,
        origin_catalog_id=updated.origin_catalog_id,
        origin_catalog_name=updated.origin_catalog_name,
        origin_step_id=updated.origin_step_id,
        governance_policy_template_id=updated.governance_policy_template_id,
        governance_policy_template_name=updated.governance_policy_template_name,
        governance_policy_catalog_id=updated.governance_policy_catalog_id,
        governance_policy_catalog_name=updated.governance_policy_catalog_name,
        governance_approval_lane=updated.governance_approval_lane,
        governance_approval_priority=updated.governance_approval_priority,
        governance_policy_guidance=updated.governance_policy_guidance,
        status=updated.status,
        actor_tab_id=revision.recorded_by_tab_id,
        actor_tab_label=revision.recorded_by_tab_label,
      )
    )
    return updated

  @staticmethod
  def _normalize_provider_provenance_scheduled_report_cadence(
    value: str | None,
  ) -> str:
    normalized_value = value.strip() if isinstance(value, str) else ""
    if not normalized_value:
      return "daily"
    if normalized_value not in {"daily", "weekly"}:
      raise ValueError("Provider provenance scheduled report cadence must be daily or weekly.")
    return normalized_value

  @staticmethod
  def _normalize_provider_provenance_scheduled_report_status(
    value: str | None,
  ) -> str:
    normalized_value = value.strip() if isinstance(value, str) else ""
    if not normalized_value:
      return "scheduled"
    if normalized_value not in {"scheduled", "paused"}:
      raise ValueError("Provider provenance scheduled report status must be scheduled or paused.")
    return normalized_value

  @classmethod
  def _matches_provider_provenance_workspace_search(
    cls,
    *,
    values: Iterable[Any],
    search: str | None,
  ) -> bool:
    if not isinstance(search, str) or not search.strip():
      return True
    needle = search.strip().lower()
    return any(
      needle in value.strip().lower()
      for value in values
      if isinstance(value, str) and value.strip()
    )

  @classmethod
  def _build_provider_provenance_workspace_focus_payload(
    cls,
    query: dict[str, Any],
  ) -> dict[str, Any]:
    focus_key = query.get("focus_key") if isinstance(query.get("focus_key"), str) else None
    market_data_provider = query.get("market_data_provider") if isinstance(query.get("market_data_provider"), str) else None
    symbol = query.get("symbol") if isinstance(query.get("symbol"), str) else None
    timeframe = query.get("timeframe") if isinstance(query.get("timeframe"), str) else None
    instrument_id = None
    if focus_key and "|" in focus_key:
      instrument_id = focus_key.split("|", 1)[0]
    elif market_data_provider and symbol:
      instrument_id = f"{market_data_provider}:{symbol}"
    return {
      "provider": market_data_provider,
      "venue": query.get("venue") if isinstance(query.get("venue"), str) else None,
      "instrument_id": instrument_id,
      "symbol": symbol,
      "timeframe": timeframe,
    }

  @classmethod
  def _build_provider_provenance_analytics_filter_summary(
    cls,
    query: dict[str, Any],
  ) -> str:
    parts = [
      "current focus" if query.get("focus_scope") == "current_focus" else "all focuses",
      f"{int(query.get('window_days', 14))}d window",
      f"provider {query['provider_label']}" if isinstance(query.get("provider_label"), str) else None,
      f"vendor field {query['vendor_field']}" if isinstance(query.get("vendor_field"), str) else None,
      f"market data {query['market_data_provider']}" if isinstance(query.get("market_data_provider"), str) else None,
      f"requester {query['requested_by_tab_id']}" if isinstance(query.get("requested_by_tab_id"), str) else None,
      (
        f"scheduler category {query['scheduler_alert_category']}"
        if isinstance(query.get("scheduler_alert_category"), str)
        else None
      ),
      (
        f"scheduler status {query['scheduler_alert_status']}"
        if isinstance(query.get("scheduler_alert_status"), str)
        else None
      ),
      (
        "scheduler post-resolution recovery"
        if query.get("scheduler_alert_narrative_facet") == "post_resolution_recovery"
        else (
          "scheduler recurring occurrences"
          if query.get("scheduler_alert_narrative_facet") == "recurring_occurrences"
          else (
            "scheduler resolved narratives"
            if query.get("scheduler_alert_narrative_facet") == "resolved_narratives"
            else None
          )
        )
      ),
      f"search {query['search']}" if isinstance(query.get("search"), str) else None,
    ]
    return " / ".join(part for part in parts if isinstance(part, str) and part)

  @classmethod
  def _build_provider_provenance_analytics_report_payload(
    cls,
    *,
    report: ProviderProvenanceScheduledReportRecord,
    analytics: dict[str, Any],
    preset: ProviderProvenanceAnalyticsPresetRecord | None,
    view: ProviderProvenanceDashboardViewRecord | None,
    exported_at: datetime,
  ) -> dict[str, Any]:
    normalized_query = cls._normalize_provider_provenance_analytics_query_payload(report.query)
    focus_payload = cls._build_provider_provenance_workspace_focus_payload(normalized_query)
    focus_payload["provider_provenance_incident_count"] = (
      analytics.get("totals", {}).get("provider_provenance_count", 0)
      if isinstance(analytics.get("totals"), dict)
      else 0
    )
    return {
      "exported_at": exported_at.isoformat(),
      "export_scope": "provider_provenance_analytics_report",
      "export_filter": deepcopy(normalized_query),
      "export_filter_summary": cls._build_provider_provenance_analytics_filter_summary(normalized_query),
      "focus": focus_payload,
      "analytics": deepcopy(analytics),
      "preset": (
        {
          "preset_id": preset.preset_id,
          "name": preset.name,
          "description": preset.description,
        }
        if preset is not None
        else None
      ),
      "view": (
        {
          "view_id": view.view_id,
          "name": view.name,
          "description": view.description,
          "layout": deepcopy(view.layout),
        }
        if view is not None
        else None
      ),
      "report": {
        "report_id": report.report_id,
        "name": report.name,
        "description": report.description,
        "cadence": report.cadence,
        "status": report.status,
        "next_run_at": report.next_run_at.isoformat() if report.next_run_at is not None else None,
        "last_run_at": report.last_run_at.isoformat() if report.last_run_at is not None else None,
        "preset_id": report.preset_id,
        "view_id": report.view_id,
      },
    }

  def create_provider_provenance_analytics_preset(
    self,
    *,
    name: str,
    description: str = "",
    query: dict[str, Any] | None = None,
    created_by_tab_id: str | None = None,
    created_by_tab_label: str | None = None,
  ) -> ProviderProvenanceAnalyticsPresetRecord:
    now = self._clock()
    record = ProviderProvenanceAnalyticsPresetRecord(
      preset_id=uuid4().hex[:12],
      name=self._normalize_provider_provenance_workspace_name(name, field_name="preset name"),
      description=description.strip() if isinstance(description, str) else "",
      query=self._normalize_provider_provenance_analytics_query_payload(query),
      created_at=now,
      updated_at=now,
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
    return self._save_provider_provenance_analytics_preset_record(record)

  def list_provider_provenance_analytics_presets(
    self,
    *,
    created_by_tab_id: str | None = None,
    focus_scope: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceAnalyticsPresetRecord, ...]:
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
    filtered: list[ProviderProvenanceAnalyticsPresetRecord] = []
    for record in self._list_provider_provenance_analytics_preset_records():
      normalized_query = self._normalize_provider_provenance_analytics_query_payload(record.query)
      if normalized_creator is not None and record.created_by_tab_id != normalized_creator:
        continue
      if normalized_focus_scope is not None and normalized_query["focus_scope"] != normalized_focus_scope:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.preset_id,
          record.name,
          record.description,
          record.created_by_tab_id,
          record.created_by_tab_label,
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
        ),
        search=search,
      ):
        continue
      filtered.append(replace(record, query=normalized_query))
    return tuple(filtered[:normalized_limit])

  def get_provider_provenance_analytics_preset(
    self,
    preset_id: str,
  ) -> ProviderProvenanceAnalyticsPresetRecord:
    normalized_preset_id = preset_id.strip()
    if not normalized_preset_id:
      raise LookupError("Provider provenance analytics preset not found.")
    record = self._load_provider_provenance_analytics_preset_record(normalized_preset_id)
    if record is None:
      raise LookupError("Provider provenance analytics preset not found.")
    return replace(
      record,
      query=self._normalize_provider_provenance_analytics_query_payload(record.query),
    )

  def create_provider_provenance_dashboard_view(
    self,
    *,
    name: str,
    description: str = "",
    query: dict[str, Any] | None = None,
    layout: dict[str, Any] | None = None,
    preset_id: str | None = None,
    created_by_tab_id: str | None = None,
    created_by_tab_label: str | None = None,
  ) -> ProviderProvenanceDashboardViewRecord:
    now = self._clock()
    normalized_preset_id = (
      preset_id.strip()
      if isinstance(preset_id, str) and preset_id.strip()
      else None
    )
    preset_record = (
      self.get_provider_provenance_analytics_preset(normalized_preset_id)
      if normalized_preset_id is not None
      else None
    )
    resolved_query = (
      query
      if isinstance(query, dict) and query
      else preset_record.query if preset_record is not None else None
    )
    record = ProviderProvenanceDashboardViewRecord(
      view_id=uuid4().hex[:12],
      name=self._normalize_provider_provenance_workspace_name(name, field_name="dashboard view name"),
      description=description.strip() if isinstance(description, str) else "",
      query=self._normalize_provider_provenance_analytics_query_payload(resolved_query),
      layout=self._normalize_provider_provenance_dashboard_layout_payload(layout),
      preset_id=normalized_preset_id,
      created_at=now,
      updated_at=now,
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
    return self._save_provider_provenance_dashboard_view_record(record)

  def list_provider_provenance_dashboard_views(
    self,
    *,
    preset_id: str | None = None,
    created_by_tab_id: str | None = None,
    focus_scope: str | None = None,
    highlight_panel: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceDashboardViewRecord, ...]:
    normalized_preset_id = (
      preset_id.strip()
      if isinstance(preset_id, str) and preset_id.strip()
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
    normalized_highlight_panel = (
      highlight_panel.strip()
      if isinstance(highlight_panel, str)
      and highlight_panel.strip() in {
        "overview",
        "drift",
        "burn_up",
        "rollups",
        "recent_exports",
        "scheduler_alerts",
      }
      else None
    )
    normalized_limit = max(1, min(limit, 200))
    filtered: list[ProviderProvenanceDashboardViewRecord] = []
    for record in self._list_provider_provenance_dashboard_view_records():
      normalized_query = self._normalize_provider_provenance_analytics_query_payload(record.query)
      normalized_layout = self._normalize_provider_provenance_dashboard_layout_payload(record.layout)
      if normalized_preset_id is not None and record.preset_id != normalized_preset_id:
        continue
      if normalized_creator is not None and record.created_by_tab_id != normalized_creator:
        continue
      if normalized_focus_scope is not None and normalized_query["focus_scope"] != normalized_focus_scope:
        continue
      if normalized_highlight_panel is not None and normalized_layout["highlight_panel"] != normalized_highlight_panel:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.view_id,
          record.name,
          record.description,
          record.preset_id,
          record.created_by_tab_id,
          record.created_by_tab_label,
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
          (
            normalized_layout.get("governance_queue_view", {}).get("queue_state")
            if isinstance(normalized_layout.get("governance_queue_view"), dict)
            else None
          ),
          (
            normalized_layout.get("governance_queue_view", {}).get("approval_lane")
            if isinstance(normalized_layout.get("governance_queue_view"), dict)
            else None
          ),
          (
            normalized_layout.get("governance_queue_view", {}).get("approval_priority")
            if isinstance(normalized_layout.get("governance_queue_view"), dict)
            else None
          ),
          (
            normalized_layout.get("governance_queue_view", {}).get("policy_template_id")
            if isinstance(normalized_layout.get("governance_queue_view"), dict)
            else None
          ),
          (
            normalized_layout.get("governance_queue_view", {}).get("policy_catalog_id")
            if isinstance(normalized_layout.get("governance_queue_view"), dict)
            else None
          ),
          (
            normalized_layout.get("governance_queue_view", {}).get("source_hierarchy_step_template_id")
            if isinstance(normalized_layout.get("governance_queue_view"), dict)
            else None
          ),
          (
            normalized_layout.get("governance_queue_view", {}).get("source_hierarchy_step_template_name")
            if isinstance(normalized_layout.get("governance_queue_view"), dict)
            else None
          ),
          (
            normalized_layout.get("governance_queue_view", {}).get("search")
            if isinstance(normalized_layout.get("governance_queue_view"), dict)
            else None
          ),
          (
            normalized_layout.get("governance_queue_view", {}).get("sort")
            if isinstance(normalized_layout.get("governance_queue_view"), dict)
            else None
          ),
        ),
        search=search,
      ):
        continue
      filtered.append(
        replace(record, query=normalized_query, layout=normalized_layout)
      )
    return tuple(filtered[:normalized_limit])

  def get_provider_provenance_dashboard_view(
    self,
    view_id: str,
  ) -> ProviderProvenanceDashboardViewRecord:
    normalized_view_id = view_id.strip()
    if not normalized_view_id:
      raise LookupError("Provider provenance dashboard view not found.")
    record = self._load_provider_provenance_dashboard_view_record(normalized_view_id)
    if record is None:
      raise LookupError("Provider provenance dashboard view not found.")
    return replace(
      record,
      query=self._normalize_provider_provenance_analytics_query_payload(record.query),
      layout=self._normalize_provider_provenance_dashboard_layout_payload(record.layout),
    )

  @staticmethod
  def _normalize_provider_provenance_scheduler_stitched_report_view_limit(
    value: int | None,
    *,
    default: int,
    minimum: int,
    maximum: int,
    field_name: str,
  ) -> int:
    if value is None:
      return default
    if not isinstance(value, int):
      raise ValueError(f"{field_name} must be an integer.")
    return max(minimum, min(value, maximum))

  def create_provider_provenance_scheduler_stitched_report_view(
    self,
    *,
    name: str,
    description: str = "",
    query: dict[str, Any] | None = None,
    occurrence_limit: int = 8,
    history_limit: int = 12,
    drilldown_history_limit: int = 12,
    created_by_tab_id: str | None = None,
    created_by_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRecord:
    now = self._clock()
    record = ProviderProvenanceSchedulerStitchedReportViewRecord(
      view_id=uuid4().hex[:12],
      name=self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler stitched report view name",
      ),
      description=description.strip() if isinstance(description, str) else "",
      query=self._normalize_provider_provenance_analytics_query_payload(query),
      occurrence_limit=self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        occurrence_limit,
        default=8,
        minimum=1,
        maximum=50,
        field_name="scheduler stitched report occurrence_limit",
      ),
      history_limit=self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        history_limit,
        default=12,
        minimum=1,
        maximum=200,
        field_name="scheduler stitched report history_limit",
      ),
      drilldown_history_limit=self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        drilldown_history_limit,
        default=12,
        minimum=1,
        maximum=100,
        field_name="scheduler stitched report drilldown_history_limit",
      ),
      created_at=now,
      updated_at=now,
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
    return self._record_provider_provenance_scheduler_stitched_report_view_revision(
      record=record,
      action="created",
      reason="scheduler_stitched_report_view_created",
      recorded_at=now,
      actor_tab_id=record.created_by_tab_id,
      actor_tab_label=record.created_by_tab_label,
    )

  def update_provider_provenance_scheduler_stitched_report_view(
    self,
    view_id: str,
    *,
    name: str | None = None,
    description: str | None = None,
    query: dict[str, Any] | None = None,
    occurrence_limit: int | None = None,
    history_limit: int | None = None,
    drilldown_history_limit: int | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_stitched_report_view_updated",
  ) -> ProviderProvenanceSchedulerStitchedReportViewRecord:
    current = self.get_provider_provenance_scheduler_stitched_report_view(view_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler stitched report views must be restored from a revision before editing."
      )
    updated_name = (
      self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler stitched report view name",
      )
      if isinstance(name, str)
      else current.name
    )
    updated_description = (
      description.strip()
      if isinstance(description, str)
      else current.description
    )
    updated_query = (
      self._normalize_provider_provenance_analytics_query_payload(query)
      if isinstance(query, dict)
      else current.query
    )
    updated_occurrence_limit = (
      self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        occurrence_limit,
        default=8,
        minimum=1,
        maximum=50,
        field_name="scheduler stitched report occurrence_limit",
      )
      if isinstance(occurrence_limit, int)
      else current.occurrence_limit
    )
    updated_history_limit = (
      self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        history_limit,
        default=12,
        minimum=1,
        maximum=200,
        field_name="scheduler stitched report history_limit",
      )
      if isinstance(history_limit, int)
      else current.history_limit
    )
    updated_drilldown_history_limit = (
      self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        drilldown_history_limit,
        default=12,
        minimum=1,
        maximum=100,
        field_name="scheduler stitched report drilldown_history_limit",
      )
      if isinstance(drilldown_history_limit, int)
      else current.drilldown_history_limit
    )
    if (
      updated_name == current.name
      and updated_description == current.description
      and updated_query == current.query
      and updated_occurrence_limit == current.occurrence_limit
      and updated_history_limit == current.history_limit
      and updated_drilldown_history_limit == current.drilldown_history_limit
    ):
      return current
    updated = replace(
      current,
      name=updated_name,
      description=updated_description,
      query=updated_query,
      occurrence_limit=updated_occurrence_limit,
      history_limit=updated_history_limit,
      drilldown_history_limit=updated_drilldown_history_limit,
      updated_at=self._clock(),
    )
    return self._record_provider_provenance_scheduler_stitched_report_view_revision(
      record=updated,
      action="updated",
      reason=reason,
      recorded_at=updated.updated_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def delete_provider_provenance_scheduler_stitched_report_view(
    self,
    view_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_stitched_report_view_deleted",
  ) -> ProviderProvenanceSchedulerStitchedReportViewRecord:
    current = self.get_provider_provenance_scheduler_stitched_report_view(view_id)
    if current.status == "deleted":
      return current
    deleted_at = self._clock()
    deleted = replace(
      current,
      status="deleted",
      updated_at=deleted_at,
      deleted_at=deleted_at,
      deleted_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      deleted_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )
    return self._record_provider_provenance_scheduler_stitched_report_view_revision(
      record=deleted,
      action="deleted",
      reason=reason,
      recorded_at=deleted_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def list_provider_provenance_scheduler_stitched_report_views(
    self,
    *,
    created_by_tab_id: str | None = None,
    category: str | None = None,
    narrative_facet: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportViewRecord, ...]:
    normalized_creator = (
      created_by_tab_id.strip()
      if isinstance(created_by_tab_id, str) and created_by_tab_id.strip()
      else None
    )
    normalized_category = self._normalize_provider_provenance_scheduler_alert_history_category(category)
    normalized_narrative_facet = self._normalize_provider_provenance_scheduler_alert_history_narrative_facet(
      narrative_facet
    )
    normalized_limit = max(1, min(limit, 200))
    filtered: list[ProviderProvenanceSchedulerStitchedReportViewRecord] = []
    for record in self._list_provider_provenance_scheduler_stitched_report_view_records():
      normalized_query = self._normalize_provider_provenance_analytics_query_payload(record.query)
      if normalized_creator is not None and record.created_by_tab_id != normalized_creator:
        continue
      if (
        normalized_category is not None
        and normalized_query.get("scheduler_alert_category") != normalized_category
      ):
        continue
      if (
        normalized_narrative_facet is not None
        and normalized_query.get("scheduler_alert_narrative_facet") != normalized_narrative_facet
      ):
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.view_id,
          record.name,
          record.description,
          record.status,
          record.created_by_tab_id,
          record.created_by_tab_label,
          normalized_query.get("scheduler_alert_category"),
          normalized_query.get("scheduler_alert_status"),
          normalized_query.get("scheduler_alert_narrative_facet"),
        ),
        search=search,
      ):
        continue
      filtered.append(
        replace(
          record,
          status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
          query=normalized_query,
        )
      )
    return tuple(filtered[:normalized_limit])

  def get_provider_provenance_scheduler_stitched_report_view(
    self,
    view_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRecord:
    normalized_view_id = view_id.strip()
    if not normalized_view_id:
      raise LookupError("Provider provenance scheduler stitched report view not found.")
    record = self._load_provider_provenance_scheduler_stitched_report_view_record(normalized_view_id)
    if record is None:
      raise LookupError("Provider provenance scheduler stitched report view not found.")
    return replace(
      record,
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
      query=self._normalize_provider_provenance_analytics_query_payload(record.query),
      occurrence_limit=self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        record.occurrence_limit,
        default=8,
        minimum=1,
        maximum=50,
        field_name="scheduler stitched report occurrence_limit",
      ),
      history_limit=self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        record.history_limit,
        default=12,
        minimum=1,
        maximum=200,
        field_name="scheduler stitched report history_limit",
      ),
      drilldown_history_limit=self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        record.drilldown_history_limit,
        default=12,
        minimum=1,
        maximum=100,
        field_name="scheduler stitched report drilldown_history_limit",
      ),
    )

  def list_provider_provenance_scheduler_stitched_report_view_revisions(
    self,
    view_id: str,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportViewRevisionRecord, ...]:
    current = self.get_provider_provenance_scheduler_stitched_report_view(view_id)
    revisions = [
      replace(
        revision,
        status=self._normalize_provider_provenance_scheduler_narrative_record_status(revision.status),
        query=self._normalize_provider_provenance_analytics_query_payload(revision.query),
        occurrence_limit=self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
          revision.occurrence_limit,
          default=8,
          minimum=1,
          maximum=50,
          field_name="scheduler stitched report occurrence_limit",
        ),
        history_limit=self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
          revision.history_limit,
          default=12,
          minimum=1,
          maximum=200,
          field_name="scheduler stitched report history_limit",
        ),
        drilldown_history_limit=self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
          revision.drilldown_history_limit,
          default=12,
          minimum=1,
          maximum=100,
          field_name="scheduler stitched report drilldown_history_limit",
        ),
      )
      for revision in self._list_provider_provenance_scheduler_stitched_report_view_revision_records()
      if revision.view_id == current.view_id
    ]
    return tuple(revisions)

  def restore_provider_provenance_scheduler_stitched_report_view_revision(
    self,
    view_id: str,
    revision_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_stitched_report_view_revision_restored",
  ) -> ProviderProvenanceSchedulerStitchedReportViewRecord:
    current = self.get_provider_provenance_scheduler_stitched_report_view(view_id)
    revision = self._load_provider_provenance_scheduler_stitched_report_view_revision_record(
      revision_id.strip()
    )
    if revision is None or revision.view_id != current.view_id:
      raise LookupError("Provider provenance scheduler stitched report view revision not found.")
    restored_at = self._clock()
    restored = replace(
      current,
      name=revision.name,
      description=revision.description,
      query=self._normalize_provider_provenance_analytics_query_payload(revision.query),
      occurrence_limit=self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        revision.occurrence_limit,
        default=8,
        minimum=1,
        maximum=50,
        field_name="scheduler stitched report occurrence_limit",
      ),
      history_limit=self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        revision.history_limit,
        default=12,
        minimum=1,
        maximum=200,
        field_name="scheduler stitched report history_limit",
      ),
      drilldown_history_limit=self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        revision.drilldown_history_limit,
        default=12,
        minimum=1,
        maximum=100,
        field_name="scheduler stitched report drilldown_history_limit",
      ),
      status="active",
      updated_at=restored_at,
      deleted_at=None,
      deleted_by_tab_id=None,
      deleted_by_tab_label=None,
    )
    return self._record_provider_provenance_scheduler_stitched_report_view_revision(
      record=restored,
      action="restored",
      reason=reason,
      recorded_at=restored_at,
      source_revision_id=revision.revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def bulk_govern_provider_provenance_scheduler_stitched_report_views(
    self,
    view_ids: Iterable[str],
    *,
    action: str,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    query_patch: dict[str, Any] | None = None,
    occurrence_limit: int | None = None,
    history_limit: int | None = None,
    drilldown_history_limit: int | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeBulkGovernanceResult:
    normalized_action = action.strip().lower() if isinstance(action, str) else ""
    if normalized_action not in {"delete", "restore", "update"}:
      raise ValueError("Bulk governance action must be delete, restore, or update.")
    normalized_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(view_ids)
    normalized_reason = (
      reason.strip()
      if isinstance(reason, str) and reason.strip()
      else f"scheduler_stitched_report_view_bulk_{normalized_action}"
    )
    normalized_name_prefix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_prefix,
      preserve_outer_spacing=True,
    )
    normalized_name_suffix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_suffix,
      preserve_outer_spacing=True,
    )
    normalized_description_append = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      description_append
    )
    normalized_occurrence_limit = (
      self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        occurrence_limit,
        default=8,
        minimum=1,
        maximum=50,
        field_name="scheduler stitched report occurrence_limit",
      )
      if isinstance(occurrence_limit, int)
      else None
    )
    normalized_history_limit = (
      self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        history_limit,
        default=12,
        minimum=1,
        maximum=200,
        field_name="scheduler stitched report history_limit",
      )
      if isinstance(history_limit, int)
      else None
    )
    normalized_drilldown_history_limit = (
      self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        drilldown_history_limit,
        default=12,
        minimum=1,
        maximum=100,
        field_name="scheduler stitched report drilldown_history_limit",
      )
      if isinstance(drilldown_history_limit, int)
      else None
    )
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    for view_id in normalized_ids:
      current = self._load_provider_provenance_scheduler_stitched_report_view_record(view_id)
      if current is None:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=view_id,
            outcome="failed",
            message="Stitched report view not found.",
          )
        )
        continue
      try:
        if normalized_action == "delete":
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.view_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Stitched report view is already deleted.",
              )
            )
            continue
          updated = self.delete_provider_provenance_scheduler_stitched_report_view(
            current.view_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=normalized_reason,
          )
        elif normalized_action == "restore":
          if current.status != "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.view_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Stitched report view is already active.",
              )
            )
            continue
          revision = self._find_latest_active_provider_provenance_scheduler_stitched_report_view_revision(
            current.view_id
          )
          if revision is None:
            failed_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.view_id,
                item_name=current.name,
                outcome="failed",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="No active revision is available for restore.",
              )
            )
            continue
          updated = self.restore_provider_provenance_scheduler_stitched_report_view_revision(
            current.view_id,
            revision.revision_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=normalized_reason,
          )
        else:
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.view_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Stitched report view is deleted; restore it before bulk editing.",
              )
            )
            continue
          updated_name = (
            f"{normalized_name_prefix or ''}{current.name}{normalized_name_suffix or ''}"
          )
          updated_description = (
            f"{current.description} {normalized_description_append}".strip()
            if normalized_description_append is not None
            else current.description
          )
          updated_query = self._build_provider_provenance_scheduler_stitched_report_view_bulk_query(
            current.query,
            query_patch,
          )
          updated_occurrence_limit = (
            normalized_occurrence_limit
            if normalized_occurrence_limit is not None
            else current.occurrence_limit
          )
          updated_history_limit = (
            normalized_history_limit
            if normalized_history_limit is not None
            else current.history_limit
          )
          updated_drilldown_history_limit = (
            normalized_drilldown_history_limit
            if normalized_drilldown_history_limit is not None
            else current.drilldown_history_limit
          )
          if (
            updated_name == current.name
            and updated_description == current.description
            and updated_query == current.query
            and updated_occurrence_limit == current.occurrence_limit
            and updated_history_limit == current.history_limit
            and updated_drilldown_history_limit == current.drilldown_history_limit
          ):
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.view_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Stitched report view already matches the requested bulk edits.",
              )
            )
            continue
          updated = self.update_provider_provenance_scheduler_stitched_report_view(
            current.view_id,
            name=updated_name,
            description=updated_description,
            query=updated_query,
            occurrence_limit=updated_occurrence_limit,
            history_limit=updated_history_limit,
            drilldown_history_limit=updated_drilldown_history_limit,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=normalized_reason,
          )
        applied_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=updated.view_id,
            item_name=updated.name,
            outcome="applied",
            status=updated.status,
            current_revision_id=updated.current_revision_id,
            message=(
              "Stitched report view updated."
              if normalized_action == "update"
              else "Stitched report view restored."
              if normalized_action == "restore"
              else "Stitched report view deleted."
            ),
          )
        )
      except Exception as error:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=current.view_id,
            item_name=current.name,
            outcome="failed",
            status=current.status,
            current_revision_id=current.current_revision_id,
            message=str(error),
          )
        )
    return ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type="stitched_report_view",
      action=normalized_action,
      reason=normalized_reason,
      requested_count=len(normalized_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )

  def list_provider_provenance_scheduler_stitched_report_view_audits(
    self,
    *,
    view_id: str | None = None,
    action: str | None = None,
    actor_tab_id: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportViewAuditRecord, ...]:
    normalized_view_id = (
      view_id.strip()
      if isinstance(view_id, str) and view_id.strip()
      else None
    )
    normalized_action = action.strip().lower() if isinstance(action, str) and action.strip() else None
    normalized_actor_tab_id = (
      actor_tab_id.strip()
      if isinstance(actor_tab_id, str) and actor_tab_id.strip()
      else None
    )
    normalized_limit = max(1, min(limit, 200))
    filtered: list[ProviderProvenanceSchedulerStitchedReportViewAuditRecord] = []
    for record in self._list_provider_provenance_scheduler_stitched_report_view_audit_records():
      if normalized_view_id is not None and record.view_id != normalized_view_id:
        continue
      if normalized_action is not None and record.action != normalized_action:
        continue
      if normalized_actor_tab_id is not None and record.actor_tab_id != normalized_actor_tab_id:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.audit_id,
          record.view_id,
          record.action,
          record.reason,
          record.detail,
          record.revision_id,
          record.source_revision_id,
          record.name,
          record.status,
          record.filter_summary,
          record.actor_tab_id,
          record.actor_tab_label,
        ),
        search=search,
      ):
        continue
      filtered.append(
        replace(
          record,
          status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
        )
      )
    return tuple(filtered[:normalized_limit])

  def create_provider_provenance_scheduler_stitched_report_governance_registry(
    self,
    *,
    name: str,
    description: str = "",
    queue_view: dict[str, Any] | None = None,
    default_policy_template_id: str | None = None,
    default_policy_catalog_id: str | None = None,
    created_by_tab_id: str | None = None,
    created_by_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord:
    now = self._clock()
    (
      resolved_policy_catalog,
      resolved_policy_template,
      _resolved_lane,
      _resolved_priority,
      _resolved_guidance,
    ) = self._resolve_provider_provenance_scheduler_narrative_governance_policy_layer(
      item_type="stitched_report_view",
      action="update",
      policy_catalog_id=default_policy_catalog_id,
      policy_template_id=default_policy_template_id,
    )
    record = ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord(
      registry_id=uuid4().hex[:12],
      name=self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler stitched report governance registry name",
      ),
      description=description.strip() if isinstance(description, str) else "",
      queue_view=self._normalize_provider_provenance_scheduler_stitched_report_governance_registry_queue_view(
        queue_view
      ),
      default_policy_template_id=(
        resolved_policy_template.policy_template_id
        if resolved_policy_template is not None
        else None
      ),
      default_policy_template_name=(
        resolved_policy_template.name
        if resolved_policy_template is not None
        else None
      ),
      default_policy_catalog_id=(
        resolved_policy_catalog.catalog_id
        if resolved_policy_catalog is not None
        else None
      ),
      default_policy_catalog_name=(
        resolved_policy_catalog.name
        if resolved_policy_catalog is not None
        else None
      ),
      created_at=now,
      updated_at=now,
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
    return self._record_provider_provenance_scheduler_stitched_report_governance_registry_revision(
      record=record,
      action="created",
      reason="scheduler_stitched_report_governance_registry_created",
      recorded_at=now,
      actor_tab_id=record.created_by_tab_id,
      actor_tab_label=record.created_by_tab_label,
    )

  def list_provider_provenance_scheduler_stitched_report_governance_registries(
    self,
    *,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord, ...]:
    normalized_limit = max(1, min(limit, 200))
    filtered: list[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord] = []
    for record in self._list_provider_provenance_scheduler_stitched_report_governance_registry_records():
      normalized_queue_view = self._normalize_provider_provenance_scheduler_stitched_report_governance_registry_queue_view(
        record.queue_view
      )
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.registry_id,
          record.name,
          record.description,
          record.status,
          record.default_policy_template_id,
          record.default_policy_template_name,
          record.default_policy_catalog_id,
          record.default_policy_catalog_name,
          normalized_queue_view.get("queue_state"),
          normalized_queue_view.get("item_type"),
          normalized_queue_view.get("approval_lane"),
          normalized_queue_view.get("approval_priority"),
          normalized_queue_view.get("policy_template_id"),
          normalized_queue_view.get("policy_catalog_id"),
          normalized_queue_view.get("search"),
          normalized_queue_view.get("sort"),
        ),
        search=search,
      ):
        continue
      filtered.append(
        replace(
          record,
          status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
          queue_view=normalized_queue_view,
        )
      )
    return tuple(filtered[:normalized_limit])

  def get_provider_provenance_scheduler_stitched_report_governance_registry(
    self,
    registry_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord:
    normalized_registry_id = registry_id.strip()
    if not normalized_registry_id:
      raise LookupError("Provider provenance stitched report governance registry not found.")
    record = self._load_provider_provenance_scheduler_stitched_report_governance_registry_record(
      normalized_registry_id
    )
    if record is None:
      raise LookupError("Provider provenance stitched report governance registry not found.")
    return replace(
      record,
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
      queue_view=self._normalize_provider_provenance_scheduler_stitched_report_governance_registry_queue_view(
        record.queue_view
      ),
    )

  def update_provider_provenance_scheduler_stitched_report_governance_registry(
    self,
    registry_id: str,
    *,
    name: str | None = None,
    description: str | None = None,
    queue_view: dict[str, Any] | None = None,
    default_policy_template_id: str | None = None,
    default_policy_catalog_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_stitched_report_governance_registry_updated",
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord:
    current = self.get_provider_provenance_scheduler_stitched_report_governance_registry(registry_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted stitched report governance registries must be restored from a revision before editing."
      )
    (
      resolved_policy_catalog,
      resolved_policy_template,
      _resolved_lane,
      _resolved_priority,
      _resolved_guidance,
    ) = self._resolve_provider_provenance_scheduler_narrative_governance_policy_layer(
      item_type="stitched_report_view",
      action="update",
      policy_catalog_id=(
        default_policy_catalog_id
        if isinstance(default_policy_catalog_id, str)
        else current.default_policy_catalog_id
      ),
      policy_template_id=(
        default_policy_template_id
        if isinstance(default_policy_template_id, str)
        else current.default_policy_template_id
      ),
    )
    updated_name = (
      self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler stitched report governance registry name",
      )
      if isinstance(name, str)
      else current.name
    )
    updated_description = (
      description.strip()
      if isinstance(description, str)
      else current.description
    )
    updated_queue_view = (
      self._normalize_provider_provenance_scheduler_stitched_report_governance_registry_queue_view(
        queue_view
      )
      if isinstance(queue_view, dict)
      else current.queue_view
    )
    updated_default_policy_template_id = (
      resolved_policy_template.policy_template_id
      if resolved_policy_template is not None
      else None
    )
    updated_default_policy_template_name = (
      resolved_policy_template.name
      if resolved_policy_template is not None
      else None
    )
    updated_default_policy_catalog_id = (
      resolved_policy_catalog.catalog_id
      if resolved_policy_catalog is not None
      else None
    )
    updated_default_policy_catalog_name = (
      resolved_policy_catalog.name
      if resolved_policy_catalog is not None
      else None
    )
    if (
      updated_name == current.name
      and updated_description == current.description
      and updated_queue_view == current.queue_view
      and updated_default_policy_template_id == current.default_policy_template_id
      and updated_default_policy_template_name == current.default_policy_template_name
      and updated_default_policy_catalog_id == current.default_policy_catalog_id
      and updated_default_policy_catalog_name == current.default_policy_catalog_name
    ):
      return current
    updated = replace(
      current,
      name=updated_name,
      description=updated_description,
      queue_view=updated_queue_view,
      default_policy_template_id=updated_default_policy_template_id,
      default_policy_template_name=updated_default_policy_template_name,
      default_policy_catalog_id=updated_default_policy_catalog_id,
      default_policy_catalog_name=updated_default_policy_catalog_name,
      updated_at=self._clock(),
    )
    return self._record_provider_provenance_scheduler_stitched_report_governance_registry_revision(
      record=updated,
      action="updated",
      reason=reason,
      recorded_at=updated.updated_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def delete_provider_provenance_scheduler_stitched_report_governance_registry(
    self,
    registry_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_stitched_report_governance_registry_deleted",
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord:
    current = self.get_provider_provenance_scheduler_stitched_report_governance_registry(registry_id)
    if current.status == "deleted":
      return current
    deleted_at = self._clock()
    deleted = replace(
      current,
      status="deleted",
      updated_at=deleted_at,
      deleted_at=deleted_at,
      deleted_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      deleted_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )
    return self._record_provider_provenance_scheduler_stitched_report_governance_registry_revision(
      record=deleted,
      action="deleted",
      reason=reason,
      recorded_at=deleted_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def list_provider_provenance_scheduler_stitched_report_governance_registry_revisions(
    self,
    registry_id: str,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord, ...]:
    current = self.get_provider_provenance_scheduler_stitched_report_governance_registry(registry_id)
    revisions = [
      replace(
        revision,
        status=self._normalize_provider_provenance_scheduler_narrative_record_status(revision.status),
        queue_view=self._normalize_provider_provenance_scheduler_stitched_report_governance_registry_queue_view(
          revision.queue_view
        ),
      )
      for revision in self._list_provider_provenance_scheduler_stitched_report_governance_registry_revision_records()
      if revision.registry_id == current.registry_id
    ]
    return tuple(revisions)

  def restore_provider_provenance_scheduler_stitched_report_governance_registry_revision(
    self,
    registry_id: str,
    revision_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_stitched_report_governance_registry_revision_restored",
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord:
    current = self.get_provider_provenance_scheduler_stitched_report_governance_registry(registry_id)
    revision = self._load_provider_provenance_scheduler_stitched_report_governance_registry_revision_record(
      revision_id.strip()
    )
    if revision is None or revision.registry_id != current.registry_id:
      raise LookupError("Provider provenance stitched report governance registry revision not found.")
    restored_at = self._clock()
    restored = replace(
      current,
      name=revision.name,
      description=revision.description,
      queue_view=self._normalize_provider_provenance_scheduler_stitched_report_governance_registry_queue_view(
        revision.queue_view
      ),
      default_policy_template_id=revision.default_policy_template_id,
      default_policy_template_name=revision.default_policy_template_name,
      default_policy_catalog_id=revision.default_policy_catalog_id,
      default_policy_catalog_name=revision.default_policy_catalog_name,
      status="active",
      updated_at=restored_at,
      deleted_at=None,
      deleted_by_tab_id=None,
      deleted_by_tab_label=None,
    )
    return self._record_provider_provenance_scheduler_stitched_report_governance_registry_revision(
      record=restored,
      action="restored",
      reason=reason,
      recorded_at=restored_at,
      source_revision_id=revision.revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def _build_provider_provenance_scheduler_stitched_report_governance_registry_bulk_queue_view(
    self,
    current_queue_view: dict[str, Any],
    queue_view_patch: dict[str, Any] | None,
  ) -> dict[str, Any]:
    candidate = deepcopy(current_queue_view) if isinstance(current_queue_view, dict) else {}
    if isinstance(queue_view_patch, dict):
      for key, value in queue_view_patch.items():
        candidate[key] = deepcopy(value)
    return (
      self._normalize_provider_provenance_scheduler_stitched_report_governance_registry_queue_view(
        candidate
      )
      or {}
    )

  def bulk_govern_provider_provenance_scheduler_stitched_report_governance_registries(
    self,
    registry_ids: Iterable[str],
    *,
    action: str,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    queue_view_patch: dict[str, Any] | None = None,
    default_policy_template_id: str | None = None,
    default_policy_catalog_id: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeBulkGovernanceResult:
    normalized_action = action.strip().lower()
    if normalized_action not in {"delete", "restore", "update"}:
      raise ValueError("Unsupported stitched governance registry bulk action.")
    normalized_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(registry_ids)
    normalized_name_prefix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_prefix,
      preserve_outer_spacing=True,
    )
    normalized_name_suffix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_suffix,
      preserve_outer_spacing=True,
    )
    normalized_description_append = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      description_append
    )
    normalized_default_policy_template_id = (
      default_policy_template_id
      if isinstance(default_policy_template_id, str)
      else None
    )
    normalized_default_policy_catalog_id = (
      default_policy_catalog_id
      if isinstance(default_policy_catalog_id, str)
      else None
    )
    normalized_queue_view_patch = (
      self._normalize_provider_provenance_scheduler_stitched_report_governance_registry_queue_view(
        queue_view_patch
      )
      if isinstance(queue_view_patch, dict)
      else None
    )
    resolved_reason = (
      reason.strip()
      if isinstance(reason, str) and reason.strip()
      else (
        "scheduler_stitched_report_governance_registry_bulk_deleted"
        if normalized_action == "delete"
        else (
          "scheduler_stitched_report_governance_registry_bulk_restored"
          if normalized_action == "restore"
          else "scheduler_stitched_report_governance_registry_bulk_updated"
        )
      )
    )
    if (
      normalized_action == "update"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and normalized_queue_view_patch is None
      and normalized_default_policy_template_id is None
      and normalized_default_policy_catalog_id is None
    ):
      raise ValueError("No stitched governance registry bulk update fields were provided.")
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    for registry_id in normalized_ids:
      try:
        current = self.get_provider_provenance_scheduler_stitched_report_governance_registry(registry_id)
        if normalized_action == "delete":
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.registry_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Registry is already deleted.",
              )
            )
            continue
          updated = self.delete_provider_provenance_scheduler_stitched_report_governance_registry(
            registry_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        elif normalized_action == "restore":
          if current.status != "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.registry_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Registry is already active.",
              )
            )
            continue
          revision = self._find_latest_active_provider_provenance_scheduler_stitched_report_governance_registry_revision(
            current.registry_id
          )
          if revision is None:
            failed_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.registry_id,
                item_name=current.name,
                outcome="failed",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="No active revision is available for restore.",
              )
            )
            continue
          updated = self.restore_provider_provenance_scheduler_stitched_report_governance_registry_revision(
            current.registry_id,
            revision.revision_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        else:
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.registry_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Deleted registry entries must be restored before editing.",
              )
            )
            continue
          updated_name = current.name
          if normalized_name_prefix is not None:
            updated_name = f"{normalized_name_prefix}{updated_name}"
          if normalized_name_suffix is not None:
            updated_name = f"{updated_name}{normalized_name_suffix}"
          updated_description = current.description
          if normalized_description_append is not None:
            updated_description = (
              f"{updated_description} {normalized_description_append}".strip()
              if updated_description
              else normalized_description_append
            )
          updated_queue_view = self._build_provider_provenance_scheduler_stitched_report_governance_registry_bulk_queue_view(
            current.queue_view,
            normalized_queue_view_patch,
          )
          updated = self.update_provider_provenance_scheduler_stitched_report_governance_registry(
            current.registry_id,
            name=updated_name,
            description=updated_description,
            queue_view=updated_queue_view,
            default_policy_template_id=(
              normalized_default_policy_template_id
              if normalized_default_policy_template_id is not None
              else current.default_policy_template_id
            ),
            default_policy_catalog_id=(
              normalized_default_policy_catalog_id
              if normalized_default_policy_catalog_id is not None
              else current.default_policy_catalog_id
            ),
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        applied_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=updated.registry_id,
            item_name=updated.name,
            outcome="applied",
            status=updated.status,
            current_revision_id=updated.current_revision_id,
            message=(
              "Stitched governance registry updated."
              if normalized_action == "update"
              else "Stitched governance registry restored."
              if normalized_action == "restore"
              else "Stitched governance registry deleted."
            ),
          )
        )
      except Exception as error:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=registry_id,
            item_name=None,
            outcome="failed",
            message=str(error),
          )
        )
    return ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type="stitched_report_governance_registry",
      action=normalized_action,
      reason=resolved_reason,
      requested_count=len(normalized_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )

  def list_provider_provenance_scheduler_stitched_report_governance_registry_audits(
    self,
    *,
    registry_id: str | None = None,
    action: str | None = None,
    actor_tab_id: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord, ...]:
    normalized_registry_id = (
      registry_id.strip()
      if isinstance(registry_id, str) and registry_id.strip()
      else None
    )
    normalized_action = action.strip().lower() if isinstance(action, str) and action.strip() else None
    normalized_actor_tab_id = (
      actor_tab_id.strip()
      if isinstance(actor_tab_id, str) and actor_tab_id.strip()
      else None
    )
    normalized_limit = max(1, min(limit, 200))
    filtered: list[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord] = []
    for record in self._list_provider_provenance_scheduler_stitched_report_governance_registry_audit_records():
      if normalized_registry_id is not None and record.registry_id != normalized_registry_id:
        continue
      if normalized_action is not None and record.action != normalized_action:
        continue
      if normalized_actor_tab_id is not None and record.actor_tab_id != normalized_actor_tab_id:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.audit_id,
          record.registry_id,
          record.action,
          record.reason,
          record.detail,
          record.revision_id,
          record.source_revision_id,
          record.name,
          record.description,
          record.status,
          record.default_policy_template_id,
          record.default_policy_template_name,
          record.default_policy_catalog_id,
          record.default_policy_catalog_name,
          record.actor_tab_id,
          record.actor_tab_label,
          record.queue_view.get("queue_state") if isinstance(record.queue_view, dict) else None,
          record.queue_view.get("search") if isinstance(record.queue_view, dict) else None,
          record.queue_view.get("sort") if isinstance(record.queue_view, dict) else None,
        ),
        search=search,
      ):
        continue
      filtered.append(
        replace(
          record,
          status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
          queue_view=self._normalize_provider_provenance_scheduler_stitched_report_governance_registry_queue_view(
            record.queue_view
          ) or {},
        )
      )
    return tuple(filtered[:normalized_limit])

  def create_provider_provenance_scheduler_narrative_template(
    self,
    *,
    name: str,
    description: str = "",
    query: dict[str, Any] | None = None,
    created_by_tab_id: str | None = None,
    created_by_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRecord:
    now = self._clock()
    record = ProviderProvenanceSchedulerNarrativeTemplateRecord(
      template_id=uuid4().hex[:12],
      name=self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler narrative template name",
      ),
      description=description.strip() if isinstance(description, str) else "",
      query=self._normalize_provider_provenance_analytics_query_payload(query),
      status="active",
      created_at=now,
      updated_at=now,
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
    return self._record_provider_provenance_scheduler_narrative_template_revision(
      record=record,
      action="created",
      reason="scheduler_narrative_template_created",
      recorded_at=now,
      actor_tab_id=record.created_by_tab_id,
      actor_tab_label=record.created_by_tab_label,
    )

  def update_provider_provenance_scheduler_narrative_template(
    self,
    template_id: str,
    *,
    name: str | None = None,
    description: str | None = None,
    query: dict[str, Any] | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_template_updated",
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRecord:
    current = self.get_provider_provenance_scheduler_narrative_template(template_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler narrative templates must be restored from a revision before editing."
      )
    updated_name = (
      self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler narrative template name",
      )
      if isinstance(name, str)
      else current.name
    )
    updated_description = (
      description.strip()
      if isinstance(description, str)
      else current.description
    )
    updated_query = (
      self._normalize_provider_provenance_analytics_query_payload(query)
      if isinstance(query, dict)
      else current.query
    )
    if (
      updated_name == current.name
      and updated_description == current.description
      and updated_query == current.query
    ):
      return current
    updated = replace(
      current,
      name=updated_name,
      description=updated_description,
      query=updated_query,
      updated_at=self._clock(),
    )
    return self._record_provider_provenance_scheduler_narrative_template_revision(
      record=updated,
      action="updated",
      reason=reason,
      recorded_at=updated.updated_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def delete_provider_provenance_scheduler_narrative_template(
    self,
    template_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_template_deleted",
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRecord:
    current = self.get_provider_provenance_scheduler_narrative_template(template_id)
    if current.status == "deleted":
      return current
    deleted_at = self._clock()
    deleted = replace(
      current,
      status="deleted",
      updated_at=deleted_at,
      deleted_at=deleted_at,
      deleted_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      deleted_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )
    return self._record_provider_provenance_scheduler_narrative_template_revision(
      record=deleted,
      action="deleted",
      reason=reason,
      recorded_at=deleted_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def list_provider_provenance_scheduler_narrative_templates(
    self,
    *,
    created_by_tab_id: str | None = None,
    focus_scope: str | None = None,
    category: str | None = None,
    narrative_facet: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeTemplateRecord, ...]:
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
    normalized_category = self._normalize_provider_provenance_scheduler_alert_history_category(category)
    normalized_narrative_facet = self._normalize_provider_provenance_scheduler_alert_history_narrative_facet(
      narrative_facet
    )
    normalized_limit = max(1, min(limit, 200))
    filtered: list[ProviderProvenanceSchedulerNarrativeTemplateRecord] = []
    for record in self._list_provider_provenance_scheduler_narrative_template_records():
      normalized_query = self._normalize_provider_provenance_analytics_query_payload(record.query)
      if normalized_creator is not None and record.created_by_tab_id != normalized_creator:
        continue
      if normalized_focus_scope is not None and normalized_query["focus_scope"] != normalized_focus_scope:
        continue
      if (
        normalized_category is not None
        and normalized_query.get("scheduler_alert_category") != normalized_category
      ):
        continue
      if (
        normalized_narrative_facet is not None
        and normalized_query.get("scheduler_alert_narrative_facet") != normalized_narrative_facet
      ):
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.template_id,
          record.name,
          record.description,
          record.status,
          record.created_by_tab_id,
          record.created_by_tab_label,
          normalized_query.get("focus_key"),
          normalized_query.get("symbol"),
          normalized_query.get("timeframe"),
          normalized_query.get("scheduler_alert_category"),
          normalized_query.get("scheduler_alert_status"),
          normalized_query.get("scheduler_alert_narrative_facet"),
          normalized_query.get("search"),
        ),
        search=search,
      ):
        continue
      filtered.append(replace(record, query=normalized_query))
    return tuple(filtered[:normalized_limit])

  def get_provider_provenance_scheduler_narrative_template(
    self,
    template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRecord:
    normalized_template_id = template_id.strip()
    if not normalized_template_id:
      raise LookupError("Provider provenance scheduler narrative template not found.")
    record = self._load_provider_provenance_scheduler_narrative_template_record(normalized_template_id)
    if record is None:
      raise LookupError("Provider provenance scheduler narrative template not found.")
    return replace(
      record,
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
      query=self._normalize_provider_provenance_analytics_query_payload(record.query),
    )

  def list_provider_provenance_scheduler_narrative_template_revisions(
    self,
    template_id: str,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord, ...]:
    current = self.get_provider_provenance_scheduler_narrative_template(template_id)
    revisions = [
      replace(
        revision,
        status=self._normalize_provider_provenance_scheduler_narrative_record_status(revision.status),
        query=self._normalize_provider_provenance_analytics_query_payload(revision.query),
      )
      for revision in self._list_provider_provenance_scheduler_narrative_template_revision_records()
      if revision.template_id == current.template_id
    ]
    return tuple(revisions)

  def restore_provider_provenance_scheduler_narrative_template_revision(
    self,
    template_id: str,
    revision_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_template_revision_restored",
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRecord:
    current = self.get_provider_provenance_scheduler_narrative_template(template_id)
    revision = self._load_provider_provenance_scheduler_narrative_template_revision_record(
      revision_id.strip()
    )
    if revision is None or revision.template_id != current.template_id:
      raise LookupError("Provider provenance scheduler narrative template revision not found.")
    restored_at = self._clock()
    restored = replace(
      current,
      name=revision.name,
      description=revision.description,
      query=self._normalize_provider_provenance_analytics_query_payload(revision.query),
      status="active",
      updated_at=restored_at,
      deleted_at=None,
      deleted_by_tab_id=None,
      deleted_by_tab_label=None,
    )
    return self._record_provider_provenance_scheduler_narrative_template_revision(
      record=restored,
      action="restored",
      reason=reason,
      recorded_at=restored_at,
      source_revision_id=revision.revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def _normalize_provider_provenance_scheduler_narrative_bulk_ids(
    self,
    values: Iterable[str],
  ) -> tuple[str, ...]:
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
      if not isinstance(value, str):
        continue
      stripped = value.strip()
      if not stripped or stripped in seen:
        continue
      normalized.append(stripped)
      seen.add(stripped)
      if len(normalized) >= 100:
        break
    return tuple(normalized)

  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
    value: str | None,
    *,
    preserve_outer_spacing: bool = False,
  ) -> str | None:
    if not isinstance(value, str):
      return None
    stripped = value.strip()
    if not stripped:
      return None
    return value if preserve_outer_spacing else stripped

  def _build_provider_provenance_scheduler_narrative_bulk_template_query(
    self,
    current_query: dict[str, Any],
    query_patch: dict[str, Any] | None,
  ) -> dict[str, Any]:
    if not isinstance(query_patch, dict) or not query_patch:
      return current_query
    merged = deepcopy(current_query)
    for key in (
      "scheduler_alert_category",
      "scheduler_alert_status",
      "scheduler_alert_narrative_facet",
      "result_limit",
      "window_days",
    ):
      if key in query_patch:
        merged[key] = query_patch[key]
    return self._normalize_provider_provenance_analytics_query_payload(merged)

  def _build_provider_provenance_scheduler_narrative_bulk_registry_layout(
    self,
    current_layout: dict[str, Any],
    layout_patch: dict[str, Any] | None,
  ) -> dict[str, Any]:
    if not isinstance(layout_patch, dict) or not layout_patch:
      return current_layout
    merged = deepcopy(current_layout)
    for key in ("show_rollups", "show_time_series", "show_recent_exports"):
      if key in layout_patch:
        merged[key] = layout_patch[key]
    return self._normalize_provider_provenance_scheduler_narrative_registry_layout_payload(merged)

  def _build_provider_provenance_scheduler_narrative_template_snapshot(
    self,
    record: ProviderProvenanceSchedulerNarrativeTemplateRecord,
  ) -> dict[str, Any]:
    normalized_query = self._normalize_provider_provenance_analytics_query_payload(record.query)
    return {
      "name": record.name,
      "description": record.description,
      "status": self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
      "query": deepcopy(normalized_query),
      "focus": self._build_provider_provenance_workspace_focus_payload(normalized_query),
      "filter_summary": self._build_provider_provenance_analytics_filter_summary(normalized_query),
    }

  def _build_provider_provenance_scheduler_narrative_governance_policy_template_snapshot(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
  ) -> dict[str, Any]:
    return {
      "name": record.name,
      "description": record.description,
      "item_type_scope": record.item_type_scope,
      "action_scope": record.action_scope,
      "approval_lane": record.approval_lane,
      "approval_priority": record.approval_priority,
      "guidance": record.guidance,
      "status": self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
    }

  def _build_provider_provenance_scheduler_narrative_registry_snapshot(
    self,
    record: ProviderProvenanceSchedulerNarrativeRegistryRecord,
  ) -> dict[str, Any]:
    normalized_query = self._normalize_provider_provenance_analytics_query_payload(record.query)
    normalized_layout = self._normalize_provider_provenance_scheduler_narrative_registry_layout_payload(
      record.layout
    )
    return {
      "name": record.name,
      "description": record.description,
      "template_id": record.template_id,
      "status": self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
      "query": deepcopy(normalized_query),
      "focus": self._build_provider_provenance_workspace_focus_payload(normalized_query),
      "filter_summary": self._build_provider_provenance_analytics_filter_summary(normalized_query),
      "layout": deepcopy(normalized_layout),
    }

  def _build_provider_provenance_scheduler_stitched_report_view_snapshot(
    self,
    record: ProviderProvenanceSchedulerStitchedReportViewRecord,
  ) -> dict[str, Any]:
    normalized_query = self._normalize_provider_provenance_analytics_query_payload(record.query)
    return {
      "name": record.name,
      "description": record.description,
      "status": self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
      "query": deepcopy(normalized_query),
      "focus": self._build_provider_provenance_workspace_focus_payload(normalized_query),
      "filter_summary": self._build_provider_provenance_analytics_filter_summary(normalized_query),
      "occurrence_limit": int(record.occurrence_limit),
      "history_limit": int(record.history_limit),
      "drilldown_history_limit": int(record.drilldown_history_limit),
    }

  def _build_provider_provenance_scheduler_stitched_report_governance_registry_snapshot(
    self,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord,
  ) -> dict[str, Any]:
    normalized_queue_view = self._normalize_provider_provenance_scheduler_stitched_report_governance_registry_queue_view(
      record.queue_view
    )
    return {
      "name": record.name,
      "description": record.description,
      "status": self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
      "queue_view": deepcopy(normalized_queue_view),
      "default_policy_template_id": record.default_policy_template_id,
      "default_policy_template_name": record.default_policy_template_name,
      "default_policy_catalog_id": record.default_policy_catalog_id,
      "default_policy_catalog_name": record.default_policy_catalog_name,
    }

  @staticmethod
  def _build_provider_provenance_scheduler_narrative_field_diffs(
    current_snapshot: dict[str, Any],
    proposed_snapshot: dict[str, Any],
    fields: Iterable[str],
  ) -> tuple[tuple[str, ...], dict[str, dict[str, Any]]]:
    changed_fields: list[str] = []
    field_diffs: dict[str, dict[str, Any]] = {}
    for field_name in fields:
      current_value = current_snapshot.get(field_name)
      proposed_value = proposed_snapshot.get(field_name)
      if current_value == proposed_value:
        continue
      changed_fields.append(field_name)
      field_diffs[field_name] = {
        "before": deepcopy(current_value),
        "after": deepcopy(proposed_value),
      }
    return tuple(changed_fields), field_diffs

  def _preview_provider_provenance_scheduler_narrative_template_governance_item(
    self,
    current: ProviderProvenanceSchedulerNarrativeTemplateRecord,
    *,
    action: str,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    query_patch: dict[str, Any] | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePreviewItem:
    current_snapshot = self._build_provider_provenance_scheduler_narrative_template_snapshot(current)
    if action == "delete":
      if current.status == "deleted":
        return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
          item_id=current.template_id,
          item_name=current.name,
          status=current.status,
          current_revision_id=current.current_revision_id,
          rollback_revision_id=current.current_revision_id,
          outcome="skipped",
          message="Template is already deleted.",
          current_snapshot=current_snapshot,
          proposed_snapshot=deepcopy(current_snapshot),
        )
      proposed = replace(current, status="deleted")
      proposed_snapshot = self._build_provider_provenance_scheduler_narrative_template_snapshot(proposed)
      changed_fields, field_diffs = self._build_provider_provenance_scheduler_narrative_field_diffs(
        current_snapshot,
        proposed_snapshot,
        ("status",),
      )
      return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
        item_id=current.template_id,
        item_name=current.name,
        status=current.status,
        current_revision_id=current.current_revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome="changed",
        message="Template will be deleted.",
        changed_fields=changed_fields,
        field_diffs=field_diffs,
        current_snapshot=current_snapshot,
        proposed_snapshot=proposed_snapshot,
      )
    if action == "restore":
      if current.status != "deleted":
        return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
          item_id=current.template_id,
          item_name=current.name,
          status=current.status,
          current_revision_id=current.current_revision_id,
          rollback_revision_id=current.current_revision_id,
          outcome="skipped",
          message="Template is already active.",
          current_snapshot=current_snapshot,
          proposed_snapshot=deepcopy(current_snapshot),
        )
      revision = self._find_latest_active_provider_provenance_scheduler_narrative_template_revision(
        current.template_id
      )
      if revision is None:
        return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
          item_id=current.template_id,
          item_name=current.name,
          status=current.status,
          current_revision_id=current.current_revision_id,
          rollback_revision_id=current.current_revision_id,
          outcome="failed",
          message="No active revision is available for restore.",
          current_snapshot=current_snapshot,
          proposed_snapshot=deepcopy(current_snapshot),
        )
      proposed = replace(
        current,
        name=revision.name,
        description=revision.description,
        query=self._normalize_provider_provenance_analytics_query_payload(revision.query),
        status="active",
      )
      proposed_snapshot = self._build_provider_provenance_scheduler_narrative_template_snapshot(proposed)
      changed_fields, field_diffs = self._build_provider_provenance_scheduler_narrative_field_diffs(
        current_snapshot,
        proposed_snapshot,
        ("name", "description", "status", "query", "filter_summary", "focus"),
      )
      return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
        item_id=current.template_id,
        item_name=current.name,
        status=current.status,
        current_revision_id=current.current_revision_id,
        apply_revision_id=revision.revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome="changed",
        message="Template will be restored from the latest active revision.",
        changed_fields=changed_fields,
        field_diffs=field_diffs,
        current_snapshot=current_snapshot,
        proposed_snapshot=proposed_snapshot,
      )
    if current.status == "deleted":
      return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
        item_id=current.template_id,
        item_name=current.name,
        status=current.status,
        current_revision_id=current.current_revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome="skipped",
        message="Template is deleted; restore it before applying bulk edits.",
        current_snapshot=current_snapshot,
        proposed_snapshot=deepcopy(current_snapshot),
      )
    updated_name = f"{name_prefix or ''}{current.name}{name_suffix or ''}"
    updated_description = (
      f"{current.description} {description_append}".strip()
      if description_append is not None
      else current.description
    )
    updated_query = self._build_provider_provenance_scheduler_narrative_bulk_template_query(
      current.query,
      query_patch,
    )
    proposed = replace(current, name=updated_name, description=updated_description, query=updated_query)
    proposed_snapshot = self._build_provider_provenance_scheduler_narrative_template_snapshot(proposed)
    changed_fields, field_diffs = self._build_provider_provenance_scheduler_narrative_field_diffs(
      current_snapshot,
      proposed_snapshot,
      ("name", "description", "query", "filter_summary", "focus"),
    )
    if not changed_fields:
      return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
        item_id=current.template_id,
        item_name=current.name,
        status=current.status,
        current_revision_id=current.current_revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome="skipped",
        message="Template already matches the requested bulk edits.",
        current_snapshot=current_snapshot,
        proposed_snapshot=deepcopy(current_snapshot),
      )
    return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
      item_id=current.template_id,
      item_name=current.name,
      status=current.status,
      current_revision_id=current.current_revision_id,
      rollback_revision_id=current.current_revision_id,
      outcome="changed",
      message="Template will be updated with the requested bulk governance patch.",
      changed_fields=changed_fields,
      field_diffs=field_diffs,
      current_snapshot=current_snapshot,
      proposed_snapshot=proposed_snapshot,
    )

  def _preview_provider_provenance_scheduler_narrative_registry_governance_item(
    self,
    current: ProviderProvenanceSchedulerNarrativeRegistryRecord,
    *,
    action: str,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    query_patch: dict[str, Any] | None = None,
    layout_patch: dict[str, Any] | None = None,
    template_id: str | None = None,
    clear_template_link: bool = False,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePreviewItem:
    current_snapshot = self._build_provider_provenance_scheduler_narrative_registry_snapshot(current)
    if action == "delete":
      if current.status == "deleted":
        return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
          item_id=current.registry_id,
          item_name=current.name,
          status=current.status,
          current_revision_id=current.current_revision_id,
          rollback_revision_id=current.current_revision_id,
          outcome="skipped",
          message="Registry is already deleted.",
          current_snapshot=current_snapshot,
          proposed_snapshot=deepcopy(current_snapshot),
        )
      proposed = replace(current, status="deleted")
      proposed_snapshot = self._build_provider_provenance_scheduler_narrative_registry_snapshot(proposed)
      changed_fields, field_diffs = self._build_provider_provenance_scheduler_narrative_field_diffs(
        current_snapshot,
        proposed_snapshot,
        ("status",),
      )
      return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
        item_id=current.registry_id,
        item_name=current.name,
        status=current.status,
        current_revision_id=current.current_revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome="changed",
        message="Registry will be deleted.",
        changed_fields=changed_fields,
        field_diffs=field_diffs,
        current_snapshot=current_snapshot,
        proposed_snapshot=proposed_snapshot,
      )
    if action == "restore":
      if current.status != "deleted":
        return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
          item_id=current.registry_id,
          item_name=current.name,
          status=current.status,
          current_revision_id=current.current_revision_id,
          rollback_revision_id=current.current_revision_id,
          outcome="skipped",
          message="Registry is already active.",
          current_snapshot=current_snapshot,
          proposed_snapshot=deepcopy(current_snapshot),
        )
      revision = self._find_latest_active_provider_provenance_scheduler_narrative_registry_revision(
        current.registry_id
      )
      if revision is None:
        return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
          item_id=current.registry_id,
          item_name=current.name,
          status=current.status,
          current_revision_id=current.current_revision_id,
          rollback_revision_id=current.current_revision_id,
          outcome="failed",
          message="No active revision is available for restore.",
          current_snapshot=current_snapshot,
          proposed_snapshot=deepcopy(current_snapshot),
        )
      proposed = replace(
        current,
        name=revision.name,
        description=revision.description,
        query=self._normalize_provider_provenance_analytics_query_payload(revision.query),
        layout=self._normalize_provider_provenance_scheduler_narrative_registry_layout_payload(
          revision.layout
        ),
        template_id=revision.template_id,
        status="active",
      )
      proposed_snapshot = self._build_provider_provenance_scheduler_narrative_registry_snapshot(proposed)
      changed_fields, field_diffs = self._build_provider_provenance_scheduler_narrative_field_diffs(
        current_snapshot,
        proposed_snapshot,
        ("name", "description", "template_id", "status", "query", "filter_summary", "focus", "layout"),
      )
      return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
        item_id=current.registry_id,
        item_name=current.name,
        status=current.status,
        current_revision_id=current.current_revision_id,
        apply_revision_id=revision.revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome="changed",
        message="Registry will be restored from the latest active revision.",
        changed_fields=changed_fields,
        field_diffs=field_diffs,
        current_snapshot=current_snapshot,
        proposed_snapshot=proposed_snapshot,
      )
    if current.status == "deleted":
      return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
        item_id=current.registry_id,
        item_name=current.name,
        status=current.status,
        current_revision_id=current.current_revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome="skipped",
        message="Registry is deleted; restore it before applying bulk edits.",
        current_snapshot=current_snapshot,
        proposed_snapshot=deepcopy(current_snapshot),
      )
    updated_name = f"{name_prefix or ''}{current.name}{name_suffix or ''}"
    updated_description = (
      f"{current.description} {description_append}".strip()
      if description_append is not None
      else current.description
    )
    updated_query = self._build_provider_provenance_scheduler_narrative_bulk_template_query(
      current.query,
      query_patch,
    )
    updated_layout = self._build_provider_provenance_scheduler_narrative_bulk_registry_layout(
      current.layout,
      layout_patch,
    )
    updated_template_id = (
      None
      if clear_template_link
      else (
        template_id.strip()
        if isinstance(template_id, str) and template_id.strip()
        else current.template_id
      )
    )
    proposed = replace(
      current,
      name=updated_name,
      description=updated_description,
      query=updated_query,
      layout=updated_layout,
      template_id=updated_template_id,
    )
    proposed_snapshot = self._build_provider_provenance_scheduler_narrative_registry_snapshot(proposed)
    changed_fields, field_diffs = self._build_provider_provenance_scheduler_narrative_field_diffs(
      current_snapshot,
      proposed_snapshot,
      ("name", "description", "template_id", "query", "filter_summary", "focus", "layout"),
    )
    if not changed_fields:
      return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
        item_id=current.registry_id,
        item_name=current.name,
        status=current.status,
        current_revision_id=current.current_revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome="skipped",
        message="Registry already matches the requested bulk edits.",
        current_snapshot=current_snapshot,
        proposed_snapshot=deepcopy(current_snapshot),
      )
    return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
      item_id=current.registry_id,
      item_name=current.name,
      status=current.status,
      current_revision_id=current.current_revision_id,
      rollback_revision_id=current.current_revision_id,
      outcome="changed",
      message="Registry will be updated with the requested bulk governance patch.",
      changed_fields=changed_fields,
      field_diffs=field_diffs,
      current_snapshot=current_snapshot,
      proposed_snapshot=proposed_snapshot,
    )

  def _preview_provider_provenance_scheduler_stitched_report_view_governance_item(
    self,
    current: ProviderProvenanceSchedulerStitchedReportViewRecord,
    *,
    action: str,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    query_patch: dict[str, Any] | None = None,
    occurrence_limit: int | None = None,
    history_limit: int | None = None,
    drilldown_history_limit: int | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePreviewItem:
    current_snapshot = self._build_provider_provenance_scheduler_stitched_report_view_snapshot(current)
    if action == "delete":
      if current.status == "deleted":
        return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
          item_id=current.view_id,
          item_name=current.name,
          status=current.status,
          current_revision_id=current.current_revision_id,
          rollback_revision_id=current.current_revision_id,
          outcome="skipped",
          message="Stitched report view is already deleted.",
          current_snapshot=current_snapshot,
          proposed_snapshot=deepcopy(current_snapshot),
        )
      proposed = replace(current, status="deleted")
      proposed_snapshot = self._build_provider_provenance_scheduler_stitched_report_view_snapshot(proposed)
      changed_fields, field_diffs = self._build_provider_provenance_scheduler_narrative_field_diffs(
        current_snapshot,
        proposed_snapshot,
        ("status",),
      )
      return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
        item_id=current.view_id,
        item_name=current.name,
        status=current.status,
        current_revision_id=current.current_revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome="changed",
        message="Stitched report view will be deleted.",
        changed_fields=changed_fields,
        field_diffs=field_diffs,
        current_snapshot=current_snapshot,
        proposed_snapshot=proposed_snapshot,
      )
    if action == "restore":
      if current.status != "deleted":
        return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
          item_id=current.view_id,
          item_name=current.name,
          status=current.status,
          current_revision_id=current.current_revision_id,
          rollback_revision_id=current.current_revision_id,
          outcome="skipped",
          message="Stitched report view is already active.",
          current_snapshot=current_snapshot,
          proposed_snapshot=deepcopy(current_snapshot),
        )
      revision = self._find_latest_active_provider_provenance_scheduler_stitched_report_view_revision(
        current.view_id
      )
      if revision is None:
        return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
          item_id=current.view_id,
          item_name=current.name,
          status=current.status,
          current_revision_id=current.current_revision_id,
          rollback_revision_id=current.current_revision_id,
          outcome="failed",
          message="No active revision is available for restore.",
          current_snapshot=current_snapshot,
          proposed_snapshot=deepcopy(current_snapshot),
        )
      proposed = replace(
        current,
        name=revision.name,
        description=revision.description,
        query=self._normalize_provider_provenance_analytics_query_payload(revision.query),
        occurrence_limit=self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
          revision.occurrence_limit,
          default=8,
          minimum=1,
          maximum=50,
          field_name="scheduler stitched report occurrence_limit",
        ),
        history_limit=self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
          revision.history_limit,
          default=12,
          minimum=1,
          maximum=200,
          field_name="scheduler stitched report history_limit",
        ),
        drilldown_history_limit=self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
          revision.drilldown_history_limit,
          default=12,
          minimum=1,
          maximum=100,
          field_name="scheduler stitched report drilldown_history_limit",
        ),
        status="active",
      )
      proposed_snapshot = self._build_provider_provenance_scheduler_stitched_report_view_snapshot(proposed)
      changed_fields, field_diffs = self._build_provider_provenance_scheduler_narrative_field_diffs(
        current_snapshot,
        proposed_snapshot,
        (
          "name",
          "description",
          "status",
          "query",
          "filter_summary",
          "focus",
          "occurrence_limit",
          "history_limit",
          "drilldown_history_limit",
        ),
      )
      return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
        item_id=current.view_id,
        item_name=current.name,
        status=current.status,
        current_revision_id=current.current_revision_id,
        apply_revision_id=revision.revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome="changed",
        message="Stitched report view will be restored from the latest active revision.",
        changed_fields=changed_fields,
        field_diffs=field_diffs,
        current_snapshot=current_snapshot,
        proposed_snapshot=proposed_snapshot,
      )
    if current.status == "deleted":
      return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
        item_id=current.view_id,
        item_name=current.name,
        status=current.status,
        current_revision_id=current.current_revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome="skipped",
        message="Stitched report view is deleted; restore it before applying bulk edits.",
        current_snapshot=current_snapshot,
        proposed_snapshot=deepcopy(current_snapshot),
      )
    updated_name = f"{name_prefix or ''}{current.name}{name_suffix or ''}"
    updated_description = (
      f"{current.description} {description_append}".strip()
      if description_append is not None
      else current.description
    )
    updated_query = self._build_provider_provenance_scheduler_stitched_report_view_bulk_query(
      current.query,
      query_patch,
    )
    proposed = replace(
      current,
      name=updated_name,
      description=updated_description,
      query=updated_query,
      occurrence_limit=(
        self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
          occurrence_limit,
          default=int(current.occurrence_limit),
          minimum=1,
          maximum=50,
          field_name="scheduler stitched report occurrence_limit",
        )
        if occurrence_limit is not None
        else current.occurrence_limit
      ),
      history_limit=(
        self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
          history_limit,
          default=int(current.history_limit),
          minimum=1,
          maximum=200,
          field_name="scheduler stitched report history_limit",
        )
        if history_limit is not None
        else current.history_limit
      ),
      drilldown_history_limit=(
        self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
          drilldown_history_limit,
          default=int(current.drilldown_history_limit),
          minimum=1,
          maximum=100,
          field_name="scheduler stitched report drilldown_history_limit",
        )
        if drilldown_history_limit is not None
        else current.drilldown_history_limit
      ),
    )
    proposed_snapshot = self._build_provider_provenance_scheduler_stitched_report_view_snapshot(proposed)
    changed_fields, field_diffs = self._build_provider_provenance_scheduler_narrative_field_diffs(
      current_snapshot,
      proposed_snapshot,
      (
        "name",
        "description",
        "query",
        "filter_summary",
        "focus",
        "occurrence_limit",
        "history_limit",
        "drilldown_history_limit",
      ),
    )
    if not changed_fields:
      return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
        item_id=current.view_id,
        item_name=current.name,
        status=current.status,
        current_revision_id=current.current_revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome="skipped",
        message="Stitched report view already matches the requested bulk edits.",
        current_snapshot=current_snapshot,
        proposed_snapshot=deepcopy(current_snapshot),
      )
    return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
      item_id=current.view_id,
      item_name=current.name,
      status=current.status,
      current_revision_id=current.current_revision_id,
      rollback_revision_id=current.current_revision_id,
      outcome="changed",
      message="Stitched report view will be updated with the requested governance patch.",
      changed_fields=changed_fields,
      field_diffs=field_diffs,
      current_snapshot=current_snapshot,
      proposed_snapshot=proposed_snapshot,
    )

  def _preview_provider_provenance_scheduler_stitched_report_governance_registry_governance_item(
    self,
    current: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord,
    *,
    action: str,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    queue_view_patch: dict[str, Any] | None = None,
    default_policy_template_id: str | None = None,
    default_policy_catalog_id: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePreviewItem:
    current_snapshot = self._build_provider_provenance_scheduler_stitched_report_governance_registry_snapshot(
      current
    )
    if action == "delete":
      if current.status == "deleted":
        return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
          item_id=current.registry_id,
          item_name=current.name,
          status=current.status,
          current_revision_id=current.current_revision_id,
          rollback_revision_id=current.current_revision_id,
          outcome="skipped",
          message="Stitched governance registry is already deleted.",
          current_snapshot=current_snapshot,
          proposed_snapshot=deepcopy(current_snapshot),
        )
      proposed = replace(current, status="deleted")
      proposed_snapshot = self._build_provider_provenance_scheduler_stitched_report_governance_registry_snapshot(
        proposed
      )
      changed_fields, field_diffs = self._build_provider_provenance_scheduler_narrative_field_diffs(
        current_snapshot,
        proposed_snapshot,
        ("status",),
      )
      return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
        item_id=current.registry_id,
        item_name=current.name,
        status=current.status,
        current_revision_id=current.current_revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome="changed",
        message="Stitched governance registry will be deleted.",
        changed_fields=changed_fields,
        field_diffs=field_diffs,
        current_snapshot=current_snapshot,
        proposed_snapshot=proposed_snapshot,
      )
    if action == "restore":
      if current.status != "deleted":
        return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
          item_id=current.registry_id,
          item_name=current.name,
          status=current.status,
          current_revision_id=current.current_revision_id,
          rollback_revision_id=current.current_revision_id,
          outcome="skipped",
          message="Stitched governance registry is already active.",
          current_snapshot=current_snapshot,
          proposed_snapshot=deepcopy(current_snapshot),
        )
      revision = self._find_latest_active_provider_provenance_scheduler_stitched_report_governance_registry_revision(
        current.registry_id
      )
      if revision is None:
        return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
          item_id=current.registry_id,
          item_name=current.name,
          status=current.status,
          current_revision_id=current.current_revision_id,
          rollback_revision_id=current.current_revision_id,
          outcome="failed",
          message="No active revision is available for restore.",
          current_snapshot=current_snapshot,
          proposed_snapshot=deepcopy(current_snapshot),
        )
      proposed = replace(
        current,
        name=revision.name,
        description=revision.description,
        queue_view=self._normalize_provider_provenance_scheduler_stitched_report_governance_registry_queue_view(
          revision.queue_view
        ),
        default_policy_template_id=revision.default_policy_template_id,
        default_policy_template_name=revision.default_policy_template_name,
        default_policy_catalog_id=revision.default_policy_catalog_id,
        default_policy_catalog_name=revision.default_policy_catalog_name,
        status="active",
      )
      proposed_snapshot = self._build_provider_provenance_scheduler_stitched_report_governance_registry_snapshot(
        proposed
      )
      changed_fields, field_diffs = self._build_provider_provenance_scheduler_narrative_field_diffs(
        current_snapshot,
        proposed_snapshot,
        (
          "name",
          "description",
          "status",
          "queue_view",
          "default_policy_template_id",
          "default_policy_template_name",
          "default_policy_catalog_id",
          "default_policy_catalog_name",
        ),
      )
      return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
        item_id=current.registry_id,
        item_name=current.name,
        status=current.status,
        current_revision_id=current.current_revision_id,
        apply_revision_id=revision.revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome="changed",
        message="Stitched governance registry will be restored from the latest active revision.",
        changed_fields=changed_fields,
        field_diffs=field_diffs,
        current_snapshot=current_snapshot,
        proposed_snapshot=proposed_snapshot,
      )
    if current.status == "deleted":
      return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
        item_id=current.registry_id,
        item_name=current.name,
        status=current.status,
        current_revision_id=current.current_revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome="skipped",
        message="Stitched governance registry is deleted; restore it before previewing edits.",
        current_snapshot=current_snapshot,
        proposed_snapshot=deepcopy(current_snapshot),
      )
    (
      resolved_default_policy_catalog,
      resolved_default_policy_template,
      _resolved_lane,
      _resolved_priority,
      _resolved_guidance,
    ) = self._resolve_provider_provenance_scheduler_narrative_governance_policy_layer(
      item_type="stitched_report_view",
      action="update",
      policy_catalog_id=(
        default_policy_catalog_id
        if isinstance(default_policy_catalog_id, str)
        else current.default_policy_catalog_id
      ),
      policy_template_id=(
        default_policy_template_id
        if isinstance(default_policy_template_id, str)
        else current.default_policy_template_id
      ),
    )
    proposed = replace(
      current,
      name=f"{name_prefix or ''}{current.name}{name_suffix or ''}",
      description=(
        f"{current.description} {description_append}".strip()
        if description_append is not None
        else current.description
      ),
      queue_view=self._build_provider_provenance_scheduler_stitched_report_governance_registry_bulk_queue_view(
        current.queue_view,
        queue_view_patch,
      ),
      default_policy_template_id=(
        resolved_default_policy_template.policy_template_id
        if resolved_default_policy_template is not None
        else None
      ),
      default_policy_template_name=(
        resolved_default_policy_template.name
        if resolved_default_policy_template is not None
        else None
      ),
      default_policy_catalog_id=(
        resolved_default_policy_catalog.catalog_id
        if resolved_default_policy_catalog is not None
        else None
      ),
      default_policy_catalog_name=(
        resolved_default_policy_catalog.name
        if resolved_default_policy_catalog is not None
        else None
      ),
    )
    proposed_snapshot = self._build_provider_provenance_scheduler_stitched_report_governance_registry_snapshot(
      proposed
    )
    changed_fields, field_diffs = self._build_provider_provenance_scheduler_narrative_field_diffs(
      current_snapshot,
      proposed_snapshot,
      (
        "name",
        "description",
        "queue_view",
        "default_policy_template_id",
        "default_policy_template_name",
        "default_policy_catalog_id",
        "default_policy_catalog_name",
      ),
    )
    if not changed_fields:
      return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
        item_id=current.registry_id,
        item_name=current.name,
        status=current.status,
        current_revision_id=current.current_revision_id,
        rollback_revision_id=current.current_revision_id,
        outcome="skipped",
        message="Stitched governance registry already matches the requested governance patch.",
        current_snapshot=current_snapshot,
        proposed_snapshot=deepcopy(current_snapshot),
      )
    return ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
      item_id=current.registry_id,
      item_name=current.name,
      status=current.status,
      current_revision_id=current.current_revision_id,
      rollback_revision_id=current.current_revision_id,
      outcome="changed",
      message="Stitched governance registry will be updated with the requested governance patch.",
      changed_fields=changed_fields,
      field_diffs=field_diffs,
      current_snapshot=current_snapshot,
      proposed_snapshot=proposed_snapshot,
    )

  def _find_latest_active_provider_provenance_scheduler_narrative_template_revision(
    self,
    template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord | None:
    for revision in reversed(
      self.list_provider_provenance_scheduler_narrative_template_revisions(template_id)
    ):
      if revision.status == "active":
        return revision
    return None

  def bulk_govern_provider_provenance_scheduler_narrative_templates(
    self,
    template_ids: Iterable[str],
    *,
    action: str,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    query_patch: dict[str, Any] | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeBulkGovernanceResult:
    normalized_action = action.strip().lower()
    if normalized_action not in {"delete", "restore", "update"}:
      raise ValueError("Unsupported scheduler narrative template bulk action.")
    normalized_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(template_ids)
    normalized_name_prefix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_prefix,
      preserve_outer_spacing=True,
    )
    normalized_name_suffix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_suffix,
      preserve_outer_spacing=True,
    )
    normalized_description_append = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      description_append
    )
    resolved_reason = (
      reason.strip()
      if isinstance(reason, str) and reason.strip()
      else (
        "scheduler_narrative_template_bulk_deleted"
        if normalized_action == "delete"
        else (
          "scheduler_narrative_template_bulk_restored"
          if normalized_action == "restore"
          else "scheduler_narrative_template_bulk_updated"
        )
      )
    )
    if (
      normalized_action == "update"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and not isinstance(query_patch, dict)
    ):
      raise ValueError("No scheduler narrative template bulk update fields were provided.")
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    for template_id in normalized_ids:
      try:
        current = self.get_provider_provenance_scheduler_narrative_template(template_id)
        if normalized_action == "delete":
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.template_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Template is already deleted.",
              )
            )
            continue
          updated = self.delete_provider_provenance_scheduler_narrative_template(
            template_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        elif normalized_action == "restore":
          if current.status != "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.template_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Template is already active.",
              )
            )
            continue
          revision = self._find_latest_active_provider_provenance_scheduler_narrative_template_revision(
            template_id
          )
          if revision is None:
            failed_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.template_id,
                item_name=current.name,
                outcome="failed",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="No active revision is available for restore.",
              )
            )
            continue
          updated = self.restore_provider_provenance_scheduler_narrative_template_revision(
            template_id,
            revision.revision_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        else:
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.template_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Template is deleted; restore it before applying bulk edits.",
              )
            )
            continue
          updated_name = (
            f"{normalized_name_prefix or ''}{current.name}{normalized_name_suffix or ''}"
          )
          updated_description = (
            f"{current.description} {normalized_description_append}".strip()
            if normalized_description_append is not None
            else current.description
          )
          updated_query = self._build_provider_provenance_scheduler_narrative_bulk_template_query(
            current.query,
            query_patch,
          )
          if (
            updated_name == current.name
            and updated_description == current.description
            and updated_query == current.query
          ):
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.template_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Template already matches the requested bulk edits.",
              )
            )
            continue
          updated = self.update_provider_provenance_scheduler_narrative_template(
            template_id,
            name=updated_name,
            description=updated_description,
            query=updated_query,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        applied_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=updated.template_id,
            item_name=updated.name,
            outcome="applied",
            status=updated.status,
            current_revision_id=updated.current_revision_id,
            message=(
              "Template deleted."
              if normalized_action == "delete"
              else (
                "Template restored from the latest active revision."
                if normalized_action == "restore"
                else "Template updated with the requested bulk governance patch."
              )
            ),
          )
        )
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=template_id,
            outcome="failed",
            message=str(exc),
          )
        )
    return ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type="template",
      action=normalized_action,
      reason=resolved_reason,
      requested_count=len(normalized_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )

  def create_provider_provenance_scheduler_narrative_registry_entry(
    self,
    *,
    name: str,
    description: str = "",
    query: dict[str, Any] | None = None,
    layout: dict[str, Any] | None = None,
    template_id: str | None = None,
    created_by_tab_id: str | None = None,
    created_by_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRecord:
    now = self._clock()
    normalized_template_id = (
      template_id.strip()
      if isinstance(template_id, str) and template_id.strip()
      else None
    )
    template_record = (
      self.get_provider_provenance_scheduler_narrative_template(normalized_template_id)
      if normalized_template_id is not None
      else None
    )
    if template_record is not None and template_record.status != "active":
      raise ValueError("Scheduler narrative registry entries can only link active templates.")
    resolved_query = (
      query
      if isinstance(query, dict) and query
      else template_record.query if template_record is not None
      else None
    )
    record = ProviderProvenanceSchedulerNarrativeRegistryRecord(
      registry_id=uuid4().hex[:12],
      name=self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler narrative registry name",
      ),
      description=description.strip() if isinstance(description, str) else "",
      query=self._normalize_provider_provenance_analytics_query_payload(resolved_query),
      layout=self._normalize_provider_provenance_scheduler_narrative_registry_layout_payload(layout),
      template_id=normalized_template_id,
      status="active",
      created_at=now,
      updated_at=now,
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
    return self._record_provider_provenance_scheduler_narrative_registry_revision(
      record=record,
      action="created",
      reason="scheduler_narrative_registry_created",
      recorded_at=now,
      actor_tab_id=record.created_by_tab_id,
      actor_tab_label=record.created_by_tab_label,
    )

  def update_provider_provenance_scheduler_narrative_registry_entry(
    self,
    registry_id: str,
    *,
    name: str | None = None,
    description: str | None = None,
    query: dict[str, Any] | None = None,
    layout: dict[str, Any] | None = None,
    template_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_registry_updated",
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRecord:
    current = self.get_provider_provenance_scheduler_narrative_registry_entry(registry_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler narrative registry entries must be restored from a revision before editing."
      )
    normalized_template_id = (
      template_id.strip() or None
      if isinstance(template_id, str)
      else current.template_id
    )
    template_record = (
      self.get_provider_provenance_scheduler_narrative_template(normalized_template_id)
      if normalized_template_id is not None
      else None
    )
    if template_record is not None and template_record.status != "active":
      raise ValueError("Scheduler narrative registry entries can only link active templates.")
    updated_name = (
      self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler narrative registry name",
      )
      if isinstance(name, str)
      else current.name
    )
    updated_description = (
      description.strip()
      if isinstance(description, str)
      else current.description
    )
    updated_query = (
      self._normalize_provider_provenance_analytics_query_payload(query)
      if isinstance(query, dict)
      else current.query
    )
    updated_layout = (
      self._normalize_provider_provenance_scheduler_narrative_registry_layout_payload(layout)
      if isinstance(layout, dict)
      else current.layout
    )
    if (
      updated_name == current.name
      and updated_description == current.description
      and updated_query == current.query
      and updated_layout == current.layout
      and normalized_template_id == current.template_id
    ):
      return current
    updated = replace(
      current,
      name=updated_name,
      description=updated_description,
      query=updated_query,
      layout=updated_layout,
      template_id=normalized_template_id,
      updated_at=self._clock(),
    )
    return self._record_provider_provenance_scheduler_narrative_registry_revision(
      record=updated,
      action="updated",
      reason=reason,
      recorded_at=updated.updated_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def delete_provider_provenance_scheduler_narrative_registry_entry(
    self,
    registry_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_registry_deleted",
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRecord:
    current = self.get_provider_provenance_scheduler_narrative_registry_entry(registry_id)
    if current.status == "deleted":
      return current
    deleted_at = self._clock()
    deleted = replace(
      current,
      status="deleted",
      updated_at=deleted_at,
      deleted_at=deleted_at,
      deleted_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      deleted_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )
    return self._record_provider_provenance_scheduler_narrative_registry_revision(
      record=deleted,
      action="deleted",
      reason=reason,
      recorded_at=deleted_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def list_provider_provenance_scheduler_narrative_registry_entries(
    self,
    *,
    template_id: str | None = None,
    created_by_tab_id: str | None = None,
    focus_scope: str | None = None,
    category: str | None = None,
    narrative_facet: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeRegistryRecord, ...]:
    normalized_template_id = (
      template_id.strip()
      if isinstance(template_id, str) and template_id.strip()
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
    normalized_category = self._normalize_provider_provenance_scheduler_alert_history_category(category)
    normalized_narrative_facet = self._normalize_provider_provenance_scheduler_alert_history_narrative_facet(
      narrative_facet
    )
    normalized_limit = max(1, min(limit, 200))
    filtered: list[ProviderProvenanceSchedulerNarrativeRegistryRecord] = []
    for record in self._list_provider_provenance_scheduler_narrative_registry_records():
      normalized_query = self._normalize_provider_provenance_analytics_query_payload(record.query)
      normalized_layout = self._normalize_provider_provenance_scheduler_narrative_registry_layout_payload(
        record.layout
      )
      if normalized_template_id is not None and record.template_id != normalized_template_id:
        continue
      if normalized_creator is not None and record.created_by_tab_id != normalized_creator:
        continue
      if normalized_focus_scope is not None and normalized_query["focus_scope"] != normalized_focus_scope:
        continue
      if (
        normalized_category is not None
        and normalized_query.get("scheduler_alert_category") != normalized_category
      ):
        continue
      if (
        normalized_narrative_facet is not None
        and normalized_query.get("scheduler_alert_narrative_facet") != normalized_narrative_facet
      ):
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.registry_id,
          record.name,
          record.description,
          record.status,
          record.template_id,
          record.created_by_tab_id,
          record.created_by_tab_label,
          normalized_query.get("focus_key"),
          normalized_query.get("symbol"),
          normalized_query.get("timeframe"),
          normalized_query.get("scheduler_alert_category"),
          normalized_query.get("scheduler_alert_status"),
          normalized_query.get("scheduler_alert_narrative_facet"),
          normalized_query.get("search"),
          normalized_layout.get("highlight_panel"),
        ),
        search=search,
      ):
        continue
      filtered.append(replace(record, query=normalized_query, layout=normalized_layout))
    return tuple(filtered[:normalized_limit])

  def get_provider_provenance_scheduler_narrative_registry_entry(
    self,
    registry_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRecord:
    normalized_registry_id = registry_id.strip()
    if not normalized_registry_id:
      raise LookupError("Provider provenance scheduler narrative registry entry not found.")
    record = self._load_provider_provenance_scheduler_narrative_registry_record(normalized_registry_id)
    if record is None:
      raise LookupError("Provider provenance scheduler narrative registry entry not found.")
    return replace(
      record,
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
      query=self._normalize_provider_provenance_analytics_query_payload(record.query),
      layout=self._normalize_provider_provenance_scheduler_narrative_registry_layout_payload(
        record.layout
      ),
    )

  def list_provider_provenance_scheduler_narrative_registry_revisions(
    self,
    registry_id: str,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord, ...]:
    current = self.get_provider_provenance_scheduler_narrative_registry_entry(registry_id)
    revisions = [
      replace(
        revision,
        status=self._normalize_provider_provenance_scheduler_narrative_record_status(revision.status),
        query=self._normalize_provider_provenance_analytics_query_payload(revision.query),
        layout=self._normalize_provider_provenance_scheduler_narrative_registry_layout_payload(
          revision.layout
        ),
      )
      for revision in self._list_provider_provenance_scheduler_narrative_registry_revision_records()
      if revision.registry_id == current.registry_id
    ]
    return tuple(revisions)

  def restore_provider_provenance_scheduler_narrative_registry_revision(
    self,
    registry_id: str,
    revision_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_registry_revision_restored",
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRecord:
    current = self.get_provider_provenance_scheduler_narrative_registry_entry(registry_id)
    revision = self._load_provider_provenance_scheduler_narrative_registry_revision_record(
      revision_id.strip()
    )
    if revision is None or revision.registry_id != current.registry_id:
      raise LookupError("Provider provenance scheduler narrative registry revision not found.")
    template_record = (
      self.get_provider_provenance_scheduler_narrative_template(revision.template_id)
      if revision.template_id is not None
      else None
    )
    if template_record is not None and template_record.status != "active":
      raise ValueError("Scheduler narrative registry entries can only link active templates.")
    restored_at = self._clock()
    restored = replace(
      current,
      name=revision.name,
      description=revision.description,
      query=self._normalize_provider_provenance_analytics_query_payload(revision.query),
      layout=self._normalize_provider_provenance_scheduler_narrative_registry_layout_payload(
        revision.layout
      ),
      template_id=revision.template_id,
      status="active",
      updated_at=restored_at,
      deleted_at=None,
      deleted_by_tab_id=None,
      deleted_by_tab_label=None,
    )
    return self._record_provider_provenance_scheduler_narrative_registry_revision(
      record=restored,
      action="restored",
      reason=reason,
      recorded_at=restored_at,
      source_revision_id=revision.revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def _find_latest_active_provider_provenance_scheduler_narrative_registry_revision(
    self,
    registry_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord | None:
    for revision in reversed(
      self.list_provider_provenance_scheduler_narrative_registry_revisions(registry_id)
    ):
      if revision.status == "active":
        return revision
    return None

  def bulk_govern_provider_provenance_scheduler_narrative_registry_entries(
    self,
    registry_ids: Iterable[str],
    *,
    action: str,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    query_patch: dict[str, Any] | None = None,
    layout_patch: dict[str, Any] | None = None,
    template_id: str | None = None,
    clear_template_link: bool = False,
  ) -> ProviderProvenanceSchedulerNarrativeBulkGovernanceResult:
    normalized_action = action.strip().lower()
    if normalized_action not in {"delete", "restore", "update"}:
      raise ValueError("Unsupported scheduler narrative registry bulk action.")
    normalized_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(registry_ids)
    normalized_name_prefix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_prefix,
      preserve_outer_spacing=True,
    )
    normalized_name_suffix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_suffix,
      preserve_outer_spacing=True,
    )
    normalized_description_append = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      description_append
    )
    resolved_reason = (
      reason.strip()
      if isinstance(reason, str) and reason.strip()
      else (
        "scheduler_narrative_registry_bulk_deleted"
        if normalized_action == "delete"
        else (
          "scheduler_narrative_registry_bulk_restored"
          if normalized_action == "restore"
          else "scheduler_narrative_registry_bulk_updated"
        )
      )
    )
    if (
      normalized_action == "update"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and not isinstance(query_patch, dict)
      and not isinstance(layout_patch, dict)
      and template_id is None
      and not clear_template_link
    ):
      raise ValueError("No scheduler narrative registry bulk update fields were provided.")
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    for registry_id in normalized_ids:
      try:
        current = self.get_provider_provenance_scheduler_narrative_registry_entry(registry_id)
        if normalized_action == "delete":
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.registry_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Registry is already deleted.",
              )
            )
            continue
          updated = self.delete_provider_provenance_scheduler_narrative_registry_entry(
            registry_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        elif normalized_action == "restore":
          if current.status != "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.registry_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Registry is already active.",
              )
            )
            continue
          revision = self._find_latest_active_provider_provenance_scheduler_narrative_registry_revision(
            registry_id
          )
          if revision is None:
            failed_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.registry_id,
                item_name=current.name,
                outcome="failed",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="No active revision is available for restore.",
              )
            )
            continue
          updated = self.restore_provider_provenance_scheduler_narrative_registry_revision(
            registry_id,
            revision.revision_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        else:
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.registry_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Registry is deleted; restore it before applying bulk edits.",
              )
            )
            continue
          updated_name = (
            f"{normalized_name_prefix or ''}{current.name}{normalized_name_suffix or ''}"
          )
          updated_description = (
            f"{current.description} {normalized_description_append}".strip()
            if normalized_description_append is not None
            else current.description
          )
          updated_query = self._build_provider_provenance_scheduler_narrative_bulk_template_query(
            current.query,
            query_patch,
          )
          updated_layout = self._build_provider_provenance_scheduler_narrative_bulk_registry_layout(
            current.layout,
            layout_patch,
          )
          updated_template_id = (
            ""
            if clear_template_link
            else (
              template_id.strip()
              if isinstance(template_id, str) and template_id.strip()
              else current.template_id
            )
          )
          if (
            updated_name == current.name
            and updated_description == current.description
            and updated_query == current.query
            and updated_layout == current.layout
            and updated_template_id == current.template_id
          ):
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.registry_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Registry already matches the requested bulk edits.",
              )
            )
            continue
          updated = self.update_provider_provenance_scheduler_narrative_registry_entry(
            registry_id,
            name=updated_name,
            description=updated_description,
            query=updated_query,
            layout=updated_layout,
            template_id=updated_template_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        applied_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=updated.registry_id,
            item_name=updated.name,
            outcome="applied",
            status=updated.status,
            current_revision_id=updated.current_revision_id,
            message=(
              "Registry deleted."
              if normalized_action == "delete"
              else (
                "Registry restored from the latest active revision."
                if normalized_action == "restore"
                else "Registry updated with the requested bulk governance patch."
              )
            ),
          )
        )
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=registry_id,
            outcome="failed",
            message=str(exc),
          )
        )
    return ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type="registry",
      action=normalized_action,
      reason=resolved_reason,
      requested_count=len(normalized_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )

  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_governance_item_type(
    item_type: str,
  ) -> str:
    normalized = item_type.strip().lower()
    if normalized not in {
      "template",
      "registry",
      "stitched_report_view",
      "stitched_report_governance_registry",
    }:
      raise ValueError("Unsupported scheduler narrative governance item type.")
    return normalized

  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_governance_item_type_scope(
    item_type_scope: str | None,
  ) -> str:
    normalized = (
      item_type_scope.strip().lower()
      if isinstance(item_type_scope, str) and item_type_scope.strip()
      else "any"
    )
    if normalized not in {
      "any",
      "template",
      "registry",
      "stitched_report_view",
      "stitched_report_governance_registry",
    }:
      raise ValueError("Unsupported scheduler narrative governance policy item-type scope.")
    return normalized

  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_governance_action_scope(
    action_scope: str | None,
  ) -> str:
    normalized = (
      action_scope.strip().lower()
      if isinstance(action_scope, str) and action_scope.strip()
      else "any"
    )
    if normalized not in {"any", "delete", "restore", "update"}:
      raise ValueError("Unsupported scheduler narrative governance policy action scope.")
    return normalized

  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_governance_approval_lane(
    approval_lane: str | None,
  ) -> str:
    raw = (
      approval_lane.strip().lower()
      if isinstance(approval_lane, str) and approval_lane.strip()
      else "general"
    )
    normalized = re.sub(r"[^a-z0-9]+", "_", raw).strip("_")
    return normalized or "general"

  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_governance_approval_priority(
    approval_priority: str | None,
  ) -> str:
    normalized = (
      approval_priority.strip().lower()
      if isinstance(approval_priority, str) and approval_priority.strip()
      else "normal"
    )
    if normalized not in {"low", "normal", "high", "critical"}:
      raise ValueError("Unsupported scheduler narrative governance approval priority.")
    return normalized

  @staticmethod
  def _build_provider_provenance_scheduler_narrative_governance_queue_state(
    status: str,
  ) -> str:
    normalized = status.strip().lower()
    if normalized == "previewed":
      return "pending_approval"
    if normalized == "approved":
      return "ready_to_apply"
    return "completed"

  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_governance_queue_state_filter(
    queue_state: str | None,
  ) -> str:
    normalized = (
      queue_state.strip().lower()
      if isinstance(queue_state, str) and queue_state.strip()
      else ""
    )
    if normalized not in {"pending_approval", "ready_to_apply", "completed"}:
      raise ValueError("Unsupported scheduler narrative governance queue state.")
    return normalized

  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_governance_plan_sort(
    sort: str | None,
  ) -> str:
    normalized = (
      sort.strip().lower()
      if isinstance(sort, str) and sort.strip()
      else "queue_priority"
    )
    if normalized not in {
      "queue_priority",
      "updated_desc",
      "updated_asc",
      "created_desc",
      "created_asc",
      "source_template_asc",
      "source_template_desc",
    }:
      raise ValueError("Unsupported scheduler narrative governance plan sort.")
    return normalized

  @staticmethod
  def _build_provider_provenance_scheduler_narrative_governance_priority_rank(
    approval_priority: str,
  ) -> int:
    normalized = approval_priority.strip().lower()
    if normalized == "critical":
      return 3
    if normalized == "high":
      return 2
    if normalized == "normal":
      return 1
    return 0

  @classmethod
  def _normalize_provider_provenance_scheduler_narrative_governance_queue_view_payload(
    cls,
    payload: dict[str, Any] | None,
  ) -> dict[str, Any] | None:
    queue_view = deepcopy(payload) if isinstance(payload, dict) else {}
    if not queue_view:
      return None
    normalized: dict[str, Any] = {}
    queue_state = queue_view.get("queue_state")
    if isinstance(queue_state, str) and queue_state.strip():
      normalized["queue_state"] = cls._normalize_provider_provenance_scheduler_narrative_governance_queue_state_filter(
        queue_state
      )
    item_type = queue_view.get("item_type")
    if isinstance(item_type, str) and item_type.strip():
      normalized["item_type"] = cls._normalize_provider_provenance_scheduler_narrative_governance_item_type(
        item_type
      )
    approval_lane = queue_view.get("approval_lane")
    if isinstance(approval_lane, str) and approval_lane.strip():
      normalized["approval_lane"] = cls._normalize_provider_provenance_scheduler_narrative_governance_approval_lane(
        approval_lane
      )
    approval_priority = queue_view.get("approval_priority")
    if isinstance(approval_priority, str) and approval_priority.strip():
      normalized["approval_priority"] = cls._normalize_provider_provenance_scheduler_narrative_governance_approval_priority(
        approval_priority
      )
    for key in ("policy_template_id", "policy_catalog_id", "source_hierarchy_step_template_id"):
      value = queue_view.get(key)
      if isinstance(value, str):
        normalized[key] = value.strip() if value.strip() else ""
    source_hierarchy_step_template_name = queue_view.get("source_hierarchy_step_template_name")
    if (
      isinstance(source_hierarchy_step_template_name, str)
      and source_hierarchy_step_template_name.strip()
    ):
      normalized["source_hierarchy_step_template_name"] = (
        source_hierarchy_step_template_name.strip()
      )
    search = queue_view.get("search")
    if isinstance(search, str) and search.strip():
      normalized["search"] = search.strip()
    normalized_sort = cls._normalize_provider_provenance_scheduler_narrative_governance_plan_sort(
      queue_view.get("sort") if isinstance(queue_view.get("sort"), str) else None
    )
    if normalized or normalized_sort != "queue_priority":
      normalized["sort"] = normalized_sort
    return normalized or None

  def _normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
    self,
    hierarchy_steps: Iterable[dict[str, Any]] | None,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep, ...]:
    if hierarchy_steps is None:
      return ()
    resolved_steps: list[ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep] = []
    for raw_step in hierarchy_steps:
      if not isinstance(raw_step, dict):
        raise ValueError("Scheduler governance hierarchy steps must be objects.")
      item_type = self._normalize_provider_provenance_scheduler_narrative_governance_item_type(
        str(raw_step.get("item_type", ""))
      )
      step_id = (
        raw_step["step_id"].strip()
        if isinstance(raw_step.get("step_id"), str) and raw_step["step_id"].strip()
        else f"hstep_{uuid4().hex[:12]}"
      )
      source_template_id = (
        raw_step["source_template_id"].strip()
        if isinstance(raw_step.get("source_template_id"), str) and raw_step["source_template_id"].strip()
        else None
      )
      source_template_name = (
        raw_step["source_template_name"].strip()
        if isinstance(raw_step.get("source_template_name"), str) and raw_step["source_template_name"].strip()
        else None
      )
      action = str(raw_step.get("action", "update")).strip().lower() or "update"
      if action != "update":
        raise ValueError("Scheduler governance policy catalog hierarchies currently support update steps only.")
      item_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(
        raw_step.get("item_ids", ())
      )
      if not item_ids:
        raise ValueError("Each scheduler governance hierarchy step must target at least one item.")
      item_names: list[str] = []
      for item_id in item_ids:
        if item_type == "template":
          item_names.append(self.get_provider_provenance_scheduler_narrative_template(item_id).name)
        else:
          item_names.append(self.get_provider_provenance_scheduler_narrative_registry_entry(item_id).name)
      name_prefix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
        raw_step.get("name_prefix"),
        preserve_outer_spacing=True,
      )
      name_suffix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
        raw_step.get("name_suffix"),
        preserve_outer_spacing=True,
      )
      description_append = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
        raw_step.get("description_append")
      )
      query_patch = (
        deepcopy(raw_step["query_patch"])
        if isinstance(raw_step.get("query_patch"), dict) and raw_step.get("query_patch")
        else {}
      )
      layout_patch = (
        deepcopy(raw_step["layout_patch"])
        if item_type == "registry"
        and isinstance(raw_step.get("layout_patch"), dict)
        and raw_step.get("layout_patch")
        else {}
      )
      template_id = (
        raw_step["template_id"].strip()
        if isinstance(raw_step.get("template_id"), str) and raw_step["template_id"].strip()
        else None
      )
      clear_template_link = bool(raw_step.get("clear_template_link", False))
      if template_id is not None:
        self.get_provider_provenance_scheduler_narrative_template(template_id)
      if item_type == "template":
        if layout_patch:
          raise ValueError("Template hierarchy steps do not support layout patches.")
        if template_id is not None or clear_template_link:
          raise ValueError("Template hierarchy steps do not support registry template link changes.")
        if (
          name_prefix is None
          and name_suffix is None
          and description_append is None
          and not query_patch
        ):
          raise ValueError("Template hierarchy steps must capture at least one update patch.")
      else:
        if (
          name_prefix is None
          and name_suffix is None
          and description_append is None
          and not query_patch
          and not layout_patch
          and template_id is None
          and not clear_template_link
        ):
          raise ValueError("Registry hierarchy steps must capture at least one update patch.")
      resolved_steps.append(
        ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep(
          item_type=item_type,
          step_id=step_id,
          source_template_id=source_template_id,
          source_template_name=source_template_name,
          action=action,
          item_ids=item_ids,
          item_names=tuple(item_names),
          name_prefix=name_prefix,
          name_suffix=name_suffix,
          description_append=description_append,
          query_patch=query_patch,
          layout_patch=layout_patch,
          template_id=template_id,
          clear_template_link=clear_template_link,
        )
      )
    return self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_steps(
      resolved_steps
    )

  @staticmethod
  def _build_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_fingerprint(
    step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep,
    *,
    index: int,
  ) -> str:
    return hashlib.sha1(
      json.dumps(
        {
          "index": index,
          "item_type": step.item_type,
          "action": step.action,
          "source_template_id": step.source_template_id,
          "source_template_name": step.source_template_name,
          "item_ids": list(step.item_ids),
          "item_names": list(step.item_names),
          "name_prefix": step.name_prefix,
          "name_suffix": step.name_suffix,
          "description_append": step.description_append,
          "query_patch": step.query_patch,
          "layout_patch": step.layout_patch,
          "template_id": step.template_id,
          "clear_template_link": step.clear_template_link,
        },
        sort_keys=True,
        separators=(",", ":"),
      ).encode("utf-8")
    ).hexdigest()[:12]

  def _materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_steps(
    self,
    hierarchy_steps: Iterable[ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep],
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep, ...]:
    seen_step_ids: set[str] = set()
    resolved_steps: list[ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep] = []
    for index, step in enumerate(hierarchy_steps, start=1):
      base_step_id = (
        step.step_id.strip()
        if isinstance(step.step_id, str) and step.step_id.strip()
        else f"hstep_{self._build_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_fingerprint(step, index=index)}"
      )
      step_id = base_step_id
      duplicate_index = 2
      while step_id in seen_step_ids:
        step_id = f"{base_step_id}_{duplicate_index}"
        duplicate_index += 1
      seen_step_ids.add(step_id)
      resolved_steps.append(replace(step, step_id=step_id))
    return tuple(resolved_steps)

  def _materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    hierarchy_steps = (
      self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_steps(
        record.hierarchy_steps
      )
    )
    if hierarchy_steps == record.hierarchy_steps:
      return record
    return replace(record, hierarchy_steps=hierarchy_steps)

  def _materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord:
    hierarchy_steps = (
      self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_steps(
        record.hierarchy_steps
      )
    )
    if hierarchy_steps == record.hierarchy_steps:
      return record
    return replace(record, hierarchy_steps=hierarchy_steps)

  def _materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record(
    self,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord:
    hierarchy_steps = (
      self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_steps(
        record.hierarchy_steps
      )
    )
    if hierarchy_steps == record.hierarchy_steps:
      return record
    return replace(record, hierarchy_steps=hierarchy_steps)

  def _get_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step(
    self,
    current: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
    step_id: str,
  ) -> tuple[int, ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep]:
    normalized_step_id = step_id.strip()
    if not normalized_step_id:
      raise LookupError("Provider provenance scheduler narrative governance policy catalog hierarchy step not found.")
    materialized = self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
      current
    )
    for index, step in enumerate(materialized.hierarchy_steps):
      if step.step_id == normalized_step_id:
        return index, step
    raise LookupError("Provider provenance scheduler narrative governance policy catalog hierarchy step not found.")

  @staticmethod
  def _summarize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
    steps: tuple[ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep, ...],
  ) -> str:
    if not steps:
      return "No reusable hierarchy steps are captured."
    parts = [
      f"{step.item_type} {len(step.item_ids)}"
      for step in steps
    ]
    return f"{len(steps)} hierarchy step(s): " + ", ".join(parts)

  @staticmethod
  def format_provider_provenance_scheduler_narrative_governance_hierarchy_step_summary(
    step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep,
  ) -> str:
    item_summary = ", ".join(step.item_names or step.item_ids[:3]) if (step.item_names or step.item_ids) else "all"
    affixes: list[str] = []
    if step.name_prefix:
      affixes.append(f"prefix={step.name_prefix}")
    if step.name_suffix:
      affixes.append(f"suffix={step.name_suffix}")
    if step.description_append:
      affixes.append("description")
    if step.template_id:
      affixes.append(f"template={step.template_id}")
    if step.clear_template_link:
      affixes.append("clear-link")
    affix_summary = f" ({', '.join(affixes)})" if affixes else ""
    return (
      f"{step.item_type} {step.action} · {len(step.item_ids)} target(s)"
      f" [{item_summary}]{affix_summary}"
    )

  def create_provider_provenance_scheduler_narrative_governance_policy_template(
    self,
    *,
    name: str,
    description: str = "",
    item_type_scope: str | None = None,
    action_scope: str | None = None,
    approval_lane: str | None = None,
    approval_priority: str | None = None,
    guidance: str | None = None,
    created_by_tab_id: str | None = None,
    created_by_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    now = self._clock()
    record = ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord(
      policy_template_id=uuid4().hex[:12],
      name=self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler narrative governance policy template name",
      ),
      description=description.strip() if isinstance(description, str) else "",
      item_type_scope=self._normalize_provider_provenance_scheduler_narrative_governance_item_type_scope(
        item_type_scope
      ),
      action_scope=self._normalize_provider_provenance_scheduler_narrative_governance_action_scope(
        action_scope
      ),
      approval_lane=self._normalize_provider_provenance_scheduler_narrative_governance_approval_lane(
        approval_lane
      ),
      approval_priority=self._normalize_provider_provenance_scheduler_narrative_governance_approval_priority(
        approval_priority
      ),
      guidance=guidance.strip() if isinstance(guidance, str) and guidance.strip() else None,
      status="active",
      created_at=now,
      updated_at=now,
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
    return self._record_provider_provenance_scheduler_narrative_governance_policy_template_revision(
      record=record,
      action="created",
      reason="scheduler_narrative_governance_policy_template_created",
      recorded_at=now,
      actor_tab_id=record.created_by_tab_id,
      actor_tab_label=record.created_by_tab_label,
    )

  def list_provider_provenance_scheduler_narrative_governance_policy_templates(
    self,
    *,
    item_type_scope: str | None = None,
    action_scope: str | None = None,
    approval_lane: str | None = None,
    approval_priority: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord, ...]:
    normalized_item_type_scope = (
      self._normalize_provider_provenance_scheduler_narrative_governance_item_type_scope(item_type_scope)
      if isinstance(item_type_scope, str) and item_type_scope.strip()
      else None
    )
    normalized_action_scope = (
      self._normalize_provider_provenance_scheduler_narrative_governance_action_scope(action_scope)
      if isinstance(action_scope, str) and action_scope.strip()
      else None
    )
    normalized_approval_lane = (
      self._normalize_provider_provenance_scheduler_narrative_governance_approval_lane(approval_lane)
      if isinstance(approval_lane, str) and approval_lane.strip()
      else None
    )
    normalized_approval_priority = (
      self._normalize_provider_provenance_scheduler_narrative_governance_approval_priority(approval_priority)
      if isinstance(approval_priority, str) and approval_priority.strip()
      else None
    )
    normalized_limit = max(1, min(limit, 200))
    filtered: list[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord] = []
    for record in self._list_provider_provenance_scheduler_narrative_governance_policy_template_records():
      if normalized_item_type_scope is not None and record.item_type_scope != normalized_item_type_scope:
        continue
      if normalized_action_scope is not None and record.action_scope != normalized_action_scope:
        continue
      if normalized_approval_lane is not None and record.approval_lane != normalized_approval_lane:
        continue
      if normalized_approval_priority is not None and record.approval_priority != normalized_approval_priority:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.policy_template_id,
          record.name,
          record.description,
          record.status,
          record.item_type_scope,
          record.action_scope,
          record.approval_lane,
          record.approval_priority,
          record.guidance,
          record.created_by_tab_id,
          record.created_by_tab_label,
        ),
        search=search,
      ):
        continue
      filtered.append(
        replace(
          record,
          status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
        )
      )
    return tuple(filtered[:normalized_limit])

  def get_provider_provenance_scheduler_narrative_governance_policy_template(
    self,
    policy_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    normalized_policy_template_id = policy_template_id.strip()
    if not normalized_policy_template_id:
      raise LookupError("Provider provenance scheduler narrative governance policy template not found.")
    record = self._load_provider_provenance_scheduler_narrative_governance_policy_template_record(
      normalized_policy_template_id
    )
    if record is None:
      raise LookupError("Provider provenance scheduler narrative governance policy template not found.")
    return replace(
      record,
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
    )

  def update_provider_provenance_scheduler_narrative_governance_policy_template(
    self,
    policy_template_id: str,
    *,
    name: str | None = None,
    description: str | None = None,
    item_type_scope: str | None = None,
    action_scope: str | None = None,
    approval_lane: str | None = None,
    approval_priority: str | None = None,
    guidance: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_template_updated",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_template(policy_template_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler governance policy templates must be restored from a revision before editing."
      )
    updated_name = (
      self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler narrative governance policy template name",
      )
      if isinstance(name, str)
      else current.name
    )
    updated_description = description.strip() if isinstance(description, str) else current.description
    updated_item_type_scope = (
      self._normalize_provider_provenance_scheduler_narrative_governance_item_type_scope(item_type_scope)
      if isinstance(item_type_scope, str)
      else current.item_type_scope
    )
    updated_action_scope = (
      self._normalize_provider_provenance_scheduler_narrative_governance_action_scope(action_scope)
      if isinstance(action_scope, str)
      else current.action_scope
    )
    updated_approval_lane = (
      self._normalize_provider_provenance_scheduler_narrative_governance_approval_lane(approval_lane)
      if isinstance(approval_lane, str)
      else current.approval_lane
    )
    updated_approval_priority = (
      self._normalize_provider_provenance_scheduler_narrative_governance_approval_priority(approval_priority)
      if isinstance(approval_priority, str)
      else current.approval_priority
    )
    updated_guidance = (
      guidance.strip() if isinstance(guidance, str) and guidance.strip() else None
      if guidance is not None
      else current.guidance
    )
    if (
      updated_name == current.name
      and updated_description == current.description
      and updated_item_type_scope == current.item_type_scope
      and updated_action_scope == current.action_scope
      and updated_approval_lane == current.approval_lane
      and updated_approval_priority == current.approval_priority
      and updated_guidance == current.guidance
    ):
      return current
    updated = replace(
      current,
      name=updated_name,
      description=updated_description,
      item_type_scope=updated_item_type_scope,
      action_scope=updated_action_scope,
      approval_lane=updated_approval_lane,
      approval_priority=updated_approval_priority,
      guidance=updated_guidance,
      updated_at=self._clock(),
    )
    return self._record_provider_provenance_scheduler_narrative_governance_policy_template_revision(
      record=updated,
      action="updated",
      reason=reason,
      recorded_at=updated.updated_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def delete_provider_provenance_scheduler_narrative_governance_policy_template(
    self,
    policy_template_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_template_deleted",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_template(policy_template_id)
    if current.status == "deleted":
      return current
    deleted_at = self._clock()
    deleted = replace(
      current,
      status="deleted",
      updated_at=deleted_at,
      deleted_at=deleted_at,
      deleted_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      deleted_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )
    return self._record_provider_provenance_scheduler_narrative_governance_policy_template_revision(
      record=deleted,
      action="deleted",
      reason=reason,
      recorded_at=deleted_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def list_provider_provenance_scheduler_narrative_governance_policy_template_revisions(
    self,
    policy_template_id: str,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord, ...]:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_template(policy_template_id)
    revisions = [
      replace(
        revision,
        status=self._normalize_provider_provenance_scheduler_narrative_record_status(revision.status),
      )
      for revision in self._list_provider_provenance_scheduler_narrative_governance_policy_template_revision_records()
      if revision.policy_template_id == current.policy_template_id
    ]
    return tuple(revisions)

  def restore_provider_provenance_scheduler_narrative_governance_policy_template_revision(
    self,
    policy_template_id: str,
    revision_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_template_revision_restored",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_template(policy_template_id)
    revision = self._load_provider_provenance_scheduler_narrative_governance_policy_template_revision_record(
      revision_id.strip()
    )
    if revision is None or revision.policy_template_id != current.policy_template_id:
      raise LookupError("Provider provenance scheduler narrative governance policy template revision not found.")
    restored_at = self._clock()
    restored = replace(
      current,
      name=revision.name,
      description=revision.description,
      item_type_scope=revision.item_type_scope,
      action_scope=revision.action_scope,
      approval_lane=revision.approval_lane,
      approval_priority=revision.approval_priority,
      guidance=revision.guidance,
      status="active",
      updated_at=restored_at,
      deleted_at=None,
      deleted_by_tab_id=None,
      deleted_by_tab_label=None,
    )
    return self._record_provider_provenance_scheduler_narrative_governance_policy_template_revision(
      record=restored,
      action="restored",
      reason=reason,
      recorded_at=restored_at,
      source_revision_id=revision.revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def list_provider_provenance_scheduler_narrative_governance_policy_template_audits(
    self,
    *,
    policy_template_id: str | None = None,
    action: str | None = None,
    actor_tab_id: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord, ...]:
    normalized_policy_template_id = (
      policy_template_id.strip()
      if isinstance(policy_template_id, str) and policy_template_id.strip()
      else None
    )
    normalized_action = action.strip().lower() if isinstance(action, str) and action.strip() else None
    normalized_actor_tab_id = (
      actor_tab_id.strip()
      if isinstance(actor_tab_id, str) and actor_tab_id.strip()
      else None
    )
    normalized_limit = max(1, min(limit, 200))
    filtered: list[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord] = []
    for record in self._list_provider_provenance_scheduler_narrative_governance_policy_template_audit_records():
      if normalized_policy_template_id is not None and record.policy_template_id != normalized_policy_template_id:
        continue
      if normalized_action is not None and record.action != normalized_action:
        continue
      if normalized_actor_tab_id is not None and record.actor_tab_id != normalized_actor_tab_id:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.audit_id,
          record.policy_template_id,
          record.action,
          record.reason,
          record.detail,
          record.revision_id,
          record.source_revision_id,
          record.name,
          record.status,
          record.item_type_scope,
          record.action_scope,
          record.approval_lane,
          record.approval_priority,
          record.guidance,
          record.actor_tab_id,
          record.actor_tab_label,
        ),
        search=search,
      ):
        continue
      filtered.append(
        replace(
          record,
          status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
        )
      )
    return tuple(filtered[:normalized_limit])

  def _resolve_provider_provenance_scheduler_narrative_governance_policy_catalog_templates(
    self,
    *,
    policy_template_ids: Iterable[str],
    default_policy_template_id: str | None = None,
  ) -> tuple[
    tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord, ...],
    ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
  ]:
    normalized_policy_template_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(
      policy_template_ids
    )
    if not normalized_policy_template_ids:
      raise ValueError("Select at least one governance policy template for the catalog.")
    resolved_templates = tuple(
      self.get_provider_provenance_scheduler_narrative_governance_policy_template(template_id)
      for template_id in normalized_policy_template_ids
    )
    if any(template.status != "active" for template in resolved_templates):
      raise ValueError("Governance policy catalog entries must reference active policy templates.")
    resolved_default_policy_template_id = (
      default_policy_template_id.strip()
      if isinstance(default_policy_template_id, str) and default_policy_template_id.strip()
      else resolved_templates[0].policy_template_id
    )
    default_template = next(
      (
        template
        for template in resolved_templates
        if template.policy_template_id == resolved_default_policy_template_id
      ),
      None,
    )
    if default_template is None:
      raise ValueError("Default governance policy template must be one of the linked templates.")
    return resolved_templates, default_template

  def create_provider_provenance_scheduler_narrative_governance_policy_catalog(
    self,
    *,
    name: str,
    description: str = "",
    policy_template_ids: Iterable[str],
    default_policy_template_id: str | None = None,
    created_by_tab_id: str | None = None,
    created_by_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    normalized_name = self._normalize_provider_provenance_workspace_name(
      name,
      field_name="scheduler narrative governance policy catalog name",
    )
    normalized_description = description.strip() if isinstance(description, str) else ""
    resolved_templates, default_template = self._resolve_provider_provenance_scheduler_narrative_governance_policy_catalog_templates(
      policy_template_ids=policy_template_ids,
      default_policy_template_id=default_policy_template_id,
    )
    now = self._clock()
    return self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
      record=ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord(
        catalog_id=uuid4().hex[:12],
        name=normalized_name,
        description=normalized_description,
        policy_template_ids=tuple(template.policy_template_id for template in resolved_templates),
        policy_template_names=tuple(template.name for template in resolved_templates),
        default_policy_template_id=default_template.policy_template_id,
        default_policy_template_name=default_template.name,
        item_type_scope=default_template.item_type_scope,
        action_scope=default_template.action_scope,
        approval_lane=default_template.approval_lane,
        approval_priority=default_template.approval_priority,
        guidance=default_template.guidance,
        hierarchy_steps=(),
        status="active",
        created_at=now,
        updated_at=now,
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
      ),
      action="created",
      reason="scheduler_narrative_governance_policy_catalog_created",
      recorded_at=now,
      actor_tab_id=created_by_tab_id,
      actor_tab_label=created_by_tab_label,
    )

  def list_provider_provenance_scheduler_narrative_governance_policy_catalogs(
    self,
    *,
    item_type_scope: str | None = None,
    search: str | None = None,
    limit: int = 20,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord, ...]:
    normalized_item_type_scope = (
      self._normalize_provider_provenance_scheduler_narrative_governance_item_type_scope(item_type_scope)
      if isinstance(item_type_scope, str) and item_type_scope.strip()
      else None
    )
    normalized_limit = max(1, min(limit, 100))
    filtered: list[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord] = []
    for raw_record in self._list_provider_provenance_scheduler_narrative_governance_policy_catalog_records():
      record = self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
        raw_record
      )
      if normalized_item_type_scope is not None and record.item_type_scope != normalized_item_type_scope:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.catalog_id,
          record.name,
          record.description,
          record.default_policy_template_id,
          record.default_policy_template_name,
          record.status,
          record.item_type_scope,
          record.action_scope,
          record.approval_lane,
          record.approval_priority,
          record.guidance,
          record.created_by_tab_id,
          record.created_by_tab_label,
          *record.policy_template_ids,
          *record.policy_template_names,
          *tuple(step.step_id for step in record.hierarchy_steps if isinstance(step.step_id, str)),
          *tuple(item_id for step in record.hierarchy_steps for item_id in step.item_ids),
          *tuple(item_name for step in record.hierarchy_steps for item_name in step.item_names),
        ),
        search=search,
      ):
        continue
      filtered.append(
        replace(
          record,
          status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
        )
      )
    return tuple(filtered[:normalized_limit])

  def get_provider_provenance_scheduler_narrative_governance_policy_catalog(
    self,
    catalog_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    normalized_catalog_id = catalog_id.strip()
    if not normalized_catalog_id:
      raise LookupError("Provider provenance scheduler narrative governance policy catalog not found.")
    record = self._load_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
      normalized_catalog_id
    )
    if record is None:
      raise LookupError("Provider provenance scheduler narrative governance policy catalog not found.")
    return replace(
      self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(record),
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
    )

  def update_provider_provenance_scheduler_narrative_governance_policy_catalog(
    self,
    catalog_id: str,
    *,
    name: str | None = None,
    description: str | None = None,
    policy_template_ids: Iterable[str] | None = None,
    default_policy_template_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_catalog_updated",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler governance policy catalogs must be restored from a revision before editing."
      )
    updated_name = (
      self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler narrative governance policy catalog name",
      )
      if isinstance(name, str)
      else current.name
    )
    updated_description = description.strip() if isinstance(description, str) else current.description
    resolved_templates, default_template = (
      self._resolve_provider_provenance_scheduler_narrative_governance_policy_catalog_templates(
        policy_template_ids=(
          policy_template_ids if policy_template_ids is not None else current.policy_template_ids
        ),
        default_policy_template_id=(
          default_policy_template_id
          if default_policy_template_id is not None
          else current.default_policy_template_id
        ),
      )
    )
    updated_policy_template_ids = tuple(template.policy_template_id for template in resolved_templates)
    updated_policy_template_names = tuple(template.name for template in resolved_templates)
    if (
      updated_name == current.name
      and updated_description == current.description
      and updated_policy_template_ids == current.policy_template_ids
      and updated_policy_template_names == current.policy_template_names
      and default_template.policy_template_id == current.default_policy_template_id
      and default_template.name == current.default_policy_template_name
      and default_template.item_type_scope == current.item_type_scope
      and default_template.action_scope == current.action_scope
      and default_template.approval_lane == current.approval_lane
      and default_template.approval_priority == current.approval_priority
      and default_template.guidance == current.guidance
    ):
      return current
    updated = replace(
      current,
      name=updated_name,
      description=updated_description,
      policy_template_ids=updated_policy_template_ids,
      policy_template_names=updated_policy_template_names,
      default_policy_template_id=default_template.policy_template_id,
      default_policy_template_name=default_template.name,
      item_type_scope=default_template.item_type_scope,
      action_scope=default_template.action_scope,
      approval_lane=default_template.approval_lane,
      approval_priority=default_template.approval_priority,
      guidance=default_template.guidance,
      updated_at=self._clock(),
    )
    return self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
      record=updated,
      action="updated",
      reason=reason,
      recorded_at=updated.updated_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def delete_provider_provenance_scheduler_narrative_governance_policy_catalog(
    self,
    catalog_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_catalog_deleted",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    if current.status == "deleted":
      return current
    deleted_at = self._clock()
    deleted = replace(
      current,
      status="deleted",
      updated_at=deleted_at,
      deleted_at=deleted_at,
      deleted_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      deleted_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )
    return self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
      record=deleted,
      action="deleted",
      reason=reason,
      recorded_at=deleted_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def list_provider_provenance_scheduler_narrative_governance_policy_catalog_revisions(
    self,
    catalog_id: str,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord, ...]:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    revisions = [
      replace(
        self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
          revision
        ),
        status=self._normalize_provider_provenance_scheduler_narrative_record_status(revision.status),
      )
      for revision in self._list_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_records()
      if revision.catalog_id == current.catalog_id
    ]
    return tuple(revisions)

  def restore_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
    self,
    catalog_id: str,
    revision_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_catalog_revision_restored",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    revision = self._load_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
      revision_id.strip()
    )
    if revision is None or revision.catalog_id != current.catalog_id:
      raise LookupError("Provider provenance scheduler narrative governance policy catalog revision not found.")
    revision = self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
      revision
    )
    resolved_templates, default_template = (
      self._resolve_provider_provenance_scheduler_narrative_governance_policy_catalog_templates(
        policy_template_ids=revision.policy_template_ids,
        default_policy_template_id=revision.default_policy_template_id,
      )
    )
    restored_at = self._clock()
    restored = replace(
      current,
      name=revision.name,
      description=revision.description,
      policy_template_ids=tuple(template.policy_template_id for template in resolved_templates),
      policy_template_names=tuple(template.name for template in resolved_templates),
      default_policy_template_id=default_template.policy_template_id,
      default_policy_template_name=default_template.name,
      item_type_scope=default_template.item_type_scope,
      action_scope=default_template.action_scope,
      approval_lane=default_template.approval_lane,
      approval_priority=default_template.approval_priority,
      guidance=default_template.guidance,
      hierarchy_steps=tuple(revision.hierarchy_steps),
      status="active",
      updated_at=restored_at,
      deleted_at=None,
      deleted_by_tab_id=None,
      deleted_by_tab_label=None,
    )
    return self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
      record=restored,
      action="restored",
      reason=reason,
      recorded_at=restored_at,
      source_revision_id=revision.revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def list_provider_provenance_scheduler_narrative_governance_policy_catalog_audits(
    self,
    *,
    catalog_id: str | None = None,
    action: str | None = None,
    actor_tab_id: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord, ...]:
    normalized_catalog_id = catalog_id.strip() if isinstance(catalog_id, str) and catalog_id.strip() else None
    normalized_action = action.strip().lower() if isinstance(action, str) and action.strip() else None
    normalized_actor_tab_id = (
      actor_tab_id.strip()
      if isinstance(actor_tab_id, str) and actor_tab_id.strip()
      else None
    )
    normalized_limit = max(1, min(limit, 200))
    filtered: list[ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord] = []
    for raw_record in self._list_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records():
      record = self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record(
        raw_record
      )
      if normalized_catalog_id is not None and record.catalog_id != normalized_catalog_id:
        continue
      if normalized_action is not None and record.action != normalized_action:
        continue
      if normalized_actor_tab_id is not None and record.actor_tab_id != normalized_actor_tab_id:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.audit_id,
          record.catalog_id,
          record.action,
          record.reason,
          record.detail,
          record.revision_id,
          record.source_revision_id,
          record.name,
          record.status,
          record.default_policy_template_id,
          record.default_policy_template_name,
          record.item_type_scope,
          record.action_scope,
          record.approval_lane,
          record.approval_priority,
          record.guidance,
          record.actor_tab_id,
          record.actor_tab_label,
          *tuple(step.step_id for step in record.hierarchy_steps if isinstance(step.step_id, str)),
          *record.policy_template_ids,
          *record.policy_template_names,
          *tuple(item_id for step in record.hierarchy_steps for item_id in step.item_ids),
          *tuple(item_name for step in record.hierarchy_steps for item_name in step.item_names),
        ),
        search=search,
      ):
        continue
      filtered.append(
        replace(
          record,
          status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
        )
      )
    return tuple(filtered[:normalized_limit])

  def capture_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy(
    self,
    catalog_id: str,
    *,
    hierarchy_steps: Iterable[dict[str, Any]],
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_catalog_hierarchy_captured",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler governance policy catalogs must be restored before capturing reusable hierarchies."
      )
    resolved_steps = self._normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
      hierarchy_steps
    )
    if not resolved_steps:
      raise ValueError("Capture at least one reusable governance hierarchy step.")
    for step in resolved_steps:
      if current.item_type_scope not in {"any", step.item_type}:
        raise ValueError("Policy catalog item-type scope does not support one or more captured hierarchy steps.")
      if current.action_scope not in {"any", step.action}:
        raise ValueError("Policy catalog action scope does not support one or more captured hierarchy steps.")
    if resolved_steps == current.hierarchy_steps:
      return current
    captured_at = self._clock()
    updated = replace(
      current,
      hierarchy_steps=resolved_steps,
      updated_at=captured_at,
    )
    return self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
      record=updated,
      action="hierarchy_captured",
      reason=reason,
      recorded_at=captured_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def update_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step(
    self,
    catalog_id: str,
    step_id: str,
    *,
    item_ids: Iterable[str] | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    query_patch: dict[str, Any] | None = None,
    layout_patch: dict[str, Any] | None = None,
    template_id: str | None = None,
    clear_template_link: bool | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_catalog_hierarchy_step_updated",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler governance policy catalogs must be restored before editing hierarchy steps."
      )
    step_index, step = self._get_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step(
      current,
      step_id,
    )
    resolved_step = self._normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
      (
        {
          "step_id": step.step_id,
          "item_type": step.item_type,
          "action": step.action,
          "item_ids": item_ids if item_ids is not None else step.item_ids,
          "name_prefix": name_prefix if name_prefix is not None else step.name_prefix,
          "name_suffix": name_suffix if name_suffix is not None else step.name_suffix,
          "description_append": (
            description_append if description_append is not None else step.description_append
          ),
          "query_patch": deepcopy(query_patch) if query_patch is not None else deepcopy(step.query_patch),
          "layout_patch": (
            deepcopy(layout_patch) if layout_patch is not None else deepcopy(step.layout_patch)
          ),
          "template_id": template_id if template_id is not None else step.template_id,
          "clear_template_link": (
            clear_template_link
            if clear_template_link is not None
            else step.clear_template_link
          ),
        },
      )
    )[0]
    if resolved_step == step:
      return current
    updated_steps = list(current.hierarchy_steps)
    updated_steps[step_index] = resolved_step
    updated_at = self._clock()
    return self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
      record=replace(current, hierarchy_steps=tuple(updated_steps), updated_at=updated_at),
      action="hierarchy_step_updated",
      reason=reason,
      recorded_at=updated_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def restore_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_revision(
    self,
    catalog_id: str,
    step_id: str,
    revision_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_catalog_hierarchy_step_restored",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler governance policy catalogs must be restored before restoring hierarchy step revisions."
      )
    revision = self._load_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
      revision_id.strip()
    )
    if revision is None or revision.catalog_id != current.catalog_id:
      raise LookupError("Provider provenance scheduler narrative governance policy catalog revision not found.")
    revision = self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
      revision
    )
    normalized_step_id = step_id.strip()
    restored_position = None
    restored_source_step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep | None = None
    for index, step in enumerate(revision.hierarchy_steps):
      if step.step_id == normalized_step_id:
        restored_position = index
        restored_source_step = step
        break
    if restored_source_step is None:
      raise LookupError(
        "Provider provenance scheduler narrative governance policy catalog hierarchy step revision not found."
      )
    if current.item_type_scope not in {"any", restored_source_step.item_type}:
      raise ValueError("Policy catalog item-type scope no longer supports the requested hierarchy step revision.")
    if current.action_scope not in {"any", restored_source_step.action}:
      raise ValueError("Policy catalog action scope no longer supports the requested hierarchy step revision.")
    restored_step = self._normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
      (
        {
          "step_id": restored_source_step.step_id,
          "item_type": restored_source_step.item_type,
          "action": restored_source_step.action,
          "item_ids": restored_source_step.item_ids,
          "name_prefix": restored_source_step.name_prefix,
          "name_suffix": restored_source_step.name_suffix,
          "description_append": restored_source_step.description_append,
          "query_patch": deepcopy(restored_source_step.query_patch),
          "layout_patch": deepcopy(restored_source_step.layout_patch),
          "template_id": restored_source_step.template_id,
          "clear_template_link": restored_source_step.clear_template_link,
        },
      )
    )[0]
    updated_steps = list(current.hierarchy_steps)
    existing_index = next(
      (index for index, step in enumerate(updated_steps) if step.step_id == normalized_step_id),
      None,
    )
    if existing_index is None:
      insert_index = min(restored_position, len(updated_steps))
      updated_steps.insert(insert_index, restored_step)
    else:
      if updated_steps[existing_index] == restored_step:
        return current
      updated_steps[existing_index] = restored_step
    restored_at = self._clock()
    return self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
      record=replace(current, hierarchy_steps=tuple(updated_steps), updated_at=restored_at),
      action="hierarchy_step_restored",
      reason=reason,
      recorded_at=restored_at,
      source_revision_id=revision.revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def bulk_govern_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_steps(
    self,
    catalog_id: str,
    step_ids: Iterable[str],
    *,
    action: str,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    query_patch: dict[str, Any] | None = None,
    layout_patch: dict[str, Any] | None = None,
    template_id: str | None = None,
    clear_template_link: bool | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeBulkGovernanceResult:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler governance policy catalogs must be restored before editing hierarchy steps."
      )
    normalized_action = action.strip().lower()
    if normalized_action not in {"delete", "update"}:
      raise ValueError("Unsupported scheduler governance policy catalog hierarchy-step bulk action.")
    normalized_step_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(step_ids)
    normalized_name_prefix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_prefix,
      preserve_outer_spacing=True,
    )
    normalized_name_suffix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_suffix,
      preserve_outer_spacing=True,
    )
    normalized_description_append = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      description_append
    )
    normalized_template_id = (
      template_id.strip() if isinstance(template_id, str) and template_id.strip() else None
    )
    if normalized_template_id is not None:
      self.get_provider_provenance_scheduler_narrative_template(normalized_template_id)
    if (
      normalized_action == "update"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and query_patch is None
      and layout_patch is None
      and normalized_template_id is None
      and clear_template_link is None
    ):
      raise ValueError("No scheduler governance policy catalog hierarchy-step bulk update fields were provided.")
    current_steps = list(current.hierarchy_steps)
    current_steps_by_id = {
      step.step_id or f"unknown_{index}": step
      for index, step in enumerate(current_steps, start=1)
    }
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    if normalized_action == "delete":
      next_steps = [
        step for step in current_steps if step.step_id not in set(normalized_step_ids)
      ]
      removed_step_ids = {step.step_id for step in current_steps if step.step_id in set(normalized_step_ids)}
      for step_id in normalized_step_ids:
        step = current_steps_by_id.get(step_id)
        if step is None:
          failed_count += 1
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=step_id,
              outcome="failed",
              message="Hierarchy step not found on the selected policy catalog.",
            )
          )
          continue
        applied_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=step_id,
            item_name=", ".join(step.item_names) or f"{step.item_type} step",
            outcome="applied",
            status=current.status,
            current_revision_id=current.current_revision_id,
            message="Hierarchy step deleted from the reusable governance hierarchy.",
          )
        )
      updated_catalog = current
      if removed_step_ids:
        deleted_at = self._clock()
        updated_catalog = self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
          record=replace(current, hierarchy_steps=tuple(next_steps), updated_at=deleted_at),
          action="hierarchy_steps_bulk_deleted",
          reason=(
            reason.strip()
            if isinstance(reason, str) and reason.strip()
            else "scheduler_narrative_governance_policy_catalog_hierarchy_steps_bulk_deleted"
          ),
          recorded_at=deleted_at,
          source_revision_id=current.current_revision_id,
          actor_tab_id=actor_tab_id,
          actor_tab_label=actor_tab_label,
        )
        results = [
          replace(result, current_revision_id=updated_catalog.current_revision_id)
          if result.outcome == "applied"
          else result
          for result in results
        ]
    else:
      next_steps = list(current_steps)
      for step_id in normalized_step_ids:
        step = current_steps_by_id.get(step_id)
        if step is None:
          failed_count += 1
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=step_id,
              outcome="failed",
              message="Hierarchy step not found on the selected policy catalog.",
            )
          )
          continue
        try:
          updated_step = self._normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
            (
              {
                "step_id": step.step_id,
                "item_type": step.item_type,
                "action": step.action,
                "item_ids": step.item_ids,
                "name_prefix": (
                  normalized_name_prefix if normalized_name_prefix is not None else step.name_prefix
                ),
                "name_suffix": (
                  normalized_name_suffix if normalized_name_suffix is not None else step.name_suffix
                ),
                "description_append": (
                  normalized_description_append
                  if normalized_description_append is not None
                  else step.description_append
                ),
                "query_patch": deepcopy(query_patch) if query_patch is not None else deepcopy(step.query_patch),
                "layout_patch": (
                  deepcopy(layout_patch) if layout_patch is not None else deepcopy(step.layout_patch)
                ),
                "template_id": (
                  normalized_template_id if template_id is not None else step.template_id
                ),
                "clear_template_link": (
                  clear_template_link if clear_template_link is not None else step.clear_template_link
                ),
              },
            )
          )[0]
        except (LookupError, ValueError, RuntimeError) as exc:
          failed_count += 1
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=step_id,
              item_name=", ".join(step.item_names) or f"{step.item_type} step",
              outcome="failed",
              status=current.status,
              current_revision_id=current.current_revision_id,
              message=str(exc),
            )
          )
          continue
        if updated_step == step:
          skipped_count += 1
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=step_id,
              item_name=", ".join(step.item_names) or f"{step.item_type} step",
              outcome="skipped",
              status=current.status,
              current_revision_id=current.current_revision_id,
              message="Hierarchy step already matches the requested bulk edits.",
            )
          )
          continue
        applied_count += 1
        step_index, _ = self._get_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step(
          current,
          step_id,
        )
        next_steps[step_index] = updated_step
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=step_id,
            item_name=", ".join(updated_step.item_names) or f"{updated_step.item_type} step",
            outcome="applied",
            status=current.status,
            current_revision_id=current.current_revision_id,
            message="Hierarchy step updated with the requested bulk governance patch.",
          )
        )
      updated_catalog = current
      if applied_count:
        updated_at = self._clock()
        updated_catalog = self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
          record=replace(current, hierarchy_steps=tuple(next_steps), updated_at=updated_at),
          action="hierarchy_steps_bulk_updated",
          reason=(
            reason.strip()
            if isinstance(reason, str) and reason.strip()
            else "scheduler_narrative_governance_policy_catalog_hierarchy_steps_bulk_updated"
          ),
          recorded_at=updated_at,
          source_revision_id=current.current_revision_id,
          actor_tab_id=actor_tab_id,
          actor_tab_label=actor_tab_label,
        )
        results = [
          replace(result, current_revision_id=updated_catalog.current_revision_id)
          if result.outcome == "applied"
          else result
          for result in results
        ]
    return ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type="policy_catalog_hierarchy_step",
      action=normalized_action,
      reason=(
        reason.strip()
        if isinstance(reason, str) and reason.strip()
        else (
          "scheduler_narrative_governance_policy_catalog_hierarchy_steps_bulk_deleted"
          if normalized_action == "delete"
          else "scheduler_narrative_governance_policy_catalog_hierarchy_steps_bulk_updated"
        )
      ),
      requested_count=len(normalized_step_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )

  def create_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
    self,
    *,
    name: str,
    description: str = "",
    step: dict[str, Any] | None = None,
    origin_catalog_id: str | None = None,
    origin_step_id: str | None = None,
    governance_policy_template_id: str | None = None,
    governance_policy_catalog_id: str | None = None,
    governance_approval_lane: str | None = None,
    governance_approval_priority: str | None = None,
    created_by_tab_id: str | None = None,
    created_by_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
    normalized_name = self._normalize_provider_provenance_workspace_name(
      name,
      field_name="scheduler governance hierarchy step template name",
    )
    normalized_description = description.strip() if isinstance(description, str) else ""
    resolved_origin_catalog = (
      self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(origin_catalog_id)
      if isinstance(origin_catalog_id, str) and origin_catalog_id.strip()
      else None
    )
    resolved_source_step: ProviderProvenanceSchedulerNarrativeGovernancePlanHierarchyStep | None = None
    if resolved_origin_catalog is not None and isinstance(origin_step_id, str) and origin_step_id.strip():
      _, resolved_source_step = self._get_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step(
        resolved_origin_catalog,
        origin_step_id,
      )
    raw_step_payload = (
      deepcopy(step)
      if isinstance(step, dict)
      else (
        {
          "item_type": resolved_source_step.item_type,
          "action": resolved_source_step.action,
          "item_ids": resolved_source_step.item_ids,
          "name_prefix": resolved_source_step.name_prefix,
          "name_suffix": resolved_source_step.name_suffix,
          "description_append": resolved_source_step.description_append,
          "query_patch": deepcopy(resolved_source_step.query_patch),
          "layout_patch": deepcopy(resolved_source_step.layout_patch),
          "template_id": resolved_source_step.template_id,
          "clear_template_link": resolved_source_step.clear_template_link,
        }
        if resolved_source_step is not None
        else None
      )
    )
    if raw_step_payload is None:
      raise ValueError("Provide a hierarchy step payload or select an origin catalog step to save as a template.")
    resolved_step = self._normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
      (raw_step_payload,)
    )[0]
    (
      resolved_policy_catalog,
      resolved_policy_template,
      resolved_approval_lane,
      resolved_approval_priority,
      resolved_policy_guidance,
    ) = self._resolve_provider_provenance_scheduler_narrative_governance_policy_layer(
      item_type=resolved_step.item_type,
      action=resolved_step.action,
      policy_catalog_id=governance_policy_catalog_id,
      policy_template_id=governance_policy_template_id,
      approval_lane=governance_approval_lane,
      approval_priority=governance_approval_priority,
    )
    now = self._clock()
    return self._record_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
      record=ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord(
        hierarchy_step_template_id=uuid4().hex[:12],
        name=normalized_name,
        description=normalized_description,
        item_type=resolved_step.item_type,
        step=replace(
          resolved_step,
          step_id=None,
          source_template_id=None,
          source_template_name=None,
        ),
        origin_catalog_id=resolved_origin_catalog.catalog_id if resolved_origin_catalog is not None else None,
        origin_catalog_name=resolved_origin_catalog.name if resolved_origin_catalog is not None else None,
        origin_step_id=resolved_source_step.step_id if resolved_source_step is not None else None,
        governance_policy_template_id=(
          resolved_policy_template.policy_template_id if resolved_policy_template is not None else None
        ),
        governance_policy_template_name=resolved_policy_template.name if resolved_policy_template is not None else None,
        governance_policy_catalog_id=(
          resolved_policy_catalog.catalog_id if resolved_policy_catalog is not None else None
        ),
        governance_policy_catalog_name=resolved_policy_catalog.name if resolved_policy_catalog is not None else None,
        governance_approval_lane=resolved_approval_lane,
        governance_approval_priority=resolved_approval_priority,
        governance_policy_guidance=resolved_policy_guidance,
        status="active",
        created_at=now,
        updated_at=now,
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
      ),
      action="created",
      reason="scheduler_narrative_governance_hierarchy_step_template_created",
      recorded_at=now,
      actor_tab_id=created_by_tab_id,
      actor_tab_label=created_by_tab_label,
    )

  def list_provider_provenance_scheduler_narrative_governance_hierarchy_step_templates(
    self,
    *,
    item_type: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord, ...]:
    normalized_item_type = (
      self._normalize_provider_provenance_scheduler_narrative_governance_item_type(item_type)
      if isinstance(item_type, str) and item_type.strip()
      else None
    )
    normalized_limit = max(1, min(limit, 100))
    filtered: list[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord] = []
    for record in self._list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_records():
      if normalized_item_type is not None and record.item_type != normalized_item_type:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.hierarchy_step_template_id,
          record.name,
          record.description,
          record.item_type,
          record.status,
          record.current_revision_id,
          record.origin_catalog_id,
          record.origin_catalog_name,
          record.origin_step_id,
          record.governance_policy_template_id,
          record.governance_policy_template_name,
          record.governance_policy_catalog_id,
          record.governance_policy_catalog_name,
          record.governance_approval_lane,
          record.governance_approval_priority,
          record.governance_policy_guidance,
          record.created_by_tab_id,
          record.created_by_tab_label,
          record.step.source_template_id,
          record.step.source_template_name,
          *record.step.item_ids,
          *record.step.item_names,
        ),
        search=search,
      ):
        continue
      filtered.append(
        replace(
          record,
          status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
        )
      )
    return tuple(filtered[:normalized_limit])

  def get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
    self,
    hierarchy_step_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
    normalized_id = hierarchy_step_template_id.strip()
    if not normalized_id:
      raise LookupError("Provider provenance scheduler narrative governance hierarchy step template not found.")
    record = self._load_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record(
      normalized_id
    )
    if record is None:
      raise LookupError("Provider provenance scheduler narrative governance hierarchy step template not found.")
    return replace(
      record,
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
    )

  def update_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
    self,
    hierarchy_step_template_id: str,
    *,
    name: str | None = None,
    description: str | None = None,
    item_ids: Iterable[str] | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    query_patch: dict[str, Any] | None = None,
    layout_patch: dict[str, Any] | None = None,
    template_id: str | None = None,
    clear_template_link: bool | None = None,
    governance_policy_template_id: str | None = None,
    governance_policy_catalog_id: str | None = None,
    governance_approval_lane: str | None = None,
    governance_approval_priority: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_hierarchy_step_template_updated",
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
      hierarchy_step_template_id
    )
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler governance hierarchy step templates must be restored from a revision before editing."
      )
    updated_name = (
      self._normalize_provider_provenance_workspace_name(
        name,
        field_name="scheduler governance hierarchy step template name",
      )
      if isinstance(name, str)
      else current.name
    )
    updated_description = description.strip() if isinstance(description, str) else current.description
    updated_step = self._normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
      (
        {
          "item_type": current.item_type,
          "action": current.step.action,
          "item_ids": item_ids if item_ids is not None else current.step.item_ids,
          "name_prefix": name_prefix if name_prefix is not None else current.step.name_prefix,
          "name_suffix": name_suffix if name_suffix is not None else current.step.name_suffix,
          "description_append": (
            description_append if description_append is not None else current.step.description_append
          ),
          "query_patch": deepcopy(query_patch) if query_patch is not None else deepcopy(current.step.query_patch),
          "layout_patch": (
            deepcopy(layout_patch) if layout_patch is not None else deepcopy(current.step.layout_patch)
          ),
          "template_id": template_id if template_id is not None else current.step.template_id,
          "clear_template_link": (
            clear_template_link if clear_template_link is not None else current.step.clear_template_link
          ),
        },
      )
    )[0]
    updated_step = replace(
      updated_step,
      step_id=None,
      source_template_id=None,
      source_template_name=None,
    )
    (
      resolved_policy_catalog,
      resolved_policy_template,
      resolved_approval_lane,
      resolved_approval_priority,
      resolved_policy_guidance,
    ) = self._resolve_provider_provenance_scheduler_narrative_governance_policy_layer(
      item_type=updated_step.item_type,
      action=updated_step.action,
      policy_catalog_id=(
        governance_policy_catalog_id
        if governance_policy_catalog_id is not None
        else current.governance_policy_catalog_id
      ),
      policy_template_id=(
        governance_policy_template_id
        if governance_policy_template_id is not None
        else current.governance_policy_template_id
      ),
      approval_lane=(
        governance_approval_lane
        if governance_approval_lane is not None
        else current.governance_approval_lane
      ),
      approval_priority=(
        governance_approval_priority
        if governance_approval_priority is not None
        else current.governance_approval_priority
      ),
    )
    if (
      updated_name == current.name
      and updated_description == current.description
      and updated_step == current.step
      and (
        resolved_policy_template.policy_template_id if resolved_policy_template is not None else None
      ) == current.governance_policy_template_id
      and (
        resolved_policy_catalog.catalog_id if resolved_policy_catalog is not None else None
      ) == current.governance_policy_catalog_id
      and resolved_approval_lane == current.governance_approval_lane
      and resolved_approval_priority == current.governance_approval_priority
      and resolved_policy_guidance == current.governance_policy_guidance
    ):
      return current
    updated = replace(
      current,
      name=updated_name,
      description=updated_description,
      item_type=updated_step.item_type,
      step=updated_step,
      governance_policy_template_id=(
        resolved_policy_template.policy_template_id if resolved_policy_template is not None else None
      ),
      governance_policy_template_name=resolved_policy_template.name if resolved_policy_template is not None else None,
      governance_policy_catalog_id=(
        resolved_policy_catalog.catalog_id if resolved_policy_catalog is not None else None
      ),
      governance_policy_catalog_name=resolved_policy_catalog.name if resolved_policy_catalog is not None else None,
      governance_approval_lane=resolved_approval_lane,
      governance_approval_priority=resolved_approval_priority,
      governance_policy_guidance=resolved_policy_guidance,
      updated_at=self._clock(),
    )
    return self._record_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
      record=updated,
      action="updated",
      reason=reason,
      recorded_at=updated.updated_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def delete_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
    self,
    hierarchy_step_template_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_hierarchy_step_template_deleted",
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
      hierarchy_step_template_id
    )
    if current.status == "deleted":
      return current
    deleted_at = self._clock()
    deleted = replace(
      current,
      status="deleted",
      updated_at=deleted_at,
      deleted_at=deleted_at,
      deleted_by_tab_id=(
        actor_tab_id.strip()
        if isinstance(actor_tab_id, str) and actor_tab_id.strip()
        else None
      ),
      deleted_by_tab_label=(
        actor_tab_label.strip()
        if isinstance(actor_tab_label, str) and actor_tab_label.strip()
        else None
      ),
    )
    return self._record_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
      record=deleted,
      action="deleted",
      reason=reason,
      recorded_at=deleted_at,
      source_revision_id=current.current_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions(
    self,
    hierarchy_step_template_id: str,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord, ...]:
    current = self.get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
      hierarchy_step_template_id
    )
    revisions = [
      replace(
        revision,
        status=self._normalize_provider_provenance_scheduler_narrative_record_status(revision.status),
      )
      for revision in self._list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_records()
      if revision.hierarchy_step_template_id == current.hierarchy_step_template_id
    ]
    return tuple(revisions)

  def restore_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
    self,
    hierarchy_step_template_id: str,
    revision_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_hierarchy_step_template_revision_restored",
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
      hierarchy_step_template_id
    )
    revision = self._load_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_record(
      revision_id.strip()
    )
    if revision is None or revision.hierarchy_step_template_id != current.hierarchy_step_template_id:
      raise LookupError("Provider provenance scheduler narrative governance hierarchy step template revision not found.")
    restored_at = self._clock()
    restored = replace(
      current,
      name=revision.name,
      description=revision.description,
      item_type=revision.item_type,
      step=replace(
        revision.step,
        step_id=None,
        source_template_id=None,
        source_template_name=None,
      ),
      origin_catalog_id=revision.origin_catalog_id,
      origin_catalog_name=revision.origin_catalog_name,
      origin_step_id=revision.origin_step_id,
      status="active",
      updated_at=restored_at,
      deleted_at=None,
      deleted_by_tab_id=None,
      deleted_by_tab_label=None,
    )
    return self._record_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
      record=restored,
      action="restored",
      reason=reason,
      recorded_at=restored_at,
      source_revision_id=revision.revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  def list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audits(
    self,
    *,
    hierarchy_step_template_id: str | None = None,
    action: str | None = None,
    actor_tab_id: str | None = None,
    search: str | None = None,
    limit: int = 50,
  ) -> tuple[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord, ...]:
    normalized_hierarchy_step_template_id = (
      hierarchy_step_template_id.strip()
      if isinstance(hierarchy_step_template_id, str) and hierarchy_step_template_id.strip()
      else None
    )
    normalized_action = action.strip().lower() if isinstance(action, str) and action.strip() else None
    normalized_actor_tab_id = (
      actor_tab_id.strip()
      if isinstance(actor_tab_id, str) and actor_tab_id.strip()
      else None
    )
    normalized_limit = max(1, min(limit, 200))
    filtered: list[ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord] = []
    for record in self._list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records():
      if (
        normalized_hierarchy_step_template_id is not None
        and record.hierarchy_step_template_id != normalized_hierarchy_step_template_id
      ):
        continue
      if normalized_action is not None and record.action != normalized_action:
        continue
      if normalized_actor_tab_id is not None and record.actor_tab_id != normalized_actor_tab_id:
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.audit_id,
          record.hierarchy_step_template_id,
          record.action,
          record.reason,
          record.detail,
          record.revision_id,
          record.source_revision_id,
          record.name,
          record.description,
          record.item_type,
          record.origin_catalog_id,
          record.origin_catalog_name,
          record.origin_step_id,
          record.status,
          record.actor_tab_id,
          record.actor_tab_label,
          record.step.step_id,
          record.step.source_template_id,
          record.step.source_template_name,
          *record.step.item_ids,
          *record.step.item_names,
        ),
        search=search,
      ):
        continue
      filtered.append(
        replace(
          record,
          status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
        )
      )
    return tuple(filtered[:normalized_limit])

  def stage_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
    self,
    hierarchy_step_template_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_hierarchy_step_template_staged",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
      hierarchy_step_template_id
    )
    if current.status == "deleted":
      raise RuntimeError(
        "Restore the hierarchy step template before staging approval queue plans."
      )
    resolved_reason = reason.strip() if isinstance(reason, str) and reason.strip() else (
      "scheduler_narrative_governance_hierarchy_step_template_staged"
    )
    plan = self.create_provider_provenance_scheduler_narrative_governance_plan(
      item_type=current.item_type,
      item_ids=current.step.item_ids,
      action=current.step.action,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
      reason=resolved_reason,
      name_prefix=current.step.name_prefix,
      name_suffix=current.step.name_suffix,
      description_append=current.step.description_append,
      query_patch=current.step.query_patch,
      layout_patch=current.step.layout_patch,
      template_id=current.step.template_id,
      clear_template_link=current.step.clear_template_link,
      policy_template_id=current.governance_policy_template_id,
      policy_catalog_id=current.governance_policy_catalog_id,
      approval_lane=current.governance_approval_lane,
      approval_priority=current.governance_approval_priority,
      source_hierarchy_step_template_id=current.hierarchy_step_template_id,
      source_hierarchy_step_template_name=current.name,
    )
    recorded_at = self._clock()
    self._save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_record(
      ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord(
        audit_id=f"{current.hierarchy_step_template_id}:{plan.plan_id}:staged",
        hierarchy_step_template_id=current.hierarchy_step_template_id,
        action="staged",
        recorded_at=recorded_at,
        reason=resolved_reason,
        detail=(
          f"Staged hierarchy step template {current.name} into the approval queue as plan "
          f"{plan.plan_id}. "
          f"{self._build_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_detail(record=current, action='staged')}"
        ),
        name=current.name,
        description=current.description,
        item_type=current.item_type,
        step=current.step,
        origin_catalog_id=current.origin_catalog_id,
        origin_catalog_name=current.origin_catalog_name,
        origin_step_id=current.origin_step_id,
        governance_policy_template_id=current.governance_policy_template_id,
        governance_policy_template_name=current.governance_policy_template_name,
        governance_policy_catalog_id=current.governance_policy_catalog_id,
        governance_policy_catalog_name=current.governance_policy_catalog_name,
        governance_approval_lane=current.governance_approval_lane,
        governance_approval_priority=current.governance_approval_priority,
        governance_policy_guidance=current.governance_policy_guidance,
        status=current.status,
        actor_tab_id=(
          actor_tab_id.strip()
          if isinstance(actor_tab_id, str) and actor_tab_id.strip()
          else None
        ),
        actor_tab_label=(
          actor_tab_label.strip()
          if isinstance(actor_tab_label, str) and actor_tab_label.strip()
          else None
        ),
      )
    )
    return plan

  def stage_provider_provenance_scheduler_narrative_governance_hierarchy_step_templates(
    self,
    hierarchy_step_template_ids: Iterable[str],
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_hierarchy_step_templates_staged",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult:
    normalized_template_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(
      hierarchy_step_template_ids
    )
    if not normalized_template_ids:
      raise ValueError("Select at least one hierarchy step template to stage.")
    results: list[ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult] = []
    succeeded_count = 0
    skipped_count = 0
    failed_count = 0
    for hierarchy_step_template_id in normalized_template_ids:
      try:
        plan = self.stage_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
          hierarchy_step_template_id,
          actor_tab_id=actor_tab_id,
          actor_tab_label=actor_tab_label,
          reason=reason,
        )
        succeeded_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult(
            plan_id=plan.plan_id,
            action="stage",
            outcome="succeeded",
            status=plan.status,
            queue_state=self._build_provider_provenance_scheduler_narrative_governance_queue_state(
              plan.status
            ),
            message="Hierarchy step template staged into the approval queue.",
            plan=plan,
          )
        )
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult(
            plan_id=hierarchy_step_template_id,
            action="stage",
            outcome="failed",
            message=str(exc),
          )
        )
    return ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult(
      action="stage",
      requested_count=len(normalized_template_ids),
      succeeded_count=succeeded_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )

  def _find_latest_active_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
    self,
    hierarchy_step_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord | None:
    for revision in reversed(
      self.list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions(
        hierarchy_step_template_id
      )
    ):
      if revision.status == "active":
        return revision
    return None

  def bulk_govern_provider_provenance_scheduler_narrative_governance_hierarchy_step_templates(
    self,
    hierarchy_step_template_ids: Iterable[str],
    *,
    action: str,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    item_ids: Iterable[str] | None = None,
    step_name_prefix: str | None = None,
    step_name_suffix: str | None = None,
    step_description_append: str | None = None,
    query_patch: dict[str, Any] | None = None,
    layout_patch: dict[str, Any] | None = None,
    template_id: str | None = None,
    clear_template_link: bool | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeBulkGovernanceResult:
    normalized_action = action.strip().lower()
    if normalized_action not in {"delete", "restore", "update"}:
      raise ValueError("Unsupported scheduler governance hierarchy step template bulk action.")
    normalized_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(
      hierarchy_step_template_ids
    )
    normalized_name_prefix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_prefix,
      preserve_outer_spacing=True,
    )
    normalized_name_suffix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_suffix,
      preserve_outer_spacing=True,
    )
    normalized_description_append = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      description_append
    )
    normalized_step_name_prefix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      step_name_prefix,
      preserve_outer_spacing=True,
    )
    normalized_step_name_suffix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      step_name_suffix,
      preserve_outer_spacing=True,
    )
    normalized_step_description_append = (
      self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(step_description_append)
    )
    normalized_item_ids = (
      self._normalize_provider_provenance_scheduler_narrative_bulk_ids(item_ids)
      if item_ids is not None
      else None
    )
    resolved_reason = (
      reason.strip()
      if isinstance(reason, str) and reason.strip()
      else (
        "scheduler_narrative_governance_hierarchy_step_template_bulk_deleted"
        if normalized_action == "delete"
        else (
          "scheduler_narrative_governance_hierarchy_step_template_bulk_restored"
          if normalized_action == "restore"
          else "scheduler_narrative_governance_hierarchy_step_template_bulk_updated"
        )
      )
    )
    if (
      normalized_action == "update"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and normalized_item_ids is None
      and normalized_step_name_prefix is None
      and normalized_step_name_suffix is None
      and normalized_step_description_append is None
      and query_patch is None
      and layout_patch is None
      and template_id is None
      and clear_template_link is None
    ):
      raise ValueError("No scheduler governance hierarchy step template bulk update fields were provided.")
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    for hierarchy_step_template_id in normalized_ids:
      try:
        current = self.get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
          hierarchy_step_template_id
        )
        if normalized_action == "delete":
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.hierarchy_step_template_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Hierarchy step template is already deleted.",
              )
            )
            continue
          updated = self.delete_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
            hierarchy_step_template_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        elif normalized_action == "restore":
          if current.status != "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.hierarchy_step_template_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Hierarchy step template is already active.",
              )
            )
            continue
          revision = self._find_latest_active_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
            hierarchy_step_template_id
          )
          if revision is None:
            failed_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.hierarchy_step_template_id,
                item_name=current.name,
                outcome="failed",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="No active revision is available for restore.",
              )
            )
            continue
          updated = self.restore_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
            hierarchy_step_template_id,
            revision.revision_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        else:
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.hierarchy_step_template_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Hierarchy step template is deleted; restore it before applying bulk edits.",
              )
            )
            continue
          updated_name = (
            f"{normalized_name_prefix or ''}{current.name}{normalized_name_suffix or ''}"
          )
          updated_description = (
            f"{current.description} {normalized_description_append}".strip()
            if normalized_description_append is not None
            else current.description
          )
          updated_step = self._normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
            (
              {
                "item_type": current.item_type,
                "action": current.step.action,
                "item_ids": normalized_item_ids if normalized_item_ids is not None else current.step.item_ids,
                "name_prefix": (
                  normalized_step_name_prefix
                  if normalized_step_name_prefix is not None
                  else current.step.name_prefix
                ),
                "name_suffix": (
                  normalized_step_name_suffix
                  if normalized_step_name_suffix is not None
                  else current.step.name_suffix
                ),
                "description_append": (
                  normalized_step_description_append
                  if normalized_step_description_append is not None
                  else current.step.description_append
                ),
                "query_patch": (
                  deepcopy(query_patch) if query_patch is not None else deepcopy(current.step.query_patch)
                ),
                "layout_patch": (
                  deepcopy(layout_patch) if layout_patch is not None else deepcopy(current.step.layout_patch)
                ),
                "template_id": template_id if template_id is not None else current.step.template_id,
                "clear_template_link": (
                  clear_template_link if clear_template_link is not None else current.step.clear_template_link
                ),
              },
            )
          )[0]
          updated_step = replace(
            updated_step,
            step_id=None,
            source_template_id=None,
            source_template_name=None,
          )
          if (
            updated_name == current.name
            and updated_description == current.description
            and updated_step == current.step
          ):
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.hierarchy_step_template_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Hierarchy step template already matches the requested bulk edits.",
              )
            )
            continue
          updated = self.update_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
            hierarchy_step_template_id,
            name=updated_name,
            description=updated_description,
            item_ids=updated_step.item_ids,
            name_prefix=updated_step.name_prefix,
            name_suffix=updated_step.name_suffix,
            description_append=updated_step.description_append,
            query_patch=updated_step.query_patch,
            layout_patch=updated_step.layout_patch,
            template_id=updated_step.template_id,
            clear_template_link=updated_step.clear_template_link,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        applied_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=updated.hierarchy_step_template_id,
            item_name=updated.name,
            outcome="applied",
            status=updated.status,
            current_revision_id=updated.current_revision_id,
            message=(
              "Hierarchy step template deleted."
              if normalized_action == "delete"
              else (
                "Hierarchy step template restored from the latest active revision."
                if normalized_action == "restore"
                else "Hierarchy step template updated with the requested bulk governance patch."
              )
            ),
          )
        )
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=hierarchy_step_template_id,
            outcome="failed",
            message=str(exc),
          )
        )
    return ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type="policy_catalog_hierarchy_step_template",
      action=normalized_action,
      reason=resolved_reason,
      requested_count=len(normalized_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )

  def apply_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_to_catalogs(
    self,
    hierarchy_step_template_id: str,
    catalog_ids: Iterable[str],
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeBulkGovernanceResult:
    template = self.get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
      hierarchy_step_template_id
    )
    if template.status != "active":
      raise RuntimeError("Restore the hierarchy step template before applying it to policy catalogs.")
    normalized_catalog_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(catalog_ids)
    resolved_reason = (
      reason.strip()
      if isinstance(reason, str) and reason.strip()
      else "scheduler_narrative_governance_hierarchy_step_template_applied"
    )
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    for catalog_id in normalized_catalog_ids:
      try:
        current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
        if current.status == "deleted":
          skipped_count += 1
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=current.catalog_id,
              item_name=current.name,
              outcome="skipped",
              status=current.status,
              current_revision_id=current.current_revision_id,
              message="Catalog is deleted; restore it before applying a hierarchy step template.",
            )
          )
          continue
        if current.item_type_scope not in {"any", template.item_type}:
          raise ValueError("Policy catalog item-type scope does not support the hierarchy step template.")
        if current.action_scope not in {"any", template.step.action}:
          raise ValueError("Policy catalog action scope does not support the hierarchy step template.")
        current_steps = list(current.hierarchy_steps)
        existing_index = next(
          (
            index
            for index, step in enumerate(current_steps)
            if step.source_template_id == template.hierarchy_step_template_id
          ),
          None,
        )
        if existing_index is None and template.origin_catalog_id == current.catalog_id and template.origin_step_id:
          existing_index = next(
            (
              index
              for index, step in enumerate(current_steps)
              if step.step_id == template.origin_step_id
            ),
            None,
          )
        resolved_step = self._normalize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
          (
            {
              "step_id": (
                current_steps[existing_index].step_id
                if existing_index is not None
                else None
              ),
              "source_template_id": template.hierarchy_step_template_id,
              "source_template_name": template.name,
              "item_type": template.item_type,
              "action": template.step.action,
              "item_ids": template.step.item_ids,
              "name_prefix": template.step.name_prefix,
              "name_suffix": template.step.name_suffix,
              "description_append": template.step.description_append,
              "query_patch": deepcopy(template.step.query_patch),
              "layout_patch": deepcopy(template.step.layout_patch),
              "template_id": template.step.template_id,
              "clear_template_link": template.step.clear_template_link,
            },
          )
        )[0]
        if existing_index is not None:
          if current_steps[existing_index] == resolved_step:
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.catalog_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Catalog already matches the selected hierarchy step template.",
              )
            )
            continue
          current_steps[existing_index] = resolved_step
        else:
          current_steps.append(resolved_step)
        updated_at = self._clock()
        updated = self._record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
          record=replace(current, hierarchy_steps=tuple(current_steps), updated_at=updated_at),
          action="hierarchy_step_template_applied",
          reason=resolved_reason,
          recorded_at=updated_at,
          source_revision_id=current.current_revision_id,
          actor_tab_id=actor_tab_id,
          actor_tab_label=actor_tab_label,
        )
        applied_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=updated.catalog_id,
            item_name=updated.name,
            outcome="applied",
            status=updated.status,
            current_revision_id=updated.current_revision_id,
            message=(
              "Hierarchy step template applied to catalog."
              if existing_index is None
              else "Hierarchy step template synchronized onto catalog."
            ),
          )
        )
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=catalog_id,
            outcome="failed",
            message=str(exc),
          )
        )
    return ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type="policy_catalog_hierarchy_step_template",
      action="apply",
      reason=resolved_reason,
      requested_count=len(normalized_catalog_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )

  def stage_provider_provenance_scheduler_narrative_governance_policy_catalog(
    self,
    catalog_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str = "scheduler_narrative_governance_policy_catalog_staged",
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogStageResult:
    current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
    if current.status == "deleted":
      raise RuntimeError(
        "Deleted scheduler governance policy catalogs must be restored before staging approval queue plans."
      )
    if not current.hierarchy_steps:
      raise RuntimeError("Capture a reusable governance hierarchy on this policy catalog before staging it.")
    for step in current.hierarchy_steps:
      if current.item_type_scope not in {"any", step.item_type}:
        raise ValueError("Policy catalog item-type scope no longer supports a captured hierarchy step.")
      if current.action_scope not in {"any", step.action}:
        raise ValueError("Policy catalog action scope no longer supports a captured hierarchy step.")
      for item_id in step.item_ids:
        if step.item_type == "template":
          self._preview_provider_provenance_scheduler_narrative_template_governance_item(
            self.get_provider_provenance_scheduler_narrative_template(item_id),
            action=step.action,
            name_prefix=step.name_prefix,
            name_suffix=step.name_suffix,
            description_append=step.description_append,
            query_patch=step.query_patch,
          )
        else:
          self._preview_provider_provenance_scheduler_narrative_registry_governance_item(
            self.get_provider_provenance_scheduler_narrative_registry_entry(item_id),
            action=step.action,
            name_prefix=step.name_prefix,
            name_suffix=step.name_suffix,
            description_append=step.description_append,
            query_patch=step.query_patch,
            layout_patch=step.layout_patch,
            template_id=step.template_id,
            clear_template_link=step.clear_template_link,
          )
    hierarchy_key = uuid4().hex[:12]
    hierarchy_name = f"{current.name} hierarchy"
    staged_plans: list[ProviderProvenanceSchedulerNarrativeGovernancePlanRecord] = []
    total = len(current.hierarchy_steps)
    resolved_reason = reason.strip() if isinstance(reason, str) and reason.strip() else (
      "scheduler_narrative_governance_policy_catalog_staged"
    )
    for index, step in enumerate(current.hierarchy_steps, start=1):
      staged_plans.append(
        self.create_provider_provenance_scheduler_narrative_governance_plan(
          item_type=step.item_type,
          item_ids=step.item_ids,
          action=step.action,
          actor_tab_id=actor_tab_id,
          actor_tab_label=actor_tab_label,
          reason=resolved_reason,
          name_prefix=step.name_prefix,
          name_suffix=step.name_suffix,
          description_append=step.description_append,
          query_patch=step.query_patch,
          layout_patch=step.layout_patch,
          template_id=step.template_id,
          clear_template_link=step.clear_template_link,
          policy_catalog_id=current.catalog_id,
          hierarchy_key=hierarchy_key,
          hierarchy_name=hierarchy_name,
          hierarchy_position=index,
          hierarchy_total=total,
        )
      )
    recorded_at = self._clock()
    self._save_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record(
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord(
        audit_id=f"{current.catalog_id}:{hierarchy_key}:staged",
        catalog_id=current.catalog_id,
        action="staged",
        recorded_at=recorded_at,
        reason=resolved_reason,
        detail=(
          f"Staged {len(staged_plans)} governance plan(s) into the approval queue from "
          f"{self._summarize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(current.hierarchy_steps)}"
        ),
        name=current.name,
        status=current.status,
        default_policy_template_id=current.default_policy_template_id,
        default_policy_template_name=current.default_policy_template_name,
        policy_template_ids=tuple(current.policy_template_ids),
        policy_template_names=tuple(current.policy_template_names),
        item_type_scope=current.item_type_scope,
        action_scope=current.action_scope,
        approval_lane=current.approval_lane,
        approval_priority=current.approval_priority,
        guidance=current.guidance,
        hierarchy_steps=tuple(current.hierarchy_steps),
        actor_tab_id=(
          actor_tab_id.strip()
          if isinstance(actor_tab_id, str) and actor_tab_id.strip()
          else None
        ),
        actor_tab_label=(
          actor_tab_label.strip()
          if isinstance(actor_tab_label, str) and actor_tab_label.strip()
          else None
        ),
      )
    )
    return ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogStageResult(
      catalog_id=current.catalog_id,
      catalog_name=current.name,
      hierarchy_key=hierarchy_key,
      hierarchy_name=hierarchy_name,
      plan_count=len(staged_plans),
      summary=(
        f"Staged {len(staged_plans)} governance plan(s) from "
        f"{self._summarize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(current.hierarchy_steps)}"
      ),
      plans=tuple(staged_plans),
    )

  def _find_latest_active_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
    self,
    catalog_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord | None:
    for revision in reversed(
      self.list_provider_provenance_scheduler_narrative_governance_policy_catalog_revisions(catalog_id)
    ):
      if revision.status == "active":
        return revision
    return None

  def bulk_govern_provider_provenance_scheduler_narrative_governance_policy_catalogs(
    self,
    catalog_ids: Iterable[str],
    *,
    action: str,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    default_policy_template_id: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeBulkGovernanceResult:
    normalized_action = action.strip().lower()
    if normalized_action not in {"delete", "restore", "update"}:
      raise ValueError("Unsupported scheduler governance policy catalog bulk action.")
    normalized_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(catalog_ids)
    normalized_name_prefix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_prefix,
      preserve_outer_spacing=True,
    )
    normalized_name_suffix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_suffix,
      preserve_outer_spacing=True,
    )
    normalized_description_append = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      description_append
    )
    normalized_default_policy_template_id = (
      default_policy_template_id.strip()
      if isinstance(default_policy_template_id, str) and default_policy_template_id.strip()
      else None
    )
    resolved_reason = (
      reason.strip()
      if isinstance(reason, str) and reason.strip()
      else (
        "scheduler_narrative_governance_policy_catalog_bulk_deleted"
        if normalized_action == "delete"
        else (
          "scheduler_narrative_governance_policy_catalog_bulk_restored"
          if normalized_action == "restore"
          else "scheduler_narrative_governance_policy_catalog_bulk_updated"
        )
      )
    )
    if (
      normalized_action == "update"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and normalized_default_policy_template_id is None
    ):
      raise ValueError("No scheduler governance policy catalog bulk update fields were provided.")
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    for catalog_id in normalized_ids:
      try:
        current = self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(catalog_id)
        if normalized_action == "delete":
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.catalog_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Catalog is already deleted.",
              )
            )
            continue
          updated = self.delete_provider_provenance_scheduler_narrative_governance_policy_catalog(
            catalog_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        elif normalized_action == "restore":
          if current.status != "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.catalog_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Catalog is already active.",
              )
            )
            continue
          revision = self._find_latest_active_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
            catalog_id
          )
          if revision is None:
            failed_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.catalog_id,
                item_name=current.name,
                outcome="failed",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="No active revision is available for restore.",
              )
            )
            continue
          updated = self.restore_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
            catalog_id,
            revision.revision_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        else:
          if current.status == "deleted":
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.catalog_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Catalog is deleted; restore it before applying bulk edits.",
              )
            )
            continue
          updated_name = f"{normalized_name_prefix or ''}{current.name}{normalized_name_suffix or ''}"
          updated_description = (
            f"{current.description} {normalized_description_append}".strip()
            if normalized_description_append is not None
            else current.description
          )
          updated_default_policy_template_id = (
            normalized_default_policy_template_id or current.default_policy_template_id
          )
          if (
            updated_name == current.name
            and updated_description == current.description
            and updated_default_policy_template_id == current.default_policy_template_id
          ):
            skipped_count += 1
            results.append(
              ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
                item_id=current.catalog_id,
                item_name=current.name,
                outcome="skipped",
                status=current.status,
                current_revision_id=current.current_revision_id,
                message="Catalog already matches the requested bulk edits.",
              )
            )
            continue
          updated = self.update_provider_provenance_scheduler_narrative_governance_policy_catalog(
            catalog_id,
            name=updated_name,
            description=updated_description,
            default_policy_template_id=updated_default_policy_template_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason=resolved_reason,
          )
        applied_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=updated.catalog_id,
            item_name=updated.name,
            outcome="applied",
            status=updated.status,
            current_revision_id=updated.current_revision_id,
            message=(
              "Catalog deleted."
              if normalized_action == "delete"
              else (
                "Catalog restored from the latest active revision."
                if normalized_action == "restore"
                else "Catalog updated with the requested bulk governance patch."
              )
            ),
          )
        )
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=catalog_id,
            outcome="failed",
            message=str(exc),
          )
        )
    return ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type="policy_catalog",
      action=normalized_action,
      reason=resolved_reason,
      requested_count=len(normalized_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )

  def _find_latest_active_provider_provenance_scheduler_narrative_governance_policy_template_revision(
    self,
    policy_template_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord | None:
    for revision in reversed(
      self.list_provider_provenance_scheduler_narrative_governance_policy_template_revisions(
        policy_template_id
      )
    ):
      if revision.status == "active":
        return revision
    return None

  def _resolve_provider_provenance_scheduler_narrative_governance_policy_layer(
    self,
    *,
    item_type: str,
    action: str,
    policy_catalog_id: str | None = None,
    policy_template_id: str | None = None,
    approval_lane: str | None = None,
    approval_priority: str | None = None,
  ) -> tuple[
    ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord | None,
    ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord | None,
    str,
    str,
    str | None,
  ]:
    resolved_policy_catalog = (
      self.get_provider_provenance_scheduler_narrative_governance_policy_catalog(policy_catalog_id)
      if isinstance(policy_catalog_id, str) and policy_catalog_id.strip()
      else None
    )
    if resolved_policy_catalog is not None:
      if resolved_policy_catalog.status != "active":
        raise ValueError("Selected scheduler governance policy catalog must be active.")
      if resolved_policy_catalog.item_type_scope not in {"any", item_type}:
        raise ValueError("Selected scheduler governance policy catalog does not support this item type.")
      if resolved_policy_catalog.action_scope not in {"any", action}:
        raise ValueError("Selected scheduler governance policy catalog does not support this action.")
    explicit_policy_template_id = (
      policy_template_id.strip()
      if isinstance(policy_template_id, str) and policy_template_id.strip()
      else None
    )
    resolved_policy_template = (
      self.get_provider_provenance_scheduler_narrative_governance_policy_template(
        explicit_policy_template_id
        if explicit_policy_template_id is not None
        else (
          resolved_policy_catalog.default_policy_template_id
          if resolved_policy_catalog is not None and resolved_policy_catalog.default_policy_template_id
          else ""
        )
      )
      if explicit_policy_template_id is not None or (
        resolved_policy_catalog is not None
        and resolved_policy_catalog.default_policy_template_id is not None
      )
      else None
    )
    if resolved_policy_template is not None:
      if resolved_policy_template.status != "active":
        raise ValueError("Selected scheduler governance policy template must be active.")
      if (
        resolved_policy_catalog is not None
        and resolved_policy_template.policy_template_id not in resolved_policy_catalog.policy_template_ids
      ):
        raise ValueError("Selected scheduler governance policy template is not linked to the chosen policy catalog.")
      if resolved_policy_template.item_type_scope not in {"any", item_type}:
        raise ValueError("Selected scheduler governance policy template does not support this item type.")
      if resolved_policy_template.action_scope not in {"any", action}:
        raise ValueError("Selected scheduler governance policy template does not support this action.")
    resolved_approval_lane = self._normalize_provider_provenance_scheduler_narrative_governance_approval_lane(
      (
        approval_lane
        if isinstance(approval_lane, str) and approval_lane.strip()
        else (
          resolved_policy_template.approval_lane
          if resolved_policy_template is not None
          else resolved_policy_catalog.approval_lane if resolved_policy_catalog is not None else None
        )
      )
    )
    resolved_approval_priority = self._normalize_provider_provenance_scheduler_narrative_governance_approval_priority(
      (
        approval_priority
        if isinstance(approval_priority, str) and approval_priority.strip()
        else (
          resolved_policy_template.approval_priority
          if resolved_policy_template is not None
          else resolved_policy_catalog.approval_priority if resolved_policy_catalog is not None else None
        )
      )
    )
    resolved_policy_guidance = (
      resolved_policy_template.guidance
      if resolved_policy_template is not None
      else resolved_policy_catalog.guidance if resolved_policy_catalog is not None else None
    )
    return (
      resolved_policy_catalog,
      resolved_policy_template,
      resolved_approval_lane,
      resolved_approval_priority,
      resolved_policy_guidance,
    )

  def create_provider_provenance_scheduler_narrative_governance_plan(
    self,
    *,
    item_type: str,
    item_ids: Iterable[str],
    action: str,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    reason: str | None = None,
    name_prefix: str | None = None,
    name_suffix: str | None = None,
    description_append: str | None = None,
    query_patch: dict[str, Any] | None = None,
    layout_patch: dict[str, Any] | None = None,
    queue_view_patch: dict[str, Any] | None = None,
    default_policy_template_id: str | None = None,
    default_policy_catalog_id: str | None = None,
    occurrence_limit: int | None = None,
    history_limit: int | None = None,
    drilldown_history_limit: int | None = None,
    template_id: str | None = None,
    clear_template_link: bool = False,
    policy_template_id: str | None = None,
    policy_catalog_id: str | None = None,
    approval_lane: str | None = None,
    approval_priority: str | None = None,
    source_hierarchy_step_template_id: str | None = None,
    source_hierarchy_step_template_name: str | None = None,
    hierarchy_key: str | None = None,
    hierarchy_name: str | None = None,
    hierarchy_position: int | None = None,
    hierarchy_total: int | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    normalized_item_type = self._normalize_provider_provenance_scheduler_narrative_governance_item_type(
      item_type
    )
    normalized_action = action.strip().lower()
    if normalized_action not in {"delete", "restore", "update"}:
      raise ValueError("Unsupported scheduler narrative governance action.")
    normalized_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(item_ids)
    normalized_name_prefix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_prefix,
      preserve_outer_spacing=True,
    )
    normalized_name_suffix = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      name_suffix,
      preserve_outer_spacing=True,
    )
    normalized_description_append = self._normalize_provider_provenance_scheduler_narrative_bulk_text_patch(
      description_append
    )
    if (
      normalized_action == "update"
      and normalized_item_type == "template"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and not isinstance(query_patch, dict)
    ):
      raise ValueError("No scheduler narrative template bulk update fields were provided.")
    if (
      normalized_action == "update"
      and normalized_item_type == "registry"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and not isinstance(query_patch, dict)
      and not isinstance(layout_patch, dict)
      and template_id is None
      and not clear_template_link
    ):
      raise ValueError("No scheduler narrative registry bulk update fields were provided.")
    if (
      normalized_action == "update"
      and normalized_item_type == "stitched_report_view"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and not isinstance(query_patch, dict)
      and occurrence_limit is None
      and history_limit is None
      and drilldown_history_limit is None
    ):
      raise ValueError("No scheduler stitched report view governance fields were provided.")
    if (
      normalized_action == "update"
      and normalized_item_type == "stitched_report_governance_registry"
      and normalized_name_prefix is None
      and normalized_name_suffix is None
      and normalized_description_append is None
      and not isinstance(queue_view_patch, dict)
      and default_policy_template_id is None
      and default_policy_catalog_id is None
    ):
      raise ValueError("No stitched governance registry governance fields were provided.")
    resolved_reason = (
      reason.strip()
      if isinstance(reason, str) and reason.strip()
      else (
        f"scheduler_narrative_{normalized_item_type}_bulk_deleted"
        if normalized_action == "delete"
        else (
          f"scheduler_narrative_{normalized_item_type}_bulk_restored"
          if normalized_action == "restore"
          else f"scheduler_narrative_{normalized_item_type}_bulk_updated"
        )
      )
    )
    preview_items: list[ProviderProvenanceSchedulerNarrativeGovernancePreviewItem] = []
    for item_id in normalized_ids:
      try:
        if normalized_item_type == "template":
          current_template = self.get_provider_provenance_scheduler_narrative_template(item_id)
          preview_items.append(
            self._preview_provider_provenance_scheduler_narrative_template_governance_item(
              current_template,
              action=normalized_action,
              name_prefix=normalized_name_prefix,
              name_suffix=normalized_name_suffix,
              description_append=normalized_description_append,
              query_patch=query_patch,
            )
          )
        elif normalized_item_type == "registry":
          current_registry = self.get_provider_provenance_scheduler_narrative_registry_entry(item_id)
          preview_items.append(
            self._preview_provider_provenance_scheduler_narrative_registry_governance_item(
              current_registry,
              action=normalized_action,
              name_prefix=normalized_name_prefix,
              name_suffix=normalized_name_suffix,
              description_append=normalized_description_append,
              query_patch=query_patch,
              layout_patch=layout_patch,
              template_id=template_id,
              clear_template_link=clear_template_link,
            )
          )
        elif normalized_item_type == "stitched_report_governance_registry":
          current_registry = self.get_provider_provenance_scheduler_stitched_report_governance_registry(
            item_id
          )
          preview_items.append(
            self._preview_provider_provenance_scheduler_stitched_report_governance_registry_governance_item(
              current_registry,
              action=normalized_action,
              name_prefix=normalized_name_prefix,
              name_suffix=normalized_name_suffix,
              description_append=normalized_description_append,
              queue_view_patch=queue_view_patch,
              default_policy_template_id=default_policy_template_id,
              default_policy_catalog_id=default_policy_catalog_id,
            )
          )
        else:
          current_view = self.get_provider_provenance_scheduler_stitched_report_view(item_id)
          preview_items.append(
            self._preview_provider_provenance_scheduler_stitched_report_view_governance_item(
              current_view,
              action=normalized_action,
              name_prefix=normalized_name_prefix,
              name_suffix=normalized_name_suffix,
              description_append=normalized_description_append,
              query_patch=query_patch,
              occurrence_limit=occurrence_limit,
              history_limit=history_limit,
              drilldown_history_limit=drilldown_history_limit,
            )
          )
      except (LookupError, RuntimeError, ValueError) as exc:
        preview_items.append(
          ProviderProvenanceSchedulerNarrativeGovernancePreviewItem(
            item_id=item_id,
            outcome="failed",
            message=str(exc),
          )
        )
    preview_changed_count = sum(1 for item in preview_items if item.outcome == "changed")
    preview_skipped_count = sum(1 for item in preview_items if item.outcome == "skipped")
    preview_failed_count = sum(1 for item in preview_items if item.outcome == "failed")
    rollback_ready_count = sum(
      1
      for item in preview_items
      if item.outcome == "changed" and item.rollback_revision_id is not None
    )
    request_payload: dict[str, Any] = {
      "item_type": normalized_item_type,
      "item_ids": list(normalized_ids),
      "action": normalized_action,
    }
    if normalized_name_prefix is not None:
      request_payload["name_prefix"] = normalized_name_prefix
    if normalized_name_suffix is not None:
      request_payload["name_suffix"] = normalized_name_suffix
    if normalized_description_append is not None:
      request_payload["description_append"] = normalized_description_append
    if isinstance(query_patch, dict) and query_patch:
      request_payload["query_patch"] = deepcopy(query_patch)
    if isinstance(layout_patch, dict) and layout_patch:
      request_payload["layout_patch"] = deepcopy(layout_patch)
    if isinstance(queue_view_patch, dict) and queue_view_patch:
      request_payload["queue_view_patch"] = deepcopy(queue_view_patch)
    if isinstance(default_policy_template_id, str):
      request_payload["default_policy_template_id"] = default_policy_template_id
    if isinstance(default_policy_catalog_id, str):
      request_payload["default_policy_catalog_id"] = default_policy_catalog_id
    if occurrence_limit is not None:
      request_payload["occurrence_limit"] = self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        occurrence_limit,
        default=8,
        minimum=1,
        maximum=50,
        field_name="scheduler stitched report occurrence_limit",
      )
    if history_limit is not None:
      request_payload["history_limit"] = self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        history_limit,
        default=12,
        minimum=1,
        maximum=200,
        field_name="scheduler stitched report history_limit",
      )
    if drilldown_history_limit is not None:
      request_payload["drilldown_history_limit"] = self._normalize_provider_provenance_scheduler_stitched_report_view_limit(
        drilldown_history_limit,
        default=12,
        minimum=1,
        maximum=100,
        field_name="scheduler stitched report drilldown_history_limit",
      )
    if isinstance(template_id, str) and template_id.strip():
      request_payload["template_id"] = template_id.strip()
    if clear_template_link:
      request_payload["clear_template_link"] = True
    (
      resolved_policy_catalog,
      resolved_policy_template,
      resolved_approval_lane,
      resolved_approval_priority,
      resolved_policy_guidance,
    ) = self._resolve_provider_provenance_scheduler_narrative_governance_policy_layer(
      item_type=normalized_item_type,
      action=normalized_action,
      policy_catalog_id=policy_catalog_id,
      policy_template_id=policy_template_id,
      approval_lane=approval_lane,
      approval_priority=approval_priority,
    )
    if resolved_policy_catalog is not None:
      request_payload["policy_catalog_id"] = resolved_policy_catalog.catalog_id
    if resolved_policy_template is not None:
      request_payload["policy_template_id"] = resolved_policy_template.policy_template_id
    request_payload["approval_lane"] = resolved_approval_lane
    request_payload["approval_priority"] = resolved_approval_priority
    normalized_source_hierarchy_step_template_id = (
      source_hierarchy_step_template_id.strip()
      if isinstance(source_hierarchy_step_template_id, str) and source_hierarchy_step_template_id.strip()
      else None
    )
    normalized_source_hierarchy_step_template_name = (
      source_hierarchy_step_template_name.strip()
      if isinstance(source_hierarchy_step_template_name, str) and source_hierarchy_step_template_name.strip()
      else None
    )
    if normalized_source_hierarchy_step_template_id is not None:
      request_payload["source_hierarchy_step_template_id"] = normalized_source_hierarchy_step_template_id
    if normalized_source_hierarchy_step_template_name is not None:
      request_payload["source_hierarchy_step_template_name"] = normalized_source_hierarchy_step_template_name
    normalized_hierarchy_key = (
      hierarchy_key.strip()
      if isinstance(hierarchy_key, str) and hierarchy_key.strip()
      else None
    )
    normalized_hierarchy_name = (
      hierarchy_name.strip()
      if isinstance(hierarchy_name, str) and hierarchy_name.strip()
      else None
    )
    resolved_hierarchy_total = (
      max(1, int(hierarchy_total))
      if isinstance(hierarchy_total, int) and hierarchy_total > 0
      else None
    )
    resolved_hierarchy_position = (
      max(1, int(hierarchy_position))
      if isinstance(hierarchy_position, int) and hierarchy_position > 0
      else None
    )
    if normalized_hierarchy_key is not None:
      request_payload["hierarchy_key"] = normalized_hierarchy_key
    if normalized_hierarchy_name is not None:
      request_payload["hierarchy_name"] = normalized_hierarchy_name
    if resolved_hierarchy_position is not None:
      request_payload["hierarchy_position"] = resolved_hierarchy_position
    if resolved_hierarchy_total is not None:
      request_payload["hierarchy_total"] = resolved_hierarchy_total
    now = self._clock()
    return self._save_provider_provenance_scheduler_narrative_governance_plan_record(
      ProviderProvenanceSchedulerNarrativeGovernancePlanRecord(
        plan_id=uuid4().hex[:12],
        item_type=normalized_item_type,
        action=normalized_action,
        reason=resolved_reason,
        status="previewed",
        source_hierarchy_step_template_id=normalized_source_hierarchy_step_template_id,
        source_hierarchy_step_template_name=normalized_source_hierarchy_step_template_name,
        policy_template_id=(
          resolved_policy_template.policy_template_id if resolved_policy_template is not None else None
        ),
        policy_template_name=(
          resolved_policy_template.name if resolved_policy_template is not None else None
        ),
        policy_catalog_id=(
          resolved_policy_catalog.catalog_id if resolved_policy_catalog is not None else None
        ),
        policy_catalog_name=(
          resolved_policy_catalog.name if resolved_policy_catalog is not None else None
        ),
        approval_lane=resolved_approval_lane,
        approval_priority=resolved_approval_priority,
        policy_guidance=resolved_policy_guidance,
        hierarchy_key=normalized_hierarchy_key,
        hierarchy_name=normalized_hierarchy_name,
        hierarchy_position=resolved_hierarchy_position,
        hierarchy_total=resolved_hierarchy_total,
        request_payload=request_payload,
        target_ids=normalized_ids,
        preview_requested_count=len(normalized_ids),
        preview_changed_count=preview_changed_count,
        preview_skipped_count=preview_skipped_count,
        preview_failed_count=preview_failed_count,
        preview_items=tuple(preview_items),
        rollback_ready_count=rollback_ready_count,
        rollback_summary=(
          f"Rollback can restore {rollback_ready_count} pre-apply revision snapshot(s)."
          if rollback_ready_count
          else "No rollback snapshot is available for this governance plan."
        ),
        created_at=now,
        updated_at=now,
        created_by_tab_id=(
          actor_tab_id.strip()
          if isinstance(actor_tab_id, str) and actor_tab_id.strip()
          else None
        ),
        created_by_tab_label=(
          actor_tab_label.strip()
          if isinstance(actor_tab_label, str) and actor_tab_label.strip()
          else None
        ),
      )
    )

  def list_provider_provenance_scheduler_narrative_governance_plans(
    self,
    *,
    item_type: str | None = None,
    status: str | None = None,
    queue_state: str | None = None,
    approval_lane: str | None = None,
    approval_priority: str | None = None,
    policy_template_id: str | None = None,
    policy_catalog_id: str | None = None,
    source_hierarchy_step_template_id: str | None = None,
    search: str | None = None,
    sort: str | None = None,
    limit: int = 20,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanListResult:
    normalized_item_type = (
      self._normalize_provider_provenance_scheduler_narrative_governance_item_type(item_type)
      if isinstance(item_type, str) and item_type.strip()
      else None
    )
    normalized_status = (
      status.strip().lower()
      if isinstance(status, str) and status.strip()
      else None
    )
    normalized_queue_state = (
      self._normalize_provider_provenance_scheduler_narrative_governance_queue_state_filter(queue_state)
      if isinstance(queue_state, str) and queue_state.strip()
      else None
    )
    normalized_approval_lane = (
      self._normalize_provider_provenance_scheduler_narrative_governance_approval_lane(approval_lane)
      if isinstance(approval_lane, str) and approval_lane.strip()
      else None
    )
    normalized_approval_priority = (
      self._normalize_provider_provenance_scheduler_narrative_governance_approval_priority(approval_priority)
      if isinstance(approval_priority, str) and approval_priority.strip()
      else None
    )
    normalized_policy_template_id = (
      None
      if not isinstance(policy_template_id, str)
      else ""
      if policy_template_id == "__none__"
      else policy_template_id.strip() or None
    )
    normalized_policy_catalog_id = (
      None
      if not isinstance(policy_catalog_id, str)
      else ""
      if policy_catalog_id == "__none__"
      else policy_catalog_id.strip() or None
    )
    normalized_source_hierarchy_step_template_id = (
      None
      if not isinstance(source_hierarchy_step_template_id, str)
      else ""
      if source_hierarchy_step_template_id == "__none__"
      else source_hierarchy_step_template_id.strip() or None
    )
    normalized_sort = self._normalize_provider_provenance_scheduler_narrative_governance_plan_sort(sort)
    normalized_limit = max(1, min(limit, 100))
    filtered: list[ProviderProvenanceSchedulerNarrativeGovernancePlanRecord] = []
    for record in self._list_provider_provenance_scheduler_narrative_governance_plan_records():
      if normalized_item_type is not None and record.item_type != normalized_item_type:
        continue
      if normalized_status is not None and record.status != normalized_status:
        continue
      if (
        normalized_queue_state is not None
        and self._build_provider_provenance_scheduler_narrative_governance_queue_state(record.status)
        != normalized_queue_state
      ):
        continue
      if normalized_approval_lane is not None and record.approval_lane != normalized_approval_lane:
        continue
      if normalized_approval_priority is not None and record.approval_priority != normalized_approval_priority:
        continue
      if normalized_policy_template_id is not None and (record.policy_template_id or "") != normalized_policy_template_id:
        continue
      if normalized_policy_catalog_id is not None and (record.policy_catalog_id or "") != normalized_policy_catalog_id:
        continue
      if (
        normalized_source_hierarchy_step_template_id is not None
        and (record.source_hierarchy_step_template_id or "") != normalized_source_hierarchy_step_template_id
      ):
        continue
      if not self._matches_provider_provenance_workspace_search(
        values=(
          record.plan_id,
          record.item_type,
          record.action,
          record.reason,
          record.status,
          self._build_provider_provenance_scheduler_narrative_governance_queue_state(record.status),
          record.policy_template_id,
          record.policy_template_name,
          record.policy_catalog_id,
          record.policy_catalog_name,
          record.source_hierarchy_step_template_id,
          record.source_hierarchy_step_template_name,
          record.approval_lane,
          record.approval_priority,
          record.policy_guidance,
          record.hierarchy_key,
          record.hierarchy_name,
          record.created_by_tab_id,
          record.created_by_tab_label,
          *(
            item.item_name
            for item in record.preview_items
            if isinstance(item.item_name, str) and item.item_name.strip()
          ),
        ),
        search=search,
      ):
        continue
      filtered.append(record)
    pending_approval_count = sum(1 for record in filtered if record.status == "previewed")
    ready_to_apply_count = sum(1 for record in filtered if record.status == "approved")
    completed_count = sum(1 for record in filtered if record.status in {"applied", "rolled_back"})

    def _sort_source_template_value(
      record: ProviderProvenanceSchedulerNarrativeGovernancePlanRecord,
    ) -> str:
      return (
        record.source_hierarchy_step_template_name
        or record.source_hierarchy_step_template_id
        or ""
      ).lower()

    filtered.sort(key=lambda record: record.plan_id)
    filtered.sort(key=lambda record: record.updated_at, reverse=True)
    if normalized_sort == "queue_priority":
      filtered.sort(
        key=lambda record: self._build_provider_provenance_scheduler_narrative_governance_priority_rank(
          record.approval_priority
        ),
        reverse=True,
      )
      filtered.sort(
        key=lambda record: {
          "pending_approval": 0,
          "ready_to_apply": 1,
          "completed": 2,
        }[
          self._build_provider_provenance_scheduler_narrative_governance_queue_state(record.status)
        ]
      )
    elif normalized_sort == "updated_asc":
      filtered.sort(key=lambda record: record.updated_at)
    elif normalized_sort == "created_desc":
      filtered.sort(key=lambda record: record.created_at, reverse=True)
    elif normalized_sort == "created_asc":
      filtered.sort(key=lambda record: record.created_at)
    elif normalized_sort == "source_template_asc":
      filtered.sort(key=_sort_source_template_value)
    elif normalized_sort == "source_template_desc":
      filtered.sort(key=_sort_source_template_value, reverse=True)

    return ProviderProvenanceSchedulerNarrativeGovernancePlanListResult(
      items=tuple(filtered[:normalized_limit]),
      total=len(filtered),
      pending_approval_count=pending_approval_count,
      ready_to_apply_count=ready_to_apply_count,
      completed_count=completed_count,
    )

  def get_provider_provenance_scheduler_narrative_governance_plan(
    self,
    plan_id: str,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    normalized_plan_id = plan_id.strip()
    if not normalized_plan_id:
      raise LookupError("Provider provenance scheduler narrative governance plan not found.")
    record = self._load_provider_provenance_scheduler_narrative_governance_plan_record(normalized_plan_id)
    if record is None:
      raise LookupError("Provider provenance scheduler narrative governance plan not found.")
    return record

  def approve_provider_provenance_scheduler_narrative_governance_plan(
    self,
    plan_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    note: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_plan(plan_id)
    if current.status == "applied":
      raise RuntimeError("Applied governance plans cannot be approved again.")
    if current.status == "rolled_back":
      raise RuntimeError("Rolled-back governance plans cannot be approved again.")
    approved_at = self._clock()
    return self._save_provider_provenance_scheduler_narrative_governance_plan_record(
      replace(
        current,
        status="approved",
        updated_at=approved_at,
        approved_at=approved_at,
        approved_by_tab_id=(
          actor_tab_id.strip()
          if isinstance(actor_tab_id, str) and actor_tab_id.strip()
          else None
        ),
        approved_by_tab_label=(
          actor_tab_label.strip()
          if isinstance(actor_tab_label, str) and actor_tab_label.strip()
          else None
        ),
        approval_note=note.strip() if isinstance(note, str) and note.strip() else current.approval_note,
      )
    )

  def apply_provider_provenance_scheduler_narrative_governance_plan(
    self,
    plan_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_plan(plan_id)
    if current.status != "approved":
      raise RuntimeError("Approve the scheduler narrative governance plan before applying it.")
    request_payload = current.request_payload
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    for preview in current.preview_items:
      if preview.outcome == "skipped":
        skipped_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=preview.item_id,
            item_name=preview.item_name,
            outcome="skipped",
            status=preview.status,
            current_revision_id=preview.current_revision_id,
            message=preview.message,
          )
        )
        continue
      if preview.outcome == "failed":
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=preview.item_id,
            item_name=preview.item_name,
            outcome="failed",
            status=preview.status,
            current_revision_id=preview.current_revision_id,
            message=preview.message,
          )
        )
        continue
      try:
        if current.item_type == "template":
          existing = self.get_provider_provenance_scheduler_narrative_template(preview.item_id)
          if existing.current_revision_id != preview.current_revision_id:
            raise RuntimeError("Template drifted since the governance preview was created.")
          if current.action == "delete":
            updated = self.delete_provider_provenance_scheduler_narrative_template(
              preview.item_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          elif current.action == "restore":
            if not preview.apply_revision_id:
              raise RuntimeError("No restore revision was captured in the governance preview.")
            updated = self.restore_provider_provenance_scheduler_narrative_template_revision(
              preview.item_id,
              preview.apply_revision_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          else:
            updated_name = (
              f"{request_payload.get('name_prefix', '')}{existing.name}{request_payload.get('name_suffix', '')}"
            )
            updated_description = (
              f"{existing.description} {request_payload['description_append']}".strip()
              if isinstance(request_payload.get("description_append"), str)
              else existing.description
            )
            updated_query = self._build_provider_provenance_scheduler_narrative_bulk_template_query(
              existing.query,
              request_payload.get("query_patch"),
            )
            updated = self.update_provider_provenance_scheduler_narrative_template(
              preview.item_id,
              name=updated_name,
              description=updated_description,
              query=updated_query,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=updated.template_id,
              item_name=updated.name,
              outcome="applied",
              status=updated.status,
              current_revision_id=updated.current_revision_id,
              message=preview.message,
            )
          )
        elif current.item_type == "registry":
          existing = self.get_provider_provenance_scheduler_narrative_registry_entry(preview.item_id)
          if existing.current_revision_id != preview.current_revision_id:
            raise RuntimeError("Registry drifted since the governance preview was created.")
          if current.action == "delete":
            updated = self.delete_provider_provenance_scheduler_narrative_registry_entry(
              preview.item_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          elif current.action == "restore":
            if not preview.apply_revision_id:
              raise RuntimeError("No restore revision was captured in the governance preview.")
            updated = self.restore_provider_provenance_scheduler_narrative_registry_revision(
              preview.item_id,
              preview.apply_revision_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          else:
            updated_name = (
              f"{request_payload.get('name_prefix', '')}{existing.name}{request_payload.get('name_suffix', '')}"
            )
            updated_description = (
              f"{existing.description} {request_payload['description_append']}".strip()
              if isinstance(request_payload.get("description_append"), str)
              else existing.description
            )
            updated_query = self._build_provider_provenance_scheduler_narrative_bulk_template_query(
              existing.query,
              request_payload.get("query_patch"),
            )
            updated_layout = self._build_provider_provenance_scheduler_narrative_bulk_registry_layout(
              existing.layout,
              request_payload.get("layout_patch"),
            )
            updated_template_id = (
              ""
              if bool(request_payload.get("clear_template_link"))
              else (
                request_payload.get("template_id")
                if isinstance(request_payload.get("template_id"), str)
                else existing.template_id
              )
            )
            updated = self.update_provider_provenance_scheduler_narrative_registry_entry(
              preview.item_id,
              name=updated_name,
              description=updated_description,
              query=updated_query,
              layout=updated_layout,
              template_id=updated_template_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=updated.registry_id,
              item_name=updated.name,
              outcome="applied",
              status=updated.status,
              current_revision_id=updated.current_revision_id,
              message=preview.message,
            )
          )
        elif current.item_type == "stitched_report_governance_registry":
          existing = self.get_provider_provenance_scheduler_stitched_report_governance_registry(
            preview.item_id
          )
          if existing.current_revision_id != preview.current_revision_id:
            raise RuntimeError("Stitched governance registry drifted since the governance preview was created.")
          if current.action == "delete":
            updated = self.delete_provider_provenance_scheduler_stitched_report_governance_registry(
              preview.item_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          elif current.action == "restore":
            if not preview.apply_revision_id:
              raise RuntimeError("No restore revision was captured in the governance preview.")
            updated = self.restore_provider_provenance_scheduler_stitched_report_governance_registry_revision(
              preview.item_id,
              preview.apply_revision_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          else:
            updated_name = (
              f"{request_payload.get('name_prefix', '')}{existing.name}{request_payload.get('name_suffix', '')}"
            )
            updated_description = (
              f"{existing.description} {request_payload['description_append']}".strip()
              if isinstance(request_payload.get("description_append"), str)
              else existing.description
            )
            updated = self.update_provider_provenance_scheduler_stitched_report_governance_registry(
              preview.item_id,
              name=updated_name,
              description=updated_description,
              queue_view=(
                request_payload.get("queue_view_patch")
                if isinstance(request_payload.get("queue_view_patch"), dict)
                else existing.queue_view
              ),
              default_policy_template_id=(
                request_payload.get("default_policy_template_id")
                if isinstance(request_payload.get("default_policy_template_id"), str)
                else existing.default_policy_template_id
              ),
              default_policy_catalog_id=(
                request_payload.get("default_policy_catalog_id")
                if isinstance(request_payload.get("default_policy_catalog_id"), str)
                else existing.default_policy_catalog_id
              ),
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=updated.registry_id,
              item_name=updated.name,
              outcome="applied",
              status=updated.status,
              current_revision_id=updated.current_revision_id,
              message=preview.message,
            )
          )
        else:
          existing = self.get_provider_provenance_scheduler_stitched_report_view(preview.item_id)
          if existing.current_revision_id != preview.current_revision_id:
            raise RuntimeError("Stitched report view drifted since the governance preview was created.")
          if current.action == "delete":
            updated = self.delete_provider_provenance_scheduler_stitched_report_view(
              preview.item_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          elif current.action == "restore":
            if not preview.apply_revision_id:
              raise RuntimeError("No restore revision was captured in the governance preview.")
            updated = self.restore_provider_provenance_scheduler_stitched_report_view_revision(
              preview.item_id,
              preview.apply_revision_id,
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          else:
            updated_name = (
              f"{request_payload.get('name_prefix', '')}{existing.name}{request_payload.get('name_suffix', '')}"
            )
            updated_description = (
              f"{existing.description} {request_payload['description_append']}".strip()
              if isinstance(request_payload.get("description_append"), str)
              else existing.description
            )
            updated_query = self._build_provider_provenance_scheduler_stitched_report_view_bulk_query(
              existing.query,
              request_payload.get("query_patch"),
            )
            updated = self.update_provider_provenance_scheduler_stitched_report_view(
              preview.item_id,
              name=updated_name,
              description=updated_description,
              query=updated_query,
              occurrence_limit=(
                request_payload.get("occurrence_limit")
                if isinstance(request_payload.get("occurrence_limit"), int)
                else existing.occurrence_limit
              ),
              history_limit=(
                request_payload.get("history_limit")
                if isinstance(request_payload.get("history_limit"), int)
                else existing.history_limit
              ),
              drilldown_history_limit=(
                request_payload.get("drilldown_history_limit")
                if isinstance(request_payload.get("drilldown_history_limit"), int)
                else existing.drilldown_history_limit
              ),
              actor_tab_id=actor_tab_id,
              actor_tab_label=actor_tab_label,
              reason=current.reason,
            )
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=updated.view_id,
              item_name=updated.name,
              outcome="applied",
              status=updated.status,
              current_revision_id=updated.current_revision_id,
              message=preview.message,
            )
          )
        applied_count += 1
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=preview.item_id,
            item_name=preview.item_name,
            outcome="failed",
            message=str(exc),
          )
        )
    applied_result = ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type=current.item_type,
      action=current.action,
      reason=current.reason,
      requested_count=len(current.target_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )
    applied_at = self._clock()
    return self._save_provider_provenance_scheduler_narrative_governance_plan_record(
      replace(
        current,
        status="applied",
        updated_at=applied_at,
        applied_at=applied_at,
        applied_by_tab_id=(
          actor_tab_id.strip()
          if isinstance(actor_tab_id, str) and actor_tab_id.strip()
          else None
        ),
        applied_by_tab_label=(
          actor_tab_label.strip()
          if isinstance(actor_tab_label, str) and actor_tab_label.strip()
          else None
        ),
        applied_result=applied_result,
      )
    )

  def run_provider_provenance_scheduler_narrative_governance_plan_batch_action(
    self,
    *,
    action: str,
    plan_ids: Iterable[str],
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    note: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult:
    normalized_action = action.strip().lower()
    if normalized_action not in {"approve", "apply"}:
      raise ValueError("Unsupported scheduler narrative governance batch action.")
    normalized_plan_ids = self._normalize_provider_provenance_scheduler_narrative_bulk_ids(plan_ids)
    if not normalized_plan_ids:
      raise ValueError("Select at least one scheduler narrative governance plan.")
    results: list[ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult] = []
    succeeded_count = 0
    skipped_count = 0
    failed_count = 0
    for plan_id in normalized_plan_ids:
      try:
        current = self.get_provider_provenance_scheduler_narrative_governance_plan(plan_id)
        if normalized_action == "approve" and current.status == "approved":
          skipped_count += 1
          results.append(
            ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult(
              plan_id=current.plan_id,
              action=normalized_action,
              outcome="skipped",
              status=current.status,
              queue_state=self._build_provider_provenance_scheduler_narrative_governance_queue_state(
                current.status
              ),
              message="Plan is already approved.",
              plan=current,
            )
          )
          continue
        if normalized_action == "apply" and current.status == "applied":
          skipped_count += 1
          results.append(
            ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult(
              plan_id=current.plan_id,
              action=normalized_action,
              outcome="skipped",
              status=current.status,
              queue_state=self._build_provider_provenance_scheduler_narrative_governance_queue_state(
                current.status
              ),
              message="Plan is already applied.",
              plan=current,
            )
          )
          continue
        updated = (
          self.approve_provider_provenance_scheduler_narrative_governance_plan(
            current.plan_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            note=note,
          )
          if normalized_action == "approve"
          else self.apply_provider_provenance_scheduler_narrative_governance_plan(
            current.plan_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
          )
        )
        succeeded_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult(
            plan_id=updated.plan_id,
            action=normalized_action,
            outcome="succeeded",
            status=updated.status,
            queue_state=self._build_provider_provenance_scheduler_narrative_governance_queue_state(
              updated.status
            ),
            message=(
              "Plan approved for apply."
              if normalized_action == "approve"
              else "Approved governance plan applied."
            ),
            plan=updated,
          )
        )
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeGovernancePlanBatchItemResult(
            plan_id=plan_id,
            action=normalized_action,
            outcome="failed",
            message=str(exc),
          )
        )
    return ProviderProvenanceSchedulerNarrativeGovernancePlanBatchResult(
      action=normalized_action,
      requested_count=len(normalized_plan_ids),
      succeeded_count=succeeded_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )

  def rollback_provider_provenance_scheduler_narrative_governance_plan(
    self,
    plan_id: str,
    *,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
    note: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePlanRecord:
    current = self.get_provider_provenance_scheduler_narrative_governance_plan(plan_id)
    if current.status != "applied":
      raise RuntimeError("Only applied scheduler narrative governance plans can be rolled back.")
    results: list[ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult] = []
    applied_count = 0
    skipped_count = 0
    failed_count = 0
    for preview in current.preview_items:
      if preview.rollback_revision_id is None:
        skipped_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=preview.item_id,
            item_name=preview.item_name,
            outcome="skipped",
            message="No rollback revision was captured for this item.",
          )
        )
        continue
      try:
        if current.item_type == "template":
          updated = self.restore_provider_provenance_scheduler_narrative_template_revision(
            preview.item_id,
            preview.rollback_revision_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason="scheduler_narrative_template_governance_rollback",
          )
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=updated.template_id,
              item_name=updated.name,
              outcome="applied",
              status=updated.status,
              current_revision_id=updated.current_revision_id,
              message="Template restored to the pre-apply revision snapshot.",
            )
          )
        elif current.item_type == "registry":
          updated = self.restore_provider_provenance_scheduler_narrative_registry_revision(
            preview.item_id,
            preview.rollback_revision_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason="scheduler_narrative_registry_governance_rollback",
          )
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=updated.registry_id,
              item_name=updated.name,
              outcome="applied",
              status=updated.status,
              current_revision_id=updated.current_revision_id,
              message="Registry restored to the pre-apply revision snapshot.",
            )
          )
        elif current.item_type == "stitched_report_governance_registry":
          updated = self.restore_provider_provenance_scheduler_stitched_report_governance_registry_revision(
            preview.item_id,
            preview.rollback_revision_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason="scheduler_stitched_report_governance_registry_governance_rollback",
          )
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=updated.registry_id,
              item_name=updated.name,
              outcome="applied",
              status=updated.status,
              current_revision_id=updated.current_revision_id,
              message="Stitched governance registry restored to the pre-apply revision snapshot.",
            )
          )
        else:
          updated = self.restore_provider_provenance_scheduler_stitched_report_view_revision(
            preview.item_id,
            preview.rollback_revision_id,
            actor_tab_id=actor_tab_id,
            actor_tab_label=actor_tab_label,
            reason="scheduler_stitched_report_view_governance_rollback",
          )
          results.append(
            ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
              item_id=updated.view_id,
              item_name=updated.name,
              outcome="applied",
              status=updated.status,
              current_revision_id=updated.current_revision_id,
              message="Stitched report view restored to the pre-apply revision snapshot.",
            )
          )
        applied_count += 1
      except (LookupError, RuntimeError, ValueError) as exc:
        failed_count += 1
        results.append(
          ProviderProvenanceSchedulerNarrativeBulkGovernanceItemResult(
            item_id=preview.item_id,
            item_name=preview.item_name,
            outcome="failed",
            message=str(exc),
          )
        )
    rollback_result = ProviderProvenanceSchedulerNarrativeBulkGovernanceResult(
      item_type=current.item_type,
      action="rollback",
      reason=current.reason,
      requested_count=len(current.target_ids),
      applied_count=applied_count,
      skipped_count=skipped_count,
      failed_count=failed_count,
      results=tuple(results),
    )
    rolled_back_at = self._clock()
    return self._save_provider_provenance_scheduler_narrative_governance_plan_record(
      replace(
        current,
        status="rolled_back",
        updated_at=rolled_back_at,
        rolled_back_at=rolled_back_at,
        rolled_back_by_tab_id=(
          actor_tab_id.strip()
          if isinstance(actor_tab_id, str) and actor_tab_id.strip()
          else None
        ),
        rolled_back_by_tab_label=(
          actor_tab_label.strip()
          if isinstance(actor_tab_label, str) and actor_tab_label.strip()
          else None
        ),
        rollback_note=note.strip() if isinstance(note, str) and note.strip() else current.rollback_note,
        rollback_result=rollback_result,
      )
    )

