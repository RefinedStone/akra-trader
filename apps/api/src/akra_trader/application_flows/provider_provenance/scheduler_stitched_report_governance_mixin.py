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

from akra_trader.domain.models import *  # noqa: F403


class ProviderProvenanceSchedulerStitchedReportGovernanceMixin:
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
