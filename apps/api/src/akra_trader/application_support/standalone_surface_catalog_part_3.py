from __future__ import annotations

from datetime import datetime

from akra_trader.application_support.runtime_queries import _build_datetime_range_filter_operators
from akra_trader.application_support.runtime_queries import _build_numeric_range_filter_operators
from akra_trader.application_support.runtime_queries import StandaloneSurfaceCollectionPathParameterSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceCollectionPathSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterConstraintSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterOpenAPISpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterOperatorSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterParamSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceRuntimeBinding
from akra_trader.application_support.runtime_queries import StandaloneSurfaceSortFieldSpec
from akra_trader.application_support.standalone_surface_catalog_core import (
  build_core_runtime_bindings,
)
from akra_trader.application_support.standalone_surface_catalog_market_data import (
  build_market_data_runtime_bindings,
)
from akra_trader.application_support.standalone_surface_catalog_replay_links import (
  build_replay_link_runtime_bindings,
)


def build_standalone_surface_runtime_bindings_part_3() -> tuple[StandaloneSurfaceRuntimeBinding, ...]:
  operator_provider_provenance_scheduler_narrative_registry_update_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_registry_update",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-registry/{registry_id}",
    route_name="update_operator_provider_provenance_scheduler_narrative_registry_entry",
    response_title="Update provider provenance scheduler narrative registry entry",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_registry_update",
    methods=("PATCH",),
    path_param_keys=("registry_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_registry_update",
  )

  operator_provider_provenance_scheduler_narrative_registry_delete_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_registry_delete",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-registry/{registry_id}/delete",
    route_name="delete_operator_provider_provenance_scheduler_narrative_registry_entry",
    response_title="Delete provider provenance scheduler narrative registry entry",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_registry_delete",
    methods=("POST",),
    path_param_keys=("registry_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_registry_delete",
  )

  operator_provider_provenance_scheduler_narrative_registry_bulk_governance_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_registry_bulk_governance",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-registry/bulk-governance",
    route_name="bulk_govern_operator_provider_provenance_scheduler_narrative_registry_entries",
    response_title="Bulk govern provider provenance scheduler narrative registry entries",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_registry_bulk_governance",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_registry_bulk_governance",
  )

  operator_provider_provenance_scheduler_narrative_registry_revision_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_registry_revision_list",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-registry/{registry_id}/revisions",
    route_name="list_operator_provider_provenance_scheduler_narrative_registry_revisions",
    response_title="List provider provenance scheduler narrative registry revisions",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_registry_revision_list",
    path_param_keys=("registry_id",),
  )

  operator_provider_provenance_scheduler_narrative_registry_revision_restore_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_registry_revision_restore",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-registry/{registry_id}/revisions/{revision_id}/restore",
    route_name="restore_operator_provider_provenance_scheduler_narrative_registry_revision",
    response_title="Restore provider provenance scheduler narrative registry revision",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_registry_revision_restore",
    methods=("POST",),
    path_param_keys=("registry_id", "revision_id"),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_registry_revision_restore",
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_template_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_template_create",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-templates",
    route_name="create_operator_provider_provenance_scheduler_narrative_governance_policy_template",
    response_title="Create provider provenance scheduler narrative governance policy template",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_template_create",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_policy_template_create",
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_template_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_template_list",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-templates",
    route_name="list_operator_provider_provenance_scheduler_narrative_governance_policy_templates",
    response_title="List provider provenance scheduler narrative governance policy templates",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_template_list",
    filter_keys=("item_type_scope", "action_scope", "approval_lane", "approval_priority", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "item_type_scope",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Item type scope",
          description="Filter scheduler governance policy templates by template, registry, or any scope.",
          examples=("template",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "action_scope",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Action scope",
          description="Filter scheduler governance policy templates by update, delete, restore, or any scope.",
          examples=("update",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "approval_lane",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Approval lane",
          description="Filter scheduler governance policy templates by approval lane.",
          examples=("shift_lead",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "approval_priority",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Approval priority",
          description="Filter scheduler governance policy templates by queue priority.",
          examples=("high",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search scheduler governance policy templates by name, scope, lane, or guidance text.",
          examples=("cleanup",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=50,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=200),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of scheduler governance policy templates to return.",
          examples=(50,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_template_update_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_template_update",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-templates/{policy_template_id}",
    route_name="update_operator_provider_provenance_scheduler_narrative_governance_policy_template",
    response_title="Update provider provenance scheduler narrative governance policy template",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_template_update",
    methods=("PATCH",),
    path_param_keys=("policy_template_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_policy_template_update",
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_template_delete_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_template_delete",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-templates/{policy_template_id}/delete",
    route_name="delete_operator_provider_provenance_scheduler_narrative_governance_policy_template",
    response_title="Delete provider provenance scheduler narrative governance policy template",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_template_delete",
    methods=("POST",),
    path_param_keys=("policy_template_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_policy_template_delete",
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_list",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-templates/{policy_template_id}/revisions",
    route_name="list_operator_provider_provenance_scheduler_narrative_governance_policy_template_revisions",
    response_title="List provider provenance scheduler narrative governance policy template revisions",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_list",
    path_param_keys=("policy_template_id",),
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_restore_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_restore",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-templates/{policy_template_id}/revisions/{revision_id}/restore",
    route_name="restore_operator_provider_provenance_scheduler_narrative_governance_policy_template_revision",
    response_title="Restore provider provenance scheduler narrative governance policy template revision",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_restore",
    methods=("POST",),
    path_param_keys=("policy_template_id", "revision_id"),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_restore",
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_template_audit_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_template_audit_list",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-templates/audits",
    route_name="list_operator_provider_provenance_scheduler_narrative_governance_policy_template_audits",
    response_title="List provider provenance scheduler narrative governance policy template audits",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_template_audit_list",
    filter_keys=("policy_template_id", "action", "actor_tab_id", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "policy_template_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Policy template ID",
          description="Filter scheduler governance policy template audits by template.",
          examples=("tmpl_123",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "action",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Action",
          description="Filter scheduler governance policy template audits by action.",
          examples=("updated",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "actor_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Actor tab ID",
          description="Filter scheduler governance policy template audits by actor tab identity.",
          examples=("tab_ops",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search scheduler governance policy template audits by template, action, actor, or guidance.",
          examples=("shift_lead",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=50,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=200),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of scheduler governance policy template audit records to return.",
          examples=(25,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_catalog_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_create",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs",
    route_name="create_operator_provider_provenance_scheduler_narrative_governance_policy_catalog",
    response_title="Create provider provenance scheduler narrative governance policy catalog",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_create",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_create",
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_catalog_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_list",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs",
    route_name="list_operator_provider_provenance_scheduler_narrative_governance_policy_catalogs",
    response_title="List provider provenance scheduler narrative governance policy catalogs",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_list",
    filter_keys=("search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search scheduler governance policy catalogs by name, linked templates, lane, or guidance.",
          examples=("shift lead",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=20,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=100),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of scheduler governance policy catalogs to return.",
          examples=(20,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_catalog_update_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_update",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/{catalog_id}",
    route_name="update_operator_provider_provenance_scheduler_narrative_governance_policy_catalog",
    response_title="Update provider provenance scheduler narrative governance policy catalog",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_update",
    methods=("PATCH",),
    path_param_keys=("catalog_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_update",
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_catalog_delete_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_delete",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/{catalog_id}/delete",
    route_name="delete_operator_provider_provenance_scheduler_narrative_governance_policy_catalog",
    response_title="Delete provider provenance scheduler narrative governance policy catalog",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_delete",
    methods=("POST",),
    path_param_keys=("catalog_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_delete",
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_catalog_bulk_governance_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_bulk_governance",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/bulk-governance",
    route_name="bulk_govern_operator_provider_provenance_scheduler_narrative_governance_policy_catalogs",
    response_title="Bulk govern provider provenance scheduler narrative governance policy catalogs",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_bulk_governance",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_bulk_governance",
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/{catalog_id}/revisions",
    route_name="list_operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revisions",
    response_title="List provider provenance scheduler narrative governance policy catalog revisions",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list",
    path_param_keys=("catalog_id",),
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_restore_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_restore",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/{catalog_id}/revisions/{revision_id}/restore",
    route_name="restore_operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision",
    response_title="Restore provider provenance scheduler narrative governance policy catalog revision",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_restore",
    methods=("POST",),
    path_param_keys=("catalog_id", "revision_id"),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_restore",
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_list",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/audits",
    route_name="list_operator_provider_provenance_scheduler_narrative_governance_policy_catalog_audits",
    response_title="List provider provenance scheduler narrative governance policy catalog audits",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_list",
    filter_keys=("catalog_id", "action", "actor_tab_id", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "catalog_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Catalog ID",
          description="Filter scheduler governance policy catalog audits by catalog.",
          examples=("cat_123",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "action",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Action",
          description="Filter scheduler governance policy catalog audits by action.",
          examples=("updated",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "actor_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Actor tab ID",
          description="Filter scheduler governance policy catalog audits by actor tab identity.",
          examples=("tab_ops",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search scheduler governance policy catalog audits by catalog, template, action, or actor.",
          examples=("shift lead",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=50,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=200),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of scheduler governance policy catalog audit records to return.",
          examples=(25,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_capture_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_capture",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/{catalog_id}/hierarchy",
    route_name="capture_operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy",
    response_title="Capture provider provenance scheduler narrative governance policy catalog hierarchy",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_capture",
    methods=("POST",),
    path_param_keys=("catalog_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_capture",
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_update_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_update",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/{catalog_id}/hierarchy-steps/{step_id}",
    route_name="update_operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step",
    response_title="Update provider provenance scheduler narrative governance policy catalog hierarchy step",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_update",
    methods=("PATCH",),
    path_param_keys=("catalog_id", "step_id"),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_update",
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_restore_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_restore",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/{catalog_id}/hierarchy-steps/{step_id}/revisions/{revision_id}/restore",
    route_name="restore_operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step",
    response_title="Restore provider provenance scheduler narrative governance policy catalog hierarchy step revision",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_restore",
    methods=("POST",),
    path_param_keys=("catalog_id", "step_id", "revision_id"),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_restore",
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_bulk_governance_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_bulk_governance",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/{catalog_id}/hierarchy-steps/bulk-governance",
    route_name="bulk_govern_operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_steps",
    response_title="Bulk govern provider provenance scheduler narrative governance policy catalog hierarchy steps",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_bulk_governance",
    methods=("POST",),
    path_param_keys=("catalog_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_bulk_governance",
  )

  operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_create",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates",
    route_name="create_operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template",
    response_title="Create provider provenance scheduler narrative governance hierarchy step template",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_create",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_create",
  )

  operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_list",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates",
    route_name="list_operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_templates",
    response_title="List provider provenance scheduler narrative governance hierarchy step templates",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_list",
    filter_keys=("item_type", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "item_type",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Item type",
          description="Filter hierarchy step templates by supported scheduler narrative item type.",
          examples=("registry",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search hierarchy step templates by name, origin catalog, template provenance, or item targets.",
          examples=("cross-catalog",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=20,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=100),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of hierarchy step templates to return.",
          examples=(20,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_bulk_governance_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_bulk_governance",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/bulk-governance",
    route_name="bulk_govern_operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_templates",
    response_title="Bulk govern provider provenance scheduler narrative governance hierarchy step templates",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_bulk_governance",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_bulk_governance",
  )

  operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_update_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_update",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/{hierarchy_step_template_id}",
    route_name="update_operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template",
    response_title="Update provider provenance scheduler narrative governance hierarchy step template",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_update",
    methods=("PATCH",),
    path_param_keys=("hierarchy_step_template_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_update",
  )

  operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_delete_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_delete",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/{hierarchy_step_template_id}/delete",
    route_name="delete_operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template",
    response_title="Delete provider provenance scheduler narrative governance hierarchy step template",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_delete",
    methods=("POST",),
    path_param_keys=("hierarchy_step_template_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_delete",
  )

  operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_list",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/{hierarchy_step_template_id}/revisions",
    route_name="list_operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions",
    response_title="List provider provenance scheduler narrative governance hierarchy step template revisions",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_list",
    path_param_keys=("hierarchy_step_template_id",),
  )

  operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_restore_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_restore",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/{hierarchy_step_template_id}/revisions/{revision_id}/restore",
    route_name="restore_operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision",
    response_title="Restore provider provenance scheduler narrative governance hierarchy step template revision",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_restore",
    methods=("POST",),
    path_param_keys=("hierarchy_step_template_id", "revision_id"),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_restore",
  )

  operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_list",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/audits",
    route_name="list_operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audits",
    response_title="List provider provenance scheduler narrative governance hierarchy step template audits",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_list",
    filter_keys=("hierarchy_step_template_id", "action", "actor_tab_id", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "hierarchy_step_template_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Hierarchy step template ID",
          description="Filter scheduler governance hierarchy step template audits by template.",
          examples=("hst_123",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "action",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Action",
          description="Filter scheduler governance hierarchy step template audits by action.",
          examples=("updated",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "actor_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Actor tab ID",
          description="Filter scheduler governance hierarchy step template audits by actor tab identity.",
          examples=("tab_ops",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search scheduler governance hierarchy step template audits by template, action, actor, or origin.",
          examples=("cross-catalog",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=50,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=200),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of scheduler governance hierarchy step template audit records to return.",
          examples=(25,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_apply_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_apply",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/{hierarchy_step_template_id}/apply",
    route_name="apply_operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template",
    response_title="Apply provider provenance scheduler narrative governance hierarchy step template to policy catalogs",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_apply",
    methods=("POST",),
    path_param_keys=("hierarchy_step_template_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_apply",
  )

  operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_stage_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_stage",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/{hierarchy_step_template_id}/stage",
    route_name="stage_operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template",
    response_title="Stage provider provenance scheduler narrative governance hierarchy step template",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_stage",
    methods=("POST",),
    path_param_keys=("hierarchy_step_template_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_stage",
  )

  operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_batch_stage_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_batch_stage",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/hierarchy-step-templates/stage-batch",
    route_name="stage_batch_operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_templates",
    response_title="Stage provider provenance scheduler narrative governance hierarchy step templates in batch",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_batch_stage",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_batch_stage",
  )

  operator_provider_provenance_scheduler_narrative_governance_policy_catalog_stage_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_stage",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/policy-catalogs/{catalog_id}/stage",
    route_name="stage_operator_provider_provenance_scheduler_narrative_governance_policy_catalog",
    response_title="Stage provider provenance scheduler narrative governance policy catalog hierarchy",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_stage",
    methods=("POST",),
    path_param_keys=("catalog_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_policy_catalog_stage",
  )

  operator_provider_provenance_scheduler_narrative_governance_plan_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_plan_create",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/plans",
    route_name="create_operator_provider_provenance_scheduler_narrative_governance_plan",
    response_title="Create provider provenance scheduler narrative governance plan",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_plan_create",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_plan_create",
  )

  return (
    operator_provider_provenance_scheduler_narrative_registry_update_binding,
    operator_provider_provenance_scheduler_narrative_registry_delete_binding,
    operator_provider_provenance_scheduler_narrative_registry_bulk_governance_binding,
    operator_provider_provenance_scheduler_narrative_registry_revision_list_binding,
    operator_provider_provenance_scheduler_narrative_registry_revision_restore_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_template_create_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_template_list_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_template_update_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_template_delete_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_list_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_restore_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_template_audit_list_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_catalog_create_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_catalog_list_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_catalog_update_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_catalog_delete_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_catalog_bulk_governance_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_restore_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_list_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_capture_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_update_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_restore_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_bulk_governance_binding,
    operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_create_binding,
    operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_list_binding,
    operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_bulk_governance_binding,
    operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_update_binding,
    operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_delete_binding,
    operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_list_binding,
    operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_restore_binding,
    operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_list_binding,
    operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_apply_binding,
    operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_stage_binding,
    operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_batch_stage_binding,
    operator_provider_provenance_scheduler_narrative_governance_policy_catalog_stage_binding,
    operator_provider_provenance_scheduler_narrative_governance_plan_create_binding,
  )
