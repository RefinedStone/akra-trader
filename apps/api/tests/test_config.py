from __future__ import annotations

from akra_trader.config import load_settings


def test_load_settings_parses_provider_provenance_report_scheduler_settings(monkeypatch) -> None:
  monkeypatch.setenv("AKRA_TRADER_PROVIDER_PROVENANCE_REPORT_SCHEDULER_ENABLED", "false")
  monkeypatch.setenv("AKRA_TRADER_PROVIDER_PROVENANCE_REPORT_SCHEDULER_INTERVAL_SECONDS", "135")
  monkeypatch.setenv("AKRA_TRADER_PROVIDER_PROVENANCE_REPORT_SCHEDULER_BATCH_LIMIT", "9")

  settings = load_settings()

  assert settings.provider_provenance_report_scheduler_enabled is False
  assert settings.provider_provenance_report_scheduler_interval_seconds == 135
  assert settings.provider_provenance_report_scheduler_batch_limit == 9
