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


def build_standalone_surface_runtime_bindings_part_5() -> tuple[StandaloneSurfaceRuntimeBinding, ...]:
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

  return (
    preset_discovery_binding,
    preset_create_binding,
    preset_item_get_binding,
    preset_item_update_binding,
    preset_revision_list_binding,
    preset_revision_restore_binding,
    preset_lifecycle_apply_binding,
    strategy_register_binding,
  )
