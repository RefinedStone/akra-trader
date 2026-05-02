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


class ProviderProvenanceCompatibilitySearchRecordsMixin:
  def _save_provider_provenance_analytics_preset_record(
    self,
    record: ProviderProvenanceAnalyticsPresetRecord,
  ) -> ProviderProvenanceAnalyticsPresetRecord:
    save_preset = getattr(self._runs, "save_provider_provenance_analytics_preset", None)
    if callable(save_preset):
      return save_preset(record)
    self._provider_provenance_analytics_presets[record.preset_id] = record
    return record

  def _load_provider_provenance_analytics_preset_record(
    self,
    preset_id: str,
  ) -> ProviderProvenanceAnalyticsPresetRecord | None:
    get_preset = getattr(self._runs, "get_provider_provenance_analytics_preset", None)
    if callable(get_preset):
      return get_preset(preset_id)
    return self._provider_provenance_analytics_presets.get(preset_id)

  def _list_provider_provenance_analytics_preset_records(
    self,
  ) -> tuple[ProviderProvenanceAnalyticsPresetRecord, ...]:
    list_presets = getattr(self._runs, "list_provider_provenance_analytics_presets", None)
    if callable(list_presets):
      return tuple(list_presets())
    return tuple(
      sorted(
        self._provider_provenance_analytics_presets.values(),
        key=lambda record: (record.updated_at, record.preset_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_dashboard_view_record(
    self,
    record: ProviderProvenanceDashboardViewRecord,
  ) -> ProviderProvenanceDashboardViewRecord:
    save_view = getattr(self._runs, "save_provider_provenance_dashboard_view", None)
    if callable(save_view):
      return save_view(record)
    self._provider_provenance_dashboard_views[record.view_id] = record
    return record

  def _load_provider_provenance_dashboard_view_record(
    self,
    view_id: str,
  ) -> ProviderProvenanceDashboardViewRecord | None:
    get_view = getattr(self._runs, "get_provider_provenance_dashboard_view", None)
    if callable(get_view):
      return get_view(view_id)
    return self._provider_provenance_dashboard_views.get(view_id)

  def _list_provider_provenance_dashboard_view_records(
    self,
  ) -> tuple[ProviderProvenanceDashboardViewRecord, ...]:
    list_views = getattr(self._runs, "list_provider_provenance_dashboard_views", None)
    if callable(list_views):
      return tuple(list_views())
    return tuple(
      sorted(
        self._provider_provenance_dashboard_views.values(),
        key=lambda record: (record.updated_at, record.view_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduled_report_record(
    self,
    record: ProviderProvenanceScheduledReportRecord,
  ) -> ProviderProvenanceScheduledReportRecord:
    save_report = getattr(self._runs, "save_provider_provenance_scheduled_report", None)
    if callable(save_report):
      return save_report(record)
    self._provider_provenance_scheduled_reports[record.report_id] = record
    return record

  def _load_provider_provenance_scheduled_report_record(
    self,
    report_id: str,
  ) -> ProviderProvenanceScheduledReportRecord | None:
    get_report = getattr(self._runs, "get_provider_provenance_scheduled_report", None)
    if callable(get_report):
      return get_report(report_id)
    return self._provider_provenance_scheduled_reports.get(report_id)

  def _list_provider_provenance_scheduled_report_records(
    self,
  ) -> tuple[ProviderProvenanceScheduledReportRecord, ...]:
    list_reports = getattr(self._runs, "list_provider_provenance_scheduled_reports", None)
    if callable(list_reports):
      return tuple(list_reports())
    return tuple(
      sorted(
        self._provider_provenance_scheduled_reports.values(),
        key=lambda record: (record.updated_at, record.report_id),
        reverse=True,
      )
    )

  def _save_provider_provenance_scheduled_report_audit_record(
    self,
    record: ProviderProvenanceScheduledReportAuditRecord,
  ) -> ProviderProvenanceScheduledReportAuditRecord:
    save_audit = getattr(self._runs, "save_provider_provenance_scheduled_report_audit_record", None)
    if callable(save_audit):
      return save_audit(record)
    self._provider_provenance_scheduled_report_audit_records[record.audit_id] = record
    return record

  def _list_provider_provenance_scheduled_report_audit_records(
    self,
    report_id: str | None = None,
  ) -> tuple[ProviderProvenanceScheduledReportAuditRecord, ...]:
    list_audits = getattr(self._runs, "list_provider_provenance_scheduled_report_audit_records", None)
    if callable(list_audits):
      return tuple(list_audits(report_id))
    records = [
      record
      for record in self._provider_provenance_scheduled_report_audit_records.values()
      if report_id is None or record.report_id == report_id
    ]
    return tuple(
      sorted(
        records,
        key=lambda record: (record.recorded_at, record.audit_id),
        reverse=True,
      )
    )

  def _prune_provider_provenance_scheduled_report_audit_records(self) -> int:
    current_time = self._clock()
    prune_audits = getattr(self._runs, "prune_provider_provenance_scheduled_report_audit_records", None)
    if callable(prune_audits):
      return int(prune_audits(current_time))
    original_count = len(self._provider_provenance_scheduled_report_audit_records)
    self._provider_provenance_scheduled_report_audit_records = {
      audit_id: record
      for audit_id, record in self._provider_provenance_scheduled_report_audit_records.items()
      if record.expires_at is None or record.expires_at > current_time
    }
    return original_count - len(self._provider_provenance_scheduled_report_audit_records)

  def _save_provider_provenance_scheduler_health_record(
    self,
    record: ProviderProvenanceSchedulerHealthRecord,
  ) -> ProviderProvenanceSchedulerHealthRecord:
    save_record = getattr(self._runs, "save_provider_provenance_scheduler_health_record", None)
    if callable(save_record):
      return save_record(record)
    self._provider_provenance_scheduler_health_records[record.record_id] = record
    return record

  def _list_provider_provenance_scheduler_health_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerHealthRecord, ...]:
    list_records = getattr(self._runs, "list_provider_provenance_scheduler_health_records", None)
    if callable(list_records):
      return tuple(list_records())
    return tuple(
      sorted(
        self._provider_provenance_scheduler_health_records.values(),
        key=lambda record: (record.recorded_at, record.record_id),
        reverse=True,
      )
    )

  def _prune_provider_provenance_scheduler_health_records(self) -> int:
    current_time = self._clock()
    prune_records = getattr(self._runs, "prune_provider_provenance_scheduler_health_records", None)
    if callable(prune_records):
      pruned_count = int(prune_records(current_time))
      self._prune_provider_provenance_scheduler_search_document_records()
      self._prune_provider_provenance_scheduler_search_query_analytics_records()
      self._prune_provider_provenance_scheduler_search_feedback_records()
      return pruned_count
    original_count = len(self._provider_provenance_scheduler_health_records)
    self._provider_provenance_scheduler_health_records = {
      record_id: record
      for record_id, record in self._provider_provenance_scheduler_health_records.items()
      if record.expires_at is None or record.expires_at > current_time
    }
    self._prune_provider_provenance_scheduler_search_document_records()
    self._prune_provider_provenance_scheduler_search_query_analytics_records()
    self._prune_provider_provenance_scheduler_search_feedback_records()
    return original_count - len(self._provider_provenance_scheduler_health_records)

  def _save_provider_provenance_scheduler_search_document_record(
    self,
    record: ProviderProvenanceSchedulerSearchDocumentRecord,
  ) -> ProviderProvenanceSchedulerSearchDocumentRecord:
    return self._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_document_record(
      record
    )

  def _list_provider_provenance_scheduler_search_document_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchDocumentRecord, ...]:
    return tuple(
      self._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_document_records()
    )

  def _prune_provider_provenance_scheduler_search_document_records(self) -> int:
    current_time = self._clock()
    return int(
      self._provider_provenance_scheduler_search_backend.prune_provider_provenance_scheduler_search_document_records(
        current_time
      )
    )

  def _save_provider_provenance_scheduler_search_query_analytics_record(
    self,
    record: ProviderProvenanceSchedulerSearchQueryAnalyticsRecord,
  ) -> ProviderProvenanceSchedulerSearchQueryAnalyticsRecord:
    return self._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_query_analytics_record(
      record
    )

  def _list_provider_provenance_scheduler_search_query_analytics_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchQueryAnalyticsRecord, ...]:
    return tuple(
      self._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_query_analytics_records()
    )

  def _prune_provider_provenance_scheduler_search_query_analytics_records(self) -> int:
    current_time = self._clock()
    return int(
      self._provider_provenance_scheduler_search_backend.prune_provider_provenance_scheduler_search_query_analytics_records(
        current_time
      )
    )

  def _save_provider_provenance_scheduler_search_feedback_record(
    self,
    record: ProviderProvenanceSchedulerSearchFeedbackRecord,
  ) -> ProviderProvenanceSchedulerSearchFeedbackRecord:
    return self._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_feedback_record(
      record
    )

  def _list_provider_provenance_scheduler_search_feedback_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchFeedbackRecord, ...]:
    return tuple(
      self._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_feedback_records()
    )

  def _prune_provider_provenance_scheduler_search_feedback_records(self) -> int:
    current_time = self._clock()
    return int(
      self._provider_provenance_scheduler_search_backend.prune_provider_provenance_scheduler_search_feedback_records(
        current_time
      )
    )

  def _save_provider_provenance_scheduler_search_moderation_policy_catalog_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord:
    return (
      self._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_moderation_policy_catalog_record(
        record
      )
    )

  def _list_provider_provenance_scheduler_search_moderation_policy_catalog_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord, ...]:
    return tuple(
      self._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_moderation_policy_catalog_records()
    )

  def _save_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord:
    return (
      self._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_moderation_policy_catalog_revision_record(
        record
      )
    )

  def _list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord, ...]:
    return tuple(
      self._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_moderation_policy_catalog_revision_records()
    )

  def _save_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord:
    return (
      self._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_moderation_policy_catalog_audit_record(
        record
      )
    )

  def _list_provider_provenance_scheduler_search_moderation_policy_catalog_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord, ...]:
    return tuple(
      self._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_moderation_policy_catalog_audit_records()
    )

  def _save_provider_provenance_scheduler_search_moderation_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationPlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationPlanRecord:
    return (
      self._provider_provenance_scheduler_search_backend.save_provider_provenance_scheduler_search_moderation_plan_record(
        record
      )
    )

  def _list_provider_provenance_scheduler_search_moderation_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationPlanRecord, ...]:
    return tuple(
      self._provider_provenance_scheduler_search_backend.list_provider_provenance_scheduler_search_moderation_plan_records()
    )

  def _save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
    return save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_record_support(
      self,
      record,
    )

  def _list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord, ...]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_records_support(
      self
    )

  def _save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord:
    return save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_record_support(
      self,
      record,
    )

  def _list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord, ...]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision_records_support(
      self
    )

  def _save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord:
    return save_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_record_support(
      self,
      record,
    )

  def _list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord, ...]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audit_records_support(
      self
    )

  def _save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord:
    return save_provider_provenance_scheduler_search_moderation_catalog_governance_plan_record_support(
      self,
      record,
    )

  def _list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord, ...]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_plan_records_support(
      self
    )

  def _save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord:
    return save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_record_support(
      self,
      record,
    )

  def _list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord, ...]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy_records_support(
      self
    )

  def _save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record(
    self,
    record: ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord,
  ) -> ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord:
    return save_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_record_support(
      self,
      record,
    )

  def _list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord, ...]:
    return list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan_records_support(
      self
    )
