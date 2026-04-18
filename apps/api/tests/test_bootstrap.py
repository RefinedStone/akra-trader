from __future__ import annotations

from pathlib import Path

from akra_trader.adapters.in_memory import SeededMarketDataAdapter
from akra_trader.bootstrap import build_container
from akra_trader.bootstrap import build_default_market_data_database_url
from akra_trader.bootstrap import build_default_runs_database_url
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


def test_build_container_wires_operator_alert_delivery_settings(monkeypatch) -> None:
  captured: dict[str, str] = {}

  class FakeRunRepository:
    def __init__(self, database_url: str) -> None:
      self.database_url = database_url

  class FakeGuardedLiveRepository:
    def __init__(self, database_url: str) -> None:
      self.database_url = database_url

  class FakeOperatorAlertDeliveryAdapter:
    def __init__(
      self,
      *,
      targets: tuple[str, ...],
      webhook_url: str | None,
      slack_webhook_url: str | None,
      pagerduty_integration_key: str | None,
      pagerduty_api_token: str | None,
      pagerduty_from_email: str | None,
      pagerduty_recovery_engine_url_template: str | None,
      pagerduty_recovery_engine_token: str | None,
      incidentio_api_token: str | None,
      incidentio_api_url: str,
      incidentio_recovery_engine_url_template: str | None,
      incidentio_recovery_engine_token: str | None,
      firehydrant_api_token: str | None,
      firehydrant_api_url: str,
      firehydrant_recovery_engine_url_template: str | None,
      firehydrant_recovery_engine_token: str | None,
      rootly_api_token: str | None,
      rootly_api_url: str,
      rootly_recovery_engine_url_template: str | None,
      rootly_recovery_engine_token: str | None,
      blameless_api_token: str | None,
      blameless_api_url: str,
      blameless_recovery_engine_url_template: str | None,
      blameless_recovery_engine_token: str | None,
      xmatters_api_token: str | None,
      xmatters_api_url: str,
      xmatters_recovery_engine_url_template: str | None,
      xmatters_recovery_engine_token: str | None,
      servicenow_api_token: str | None,
      servicenow_api_url: str,
      servicenow_recovery_engine_url_template: str | None,
      servicenow_recovery_engine_token: str | None,
      squadcast_api_token: str | None,
      squadcast_api_url: str,
      squadcast_recovery_engine_url_template: str | None,
      squadcast_recovery_engine_token: str | None,
      bigpanda_api_token: str | None,
      bigpanda_api_url: str,
      bigpanda_recovery_engine_url_template: str | None,
      bigpanda_recovery_engine_token: str | None,
      grafana_oncall_api_token: str | None,
      grafana_oncall_api_url: str,
      grafana_oncall_recovery_engine_url_template: str | None,
      grafana_oncall_recovery_engine_token: str | None,
      splunk_oncall_api_token: str | None,
      splunk_oncall_api_url: str,
      splunk_oncall_recovery_engine_url_template: str | None,
      splunk_oncall_recovery_engine_token: str | None,
      jira_service_management_api_token: str | None,
      jira_service_management_api_url: str,
      jira_service_management_recovery_engine_url_template: str | None,
      jira_service_management_recovery_engine_token: str | None,
      pagertree_api_token: str | None,
      pagertree_api_url: str,
      pagertree_recovery_engine_url_template: str | None,
      pagertree_recovery_engine_token: str | None,
      alertops_api_token: str | None,
      alertops_api_url: str,
      alertops_recovery_engine_url_template: str | None,
      alertops_recovery_engine_token: str | None,
      signl4_api_token: str | None,
      signl4_api_url: str,
      signl4_recovery_engine_url_template: str | None,
      signl4_recovery_engine_token: str | None,
      ilert_api_token: str | None,
      ilert_api_url: str,
      ilert_recovery_engine_url_template: str | None,
      ilert_recovery_engine_token: str | None,
      betterstack_api_token: str | None,
      betterstack_api_url: str,
      betterstack_recovery_engine_url_template: str | None,
      betterstack_recovery_engine_token: str | None,
      onpage_api_token: str | None,
      onpage_api_url: str,
      onpage_recovery_engine_url_template: str | None,
      onpage_recovery_engine_token: str | None,
      allquiet_api_token: str | None,
      allquiet_api_url: str,
      allquiet_recovery_engine_url_template: str | None,
      allquiet_recovery_engine_token: str | None,
      moogsoft_api_token: str | None,
      moogsoft_api_url: str,
      moogsoft_recovery_engine_url_template: str | None,
      moogsoft_recovery_engine_token: str | None,
      spikesh_api_token: str | None,
      spikesh_api_url: str,
      spikesh_recovery_engine_url_template: str | None,
      spikesh_recovery_engine_token: str | None,
      dutycalls_api_token: str | None,
      dutycalls_api_url: str,
      dutycalls_recovery_engine_url_template: str | None,
      dutycalls_recovery_engine_token: str | None,
      incidenthub_api_token: str | None,
      incidenthub_api_url: str,
      incidenthub_recovery_engine_url_template: str | None,
      incidenthub_recovery_engine_token: str | None,
      resolver_api_token: str | None,
      resolver_api_url: str,
      resolver_recovery_engine_url_template: str | None,
      resolver_recovery_engine_token: str | None,
      openduty_api_token: str | None,
      openduty_api_url: str,
      openduty_recovery_engine_url_template: str | None,
      openduty_recovery_engine_token: str | None,
      cabot_api_token: str | None,
      cabot_api_url: str,
      cabot_recovery_engine_url_template: str | None,
      cabot_recovery_engine_token: str | None,
      haloitsm_api_token: str | None,
      haloitsm_api_url: str,
      haloitsm_recovery_engine_url_template: str | None,
      haloitsm_recovery_engine_token: str | None,
      incidentmanagerio_api_token: str | None,
      incidentmanagerio_api_url: str,
      incidentmanagerio_recovery_engine_url_template: str | None,
      incidentmanagerio_recovery_engine_token: str | None,
      oneuptime_api_token: str | None,
      oneuptime_api_url: str,
      oneuptime_recovery_engine_url_template: str | None,
      oneuptime_recovery_engine_token: str | None,
      squzy_api_token: str | None,
      squzy_api_url: str,
      squzy_recovery_engine_url_template: str | None,
      squzy_recovery_engine_token: str | None,
      crisescontrol_api_token: str | None,
      crisescontrol_api_url: str,
      crisescontrol_recovery_engine_url_template: str | None,
      crisescontrol_recovery_engine_token: str | None,
      freshservice_api_token: str | None,
      freshservice_api_url: str,
      freshservice_recovery_engine_url_template: str | None,
      freshservice_recovery_engine_token: str | None,
      freshdesk_api_token: str | None,
      freshdesk_api_url: str,
      freshdesk_recovery_engine_url_template: str | None,
      freshdesk_recovery_engine_token: str | None,
      servicedeskplus_api_token: str | None,
      servicedeskplus_api_url: str,
      servicedeskplus_recovery_engine_url_template: str | None,
      servicedeskplus_recovery_engine_token: str | None,
      sysaid_api_token: str | None,
      sysaid_api_url: str,
      sysaid_recovery_engine_url_template: str | None,
      sysaid_recovery_engine_token: str | None,
      bmchelix_api_token: str | None,
      bmchelix_api_url: str,
      bmchelix_recovery_engine_url_template: str | None,
      bmchelix_recovery_engine_token: str | None,
      solarwindsservicedesk_api_token: str | None,
      solarwindsservicedesk_api_url: str,
      solarwindsservicedesk_recovery_engine_url_template: str | None,
      solarwindsservicedesk_recovery_engine_token: str | None,
      topdesk_api_token: str | None,
      topdesk_api_url: str,
      topdesk_recovery_engine_url_template: str | None,
      topdesk_recovery_engine_token: str | None,
      invgateservicedesk_api_token: str | None,
      invgateservicedesk_api_url: str,
      invgateservicedesk_recovery_engine_url_template: str | None,
      invgateservicedesk_recovery_engine_token: str | None,
      opsramp_api_token: str | None,
      opsramp_api_url: str,
      opsramp_recovery_engine_url_template: str | None,
      opsramp_recovery_engine_token: str | None,
      zenduty_api_token: str | None,
      zenduty_api_url: str,
      zenduty_recovery_engine_url_template: str | None,
      zenduty_recovery_engine_token: str | None,
      opsgenie_api_key: str | None,
      opsgenie_api_url: str,
      opsgenie_recovery_engine_url_template: str | None,
      opsgenie_recovery_engine_api_key: str | None,
      webhook_timeout_seconds: int,
    ) -> None:
      captured["targets"] = ",".join(targets)
      captured["webhook_url"] = webhook_url or ""
      captured["slack_webhook_url"] = slack_webhook_url or ""
      captured["pagerduty_integration_key"] = pagerduty_integration_key or ""
      captured["pagerduty_api_token"] = pagerduty_api_token or ""
      captured["pagerduty_from_email"] = pagerduty_from_email or ""
      captured["pagerduty_recovery_engine_url_template"] = pagerduty_recovery_engine_url_template or ""
      captured["pagerduty_recovery_engine_token"] = pagerduty_recovery_engine_token or ""
      captured["incidentio_api_token"] = incidentio_api_token or ""
      captured["incidentio_api_url"] = incidentio_api_url
      captured["incidentio_recovery_engine_url_template"] = incidentio_recovery_engine_url_template or ""
      captured["incidentio_recovery_engine_token"] = incidentio_recovery_engine_token or ""
      captured["firehydrant_api_token"] = firehydrant_api_token or ""
      captured["firehydrant_api_url"] = firehydrant_api_url
      captured["firehydrant_recovery_engine_url_template"] = firehydrant_recovery_engine_url_template or ""
      captured["firehydrant_recovery_engine_token"] = firehydrant_recovery_engine_token or ""
      captured["rootly_api_token"] = rootly_api_token or ""
      captured["rootly_api_url"] = rootly_api_url
      captured["rootly_recovery_engine_url_template"] = rootly_recovery_engine_url_template or ""
      captured["rootly_recovery_engine_token"] = rootly_recovery_engine_token or ""
      captured["blameless_api_token"] = blameless_api_token or ""
      captured["blameless_api_url"] = blameless_api_url
      captured["blameless_recovery_engine_url_template"] = blameless_recovery_engine_url_template or ""
      captured["blameless_recovery_engine_token"] = blameless_recovery_engine_token or ""
      captured["xmatters_api_token"] = xmatters_api_token or ""
      captured["xmatters_api_url"] = xmatters_api_url
      captured["xmatters_recovery_engine_url_template"] = xmatters_recovery_engine_url_template or ""
      captured["xmatters_recovery_engine_token"] = xmatters_recovery_engine_token or ""
      captured["servicenow_api_token"] = servicenow_api_token or ""
      captured["servicenow_api_url"] = servicenow_api_url
      captured["servicenow_recovery_engine_url_template"] = servicenow_recovery_engine_url_template or ""
      captured["servicenow_recovery_engine_token"] = servicenow_recovery_engine_token or ""
      captured["squadcast_api_token"] = squadcast_api_token or ""
      captured["squadcast_api_url"] = squadcast_api_url
      captured["squadcast_recovery_engine_url_template"] = squadcast_recovery_engine_url_template or ""
      captured["squadcast_recovery_engine_token"] = squadcast_recovery_engine_token or ""
      captured["bigpanda_api_token"] = bigpanda_api_token or ""
      captured["bigpanda_api_url"] = bigpanda_api_url
      captured["bigpanda_recovery_engine_url_template"] = bigpanda_recovery_engine_url_template or ""
      captured["bigpanda_recovery_engine_token"] = bigpanda_recovery_engine_token or ""
      captured["grafana_oncall_api_token"] = grafana_oncall_api_token or ""
      captured["grafana_oncall_api_url"] = grafana_oncall_api_url
      captured["grafana_oncall_recovery_engine_url_template"] = (
        grafana_oncall_recovery_engine_url_template or ""
      )
      captured["grafana_oncall_recovery_engine_token"] = grafana_oncall_recovery_engine_token or ""
      captured["splunk_oncall_api_token"] = splunk_oncall_api_token or ""
      captured["splunk_oncall_api_url"] = splunk_oncall_api_url
      captured["splunk_oncall_recovery_engine_url_template"] = (
        splunk_oncall_recovery_engine_url_template or ""
      )
      captured["splunk_oncall_recovery_engine_token"] = splunk_oncall_recovery_engine_token or ""
      captured["jira_service_management_api_token"] = jira_service_management_api_token or ""
      captured["jira_service_management_api_url"] = jira_service_management_api_url
      captured["jira_service_management_recovery_engine_url_template"] = (
        jira_service_management_recovery_engine_url_template or ""
      )
      captured["jira_service_management_recovery_engine_token"] = (
        jira_service_management_recovery_engine_token or ""
      )
      captured["pagertree_api_token"] = pagertree_api_token or ""
      captured["pagertree_api_url"] = pagertree_api_url
      captured["pagertree_recovery_engine_url_template"] = (
        pagertree_recovery_engine_url_template or ""
      )
      captured["pagertree_recovery_engine_token"] = pagertree_recovery_engine_token or ""
      captured["alertops_api_token"] = alertops_api_token or ""
      captured["alertops_api_url"] = alertops_api_url
      captured["alertops_recovery_engine_url_template"] = (
        alertops_recovery_engine_url_template or ""
      )
      captured["alertops_recovery_engine_token"] = alertops_recovery_engine_token or ""
      captured["signl4_api_token"] = signl4_api_token or ""
      captured["signl4_api_url"] = signl4_api_url
      captured["signl4_recovery_engine_url_template"] = (
        signl4_recovery_engine_url_template or ""
      )
      captured["signl4_recovery_engine_token"] = signl4_recovery_engine_token or ""
      captured["ilert_api_token"] = ilert_api_token or ""
      captured["ilert_api_url"] = ilert_api_url
      captured["ilert_recovery_engine_url_template"] = (
        ilert_recovery_engine_url_template or ""
      )
      captured["ilert_recovery_engine_token"] = ilert_recovery_engine_token or ""
      captured["betterstack_api_token"] = betterstack_api_token or ""
      captured["betterstack_api_url"] = betterstack_api_url
      captured["betterstack_recovery_engine_url_template"] = (
        betterstack_recovery_engine_url_template or ""
      )
      captured["betterstack_recovery_engine_token"] = betterstack_recovery_engine_token or ""
      captured["onpage_api_token"] = onpage_api_token or ""
      captured["onpage_api_url"] = onpage_api_url
      captured["onpage_recovery_engine_url_template"] = (
        onpage_recovery_engine_url_template or ""
      )
      captured["onpage_recovery_engine_token"] = onpage_recovery_engine_token or ""
      captured["allquiet_api_token"] = allquiet_api_token or ""
      captured["allquiet_api_url"] = allquiet_api_url
      captured["allquiet_recovery_engine_url_template"] = (
        allquiet_recovery_engine_url_template or ""
      )
      captured["allquiet_recovery_engine_token"] = allquiet_recovery_engine_token or ""
      captured["moogsoft_api_token"] = moogsoft_api_token or ""
      captured["moogsoft_api_url"] = moogsoft_api_url
      captured["moogsoft_recovery_engine_url_template"] = (
        moogsoft_recovery_engine_url_template or ""
      )
      captured["moogsoft_recovery_engine_token"] = moogsoft_recovery_engine_token or ""
      captured["spikesh_api_token"] = spikesh_api_token or ""
      captured["spikesh_api_url"] = spikesh_api_url
      captured["spikesh_recovery_engine_url_template"] = (
        spikesh_recovery_engine_url_template or ""
      )
      captured["spikesh_recovery_engine_token"] = spikesh_recovery_engine_token or ""
      captured["dutycalls_api_token"] = dutycalls_api_token or ""
      captured["dutycalls_api_url"] = dutycalls_api_url
      captured["dutycalls_recovery_engine_url_template"] = (
        dutycalls_recovery_engine_url_template or ""
      )
      captured["dutycalls_recovery_engine_token"] = dutycalls_recovery_engine_token or ""
      captured["incidenthub_api_token"] = incidenthub_api_token or ""
      captured["incidenthub_api_url"] = incidenthub_api_url
      captured["incidenthub_recovery_engine_url_template"] = (
        incidenthub_recovery_engine_url_template or ""
      )
      captured["incidenthub_recovery_engine_token"] = incidenthub_recovery_engine_token or ""
      captured["resolver_api_token"] = resolver_api_token or ""
      captured["resolver_api_url"] = resolver_api_url
      captured["resolver_recovery_engine_url_template"] = (
        resolver_recovery_engine_url_template or ""
      )
      captured["resolver_recovery_engine_token"] = resolver_recovery_engine_token or ""
      captured["openduty_api_token"] = openduty_api_token or ""
      captured["openduty_api_url"] = openduty_api_url
      captured["openduty_recovery_engine_url_template"] = (
        openduty_recovery_engine_url_template or ""
      )
      captured["openduty_recovery_engine_token"] = openduty_recovery_engine_token or ""
      captured["cabot_api_token"] = cabot_api_token or ""
      captured["cabot_api_url"] = cabot_api_url
      captured["cabot_recovery_engine_url_template"] = (
        cabot_recovery_engine_url_template or ""
      )
      captured["cabot_recovery_engine_token"] = cabot_recovery_engine_token or ""
      captured["haloitsm_api_token"] = haloitsm_api_token or ""
      captured["haloitsm_api_url"] = haloitsm_api_url
      captured["haloitsm_recovery_engine_url_template"] = (
        haloitsm_recovery_engine_url_template or ""
      )
      captured["haloitsm_recovery_engine_token"] = haloitsm_recovery_engine_token or ""
      captured["incidentmanagerio_api_token"] = incidentmanagerio_api_token or ""
      captured["incidentmanagerio_api_url"] = incidentmanagerio_api_url
      captured["incidentmanagerio_recovery_engine_url_template"] = (
        incidentmanagerio_recovery_engine_url_template or ""
      )
      captured["incidentmanagerio_recovery_engine_token"] = (
        incidentmanagerio_recovery_engine_token or ""
      )
      captured["oneuptime_api_token"] = oneuptime_api_token or ""
      captured["oneuptime_api_url"] = oneuptime_api_url
      captured["oneuptime_recovery_engine_url_template"] = (
        oneuptime_recovery_engine_url_template or ""
      )
      captured["oneuptime_recovery_engine_token"] = oneuptime_recovery_engine_token or ""
      captured["squzy_api_token"] = squzy_api_token or ""
      captured["squzy_api_url"] = squzy_api_url
      captured["squzy_recovery_engine_url_template"] = (
        squzy_recovery_engine_url_template or ""
      )
      captured["squzy_recovery_engine_token"] = squzy_recovery_engine_token or ""
      captured["crisescontrol_api_token"] = crisescontrol_api_token or ""
      captured["crisescontrol_api_url"] = crisescontrol_api_url
      captured["crisescontrol_recovery_engine_url_template"] = (
        crisescontrol_recovery_engine_url_template or ""
      )
      captured["crisescontrol_recovery_engine_token"] = crisescontrol_recovery_engine_token or ""
      captured["freshservice_api_token"] = freshservice_api_token or ""
      captured["freshservice_api_url"] = freshservice_api_url
      captured["freshservice_recovery_engine_url_template"] = (
        freshservice_recovery_engine_url_template or ""
      )
      captured["freshservice_recovery_engine_token"] = freshservice_recovery_engine_token or ""
      captured["freshdesk_api_token"] = freshdesk_api_token or ""
      captured["freshdesk_api_url"] = freshdesk_api_url
      captured["freshdesk_recovery_engine_url_template"] = (
        freshdesk_recovery_engine_url_template or ""
      )
      captured["freshdesk_recovery_engine_token"] = freshdesk_recovery_engine_token or ""
      captured["servicedeskplus_api_token"] = servicedeskplus_api_token or ""
      captured["servicedeskplus_api_url"] = servicedeskplus_api_url
      captured["servicedeskplus_recovery_engine_url_template"] = (
        servicedeskplus_recovery_engine_url_template or ""
      )
      captured["servicedeskplus_recovery_engine_token"] = servicedeskplus_recovery_engine_token or ""
      captured["sysaid_api_token"] = sysaid_api_token or ""
      captured["sysaid_api_url"] = sysaid_api_url
      captured["sysaid_recovery_engine_url_template"] = sysaid_recovery_engine_url_template or ""
      captured["sysaid_recovery_engine_token"] = sysaid_recovery_engine_token or ""
      captured["bmchelix_api_token"] = bmchelix_api_token or ""
      captured["bmchelix_api_url"] = bmchelix_api_url
      captured["bmchelix_recovery_engine_url_template"] = bmchelix_recovery_engine_url_template or ""
      captured["bmchelix_recovery_engine_token"] = bmchelix_recovery_engine_token or ""
      captured["solarwindsservicedesk_api_token"] = solarwindsservicedesk_api_token or ""
      captured["solarwindsservicedesk_api_url"] = solarwindsservicedesk_api_url
      captured["solarwindsservicedesk_recovery_engine_url_template"] = (
        solarwindsservicedesk_recovery_engine_url_template or ""
      )
      captured["solarwindsservicedesk_recovery_engine_token"] = (
        solarwindsservicedesk_recovery_engine_token or ""
      )
      captured["topdesk_api_token"] = topdesk_api_token or ""
      captured["topdesk_api_url"] = topdesk_api_url
      captured["topdesk_recovery_engine_url_template"] = topdesk_recovery_engine_url_template or ""
      captured["topdesk_recovery_engine_token"] = topdesk_recovery_engine_token or ""
      captured["invgateservicedesk_api_token"] = invgateservicedesk_api_token or ""
      captured["invgateservicedesk_api_url"] = invgateservicedesk_api_url
      captured["invgateservicedesk_recovery_engine_url_template"] = (
        invgateservicedesk_recovery_engine_url_template or ""
      )
      captured["invgateservicedesk_recovery_engine_token"] = (
        invgateservicedesk_recovery_engine_token or ""
      )
      captured["opsramp_api_token"] = opsramp_api_token or ""
      captured["opsramp_api_url"] = opsramp_api_url
      captured["opsramp_recovery_engine_url_template"] = (
        opsramp_recovery_engine_url_template or ""
      )
      captured["opsramp_recovery_engine_token"] = opsramp_recovery_engine_token or ""
      captured["zenduty_api_token"] = zenduty_api_token or ""
      captured["zenduty_api_url"] = zenduty_api_url
      captured["zenduty_recovery_engine_url_template"] = zenduty_recovery_engine_url_template or ""
      captured["zenduty_recovery_engine_token"] = zenduty_recovery_engine_token or ""
      captured["opsgenie_api_key"] = opsgenie_api_key or ""
      captured["opsgenie_api_url"] = opsgenie_api_url
      captured["opsgenie_recovery_engine_url_template"] = opsgenie_recovery_engine_url_template or ""
      captured["opsgenie_recovery_engine_api_key"] = opsgenie_recovery_engine_api_key or ""
      captured["webhook_timeout_seconds"] = str(webhook_timeout_seconds)

    def list_targets(self) -> tuple[str, ...]:
      return ("operator_console",)

    def list_supported_workflow_providers(self) -> tuple[str, ...]:
      return ("pagerduty", "opsgenie")

    def deliver(self, *, incident, targets=None, attempt_number: int = 1, phase: str = "initial"):
      return ()

    def sync_incident_workflow(
      self,
      *,
      incident,
      provider: str,
      action: str,
      actor: str,
      detail: str,
      payload=None,
      attempt_number: int = 1,
    ):
      return ()

    def pull_incident_workflow_state(
      self,
      *,
      incident,
      provider: str,
    ):
      return None

  monkeypatch.setattr("akra_trader.bootstrap.SqlAlchemyRunRepository", FakeRunRepository)
  monkeypatch.setattr("akra_trader.bootstrap.SqlAlchemyGuardedLiveStateRepository", FakeGuardedLiveRepository)
  monkeypatch.setattr("akra_trader.bootstrap.OperatorAlertDeliveryAdapter", FakeOperatorAlertDeliveryAdapter)

  container = build_container(
    Settings(
      market_data_provider="seeded",
      operator_alert_delivery_targets=("console", "slack", "pagerduty", "webhook"),
      operator_alert_escalation_targets=("pagerduty", "slack"),
      operator_alert_webhook_url="https://ops.example.com/alert",
      operator_alert_slack_webhook_url="https://hooks.slack.example/services/ops",
      operator_alert_pagerduty_integration_key="pagerduty-key",
      operator_alert_pagerduty_api_token="pagerduty-api-token",
      operator_alert_pagerduty_from_email="akra-ops@example.com",
      operator_alert_pagerduty_recovery_engine_url_template=(
        "https://pagerduty.example/recovery/{job_id_urlencoded}"
      ),
      operator_alert_pagerduty_recovery_engine_token="pagerduty-recovery-token",
      operator_alert_incidentio_api_token="incidentio-token",
      operator_alert_incidentio_api_url="https://api.incidentio.example",
      operator_alert_incidentio_recovery_engine_url_template=(
        "https://incidentio.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_incidentio_recovery_engine_token="incidentio-recovery-token",
      operator_alert_firehydrant_api_token="firehydrant-token",
      operator_alert_firehydrant_api_url="https://api.firehydrant.example",
      operator_alert_firehydrant_recovery_engine_url_template=(
        "https://firehydrant.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_firehydrant_recovery_engine_token="firehydrant-recovery-token",
      operator_alert_rootly_api_token="rootly-token",
      operator_alert_rootly_api_url="https://api.rootly.example",
      operator_alert_rootly_recovery_engine_url_template=(
        "https://rootly.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_rootly_recovery_engine_token="rootly-recovery-token",
      operator_alert_blameless_api_token="blameless-token",
      operator_alert_blameless_api_url="https://api.blameless.example",
      operator_alert_blameless_recovery_engine_url_template=(
        "https://blameless.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_blameless_recovery_engine_token="blameless-recovery-token",
      operator_alert_xmatters_api_token="xmatters-token",
      operator_alert_xmatters_api_url="https://api.xmatters.example",
      operator_alert_xmatters_recovery_engine_url_template=(
        "https://xmatters.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_xmatters_recovery_engine_token="xmatters-recovery-token",
      operator_alert_servicenow_api_token="servicenow-token",
      operator_alert_servicenow_api_url="https://api.servicenow.example",
      operator_alert_servicenow_recovery_engine_url_template=(
        "https://servicenow.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_servicenow_recovery_engine_token="servicenow-recovery-token",
      operator_alert_squadcast_api_token="squadcast-token",
      operator_alert_squadcast_api_url="https://api.squadcast.example",
      operator_alert_squadcast_recovery_engine_url_template=(
        "https://squadcast.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_squadcast_recovery_engine_token="squadcast-recovery-token",
      operator_alert_bigpanda_api_token="bigpanda-token",
      operator_alert_bigpanda_api_url="https://api.bigpanda.example",
      operator_alert_bigpanda_recovery_engine_url_template=(
        "https://bigpanda.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_bigpanda_recovery_engine_token="bigpanda-recovery-token",
      operator_alert_grafana_oncall_api_token="grafana-oncall-token",
      operator_alert_grafana_oncall_api_url="https://oncall-api.grafana.example",
      operator_alert_grafana_oncall_recovery_engine_url_template=(
        "https://grafana-oncall.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_grafana_oncall_recovery_engine_token="grafana-oncall-recovery-token",
      operator_alert_splunk_oncall_api_token="splunk-oncall-token",
      operator_alert_splunk_oncall_api_url="https://api.splunkoncall.example",
      operator_alert_splunk_oncall_recovery_engine_url_template=(
        "https://splunk-oncall.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_splunk_oncall_recovery_engine_token="splunk-oncall-recovery-token",
      operator_alert_jira_service_management_api_token="jsm-token",
      operator_alert_jira_service_management_api_url="https://api.jsm.example",
      operator_alert_jira_service_management_recovery_engine_url_template=(
        "https://jsm.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_jira_service_management_recovery_engine_token="jsm-recovery-token",
      operator_alert_pagertree_api_token="pagertree-token",
      operator_alert_pagertree_api_url="https://api.pagertree.example",
      operator_alert_pagertree_recovery_engine_url_template=(
        "https://pagertree.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_pagertree_recovery_engine_token="pagertree-recovery-token",
      operator_alert_alertops_api_token="alertops-token",
      operator_alert_alertops_api_url="https://api.alertops.example",
      operator_alert_alertops_recovery_engine_url_template=(
        "https://alertops.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_alertops_recovery_engine_token="alertops-recovery-token",
      operator_alert_signl4_api_token="signl4-token",
      operator_alert_signl4_api_url="https://api.signl4.example",
      operator_alert_signl4_recovery_engine_url_template=(
        "https://signl4.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_signl4_recovery_engine_token="signl4-recovery-token",
      operator_alert_ilert_api_token="ilert-token",
      operator_alert_ilert_api_url="https://api.ilert.example",
      operator_alert_ilert_recovery_engine_url_template=(
        "https://ilert.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_ilert_recovery_engine_token="ilert-recovery-token",
      operator_alert_betterstack_api_token="betterstack-token",
      operator_alert_betterstack_api_url="https://api.betterstack.example",
      operator_alert_betterstack_recovery_engine_url_template=(
        "https://betterstack.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_betterstack_recovery_engine_token="betterstack-recovery-token",
      operator_alert_onpage_api_token="onpage-token",
      operator_alert_onpage_api_url="https://api.onpage.example",
      operator_alert_onpage_recovery_engine_url_template=(
        "https://onpage.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_onpage_recovery_engine_token="onpage-recovery-token",
      operator_alert_allquiet_api_token="allquiet-token",
      operator_alert_allquiet_api_url="https://api.allquiet.example",
      operator_alert_allquiet_recovery_engine_url_template=(
        "https://allquiet.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_allquiet_recovery_engine_token="allquiet-recovery-token",
      operator_alert_moogsoft_api_token="moogsoft-token",
      operator_alert_moogsoft_api_url="https://api.moogsoft.example",
      operator_alert_moogsoft_recovery_engine_url_template=(
        "https://moogsoft.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_moogsoft_recovery_engine_token="moogsoft-recovery-token",
      operator_alert_spikesh_api_token="spikesh-token",
      operator_alert_spikesh_api_url="https://api.spikesh.example",
      operator_alert_spikesh_recovery_engine_url_template=(
        "https://spikesh.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_spikesh_recovery_engine_token="spikesh-recovery-token",
      operator_alert_dutycalls_api_token="dutycalls-token",
      operator_alert_dutycalls_api_url="https://api.dutycalls.example",
      operator_alert_dutycalls_recovery_engine_url_template=(
        "https://dutycalls.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_dutycalls_recovery_engine_token="dutycalls-recovery-token",
      operator_alert_incidenthub_api_token="incidenthub-token",
      operator_alert_incidenthub_api_url="https://api.incidenthub.example",
      operator_alert_incidenthub_recovery_engine_url_template=(
        "https://incidenthub.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_incidenthub_recovery_engine_token="incidenthub-recovery-token",
      operator_alert_resolver_api_token="resolver-token",
      operator_alert_resolver_api_url="https://api.resolver.example",
      operator_alert_resolver_recovery_engine_url_template=(
        "https://resolver.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_resolver_recovery_engine_token="resolver-recovery-token",
      operator_alert_openduty_api_token="openduty-token",
      operator_alert_openduty_api_url="https://api.openduty.example",
      operator_alert_openduty_recovery_engine_url_template=(
        "https://openduty.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_openduty_recovery_engine_token="openduty-recovery-token",
      operator_alert_cabot_api_token="cabot-token",
      operator_alert_cabot_api_url="https://api.cabot.example",
      operator_alert_cabot_recovery_engine_url_template=(
        "https://cabot.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_cabot_recovery_engine_token="cabot-recovery-token",
      operator_alert_haloitsm_api_token="haloitsm-token",
      operator_alert_haloitsm_api_url="https://api.haloitsm.example",
      operator_alert_haloitsm_recovery_engine_url_template=(
        "https://haloitsm.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_haloitsm_recovery_engine_token="haloitsm-recovery-token",
      operator_alert_incidentmanagerio_api_token="incidentmanagerio-token",
      operator_alert_incidentmanagerio_api_url="https://api.incidentmanagerio.example",
      operator_alert_incidentmanagerio_recovery_engine_url_template=(
        "https://incidentmanagerio.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_incidentmanagerio_recovery_engine_token="incidentmanagerio-recovery-token",
      operator_alert_oneuptime_api_token="oneuptime-token",
      operator_alert_oneuptime_api_url="https://api.oneuptime.example",
      operator_alert_oneuptime_recovery_engine_url_template=(
        "https://oneuptime.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_oneuptime_recovery_engine_token="oneuptime-recovery-token",
      operator_alert_squzy_api_token="squzy-token",
      operator_alert_squzy_api_url="https://api.squzy.example",
      operator_alert_squzy_recovery_engine_url_template=(
        "https://squzy.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_squzy_recovery_engine_token="squzy-recovery-token",
      operator_alert_crisescontrol_api_token="crisescontrol-token",
      operator_alert_crisescontrol_api_url="https://api.crisescontrol.example",
      operator_alert_crisescontrol_recovery_engine_url_template=(
        "https://crisescontrol.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_crisescontrol_recovery_engine_token="crisescontrol-recovery-token",
      operator_alert_freshservice_api_token="freshservice-token",
      operator_alert_freshservice_api_url="https://api.freshservice.example",
      operator_alert_freshservice_recovery_engine_url_template=(
        "https://freshservice.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_freshservice_recovery_engine_token="freshservice-recovery-token",
      operator_alert_freshdesk_api_token="freshdesk-token",
      operator_alert_freshdesk_api_url="https://api.freshdesk.example",
      operator_alert_freshdesk_recovery_engine_url_template=(
        "https://freshdesk.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_freshdesk_recovery_engine_token="freshdesk-recovery-token",
      operator_alert_servicedeskplus_api_token="servicedeskplus-token",
      operator_alert_servicedeskplus_api_url="https://api.servicedeskplus.example",
      operator_alert_servicedeskplus_recovery_engine_url_template=(
        "https://servicedeskplus.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_servicedeskplus_recovery_engine_token="servicedeskplus-recovery-token",
      operator_alert_sysaid_api_token="sysaid-token",
      operator_alert_sysaid_api_url="https://api.sysaid.example",
      operator_alert_sysaid_recovery_engine_url_template=(
        "https://sysaid.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_sysaid_recovery_engine_token="sysaid-recovery-token",
      operator_alert_bmchelix_api_token="bmchelix-token",
      operator_alert_bmchelix_api_url="https://api.bmchelix.example",
      operator_alert_bmchelix_recovery_engine_url_template=(
        "https://bmchelix.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_bmchelix_recovery_engine_token="bmchelix-recovery-token",
      operator_alert_solarwindsservicedesk_api_token="solarwindsservicedesk-token",
      operator_alert_solarwindsservicedesk_api_url="https://api.solarwindsservicedesk.example",
      operator_alert_solarwindsservicedesk_recovery_engine_url_template=(
        "https://solarwindsservicedesk.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_solarwindsservicedesk_recovery_engine_token=(
        "solarwindsservicedesk-recovery-token"
      ),
      operator_alert_topdesk_api_token="topdesk-token",
      operator_alert_topdesk_api_url="https://api.topdesk.example",
      operator_alert_topdesk_recovery_engine_url_template=(
        "https://topdesk.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_topdesk_recovery_engine_token="topdesk-recovery-token",
      operator_alert_invgateservicedesk_api_token="invgateservicedesk-token",
      operator_alert_invgateservicedesk_api_url="https://api.invgateservicedesk.example",
      operator_alert_invgateservicedesk_recovery_engine_url_template=(
        "https://invgateservicedesk.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_invgateservicedesk_recovery_engine_token=(
        "invgateservicedesk-recovery-token"
      ),
      operator_alert_opsramp_api_token="opsramp-token",
      operator_alert_opsramp_api_url="https://api.opsramp.example",
      operator_alert_opsramp_recovery_engine_url_template=(
        "https://opsramp.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_opsramp_recovery_engine_token="opsramp-recovery-token",
      operator_alert_zenduty_api_token="zenduty-token",
      operator_alert_zenduty_api_url="https://api.zenduty.example",
      operator_alert_zenduty_recovery_engine_url_template=(
        "https://zenduty.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_zenduty_recovery_engine_token="zenduty-recovery-token",
      operator_alert_opsgenie_api_key="opsgenie-key",
      operator_alert_opsgenie_api_url="https://api.opsgenie.example",
      operator_alert_opsgenie_recovery_engine_url_template=(
        "https://opsgenie.example/recovery/{workflow_reference_urlencoded}"
      ),
      operator_alert_opsgenie_recovery_engine_api_key="opsgenie-recovery-key",
      operator_alert_webhook_timeout_seconds=7,
      operator_alert_paging_policy_default_provider="pagerduty",
      operator_alert_paging_policy_warning_targets=("slack", "pagerduty"),
      operator_alert_paging_policy_critical_targets=("slack", "pagerduty"),
      operator_alert_paging_policy_warning_escalation_targets=("pagerduty",),
      operator_alert_paging_policy_critical_escalation_targets=("pagerduty",),
      operator_alert_external_sync_token="shared-token",
      operator_alert_incident_ack_timeout_seconds=180,
      operator_alert_incident_max_escalations=3,
      operator_alert_incident_escalation_backoff_multiplier=3.0,
    )
  )

  assert captured["targets"] == "console,slack,pagerduty,webhook"
  assert captured["webhook_url"] == "https://ops.example.com/alert"
  assert captured["slack_webhook_url"] == "https://hooks.slack.example/services/ops"
  assert captured["pagerduty_integration_key"] == "pagerduty-key"
  assert captured["pagerduty_api_token"] == "pagerduty-api-token"
  assert captured["pagerduty_from_email"] == "akra-ops@example.com"
  assert captured["pagerduty_recovery_engine_url_template"] == "https://pagerduty.example/recovery/{job_id_urlencoded}"
  assert captured["pagerduty_recovery_engine_token"] == "pagerduty-recovery-token"
  assert captured["incidentio_api_token"] == "incidentio-token"
  assert captured["incidentio_api_url"] == "https://api.incidentio.example"
  assert captured["incidentio_recovery_engine_url_template"] == "https://incidentio.example/recovery/{workflow_reference_urlencoded}"
  assert captured["incidentio_recovery_engine_token"] == "incidentio-recovery-token"
  assert captured["firehydrant_api_token"] == "firehydrant-token"
  assert captured["firehydrant_api_url"] == "https://api.firehydrant.example"
  assert captured["firehydrant_recovery_engine_url_template"] == "https://firehydrant.example/recovery/{workflow_reference_urlencoded}"
  assert captured["firehydrant_recovery_engine_token"] == "firehydrant-recovery-token"
  assert captured["rootly_api_token"] == "rootly-token"
  assert captured["rootly_api_url"] == "https://api.rootly.example"
  assert captured["rootly_recovery_engine_url_template"] == "https://rootly.example/recovery/{workflow_reference_urlencoded}"
  assert captured["rootly_recovery_engine_token"] == "rootly-recovery-token"
  assert captured["blameless_api_token"] == "blameless-token"
  assert captured["blameless_api_url"] == "https://api.blameless.example"
  assert captured["blameless_recovery_engine_url_template"] == "https://blameless.example/recovery/{workflow_reference_urlencoded}"
  assert captured["blameless_recovery_engine_token"] == "blameless-recovery-token"
  assert captured["xmatters_api_token"] == "xmatters-token"
  assert captured["xmatters_api_url"] == "https://api.xmatters.example"
  assert captured["xmatters_recovery_engine_url_template"] == "https://xmatters.example/recovery/{workflow_reference_urlencoded}"
  assert captured["xmatters_recovery_engine_token"] == "xmatters-recovery-token"
  assert captured["servicenow_api_token"] == "servicenow-token"
  assert captured["servicenow_api_url"] == "https://api.servicenow.example"
  assert captured["servicenow_recovery_engine_url_template"] == "https://servicenow.example/recovery/{workflow_reference_urlencoded}"
  assert captured["servicenow_recovery_engine_token"] == "servicenow-recovery-token"
  assert captured["squadcast_api_token"] == "squadcast-token"
  assert captured["squadcast_api_url"] == "https://api.squadcast.example"
  assert captured["squadcast_recovery_engine_url_template"] == "https://squadcast.example/recovery/{workflow_reference_urlencoded}"
  assert captured["squadcast_recovery_engine_token"] == "squadcast-recovery-token"
  assert captured["bigpanda_api_token"] == "bigpanda-token"
  assert captured["bigpanda_api_url"] == "https://api.bigpanda.example"
  assert captured["bigpanda_recovery_engine_url_template"] == "https://bigpanda.example/recovery/{workflow_reference_urlencoded}"
  assert captured["bigpanda_recovery_engine_token"] == "bigpanda-recovery-token"
  assert captured["grafana_oncall_api_token"] == "grafana-oncall-token"
  assert captured["grafana_oncall_api_url"] == "https://oncall-api.grafana.example"
  assert captured["grafana_oncall_recovery_engine_url_template"] == "https://grafana-oncall.example/recovery/{workflow_reference_urlencoded}"
  assert captured["grafana_oncall_recovery_engine_token"] == "grafana-oncall-recovery-token"
  assert captured["splunk_oncall_api_token"] == "splunk-oncall-token"
  assert captured["splunk_oncall_api_url"] == "https://api.splunkoncall.example"
  assert captured["splunk_oncall_recovery_engine_url_template"] == "https://splunk-oncall.example/recovery/{workflow_reference_urlencoded}"
  assert captured["splunk_oncall_recovery_engine_token"] == "splunk-oncall-recovery-token"
  assert captured["jira_service_management_api_token"] == "jsm-token"
  assert captured["jira_service_management_api_url"] == "https://api.jsm.example"
  assert captured["jira_service_management_recovery_engine_url_template"] == "https://jsm.example/recovery/{workflow_reference_urlencoded}"
  assert captured["jira_service_management_recovery_engine_token"] == "jsm-recovery-token"
  assert captured["pagertree_api_token"] == "pagertree-token"
  assert captured["pagertree_api_url"] == "https://api.pagertree.example"
  assert captured["pagertree_recovery_engine_url_template"] == "https://pagertree.example/recovery/{workflow_reference_urlencoded}"
  assert captured["pagertree_recovery_engine_token"] == "pagertree-recovery-token"
  assert captured["alertops_api_token"] == "alertops-token"
  assert captured["alertops_api_url"] == "https://api.alertops.example"
  assert captured["alertops_recovery_engine_url_template"] == "https://alertops.example/recovery/{workflow_reference_urlencoded}"
  assert captured["alertops_recovery_engine_token"] == "alertops-recovery-token"
  assert captured["signl4_api_token"] == "signl4-token"
  assert captured["signl4_api_url"] == "https://api.signl4.example"
  assert captured["signl4_recovery_engine_url_template"] == "https://signl4.example/recovery/{workflow_reference_urlencoded}"
  assert captured["signl4_recovery_engine_token"] == "signl4-recovery-token"
  assert captured["ilert_api_token"] == "ilert-token"
  assert captured["ilert_api_url"] == "https://api.ilert.example"
  assert captured["ilert_recovery_engine_url_template"] == "https://ilert.example/recovery/{workflow_reference_urlencoded}"
  assert captured["ilert_recovery_engine_token"] == "ilert-recovery-token"
  assert captured["betterstack_api_token"] == "betterstack-token"
  assert captured["betterstack_api_url"] == "https://api.betterstack.example"
  assert captured["betterstack_recovery_engine_url_template"] == "https://betterstack.example/recovery/{workflow_reference_urlencoded}"
  assert captured["betterstack_recovery_engine_token"] == "betterstack-recovery-token"
  assert captured["onpage_api_token"] == "onpage-token"
  assert captured["onpage_api_url"] == "https://api.onpage.example"
  assert captured["onpage_recovery_engine_url_template"] == "https://onpage.example/recovery/{workflow_reference_urlencoded}"
  assert captured["onpage_recovery_engine_token"] == "onpage-recovery-token"
  assert captured["allquiet_api_token"] == "allquiet-token"
  assert captured["allquiet_api_url"] == "https://api.allquiet.example"
  assert captured["allquiet_recovery_engine_url_template"] == "https://allquiet.example/recovery/{workflow_reference_urlencoded}"
  assert captured["allquiet_recovery_engine_token"] == "allquiet-recovery-token"
  assert captured["moogsoft_api_token"] == "moogsoft-token"
  assert captured["moogsoft_api_url"] == "https://api.moogsoft.example"
  assert captured["moogsoft_recovery_engine_url_template"] == "https://moogsoft.example/recovery/{workflow_reference_urlencoded}"
  assert captured["moogsoft_recovery_engine_token"] == "moogsoft-recovery-token"
  assert captured["spikesh_api_token"] == "spikesh-token"
  assert captured["spikesh_api_url"] == "https://api.spikesh.example"
  assert captured["spikesh_recovery_engine_url_template"] == "https://spikesh.example/recovery/{workflow_reference_urlencoded}"
  assert captured["spikesh_recovery_engine_token"] == "spikesh-recovery-token"
  assert captured["dutycalls_api_token"] == "dutycalls-token"
  assert captured["dutycalls_api_url"] == "https://api.dutycalls.example"
  assert captured["dutycalls_recovery_engine_url_template"] == "https://dutycalls.example/recovery/{workflow_reference_urlencoded}"
  assert captured["dutycalls_recovery_engine_token"] == "dutycalls-recovery-token"
  assert captured["incidenthub_api_token"] == "incidenthub-token"
  assert captured["incidenthub_api_url"] == "https://api.incidenthub.example"
  assert captured["incidenthub_recovery_engine_url_template"] == "https://incidenthub.example/recovery/{workflow_reference_urlencoded}"
  assert captured["incidenthub_recovery_engine_token"] == "incidenthub-recovery-token"
  assert captured["resolver_api_token"] == "resolver-token"
  assert captured["resolver_api_url"] == "https://api.resolver.example"
  assert captured["resolver_recovery_engine_url_template"] == "https://resolver.example/recovery/{workflow_reference_urlencoded}"
  assert captured["resolver_recovery_engine_token"] == "resolver-recovery-token"
  assert captured["openduty_api_token"] == "openduty-token"
  assert captured["openduty_api_url"] == "https://api.openduty.example"
  assert captured["openduty_recovery_engine_url_template"] == "https://openduty.example/recovery/{workflow_reference_urlencoded}"
  assert captured["openduty_recovery_engine_token"] == "openduty-recovery-token"
  assert captured["cabot_api_token"] == "cabot-token"
  assert captured["cabot_api_url"] == "https://api.cabot.example"
  assert captured["cabot_recovery_engine_url_template"] == "https://cabot.example/recovery/{workflow_reference_urlencoded}"
  assert captured["cabot_recovery_engine_token"] == "cabot-recovery-token"
  assert captured["haloitsm_api_token"] == "haloitsm-token"
  assert captured["haloitsm_api_url"] == "https://api.haloitsm.example"
  assert captured["haloitsm_recovery_engine_url_template"] == "https://haloitsm.example/recovery/{workflow_reference_urlencoded}"
  assert captured["haloitsm_recovery_engine_token"] == "haloitsm-recovery-token"
  assert captured["incidentmanagerio_api_token"] == "incidentmanagerio-token"
  assert captured["incidentmanagerio_api_url"] == "https://api.incidentmanagerio.example"
  assert captured["incidentmanagerio_recovery_engine_url_template"] == "https://incidentmanagerio.example/recovery/{workflow_reference_urlencoded}"
  assert captured["incidentmanagerio_recovery_engine_token"] == "incidentmanagerio-recovery-token"
  assert captured["oneuptime_api_token"] == "oneuptime-token"
  assert captured["oneuptime_api_url"] == "https://api.oneuptime.example"
  assert captured["oneuptime_recovery_engine_url_template"] == "https://oneuptime.example/recovery/{workflow_reference_urlencoded}"
  assert captured["oneuptime_recovery_engine_token"] == "oneuptime-recovery-token"
  assert captured["squzy_api_token"] == "squzy-token"
  assert captured["squzy_api_url"] == "https://api.squzy.example"
  assert captured["squzy_recovery_engine_url_template"] == "https://squzy.example/recovery/{workflow_reference_urlencoded}"
  assert captured["squzy_recovery_engine_token"] == "squzy-recovery-token"
  assert captured["crisescontrol_api_token"] == "crisescontrol-token"
  assert captured["crisescontrol_api_url"] == "https://api.crisescontrol.example"
  assert captured["crisescontrol_recovery_engine_url_template"] == "https://crisescontrol.example/recovery/{workflow_reference_urlencoded}"
  assert captured["crisescontrol_recovery_engine_token"] == "crisescontrol-recovery-token"
  assert captured["freshservice_api_token"] == "freshservice-token"
  assert captured["freshservice_api_url"] == "https://api.freshservice.example"
  assert captured["freshservice_recovery_engine_url_template"] == "https://freshservice.example/recovery/{workflow_reference_urlencoded}"
  assert captured["freshservice_recovery_engine_token"] == "freshservice-recovery-token"
  assert captured["freshdesk_api_token"] == "freshdesk-token"
  assert captured["freshdesk_api_url"] == "https://api.freshdesk.example"
  assert captured["freshdesk_recovery_engine_url_template"] == "https://freshdesk.example/recovery/{workflow_reference_urlencoded}"
  assert captured["freshdesk_recovery_engine_token"] == "freshdesk-recovery-token"
  assert captured["servicedeskplus_api_token"] == "servicedeskplus-token"
  assert captured["servicedeskplus_api_url"] == "https://api.servicedeskplus.example"
  assert captured["servicedeskplus_recovery_engine_url_template"] == "https://servicedeskplus.example/recovery/{workflow_reference_urlencoded}"
  assert captured["servicedeskplus_recovery_engine_token"] == "servicedeskplus-recovery-token"
  assert captured["sysaid_api_token"] == "sysaid-token"
  assert captured["sysaid_api_url"] == "https://api.sysaid.example"
  assert captured["sysaid_recovery_engine_url_template"] == "https://sysaid.example/recovery/{workflow_reference_urlencoded}"
  assert captured["sysaid_recovery_engine_token"] == "sysaid-recovery-token"
  assert captured["bmchelix_api_token"] == "bmchelix-token"
  assert captured["bmchelix_api_url"] == "https://api.bmchelix.example"
  assert captured["bmchelix_recovery_engine_url_template"] == "https://bmchelix.example/recovery/{workflow_reference_urlencoded}"
  assert captured["bmchelix_recovery_engine_token"] == "bmchelix-recovery-token"
  assert captured["solarwindsservicedesk_api_token"] == "solarwindsservicedesk-token"
  assert captured["solarwindsservicedesk_api_url"] == "https://api.solarwindsservicedesk.example"
  assert captured["solarwindsservicedesk_recovery_engine_url_template"] == (
    "https://solarwindsservicedesk.example/recovery/{workflow_reference_urlencoded}"
  )
  assert captured["solarwindsservicedesk_recovery_engine_token"] == (
    "solarwindsservicedesk-recovery-token"
  )
  assert captured["topdesk_api_token"] == "topdesk-token"
  assert captured["topdesk_api_url"] == "https://api.topdesk.example"
  assert captured["topdesk_recovery_engine_url_template"] == (
    "https://topdesk.example/recovery/{workflow_reference_urlencoded}"
  )
  assert captured["topdesk_recovery_engine_token"] == "topdesk-recovery-token"
  assert captured["invgateservicedesk_api_token"] == "invgateservicedesk-token"
  assert captured["invgateservicedesk_api_url"] == "https://api.invgateservicedesk.example"
  assert captured["invgateservicedesk_recovery_engine_url_template"] == (
    "https://invgateservicedesk.example/recovery/{workflow_reference_urlencoded}"
  )
  assert captured["invgateservicedesk_recovery_engine_token"] == (
    "invgateservicedesk-recovery-token"
  )
  assert captured["opsramp_api_token"] == "opsramp-token"
  assert captured["opsramp_api_url"] == "https://api.opsramp.example"
  assert captured["opsramp_recovery_engine_url_template"] == "https://opsramp.example/recovery/{workflow_reference_urlencoded}"
  assert captured["opsramp_recovery_engine_token"] == "opsramp-recovery-token"
  assert captured["zenduty_api_token"] == "zenduty-token"
  assert captured["zenduty_api_url"] == "https://api.zenduty.example"
  assert captured["zenduty_recovery_engine_url_template"] == "https://zenduty.example/recovery/{workflow_reference_urlencoded}"
  assert captured["zenduty_recovery_engine_token"] == "zenduty-recovery-token"
  assert captured["opsgenie_api_key"] == "opsgenie-key"
  assert captured["opsgenie_api_url"] == "https://api.opsgenie.example"
  assert captured["opsgenie_recovery_engine_url_template"] == "https://opsgenie.example/recovery/{workflow_reference_urlencoded}"
  assert captured["opsgenie_recovery_engine_api_key"] == "opsgenie-recovery-key"
  assert captured["webhook_timeout_seconds"] == "7"
  assert container.app._operator_alert_paging_policy_default_provider == "pagerduty"
  assert container.app._operator_alert_paging_policy_warning_targets == (
    "slack",
    "pagerduty",
  )
  assert container.app._operator_alert_paging_policy_critical_escalation_targets == ("pagerduty",)
  assert container.app._operator_alert_external_sync_token == "shared-token"
  assert container.app._operator_alert_escalation_targets == ("pagerduty", "slack")
  assert container.app._operator_alert_incident_ack_timeout_seconds == 180
  assert container.app._operator_alert_incident_max_escalations == 3
  assert container.app._operator_alert_incident_escalation_backoff_multiplier == 3.0


def test_build_container_reuses_runs_database_for_binance_market_data(monkeypatch) -> None:
  captured: dict[str, str] = {}

  class FakeRunRepository:
    def __init__(self, database_url: str) -> None:
      self.database_url = database_url

  class FakeGuardedLiveRepository:
    def __init__(self, database_url: str) -> None:
      captured["guarded_live_database_url"] = database_url

  class FakeCcxtVenueStateAdapter:
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

  class FakeBinanceVenueExecutionAdapter:
    def __init__(
      self,
      *,
      venue: str = "binance",
      api_key: str | None,
      api_secret: str | None,
    ) -> None:
      captured["venue_execution_venue"] = venue
      captured["venue_execution_api_key"] = api_key or ""
      captured["venue_execution_api_secret"] = api_secret or ""

  class FakeCcxtMarketDataAdapter:
    def __init__(
      self,
      *,
      database_url: str,
      venue: str,
      tracked_symbols: tuple[str, ...],
      default_candle_limit: int,
      historical_candle_limit: int,
    ) -> None:
      captured["database_url"] = database_url
      captured["market_data_venue"] = venue
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
  monkeypatch.setattr("akra_trader.bootstrap.CcxtMarketDataAdapter", FakeCcxtMarketDataAdapter)
  monkeypatch.setattr("akra_trader.bootstrap.CcxtVenueStateAdapter", FakeCcxtVenueStateAdapter)
  monkeypatch.setattr("akra_trader.bootstrap.BinanceVenueExecutionAdapter", FakeBinanceVenueExecutionAdapter)
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
  assert captured["market_data_venue"] == "binance"
  assert captured["tracked_symbols"] == "BTC/USDT"
  assert captured["venue_state_symbols"] == "BTC/USDT"
  assert captured["venue_state_api_key"] == "test-key"
  assert captured["venue_state_api_secret"] == "test-secret"
  assert captured["venue_execution_venue"] == "binance"
  assert captured["venue_execution_api_key"] == "test-key"
  assert captured["venue_execution_api_secret"] == "test-secret"
  assert captured["sync_timeframes"] == "5m,1h"
  assert captured["sync_interval_seconds"] == "120"
  assert captured["sandbox_interval_seconds"] == "11"
  assert captured["default_candle_limit"] == "144"
  assert captured["historical_candle_limit"] == "720"
  assert container.app._guarded_live_market_data_timeframes == ("5m", "1h")
  assert len(container.background_jobs) == 2


def test_build_container_supports_non_binance_ccxt_market_data_provider(monkeypatch) -> None:
  captured: dict[str, str] = {}

  class FakeRunRepository:
    def __init__(self, database_url: str) -> None:
      self.database_url = database_url

  class FakeGuardedLiveRepository:
    def __init__(self, database_url: str) -> None:
      self.database_url = database_url

  class FakeCcxtMarketDataAdapter:
    def __init__(
      self,
      *,
      database_url: str,
      venue: str,
      tracked_symbols: tuple[str, ...],
      default_candle_limit: int,
      historical_candle_limit: int,
    ) -> None:
      captured["database_url"] = database_url
      captured["market_data_venue"] = venue
      captured["tracked_symbols"] = ",".join(tracked_symbols)
      captured["default_candle_limit"] = str(default_candle_limit)
      captured["historical_candle_limit"] = str(historical_candle_limit)

  class FakeCcxtVenueStateAdapter:
    def __init__(
      self,
      *,
      tracked_symbols: tuple[str, ...],
      venue: str = "binance",
      api_key: str | None,
      api_secret: str | None,
    ) -> None:
      captured["venue_state_venue"] = venue

  class FakeBinanceVenueExecutionAdapter:
    def __init__(
      self,
      *,
      venue: str = "binance",
      api_key: str | None,
      api_secret: str | None,
    ) -> None:
      captured["venue_execution_venue"] = venue

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
      self._application = application

    async def start(self) -> None:
      return None

    async def stop(self) -> None:
      return None

  monkeypatch.setattr("akra_trader.bootstrap.SqlAlchemyRunRepository", FakeRunRepository)
  monkeypatch.setattr("akra_trader.bootstrap.SqlAlchemyGuardedLiveStateRepository", FakeGuardedLiveRepository)
  monkeypatch.setattr("akra_trader.bootstrap.CcxtMarketDataAdapter", FakeCcxtMarketDataAdapter)
  monkeypatch.setattr("akra_trader.bootstrap.CcxtVenueStateAdapter", FakeCcxtVenueStateAdapter)
  monkeypatch.setattr("akra_trader.bootstrap.BinanceVenueExecutionAdapter", FakeBinanceVenueExecutionAdapter)
  monkeypatch.setattr("akra_trader.bootstrap.MarketDataSyncJob", FakeMarketDataSyncJob)
  monkeypatch.setattr("akra_trader.bootstrap.SandboxWorkerSessionsJob", FakeSandboxWorkerSessionsJob)

  container = build_container(
    Settings(
      market_data_provider="coinbase",
      market_data_symbols=("ETH/USDT",),
      market_data_sync_timeframes=("5m", "1h"),
      market_data_sync_interval_seconds=90,
      market_data_default_candle_limit=128,
      market_data_historical_candle_limit=512,
    )
  )

  assert captured["market_data_venue"] == "coinbase"
  assert captured["tracked_symbols"] == "ETH/USDT"
  assert captured["default_candle_limit"] == "128"
  assert captured["historical_candle_limit"] == "512"
  assert captured["sync_timeframes"] == "5m,1h"
  assert captured["sync_interval_seconds"] == "90"
  assert captured["venue_state_venue"] == "coinbase"
  assert captured["venue_execution_venue"] == "coinbase"
  assert container.app._guarded_live_market_data_timeframes == ("5m", "1h")
  assert len(container.background_jobs) == 2


def test_build_container_can_target_guarded_live_venue_separately_from_market_data(monkeypatch) -> None:
  captured: dict[str, str] = {}

  class FakeRunRepository:
    def __init__(self, database_url: str) -> None:
      self.database_url = database_url

  class FakeGuardedLiveRepository:
    def __init__(self, database_url: str) -> None:
      self.database_url = database_url

  class FakeCcxtVenueStateAdapter:
    def __init__(
      self,
      *,
      tracked_symbols: tuple[str, ...],
      venue: str = "binance",
      api_key: str | None,
      api_secret: str | None,
    ) -> None:
      captured["venue_state_symbols"] = ",".join(tracked_symbols)
      captured["venue_state_venue"] = venue
      captured["venue_state_api_key"] = api_key or ""
      captured["venue_state_api_secret"] = api_secret or ""

  class FakeBinanceVenueExecutionAdapter:
    def __init__(
      self,
      *,
      venue: str = "binance",
      api_key: str | None,
      api_secret: str | None,
    ) -> None:
      captured["venue_execution_venue"] = venue
      captured["venue_execution_api_key"] = api_key or ""
      captured["venue_execution_api_secret"] = api_secret or ""

  monkeypatch.setattr("akra_trader.bootstrap.SqlAlchemyRunRepository", FakeRunRepository)
  monkeypatch.setattr("akra_trader.bootstrap.SqlAlchemyGuardedLiveStateRepository", FakeGuardedLiveRepository)
  monkeypatch.setattr("akra_trader.bootstrap.CcxtVenueStateAdapter", FakeCcxtVenueStateAdapter)
  monkeypatch.setattr("akra_trader.bootstrap.BinanceVenueExecutionAdapter", FakeBinanceVenueExecutionAdapter)

  container = build_container(
    Settings(
      market_data_provider="seeded",
      guarded_live_venue="coinbase",
      guarded_live_api_key="coinbase-key",
      guarded_live_api_secret="coinbase-secret",
      market_data_symbols=("BTC/USDT", "ETH/USDT"),
    )
  )

  assert isinstance(container.app._market_data, SeededMarketDataAdapter)
  assert container.app._guarded_live_venue == "coinbase"
  assert captured["venue_state_symbols"] == "BTC/USDT,ETH/USDT"
  assert captured["venue_state_venue"] == "coinbase"
  assert captured["venue_state_api_key"] == "coinbase-key"
  assert captured["venue_state_api_secret"] == "coinbase-secret"
  assert captured["venue_execution_venue"] == "coinbase"
  assert captured["venue_execution_api_key"] == "coinbase-key"
  assert captured["venue_execution_api_secret"] == "coinbase-secret"
