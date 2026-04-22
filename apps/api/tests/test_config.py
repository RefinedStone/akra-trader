from __future__ import annotations

from akra_trader.config import load_settings


def test_load_settings_parses_provider_provenance_report_scheduler_settings(monkeypatch) -> None:
  monkeypatch.setenv("AKRA_TRADER_PROVIDER_PROVENANCE_REPORT_SCHEDULER_ENABLED", "false")
  monkeypatch.setenv("AKRA_TRADER_PROVIDER_PROVENANCE_REPORT_SCHEDULER_INTERVAL_SECONDS", "135")
  monkeypatch.setenv("AKRA_TRADER_PROVIDER_PROVENANCE_REPORT_SCHEDULER_BATCH_LIMIT", "9")
  monkeypatch.setenv(
    "AKRA_TRADER_PROVIDER_PROVENANCE_SCHEDULER_SEARCH_DATABASE_URL",
    "sqlite:////tmp/provider-provenance-scheduler-search.sqlite3",
  )

  settings = load_settings()

  assert settings.provider_provenance_report_scheduler_enabled is False
  assert settings.provider_provenance_report_scheduler_interval_seconds == 135
  assert settings.provider_provenance_report_scheduler_batch_limit == 9
  assert (
    settings.provider_provenance_scheduler_search_database_url
    == "sqlite:////tmp/provider-provenance-scheduler-search.sqlite3"
  )
