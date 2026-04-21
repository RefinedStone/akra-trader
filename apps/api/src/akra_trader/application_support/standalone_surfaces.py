from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from types import UnionType
from typing import Any
from typing import Callable
from typing import Union
from typing import get_args
from typing import get_origin

from akra_trader.application_support.standalone_surface_catalog import build_standalone_surface_runtime_bindings
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_comparison
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_market_data_ingestion_jobs
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_market_data_lineage_history
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_presets
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_runs
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_strategies
from akra_trader.application_support.runtime_queries import RunSubresourceContract
from akra_trader.application_support.runtime_queries import RunSubresourceRuntimeBinding
from akra_trader.application_support.runtime_queries import StandaloneSurfaceCollectionPathParameterSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceCollectionPathSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterParamSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceRuntimeBinding
from akra_trader.application_support.run_surfaces import serialize_run
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunSurfaceCapabilities
from akra_trader.domain.models import RunSurfaceSharedContract


def _application_module():
  from akra_trader import application as application_module
  return application_module


def _application_symbol(name: str):
  return getattr(_application_module(), name)


def _serialize_run_orders_subresource_body(*args, **kwargs):
  return _application_symbol('_serialize_run_orders_subresource_body')(*args, **kwargs)


def _serialize_run_positions_subresource_body(*args, **kwargs):
  return _application_symbol('_serialize_run_positions_subresource_body')(*args, **kwargs)


def _serialize_run_metrics_subresource_body(*args, **kwargs):
  return _application_symbol('_serialize_run_metrics_subresource_body')(*args, **kwargs)


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


def serialize_run_subresource_response(*args, **kwargs):
  return _application_symbol('serialize_run_subresource_response')(*args, **kwargs)


def serialize_run_surface_capabilities(*args, **kwargs):
  return _application_symbol('serialize_run_surface_capabilities')(*args, **kwargs)


def _resolve_run_subresource_body_serializer(
  body_key: str,
) -> Callable[[RunRecord, RunSurfaceCapabilities], Any]:
  if body_key == "orders":
    return lambda run, capabilities: _serialize_run_orders_subresource_body(
      run,
      capabilities=capabilities,
    )
  if body_key == "positions":
    return lambda run, capabilities: _serialize_run_positions_subresource_body(
      run,
      capabilities=capabilities,
    )
  if body_key == "metrics":
    return lambda run, capabilities: _serialize_run_metrics_subresource_body(
      run,
      capabilities=capabilities,
    )
  raise ValueError(f"Unsupported run subresource serializer body: {body_key}")


def list_run_subresource_runtime_bindings(
  capabilities: RunSurfaceCapabilities | None = None,
) -> tuple[RunSubresourceRuntimeBinding, ...]:
  resolved_capabilities = capabilities or RunSurfaceCapabilities()
  bindings: list[RunSubresourceRuntimeBinding] = []
  for shared_contract in resolved_capabilities.shared_contracts:
    if shared_contract.contract_kind != "run_subresource":
      continue
    subresource_key = shared_contract.contract_key.removeprefix("subresource:")
    body_key = shared_contract.schema_detail.get("body_key")
    route_path = shared_contract.schema_detail.get("route_path")
    route_name = shared_contract.schema_detail.get("route_name")
    if not all(isinstance(value, str) and value for value in (body_key, route_path, route_name)):
      raise ValueError(f"Invalid run subresource contract metadata: {shared_contract.contract_key}")
    bindings.append(
      RunSubresourceRuntimeBinding(
        contract=RunSubresourceContract(
          subresource_key=subresource_key,
          body_key=body_key,
          response_title=shared_contract.title,
          route_path=route_path,
          route_name=route_name,
        ),
        body_serializer=_resolve_run_subresource_body_serializer(body_key),
      )
    )
  return tuple(bindings)


def list_run_subresource_contracts(
  capabilities: RunSurfaceCapabilities | None = None,
) -> tuple[RunSubresourceContract, ...]:
  return tuple(
    binding.contract
    for binding in list_run_subresource_runtime_bindings(capabilities)
  )


