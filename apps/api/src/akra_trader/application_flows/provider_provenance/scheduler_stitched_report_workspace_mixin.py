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


class ProviderProvenanceSchedulerStitchedReportWorkspaceMixin:
  def _build_provider_provenance_scheduler_narrative_template_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeTemplateRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord:
    revision_count = sum(
      1
      for revision in self._list_provider_provenance_scheduler_narrative_template_revision_records()
      if revision.template_id == record.template_id
    )
    return ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord(
      revision_id=f"{record.template_id}:r{revision_count + 1:04d}",
      template_id=record.template_id,
      action=action,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      name=record.name,
      description=record.description,
      query=deepcopy(record.query),
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
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

  def _record_provider_provenance_scheduler_narrative_template_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeTemplateRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeTemplateRecord:
    revision = self._save_provider_provenance_scheduler_narrative_template_revision_record(
      self._build_provider_provenance_scheduler_narrative_template_revision(
        record=record,
        action=action,
        reason=reason,
        recorded_at=recorded_at,
        source_revision_id=source_revision_id,
        actor_tab_id=actor_tab_id,
        actor_tab_label=actor_tab_label,
      )
    )
    return self._save_provider_provenance_scheduler_narrative_template_record(
      replace(
        record,
        current_revision_id=revision.revision_id,
        revision_count=int(record.revision_count or 0) + 1,
      )
    )

  def _build_provider_provenance_scheduler_narrative_registry_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeRegistryRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord:
    revision_count = sum(
      1
      for revision in self._list_provider_provenance_scheduler_narrative_registry_revision_records()
      if revision.registry_id == record.registry_id
    )
    return ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord(
      revision_id=f"{record.registry_id}:r{revision_count + 1:04d}",
      registry_id=record.registry_id,
      action=action,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      name=record.name,
      description=record.description,
      query=deepcopy(record.query),
      layout=deepcopy(record.layout),
      template_id=record.template_id,
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
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

  def _record_provider_provenance_scheduler_narrative_registry_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeRegistryRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeRegistryRecord:
    revision = self._save_provider_provenance_scheduler_narrative_registry_revision_record(
      self._build_provider_provenance_scheduler_narrative_registry_revision(
        record=record,
        action=action,
        reason=reason,
        recorded_at=recorded_at,
        source_revision_id=source_revision_id,
        actor_tab_id=actor_tab_id,
        actor_tab_label=actor_tab_label,
      )
    )
    return self._save_provider_provenance_scheduler_narrative_registry_record(
      replace(
        record,
        current_revision_id=revision.revision_id,
        revision_count=int(record.revision_count or 0) + 1,
      )
    )

  def _build_provider_provenance_scheduler_narrative_governance_policy_template_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord:
    revision_count = sum(
      1
      for revision in self._list_provider_provenance_scheduler_narrative_governance_policy_template_revision_records()
      if revision.policy_template_id == record.policy_template_id
    )
    return ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord(
      revision_id=f"{record.policy_template_id}:r{revision_count + 1:04d}",
      policy_template_id=record.policy_template_id,
      action=action,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      name=record.name,
      description=record.description,
      item_type_scope=record.item_type_scope,
      action_scope=record.action_scope,
      approval_lane=record.approval_lane,
      approval_priority=record.approval_priority,
      guidance=record.guidance,
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
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
  def _build_provider_provenance_scheduler_narrative_governance_policy_template_audit_detail(
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
    action: str,
  ) -> str:
    scope = f"{record.item_type_scope}/{record.action_scope}"
    lane = f"{record.approval_lane}/{record.approval_priority}"
    if action == "created":
      return f"Created governance policy template {record.name} for {scope} on {lane}."
    if action == "updated":
      return f"Updated governance policy template {record.name} for {scope} on {lane}."
    if action == "deleted":
      return f"Deleted governance policy template {record.name}."
    if action == "restored":
      return f"Restored governance policy template {record.name}."
    return f"Recorded governance policy template action {action} for {record.name}."

  def _record_provider_provenance_scheduler_narrative_governance_policy_template_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord:
    revision = self._save_provider_provenance_scheduler_narrative_governance_policy_template_revision_record(
      self._build_provider_provenance_scheduler_narrative_governance_policy_template_revision(
        record=record,
        action=action,
        reason=reason,
        recorded_at=recorded_at,
        source_revision_id=source_revision_id,
        actor_tab_id=actor_tab_id,
        actor_tab_label=actor_tab_label,
      )
    )
    updated = self._save_provider_provenance_scheduler_narrative_governance_policy_template_record(
      replace(
        record,
        current_revision_id=revision.revision_id,
        revision_count=int(record.revision_count or 0) + 1,
      )
    )
    self._save_provider_provenance_scheduler_narrative_governance_policy_template_audit_record(
      ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord(
        audit_id=f"{updated.policy_template_id}:{revision.revision_id}:{action}",
        policy_template_id=updated.policy_template_id,
        action=action,
        recorded_at=recorded_at,
        reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
        detail=self._build_provider_provenance_scheduler_narrative_governance_policy_template_audit_detail(
          record=updated,
          action=action,
        ),
        revision_id=revision.revision_id,
        source_revision_id=source_revision_id,
        name=updated.name,
        status=updated.status,
        item_type_scope=updated.item_type_scope,
        action_scope=updated.action_scope,
        approval_lane=updated.approval_lane,
        approval_priority=updated.approval_priority,
        guidance=updated.guidance,
        actor_tab_id=revision.recorded_by_tab_id,
        actor_tab_label=revision.recorded_by_tab_label,
      )
    )
    return updated

  def _build_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord:
    record = self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(record)
    revision_count = sum(
      1
      for revision in self._list_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_records()
      if revision.catalog_id == record.catalog_id
    )
    return ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord(
      revision_id=f"{record.catalog_id}:r{revision_count + 1:04d}",
      catalog_id=record.catalog_id,
      action=action,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      name=record.name,
      description=record.description,
      policy_template_ids=tuple(record.policy_template_ids),
      policy_template_names=tuple(record.policy_template_names),
      default_policy_template_id=record.default_policy_template_id,
      default_policy_template_name=record.default_policy_template_name,
      item_type_scope=record.item_type_scope,
      action_scope=record.action_scope,
      approval_lane=record.approval_lane,
      approval_priority=record.approval_priority,
      guidance=record.guidance,
      hierarchy_steps=tuple(record.hierarchy_steps),
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
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

  def _build_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_detail(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
    action: str,
  ) -> str:
    template_summary = ", ".join(record.policy_template_names) if record.policy_template_names else "no templates"
    default_summary = record.default_policy_template_name or "no default"
    lane = f"{record.approval_lane}/{record.approval_priority}"
    hierarchy_summary = self._summarize_provider_provenance_scheduler_narrative_governance_plan_hierarchy_steps(
      record.hierarchy_steps
    )
    if action == "created":
      return (
        f"Created governance policy catalog {record.name} with default {default_summary} and linked templates "
        f"{template_summary} on {lane}. {hierarchy_summary}"
      )
    if action == "updated":
      return (
        f"Updated governance policy catalog {record.name}; default {default_summary}, linked templates "
        f"{template_summary}. {hierarchy_summary}"
      )
    if action == "hierarchy_captured":
      return f"Captured reusable governance hierarchy for policy catalog {record.name}. {hierarchy_summary}"
    if action == "staged":
      return f"Staged reusable governance hierarchy for policy catalog {record.name}. {hierarchy_summary}"
    if action == "hierarchy_step_updated":
      return f"Updated one hierarchy step on policy catalog {record.name}. {hierarchy_summary}"
    if action == "hierarchy_step_restored":
      return f"Restored one hierarchy step from revision history on policy catalog {record.name}. {hierarchy_summary}"
    if action == "hierarchy_steps_bulk_updated":
      return f"Applied bulk hierarchy step updates on policy catalog {record.name}. {hierarchy_summary}"
    if action == "hierarchy_steps_bulk_deleted":
      return f"Deleted one or more hierarchy steps from policy catalog {record.name}. {hierarchy_summary}"
    if action == "deleted":
      return f"Deleted governance policy catalog {record.name}."
    if action == "restored":
      return f"Restored governance policy catalog {record.name}."
    return f"Recorded governance policy catalog action {action} for {record.name}."

  def _record_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord:
    record = self._materialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(record)
    revision = self._save_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_record(
      self._build_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
        record=record,
        action=action,
        reason=reason,
        recorded_at=recorded_at,
        source_revision_id=source_revision_id,
        actor_tab_id=actor_tab_id,
        actor_tab_label=actor_tab_label,
      )
    )
    updated = self._save_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
      replace(
        record,
        current_revision_id=revision.revision_id,
        revision_count=int(record.revision_count or 0) + 1,
      )
    )
    self._save_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_record(
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord(
        audit_id=f"{updated.catalog_id}:{revision.revision_id}:{action}",
        catalog_id=updated.catalog_id,
        action=action,
        recorded_at=recorded_at,
        reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
        detail=self._build_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_detail(
          record=updated,
          action=action,
        ),
        revision_id=revision.revision_id,
        source_revision_id=source_revision_id,
        name=updated.name,
        status=updated.status,
        default_policy_template_id=updated.default_policy_template_id,
        default_policy_template_name=updated.default_policy_template_name,
        policy_template_ids=tuple(updated.policy_template_ids),
        policy_template_names=tuple(updated.policy_template_names),
        item_type_scope=updated.item_type_scope,
        action_scope=updated.action_scope,
        approval_lane=updated.approval_lane,
        approval_priority=updated.approval_priority,
        guidance=updated.guidance,
        hierarchy_steps=tuple(updated.hierarchy_steps),
        actor_tab_id=revision.recorded_by_tab_id,
        actor_tab_label=revision.recorded_by_tab_label,
      )
    )
    return updated

  def _build_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord:
    revision_count = sum(
      1
      for revision in self._list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_records()
      if revision.hierarchy_step_template_id == record.hierarchy_step_template_id
    )
    return ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord(
      revision_id=f"{record.hierarchy_step_template_id}:r{revision_count + 1:04d}",
      hierarchy_step_template_id=record.hierarchy_step_template_id,
      action=action,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      name=record.name,
      description=record.description,
      item_type=record.item_type,
      step=record.step,
      origin_catalog_id=record.origin_catalog_id,
      origin_catalog_name=record.origin_catalog_name,
      origin_step_id=record.origin_step_id,
      governance_policy_template_id=record.governance_policy_template_id,
      governance_policy_template_name=record.governance_policy_template_name,
      governance_policy_catalog_id=record.governance_policy_catalog_id,
      governance_policy_catalog_name=record.governance_policy_catalog_name,
      governance_approval_lane=record.governance_approval_lane,
      governance_approval_priority=record.governance_approval_priority,
      governance_policy_guidance=record.governance_policy_guidance,
      status=self._normalize_provider_provenance_scheduler_narrative_record_status(record.status),
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

  def _build_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_detail(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord,
    action: str,
  ) -> str:
    summary = self.format_provider_provenance_scheduler_narrative_governance_hierarchy_step_summary(
      record.step
    )
    origin = record.origin_catalog_name or "ad hoc source"
    policy = (
      record.governance_policy_template_name
      or record.governance_policy_catalog_name
      or f"{record.governance_approval_lane}/{record.governance_approval_priority}"
    )
    if action == "created":
      return f"Created hierarchy step template {record.name} from {origin} on {policy}. {summary}"
    if action == "updated":
      return f"Updated hierarchy step template {record.name} on {policy}. {summary}"
    if action == "deleted":
      return f"Deleted hierarchy step template {record.name}."
    if action == "restored":
      return f"Restored hierarchy step template {record.name} on {policy}. {summary}"
    if action == "staged":
      return f"Staged hierarchy step template {record.name} into the approval queue on {policy}. {summary}"
    return f"Recorded hierarchy step template action {action} for {record.name}. {summary}"

  def _record_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord:
    revision = self._save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_record(
      self._build_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
        record=record,
        action=action,
        reason=reason,
        recorded_at=recorded_at,
        source_revision_id=source_revision_id,
        actor_tab_id=actor_tab_id,
        actor_tab_label=actor_tab_label,
      )
    )
    updated = self._save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record(
      replace(
        record,
        current_revision_id=revision.revision_id,
        revision_count=int(record.revision_count or 0) + 1,
      )
    )
    self._save_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_record(
      ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord(
        audit_id=f"{updated.hierarchy_step_template_id}:{revision.revision_id}:{action}",
        hierarchy_step_template_id=updated.hierarchy_step_template_id,
        action=action,
        recorded_at=recorded_at,
        reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
        detail=self._build_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_detail(
          record=updated,
          action=action,
        ),
        revision_id=revision.revision_id,
        source_revision_id=source_revision_id,
        name=updated.name,
        description=updated.description,
        item_type=updated.item_type,
        step=updated.step,
        origin_catalog_id=updated.origin_catalog_id,
        origin_catalog_name=updated.origin_catalog_name,
        origin_step_id=updated.origin_step_id,
        governance_policy_template_id=updated.governance_policy_template_id,
        governance_policy_template_name=updated.governance_policy_template_name,
        governance_policy_catalog_id=updated.governance_policy_catalog_id,
        governance_policy_catalog_name=updated.governance_policy_catalog_name,
        governance_approval_lane=updated.governance_approval_lane,
        governance_approval_priority=updated.governance_approval_priority,
        governance_policy_guidance=updated.governance_policy_guidance,
        status=updated.status,
        actor_tab_id=revision.recorded_by_tab_id,
        actor_tab_label=revision.recorded_by_tab_label,
      )
    )
    return updated

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
