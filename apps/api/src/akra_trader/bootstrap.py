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
    pagerduty_recovery_engine_url_template=(
      settings.operator_alert_pagerduty_recovery_engine_url_template
    ),
    pagerduty_recovery_engine_token=settings.operator_alert_pagerduty_recovery_engine_token,
    incidentio_api_token=settings.operator_alert_incidentio_api_token,
    incidentio_api_url=settings.operator_alert_incidentio_api_url,
    incidentio_recovery_engine_url_template=(
      settings.operator_alert_incidentio_recovery_engine_url_template
    ),
    incidentio_recovery_engine_token=settings.operator_alert_incidentio_recovery_engine_token,
    firehydrant_api_token=settings.operator_alert_firehydrant_api_token,
    firehydrant_api_url=settings.operator_alert_firehydrant_api_url,
    firehydrant_recovery_engine_url_template=(
      settings.operator_alert_firehydrant_recovery_engine_url_template
    ),
    firehydrant_recovery_engine_token=settings.operator_alert_firehydrant_recovery_engine_token,
    rootly_api_token=settings.operator_alert_rootly_api_token,
    rootly_api_url=settings.operator_alert_rootly_api_url,
    rootly_recovery_engine_url_template=(
      settings.operator_alert_rootly_recovery_engine_url_template
    ),
    rootly_recovery_engine_token=settings.operator_alert_rootly_recovery_engine_token,
    blameless_api_token=settings.operator_alert_blameless_api_token,
    blameless_api_url=settings.operator_alert_blameless_api_url,
    blameless_recovery_engine_url_template=(
      settings.operator_alert_blameless_recovery_engine_url_template
    ),
    blameless_recovery_engine_token=settings.operator_alert_blameless_recovery_engine_token,
    xmatters_api_token=settings.operator_alert_xmatters_api_token,
    xmatters_api_url=settings.operator_alert_xmatters_api_url,
    xmatters_recovery_engine_url_template=(
      settings.operator_alert_xmatters_recovery_engine_url_template
    ),
    xmatters_recovery_engine_token=settings.operator_alert_xmatters_recovery_engine_token,
    servicenow_api_token=settings.operator_alert_servicenow_api_token,
    servicenow_api_url=settings.operator_alert_servicenow_api_url,
    servicenow_recovery_engine_url_template=(
      settings.operator_alert_servicenow_recovery_engine_url_template
    ),
    servicenow_recovery_engine_token=settings.operator_alert_servicenow_recovery_engine_token,
    squadcast_api_token=settings.operator_alert_squadcast_api_token,
    squadcast_api_url=settings.operator_alert_squadcast_api_url,
    squadcast_recovery_engine_url_template=(
      settings.operator_alert_squadcast_recovery_engine_url_template
    ),
    squadcast_recovery_engine_token=settings.operator_alert_squadcast_recovery_engine_token,
    bigpanda_api_token=settings.operator_alert_bigpanda_api_token,
    bigpanda_api_url=settings.operator_alert_bigpanda_api_url,
    bigpanda_recovery_engine_url_template=(
      settings.operator_alert_bigpanda_recovery_engine_url_template
    ),
    bigpanda_recovery_engine_token=settings.operator_alert_bigpanda_recovery_engine_token,
    grafana_oncall_api_token=settings.operator_alert_grafana_oncall_api_token,
    grafana_oncall_api_url=settings.operator_alert_grafana_oncall_api_url,
    grafana_oncall_recovery_engine_url_template=(
      settings.operator_alert_grafana_oncall_recovery_engine_url_template
    ),
    grafana_oncall_recovery_engine_token=settings.operator_alert_grafana_oncall_recovery_engine_token,
    zenduty_api_token=settings.operator_alert_zenduty_api_token,
    zenduty_api_url=settings.operator_alert_zenduty_api_url,
    zenduty_recovery_engine_url_template=(
      settings.operator_alert_zenduty_recovery_engine_url_template
    ),
    zenduty_recovery_engine_token=settings.operator_alert_zenduty_recovery_engine_token,
    splunk_oncall_api_token=settings.operator_alert_splunk_oncall_api_token,
    splunk_oncall_api_url=settings.operator_alert_splunk_oncall_api_url,
    splunk_oncall_recovery_engine_url_template=(
      settings.operator_alert_splunk_oncall_recovery_engine_url_template
    ),
    splunk_oncall_recovery_engine_token=settings.operator_alert_splunk_oncall_recovery_engine_token,
    jira_service_management_api_token=settings.operator_alert_jira_service_management_api_token,
    jira_service_management_api_url=settings.operator_alert_jira_service_management_api_url,
    jira_service_management_recovery_engine_url_template=(
      settings.operator_alert_jira_service_management_recovery_engine_url_template
    ),
    jira_service_management_recovery_engine_token=(
      settings.operator_alert_jira_service_management_recovery_engine_token
    ),
    pagertree_api_token=settings.operator_alert_pagertree_api_token,
    pagertree_api_url=settings.operator_alert_pagertree_api_url,
    pagertree_recovery_engine_url_template=(
      settings.operator_alert_pagertree_recovery_engine_url_template
    ),
    pagertree_recovery_engine_token=settings.operator_alert_pagertree_recovery_engine_token,
    alertops_api_token=settings.operator_alert_alertops_api_token,
    alertops_api_url=settings.operator_alert_alertops_api_url,
    alertops_recovery_engine_url_template=(
      settings.operator_alert_alertops_recovery_engine_url_template
    ),
    alertops_recovery_engine_token=settings.operator_alert_alertops_recovery_engine_token,
    signl4_api_token=settings.operator_alert_signl4_api_token,
    signl4_api_url=settings.operator_alert_signl4_api_url,
    signl4_recovery_engine_url_template=(
      settings.operator_alert_signl4_recovery_engine_url_template
    ),
    signl4_recovery_engine_token=settings.operator_alert_signl4_recovery_engine_token,
    ilert_api_token=settings.operator_alert_ilert_api_token,
    ilert_api_url=settings.operator_alert_ilert_api_url,
    ilert_recovery_engine_url_template=(
      settings.operator_alert_ilert_recovery_engine_url_template
    ),
    ilert_recovery_engine_token=settings.operator_alert_ilert_recovery_engine_token,
    betterstack_api_token=settings.operator_alert_betterstack_api_token,
    betterstack_api_url=settings.operator_alert_betterstack_api_url,
    betterstack_recovery_engine_url_template=(
      settings.operator_alert_betterstack_recovery_engine_url_template
    ),
    betterstack_recovery_engine_token=settings.operator_alert_betterstack_recovery_engine_token,
    onpage_api_token=settings.operator_alert_onpage_api_token,
    onpage_api_url=settings.operator_alert_onpage_api_url,
    onpage_recovery_engine_url_template=(
      settings.operator_alert_onpage_recovery_engine_url_template
    ),
    onpage_recovery_engine_token=settings.operator_alert_onpage_recovery_engine_token,
    allquiet_api_token=settings.operator_alert_allquiet_api_token,
    allquiet_api_url=settings.operator_alert_allquiet_api_url,
    allquiet_recovery_engine_url_template=(
      settings.operator_alert_allquiet_recovery_engine_url_template
    ),
    allquiet_recovery_engine_token=settings.operator_alert_allquiet_recovery_engine_token,
    moogsoft_api_token=settings.operator_alert_moogsoft_api_token,
    moogsoft_api_url=settings.operator_alert_moogsoft_api_url,
    moogsoft_recovery_engine_url_template=(
      settings.operator_alert_moogsoft_recovery_engine_url_template
    ),
    moogsoft_recovery_engine_token=settings.operator_alert_moogsoft_recovery_engine_token,
    spikesh_api_token=settings.operator_alert_spikesh_api_token,
    spikesh_api_url=settings.operator_alert_spikesh_api_url,
    spikesh_recovery_engine_url_template=(
      settings.operator_alert_spikesh_recovery_engine_url_template
    ),
    spikesh_recovery_engine_token=settings.operator_alert_spikesh_recovery_engine_token,
    dutycalls_api_token=settings.operator_alert_dutycalls_api_token,
    dutycalls_api_url=settings.operator_alert_dutycalls_api_url,
    dutycalls_recovery_engine_url_template=(
      settings.operator_alert_dutycalls_recovery_engine_url_template
    ),
    dutycalls_recovery_engine_token=settings.operator_alert_dutycalls_recovery_engine_token,
    incidenthub_api_token=settings.operator_alert_incidenthub_api_token,
    incidenthub_api_url=settings.operator_alert_incidenthub_api_url,
    incidenthub_recovery_engine_url_template=(
      settings.operator_alert_incidenthub_recovery_engine_url_template
    ),
    incidenthub_recovery_engine_token=settings.operator_alert_incidenthub_recovery_engine_token,
    resolver_api_token=settings.operator_alert_resolver_api_token,
    resolver_api_url=settings.operator_alert_resolver_api_url,
    resolver_recovery_engine_url_template=(
      settings.operator_alert_resolver_recovery_engine_url_template
    ),
    resolver_recovery_engine_token=settings.operator_alert_resolver_recovery_engine_token,
    openduty_api_token=settings.operator_alert_openduty_api_token,
    openduty_api_url=settings.operator_alert_openduty_api_url,
    openduty_recovery_engine_url_template=(
      settings.operator_alert_openduty_recovery_engine_url_template
    ),
    openduty_recovery_engine_token=settings.operator_alert_openduty_recovery_engine_token,
    cabot_api_token=settings.operator_alert_cabot_api_token,
    cabot_api_url=settings.operator_alert_cabot_api_url,
    cabot_recovery_engine_url_template=(
      settings.operator_alert_cabot_recovery_engine_url_template
    ),
    cabot_recovery_engine_token=settings.operator_alert_cabot_recovery_engine_token,
    haloitsm_api_token=settings.operator_alert_haloitsm_api_token,
    haloitsm_api_url=settings.operator_alert_haloitsm_api_url,
    haloitsm_recovery_engine_url_template=(
      settings.operator_alert_haloitsm_recovery_engine_url_template
    ),
    haloitsm_recovery_engine_token=settings.operator_alert_haloitsm_recovery_engine_token,
    incidentmanagerio_api_token=settings.operator_alert_incidentmanagerio_api_token,
    incidentmanagerio_api_url=settings.operator_alert_incidentmanagerio_api_url,
    incidentmanagerio_recovery_engine_url_template=(
      settings.operator_alert_incidentmanagerio_recovery_engine_url_template
    ),
    incidentmanagerio_recovery_engine_token=(
      settings.operator_alert_incidentmanagerio_recovery_engine_token
    ),
    oneuptime_api_token=settings.operator_alert_oneuptime_api_token,
    oneuptime_api_url=settings.operator_alert_oneuptime_api_url,
    oneuptime_recovery_engine_url_template=(
      settings.operator_alert_oneuptime_recovery_engine_url_template
    ),
    oneuptime_recovery_engine_token=settings.operator_alert_oneuptime_recovery_engine_token,
    squzy_api_token=settings.operator_alert_squzy_api_token,
    squzy_api_url=settings.operator_alert_squzy_api_url,
    squzy_recovery_engine_url_template=(
      settings.operator_alert_squzy_recovery_engine_url_template
    ),
    squzy_recovery_engine_token=settings.operator_alert_squzy_recovery_engine_token,
    crisescontrol_api_token=settings.operator_alert_crisescontrol_api_token,
    crisescontrol_api_url=settings.operator_alert_crisescontrol_api_url,
    crisescontrol_recovery_engine_url_template=(
      settings.operator_alert_crisescontrol_recovery_engine_url_template
    ),
    crisescontrol_recovery_engine_token=settings.operator_alert_crisescontrol_recovery_engine_token,
    freshservice_api_token=settings.operator_alert_freshservice_api_token,
    freshservice_api_url=settings.operator_alert_freshservice_api_url,
    freshservice_recovery_engine_url_template=(
      settings.operator_alert_freshservice_recovery_engine_url_template
    ),
    freshservice_recovery_engine_token=settings.operator_alert_freshservice_recovery_engine_token,
    servicedeskplus_api_token=settings.operator_alert_servicedeskplus_api_token,
    servicedeskplus_api_url=settings.operator_alert_servicedeskplus_api_url,
    servicedeskplus_recovery_engine_url_template=(
      settings.operator_alert_servicedeskplus_recovery_engine_url_template
    ),
    servicedeskplus_recovery_engine_token=settings.operator_alert_servicedeskplus_recovery_engine_token,
    sysaid_api_token=settings.operator_alert_sysaid_api_token,
    sysaid_api_url=settings.operator_alert_sysaid_api_url,
    sysaid_recovery_engine_url_template=(
      settings.operator_alert_sysaid_recovery_engine_url_template
    ),
    sysaid_recovery_engine_token=settings.operator_alert_sysaid_recovery_engine_token,
    bmchelix_api_token=settings.operator_alert_bmchelix_api_token,
    bmchelix_api_url=settings.operator_alert_bmchelix_api_url,
    bmchelix_recovery_engine_url_template=(
      settings.operator_alert_bmchelix_recovery_engine_url_template
    ),
    bmchelix_recovery_engine_token=settings.operator_alert_bmchelix_recovery_engine_token,
    opsramp_api_token=settings.operator_alert_opsramp_api_token,
    opsramp_api_url=settings.operator_alert_opsramp_api_url,
    opsramp_recovery_engine_url_template=(
      settings.operator_alert_opsramp_recovery_engine_url_template
    ),
    opsramp_recovery_engine_token=settings.operator_alert_opsramp_recovery_engine_token,
    opsgenie_api_key=settings.operator_alert_opsgenie_api_key,
    opsgenie_api_url=settings.operator_alert_opsgenie_api_url,
    opsgenie_recovery_engine_url_template=(
      settings.operator_alert_opsgenie_recovery_engine_url_template
    ),
    opsgenie_recovery_engine_api_key=settings.operator_alert_opsgenie_recovery_engine_api_key,
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
    market_data_sync_timeframes=settings.market_data_sync_timeframes,
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
