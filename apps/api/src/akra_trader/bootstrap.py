from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from akra_trader.adapters.binance import CcxtMarketDataAdapter
from akra_trader.adapters.binance import SUPPORTED_CCXT_MARKET_DATA_VENUES
from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter
from akra_trader.adapters.guarded_live import SqlAlchemyGuardedLiveStateRepository
from akra_trader.adapters.in_memory import LocalStrategyCatalog
from akra_trader.adapters.operator_delivery import OperatorAlertDeliveryAdapter
from akra_trader.adapters.references import load_reference_catalog
from akra_trader.adapters.in_memory import SeededMarketDataAdapter
from akra_trader.adapters.sqlalchemy import SqlAlchemyRunRepository
from akra_trader.adapters.venue_execution import BinanceVenueExecutionAdapter
from akra_trader.adapters.venue_execution import SeededVenueExecutionAdapter
from akra_trader.adapters.venue_state import CcxtVenueStateAdapter
from akra_trader.adapters.venue_state import SeededVenueStateAdapter
from akra_trader.application import TradingApplication
from akra_trader.config import Settings
from akra_trader.guarded_live_workers import GuardedLiveWorkerSessionsJob
from akra_trader.market_data_sync import MarketDataSyncJob
from akra_trader.sandbox_workers import SandboxWorkerSessionsJob


class AppLifecycle(Protocol):
  async def start(self) -> None: ...

  async def stop(self) -> None: ...


@dataclass
class Container:
  app: TradingApplication
  background_jobs: tuple[AppLifecycle, ...] = ()


def resolve_guarded_live_venue(settings: Settings) -> str:
  if settings.guarded_live_venue:
    return settings.guarded_live_venue
  if settings.market_data_provider == "seeded":
    return "binance"
  return settings.market_data_provider


def _use_seeded_guarded_live_adapters(settings: Settings) -> bool:
  return settings.market_data_provider == "seeded" and settings.guarded_live_venue is None


def _resolve_guarded_live_credentials(settings: Settings, *, venue: str) -> tuple[str | None, str | None]:
  if settings.guarded_live_api_key or settings.guarded_live_api_secret:
    return settings.guarded_live_api_key, settings.guarded_live_api_secret
  if venue == "binance":
    return settings.binance_api_key, settings.binance_api_secret
  return None, None


def build_default_runs_database_url(repo_root: Path) -> str:
  database_path = (repo_root / ".local" / "state" / "runs.sqlite3").resolve()
  return f"sqlite:///{database_path}"


def build_default_market_data_database_url(repo_root: Path) -> str:
  database_path = (repo_root / ".local" / "state" / "market-data.sqlite3").resolve()
  return f"sqlite:///{database_path}"


def build_market_data_adapter(settings: Settings, repo_root: Path):
  if settings.market_data_provider == "seeded":
    return SeededMarketDataAdapter()
  if settings.market_data_provider in SUPPORTED_CCXT_MARKET_DATA_VENUES:
    return CcxtMarketDataAdapter(
      database_url=(
        settings.market_data_database_url
        or settings.runs_database_url
        or build_default_market_data_database_url(repo_root)
      ),
      venue=settings.market_data_provider,
      tracked_symbols=settings.market_data_symbols,
      default_candle_limit=settings.market_data_default_candle_limit,
      historical_candle_limit=settings.market_data_historical_candle_limit,
    )
  raise ValueError(f"Unsupported market data provider: {settings.market_data_provider}")


def build_venue_state_adapter(settings: Settings):
  venue = resolve_guarded_live_venue(settings)
  if _use_seeded_guarded_live_adapters(settings):
    return SeededVenueStateAdapter(venue=venue)
  if venue in {"binance", "coinbase", "kraken"}:
    api_key, api_secret = _resolve_guarded_live_credentials(settings, venue=venue)
    return CcxtVenueStateAdapter(
      tracked_symbols=settings.market_data_symbols,
      venue=venue,
      api_key=api_key,
      api_secret=api_secret,
    )
  raise ValueError(f"Unsupported guarded-live venue: {venue}")


def build_venue_execution_adapter(settings: Settings):
  venue = resolve_guarded_live_venue(settings)
  if _use_seeded_guarded_live_adapters(settings):
    return SeededVenueExecutionAdapter(venue=venue)
  if venue in {"binance", "coinbase", "kraken"}:
    api_key, api_secret = _resolve_guarded_live_credentials(settings, venue=venue)
    return BinanceVenueExecutionAdapter(
      venue=venue,
      api_key=api_key,
      api_secret=api_secret,
    )
  raise ValueError(f"Unsupported guarded-live venue: {venue}")


