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


class ProviderProvenanceSchedulerNarrativeRegistryGovernanceMixin:
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
