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


class ProviderProvenanceCompatibilitySchedulerAlertsMixin:
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
