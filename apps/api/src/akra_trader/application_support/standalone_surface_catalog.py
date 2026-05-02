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


from akra_trader.application_support.standalone_surface_catalog_part_1 import build_standalone_surface_runtime_bindings_part_1
from akra_trader.application_support.standalone_surface_catalog_part_2 import build_standalone_surface_runtime_bindings_part_2
from akra_trader.application_support.standalone_surface_catalog_part_3 import build_standalone_surface_runtime_bindings_part_3
from akra_trader.application_support.standalone_surface_catalog_part_4 import build_standalone_surface_runtime_bindings_part_4
from akra_trader.application_support.standalone_surface_catalog_part_5 import build_standalone_surface_runtime_bindings_part_5
from akra_trader.application_support.standalone_surface_catalog_part_6 import build_standalone_surface_runtime_bindings_part_6
from akra_trader.application_support.standalone_surface_catalog_part_7 import build_standalone_surface_runtime_bindings_part_7

def build_standalone_surface_runtime_bindings(
  *,
  run_subresource_bindings: tuple[StandaloneSurfaceRuntimeBinding, ...] = (),
) -> tuple[StandaloneSurfaceRuntimeBinding, ...]:
  core_bindings = build_core_runtime_bindings()
  replay_link_bindings = build_replay_link_runtime_bindings()
  market_data_bindings = build_market_data_runtime_bindings()
  return (
    *core_bindings,
    *replay_link_bindings,
    *market_data_bindings,
    *build_standalone_surface_runtime_bindings_part_1(),
    *build_standalone_surface_runtime_bindings_part_2(),
    *build_standalone_surface_runtime_bindings_part_3(),
    *build_standalone_surface_runtime_bindings_part_4(),
    *build_standalone_surface_runtime_bindings_part_5(),
    *build_standalone_surface_runtime_bindings_part_6(),
    *build_standalone_surface_runtime_bindings_part_7(),
    *run_subresource_bindings,
  )
