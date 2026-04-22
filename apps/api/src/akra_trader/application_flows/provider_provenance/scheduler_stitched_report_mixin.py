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


class ProviderProvenanceSchedulerStitchedReportMixin:
  def _save_provider_provenance_scheduler_stitched_report_view_record(
    self,
    record: ProviderProvenanceSchedulerStitchedReportViewRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRecord:
    save_view = getattr(self._runs, "save_provider_provenance_scheduler_stitched_report_view", None)
    if callable(save_view):
      return save_view(record)
    self._provider_provenance_scheduler_stitched_report_views[record.view_id] = record
    return record

  def _load_provider_provenance_scheduler_stitched_report_view_record(
    self,
    view_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRecord | None:
    get_view = getattr(self._runs, "get_provider_provenance_scheduler_stitched_report_view", None)
    if callable(get_view):
      return get_view(view_id)
    return self._provider_provenance_scheduler_stitched_report_views.get(view_id)

  def _list_provider_provenance_scheduler_stitched_report_view_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportViewRecord, ...]:
    list_views = getattr(self._runs, "list_provider_provenance_scheduler_stitched_report_views", None)
    if callable(list_views):
      return tuple(list_views())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_views.values(),
        key=lambda record: (record.updated_at, record.view_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_stitched_report_view_revision_record(
    self,
    record: ProviderProvenanceSchedulerStitchedReportViewRevisionRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRevisionRecord:
    save_revision = getattr(self._runs, "save_provider_provenance_scheduler_stitched_report_view_revision", None)
    if callable(save_revision):
      return save_revision(record)
    self._provider_provenance_scheduler_stitched_report_view_revisions[record.revision_id] = record
    return record

  def _load_provider_provenance_scheduler_stitched_report_view_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRevisionRecord | None:
    get_revision = getattr(self._runs, "get_provider_provenance_scheduler_stitched_report_view_revision", None)
    if callable(get_revision):
      return get_revision(revision_id)
    return self._provider_provenance_scheduler_stitched_report_view_revisions.get(revision_id)

  def _list_provider_provenance_scheduler_stitched_report_view_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportViewRevisionRecord, ...]:
    list_revisions = getattr(self._runs, "list_provider_provenance_scheduler_stitched_report_view_revisions", None)
    if callable(list_revisions):
      return tuple(list_revisions())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_view_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_stitched_report_view_audit_record(
    self,
    record: ProviderProvenanceSchedulerStitchedReportViewAuditRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportViewAuditRecord:
    save_audit = getattr(self._runs, "save_provider_provenance_scheduler_stitched_report_view_audit_record", None)
    if callable(save_audit):
      return save_audit(record)
    self._provider_provenance_scheduler_stitched_report_view_audit_records[record.audit_id] = record
    return record

  def _list_provider_provenance_scheduler_stitched_report_view_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportViewAuditRecord, ...]:
    list_audits = getattr(self._runs, "list_provider_provenance_scheduler_stitched_report_view_audit_records", None)
    if callable(list_audits):
      return tuple(list_audits())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_view_audit_records.values(),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_stitched_report_governance_registry_record(
    self,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord:
    save_registry = getattr(
      self._runs,
      "save_provider_provenance_scheduler_stitched_report_governance_registry",
      None,
    )
    if callable(save_registry):
      return save_registry(record)
    self._provider_provenance_scheduler_stitched_report_governance_registries[record.registry_id] = record
    return record

  def _load_provider_provenance_scheduler_stitched_report_governance_registry_record(
    self,
    registry_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord | None:
    get_registry = getattr(
      self._runs,
      "get_provider_provenance_scheduler_stitched_report_governance_registry",
      None,
    )
    if callable(get_registry):
      return get_registry(registry_id)
    return self._provider_provenance_scheduler_stitched_report_governance_registries.get(registry_id)

  def _list_provider_provenance_scheduler_stitched_report_governance_registry_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord, ...]:
    list_registries = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_registries",
      None,
    )
    if callable(list_registries):
      return tuple(list_registries())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_governance_registries.values(),
        key=lambda record: (record.updated_at, record.registry_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_stitched_report_governance_registry_audit_record(
    self,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord:
    save_audit = getattr(
      self._runs,
      "save_provider_provenance_scheduler_stitched_report_governance_registry_audit_record",
      None,
    )
    if callable(save_audit):
      return save_audit(record)
    self._provider_provenance_scheduler_stitched_report_governance_registry_audit_records[record.audit_id] = record
    return record

  def _list_provider_provenance_scheduler_stitched_report_governance_registry_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord, ...]:
    list_audits = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_registry_audit_records",
      None,
    )
    if callable(list_audits):
      return tuple(list_audits())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_governance_registry_audit_records.values(),
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduler_stitched_report_governance_registry_revision_record(
    self,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord:
    save_revision = getattr(
      self._runs,
      "save_provider_provenance_scheduler_stitched_report_governance_registry_revision",
      None,
    )
    if callable(save_revision):
      return save_revision(record)
    self._provider_provenance_scheduler_stitched_report_governance_registry_revisions[record.revision_id] = record
    return record

  def _load_provider_provenance_scheduler_stitched_report_governance_registry_revision_record(
    self,
    revision_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord | None:
    get_revision = getattr(
      self._runs,
      "get_provider_provenance_scheduler_stitched_report_governance_registry_revision",
      None,
    )
    if callable(get_revision):
      return get_revision(revision_id)
    return self._provider_provenance_scheduler_stitched_report_governance_registry_revisions.get(
      revision_id
    )

  def _list_provider_provenance_scheduler_stitched_report_governance_registry_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord, ...]:
    list_revisions = getattr(
      self._runs,
      "list_provider_provenance_scheduler_stitched_report_governance_registry_revisions",
      None,
    )
    if callable(list_revisions):
      return tuple(list_revisions())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_stitched_report_governance_registry_revisions.values(),
        key=lambda record: (record.recorded_at, record.revision_id),
        reverse=True,
      )
    )

  def _build_provider_provenance_scheduler_stitched_report_view_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerStitchedReportViewRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRevisionRecord:
    revision_count = sum(
      1
      for revision in self._list_provider_provenance_scheduler_stitched_report_view_revision_records()
      if revision.view_id == record.view_id
    )
    return ProviderProvenanceSchedulerStitchedReportViewRevisionRecord(
      revision_id=f"{record.view_id}:r{revision_count + 1:04d}",
      view_id=record.view_id,
      action=action,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      name=record.name,
      description=record.description,
      query=deepcopy(record.query),
      occurrence_limit=int(record.occurrence_limit),
      history_limit=int(record.history_limit),
      drilldown_history_limit=int(record.drilldown_history_limit),
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

  def _find_latest_active_provider_provenance_scheduler_stitched_report_view_revision(
    self,
    view_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRevisionRecord | None:
    for revision in self._list_provider_provenance_scheduler_stitched_report_view_revision_records():
      if revision.view_id != view_id:
        continue
      if self._normalize_provider_provenance_scheduler_narrative_record_status(revision.status) != "active":
        continue
      return revision
    return None

  def _build_provider_provenance_scheduler_stitched_report_view_bulk_query(
    self,
    current_query: dict[str, Any],
    query_patch: dict[str, Any] | None,
  ) -> dict[str, Any]:
    candidate = deepcopy(current_query)
    if isinstance(query_patch, dict):
      for key, value in query_patch.items():
        candidate[key] = deepcopy(value)
    return self._normalize_provider_provenance_analytics_query_payload(candidate)

  @staticmethod
  def _build_provider_provenance_scheduler_stitched_report_view_audit_detail(
    *,
    record: ProviderProvenanceSchedulerStitchedReportViewRecord,
    action: str,
  ) -> str:
    lens = f"{record.occurrence_limit} occurrences / {record.history_limit} history / {record.drilldown_history_limit} drill-down"
    if action == "created":
      return f"Created stitched report view {record.name} with {lens}."
    if action == "updated":
      return f"Updated stitched report view {record.name} with {lens}."
    if action == "deleted":
      return f"Deleted stitched report view {record.name}."
    if action == "restored":
      return f"Restored stitched report view {record.name}."
    return f"Recorded stitched report view action {action} for {record.name}."

  def _record_provider_provenance_scheduler_stitched_report_view_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerStitchedReportViewRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerStitchedReportViewRecord:
    revision = self._save_provider_provenance_scheduler_stitched_report_view_revision_record(
      self._build_provider_provenance_scheduler_stitched_report_view_revision(
        record=record,
        action=action,
        reason=reason,
        recorded_at=recorded_at,
        source_revision_id=source_revision_id,
        actor_tab_id=actor_tab_id,
        actor_tab_label=actor_tab_label,
      )
    )
    updated = self._save_provider_provenance_scheduler_stitched_report_view_record(
      replace(
        record,
        current_revision_id=revision.revision_id,
        revision_count=int(record.revision_count or 0) + 1,
      )
    )
    normalized_query = self._normalize_provider_provenance_analytics_query_payload(updated.query)
    self._save_provider_provenance_scheduler_stitched_report_view_audit_record(
      ProviderProvenanceSchedulerStitchedReportViewAuditRecord(
        audit_id=f"{updated.view_id}:{revision.revision_id}:{action}",
        view_id=updated.view_id,
        action=action,
        recorded_at=recorded_at,
        reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
        detail=self._build_provider_provenance_scheduler_stitched_report_view_audit_detail(
          record=updated,
          action=action,
        ),
        revision_id=revision.revision_id,
        source_revision_id=source_revision_id,
        name=updated.name,
        status=updated.status,
        occurrence_limit=int(updated.occurrence_limit),
        history_limit=int(updated.history_limit),
        drilldown_history_limit=int(updated.drilldown_history_limit),
        filter_summary=self._build_provider_provenance_analytics_filter_summary(normalized_query),
        actor_tab_id=revision.recorded_by_tab_id,
        actor_tab_label=revision.recorded_by_tab_label,
      )
    )
    return updated

  def _normalize_provider_provenance_scheduler_stitched_report_governance_registry_queue_view(
    self,
    queue_view: dict[str, Any] | None,
  ) -> dict[str, Any]:
    normalized = self._normalize_provider_provenance_scheduler_narrative_governance_queue_view_payload(
      queue_view
    )
    if not isinstance(normalized, dict):
      return {}
    normalized["item_type"] = "stitched_report_view"
    return normalized

  def _build_provider_provenance_scheduler_stitched_report_governance_registry_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord:
    revision_count = sum(
      1
      for revision in self._list_provider_provenance_scheduler_stitched_report_governance_registry_revision_records()
      if revision.registry_id == record.registry_id
    )
    return ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord(
      revision_id=f"{record.registry_id}:r{revision_count + 1:04d}",
      registry_id=record.registry_id,
      action=action,
      reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
      name=record.name,
      description=record.description,
      queue_view=deepcopy(record.queue_view),
      default_policy_template_id=record.default_policy_template_id,
      default_policy_template_name=record.default_policy_template_name,
      default_policy_catalog_id=record.default_policy_catalog_id,
      default_policy_catalog_name=record.default_policy_catalog_name,
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
  def _build_provider_provenance_scheduler_stitched_report_governance_registry_audit_detail(
    *,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord,
    action: str,
  ) -> str:
    queue_view = record.queue_view if isinstance(record.queue_view, dict) else {}
    queue_tokens: list[str] = []
    if isinstance(queue_view.get("queue_state"), str) and queue_view["queue_state"]:
      queue_tokens.append(f"queue {queue_view['queue_state']}")
    if isinstance(queue_view.get("approval_lane"), str) and queue_view["approval_lane"]:
      queue_tokens.append(f"lane {queue_view['approval_lane']}")
    if isinstance(queue_view.get("approval_priority"), str) and queue_view["approval_priority"]:
      queue_tokens.append(f"priority {queue_view['approval_priority']}")
    if isinstance(queue_view.get("search"), str) and queue_view["search"]:
      queue_tokens.append(f"search \"{queue_view['search']}\"")
    if isinstance(queue_view.get("sort"), str) and queue_view["sort"]:
      queue_tokens.append(f"sort {queue_view['sort']}")
    queue_summary = " / ".join(queue_tokens) if queue_tokens else "default stitched-report queue"
    policy_tokens = [
      value
      for value in (
        record.default_policy_template_name or record.default_policy_template_id,
        record.default_policy_catalog_name or record.default_policy_catalog_id,
      )
      if isinstance(value, str) and value
    ]
    policy_summary = " / ".join(policy_tokens) if policy_tokens else "no default policy bundle"
    if action == "created":
      return f"Created stitched governance registry {record.name} on {queue_summary}. {policy_summary}."
    if action == "updated":
      return f"Updated stitched governance registry {record.name} on {queue_summary}. {policy_summary}."
    if action == "deleted":
      return f"Deleted stitched governance registry {record.name}."
    if action == "restored":
      return f"Restored stitched governance registry {record.name} on {queue_summary}. {policy_summary}."
    return f"Recorded stitched governance registry action {action} for {record.name}. {queue_summary}."

  def _record_provider_provenance_scheduler_stitched_report_governance_registry_revision(
    self,
    *,
    record: ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord,
    action: str,
    reason: str,
    recorded_at: datetime,
    source_revision_id: str | None = None,
    actor_tab_id: str | None = None,
    actor_tab_label: str | None = None,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord:
    revision = self._save_provider_provenance_scheduler_stitched_report_governance_registry_revision_record(
      self._build_provider_provenance_scheduler_stitched_report_governance_registry_revision(
        record=record,
        action=action,
        reason=reason,
        recorded_at=recorded_at,
        source_revision_id=source_revision_id,
        actor_tab_id=actor_tab_id,
        actor_tab_label=actor_tab_label,
      )
    )
    updated = self._save_provider_provenance_scheduler_stitched_report_governance_registry_record(
      replace(
        record,
        current_revision_id=revision.revision_id,
        revision_count=int(record.revision_count or 0) + 1,
      )
    )
    normalized_queue_view = self._normalize_provider_provenance_scheduler_stitched_report_governance_registry_queue_view(
      updated.queue_view
    )
    self._save_provider_provenance_scheduler_stitched_report_governance_registry_audit_record(
      ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord(
        audit_id=f"{updated.registry_id}:{revision.revision_id}:{action}",
        registry_id=updated.registry_id,
        action=action,
        recorded_at=recorded_at,
        reason=reason.strip() if isinstance(reason, str) and reason.strip() else action,
        detail=self._build_provider_provenance_scheduler_stitched_report_governance_registry_audit_detail(
          record=replace(updated, queue_view=normalized_queue_view),
          action=action,
        ),
        revision_id=revision.revision_id,
        source_revision_id=source_revision_id,
        name=updated.name,
        description=updated.description,
        queue_view=deepcopy(normalized_queue_view) if normalized_queue_view is not None else {},
        default_policy_template_id=updated.default_policy_template_id,
        default_policy_template_name=updated.default_policy_template_name,
        default_policy_catalog_id=updated.default_policy_catalog_id,
        default_policy_catalog_name=updated.default_policy_catalog_name,
        status=updated.status,
        actor_tab_id=revision.recorded_by_tab_id,
        actor_tab_label=revision.recorded_by_tab_label,
      )
    )
    return updated

  def _find_latest_active_provider_provenance_scheduler_stitched_report_governance_registry_revision(
    self,
    registry_id: str,
  ) -> ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord | None:
    for revision in self._list_provider_provenance_scheduler_stitched_report_governance_registry_revision_records():
      if revision.registry_id != registry_id:
        continue
      if self._normalize_provider_provenance_scheduler_narrative_record_status(revision.status) != "active":
        continue
      return revision
    return None

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
