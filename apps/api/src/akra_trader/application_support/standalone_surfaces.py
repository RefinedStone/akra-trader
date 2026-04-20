from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from types import UnionType
from typing import Any
from typing import Callable
from typing import Union
from typing import get_args
from typing import get_origin

from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_comparison
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_presets
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_runs
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_strategies
from akra_trader.application_support.runtime_queries import _build_datetime_range_filter_operators
from akra_trader.application_support.runtime_queries import _build_numeric_range_filter_operators
from akra_trader.application_support.runtime_queries import RunSubresourceContract
from akra_trader.application_support.runtime_queries import RunSubresourceRuntimeBinding
from akra_trader.application_support.runtime_queries import StandaloneSurfaceCollectionPathParameterSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceCollectionPathSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterConstraintSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterOpenAPISpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterOperatorSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterParamSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceRuntimeBinding
from akra_trader.application_support.runtime_queries import StandaloneSurfaceSortFieldSpec
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
  health_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="health_status",
    route_path="/health",
    route_name="health",
    response_title="Health",
    scope="app",
    binding_kind="health_status",
  )
  capability_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_surface_capabilities",
    route_path="/capabilities/run-surfaces",
    route_name="get_run_surface_capabilities",
    response_title="Run surface capabilities",
    scope="app",
    binding_kind="run_surface_capabilities",
  )
  replay_alias_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_alias_create",
    route_path="/replay-links/aliases",
    route_name="create_replay_link_alias",
    response_title="Create replay link alias",
    scope="app",
    binding_kind="replay_link_alias_create",
    methods=("POST",),
    request_payload_kind="replay_link_alias_create",
  )
  replay_alias_resolve_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_alias_resolve",
    route_path="/replay-links/aliases/{alias_token}",
    route_name="resolve_replay_link_alias",
    response_title="Resolve replay link alias",
    scope="app",
    binding_kind="replay_link_alias_resolve",
    path_param_keys=("alias_token",),
  )
  replay_alias_history_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_alias_history",
    route_path="/replay-links/aliases/{alias_token}/history",
    route_name="get_replay_link_alias_history",
    response_title="Replay link alias history",
    scope="app",
    binding_kind="replay_link_alias_history",
    path_param_keys=("alias_token",),
  )
  replay_alias_audit_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_audit_list",
    route_path="/replay-links/audits",
    route_name="list_replay_link_alias_audits",
    response_title="List replay link alias audits",
    scope="app",
    binding_kind="replay_link_audit_list",
    header_keys=("x_akra_replay_audit_admin_token",),
    filter_keys=("alias_id", "template_key", "action", "retention_policy", "source_tab_id", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "alias_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Alias ID",
          description="Filter replay alias audits by alias identifier.",
          examples=("abc123def4",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "template_key",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Template key",
          description="Filter replay alias audits by template key.",
          examples=("template_a",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "action",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Audit action",
          description="Filter replay alias audits by action kind.",
          examples=("revoked",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "retention_policy",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Retention policy",
          description="Filter replay alias audits by retention policy.",
          examples=("7d",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "source_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Source tab ID",
          description="Filter replay alias audits by source tab identity.",
          examples=("tab_local",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search replay alias audit ids, template labels, source tabs, and detail text.",
          examples=("Remote tab",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=100,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=500),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of replay alias audit records to return.",
          examples=(50,),
        ),
      ),
    ),
  )
  replay_alias_audit_export_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_audit_export",
    route_path="/replay-links/audits/export",
    route_name="export_replay_link_alias_audits",
    response_title="Export replay link alias audits",
    scope="app",
    binding_kind="replay_link_audit_export",
    header_keys=("x_akra_replay_audit_admin_token",),
    filter_keys=("alias_id", "template_key", "action", "retention_policy", "source_tab_id", "search", "format"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "alias_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Alias ID",
          description="Filter replay alias audit export by alias identifier.",
          examples=("abc123def4",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "template_key",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Template key",
          description="Filter replay alias audit export by template key.",
          examples=("template_a",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "action",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Audit action",
          description="Filter replay alias audit export by action kind.",
          examples=("revoked",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "retention_policy",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Retention policy",
          description="Filter replay alias audit export by retention policy.",
          examples=("7d",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "source_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Source tab ID",
          description="Filter replay alias audit export by source tab identity.",
          examples=("tab_local",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search replay alias audit export ids, template labels, source tabs, and detail text.",
          examples=("Remote tab",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "format",
        str,
        default="json",
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=3, max_length=4),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Export format",
          description="Replay alias audit export format.",
          examples=("json", "csv"),
        ),
      ),
    ),
  )
  replay_alias_audit_export_job_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_audit_export_job_create",
    route_path="/replay-links/audits/export-jobs",
    route_name="create_replay_link_alias_audit_export_job",
    response_title="Create replay link alias audit export job",
    scope="app",
    binding_kind="replay_link_audit_export_job_create",
    methods=("POST",),
    header_keys=("x_akra_replay_audit_admin_token",),
    request_payload_kind="replay_link_audit_export_job_create",
  )
  replay_alias_audit_export_job_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_audit_export_job_list",
    route_path="/replay-links/audits/export-jobs",
    route_name="list_replay_link_alias_audit_export_jobs",
    response_title="List replay link alias audit export jobs",
    scope="app",
    binding_kind="replay_link_audit_export_job_list",
    header_keys=("x_akra_replay_audit_admin_token",),
    filter_keys=("template_key", "format", "status", "requested_by_tab_id", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "template_key",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Template key",
          description="Filter replay alias audit export jobs by template key.",
          examples=("template_a",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "format",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=3, max_length=4),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Export format",
          description="Filter replay alias audit export jobs by export format.",
          examples=("json", "csv"),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "status",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Job status",
          description="Filter replay alias audit export jobs by status.",
          examples=("completed",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "requested_by_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Requested by tab ID",
          description="Filter replay alias audit export jobs by requesting tab identity.",
          examples=("tab_local",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search replay alias audit export job ids, filenames, formats, and requester labels.",
          examples=("template_a",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=100,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=500),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of replay alias audit export jobs to return.",
          examples=(25,),
        ),
      ),
    ),
  )
  replay_alias_audit_export_job_download_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_audit_export_job_download",
    route_path="/replay-links/audits/export-jobs/{job_id}/download",
    route_name="download_replay_link_alias_audit_export_job",
    response_title="Download replay link alias audit export job",
    scope="app",
    binding_kind="replay_link_audit_export_job_download",
    header_keys=("x_akra_replay_audit_admin_token",),
    path_param_keys=("job_id",),
  )
  replay_alias_audit_export_job_history_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_audit_export_job_history",
    route_path="/replay-links/audits/export-jobs/{job_id}/history",
    route_name="get_replay_link_alias_audit_export_job_history",
    response_title="Replay link alias audit export job history",
    scope="app",
    binding_kind="replay_link_audit_export_job_history",
    header_keys=("x_akra_replay_audit_admin_token",),
    path_param_keys=("job_id",),
  )
  replay_alias_audit_export_job_prune_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_audit_export_job_prune",
    route_path="/replay-links/audits/export-jobs/prune",
    route_name="prune_replay_link_alias_audit_export_jobs",
    response_title="Prune replay link alias audit export jobs",
    scope="app",
    binding_kind="replay_link_audit_export_job_prune",
    methods=("POST",),
    header_keys=("x_akra_replay_audit_admin_token",),
    request_payload_kind="replay_link_audit_export_job_prune",
  )
  replay_alias_audit_prune_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_audit_prune",
    route_path="/replay-links/audits/prune",
    route_name="prune_replay_link_alias_audits",
    response_title="Prune replay link alias audits",
    scope="app",
    binding_kind="replay_link_audit_prune",
    methods=("POST",),
    header_keys=("x_akra_replay_audit_admin_token",),
    request_payload_kind="replay_link_audit_prune",
  )
  replay_alias_revoke_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="replay_link_alias_revoke",
    route_path="/replay-links/aliases/{alias_token}/revoke",
    route_name="revoke_replay_link_alias",
    response_title="Revoke replay link alias",
    scope="app",
    binding_kind="replay_link_alias_revoke",
    methods=("POST",),
    path_param_keys=("alias_token",),
    request_payload_kind="replay_link_alias_revoke",
  )
  market_data_status_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="market_data_status",
    route_path="/market-data/status",
    route_name="get_market_data_status",
    response_title="Market data status",
    scope="app",
    binding_kind="market_data_status",
    filter_keys=("timeframe",),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "timeframe",
        str,
        default="5m",
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=2, max_length=10),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Timeframe",
          description="Candlestick timeframe to inspect in market-data status.",
          examples=("5m",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches exactly one timeframe value.",
          ),
        ),
      ),
    ),
  )
  operator_visibility_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_visibility",
    route_path="/operator/visibility",
    route_name="get_operator_visibility",
    response_title="Operator visibility",
    scope="app",
    binding_kind="operator_visibility",
  )
  guarded_live_status_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_status",
    route_path="/guarded-live",
    route_name="get_guarded_live_status",
    response_title="Guarded live status",
    scope="app",
    binding_kind="guarded_live_status",
  )
  strategy_discovery_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="strategy_catalog_discovery",
    route_path="/strategies",
    route_name="list_strategies",
    response_title="Strategy catalog discovery",
    scope="app",
    binding_kind="strategy_catalog_discovery",
    filter_keys=("lane", "lifecycle_stage", "version", "registered_at"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "lane",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Lane",
          description="Filter strategies by runtime lane.",
          examples=("native",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single runtime lane value.",
          ),
        ),
        value_path=("runtime",),
      ),
      StandaloneSurfaceFilterParamSpec(
        "lifecycle_stage",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Lifecycle stage",
          description="Filter strategies by lifecycle stage.",
          examples=("active",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single lifecycle stage.",
          ),
        ),
        value_path=("lifecycle", "stage"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "version",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Version",
          description="Filter strategies by declared version string.",
          examples=("1.0.0",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches one declared version value.",
          ),
          StandaloneSurfaceFilterOperatorSpec(
            key="prefix",
            label="Version prefix",
            description="Matches a version prefix such as a major or minor line.",
          ),
        ),
        value_path=("version",),
      ),
      StandaloneSurfaceFilterParamSpec(
        "registered_at",
        datetime | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Registered at",
          description="Filter imported strategies by registration timestamp.",
          examples=("2025-01-01T00:00:00+00:00",),
        ),
        operators=_build_datetime_range_filter_operators("strategy registration time"),
        value_path=("lifecycle", "registered_at"),
      ),
    ),
    sort_field_specs=(
      StandaloneSurfaceSortFieldSpec(
        key="strategy_id",
        label="Strategy ID",
        description="Sorts by strategy identifier.",
        value_path=("strategy_id",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="runtime",
        label="Runtime lane",
        description="Sorts by runtime lane grouping.",
        value_path=("runtime",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="registered_at",
        label="Registration time",
        description="Sorts imported strategies by registration timestamp.",
        default_direction="desc",
        value_type="datetime",
        value_path=("lifecycle", "registered_at"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="lifecycle.registered_at",
        label="Lifecycle registration time",
        description="Sorts imported strategies by the nested lifecycle registration timestamp.",
        default_direction="desc",
        value_type="datetime",
        value_path=("lifecycle", "registered_at"),
      ),
    ),
  )
  reference_discovery_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="reference_catalog_discovery",
    route_path="/references",
    route_name="list_references",
    response_title="Reference catalog discovery",
    scope="app",
    binding_kind="reference_catalog_discovery",
  )
  preset_discovery_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="preset_catalog_discovery",
    route_path="/presets",
    route_name="list_presets",
    response_title="Preset catalog discovery",
    scope="app",
    binding_kind="preset_catalog_discovery",
    filter_keys=("strategy_id", "timeframe", "lifecycle_stage", "created_at", "updated_at"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "strategy_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Strategy ID",
          description="Filter presets by strategy identifier.",
          examples=("ma_cross_v1",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single strategy identifier.",
          ),
        ),
        value_path=("strategy_id",),
      ),
      StandaloneSurfaceFilterParamSpec(
        "timeframe",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=2, max_length=10),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Timeframe",
          description="Filter presets by configured timeframe.",
          examples=("5m",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single configured timeframe.",
          ),
        ),
        value_path=("timeframe",),
      ),
      StandaloneSurfaceFilterParamSpec(
        "lifecycle_stage",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Lifecycle stage",
          description="Filter presets by lifecycle stage.",
          examples=("draft",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single lifecycle stage.",
          ),
        ),
        value_path=("lifecycle", "stage"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "created_at",
        datetime | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Created at",
          description="Filter presets by creation timestamp.",
          examples=("2025-01-01T00:00:00+00:00",),
        ),
        operators=_build_datetime_range_filter_operators("preset creation time"),
        value_path=("created_at",),
      ),
      StandaloneSurfaceFilterParamSpec(
        "updated_at",
        datetime | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Updated at",
          description="Filter presets by last update timestamp.",
          examples=("2025-01-02T00:00:00+00:00",),
        ),
        operators=_build_datetime_range_filter_operators("preset update time"),
        value_path=("updated_at",),
      ),
    ),
    sort_field_specs=(
      StandaloneSurfaceSortFieldSpec(
        key="updated_at",
        label="Updated at",
        description="Sorts presets by most recent update time.",
        default_direction="desc",
        value_type="datetime",
        value_path=("updated_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="created_at",
        label="Created at",
        description="Sorts presets by creation time.",
        default_direction="desc",
        value_type="datetime",
        value_path=("created_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="preset_id",
        label="Preset ID",
        description="Sorts presets by preset identifier.",
        value_path=("preset_id",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="timestamps.updated_at",
        label="Nested updated at",
        description="Sorts presets by the nested update timestamp contract.",
        default_direction="desc",
        value_type="datetime",
        value_path=("updated_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="timestamps.created_at",
        label="Nested created at",
        description="Sorts presets by the nested creation timestamp contract.",
        default_direction="desc",
        value_type="datetime",
        value_path=("created_at",),
      ),
    ),
  )
  preset_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="preset_catalog_create",
    route_path="/presets",
    route_name="create_preset",
    response_title="Create preset",
    scope="app",
    binding_kind="preset_catalog_create",
    methods=("POST",),
    request_payload_kind="preset_create",
  )
  preset_item_get_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="preset_catalog_item_get",
    route_path="/presets/{preset_id}",
    route_name="get_preset",
    response_title="Get preset",
    scope="app",
    binding_kind="preset_catalog_item_get",
    path_param_keys=("preset_id",),
  )
  preset_item_update_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="preset_catalog_item_update",
    route_path="/presets/{preset_id}",
    route_name="update_preset",
    response_title="Update preset",
    scope="app",
    binding_kind="preset_catalog_item_update",
    methods=("PATCH",),
    path_param_keys=("preset_id",),
    request_payload_kind="preset_update",
  )
  preset_revision_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="preset_catalog_revision_list",
    route_path="/presets/{preset_id}/revisions",
    route_name="list_preset_revisions",
    response_title="List preset revisions",
    scope="app",
    binding_kind="preset_catalog_revision_list",
    path_param_keys=("preset_id",),
  )
  preset_revision_restore_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="preset_catalog_revision_restore",
    route_path="/presets/{preset_id}/revisions/{revision_id}/restore",
    route_name="restore_preset_revision",
    response_title="Restore preset revision",
    scope="app",
    binding_kind="preset_catalog_revision_restore",
    methods=("POST",),
    path_param_keys=("preset_id", "revision_id"),
    request_payload_kind="preset_revision_restore",
  )
  preset_lifecycle_apply_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="preset_catalog_lifecycle_apply",
    route_path="/presets/{preset_id}/lifecycle",
    route_name="apply_preset_lifecycle_action",
    response_title="Apply preset lifecycle action",
    scope="app",
    binding_kind="preset_catalog_lifecycle_apply",
    methods=("POST",),
    path_param_keys=("preset_id",),
    request_payload_kind="preset_lifecycle_action",
  )
  strategy_register_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="strategy_catalog_register",
    route_path="/strategies/register",
    route_name="register_strategy",
    response_title="Register strategy",
    scope="app",
    binding_kind="strategy_catalog_register",
    methods=("POST",),
    request_payload_kind="strategy_register",
  )
  run_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_list",
    route_path="/runs",
    route_name="list_runs",
    response_title="List runs",
    scope="app",
    binding_kind="run_list",
    filter_keys=(
      "mode",
      "strategy_id",
      "strategy_version",
      "rerun_boundary_id",
      "preset_id",
      "benchmark_family",
      "dataset_identity",
      "started_at",
      "updated_at",
      "initial_cash",
      "ending_equity",
      "exposure_pct",
      "total_return_pct",
      "max_drawdown_pct",
      "win_rate_pct",
      "trade_count",
      "tag",
    ),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "mode",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Run mode",
          description="Filter runs by execution mode.",
          examples=("backtest",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single run mode.",
          ),
        ),
        value_path=("config", "mode", "value"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "strategy_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Strategy ID",
          description="Filter runs by strategy identifier.",
          examples=("ma_cross_v1",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single strategy identifier.",
          ),
        ),
        value_path=("config", "strategy_id"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "strategy_version",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Strategy version",
          description="Filter runs by strategy version.",
          examples=("1.0.0",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches one strategy version.",
          ),
          StandaloneSurfaceFilterOperatorSpec(
            key="prefix",
            label="Version prefix",
            description="Matches a strategy version prefix.",
          ),
        ),
        value_path=("config", "strategy_version"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "rerun_boundary_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Rerun boundary ID",
          description="Filter runs by rerun boundary identifier.",
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single rerun boundary identifier.",
          ),
        ),
        value_path=("provenance", "rerun_boundary_id"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "preset_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Preset ID",
          description="Filter runs by preset identifier.",
          examples=("core_5m",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single preset identifier.",
          ),
        ),
        value_path=("provenance", "experiment", "preset_id"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "benchmark_family",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Benchmark family",
          description="Filter runs by benchmark family tag.",
          examples=("native_validation",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single benchmark family tag.",
          ),
        ),
        value_path=("provenance", "experiment", "benchmark_family"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "dataset_identity",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Dataset identity",
          description="Filter runs by dataset identity.",
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single dataset identity.",
          ),
          StandaloneSurfaceFilterOperatorSpec(
            key="prefix",
            label="Prefix",
            description="Matches a dataset identity prefix.",
          ),
        ),
        value_path=("provenance", "market_data", "dataset_identity"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "started_at",
        datetime | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Started at",
          description="Filter runs by start timestamp.",
          examples=("2025-01-01T00:00:00+00:00",),
        ),
        operators=_build_datetime_range_filter_operators("run start time"),
        value_path=("started_at",),
      ),
      StandaloneSurfaceFilterParamSpec(
        "updated_at",
        datetime | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Updated at",
          description="Filter runs by effective update timestamp.",
          examples=("2025-01-01T00:05:00+00:00",),
        ),
        operators=_build_datetime_range_filter_operators("run update time"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "initial_cash",
        float | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=0),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Initial cash",
          description="Filter runs by initial cash baseline.",
          examples=(10000.0,),
        ),
        operators=_build_numeric_range_filter_operators("run initial cash"),
        value_path=("metrics", "initial_cash"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "ending_equity",
        float | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=0),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Ending equity",
          description="Filter runs by ending equity.",
          examples=(11250.0,),
        ),
        operators=_build_numeric_range_filter_operators("run ending equity"),
        value_path=("metrics", "ending_equity"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "exposure_pct",
        float | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=0, le=100),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Exposure %",
          description="Filter runs by exposure percentage.",
          examples=(45.0,),
        ),
        operators=_build_numeric_range_filter_operators("run exposure percentage"),
        value_path=("metrics", "exposure_pct"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "total_return_pct",
        float | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Total return %",
          description="Filter runs by realized total return percentage.",
          examples=(10.0,),
        ),
        operators=_build_numeric_range_filter_operators("run total return percentage"),
        value_path=("metrics", "total_return_pct"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "max_drawdown_pct",
        float | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=0),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Max drawdown %",
          description="Filter runs by realized max drawdown percentage.",
          examples=(15.0,),
        ),
        operators=_build_numeric_range_filter_operators("run max drawdown percentage"),
        value_path=("metrics", "max_drawdown_pct"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "win_rate_pct",
        float | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=0, le=100),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Win rate %",
          description="Filter runs by realized win-rate percentage.",
          examples=(60.0,),
        ),
        operators=_build_numeric_range_filter_operators("run win-rate percentage"),
        value_path=("metrics", "win_rate_pct"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "trade_count",
        int | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=0),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Trade count",
          description="Filter runs by realized trade count.",
          examples=(10,),
        ),
        operators=_build_numeric_range_filter_operators("run trade count"),
        value_path=("metrics", "trade_count"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "order_status",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Order status",
          description="Expression-only order collection field for nested order predicates.",
          examples=("open",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single order status on a collection element.",
          ),
        ),
        value_path=("status", "value"),
        query_exposed=False,
      ),
      StandaloneSurfaceFilterParamSpec(
        "order_type",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Order type",
          description="Expression-only order collection field for nested order predicates.",
          examples=("limit",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single order type on a collection element.",
          ),
        ),
        value_path=("order_type", "value"),
        query_exposed=False,
      ),
      StandaloneSurfaceFilterParamSpec(
        "issue_text",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Issue text",
          description="Expression-only nested issue text field for collection predicates.",
          examples=("gap:",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single issue text value on a collection element.",
          ),
          StandaloneSurfaceFilterOperatorSpec(
            key="prefix",
            label="Prefix",
            description="Matches an issue text prefix on a collection element.",
          ),
        ),
        query_exposed=False,
        value_root=True,
      ),
      StandaloneSurfaceFilterParamSpec(
        "tag",
        list[str],
        default_factory=list,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Tags",
          description="Filter runs by experiment tags.",
          examples=(["baseline"],),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="contains_all",
            label="Contains all",
            description="Requires all requested tags to be present on the run.",
            value_shape="list",
          ),
          StandaloneSurfaceFilterOperatorSpec(
            key="contains_any",
            label="Contains any",
            description="Matches if any requested tag is present on the run.",
            value_shape="list",
          ),
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches an exact tag value inside expression predicates.",
          ),
          StandaloneSurfaceFilterOperatorSpec(
            key="prefix",
            label="Prefix",
            description="Matches a tag prefix inside expression predicates.",
          ),
        ),
        value_path=("provenance", "experiment", "tags"),
      ),
    ),
    collection_path_specs=(
      StandaloneSurfaceCollectionPathSpec(
        path=("orders",),
        label="Run orders",
        collection_kind="object_collection",
        item_kind="order",
        filter_keys=("order_status", "order_type"),
        description="Evaluates predicates against individual run order objects.",
        path_template=("orders",),
      ),
      StandaloneSurfaceCollectionPathSpec(
        path=("provenance", "market_data_by_symbol", "issues"),
        label="Market-data issues",
        collection_kind="nested_collection",
        item_kind="issue_text",
        filter_keys=("issue_text",),
        description="Evaluates predicates against flattened issue strings across market-data lineage entries.",
        path_template=("provenance", "market_data_by_symbol", "{symbol_key}", "issues"),
        parameters=(
          StandaloneSurfaceCollectionPathParameterSpec(
            key="symbol_key",
            kind="dynamic_map_key",
            description="Symbol-keyed lineage entry inside `market_data_by_symbol`.",
            examples=("binance:BTC/USDT",),
            domain_key="market_data_symbol_key",
            domain_source="run.provenance.market_data_by_symbol",
            enum_source_kind="dynamic_map_keys",
            enum_source_surface_key="run_list",
            enum_source_path=("provenance", "market_data_by_symbol"),
          ),
        ),
      ),
    ),
    sort_field_specs=(
      StandaloneSurfaceSortFieldSpec(
        key="updated_at",
        label="Updated at",
        description="Sorts runs by most recent update time.",
        default_direction="desc",
        value_type="datetime",
        value_path=("updated_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="started_at",
        label="Started at",
        description="Sorts runs by start timestamp.",
        default_direction="desc",
        value_type="datetime",
        value_path=("started_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="run_id",
        label="Run ID",
        description="Sorts runs by run identifier.",
        value_path=("config", "run_id"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="initial_cash",
        label="Initial cash",
        description="Sorts runs by initial cash baseline.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "initial_cash"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="ending_equity",
        label="Ending equity",
        description="Sorts runs by ending equity.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "ending_equity"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="exposure_pct",
        label="Exposure %",
        description="Sorts runs by exposure percentage.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "exposure_pct"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="total_return_pct",
        label="Total return %",
        description="Sorts runs by realized total return percentage.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "total_return_pct"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="max_drawdown_pct",
        label="Max drawdown %",
        description="Sorts runs by realized max drawdown percentage.",
        value_type="number",
        value_path=("metrics", "max_drawdown_pct"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="win_rate_pct",
        label="Win rate %",
        description="Sorts runs by realized win-rate percentage.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "win_rate_pct"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="trade_count",
        label="Trade count",
        description="Sorts runs by realized trade count.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "trade_count"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="config.run_id",
        label="Nested run ID",
        description="Sorts runs by the nested config run identifier.",
        value_path=("config", "run_id"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="timing.started_at",
        label="Nested started at",
        description="Sorts runs by the nested timing start timestamp.",
        default_direction="desc",
        value_type="datetime",
        value_path=("started_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="timing.updated_at",
        label="Nested updated at",
        description="Sorts runs by the nested timing update timestamp.",
        default_direction="desc",
        value_type="datetime",
        value_path=("updated_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="metrics.initial_cash",
        label="Nested initial cash",
        description="Sorts runs by the nested initial cash metric.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "initial_cash"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="metrics.ending_equity",
        label="Nested ending equity",
        description="Sorts runs by the nested ending equity metric.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "ending_equity"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="metrics.exposure_pct",
        label="Nested exposure %",
        description="Sorts runs by the nested exposure percentage metric.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "exposure_pct"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="metrics.total_return_pct",
        label="Nested total return %",
        description="Sorts runs by the nested total return metric.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "total_return_pct"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="metrics.max_drawdown_pct",
        label="Nested max drawdown %",
        description="Sorts runs by the nested max drawdown metric.",
        value_type="number",
        value_path=("metrics", "max_drawdown_pct"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="metrics.win_rate_pct",
        label="Nested win rate %",
        description="Sorts runs by the nested win-rate metric.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "win_rate_pct"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="metrics.trade_count",
        label="Nested trade count",
        description="Sorts runs by the nested trade-count metric.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "trade_count"),
      ),
    ),
  )
  run_compare_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_compare",
    route_path="/runs/compare",
    route_name="compare_runs",
    response_title="Compare runs",
    scope="app",
    binding_kind="run_compare",
    filter_keys=("run_id", "intent", "narrative_score"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "run_id",
        list[str],
        default_factory=list,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Run IDs",
          description="Run identifiers to include in the comparison set.",
          examples=(["run-001", "run-002"],),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="include",
            label="Include set",
            description="Preserves the explicit set and order of compared run IDs.",
            value_shape="list",
          ),
        ),
        value_path=("run_id",),
      ),
      StandaloneSurfaceFilterParamSpec(
        "intent",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Comparison intent",
          description="Narrative intent used for run comparison scoring.",
          examples=("strategy_tuning",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Uses a single comparison intent profile.",
          ),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "narrative_score",
        float | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Narrative score",
          description="Filter comparison narratives by computed insight score.",
          examples=(5.0,),
        ),
        operators=_build_numeric_range_filter_operators("comparison narrative score"),
        value_path=("insight_score",),
      ),
    ),
    sort_field_specs=(
      StandaloneSurfaceSortFieldSpec(
        key="run_id_order",
        label="Input run order",
        description="Keeps the compared runs in the explicit query order.",
        value_type="integer",
      ),
      StandaloneSurfaceSortFieldSpec(
        key="narrative_score",
        label="Narrative score",
        description="Ranks comparison narratives by computed score.",
        default_direction="desc",
        value_type="number",
        value_path=("narratives", "insight_score"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="narratives.run_id_order",
        label="Nested narrative input order",
        description="Sorts comparison narratives by their nested requested run order.",
        value_type="integer",
      ),
      StandaloneSurfaceSortFieldSpec(
        key="narratives.insight_score",
        label="Nested narrative score",
        description="Sorts comparison narratives by the nested insight score field.",
        default_direction="desc",
        value_type="number",
        value_path=("narratives", "insight_score"),
      ),
    ),
  )
  run_backtest_launch_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_backtest_launch",
    route_path="/runs/backtests",
    route_name="run_backtest",
    response_title="Run backtest",
    scope="app",
    binding_kind="run_backtest_launch",
    methods=("POST",),
    request_payload_kind="backtest_launch",
  )
  run_backtest_item_get_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_backtest_item_get",
    route_path="/runs/backtests/{run_id}",
    route_name="get_backtest_run",
    response_title="Get backtest run",
    scope="run",
    binding_kind="run_backtest_item_get",
  )
  run_rerun_backtest_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_rerun_backtest",
    route_path="/runs/rerun-boundaries/{rerun_boundary_id}/backtests",
    route_name="rerun_backtest_from_boundary",
    response_title="Rerun backtest from boundary",
    scope="app",
    binding_kind="run_rerun_backtest",
    methods=("POST",),
    path_param_keys=("rerun_boundary_id",),
  )
  run_rerun_sandbox_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_rerun_sandbox",
    route_path="/runs/rerun-boundaries/{rerun_boundary_id}/sandbox",
    route_name="rerun_sandbox_from_boundary",
    response_title="Rerun sandbox from boundary",
    scope="app",
    binding_kind="run_rerun_sandbox",
    methods=("POST",),
    path_param_keys=("rerun_boundary_id",),
  )
  run_rerun_paper_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_rerun_paper",
    route_path="/runs/rerun-boundaries/{rerun_boundary_id}/paper",
    route_name="rerun_paper_from_boundary",
    response_title="Rerun paper from boundary",
    scope="app",
    binding_kind="run_rerun_paper",
    methods=("POST",),
    path_param_keys=("rerun_boundary_id",),
  )
  run_sandbox_launch_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_sandbox_launch",
    route_path="/runs/sandbox",
    route_name="start_sandbox_run",
    response_title="Start sandbox run",
    scope="app",
    binding_kind="run_sandbox_launch",
    methods=("POST",),
    request_payload_kind="sandbox_launch",
  )
  run_paper_launch_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_paper_launch",
    route_path="/runs/paper",
    route_name="start_paper_run",
    response_title="Start paper run",
    scope="app",
    binding_kind="run_paper_launch",
    methods=("POST",),
    request_payload_kind="paper_launch",
  )
  run_live_launch_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_live_launch",
    route_path="/runs/live",
    route_name="start_live_run",
    response_title="Start live run",
    scope="app",
    binding_kind="run_live_launch",
    methods=("POST",),
    request_payload_kind="live_launch",
  )
  operator_incident_external_sync_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_incident_external_sync",
    route_path="/operator/incidents/external-sync",
    route_name="sync_external_incident",
    response_title="External incident sync",
    scope="app",
    binding_kind="operator_incident_external_sync",
    methods=("POST",),
    header_keys=("x_akra_incident_sync_token",),
    request_payload_kind="external_incident_sync",
  )
  guarded_live_kill_switch_engage_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_kill_switch_engage",
    route_path="/guarded-live/kill-switch/engage",
    route_name="engage_guarded_live_kill_switch",
    response_title="Engage guarded-live kill switch",
    scope="app",
    binding_kind="guarded_live_kill_switch_engage",
    methods=("POST",),
    request_payload_kind="guarded_live_action",
  )
  guarded_live_kill_switch_release_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_kill_switch_release",
    route_path="/guarded-live/kill-switch/release",
    route_name="release_guarded_live_kill_switch",
    response_title="Release guarded-live kill switch",
    scope="app",
    binding_kind="guarded_live_kill_switch_release",
    methods=("POST",),
    request_payload_kind="guarded_live_action",
  )
  guarded_live_reconciliation_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_reconciliation",
    route_path="/guarded-live/reconciliation",
    route_name="run_guarded_live_reconciliation",
    response_title="Run guarded-live reconciliation",
    scope="app",
    binding_kind="guarded_live_reconciliation",
    methods=("POST",),
    request_payload_kind="guarded_live_action",
  )
  guarded_live_recovery_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_recovery",
    route_path="/guarded-live/recovery",
    route_name="recover_guarded_live_runtime_state",
    response_title="Recover guarded-live runtime state",
    scope="app",
    binding_kind="guarded_live_recovery",
    methods=("POST",),
    request_payload_kind="guarded_live_action",
  )
  guarded_live_incident_acknowledge_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_incident_acknowledge",
    route_path="/guarded-live/incidents/{event_id}/acknowledge",
    route_name="acknowledge_guarded_live_incident",
    response_title="Acknowledge guarded-live incident",
    scope="app",
    binding_kind="guarded_live_incident_acknowledge",
    methods=("POST",),
    path_param_keys=("event_id",),
    request_payload_kind="guarded_live_action",
  )
  guarded_live_incident_remediate_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_incident_remediate",
    route_path="/guarded-live/incidents/{event_id}/remediate",
    route_name="remediate_guarded_live_incident",
    response_title="Remediate guarded-live incident",
    scope="app",
    binding_kind="guarded_live_incident_remediate",
    methods=("POST",),
    path_param_keys=("event_id",),
    request_payload_kind="guarded_live_action",
  )
  guarded_live_incident_escalate_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_incident_escalate",
    route_path="/guarded-live/incidents/{event_id}/escalate",
    route_name="escalate_guarded_live_incident",
    response_title="Escalate guarded-live incident",
    scope="app",
    binding_kind="guarded_live_incident_escalate",
    methods=("POST",),
    path_param_keys=("event_id",),
    request_payload_kind="guarded_live_action",
  )
  guarded_live_resume_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_resume",
    route_path="/guarded-live/resume",
    route_name="resume_guarded_live_run",
    response_title="Resume guarded-live run",
    scope="app",
    binding_kind="guarded_live_resume",
    methods=("POST",),
    request_payload_kind="guarded_live_action",
  )
  stop_sandbox_run_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_stop_sandbox",
    route_path="/runs/sandbox/{run_id}/stop",
    route_name="stop_sandbox_run",
    response_title="Stop sandbox run",
    scope="run",
    binding_kind="run_stop_sandbox",
    methods=("POST",),
  )
  stop_paper_run_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_stop_paper",
    route_path="/runs/paper/{run_id}/stop",
    route_name="stop_paper_run",
    response_title="Stop paper run",
    scope="run",
    binding_kind="run_stop_paper",
    methods=("POST",),
  )
  stop_live_run_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_stop_live",
    route_path="/runs/live/{run_id}/stop",
    route_name="stop_live_run",
    response_title="Stop live run",
    scope="run",
    binding_kind="run_stop_live",
    methods=("POST",),
  )
  cancel_live_order_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_live_order_cancel",
    route_path="/runs/live/{run_id}/orders/{order_id}/cancel",
    route_name="cancel_live_order",
    response_title="Cancel live order",
    scope="run",
    binding_kind="run_live_order_cancel",
    methods=("POST",),
    path_param_keys=("order_id",),
    request_payload_kind="guarded_live_action",
  )
  replace_live_order_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_live_order_replace",
    route_path="/runs/live/{run_id}/orders/{order_id}/replace",
    route_name="replace_live_order",
    response_title="Replace live order",
    scope="run",
    binding_kind="run_live_order_replace",
    methods=("POST",),
    path_param_keys=("order_id",),
    request_payload_kind="guarded_live_order_replace",
  )
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
  return (
    health_binding,
    capability_binding,
    replay_alias_create_binding,
    replay_alias_resolve_binding,
    replay_alias_history_binding,
    replay_alias_audit_list_binding,
    replay_alias_audit_export_binding,
    replay_alias_audit_export_job_create_binding,
    replay_alias_audit_export_job_list_binding,
    replay_alias_audit_export_job_download_binding,
    replay_alias_audit_export_job_history_binding,
    replay_alias_audit_export_job_prune_binding,
    replay_alias_audit_prune_binding,
    replay_alias_revoke_binding,
    market_data_status_binding,
    operator_visibility_binding,
    guarded_live_status_binding,
    strategy_discovery_binding,
    reference_discovery_binding,
    preset_discovery_binding,
    preset_create_binding,
    preset_item_get_binding,
    preset_item_update_binding,
    preset_revision_list_binding,
    preset_revision_restore_binding,
    preset_lifecycle_apply_binding,
    strategy_register_binding,
    run_list_binding,
    run_compare_binding,
    run_backtest_launch_binding,
    run_backtest_item_get_binding,
    run_rerun_backtest_binding,
    run_rerun_sandbox_binding,
    run_rerun_paper_binding,
    run_sandbox_launch_binding,
    run_paper_launch_binding,
    run_live_launch_binding,
    operator_incident_external_sync_binding,
    guarded_live_kill_switch_engage_binding,
    guarded_live_kill_switch_release_binding,
    guarded_live_reconciliation_binding,
    guarded_live_recovery_binding,
    guarded_live_incident_acknowledge_binding,
    guarded_live_incident_remediate_binding,
    guarded_live_incident_escalate_binding,
    guarded_live_resume_binding,
    stop_sandbox_run_binding,
    stop_paper_run_binding,
    stop_live_run_binding,
    cancel_live_order_binding,
    replace_live_order_binding,
    *run_subresource_bindings,
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
  if binding.binding_kind == "operator_visibility":
    return asdict(app.get_operator_visibility())
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
