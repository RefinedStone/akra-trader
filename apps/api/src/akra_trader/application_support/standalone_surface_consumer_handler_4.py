from __future__ import annotations

from dataclasses import asdict
from typing import Any

from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_comparison
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_market_data_ingestion_jobs
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_market_data_lineage_history
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_presets
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_runs
from akra_trader.application_support.runtime_queries import _apply_runtime_query_to_strategies
from akra_trader.application_support.runtime_queries import StandaloneSurfaceRuntimeBinding
from akra_trader.application_support.run_subresources import serialize_run_subresource_response
from akra_trader.application_support.run_surfaces import serialize_run
from akra_trader.application_support.standalone_surface_consumer_handler_common import UNHANDLED
from akra_trader.application_support.standalone_surface_consumer_serializers import *

def handle_standalone_surface_binding_part_4(
  *,
  binding: StandaloneSurfaceRuntimeBinding,
  app: Any,
  run_id: str | None,
  resolved_filters: dict[str, Any],
  resolved_payload: dict[str, Any],
  resolved_path_params: dict[str, Any],
  resolved_headers: dict[str, Any],
) -> Any:
  if binding.binding_kind == "strategy_catalog_register":
    metadata = app.register_strategy(
      strategy_id=resolved_payload["strategy_id"],
      module_path=resolved_payload["module_path"],
      class_name=resolved_payload["class_name"],
    )
    return serialize_strategy(metadata)

  if binding.binding_kind == "run_list":
    return [
      serialize_run(run, capabilities=app.get_run_surface_capabilities())
      for run in _apply_runtime_query_to_runs(
        app.list_runs(
          mode=resolved_filters.get("mode"),
          strategy_id=resolved_filters.get("strategy_id"),
          strategy_version=resolved_filters.get("strategy_version"),
          rerun_boundary_id=resolved_filters.get("rerun_boundary_id"),
          preset_id=resolved_filters.get("preset_id"),
          benchmark_family=resolved_filters.get("benchmark_family"),
          dataset_identity=resolved_filters.get("dataset_identity"),
          tags=resolved_filters.get("tag") or [],
        ),
        resolved_filters,
        binding=binding,
      )
    ]

  if binding.binding_kind == "run_compare":
    comparison = _apply_runtime_query_to_comparison(
      app.compare_runs(
        run_ids=resolved_filters.get("run_id") or [],
        intent=resolved_filters.get("intent"),
      ),
      resolved_filters,
      binding=binding,
    )
    return serialize_run_comparison(
      comparison,
      capabilities=app.get_run_surface_capabilities(),
    )

  if binding.binding_kind == "run_backtest_launch":
    run = app.run_backtest(
      strategy_id=resolved_payload["strategy_id"],
      symbol=resolved_payload["symbol"],
      timeframe=resolved_payload.get("timeframe", "5m"),
      initial_cash=resolved_payload.get("initial_cash", 10_000),
      fee_rate=resolved_payload.get("fee_rate", 0.001),
      slippage_bps=resolved_payload.get("slippage_bps", 3),
      parameters=resolved_payload.get("parameters") or {},
      start_at=resolved_payload.get("start_at"),
      end_at=resolved_payload.get("end_at"),
      tags=resolved_payload.get("tags") or [],
      preset_id=resolved_payload.get("preset_id"),
      benchmark_family=resolved_payload.get("benchmark_family"),
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())

  if binding.binding_kind == "run_backtest_item_get":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.get_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())

  if binding.binding_kind == "run_rerun_backtest":
    run = app.rerun_backtest_from_boundary(
      rerun_boundary_id=resolved_path_params["rerun_boundary_id"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())

  if binding.binding_kind == "run_rerun_sandbox":
    run = app.rerun_sandbox_from_boundary(
      rerun_boundary_id=resolved_path_params["rerun_boundary_id"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())

  if binding.binding_kind == "run_rerun_paper":
    run = app.rerun_paper_from_boundary(
      rerun_boundary_id=resolved_path_params["rerun_boundary_id"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())

  if binding.binding_kind == "run_sandbox_launch":
    run = app.start_sandbox_run(
      strategy_id=resolved_payload["strategy_id"],
      symbol=resolved_payload["symbol"],
      timeframe=resolved_payload.get("timeframe", "5m"),
      initial_cash=resolved_payload.get("initial_cash", 10_000),
      fee_rate=resolved_payload.get("fee_rate", 0.001),
      slippage_bps=resolved_payload.get("slippage_bps", 3),
      parameters=resolved_payload.get("parameters") or {},
      replay_bars=resolved_payload.get("replay_bars", 96),
      tags=resolved_payload.get("tags") or [],
      preset_id=resolved_payload.get("preset_id"),
      benchmark_family=resolved_payload.get("benchmark_family"),
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())

  if binding.binding_kind == "run_paper_launch":
    run = app.start_paper_run(
      strategy_id=resolved_payload["strategy_id"],
      symbol=resolved_payload["symbol"],
      timeframe=resolved_payload.get("timeframe", "5m"),
      initial_cash=resolved_payload.get("initial_cash", 10_000),
      fee_rate=resolved_payload.get("fee_rate", 0.001),
      slippage_bps=resolved_payload.get("slippage_bps", 3),
      parameters=resolved_payload.get("parameters") or {},
      replay_bars=resolved_payload.get("replay_bars", 96),
      tags=resolved_payload.get("tags") or [],
      preset_id=resolved_payload.get("preset_id"),
      benchmark_family=resolved_payload.get("benchmark_family"),
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())

  if binding.binding_kind == "run_live_launch":
    run = app.start_live_run(
      strategy_id=resolved_payload["strategy_id"],
      symbol=resolved_payload["symbol"],
      timeframe=resolved_payload.get("timeframe", "5m"),
      initial_cash=resolved_payload.get("initial_cash", 10_000),
      fee_rate=resolved_payload.get("fee_rate", 0.001),
      slippage_bps=resolved_payload.get("slippage_bps", 3),
      parameters=resolved_payload.get("parameters") or {},
      replay_bars=resolved_payload.get("replay_bars", 96),
      operator_reason=resolved_payload.get("operator_reason", "guarded_live_launch"),
      tags=resolved_payload.get("tags") or [],
      preset_id=resolved_payload.get("preset_id"),
      benchmark_family=resolved_payload.get("benchmark_family"),
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())

  if binding.binding_kind == "operator_incident_external_sync":
    app.require_operator_alert_external_sync_token(
      resolved_headers.get("x_akra_incident_sync_token"),
    )
    status = app.sync_guarded_live_incident_from_external(
      provider=resolved_payload["provider"],
      event_kind=resolved_payload["event_kind"],
      actor=resolved_payload["actor"],
      detail=resolved_payload["detail"],
      alert_id=resolved_payload.get("alert_id"),
      external_reference=resolved_payload.get("external_reference"),
      workflow_reference=resolved_payload.get("workflow_reference"),
      occurred_at=resolved_payload.get("occurred_at"),
      escalation_level=resolved_payload.get("escalation_level"),
      payload=resolved_payload.get("payload"),
    )
    return asdict(status)

  if binding.binding_kind == "guarded_live_kill_switch_engage":
    return asdict(
      app.engage_guarded_live_kill_switch(
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )

  if binding.binding_kind == "guarded_live_kill_switch_release":
    return asdict(
      app.release_guarded_live_kill_switch(
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )

  if binding.binding_kind == "guarded_live_reconciliation":
    return asdict(
      app.run_guarded_live_reconciliation(
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )

  if binding.binding_kind == "guarded_live_recovery":
    return asdict(
      app.recover_guarded_live_runtime_state(
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )

  if binding.binding_kind == "guarded_live_incident_acknowledge":
    return asdict(
      app.acknowledge_guarded_live_incident(
        event_id=resolved_path_params["event_id"],
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )

  if binding.binding_kind == "guarded_live_incident_remediate":
    return asdict(
      app.remediate_guarded_live_incident(
        event_id=resolved_path_params["event_id"],
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )

  if binding.binding_kind == "guarded_live_incident_escalate":
    return asdict(
      app.escalate_guarded_live_incident(
        event_id=resolved_path_params["event_id"],
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
        lineage_evidence_pack_id=resolved_payload.get("lineage_evidence_pack_id"),
        lineage_evidence_retention_expires_at=resolved_payload.get(
          "lineage_evidence_retention_expires_at"
        ),
        lineage_evidence_summary=resolved_payload.get("lineage_evidence_summary"),
      )
    )

  if binding.binding_kind == "guarded_live_resume":
    run = app.resume_guarded_live_run(
      actor=resolved_payload["actor"],
      reason=resolved_payload["reason"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())

  if binding.binding_kind == "run_stop_sandbox":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.stop_sandbox_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())

  if binding.binding_kind == "run_stop_paper":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.stop_paper_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())

  if binding.binding_kind == "run_stop_live":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.stop_live_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())

  if binding.binding_kind == "run_live_order_cancel":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.cancel_live_order(
      run_id=run_id,
      order_id=resolved_path_params["order_id"],
      actor=resolved_payload["actor"],
      reason=resolved_payload["reason"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())

  if binding.binding_kind == "run_live_order_replace":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.replace_live_order(
      run_id=run_id,
      order_id=resolved_path_params["order_id"],
      price=resolved_payload["price"],
      quantity=resolved_payload.get("quantity"),
      actor=resolved_payload["actor"],
      reason=resolved_payload["reason"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())

  if binding.binding_kind == "run_subresource":
    if binding.subresource_key is None:
      raise ValueError(f"Standalone surface binding is missing subresource metadata: {binding.surface_key}")
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.get_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    return serialize_run_subresource_response(
      run,
      subresource_key=binding.subresource_key,
      capabilities=app.get_run_surface_capabilities(),
    )

  return UNHANDLED
