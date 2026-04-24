from __future__ import annotations

from akra_trader.application_support.runtime_queries import StandaloneSurfaceRuntimeBinding


def build_core_runtime_bindings() -> tuple[StandaloneSurfaceRuntimeBinding, ...]:
  health_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="health_status",
    route_path="/health",
    route_name="health",
    response_title="Health",
    scope="app",
    binding_kind="health_status",
  )
  capability_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_surface_capabilities",
    route_path="/capabilities/run-surfaces",
    route_name="get_run_surface_capabilities",
    response_title="Run surface capabilities",
    scope="app",
    binding_kind="run_surface_capabilities",
  )
  return (
    health_binding,
    capability_binding,
  )
