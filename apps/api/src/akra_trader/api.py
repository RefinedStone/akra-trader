from __future__ import annotations

from dataclasses import fields
from dataclasses import is_dataclass
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from enum import Enum
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query
from pydantic import BaseModel
from pydantic import Field

from akra_trader.application import TradingApplication
from akra_trader.bootstrap import Container


class RunCreateRequest(BaseModel):
  strategy_id: str = Field(default="ma_cross_v1", min_length=1)
  symbol: str = Field(default="BTC/USDT", min_length=1)
  timeframe: str = Field(default="5m", min_length=1)
  initial_cash: float = Field(default=10_000.0, gt=0)
  fee_rate: float = Field(default=0.001, ge=0)
  slippage_bps: float = Field(default=5.0, ge=0)
  parameters: dict[str, Any] = Field(default_factory=dict)
  replay_bars: int | None = Field(default=96, ge=2, le=5_000)
  start_at: datetime | None = None
  end_at: datetime | None = None


class MarketDataSyncRequest(BaseModel):
  symbol: str = Field(default="BTC/USDT", min_length=1)
  timeframe: str = Field(default="5m", min_length=1)
  start_at: datetime | None = None
  end_at: datetime | None = None
  limit: int | None = Field(default=None, ge=1, le=200_000)


def create_router(container: Container) -> APIRouter:
  router = APIRouter()

  def get_app() -> TradingApplication:
    return container.app

  @router.get("/health")
  def health(app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    return app.health()

  @router.get("/strategies")
  def list_strategies(app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    return {
      "strategies": [_to_json(strategy) for strategy in app.list_strategies()],
      "llm_strategy": app.get_llm_strategy_interface(),
    }

  @router.get("/runs")
  def list_runs(
    mode: str | None = Query(default=None, pattern="^(backtest|sandbox|live)$"),
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return {"runs": [serialize_run(run) for run in app.list_runs(mode)]}

  @router.get("/runs/{run_id}")
  def get_run(run_id: str, app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    run = app.get_run(run_id)
    if run is None:
      raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
    return serialize_run(run)

  @router.post("/runs/backtests")
  def create_backtest(
    request: RunCreateRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      run = app.run_backtest(**_run_request_kwargs(request, include_replay_bars=False))
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_run(run)

  @router.post("/runs/sandbox")
  def create_sandbox(
    request: RunCreateRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      run = app.start_sandbox_run(**_run_request_kwargs(request, include_replay_bars=True))
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_run(run)

  @router.post("/runs/live")
  def create_live(
    request: RunCreateRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      run = app.start_live_run(**_run_request_kwargs(request, include_replay_bars=True))
    except PermissionError as exc:
      raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_run(run)

  @router.post("/runs/{run_id}/stop")
  def stop_run(run_id: str, app: TradingApplication = Depends(get_app)) -> dict[str, Any]:
    try:
      return serialize_run(app.stop_run(run_id))
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc

  @router.get("/runs/{run_id}/orders")
  def get_run_orders(
    run_id: str,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return {"run_id": run_id, "orders": _to_json(app.get_run_orders(run_id))}
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc

  @router.get("/runs/{run_id}/positions")
  def get_run_positions(
    run_id: str,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return {"run_id": run_id, "positions": _to_json(app.get_run_positions(run_id))}
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc

  @router.get("/runs/{run_id}/metrics")
  def get_run_metrics(
    run_id: str,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return {"run_id": run_id, "metrics": _to_json(app.get_run_metrics(run_id))}
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc

  @router.get("/runs/{run_id}/logs")
  def get_run_logs(
    run_id: str,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return {"run_id": run_id, "logs": _to_json(app.get_run_logs(run_id))}
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc

  @router.get("/runs/{run_id}/llm-judgements")
  def get_run_llm_judgements(
    run_id: str,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return {
        "run_id": run_id,
        "judgements": _to_json(app.get_run_llm_judgements(run_id)),
      }
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc

  @router.get("/market-data/candles")
  def list_market_data_candles(
    symbol: str = Query(..., min_length=1),
    timeframe: str = Query("5m", min_length=1),
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int | None = Query(default=None, ge=1, le=200_000),
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    aligned_start_at, aligned_end_at = _align_time_range(
      timeframe=timeframe.strip(),
      start_at=_ensure_utc(start_at),
      end_at=_ensure_utc(end_at),
    )
    effective_limit = limit
    if effective_limit is None and aligned_start_at is None:
      effective_limit = 500
    candles = app.get_market_data_candles(
      symbol=symbol.strip(),
      timeframe=timeframe.strip(),
      start_at=aligned_start_at,
      end_at=aligned_end_at,
      limit=effective_limit,
    )
    return {
      "symbol": symbol.strip(),
      "timeframe": timeframe.strip(),
      "limit": effective_limit,
      "candles": _to_json(candles),
    }

  @router.get("/market-data/status")
  def get_market_data_status(
    timeframe: str = Query("5m", min_length=1),
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return _to_json(app.get_market_data_status(timeframe=timeframe.strip()))

  @router.post("/market-data/sync")
  def sync_market_data(
    request: MarketDataSyncRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      aligned_start_at, aligned_end_at = _align_time_range(
        timeframe=request.timeframe.strip(),
        start_at=_ensure_utc(request.start_at),
        end_at=_ensure_utc(request.end_at),
      )
      return _to_json(
        app.sync_market_data(
          symbol=request.symbol.strip(),
          timeframe=request.timeframe.strip(),
          start_at=aligned_start_at,
          end_at=aligned_end_at,
          limit=request.limit,
        )
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  @router.get("/logs")
  def list_logs(
    run_id: str | None = None,
    mode: str | None = Query(default=None, pattern="^(backtest|sandbox|live)$"),
    severity: str | None = Query(default=None, pattern="^(info|warning|error)$"),
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = Query(default=200, ge=1, le=1_000),
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return {
      "logs": _to_json(
        app.list_operation_logs(
          run_id=run_id,
          mode=mode,
          severity=severity,
          since=_ensure_utc(since),
          until=_ensure_utc(until),
          limit=limit,
        )
      )
    }

  return router


def include_routes(app: FastAPI, container: Container, prefix: str) -> None:
  app.include_router(create_router(container), prefix=prefix)


def serialize_run(run) -> dict[str, Any]:
  return {
    "run_id": run.config.run_id,
    "mode": run.config.mode.value,
    "status": run.status.value,
    "started_at": _to_json(run.started_at),
    "ended_at": _to_json(run.ended_at),
    "config": _to_json(run.config),
    "strategy": _to_json(run.provenance.strategy),
    "runtime_session": _to_json(run.provenance.runtime_session),
    "market_data": _to_json(run.provenance.market_data),
    "metrics": _to_json(run.metrics),
    "orders_count": len(run.orders),
    "positions_count": len(run.positions),
    "notes": list(run.notes[-20:]),
  }


def _run_request_kwargs(
  request: RunCreateRequest,
  *,
  include_replay_bars: bool,
) -> dict[str, Any]:
  values = request.model_dump()
  values["start_at"], values["end_at"] = _align_time_range(
    timeframe=str(values["timeframe"]),
    start_at=_ensure_utc(values["start_at"]),
    end_at=_ensure_utc(values["end_at"]),
  )
  if not include_replay_bars:
    values.pop("replay_bars", None)
  return values


def _ensure_utc(value: datetime | None) -> datetime | None:
  if value is None:
    return None
  if value.tzinfo is None:
    return value.replace(tzinfo=UTC)
  return value.astimezone(UTC)


def _align_time_range(
  *,
  timeframe: str,
  start_at: datetime | None,
  end_at: datetime | None,
) -> tuple[datetime | None, datetime | None]:
  aligned_start = _align_datetime_to_timeframe(start_at, timeframe=timeframe, boundary="start")
  aligned_end = _align_datetime_to_timeframe(end_at, timeframe=timeframe, boundary="end")
  if aligned_start is not None and aligned_end is not None and aligned_end < aligned_start:
    aligned_end = aligned_start
  return aligned_start, aligned_end


def _align_datetime_to_timeframe(
  value: datetime | None,
  *,
  timeframe: str,
  boundary: str,
) -> datetime | None:
  if value is None:
    return None
  if timeframe.endswith("M"):
    return _align_datetime_to_month_boundary(value, timeframe=timeframe, boundary=boundary)
  if timeframe.endswith("w"):
    return _align_datetime_to_week_boundary(value, timeframe=timeframe, boundary=boundary)
  seconds = _timeframe_seconds(timeframe)
  if seconds is None:
    return value
  epoch = datetime(1970, 1, 1, tzinfo=UTC)
  offset = value - epoch
  interval = timedelta(seconds=seconds)
  remainder = offset % interval
  if remainder == timedelta(0):
    return value
  if boundary == "start":
    return value + (interval - remainder)
  return value - remainder


def _align_datetime_to_week_boundary(value: datetime, *, timeframe: str, boundary: str) -> datetime:
  amount = _timeframe_amount(timeframe)
  if amount is None:
    return value
  value = value.astimezone(UTC)
  epoch = datetime(1970, 1, 5, tzinfo=UTC)
  interval = timedelta(weeks=amount)
  remainder = (value - epoch) % interval
  if remainder == timedelta(0):
    return value
  if boundary == "start":
    return value + (interval - remainder)
  return value - remainder


def _align_datetime_to_month_boundary(value: datetime, *, timeframe: str, boundary: str) -> datetime:
  amount = _timeframe_amount(timeframe)
  if amount is None:
    return value
  value = value.astimezone(UTC)
  month_index = value.year * 12 + value.month - 1
  bucket_index = month_index - (month_index % amount)
  bucket_start = datetime(bucket_index // 12, bucket_index % 12 + 1, 1, tzinfo=UTC)
  if value == bucket_start:
    return value
  if boundary == "start":
    return _add_months(bucket_start, amount)
  return bucket_start


def _add_months(value: datetime, amount: int) -> datetime:
  month_index = value.year * 12 + value.month - 1 + amount
  return datetime(month_index // 12, month_index % 12 + 1, 1, tzinfo=UTC)


def _timeframe_amount(timeframe: str) -> int | None:
  try:
    amount = int(timeframe[:-1])
  except ValueError:
    return None
  return amount if amount > 0 else None


def _timeframe_seconds(timeframe: str) -> int | None:
  if len(timeframe) < 2:
    return None
  try:
    amount = int(timeframe[:-1])
  except ValueError:
    return None
  if amount <= 0:
    return None
  unit = timeframe[-1]
  if unit == "m":
    return amount * 60
  if unit == "h":
    return amount * 60 * 60
  if unit == "d":
    return amount * 24 * 60 * 60
  if unit == "w":
    return amount * 7 * 24 * 60 * 60
  if unit == "M":
    return amount * 30 * 24 * 60 * 60
  return None


def _to_json(value: Any) -> Any:
  if value is None or isinstance(value, str | int | float | bool):
    return value
  if isinstance(value, datetime):
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
  if isinstance(value, Enum):
    return value.value
  if is_dataclass(value):
    return {
      field.name: _to_json(getattr(value, field.name))
      for field in fields(value)
    }
  if isinstance(value, dict):
    return {str(key): _to_json(item) for key, item in value.items()}
  if isinstance(value, (list, tuple, set)):
    return [_to_json(item) for item in value]
  return value
