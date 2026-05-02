from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from pathlib import Path

from pydantic import TypeAdapter
from sqlalchemy import JSON
from sqlalchemy import Column
from sqlalchemy import delete
from sqlalchemy import inspect
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.engine import Engine
from sqlalchemy.engine import make_url

from akra_trader.domain.models import ExperimentPreset
from akra_trader.domain.models import ReplayIntentAliasAuditRecord
from akra_trader.domain.models import ReplayIntentAliasAuditExportArtifactRecord
from akra_trader.domain.models import ReplayIntentAliasAuditExportJobAuditRecord
from akra_trader.domain.models import ReplayIntentAliasAuditExportJobRecord
from akra_trader.domain.models import ReplayIntentAliasRecord
from akra_trader.domain.models import ProviderProvenanceExportArtifactRecord
from akra_trader.domain.models import ProviderProvenanceAnalyticsPresetRecord
from akra_trader.domain.models import ProviderProvenanceDashboardViewRecord
from akra_trader.domain.models import ProviderProvenanceExportJobAuditRecord
from akra_trader.domain.models import ProviderProvenanceExportJobRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerHealthRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchDocumentRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerStitchedReportViewAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerStitchedReportViewRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerStitchedReportViewRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernancePlanRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeRegistryRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeTemplateRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord
from akra_trader.domain.models import ProviderProvenanceScheduledReportAuditRecord
from akra_trader.domain.models import ProviderProvenanceScheduledReportRecord
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.ports import ExperimentPresetCatalogPort
from akra_trader.ports import RunRepositoryPort


metadata = MetaData()

_COMPACT_SQL_TABLE_NAMES: dict[str, str] = {
  "replay_intent_alias_audit_export_job_audit_records": "ria_export_job_audit",
  "provider_provenance_scheduler_stitched_report_views": "pp_sched_stitch_views",
  "provider_provenance_scheduler_stitched_report_view_revisions": "pp_sched_stitch_view_rev",
  "provider_provenance_scheduler_stitched_report_view_audit_records": "pp_sched_stitch_view_audit",
  "provider_provenance_scheduler_stitched_report_governance_registries": "pp_sched_stitch_gov_reg",
  "provider_provenance_scheduler_stitched_report_governance_registry_audit_records": "pp_sched_stitch_gov_reg_audit",
  "provider_provenance_scheduler_stitched_report_governance_registry_revisions": "pp_sched_stitch_gov_reg_rev",
  "provider_provenance_scheduler_narrative_templates": "pp_sched_narr_tmpl",
  "provider_provenance_scheduler_narrative_template_revisions": "pp_sched_narr_tmpl_rev",
  "provider_provenance_scheduler_narrative_registry": "pp_sched_narr_reg",
  "provider_provenance_scheduler_narrative_registry_revisions": "pp_sched_narr_reg_rev",
  "provider_provenance_scheduler_narrative_governance_policy_templates": "pp_sched_narr_gov_poltmpl",
  "provider_provenance_scheduler_narrative_governance_policy_template_revisions": "pp_sched_narr_gov_poltmpl_rev",
  "provider_provenance_scheduler_narrative_governance_policy_template_audit_records": "pp_sched_narr_gov_poltmpl_audit",
  "provider_provenance_scheduler_stitched_report_governance_policy_templates": "pp_sched_stitch_gov_poltmpl",
  "provider_provenance_scheduler_stitched_report_governance_policy_template_revisions": "pp_sched_stitch_gov_poltmpl_rev",
  "provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records": "pp_sched_stitch_gov_poltmpl_audit",
  "provider_provenance_scheduler_narrative_governance_policy_catalogs": "pp_sched_narr_gov_polcat",
  "provider_provenance_scheduler_narrative_governance_policy_catalog_revisions": "pp_sched_narr_gov_polcat_rev",
  "provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records": "pp_sched_narr_gov_polcat_audit",
  "provider_provenance_scheduler_stitched_report_governance_policy_catalogs": "pp_sched_stitch_gov_polcat",
  "provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions": "pp_sched_stitch_gov_polcat_rev",
  "provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records": "pp_sched_stitch_gov_polcat_audit",
  "provider_provenance_scheduler_narrative_governance_hierarchy_step_templates": "pp_sched_narr_gov_hierstep",
  "provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions": "pp_sched_narr_gov_hierstep_rev",
  "provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records": "pp_sched_narr_gov_hierstep_audit",
  "provider_provenance_scheduler_narrative_governance_plans": "pp_sched_narr_gov_plan",
  "provider_provenance_scheduler_stitched_report_governance_plans": "pp_sched_stitch_gov_plan",
  "provider_provenance_scheduled_report_audit_records": "pp_sched_report_audit",
}


def _sql_table_name(logical_name: str) -> str:
  return _COMPACT_SQL_TABLE_NAMES.get(logical_name, logical_name)


def _quote_identifier(identifier: str) -> str:
  return f"\"{identifier.replace('\"', '\"\"')}\""


