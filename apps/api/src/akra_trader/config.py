from __future__ import annotations

from dataclasses import dataclass
import os


def _parse_csv_env(value: str) -> tuple[str, ...]:
  return tuple(item.strip() for item in value.split(",") if item.strip())


def _parse_bool_env(value: str) -> bool:
  return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
  app_name: str = "Akra Trader API"
  api_prefix: str = "/api"
  cors_origin: str = "http://localhost:5173"
  market_data_provider: str = "binance"
  guarded_live_venue: str | None = None
  default_quote_currency: str = "USDT"
  runs_database_url: str | None = None
  market_data_database_url: str | None = None
  market_data_symbols: tuple[str, ...] = ("BTC/USDT", "ETH/USDT", "SOL/USDT")
  market_data_sync_timeframes: tuple[str, ...] = ("5m",)
  market_data_sync_interval_seconds: int = 60
  market_data_default_candle_limit: int = 500
  market_data_historical_candle_limit: int = 2_000
  sandbox_worker_heartbeat_interval_seconds: int = 15
  sandbox_worker_heartbeat_timeout_seconds: int = 45
  guarded_live_execution_enabled: bool = False
  guarded_live_worker_heartbeat_interval_seconds: int = 15
  guarded_live_worker_heartbeat_timeout_seconds: int = 45
  operator_alert_delivery_targets: tuple[str, ...] = ("console",)
  operator_alert_escalation_targets: tuple[str, ...] = ()
  operator_alert_webhook_url: str | None = None
  operator_alert_slack_webhook_url: str | None = None
  operator_alert_pagerduty_integration_key: str | None = None
  operator_alert_pagerduty_api_token: str | None = None
  operator_alert_pagerduty_from_email: str | None = None
  operator_alert_pagerduty_recovery_engine_url_template: str | None = None
  operator_alert_pagerduty_recovery_engine_token: str | None = None
  operator_alert_incidentio_api_token: str | None = None
  operator_alert_incidentio_api_url: str = "https://api.incident.io"
  operator_alert_incidentio_recovery_engine_url_template: str | None = None
  operator_alert_incidentio_recovery_engine_token: str | None = None
  operator_alert_firehydrant_api_token: str | None = None
  operator_alert_firehydrant_api_url: str = "https://api.firehydrant.io"
  operator_alert_firehydrant_recovery_engine_url_template: str | None = None
  operator_alert_firehydrant_recovery_engine_token: str | None = None
  operator_alert_rootly_api_token: str | None = None
  operator_alert_rootly_api_url: str = "https://api.rootly.com"
  operator_alert_rootly_recovery_engine_url_template: str | None = None
  operator_alert_rootly_recovery_engine_token: str | None = None
  operator_alert_blameless_api_token: str | None = None
  operator_alert_blameless_api_url: str = "https://api.blameless.com"
  operator_alert_blameless_recovery_engine_url_template: str | None = None
  operator_alert_blameless_recovery_engine_token: str | None = None
  operator_alert_xmatters_api_token: str | None = None
  operator_alert_xmatters_api_url: str = "https://api.xmatters.com"
  operator_alert_xmatters_recovery_engine_url_template: str | None = None
  operator_alert_xmatters_recovery_engine_token: str | None = None
  operator_alert_servicenow_api_token: str | None = None
  operator_alert_servicenow_api_url: str = "https://api.servicenow.com"
  operator_alert_servicenow_recovery_engine_url_template: str | None = None
  operator_alert_servicenow_recovery_engine_token: str | None = None
  operator_alert_squadcast_api_token: str | None = None
  operator_alert_squadcast_api_url: str = "https://api.squadcast.com"
  operator_alert_squadcast_recovery_engine_url_template: str | None = None
  operator_alert_squadcast_recovery_engine_token: str | None = None
  operator_alert_bigpanda_api_token: str | None = None
  operator_alert_bigpanda_api_url: str = "https://api.bigpanda.io"
  operator_alert_bigpanda_recovery_engine_url_template: str | None = None
  operator_alert_bigpanda_recovery_engine_token: str | None = None
  operator_alert_grafana_oncall_api_token: str | None = None
  operator_alert_grafana_oncall_api_url: str = "https://oncall-api.grafana.com"
  operator_alert_grafana_oncall_recovery_engine_url_template: str | None = None
  operator_alert_grafana_oncall_recovery_engine_token: str | None = None
  operator_alert_zenduty_api_token: str | None = None
  operator_alert_zenduty_api_url: str = "https://api.zenduty.com"
  operator_alert_zenduty_recovery_engine_url_template: str | None = None
  operator_alert_zenduty_recovery_engine_token: str | None = None
  operator_alert_splunk_oncall_api_token: str | None = None
  operator_alert_splunk_oncall_api_url: str = "https://api.splunkoncall.com"
  operator_alert_splunk_oncall_recovery_engine_url_template: str | None = None
  operator_alert_splunk_oncall_recovery_engine_token: str | None = None
  operator_alert_jira_service_management_api_token: str | None = None
  operator_alert_jira_service_management_api_url: str = "https://api.atlassian.com/jsm"
  operator_alert_jira_service_management_recovery_engine_url_template: str | None = None
  operator_alert_jira_service_management_recovery_engine_token: str | None = None
  operator_alert_pagertree_api_token: str | None = None
  operator_alert_pagertree_api_url: str = "https://api.pagertree.com"
  operator_alert_pagertree_recovery_engine_url_template: str | None = None
  operator_alert_pagertree_recovery_engine_token: str | None = None
  operator_alert_alertops_api_token: str | None = None
  operator_alert_alertops_api_url: str = "https://api.alertops.com"
  operator_alert_alertops_recovery_engine_url_template: str | None = None
  operator_alert_alertops_recovery_engine_token: str | None = None
  operator_alert_signl4_api_token: str | None = None
  operator_alert_signl4_api_url: str = "https://connect.signl4.com"
  operator_alert_signl4_recovery_engine_url_template: str | None = None
  operator_alert_signl4_recovery_engine_token: str | None = None
  operator_alert_ilert_api_token: str | None = None
  operator_alert_ilert_api_url: str = "https://api.ilert.com"
  operator_alert_ilert_recovery_engine_url_template: str | None = None
  operator_alert_ilert_recovery_engine_token: str | None = None
  operator_alert_betterstack_api_token: str | None = None
  operator_alert_betterstack_api_url: str = "https://uptime.betterstack.com/api/v2"
  operator_alert_betterstack_recovery_engine_url_template: str | None = None
  operator_alert_betterstack_recovery_engine_token: str | None = None
  operator_alert_onpage_api_token: str | None = None
  operator_alert_onpage_api_url: str = "https://api.onpage.com/v1"
  operator_alert_onpage_recovery_engine_url_template: str | None = None
  operator_alert_onpage_recovery_engine_token: str | None = None
  operator_alert_allquiet_api_token: str | None = None
  operator_alert_allquiet_api_url: str = "https://api.allquiet.app/v1"
  operator_alert_allquiet_recovery_engine_url_template: str | None = None
  operator_alert_allquiet_recovery_engine_token: str | None = None
  operator_alert_moogsoft_api_token: str | None = None
  operator_alert_moogsoft_api_url: str = "https://api.moogsoft.com/v1"
  operator_alert_moogsoft_recovery_engine_url_template: str | None = None
  operator_alert_moogsoft_recovery_engine_token: str | None = None
  operator_alert_spikesh_api_token: str | None = None
  operator_alert_spikesh_api_url: str = "https://api.spike.sh/v1"
  operator_alert_spikesh_recovery_engine_url_template: str | None = None
  operator_alert_spikesh_recovery_engine_token: str | None = None
  operator_alert_dutycalls_api_token: str | None = None
  operator_alert_dutycalls_api_url: str = "https://api.dutycalls.com/v1"
  operator_alert_dutycalls_recovery_engine_url_template: str | None = None
  operator_alert_dutycalls_recovery_engine_token: str | None = None
  operator_alert_incidenthub_api_token: str | None = None
  operator_alert_incidenthub_api_url: str = "https://api.incidenthub.cloud/v1"
  operator_alert_incidenthub_recovery_engine_url_template: str | None = None
  operator_alert_incidenthub_recovery_engine_token: str | None = None
  operator_alert_resolver_api_token: str | None = None
  operator_alert_resolver_api_url: str = "https://api.resolver.com/v1"
  operator_alert_resolver_recovery_engine_url_template: str | None = None
  operator_alert_resolver_recovery_engine_token: str | None = None
  operator_alert_openduty_api_token: str | None = None
  operator_alert_openduty_api_url: str = "https://api.openduty.com/v1"
  operator_alert_openduty_recovery_engine_url_template: str | None = None
  operator_alert_openduty_recovery_engine_token: str | None = None
  operator_alert_cabot_api_token: str | None = None
  operator_alert_cabot_api_url: str = "https://api.cabot.io/v1"
  operator_alert_cabot_recovery_engine_url_template: str | None = None
  operator_alert_cabot_recovery_engine_token: str | None = None
  operator_alert_haloitsm_api_token: str | None = None
  operator_alert_haloitsm_api_url: str = "https://api.haloitsm.com/v1"
  operator_alert_haloitsm_recovery_engine_url_template: str | None = None
  operator_alert_haloitsm_recovery_engine_token: str | None = None
  operator_alert_incidentmanagerio_api_token: str | None = None
  operator_alert_incidentmanagerio_api_url: str = "https://api.incidentmanager.io/v1"
  operator_alert_incidentmanagerio_recovery_engine_url_template: str | None = None
  operator_alert_incidentmanagerio_recovery_engine_token: str | None = None
  operator_alert_oneuptime_api_token: str | None = None
  operator_alert_oneuptime_api_url: str = "https://api.oneuptime.com/v1"
  operator_alert_oneuptime_recovery_engine_url_template: str | None = None
  operator_alert_oneuptime_recovery_engine_token: str | None = None
  operator_alert_squzy_api_token: str | None = None
  operator_alert_squzy_api_url: str = "https://api.squzy.app/v1"
  operator_alert_squzy_recovery_engine_url_template: str | None = None
  operator_alert_squzy_recovery_engine_token: str | None = None
  operator_alert_opsramp_api_token: str | None = None
  operator_alert_opsramp_api_url: str = "https://api.opsramp.com/v1"
  operator_alert_opsramp_recovery_engine_url_template: str | None = None
  operator_alert_opsramp_recovery_engine_token: str | None = None
  operator_alert_opsgenie_api_key: str | None = None
  operator_alert_opsgenie_api_url: str = "https://api.opsgenie.com"
  operator_alert_opsgenie_recovery_engine_url_template: str | None = None
  operator_alert_opsgenie_recovery_engine_api_key: str | None = None
  operator_alert_webhook_timeout_seconds: int = 5
  operator_alert_delivery_max_attempts: int = 4
  operator_alert_delivery_initial_backoff_seconds: int = 15
  operator_alert_delivery_max_backoff_seconds: int = 300
  operator_alert_delivery_backoff_multiplier: float = 2.0
  operator_alert_paging_policy_default_provider: str | None = None
  operator_alert_paging_policy_warning_targets: tuple[str, ...] = ()
  operator_alert_paging_policy_critical_targets: tuple[str, ...] = ()
  operator_alert_paging_policy_warning_escalation_targets: tuple[str, ...] = ()
  operator_alert_paging_policy_critical_escalation_targets: tuple[str, ...] = ()
  operator_alert_external_sync_token: str | None = None
  operator_alert_incident_ack_timeout_seconds: int = 300
  operator_alert_incident_max_escalations: int = 2
  operator_alert_incident_escalation_backoff_multiplier: float = 2.0
  guarded_live_api_key: str | None = None
  guarded_live_api_secret: str | None = None
  binance_api_key: str | None = None
  binance_api_secret: str | None = None


