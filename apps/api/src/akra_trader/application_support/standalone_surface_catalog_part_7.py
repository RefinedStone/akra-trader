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


def build_standalone_surface_runtime_bindings_part_7() -> tuple[StandaloneSurfaceRuntimeBinding, ...]:
  operator_incident_external_sync_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_incident_external_sync",
    route_path="/operator/incidents/external-sync",
    route_name="sync_external_incident",
    response_title="External incident sync",
    scope="app",
    binding_kind="operator_incident_external_sync",
    methods=("POST",),
    header_keys=("x_akra_incident_sync_token",),
    request_payload_kind="external_incident_sync",
  )

  guarded_live_kill_switch_engage_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_kill_switch_engage",
    route_path="/guarded-live/kill-switch/engage",
    route_name="engage_guarded_live_kill_switch",
    response_title="Engage guarded-live kill switch",
    scope="app",
    binding_kind="guarded_live_kill_switch_engage",
    methods=("POST",),
    request_payload_kind="guarded_live_action",
  )

  guarded_live_kill_switch_release_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_kill_switch_release",
    route_path="/guarded-live/kill-switch/release",
    route_name="release_guarded_live_kill_switch",
    response_title="Release guarded-live kill switch",
    scope="app",
    binding_kind="guarded_live_kill_switch_release",
    methods=("POST",),
    request_payload_kind="guarded_live_action",
  )

  guarded_live_reconciliation_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_reconciliation",
    route_path="/guarded-live/reconciliation",
    route_name="run_guarded_live_reconciliation",
    response_title="Run guarded-live reconciliation",
    scope="app",
    binding_kind="guarded_live_reconciliation",
    methods=("POST",),
    request_payload_kind="guarded_live_action",
  )

  guarded_live_recovery_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_recovery",
    route_path="/guarded-live/recovery",
    route_name="recover_guarded_live_runtime_state",
    response_title="Recover guarded-live runtime state",
    scope="app",
    binding_kind="guarded_live_recovery",
    methods=("POST",),
    request_payload_kind="guarded_live_action",
  )

  guarded_live_incident_acknowledge_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_incident_acknowledge",
    route_path="/guarded-live/incidents/{event_id}/acknowledge",
    route_name="acknowledge_guarded_live_incident",
    response_title="Acknowledge guarded-live incident",
    scope="app",
    binding_kind="guarded_live_incident_acknowledge",
    methods=("POST",),
    path_param_keys=("event_id",),
    request_payload_kind="guarded_live_action",
  )

  guarded_live_incident_remediate_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_incident_remediate",
    route_path="/guarded-live/incidents/{event_id}/remediate",
    route_name="remediate_guarded_live_incident",
    response_title="Remediate guarded-live incident",
    scope="app",
    binding_kind="guarded_live_incident_remediate",
    methods=("POST",),
    path_param_keys=("event_id",),
    request_payload_kind="guarded_live_action",
  )

  guarded_live_incident_escalate_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_incident_escalate",
    route_path="/guarded-live/incidents/{event_id}/escalate",
    route_name="escalate_guarded_live_incident",
    response_title="Escalate guarded-live incident",
    scope="app",
    binding_kind="guarded_live_incident_escalate",
    methods=("POST",),
    path_param_keys=("event_id",),
    request_payload_kind="guarded_live_action",
  )

  guarded_live_resume_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_resume",
    route_path="/guarded-live/resume",
    route_name="resume_guarded_live_run",
    response_title="Resume guarded-live run",
    scope="app",
    binding_kind="guarded_live_resume",
    methods=("POST",),
    request_payload_kind="guarded_live_action",
  )

  stop_sandbox_run_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_stop_sandbox",
    route_path="/runs/sandbox/{run_id}/stop",
    route_name="stop_sandbox_run",
    response_title="Stop sandbox run",
    scope="run",
    binding_kind="run_stop_sandbox",
    methods=("POST",),
  )

  stop_paper_run_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_stop_paper",
    route_path="/runs/paper/{run_id}/stop",
    route_name="stop_paper_run",
    response_title="Stop paper run",
    scope="run",
    binding_kind="run_stop_paper",
    methods=("POST",),
  )

  stop_live_run_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_stop_live",
    route_path="/runs/live/{run_id}/stop",
    route_name="stop_live_run",
    response_title="Stop live run",
    scope="run",
    binding_kind="run_stop_live",
    methods=("POST",),
  )

  cancel_live_order_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_live_order_cancel",
    route_path="/runs/live/{run_id}/orders/{order_id}/cancel",
    route_name="cancel_live_order",
    response_title="Cancel live order",
    scope="run",
    binding_kind="run_live_order_cancel",
    methods=("POST",),
    path_param_keys=("order_id",),
    request_payload_kind="guarded_live_action",
  )

  replace_live_order_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_live_order_replace",
    route_path="/runs/live/{run_id}/orders/{order_id}/replace",
    route_name="replace_live_order",
    response_title="Replace live order",
    scope="run",
    binding_kind="run_live_order_replace",
    methods=("POST",),
    path_param_keys=("order_id",),
    request_payload_kind="guarded_live_order_replace",
  )

  return (
    operator_incident_external_sync_binding,
    guarded_live_kill_switch_engage_binding,
    guarded_live_kill_switch_release_binding,
    guarded_live_reconciliation_binding,
    guarded_live_recovery_binding,
    guarded_live_incident_acknowledge_binding,
    guarded_live_incident_remediate_binding,
    guarded_live_incident_escalate_binding,
    guarded_live_resume_binding,
    stop_sandbox_run_binding,
    stop_paper_run_binding,
    stop_live_run_binding,
    cancel_live_order_binding,
    replace_live_order_binding,
  )
