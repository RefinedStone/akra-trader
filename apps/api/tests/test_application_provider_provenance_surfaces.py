from __future__ import annotations

from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
import json
from pathlib import Path
from typing import Any

import pytest

from akra_trader.adapters.binance import BinanceMarketDataAdapter
from akra_trader.adapters.guarded_live import SqlAlchemyGuardedLiveStateRepository
from akra_trader.adapters.in_memory import LocalStrategyCatalog
from akra_trader.adapters.in_memory import SeededMarketDataAdapter
from akra_trader.adapters.sqlalchemy import SqlAlchemyExperimentPresetCatalog
from akra_trader.adapters.sqlalchemy import SqlAlchemyRunRepository
from akra_trader.adapters.venue_execution import SeededVenueExecutionAdapter
from akra_trader.application import get_run_subresource_contract
from akra_trader.application import get_run_subresource_runtime_binding
from akra_trader.application import list_run_subresource_contracts
from akra_trader.application import list_run_subresource_runtime_bindings
from akra_trader.application import list_standalone_surface_runtime_bindings
from akra_trader.application import execute_standalone_surface_binding
from akra_trader.application import serialize_standalone_surface_response
from akra_trader.application import TradingApplication
from akra_trader.application import serialize_run_surface_capabilities
from akra_trader.application import serialize_run_subresource_response
from akra_trader.domain.models import AssetType
from akra_trader.domain.models import BenchmarkArtifact
from akra_trader.domain.models import Candle
from akra_trader.domain.models import DatasetBoundaryContract
from akra_trader.domain.models import GapWindow
from akra_trader.domain.models import GuardedLiveBookTickerChannelSnapshot
from akra_trader.domain.models import GuardedLiveKlineChannelSnapshot
from akra_trader.domain.models import GuardedLiveOrderBookLevel
from akra_trader.domain.models import GuardedLiveVenueBalance
from akra_trader.domain.models import GuardedLiveVenueOpenOrder
from akra_trader.domain.models import GuardedLiveVenueOrderResult
from akra_trader.domain.models import GuardedLiveVenueStateSnapshot
from akra_trader.domain.models import InstrumentStatus
from akra_trader.domain.models import MarketDataIngestionJobRecord
from akra_trader.domain.models import MarketDataLineageHistoryRecord
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync
from akra_trader.domain.models import Order
from akra_trader.domain.models import OrderSide
from akra_trader.domain.models import OrderStatus
from akra_trader.domain.models import OrderType
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.models import Position
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunSurfaceCapabilities
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import SyncFailure
from akra_trader.domain.models import WarmupSpec
from akra_trader.lineage import build_dataset_boundary_contract
from akra_trader.strategies.base import Strategy

from .application_test_support import AlwaysBuyStrategy
from .application_test_support import FakeExchange
from .application_test_support import FakeOperatorAlertDeliveryAdapter
from .application_test_support import MutableClock
from .application_test_support import MutableSeededMarketDataAdapter
from .application_test_support import StaticVenueStateAdapter
from .application_test_support import StatusOverrideSeededMarketDataAdapter
from .application_test_support import build_preset_catalog
from .application_test_support import build_runs_repository
from .application_test_support import without_surface_rule


def test_replay_link_alias_bindings_create_resolve_and_revoke(tmp_path: Path) -> None:
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    presets=build_preset_catalog(tmp_path),
    runs=build_runs_repository(tmp_path),
  )
  bindings_by_key = {
    binding.surface_key: binding
    for binding in list_standalone_surface_runtime_bindings(app.get_run_surface_capabilities())
  }

  created_alias = execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_alias_create"],
    app=app,
    request_payload={
      "template_key": "template_a",
      "template_label": "Template A",
      "intent": {
        "replayScope": "all",
        "replayIndex": 2,
        "replayGroupFilter": "group_a",
      },
      "redaction_policy": "omit_preview",
      "retention_policy": "7d",
      "source_tab_id": "tab_local",
      "source_tab_label": "Local tab",
    },
  )

  assert created_alias["template_key"] == "template_a"
  assert created_alias["resolution_source"] == "server"
  assert created_alias["alias_token"].startswith(f"{created_alias['alias_id']}.")

  resolved_alias = execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_alias_resolve"],
    app=app,
    path_params={"alias_token": created_alias["alias_token"]},
  )

  assert resolved_alias["intent"]["replayIndex"] == 2
  assert resolved_alias["retention_policy"] == "7d"
  assert resolved_alias["revoked_at"] is None

  revoked_alias = execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_alias_revoke"],
    app=app,
    path_params={"alias_token": created_alias["alias_token"]},
    request_payload={
      "source_tab_id": "tab_remote",
      "source_tab_label": "Remote tab",
    },
  )

  assert revoked_alias["revoked_at"] is not None
  assert revoked_alias["revoked_by_tab_label"] == "Remote tab"

  history_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_alias_history"],
    app=app,
    path_params={"alias_token": created_alias["alias_token"]},
  )

  assert history_payload["alias"]["revoked_by_tab_label"] == "Remote tab"
  assert [item["action"] for item in history_payload["history"]] == [
    "revoked",
    "resolved",
    "created",
  ]
  assert history_payload["history"][0]["source_tab_label"] == "Remote tab"
  assert all(item["retention_policy"] == "7d" for item in history_payload["history"])

  with pytest.raises(LookupError, match="revoked"):
    execute_standalone_surface_binding(
      binding=bindings_by_key["replay_link_alias_resolve"],
      app=app,
      path_params={"alias_token": created_alias["alias_token"]},
    )

def test_replay_link_alias_records_survive_application_restart(tmp_path: Path) -> None:
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )

  created_alias = app.create_replay_intent_alias(
    template_key="template_a",
    template_label="Template A",
    intent={"replayScope": "all", "replayIndex": 3},
    redaction_policy="full",
    retention_policy="7d",
    source_tab_id="tab_local",
    source_tab_label="Local tab",
  )
  alias_token = f"{created_alias.alias_id}.{created_alias.signature}"

  restarted = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )

  resolved_alias = restarted.resolve_replay_intent_alias(alias_token)
  assert resolved_alias.alias_id == created_alias.alias_id

  restarted.revoke_replay_intent_alias(
    alias_token,
    source_tab_id="tab_remote",
    source_tab_label="Remote tab",
  )

  second_restart = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
  )

  history = second_restart.list_replay_intent_alias_history(alias_token)
  assert [item.action for item in history] == ["revoked", "resolved", "created"]
  assert history[0].source_tab_label == "Remote tab"

  with pytest.raises(LookupError, match="revoked"):
    second_restart.resolve_replay_intent_alias(alias_token)

def test_replay_link_alias_history_retention_prunes_expired_audit_records(tmp_path: Path) -> None:
  clock = MutableClock(datetime(2026, 1, 1, tzinfo=UTC))
  runs = build_runs_repository(tmp_path)
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
  )

  created_alias = app.create_replay_intent_alias(
    template_key="template_a",
    template_label="Template A",
    intent={"replayScope": "all", "replayIndex": 1},
    redaction_policy="summary_only",
    retention_policy="1d",
    source_tab_id="tab_local",
    source_tab_label="Local tab",
  )
  alias_token = f"{created_alias.alias_id}.{created_alias.signature}"

  clock.advance(timedelta(hours=2))
  app.resolve_replay_intent_alias(alias_token)

  clock.advance(timedelta(days=2))
  restarted = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=runs,
    clock=clock,
  )

  assert restarted.list_replay_intent_alias_history(alias_token) == ()

def test_replay_link_alias_audit_admin_listing_and_pruning(tmp_path: Path) -> None:
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    presets=build_preset_catalog(tmp_path),
    runs=build_runs_repository(tmp_path),
    replay_alias_audit_admin_read_token="read-token",
    replay_alias_audit_admin_write_token="write-token",
  )
  bindings_by_key = {
    binding.surface_key: binding
    for binding in list_standalone_surface_runtime_bindings(app.get_run_surface_capabilities())
  }

  created_alias = execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_alias_create"],
    app=app,
    request_payload={
      "template_key": "template_a",
      "template_label": "Template A",
      "intent": {"replayScope": "all", "replayIndex": 2},
      "redaction_policy": "full",
      "retention_policy": "7d",
      "source_tab_id": "tab_local",
      "source_tab_label": "Local tab",
    },
  )
  execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_alias_resolve"],
    app=app,
    path_params={"alias_token": created_alias["alias_token"]},
  )
  execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_alias_revoke"],
    app=app,
    path_params={"alias_token": created_alias["alias_token"]},
    request_payload={"source_tab_id": "tab_remote", "source_tab_label": "Remote tab"},
  )
  manual_alias = app.create_replay_intent_alias(
    template_key="template_b",
    template_label="Template B",
    intent={"replayScope": "grouped"},
    redaction_policy="summary_only",
    retention_policy="manual",
    source_tab_id="tab_manual",
    source_tab_label="Manual tab",
  )

  audit_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_list"],
    app=app,
    filters={"template_key": "template_a", "action": "revoked", "search": "Remote", "limit": 10},
    headers={"x_akra_replay_audit_admin_token": "read-token"},
  )
  assert audit_list_payload["total"] == 1
  assert audit_list_payload["items"][0]["action"] == "revoked"

  export_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_export"],
    app=app,
    filters={"template_key": "template_a", "format": "csv"},
    headers={"x_akra_replay_audit_admin_token": "read-token"},
  )
  assert export_payload["format"] == "csv"
  assert export_payload["filename"].endswith(".csv")
  assert export_payload["record_count"] == 3
  assert "audit_id,alias_id,action" in export_payload["content"]

  prune_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_prune"],
    app=app,
    request_payload={
      "prune_mode": "matched",
      "template_key": "template_b",
      "include_manual": False,
    },
    headers={"x_akra_replay_audit_admin_token": "write-token"},
  )
  assert prune_payload["deleted_count"] == 0

  prune_manual_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_prune"],
    app=app,
    request_payload={
      "prune_mode": "matched",
      "alias_id": manual_alias.alias_id,
      "include_manual": True,
    },
    headers={"x_akra_replay_audit_admin_token": "write-token"},
  )
  assert prune_manual_payload["deleted_count"] == 1

  export_job_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_export_job_create"],
    app=app,
    request_payload={
      "format": "json",
      "template_key": "template_a",
      "requested_by_tab_id": "tab_export",
      "requested_by_tab_label": "Export tab",
    },
    headers={"x_akra_replay_audit_admin_token": "write-token"},
  )
  assert export_job_payload["export_format"] == "json"
  assert export_job_payload["record_count"] == 3
  assert export_job_payload["artifact_id"] is not None
  assert export_job_payload["content_length"] > 0

  export_job_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_export_job_list"],
    app=app,
    filters={"template_key": "template_a", "format": "json", "limit": 10},
    headers={"x_akra_replay_audit_admin_token": "read-token"},
  )
  assert export_job_list_payload["total"] == 1
  export_job_id = export_job_list_payload["items"][0]["job_id"]

  download_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_export_job_download"],
    app=app,
    path_params={"job_id": export_job_id},
    headers={"x_akra_replay_audit_admin_token": "read-token"},
  )
  assert download_payload["content"]
  assert download_payload["record_count"] == 3

  export_job_history_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_export_job_history"],
    app=app,
    path_params={"job_id": export_job_id},
    headers={"x_akra_replay_audit_admin_token": "read-token"},
  )
  assert [item["action"] for item in export_job_history_payload["history"]] == [
    "downloaded",
    "created",
  ]

  prune_export_job_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_export_job_prune"],
    app=app,
    request_payload={
      "prune_mode": "matched",
      "template_key": "template_a",
      "format": "json",
    },
    headers={"x_akra_replay_audit_admin_token": "write-token"},
  )
  assert prune_export_job_payload["deleted_job_count"] == 1
  assert prune_export_job_payload["deleted_artifact_count"] == 1
  assert prune_export_job_payload["deleted_history_count"] == 2

