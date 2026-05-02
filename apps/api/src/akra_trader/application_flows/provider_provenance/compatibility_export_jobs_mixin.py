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


class ProviderProvenanceCompatibilityExportJobsMixin:
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
