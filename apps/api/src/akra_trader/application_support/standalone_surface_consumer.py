from __future__ import annotations

from typing import Any

from akra_trader.application_support.runtime_queries import StandaloneSurfaceRuntimeBinding
from akra_trader.application_support.standalone_surface_consumer_handler_common import UNHANDLED
from akra_trader.application_support.standalone_surface_consumer_serializers import *
from akra_trader.application_support.standalone_surface_consumer_handler_1 import handle_standalone_surface_binding_part_1
from akra_trader.application_support.standalone_surface_consumer_handler_2 import handle_standalone_surface_binding_part_2
from akra_trader.application_support.standalone_surface_consumer_handler_3 import handle_standalone_surface_binding_part_3
from akra_trader.application_support.standalone_surface_consumer_handler_4 import handle_standalone_surface_binding_part_4

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
  for handler in (
    handle_standalone_surface_binding_part_1,
    handle_standalone_surface_binding_part_2,
    handle_standalone_surface_binding_part_3,
    handle_standalone_surface_binding_part_4,
  ):
    result = handler(
      binding=binding,
      app=app,
      run_id=run_id,
      resolved_filters=resolved_filters,
      resolved_payload=resolved_payload,
      resolved_path_params=resolved_path_params,
      resolved_headers=resolved_headers,
    )
    if result is not UNHANDLED:
      return result
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
