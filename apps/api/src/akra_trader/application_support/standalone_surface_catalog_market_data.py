from __future__ import annotations

from datetime import datetime

from akra_trader.application_support.runtime_queries import _build_datetime_range_filter_operators
from akra_trader.application_support.runtime_queries import _build_numeric_range_filter_operators
from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterConstraintSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterOpenAPISpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterOperatorSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceFilterParamSpec
from akra_trader.application_support.runtime_queries import StandaloneSurfaceRuntimeBinding
from akra_trader.application_support.runtime_queries import StandaloneSurfaceSortFieldSpec


def build_market_data_runtime_bindings() -> tuple[StandaloneSurfaceRuntimeBinding, ...]:
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
  market_data_lineage_history_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="market_data_lineage_history",
    route_path="/market-data/lineage-history",
    route_name="list_market_data_lineage_history",
    response_title="Market data lineage history",
    scope="app",
    binding_kind="market_data_lineage_history",
    filter_keys=(
      "symbol",
      "timeframe",
      "sync_status",
      "validation_claim",
      "boundary_id",
      "checkpoint_id",
      "recorded_at",
      "last_sync_at",
      "candle_count",
      "failure_count_24h",
      "lag_seconds",
      "issue",
    ),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "symbol",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=3),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Symbol",
          description="Filter lineage history by symbol.",
          examples=("BTC/USDT",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single market symbol.",
          ),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "timeframe",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=2, max_length=10),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Timeframe",
          description="Filter lineage history by candlestick timeframe.",
          examples=("5m",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single timeframe value.",
          ),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "sync_status",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Sync status",
          description="Filter lineage history by sync status snapshot.",
          examples=("error",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single sync status.",
          ),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "validation_claim",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Validation claim",
          description="Filter lineage history by normalized dataset-boundary claim.",
          examples=("checkpoint_window",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single validation-claim category.",
          ),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "boundary_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Boundary ID",
          description="Filter lineage history by normalized dataset-boundary identifier.",
          examples=("checkpoint-v1:binance:BTC/USDT:5m:2025-01-02T00:00:00+00:00",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches one normalized boundary identifier.",
          ),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "checkpoint_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Checkpoint ID",
          description="Filter lineage history by sync-checkpoint identifier.",
          examples=("checkpoint-v1:binance:BTC/USDT:5m:2025-01-02T00:00:00+00:00",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches one sync-checkpoint identifier.",
          ),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "recorded_at",
        datetime | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Recorded at",
          description="Filter lineage history by when the snapshot was recorded.",
          examples=("2025-01-02T00:00:00+00:00",),
        ),
        operators=_build_datetime_range_filter_operators("lineage snapshot recording time"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "last_sync_at",
        datetime | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Last sync at",
          description="Filter lineage history by the underlying sync completion time.",
          examples=("2025-01-02T00:00:00+00:00",),
        ),
        operators=_build_datetime_range_filter_operators("underlying sync completion time"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "candle_count",
        int | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Candle count",
          description="Filter lineage history by covered candle count.",
          examples=(500,),
        ),
        operators=_build_numeric_range_filter_operators("covered candle count"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "failure_count_24h",
        int | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Failure count (24h)",
          description="Filter lineage history by recent sync failure count.",
          examples=(1,),
        ),
        operators=_build_numeric_range_filter_operators("recent failure count"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "lag_seconds",
        int | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Lag seconds",
          description="Filter lineage history by observed freshness lag.",
          examples=(300,),
        ),
        operators=_build_numeric_range_filter_operators("freshness lag seconds"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "issue",
        list[str],
        default_factory=list,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Issues",
          description="Filter lineage history by recorded issue tokens.",
          examples=(["last_sync_failed"],),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="contains_all",
            label="Contains all",
            description="Requires all requested issue tokens to be present.",
            value_shape="list",
          ),
          StandaloneSurfaceFilterOperatorSpec(
            key="contains_any",
            label="Contains any",
            description="Matches if any requested issue token is present.",
            value_shape="list",
          ),
        ),
        value_path=("issues",),
      ),
    ),
    sort_field_specs=(
      StandaloneSurfaceSortFieldSpec(
        key="recorded_at",
        label="Recorded at",
        description="Sorts lineage history by snapshot recording time.",
        default_direction="desc",
        value_type="datetime",
        value_path=("recorded_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="last_sync_at",
        label="Last sync at",
        description="Sorts lineage history by underlying sync completion time.",
        default_direction="desc",
        value_type="datetime",
        value_path=("last_sync_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="symbol",
        label="Symbol",
        description="Sorts lineage history by market symbol.",
        value_path=("symbol",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="candle_count",
        label="Candle count",
        description="Sorts lineage history by covered candle count.",
        default_direction="desc",
        value_type="number",
        value_path=("candle_count",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="failure_count_24h",
        label="Failure count (24h)",
        description="Sorts lineage history by recent failure count.",
        default_direction="desc",
        value_type="number",
        value_path=("failure_count_24h",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="lag_seconds",
        label="Lag seconds",
        description="Sorts lineage history by observed freshness lag.",
        default_direction="desc",
        value_type="number",
        value_path=("lag_seconds",),
      ),
    ),
  )
  market_data_ingestion_job_history_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="market_data_ingestion_job_history",
    route_path="/market-data/ingestion-jobs",
    route_name="list_market_data_ingestion_jobs",
    response_title="Market data ingestion jobs",
    scope="app",
    binding_kind="market_data_ingestion_job_history",
    filter_keys=(
      "symbol",
      "timeframe",
      "operation",
      "status",
      "validation_claim",
      "checkpoint_id",
      "started_at",
      "finished_at",
      "fetched_candle_count",
      "duration_ms",
      "last_error",
    ),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "symbol",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=3),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Symbol",
          description="Filter ingestion jobs by symbol.",
          examples=("BTC/USDT",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single market symbol.",
          ),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "timeframe",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=2, max_length=10),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Timeframe",
          description="Filter ingestion jobs by candlestick timeframe.",
          examples=("5m",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single timeframe value.",
          ),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "operation",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Operation",
          description="Filter ingestion jobs by sync operation kind.",
          examples=("sync_recent", "backfill_history"),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single ingestion operation.",
          ),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "status",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Status",
          description="Filter ingestion jobs by execution status.",
          examples=("failed",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single ingestion-job status.",
          ),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "validation_claim",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Validation claim",
          description="Filter ingestion jobs by the resulting dataset-boundary claim.",
          examples=("checkpoint_window",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single validation-claim category.",
          ),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "checkpoint_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Checkpoint ID",
          description="Filter ingestion jobs by the checkpoint captured after completion.",
          examples=("checkpoint-v1:binance:BTC/USDT:5m:2025-01-02T00:00:00+00:00",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches one sync-checkpoint identifier.",
          ),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "started_at",
        datetime | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Started at",
          description="Filter ingestion jobs by job start time.",
          examples=("2025-01-02T00:00:00+00:00",),
        ),
        operators=_build_datetime_range_filter_operators("ingestion job start time"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "finished_at",
        datetime | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Finished at",
          description="Filter ingestion jobs by completion time.",
          examples=("2025-01-02T00:00:01+00:00",),
        ),
        operators=_build_datetime_range_filter_operators("ingestion job completion time"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "fetched_candle_count",
        int | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Fetched candle count",
          description="Filter ingestion jobs by fetched candle count.",
          examples=(96,),
        ),
        operators=_build_numeric_range_filter_operators("fetched candle count"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "duration_ms",
        int | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Duration ms",
          description="Filter ingestion jobs by execution duration in milliseconds.",
          examples=(250,),
        ),
        operators=_build_numeric_range_filter_operators("ingestion job duration"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "last_error",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Last error",
          description="Filter ingestion jobs by error text.",
          examples=("upstream fetch failed",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches an exact error string.",
          ),
          StandaloneSurfaceFilterOperatorSpec(
            key="prefix",
            label="Prefix",
            description="Matches an error-text prefix.",
          ),
        ),
      ),
    ),
    sort_field_specs=(
      StandaloneSurfaceSortFieldSpec(
        key="started_at",
        label="Started at",
        description="Sorts ingestion jobs by start time.",
        default_direction="desc",
        value_type="datetime",
        value_path=("started_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="finished_at",
        label="Finished at",
        description="Sorts ingestion jobs by completion time.",
        default_direction="desc",
        value_type="datetime",
        value_path=("finished_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="symbol",
        label="Symbol",
        description="Sorts ingestion jobs by market symbol.",
        value_path=("symbol",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="operation",
        label="Operation",
        description="Sorts ingestion jobs by operation kind.",
        value_path=("operation",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="duration_ms",
        label="Duration ms",
        description="Sorts ingestion jobs by execution duration.",
        default_direction="desc",
        value_type="number",
        value_path=("duration_ms",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="fetched_candle_count",
        label="Fetched candle count",
        description="Sorts ingestion jobs by fetched candle count.",
        default_direction="desc",
        value_type="number",
        value_path=("fetched_candle_count",),
      ),
    ),
  )
  return (
    market_data_status_binding,
    market_data_lineage_history_binding,
    market_data_ingestion_job_history_binding,
  )