def test_replay_link_alias_audit_admin_binding_enforces_scoped_tokens(tmp_path: Path) -> None:
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=build_runs_repository(tmp_path),
    replay_alias_audit_admin_read_token="read-token",
    replay_alias_audit_admin_write_token="write-token",
  )
  bindings_by_key = {
    binding.surface_key: binding
    for binding in list_standalone_surface_runtime_bindings(app.get_run_surface_capabilities())
  }

  with pytest.raises(PermissionError, match="invalid replay alias audit admin token"):
    execute_standalone_surface_binding(
      binding=bindings_by_key["replay_link_audit_list"],
      app=app,
      filters={"limit": 10},
    )

  execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_list"],
    app=app,
    filters={"limit": 10},
    headers={"x_akra_replay_audit_admin_token": "read-token"},
  )

  execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_export"],
    app=app,
    filters={"format": "json"},
    headers={"x_akra_replay_audit_admin_token": "read-token"},
  )

  with pytest.raises(PermissionError, match="invalid replay alias audit admin token"):
    execute_standalone_surface_binding(
      binding=bindings_by_key["replay_link_audit_export_job_create"],
      app=app,
      request_payload={"format": "json"},
      headers={"x_akra_replay_audit_admin_token": "read-token"},
    )

  created_export_job = execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_export_job_create"],
    app=app,
    request_payload={"format": "json", "requested_by_tab_id": "tab_local"},
    headers={"x_akra_replay_audit_admin_token": "write-token"},
  )

  execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_export_job_list"],
    app=app,
    filters={"limit": 10},
    headers={"x_akra_replay_audit_admin_token": "read-token"},
  )

  execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_export_job_download"],
    app=app,
    path_params={"job_id": created_export_job["job_id"]},
    headers={"x_akra_replay_audit_admin_token": "read-token"},
  )

  execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_export_job_history"],
    app=app,
    path_params={"job_id": created_export_job["job_id"]},
    headers={"x_akra_replay_audit_admin_token": "read-token"},
  )

  with pytest.raises(PermissionError, match="invalid replay alias audit admin token"):
    execute_standalone_surface_binding(
      binding=bindings_by_key["replay_link_audit_export_job_prune"],
      app=app,
      request_payload={"prune_mode": "expired"},
      headers={"x_akra_replay_audit_admin_token": "read-token"},
    )

  execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_export_job_prune"],
    app=app,
    request_payload={"prune_mode": "expired"},
    headers={"x_akra_replay_audit_admin_token": "write-token"},
  )

  with pytest.raises(PermissionError, match="invalid replay alias audit admin token"):
    execute_standalone_surface_binding(
      binding=bindings_by_key["replay_link_audit_prune"],
      app=app,
      request_payload={"prune_mode": "expired"},
      headers={"x_akra_replay_audit_admin_token": "read-token"},
    )

  execute_standalone_surface_binding(
    binding=bindings_by_key["replay_link_audit_prune"],
    app=app,
    request_payload={"prune_mode": "expired"},
    headers={"x_akra_replay_audit_admin_token": "write-token"},
  )

def test_operator_provider_provenance_export_job_bindings_round_trip(tmp_path: Path) -> None:
  clock = MutableClock(datetime(2026, 4, 20, 9, 0, tzinfo=UTC))
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=build_runs_repository(tmp_path),
    clock=clock,
  )
  bindings_by_key = {
    binding.surface_key: binding
    for binding in list_standalone_surface_runtime_bindings(app.get_run_surface_capabilities())
  }
  export_content = json.dumps(
    {
      "exported_at": "2026-04-20T09:00:00Z",
      "export_scope": "provider_market_context_provenance",
      "export_filter": {
        "provider": "pagerduty",
        "vendor_field": "custom_details.market_context",
        "search_query": "",
        "sort": "newest",
      },
      "export_filter_summary": "provider pagerduty / vendor field custom_details.market_context",
      "export_result_count": 1,
      "focus": {
        "provider": "binance",
        "venue": "binance",
        "instrument_id": "binance:BTC/USDT",
        "symbol": "BTC/USDT",
        "timeframe": "5m",
        "provider_provenance_incident_count": 2,
      },
      "provider_provenance_incidents": [
        {
          "event_id": "incident_1",
          "provider": "pagerduty",
          "vendor_field": "custom_details.market_context",
        }
      ],
    },
    indent=2,
  )
  later_export_content = json.dumps(
    {
      "exported_at": "2026-04-21T09:00:00Z",
      "export_scope": "provider_market_context_provenance",
      "export_filter": {
        "provider": "pagerduty",
        "vendor_field": "custom_details.market_context",
        "search_query": "",
        "sort": "newest",
      },
      "export_filter_summary": "provider pagerduty / vendor field custom_details.market_context",
      "export_result_count": 2,
      "focus": {
        "provider": "binance",
        "venue": "binance",
        "instrument_id": "binance:BTC/USDT",
        "symbol": "BTC/USDT",
        "timeframe": "5m",
        "provider_provenance_incident_count": 3,
      },
      "provider_provenance_incidents": [
        {
          "event_id": "incident_2",
          "provider": "pagerduty",
          "vendor_field": "custom_details.market_context",
        }
      ],
    },
    indent=2,
  )

  created_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_export_job_create"],
    app=app,
    request_payload={
      "content": export_content,
      "requested_by_tab_id": "tab_ops",
      "requested_by_tab_label": "Ops desk",
    },
  )
  assert created_payload["export_scope"] == "provider_market_context_provenance"
  assert created_payload["focus_key"] == "binance:BTC/USDT|5m"
  assert created_payload["provider_labels"] == ["pagerduty"]
  assert created_payload["vendor_fields"] == ["custom_details.market_context"]

  listed_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_export_job_list"],
    app=app,
    filters={"focus_key": "binance:BTC/USDT|5m", "limit": 10},
  )
  assert listed_payload["total"] == 1
  assert listed_payload["items"][0]["job_id"] == created_payload["job_id"]

  downloaded_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_export_job_download"],
    app=app,
    path_params={"job_id": created_payload["job_id"]},
    filters={"source_tab_id": "tab_review", "source_tab_label": "Review tab"},
  )
  assert downloaded_payload["content"] == export_content

  clock.advance(timedelta(days=1))
  later_created_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_export_job_create"],
    app=app,
    request_payload={
      "content": later_export_content,
      "requested_by_tab_id": "tab_ops",
      "requested_by_tab_label": "Ops desk",
    },
  )
  execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_export_job_download"],
    app=app,
    path_params={"job_id": later_created_payload["job_id"]},
    filters={"source_tab_id": "tab_review", "source_tab_label": "Review tab"},
  )
  clock.advance(timedelta(days=1))

  analytics_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_export_analytics"],
    app=app,
    filters={
      "focus_key": "binance:BTC/USDT|5m",
      "provider_label": "pagerduty",
      "vendor_field": "custom_details.market_context",
      "result_limit": 10,
      "window_days": 3,
    },
  )
  assert analytics_payload["totals"]["export_count"] == 2
  assert analytics_payload["totals"]["download_count"] == 2
  assert analytics_payload["query"]["window_days"] == 3
  assert analytics_payload["rollups"]["providers"][0]["key"] == "pagerduty"
  assert analytics_payload["rollups"]["focuses"][0]["key"] == "binance:BTC/USDT|5m"
  assert analytics_payload["recent_exports"][0]["job_id"] == later_created_payload["job_id"]
  assert [bucket["bucket_key"] for bucket in analytics_payload["time_series"]["provider_drift"]["series"]] == [
    "2026-04-20",
    "2026-04-21",
    "2026-04-22",
  ]
  assert analytics_payload["time_series"]["provider_drift"]["summary"] == {
    "peak_bucket_key": "2026-04-21",
    "peak_bucket_label": "Apr 21",
    "peak_export_count": 1,
    "peak_provider_provenance_count": 3,
    "latest_bucket_key": "2026-04-22",
    "latest_bucket_label": "Apr 22",
    "latest_export_count": 0,
    "latest_provider_provenance_count": 0,
  }
  assert analytics_payload["time_series"]["export_burn_up"]["summary"] == {
    "latest_bucket_key": "2026-04-22",
    "latest_bucket_label": "Apr 22",
    "cumulative_export_count": 2,
    "cumulative_result_count": 3,
    "cumulative_provider_provenance_count": 5,
    "cumulative_download_count": 2,
  }

  history_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_export_job_history"],
    app=app,
    path_params={"job_id": created_payload["job_id"]},
  )
  assert {item["action"] for item in history_payload["history"]} == {"created", "downloaded"}
  assert any(item["source_tab_id"] == "tab_review" for item in history_payload["history"])

