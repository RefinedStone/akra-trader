from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

@dataclass(frozen=True)
class ProviderProvenanceSchedulerHealth:
  generated_at: datetime
  enabled: bool = True
  status: str = "starting"
  summary: str = ""
  interval_seconds: int = 60
  batch_limit: int = 25
  last_cycle_started_at: datetime | None = None
  last_cycle_finished_at: datetime | None = None
  last_success_at: datetime | None = None
  last_failure_at: datetime | None = None
  last_error: str | None = None
  cycle_count: int = 0
  success_count: int = 0
  failure_count: int = 0
  consecutive_failure_count: int = 0
  last_executed_count: int = 0
  total_executed_count: int = 0
  due_report_count: int = 0
  oldest_due_at: datetime | None = None
  max_due_lag_seconds: int = 0
  active_alert_key: str | None = None
  alert_workflow_job_id: str | None = None
  alert_workflow_triggered_at: datetime | None = None
  alert_workflow_state: str | None = None
  alert_workflow_summary: str | None = None
  issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProviderProvenanceSchedulerHealthRecord:
  record_id: str
  recorded_at: datetime
  scheduler_key: str = "provider_provenance_reports"
  expires_at: datetime | None = None
  enabled: bool = True
  status: str = "starting"
  summary: str = ""
  interval_seconds: int = 60
  batch_limit: int = 25
  last_cycle_started_at: datetime | None = None
  last_cycle_finished_at: datetime | None = None
  last_success_at: datetime | None = None
  last_failure_at: datetime | None = None
  last_error: str | None = None
  cycle_count: int = 0
  success_count: int = 0
  failure_count: int = 0
  consecutive_failure_count: int = 0
  last_executed_count: int = 0
  total_executed_count: int = 0
  due_report_count: int = 0
  oldest_due_at: datetime | None = None
  max_due_lag_seconds: int = 0
  active_alert_key: str | None = None
  alert_workflow_job_id: str | None = None
  alert_workflow_triggered_at: datetime | None = None
  alert_workflow_state: str | None = None
  alert_workflow_summary: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  issues: tuple[str, ...] = ()
  search_projection: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchDocumentRecord:
  record_id: str
  recorded_at: datetime
  scheduler_key: str = "provider_provenance_reports"
  expires_at: datetime | None = None
  index_version: str = "scheduler-search-store.v1"
  lexical_terms: tuple[str, ...] = ()
  semantic_concepts: tuple[str, ...] = ()
  fields: dict[str, tuple[str, ...]] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchQueryAnalyticsRecord:
  query_id: str
  recorded_at: datetime
  query: str
  scheduler_key: str = "provider_provenance_reports"
  expires_at: datetime | None = None
  category: str | None = None
  status: str | None = None
  narrative_facet: str | None = None
  persistence_mode: str | None = None
  relevance_model: str | None = None
  token_count: int = 0
  operator_count: int = 0
  boolean_operator_count: int = 0
  semantic_concept_count: int = 0
  matched_occurrences: int = 0
  top_score: int = 0
  indexed_occurrence_count: int = 0
  indexed_term_count: int = 0
  query_terms: tuple[str, ...] = ()
  query_phrases: tuple[str, ...] = ()
  query_semantic_concepts: tuple[str, ...] = ()
  parsed_operators: tuple[str, ...] = ()
  matched_occurrence_ids: tuple[str, ...] = ()
  top_cluster_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchFeedbackRecord:
  feedback_id: str
  recorded_at: datetime
  query_id: str
  query: str
  occurrence_id: str
  signal: str
  scheduler_key: str = "provider_provenance_reports"
  expires_at: datetime | None = None
  actor: str = "operator"
  note: str | None = None
  category: str | None = None
  status: str | None = None
  narrative_facet: str | None = None
  query_terms: tuple[str, ...] = ()
  query_phrases: tuple[str, ...] = ()
  query_semantic_concepts: tuple[str, ...] = ()
  parsed_operators: tuple[str, ...] = ()
  matched_fields: tuple[str, ...] = ()
  semantic_concepts: tuple[str, ...] = ()
  operator_hits: tuple[str, ...] = ()
  lexical_score: int = 0
  semantic_score: int = 0
  operator_score: int = 0
  score: int = 0
  ranking_reason: str | None = None
  source_tab_id: str | None = None
  source_tab_label: str | None = None
  moderation_status: str = "pending"
  moderation_note: str | None = None
  moderated_at: datetime | None = None
  moderated_by: str | None = None
  moderated_by_tab_id: str | None = None
  moderated_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord:
  catalog_id: str
  created_at: datetime
  updated_at: datetime
  name: str
  scheduler_key: str = "provider_provenance_reports"
  description: str = ""
  status: str = "active"
  default_moderation_status: str = "approved"
  governance_view: str = "pending_queue"
  window_days: int = 30
  stale_pending_hours: int = 24
  minimum_score: int = 0
  require_note: bool = False
  current_revision_id: str | None = None
  revision_count: int = 0
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  deleted_at: datetime | None = None
  deleted_by_tab_id: str | None = None
  deleted_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord:
  revision_id: str
  catalog_id: str
  action: str
  reason: str
  name: str
  description: str = ""
  scheduler_key: str = "provider_provenance_reports"
  status: str = "active"
  default_moderation_status: str = "approved"
  governance_view: str = "pending_queue"
  window_days: int = 30
  stale_pending_hours: int = 24
  minimum_score: int = 0
  require_note: bool = False
  recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  source_revision_id: str | None = None
  recorded_by_tab_id: str | None = None
  recorded_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord:
  audit_id: str
  catalog_id: str
  action: str
  recorded_at: datetime
  reason: str
  detail: str = ""
  revision_id: str | None = None
  source_revision_id: str | None = None
  scheduler_key: str = "provider_provenance_reports"
  name: str = ""
  status: str = "active"
  default_moderation_status: str = "approved"
  governance_view: str = "pending_queue"
  window_days: int = 30
  stale_pending_hours: int = 24
  minimum_score: int = 0
  require_note: bool = False
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationPlanPreviewItem:
  feedback_id: str
  occurrence_id: str
  query: str
  signal: str
  current_moderation_status: str
  proposed_moderation_status: str
  score: int = 0
  age_hours: int = 0
  stale_pending: bool = False
  high_score_pending: bool = False
  query_run_count: int = 0
  eligible: bool = True
  reason_tags: tuple[str, ...] = ()
  matched_fields: tuple[str, ...] = ()
  semantic_concepts: tuple[str, ...] = ()
  operator_hits: tuple[str, ...] = ()
  note: str | None = None
  ranking_reason: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationPlanRecord:
  plan_id: str
  created_at: datetime
  updated_at: datetime
  scheduler_key: str = "provider_provenance_reports"
  status: str = "previewed"
  queue_state: str = "pending_approval"
  policy_catalog_id: str | None = None
  policy_catalog_name: str | None = None
  proposed_moderation_status: str = "approved"
  governance_view: str = "pending_queue"
  window_days: int = 30
  stale_pending_hours: int = 24
  minimum_score: int = 0
  require_note: bool = False
  requested_feedback_ids: tuple[str, ...] = ()
  feedback_ids: tuple[str, ...] = ()
  missing_feedback_ids: tuple[str, ...] = ()
  preview_items: tuple[ProviderProvenanceSchedulerSearchModerationPlanPreviewItem, ...] = ()
  created_by: str = "operator"
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  approved_at: datetime | None = None
  approved_by: str | None = None
  approved_by_tab_id: str | None = None
  approved_by_tab_label: str | None = None
  approval_note: str | None = None
  applied_at: datetime | None = None
  applied_by: str | None = None
  applied_by_tab_id: str | None = None
  applied_by_tab_label: str | None = None
  apply_note: str | None = None
  applied_result: dict[str, Any] | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord:
  governance_policy_id: str
  created_at: datetime
  updated_at: datetime
  name: str
  description: str = ""
  scheduler_key: str = "provider_provenance_reports"
  status: str = "active"
  action_scope: str = "any"
  require_approval_note: bool = False
  guidance: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  default_moderation_status: str = "approved"
  governance_view: str = "pending_queue"
  window_days: int = 30
  stale_pending_hours: int = 24
  minimum_score: int = 0
  require_note: bool = False
  current_revision_id: str | None = None
  revision_count: int = 0
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  deleted_at: datetime | None = None
  deleted_by_tab_id: str | None = None
  deleted_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord:
  revision_id: str
  governance_policy_id: str
  action: str
  reason: str
  name: str
  description: str = ""
  scheduler_key: str = "provider_provenance_reports"
  status: str = "active"
  action_scope: str = "any"
  require_approval_note: bool = False
  guidance: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  default_moderation_status: str = "approved"
  governance_view: str = "pending_queue"
  window_days: int = 30
  stale_pending_hours: int = 24
  minimum_score: int = 0
  require_note: bool = False
  recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))
  source_revision_id: str | None = None
  recorded_by_tab_id: str | None = None
  recorded_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord:
  audit_id: str
  governance_policy_id: str
  action: str
  recorded_at: datetime
  reason: str
  detail: str
  scheduler_key: str = "provider_provenance_reports"
  revision_id: str | None = None
  source_revision_id: str | None = None
  name: str = ""
  status: str = "active"
  action_scope: str = "any"
  require_approval_note: bool = False
  default_moderation_status: str = "approved"
  governance_view: str = "pending_queue"
  window_days: int = 30
  stale_pending_hours: int = 24
  minimum_score: int = 0
  require_note: bool = False
  actor_tab_id: str | None = None
  actor_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanPreviewItem:
  catalog_id: str
  catalog_name: str
  action: str
  current_status: str
  current_revision_id: str | None = None
  rollback_revision_id: str | None = None
  outcome: str = "changed"
  message: str | None = None
  changed_fields: tuple[str, ...] = ()
  field_diffs: dict[str, dict[str, Any]] = field(default_factory=dict)
  current_snapshot: dict[str, Any] = field(default_factory=dict)
  proposed_snapshot: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord:
  plan_id: str
  created_at: datetime
  updated_at: datetime
  scheduler_key: str = "provider_provenance_reports"
  action: str = "update"
  status: str = "previewed"
  queue_state: str = "pending_approval"
  governance_policy_id: str | None = None
  governance_policy_name: str | None = None
  require_approval_note: bool = False
  guidance: str | None = None
  requested_catalog_ids: tuple[str, ...] = ()
  preview_items: tuple[
    ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanPreviewItem,
    ...,
  ] = ()
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  default_moderation_status: str | None = None
  governance_view: str | None = None
  window_days: int | None = None
  stale_pending_hours: int | None = None
  minimum_score: int | None = None
  require_note: bool | None = None
  created_by: str = "operator"
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  approved_at: datetime | None = None
  approved_by: str | None = None
  approved_by_tab_id: str | None = None
  approved_by_tab_label: str | None = None
  approval_note: str | None = None
  applied_at: datetime | None = None
  applied_by: str | None = None
  applied_by_tab_id: str | None = None
  applied_by_tab_label: str | None = None
  apply_note: str | None = None
  applied_result: dict[str, Any] | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord:
  meta_policy_id: str
  created_at: datetime
  updated_at: datetime
  name: str
  description: str = ""
  scheduler_key: str = "provider_provenance_reports"
  status: str = "active"
  action_scope: str = "any"
  require_approval_note: bool = False
  guidance: str | None = None
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  policy_action_scope: str | None = None
  policy_require_approval_note: bool | None = None
  policy_guidance: str | None = None
  default_moderation_status: str | None = None
  governance_view: str | None = None
  window_days: int | None = None
  stale_pending_hours: int | None = None
  minimum_score: int | None = None
  require_note: bool | None = None
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPreviewItem:
  governance_policy_id: str
  governance_policy_name: str
  action: str
  current_status: str
  current_revision_id: str | None = None
  rollback_revision_id: str | None = None
  outcome: str = "changed"
  message: str | None = None
  changed_fields: tuple[str, ...] = ()
  field_diffs: dict[str, dict[str, Any]] = field(default_factory=dict)
  current_snapshot: dict[str, Any] = field(default_factory=dict)
  proposed_snapshot: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord:
  plan_id: str
  created_at: datetime
  updated_at: datetime
  scheduler_key: str = "provider_provenance_reports"
  action: str = "update"
  status: str = "previewed"
  queue_state: str = "pending_approval"
  meta_policy_id: str | None = None
  meta_policy_name: str | None = None
  require_approval_note: bool = False
  guidance: str | None = None
  requested_governance_policy_ids: tuple[str, ...] = ()
  preview_items: tuple[
    ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPreviewItem,
    ...,
  ] = ()
  name_prefix: str | None = None
  name_suffix: str | None = None
  description_append: str | None = None
  policy_action_scope: str | None = None
  policy_require_approval_note: bool | None = None
  policy_guidance: str | None = None
  default_moderation_status: str | None = None
  governance_view: str | None = None
  window_days: int | None = None
  stale_pending_hours: int | None = None
  minimum_score: int | None = None
  require_note: bool | None = None
  created_by: str = "operator"
  created_by_tab_id: str | None = None
  created_by_tab_label: str | None = None
  approved_at: datetime | None = None
  approved_by: str | None = None
  approved_by_tab_id: str | None = None
  approved_by_tab_label: str | None = None
  approval_note: str | None = None
  applied_at: datetime | None = None
  applied_by: str | None = None
  applied_by_tab_id: str | None = None
  applied_by_tab_label: str | None = None
  apply_note: str | None = None
  applied_result: dict[str, Any] | None = None
