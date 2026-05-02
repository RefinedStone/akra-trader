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


class ProviderProvenanceSchedulerStitchedReportViewsMixin:
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
