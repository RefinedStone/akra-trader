from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Iterable
from typing import Mapping
from uuid import uuid4

from akra_trader.application_support.provider_governance_catalog_plan_workflows import (
  apply_provider_provenance_scheduler_search_moderation_catalog_governance_plan as apply_provider_provenance_scheduler_search_moderation_catalog_governance_plan_support,
)
from akra_trader.application_support.provider_governance_catalog_plan_workflows import (
  approve_provider_provenance_scheduler_search_moderation_catalog_governance_plan as approve_provider_provenance_scheduler_search_moderation_catalog_governance_plan_support,
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
  apply_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan as apply_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_support,
)
from akra_trader.application_support.provider_governance_meta_workflows import (
  approve_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan as approve_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_support,
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
from akra_trader.domain.models import *  # noqa: F403


class ProviderProvenanceSearchModerationSupportMixin:
  @staticmethod
  def _normalize_provider_provenance_scheduler_search_moderation_plan_status(
    status: str | None,
  ) -> str | None:
    if not isinstance(status, str):
      return None
    normalized = status.strip().lower().replace("-", "_")
    if normalized in {"previewed", "approved", "applied"}:
      return normalized
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_moderation_plan_queue_state(
    queue_state: str | None,
  ) -> str | None:
    if not isinstance(queue_state, str):
      return None
    normalized = queue_state.strip().lower().replace("-", "_")
    if normalized in {"pending_approval", "ready_to_apply", "completed"}:
      return normalized
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_moderation_catalog_governance_action(
    action: str | None,
  ) -> str | None:
    if not isinstance(action, str):
      return None
    normalized = action.strip().lower().replace("-", "_")
    if normalized in {"update", "delete", "restore"}:
      return normalized
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_moderation_catalog_governance_action_scope(
    action_scope: str | None,
  ) -> str | None:
    if not isinstance(action_scope, str):
      return None
    normalized = action_scope.strip().lower().replace("-", "_")
    if normalized in {"any", "update", "delete", "restore"}:
      return normalized
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_status(
    status: str | None,
  ) -> str | None:
    if not isinstance(status, str):
      return None
    normalized = status.strip().lower().replace("-", "_")
    if normalized in {"previewed", "approved", "applied"}:
      return normalized
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_queue_state(
    queue_state: str | None,
  ) -> str | None:
    if not isinstance(queue_state, str):
      return None
    normalized = queue_state.strip().lower().replace("-", "_")
    if normalized in {"pending_approval", "ready_to_apply", "completed"}:
      return normalized
    return None

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_status(
    status: str | None,
  ) -> str:
    return normalize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_status_support(
      status
    )

  def _build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord:
    return build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_support(
      self,
      record=record,
      action=action,
      reason=reason,
      recorded_at=recorded_at,
      source_revision_id=source_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  @staticmethod
  def _build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_detail(
    *,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
    action: str,
  ) -> str:
    return build_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_detail_support(
      record=record,
      action=action,
    )

  def _record_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
    return record_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_support(
      self,
      record=record,
      action=action,
      reason=reason,
      recorded_at=recorded_at,
      source_revision_id=source_revision_id,
      actor_tab_id=actor_tab_id,
      actor_tab_label=actor_tab_label,
    )

  @staticmethod
  def _normalize_provider_provenance_scheduler_search_moderation_policy_catalog_status(
    status: str | None,
  ) -> str:
    if not isinstance(status, str):
      return "active"
    normalized = status.strip().lower().replace("-", "_")
    return "deleted" if normalized == "deleted" else "active"

  def _build_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord:
    revision_count = sum(
      1
      for revision in self._list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records()
      if revision.catalog_id == record.catalog_id
    )
    return ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord(
      revision_id=f"{record.catalog_id}:r{revision_count + 1:04d}",
      catalog_id=record.catalog_id,
      action=action,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      name=record.name,
      description=record.description,
      scheduler_key=record.scheduler_key,
      status=self._normalize_provider_provenance_scheduler_search_moderation_policy_catalog_status(
        record.status
      ),
      default_moderation_status=record.default_moderation_status,
      governance_view=record.governance_view,
      window_days=record.window_days,
      stale_pending_hours=record.stale_pending_hours,
      minimum_score=record.minimum_score,
      require_note=record.require_note,
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
  def _build_provider_provenance_scheduler_search_moderation_policy_catalog_audit_detail(
    *,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
    action: str,
  ) -> str:
    default_summary = (
      f"{record.default_moderation_status} @ {record.minimum_score}+"
      if record.minimum_score > 0
      else record.default_moderation_status
    )
    governance_summary = (
      f"{record.governance_view} / {record.window_days}d / stale {record.stale_pending_hours}h"
    )
    if action == "created":
      return (
        f"Created moderation policy catalog {record.name} with {default_summary}; "
        f"view {governance_summary}; note {'required' if record.require_note else 'optional'}."
      )
    if action == "updated":
      return (
        f"Updated moderation policy catalog {record.name}; "
        f"{default_summary}; view {governance_summary}."
      )
    if action == "deleted":
      return f"Deleted moderation policy catalog {record.name}."
    if action == "restored":
      return f"Restored moderation policy catalog {record.name}."
    if action == "bulk_updated":
      return f"Bulk-updated moderation policy catalog {record.name}."
    if action == "bulk_deleted":
      return f"Bulk-deleted moderation policy catalog {record.name}."
    if action == "bulk_restored":
      return f"Bulk-restored moderation policy catalog {record.name}."
    return f"Recorded moderation policy catalog action {action} for {record.name}."

  def _record_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord:
    revision = self._save_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
      self._build_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
        record=record,
        action=action,
        reason=reason,
        recorded_at=recorded_at,
        source_revision_id=source_revision_id,
        actor_tab_id=actor_tab_id,
        actor_tab_label=actor_tab_label,
      )
    )
    saved = self._save_provider_provenance_scheduler_search_moderation_policy_catalog_record(
      replace(
        record,
        status=self._normalize_provider_provenance_scheduler_search_moderation_policy_catalog_status(
          record.status
        ),
        current_revision_id=revision.revision_id,
        revision_count=int(record.revision_count or 0) + 1,
      )
    )
    self._save_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
      ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord(
        audit_id=uuid4().hex[:12],
        catalog_id=saved.catalog_id,
        action=action,
        recorded_at=recorded_at,
        reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
        detail=self._build_provider_provenance_scheduler_search_moderation_policy_catalog_audit_detail(
          record=saved,
          action=action,
        ),
        revision_id=revision.revision_id,
        source_revision_id=source_revision_id,
        scheduler_key=saved.scheduler_key,
        name=saved.name,
        status=saved.status,
        default_moderation_status=saved.default_moderation_status,
        governance_view=saved.governance_view,
        window_days=saved.window_days,
        stale_pending_hours=saved.stale_pending_hours,
        minimum_score=saved.minimum_score,
        require_note=saved.require_note,
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
    return saved

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_policy_catalog_record(
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
  ) -> dict[str, Any]:
    return {
      "catalog_id": record.catalog_id,
      "created_at": record.created_at,
      "updated_at": record.updated_at,
      "scheduler_key": record.scheduler_key,
      "name": record.name,
      "description": record.description,
      "status": record.status,
      "default_moderation_status": record.default_moderation_status,
      "governance_view": record.governance_view,
      "window_days": record.window_days,
      "stale_pending_hours": record.stale_pending_hours,
      "minimum_score": record.minimum_score,
      "require_note": record.require_note,
      "current_revision_id": record.current_revision_id,
      "revision_count": record.revision_count,
      "created_by_tab_id": record.created_by_tab_id,
      "created_by_tab_label": record.created_by_tab_label,
      "deleted_at": record.deleted_at,
      "deleted_by_tab_id": record.deleted_by_tab_id,
      "deleted_by_tab_label": record.deleted_by_tab_label,
    }

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord,
  ) -> dict[str, Any]:
    return {
      "revision_id": record.revision_id,
      "catalog_id": record.catalog_id,
      "action": record.action,
      "reason": record.reason,
      "name": record.name,
      "description": record.description,
      "scheduler_key": record.scheduler_key,
      "status": record.status,
      "default_moderation_status": record.default_moderation_status,
      "governance_view": record.governance_view,
      "window_days": record.window_days,
      "stale_pending_hours": record.stale_pending_hours,
      "minimum_score": record.minimum_score,
      "require_note": record.require_note,
      "recorded_at": record.recorded_at,
      "source_revision_id": record.source_revision_id,
      "recorded_by_tab_id": record.recorded_by_tab_id,
      "recorded_by_tab_label": record.recorded_by_tab_label,
    }

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord,
  ) -> dict[str, Any]:
    return {
      "audit_id": record.audit_id,
      "catalog_id": record.catalog_id,
      "action": record.action,
      "recorded_at": record.recorded_at,
      "reason": record.reason,
      "detail": record.detail,
      "revision_id": record.revision_id,
      "source_revision_id": record.source_revision_id,
      "scheduler_key": record.scheduler_key,
      "name": record.name,
      "status": record.status,
      "default_moderation_status": record.default_moderation_status,
      "governance_view": record.governance_view,
      "window_days": record.window_days,
      "stale_pending_hours": record.stale_pending_hours,
      "minimum_score": record.minimum_score,
      "require_note": record.require_note,
      "actor_tab_id": record.actor_tab_id,
      "actor_tab_label": record.actor_tab_label,
    }

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_plan_preview_item(
    item: ProviderProvenanceSchedulerSearchModerationPlanPreviewItem,
  ) -> dict[str, Any]:
    return {
      "feedback_id": item.feedback_id,
      "occurrence_id": item.occurrence_id,
      "query": item.query,
      "signal": item.signal,
      "current_moderation_status": item.current_moderation_status,
      "proposed_moderation_status": item.proposed_moderation_status,
      "score": item.score,
      "age_hours": item.age_hours,
      "stale_pending": item.stale_pending,
      "high_score_pending": item.high_score_pending,
      "query_run_count": item.query_run_count,
      "eligible": item.eligible,
      "reason_tags": tuple(item.reason_tags),
      "matched_fields": tuple(item.matched_fields),
      "semantic_concepts": tuple(item.semantic_concepts),
      "operator_hits": tuple(item.operator_hits),
      "note": item.note,
      "ranking_reason": item.ranking_reason,
    }

  def _serialize_provider_provenance_scheduler_search_moderation_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPlanRecord,
  ) -> dict[str, Any]:
    return {
      "plan_id": record.plan_id,
      "created_at": record.created_at,
      "updated_at": record.updated_at,
      "scheduler_key": record.scheduler_key,
      "status": record.status,
      "queue_state": record.queue_state,
      "policy_catalog_id": record.policy_catalog_id,
      "policy_catalog_name": record.policy_catalog_name,
      "proposed_moderation_status": record.proposed_moderation_status,
      "governance_view": record.governance_view,
      "window_days": record.window_days,
      "stale_pending_hours": record.stale_pending_hours,
      "minimum_score": record.minimum_score,
      "require_note": record.require_note,
      "requested_feedback_ids": tuple(record.requested_feedback_ids),
      "feedback_ids": tuple(record.feedback_ids),
      "missing_feedback_ids": tuple(record.missing_feedback_ids),
      "preview_count": len(record.preview_items),
      "preview_items": tuple(
        self._serialize_provider_provenance_scheduler_search_moderation_plan_preview_item(item)
        for item in record.preview_items
      ),
      "created_by": record.created_by,
      "created_by_tab_id": record.created_by_tab_id,
      "created_by_tab_label": record.created_by_tab_label,
      "approved_at": record.approved_at,
      "approved_by": record.approved_by,
      "approved_by_tab_id": record.approved_by_tab_id,
      "approved_by_tab_label": record.approved_by_tab_label,
      "approval_note": record.approval_note,
      "applied_at": record.applied_at,
      "applied_by": record.applied_by,
      "applied_by_tab_id": record.applied_by_tab_id,
      "applied_by_tab_label": record.applied_by_tab_label,
      "apply_note": record.apply_note,
      "applied_result": record.applied_result,
    }

  def _get_provider_provenance_scheduler_search_moderation_policy_catalog_record(
    self,
    catalog_id: str,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord:
    normalized_catalog_id = catalog_id.strip() if isinstance(catalog_id, str) else ""
    for record in self._list_provider_provenance_scheduler_search_moderation_policy_catalog_records():
      if record.catalog_id == normalized_catalog_id:
        return replace(
          record,
          status=self._normalize_provider_provenance_scheduler_search_moderation_policy_catalog_status(
            record.status
          ),
        )
    raise LookupError("Scheduler search moderation policy catalog not found.")

  def _load_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord | None:
    normalized_revision_id = revision_id.strip() if isinstance(revision_id, str) else ""
    if not normalized_revision_id:
      return None
    for revision in self._list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records():
      if revision.revision_id == normalized_revision_id:
        return revision
    return None

  def _get_provider_provenance_scheduler_search_moderation_plan_record(
    self,
    plan_id: str,
  ) -> ProviderProvenanceSchedulerSearchModerationPlanRecord:
    normalized_plan_id = plan_id.strip() if isinstance(plan_id, str) else ""
    for record in self._list_provider_provenance_scheduler_search_moderation_plan_records():
      if record.plan_id == normalized_plan_id:
        return record
    raise LookupError("Scheduler search moderation plan not found.")

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
  ) -> dict[str, Any]:
    return serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record_support(
      record
    )

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord,
  ) -> dict[str, Any]:
    return serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record_support(
      record
    )

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord,
  ) -> dict[str, Any]:
    return serialize_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record_support(
      record
    )

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_preview_item(
    item: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanPreviewItem,
  ) -> dict[str, Any]:
    return serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_preview_item_support(
      item
    )

  def _serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord,
  ) -> dict[str, Any]:
    return serialize_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record_support(
      record
    )

  def _get_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    self,
    governance_policy_id: str,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
    return get_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record_support(
      self,
      governance_policy_id,
    )

  def _load_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord | None:
    return load_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record_support(
      self,
      revision_id,
    )

  def _get_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    self,
    plan_id: str,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord:
    return get_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record_support(
      self,
      plan_id,
    )

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord,
  ) -> dict[str, Any]:
    return serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record_support(
      record
    )

  @staticmethod
  def _serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_preview_item(
    item: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPreviewItem,
  ) -> dict[str, Any]:
    return serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_preview_item_support(
      item
    )

  def _serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord,
  ) -> dict[str, Any]:
    return serialize_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record_support(
      record
    )

  def _get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
    self,
    meta_policy_id: str,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord:
    return get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record_support(
      self,
      meta_policy_id,
    )

  def _get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    self,
    plan_id: str,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord:
    return get_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record_support(
      self,
      plan_id,
    )
