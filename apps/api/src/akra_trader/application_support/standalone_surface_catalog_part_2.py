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


def build_standalone_surface_runtime_bindings_part_2() -> tuple[StandaloneSurfaceRuntimeBinding, ...]:
  operator_provider_provenance_scheduler_stitched_report_view_audit_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_view_audit_list",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-views/audits",
    route_name="list_operator_provider_provenance_scheduler_stitched_report_view_audits",
    response_title="List provider provenance scheduler stitched report view audits",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_view_audit_list",
    filter_keys=("view_id", "action", "actor_tab_id", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "view_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="View ID",
          description="Filter stitched report view audit rows by saved view.",
          examples=("view_demo",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "action",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Action",
          description="Filter stitched report view audit rows by lifecycle action.",
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
          description="Filter stitched report view audit rows by actor tab identity.",
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
          description="Search stitched report view audits by name, reason, detail, actor, or filter summary.",
          examples=("lag recovery",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=50,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=200),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of stitched report view audit rows to return.",
          examples=(20,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_stitched_report_governance_registry_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_governance_registry_create",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-governance-registries",
    route_name="create_operator_provider_provenance_scheduler_stitched_report_governance_registry",
    response_title="Create provider provenance stitched report governance registry",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_governance_registry_create",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_stitched_report_governance_registry_create",
  )

  operator_provider_provenance_scheduler_stitched_report_governance_registry_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_governance_registry_list",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-governance-registries",
    route_name="list_operator_provider_provenance_scheduler_stitched_report_governance_registries",
    response_title="List provider provenance stitched report governance registries",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_governance_registry_list",
    filter_keys=("search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search stitched report governance registries by name, description, queue slice, or default policy.",
          examples=("stitched queue",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=50,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=200),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of stitched report governance registries to return.",
          examples=(24,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_stitched_report_governance_registry_update_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_governance_registry_update",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-governance-registries/{registry_id}",
    route_name="update_operator_provider_provenance_scheduler_stitched_report_governance_registry",
    response_title="Update provider provenance stitched report governance registry",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_governance_registry_update",
    methods=("PATCH",),
    path_param_keys=("registry_id",),
    request_payload_kind="operator_provider_provenance_scheduler_stitched_report_governance_registry_update",
  )

  operator_provider_provenance_scheduler_stitched_report_governance_registry_delete_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_governance_registry_delete",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-governance-registries/{registry_id}/delete",
    route_name="delete_operator_provider_provenance_scheduler_stitched_report_governance_registry",
    response_title="Delete provider provenance stitched report governance registry",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_governance_registry_delete",
    methods=("POST",),
    path_param_keys=("registry_id",),
    request_payload_kind="operator_provider_provenance_scheduler_stitched_report_governance_registry_delete",
  )

  operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_list",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-governance-registries/{registry_id}/revisions",
    route_name="list_operator_provider_provenance_scheduler_stitched_report_governance_registry_revisions",
    response_title="List provider provenance stitched report governance registry revisions",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_list",
    path_param_keys=("registry_id",),
  )

  operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_restore_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_restore",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-governance-registries/{registry_id}/revisions/{revision_id}/restore",
    route_name="restore_operator_provider_provenance_scheduler_stitched_report_governance_registry_revision",
    response_title="Restore provider provenance stitched report governance registry revision",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_restore",
    methods=("POST",),
    path_param_keys=("registry_id", "revision_id"),
    request_payload_kind="operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_restore",
  )

  operator_provider_provenance_scheduler_stitched_report_governance_registry_bulk_governance_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_governance_registry_bulk_governance",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-governance-registries/bulk-governance",
    route_name="bulk_govern_operator_provider_provenance_scheduler_stitched_report_governance_registries",
    response_title="Bulk govern provider provenance stitched report governance registries",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_governance_registry_bulk_governance",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_stitched_report_governance_registry_bulk_governance",
  )

  operator_provider_provenance_scheduler_stitched_report_governance_registry_audit_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_governance_registry_audit_list",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-governance-registries/audits",
    route_name="list_operator_provider_provenance_scheduler_stitched_report_governance_registry_audits",
    response_title="List provider provenance stitched report governance registry audits",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_governance_registry_audit_list",
    filter_keys=("registry_id", "action", "actor_tab_id", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "registry_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Registry ID",
          description="Filter stitched governance registry audits by registry.",
          examples=("reg_demo",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "action",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Action",
          description="Filter stitched governance registry audits by lifecycle action.",
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
          description="Filter stitched governance registry audits by actor tab identity.",
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
          description="Search stitched governance registry audits by name, reason, detail, actor, queue slice, or default policy.",
          examples=("lag recovery",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=50,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=200),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of stitched governance registry audit rows to return.",
          examples=(20,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_stitched_report_governance_policy_template_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_governance_policy_template_list",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-governance/policy-templates",
    route_name="list_operator_provider_provenance_scheduler_stitched_report_governance_policy_templates",
    response_title="List provider provenance stitched report governance policy templates",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_governance_policy_template_list",
    filter_keys=("action_scope", "approval_lane", "approval_priority", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "action_scope",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Action scope",
          description="Filter stitched-governance-registry policy templates by update, delete, restore, or any scope.",
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
          description="Filter stitched-governance-registry policy templates by approval lane.",
          examples=("ops",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "approval_priority",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Approval priority",
          description="Filter stitched-governance-registry policy templates by approval priority.",
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
          description="Search stitched-governance-registry policy templates by name, lane, scope, or guidance.",
          examples=("registry cleanup",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=50,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=200),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of stitched-governance-registry policy templates to return.",
          examples=(24,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_stitched_report_governance_policy_catalog_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_governance_policy_catalog_list",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-governance/policy-catalogs",
    route_name="list_operator_provider_provenance_scheduler_stitched_report_governance_policy_catalogs",
    response_title="List provider provenance stitched report governance policy catalogs",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_governance_policy_catalog_list",
    filter_keys=("search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search stitched-governance-registry policy catalogs by name, template, lane, or guidance.",
          examples=("registry catalog",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=20,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=100),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of stitched-governance-registry policy catalogs to return.",
          examples=(20,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_stitched_report_governance_plan_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_governance_plan_create",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-governance/plans",
    route_name="create_operator_provider_provenance_scheduler_stitched_report_governance_plan",
    response_title="Create provider provenance stitched report governance plan",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_governance_plan_create",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_plan_create",
  )

  operator_provider_provenance_scheduler_stitched_report_governance_plan_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_governance_plan_list",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-governance/plans",
    route_name="list_operator_provider_provenance_scheduler_stitched_report_governance_plans",
    response_title="List provider provenance stitched report governance plans",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_governance_plan_list",
    filter_keys=(
      "status",
      "queue_state",
      "approval_lane",
      "approval_priority",
      "policy_template_id",
      "policy_catalog_id",
      "search",
      "sort",
      "limit",
    ),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "status",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Plan status",
          description="Filter stitched-governance-registry plans by previewed, approved, applied, or rolled_back state.",
          examples=("approved",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "queue_state",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Queue state",
          description="Filter stitched-governance-registry plans by pending approval, ready to apply, or completed queue state.",
          examples=("pending_approval",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "approval_lane",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Approval lane",
          description="Filter stitched-governance-registry plans by approval lane.",
          examples=("ops",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "approval_priority",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Approval priority",
          description="Filter stitched-governance-registry plans by approval priority.",
          examples=("critical",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "policy_template_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Policy template ID",
          description="Filter stitched-governance-registry plans by linked policy template.",
          examples=("pt_123",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "policy_catalog_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Policy catalog ID",
          description="Filter stitched-governance-registry plans by policy catalog source.",
          examples=("cat_123",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search stitched-governance-registry plans by policy, reason, queue slice, or creator.",
          examples=("registry queue",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "sort",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Sort",
          description="Sort stitched-governance-registry plans by queue priority or recency.",
          examples=("updated_desc",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=20,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=100),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of stitched-governance-registry plans to return.",
          examples=(24,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_stitched_report_governance_plan_approve_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_governance_plan_approve",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-governance/plans/{plan_id}/approve",
    route_name="approve_operator_provider_provenance_scheduler_stitched_report_governance_plan",
    response_title="Approve provider provenance stitched report governance plan",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_governance_plan_approve",
    methods=("POST",),
    path_param_keys=("plan_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_plan_approve",
  )

  operator_provider_provenance_scheduler_stitched_report_governance_plan_apply_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_governance_plan_apply",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-governance/plans/{plan_id}/apply",
    route_name="apply_operator_provider_provenance_scheduler_stitched_report_governance_plan",
    response_title="Apply provider provenance stitched report governance plan",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_governance_plan_apply",
    methods=("POST",),
    path_param_keys=("plan_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_plan_apply",
  )

  operator_provider_provenance_scheduler_stitched_report_governance_plan_rollback_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_governance_plan_rollback",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-governance/plans/{plan_id}/rollback",
    route_name="rollback_operator_provider_provenance_scheduler_stitched_report_governance_plan",
    response_title="Rollback provider provenance stitched report governance plan",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_governance_plan_rollback",
    methods=("POST",),
    path_param_keys=("plan_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_plan_rollback",
  )

  operator_provider_provenance_scheduler_narrative_template_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_template_create",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-templates",
    route_name="create_operator_provider_provenance_scheduler_narrative_template",
    response_title="Create provider provenance scheduler narrative template",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_template_create",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_template_create",
  )

  operator_provider_provenance_scheduler_narrative_template_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_template_list",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-templates",
    route_name="list_operator_provider_provenance_scheduler_narrative_templates",
    response_title="List provider provenance scheduler narrative templates",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_template_list",
    filter_keys=("created_by_tab_id", "focus_scope", "category", "narrative_facet", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "created_by_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Created by tab ID",
          description="Filter scheduler narrative templates by creating tab identity.",
          examples=("tab_ops",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "focus_scope",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Focus scope",
          description="Filter scheduler narrative templates by current-focus or all-focuses scope.",
          examples=("all_focuses",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "category",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Scheduler category",
          description="Filter scheduler narrative templates by scheduler alert category.",
          examples=("scheduler_lag",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "narrative_facet",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Narrative facet",
          description="Filter scheduler narrative templates by saved occurrence narrative facet.",
          examples=("post_resolution_recovery",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search scheduler narrative templates by name, category, or facet.",
          examples=("recovery",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=50,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=200),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of scheduler narrative templates to return.",
          examples=(25,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_narrative_template_update_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_template_update",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-templates/{template_id}",
    route_name="update_operator_provider_provenance_scheduler_narrative_template",
    response_title="Update provider provenance scheduler narrative template",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_template_update",
    methods=("PATCH",),
    path_param_keys=("template_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_template_update",
  )

  operator_provider_provenance_scheduler_narrative_template_delete_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_template_delete",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-templates/{template_id}/delete",
    route_name="delete_operator_provider_provenance_scheduler_narrative_template",
    response_title="Delete provider provenance scheduler narrative template",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_template_delete",
    methods=("POST",),
    path_param_keys=("template_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_template_delete",
  )

  operator_provider_provenance_scheduler_narrative_template_bulk_governance_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_template_bulk_governance",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-templates/bulk-governance",
    route_name="bulk_govern_operator_provider_provenance_scheduler_narrative_templates",
    response_title="Bulk govern provider provenance scheduler narrative templates",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_template_bulk_governance",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_template_bulk_governance",
  )

  operator_provider_provenance_scheduler_narrative_template_revision_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_template_revision_list",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-templates/{template_id}/revisions",
    route_name="list_operator_provider_provenance_scheduler_narrative_template_revisions",
    response_title="List provider provenance scheduler narrative template revisions",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_template_revision_list",
    path_param_keys=("template_id",),
  )

  operator_provider_provenance_scheduler_narrative_template_revision_restore_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_template_revision_restore",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-templates/{template_id}/revisions/{revision_id}/restore",
    route_name="restore_operator_provider_provenance_scheduler_narrative_template_revision",
    response_title="Restore provider provenance scheduler narrative template revision",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_template_revision_restore",
    methods=("POST",),
    path_param_keys=("template_id", "revision_id"),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_template_revision_restore",
  )

  operator_provider_provenance_scheduler_narrative_registry_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_registry_create",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-registry",
    route_name="create_operator_provider_provenance_scheduler_narrative_registry_entry",
    response_title="Create provider provenance scheduler narrative registry entry",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_registry_create",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_registry_create",
  )

  operator_provider_provenance_scheduler_narrative_registry_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_registry_list",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-registry",
    route_name="list_operator_provider_provenance_scheduler_narrative_registry_entries",
    response_title="List provider provenance scheduler narrative registry entries",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_registry_list",
    filter_keys=("template_id", "created_by_tab_id", "focus_scope", "category", "narrative_facet", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "template_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Template ID",
          description="Filter scheduler narrative registry entries by linked template.",
          examples=("tmpl_123",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "created_by_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Created by tab ID",
          description="Filter scheduler narrative registry entries by creating tab identity.",
          examples=("tab_ops",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "focus_scope",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Focus scope",
          description="Filter scheduler narrative registry entries by current-focus or all-focuses scope.",
          examples=("current_focus",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "category",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Scheduler category",
          description="Filter scheduler narrative registry entries by scheduler alert category.",
          examples=("scheduler_failure",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "narrative_facet",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Narrative facet",
          description="Filter scheduler narrative registry entries by saved occurrence narrative facet.",
          examples=("recurring_occurrences",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search scheduler narrative registry entries by name, template, category, or facet.",
          examples=("timeline",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=50,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=200),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of scheduler narrative registry entries to return.",
          examples=(25,),
        ),
      ),
    ),
  )

  return (
    operator_provider_provenance_scheduler_stitched_report_view_audit_list_binding,
    operator_provider_provenance_scheduler_stitched_report_governance_registry_create_binding,
    operator_provider_provenance_scheduler_stitched_report_governance_registry_list_binding,
    operator_provider_provenance_scheduler_stitched_report_governance_registry_update_binding,
    operator_provider_provenance_scheduler_stitched_report_governance_registry_delete_binding,
    operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_list_binding,
    operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_restore_binding,
    operator_provider_provenance_scheduler_stitched_report_governance_registry_bulk_governance_binding,
    operator_provider_provenance_scheduler_stitched_report_governance_registry_audit_list_binding,
    operator_provider_provenance_scheduler_stitched_report_governance_policy_template_list_binding,
    operator_provider_provenance_scheduler_stitched_report_governance_policy_catalog_list_binding,
    operator_provider_provenance_scheduler_stitched_report_governance_plan_create_binding,
    operator_provider_provenance_scheduler_stitched_report_governance_plan_list_binding,
    operator_provider_provenance_scheduler_stitched_report_governance_plan_approve_binding,
    operator_provider_provenance_scheduler_stitched_report_governance_plan_apply_binding,
    operator_provider_provenance_scheduler_stitched_report_governance_plan_rollback_binding,
    operator_provider_provenance_scheduler_narrative_template_create_binding,
    operator_provider_provenance_scheduler_narrative_template_list_binding,
    operator_provider_provenance_scheduler_narrative_template_update_binding,
    operator_provider_provenance_scheduler_narrative_template_delete_binding,
    operator_provider_provenance_scheduler_narrative_template_bulk_governance_binding,
    operator_provider_provenance_scheduler_narrative_template_revision_list_binding,
    operator_provider_provenance_scheduler_narrative_template_revision_restore_binding,
    operator_provider_provenance_scheduler_narrative_registry_create_binding,
    operator_provider_provenance_scheduler_narrative_registry_list_binding,
  )