def load_settings() -> Settings:
  return Settings(
    cors_origin=os.getenv("AKRA_TRADER_CORS_ORIGIN", "http://localhost:5173"),
    market_data_provider=os.getenv("AKRA_TRADER_MARKET_DATA_PROVIDER", "binance"),
    guarded_live_venue=os.getenv("AKRA_TRADER_GUARDED_LIVE_VENUE") or None,
    default_quote_currency=os.getenv("AKRA_TRADER_DEFAULT_QUOTE", "USDT"),
    runs_database_url=os.getenv("AKRA_TRADER_RUNS_DATABASE_URL") or None,
    market_data_database_url=os.getenv("AKRA_TRADER_MARKET_DATA_DATABASE_URL") or None,
    market_data_symbols=_parse_csv_env(
      os.getenv("AKRA_TRADER_MARKET_DATA_SYMBOLS", "BTC/USDT,ETH/USDT,SOL/USDT")
    ),
    market_data_sync_timeframes=_parse_csv_env(
      os.getenv("AKRA_TRADER_MARKET_DATA_SYNC_TIMEFRAMES", "5m")
    ),
    market_data_sync_interval_seconds=int(
      os.getenv("AKRA_TRADER_MARKET_DATA_SYNC_INTERVAL_SECONDS", "60")
    ),
    market_data_default_candle_limit=int(
      os.getenv("AKRA_TRADER_MARKET_DATA_DEFAULT_CANDLE_LIMIT", "500")
    ),
    market_data_historical_candle_limit=int(
      os.getenv("AKRA_TRADER_MARKET_DATA_HISTORICAL_CANDLE_LIMIT", "2000")
    ),
    sandbox_worker_heartbeat_interval_seconds=int(
      os.getenv("AKRA_TRADER_SANDBOX_WORKER_HEARTBEAT_INTERVAL_SECONDS", "15")
    ),
    sandbox_worker_heartbeat_timeout_seconds=int(
      os.getenv("AKRA_TRADER_SANDBOX_WORKER_HEARTBEAT_TIMEOUT_SECONDS", "45")
    ),
    guarded_live_execution_enabled=_parse_bool_env(
      os.getenv("AKRA_TRADER_GUARDED_LIVE_EXECUTION_ENABLED", "false")
    ),
    guarded_live_worker_heartbeat_interval_seconds=int(
      os.getenv("AKRA_TRADER_GUARDED_LIVE_WORKER_HEARTBEAT_INTERVAL_SECONDS", "15")
    ),
    guarded_live_worker_heartbeat_timeout_seconds=int(
      os.getenv("AKRA_TRADER_GUARDED_LIVE_WORKER_HEARTBEAT_TIMEOUT_SECONDS", "45")
    ),
    operator_alert_delivery_targets=_parse_csv_env(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_DELIVERY_TARGETS", "console")
    ),
    operator_alert_escalation_targets=_parse_csv_env(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ESCALATION_TARGETS", "")
    ),
    operator_alert_webhook_url=os.getenv("AKRA_TRADER_OPERATOR_ALERT_WEBHOOK_URL") or None,
    operator_alert_slack_webhook_url=os.getenv("AKRA_TRADER_OPERATOR_ALERT_SLACK_WEBHOOK_URL") or None,
    operator_alert_pagerduty_integration_key=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_PAGERDUTY_INTEGRATION_KEY") or None
    ),
    operator_alert_pagerduty_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_PAGERDUTY_API_TOKEN") or None
    ),
    operator_alert_pagerduty_from_email=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_PAGERDUTY_FROM_EMAIL") or None
    ),
    operator_alert_pagerduty_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_PAGERDUTY_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_pagerduty_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_PAGERDUTY_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_incidentio_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_INCIDENTIO_API_TOKEN") or None
    ),
    operator_alert_incidentio_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_INCIDENTIO_API_URL",
      "https://api.incident.io",
    ),
    operator_alert_incidentio_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_INCIDENTIO_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_incidentio_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_INCIDENTIO_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_firehydrant_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_FIREHYDRANT_API_TOKEN") or None
    ),
    operator_alert_firehydrant_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_FIREHYDRANT_API_URL",
      "https://api.firehydrant.io",
    ),
    operator_alert_firehydrant_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_FIREHYDRANT_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_firehydrant_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_FIREHYDRANT_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_rootly_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ROOTLY_API_TOKEN") or None
    ),
    operator_alert_rootly_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_ROOTLY_API_URL",
      "https://api.rootly.com",
    ),
    operator_alert_rootly_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ROOTLY_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_rootly_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ROOTLY_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_blameless_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_BLAMELESS_API_TOKEN") or None
    ),
    operator_alert_blameless_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_BLAMELESS_API_URL",
      "https://api.blameless.com",
    ),
    operator_alert_blameless_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_BLAMELESS_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_blameless_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_BLAMELESS_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_xmatters_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_XMATTERS_API_TOKEN") or None
    ),
    operator_alert_xmatters_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_XMATTERS_API_URL",
      "https://api.xmatters.com",
    ),
    operator_alert_xmatters_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_XMATTERS_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_xmatters_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_XMATTERS_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_servicenow_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SERVICENOW_API_TOKEN") or None
    ),
    operator_alert_servicenow_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_SERVICENOW_API_URL",
      "https://api.servicenow.com",
    ),
    operator_alert_servicenow_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SERVICENOW_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_servicenow_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SERVICENOW_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_squadcast_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SQUADCAST_API_TOKEN") or None
    ),
    operator_alert_squadcast_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_SQUADCAST_API_URL",
      "https://api.squadcast.com",
    ),
    operator_alert_squadcast_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SQUADCAST_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_squadcast_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SQUADCAST_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_bigpanda_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_BIGPANDA_API_TOKEN") or None
    ),
    operator_alert_bigpanda_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_BIGPANDA_API_URL",
      "https://api.bigpanda.io",
    ),
    operator_alert_bigpanda_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_BIGPANDA_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_bigpanda_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_BIGPANDA_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_grafana_oncall_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_GRAFANA_ONCALL_API_TOKEN") or None
    ),
    operator_alert_grafana_oncall_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_GRAFANA_ONCALL_API_URL",
      "https://oncall-api.grafana.com",
    ),
    operator_alert_grafana_oncall_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_GRAFANA_ONCALL_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_grafana_oncall_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_GRAFANA_ONCALL_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_zenduty_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ZENDUTY_API_TOKEN") or None
    ),
    operator_alert_zenduty_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_ZENDUTY_API_URL",
      "https://api.zenduty.com",
    ),
    operator_alert_zenduty_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ZENDUTY_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_zenduty_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ZENDUTY_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_splunk_oncall_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SPLUNK_ONCALL_API_TOKEN") or None
    ),
    operator_alert_splunk_oncall_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_SPLUNK_ONCALL_API_URL",
      "https://api.splunkoncall.com",
    ),
    operator_alert_splunk_oncall_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SPLUNK_ONCALL_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_splunk_oncall_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SPLUNK_ONCALL_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_jira_service_management_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_JIRA_SERVICE_MANAGEMENT_API_TOKEN") or None
    ),
    operator_alert_jira_service_management_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_JIRA_SERVICE_MANAGEMENT_API_URL",
      "https://api.atlassian.com/jsm",
    ),
    operator_alert_jira_service_management_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_JIRA_SERVICE_MANAGEMENT_RECOVERY_ENGINE_URL_TEMPLATE")
      or None
    ),
    operator_alert_jira_service_management_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_JIRA_SERVICE_MANAGEMENT_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_pagertree_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_PAGERTREE_API_TOKEN") or None
    ),
    operator_alert_pagertree_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_PAGERTREE_API_URL",
      "https://api.pagertree.com",
    ),
    operator_alert_pagertree_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_PAGERTREE_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_pagertree_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_PAGERTREE_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_alertops_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ALERTOPS_API_TOKEN") or None
    ),
    operator_alert_alertops_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_ALERTOPS_API_URL",
      "https://api.alertops.com",
    ),
    operator_alert_alertops_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ALERTOPS_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_alertops_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ALERTOPS_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_signl4_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SIGNL4_API_TOKEN") or None
    ),
    operator_alert_signl4_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_SIGNL4_API_URL",
      "https://connect.signl4.com",
    ),
    operator_alert_signl4_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SIGNL4_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_signl4_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SIGNL4_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_ilert_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ILERT_API_TOKEN") or None
    ),
    operator_alert_ilert_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_ILERT_API_URL",
      "https://api.ilert.com",
    ),
    operator_alert_ilert_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ILERT_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_ilert_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ILERT_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_betterstack_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_BETTERSTACK_API_TOKEN") or None
    ),
    operator_alert_betterstack_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_BETTERSTACK_API_URL",
      "https://uptime.betterstack.com/api/v2",
    ),
    operator_alert_betterstack_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_BETTERSTACK_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_betterstack_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_BETTERSTACK_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_onpage_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ONPAGE_API_TOKEN") or None
    ),
    operator_alert_onpage_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_ONPAGE_API_URL",
      "https://api.onpage.com/v1",
    ),
    operator_alert_onpage_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ONPAGE_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_onpage_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ONPAGE_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_allquiet_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ALLQUIET_API_TOKEN") or None
    ),
    operator_alert_allquiet_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_ALLQUIET_API_URL",
      "https://api.allquiet.app/v1",
    ),
    operator_alert_allquiet_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ALLQUIET_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_allquiet_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ALLQUIET_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_moogsoft_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_MOOGSOFT_API_TOKEN") or None
    ),
    operator_alert_moogsoft_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_MOOGSOFT_API_URL",
      "https://api.moogsoft.com/v1",
    ),
    operator_alert_moogsoft_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_MOOGSOFT_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_moogsoft_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_MOOGSOFT_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_spikesh_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SPIKESH_API_TOKEN") or None
    ),
    operator_alert_spikesh_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_SPIKESH_API_URL",
      "https://api.spike.sh/v1",
    ),
    operator_alert_spikesh_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SPIKESH_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_spikesh_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SPIKESH_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_dutycalls_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_DUTYCALLS_API_TOKEN") or None
    ),
    operator_alert_dutycalls_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_DUTYCALLS_API_URL",
      "https://api.dutycalls.com/v1",
    ),
    operator_alert_dutycalls_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_DUTYCALLS_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_dutycalls_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_DUTYCALLS_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_incidenthub_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_INCIDENTHUB_API_TOKEN") or None
    ),
    operator_alert_incidenthub_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_INCIDENTHUB_API_URL",
      "https://api.incidenthub.cloud/v1",
    ),
    operator_alert_incidenthub_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_INCIDENTHUB_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_incidenthub_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_INCIDENTHUB_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_resolver_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_RESOLVER_API_TOKEN") or None
    ),
    operator_alert_resolver_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_RESOLVER_API_URL",
      "https://api.resolver.com/v1",
    ),
    operator_alert_resolver_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_RESOLVER_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_resolver_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_RESOLVER_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_openduty_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_OPENDUTY_API_TOKEN") or None
    ),
    operator_alert_openduty_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_OPENDUTY_API_URL",
      "https://api.openduty.com/v1",
    ),
    operator_alert_openduty_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_OPENDUTY_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_openduty_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_OPENDUTY_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_cabot_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_CABOT_API_TOKEN") or None
    ),
    operator_alert_cabot_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_CABOT_API_URL",
      "https://api.cabot.io/v1",
    ),
    operator_alert_cabot_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_CABOT_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_cabot_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_CABOT_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_haloitsm_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_HALOITSM_API_TOKEN") or None
    ),
    operator_alert_haloitsm_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_HALOITSM_API_URL",
      "https://api.haloitsm.com/v1",
    ),
    operator_alert_haloitsm_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_HALOITSM_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_haloitsm_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_HALOITSM_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_incidentmanagerio_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_INCIDENTMANAGERIO_API_TOKEN") or None
    ),
    operator_alert_incidentmanagerio_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_INCIDENTMANAGERIO_API_URL",
      "https://api.incidentmanager.io/v1",
    ),
    operator_alert_incidentmanagerio_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_INCIDENTMANAGERIO_RECOVERY_ENGINE_URL_TEMPLATE")
      or None
    ),
    operator_alert_incidentmanagerio_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_INCIDENTMANAGERIO_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_oneuptime_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ONEUPTIME_API_TOKEN") or None
    ),
    operator_alert_oneuptime_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_ONEUPTIME_API_URL",
      "https://api.oneuptime.com/v1",
    ),
    operator_alert_oneuptime_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ONEUPTIME_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_oneuptime_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_ONEUPTIME_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_squzy_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SQUZY_API_TOKEN") or None
    ),
    operator_alert_squzy_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_SQUZY_API_URL",
      "https://api.squzy.app/v1",
    ),
    operator_alert_squzy_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SQUZY_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_squzy_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_SQUZY_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_opsramp_api_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_OPSRAMP_API_TOKEN") or None
    ),
    operator_alert_opsramp_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_OPSRAMP_API_URL",
      "https://api.opsramp.com/v1",
    ),
    operator_alert_opsramp_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_OPSRAMP_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_opsramp_recovery_engine_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_OPSRAMP_RECOVERY_ENGINE_TOKEN") or None
    ),
    operator_alert_opsgenie_api_key=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_OPSGENIE_API_KEY") or None
    ),
    operator_alert_opsgenie_api_url=os.getenv(
      "AKRA_TRADER_OPERATOR_ALERT_OPSGENIE_API_URL",
      "https://api.opsgenie.com",
    ),
    operator_alert_opsgenie_recovery_engine_url_template=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_OPSGENIE_RECOVERY_ENGINE_URL_TEMPLATE") or None
    ),
    operator_alert_opsgenie_recovery_engine_api_key=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_OPSGENIE_RECOVERY_ENGINE_API_KEY") or None
    ),
    operator_alert_webhook_timeout_seconds=int(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_WEBHOOK_TIMEOUT_SECONDS", "5")
    ),
    operator_alert_delivery_max_attempts=int(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_DELIVERY_MAX_ATTEMPTS", "4")
    ),
    operator_alert_delivery_initial_backoff_seconds=int(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_DELIVERY_INITIAL_BACKOFF_SECONDS", "15")
    ),
    operator_alert_delivery_max_backoff_seconds=int(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_DELIVERY_MAX_BACKOFF_SECONDS", "300")
    ),
    operator_alert_delivery_backoff_multiplier=float(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_DELIVERY_BACKOFF_MULTIPLIER", "2.0")
    ),
    operator_alert_paging_policy_default_provider=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_PAGING_POLICY_DEFAULT_PROVIDER") or None
    ),
    operator_alert_paging_policy_warning_targets=_parse_csv_env(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_PAGING_POLICY_WARNING_TARGETS", "")
    ),
    operator_alert_paging_policy_critical_targets=_parse_csv_env(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_PAGING_POLICY_CRITICAL_TARGETS", "")
    ),
    operator_alert_paging_policy_warning_escalation_targets=_parse_csv_env(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_PAGING_POLICY_WARNING_ESCALATION_TARGETS", "")
    ),
    operator_alert_paging_policy_critical_escalation_targets=_parse_csv_env(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_PAGING_POLICY_CRITICAL_ESCALATION_TARGETS", "")
    ),
    operator_alert_external_sync_token=(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_EXTERNAL_SYNC_TOKEN") or None
    ),
    operator_alert_incident_ack_timeout_seconds=int(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_INCIDENT_ACK_TIMEOUT_SECONDS", "300")
    ),
    operator_alert_incident_max_escalations=int(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_INCIDENT_MAX_ESCALATIONS", "2")
    ),
    operator_alert_incident_escalation_backoff_multiplier=float(
      os.getenv("AKRA_TRADER_OPERATOR_ALERT_INCIDENT_ESCALATION_BACKOFF_MULTIPLIER", "2.0")
    ),
    guarded_live_api_key=os.getenv("AKRA_TRADER_GUARDED_LIVE_API_KEY") or None,
    guarded_live_api_secret=os.getenv("AKRA_TRADER_GUARDED_LIVE_API_SECRET") or None,
    binance_api_key=os.getenv("AKRA_TRADER_BINANCE_API_KEY") or None,
    binance_api_secret=os.getenv("AKRA_TRADER_BINANCE_API_SECRET") or None,
  )
