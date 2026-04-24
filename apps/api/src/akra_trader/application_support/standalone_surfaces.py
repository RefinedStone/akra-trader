from __future__ import annotations

from typing import Any
from typing import Callable

from akra_trader.application_support.standalone_surface_catalog import (
  build_standalone_surface_runtime_bindings,
)
from akra_trader.application_support.runtime_queries import RunSubresourceContract
from akra_trader.application_support.runtime_queries import RunSubresourceRuntimeBinding
from akra_trader.application_support.runtime_queries import StandaloneSurfaceRuntimeBinding
from akra_trader.application_support.run_subresources import _serialize_run_metrics_subresource_body
from akra_trader.application_support.run_subresources import _serialize_run_orders_subresource_body
from akra_trader.application_support.run_subresources import (
  _serialize_run_positions_subresource_body,
)
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunSurfaceCapabilities
from akra_trader.application_support.standalone_surface_consumer import (
  serialize_preset,
  serialize_preset_revision,
  serialize_replay_intent_alias_record,
  serialize_replay_intent_alias_history,
  serialize_replay_intent_alias_audit_list,
  serialize_replay_intent_alias_audit_export_job_record,
  serialize_replay_intent_alias_audit_export_job_list,
  serialize_replay_intent_alias_audit_export_job_history,
  serialize_provider_provenance_export_job_record,
  serialize_provider_provenance_export_job_list,
  serialize_provider_provenance_export_job_history,
  serialize_provider_provenance_export_job_escalation_result,
  serialize_provider_provenance_export_job_policy_result,
  serialize_provider_provenance_analytics_preset_record,
  serialize_provider_provenance_analytics_preset_list,
  serialize_provider_provenance_dashboard_view_record,
  serialize_provider_provenance_dashboard_view_list,
  serialize_provider_provenance_scheduler_stitched_report_view_record,
  serialize_provider_provenance_scheduler_stitched_report_view_list,
  serialize_provider_provenance_scheduler_stitched_report_view_revision_list,
  serialize_provider_provenance_scheduler_stitched_report_view_audit_list,
  serialize_provider_provenance_scheduler_stitched_report_governance_registry_record,
  serialize_provider_provenance_scheduler_stitched_report_governance_registry_list,
  serialize_provider_provenance_scheduler_stitched_report_governance_registry_revision_list,
  serialize_provider_provenance_scheduler_stitched_report_governance_registry_audit_list,
  serialize_provider_provenance_scheduler_narrative_template_record,
  serialize_provider_provenance_scheduler_narrative_template_list,
  serialize_provider_provenance_scheduler_narrative_template_revision_list,
  serialize_provider_provenance_scheduler_narrative_bulk_governance_result,
  serialize_provider_provenance_scheduler_narrative_registry_record,
  serialize_provider_provenance_scheduler_narrative_registry_list,
  serialize_provider_provenance_scheduler_narrative_registry_revision_list,
  serialize_provider_provenance_scheduler_narrative_governance_plan_record,
  serialize_provider_provenance_scheduler_narrative_governance_plan_list,
  serialize_provider_provenance_scheduler_narrative_governance_policy_template_record,
  serialize_provider_provenance_scheduler_narrative_governance_policy_template_list,
  serialize_provider_provenance_scheduler_narrative_governance_policy_template_revision_list,
  serialize_provider_provenance_scheduler_narrative_governance_policy_template_audit_list,
  serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_record,
  serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_list,
  serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_list,
  serialize_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_list,
  serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_record,
  serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_list,
  serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list,
  serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_list,
  serialize_provider_provenance_scheduler_narrative_governance_policy_catalog_stage_result,
  serialize_provider_provenance_scheduler_narrative_governance_plan_batch_result,
  serialize_provider_provenance_scheduled_report_record,
  serialize_provider_provenance_scheduled_report_list,
  serialize_provider_provenance_scheduled_report_history,
  serialize_provider_provenance_scheduled_report_run_result,
  serialize_provider_provenance_scheduled_report_run_due_result,
  serialize_provider_provenance_scheduler_health_history,
  serialize_provider_provenance_scheduler_alert_history,
  serialize_strategy,
  serialize_run_comparison,
  serialize_run_surface_capabilities,
  execute_standalone_surface_binding,
  serialize_standalone_surface_response,
)
from akra_trader.application_support.standalone_surface_composer import (
  list_collection_query_shared_contracts,
  list_run_surface_shared_contracts,
  serialize_collection_path_parameter_domain,
  serialize_collection_path_parameter_spec,
  serialize_collection_path_spec,
  serialize_collection_query_expression_authoring,
  serialize_run_surface_shared_contracts,
  serialize_standalone_filter_param_spec,
)


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
