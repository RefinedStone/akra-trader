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

from akra_trader.application import TradingApplication
from akra_trader.application import serialize_run_comparison
from akra_trader.application import serialize_run
from akra_trader.application import serialize_strategy
from akra_trader.application import serialize_preset
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
  benchmark_family: str | None = None


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

  @router.get("/health")
  def health() -> dict[str, str]:
    return {"status": "ok"}

  @router.get("/strategies")
  def list_strategies(
    lane: str | None = None,
    lifecycle_stage: str | None = None,
    version: str | None = None,
    app: TradingApplication = Depends(get_app),
  ) -> list[dict[str, Any]]:
    return [
      serialize_strategy(strategy)
      for strategy in app.list_strategies(
        lane=lane,
        lifecycle_stage=lifecycle_stage,
        version=version,
      )
    ]

  @router.get("/references")
  def list_references(app: TradingApplication = Depends(get_app)) -> list[dict[str, Any]]:
    return [asdict(reference) for reference in app.list_references()]

  @router.get("/presets")
  def list_presets(
    strategy_id: str | None = None,
    timeframe: str | None = None,
    app: TradingApplication = Depends(get_app),
  ) -> list[dict[str, Any]]:
    return [
      serialize_preset(preset)
      for preset in app.list_presets(strategy_id=strategy_id, timeframe=timeframe)
    ]

  @router.post("/presets")
  def create_preset(
    request: ExperimentPresetRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      preset = app.create_preset(
        name=request.name,
        preset_id=request.preset_id,
        description=request.description,
        strategy_id=request.strategy_id,
        timeframe=request.timeframe,
        tags=request.tags,
        benchmark_family=request.benchmark_family,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_preset(preset)

  @router.post("/strategies/register")
  def register_strategy(
    request: StrategyRegistrationRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    metadata = app.register_strategy(
      strategy_id=request.strategy_id,
      module_path=request.module_path,
      class_name=request.class_name,
    )
    return serialize_strategy(metadata)

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
      serialize_run(run)
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
    return serialize_run_comparison(comparison)

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
    return serialize_run(run)

  @router.get("/runs/backtests/{run_id}")
  def get_backtest_run(run_id: str, app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    run = app.get_run(run_id)
    if run is None:
      raise HTTPException(status_code=404, detail="Run not found")
    return serialize_run(run)

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
    return serialize_run(run)

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
    return serialize_run(run)

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
    return serialize_run(run)

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
    return serialize_run(run)

  @router.post("/runs/sandbox/{run_id}/stop")
  def stop_sandbox_run(run_id: str, app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    run = app.stop_sandbox_run(run_id)
    if run is None:
      raise HTTPException(status_code=404, detail="Run not found")
    return serialize_run(run)

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
    return serialize_run(run)

  @router.post("/runs/paper/{run_id}/stop")
  def stop_paper_run(run_id: str, app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    run = app.stop_paper_run(run_id)
    if run is None:
      raise HTTPException(status_code=404, detail="Run not found")
    return serialize_run(run)

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
    return serialize_run(run)

  @router.post("/runs/live/{run_id}/stop")
  def stop_live_run(run_id: str, app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    run = app.stop_live_run(run_id)
    if run is None:
      raise HTTPException(status_code=404, detail="Run not found")
    return serialize_run(run)

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
    return serialize_run(run)

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
    return serialize_run(run)

  @router.get("/runs/{run_id}/orders")
  def get_run_orders(run_id: str, app: TradingApplication = Depends(get_app)) -> list[dict[str, Any]]:
    run = app.get_run(run_id)
    if run is None:
      raise HTTPException(status_code=404, detail="Run not found")
    return [asdict(order) for order in run.orders]

  @router.get("/runs/{run_id}/positions")
  def get_run_positions(run_id: str, app: TradingApplication = Depends(get_app)) -> list[dict[str, Any]]:
    run = app.get_run(run_id)
    if run is None:
      raise HTTPException(status_code=404, detail="Run not found")
    return [asdict(position) for position in run.positions.values()]

  @router.get("/runs/{run_id}/metrics")
  def get_run_metrics(run_id: str, app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    run = app.get_run(run_id)
    if run is None:
      raise HTTPException(status_code=404, detail="Run not found")
    return run.metrics

  @router.get("/market-data/status")
  def get_market_data_status(timeframe: str = "5m", app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    status = app.get_market_data_status(timeframe)
    return asdict(status)

  @router.get("/operator/visibility")
  def get_operator_visibility(app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    visibility = app.get_operator_visibility()
    return asdict(visibility)

  @router.post("/operator/incidents/external-sync")
  def sync_external_incident(
    request: ExternalIncidentSyncRequest,
    x_akra_incident_sync_token: str | None = Header(default=None, alias="X-Akra-Incident-Sync-Token"),
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      app.require_operator_alert_external_sync_token(x_akra_incident_sync_token)
      status = app.sync_guarded_live_incident_from_external(
        provider=request.provider,
        event_kind=request.event_kind,
        actor=request.actor,
        detail=request.detail,
        alert_id=request.alert_id,
        external_reference=request.external_reference,
        workflow_reference=request.workflow_reference,
        occurred_at=request.occurred_at,
        escalation_level=request.escalation_level,
        payload=request.payload,
      )
    except PermissionError as exc:
      raise HTTPException(status_code=403, detail=str(exc)) from exc
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return asdict(status)

  @router.get("/guarded-live")
  def get_guarded_live_status(app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    status = app.get_guarded_live_status()
    return asdict(status)

  @router.post("/guarded-live/kill-switch/engage")
  def engage_guarded_live_kill_switch(
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    status = app.engage_guarded_live_kill_switch(actor=request.actor, reason=request.reason)
    return asdict(status)

  @router.post("/guarded-live/kill-switch/release")
  def release_guarded_live_kill_switch(
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    status = app.release_guarded_live_kill_switch(actor=request.actor, reason=request.reason)
    return asdict(status)

  @router.post("/guarded-live/reconciliation")
  def run_guarded_live_reconciliation(
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    status = app.run_guarded_live_reconciliation(actor=request.actor, reason=request.reason)
    return asdict(status)

  @router.post("/guarded-live/recovery")
  def recover_guarded_live_runtime_state(
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    status = app.recover_guarded_live_runtime_state(actor=request.actor, reason=request.reason)
    return asdict(status)

  @router.post("/guarded-live/incidents/{event_id}/acknowledge")
  def acknowledge_guarded_live_incident(
    event_id: str,
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      status = app.acknowledge_guarded_live_incident(
        event_id=event_id,
        actor=request.actor,
        reason=request.reason,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return asdict(status)

  @router.post("/guarded-live/incidents/{event_id}/remediate")
  def remediate_guarded_live_incident(
    event_id: str,
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      status = app.remediate_guarded_live_incident(
        event_id=event_id,
        actor=request.actor,
        reason=request.reason,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return asdict(status)

  @router.post("/guarded-live/incidents/{event_id}/escalate")
  def escalate_guarded_live_incident(
    event_id: str,
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      status = app.escalate_guarded_live_incident(
        event_id=event_id,
        actor=request.actor,
        reason=request.reason,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return asdict(status)

  @router.post("/guarded-live/resume")
  def resume_guarded_live_run(
    request: GuardedLiveActionRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      run = app.resume_guarded_live_run(actor=request.actor, reason=request.reason)
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, RuntimeError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_run(run)

  return router


def include_routes(app: FastAPI, container: Container, prefix: str) -> None:
  app.include_router(create_router(container), prefix=prefix)
