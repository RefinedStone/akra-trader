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

def handle_standalone_surface_binding_part_2(
  *,
  binding: StandaloneSurfaceRuntimeBinding,
  app: Any,
  run_id: str | None,
  resolved_filters: dict[str, Any],
  resolved_payload: dict[str, Any],
  resolved_path_params: dict[str, Any],
  resolved_headers: dict[str, Any],
) -> Any:
  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_governance_registry_update":
    return serialize_provider_provenance_scheduler_stitched_report_governance_registry_record(
      app.update_provider_provenance_scheduler_stitched_report_governance_registry(
        resolved_path_params["registry_id"],
        name=resolved_payload.get("name"),
        description=resolved_payload.get("description"),
        queue_view=resolved_payload.get("queue_view"),
        default_policy_template_id=resolved_payload.get("default_policy_template_id"),
        default_policy_catalog_id=resolved_payload.get("default_policy_catalog_id"),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_stitched_report_governance_registry_updated"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_governance_registry_delete":
    return serialize_provider_provenance_scheduler_stitched_report_governance_registry_record(
      app.delete_provider_provenance_scheduler_stitched_report_governance_registry(
        resolved_path_params["registry_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_stitched_report_governance_registry_deleted"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_list":
    registry = app.get_provider_provenance_scheduler_stitched_report_governance_registry(
      resolved_path_params["registry_id"]
    )
    return serialize_provider_provenance_scheduler_stitched_report_governance_registry_revision_list(
      registry,
      app.list_provider_provenance_scheduler_stitched_report_governance_registry_revisions(
        resolved_path_params["registry_id"]
      ),
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_restore":
    return serialize_provider_provenance_scheduler_stitched_report_governance_registry_record(
      app.restore_provider_provenance_scheduler_stitched_report_governance_registry_revision(
        resolved_path_params["registry_id"],
        resolved_path_params["revision_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_stitched_report_governance_registry_revision_restored"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_governance_registry_bulk_governance":
    return serialize_provider_provenance_scheduler_narrative_bulk_governance_result(
      app.bulk_govern_provider_provenance_scheduler_stitched_report_governance_registries(
        resolved_payload.get("registry_ids", ()),
        action=resolved_payload.get("action", ""),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason"),
        name_prefix=resolved_payload.get("name_prefix"),
        name_suffix=resolved_payload.get("name_suffix"),
        description_append=resolved_payload.get("description_append"),
        queue_view_patch=resolved_payload.get("queue_view_patch"),
        default_policy_template_id=resolved_payload.get("default_policy_template_id"),
        default_policy_catalog_id=resolved_payload.get("default_policy_catalog_id"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_governance_registry_audit_list":
    return serialize_provider_provenance_scheduler_stitched_report_governance_registry_audit_list(
      app.list_provider_provenance_scheduler_stitched_report_governance_registry_audits(
        registry_id=resolved_filters.get("registry_id"),
        action=resolved_filters.get("action"),
        actor_tab_id=resolved_filters.get("actor_tab_id"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 50),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_governance_policy_template_list":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_template_list(
      app.list_provider_provenance_scheduler_narrative_governance_policy_templates(
        item_type_scope="stitched_report_governance_registry",
        action_scope=resolved_filters.get("action_scope"),
        approval_lane=resolved_filters.get("approval_lane"),
        approval_priority=resolved_filters.get("approval_priority"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 50),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_governance_policy_catalog_list":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_list(
      app.list_provider_provenance_scheduler_narrative_governance_policy_catalogs(
        item_type_scope="stitched_report_governance_registry",
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 20),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_governance_plan_create":
    return serialize_provider_provenance_scheduler_narrative_governance_plan_record(
      app.create_provider_provenance_scheduler_narrative_governance_plan(
        item_type="stitched_report_governance_registry",
        item_ids=resolved_payload.get("item_ids", ()),
        action=resolved_payload.get("action", ""),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason"),
        name_prefix=resolved_payload.get("name_prefix"),
        name_suffix=resolved_payload.get("name_suffix"),
        description_append=resolved_payload.get("description_append"),
        queue_view_patch=resolved_payload.get("queue_view_patch"),
        default_policy_template_id=resolved_payload.get("default_policy_template_id"),
        default_policy_catalog_id=resolved_payload.get("default_policy_catalog_id"),
        policy_template_id=resolved_payload.get("policy_template_id"),
        policy_catalog_id=resolved_payload.get("policy_catalog_id"),
        approval_lane=resolved_payload.get("approval_lane"),
        approval_priority=resolved_payload.get("approval_priority"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_governance_plan_list":
    return serialize_provider_provenance_scheduler_narrative_governance_plan_list(
      app.list_provider_provenance_scheduler_narrative_governance_plans(
        item_type="stitched_report_governance_registry",
        status=resolved_filters.get("status"),
        queue_state=resolved_filters.get("queue_state"),
        approval_lane=resolved_filters.get("approval_lane"),
        approval_priority=resolved_filters.get("approval_priority"),
        policy_template_id=resolved_filters.get("policy_template_id"),
        policy_catalog_id=resolved_filters.get("policy_catalog_id"),
        search=resolved_filters.get("search"),
        sort=resolved_filters.get("sort"),
        limit=resolved_filters.get("limit", 20),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_governance_plan_approve":
    return serialize_provider_provenance_scheduler_narrative_governance_plan_record(
      app.approve_provider_provenance_scheduler_narrative_governance_plan(
        resolved_path_params["plan_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        note=resolved_payload.get("note"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_governance_plan_apply":
    return serialize_provider_provenance_scheduler_narrative_governance_plan_record(
      app.apply_provider_provenance_scheduler_narrative_governance_plan(
        resolved_path_params["plan_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_governance_plan_rollback":
    return serialize_provider_provenance_scheduler_narrative_governance_plan_record(
      app.rollback_provider_provenance_scheduler_narrative_governance_plan(
        resolved_path_params["plan_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        note=resolved_payload.get("note"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_template_create":
    return serialize_provider_provenance_scheduler_narrative_template_record(
      app.create_provider_provenance_scheduler_narrative_template(
        name=resolved_payload["name"],
        description=resolved_payload.get("description") or "",
        query=resolved_payload.get("query"),
        created_by_tab_id=resolved_payload.get("created_by_tab_id"),
        created_by_tab_label=resolved_payload.get("created_by_tab_label"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_template_list":
    return serialize_provider_provenance_scheduler_narrative_template_list(
      app.list_provider_provenance_scheduler_narrative_templates(
        created_by_tab_id=resolved_filters.get("created_by_tab_id"),
        focus_scope=resolved_filters.get("focus_scope"),
        category=resolved_filters.get("category"),
        narrative_facet=resolved_filters.get("narrative_facet"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 50),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_template_update":
    return serialize_provider_provenance_scheduler_narrative_template_record(
      app.update_provider_provenance_scheduler_narrative_template(
        resolved_path_params["template_id"],
        name=resolved_payload.get("name"),
        description=resolved_payload.get("description"),
        query=resolved_payload.get("query"),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_template_updated"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_template_delete":
    return serialize_provider_provenance_scheduler_narrative_template_record(
      app.delete_provider_provenance_scheduler_narrative_template(
        resolved_path_params["template_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_template_deleted"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_template_bulk_governance":
    return serialize_provider_provenance_scheduler_narrative_bulk_governance_result(
      app.bulk_govern_provider_provenance_scheduler_narrative_templates(
        resolved_payload.get("template_ids", ()),
        action=resolved_payload.get("action", ""),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason"),
        name_prefix=resolved_payload.get("name_prefix"),
        name_suffix=resolved_payload.get("name_suffix"),
        description_append=resolved_payload.get("description_append"),
        query_patch=resolved_payload.get("query_patch"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_template_revision_list":
    template = app.get_provider_provenance_scheduler_narrative_template(
      resolved_path_params["template_id"]
    )
    return serialize_provider_provenance_scheduler_narrative_template_revision_list(
      template,
      app.list_provider_provenance_scheduler_narrative_template_revisions(
        resolved_path_params["template_id"]
      ),
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_template_revision_restore":
    return serialize_provider_provenance_scheduler_narrative_template_record(
      app.restore_provider_provenance_scheduler_narrative_template_revision(
        resolved_path_params["template_id"],
        resolved_path_params["revision_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_template_revision_restored"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_registry_create":
    return serialize_provider_provenance_scheduler_narrative_registry_record(
      app.create_provider_provenance_scheduler_narrative_registry_entry(
        name=resolved_payload["name"],
        description=resolved_payload.get("description") or "",
        query=resolved_payload.get("query"),
        layout=resolved_payload.get("layout"),
        template_id=resolved_payload.get("template_id"),
        created_by_tab_id=resolved_payload.get("created_by_tab_id"),
        created_by_tab_label=resolved_payload.get("created_by_tab_label"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_registry_list":
    return serialize_provider_provenance_scheduler_narrative_registry_list(
      app.list_provider_provenance_scheduler_narrative_registry_entries(
        template_id=resolved_filters.get("template_id"),
        created_by_tab_id=resolved_filters.get("created_by_tab_id"),
        focus_scope=resolved_filters.get("focus_scope"),
        category=resolved_filters.get("category"),
        narrative_facet=resolved_filters.get("narrative_facet"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 50),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_registry_update":
    return serialize_provider_provenance_scheduler_narrative_registry_record(
      app.update_provider_provenance_scheduler_narrative_registry_entry(
        resolved_path_params["registry_id"],
        name=resolved_payload.get("name"),
        description=resolved_payload.get("description"),
        query=resolved_payload.get("query"),
        layout=resolved_payload.get("layout"),
        template_id=resolved_payload.get("template_id"),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_registry_updated"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_registry_delete":
    return serialize_provider_provenance_scheduler_narrative_registry_record(
      app.delete_provider_provenance_scheduler_narrative_registry_entry(
        resolved_path_params["registry_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_registry_deleted"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_registry_bulk_governance":
    return serialize_provider_provenance_scheduler_narrative_bulk_governance_result(
      app.bulk_govern_provider_provenance_scheduler_narrative_registry_entries(
        resolved_payload.get("registry_ids", ()),
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
        clear_template_link=bool(resolved_payload.get("clear_template_link", False)),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_registry_revision_list":
    registry = app.get_provider_provenance_scheduler_narrative_registry_entry(
      resolved_path_params["registry_id"]
    )
    return serialize_provider_provenance_scheduler_narrative_registry_revision_list(
      registry,
      app.list_provider_provenance_scheduler_narrative_registry_revisions(
        resolved_path_params["registry_id"]
      ),
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_registry_revision_restore":
    return serialize_provider_provenance_scheduler_narrative_registry_record(
      app.restore_provider_provenance_scheduler_narrative_registry_revision(
        resolved_path_params["registry_id"],
        resolved_path_params["revision_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_registry_revision_restored"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_template_create":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_template_record(
      app.create_provider_provenance_scheduler_narrative_governance_policy_template(
        name=resolved_payload.get("name", ""),
        description=resolved_payload.get("description", ""),
        item_type_scope=resolved_payload.get("item_type_scope"),
        action_scope=resolved_payload.get("action_scope"),
        approval_lane=resolved_payload.get("approval_lane"),
        approval_priority=resolved_payload.get("approval_priority"),
        guidance=resolved_payload.get("guidance"),
        created_by_tab_id=resolved_payload.get("created_by_tab_id"),
        created_by_tab_label=resolved_payload.get("created_by_tab_label"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_template_list":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_template_list(
      app.list_provider_provenance_scheduler_narrative_governance_policy_templates(
        item_type_scope=resolved_filters.get("item_type_scope"),
        action_scope=resolved_filters.get("action_scope"),
        approval_lane=resolved_filters.get("approval_lane"),
        approval_priority=resolved_filters.get("approval_priority"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 50),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_template_update":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_template_record(
      app.update_provider_provenance_scheduler_narrative_governance_policy_template(
        resolved_path_params["policy_template_id"],
        name=resolved_payload.get("name"),
        description=resolved_payload.get("description"),
        item_type_scope=resolved_payload.get("item_type_scope"),
        action_scope=resolved_payload.get("action_scope"),
        approval_lane=resolved_payload.get("approval_lane"),
        approval_priority=resolved_payload.get("approval_priority"),
        guidance=resolved_payload.get("guidance"),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_governance_policy_template_updated"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_template_delete":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_template_record(
      app.delete_provider_provenance_scheduler_narrative_governance_policy_template(
        resolved_path_params["policy_template_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_governance_policy_template_deleted"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_list":
    policy_template = app.get_provider_provenance_scheduler_narrative_governance_policy_template(
      resolved_path_params["policy_template_id"]
    )
    return serialize_provider_provenance_scheduler_narrative_governance_policy_template_revision_list(
      policy_template,
      app.list_provider_provenance_scheduler_narrative_governance_policy_template_revisions(
        resolved_path_params["policy_template_id"]
      ),
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_restore":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_template_record(
      app.restore_provider_provenance_scheduler_narrative_governance_policy_template_revision(
        resolved_path_params["policy_template_id"],
        resolved_path_params["revision_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_governance_policy_template_revision_restored"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_template_audit_list":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_template_audit_list(
      app.list_provider_provenance_scheduler_narrative_governance_policy_template_audits(
        policy_template_id=resolved_filters.get("policy_template_id"),
        action=resolved_filters.get("action"),
        actor_tab_id=resolved_filters.get("actor_tab_id"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 50),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_create":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
      app.create_provider_provenance_scheduler_narrative_governance_policy_catalog(
        name=resolved_payload.get("name", ""),
        description=resolved_payload.get("description", ""),
        policy_template_ids=resolved_payload.get("policy_template_ids", ()),
        default_policy_template_id=resolved_payload.get("default_policy_template_id"),
        created_by_tab_id=resolved_payload.get("created_by_tab_id"),
        created_by_tab_label=resolved_payload.get("created_by_tab_label"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_list":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_list(
      app.list_provider_provenance_scheduler_narrative_governance_policy_catalogs(
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 20),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_update":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
      app.update_provider_provenance_scheduler_narrative_governance_policy_catalog(
        resolved_path_params["catalog_id"],
        name=resolved_payload.get("name"),
        description=resolved_payload.get("description"),
        policy_template_ids=resolved_payload.get("policy_template_ids"),
        default_policy_template_id=resolved_payload.get("default_policy_template_id"),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_governance_policy_catalog_updated"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_delete":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
      app.delete_provider_provenance_scheduler_narrative_governance_policy_catalog(
        resolved_path_params["catalog_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_governance_policy_catalog_deleted"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_bulk_governance":
    return serialize_provider_provenance_scheduler_narrative_bulk_governance_result(
      app.bulk_govern_provider_provenance_scheduler_narrative_governance_policy_catalogs(
        resolved_payload.get("catalog_ids", ()),
        action=resolved_payload.get("action", ""),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason"),
        name_prefix=resolved_payload.get("name_prefix"),
        name_suffix=resolved_payload.get("name_suffix"),
        description_append=resolved_payload.get("description_append"),
        default_policy_template_id=resolved_payload.get("default_policy_template_id"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list":
    catalog = app.get_provider_provenance_scheduler_narrative_governance_policy_catalog(
      resolved_path_params["catalog_id"]
    )
    return serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list(
      catalog,
      app.list_provider_provenance_scheduler_narrative_governance_policy_catalog_revisions(
        resolved_path_params["catalog_id"]
      ),
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_restore":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record(
      app.restore_provider_provenance_scheduler_narrative_governance_policy_catalog_revision(
        resolved_path_params["catalog_id"],
        resolved_path_params["revision_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_narrative_governance_policy_catalog_revision_restored"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_list":
    return serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_list(
      app.list_provider_provenance_scheduler_narrative_governance_policy_catalog_audits(
        catalog_id=resolved_filters.get("catalog_id"),
        action=resolved_filters.get("action"),
        actor_tab_id=resolved_filters.get("actor_tab_id"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 50),
      )
    )

  return UNHANDLED
