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
from akra_trader.application_flows.provider_provenance.scheduler_narrative_governance_normalization_mixin import (
  ProviderProvenanceSchedulerNarrativeGovernanceNormalizationMixin,
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


class ProviderProvenanceCompatibilityWorkspacesMixin:
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
      ProviderProvenanceSchedulerNarrativeGovernanceNormalizationMixin._normalize_provider_provenance_scheduler_narrative_governance_queue_view_payload(
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
