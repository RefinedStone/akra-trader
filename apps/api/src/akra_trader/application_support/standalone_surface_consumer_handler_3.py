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
from akra_trader.application_support.standalone_surface_consumer_handler_common import UNHANDLED
from akra_trader.application_support.standalone_surface_consumer_serializers import *

def handle_standalone_surface_binding_part_3(
  *,
  binding: StandaloneSurfaceRuntimeBinding,
  app: Any,
  run_id: str | None,
  resolved_filters: dict[str, Any],
  resolved_payload: dict[str, Any],
  resolved_path_params: dict[str, Any],
  resolved_headers: dict[str, Any],
) -> Any:
  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_capture":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
      app.capture_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy(
        resolved_path_params["catalog_id"],
        hierarchy_steps=resolved_payload.get("hierarchy_steps", ()),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_governance_policy_catalog_hierarchy_captured"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_update":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
      app.update_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step(
        resolved_path_params["catalog_id"],
        resolved_path_params["step_id"],
        item_ids=resolved_payload.get("item_ids"),
        name_prefix=resolved_payload.get("name_prefix"),
        name_suffix=resolved_payload.get("name_suffix"),
        description_append=resolved_payload.get("description_append"),
        query_patch=resolved_payload.get("query_patch"),
        layout_patch=resolved_payload.get("layout_patch"),
        template_id=resolved_payload.get("template_id"),
        clear_template_link=resolved_payload.get("clear_template_link"),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get(
          "reason",
          "scheduler_narrative_governance_policy_catalog_hierarchy_step_updated",
        ),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_restore":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
      app.restore_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_revision(
        resolved_path_params["catalog_id"],
        resolved_path_params["step_id"],
        resolved_path_params["revision_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get(
          "reason",
          "scheduler_narrative_governance_policy_catalog_hierarchy_step_restored",
        ),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_bulk_governance":
    return serialize_provider_provenance_scheduler_narrative_bulk_governance_result(
      app.bulk_govern_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_steps(
        resolved_path_params["catalog_id"],
        resolved_payload.get("step_ids", ()),
        action=resolved_payload.get("action", ""),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason"),
        name_prefix=resolved_payload.get("name_prefix"),
        name_suffix=resolved_payload.get("name_suffix"),
        description_append=resolved_payload.get("description_append"),
        query_patch=resolved_payload.get("query_patch"),
        layout_patch=resolved_payload.get("layout_patch"),
        template_id=resolved_payload.get("template_id"),
        clear_template_link=resolved_payload.get("clear_template_link"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_create":
    return serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record(
      app.create_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
        name=resolved_payload.get("name", ""),
        description=resolved_payload.get("description", ""),
        step=resolved_payload.get("step"),
        origin_catalog_id=resolved_payload.get("origin_catalog_id"),
        origin_step_id=resolved_payload.get("origin_step_id"),
        governance_policy_template_id=resolved_payload.get("governance_policy_template_id"),
        governance_policy_catalog_id=resolved_payload.get("governance_policy_catalog_id"),
        governance_approval_lane=resolved_payload.get("governance_approval_lane"),
        governance_approval_priority=resolved_payload.get("governance_approval_priority"),
        created_by_tab_id=resolved_payload.get("created_by_tab_id"),
        created_by_tab_label=resolved_payload.get("created_by_tab_label"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_list":
    return serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_list(
      app.list_provider_provenance_scheduler_narrative_governance_hierarchy_step_templates(
        item_type=resolved_filters.get("item_type"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 20),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_bulk_governance":
    return serialize_provider_provenance_scheduler_narrative_bulk_governance_result(
      app.bulk_govern_provider_provenance_scheduler_narrative_governance_hierarchy_step_templates(
        resolved_payload.get("hierarchy_step_template_ids", ()),
        action=resolved_payload.get("action", ""),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason"),
        name_prefix=resolved_payload.get("name_prefix"),
        name_suffix=resolved_payload.get("name_suffix"),
        description_append=resolved_payload.get("description_append"),
        item_ids=resolved_payload.get("item_ids"),
        step_name_prefix=resolved_payload.get("step_name_prefix"),
        step_name_suffix=resolved_payload.get("step_name_suffix"),
        step_description_append=resolved_payload.get("step_description_append"),
        query_patch=resolved_payload.get("query_patch"),
        layout_patch=resolved_payload.get("layout_patch"),
        template_id=resolved_payload.get("template_id"),
        clear_template_link=resolved_payload.get("clear_template_link"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_update":
    return serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record(
      app.update_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
        resolved_path_params["hierarchy_step_template_id"],
        name=resolved_payload.get("name"),
        description=resolved_payload.get("description"),
        item_ids=resolved_payload.get("item_ids"),
        name_prefix=resolved_payload.get("name_prefix"),
        name_suffix=resolved_payload.get("name_suffix"),
        description_append=resolved_payload.get("description_append"),
        query_patch=resolved_payload.get("query_patch"),
        layout_patch=resolved_payload.get("layout_patch"),
        template_id=resolved_payload.get("template_id"),
        clear_template_link=resolved_payload.get("clear_template_link"),
        governance_policy_template_id=resolved_payload.get("governance_policy_template_id"),
        governance_policy_catalog_id=resolved_payload.get("governance_policy_catalog_id"),
        governance_approval_lane=resolved_payload.get("governance_approval_lane"),
        governance_approval_priority=resolved_payload.get("governance_approval_priority"),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_governance_hierarchy_step_template_updated"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_delete":
    return serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record(
      app.delete_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
        resolved_path_params["hierarchy_step_template_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_governance_hierarchy_step_template_deleted"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_list":
    return serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_list(
      app.get_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
        resolved_path_params["hierarchy_step_template_id"]
      ),
      app.list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions(
        resolved_path_params["hierarchy_step_template_id"]
      ),
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_restore":
    return serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record(
      app.restore_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision(
        resolved_path_params["hierarchy_step_template_id"],
        resolved_path_params["revision_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_governance_hierarchy_step_template_revision_restored"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_list":
    return serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_list(
      app.list_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audits(
        hierarchy_step_template_id=resolved_filters.get("hierarchy_step_template_id"),
        action=resolved_filters.get("action"),
        actor_tab_id=resolved_filters.get("actor_tab_id"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 50),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_apply":
    return serialize_provider_provenance_scheduler_narrative_bulk_governance_result(
      app.apply_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_to_catalogs(
        resolved_path_params["hierarchy_step_template_id"],
        resolved_payload.get("catalog_ids", ()),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_stage":
    return serialize_provider_provenance_scheduler_narrative_governance_plan_record(
      app.stage_provider_provenance_scheduler_narrative_governance_hierarchy_step_template(
        resolved_path_params["hierarchy_step_template_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get(
          "reason",
          "scheduler_narrative_governance_hierarchy_step_template_staged",
        ),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_batch_stage":
    return serialize_provider_provenance_scheduler_narrative_governance_plan_batch_result(
      app.stage_provider_provenance_scheduler_narrative_governance_hierarchy_step_templates(
        resolved_payload.get("hierarchy_step_template_ids", ()),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get(
          "reason",
          "scheduler_narrative_governance_hierarchy_step_templates_staged",
        ),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_stage":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_stage_result(
      app.stage_provider_provenance_scheduler_narrative_governance_policy_catalog(
        resolved_path_params["catalog_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_governance_policy_catalog_staged"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_plan_create":
    return serialize_provider_provenance_scheduler_narrative_governance_plan_record(
      app.create_provider_provenance_scheduler_narrative_governance_plan(
        item_type=resolved_payload.get("item_type", ""),
        item_ids=resolved_payload.get("item_ids", ()),
        action=resolved_payload.get("action", ""),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason"),
        name_prefix=resolved_payload.get("name_prefix"),
        name_suffix=resolved_payload.get("name_suffix"),
        description_append=resolved_payload.get("description_append"),
        query_patch=resolved_payload.get("query_patch"),
        layout_patch=resolved_payload.get("layout_patch"),
        queue_view_patch=resolved_payload.get("queue_view_patch"),
        default_policy_template_id=resolved_payload.get("default_policy_template_id"),
        default_policy_catalog_id=resolved_payload.get("default_policy_catalog_id"),
        occurrence_limit=resolved_payload.get("occurrence_limit"),
        history_limit=resolved_payload.get("history_limit"),
        drilldown_history_limit=resolved_payload.get("drilldown_history_limit"),
        template_id=resolved_payload.get("template_id"),
        clear_template_link=bool(resolved_payload.get("clear_template_link", False)),
        policy_template_id=resolved_payload.get("policy_template_id"),
        policy_catalog_id=resolved_payload.get("policy_catalog_id"),
        approval_lane=resolved_payload.get("approval_lane"),
        approval_priority=resolved_payload.get("approval_priority"),
        hierarchy_key=resolved_payload.get("hierarchy_key"),
        hierarchy_name=resolved_payload.get("hierarchy_name"),
        hierarchy_position=resolved_payload.get("hierarchy_position"),
        hierarchy_total=resolved_payload.get("hierarchy_total"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_plan_list":
    return serialize_provider_provenance_scheduler_narrative_governance_plan_list(
      app.list_provider_provenance_scheduler_narrative_governance_plans(
        item_type=resolved_filters.get("item_type"),
        status=resolved_filters.get("status"),
        queue_state=resolved_filters.get("queue_state"),
        approval_lane=resolved_filters.get("approval_lane"),
        approval_priority=resolved_filters.get("approval_priority"),
        policy_template_id=resolved_filters.get("policy_template_id"),
        policy_catalog_id=resolved_filters.get("policy_catalog_id"),
        source_hierarchy_step_template_id=resolved_filters.get("source_hierarchy_step_template_id"),
        search=resolved_filters.get("search"),
        sort=resolved_filters.get("sort"),
        limit=resolved_filters.get("limit", 20),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_plan_approve":
    return serialize_provider_provenance_scheduler_narrative_governance_plan_record(
      app.approve_provider_provenance_scheduler_narrative_governance_plan(
        resolved_path_params["plan_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        note=resolved_payload.get("note"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_plan_apply":
    return serialize_provider_provenance_scheduler_narrative_governance_plan_record(
      app.apply_provider_provenance_scheduler_narrative_governance_plan(
        resolved_path_params["plan_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_plan_batch_action":
    return serialize_provider_provenance_scheduler_narrative_governance_plan_batch_result(
      app.run_provider_provenance_scheduler_narrative_governance_plan_batch_action(
        action=resolved_payload.get("action", ""),
        plan_ids=resolved_payload.get("plan_ids", ()),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        note=resolved_payload.get("note"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_plan_rollback":
    return serialize_provider_provenance_scheduler_narrative_governance_plan_record(
      app.rollback_provider_provenance_scheduler_narrative_governance_plan(
        resolved_path_params["plan_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        note=resolved_payload.get("note"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduled_report_create":
    return serialize_provider_provenance_scheduled_report_record(
      app.create_provider_provenance_scheduled_report(
        name=resolved_payload["name"],
        description=resolved_payload.get("description") or "",
        query=resolved_payload.get("query"),
        layout=resolved_payload.get("layout"),
        preset_id=resolved_payload.get("preset_id"),
        view_id=resolved_payload.get("view_id"),
        cadence=resolved_payload.get("cadence") or "daily",
        status=resolved_payload.get("status") or "scheduled",
        created_by_tab_id=resolved_payload.get("created_by_tab_id"),
        created_by_tab_label=resolved_payload.get("created_by_tab_label"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduled_report_list":
    return serialize_provider_provenance_scheduled_report_list(
      app.list_provider_provenance_scheduled_reports(
        status=resolved_filters.get("status"),
        cadence=resolved_filters.get("cadence"),
        preset_id=resolved_filters.get("preset_id"),
        view_id=resolved_filters.get("view_id"),
        created_by_tab_id=resolved_filters.get("created_by_tab_id"),
        focus_scope=resolved_filters.get("focus_scope"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 50),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduled_report_run":
    return serialize_provider_provenance_scheduled_report_run_result(
      app.run_provider_provenance_scheduled_report(
        resolved_path_params["report_id"],
        source_tab_id=resolved_payload.get("source_tab_id"),
        source_tab_label=resolved_payload.get("source_tab_label"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduled_report_run_due":
    return serialize_provider_provenance_scheduled_report_run_due_result(
      app.run_due_provider_provenance_scheduled_reports(
        source_tab_id=resolved_payload.get("source_tab_id"),
        source_tab_label=resolved_payload.get("source_tab_label"),
        due_before=resolved_payload.get("due_before"),
        limit=resolved_payload.get("limit", 25),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduled_report_history":
    report = app.get_provider_provenance_scheduled_report(resolved_path_params["report_id"])
    return serialize_provider_provenance_scheduled_report_history(
      report,
      app.list_provider_provenance_scheduled_report_history(resolved_path_params["report_id"]),
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_health_history":
    current = app.get_provider_provenance_scheduler_health()
    payload = app.get_provider_provenance_scheduler_health_history_page(
      status=resolved_filters.get("status"),
      limit=resolved_filters.get("limit", 25),
      offset=resolved_filters.get("offset", 0),
    )
    return serialize_provider_provenance_scheduler_health_history(
      current,
      payload,
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_alert_history":
    payload = app.get_provider_provenance_scheduler_alert_history_page(
      category=resolved_filters.get("category"),
      status=resolved_filters.get("status"),
      narrative_facet=resolved_filters.get("narrative_facet"),
      search=resolved_filters.get("search"),
      limit=resolved_filters.get("limit", 25),
      offset=resolved_filters.get("offset", 0),
    )
    return serialize_provider_provenance_scheduler_alert_history(payload)

  if binding.binding_kind == "operator_provider_provenance_scheduler_health_analytics":
    return app.get_provider_provenance_scheduler_health_analytics(
      status=resolved_filters.get("status"),
      window_days=resolved_filters.get("window_days", 14),
      history_limit=resolved_filters.get("history_limit", 12),
      drilldown_bucket_key=resolved_filters.get("drilldown_bucket_key"),
      drilldown_history_limit=resolved_filters.get("drilldown_history_limit", 24),
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_health_export":
    return app.export_provider_provenance_scheduler_health(
      export_format=resolved_filters.get("format", "json"),
      status=resolved_filters.get("status"),
      window_days=resolved_filters.get("window_days", 14),
      history_limit=resolved_filters.get("history_limit", 12),
      drilldown_bucket_key=resolved_filters.get("drilldown_bucket_key"),
      drilldown_history_limit=resolved_filters.get("drilldown_history_limit", 24),
      offset=resolved_filters.get("offset", 0),
      limit=resolved_filters.get("limit", 25),
    )

  if binding.binding_kind == "guarded_live_status":
    return asdict(app.get_guarded_live_status())

  if binding.binding_kind == "strategy_catalog_discovery":
    return [
      serialize_strategy(strategy)
      for strategy in _apply_runtime_query_to_strategies(
        app.list_strategies(
          lane=resolved_filters.get("lane"),
          lifecycle_stage=resolved_filters.get("lifecycle_stage"),
          version=resolved_filters.get("version"),
        ),
        resolved_filters,
        binding=binding,
      )
    ]

  if binding.binding_kind == "reference_catalog_discovery":
    return [asdict(reference) for reference in app.list_references()]

  if binding.binding_kind == "preset_catalog_discovery":
    return [
      serialize_preset(preset)
      for preset in _apply_runtime_query_to_presets(
        app.list_presets(
          strategy_id=resolved_filters.get("strategy_id"),
          timeframe=resolved_filters.get("timeframe"),
          lifecycle_stage=resolved_filters.get("lifecycle_stage"),
        ),
        resolved_filters,
        binding=binding,
      )
    ]

  if binding.binding_kind == "preset_catalog_create":
    preset = app.create_preset(
      name=resolved_payload["name"],
      preset_id=resolved_payload.get("preset_id"),
      description=resolved_payload.get("description") or "",
      strategy_id=resolved_payload.get("strategy_id"),
      timeframe=resolved_payload.get("timeframe"),
      tags=resolved_payload.get("tags") or [],
      parameters=resolved_payload.get("parameters") or {},
      benchmark_family=resolved_payload.get("benchmark_family"),
    )
    return serialize_preset(preset)

  if binding.binding_kind == "preset_catalog_item_get":
    preset = app.get_preset(
      preset_id=resolved_path_params["preset_id"],
    )
    return serialize_preset(preset)

  if binding.binding_kind == "preset_catalog_item_update":
    changes = {
      key: value
      for key, value in resolved_payload.items()
      if key not in {"actor", "reason"}
    }
    preset = app.update_preset(
      preset_id=resolved_path_params["preset_id"],
      changes=changes,
      actor=resolved_payload.get("actor", "operator"),
      reason=resolved_payload.get("reason", "manual_preset_edit"),
    )
    return serialize_preset(preset)

  if binding.binding_kind == "preset_catalog_revision_list":
    return [
      serialize_preset_revision(revision)
      for revision in app.list_preset_revisions(
        preset_id=resolved_path_params["preset_id"],
      )
    ]

  if binding.binding_kind == "preset_catalog_revision_restore":
    preset = app.restore_preset_revision(
      preset_id=resolved_path_params["preset_id"],
      revision_id=resolved_path_params["revision_id"],
      actor=resolved_payload.get("actor", "operator"),
      reason=resolved_payload.get("reason", "manual_preset_revision_restore"),
    )
    return serialize_preset(preset)

  if binding.binding_kind == "preset_catalog_lifecycle_apply":
    preset = app.apply_preset_lifecycle_action(
      preset_id=resolved_path_params["preset_id"],
      action=resolved_payload["action"],
      actor=resolved_payload.get("actor", "operator"),
      reason=resolved_payload.get("reason", "manual_preset_lifecycle_action"),
      lineage_evidence_pack_id=resolved_payload.get("lineage_evidence_pack_id"),
      lineage_evidence_retention_expires_at=resolved_payload.get(
        "lineage_evidence_retention_expires_at"
      ),
      lineage_evidence_summary=resolved_payload.get("lineage_evidence_summary"),
    )
    return serialize_preset(preset)

  return UNHANDLED