def test_operator_provider_provenance_workspace_bindings_round_trip(tmp_path: Path) -> None:
  clock = MutableClock(datetime(2026, 4, 22, 9, 0, tzinfo=UTC))
  delivery = FakeOperatorAlertDeliveryAdapter(
    targets=("slack_webhook", "pagerduty_events"),
    clock=clock,
  )
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=LocalStrategyCatalog(),
    runs=build_runs_repository(tmp_path),
    clock=clock,
    operator_alert_delivery=delivery,
  )
  bindings_by_key = {
    binding.surface_key: binding
    for binding in list_standalone_surface_runtime_bindings(app.get_run_surface_capabilities())
  }

  preset_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_analytics_preset_create"],
    app=app,
    request_payload={
      "name": "BTC drift watch",
      "description": "Current focus drift watch preset.",
      "query": {
        "focus_scope": "current_focus",
        "focus_key": "binance:BTC/USDT|5m",
        "symbol": "BTC/USDT",
        "timeframe": "5m",
        "provider_label": "pagerduty",
        "vendor_field": "custom_details.market_context",
        "market_data_provider": "binance",
        "scheduler_alert_category": "scheduler_lag",
        "scheduler_alert_status": "resolved",
        "scheduler_alert_narrative_facet": "post_resolution_recovery",
        "window_days": 14,
        "result_limit": 12,
      },
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  assert preset_payload["query"]["focus_scope"] == "current_focus"
  assert preset_payload["focus"]["symbol"] == "BTC/USDT"
  assert preset_payload["query"]["scheduler_alert_narrative_facet"] == "post_resolution_recovery"

  preset_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_analytics_preset_list"],
    app=app,
    filters={"focus_scope": "current_focus", "limit": 10},
  )
  assert preset_list_payload["total"] == 1
  assert preset_list_payload["items"][0]["preset_id"] == preset_payload["preset_id"]

  view_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_dashboard_view_create"],
    app=app,
    request_payload={
      "name": "BTC drift board",
      "description": "Shared drift dashboard view.",
      "preset_id": preset_payload["preset_id"],
      "layout": {
        "highlight_panel": "scheduler_alerts",
        "show_rollups": True,
        "show_time_series": True,
        "show_recent_exports": False,
        "governance_queue_view": {
          "queue_state": "pending_approval",
          "source_hierarchy_step_template_id": "hst_demo",
          "source_hierarchy_step_template_name": "Lag triage step",
          "search": "lag recovery",
          "sort": "source_template_asc",
        },
      },
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  assert view_payload["preset_id"] == preset_payload["preset_id"]
  assert view_payload["layout"]["highlight_panel"] == "scheduler_alerts"
  assert view_payload["layout"]["governance_queue_view"]["source_hierarchy_step_template_id"] == "hst_demo"
  assert view_payload["query"]["scheduler_alert_status"] == "resolved"

  view_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_dashboard_view_list"],
    app=app,
    filters={"preset_id": preset_payload["preset_id"], "highlight_panel": "scheduler_alerts", "limit": 10},
  )
  assert view_list_payload["total"] == 1
  assert view_list_payload["items"][0]["view_id"] == view_payload["view_id"]

  stitched_report_view_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_create"],
    app=app,
    request_payload={
      "name": "Lag recovery stitched report",
      "description": "Saved stitched report slice for lag recovery.",
      "query": {
        "focus_scope": "all_focuses",
        "scheduler_alert_category": "scheduler_lag",
        "scheduler_alert_status": "resolved",
        "scheduler_alert_narrative_facet": "post_resolution_recovery",
        "window_days": 14,
        "result_limit": 12,
      },
      "occurrence_limit": 6,
      "history_limit": 16,
      "drilldown_history_limit": 18,
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  assert stitched_report_view_payload["query"]["scheduler_alert_category"] == "scheduler_lag"
  assert stitched_report_view_payload["query"]["scheduler_alert_narrative_facet"] == "post_resolution_recovery"
  assert stitched_report_view_payload["occurrence_limit"] == 6
  assert stitched_report_view_payload["history_limit"] == 16
  assert stitched_report_view_payload["drilldown_history_limit"] == 18
  assert stitched_report_view_payload["revision_count"] == 1
  assert stitched_report_view_payload["status"] == "active"

  stitched_report_view_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_list"],
    app=app,
    filters={
      "category": "scheduler_lag",
      "narrative_facet": "post_resolution_recovery",
      "limit": 10,
    },
  )
  assert stitched_report_view_list_payload["total"] == 1
  assert stitched_report_view_list_payload["items"][0]["view_id"] == stitched_report_view_payload["view_id"]

  updated_stitched_report_view_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_update"],
    app=app,
    path_params={"view_id": stitched_report_view_payload["view_id"]},
    request_payload={
      "name": "Lag recovery stitched report v2",
      "description": "Saved stitched report slice for recurring lag recovery.",
      "query": {
        "focus_scope": "all_focuses",
        "scheduler_alert_category": "scheduler_lag",
        "scheduler_alert_status": "resolved",
        "scheduler_alert_narrative_facet": "recurring_occurrences",
        "window_days": 21,
        "result_limit": 10,
      },
      "occurrence_limit": 7,
      "history_limit": 18,
      "drilldown_history_limit": 20,
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "scheduler_stitched_report_view_manual_edit",
    },
  )
  assert updated_stitched_report_view_payload["name"] == "Lag recovery stitched report v2"
  assert updated_stitched_report_view_payload["query"]["scheduler_alert_narrative_facet"] == "recurring_occurrences"
  assert updated_stitched_report_view_payload["revision_count"] == 2

  stitched_report_view_revision_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_revision_list"],
    app=app,
    path_params={"view_id": stitched_report_view_payload["view_id"]},
  )
  assert stitched_report_view_revision_payload["view"]["view_id"] == stitched_report_view_payload["view_id"]
  assert [item["action"] for item in stitched_report_view_revision_payload["history"][:2]] == [
    "updated",
    "created",
  ]
  created_stitched_report_view_revision_id = stitched_report_view_revision_payload["history"][-1]["revision_id"]

  deleted_stitched_report_view_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_delete"],
    app=app,
    path_params={"view_id": stitched_report_view_payload["view_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "scheduler_stitched_report_view_deleted_from_control_room",
    },
  )
  assert deleted_stitched_report_view_payload["status"] == "deleted"
  assert deleted_stitched_report_view_payload["revision_count"] == 3

  restored_stitched_report_view_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_revision_restore"],
    app=app,
    path_params={
      "view_id": stitched_report_view_payload["view_id"],
      "revision_id": created_stitched_report_view_revision_id,
    },
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "scheduler_stitched_report_view_revision_restore_from_control_room",
    },
  )
  assert restored_stitched_report_view_payload["status"] == "active"
  assert restored_stitched_report_view_payload["name"] == "Lag recovery stitched report"
  assert restored_stitched_report_view_payload["revision_count"] == 4

  secondary_stitched_report_view_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_create"],
    app=app,
    request_payload={
      "name": "Failure stitched report",
      "description": "Saved stitched report slice for failure review.",
      "query": {
        "focus_scope": "all_focuses",
        "scheduler_alert_category": "scheduler_failure",
        "scheduler_alert_status": "resolved",
        "scheduler_alert_narrative_facet": "resolved_narratives",
        "window_days": 10,
        "result_limit": 8,
      },
      "occurrence_limit": 5,
      "history_limit": 14,
      "drilldown_history_limit": 16,
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )

  bulk_governed_stitched_report_views_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_bulk_governance"],
    app=app,
    request_payload={
      "action": "update",
      "view_ids": [
        stitched_report_view_payload["view_id"],
        secondary_stitched_report_view_payload["view_id"],
      ],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "bulk_govern_stitched_report_views",
      "name_prefix": "Shift / ",
      "description_append": "bulk-reviewed",
      "query_patch": {
        "scheduler_alert_category": "scheduler_failure",
        "scheduler_alert_status": "active",
        "scheduler_alert_narrative_facet": "recurring_occurrences",
        "window_days": 12,
        "result_limit": 9,
      },
      "occurrence_limit": 9,
      "history_limit": 20,
      "drilldown_history_limit": 22,
    },
  )
  assert bulk_governed_stitched_report_views_payload["action"] == "update"
  assert bulk_governed_stitched_report_views_payload["item_type"] == "stitched_report_view"
  assert bulk_governed_stitched_report_views_payload["applied_count"] == 2
  assert all(item["status"] == "active" for item in bulk_governed_stitched_report_views_payload["results"])

  updated_stitched_report_view_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_list"],
    app=app,
    filters={"category": "scheduler_failure", "narrative_facet": "recurring_occurrences", "limit": 10},
  )
  assert updated_stitched_report_view_list_payload["total"] == 2
  assert all(item["name"].startswith("Shift / ") for item in updated_stitched_report_view_list_payload["items"])
  assert all(item["description"].endswith("bulk-reviewed") for item in updated_stitched_report_view_list_payload["items"])

  stitched_report_view_audit_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_audit_list"],
    app=app,
    filters={
      "view_id": stitched_report_view_payload["view_id"],
      "action": "updated",
      "actor_tab_id": "tab_ops",
      "search": "Shift /",
      "limit": 10,
    },
  )
  assert stitched_report_view_audit_payload["total"] >= 1
  assert stitched_report_view_audit_payload["items"][0]["view_id"] == stitched_report_view_payload["view_id"]
  assert stitched_report_view_audit_payload["items"][0]["action"] == "updated"
  assert stitched_report_view_audit_payload["items"][0]["actor_tab_id"] == "tab_ops"
  assert "Shift /" in stitched_report_view_audit_payload["items"][0]["detail"]

  stitched_governance_registry_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_create"],
    app=app,
    request_payload={
      "name": "Lag stitched governance bundle",
      "description": "Dedicated stitched-report queue slice and defaults.",
      "queue_view": {
        "queue_state": "pending_approval",
        "item_type": "stitched_report_view",
        "approval_lane": "ops",
        "approval_priority": "high",
        "search": "lag recovery",
        "sort": "updated_desc",
      },
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  assert stitched_governance_registry_payload["status"] == "active"
  assert stitched_governance_registry_payload["queue_view"]["item_type"] == "stitched_report_view"
  assert stitched_governance_registry_payload["revision_count"] == 1

  stitched_governance_registry_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_list"],
    app=app,
    filters={"search": "lag recovery", "limit": 10},
  )
  assert stitched_governance_registry_list_payload["total"] == 1
  assert stitched_governance_registry_list_payload["items"][0]["registry_id"] == stitched_governance_registry_payload["registry_id"]

  updated_stitched_governance_registry_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_update"],
    app=app,
    path_params={"registry_id": stitched_governance_registry_payload["registry_id"]},
    request_payload={
      "name": "Lag stitched governance bundle v2",
      "description": "Dedicated stitched-report queue slice and defaults v2.",
      "queue_view": {
        "queue_state": "ready_to_apply",
        "item_type": "stitched_report_view",
        "approval_lane": "ops",
        "approval_priority": "critical",
        "search": "lag recovery reviewed",
        "sort": "created_desc",
      },
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "scheduler_stitched_report_governance_registry_manual_edit",
    },
  )
  assert updated_stitched_governance_registry_payload["name"] == "Lag stitched governance bundle v2"
  assert updated_stitched_governance_registry_payload["queue_view"]["queue_state"] == "ready_to_apply"
  assert updated_stitched_governance_registry_payload["revision_count"] == 2

  stitched_governance_registry_revision_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_list"],
    app=app,
    path_params={"registry_id": stitched_governance_registry_payload["registry_id"]},
  )
  assert stitched_governance_registry_revision_payload["registry"]["registry_id"] == stitched_governance_registry_payload["registry_id"]
  assert [item["action"] for item in stitched_governance_registry_revision_payload["history"][:2]] == [
    "updated",
    "created",
  ]
  created_stitched_governance_registry_revision_id = (
    stitched_governance_registry_revision_payload["history"][-1]["revision_id"]
  )

  deleted_stitched_governance_registry_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_delete"],
    app=app,
    path_params={"registry_id": stitched_governance_registry_payload["registry_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "scheduler_stitched_report_governance_registry_deleted_from_control_room",
    },
  )
  assert deleted_stitched_governance_registry_payload["status"] == "deleted"
  assert deleted_stitched_governance_registry_payload["revision_count"] == 3

  restored_stitched_governance_registry_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_revision_restore"],
    app=app,
    path_params={
      "registry_id": stitched_governance_registry_payload["registry_id"],
      "revision_id": created_stitched_governance_registry_revision_id,
    },
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "scheduler_stitched_report_governance_registry_revision_restore_from_control_room",
    },
  )
  assert restored_stitched_governance_registry_payload["status"] == "active"
  assert restored_stitched_governance_registry_payload["name"] == "Lag stitched governance bundle"
  assert restored_stitched_governance_registry_payload["revision_count"] == 4

  secondary_stitched_governance_registry_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_create"],
    app=app,
    request_payload={
      "name": "Failure stitched governance bundle",
      "description": "Dedicated failure stitched-report queue slice and defaults.",
      "queue_view": {
        "queue_state": "pending_approval",
        "item_type": "stitched_report_view",
        "approval_lane": "chatops",
        "approval_priority": "normal",
        "search": "failure recovery",
        "sort": "queue_priority",
      },
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )

  bulk_governed_stitched_governance_registry_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_bulk_governance"],
    app=app,
    request_payload={
      "action": "update",
      "registry_ids": [
        stitched_governance_registry_payload["registry_id"],
        secondary_stitched_governance_registry_payload["registry_id"],
      ],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "bulk_govern_stitched_governance_registries",
      "name_prefix": "Shift / ",
      "description_append": "bulk-reviewed",
      "queue_view_patch": {
        "item_type": "stitched_report_view",
        "queue_state": "ready_to_apply",
        "approval_priority": "critical",
        "search": "reviewed handoff",
        "sort": "updated_desc",
      },
    },
  )
  assert bulk_governed_stitched_governance_registry_payload["action"] == "update"
  assert bulk_governed_stitched_governance_registry_payload["item_type"] == "stitched_report_governance_registry"
  assert bulk_governed_stitched_governance_registry_payload["applied_count"] == 2

  bulk_updated_stitched_governance_registry_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_list"],
    app=app,
    filters={"search": "Shift /", "limit": 10},
  )
  assert bulk_updated_stitched_governance_registry_list_payload["total"] == 2
  assert all(
    item["name"].startswith("Shift / ")
    for item in bulk_updated_stitched_governance_registry_list_payload["items"]
  )
  assert all(
    item["description"].endswith("bulk-reviewed")
    for item in bulk_updated_stitched_governance_registry_list_payload["items"]
  )
  assert all(
    item["queue_view"]["queue_state"] == "ready_to_apply"
    for item in bulk_updated_stitched_governance_registry_list_payload["items"]
  )

  stitched_governance_registry_audit_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_audit_list"],
    app=app,
    filters={
      "registry_id": stitched_governance_registry_payload["registry_id"],
      "action": "updated",
      "actor_tab_id": "tab_ops",
      "search": "Shift /",
      "limit": 10,
    },
  )
  assert stitched_governance_registry_audit_payload["total"] >= 1
  assert stitched_governance_registry_audit_payload["items"][0]["registry_id"] == (
    stitched_governance_registry_payload["registry_id"]
  )
  assert stitched_governance_registry_audit_payload["items"][0]["action"] == "updated"
  assert stitched_governance_registry_audit_payload["items"][0]["actor_tab_id"] == "tab_ops"
  assert "Shift /" in stitched_governance_registry_audit_payload["items"][0]["detail"]

  template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_template_create"],
    app=app,
    request_payload={
      "name": "Lag recovery narrative",
      "description": "Post-resolution lag recovery lens.",
      "query": {
        "focus_scope": "all_focuses",
        "scheduler_alert_category": "scheduler_lag",
        "scheduler_alert_status": "resolved",
        "scheduler_alert_narrative_facet": "post_resolution_recovery",
        "window_days": 30,
        "result_limit": 12,
      },
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  assert template_payload["query"]["scheduler_alert_narrative_facet"] == "post_resolution_recovery"

  template_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_template_list"],
    app=app,
    filters={"category": "scheduler_lag", "narrative_facet": "post_resolution_recovery", "limit": 10},
  )
  assert template_list_payload["total"] == 1
  assert template_list_payload["items"][0]["template_id"] == template_payload["template_id"]
  assert template_list_payload["items"][0]["revision_count"] == 1

  updated_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_template_update"],
    app=app,
    path_params={"template_id": template_payload["template_id"]},
    request_payload={
      "name": "Lag recovery narrative v2",
      "description": "Updated post-resolution lag recovery lens.",
      "query": {
        "focus_scope": "all_focuses",
        "scheduler_alert_category": "scheduler_lag",
        "scheduler_alert_status": "resolved",
        "scheduler_alert_narrative_facet": "recurring_occurrences",
        "window_days": 21,
        "result_limit": 12,
      },
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "refined_scheduler_recovery_lens",
    },
  )
  assert updated_template_payload["name"] == "Lag recovery narrative v2"
  assert updated_template_payload["query"]["scheduler_alert_narrative_facet"] == "recurring_occurrences"
  assert updated_template_payload["revision_count"] == 2

  template_revision_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_template_revision_list"],
    app=app,
    path_params={"template_id": template_payload["template_id"]},
  )
  assert template_revision_payload["template"]["template_id"] == template_payload["template_id"]
  assert [item["action"] for item in template_revision_payload["history"][:2]] == ["updated", "created"]
  created_template_revision_id = template_revision_payload["history"][-1]["revision_id"]

  deleted_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_template_delete"],
    app=app,
    path_params={"template_id": template_payload["template_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "retire_superseded_template",
    },
  )
  assert deleted_template_payload["status"] == "deleted"
  assert deleted_template_payload["revision_count"] == 3

  restored_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_template_revision_restore"],
    app=app,
    path_params={
      "template_id": template_payload["template_id"],
      "revision_id": created_template_revision_id,
    },
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "restore_baseline_template",
    },
  )
  assert restored_template_payload["status"] == "active"
  assert restored_template_payload["query"]["scheduler_alert_narrative_facet"] == "post_resolution_recovery"
  assert restored_template_payload["revision_count"] == 4

  bulk_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_template_create"],
    app=app,
    request_payload={
      "name": "Failure narrative",
      "description": "Reusable failure narrative lens.",
      "query": {
        "focus_scope": "all_focuses",
        "scheduler_alert_category": "scheduler_failure",
        "scheduler_alert_status": "resolved",
        "scheduler_alert_narrative_facet": "resolved_narratives",
        "window_days": 14,
        "result_limit": 8,
      },
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  bulk_delete_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_template_bulk_governance"],
    app=app,
    request_payload={
      "action": "delete",
      "template_ids": [template_payload["template_id"], bulk_template_payload["template_id"]],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "bulk_template_governance_delete",
    },
  )
  assert bulk_delete_template_payload["action"] == "delete"
  assert bulk_delete_template_payload["requested_count"] == 2
  assert bulk_delete_template_payload["applied_count"] == 2
  assert bulk_delete_template_payload["failed_count"] == 0
  assert {item["status"] for item in bulk_delete_template_payload["results"]} == {"deleted"}

  bulk_restore_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_template_bulk_governance"],
    app=app,
    request_payload={
      "action": "restore",
      "template_ids": [template_payload["template_id"], bulk_template_payload["template_id"]],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "bulk_template_governance_restore",
    },
  )
  assert bulk_restore_template_payload["action"] == "restore"
  assert bulk_restore_template_payload["applied_count"] == 2
  assert all(item["status"] == "active" for item in bulk_restore_template_payload["results"])

  bulk_update_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_template_bulk_governance"],
    app=app,
    request_payload={
      "action": "update",
      "template_ids": [template_payload["template_id"], bulk_template_payload["template_id"]],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "bulk_template_governance_update",
      "name_prefix": "Gov / ",
      "description_append": "bulk-reviewed",
      "query_patch": {
        "scheduler_alert_category": "scheduler_failure",
        "scheduler_alert_status": "active",
        "scheduler_alert_narrative_facet": "recurring_occurrences",
        "window_days": 10,
        "result_limit": 9,
      },
    },
  )
  assert bulk_update_template_payload["action"] == "update"
  assert bulk_update_template_payload["applied_count"] == 2
  updated_template_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_template_list"],
    app=app,
    filters={"category": "scheduler_failure", "narrative_facet": "recurring_occurrences", "limit": 10},
  )
  assert updated_template_list_payload["total"] == 2
  assert all(item["name"].startswith("Gov / ") for item in updated_template_list_payload["items"])
  assert all(item["description"].endswith("bulk-reviewed") for item in updated_template_list_payload["items"])

  registry_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_create"],
    app=app,
    request_payload={
      "name": "Lag recovery board",
      "description": "Shared scheduler narrative board.",
      "template_id": template_payload["template_id"],
      "query": {
        "focus_scope": "current_focus",
        "focus_key": "binance:BTC/USDT|5m",
        "symbol": "BTC/USDT",
        "timeframe": "5m",
        "scheduler_alert_category": "scheduler_lag",
        "scheduler_alert_status": "resolved",
        "scheduler_alert_narrative_facet": "post_resolution_recovery",
        "window_days": 14,
        "result_limit": 12,
      },
      "layout": {
        "highlight_panel": "overview",
        "show_rollups": False,
        "show_time_series": True,
        "show_recent_exports": False,
      },
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  assert registry_payload["template_id"] == template_payload["template_id"]
  assert registry_payload["layout"]["highlight_panel"] == "scheduler_alerts"
  assert registry_payload["revision_count"] == 1

  registry_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_list"],
    app=app,
    filters={
      "template_id": template_payload["template_id"],
      "category": "scheduler_lag",
      "narrative_facet": "post_resolution_recovery",
      "limit": 10,
    },
  )
  assert registry_list_payload["total"] == 1
  assert registry_list_payload["items"][0]["registry_id"] == registry_payload["registry_id"]

  updated_registry_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_update"],
    app=app,
    path_params={"registry_id": registry_payload["registry_id"]},
    request_payload={
      "name": "Lag recovery board v2",
      "description": "Updated shared scheduler narrative board.",
      "layout": {
        "highlight_panel": "drift",
        "show_rollups": True,
        "show_time_series": False,
        "show_recent_exports": True,
      },
      "template_id": "",
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "switch_to_template_free_board",
    },
  )
  assert updated_registry_payload["name"] == "Lag recovery board v2"
  assert updated_registry_payload["template_id"] is None
  assert updated_registry_payload["layout"]["highlight_panel"] == "scheduler_alerts"
  assert updated_registry_payload["revision_count"] == 2

  registry_revision_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_revision_list"],
    app=app,
    path_params={"registry_id": registry_payload["registry_id"]},
  )
  assert [item["action"] for item in registry_revision_payload["history"][:2]] == ["updated", "created"]
  created_registry_revision_id = registry_revision_payload["history"][-1]["revision_id"]

  deleted_registry_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_delete"],
    app=app,
    path_params={"registry_id": registry_payload["registry_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "retire_registry_board",
    },
  )
  assert deleted_registry_payload["status"] == "deleted"
  assert deleted_registry_payload["revision_count"] == 3

  restored_registry_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_revision_restore"],
    app=app,
    path_params={
      "registry_id": registry_payload["registry_id"],
      "revision_id": created_registry_revision_id,
    },
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "restore_linked_registry",
    },
  )
  assert restored_registry_payload["status"] == "active"
  assert restored_registry_payload["template_id"] == template_payload["template_id"]
  assert restored_registry_payload["revision_count"] == 4

  bulk_registry_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_create"],
    app=app,
    request_payload={
      "name": "Failure board",
      "description": "Failure narrative board.",
      "query": {
        "focus_scope": "all_focuses",
        "scheduler_alert_category": "scheduler_failure",
        "scheduler_alert_status": "resolved",
        "scheduler_alert_narrative_facet": "resolved_narratives",
        "window_days": 14,
        "result_limit": 8,
      },
      "layout": {
        "highlight_panel": "rollups",
        "show_rollups": True,
        "show_time_series": False,
        "show_recent_exports": False,
      },
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  bulk_delete_registry_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_bulk_governance"],
    app=app,
    request_payload={
      "action": "delete",
      "registry_ids": [registry_payload["registry_id"], bulk_registry_payload["registry_id"]],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "bulk_registry_governance_delete",
    },
  )
  assert bulk_delete_registry_payload["action"] == "delete"
  assert bulk_delete_registry_payload["requested_count"] == 2
  assert bulk_delete_registry_payload["applied_count"] == 2
  assert {item["status"] for item in bulk_delete_registry_payload["results"]} == {"deleted"}

  bulk_restore_registry_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_bulk_governance"],
    app=app,
    request_payload={
      "action": "restore",
      "registry_ids": [registry_payload["registry_id"], bulk_registry_payload["registry_id"]],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "bulk_registry_governance_restore",
    },
  )
  assert bulk_restore_registry_payload["action"] == "restore"
  assert bulk_restore_registry_payload["applied_count"] == 2
  assert all(item["status"] == "active" for item in bulk_restore_registry_payload["results"])

  bulk_update_registry_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_bulk_governance"],
    app=app,
    request_payload={
      "action": "update",
      "registry_ids": [registry_payload["registry_id"], bulk_registry_payload["registry_id"]],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "bulk_registry_governance_update",
      "name_suffix": " / governed",
      "description_append": "shared",
      "template_id": template_payload["template_id"],
      "query_patch": {
        "scheduler_alert_category": "scheduler_failure",
        "scheduler_alert_status": "active",
        "scheduler_alert_narrative_facet": "resolved_narratives",
        "window_days": 11,
        "result_limit": 7,
      },
      "layout_patch": {
        "show_rollups": True,
        "show_time_series": False,
        "show_recent_exports": True,
      },
    },
  )
  assert bulk_update_registry_payload["action"] == "update"
  assert bulk_update_registry_payload["applied_count"] == 2
  updated_registry_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_list"],
    app=app,
    filters={
      "template_id": template_payload["template_id"],
      "category": "scheduler_failure",
      "narrative_facet": "resolved_narratives",
      "limit": 10,
    },
  )
  assert updated_registry_list_payload["total"] == 2
  assert all(item["name"].endswith(" / governed") for item in updated_registry_list_payload["items"])
  assert all(item["template_id"] == template_payload["template_id"] for item in updated_registry_list_payload["items"])
  assert all(item["layout"]["show_recent_exports"] is True for item in updated_registry_list_payload["items"])

  governance_policy_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_template_create"],
    app=app,
    request_payload={
      "name": "Shift lead staged updates",
      "description": "Reusable high-priority update lane.",
      "item_type_scope": "any",
      "action_scope": "update",
      "approval_lane": "shift_lead",
      "approval_priority": "high",
      "guidance": "Review with the active shift lead before apply.",
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  assert governance_policy_template_payload["approval_lane"] == "shift_lead"
  assert governance_policy_template_payload["approval_priority"] == "high"

  governance_policy_template_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_template_list"],
    app=app,
    filters={"action_scope": "update", "approval_priority": "high", "limit": 10},
  )
  assert governance_policy_template_list_payload["total"] == 1
  assert governance_policy_template_list_payload["items"][0]["policy_template_id"] == (
    governance_policy_template_payload["policy_template_id"]
  )
  assert governance_policy_template_list_payload["items"][0]["revision_count"] == 1

  updated_governance_policy_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_template_update"],
    app=app,
    path_params={"policy_template_id": governance_policy_template_payload["policy_template_id"]},
    request_payload={
      "description": "Reusable high-priority update lane with team review.",
      "approval_priority": "critical",
      "guidance": "Review with the active shift lead and incident commander before apply.",
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "scheduler_governance_policy_template_manual_update",
    },
  )
  assert updated_governance_policy_template_payload["approval_priority"] == "critical"
  assert updated_governance_policy_template_payload["revision_count"] == 2

  governance_policy_template_revision_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_list"],
    app=app,
    path_params={"policy_template_id": governance_policy_template_payload["policy_template_id"]},
  )
  assert governance_policy_template_revision_payload["policy_template"]["policy_template_id"] == (
    governance_policy_template_payload["policy_template_id"]
  )
  assert governance_policy_template_revision_payload["history"][0]["action"] == "updated"
  assert governance_policy_template_revision_payload["history"][-1]["action"] == "created"

  deleted_governance_policy_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_template_delete"],
    app=app,
    path_params={"policy_template_id": governance_policy_template_payload["policy_template_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "scheduler_governance_policy_template_manual_delete",
    },
  )
  assert deleted_governance_policy_template_payload["status"] == "deleted"
  assert deleted_governance_policy_template_payload["revision_count"] == 3

  restored_governance_policy_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_template_revision_restore"],
    app=app,
    path_params={
      "policy_template_id": governance_policy_template_payload["policy_template_id"],
      "revision_id": governance_policy_template_revision_payload["history"][0]["revision_id"],
    },
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "scheduler_governance_policy_template_restore_latest_revision",
    },
  )
  assert restored_governance_policy_template_payload["status"] == "active"
  assert restored_governance_policy_template_payload["revision_count"] == 4

  governance_policy_template_audit_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_template_audit_list"],
    app=app,
    filters={
      "policy_template_id": governance_policy_template_payload["policy_template_id"],
      "limit": 10,
    },
  )
  assert [item["action"] for item in governance_policy_template_audit_payload["items"][:4]] == [
    "restored",
    "deleted",
    "updated",
    "created",
  ]

  governance_policy_catalog_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_create"],
    app=app,
    request_payload={
      "name": "Shift lead batch catalog",
      "description": "Reusable queue defaults for staged shift-lead reviews.",
      "policy_template_ids": [governance_policy_template_payload["policy_template_id"]],
      "default_policy_template_id": governance_policy_template_payload["policy_template_id"],
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  assert governance_policy_catalog_payload["default_policy_template_id"] == (
    governance_policy_template_payload["policy_template_id"]
  )
  assert governance_policy_catalog_payload["approval_priority"] == "critical"

  governance_policy_catalog_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_list"],
    app=app,
    filters={"search": "shift lead batch", "limit": 10},
  )
  assert governance_policy_catalog_list_payload["total"] == 1
  assert governance_policy_catalog_list_payload["items"][0]["catalog_id"] == governance_policy_catalog_payload["catalog_id"]

  updated_governance_policy_catalog_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_update"],
    app=app,
    path_params={"catalog_id": governance_policy_catalog_payload["catalog_id"]},
    request_payload={
      "name": "Shift lead batch catalog / reviewed",
      "description": "Reusable queue defaults for reviewed shift-lead policies.",
      "policy_template_ids": [governance_policy_template_payload["policy_template_id"]],
      "default_policy_template_id": governance_policy_template_payload["policy_template_id"],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "scheduler_governance_policy_catalog_update",
    },
  )
  assert updated_governance_policy_catalog_payload["name"].endswith("/ reviewed")
  assert updated_governance_policy_catalog_payload["revision_count"] == 2

  deleted_governance_policy_catalog_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_delete"],
    app=app,
    path_params={"catalog_id": governance_policy_catalog_payload["catalog_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "scheduler_governance_policy_catalog_delete",
    },
  )
  assert deleted_governance_policy_catalog_payload["status"] == "deleted"

  governance_policy_catalog_revision_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list"],
    app=app,
    path_params={"catalog_id": governance_policy_catalog_payload["catalog_id"]},
  )
  assert governance_policy_catalog_revision_payload["current"]["status"] == "deleted"
  assert governance_policy_catalog_revision_payload["history"][0]["action"] == "deleted"

  restored_governance_policy_catalog_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_restore"],
    app=app,
    path_params={
      "catalog_id": governance_policy_catalog_payload["catalog_id"],
      "revision_id": governance_policy_catalog_revision_payload["history"][-1]["revision_id"],
    },
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "scheduler_governance_policy_catalog_restore",
    },
  )
  assert restored_governance_policy_catalog_payload["status"] == "active"
  assert restored_governance_policy_catalog_payload["revision_count"] == 4

  governance_policy_catalog_audit_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_audit_list"],
    app=app,
    filters={
      "catalog_id": governance_policy_catalog_payload["catalog_id"],
      "limit": 10,
    },
  )
  assert [item["action"] for item in governance_policy_catalog_audit_payload["items"][:4]] == [
    "restored",
    "deleted",
    "updated",
    "created",
  ]

  bulk_governance_policy_catalog_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_bulk_governance"],
    app=app,
    request_payload={
      "action": "update",
      "catalog_ids": [governance_policy_catalog_payload["catalog_id"]],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "scheduler_governance_policy_catalog_bulk_update",
      "name_suffix": " / bulk",
    },
  )
  assert bulk_governance_policy_catalog_payload["applied_count"] == 1
  refreshed_governance_policy_catalog_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_list"],
    app=app,
    filters={"search": "/ bulk", "limit": 10},
  )
  assert refreshed_governance_policy_catalog_payload["items"][0]["name"].endswith("/ bulk")

  template_governance_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_create"],
    app=app,
    request_payload={
      "item_type": "template",
      "item_ids": [template_payload["template_id"], bulk_template_payload["template_id"]],
      "action": "update",
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "stage_template_governance_plan",
      "name_suffix": " / staged",
      "query_patch": {
        "scheduler_alert_status": "resolved",
      },
      "policy_template_id": governance_policy_template_payload["policy_template_id"],
    },
  )
  assert template_governance_plan_payload["status"] == "previewed"
  assert template_governance_plan_payload["preview_changed_count"] == 2
  assert template_governance_plan_payload["rollback_ready_count"] == 2
  assert template_governance_plan_payload["policy_template_id"] == governance_policy_template_payload["policy_template_id"]
  assert template_governance_plan_payload["approval_lane"] == "shift_lead"
  assert template_governance_plan_payload["approval_priority"] == "critical"
  assert any("name" in item["changed_fields"] for item in template_governance_plan_payload["preview_items"])

  governance_plan_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_list"],
    app=app,
    filters={"item_type": "template", "status": "previewed", "limit": 10},
  )
  assert governance_plan_list_payload["total"] >= 1
  assert governance_plan_list_payload["items"][0]["plan_id"] == template_governance_plan_payload["plan_id"]

  approved_template_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_approve"],
    app=app,
    path_params={"plan_id": template_governance_plan_payload["plan_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "note": "approved for shift rollout",
    },
  )
  assert approved_template_plan_payload["status"] == "approved"
  assert approved_template_plan_payload["approved_at"] is not None

  applied_template_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_apply"],
    app=app,
    path_params={"plan_id": template_governance_plan_payload["plan_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
    },
  )
  assert applied_template_plan_payload["status"] == "applied"
  assert applied_template_plan_payload["applied_result"]["applied_count"] == 2
  staged_template_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_template_list"],
    app=app,
    filters={"category": "scheduler_failure", "narrative_facet": "recurring_occurrences", "limit": 10},
  )
  assert all(item["name"].endswith(" / staged") for item in staged_template_list_payload["items"])

  rolled_back_template_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_rollback"],
    app=app,
    path_params={"plan_id": template_governance_plan_payload["plan_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "note": "rollback after review",
    },
  )
  assert rolled_back_template_plan_payload["status"] == "rolled_back"
  assert rolled_back_template_plan_payload["rollback_result"]["applied_count"] == 2
  reverted_template_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_template_list"],
    app=app,
    filters={"category": "scheduler_failure", "narrative_facet": "recurring_occurrences", "limit": 10},
  )
  assert all(not item["name"].endswith(" / staged") for item in reverted_template_list_payload["items"])

  registry_governance_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_create"],
    app=app,
    request_payload={
      "item_type": "registry",
      "item_ids": [registry_payload["registry_id"], bulk_registry_payload["registry_id"]],
      "action": "update",
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "stage_registry_governance_plan",
      "clear_template_link": True,
      "layout_patch": {
        "show_time_series": True,
      },
      "policy_template_id": governance_policy_template_payload["policy_template_id"],
    },
  )
  assert registry_governance_plan_payload["status"] == "previewed"
  assert registry_governance_plan_payload["preview_changed_count"] == 2
  assert registry_governance_plan_payload["policy_template_name"] == "Shift lead staged updates"
  assert any(
    "template_id" in item["changed_fields"] or "layout" in item["changed_fields"]
    for item in registry_governance_plan_payload["preview_items"]
  )

  approved_registry_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_approve"],
    app=app,
    path_params={"plan_id": registry_governance_plan_payload["plan_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
    },
  )
  assert approved_registry_plan_payload["status"] == "approved"

  applied_registry_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_apply"],
    app=app,
    path_params={"plan_id": registry_governance_plan_payload["plan_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
    },
  )
  assert applied_registry_plan_payload["status"] == "applied"
  registry_without_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_list"],
    app=app,
    filters={"category": "scheduler_failure", "narrative_facet": "resolved_narratives", "limit": 10},
  )
  assert all(item["template_id"] is None for item in registry_without_template_payload["items"])

  rolled_back_registry_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_rollback"],
    app=app,
    path_params={"plan_id": registry_governance_plan_payload["plan_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
    },
  )
  assert rolled_back_registry_plan_payload["status"] == "rolled_back"
  reverted_registry_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_registry_list"],
    app=app,
    filters={
      "template_id": template_payload["template_id"],
      "category": "scheduler_failure",
      "narrative_facet": "resolved_narratives",
      "limit": 10,
    },
  )
  assert reverted_registry_list_payload["total"] == 2

  stitched_report_view_governance_policy_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_template_create"],
    app=app,
    request_payload={
      "name": "Stitched report staged updates",
      "description": "Reusable staged review lane for saved stitched scheduler reports.",
      "item_type_scope": "stitched_report_view",
      "action_scope": "update",
      "approval_lane": "scheduler_reports",
      "approval_priority": "high",
      "guidance": "Review stitched report diffs before cross-shift apply.",
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  assert stitched_report_view_governance_policy_template_payload["item_type_scope"] == (
    "stitched_report_view"
  )

  stitched_report_view_governance_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_create"],
    app=app,
    request_payload={
      "item_type": "stitched_report_view",
      "item_ids": [
        stitched_report_view_payload["view_id"],
        secondary_stitched_report_view_payload["view_id"],
      ],
      "action": "update",
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "stage_stitched_report_view_governance_plan",
      "name_suffix": " / staged",
      "query_patch": {
        "scheduler_alert_status": "resolved",
      },
      "occurrence_limit": 11,
      "history_limit": 21,
      "drilldown_history_limit": 23,
      "policy_template_id": stitched_report_view_governance_policy_template_payload["policy_template_id"],
    },
  )
  assert stitched_report_view_governance_plan_payload["status"] == "previewed"
  assert stitched_report_view_governance_plan_payload["item_type"] == "stitched_report_view"
  assert stitched_report_view_governance_plan_payload["preview_changed_count"] == 2
  assert stitched_report_view_governance_plan_payload["policy_template_id"] == (
    stitched_report_view_governance_policy_template_payload["policy_template_id"]
  )
  assert stitched_report_view_governance_plan_payload["approval_lane"] == "scheduler_reports"
  assert stitched_report_view_governance_plan_payload["approval_priority"] == "high"
  assert stitched_report_view_governance_plan_payload["request_payload"]["occurrence_limit"] == 11
  assert stitched_report_view_governance_plan_payload["request_payload"]["history_limit"] == 21
  assert stitched_report_view_governance_plan_payload["request_payload"]["drilldown_history_limit"] == 23
  assert any(
    "occurrence_limit" in item["changed_fields"] or "history_limit" in item["changed_fields"]
    for item in stitched_report_view_governance_plan_payload["preview_items"]
  )

  stitched_report_view_governance_plan_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_list"],
    app=app,
    filters={"item_type": "stitched_report_view", "status": "previewed", "limit": 10},
  )
  assert stitched_report_view_governance_plan_list_payload["total"] >= 1
  assert stitched_report_view_governance_plan_payload["plan_id"] in {
    item["plan_id"] for item in stitched_report_view_governance_plan_list_payload["items"]
  }

  approved_stitched_report_view_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_approve"],
    app=app,
    path_params={"plan_id": stitched_report_view_governance_plan_payload["plan_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "note": "approved stitched view rollout",
    },
  )
  assert approved_stitched_report_view_plan_payload["status"] == "approved"

  applied_stitched_report_view_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_apply"],
    app=app,
    path_params={"plan_id": stitched_report_view_governance_plan_payload["plan_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
    },
  )
  assert applied_stitched_report_view_plan_payload["status"] == "applied"
  assert applied_stitched_report_view_plan_payload["applied_result"]["applied_count"] == 2
  staged_stitched_report_view_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_list"],
    app=app,
    filters={"category": "scheduler_failure", "status": "active", "limit": 10},
  )
  assert all(
    item["name"].endswith(" / staged")
    and item["occurrence_limit"] == 11
    and item["history_limit"] == 21
    and item["drilldown_history_limit"] == 23
    for item in staged_stitched_report_view_list_payload["items"]
  )

  rolled_back_stitched_report_view_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_rollback"],
    app=app,
    path_params={"plan_id": stitched_report_view_governance_plan_payload["plan_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "note": "rollback stitched view staged rollout",
    },
  )
  assert rolled_back_stitched_report_view_plan_payload["status"] == "rolled_back"
  assert rolled_back_stitched_report_view_plan_payload["rollback_result"]["applied_count"] == 2
  reverted_stitched_report_view_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_view_list"],
    app=app,
    filters={"category": "scheduler_failure", "status": "active", "limit": 10},
  )
  assert all(
    not item["name"].endswith(" / staged")
    and item["occurrence_limit"] == 9
    and item["history_limit"] == 20
    and item["drilldown_history_limit"] == 22
    for item in reverted_stitched_report_view_list_payload["items"]
  )

  stitched_report_governance_registry_policy_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_template_create"],
    app=app,
    request_payload={
      "name": "Stitched governance registry staged updates",
      "description": "Reusable staged review lane for stitched governance registry updates.",
      "item_type_scope": "stitched_report_governance_registry",
      "action_scope": "update",
      "approval_lane": "stitched_registry",
      "approval_priority": "critical",
      "guidance": "Review stitched queue bundles before apply.",
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  assert stitched_report_governance_registry_policy_template_payload["item_type_scope"] == (
    "stitched_report_governance_registry"
  )
  stitched_report_governance_registry_policy_template_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_policy_template_list"],
    app=app,
    filters={"limit": 10},
  )
  assert stitched_report_governance_registry_policy_template_payload["policy_template_id"] in {
    item["policy_template_id"]
    for item in stitched_report_governance_registry_policy_template_list_payload["items"]
  }

  stitched_report_view_default_policy_catalog_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_create"],
    app=app,
    request_payload={
      "name": "Stitched report default review catalog",
      "description": "Reusable default-policy bundle for stitched governance registries.",
      "policy_template_ids": [
        stitched_report_view_governance_policy_template_payload["policy_template_id"],
      ],
      "default_policy_template_id": stitched_report_view_governance_policy_template_payload[
        "policy_template_id"
      ],
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  assert stitched_report_view_default_policy_catalog_payload["item_type_scope"] == (
    "stitched_report_view"
  )

  stitched_report_governance_registry_policy_catalog_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_create"],
    app=app,
    request_payload={
      "name": "Stitched governance registry staged catalog",
      "description": "Reusable approval defaults for stitched governance registry plans.",
      "policy_template_ids": [
        stitched_report_governance_registry_policy_template_payload["policy_template_id"],
      ],
      "default_policy_template_id": stitched_report_governance_registry_policy_template_payload[
        "policy_template_id"
      ],
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  assert stitched_report_governance_registry_policy_catalog_payload["item_type_scope"] == (
    "stitched_report_governance_registry"
  )
  stitched_report_governance_registry_policy_catalog_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_policy_catalog_list"],
    app=app,
    filters={"limit": 10},
  )
  assert stitched_report_governance_registry_policy_catalog_payload["catalog_id"] in {
    item["catalog_id"]
    for item in stitched_report_governance_registry_policy_catalog_list_payload["items"]
  }

  stitched_governance_registry_governance_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_plan_create"],
    app=app,
    request_payload={
      "item_ids": [
        stitched_governance_registry_payload["registry_id"],
        secondary_stitched_governance_registry_payload["registry_id"],
      ],
      "action": "update",
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "stage_stitched_report_governance_registry_governance_plan",
      "name_suffix": " / staged",
      "queue_view_patch": {
        "queue_state": "pending_approval",
        "approval_lane": "scheduler_reports",
        "approval_priority": "high",
        "search": "staged stitched handoff",
        "sort": "queue_priority",
      },
      "default_policy_template_id": stitched_report_view_governance_policy_template_payload[
        "policy_template_id"
      ],
      "default_policy_catalog_id": stitched_report_view_default_policy_catalog_payload["catalog_id"],
      "policy_catalog_id": stitched_report_governance_registry_policy_catalog_payload["catalog_id"],
    },
  )
  assert stitched_governance_registry_governance_plan_payload["status"] == "previewed"
  assert stitched_governance_registry_governance_plan_payload["item_type"] == (
    "stitched_report_governance_registry"
  )
  assert stitched_governance_registry_governance_plan_payload["preview_changed_count"] == 2
  assert stitched_governance_registry_governance_plan_payload["policy_catalog_id"] == (
    stitched_report_governance_registry_policy_catalog_payload["catalog_id"]
  )
  assert stitched_governance_registry_governance_plan_payload["policy_template_id"] == (
    stitched_report_governance_registry_policy_template_payload["policy_template_id"]
  )
  assert stitched_governance_registry_governance_plan_payload["approval_lane"] == "stitched_registry"
  assert stitched_governance_registry_governance_plan_payload["approval_priority"] == "critical"
  assert stitched_governance_registry_governance_plan_payload["request_payload"]["queue_view_patch"] == {
    "queue_state": "pending_approval",
    "approval_lane": "scheduler_reports",
    "approval_priority": "high",
    "search": "staged stitched handoff",
    "sort": "queue_priority",
  }
  assert stitched_governance_registry_governance_plan_payload["request_payload"][
    "default_policy_template_id"
  ] == stitched_report_view_governance_policy_template_payload["policy_template_id"]
  assert stitched_governance_registry_governance_plan_payload["request_payload"][
    "default_policy_catalog_id"
  ] == stitched_report_view_default_policy_catalog_payload["catalog_id"]
  assert any("queue_view" in item["changed_fields"] for item in stitched_governance_registry_governance_plan_payload["preview_items"])
  assert any(
    "default_policy_template_id" in item["changed_fields"]
    or "default_policy_catalog_id" in item["changed_fields"]
    for item in stitched_governance_registry_governance_plan_payload["preview_items"]
  )

  stitched_governance_registry_governance_plan_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_plan_list"],
    app=app,
    filters={
      "status": "previewed",
      "limit": 10,
    },
  )
  assert stitched_governance_registry_governance_plan_list_payload["total"] >= 1
  assert stitched_governance_registry_governance_plan_payload["plan_id"] in {
    item["plan_id"] for item in stitched_governance_registry_governance_plan_list_payload["items"]
  }

  approved_stitched_governance_registry_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_plan_approve"],
    app=app,
    path_params={"plan_id": stitched_governance_registry_governance_plan_payload["plan_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "note": "approved stitched governance registry rollout",
    },
  )
  assert approved_stitched_governance_registry_plan_payload["status"] == "approved"

  applied_stitched_governance_registry_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_plan_apply"],
    app=app,
    path_params={"plan_id": stitched_governance_registry_governance_plan_payload["plan_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
    },
  )
  assert applied_stitched_governance_registry_plan_payload["status"] == "applied"
  assert applied_stitched_governance_registry_plan_payload["applied_result"]["applied_count"] == 2

  staged_stitched_governance_registry_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_list"],
    app=app,
    filters={"search": "Shift /", "limit": 10},
  )
  staged_stitched_governance_registry_items = {
    item["registry_id"]: item for item in staged_stitched_governance_registry_list_payload["items"]
  }
  assert {
    stitched_governance_registry_payload["registry_id"],
    secondary_stitched_governance_registry_payload["registry_id"],
  }.issubset(staged_stitched_governance_registry_items)
  assert all(
    item["name"].endswith(" / staged")
    and item["queue_view"]["queue_state"] == "pending_approval"
    and item["queue_view"]["approval_lane"] == "scheduler_reports"
    and item["queue_view"]["approval_priority"] == "high"
    and item["queue_view"]["search"] == "staged stitched handoff"
    and item["queue_view"]["sort"] == "queue_priority"
    and item["default_policy_template_id"]
    == stitched_report_view_governance_policy_template_payload["policy_template_id"]
    and item["default_policy_catalog_id"] == stitched_report_view_default_policy_catalog_payload["catalog_id"]
    for item in staged_stitched_governance_registry_items.values()
  )

  rolled_back_stitched_governance_registry_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_plan_rollback"],
    app=app,
    path_params={"plan_id": stitched_governance_registry_governance_plan_payload["plan_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "note": "rollback stitched governance registry rollout",
    },
  )
  assert rolled_back_stitched_governance_registry_plan_payload["status"] == "rolled_back"
  assert rolled_back_stitched_governance_registry_plan_payload["rollback_result"]["applied_count"] == 2

  reverted_stitched_governance_registry_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_stitched_report_governance_registry_list"],
    app=app,
    filters={"search": "Shift /", "limit": 10},
  )
  reverted_stitched_governance_registry_items = {
    item["registry_id"]: item
    for item in reverted_stitched_governance_registry_list_payload["items"]
    if item["registry_id"] in staged_stitched_governance_registry_items
  }
  assert len(reverted_stitched_governance_registry_items) == 2
  assert all(
    not item["name"].endswith(" / staged")
    and item["queue_view"]["queue_state"] == "ready_to_apply"
    and item["queue_view"]["approval_priority"] == "critical"
    and item["queue_view"]["search"] == "reviewed handoff"
    and item["queue_view"]["sort"] == "updated_desc"
    and item["default_policy_template_id"] is None
    and item["default_policy_catalog_id"] is None
    for item in reverted_stitched_governance_registry_items.values()
  )

  batch_template_governance_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_create"],
    app=app,
    request_payload={
      "item_type": "template",
      "item_ids": [template_payload["template_id"]],
      "action": "update",
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "batch_template_governance_plan",
      "name_suffix": " / batch",
      "policy_template_id": governance_policy_template_payload["policy_template_id"],
    },
  )
  batch_registry_governance_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_create"],
    app=app,
    request_payload={
      "item_type": "registry",
      "item_ids": [registry_payload["registry_id"]],
      "action": "update",
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "batch_registry_governance_plan",
      "layout_patch": {
        "show_rollups": False,
      },
      "policy_template_id": governance_policy_template_payload["policy_template_id"],
    },
  )
  batch_approve_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_batch_action"],
    app=app,
    request_payload={
      "action": "approve",
      "plan_ids": [
        batch_template_governance_plan_payload["plan_id"],
        batch_registry_governance_plan_payload["plan_id"],
      ],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "note": "batch approval",
    },
  )
  assert batch_approve_payload["succeeded_count"] == 2
  assert all(item["status"] == "approved" for item in batch_approve_payload["results"] if item["plan"])

  batch_apply_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_batch_action"],
    app=app,
    request_payload={
      "action": "apply",
      "plan_ids": [
        batch_template_governance_plan_payload["plan_id"],
        batch_registry_governance_plan_payload["plan_id"],
      ],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
    },
  )
  assert batch_apply_payload["succeeded_count"] == 2
  assert all(item["status"] == "applied" for item in batch_apply_payload["results"] if item["plan"])

  captured_governance_policy_catalog_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_capture"],
    app=app,
    path_params={"catalog_id": governance_policy_catalog_payload["catalog_id"]},
    request_payload={
      "hierarchy_steps": [
        {
          "item_type": "template",
          "item_ids": [template_payload["template_id"]],
          "name_suffix": " / catalog",
          "query_patch": {
            "scheduler_alert_status": "resolved",
          },
        },
        {
          "item_type": "registry",
          "item_ids": [registry_payload["registry_id"]],
          "layout_patch": {
            "show_recent_exports": True,
          },
        },
      ],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "capture_catalog_hierarchy",
    },
  )
  assert len(captured_governance_policy_catalog_payload["hierarchy_steps"]) == 2
  template_hierarchy_step_id = captured_governance_policy_catalog_payload["hierarchy_steps"][0]["step_id"]
  registry_hierarchy_step_id = captured_governance_policy_catalog_payload["hierarchy_steps"][1]["step_id"]

  updated_catalog_hierarchy_step_payload = execute_standalone_surface_binding(
    binding=bindings_by_key[
      "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_update"
    ],
    app=app,
    path_params={
      "catalog_id": governance_policy_catalog_payload["catalog_id"],
      "step_id": template_hierarchy_step_id,
    },
    request_payload={
      "name_prefix": "Reviewed / ",
      "query_patch": {
        "scheduler_alert_status": "active",
      },
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "update_catalog_hierarchy_step",
    },
  )
  assert updated_catalog_hierarchy_step_payload["hierarchy_steps"][0]["name_prefix"] == "Reviewed / "
  assert (
    updated_catalog_hierarchy_step_payload["hierarchy_steps"][0]["query_patch"]["scheduler_alert_status"]
    == "active"
  )

  bulk_governed_catalog_hierarchy_step_payload = execute_standalone_surface_binding(
    binding=bindings_by_key[
      "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_bulk_governance"
    ],
    app=app,
    path_params={"catalog_id": governance_policy_catalog_payload["catalog_id"]},
    request_payload={
      "action": "update",
      "step_ids": [registry_hierarchy_step_id],
      "layout_patch": {
        "show_time_series": True,
      },
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "bulk_update_catalog_hierarchy_step",
    },
  )
  assert bulk_governed_catalog_hierarchy_step_payload["applied_count"] == 1

  catalog_history_after_bulk_update_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list"],
    app=app,
    path_params={"catalog_id": governance_policy_catalog_payload["catalog_id"]},
  )
  assert catalog_history_after_bulk_update_payload["history"][0]["action"] == "hierarchy_steps_bulk_updated"
  template_hierarchy_restore_revision_id = next(
    entry["revision_id"]
    for entry in reversed(catalog_history_after_bulk_update_payload["history"])
    if any(step["step_id"] == template_hierarchy_step_id for step in entry["hierarchy_steps"])
  )

  restored_catalog_hierarchy_step_payload = execute_standalone_surface_binding(
    binding=bindings_by_key[
      "operator_provider_provenance_scheduler_narrative_governance_policy_catalog_hierarchy_step_restore"
    ],
    app=app,
    path_params={
      "catalog_id": governance_policy_catalog_payload["catalog_id"],
      "step_id": template_hierarchy_step_id,
      "revision_id": template_hierarchy_restore_revision_id,
    },
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "restore_catalog_hierarchy_step_revision",
    },
  )
  assert restored_catalog_hierarchy_step_payload["hierarchy_steps"][0]["name_prefix"] is None

  secondary_governance_policy_catalog_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_create"],
    app=app,
    request_payload={
      "name": "Shift lead secondary catalog",
      "description": "Secondary reusable queue defaults for cross-catalog governance.",
      "policy_template_ids": [governance_policy_template_payload["policy_template_id"]],
      "default_policy_template_id": governance_policy_template_payload["policy_template_id"],
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )

  hierarchy_step_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key[
      "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_create"
    ],
    app=app,
    request_payload={
      "name": "Cross-catalog template sync",
      "description": "Reusable hierarchy step for template governance sync.",
      "origin_catalog_id": governance_policy_catalog_payload["catalog_id"],
      "origin_step_id": template_hierarchy_step_id,
      "governance_policy_catalog_id": governance_policy_catalog_payload["catalog_id"],
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  assert hierarchy_step_template_payload["origin_catalog_id"] == governance_policy_catalog_payload["catalog_id"]
  assert hierarchy_step_template_payload["origin_step_id"] == template_hierarchy_step_id
  assert hierarchy_step_template_payload["step"]["source_template_id"] is None
  assert (
    hierarchy_step_template_payload["governance_policy_catalog_id"]
    == governance_policy_catalog_payload["catalog_id"]
  )
  assert (
    hierarchy_step_template_payload["governance_policy_template_id"]
    == governance_policy_template_payload["policy_template_id"]
  )

  hierarchy_step_template_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key[
      "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_list"
    ],
    app=app,
    filters={"search": "cross-catalog", "limit": 10},
  )
  assert hierarchy_step_template_list_payload["total"] == 1
  assert (
    hierarchy_step_template_list_payload["items"][0]["hierarchy_step_template_id"]
    == hierarchy_step_template_payload["hierarchy_step_template_id"]
  )
  assert hierarchy_step_template_list_payload["items"][0]["revision_count"] == 1

  secondary_hierarchy_step_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key[
      "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_create"
    ],
    app=app,
    request_payload={
      "name": "Registry rollout sync",
      "description": "Reusable hierarchy step for registry governance sync.",
      "origin_catalog_id": governance_policy_catalog_payload["catalog_id"],
      "origin_step_id": registry_hierarchy_step_id,
      "governance_policy_catalog_id": governance_policy_catalog_payload["catalog_id"],
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  assert (
    secondary_hierarchy_step_template_payload["governance_policy_template_id"]
    == governance_policy_template_payload["policy_template_id"]
  )

  updated_hierarchy_step_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key[
      "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_update"
    ],
    app=app,
    path_params={
      "hierarchy_step_template_id": hierarchy_step_template_payload["hierarchy_step_template_id"],
    },
    request_payload={
      "description": "Reusable hierarchy step for reviewed template governance sync.",
      "name_suffix": " / reviewed",
      "query_patch": {
        "scheduler_alert_status": "resolved",
      },
      "governance_approval_priority": "critical",
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "update_hierarchy_step_template",
    },
  )
  assert updated_hierarchy_step_template_payload["revision_count"] == 2
  assert updated_hierarchy_step_template_payload["step"]["name_suffix"] == " / reviewed"
  assert updated_hierarchy_step_template_payload["governance_approval_priority"] == "critical"

  hierarchy_step_template_revision_payload = execute_standalone_surface_binding(
    binding=bindings_by_key[
      "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_list"
    ],
    app=app,
    path_params={
      "hierarchy_step_template_id": hierarchy_step_template_payload["hierarchy_step_template_id"],
    },
  )
  assert hierarchy_step_template_revision_payload["current"]["hierarchy_step_template_id"] == (
    hierarchy_step_template_payload["hierarchy_step_template_id"]
  )
  assert hierarchy_step_template_revision_payload["history"][0]["action"] == "updated"

  deleted_hierarchy_step_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key[
      "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_delete"
    ],
    app=app,
    path_params={
      "hierarchy_step_template_id": hierarchy_step_template_payload["hierarchy_step_template_id"],
    },
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "delete_hierarchy_step_template",
    },
  )
  assert deleted_hierarchy_step_template_payload["status"] == "deleted"

  restored_hierarchy_step_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key[
      "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_restore"
    ],
    app=app,
    path_params={
      "hierarchy_step_template_id": hierarchy_step_template_payload["hierarchy_step_template_id"],
      "revision_id": hierarchy_step_template_revision_payload["history"][0]["revision_id"],
    },
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "restore_hierarchy_step_template_revision",
    },
  )
  assert restored_hierarchy_step_template_payload["status"] == "active"
  assert restored_hierarchy_step_template_payload["revision_count"] == 4

  bulk_governed_hierarchy_step_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key[
      "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_bulk_governance"
    ],
    app=app,
    request_payload={
      "action": "update",
      "hierarchy_step_template_ids": [hierarchy_step_template_payload["hierarchy_step_template_id"]],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "bulk_update_hierarchy_step_template",
      "name_suffix": " / bulk",
      "step_name_prefix": "Reviewed / ",
    },
  )
  assert bulk_governed_hierarchy_step_template_payload["applied_count"] == 1

  staged_hierarchy_step_template_plan_payload = execute_standalone_surface_binding(
    binding=bindings_by_key[
      "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_stage"
    ],
    app=app,
    path_params={
      "hierarchy_step_template_id": hierarchy_step_template_payload["hierarchy_step_template_id"],
    },
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "stage_hierarchy_step_template",
    },
  )
  assert (
    staged_hierarchy_step_template_plan_payload["source_hierarchy_step_template_id"]
    == hierarchy_step_template_payload["hierarchy_step_template_id"]
  )
  assert staged_hierarchy_step_template_plan_payload["source_hierarchy_step_template_name"] == (
    "Cross-catalog template sync / bulk"
  )
  assert (
    staged_hierarchy_step_template_plan_payload["policy_catalog_id"]
    == governance_policy_catalog_payload["catalog_id"]
  )
  assert staged_hierarchy_step_template_plan_payload["approval_priority"] == "critical"

  batch_staged_hierarchy_step_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key[
      "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_batch_stage"
    ],
    app=app,
    request_payload={
      "hierarchy_step_template_ids": [
        hierarchy_step_template_payload["hierarchy_step_template_id"],
        secondary_hierarchy_step_template_payload["hierarchy_step_template_id"],
      ],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "stage_hierarchy_step_templates_batch",
    },
  )
  assert batch_staged_hierarchy_step_template_payload["action"] == "stage"
  assert batch_staged_hierarchy_step_template_payload["requested_count"] == 2
  assert batch_staged_hierarchy_step_template_payload["succeeded_count"] == 2
  assert {
    item["plan"]["source_hierarchy_step_template_id"]
    for item in batch_staged_hierarchy_step_template_payload["results"]
    if item["plan"] is not None
  } == {
    hierarchy_step_template_payload["hierarchy_step_template_id"],
    secondary_hierarchy_step_template_payload["hierarchy_step_template_id"],
  }

  hierarchy_step_template_audit_payload = execute_standalone_surface_binding(
    binding=bindings_by_key[
      "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_list"
    ],
    app=app,
    filters={
      "hierarchy_step_template_id": hierarchy_step_template_payload["hierarchy_step_template_id"],
      "limit": 10,
    },
  )
  hierarchy_step_template_audit_actions = [
    item["action"] for item in hierarchy_step_template_audit_payload["items"]
  ]
  assert "staged" in hierarchy_step_template_audit_actions
  assert hierarchy_step_template_audit_actions.count("updated") >= 2
  assert "restored" in hierarchy_step_template_audit_actions
  assert "deleted" in hierarchy_step_template_audit_actions
  assert "created" in hierarchy_step_template_audit_actions

  applied_hierarchy_step_template_payload = execute_standalone_surface_binding(
    binding=bindings_by_key[
      "operator_provider_provenance_scheduler_narrative_governance_hierarchy_step_template_apply"
    ],
    app=app,
    path_params={
      "hierarchy_step_template_id": hierarchy_step_template_payload["hierarchy_step_template_id"],
    },
    request_payload={
      "catalog_ids": [
        governance_policy_catalog_payload["catalog_id"],
        secondary_governance_policy_catalog_payload["catalog_id"],
      ],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "apply_hierarchy_step_template",
    },
  )
  assert applied_hierarchy_step_template_payload["applied_count"] == 2

  refreshed_primary_catalog_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list"],
    app=app,
    path_params={"catalog_id": governance_policy_catalog_payload["catalog_id"]},
  )
  primary_template_backed_step = next(
    step
    for step in refreshed_primary_catalog_payload["current"]["hierarchy_steps"]
    if step["step_id"] == template_hierarchy_step_id
  )
  assert (
    primary_template_backed_step["source_template_id"]
    == hierarchy_step_template_payload["hierarchy_step_template_id"]
  )
  assert primary_template_backed_step["name_prefix"] == "Reviewed / "

  refreshed_secondary_catalog_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_revision_list"],
    app=app,
    path_params={"catalog_id": secondary_governance_policy_catalog_payload["catalog_id"]},
  )
  assert len(refreshed_secondary_catalog_payload["current"]["hierarchy_steps"]) == 1
  assert (
    refreshed_secondary_catalog_payload["current"]["hierarchy_steps"][0]["source_template_id"]
    == hierarchy_step_template_payload["hierarchy_step_template_id"]
  )

  staged_governance_policy_catalog_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_policy_catalog_stage"],
    app=app,
    path_params={"catalog_id": governance_policy_catalog_payload["catalog_id"]},
    request_payload={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "stage_catalog_hierarchy",
    },
  )
  assert staged_governance_policy_catalog_payload["plan_count"] == 2
  assert all(
    item["policy_catalog_id"] == governance_policy_catalog_payload["catalog_id"]
    for item in staged_governance_policy_catalog_payload["plans"]
  )
  assert {
    item["hierarchy_position"]
    for item in staged_governance_policy_catalog_payload["plans"]
  } == {1, 2}

  governance_plan_catalog_slice_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_list"],
    app=app,
    filters={"policy_catalog_id": governance_policy_catalog_payload["catalog_id"], "limit": 10},
  )
  assert governance_plan_catalog_slice_payload["total"] >= 2
  assert all(
    item["policy_catalog_id"] == governance_policy_catalog_payload["catalog_id"]
    for item in governance_plan_catalog_slice_payload["items"][:2]
  )

  governance_plan_source_template_slice_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_narrative_governance_plan_list"],
    app=app,
    filters={
      "source_hierarchy_step_template_id": hierarchy_step_template_payload["hierarchy_step_template_id"],
      "search": hierarchy_step_template_payload["name"],
      "sort": "source_template_desc",
      "limit": 10,
    },
  )
  assert governance_plan_source_template_slice_payload["total"] >= 2
  assert all(
    item["source_hierarchy_step_template_id"] == hierarchy_step_template_payload["hierarchy_step_template_id"]
    for item in governance_plan_source_template_slice_payload["items"]
  )

  report_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduled_report_create"],
    app=app,
    request_payload={
      "name": "BTC weekly provenance report",
      "description": "Weekly roll-up for provider provenance.",
      "preset_id": preset_payload["preset_id"],
      "view_id": view_payload["view_id"],
      "cadence": "weekly",
      "status": "scheduled",
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  assert report_payload["cadence"] == "weekly"
  assert report_payload["status"] == "scheduled"
  assert report_payload["next_run_at"] == "2026-04-29T09:00:00+00:00"

  report_list_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduled_report_list"],
    app=app,
    filters={"status": "scheduled", "view_id": view_payload["view_id"], "limit": 10},
  )
  assert report_list_payload["total"] == 1
  assert report_list_payload["items"][0]["report_id"] == report_payload["report_id"]

  run_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduled_report_run"],
    app=app,
    path_params={"report_id": report_payload["report_id"]},
    request_payload={
      "source_tab_id": "tab_review",
      "source_tab_label": "Review tab",
    },
  )
  assert run_payload["report"]["last_export_job_id"] == run_payload["export_job"]["job_id"]
  assert run_payload["export_job"]["export_scope"] == "provider_provenance_analytics_report"
  assert run_payload["export_job"]["provider_provenance_count"] == 0

  history_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduled_report_history"],
    app=app,
    path_params={"report_id": report_payload["report_id"]},
  )
  assert {item["action"] for item in history_payload["history"]} == {"created", "ran"}
  assert any(item["export_job_id"] == run_payload["export_job"]["job_id"] for item in history_payload["history"])

  clock.advance(timedelta(days=7))
  due_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduled_report_run_due"],
    app=app,
    request_payload={
      "source_tab_id": "tab_scheduler",
      "source_tab_label": "Scheduler",
      "limit": 10,
    },
  )
  assert due_payload["executed_count"] == 1
  assert due_payload["items"][0]["report"]["report_id"] == report_payload["report_id"]

  clock.advance(timedelta(days=1))
  app.execute_provider_provenance_scheduler_cycle(
    source_tab_id="system:provider-provenance-scheduler",
    source_tab_label="Background scheduler",
  )

  scheduler_history_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_health_history"],
    app=app,
    filters={"limit": 1, "offset": 1},
  )
  assert scheduler_history_payload["current"]["status"] == "healthy"
  assert scheduler_history_payload["total"] == 1
  assert scheduler_history_payload["returned"] == 0
  assert scheduler_history_payload["query"]["offset"] == 1
  assert scheduler_history_payload["previous_offset"] == 0
  assert scheduler_history_payload["has_more"] is False
  assert scheduler_history_payload["items"] == []

  scheduler_history_first_page_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_health_history"],
    app=app,
    filters={"limit": 1, "offset": 0},
  )
  assert scheduler_history_first_page_payload["returned"] == 1
  assert scheduler_history_first_page_payload["next_offset"] is None
  assert scheduler_history_first_page_payload["items"][0]["status"] == "healthy"

  scheduler_analytics_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_health_analytics"],
    app=app,
    filters={
      "window_days": 3,
      "history_limit": 5,
      "drilldown_bucket_key": "2026-04-30",
      "drilldown_history_limit": 2,
    },
  )
  assert scheduler_analytics_payload["totals"]["record_count"] == 1
  assert scheduler_analytics_payload["time_series"]["health_status"]["summary"]["latest_status"] == "healthy"
  assert scheduler_analytics_payload["drill_down"]["bucket_key"] == "2026-04-30"
  assert scheduler_analytics_payload["drill_down"]["bucket_size"] == "hour"
  assert scheduler_analytics_payload["drill_down"]["history_limit"] == 2
  assert scheduler_analytics_payload["drill_down"]["history"][0]["record_id"] == (
    scheduler_history_first_page_payload["items"][0]["record_id"]
  )
  assert scheduler_analytics_payload["recent_history"][0]["record_id"] == (
    scheduler_history_first_page_payload["items"][0]["record_id"]
  )

  scheduler_export_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_health_export"],
    app=app,
    filters={
      "window_days": 3,
      "history_limit": 5,
      "drilldown_bucket_key": "2026-04-30",
      "drilldown_history_limit": 2,
      "limit": 1,
      "offset": 0,
      "format": "json",
    },
  )
  assert scheduler_export_payload["format"] == "json"
  assert scheduler_export_payload["record_count"] == 1
  assert scheduler_export_payload["total_count"] == 1
  assert "\"drill_down\"" in scheduler_export_payload["content"]

  scheduler_csv_export_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_scheduler_health_export"],
    app=app,
    filters={"limit": 1, "offset": 0, "format": "csv"},
  )
  assert scheduler_csv_export_payload["format"] == "csv"
  assert "record_id,recorded_at,status,summary" in scheduler_csv_export_payload["content"]
  assert scheduler_csv_export_payload["record_count"] == 1
  assert scheduler_csv_export_payload["total_count"] == 1

  shared_scheduler_export_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_export_job_create"],
    app=app,
    request_payload={
      "content": scheduler_export_payload["content"],
      "requested_by_tab_id": "tab_scheduler",
      "requested_by_tab_label": "Scheduler panel",
    },
  )
  assert shared_scheduler_export_payload["export_scope"] == "provider_provenance_scheduler_health"
  assert shared_scheduler_export_payload["focus_key"] == "provider-provenance-scheduler-health"
  assert shared_scheduler_export_payload["result_count"] == 1
  assert shared_scheduler_export_payload["routing_policy_id"] == "chatops_only"
  assert shared_scheduler_export_payload["routing_targets"] == ["slack_webhook"]
  assert shared_scheduler_export_payload["approval_state"] == "not_required"
  assert shared_scheduler_export_payload["available_delivery_targets"] == [
    "slack_webhook",
    "pagerduty_events",
  ]

  listed_scheduler_exports_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_export_job_list"],
    app=app,
    filters={"export_scope": "provider_provenance_scheduler_health", "limit": 10},
  )
  assert listed_scheduler_exports_payload["total"] >= 1
  assert any(
    item["job_id"] == shared_scheduler_export_payload["job_id"]
    for item in listed_scheduler_exports_payload["items"]
  )

  updated_scheduler_policy_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_export_job_policy"],
    app=app,
    path_params={"job_id": shared_scheduler_export_payload["job_id"]},
    request_payload={
      "actor": "operator",
      "routing_policy_id": "all_targets",
      "approval_policy_id": "manual_required",
      "source_tab_id": "tab_scheduler",
      "source_tab_label": "Scheduler panel",
    },
  )
  assert updated_scheduler_policy_payload["export_job"]["routing_policy_id"] == "all_targets"
  assert updated_scheduler_policy_payload["export_job"]["routing_targets"] == [
    "slack_webhook",
    "pagerduty_events",
  ]
  assert updated_scheduler_policy_payload["export_job"]["approval_state"] == "pending"
  assert updated_scheduler_policy_payload["audit_record"]["action"] == "policy_updated"

  with pytest.raises(ValueError, match="requires approval"):
    execute_standalone_surface_binding(
      binding=bindings_by_key["operator_provider_provenance_export_job_escalate"],
      app=app,
      path_params={"job_id": shared_scheduler_export_payload["job_id"]},
      request_payload={
        "actor": "operator",
        "reason": "scheduler_health_export_review",
        "source_tab_id": "tab_scheduler",
        "source_tab_label": "Scheduler panel",
      },
    )

  approved_scheduler_export_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_export_job_approval"],
    app=app,
    path_params={"job_id": shared_scheduler_export_payload["job_id"]},
    request_payload={
      "actor": "operator",
      "note": "manager_review_complete",
      "source_tab_id": "tab_scheduler",
      "source_tab_label": "Scheduler panel",
    },
  )
  assert approved_scheduler_export_payload["export_job"]["approval_state"] == "approved"
  assert approved_scheduler_export_payload["export_job"]["approved_by"] == "operator"
  assert approved_scheduler_export_payload["audit_record"]["action"] == "approved"

  escalated_scheduler_export_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_export_job_escalate"],
    app=app,
    path_params={"job_id": shared_scheduler_export_payload["job_id"]},
    request_payload={
      "actor": "operator",
      "reason": "scheduler_health_export_review",
      "source_tab_id": "tab_scheduler",
      "source_tab_label": "Scheduler panel",
    },
  )
  assert escalated_scheduler_export_payload["export_job"]["escalation_count"] == 1
  assert escalated_scheduler_export_payload["export_job"]["last_delivery_status"] == "delivered"
  assert escalated_scheduler_export_payload["audit_record"]["action"] == "escalated"
  assert escalated_scheduler_export_payload["audit_record"]["routing_policy_id"] == "all_targets"
  assert escalated_scheduler_export_payload["audit_record"]["approval_state"] == "approved"
  assert escalated_scheduler_export_payload["audit_record"]["delivery_targets"] == [
    "slack_webhook",
    "pagerduty_events",
  ]
  assert len(escalated_scheduler_export_payload["delivery_history"]) == 2
  assert {record["target"] for record in escalated_scheduler_export_payload["delivery_history"]} == {
    "slack_webhook",
    "pagerduty_events",
  }
  assert any(
    delivered_incident.alert_id.startswith("provider-provenance:scheduler-export:")
    for delivered_incident in delivery.delivered_incidents
  )

  shared_scheduler_export_history_payload = execute_standalone_surface_binding(
    binding=bindings_by_key["operator_provider_provenance_export_job_history"],
    app=app,
    path_params={"job_id": shared_scheduler_export_payload["job_id"]},
  )
  assert [record["action"] for record in shared_scheduler_export_history_payload["history"]] == [
    "escalated",
    "approved",
    "policy_updated",
    "created",
  ]
