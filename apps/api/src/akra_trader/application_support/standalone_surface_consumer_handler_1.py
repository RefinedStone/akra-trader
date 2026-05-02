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

def handle_standalone_surface_binding_part_1(
  *,
  binding: StandaloneSurfaceRuntimeBinding,
  app: Any,
  run_id: str | None,
  resolved_filters: dict[str, Any],
  resolved_payload: dict[str, Any],
  resolved_path_params: dict[str, Any],
  resolved_headers: dict[str, Any],
) -> Any:
  if binding.binding_kind == "health_status":
    return {"status": "ok"}

  if binding.binding_kind == "run_surface_capabilities":
    return serialize_run_surface_capabilities(app.get_run_surface_capabilities())

  if binding.binding_kind == "replay_link_alias_create":
    return serialize_replay_intent_alias_record(
      app.create_replay_intent_alias(
        template_key=resolved_payload["template_key"],
        template_label=resolved_payload.get("template_label"),
        intent=resolved_payload["intent"],
        redaction_policy=resolved_payload.get("redaction_policy", "full"),
        retention_policy=resolved_payload.get("retention_policy", "30d"),
        source_tab_id=resolved_payload.get("source_tab_id"),
        source_tab_label=resolved_payload.get("source_tab_label"),
      )
    )

  if binding.binding_kind == "replay_link_alias_resolve":
    return serialize_replay_intent_alias_record(
      app.resolve_replay_intent_alias(resolved_path_params["alias_token"])
    )

  if binding.binding_kind == "replay_link_alias_history":
    resolved_record = app.get_replay_intent_alias(
      resolved_path_params["alias_token"],
      require_active=False,
    )
    return serialize_replay_intent_alias_history(
      resolved_record,
      app.list_replay_intent_alias_history(resolved_path_params["alias_token"]),
    )

  if binding.binding_kind == "replay_link_audit_list":
    app.require_replay_alias_audit_admin_token(
      resolved_headers.get("x_akra_replay_audit_admin_token"),
      scope="read",
    )
    return serialize_replay_intent_alias_audit_list(
      app.list_replay_intent_alias_audits(
        alias_id=resolved_filters.get("alias_id"),
        template_key=resolved_filters.get("template_key"),
        action=resolved_filters.get("action"),
        retention_policy=resolved_filters.get("retention_policy"),
        source_tab_id=resolved_filters.get("source_tab_id"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 100),
      )
    )

  if binding.binding_kind == "replay_link_audit_export":
    app.require_replay_alias_audit_admin_token(
      resolved_headers.get("x_akra_replay_audit_admin_token"),
      scope="read",
    )
    return app.export_replay_intent_alias_audits(
      export_format=resolved_filters.get("format", "json"),
      alias_id=resolved_filters.get("alias_id"),
      template_key=resolved_filters.get("template_key"),
      action=resolved_filters.get("action"),
      retention_policy=resolved_filters.get("retention_policy"),
      source_tab_id=resolved_filters.get("source_tab_id"),
      search=resolved_filters.get("search"),
    )

  if binding.binding_kind == "replay_link_audit_export_job_create":
    app.require_replay_alias_audit_admin_token(
      resolved_headers.get("x_akra_replay_audit_admin_token"),
      scope="write",
    )
    return serialize_replay_intent_alias_audit_export_job_record(
      app.create_replay_intent_alias_audit_export_job(
        export_format=resolved_payload.get("format", "json"),
        alias_id=resolved_payload.get("alias_id"),
        template_key=resolved_payload.get("template_key"),
        action=resolved_payload.get("action"),
        retention_policy=resolved_payload.get("retention_policy"),
        source_tab_id=resolved_payload.get("source_tab_id"),
        search=resolved_payload.get("search"),
        requested_by_tab_id=resolved_payload.get("requested_by_tab_id"),
        requested_by_tab_label=resolved_payload.get("requested_by_tab_label"),
      )
    )

  if binding.binding_kind == "replay_link_audit_export_job_list":
    app.require_replay_alias_audit_admin_token(
      resolved_headers.get("x_akra_replay_audit_admin_token"),
      scope="read",
    )
    return serialize_replay_intent_alias_audit_export_job_list(
      app.list_replay_intent_alias_audit_export_jobs(
        template_key=resolved_filters.get("template_key"),
        export_format=resolved_filters.get("format"),
        status=resolved_filters.get("status"),
        requested_by_tab_id=resolved_filters.get("requested_by_tab_id"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 100),
      )
    )

  if binding.binding_kind == "replay_link_audit_export_job_download":
    app.require_replay_alias_audit_admin_token(
      resolved_headers.get("x_akra_replay_audit_admin_token"),
      scope="read",
    )
    return app.download_replay_intent_alias_audit_export_job(resolved_path_params["job_id"])

  if binding.binding_kind == "replay_link_audit_export_job_history":
    app.require_replay_alias_audit_admin_token(
      resolved_headers.get("x_akra_replay_audit_admin_token"),
      scope="read",
    )
    export_job = app.get_replay_intent_alias_audit_export_job(resolved_path_params["job_id"])
    return serialize_replay_intent_alias_audit_export_job_history(
      export_job,
      app.list_replay_intent_alias_audit_export_job_history(resolved_path_params["job_id"]),
    )

  if binding.binding_kind == "replay_link_audit_export_job_prune":
    app.require_replay_alias_audit_admin_token(
      resolved_headers.get("x_akra_replay_audit_admin_token"),
      scope="write",
    )
    return app.prune_replay_intent_alias_audit_export_jobs(
      template_key=resolved_payload.get("template_key"),
      export_format=resolved_payload.get("format"),
      status=resolved_payload.get("status"),
      requested_by_tab_id=resolved_payload.get("requested_by_tab_id"),
      search=resolved_payload.get("search"),
      created_before=resolved_payload.get("created_before"),
      prune_mode=resolved_payload.get("prune_mode", "expired"),
    )

  if binding.binding_kind == "replay_link_audit_prune":
    app.require_replay_alias_audit_admin_token(
      resolved_headers.get("x_akra_replay_audit_admin_token"),
      scope="write",
    )
    return app.prune_replay_intent_alias_audits(
      alias_id=resolved_payload.get("alias_id"),
      template_key=resolved_payload.get("template_key"),
      action=resolved_payload.get("action"),
      retention_policy=resolved_payload.get("retention_policy"),
      source_tab_id=resolved_payload.get("source_tab_id"),
      search=resolved_payload.get("search"),
      recorded_before=resolved_payload.get("recorded_before"),
      include_manual=resolved_payload.get("include_manual", False),
      prune_mode=resolved_payload.get("prune_mode", "expired"),
    )

  if binding.binding_kind == "replay_link_alias_revoke":
    return serialize_replay_intent_alias_record(
      app.revoke_replay_intent_alias(
        resolved_path_params["alias_token"],
        source_tab_id=resolved_payload.get("source_tab_id"),
        source_tab_label=resolved_payload.get("source_tab_label"),
      )
    )

  if binding.binding_kind == "market_data_status":
    return asdict(app.get_market_data_status(resolved_filters.get("timeframe") or "5m"))

  if binding.binding_kind == "market_data_lineage_history":
    return [
      asdict(record)
      for record in _apply_runtime_query_to_market_data_lineage_history(
        app.list_market_data_lineage_history(
          timeframe=resolved_filters.get("timeframe"),
          symbol=resolved_filters.get("symbol"),
          sync_status=resolved_filters.get("sync_status"),
          validation_claim=resolved_filters.get("validation_claim"),
        ),
        resolved_filters,
        binding=binding,
      )
    ]

  if binding.binding_kind == "market_data_ingestion_job_history":
    return [
      asdict(record)
      for record in _apply_runtime_query_to_market_data_ingestion_jobs(
        app.list_market_data_ingestion_jobs(
          timeframe=resolved_filters.get("timeframe"),
          symbol=resolved_filters.get("symbol"),
          operation=resolved_filters.get("operation"),
          status=resolved_filters.get("status"),
        ),
        resolved_filters,
        binding=binding,
      )
    ]

  if binding.binding_kind == "market_data_lineage_evidence_retention_prune":
    return asdict(
      app.prune_operator_lineage_evidence_retention(
        dry_run=resolved_payload.get("dry_run", False),
        lineage_history_days=resolved_payload.get("lineage_history_days"),
        lineage_issue_history_days=resolved_payload.get("lineage_issue_history_days"),
        ingestion_job_days=resolved_payload.get("ingestion_job_days"),
        ingestion_issue_job_days=resolved_payload.get("ingestion_issue_job_days"),
        protected_history_ids=tuple(resolved_payload.get("protected_history_ids") or ()),
        protected_job_ids=tuple(resolved_payload.get("protected_job_ids") or ()),
      )
    )

  if binding.binding_kind == "market_data_lineage_drill_evidence_pack_export":
    return asdict(
      app.export_operator_lineage_drill_evidence_pack(
        scenario_key=resolved_payload.get("scenario_key"),
        scenario_label=resolved_payload.get("scenario_label"),
        incident_id=resolved_payload.get("incident_id"),
        operator_decision=resolved_payload.get("operator_decision", "reviewed"),
        final_posture=resolved_payload.get("final_posture", "unresolved"),
        venue=resolved_payload.get("venue"),
        symbol=resolved_payload.get("symbol"),
        timeframe=resolved_payload.get("timeframe"),
        sync_status=resolved_payload.get("sync_status"),
        validation_claim=resolved_payload.get("validation_claim"),
        operation=resolved_payload.get("operation"),
        status=resolved_payload.get("status"),
        source_run_id=resolved_payload.get("source_run_id"),
        rerun_id=resolved_payload.get("rerun_id"),
        dataset_identity=resolved_payload.get("dataset_identity"),
        sync_checkpoint_id=resolved_payload.get("sync_checkpoint_id"),
        rerun_boundary_id=resolved_payload.get("rerun_boundary_id"),
        rerun_validation_category=resolved_payload.get("rerun_validation_category"),
        generated_by=resolved_payload.get("generated_by", "operator"),
        export_format=resolved_payload.get("format", "json"),
        lineage_history_limit=resolved_payload.get("lineage_history_limit"),
        ingestion_job_limit=resolved_payload.get("ingestion_job_limit"),
      )
    )

  if binding.binding_kind == "operator_visibility":
    return asdict(app.get_operator_visibility())

  if binding.binding_kind == "operator_provider_provenance_export_job_create":
    return serialize_provider_provenance_export_job_record(
      app.create_provider_provenance_export_job(
        content=resolved_payload.get("content", ""),
        requested_by_tab_id=resolved_payload.get("requested_by_tab_id"),
        requested_by_tab_label=resolved_payload.get("requested_by_tab_label"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_export_job_list":
    return serialize_provider_provenance_export_job_list(
      app.list_provider_provenance_export_jobs(
        export_scope=resolved_filters.get("export_scope"),
        focus_key=resolved_filters.get("focus_key"),
        symbol=resolved_filters.get("symbol"),
        timeframe=resolved_filters.get("timeframe"),
        provider_label=resolved_filters.get("provider_label"),
        vendor_field=resolved_filters.get("vendor_field"),
        market_data_provider=resolved_filters.get("market_data_provider"),
        venue=resolved_filters.get("venue"),
        requested_by_tab_id=resolved_filters.get("requested_by_tab_id"),
        status=resolved_filters.get("status"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 100),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_export_analytics":
    return app.get_provider_provenance_export_analytics(
      focus_key=resolved_filters.get("focus_key"),
      symbol=resolved_filters.get("symbol"),
      timeframe=resolved_filters.get("timeframe"),
      provider_label=resolved_filters.get("provider_label"),
      vendor_field=resolved_filters.get("vendor_field"),
      market_data_provider=resolved_filters.get("market_data_provider"),
      venue=resolved_filters.get("venue"),
      requested_by_tab_id=resolved_filters.get("requested_by_tab_id"),
      status=resolved_filters.get("status"),
      search=resolved_filters.get("search"),
      result_limit=resolved_filters.get("result_limit", 12),
      window_days=resolved_filters.get("window_days", 14),
    )

  if binding.binding_kind == "operator_provider_provenance_export_job_download":
    return app.download_provider_provenance_export_job(
      resolved_path_params["job_id"],
      source_tab_id=resolved_filters.get("source_tab_id"),
      source_tab_label=resolved_filters.get("source_tab_label"),
    )

  if binding.binding_kind == "operator_provider_provenance_export_job_history":
    export_job = app.get_provider_provenance_export_job(resolved_path_params["job_id"])
    return serialize_provider_provenance_export_job_history(
      export_job,
      app.list_provider_provenance_export_job_history(resolved_path_params["job_id"]),
    )

  if binding.binding_kind == "operator_provider_provenance_export_job_policy":
    policy_result = app.update_provider_provenance_export_job_routing_policy(
      resolved_path_params["job_id"],
      actor=resolved_payload.get("actor", "operator"),
      routing_policy_id=resolved_payload.get("routing_policy_id", "default"),
      approval_policy_id=resolved_payload.get("approval_policy_id", "auto"),
      source_tab_id=resolved_payload.get("source_tab_id"),
      source_tab_label=resolved_payload.get("source_tab_label"),
      delivery_targets=resolved_payload.get("delivery_targets"),
    )
    return serialize_provider_provenance_export_job_policy_result(
      policy_result["export_job"],
      policy_result["audit_record"],
    )

  if binding.binding_kind == "operator_provider_provenance_export_job_approval":
    approval_result = app.approve_provider_provenance_export_job(
      resolved_path_params["job_id"],
      actor=resolved_payload.get("actor", "operator"),
      note=resolved_payload.get("note"),
      source_tab_id=resolved_payload.get("source_tab_id"),
      source_tab_label=resolved_payload.get("source_tab_label"),
    )
    return serialize_provider_provenance_export_job_policy_result(
      approval_result["export_job"],
      approval_result["audit_record"],
    )

  if binding.binding_kind == "operator_provider_provenance_export_job_escalate":
    escalation_result = app.escalate_provider_provenance_export_job(
      resolved_path_params["job_id"],
      actor=resolved_payload.get("actor", "operator"),
      reason=resolved_payload.get("reason", "scheduler_health_review"),
      source_tab_id=resolved_payload.get("source_tab_id"),
      source_tab_label=resolved_payload.get("source_tab_label"),
      delivery_targets=resolved_payload.get("delivery_targets"),
    )
    return serialize_provider_provenance_export_job_escalation_result(
      escalation_result["export_job"],
      escalation_result["audit_record"],
      escalation_result["delivery_history"],
    )

  if binding.binding_kind == "operator_provider_provenance_analytics_preset_create":
    return serialize_provider_provenance_analytics_preset_record(
      app.create_provider_provenance_analytics_preset(
        name=resolved_payload["name"],
        description=resolved_payload.get("description") or "",
        query=resolved_payload.get("query"),
        created_by_tab_id=resolved_payload.get("created_by_tab_id"),
        created_by_tab_label=resolved_payload.get("created_by_tab_label"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_analytics_preset_list":
    return serialize_provider_provenance_analytics_preset_list(
      app.list_provider_provenance_analytics_presets(
        created_by_tab_id=resolved_filters.get("created_by_tab_id"),
        focus_scope=resolved_filters.get("focus_scope"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 50),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_dashboard_view_create":
    return serialize_provider_provenance_dashboard_view_record(
      app.create_provider_provenance_dashboard_view(
        name=resolved_payload["name"],
        description=resolved_payload.get("description") or "",
        query=resolved_payload.get("query"),
        layout=resolved_payload.get("layout"),
        preset_id=resolved_payload.get("preset_id"),
        created_by_tab_id=resolved_payload.get("created_by_tab_id"),
        created_by_tab_label=resolved_payload.get("created_by_tab_label"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_dashboard_view_list":
    return serialize_provider_provenance_dashboard_view_list(
      app.list_provider_provenance_dashboard_views(
        preset_id=resolved_filters.get("preset_id"),
        created_by_tab_id=resolved_filters.get("created_by_tab_id"),
        focus_scope=resolved_filters.get("focus_scope"),
        highlight_panel=resolved_filters.get("highlight_panel"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 50),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_view_create":
    return serialize_provider_provenance_scheduler_stitched_report_view_record(
      app.create_provider_provenance_scheduler_stitched_report_view(
        name=resolved_payload["name"],
        description=resolved_payload.get("description") or "",
        query=resolved_payload.get("query"),
        occurrence_limit=resolved_payload.get("occurrence_limit", 8),
        history_limit=resolved_payload.get("history_limit", 12),
        drilldown_history_limit=resolved_payload.get("drilldown_history_limit", 12),
        created_by_tab_id=resolved_payload.get("created_by_tab_id"),
        created_by_tab_label=resolved_payload.get("created_by_tab_label"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_view_list":
    return serialize_provider_provenance_scheduler_stitched_report_view_list(
      app.list_provider_provenance_scheduler_stitched_report_views(
        created_by_tab_id=resolved_filters.get("created_by_tab_id"),
        category=resolved_filters.get("category"),
        narrative_facet=resolved_filters.get("narrative_facet"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 50),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_view_update":
    return serialize_provider_provenance_scheduler_stitched_report_view_record(
      app.update_provider_provenance_scheduler_stitched_report_view(
        resolved_path_params["view_id"],
        name=resolved_payload.get("name"),
        description=resolved_payload.get("description"),
        query=resolved_payload.get("query"),
        occurrence_limit=resolved_payload.get("occurrence_limit"),
        history_limit=resolved_payload.get("history_limit"),
        drilldown_history_limit=resolved_payload.get("drilldown_history_limit"),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_stitched_report_view_updated"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_view_delete":
    return serialize_provider_provenance_scheduler_stitched_report_view_record(
      app.delete_provider_provenance_scheduler_stitched_report_view(
        resolved_path_params["view_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_stitched_report_view_deleted"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_view_bulk_governance":
    return serialize_provider_provenance_scheduler_narrative_bulk_governance_result(
      app.bulk_govern_provider_provenance_scheduler_stitched_report_views(
        resolved_payload.get("view_ids", ()),
        action=resolved_payload.get("action", ""),
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason"),
        name_prefix=resolved_payload.get("name_prefix"),
        name_suffix=resolved_payload.get("name_suffix"),
        description_append=resolved_payload.get("description_append"),
        query_patch=resolved_payload.get("query_patch"),
        occurrence_limit=resolved_payload.get("occurrence_limit"),
        history_limit=resolved_payload.get("history_limit"),
        drilldown_history_limit=resolved_payload.get("drilldown_history_limit"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_view_revision_list":
    view = app.get_provider_provenance_scheduler_stitched_report_view(
      resolved_path_params["view_id"]
    )
    return serialize_provider_provenance_scheduler_stitched_report_view_revision_list(
      view,
      app.list_provider_provenance_scheduler_stitched_report_view_revisions(
        resolved_path_params["view_id"]
      ),
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_view_revision_restore":
    return serialize_provider_provenance_scheduler_stitched_report_view_record(
      app.restore_provider_provenance_scheduler_stitched_report_view_revision(
        resolved_path_params["view_id"],
        resolved_path_params["revision_id"],
        actor_tab_id=resolved_payload.get("actor_tab_id"),
        actor_tab_label=resolved_payload.get("actor_tab_label"),
        reason=resolved_payload.get("reason", "scheduler_stitched_report_view_revision_restored"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_view_audit_list":
    return serialize_provider_provenance_scheduler_stitched_report_view_audit_list(
      app.list_provider_provenance_scheduler_stitched_report_view_audits(
        view_id=resolved_filters.get("view_id"),
        action=resolved_filters.get("action"),
        actor_tab_id=resolved_filters.get("actor_tab_id"),
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 50),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_governance_registry_create":
    return serialize_provider_provenance_scheduler_stitched_report_governance_registry_record(
      app.create_provider_provenance_scheduler_stitched_report_governance_registry(
        name=resolved_payload["name"],
        description=resolved_payload.get("description") or "",
        queue_view=resolved_payload.get("queue_view"),
        default_policy_template_id=resolved_payload.get("default_policy_template_id"),
        default_policy_catalog_id=resolved_payload.get("default_policy_catalog_id"),
        created_by_tab_id=resolved_payload.get("created_by_tab_id"),
        created_by_tab_label=resolved_payload.get("created_by_tab_label"),
      )
    )

  if binding.binding_kind == "operator_provider_provenance_scheduler_stitched_report_governance_registry_list":
    return serialize_provider_provenance_scheduler_stitched_report_governance_registry_list(
      app.list_provider_provenance_scheduler_stitched_report_governance_registries(
        search=resolved_filters.get("search"),
        limit=resolved_filters.get("limit", 50),
      )
    )

  return UNHANDLED