def build_operator_alert_delivery_adapter(settings: Settings) -> OperatorAlertDeliveryAdapter:
  return OperatorAlertDeliveryAdapter(
    targets=settings.operator_alert_delivery_targets,
    webhook_url=settings.operator_alert_webhook_url,
    slack_webhook_url=settings.operator_alert_slack_webhook_url,
    pagerduty_integration_key=settings.operator_alert_pagerduty_integration_key,
    pagerduty_api_token=settings.operator_alert_pagerduty_api_token,
    pagerduty_from_email=settings.operator_alert_pagerduty_from_email,
    opsgenie_api_key=settings.operator_alert_opsgenie_api_key,
    opsgenie_api_url=settings.operator_alert_opsgenie_api_url,
    webhook_timeout_seconds=settings.operator_alert_webhook_timeout_seconds,
  )


def build_background_jobs(
  settings: Settings,
  market_data,
  application: TradingApplication,
) -> tuple[AppLifecycle, ...]:
  jobs: list[AppLifecycle] = [
    SandboxWorkerSessionsJob(
      application,
      interval_seconds=settings.sandbox_worker_heartbeat_interval_seconds,
    )
  ]
  if settings.guarded_live_execution_enabled:
    jobs.append(
      GuardedLiveWorkerSessionsJob(
        application,
        interval_seconds=settings.guarded_live_worker_heartbeat_interval_seconds,
      )
    )
  if settings.market_data_provider in SUPPORTED_CCXT_MARKET_DATA_VENUES:
    jobs.append(
      MarketDataSyncJob(
        market_data=market_data,
        timeframes=settings.market_data_sync_timeframes,
        interval_seconds=settings.market_data_sync_interval_seconds,
      )
    )
  return tuple(jobs)


def build_container(settings: Settings) -> Container:
  repo_root = Path(__file__).resolve().parents[4]
  market_data = build_market_data_adapter(settings, repo_root)
  strategies = LocalStrategyCatalog()
  references = load_reference_catalog(repo_root / "reference" / "catalog.toml")
  runs = SqlAlchemyRunRepository(
    settings.runs_database_url or build_default_runs_database_url(repo_root)
  )
  guarded_live_state = SqlAlchemyGuardedLiveStateRepository(
    settings.runs_database_url or build_default_runs_database_url(repo_root)
  )
  venue_state = build_venue_state_adapter(settings)
  venue_execution = build_venue_execution_adapter(settings)
  operator_alert_delivery = build_operator_alert_delivery_adapter(settings)
  application = TradingApplication(
    market_data=market_data,
    strategies=strategies,
    references=references,
    runs=runs,
    guarded_live_state=guarded_live_state,
    venue_state=venue_state,
    venue_execution=venue_execution,
    operator_alert_delivery=operator_alert_delivery,
    freqtrade_reference=FreqtradeReferenceAdapter(repo_root, references),
    guarded_live_venue=resolve_guarded_live_venue(settings),
    guarded_live_execution_enabled=settings.guarded_live_execution_enabled,
    sandbox_worker_heartbeat_interval_seconds=settings.sandbox_worker_heartbeat_interval_seconds,
    sandbox_worker_heartbeat_timeout_seconds=settings.sandbox_worker_heartbeat_timeout_seconds,
    guarded_live_worker_heartbeat_interval_seconds=settings.guarded_live_worker_heartbeat_interval_seconds,
    guarded_live_worker_heartbeat_timeout_seconds=settings.guarded_live_worker_heartbeat_timeout_seconds,
    operator_alert_delivery_max_attempts=settings.operator_alert_delivery_max_attempts,
    operator_alert_delivery_initial_backoff_seconds=settings.operator_alert_delivery_initial_backoff_seconds,
    operator_alert_delivery_max_backoff_seconds=settings.operator_alert_delivery_max_backoff_seconds,
    operator_alert_delivery_backoff_multiplier=settings.operator_alert_delivery_backoff_multiplier,
    operator_alert_paging_policy_default_provider=settings.operator_alert_paging_policy_default_provider,
    operator_alert_paging_policy_warning_targets=settings.operator_alert_paging_policy_warning_targets,
    operator_alert_paging_policy_critical_targets=settings.operator_alert_paging_policy_critical_targets,
    operator_alert_paging_policy_warning_escalation_targets=(
      settings.operator_alert_paging_policy_warning_escalation_targets
    ),
    operator_alert_paging_policy_critical_escalation_targets=(
      settings.operator_alert_paging_policy_critical_escalation_targets
    ),
    operator_alert_external_sync_token=settings.operator_alert_external_sync_token,
    operator_alert_escalation_targets=settings.operator_alert_escalation_targets,
    operator_alert_incident_ack_timeout_seconds=settings.operator_alert_incident_ack_timeout_seconds,
    operator_alert_incident_max_escalations=settings.operator_alert_incident_max_escalations,
    operator_alert_incident_escalation_backoff_multiplier=(
      settings.operator_alert_incident_escalation_backoff_multiplier
    ),
  )
  return Container(
    app=application,
    background_jobs=build_background_jobs(settings, market_data, application),
  )
