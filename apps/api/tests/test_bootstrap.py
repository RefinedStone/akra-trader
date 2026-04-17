from __future__ import annotations

from pathlib import Path

from akra_trader.adapters.in_memory import SeededMarketDataAdapter
from akra_trader.bootstrap import build_container
from akra_trader.bootstrap import build_default_market_data_database_url
from akra_trader.bootstrap import build_default_runs_database_url
from akra_trader.bootstrap import build_venue_execution_adapter
from akra_trader.config import Settings


def test_build_container_uses_configured_runs_database_url(monkeypatch) -> None:
  captured: dict[str, str] = {}

  class FakeRunRepository:
    def __init__(self, database_url: str) -> None:
      captured["database_url"] = database_url

  class FakeGuardedLiveRepository:
    def __init__(self, database_url: str) -> None:
      captured["guarded_live_database_url"] = database_url

  monkeypatch.setattr("akra_trader.bootstrap.SqlAlchemyRunRepository", FakeRunRepository)
  monkeypatch.setattr("akra_trader.bootstrap.SqlAlchemyGuardedLiveStateRepository", FakeGuardedLiveRepository)

  build_container(
    Settings(
      runs_database_url="postgresql+psycopg://akra:akra@postgres:5432/akra_trader",
      market_data_provider="seeded",
    )
  )

  assert captured["database_url"] == "postgresql+psycopg://akra:akra@postgres:5432/akra_trader"
  assert captured["guarded_live_database_url"] == "postgresql+psycopg://akra:akra@postgres:5432/akra_trader"


def test_build_default_runs_database_url_points_to_local_sqlite() -> None:
  repo_root = Path(__file__).resolve().parents[2]

  database_url = build_default_runs_database_url(repo_root)

  assert database_url.startswith("sqlite:///")
  assert database_url.endswith("/.local/state/runs.sqlite3")


def test_build_default_market_data_database_url_points_to_local_sqlite() -> None:
  repo_root = Path(__file__).resolve().parents[2]

  database_url = build_default_market_data_database_url(repo_root)

  assert database_url.startswith("sqlite:///")
  assert database_url.endswith("/.local/state/market-data.sqlite3")


def test_build_container_uses_seeded_provider_when_requested(monkeypatch) -> None:
  class FakeRunRepository:
    def __init__(self, database_url: str) -> None:
      self.database_url = database_url

  class FakeGuardedLiveRepository:
    def __init__(self, database_url: str) -> None:
      self.database_url = database_url

  class FakeSandboxWorkerSessionsJob:
    def __init__(self, application, *, interval_seconds: int) -> None:
      self._application = application
      self._interval_seconds = interval_seconds

    async def start(self) -> None:
      return None

    async def stop(self) -> None:
      return None

  monkeypatch.setattr("akra_trader.bootstrap.SqlAlchemyRunRepository", FakeRunRepository)
  monkeypatch.setattr("akra_trader.bootstrap.SqlAlchemyGuardedLiveStateRepository", FakeGuardedLiveRepository)
  monkeypatch.setattr("akra_trader.bootstrap.SandboxWorkerSessionsJob", FakeSandboxWorkerSessionsJob)

  container = build_container(Settings(market_data_provider="seeded"))

  assert isinstance(container.app._market_data, SeededMarketDataAdapter)
  assert len(container.background_jobs) == 1


def test_build_container_adds_guarded_live_worker_job_when_enabled(monkeypatch) -> None:
  captured: dict[str, str] = {}

  class FakeRunRepository:
    def __init__(self, database_url: str) -> None:
      self.database_url = database_url

  class FakeGuardedLiveRepository:
    def __init__(self, database_url: str) -> None:
      self.database_url = database_url

  class FakeSandboxWorkerSessionsJob:
    def __init__(self, application, *, interval_seconds: int) -> None:
      captured["sandbox_interval_seconds"] = str(interval_seconds)
      self._application = application

    async def start(self) -> None:
      return None

    async def stop(self) -> None:
      return None

  class FakeGuardedLiveWorkerSessionsJob:
    def __init__(self, application, *, interval_seconds: int) -> None:
      captured["guarded_live_interval_seconds"] = str(interval_seconds)
      self._application = application

    async def start(self) -> None:
      return None

    async def stop(self) -> None:
      return None

  monkeypatch.setattr("akra_trader.bootstrap.SqlAlchemyRunRepository", FakeRunRepository)
  monkeypatch.setattr("akra_trader.bootstrap.SqlAlchemyGuardedLiveStateRepository", FakeGuardedLiveRepository)
  monkeypatch.setattr("akra_trader.bootstrap.SandboxWorkerSessionsJob", FakeSandboxWorkerSessionsJob)
  monkeypatch.setattr("akra_trader.bootstrap.GuardedLiveWorkerSessionsJob", FakeGuardedLiveWorkerSessionsJob)

  container = build_container(
    Settings(
      market_data_provider="seeded",
      guarded_live_execution_enabled=True,
      sandbox_worker_heartbeat_interval_seconds=11,
      guarded_live_worker_heartbeat_interval_seconds=19,
    )
  )

  assert len(container.background_jobs) == 2
  assert captured["sandbox_interval_seconds"] == "11"
  assert captured["guarded_live_interval_seconds"] == "19"


