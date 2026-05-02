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


class ProviderProvenanceCompatibilityStorageMixin:
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
