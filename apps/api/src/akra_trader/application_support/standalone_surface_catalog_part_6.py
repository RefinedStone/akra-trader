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


def build_standalone_surface_runtime_bindings_part_6() -> tuple[StandaloneSurfaceRuntimeBinding, ...]:
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

  return (
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
  )
