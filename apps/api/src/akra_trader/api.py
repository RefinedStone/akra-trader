from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query
from pydantic import BaseModel
from pydantic import Field

from akra_trader.application import TradingApplication
from akra_trader.application import serialize_run_comparison
from akra_trader.application import serialize_run
from akra_trader.application import serialize_strategy
from akra_trader.bootstrap import Container


class StrategyRegistrationRequest(BaseModel):
  strategy_id: str
  module_path: str
  class_name: str


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


class SandboxRunRequest(BaseModel):
  strategy_id: str
  symbol: str
  timeframe: str = "5m"
  initial_cash: float = 10_000
  fee_rate: float = 0.001
  slippage_bps: float = 3
  replay_bars: int = 96
  parameters: dict[str, Any] = Field(default_factory=dict)


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
    app: TradingApplication = Depends(get_app),
  ) -> list[dict[str, Any]]:
    return [
      serialize_run(run)
      for run in app.list_runs(
        mode=mode,
        strategy_id=strategy_id,
        strategy_version=strategy_version,
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
    )
    return serialize_run(run)

  @router.get("/runs/backtests/{run_id}")
  def get_backtest_run(run_id: str, app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    run = app.get_run(run_id)
    if run is None:
      raise HTTPException(status_code=404, detail="Run not found")
    return serialize_run(run)

  @router.post("/runs/sandbox")
  def start_sandbox_run(
    request: SandboxRunRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    run = app.start_sandbox_run(
      strategy_id=request.strategy_id,
      symbol=request.symbol,
      timeframe=request.timeframe,
      initial_cash=request.initial_cash,
      fee_rate=request.fee_rate,
      slippage_bps=request.slippage_bps,
      parameters=request.parameters,
      replay_bars=request.replay_bars,
    )
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
    return start_sandbox_run(request, app)

  @router.post("/runs/paper/{run_id}/stop")
  def stop_paper_run(run_id: str, app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    return stop_sandbox_run(run_id, app)

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

  return router


def include_routes(app: FastAPI, container: Container, prefix: str) -> None:
  app.include_router(create_router(container), prefix=prefix)
