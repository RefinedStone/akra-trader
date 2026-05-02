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


def build_standalone_surface_runtime_bindings_part_4() -> tuple[StandaloneSurfaceRuntimeBinding, ...]:
  operator_provider_provenance_scheduler_narrative_governance_plan_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_plan_list",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/plans",
    route_name="list_operator_provider_provenance_scheduler_narrative_governance_plans",
    response_title="List provider provenance scheduler narrative governance plans",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_plan_list",
    filter_keys=(
      "item_type",
      "status",
      "queue_state",
      "approval_lane",
      "approval_priority",
      "policy_template_id",
      "policy_catalog_id",
      "source_hierarchy_step_template_id",
      "search",
      "sort",
      "limit",
    ),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "item_type",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Item type",
          description="Filter scheduler narrative governance plans by template or registry scope.",
          examples=("template",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "status",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Plan status",
          description="Filter scheduler narrative governance plans by previewed, approved, applied, or rolled_back state.",
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
          description="Filter scheduler narrative governance plans by pending approval, ready to apply, or completed queue state.",
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
          description="Filter scheduler narrative governance plans by approval lane.",
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
          description="Filter scheduler narrative governance plans by approval priority.",
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
          description="Filter scheduler narrative governance plans by linked policy template.",
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
          description="Filter scheduler narrative governance plans by policy catalog source.",
          examples=("cat_123",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "source_hierarchy_step_template_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Source hierarchy-step template ID",
          description="Filter scheduler narrative governance plans by source hierarchy-step template provenance.",
          examples=("hst_123",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search scheduler narrative governance plans by source template, policy, hierarchy, reason, or creator fields.",
          examples=("lag recovery",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "sort",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Sort",
          description="Sort scheduler narrative governance plans by queue priority, recency, or source template name.",
          examples=("source_template_asc",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=20,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=100),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of scheduler narrative governance plans to return.",
          examples=(20,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_narrative_governance_plan_approve_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_plan_approve",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/plans/{plan_id}/approve",
    route_name="approve_operator_provider_provenance_scheduler_narrative_governance_plan",
    response_title="Approve provider provenance scheduler narrative governance plan",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_plan_approve",
    methods=("POST",),
    path_param_keys=("plan_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_plan_approve",
  )

  operator_provider_provenance_scheduler_narrative_governance_plan_apply_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_plan_apply",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/plans/{plan_id}/apply",
    route_name="apply_operator_provider_provenance_scheduler_narrative_governance_plan",
    response_title="Apply provider provenance scheduler narrative governance plan",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_plan_apply",
    methods=("POST",),
    path_param_keys=("plan_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_plan_apply",
  )

  operator_provider_provenance_scheduler_narrative_governance_plan_batch_action_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_plan_batch_action",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/plans/batch",
    route_name="run_operator_provider_provenance_scheduler_narrative_governance_plan_batch_action",
    response_title="Run provider provenance scheduler narrative governance plan batch action",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_plan_batch_action",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_plan_batch_action",
  )

  operator_provider_provenance_scheduler_narrative_governance_plan_rollback_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_narrative_governance_plan_rollback",
    route_path="/operator/provider-provenance-analytics/scheduler-narrative-governance/plans/{plan_id}/rollback",
    route_name="rollback_operator_provider_provenance_scheduler_narrative_governance_plan",
    response_title="Rollback provider provenance scheduler narrative governance plan",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_narrative_governance_plan_rollback",
    methods=("POST",),
    path_param_keys=("plan_id",),
    request_payload_kind="operator_provider_provenance_scheduler_narrative_governance_plan_rollback",
  )

  operator_provider_provenance_scheduled_report_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduled_report_create",
    route_path="/operator/provider-provenance-analytics/reports",
    route_name="create_operator_provider_provenance_scheduled_report",
    response_title="Create provider provenance scheduled report",
    scope="app",
    binding_kind="operator_provider_provenance_scheduled_report_create",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduled_report_create",
  )

  operator_provider_provenance_scheduled_report_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduled_report_list",
    route_path="/operator/provider-provenance-analytics/reports",
    route_name="list_operator_provider_provenance_scheduled_reports",
    response_title="List provider provenance scheduled reports",
    scope="app",
    binding_kind="operator_provider_provenance_scheduled_report_list",
    filter_keys=("status", "cadence", "preset_id", "view_id", "created_by_tab_id", "focus_scope", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "status",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Status",
          description="Filter scheduled reports by scheduled or paused status.",
          examples=("scheduled",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "cadence",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Cadence",
          description="Filter scheduled reports by daily or weekly cadence.",
          examples=("daily",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "preset_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Preset ID",
          description="Filter scheduled reports by linked analytics preset.",
          examples=("preset_123",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "view_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="View ID",
          description="Filter scheduled reports by linked dashboard view.",
          examples=("view_123",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "created_by_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Created by tab ID",
          description="Filter scheduled reports by creating tab identity.",
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
          description="Filter scheduled reports by current-focus or all-focuses scope.",
          examples=("all_focuses",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search scheduled reports by name, cadence, focus, or provider filters.",
          examples=("weekly",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=50,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=200),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of scheduled reports to return.",
          examples=(25,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduled_report_run_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduled_report_run",
    route_path="/operator/provider-provenance-analytics/reports/{report_id}/run",
    route_name="run_operator_provider_provenance_scheduled_report",
    response_title="Run provider provenance scheduled report",
    scope="app",
    binding_kind="operator_provider_provenance_scheduled_report_run",
    methods=("POST",),
    path_param_keys=("report_id",),
    request_payload_kind="operator_provider_provenance_scheduled_report_run",
  )

  operator_provider_provenance_scheduled_report_run_due_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduled_report_run_due",
    route_path="/operator/provider-provenance-analytics/reports/run-due",
    route_name="run_due_operator_provider_provenance_scheduled_reports",
    response_title="Run due provider provenance scheduled reports",
    scope="app",
    binding_kind="operator_provider_provenance_scheduled_report_run_due",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduled_report_run_due",
  )

  operator_provider_provenance_scheduled_report_history_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduled_report_history",
    route_path="/operator/provider-provenance-analytics/reports/{report_id}/history",
    route_name="get_operator_provider_provenance_scheduled_report_history",
    response_title="Provider provenance scheduled report history",
    scope="app",
    binding_kind="operator_provider_provenance_scheduled_report_history",
    path_param_keys=("report_id",),
  )

  operator_provider_provenance_scheduler_health_history_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_health_history",
    route_path="/operator/provider-provenance-analytics/scheduler-health",
    route_name="list_operator_provider_provenance_scheduler_health_history",
    response_title="Provider provenance scheduler health history",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_health_history",
    filter_keys=("status", "limit", "offset"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "status",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Status",
          description="Filter scheduler health history by health status.",
          examples=("lagging",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=25,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=200),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of scheduler health records to return.",
          examples=(25,),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "offset",
        int,
        default=0,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=0, le=10_000),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Offset",
          description="Pagination offset into matching scheduler health records.",
          examples=(25,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_alert_history_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_alert_history",
    route_path="/operator/provider-provenance-analytics/scheduler-alerts",
    route_name="list_operator_provider_provenance_scheduler_alert_history",
    response_title="Provider provenance scheduler alert history",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_alert_history",
    filter_keys=("category", "status", "narrative_facet", "search", "limit", "offset"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "category",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Category",
          description="Filter scheduler alert history by occurrence category.",
          examples=("scheduler_lag",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "status",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Status",
          description="Filter scheduler alert history by occurrence state.",
          examples=("resolved",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "narrative_facet",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Narrative facet",
          description="Filter scheduler alert history by occurrence narrative facet.",
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
          description="Search scheduler alert occurrences by occurrence ID, summary, symbol, timeline, or narrative status sequence.",
          examples=("healthy",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=25,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=200),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of scheduler alert occurrences to return.",
          examples=(25,),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "offset",
        int,
        default=0,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=0, le=10_000),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Offset",
          description="Pagination offset into matching scheduler alert occurrences.",
          examples=(25,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_health_analytics_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_health_analytics",
    route_path="/operator/provider-provenance-analytics/scheduler-health/analytics",
    route_name="get_operator_provider_provenance_scheduler_health_analytics",
    response_title="Provider provenance scheduler health analytics",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_health_analytics",
    filter_keys=("status", "window_days", "history_limit", "drilldown_bucket_key", "drilldown_history_limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "status",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Status",
          description="Filter scheduler health analytics by health status.",
          examples=("failed",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "window_days",
        int,
        default=14,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=3, le=90),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Window days",
          description="Rolling day window for scheduler health analytics buckets.",
          examples=(14,),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "history_limit",
        int,
        default=12,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=50),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="History limit",
          description="Maximum number of recent scheduler health records to embed in analytics.",
          examples=(12,),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "drilldown_bucket_key",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=10, max_length=32),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Drill-down bucket key",
          description="Daily bucket key to expand into hourly scheduler health drill-down.",
          examples=("2026-04-22",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "drilldown_history_limit",
        int,
        default=24,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=100),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Drill-down history limit",
          description="Maximum number of selected-bucket scheduler records to embed in drill-down.",
          examples=(24,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_health_export_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_health_export",
    route_path="/operator/provider-provenance-analytics/scheduler-health/export",
    route_name="export_operator_provider_provenance_scheduler_health",
    response_title="Export provider provenance scheduler health",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_health_export",
    filter_keys=(
      "status",
      "window_days",
      "history_limit",
      "drilldown_bucket_key",
      "drilldown_history_limit",
      "offset",
      "limit",
      "format",
    ),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "status",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Status",
          description="Filter scheduler health export by status.",
          examples=("lagging",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "window_days",
        int,
        default=14,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=3, le=90),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Window days",
          description="Rolling day window for exported scheduler analytics buckets.",
          examples=(14,),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "history_limit",
        int,
        default=12,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=50),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="History limit",
          description="Maximum number of recent scheduler health records to embed in analytics export.",
          examples=(12,),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "drilldown_bucket_key",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=10, max_length=32),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Drill-down bucket key",
          description="Daily bucket key to expand into hourly scheduler health drill-down export.",
          examples=("2026-04-22",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "drilldown_history_limit",
        int,
        default=24,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=100),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Drill-down history limit",
          description="Maximum number of selected-bucket scheduler records to embed in export drill-down.",
          examples=(24,),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "offset",
        int,
        default=0,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=0, le=10_000),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Offset",
          description="Pagination offset for exported scheduler history page.",
          examples=(0,),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=25,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=200),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of scheduler health records to include in export history page.",
          examples=(25,),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "format",
        str,
        default="json",
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=3, max_length=4),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Format",
          description="Scheduler health export format.",
          examples=("json", "csv"),
        ),
      ),
    ),
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

  return (
    operator_provider_provenance_scheduler_narrative_governance_plan_list_binding,
    operator_provider_provenance_scheduler_narrative_governance_plan_approve_binding,
    operator_provider_provenance_scheduler_narrative_governance_plan_apply_binding,
    operator_provider_provenance_scheduler_narrative_governance_plan_batch_action_binding,
    operator_provider_provenance_scheduler_narrative_governance_plan_rollback_binding,
    operator_provider_provenance_scheduled_report_create_binding,
    operator_provider_provenance_scheduled_report_list_binding,
    operator_provider_provenance_scheduled_report_run_binding,
    operator_provider_provenance_scheduled_report_run_due_binding,
    operator_provider_provenance_scheduled_report_history_binding,
    operator_provider_provenance_scheduler_health_history_binding,
    operator_provider_provenance_scheduler_alert_history_binding,
    operator_provider_provenance_scheduler_health_analytics_binding,
    operator_provider_provenance_scheduler_health_export_binding,
    guarded_live_status_binding,
    strategy_discovery_binding,
  )
