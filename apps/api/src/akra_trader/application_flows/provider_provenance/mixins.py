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
from akra_trader.application_flows.provider_provenance.scheduler_narrative_governance_mixin import ProviderProvenanceSchedulerNarrativeGovernanceMixin
from akra_trader.application_flows.provider_provenance.scheduler_stitched_report_mixin import ProviderProvenanceSchedulerStitchedReportMixin
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
  ProviderProvenanceSchedulerNarrativeGovernanceMixin,
  ProviderProvenanceSchedulerStitchedReportMixin,
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

  @staticmethod
  def _normalize_provider_provenance_scheduler_narrative_record_status(
    value: str | None,
  ) -> str:
    normalized_value = value.strip() if isinstance(value, str) else ""
    return "deleted" if normalized_value == "deleted" else "active"

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