def test_build_container_reuses_runs_database_for_binance_market_data(monkeypatch) -> None:
  captured: dict[str, str] = {}

  class FakeRunRepository:
    def __init__(self, database_url: str) -> None:
      self.database_url = database_url

  class FakeGuardedLiveRepository:
    def __init__(self, database_url: str) -> None:
      captured["guarded_live_database_url"] = database_url

  class FakeBinanceVenueStateAdapter:
    def __init__(
      self,
      *,
      tracked_symbols: tuple[str, ...],
      api_key: str | None,
      api_secret: str | None,
      venue: str = "binance",
    ) -> None:
      captured["venue_state_symbols"] = ",".join(tracked_symbols)
      captured["venue_state_api_key"] = api_key or ""
      captured["venue_state_api_secret"] = api_secret or ""
      captured["venue_state_venue"] = venue

  class FakeBinanceMarketDataAdapter:
    def __init__(
      self,
      *,
      database_url: str,
      tracked_symbols: tuple[str, ...],
      default_candle_limit: int,
      historical_candle_limit: int,
    ) -> None:
      captured["database_url"] = database_url
      captured["tracked_symbols"] = ",".join(tracked_symbols)
      captured["default_candle_limit"] = str(default_candle_limit)
      captured["historical_candle_limit"] = str(historical_candle_limit)

  class FakeMarketDataSyncJob:
    def __init__(self, market_data, *, timeframes: tuple[str, ...], interval_seconds: int) -> None:
      captured["sync_timeframes"] = ",".join(timeframes)
      captured["sync_interval_seconds"] = str(interval_seconds)
      self._market_data = market_data

    async def start(self) -> None:
      return None

    async def stop(self) -> None:
      return None

  class FakeSandboxWorkerSessionsJob:
    def __init__(self, application, *, interval_seconds: int) -> None:
      captured["sandbox_interval_seconds"] = str(interval_seconds)
      self._application = application

    async def start(self) -> None:
      return None

    async def stop(self) -> None:
      return None

  monkeypatch.setattr("akra_trader.bootstrap.SqlAlchemyRunRepository", FakeRunRepository)
  monkeypatch.setattr("akra_trader.bootstrap.SqlAlchemyGuardedLiveStateRepository", FakeGuardedLiveRepository)
  monkeypatch.setattr("akra_trader.bootstrap.BinanceMarketDataAdapter", FakeBinanceMarketDataAdapter)
  monkeypatch.setattr("akra_trader.bootstrap.BinanceVenueStateAdapter", FakeBinanceVenueStateAdapter)
  monkeypatch.setattr("akra_trader.bootstrap.MarketDataSyncJob", FakeMarketDataSyncJob)
  monkeypatch.setattr("akra_trader.bootstrap.SandboxWorkerSessionsJob", FakeSandboxWorkerSessionsJob)

  container = build_container(
    Settings(
      runs_database_url="postgresql+psycopg://akra:akra@postgres:5432/akra_trader",
      market_data_provider="binance",
      market_data_symbols=("BTC/USDT",),
      market_data_sync_timeframes=("5m", "1h"),
      market_data_sync_interval_seconds=120,
      market_data_default_candle_limit=144,
      market_data_historical_candle_limit=720,
      sandbox_worker_heartbeat_interval_seconds=11,
      binance_api_key="test-key",
      binance_api_secret="test-secret",
    )
  )

  assert captured["database_url"] == "postgresql+psycopg://akra:akra@postgres:5432/akra_trader"
  assert captured["guarded_live_database_url"] == "postgresql+psycopg://akra:akra@postgres:5432/akra_trader"
  assert captured["tracked_symbols"] == "BTC/USDT"
  assert captured["venue_state_symbols"] == "BTC/USDT"
  assert captured["venue_state_api_key"] == "test-key"
  assert captured["venue_state_api_secret"] == "test-secret"
  assert captured["sync_timeframes"] == "5m,1h"
  assert captured["sync_interval_seconds"] == "120"
  assert captured["sandbox_interval_seconds"] == "11"
  assert captured["default_candle_limit"] == "144"
  assert captured["historical_candle_limit"] == "720"
  assert len(container.background_jobs) == 2


def test_build_venue_execution_adapter_passes_poll_interval(monkeypatch) -> None:
  captured: dict[str, object] = {}

  class FakeBinanceVenueExecutionAdapter:
    def __init__(self, **kwargs) -> None:
      captured.update(kwargs)

  monkeypatch.setattr("akra_trader.bootstrap.BinanceVenueExecutionAdapter", FakeBinanceVenueExecutionAdapter)

  adapter = build_venue_execution_adapter(
    Settings(
      market_data_provider="binance",
      binance_api_key="test-key",
      binance_api_secret="test-secret",
      guarded_live_venue_poll_interval_seconds=27,
    )
  )

  assert isinstance(adapter, FakeBinanceVenueExecutionAdapter)
  assert captured["api_key"] == "test-key"
  assert captured["api_secret"] == "test-secret"
  assert captured["poll_interval_seconds"] == 27