def get_run_subresource_contract(
  subresource_key: str,
  capabilities: RunSurfaceCapabilities | None = None,
) -> RunSubresourceContract:
  for binding in list_run_subresource_runtime_bindings(capabilities):
    if binding.contract.subresource_key == subresource_key:
      return binding.contract
  raise ValueError(f"Unsupported run subresource serializer: {subresource_key}")


def get_run_subresource_runtime_binding(
  subresource_key: str,
  capabilities: RunSurfaceCapabilities | None = None,
) -> RunSubresourceRuntimeBinding:
  for binding in list_run_subresource_runtime_bindings(capabilities):
    if binding.contract.subresource_key == subresource_key:
      return binding
  raise ValueError(f"Unsupported run subresource serializer: {subresource_key}")


def list_standalone_surface_runtime_bindings(
  capabilities: RunSurfaceCapabilities | None = None,
) -> tuple[StandaloneSurfaceRuntimeBinding, ...]:
  resolved_capabilities = capabilities or RunSurfaceCapabilities()
  run_subresource_bindings = tuple(
    StandaloneSurfaceRuntimeBinding(
      surface_key=f"run_subresource:{binding.contract.subresource_key}",
      route_path=binding.contract.route_path,
      route_name=binding.contract.route_name,
      response_title=binding.contract.response_title,
      scope="run",
      binding_kind="run_subresource",
      subresource_key=binding.contract.subresource_key,
    )
    for binding in list_run_subresource_runtime_bindings(resolved_capabilities)
  )
  return build_standalone_surface_runtime_bindings(
    run_subresource_bindings=run_subresource_bindings,
  )


def get_standalone_surface_runtime_binding(
  surface_key: str,
  capabilities: RunSurfaceCapabilities | None = None,
) -> StandaloneSurfaceRuntimeBinding:
  for binding in list_standalone_surface_runtime_bindings(capabilities):
    if binding.surface_key == surface_key:
      return binding
  raise ValueError(f"Unsupported standalone surface binding: {surface_key}")


