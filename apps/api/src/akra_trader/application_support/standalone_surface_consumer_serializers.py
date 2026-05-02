from __future__ import annotations

from dataclasses import asdict
from typing import Any

from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_comparison
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_market_data_ingestion_jobs
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_market_data_lineage_history
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_presets
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_runs
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_strategies
from akra_trader.application_support.runtime_queries import StandaloneSurfaceRuntimeBinding
from akra_trader.application_support.run_subresources import serialize_run_subresource_response
from akra_trader.application_support.run_surfaces import serialize_run


def _application_module():
  from akra_trader import application as application_module
  return application_module


def _application_symbol(name: str):
  return getattr(_application_module(), name)


def serialize_preset(*args, **kwargs):
  return _application_symbol('serialize_preset')(*args, **kwargs)


def serialize_preset_revision(*args, **kwargs):
  return _application_symbol('serialize_preset_revision')(*args, **kwargs)


def serialize_replay_intent_alias_record(*args, **kwargs):
  return _application_symbol('serialize_replay_intent_alias_record')(*args, **kwargs)


def serialize_replay_intent_alias_history(*args, **kwargs):
  return _application_symbol('serialize_replay_intent_alias_history')(*args, **kwargs)


def serialize_replay_intent_alias_audit_list(*args, **kwargs):
  return _application_symbol('serialize_replay_intent_alias_audit_list')(*args, **kwargs)


def serialize_replay_intent_alias_audit_export_job_record(*args, **kwargs):
  return _application_symbol('serialize_replay_intent_alias_audit_export_job_record')(*args, **kwargs)


def serialize_replay_intent_alias_audit_export_job_list(*args, **kwargs):
  return _application_symbol('serialize_replay_intent_alias_audit_export_job_list')(*args, **kwargs)


def serialize_replay_intent_alias_audit_export_job_history(*args, **kwargs):
  return _application_symbol('serialize_replay_intent_alias_audit_export_job_history')(*args, **kwargs)


def serialize_provider_provenance_export_job_record(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_export_job_record')(*args, **kwargs)


def serialize_provider_provenance_export_job_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_export_job_list')(*args, **kwargs)


def serialize_provider_provenance_export_job_history(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_export_job_history')(*args, **kwargs)


def serialize_provider_provenance_export_job_escalation_result(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_export_job_escalation_result')(*args, **kwargs)


def serialize_provider_provenance_export_job_policy_result(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_export_job_policy_result')(*args, **kwargs)


def serialize_provider_provenance_analytics_preset_record(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_analytics_preset_record')(*args, **kwargs)


def serialize_provider_provenance_analytics_preset_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_analytics_preset_list')(*args, **kwargs)


def serialize_provider_provenance_dashboard_view_record(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_dashboard_view_record')(*args, **kwargs)


def serialize_provider_provenance_dashboard_view_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_dashboard_view_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_stitched_report_view_record(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_stitched_report_view_record')(*args, **kwargs)


def serialize_provider_provenance_scheduler_stitched_report_view_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_stitched_report_view_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_stitched_report_view_revision_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_stitched_report_view_revision_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_stitched_report_view_audit_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_stitched_report_view_audit_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_stitched_report_governance_registry_record(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_stitched_report_governance_registry_record')(*args, **kwargs)


def serialize_provider_provenance_scheduler_stitched_report_governance_registry_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_stitched_report_governance_registry_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_stitched_report_governance_registry_revision_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_stitched_report_governance_registry_revision_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_stitched_report_governance_registry_audit_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_stitched_report_governance_registry_audit_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_template_record(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_template_record')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_template_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_template_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_template_revision_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_template_revision_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_bulk_governance_result(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_bulk_governance_result')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_registry_record(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_registry_record')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_registry_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_registry_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_registry_revision_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_registry_revision_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_governance_plan_record(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_governance_plan_record')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_governance_plan_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_governance_plan_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_governance_policy_template_record(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_governance_policy_template_record')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_governance_policy_template_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_governance_policy_template_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_governance_policy_template_revision_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_governance_policy_template_revision_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_governance_policy_template_audit_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_governance_policy_template_audit_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_list')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_stage_result(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_stage_result')(*args, **kwargs)


def serialize_provider_provenance_scheduler_narrative_governance_plan_batch_result(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_narrative_governance_plan_batch_result')(*args, **kwargs)


def serialize_provider_provenance_scheduled_report_record(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduled_report_record')(*args, **kwargs)


def serialize_provider_provenance_scheduled_report_list(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduled_report_list')(*args, **kwargs)


def serialize_provider_provenance_scheduled_report_history(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduled_report_history')(*args, **kwargs)


def serialize_provider_provenance_scheduled_report_run_result(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduled_report_run_result')(*args, **kwargs)


def serialize_provider_provenance_scheduled_report_run_due_result(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduled_report_run_due_result')(*args, **kwargs)


def serialize_provider_provenance_scheduler_health_history(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_health_history')(*args, **kwargs)


def serialize_provider_provenance_scheduler_alert_history(*args, **kwargs):
  return _application_symbol('serialize_provider_provenance_scheduler_alert_history')(*args, **kwargs)


def serialize_strategy(*args, **kwargs):
  return _application_symbol('serialize_strategy')(*args, **kwargs)


def serialize_run_comparison(*args, **kwargs):
  return _application_symbol('serialize_run_comparison')(*args, **kwargs)


def serialize_run_surface_capabilities(*args, **kwargs):
  return _application_symbol('serialize_run_surface_capabilities')(*args, **kwargs)
