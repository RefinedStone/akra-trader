from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from akra_trader.adapters.binance import CcxtMarketDataAdapter
from akra_trader.adapters.core_storage import SqlAlchemyCoreRepository
from akra_trader.adapters.in_memory_catalogs import LocalStrategyCatalog
from akra_trader.adapters.in_memory_market_data import SeededMarketDataAdapter
from akra_trader.adapters.venue_execution_binance_adapter import BinanceVenueExecutionAdapter
from akra_trader.adapters.venue_execution_seeded_adapter import SeededVenueExecutionAdapter
from akra_trader.application import TradingApplication
from akra_trader.config import Settings
from akra_trader.guarded_live_workers import GuardedLiveWorkerSessionsJob
from akra_trader.sandbox_workers import SandboxWorkerSessionsJob


class AppLifecycle(Protocol):
  async def start(self) -> None: ...

  async def stop(self) -> None: ...


@dataclass
class Container:
  app: TradingApplication
  background_jobs: tuple[AppLifecycle, ...] = ()


def build_default_runs_database_url(repo_root: Path) -> str:
  database_path = (repo_root / ".local" / "state" / "core-runtime.sqlite3").resolve()
  return f"sqlite:///{database_path}"


def build_default_market_data_database_url(repo_root: Path) -> str:
  database_path = (repo_root / ".local" / "state" / "market-data.sqlite3").resolve()
  return f"sqlite:///{database_path}"


def resolve_guarded_live_venue(settings: Settings) -> str:
  return settings.guarded_live_venue or "binance"


def build_market_data_adapter(settings: Settings, repo_root: Path):
  provider = settings.market_data_provider.strip().lower()
  if provider == "seeded":
    return SeededMarketDataAdapter(venue="binance")
  if provider == "binance":
    return CcxtMarketDataAdapter(
      database_url=(
        settings.market_data_database_url
        or settings.runs_database_url
        or build_default_market_data_database_url(repo_root)
      ),
      venue="binance",
      tracked_symbols=settings.market_data_symbols,
      default_candle_limit=settings.market_data_default_candle_limit,
      historical_candle_limit=settings.market_data_historical_candle_limit,
    )
  raise ValueError(f"Unsupported market data provider: {settings.market_data_provider}")


def build_venue_execution_adapter(settings: Settings):
  provider = settings.market_data_provider.strip().lower()
  venue = resolve_guarded_live_venue(settings)
  if venue != "binance":
    raise ValueError(f"Unsupported guarded-live venue: {venue}")
  if provider == "seeded" and settings.guarded_live_venue is None:
    return SeededVenueExecutionAdapter(venue="binance")
  api_key, api_secret = _resolve_guarded_live_credentials(settings)
  return BinanceVenueExecutionAdapter(
    venue="binance",
    api_key=api_key,
    api_secret=api_secret,
  )


def build_container(settings: Settings | None = None) -> Container:
  app_settings = settings or Settings()
  repo_root = Path(__file__).resolve().parents[4]
  market_data = build_market_data_adapter(app_settings, repo_root)
  runs = SqlAlchemyCoreRepository(
    app_settings.runs_database_url or build_default_runs_database_url(repo_root)
  )
  strategies = LocalStrategyCatalog()
  venue_execution = build_venue_execution_adapter(app_settings)
  app = TradingApplication(
    market_data=market_data,
    strategies=strategies,
    runs=runs,
    venue_execution=venue_execution,
    guarded_live_venue=resolve_guarded_live_venue(app_settings),
    guarded_live_execution_enabled=app_settings.guarded_live_execution_enabled,
    sandbox_worker_heartbeat_interval_seconds=(
      app_settings.sandbox_worker_heartbeat_interval_seconds
    ),
    sandbox_worker_heartbeat_timeout_seconds=(
      app_settings.sandbox_worker_heartbeat_timeout_seconds
    ),
    guarded_live_worker_heartbeat_interval_seconds=(
      app_settings.guarded_live_worker_heartbeat_interval_seconds
    ),
    guarded_live_worker_heartbeat_timeout_seconds=(
      app_settings.guarded_live_worker_heartbeat_timeout_seconds
    ),
  )
  background_jobs: list[AppLifecycle] = [
    SandboxWorkerSessionsJob(
      app,
      interval_seconds=app_settings.sandbox_worker_heartbeat_interval_seconds,
    ),
    GuardedLiveWorkerSessionsJob(
      app,
      interval_seconds=app_settings.guarded_live_worker_heartbeat_interval_seconds,
    ),
  ]
  return Container(app=app, background_jobs=tuple(background_jobs))


def _resolve_guarded_live_credentials(settings: Settings) -> tuple[str | None, str | None]:
  if settings.guarded_live_api_key or settings.guarded_live_api_secret:
    return settings.guarded_live_api_key, settings.guarded_live_api_secret
  return settings.binance_api_key, settings.binance_api_secret