def execute_standalone_surface_binding(
  *,
  binding: StandaloneSurfaceRuntimeBinding,
  app: TradingApplication,
  run_id: str | None = None,
  filters: dict[str, Any] | None = None,
  request_payload: dict[str, Any] | None = None,
  path_params: dict[str, Any] | None = None,
  headers: dict[str, Any] | None = None,
) -> Any:
  resolved_filters = filters or {}
  resolved_payload = request_payload or {}
  resolved_path_params = path_params or {}
  resolved_headers = headers or {}
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
        template_id=resolved_payload.get("template_id"),
        clear_template_link=bool(resolved_payload.get("clear_template_link", False)),
        policy_template_id=resolved_payload.get("policy_template_id"),
        approval_lane=resolved_payload.get("approval_lane"),
        approval_priority=resolved_payload.get("approval_priority"),
      )
    )
  if binding.binding_kind == "operator_provider_provenance_scheduler_narrative_governance_plan_list":
    return serialize_provider_provenance_scheduler_narrative_governance_plan_list(
      app.list_provider_provenance_scheduler_narrative_governance_plans(
        item_type=resolved_filters.get("item_type"),
        status=resolved_filters.get("status"),
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
    )
    return serialize_preset(preset)
  if binding.binding_kind == "strategy_catalog_register":
    metadata = app.register_strategy(
      strategy_id=resolved_payload["strategy_id"],
      module_path=resolved_payload["module_path"],
      class_name=resolved_payload["class_name"],
    )
    return serialize_strategy(metadata)
  if binding.binding_kind == "run_list":
    return [
      serialize_run(run, capabilities=app.get_run_surface_capabilities())
      for run in _apply_runtime_query_to_runs(
        app.list_runs(
          mode=resolved_filters.get("mode"),
          strategy_id=resolved_filters.get("strategy_id"),
          strategy_version=resolved_filters.get("strategy_version"),
          rerun_boundary_id=resolved_filters.get("rerun_boundary_id"),
          preset_id=resolved_filters.get("preset_id"),
          benchmark_family=resolved_filters.get("benchmark_family"),
          dataset_identity=resolved_filters.get("dataset_identity"),
          tags=resolved_filters.get("tag") or [],
        ),
        resolved_filters,
        binding=binding,
      )
    ]
  if binding.binding_kind == "run_compare":
    comparison = _apply_runtime_query_to_comparison(
      app.compare_runs(
        run_ids=resolved_filters.get("run_id") or [],
        intent=resolved_filters.get("intent"),
      ),
      resolved_filters,
      binding=binding,
    )
    return serialize_run_comparison(
      comparison,
      capabilities=app.get_run_surface_capabilities(),
    )
  if binding.binding_kind == "run_backtest_launch":
    run = app.run_backtest(
      strategy_id=resolved_payload["strategy_id"],
      symbol=resolved_payload["symbol"],
      timeframe=resolved_payload.get("timeframe", "5m"),
      initial_cash=resolved_payload.get("initial_cash", 10_000),
      fee_rate=resolved_payload.get("fee_rate", 0.001),
      slippage_bps=resolved_payload.get("slippage_bps", 3),
      parameters=resolved_payload.get("parameters") or {},
      start_at=resolved_payload.get("start_at"),
      end_at=resolved_payload.get("end_at"),
      tags=resolved_payload.get("tags") or [],
      preset_id=resolved_payload.get("preset_id"),
      benchmark_family=resolved_payload.get("benchmark_family"),
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_backtest_item_get":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.get_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_rerun_backtest":
    run = app.rerun_backtest_from_boundary(
      rerun_boundary_id=resolved_path_params["rerun_boundary_id"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_rerun_sandbox":
    run = app.rerun_sandbox_from_boundary(
      rerun_boundary_id=resolved_path_params["rerun_boundary_id"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_rerun_paper":
    run = app.rerun_paper_from_boundary(
      rerun_boundary_id=resolved_path_params["rerun_boundary_id"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_sandbox_launch":
    run = app.start_sandbox_run(
      strategy_id=resolved_payload["strategy_id"],
      symbol=resolved_payload["symbol"],
      timeframe=resolved_payload.get("timeframe", "5m"),
      initial_cash=resolved_payload.get("initial_cash", 10_000),
      fee_rate=resolved_payload.get("fee_rate", 0.001),
      slippage_bps=resolved_payload.get("slippage_bps", 3),
      parameters=resolved_payload.get("parameters") or {},
      replay_bars=resolved_payload.get("replay_bars", 96),
      tags=resolved_payload.get("tags") or [],
      preset_id=resolved_payload.get("preset_id"),
      benchmark_family=resolved_payload.get("benchmark_family"),
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_paper_launch":
    run = app.start_paper_run(
      strategy_id=resolved_payload["strategy_id"],
      symbol=resolved_payload["symbol"],
      timeframe=resolved_payload.get("timeframe", "5m"),
      initial_cash=resolved_payload.get("initial_cash", 10_000),
      fee_rate=resolved_payload.get("fee_rate", 0.001),
      slippage_bps=resolved_payload.get("slippage_bps", 3),
      parameters=resolved_payload.get("parameters") or {},
      replay_bars=resolved_payload.get("replay_bars", 96),
      tags=resolved_payload.get("tags") or [],
      preset_id=resolved_payload.get("preset_id"),
      benchmark_family=resolved_payload.get("benchmark_family"),
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_live_launch":
    run = app.start_live_run(
      strategy_id=resolved_payload["strategy_id"],
      symbol=resolved_payload["symbol"],
      timeframe=resolved_payload.get("timeframe", "5m"),
      initial_cash=resolved_payload.get("initial_cash", 10_000),
      fee_rate=resolved_payload.get("fee_rate", 0.001),
      slippage_bps=resolved_payload.get("slippage_bps", 3),
      parameters=resolved_payload.get("parameters") or {},
      replay_bars=resolved_payload.get("replay_bars", 96),
      operator_reason=resolved_payload.get("operator_reason", "guarded_live_launch"),
      tags=resolved_payload.get("tags") or [],
      preset_id=resolved_payload.get("preset_id"),
      benchmark_family=resolved_payload.get("benchmark_family"),
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "operator_incident_external_sync":
    app.require_operator_alert_external_sync_token(
      resolved_headers.get("x_akra_incident_sync_token"),
    )
    status = app.sync_guarded_live_incident_from_external(
      provider=resolved_payload["provider"],
      event_kind=resolved_payload["event_kind"],
      actor=resolved_payload["actor"],
      detail=resolved_payload["detail"],
      alert_id=resolved_payload.get("alert_id"),
      external_reference=resolved_payload.get("external_reference"),
      workflow_reference=resolved_payload.get("workflow_reference"),
      occurred_at=resolved_payload.get("occurred_at"),
      escalation_level=resolved_payload.get("escalation_level"),
      payload=resolved_payload.get("payload"),
    )
    return asdict(status)
  if binding.binding_kind == "guarded_live_kill_switch_engage":
    return asdict(
      app.engage_guarded_live_kill_switch(
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )
  if binding.binding_kind == "guarded_live_kill_switch_release":
    return asdict(
      app.release_guarded_live_kill_switch(
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )
  if binding.binding_kind == "guarded_live_reconciliation":
    return asdict(
      app.run_guarded_live_reconciliation(
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )
  if binding.binding_kind == "guarded_live_recovery":
    return asdict(
      app.recover_guarded_live_runtime_state(
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )
  if binding.binding_kind == "guarded_live_incident_acknowledge":
    return asdict(
      app.acknowledge_guarded_live_incident(
        event_id=resolved_path_params["event_id"],
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )
  if binding.binding_kind == "guarded_live_incident_remediate":
    return asdict(
      app.remediate_guarded_live_incident(
        event_id=resolved_path_params["event_id"],
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )
  if binding.binding_kind == "guarded_live_incident_escalate":
    return asdict(
      app.escalate_guarded_live_incident(
        event_id=resolved_path_params["event_id"],
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )
  if binding.binding_kind == "guarded_live_resume":
    run = app.resume_guarded_live_run(
      actor=resolved_payload["actor"],
      reason=resolved_payload["reason"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_stop_sandbox":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.stop_sandbox_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_stop_paper":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.stop_paper_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_stop_live":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.stop_live_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_live_order_cancel":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.cancel_live_order(
      run_id=run_id,
      order_id=resolved_path_params["order_id"],
      actor=resolved_payload["actor"],
      reason=resolved_payload["reason"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_live_order_replace":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.replace_live_order(
      run_id=run_id,
      order_id=resolved_path_params["order_id"],
      price=resolved_payload["price"],
      quantity=resolved_payload.get("quantity"),
      actor=resolved_payload["actor"],
      reason=resolved_payload["reason"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_subresource":
    if binding.subresource_key is None:
      raise ValueError(f"Standalone surface binding is missing subresource metadata: {binding.surface_key}")
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.get_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    return serialize_run_subresource_response(
      run,
      subresource_key=binding.subresource_key,
      capabilities=app.get_run_surface_capabilities(),
    )
  raise ValueError(f"Unsupported standalone surface binding: {binding.binding_kind}")


def serialize_standalone_surface_response(
  *,
  binding: StandaloneSurfaceRuntimeBinding,
  app: TradingApplication,
  run_id: str | None = None,
  filters: dict[str, Any] | None = None,
) -> Any:
  return execute_standalone_surface_binding(
    binding=binding,
    app=app,
    run_id=run_id,
    filters=filters,
  )


def _describe_standalone_filter_value_type(annotation: Any) -> str:
  origin = get_origin(annotation)
  if origin in {list, tuple}:
    args = tuple(arg for arg in get_args(annotation) if arg is not Ellipsis)
    if args:
      return f"list[{_describe_standalone_filter_value_type(args[0])}]"
  if origin in {UnionType, Union}:
    args = tuple(arg for arg in get_args(annotation) if arg is not type(None))
    if len(args) == 1:
      return _describe_standalone_filter_value_type(args[0])
  if annotation is int:
    return "integer"
  if annotation is float:
    return "number"
  if annotation is datetime:
    return "datetime"
  return "string"


def serialize_standalone_filter_param_spec(
  spec: StandaloneSurfaceFilterParamSpec,
) -> dict[str, Any]:
  return {
    "key": spec.key,
    "query_exposed": spec.query_exposed,
    "value_type": _describe_standalone_filter_value_type(spec.annotation),
    "value_path": list(spec.value_path),
    "value_root": spec.value_root,
    "title": spec.openapi.title if spec.openapi is not None else None,
    "description": spec.openapi.description if spec.openapi is not None else None,
    "operators": [
      {
        "key": operator.key,
        "label": operator.label,
        "description": operator.description,
        "value_shape": operator.value_shape,
      }
      for operator in spec.operators
    ],
  }


def serialize_collection_path_parameter_spec(
  spec: StandaloneSurfaceCollectionPathParameterSpec,
) -> dict[str, Any]:
  hydrated_domain_values = list(spec.domain_values) if spec.domain_values else (
    list(dict.fromkeys(spec.examples))
    if spec.enum_source_kind and spec.examples
    else []
  )
  payload = {
    "key": spec.key,
    "kind": spec.kind,
    "description": spec.description,
    "examples": list(spec.examples),
  }
  if spec.domain_key or spec.domain_source or spec.domain_values:
    payload["domain"] = {
      "key": spec.domain_key or None,
      "source": spec.domain_source or None,
      "values": hydrated_domain_values,
    }
    if spec.enum_source_kind or spec.enum_source_surface_key or spec.enum_source_path:
      payload["domain"]["enum_source"] = {
        "kind": spec.enum_source_kind or None,
        "surface_key": spec.enum_source_surface_key or None,
        "path": list(spec.enum_source_path),
      }
  return payload


def serialize_collection_path_parameter_domain(
  binding: StandaloneSurfaceRuntimeBinding,
  collection_spec: StandaloneSurfaceCollectionPathSpec,
  parameter_spec: StandaloneSurfaceCollectionPathParameterSpec,
) -> dict[str, Any]:
  return {
    "parameter_key": parameter_spec.key,
    "parameter_kind": parameter_spec.kind,
    "collection_label": collection_spec.label,
    "collection_path": list(collection_spec.path),
    "collection_path_template": list(collection_spec.path_template or collection_spec.path),
    "domain": serialize_collection_path_parameter_spec(parameter_spec).get("domain"),
    "surface_key": binding.surface_key,
  }


def serialize_collection_path_spec(
  binding: StandaloneSurfaceRuntimeBinding,
  spec: StandaloneSurfaceCollectionPathSpec,
) -> dict[str, Any]:
  filter_specs_by_key = {
    filter_spec.key: filter_spec
    for filter_spec in binding.filter_param_specs
  }
  return {
    "path": list(spec.path),
    "path_template": list(spec.path_template or spec.path),
    "label": spec.label,
    "collection_kind": spec.collection_kind,
    "item_kind": spec.item_kind,
    "filter_keys": list(spec.filter_keys),
    "description": spec.description,
    "parameters": [
      serialize_collection_path_parameter_spec(parameter)
      for parameter in spec.parameters
    ],
    "element_schema": [
      serialize_standalone_filter_param_spec(filter_specs_by_key[filter_key])
      for filter_key in spec.filter_keys
      if filter_key in filter_specs_by_key
    ],
  }


def serialize_collection_query_expression_authoring() -> dict[str, Any]:
  return {
    "predicate_refs": {
      "registry_field": "predicates",
      "reference_field": "predicate_ref",
    },
    "predicate_templates": {
      "registry_field": "predicate_templates",
      "template_field": "template",
      "parameters_field": "parameters",
      "bindings_field": "bindings",
      "binding_reference_shape": {
        "binding": "<parameter_name>",
      },
    },
    "collection_nodes": {
      "field": "collection",
      "shape": {
        "path": "<collection path>",
        "path_template": "<collection path template>",
        "bindings": {
          "<parameter_key>": "<value or binding reference>",
        },
        "quantifier": "any|all|none",
      },
    },
  }


def list_collection_query_shared_contracts(
  capabilities: RunSurfaceCapabilities | None = None,
) -> tuple[RunSurfaceSharedContract, ...]:
  resolved_capabilities = capabilities or RunSurfaceCapabilities()
  contracts: list[RunSurfaceSharedContract] = []
  for binding in list_standalone_surface_runtime_bindings(resolved_capabilities):
    if not binding.collection_path_specs:
      continue
    parameter_domains = [
      serialize_collection_path_parameter_domain(binding, spec, parameter)
      for spec in binding.collection_path_specs
      for parameter in spec.parameters
      if parameter.domain_key or parameter.domain_source or parameter.domain_values
    ]
    contracts.append(
      RunSurfaceSharedContract(
        contract_key=f"query_collection:{binding.surface_key}",
        contract_kind="query_collection_schema",
        title=f"{binding.response_title} collection query schema",
        summary=(
          "Advertises typed collection expression schemas, element fields, and parameter domain metadata "
          f"for the `{binding.surface_key}` surface."
        ),
        source_of_truth="standalone_surface_runtime_bindings.collection_path_specs",
        related_family_keys=("collection_query",),
        member_keys=tuple(
          [
            f"collection:{'.'.join(spec.path_template or spec.path)}"
            for spec in binding.collection_path_specs
          ]
          + [
            f"parameter_domain:{domain['parameter_key']}"
            for domain in parameter_domains
          ]
        ),
        schema_detail={
          "surface_key": binding.surface_key,
          "route_path": binding.route_path,
          "expression_param": "filter_expr",
          "expression_authoring": serialize_collection_query_expression_authoring(),
          "collection_schemas": [
            serialize_collection_path_spec(binding, spec)
            for spec in binding.collection_path_specs
          ],
          "parameter_domains": parameter_domains,
        },
      )
    )
  return tuple(contracts)


def list_run_surface_shared_contracts(
  capabilities: RunSurfaceCapabilities | None = None,
) -> tuple[RunSurfaceSharedContract, ...]:
  resolved_capabilities = capabilities or RunSurfaceCapabilities()
  return resolved_capabilities.shared_contracts


def serialize_run_surface_shared_contracts(
  capabilities: RunSurfaceCapabilities | None = None,
) -> list[dict[str, Any]]:
  def normalize_schema_detail(value: Any) -> Any:
    if isinstance(value, tuple):
      return [
        normalize_schema_detail(item)
        for item in value
      ]
    if isinstance(value, list):
      return [
        normalize_schema_detail(item)
        for item in value
      ]
    if isinstance(value, dict):
      return {
        key: normalize_schema_detail(item)
        for key, item in value.items()
      }
    return value

  return [
    {
      **asdict(contract),
      "ui_surfaces": list(contract.ui_surfaces),
      "schema_sources": list(contract.schema_sources),
      "policy": (
        {
          **asdict(contract.policy),
          "applies_to": list(contract.policy.applies_to),
        }
        if contract.policy is not None
        else None
      ),
      "enforcement": (
        {
          **asdict(contract.enforcement),
          "enforcement_points": list(contract.enforcement.enforcement_points),
        }
        if contract.enforcement is not None
        else None
      ),
      "surface_rules": [
        asdict(rule)
        for rule in contract.surface_rules
      ],
      "related_family_keys": list(contract.related_family_keys),
      "member_keys": list(contract.member_keys),
      "schema_detail": normalize_schema_detail(contract.schema_detail),
    }
    for contract in (
      list_run_surface_shared_contracts(capabilities)
      + list_collection_query_shared_contracts(capabilities)
    )
  ]
