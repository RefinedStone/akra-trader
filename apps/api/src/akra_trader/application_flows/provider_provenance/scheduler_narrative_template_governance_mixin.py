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


class ProviderProvenanceSchedulerNarrativeTemplateGovernanceMixin:
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
