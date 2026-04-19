from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Header
from fastapi import HTTPException
from fastapi import Query
from pydantic import BaseModel
from pydantic import Field

from akra_trader.application import list_standalone_surface_runtime_bindings
from akra_trader.application import TradingApplication
from akra_trader.application import execute_standalone_surface_binding
from akra_trader.application import get_standalone_surface_runtime_binding
from akra_trader.application import serialize_run_comparison
from akra_trader.application import serialize_run
from akra_trader.application import serialize_standalone_surface_response
from akra_trader.application import serialize_strategy
from akra_trader.application import serialize_preset
from akra_trader.application import serialize_preset_revision
from akra_trader.application import StandaloneSurfaceRuntimeBinding
from akra_trader.bootstrap import Container


class StrategyRegistrationRequest(BaseModel):
  strategy_id: str
  module_path: str
  class_name: str


class ExperimentPresetRequest(BaseModel):
  name: str
  preset_id: str | None = None
  description: str = ""
  strategy_id: str | None = None
  timeframe: str | None = None
  tags: list[str] = Field(default_factory=list)
  parameters: dict[str, Any] = Field(default_factory=dict)
  benchmark_family: str | None = None


class ExperimentPresetLifecycleActionRequest(BaseModel):
  action: str
  actor: str = "operator"
  reason: str = "manual_preset_lifecycle_action"


class ExperimentPresetUpdateRequest(BaseModel):
  name: str | None = None
  description: str | None = None
  strategy_id: str | None = None
  timeframe: str | None = None
  tags: list[str] | None = None
  parameters: dict[str, Any] | None = None
  benchmark_family: str | None = None
  actor: str = "operator"
  reason: str = "manual_preset_edit"


class ExperimentPresetRevisionRestoreRequest(BaseModel):
  actor: str = "operator"
  reason: str = "manual_preset_revision_restore"


class BacktestRequest(BaseModel):
  strategy_id: str
  symbol: str
  timeframe: str = "5m"
  initial_cash: float = 10_000
  fee_rate: float = 0.001
  slippage_bps: float = 3
  parameters: dict[str, Any] = Field(default_factory=dict)
  start_at: datetime | None = None
  end_at: datetime | None = None
  tags: list[str] = Field(default_factory=list)
  preset_id: str | None = None
  benchmark_family: str | None = None


class SandboxRunRequest(BaseModel):
  strategy_id: str
  symbol: str
  timeframe: str = "5m"
  initial_cash: float = 10_000
  fee_rate: float = 0.001
  slippage_bps: float = 3
  replay_bars: int = 96
  parameters: dict[str, Any] = Field(default_factory=dict)
  tags: list[str] = Field(default_factory=list)
  preset_id: str | None = None
  benchmark_family: str | None = None


class LiveRunRequest(BaseModel):
  strategy_id: str
  symbol: str
  timeframe: str = "5m"
  initial_cash: float = 10_000
  fee_rate: float = 0.001
  slippage_bps: float = 3
  replay_bars: int = 96
  operator_reason: str = "guarded_live_launch"
  parameters: dict[str, Any] = Field(default_factory=dict)
  tags: list[str] = Field(default_factory=list)
  preset_id: str | None = None
  benchmark_family: str | None = None


class GuardedLiveActionRequest(BaseModel):
  actor: str = "operator"
  reason: str = "manual_operator_action"


class GuardedLiveOrderReplaceRequest(GuardedLiveActionRequest):
  price: float = Field(gt=0)
  quantity: float | None = Field(default=None, gt=0)


class ExternalIncidentSyncRequest(BaseModel):
  provider: str
  event_kind: str
  actor: str = "external"
  detail: str = "external_incident_sync"
  alert_id: str | None = None
  external_reference: str | None = None
  workflow_reference: str | None = None
  occurred_at: datetime | None = None
  escalation_level: int | None = Field(default=None, ge=1)
  payload: dict[str, Any] = Field(default_factory=dict)

