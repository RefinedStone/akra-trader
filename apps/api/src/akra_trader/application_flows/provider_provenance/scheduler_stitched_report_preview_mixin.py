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


class ProviderProvenanceSchedulerStitchedReportPreviewMixin:
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