run_records = Table(
  "run_records",
  metadata,
  Column("run_id", String, primary_key=True),
  Column("mode", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("strategy_id", String, nullable=True, index=True),
  Column("strategy_version", String, nullable=True, index=True),
  Column("rerun_boundary_id", String, nullable=True, index=True),
  Column("dataset_identity", String, nullable=True, index=True),
  Column("preset_id", String, nullable=True, index=True),
  Column("benchmark_family", String, nullable=True, index=True),
  Column("started_at", String, nullable=False),
  Column("ended_at", String, nullable=True),
  Column("payload", JSON, nullable=False),
)
run_record_tags = Table(
  "run_record_tags",
  metadata,
  Column("run_id", String, primary_key=True),
  Column("tag", String, primary_key=True, index=True),
)
experiment_presets = Table(
  "experiment_presets",
  metadata,
  Column("preset_id", String, primary_key=True),
  Column("strategy_id", String, nullable=True, index=True),
  Column("timeframe", String, nullable=True, index=True),
  Column("lifecycle_stage", String, nullable=False, index=True, server_default="draft"),
  Column("updated_at", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
replay_intent_alias_records = Table(
  "replay_intent_alias_records",
  metadata,
  Column("alias_id", String, primary_key=True),
  Column("template_key", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("revoked_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
replay_intent_alias_audit_records = Table(
  "replay_intent_alias_audit_records",
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("alias_id", String, nullable=False, index=True),
  Column("template_key", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
replay_intent_alias_audit_export_jobs = Table(
  "replay_intent_alias_audit_export_jobs",
  metadata,
  Column("job_id", String, primary_key=True),
  Column("template_key", String, nullable=True, index=True),
  Column("export_format", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("requested_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
replay_intent_alias_audit_export_artifacts = Table(
  "replay_intent_alias_audit_export_artifacts",
  metadata,
  Column("artifact_id", String, primary_key=True),
  Column("job_id", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
replay_intent_alias_audit_export_job_audit_records = Table(
  _sql_table_name("replay_intent_alias_audit_export_job_audit_records"),
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("job_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_export_jobs = Table(
  "provider_provenance_export_jobs",
  metadata,
  Column("job_id", String, primary_key=True),
  Column("focus_key", String, nullable=True, index=True),
  Column("symbol", String, nullable=True, index=True),
  Column("timeframe", String, nullable=True, index=True),
  Column("market_data_provider", String, nullable=True, index=True),
  Column("export_format", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("exported_at", String, nullable=True, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("requested_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_export_artifacts = Table(
  "provider_provenance_export_artifacts",
  metadata,
  Column("artifact_id", String, primary_key=True),
  Column("job_id", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_export_job_audit_records = Table(
  "provider_provenance_export_job_audit_records",
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("job_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_analytics_presets = Table(
  "provider_provenance_analytics_presets",
  metadata,
  Column("preset_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_dashboard_views = Table(
  "provider_provenance_dashboard_views",
  metadata,
  Column("view_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("preset_id", String, nullable=True, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_stitched_report_views = Table(
  _sql_table_name("provider_provenance_scheduler_stitched_report_views"),
  metadata,
  Column("view_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_stitched_report_view_revisions = Table(
  _sql_table_name("provider_provenance_scheduler_stitched_report_view_revisions"),
  metadata,
  Column("revision_id", String, primary_key=True),
  Column("view_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_stitched_report_view_audit_records = Table(
  _sql_table_name("provider_provenance_scheduler_stitched_report_view_audit_records"),
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("view_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_stitched_report_governance_registries = Table(
  _sql_table_name("provider_provenance_scheduler_stitched_report_governance_registries"),
  metadata,
  Column("registry_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_stitched_report_governance_registry_audit_records = Table(
  _sql_table_name("provider_provenance_scheduler_stitched_report_governance_registry_audit_records"),
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("registry_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_stitched_report_governance_registry_revisions = Table(
  _sql_table_name("provider_provenance_scheduler_stitched_report_governance_registry_revisions"),
  metadata,
  Column("revision_id", String, primary_key=True),
  Column("registry_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduled_reports = Table(
  "provider_provenance_scheduled_reports",
  metadata,
  Column("report_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("cadence", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("next_run_at", String, nullable=True, index=True),
  Column("last_run_at", String, nullable=True, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_narrative_templates = Table(
  _sql_table_name("provider_provenance_scheduler_narrative_templates"),
  metadata,
  Column("template_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_narrative_template_revisions = Table(
  _sql_table_name("provider_provenance_scheduler_narrative_template_revisions"),
  metadata,
  Column("revision_id", String, primary_key=True),
  Column("template_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_narrative_registry = Table(
  _sql_table_name("provider_provenance_scheduler_narrative_registry"),
  metadata,
  Column("registry_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("template_id", String, nullable=True, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_narrative_registry_revisions = Table(
  _sql_table_name("provider_provenance_scheduler_narrative_registry_revisions"),
  metadata,
  Column("revision_id", String, primary_key=True),
  Column("registry_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_narrative_governance_policy_templates = Table(
  _sql_table_name("provider_provenance_scheduler_narrative_governance_policy_templates"),
  metadata,
  Column("policy_template_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("item_type_scope", String, nullable=False, index=True),
  Column("action_scope", String, nullable=False, index=True),
  Column("approval_lane", String, nullable=False, index=True),
  Column("approval_priority", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_narrative_governance_policy_template_revisions = Table(
  _sql_table_name("provider_provenance_scheduler_narrative_governance_policy_template_revisions"),
  metadata,
  Column("revision_id", String, primary_key=True),
  Column("policy_template_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_narrative_governance_policy_template_audit_records = Table(
  _sql_table_name("provider_provenance_scheduler_narrative_governance_policy_template_audit_records"),
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("policy_template_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("actor_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_stitched_report_governance_policy_templates = Table(
  _sql_table_name("provider_provenance_scheduler_stitched_report_governance_policy_templates"),
  metadata,
  Column("policy_template_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("item_type_scope", String, nullable=False, index=True),
  Column("action_scope", String, nullable=False, index=True),
  Column("approval_lane", String, nullable=False, index=True),
  Column("approval_priority", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_stitched_report_governance_policy_template_revisions = Table(
  _sql_table_name("provider_provenance_scheduler_stitched_report_governance_policy_template_revisions"),
  metadata,
  Column("revision_id", String, primary_key=True),
  Column("policy_template_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records = Table(
  _sql_table_name("provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records"),
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("policy_template_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("actor_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_narrative_governance_policy_catalogs = Table(
  _sql_table_name("provider_provenance_scheduler_narrative_governance_policy_catalogs"),
  metadata,
  Column("catalog_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("default_policy_template_id", String, nullable=True, index=True),
  Column("item_type_scope", String, nullable=False, index=True),
  Column("action_scope", String, nullable=False, index=True),
  Column("approval_lane", String, nullable=False, index=True),
  Column("approval_priority", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_narrative_governance_policy_catalog_revisions = Table(
  _sql_table_name("provider_provenance_scheduler_narrative_governance_policy_catalog_revisions"),
  metadata,
  Column("revision_id", String, primary_key=True),
  Column("catalog_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records = Table(
  _sql_table_name("provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records"),
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("catalog_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("actor_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_stitched_report_governance_policy_catalogs = Table(
  _sql_table_name("provider_provenance_scheduler_stitched_report_governance_policy_catalogs"),
  metadata,
  Column("catalog_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("default_policy_template_id", String, nullable=True, index=True),
  Column("item_type_scope", String, nullable=False, index=True),
  Column("action_scope", String, nullable=False, index=True),
  Column("approval_lane", String, nullable=False, index=True),
  Column("approval_priority", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions = Table(
  _sql_table_name("provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions"),
  metadata,
  Column("revision_id", String, primary_key=True),
  Column("catalog_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records = Table(
  _sql_table_name("provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records"),
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("catalog_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("actor_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_narrative_governance_hierarchy_step_templates = Table(
  _sql_table_name("provider_provenance_scheduler_narrative_governance_hierarchy_step_templates"),
  metadata,
  Column("hierarchy_step_template_id", String, primary_key=True),
  Column("name", String, nullable=False, index=True),
  Column("item_type", String, nullable=False, index=True),
  Column("origin_catalog_id", String, nullable=True, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions = Table(
  _sql_table_name("provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions"),
  metadata,
  Column("revision_id", String, primary_key=True),
  Column("hierarchy_step_template_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records = Table(
  _sql_table_name("provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records"),
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("hierarchy_step_template_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("actor_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_narrative_governance_plans = Table(
  _sql_table_name("provider_provenance_scheduler_narrative_governance_plans"),
  metadata,
  Column("plan_id", String, primary_key=True),
  Column("item_type", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("policy_template_id", String, nullable=True, index=True),
  Column("approval_lane", String, nullable=False, index=True),
  Column("approval_priority", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_stitched_report_governance_plans = Table(
  _sql_table_name("provider_provenance_scheduler_stitched_report_governance_plans"),
  metadata,
  Column("plan_id", String, primary_key=True),
  Column("item_type", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("policy_template_id", String, nullable=True, index=True),
  Column("approval_lane", String, nullable=False, index=True),
  Column("approval_priority", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("created_by_tab_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduled_report_audit_records = Table(
  _sql_table_name("provider_provenance_scheduled_report_audit_records"),
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("report_id", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_health_records = Table(
  "provider_provenance_scheduler_health_records",
  metadata,
  Column("record_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_documents = Table(
  "provider_provenance_scheduler_search_documents",
  metadata,
  Column("record_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
replay_intent_alias_state = Table(
  "replay_intent_alias_state",
  metadata,
  Column("state_key", String, primary_key=True),
  Column("payload", JSON, nullable=False),
)


def _build_engine(database_url: str) -> Engine:
  url = make_url(database_url)
  engine_kwargs = {"pool_pre_ping": True}
  if url.get_backend_name() == "sqlite" and url.database not in {None, "", ":memory:"}:
    Path(url.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
      database_url,
      connect_args={"check_same_thread": False},
      **engine_kwargs,
    )
  return create_engine(database_url, **engine_kwargs)
