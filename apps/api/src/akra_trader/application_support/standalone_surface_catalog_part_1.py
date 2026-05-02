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


def build_standalone_surface_runtime_bindings_part_1() -> tuple[StandaloneSurfaceRuntimeBinding, ...]:
  operator_visibility_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_visibility",
    route_path="/operator/visibility",
    route_name="get_operator_visibility",
    response_title="Operator visibility",
    scope="app",
    binding_kind="operator_visibility",
  )

  operator_provider_provenance_export_job_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_export_job_create",
    route_path="/operator/provider-provenance-exports",
    route_name="create_operator_provider_provenance_export_job",
    response_title="Create provider provenance export job",
    scope="app",
    binding_kind="operator_provider_provenance_export_job_create",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_export_job_create",
  )

  operator_provider_provenance_export_job_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_export_job_list",
    route_path="/operator/provider-provenance-exports",
    route_name="list_operator_provider_provenance_export_jobs",
    response_title="List provider provenance export jobs",
    scope="app",
    binding_kind="operator_provider_provenance_export_job_list",
    filter_keys=(
      "export_scope",
      "focus_key",
      "symbol",
      "timeframe",
      "provider_label",
      "vendor_field",
      "market_data_provider",
      "venue",
      "requested_by_tab_id",
      "status",
      "search",
      "limit",
    ),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "export_scope",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Export scope",
          description="Filter provider provenance export jobs by export scope.",
          examples=("provider_provenance_scheduler_health",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "focus_key",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=3),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Focus key",
          description="Filter provider provenance export jobs by triage focus key.",
          examples=("binance:BTC/USDT|5m",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "symbol",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=3),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Symbol",
          description="Filter provider provenance export jobs by symbol.",
          examples=("BTC/USDT",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "timeframe",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=2, max_length=10),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Timeframe",
          description="Filter provider provenance export jobs by timeframe.",
          examples=("5m",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "provider_label",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Provider label",
          description="Filter provider provenance export jobs by linked provider label.",
          examples=("pagerduty",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "vendor_field",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Vendor field",
          description="Filter provider provenance export jobs by vendor-native market-context field.",
          examples=("custom_details.market_context",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "market_data_provider",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Market-data provider",
          description="Filter provider provenance export jobs by market-data provider.",
          examples=("binance",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "venue",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Venue",
          description="Filter provider provenance export jobs by market venue.",
          examples=("binance",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "requested_by_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Requested by tab ID",
          description="Filter provider provenance export jobs by requesting tab identity.",
          examples=("tab_local",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "status",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Status",
          description="Filter provider provenance export jobs by status.",
          examples=("completed",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search provider provenance export jobs by focus, requester, provider labels, or vendor fields.",
          examples=("BTC/USDT",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=100,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=500),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of provider provenance export jobs to return.",
          examples=(25,),
        ),
      ),
    ),
  )

  operator_provider_provenance_export_analytics_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_export_analytics",
    route_path="/operator/provider-provenance-exports/analytics",
    route_name="get_operator_provider_provenance_export_analytics",
    response_title="Provider provenance export analytics",
    scope="app",
    binding_kind="operator_provider_provenance_export_analytics",
    filter_keys=(
      "focus_key",
      "symbol",
      "timeframe",
      "provider_label",
      "vendor_field",
      "market_data_provider",
      "venue",
      "requested_by_tab_id",
      "status",
      "search",
      "result_limit",
      "window_days",
    ),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "focus_key",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=3),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Focus key",
          description="Filter provider provenance analytics by triage focus key.",
          examples=("binance:BTC/USDT|5m",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "symbol",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=3),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Symbol",
          description="Filter provider provenance analytics by symbol.",
          examples=("BTC/USDT",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "timeframe",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=2, max_length=10),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Timeframe",
          description="Filter provider provenance analytics by timeframe.",
          examples=("5m",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "provider_label",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Provider label",
          description="Filter provider provenance analytics by linked provider label.",
          examples=("pagerduty",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "vendor_field",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Vendor field",
          description="Filter provider provenance analytics by vendor-native field.",
          examples=("custom_details.market_context",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "market_data_provider",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Market-data provider",
          description="Filter provider provenance analytics by market-data provider.",
          examples=("binance",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "venue",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Venue",
          description="Filter provider provenance analytics by venue.",
          examples=("binance",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "requested_by_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Requested by tab ID",
          description="Filter provider provenance analytics by requesting tab identity.",
          examples=("tab_local",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "status",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Status",
          description="Filter provider provenance analytics by export job status.",
          examples=("completed",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search provider provenance analytics by focus, requester, provider labels, or vendor fields.",
          examples=("BTC/USDT",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "result_limit",
        int,
        default=12,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=50),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Result limit",
          description="Maximum number of recent export rows to return with the analytics payload.",
          examples=(12,),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "window_days",
        int,
        default=14,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=3, le=90),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Window days",
          description="Number of daily buckets to include in provider provenance time-series analytics.",
          examples=(14,),
        ),
      ),
    ),
  )

  operator_provider_provenance_export_job_download_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_export_job_download",
    route_path="/operator/provider-provenance-exports/{job_id}/download",
    route_name="download_operator_provider_provenance_export_job",
    response_title="Download provider provenance export job",
    scope="app",
    binding_kind="operator_provider_provenance_export_job_download",
    path_param_keys=("job_id",),
    filter_keys=("source_tab_id", "source_tab_label"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "source_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Source tab ID",
          description="Optional tab identity to attribute download audit events.",
          examples=("tab_local",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "source_tab_label",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Source tab label",
          description="Optional tab label to attribute download audit events.",
          examples=("Control Room",),
        ),
      ),
    ),
  )

  operator_provider_provenance_export_job_history_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_export_job_history",
    route_path="/operator/provider-provenance-exports/{job_id}/history",
    route_name="get_operator_provider_provenance_export_job_history",
    response_title="Provider provenance export job history",
    scope="app",
    binding_kind="operator_provider_provenance_export_job_history",
    path_param_keys=("job_id",),
  )

  operator_provider_provenance_export_job_policy_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_export_job_policy",
    route_path="/operator/provider-provenance-exports/{job_id}/policy",
    route_name="update_operator_provider_provenance_export_job_policy",
    response_title="Update provider provenance export job routing policy",
    scope="app",
    binding_kind="operator_provider_provenance_export_job_policy",
    methods=("POST",),
    path_param_keys=("job_id",),
    request_payload_kind="operator_provider_provenance_export_job_policy",
  )

  operator_provider_provenance_export_job_approval_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_export_job_approval",
    route_path="/operator/provider-provenance-exports/{job_id}/approval",
    route_name="approve_operator_provider_provenance_export_job",
    response_title="Approve provider provenance export job escalation",
    scope="app",
    binding_kind="operator_provider_provenance_export_job_approval",
    methods=("POST",),
    path_param_keys=("job_id",),
    request_payload_kind="operator_provider_provenance_export_job_approval",
  )

  operator_provider_provenance_export_job_escalate_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_export_job_escalate",
    route_path="/operator/provider-provenance-exports/{job_id}/escalate",
    route_name="escalate_operator_provider_provenance_export_job",
    response_title="Escalate provider provenance export job",
    scope="app",
    binding_kind="operator_provider_provenance_export_job_escalate",
    methods=("POST",),
    path_param_keys=("job_id",),
    request_payload_kind="operator_provider_provenance_export_job_escalate",
  )

  operator_provider_provenance_analytics_preset_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_analytics_preset_create",
    route_path="/operator/provider-provenance-analytics/presets",
    route_name="create_operator_provider_provenance_analytics_preset",
    response_title="Create provider provenance analytics preset",
    scope="app",
    binding_kind="operator_provider_provenance_analytics_preset_create",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_analytics_preset_create",
  )

  operator_provider_provenance_analytics_preset_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_analytics_preset_list",
    route_path="/operator/provider-provenance-analytics/presets",
    route_name="list_operator_provider_provenance_analytics_presets",
    response_title="List provider provenance analytics presets",
    scope="app",
    binding_kind="operator_provider_provenance_analytics_preset_list",
    filter_keys=("created_by_tab_id", "focus_scope", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "created_by_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Created by tab ID",
          description="Filter analytics presets by creating tab identity.",
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
          description="Filter analytics presets by current-focus or all-focuses scope.",
          examples=("current_focus",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search analytics presets by name, description, focus, or provider filters.",
          examples=("BTC/USDT",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=50,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=200),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of analytics presets to return.",
          examples=(25,),
        ),
      ),
    ),
  )

  operator_provider_provenance_dashboard_view_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_dashboard_view_create",
    route_path="/operator/provider-provenance-analytics/views",
    route_name="create_operator_provider_provenance_dashboard_view",
    response_title="Create provider provenance dashboard view",
    scope="app",
    binding_kind="operator_provider_provenance_dashboard_view_create",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_dashboard_view_create",
  )

  operator_provider_provenance_dashboard_view_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_dashboard_view_list",
    route_path="/operator/provider-provenance-analytics/views",
    route_name="list_operator_provider_provenance_dashboard_views",
    response_title="List provider provenance dashboard views",
    scope="app",
    binding_kind="operator_provider_provenance_dashboard_view_list",
    filter_keys=("preset_id", "created_by_tab_id", "focus_scope", "highlight_panel", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "preset_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Preset ID",
          description="Filter dashboard views by linked analytics preset.",
          examples=("preset_123",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "created_by_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Created by tab ID",
          description="Filter dashboard views by creating tab identity.",
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
          description="Filter dashboard views by current-focus or all-focuses scope.",
          examples=("all_focuses",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "highlight_panel",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Highlight panel",
          description="Filter dashboard views by highlighted analytics panel.",
          examples=("drift",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "search",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Search",
          description="Search dashboard views by name, description, focus, or provider filters.",
          examples=("pagerduty",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "limit",
        int,
        default=50,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=1, le=200),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Limit",
          description="Maximum number of dashboard views to return.",
          examples=(25,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_stitched_report_view_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_view_create",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-views",
    route_name="create_operator_provider_provenance_scheduler_stitched_report_view",
    response_title="Create provider provenance scheduler stitched report view",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_view_create",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_stitched_report_view_create",
  )

  operator_provider_provenance_scheduler_stitched_report_view_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_view_list",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-views",
    route_name="list_operator_provider_provenance_scheduler_stitched_report_views",
    response_title="List provider provenance scheduler stitched report views",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_view_list",
    filter_keys=("created_by_tab_id", "category", "narrative_facet", "search", "limit"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "created_by_tab_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Created by tab ID",
          description="Filter stitched report views by creating tab identity.",
          examples=("tab_ops",),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "category",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Scheduler alert category",
          description="Filter stitched report views by scheduler alert category.",
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
          description="Filter stitched report views by scheduler narrative facet.",
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
          description="Search stitched report views by name, description, or scheduler query fields.",
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
          description="Maximum number of stitched report views to return.",
          examples=(12,),
        ),
      ),
    ),
  )

  operator_provider_provenance_scheduler_stitched_report_view_update_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_view_update",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-views/{view_id}",
    route_name="update_operator_provider_provenance_scheduler_stitched_report_view",
    response_title="Update provider provenance scheduler stitched report view",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_view_update",
    methods=("PATCH",),
    path_param_keys=("view_id",),
    request_payload_kind="operator_provider_provenance_scheduler_stitched_report_view_update",
  )

  operator_provider_provenance_scheduler_stitched_report_view_delete_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_view_delete",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-views/{view_id}/delete",
    route_name="delete_operator_provider_provenance_scheduler_stitched_report_view",
    response_title="Delete provider provenance scheduler stitched report view",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_view_delete",
    methods=("POST",),
    path_param_keys=("view_id",),
    request_payload_kind="operator_provider_provenance_scheduler_stitched_report_view_delete",
  )

  operator_provider_provenance_scheduler_stitched_report_view_bulk_governance_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_view_bulk_governance",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-views/bulk-governance",
    route_name="bulk_govern_operator_provider_provenance_scheduler_stitched_report_views",
    response_title="Bulk govern provider provenance scheduler stitched report views",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_view_bulk_governance",
    methods=("POST",),
    request_payload_kind="operator_provider_provenance_scheduler_stitched_report_view_bulk_governance",
  )

  operator_provider_provenance_scheduler_stitched_report_view_revision_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_view_revision_list",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-views/{view_id}/revisions",
    route_name="list_operator_provider_provenance_scheduler_stitched_report_view_revisions",
    response_title="List provider provenance scheduler stitched report view revisions",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_view_revision_list",
    path_param_keys=("view_id",),
  )

  operator_provider_provenance_scheduler_stitched_report_view_revision_restore_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_provider_provenance_scheduler_stitched_report_view_revision_restore",
    route_path="/operator/provider-provenance-analytics/scheduler-stitched-report-views/{view_id}/revisions/{revision_id}/restore",
    route_name="restore_operator_provider_provenance_scheduler_stitched_report_view_revision",
    response_title="Restore provider provenance scheduler stitched report view revision",
    scope="app",
    binding_kind="operator_provider_provenance_scheduler_stitched_report_view_revision_restore",
    methods=("POST",),
    path_param_keys=("view_id", "revision_id"),
    request_payload_kind="operator_provider_provenance_scheduler_stitched_report_view_revision_restore",
  )

  return (
    operator_visibility_binding,
    operator_provider_provenance_export_job_create_binding,
    operator_provider_provenance_export_job_list_binding,
    operator_provider_provenance_export_analytics_binding,
    operator_provider_provenance_export_job_download_binding,
    operator_provider_provenance_export_job_history_binding,
    operator_provider_provenance_export_job_policy_binding,
    operator_provider_provenance_export_job_approval_binding,
    operator_provider_provenance_export_job_escalate_binding,
    operator_provider_provenance_analytics_preset_create_binding,
    operator_provider_provenance_analytics_preset_list_binding,
    operator_provider_provenance_dashboard_view_create_binding,
    operator_provider_provenance_dashboard_view_list_binding,
    operator_provider_provenance_scheduler_stitched_report_view_create_binding,
    operator_provider_provenance_scheduler_stitched_report_view_list_binding,
    operator_provider_provenance_scheduler_stitched_report_view_update_binding,
    operator_provider_provenance_scheduler_stitched_report_view_delete_binding,
    operator_provider_provenance_scheduler_stitched_report_view_bulk_governance_binding,
    operator_provider_provenance_scheduler_stitched_report_view_revision_list_binding,
    operator_provider_provenance_scheduler_stitched_report_view_revision_restore_binding,
  )