def create_router(container: Container) -> APIRouter:
  router = APIRouter()

  def get_app() -> TradingApplication:
    return container.app

  def serialize_run_response(run: Any, app: TradingApplication) -> dict[str, Any]:
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())

  def serialize_run_comparison_response(
    comparison: Any,
    app: TradingApplication,
  ) -> dict[str, Any]:
    return serialize_run_comparison(
      comparison,
      capabilities=app.get_run_surface_capabilities(),
    )

  def build_standalone_surface_route_handler(binding: StandaloneSurfaceRuntimeBinding):
    def dispatch_binding(
      *,
      app: TradingApplication,
      run_id: str | None = None,
      filters: dict[str, Any] | None = None,
      request_payload: dict[str, Any] | None = None,
      path_params: dict[str, Any] | None = None,
      headers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
      try:
        return execute_standalone_surface_binding(
          binding=binding,
          app=app,
          run_id=run_id,
          filters=filters,
          request_payload=request_payload,
          path_params=path_params,
          headers=headers,
        )
      except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
      except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
      except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if binding.scope == "app":
      def get_app_surface(
        app: TradingApplication = Depends(get_app),
      ) -> dict[str, Any]:
        return dispatch_binding(app=app)

      get_app_surface.__name__ = binding.route_name
      return get_app_surface

    def get_run_surface(
      run_id: str,
      app: TradingApplication = Depends(get_app),
    ) -> dict[str, Any]:
      return dispatch_binding(app=app, run_id=run_id)

    get_run_surface.__name__ = binding.route_name
    return get_run_surface

  @router.get("/strategies")
  def list_strategies(
    lane: str | None = None,
    lifecycle_stage: str | None = None,
    version: str | None = None,
    app: TradingApplication = Depends(get_app),
  ) -> list[dict[str, Any]]:
    binding = get_standalone_surface_runtime_binding(
      "strategy_catalog_discovery",
      app.get_run_surface_capabilities(),
    )
    return serialize_standalone_surface_response(
      binding=binding,
      app=app,
      filters={
        "lane": lane,
        "lifecycle_stage": lifecycle_stage,
        "version": version,
      },
    )

  @router.get("/presets")
  def list_presets(
    strategy_id: str | None = None,
    timeframe: str | None = None,
    lifecycle_stage: str | None = None,
    app: TradingApplication = Depends(get_app),
  ) -> list[dict[str, Any]]:
    binding = get_standalone_surface_runtime_binding(
      "preset_catalog_discovery",
      app.get_run_surface_capabilities(),
    )
    return serialize_standalone_surface_response(
      binding=binding,
      app=app,
      filters={
        "strategy_id": strategy_id,
        "timeframe": timeframe,
        "lifecycle_stage": lifecycle_stage,
      },
    )

  @router.post("/presets")
  def create_preset(
    request: ExperimentPresetRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    binding = get_standalone_surface_runtime_binding(
      "preset_catalog_create",
      app.get_run_surface_capabilities(),
    )
    try:
      return execute_standalone_surface_binding(
        binding=binding,
        app=app,
        request_payload=request.model_dump(),
      )
    except (ValueError, RuntimeError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  @router.get("/presets/{preset_id}")
  def get_preset(
    preset_id: str,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      preset = app.get_preset(preset_id=preset_id)
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    return serialize_preset(preset)

  @router.patch("/presets/{preset_id}")
  def update_preset(
    preset_id: str,
    request: ExperimentPresetUpdateRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    changes = request.model_dump(
      exclude={"actor", "reason"},
      exclude_unset=True,
    )
    try:
      preset = app.update_preset(
        preset_id=preset_id,
        changes=changes,
        actor=request.actor,
        reason=request.reason,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    return serialize_preset(preset)

  @router.get("/presets/{preset_id}/revisions")
  def list_preset_revisions(
    preset_id: str,
    app: TradingApplication = Depends(get_app),
  ) -> list[dict[str, Any]]:
    try:
      revisions = app.list_preset_revisions(preset_id=preset_id)
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [serialize_preset_revision(revision) for revision in revisions]

  @router.post("/presets/{preset_id}/revisions/{revision_id}/restore")
  def restore_preset_revision(
    preset_id: str,
    revision_id: str,
    request: ExperimentPresetRevisionRestoreRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      preset = app.restore_preset_revision(
        preset_id=preset_id,
        revision_id=revision_id,
        actor=request.actor,
        reason=request.reason,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    return serialize_preset(preset)

  @router.post("/presets/{preset_id}/lifecycle")
  def apply_preset_lifecycle_action(
    preset_id: str,
    request: ExperimentPresetLifecycleActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      preset = app.apply_preset_lifecycle_action(
        preset_id=preset_id,
        action=request.action,
        actor=request.actor,
        reason=request.reason,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    return serialize_preset(preset)

  @router.post("/strategies/register")
  def register_strategy(
    request: StrategyRegistrationRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    binding = get_standalone_surface_runtime_binding(
      "strategy_catalog_register",
      app.get_run_surface_capabilities(),
    )
    try:
      return execute_standalone_surface_binding(
        binding=binding,
        app=app,
        request_payload=request.model_dump(),
      )
    except (ValueError, RuntimeError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  @router.get("/runs")
  def list_runs(
    mode: str | None = None,
    strategy_id: str | None = None,
    strategy_version: str | None = None,
    rerun_boundary_id: str | None = None,
    preset_id: str | None = None,
    benchmark_family: str | None = None,
    dataset_identity: str | None = None,
    tag: list[str] = Query(default_factory=list),
    app: TradingApplication = Depends(get_app),
  ) -> list[dict[str, Any]]:
    return [
      serialize_run_response(run, app)
      for run in app.list_runs(
        mode=mode,
        strategy_id=strategy_id,
        strategy_version=strategy_version,
        rerun_boundary_id=rerun_boundary_id,
        preset_id=preset_id,
        benchmark_family=benchmark_family,
        dataset_identity=dataset_identity,
        tags=tag,
      )
    ]

  @router.get("/runs/compare")
  def compare_runs(
    run_id: list[str] = Query(default_factory=list),
    intent: str | None = None,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      comparison = app.compare_runs(run_ids=run_id, intent=intent)
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    return serialize_run_comparison_response(comparison, app)

  @router.post("/runs/backtests")
  def run_backtest(request: BacktestRequest, app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    try:
      run = app.run_backtest(
        strategy_id=request.strategy_id,
        symbol=request.symbol,
        timeframe=request.timeframe,
        initial_cash=request.initial_cash,
        fee_rate=request.fee_rate,
        slippage_bps=request.slippage_bps,
        parameters=request.parameters,
        start_at=request.start_at,
        end_at=request.end_at,
        tags=request.tags,
        preset_id=request.preset_id,
        benchmark_family=request.benchmark_family,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_run_response(run, app)

  @router.get("/runs/backtests/{run_id}")
  def get_backtest_run(run_id: str, app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    run = app.get_run(run_id)
    if run is None:
      raise HTTPException(status_code=404, detail="Run not found")
    return serialize_run_response(run, app)

  @router.post("/runs/rerun-boundaries/{rerun_boundary_id}/backtests")
  def rerun_backtest_from_boundary(
    rerun_boundary_id: str,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      run = app.rerun_backtest_from_boundary(rerun_boundary_id=rerun_boundary_id)
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    return serialize_run_response(run, app)

  @router.post("/runs/rerun-boundaries/{rerun_boundary_id}/sandbox")
  def rerun_sandbox_from_boundary(
    rerun_boundary_id: str,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      run = app.rerun_sandbox_from_boundary(rerun_boundary_id=rerun_boundary_id)
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    return serialize_run_response(run, app)

  @router.post("/runs/rerun-boundaries/{rerun_boundary_id}/paper")
  def rerun_paper_from_boundary(
    rerun_boundary_id: str,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      run = app.rerun_paper_from_boundary(rerun_boundary_id=rerun_boundary_id)
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    return serialize_run_response(run, app)

  @router.post("/runs/sandbox")
  def start_sandbox_run(
    request: SandboxRunRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      run = app.start_sandbox_run(
        strategy_id=request.strategy_id,
        symbol=request.symbol,
        timeframe=request.timeframe,
        initial_cash=request.initial_cash,
        fee_rate=request.fee_rate,
        slippage_bps=request.slippage_bps,
        parameters=request.parameters,
        replay_bars=request.replay_bars,
        tags=request.tags,
        preset_id=request.preset_id,
        benchmark_family=request.benchmark_family,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_run_response(run, app)

  @router.post("/runs/sandbox/{run_id}/stop")
  def stop_sandbox_run(run_id: str, app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    try:
      run = app.stop_sandbox_run(run_id)
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    if run is None:
      raise HTTPException(status_code=404, detail="Run not found")
    return serialize_run_response(run, app)

  @router.post("/runs/paper")
  def start_paper_run(
    request: SandboxRunRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      run = app.start_paper_run(
        strategy_id=request.strategy_id,
        symbol=request.symbol,
        timeframe=request.timeframe,
        initial_cash=request.initial_cash,
        fee_rate=request.fee_rate,
        slippage_bps=request.slippage_bps,
        parameters=request.parameters,
        replay_bars=request.replay_bars,
        tags=request.tags,
        preset_id=request.preset_id,
        benchmark_family=request.benchmark_family,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_run_response(run, app)

  @router.post("/runs/paper/{run_id}/stop")
  def stop_paper_run(run_id: str, app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    try:
      run = app.stop_paper_run(run_id)
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    if run is None:
      raise HTTPException(status_code=404, detail="Run not found")
    return serialize_run_response(run, app)

  @router.post("/runs/live")
  def start_live_run(
    request: LiveRunRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      run = app.start_live_run(
        strategy_id=request.strategy_id,
        symbol=request.symbol,
        timeframe=request.timeframe,
        initial_cash=request.initial_cash,
        fee_rate=request.fee_rate,
        slippage_bps=request.slippage_bps,
          parameters=request.parameters,
          replay_bars=request.replay_bars,
          operator_reason=request.operator_reason,
          tags=request.tags,
          preset_id=request.preset_id,
          benchmark_family=request.benchmark_family,
        )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_run_response(run, app)

  @router.post("/runs/live/{run_id}/stop")
  def stop_live_run(run_id: str, app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    try:
      run = app.stop_live_run(run_id)
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    if run is None:
      raise HTTPException(status_code=404, detail="Run not found")
    return serialize_run_response(run, app)

  @router.post("/runs/live/{run_id}/orders/{order_id}/cancel")
  def cancel_live_order(
    run_id: str,
    order_id: str,
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      run = app.cancel_live_order(
        run_id=run_id,
        order_id=order_id,
        actor=request.actor,
        reason=request.reason,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, RuntimeError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_run_response(run, app)

  @router.post("/runs/live/{run_id}/orders/{order_id}/replace")
  def replace_live_order(
    run_id: str,
    order_id: str,
    request: GuardedLiveOrderReplaceRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      run = app.replace_live_order(
        run_id=run_id,
        order_id=order_id,
        price=request.price,
        quantity=request.quantity,
        actor=request.actor,
        reason=request.reason,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, RuntimeError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_run_response(run, app)

  for binding in list_standalone_surface_runtime_bindings(get_app().get_run_surface_capabilities()):
    if (
      binding.scope == "app"
      and (
        binding.filter_keys
        or binding.request_payload_kind is not None
        or binding.path_param_keys
        or binding.header_keys
      )
    ):
      continue
    router.add_api_route(
      binding.route_path,
      build_standalone_surface_route_handler(binding),
      methods=list(binding.methods),
      name=binding.route_name,
      summary=binding.response_title,
    )

  @router.get("/market-data/status")
  def get_market_data_status(timeframe: str = "5m", app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    binding = get_standalone_surface_runtime_binding(
      "market_data_status",
      app.get_run_surface_capabilities(),
    )
    return serialize_standalone_surface_response(
      binding=binding,
      app=app,
      filters={"timeframe": timeframe},
    )

  @router.post("/operator/incidents/external-sync")
  def sync_external_incident(
    request: ExternalIncidentSyncRequest,
    x_akra_incident_sync_token: str | None = Header(default=None, alias="X-Akra-Incident-Sync-Token"),
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    binding = get_standalone_surface_runtime_binding(
      "operator_incident_external_sync",
      app.get_run_surface_capabilities(),
    )
    try:
      return execute_standalone_surface_binding(
        binding=binding,
        app=app,
        request_payload=request.model_dump(),
        headers={"x_akra_incident_sync_token": x_akra_incident_sync_token},
      )
    except PermissionError as exc:
      raise HTTPException(status_code=403, detail=str(exc)) from exc
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  @router.post("/guarded-live/kill-switch/engage")
  def engage_guarded_live_kill_switch(
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    binding = get_standalone_surface_runtime_binding(
      "guarded_live_kill_switch_engage",
      app.get_run_surface_capabilities(),
    )
    return execute_standalone_surface_binding(
      binding=binding,
      app=app,
      request_payload=request.model_dump(),
    )

  @router.post("/guarded-live/kill-switch/release")
  def release_guarded_live_kill_switch(
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    binding = get_standalone_surface_runtime_binding(
      "guarded_live_kill_switch_release",
      app.get_run_surface_capabilities(),
    )
    return execute_standalone_surface_binding(
      binding=binding,
      app=app,
      request_payload=request.model_dump(),
    )

  @router.post("/guarded-live/reconciliation")
  def run_guarded_live_reconciliation(
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    binding = get_standalone_surface_runtime_binding(
      "guarded_live_reconciliation",
      app.get_run_surface_capabilities(),
    )
    return execute_standalone_surface_binding(
      binding=binding,
      app=app,
      request_payload=request.model_dump(),
    )

  @router.post("/guarded-live/recovery")
  def recover_guarded_live_runtime_state(
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    binding = get_standalone_surface_runtime_binding(
      "guarded_live_recovery",
      app.get_run_surface_capabilities(),
    )
    return execute_standalone_surface_binding(
      binding=binding,
      app=app,
      request_payload=request.model_dump(),
    )

  @router.post("/guarded-live/incidents/{event_id}/acknowledge")
  def acknowledge_guarded_live_incident(
    event_id: str,
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    binding = get_standalone_surface_runtime_binding(
      "guarded_live_incident_acknowledge",
      app.get_run_surface_capabilities(),
    )
    try:
      return execute_standalone_surface_binding(
        binding=binding,
        app=app,
        request_payload=request.model_dump(),
        path_params={"event_id": event_id},
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  @router.post("/guarded-live/incidents/{event_id}/remediate")
  def remediate_guarded_live_incident(
    event_id: str,
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    binding = get_standalone_surface_runtime_binding(
      "guarded_live_incident_remediate",
      app.get_run_surface_capabilities(),
    )
    try:
      return execute_standalone_surface_binding(
        binding=binding,
        app=app,
        request_payload=request.model_dump(),
        path_params={"event_id": event_id},
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  @router.post("/guarded-live/incidents/{event_id}/escalate")
  def escalate_guarded_live_incident(
    event_id: str,
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    binding = get_standalone_surface_runtime_binding(
      "guarded_live_incident_escalate",
      app.get_run_surface_capabilities(),
    )
    try:
      return execute_standalone_surface_binding(
        binding=binding,
        app=app,
        request_payload=request.model_dump(),
        path_params={"event_id": event_id},
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  @router.post("/guarded-live/resume")
  def resume_guarded_live_run(
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    binding = get_standalone_surface_runtime_binding(
      "guarded_live_resume",
      app.get_run_surface_capabilities(),
    )
    try:
      return execute_standalone_surface_binding(
        binding=binding,
        app=app,
        request_payload=request.model_dump(),
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, RuntimeError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  return router


def include_routes(app: FastAPI, container: Container, prefix: str) -> None:
  app.include_router(create_router(container), prefix=prefix)
