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


class ProviderProvenanceSchedulerStitchedReportRecordsMixin:
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
