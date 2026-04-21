from __future__ import annotations

from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
import inspect
import json
from pathlib import Path

from fastapi.testclient import TestClient
from akra_trader.adapters.in_memory import SeededMarketDataAdapter
from akra_trader.config import Settings
from akra_trader.domain.models import DatasetBoundaryContract
from akra_trader.domain.models import GapWindow
from akra_trader.domain.models import GuardedLiveBookTickerChannelSnapshot
from akra_trader.domain.models import GuardedLiveKlineChannelSnapshot
from akra_trader.domain.models import GuardedLiveOrderBookLevel
from akra_trader.domain.models import InstrumentStatus
from akra_trader.domain.models import MarketDataIngestionJobRecord
from akra_trader.domain.models import MarketDataLineageHistoryRecord
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync
from akra_trader.domain.models import GuardedLiveVenueBalance
from akra_trader.domain.models import GuardedLiveVenueOpenOrder
from akra_trader.domain.models import GuardedLiveVenueOrderResult
from akra_trader.domain.models import GuardedLiveVenueStateSnapshot
from akra_trader.domain.models import Order
from akra_trader.domain.models import OrderSide
from akra_trader.domain.models import OrderStatus
from akra_trader.domain.models import OrderType
from akra_trader.domain.models import Position
from akra_trader.domain.models import RunComparison
from akra_trader.domain.models import RunComparisonNarrative
from akra_trader.domain.models import RunComparisonRun
from akra_trader.domain.models import RunSurfaceCapabilities
from akra_trader.domain.models import ProviderProvenanceSchedulerHealth
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import SyncFailure
from akra_trader.main import create_app
from akra_trader.adapters.venue_execution import SeededVenueExecutionAdapter
from akra_trader.strategies.llm import ExternalDecisionStrategy


def build_client(
  database_path: Path,
  *,
  guarded_live_execution_enabled: bool = False,
  guarded_live_venue: str | None = None,
  provider_provenance_report_scheduler_enabled: bool = True,
  operator_alert_external_sync_token: str | None = None,
  replay_alias_audit_admin_read_token: str | None = None,
  replay_alias_audit_admin_write_token: str | None = None,
) -> TestClient:
  settings = Settings(
    runs_database_url=f"sqlite:///{database_path}",
    market_data_provider="seeded",
    guarded_live_execution_enabled=guarded_live_execution_enabled,
    guarded_live_venue=guarded_live_venue,
    provider_provenance_report_scheduler_enabled=provider_provenance_report_scheduler_enabled,
    operator_alert_external_sync_token=operator_alert_external_sync_token,
    replay_alias_audit_admin_read_token=replay_alias_audit_admin_read_token,
    replay_alias_audit_admin_write_token=replay_alias_audit_admin_write_token,
  )
  return TestClient(create_app(settings))


def _first_non_null_schema_branch(schema: dict) -> dict:
  if "anyOf" not in schema:
    return schema
  return next(branch for branch in schema["anyOf"] if branch.get("type") != "null")


def create_preset(
  client: TestClient,
  *,
  name: str,
  preset_id: str,
  strategy_id: str | None = None,
  timeframe: str | None = None,
  benchmark_family: str | None = None,
  tags: list[str] | None = None,
  parameters: dict[str, object] | None = None,
) -> dict:
  response = client.post(
    "/api/presets",
    json={
      "name": name,
      "preset_id": preset_id,
      "strategy_id": strategy_id,
      "timeframe": timeframe,
      "benchmark_family": benchmark_family,
      "tags": tags or [],
      "parameters": parameters or {},
    },
  )
  assert response.status_code == 200
  return response.json()


def without_surface_rule(
  capabilities: RunSurfaceCapabilities,
  *,
  family_key: str,
  surface_key: str,
) -> RunSurfaceCapabilities:
  return replace(
    capabilities,
    shared_contracts=tuple(
      replace(
        contract,
        surface_rules=tuple(
          rule
          for rule in contract.surface_rules
          if rule.surface_key != surface_key
        ),
      )
      if contract.contract_key == f"family:{family_key}" and contract.contract_kind == "capability_family"
      else contract
      for contract in capabilities.shared_contracts
    ),
  )


class StaticVenueStateAdapter:
  def __init__(self, snapshot: GuardedLiveVenueStateSnapshot) -> None:
    self._snapshot = snapshot

  def capture_snapshot(self) -> GuardedLiveVenueStateSnapshot:
    return self._snapshot


class StatusOverrideSeededMarketDataAdapter(SeededMarketDataAdapter):
  def __init__(self) -> None:
    super().__init__()
    self._status_by_timeframe: dict[str, MarketDataStatus] = {}
    self._remediation_status_by_key: dict[tuple[str, str], MarketDataStatus] = {}
    self._lineage_history: tuple[MarketDataLineageHistoryRecord, ...] = ()
    self._ingestion_jobs: tuple[MarketDataIngestionJobRecord, ...] = ()

  def set_status(self, *, timeframe: str, status: MarketDataStatus) -> None:
    self._status_by_timeframe[timeframe] = status

  def set_remediation_status(
    self,
    *,
    kind: str,
    timeframe: str,
    status: MarketDataStatus,
  ) -> None:
    self._remediation_status_by_key[(kind, timeframe)] = status

  def set_lineage_history(
    self,
    records: tuple[MarketDataLineageHistoryRecord, ...],
  ) -> None:
    self._lineage_history = records

  def set_ingestion_jobs(
    self,
    records: tuple[MarketDataIngestionJobRecord, ...],
  ) -> None:
    self._ingestion_jobs = records

  def get_status(self, timeframe: str) -> MarketDataStatus:
    status = self._status_by_timeframe.get(timeframe)
    if status is not None:
      return status
    return super().get_status(timeframe)

  def list_lineage_history(
    self,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    sync_status: str | None = None,
    validation_claim: str | None = None,
    limit: int | None = None,
  ) -> tuple[MarketDataLineageHistoryRecord, ...]:
    records = self._lineage_history or super().list_lineage_history(
      timeframe=timeframe,
      symbol=symbol,
      sync_status=sync_status,
      validation_claim=validation_claim,
      limit=limit,
    )
    filtered = [
      record
      for record in records
      if (timeframe is None or record.timeframe == timeframe)
      and (symbol is None or record.symbol == symbol)
      and (sync_status is None or record.sync_status == sync_status)
      and (validation_claim is None or record.validation_claim == validation_claim)
    ]
    if limit is not None:
      filtered = filtered[:limit]
    return tuple(filtered)

  def list_ingestion_jobs(
    self,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    operation: str | None = None,
    status: str | None = None,
    limit: int | None = None,
  ) -> tuple[MarketDataIngestionJobRecord, ...]:
    records = self._ingestion_jobs or super().list_ingestion_jobs(
      timeframe=timeframe,
      symbol=symbol,
      operation=operation,
      status=status,
      limit=limit,
    )
    filtered = [
      record
      for record in records
      if (timeframe is None or record.timeframe == timeframe)
      and (symbol is None or record.symbol == symbol)
      and (operation is None or record.operation == operation)
      and (status is None or record.status == status)
    ]
    if limit is not None:
      filtered = filtered[:limit]
    return tuple(filtered)

  def remediate(
    self,
    *,
    kind: str,
    symbol: str,
    timeframe: str,
  ) -> MarketDataRemediationResult:
    current_time = datetime.now(UTC)
    remediated_status = self._remediation_status_by_key.get((kind, timeframe))
    if remediated_status is not None:
      self._status_by_timeframe[timeframe] = remediated_status
      return MarketDataRemediationResult(
        kind=kind,
        symbol=symbol,
        timeframe=timeframe,
        status="executed",
        started_at=current_time,
        finished_at=current_time,
        detail=f"{kind}:{symbol}:{timeframe}:status_repaired",
      )
    return super().remediate(kind=kind, symbol=symbol, timeframe=timeframe)


class StubDecisionEngine:
  def decide(self, context) -> StrategyDecisionEnvelope:
    return StrategyDecisionEnvelope(
      signal=SignalDecision(timestamp=context.timestamp, action=SignalAction.HOLD),
      rationale="stub",
      context=context,
    )


def test_list_strategies_returns_builtin_strategy(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  response = client.get("/api/strategies")
  assert response.status_code == 200
  payload = response.json()
  ma_cross = next(item for item in payload if item["strategy_id"] == "ma_cross_v1")
  assert ma_cross["lifecycle"]["stage"] == "active"
  assert ma_cross["version_lineage"] == ["1.0.0"]
  assert ma_cross["supported_timeframes"] == ["5m", "1h"]
  assert ma_cross["parameter_schema"]["short_window"]["semantic_hint"] == "Fast crossover trigger leg."
  assert ma_cross["parameter_schema"]["short_window"]["delta_higher_label"] == "slower trigger leg"
  assert ma_cross["parameter_schema"]["short_window"]["unit"] == "bars"


def test_external_decision_strategy_exposes_semantic_prompt_profile_metadata() -> None:
  metadata = ExternalDecisionStrategy(decision_engine=StubDecisionEngine()).describe()
  prompt_profile = metadata.parameter_schema["prompt_profile"]
  assert prompt_profile["semantic_hint"] == "Decision-engine prompt posture."
  assert prompt_profile["semantic_ranks"]["aggressive"] == 4
  assert prompt_profile["delta_lower_label"] == "safer prompt posture"


def test_list_strategies_can_filter_by_lane_and_lifecycle_stage(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  response = client.get("/api/strategies?lane=freqtrade_reference&lifecycle_stage=imported")

  assert response.status_code == 200
  payload = response.json()
  assert payload
  assert all(item["runtime"] == "freqtrade_reference" for item in payload)
  assert all(item["lifecycle"]["stage"] == "imported" for item in payload)
  assert all(item["catalog_semantics"]["strategy_kind"] == "reference_delegate" for item in payload)
  assert all(item["catalog_semantics"]["source_descriptor"] for item in payload)
  assert all(
    "Freqtrade reference runtime" in item["catalog_semantics"]["execution_model"]
    for item in payload
  )


def test_register_strategy_endpoint_returns_import_catalog_semantics(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  response = client.post(
    "/api/strategies/register",
    json={
      "strategy_id": "ma_cross_v1",
      "module_path": "akra_trader.strategies.examples",
      "class_name": "MovingAverageCrossStrategy",
    },
  )

  assert response.status_code == 200
  payload = response.json()
  assert payload["catalog_semantics"]["strategy_kind"] == "imported_module"
  assert payload["catalog_semantics"]["source_descriptor"] == (
    "akra_trader.strategies.examples:MovingAverageCrossStrategy"
  )
  assert "typed parameter schema" in payload["catalog_semantics"]["parameter_contract"]
  assert "locally registered module" in payload["catalog_semantics"]["execution_model"]
  assert "Imported from a locally registered module path." in payload["catalog_semantics"]["operator_notes"]
  assert payload["lifecycle"]["registered_at"] is not None


def test_standalone_binding_routes_expose_generated_signatures(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  routes = {
    route.name: route
    for route in client.app.router.routes
    if getattr(route, "name", None)
  }

  assert tuple(inspect.signature(routes["list_strategies"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "lane",
    "lifecycle_stage",
    "version",
    "registered_at",
    "sort",
    "app",
  )
  assert tuple(inspect.signature(routes["list_presets"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "strategy_id",
    "timeframe",
    "lifecycle_stage",
    "created_at",
    "updated_at",
    "sort",
    "app",
  )
  assert tuple(inspect.signature(routes["list_runs"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "mode",
    "strategy_id",
    "strategy_version",
    "rerun_boundary_id",
    "preset_id",
    "benchmark_family",
    "dataset_identity",
    "started_at",
    "updated_at",
    "initial_cash",
    "ending_equity",
    "exposure_pct",
    "total_return_pct",
    "max_drawdown_pct",
    "win_rate_pct",
    "trade_count",
    "tag",
    "sort",
    "app",
  )
  assert tuple(inspect.signature(routes["compare_runs"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "run_id",
    "intent",
    "narrative_score",
    "sort",
    "app",
  )
  assert tuple(inspect.signature(routes["get_market_data_status"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "timeframe",
    "app",
  )
  assert tuple(inspect.signature(routes["list_market_data_lineage_history"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "symbol",
    "timeframe",
    "sync_status",
    "validation_claim",
    "boundary_id",
    "checkpoint_id",
    "recorded_at",
    "last_sync_at",
    "candle_count",
    "failure_count_24h",
    "lag_seconds",
    "issue",
    "sort",
    "app",
  )
  assert tuple(inspect.signature(routes["list_market_data_ingestion_jobs"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "symbol",
    "timeframe",
    "operation",
    "status",
    "validation_claim",
    "checkpoint_id",
    "started_at",
    "finished_at",
    "fetched_candle_count",
    "duration_ms",
    "last_error",
    "sort",
    "app",
  )
  assert tuple(inspect.signature(routes["create_replay_link_alias"].endpoint).parameters) == ("request", "app")
  assert tuple(inspect.signature(routes["resolve_replay_link_alias"].endpoint).parameters) == (
    "alias_token",
    "app",
  )
  assert tuple(inspect.signature(routes["get_replay_link_alias_history"].endpoint).parameters) == (
    "alias_token",
    "app",
  )
  assert tuple(inspect.signature(routes["list_replay_link_alias_audits"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "alias_id",
    "template_key",
    "action",
    "retention_policy",
    "source_tab_id",
    "search",
    "limit",
    "x_akra_replay_audit_admin_token",
    "app",
  )
  assert tuple(inspect.signature(routes["export_replay_link_alias_audits"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "alias_id",
    "template_key",
    "action",
    "retention_policy",
    "source_tab_id",
    "search",
    "format",
    "x_akra_replay_audit_admin_token",
    "app",
  )
  assert tuple(inspect.signature(routes["create_replay_link_alias_audit_export_job"].endpoint).parameters) == (
    "request",
    "x_akra_replay_audit_admin_token",
    "app",
  )
  assert tuple(inspect.signature(routes["list_replay_link_alias_audit_export_jobs"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "template_key",
    "format",
    "status",
    "requested_by_tab_id",
    "search",
    "limit",
    "x_akra_replay_audit_admin_token",
    "app",
  )
  assert tuple(inspect.signature(routes["download_replay_link_alias_audit_export_job"].endpoint).parameters) == (
    "job_id",
    "x_akra_replay_audit_admin_token",
    "app",
  )
  assert tuple(inspect.signature(routes["get_replay_link_alias_audit_export_job_history"].endpoint).parameters) == (
    "job_id",
    "x_akra_replay_audit_admin_token",
    "app",
  )
  assert tuple(inspect.signature(routes["prune_replay_link_alias_audit_export_jobs"].endpoint).parameters) == (
    "request",
    "x_akra_replay_audit_admin_token",
    "app",
  )
  assert tuple(inspect.signature(routes["prune_replay_link_alias_audits"].endpoint).parameters) == (
    "request",
    "x_akra_replay_audit_admin_token",
    "app",
  )
  assert tuple(inspect.signature(routes["revoke_replay_link_alias"].endpoint).parameters) == (
    "alias_token",
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["create_operator_provider_provenance_export_job"].endpoint).parameters) == (
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["list_operator_provider_provenance_export_jobs"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "export_scope",
    "focus_key",
    "symbol",
    "timeframe",
    "provider_label",
    "vendor_field",
    "market_data_provider",
    "venue",
    "requested_by_tab_id",
    "status",
    "search",
    "limit",
    "app",
  )
  assert tuple(inspect.signature(routes["update_operator_provider_provenance_export_job_policy"].endpoint).parameters) == (
    "job_id",
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["approve_operator_provider_provenance_export_job"].endpoint).parameters) == (
    "job_id",
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["escalate_operator_provider_provenance_export_job"].endpoint).parameters) == (
    "job_id",
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["get_operator_provider_provenance_export_analytics"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "focus_key",
    "symbol",
    "timeframe",
    "provider_label",
    "vendor_field",
    "market_data_provider",
    "venue",
    "requested_by_tab_id",
    "status",
    "search",
    "result_limit",
    "window_days",
    "app",
  )
  assert tuple(inspect.signature(routes["download_operator_provider_provenance_export_job"].endpoint).parameters) == (
    "job_id",
    "request",
    "filter_expr",
    "source_tab_id",
    "source_tab_label",
    "app",
  )
  assert tuple(inspect.signature(routes["get_operator_provider_provenance_export_job_history"].endpoint).parameters) == (
    "job_id",
    "app",
  )
  assert tuple(inspect.signature(routes["create_operator_provider_provenance_analytics_preset"].endpoint).parameters) == (
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["list_operator_provider_provenance_analytics_presets"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "created_by_tab_id",
    "focus_scope",
    "search",
    "limit",
    "app",
  )
  assert tuple(inspect.signature(routes["create_operator_provider_provenance_dashboard_view"].endpoint).parameters) == (
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["list_operator_provider_provenance_dashboard_views"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "preset_id",
    "created_by_tab_id",
    "focus_scope",
    "highlight_panel",
    "search",
    "limit",
    "app",
  )
  assert tuple(inspect.signature(routes["create_operator_provider_provenance_scheduler_narrative_template"].endpoint).parameters) == (
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["list_operator_provider_provenance_scheduler_narrative_templates"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "created_by_tab_id",
    "focus_scope",
    "category",
    "narrative_facet",
    "search",
    "limit",
    "app",
  )
  assert tuple(inspect.signature(routes["update_operator_provider_provenance_scheduler_narrative_template"].endpoint).parameters) == (
    "template_id",
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["delete_operator_provider_provenance_scheduler_narrative_template"].endpoint).parameters) == (
    "template_id",
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["bulk_govern_operator_provider_provenance_scheduler_narrative_templates"].endpoint).parameters) == (
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["list_operator_provider_provenance_scheduler_narrative_template_revisions"].endpoint).parameters) == (
    "template_id",
    "app",
  )
  assert tuple(inspect.signature(routes["restore_operator_provider_provenance_scheduler_narrative_template_revision"].endpoint).parameters) == (
    "template_id",
    "revision_id",
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["create_operator_provider_provenance_scheduler_narrative_registry_entry"].endpoint).parameters) == (
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["list_operator_provider_provenance_scheduler_narrative_registry_entries"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "template_id",
    "created_by_tab_id",
    "focus_scope",
    "category",
    "narrative_facet",
    "search",
    "limit",
    "app",
  )
  assert tuple(inspect.signature(routes["update_operator_provider_provenance_scheduler_narrative_registry_entry"].endpoint).parameters) == (
    "registry_id",
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["delete_operator_provider_provenance_scheduler_narrative_registry_entry"].endpoint).parameters) == (
    "registry_id",
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["bulk_govern_operator_provider_provenance_scheduler_narrative_registry_entries"].endpoint).parameters) == (
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["list_operator_provider_provenance_scheduler_narrative_registry_revisions"].endpoint).parameters) == (
    "registry_id",
    "app",
  )
  assert tuple(inspect.signature(routes["restore_operator_provider_provenance_scheduler_narrative_registry_revision"].endpoint).parameters) == (
    "registry_id",
    "revision_id",
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["create_operator_provider_provenance_scheduled_report"].endpoint).parameters) == (
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["list_operator_provider_provenance_scheduled_reports"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "status",
    "cadence",
    "preset_id",
    "view_id",
    "created_by_tab_id",
    "focus_scope",
    "search",
    "limit",
    "app",
  )
  assert tuple(inspect.signature(routes["run_operator_provider_provenance_scheduled_report"].endpoint).parameters) == (
    "report_id",
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["run_due_operator_provider_provenance_scheduled_reports"].endpoint).parameters) == (
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["get_operator_provider_provenance_scheduled_report_history"].endpoint).parameters) == (
    "report_id",
    "app",
  )
  assert tuple(inspect.signature(routes["list_operator_provider_provenance_scheduler_health_history"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "status",
    "limit",
    "offset",
    "app",
  )
  assert tuple(inspect.signature(routes["list_operator_provider_provenance_scheduler_alert_history"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "category",
    "status",
    "narrative_facet",
    "limit",
    "offset",
    "app",
  )
  assert tuple(inspect.signature(routes["get_operator_provider_provenance_scheduler_health_analytics"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "status",
    "window_days",
    "history_limit",
    "drilldown_bucket_key",
    "drilldown_history_limit",
    "app",
  )
  assert tuple(inspect.signature(routes["export_operator_provider_provenance_scheduler_health"].endpoint).parameters) == (
    "request",
    "filter_expr",
    "status",
    "window_days",
    "history_limit",
    "drilldown_bucket_key",
    "drilldown_history_limit",
    "offset",
    "limit",
    "format",
    "app",
  )
  assert tuple(inspect.signature(routes["reconstruct_operator_provider_provenance_scheduler_health_export"].endpoint).parameters) == (
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["create_preset"].endpoint).parameters) == ("request", "app")
  assert tuple(inspect.signature(routes["update_preset"].endpoint).parameters) == ("preset_id", "request", "app")
  assert tuple(inspect.signature(routes["restore_preset_revision"].endpoint).parameters) == (
    "preset_id",
    "revision_id",
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["run_backtest"].endpoint).parameters) == ("request", "app")
  assert tuple(inspect.signature(routes["cancel_live_order"].endpoint).parameters) == (
    "run_id",
    "order_id",
    "request",
    "app",
  )
  assert tuple(inspect.signature(routes["sync_external_incident"].endpoint).parameters) == (
    "request",
    "x_akra_incident_sync_token",
    "app",
  )


def test_replay_link_alias_endpoints_resolve_and_revoke(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  create_response = client.post(
    "/api/replay-links/aliases",
    json={
      "template_key": "template_a",
      "template_label": "Template A",
      "intent": {
        "replayScope": "all",
        "replayIndex": 2,
        "replayGroupFilter": "group_a",
      },
      "redaction_policy": "summary_only",
      "retention_policy": "7d",
      "source_tab_id": "tab_local",
      "source_tab_label": "Local tab",
    },
  )

  assert create_response.status_code == 200
  created_alias = create_response.json()
  assert created_alias["resolution_source"] == "server"

  resolve_response = client.get(
    f"/api/replay-links/aliases/{created_alias['alias_token']}",
  )

  assert resolve_response.status_code == 200
  assert resolve_response.json()["intent"]["replayIndex"] == 2

  revoke_response = client.post(
    f"/api/replay-links/aliases/{created_alias['alias_token']}/revoke",
    json={
      "source_tab_id": "tab_remote",
      "source_tab_label": "Remote tab",
    },
  )

  assert revoke_response.status_code == 200
  assert revoke_response.json()["revoked_by_tab_label"] == "Remote tab"

  history_response = client.get(
    f"/api/replay-links/aliases/{created_alias['alias_token']}/history",
  )

  assert history_response.status_code == 200
  history_payload = history_response.json()
  assert history_payload["alias"]["retention_policy"] == "7d"
  assert [item["action"] for item in history_payload["history"]] == [
    "revoked",
    "resolved",
    "created",
  ]

  revoked_resolve_response = client.get(
    f"/api/replay-links/aliases/{created_alias['alias_token']}",
  )

  assert revoked_resolve_response.status_code == 404
  assert "revoked" in revoked_resolve_response.json()["detail"]


def test_replay_link_alias_registry_survives_restart(tmp_path: Path) -> None:
  database_path = tmp_path / "runs.sqlite3"
  client = build_client(database_path)

  create_response = client.post(
    "/api/replay-links/aliases",
    json={
      "template_key": "template_a",
      "template_label": "Template A",
      "intent": {
        "replayScope": "all",
        "replayIndex": 4,
      },
      "redaction_policy": "full",
      "retention_policy": "7d",
      "source_tab_id": "tab_local",
      "source_tab_label": "Local tab",
    },
  )

  assert create_response.status_code == 200
  alias_token = create_response.json()["alias_token"]

  restarted_client = build_client(database_path)
  resolve_response = restarted_client.get(f"/api/replay-links/aliases/{alias_token}")

  assert resolve_response.status_code == 200
  assert resolve_response.json()["intent"]["replayIndex"] == 4

  revoke_response = restarted_client.post(
    f"/api/replay-links/aliases/{alias_token}/revoke",
    json={"source_tab_id": "tab_remote", "source_tab_label": "Remote tab"},
  )

  assert revoke_response.status_code == 200

  second_restart_client = build_client(database_path)
  history_response = second_restart_client.get(
    f"/api/replay-links/aliases/{alias_token}/history",
  )
  assert history_response.status_code == 200
  assert [item["action"] for item in history_response.json()["history"]] == [
    "revoked",
    "resolved",
    "created",
  ]
  revoked_resolve_response = second_restart_client.get(f"/api/replay-links/aliases/{alias_token}")

  assert revoked_resolve_response.status_code == 404
  assert "revoked" in revoked_resolve_response.json()["detail"]


def test_replay_link_alias_audit_admin_endpoints_support_search_and_prune(tmp_path: Path) -> None:
  client = build_client(
    tmp_path / "runs.sqlite3",
    replay_alias_audit_admin_read_token="read-token",
    replay_alias_audit_admin_write_token="write-token",
  )

  created_response = client.post(
    "/api/replay-links/aliases",
    json={
      "template_key": "template_admin",
      "template_label": "Template Admin",
      "intent": {"replayScope": "all", "replayIndex": 1},
      "redaction_policy": "full",
      "retention_policy": "7d",
      "source_tab_id": "tab_local",
      "source_tab_label": "Local tab",
    },
  )
  assert created_response.status_code == 200
  alias_token = created_response.json()["alias_token"]

  resolve_response = client.get(f"/api/replay-links/aliases/{alias_token}")
  assert resolve_response.status_code == 200

  revoke_response = client.post(
    f"/api/replay-links/aliases/{alias_token}/revoke",
    json={"source_tab_id": "tab_remote", "source_tab_label": "Remote tab"},
  )
  assert revoke_response.status_code == 200

  audit_list_response = client.get(
    "/api/replay-links/audits",
    params={
      "template_key": "template_admin",
      "action": "revoked",
      "search": "Remote",
      "limit": 10,
    },
    headers={"X-Akra-Replay-Audit-Admin-Token": "read-token"},
  )
  assert audit_list_response.status_code == 200
  audit_items = audit_list_response.json()["items"]
  assert len(audit_items) == 1
  assert audit_items[0]["action"] == "revoked"

  prune_response = client.post(
    "/api/replay-links/audits/prune",
    json={
      "prune_mode": "matched",
      "template_key": "template_admin",
      "action": "resolved",
    },
    headers={"X-Akra-Replay-Audit-Admin-Token": "write-token"},
  )
  assert prune_response.status_code == 200
  assert prune_response.json()["deleted_count"] == 1

  post_prune_list_response = client.get(
    "/api/replay-links/audits",
    params={"template_key": "template_admin", "action": "resolved", "limit": 10},
    headers={"X-Akra-Replay-Audit-Admin-Token": "read-token"},
  )
  assert post_prune_list_response.status_code == 200
  assert post_prune_list_response.json()["total"] == 0


def test_replay_link_alias_audit_admin_endpoints_require_scoped_tokens(tmp_path: Path) -> None:
  client = build_client(
    tmp_path / "runs.sqlite3",
    replay_alias_audit_admin_read_token="read-token",
    replay_alias_audit_admin_write_token="write-token",
  )

  created_response = client.post(
    "/api/replay-links/aliases",
    json={
      "template_key": "template_admin",
      "template_label": "Template Admin",
      "intent": {"replayScope": "all", "replayIndex": 1},
      "redaction_policy": "full",
      "retention_policy": "7d",
      "source_tab_id": "tab_local",
      "source_tab_label": "Local tab",
    },
  )
  assert created_response.status_code == 200

  forbidden_list_response = client.get("/api/replay-links/audits")
  assert forbidden_list_response.status_code == 403

  read_list_response = client.get(
    "/api/replay-links/audits",
    headers={"X-Akra-Replay-Audit-Admin-Token": "read-token"},
  )
  assert read_list_response.status_code == 200

  write_list_response = client.get(
    "/api/replay-links/audits",
    headers={"X-Akra-Replay-Audit-Admin-Token": "write-token"},
  )
  assert write_list_response.status_code == 200

  forbidden_prune_response = client.post(
    "/api/replay-links/audits/prune",
    json={"prune_mode": "expired"},
    headers={"X-Akra-Replay-Audit-Admin-Token": "read-token"},
  )
  assert forbidden_prune_response.status_code == 403

  write_prune_response = client.post(
    "/api/replay-links/audits/prune",
    json={"prune_mode": "expired"},
    headers={"X-Akra-Replay-Audit-Admin-Token": "write-token"},
  )
  assert write_prune_response.status_code == 200


def test_replay_link_alias_audit_export_endpoint_supports_json_and_csv(tmp_path: Path) -> None:
  client = build_client(
    tmp_path / "runs.sqlite3",
    replay_alias_audit_admin_read_token="read-token",
  )

  created_response = client.post(
    "/api/replay-links/aliases",
    json={
      "template_key": "template_export",
      "template_label": "Template Export",
      "intent": {"replayScope": "all", "replayIndex": 7},
      "redaction_policy": "summary_only",
      "retention_policy": "30d",
      "source_tab_id": "tab_local",
      "source_tab_label": "Local tab",
    },
  )
  assert created_response.status_code == 200
  alias_token = created_response.json()["alias_token"]
  assert client.get(f"/api/replay-links/aliases/{alias_token}").status_code == 200

  forbidden_response = client.get("/api/replay-links/audits/export")
  assert forbidden_response.status_code == 403

  json_export_response = client.get(
    "/api/replay-links/audits/export",
    params={"template_key": "template_export", "format": "json"},
    headers={"X-Akra-Replay-Audit-Admin-Token": "read-token"},
  )
  assert json_export_response.status_code == 200
  json_export_payload = json_export_response.json()
  assert json_export_payload["format"] == "json"
  assert json_export_payload["filename"].endswith(".json")
  assert json_export_payload["record_count"] == 2
  assert "\"template_key\": \"template_export\"" in json_export_payload["content"]

  csv_export_response = client.get(
    "/api/replay-links/audits/export",
    params={"template_key": "template_export", "format": "csv"},
    headers={"X-Akra-Replay-Audit-Admin-Token": "read-token"},
  )
  assert csv_export_response.status_code == 200
  csv_export_payload = csv_export_response.json()
  assert csv_export_payload["format"] == "csv"
  assert csv_export_payload["filename"].endswith(".csv")
  assert csv_export_payload["record_count"] == 2
  assert "audit_id,alias_id,action" in csv_export_payload["content"]


def test_replay_link_alias_audit_export_job_endpoints_support_creation_and_history(tmp_path: Path) -> None:
  client = build_client(
    tmp_path / "runs.sqlite3",
    replay_alias_audit_admin_read_token="read-token",
    replay_alias_audit_admin_write_token="write-token",
  )

  created_response = client.post(
    "/api/replay-links/aliases",
    json={
      "template_key": "template_export_jobs",
      "template_label": "Template Export Jobs",
      "intent": {"replayScope": "all", "replayIndex": 7},
      "redaction_policy": "summary_only",
      "retention_policy": "30d",
      "source_tab_id": "tab_local",
      "source_tab_label": "Local tab",
    },
  )
  assert created_response.status_code == 200
  alias_token = created_response.json()["alias_token"]
  assert client.get(f"/api/replay-links/aliases/{alias_token}").status_code == 200

  create_job_response = client.post(
    "/api/replay-links/audits/export-jobs",
    json={
      "format": "csv",
      "template_key": "template_export_jobs",
      "requested_by_tab_id": "tab_export",
      "requested_by_tab_label": "Export tab",
    },
    headers={"X-Akra-Replay-Audit-Admin-Token": "write-token"},
  )
  assert create_job_response.status_code == 200
  created_job = create_job_response.json()
  assert created_job["export_format"] == "csv"
  assert created_job["record_count"] == 2

  list_jobs_response = client.get(
    "/api/replay-links/audits/export-jobs",
    params={"template_key": "template_export_jobs", "format": "csv", "limit": 10},
    headers={"X-Akra-Replay-Audit-Admin-Token": "read-token"},
  )
  assert list_jobs_response.status_code == 200
  jobs_payload = list_jobs_response.json()
  assert jobs_payload["total"] == 1
  assert jobs_payload["items"][0]["job_id"] == created_job["job_id"]

  download_response = client.get(
    f"/api/replay-links/audits/export-jobs/{created_job['job_id']}/download",
    headers={"X-Akra-Replay-Audit-Admin-Token": "read-token"},
  )
  assert download_response.status_code == 200
  download_payload = download_response.json()
  assert download_payload["content"]
  assert download_payload["filename"].endswith(".csv")

  history_response = client.get(
    f"/api/replay-links/audits/export-jobs/{created_job['job_id']}/history",
    headers={"X-Akra-Replay-Audit-Admin-Token": "read-token"},
  )
  assert history_response.status_code == 200
  assert [item["action"] for item in history_response.json()["history"]] == [
    "downloaded",
    "created",
  ]

  prune_response = client.post(
    "/api/replay-links/audits/export-jobs/prune",
    json={
      "prune_mode": "matched",
      "template_key": "template_export_jobs",
      "format": "csv",
    },
    headers={"X-Akra-Replay-Audit-Admin-Token": "write-token"},
  )
  assert prune_response.status_code == 200
  prune_payload = prune_response.json()
  assert prune_payload["deleted_job_count"] == 1
  assert prune_payload["deleted_artifact_count"] == 1
  assert prune_payload["deleted_history_count"] == 2


def test_replay_link_alias_audit_export_job_endpoints_require_scoped_tokens(tmp_path: Path) -> None:
  client = build_client(
    tmp_path / "runs.sqlite3",
    replay_alias_audit_admin_read_token="read-token",
    replay_alias_audit_admin_write_token="write-token",
  )

  forbidden_create_response = client.post(
    "/api/replay-links/audits/export-jobs",
    json={"format": "json"},
    headers={"X-Akra-Replay-Audit-Admin-Token": "read-token"},
  )
  assert forbidden_create_response.status_code == 403

  create_job_response = client.post(
    "/api/replay-links/audits/export-jobs",
    json={"format": "json"},
    headers={"X-Akra-Replay-Audit-Admin-Token": "write-token"},
  )
  assert create_job_response.status_code == 200
  job_id = create_job_response.json()["job_id"]

  forbidden_list_response = client.get("/api/replay-links/audits/export-jobs")
  assert forbidden_list_response.status_code == 403

  read_list_response = client.get(
    "/api/replay-links/audits/export-jobs",
    headers={"X-Akra-Replay-Audit-Admin-Token": "read-token"},
  )
  assert read_list_response.status_code == 200

  download_response = client.get(
    f"/api/replay-links/audits/export-jobs/{job_id}/download",
    headers={"X-Akra-Replay-Audit-Admin-Token": "read-token"},
  )
  assert download_response.status_code == 200

  history_response = client.get(
    f"/api/replay-links/audits/export-jobs/{job_id}/history",
    headers={"X-Akra-Replay-Audit-Admin-Token": "read-token"},
  )
  assert history_response.status_code == 200

  forbidden_prune_response = client.post(
    "/api/replay-links/audits/export-jobs/prune",
    json={"prune_mode": "expired"},
    headers={"X-Akra-Replay-Audit-Admin-Token": "read-token"},
  )
  assert forbidden_prune_response.status_code == 403

  write_prune_response = client.post(
    "/api/replay-links/audits/export-jobs/prune",
    json={"prune_mode": "expired"},
    headers={"X-Akra-Replay-Audit-Admin-Token": "write-token"},
  )
  assert write_prune_response.status_code == 200


def test_operator_provider_provenance_export_job_endpoints_round_trip(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  export_content = json.dumps(
    {
      "exported_at": "2026-04-22T00:00:00Z",
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

  create_response = client.post(
    "/api/operator/provider-provenance-exports",
    json={
      "content": export_content,
      "requested_by_tab_id": "tab_ops",
      "requested_by_tab_label": "Ops desk",
    },
  )
  assert create_response.status_code == 200
  created_job = create_response.json()
  assert created_job["focus_key"] == "binance:BTC/USDT|5m"
  assert created_job["provider_labels"] == ["pagerduty"]

  list_response = client.get(
    "/api/operator/provider-provenance-exports",
    params={
      "focus_key": "binance:BTC/USDT|5m",
      "vendor_field": "custom_details.market_context",
      "limit": 10,
    },
  )
  assert list_response.status_code == 200
  list_payload = list_response.json()
  assert list_payload["total"] == 1
  assert list_payload["items"][0]["job_id"] == created_job["job_id"]

  download_response = client.get(
    f"/api/operator/provider-provenance-exports/{created_job['job_id']}/download",
    params={"source_tab_id": "tab_review", "source_tab_label": "Review tab"},
  )
  assert download_response.status_code == 200
  download_payload = download_response.json()
  assert download_payload["content"] == export_content

  analytics_response = client.get(
    "/api/operator/provider-provenance-exports/analytics",
    params={
      "focus_key": "binance:BTC/USDT|5m",
      "provider_label": "pagerduty",
      "vendor_field": "custom_details.market_context",
      "result_limit": 10,
      "window_days": 5,
    },
  )
  assert analytics_response.status_code == 200
  analytics_payload = analytics_response.json()
  assert analytics_payload["totals"]["export_count"] == 1
  assert analytics_payload["totals"]["download_count"] == 1
  assert analytics_payload["query"]["window_days"] == 5
  assert analytics_payload["rollups"]["providers"][0]["key"] == "pagerduty"
  assert len(analytics_payload["time_series"]["provider_drift"]["series"]) == 5
  assert analytics_payload["time_series"]["export_burn_up"]["summary"]["cumulative_export_count"] == 1
  assert analytics_payload["recent_exports"][0]["job_id"] == created_job["job_id"]

  history_response = client.get(
    f"/api/operator/provider-provenance-exports/{created_job['job_id']}/history",
  )
  assert history_response.status_code == 200
  history_payload = history_response.json()
  assert {item["action"] for item in history_payload["history"]} == {"created", "downloaded"}
  assert any(item["source_tab_id"] == "tab_review" for item in history_payload["history"])


def test_operator_provider_provenance_workspace_endpoints_round_trip(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  preset_response = client.post(
    "/api/operator/provider-provenance-analytics/presets",
    json={
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
  assert preset_response.status_code == 200
  preset_payload = preset_response.json()
  assert preset_payload["query"]["focus_scope"] == "current_focus"
  assert preset_payload["query"]["scheduler_alert_narrative_facet"] == "post_resolution_recovery"

  list_presets_response = client.get(
    "/api/operator/provider-provenance-analytics/presets",
    params={"focus_scope": "current_focus", "limit": 10},
  )
  assert list_presets_response.status_code == 200
  list_presets_payload = list_presets_response.json()
  assert list_presets_payload["total"] == 1
  assert list_presets_payload["items"][0]["preset_id"] == preset_payload["preset_id"]

  view_response = client.post(
    "/api/operator/provider-provenance-analytics/views",
    json={
      "name": "BTC drift board",
      "description": "Shared drift dashboard view.",
      "preset_id": preset_payload["preset_id"],
      "layout": {
        "highlight_panel": "scheduler_alerts",
        "show_rollups": True,
        "show_time_series": True,
        "show_recent_exports": False,
      },
      "created_by_tab_id": "tab_ops",
      "created_by_tab_label": "Ops desk",
    },
  )
  assert view_response.status_code == 200
  view_payload = view_response.json()
  assert view_payload["layout"]["highlight_panel"] == "scheduler_alerts"
  assert view_payload["query"]["scheduler_alert_status"] == "resolved"

  list_views_response = client.get(
    "/api/operator/provider-provenance-analytics/views",
    params={"preset_id": preset_payload["preset_id"], "highlight_panel": "scheduler_alerts", "limit": 10},
  )
  assert list_views_response.status_code == 200
  list_views_payload = list_views_response.json()
  assert list_views_payload["total"] == 1
  assert list_views_payload["items"][0]["view_id"] == view_payload["view_id"]

  template_response = client.post(
    "/api/operator/provider-provenance-analytics/scheduler-narrative-templates",
    json={
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
  assert template_response.status_code == 200
  template_payload = template_response.json()
  assert template_payload["query"]["scheduler_alert_narrative_facet"] == "post_resolution_recovery"

  list_templates_response = client.get(
    "/api/operator/provider-provenance-analytics/scheduler-narrative-templates",
    params={"category": "scheduler_lag", "narrative_facet": "post_resolution_recovery", "limit": 10},
  )
  assert list_templates_response.status_code == 200
  list_templates_payload = list_templates_response.json()
  assert list_templates_payload["total"] == 1
  assert list_templates_payload["items"][0]["template_id"] == template_payload["template_id"]
  assert list_templates_payload["items"][0]["revision_count"] == 1

  update_template_response = client.patch(
    f"/api/operator/provider-provenance-analytics/scheduler-narrative-templates/{template_payload['template_id']}",
    json={
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
  assert update_template_response.status_code == 200
  updated_template_payload = update_template_response.json()
  assert updated_template_payload["revision_count"] == 2
  assert updated_template_payload["query"]["scheduler_alert_narrative_facet"] == "recurring_occurrences"

  template_revisions_response = client.get(
    f"/api/operator/provider-provenance-analytics/scheduler-narrative-templates/{template_payload['template_id']}/revisions",
  )
  assert template_revisions_response.status_code == 200
  template_revisions_payload = template_revisions_response.json()
  assert [item["action"] for item in template_revisions_payload["history"][:2]] == ["updated", "created"]
  created_template_revision_id = template_revisions_payload["history"][-1]["revision_id"]

  delete_template_response = client.post(
    f"/api/operator/provider-provenance-analytics/scheduler-narrative-templates/{template_payload['template_id']}/delete",
    json={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "retire_superseded_template",
    },
  )
  assert delete_template_response.status_code == 200
  deleted_template_payload = delete_template_response.json()
  assert deleted_template_payload["status"] == "deleted"
  assert deleted_template_payload["revision_count"] == 3

  restore_template_response = client.post(
    f"/api/operator/provider-provenance-analytics/scheduler-narrative-templates/{template_payload['template_id']}/revisions/{created_template_revision_id}/restore",
    json={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "restore_baseline_template",
    },
  )
  assert restore_template_response.status_code == 200
  restored_template_payload = restore_template_response.json()
  assert restored_template_payload["status"] == "active"
  assert restored_template_payload["query"]["scheduler_alert_narrative_facet"] == "post_resolution_recovery"
  assert restored_template_payload["revision_count"] == 4

  bulk_template_response = client.post(
    "/api/operator/provider-provenance-analytics/scheduler-narrative-templates",
    json={
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
  assert bulk_template_response.status_code == 200
  bulk_template_payload = bulk_template_response.json()

  bulk_delete_templates_response = client.post(
    "/api/operator/provider-provenance-analytics/scheduler-narrative-templates/bulk-governance",
    json={
      "action": "delete",
      "template_ids": [template_payload["template_id"], bulk_template_payload["template_id"]],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "bulk_template_governance_delete",
    },
  )
  assert bulk_delete_templates_response.status_code == 200
  bulk_delete_templates_payload = bulk_delete_templates_response.json()
  assert bulk_delete_templates_payload["action"] == "delete"
  assert bulk_delete_templates_payload["requested_count"] == 2
  assert bulk_delete_templates_payload["applied_count"] == 2
  assert {item["status"] for item in bulk_delete_templates_payload["results"]} == {"deleted"}

  bulk_restore_templates_response = client.post(
    "/api/operator/provider-provenance-analytics/scheduler-narrative-templates/bulk-governance",
    json={
      "action": "restore",
      "template_ids": [template_payload["template_id"], bulk_template_payload["template_id"]],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "bulk_template_governance_restore",
    },
  )
  assert bulk_restore_templates_response.status_code == 200
  bulk_restore_templates_payload = bulk_restore_templates_response.json()
  assert bulk_restore_templates_payload["action"] == "restore"
  assert bulk_restore_templates_payload["applied_count"] == 2
  assert all(item["status"] == "active" for item in bulk_restore_templates_payload["results"])

  bulk_update_templates_response = client.post(
    "/api/operator/provider-provenance-analytics/scheduler-narrative-templates/bulk-governance",
    json={
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
  assert bulk_update_templates_response.status_code == 200
  bulk_update_templates_payload = bulk_update_templates_response.json()
  assert bulk_update_templates_payload["action"] == "update"
  assert bulk_update_templates_payload["applied_count"] == 2

  list_updated_templates_response = client.get(
    "/api/operator/provider-provenance-analytics/scheduler-narrative-templates",
    params={"category": "scheduler_failure", "narrative_facet": "recurring_occurrences", "limit": 10},
  )
  assert list_updated_templates_response.status_code == 200
  list_updated_templates_payload = list_updated_templates_response.json()
  assert list_updated_templates_payload["total"] == 2
  assert all(item["name"].startswith("Gov / ") for item in list_updated_templates_payload["items"])
  assert all(item["description"].endswith("bulk-reviewed") for item in list_updated_templates_payload["items"])

  registry_response = client.post(
    "/api/operator/provider-provenance-analytics/scheduler-narrative-registry",
    json={
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
  assert registry_response.status_code == 200
  registry_payload = registry_response.json()
  assert registry_payload["template_id"] == template_payload["template_id"]
  assert registry_payload["layout"]["highlight_panel"] == "scheduler_alerts"
  assert registry_payload["revision_count"] == 1

  list_registry_response = client.get(
    "/api/operator/provider-provenance-analytics/scheduler-narrative-registry",
    params={
      "template_id": template_payload["template_id"],
      "category": "scheduler_lag",
      "narrative_facet": "post_resolution_recovery",
      "limit": 10,
    },
  )
  assert list_registry_response.status_code == 200
  list_registry_payload = list_registry_response.json()
  assert list_registry_payload["total"] == 1
  assert list_registry_payload["items"][0]["registry_id"] == registry_payload["registry_id"]

  update_registry_response = client.patch(
    f"/api/operator/provider-provenance-analytics/scheduler-narrative-registry/{registry_payload['registry_id']}",
    json={
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
  assert update_registry_response.status_code == 200
  updated_registry_payload = update_registry_response.json()
  assert updated_registry_payload["revision_count"] == 2
  assert updated_registry_payload["template_id"] is None
  assert updated_registry_payload["layout"]["highlight_panel"] == "scheduler_alerts"

  registry_revisions_response = client.get(
    f"/api/operator/provider-provenance-analytics/scheduler-narrative-registry/{registry_payload['registry_id']}/revisions",
  )
  assert registry_revisions_response.status_code == 200
  registry_revisions_payload = registry_revisions_response.json()
  assert [item["action"] for item in registry_revisions_payload["history"][:2]] == ["updated", "created"]
  created_registry_revision_id = registry_revisions_payload["history"][-1]["revision_id"]

  delete_registry_response = client.post(
    f"/api/operator/provider-provenance-analytics/scheduler-narrative-registry/{registry_payload['registry_id']}/delete",
    json={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "retire_registry_board",
    },
  )
  assert delete_registry_response.status_code == 200
  deleted_registry_payload = delete_registry_response.json()
  assert deleted_registry_payload["status"] == "deleted"
  assert deleted_registry_payload["revision_count"] == 3

  restore_registry_response = client.post(
    f"/api/operator/provider-provenance-analytics/scheduler-narrative-registry/{registry_payload['registry_id']}/revisions/{created_registry_revision_id}/restore",
    json={
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "restore_linked_registry",
    },
  )
  assert restore_registry_response.status_code == 200
  restored_registry_payload = restore_registry_response.json()
  assert restored_registry_payload["status"] == "active"
  assert restored_registry_payload["template_id"] == template_payload["template_id"]
  assert restored_registry_payload["revision_count"] == 4

  bulk_registry_response = client.post(
    "/api/operator/provider-provenance-analytics/scheduler-narrative-registry",
    json={
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
  assert bulk_registry_response.status_code == 200
  bulk_registry_payload = bulk_registry_response.json()

  bulk_delete_registry_response = client.post(
    "/api/operator/provider-provenance-analytics/scheduler-narrative-registry/bulk-governance",
    json={
      "action": "delete",
      "registry_ids": [registry_payload["registry_id"], bulk_registry_payload["registry_id"]],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "bulk_registry_governance_delete",
    },
  )
  assert bulk_delete_registry_response.status_code == 200
  bulk_delete_registry_payload = bulk_delete_registry_response.json()
  assert bulk_delete_registry_payload["action"] == "delete"
  assert bulk_delete_registry_payload["requested_count"] == 2
  assert bulk_delete_registry_payload["applied_count"] == 2
  assert {item["status"] for item in bulk_delete_registry_payload["results"]} == {"deleted"}

  bulk_restore_registry_response = client.post(
    "/api/operator/provider-provenance-analytics/scheduler-narrative-registry/bulk-governance",
    json={
      "action": "restore",
      "registry_ids": [registry_payload["registry_id"], bulk_registry_payload["registry_id"]],
      "actor_tab_id": "tab_ops",
      "actor_tab_label": "Ops desk",
      "reason": "bulk_registry_governance_restore",
    },
  )
  assert bulk_restore_registry_response.status_code == 200
  bulk_restore_registry_payload = bulk_restore_registry_response.json()
  assert bulk_restore_registry_payload["action"] == "restore"
  assert bulk_restore_registry_payload["applied_count"] == 2
  assert all(item["status"] == "active" for item in bulk_restore_registry_payload["results"])

  bulk_update_registry_response = client.post(
    "/api/operator/provider-provenance-analytics/scheduler-narrative-registry/bulk-governance",
    json={
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
  assert bulk_update_registry_response.status_code == 200
  bulk_update_registry_payload = bulk_update_registry_response.json()
  assert bulk_update_registry_payload["action"] == "update"
  assert bulk_update_registry_payload["applied_count"] == 2

  list_updated_registry_response = client.get(
    "/api/operator/provider-provenance-analytics/scheduler-narrative-registry",
    params={
      "template_id": template_payload["template_id"],
      "category": "scheduler_failure",
      "narrative_facet": "resolved_narratives",
      "limit": 10,
    },
  )
  assert list_updated_registry_response.status_code == 200
  list_updated_registry_payload = list_updated_registry_response.json()
  assert list_updated_registry_payload["total"] == 2
  assert all(item["name"].endswith(" / governed") for item in list_updated_registry_payload["items"])
  assert all(item["template_id"] == template_payload["template_id"] for item in list_updated_registry_payload["items"])
  assert all(item["layout"]["show_recent_exports"] is True for item in list_updated_registry_payload["items"])

  report_response = client.post(
    "/api/operator/provider-provenance-analytics/reports",
    json={
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
  assert report_response.status_code == 200
  report_payload = report_response.json()
  assert report_payload["cadence"] == "weekly"
  assert report_payload["status"] == "scheduled"

  list_reports_response = client.get(
    "/api/operator/provider-provenance-analytics/reports",
    params={"status": "scheduled", "view_id": view_payload["view_id"], "limit": 10},
  )
  assert list_reports_response.status_code == 200
  list_reports_payload = list_reports_response.json()
  assert list_reports_payload["total"] == 1
  assert list_reports_payload["items"][0]["report_id"] == report_payload["report_id"]

  run_response = client.post(
    f"/api/operator/provider-provenance-analytics/reports/{report_payload['report_id']}/run",
    json={"source_tab_id": "tab_review", "source_tab_label": "Review tab"},
  )
  assert run_response.status_code == 200
  run_payload = run_response.json()
  assert run_payload["report"]["last_export_job_id"] == run_payload["export_job"]["job_id"]
  assert run_payload["export_job"]["export_scope"] == "provider_provenance_analytics_report"

  history_response = client.get(
    f"/api/operator/provider-provenance-analytics/reports/{report_payload['report_id']}/history",
  )
  assert history_response.status_code == 200
  history_payload = history_response.json()
  assert {item["action"] for item in history_payload["history"]} == {"created", "ran"}
  assert any(item["export_job_id"] == run_payload["export_job"]["job_id"] for item in history_payload["history"])

  run_due_response = client.post(
    "/api/operator/provider-provenance-analytics/reports/run-due",
    json={
      "source_tab_id": "tab_scheduler",
      "source_tab_label": "Scheduler",
      "due_before": "2026-04-29T00:00:00Z",
      "limit": 10,
    },
  )
  assert run_due_response.status_code == 200
  run_due_payload = run_due_response.json()
  assert run_due_payload["executed_count"] == 1
  assert run_due_payload["items"][0]["report"]["report_id"] == report_payload["report_id"]


def test_query_bound_routes_expose_openapi_metadata(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  openapi = client.app.openapi()

  runs_params = {
    param["name"]: param
    for param in openapi["paths"]["/api/runs"]["get"]["parameters"]
  }
  assert runs_params["strategy_id"]["description"] == "Filter runs by strategy identifier."
  assert runs_params["strategy_id"]["schema"]["title"] == "Strategy ID"
  assert _first_non_null_schema_branch(runs_params["strategy_id"]["schema"])["minLength"] == 1
  assert runs_params["tag"]["description"] == "Filter runs by experiment tags."
  assert runs_params["tag"]["schema"]["title"] == "Tags"

  compare_params = {
    param["name"]: param
    for param in openapi["paths"]["/api/runs/compare"]["get"]["parameters"]
  }
  assert compare_params["run_id"]["description"] == "Run identifiers to include in the comparison set."
  assert _first_non_null_schema_branch(compare_params["intent"]["schema"])["minLength"] == 1
  assert compare_params["intent"]["schema"]["title"] == "Comparison intent"
  assert _first_non_null_schema_branch(runs_params["started_at"]["schema"])["format"] == "date-time"
  assert _first_non_null_schema_branch(runs_params["updated_at"]["schema"])["format"] == "date-time"
  assert _first_non_null_schema_branch(runs_params["exposure_pct"]["schema"])["maximum"] == 100

  run_query_schema = openapi["paths"]["/api/runs"]["get"]["x-akra-query-schema"]
  assert run_query_schema["grouped_filters"]["param_pattern"] == "group__<group_key>__<filter_key>__<operator>"
  assert run_query_schema["expression_trees"]["param"] == "filter_expr"
  assert run_query_schema["expression_trees"]["logic_values"] == ["and", "or"]
  assert run_query_schema["expression_trees"]["supports_negation"] is True
  assert run_query_schema["expression_trees"]["predicate_refs"]["registry_field"] == "predicates"
  assert run_query_schema["expression_trees"]["predicate_refs"]["reference_field"] == "predicate_ref"
  assert run_query_schema["expression_trees"]["predicate_templates"]["registry_field"] == "predicate_templates"
  assert run_query_schema["expression_trees"]["predicate_templates"]["template_field"] == "template"
  assert run_query_schema["expression_trees"]["predicate_templates"]["bindings_field"] == "bindings"
  assert run_query_schema["expression_trees"]["predicate_templates"]["binding_reference_shape"] == {
    "binding": "<parameter_name>",
  }
  assert run_query_schema["expression_trees"]["quantified_conditions"]["field"] == "quantifier"
  assert run_query_schema["expression_trees"]["quantified_conditions"]["values"] == ["any", "all", "none"]
  assert run_query_schema["expression_trees"]["collection_nodes"]["field"] == "collection"
  assert run_query_schema["expression_trees"]["collection_nodes"]["shape"]["path_template"] == "<collection path template>"
  assert run_query_schema["expression_trees"]["collection_nodes"]["shape"]["bindings"] == {
    "<parameter_key>": "<value or binding reference>",
  }
  assert run_query_schema["expression_trees"]["collection_nodes"]["shape"]["quantifier"] == "any|all|none"
  assert "flattening nested collection-of-collection paths" in run_query_schema["expression_trees"]["collection_nodes"]["semantics"]
  assert run_query_schema["expression_trees"]["collection_schemas"][0]["path"] == ["orders"]
  assert run_query_schema["expression_trees"]["collection_schemas"][0]["path_template"] == ["orders"]
  assert run_query_schema["expression_trees"]["collection_schemas"][0]["filter_keys"] == [
    "order_status",
    "order_type",
  ]
  assert run_query_schema["expression_trees"]["collection_schemas"][0]["element_schema"][0]["key"] == "order_status"
  assert run_query_schema["expression_trees"]["collection_schemas"][0]["element_schema"][0]["value_path"] == [
    "status",
    "value",
  ]
  assert run_query_schema["expression_trees"]["collection_schemas"][0]["element_schema"][0]["query_exposed"] is False
  assert run_query_schema["expression_trees"]["collection_schemas"][1]["path"] == [
    "provenance",
    "market_data_by_symbol",
    "issues",
  ]
  assert run_query_schema["expression_trees"]["collection_schemas"][1]["path_template"] == [
    "provenance",
    "market_data_by_symbol",
    "{symbol_key}",
    "issues",
  ]
  assert run_query_schema["expression_trees"]["collection_schemas"][1]["item_kind"] == "issue_text"
  assert run_query_schema["expression_trees"]["collection_schemas"][1]["parameters"][0]["key"] == "symbol_key"
  assert run_query_schema["expression_trees"]["collection_schemas"][1]["parameters"][0]["kind"] == "dynamic_map_key"
  assert run_query_schema["expression_trees"]["collection_schemas"][1]["parameters"][0]["domain"] == {
    "key": "market_data_symbol_key",
    "source": "run.provenance.market_data_by_symbol",
    "values": ["binance:BTC/USDT"],
    "enum_source": {
      "kind": "dynamic_map_keys",
      "surface_key": "run_list",
      "path": ["provenance", "market_data_by_symbol"],
    },
  }
  assert run_query_schema["expression_trees"]["collection_schemas"][1]["element_schema"][0]["key"] == "issue_text"
  assert run_query_schema["expression_trees"]["collection_schemas"][1]["element_schema"][0]["value_root"] is True
  started_at_filter = next(item for item in run_query_schema["filters"] if item["key"] == "started_at")
  assert started_at_filter["value_type"] == "datetime"
  assert started_at_filter["value_path"] == ["started_at"]
  assert [operator["key"] for operator in started_at_filter["operators"]] == [
    "eq",
    "gt",
    "ge",
    "lt",
    "le",
  ]
  total_return_filter = next(item for item in run_query_schema["filters"] if item["key"] == "total_return_pct")
  assert total_return_filter["value_type"] == "number"
  assert total_return_filter["value_path"] == ["metrics", "total_return_pct"]
  assert [operator["key"] for operator in total_return_filter["operators"]] == [
    "eq",
    "gt",
    "ge",
    "lt",
    "le",
  ]
  tag_filter = next(item for item in run_query_schema["filters"] if item["key"] == "tag")
  assert [operator["key"] for operator in tag_filter["operators"]] == [
    "contains_all",
    "contains_any",
    "eq",
    "prefix",
  ]
  order_status_filter = next(item for item in run_query_schema["filters"] if item["key"] == "order_status")
  assert order_status_filter["query_exposed"] is False
  assert order_status_filter["value_path"] == ["status", "value"]
  issue_text_filter = next(item for item in run_query_schema["filters"] if item["key"] == "issue_text")
  assert issue_text_filter["query_exposed"] is False
  assert issue_text_filter["value_path"] == []
  assert run_query_schema["sort_fields"][0]["key"] == "updated_at"
  assert run_query_schema["sort_fields"][0]["default_direction"] == "desc"
  assert any(field["key"] == "trade_count" for field in run_query_schema["sort_fields"])
  nested_metric_sort = next(
    field
    for field in run_query_schema["sort_fields"]
    if field["key"] == "metrics.total_return_pct"
  )
  assert nested_metric_sort["value_type"] == "number"
  assert nested_metric_sort["value_path"] == ["metrics", "total_return_pct"]
  run_sort_param = next(
    param for param in openapi["paths"]["/api/runs"]["get"]["parameters"]
    if param["name"] == "sort"
  )
  assert run_sort_param["description"] == "Sort fields in `<field>` or `<field>:<direction>` format."
  filter_expr_param = next(
    param for param in openapi["paths"]["/api/runs"]["get"]["parameters"]
    if param["name"] == "filter_expr"
  )
  assert filter_expr_param["description"] == (
    "JSON boolean expression tree using `logic`, `conditions`, `children`, and optional `negated` fields."
  )
  assert "order_status" not in runs_params
  assert _first_non_null_schema_branch(runs_params["trade_count"]["schema"])["minimum"] == 0
  assert runs_params["total_return_pct"]["schema"]["title"] == "Total return %"

  compare_query_schema = openapi["paths"]["/api/runs/compare"]["get"]["x-akra-query-schema"]
  assert compare_query_schema["filters"][0]["operators"][0]["key"] == "include"
  compare_score_filter = next(item for item in compare_query_schema["filters"] if item["key"] == "narrative_score")
  assert compare_score_filter["value_path"] == ["insight_score"]
  assert [operator["key"] for operator in compare_score_filter["operators"]] == [
    "eq",
    "gt",
    "ge",
    "lt",
    "le",
  ]
  assert compare_query_schema["sort_fields"][1]["key"] == "narrative_score"
  assert any(field["key"] == "narratives.insight_score" for field in compare_query_schema["sort_fields"])
  assert compare_params["narrative_score"]["schema"]["title"] == "Narrative score"

  market_data_params = {
    param["name"]: param
    for param in openapi["paths"]["/api/market-data/status"]["get"]["parameters"]
  }
  assert market_data_params["timeframe"]["description"] == (
    "Candlestick timeframe to inspect in market-data status."
  )
  assert market_data_params["timeframe"]["schema"]["minLength"] == 2
  assert openapi["paths"]["/api/market-data/status"]["get"]["x-akra-query-schema"]["filters"][0]["operators"][0]["key"] == "eq"

  lineage_history_params = {
    param["name"]: param
    for param in openapi["paths"]["/api/market-data/lineage-history"]["get"]["parameters"]
  }
  assert lineage_history_params["validation_claim"]["description"] == (
    "Filter lineage history by normalized dataset-boundary claim."
  )
  assert lineage_history_params["issue"]["schema"]["type"] == "array"
  assert openapi["paths"]["/api/market-data/lineage-history"]["get"]["x-akra-query-schema"]["sort_fields"][0]["key"] == (
    "recorded_at"
  )

  ingestion_job_params = {
    param["name"]: param
    for param in openapi["paths"]["/api/market-data/ingestion-jobs"]["get"]["parameters"]
  }
  assert ingestion_job_params["operation"]["description"] == (
    "Filter ingestion jobs by sync operation kind."
  )
  assert ingestion_job_params["duration_ms"]["schema"]["title"] == "Duration ms"
  assert openapi["paths"]["/api/market-data/ingestion-jobs"]["get"]["x-akra-query-schema"]["sort_fields"][0]["key"] == (
    "started_at"
  )


def test_strategy_query_contract_applies_prefix_filter_and_sort(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  response = client.get("/api/strategies?version__prefix=1.&sort=strategy_id:asc")

  assert response.status_code == 200
  payload = response.json()
  assert payload
  assert all(item["version"].startswith("1.") for item in payload)
  assert [item["strategy_id"] for item in payload] == sorted(item["strategy_id"] for item in payload)


def test_strategy_query_contract_applies_nested_datetime_filter_and_sort(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  response = client.post(
    "/api/strategies/register",
    json={
      "strategy_id": "ma_cross_v1",
      "module_path": "akra_trader.strategies.examples",
      "class_name": "MovingAverageCrossStrategy",
    },
  )
  assert response.status_code == 200

  response = client.get(
    "/api/strategies",
    params=[
      ("registered_at__ge", "2000-01-01T00:00:00+00:00"),
      ("sort", "lifecycle.registered_at:desc"),
    ],
  )

  assert response.status_code == 200
  payload = response.json()
  assert payload
  assert [item["strategy_id"] for item in payload] == ["ma_cross_v1"]
  assert payload[0]["lifecycle"]["registered_at"] is not None


def test_preset_query_contract_applies_operator_filter_and_sort(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  create_preset(client, name="First", preset_id="first", strategy_id="ma_cross_v1", timeframe="5m")
  create_preset(client, name="Second", preset_id="second", strategy_id="ma_cross_v1", timeframe="5m")

  response = client.get("/api/presets?strategy_id__eq=ma_cross_v1&sort=created_at:asc")

  assert response.status_code == 200
  payload = response.json()
  assert [item["preset_id"] for item in payload[:2]] == ["first", "second"]


def test_run_query_contract_applies_tag_operator_and_sort(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  baseline_run = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "tags": ["baseline"],
    },
  ).json()
  client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "ETH/USDT",
      "timeframe": "5m",
      "tags": ["stress"],
    },
  )
  second_baseline_run = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "SOL/USDT",
      "timeframe": "5m",
      "tags": ["baseline", "review"],
    },
  ).json()

  response = client.get("/api/runs?tag__contains_any=baseline&sort=started_at:asc")

  assert response.status_code == 200
  payload = response.json()
  assert [item["config"]["run_id"] for item in payload[:2]] == [
    baseline_run["config"]["run_id"],
    second_baseline_run["config"]["run_id"],
  ]


def test_run_query_contract_applies_numeric_range_filters_and_multi_field_sort(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    run_ids: list[str] = []
    for symbol in ("BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"):
      response = client.post(
        "/api/runs/backtests",
        json={
          "strategy_id": "ma_cross_v1",
          "symbol": symbol,
          "timeframe": "5m",
        },
      )
      assert response.status_code == 200
      run_ids.append(response.json()["config"]["run_id"])

    app = client.app.state.container.app
    metric_overrides = {
      run_ids[0]: {"total_return_pct": 18.0, "trade_count": 4},
      run_ids[1]: {"total_return_pct": 12.0, "trade_count": 4},
      run_ids[2]: {"total_return_pct": 12.0, "trade_count": 4},
      run_ids[3]: {"total_return_pct": 22.0, "trade_count": 2},
    }
    for run_id, metrics in metric_overrides.items():
      run = app.get_run(run_id)
      assert run is not None
      run.metrics.update(metrics)
      app._runs.save_run(run)

    response = client.get(
      "/api/runs",
      params=[
        ("total_return_pct__ge", "10"),
        ("trade_count__ge", "2"),
        ("sort", "trade_count:desc"),
        ("sort", "total_return_pct:asc"),
        ("sort", "run_id:asc"),
      ],
    )

    assert response.status_code == 200
    payload = response.json()
    expected_leading_ids = [
      *sorted((run_ids[1], run_ids[2])),
      run_ids[0],
      run_ids[3],
    ]
    assert [item["config"]["run_id"] for item in payload[:4]] == expected_leading_ids
    assert all(item["metrics"]["total_return_pct"] >= 10 for item in payload[:4])
    assert all(item["metrics"]["trade_count"] >= 2 for item in payload[:4])


def test_run_query_contract_applies_datetime_ranges_wider_metrics_and_nested_sort(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    run_ids: list[str] = []
    for symbol in ("BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"):
      response = client.post(
        "/api/runs/backtests",
        json={
          "strategy_id": "ma_cross_v1",
          "symbol": symbol,
          "timeframe": "5m",
        },
      )
      assert response.status_code == 200
      run_ids.append(response.json()["config"]["run_id"])

    app = client.app.state.container.app
    started_at_by_run = {
      run_ids[0]: datetime(2025, 1, 1, 0, 0, tzinfo=UTC),
      run_ids[1]: datetime(2025, 1, 1, 1, 0, tzinfo=UTC),
      run_ids[2]: datetime(2025, 1, 1, 2, 0, tzinfo=UTC),
      run_ids[3]: datetime(2025, 1, 1, 3, 0, tzinfo=UTC),
    }
    metric_overrides = {
      run_ids[0]: {"ending_equity": 10800.0, "exposure_pct": 35.0, "total_return_pct": 8.0, "trade_count": 3},
      run_ids[1]: {"ending_equity": 11200.0, "exposure_pct": 40.0, "total_return_pct": 12.0, "trade_count": 4},
      run_ids[2]: {"ending_equity": 11200.0, "exposure_pct": 65.0, "total_return_pct": 12.0, "trade_count": 4},
      run_ids[3]: {"ending_equity": 12200.0, "exposure_pct": 70.0, "total_return_pct": 22.0, "trade_count": 2},
    }
    for run_id in run_ids:
      run = app.get_run(run_id)
      assert run is not None
      run.started_at = started_at_by_run[run_id]
      run.ended_at = started_at_by_run[run_id] + timedelta(minutes=15)
      run.metrics.update(metric_overrides[run_id])
      app._runs.save_run(run)

    response = client.get(
      "/api/runs",
      params=[
        ("started_at__ge", "2025-01-01T01:00:00+00:00"),
        ("ending_equity__ge", "11200"),
        ("exposure_pct__ge", "40"),
        ("sort", "metrics.trade_count:desc"),
        ("sort", "metrics.total_return_pct:asc"),
        ("sort", "config.run_id:asc"),
      ],
    )

    assert response.status_code == 200
    payload = response.json()
    expected_leading_ids = [
      *sorted((run_ids[1], run_ids[2])),
      run_ids[3],
    ]
    assert [item["config"]["run_id"] for item in payload[:3]] == expected_leading_ids
    assert all(
      datetime.fromisoformat(item["started_at"]) >= datetime(2025, 1, 1, 1, 0, tzinfo=UTC)
      for item in payload[:3]
    )
    assert all(item["metrics"]["ending_equity"] >= 11200 for item in payload[:3])
    assert all(item["metrics"]["exposure_pct"] >= 40 for item in payload[:3])


def test_run_query_contract_applies_grouped_filter_expressions(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    run_ids: list[str] = []
    for symbol in ("BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"):
      response = client.post(
        "/api/runs/backtests",
        json={
          "strategy_id": "ma_cross_v1",
          "symbol": symbol,
          "timeframe": "5m",
        },
      )
      assert response.status_code == 200
      run_ids.append(response.json()["config"]["run_id"])

    app = client.app.state.container.app
    metric_overrides = {
      run_ids[0]: {"total_return_pct": 25.0, "trade_count": 3},
      run_ids[1]: {"total_return_pct": 18.0, "trade_count": 5},
      run_ids[2]: {"total_return_pct": 9.0, "trade_count": 1},
      run_ids[3]: {"total_return_pct": 30.0, "trade_count": 1},
    }
    for run_id, metrics in metric_overrides.items():
      run = app.get_run(run_id)
      assert run is not None
      run.metrics.update(metrics)
      app._runs.save_run(run)

    response = client.get(
      "/api/runs",
      params=[
        ("group__return_band__total_return_pct__ge", "20"),
        ("group__return_band__trade_count__ge", "2"),
        ("group__volume_band__trade_count__ge", "5"),
        ("group__volume_band__total_return_pct__ge", "15"),
        ("sort", "config.run_id:asc"),
      ],
    )

    assert response.status_code == 200
    payload = response.json()
    returned_run_ids = [item["config"]["run_id"] for item in payload]
    assert returned_run_ids == sorted([run_ids[0], run_ids[1]])
    assert run_ids[2] not in returned_run_ids
    assert run_ids[3] not in returned_run_ids


def test_run_query_contract_applies_nested_boolean_filter_expression_tree(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    run_ids: list[str] = []
    for symbol in ("BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"):
      response = client.post(
        "/api/runs/backtests",
        json={
          "strategy_id": "ma_cross_v1",
          "symbol": symbol,
          "timeframe": "5m",
        },
      )
      assert response.status_code == 200
      run_ids.append(response.json()["config"]["run_id"])

    app = client.app.state.container.app
    metric_overrides = {
      run_ids[0]: {"total_return_pct": 25.0, "trade_count": 3},
      run_ids[1]: {"total_return_pct": 18.0, "trade_count": 5},
      run_ids[2]: {"total_return_pct": 9.0, "trade_count": 1},
      run_ids[3]: {"total_return_pct": 30.0, "trade_count": 1},
    }
    for run_id, metrics in metric_overrides.items():
      run = app.get_run(run_id)
      assert run is not None
      run.metrics.update(metrics)
      app._runs.save_run(run)

    filter_expression = {
      "logic": "and",
      "children": [
        {
          "logic": "or",
          "children": [
            {
              "logic": "and",
              "conditions": [
                {"key": "total_return_pct", "operator": "ge", "value": 20},
                {"key": "trade_count", "operator": "ge", "value": 2},
              ],
            },
            {
              "logic": "and",
              "conditions": [
                {"key": "trade_count", "operator": "ge", "value": 5},
                {"key": "total_return_pct", "operator": "ge", "value": 15},
              ],
            },
          ],
        },
        {
          "logic": "and",
          "negated": True,
          "conditions": [
            {"key": "total_return_pct", "operator": "ge", "value": 30},
            {"key": "trade_count", "operator": "le", "value": 1},
          ],
        },
      ],
    }

    response = client.get(
      "/api/runs",
      params=[
        ("filter_expr", json.dumps(filter_expression)),
        ("sort", "config.run_id:asc"),
      ],
    )

    assert response.status_code == 200
    payload = response.json()
    returned_run_ids = [item["config"]["run_id"] for item in payload]
    assert returned_run_ids == sorted([run_ids[0], run_ids[1]])
    assert run_ids[2] not in returned_run_ids
    assert run_ids[3] not in returned_run_ids


def test_run_query_contract_supports_predicate_references_and_quantified_list_predicates(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    runs_by_symbol: dict[str, str] = {}
    tags_by_symbol = {
      "BTC/USDT": ["baseline", "review"],
      "ETH/USDT": ["review", "candidate"],
      "SOL/USDT": ["stress-alpha", "candidate"],
      "XRP/USDT": ["baseline", "stress-beta"],
    }
    for symbol, tags in tags_by_symbol.items():
      response = client.post(
        "/api/runs/backtests",
        json={
          "strategy_id": "ma_cross_v1",
          "symbol": symbol,
          "timeframe": "5m",
          "tags": tags,
        },
      )
      assert response.status_code == 200
      runs_by_symbol[symbol] = response.json()["config"]["run_id"]

    filter_expression = {
      "predicates": {
        "baseline_or_review": {
          "logic": "or",
          "conditions": [
            {"key": "tag", "operator": "eq", "quantifier": "any", "value": "baseline"},
            {"key": "tag", "operator": "eq", "quantifier": "any", "value": "review"},
          ],
        },
        "no_stress_prefix": {
          "logic": "and",
          "conditions": [
            {"key": "tag", "operator": "prefix", "quantifier": "none", "value": "stress"},
          ],
        },
      },
      "root": {
        "logic": "and",
        "children": [
          {"predicate_ref": "baseline_or_review"},
          {"predicate_ref": "no_stress_prefix"},
        ],
      },
    }

    response = client.get(
      "/api/runs",
      params=[
        ("filter_expr", json.dumps(filter_expression)),
        ("sort", "config.run_id:asc"),
      ],
    )

    assert response.status_code == 200
    payload = response.json()
    returned_run_ids = [item["config"]["run_id"] for item in payload]
    assert returned_run_ids == sorted(
      [
        runs_by_symbol["BTC/USDT"],
        runs_by_symbol["ETH/USDT"],
      ]
    )
    assert runs_by_symbol["SOL/USDT"] not in returned_run_ids
    assert runs_by_symbol["XRP/USDT"] not in returned_run_ids


def test_run_query_contract_supports_parameterized_predicate_templates_and_collection_bindings(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    runs_by_symbol: dict[str, str] = {}
    for symbol in ("BTC/USDT", "ETH/USDT", "SOL/USDT"):
      response = client.post(
        "/api/runs/backtests",
        json={
          "strategy_id": "ma_cross_v1",
          "symbol": symbol,
          "timeframe": "5m",
        },
      )
      assert response.status_code == 200
      runs_by_symbol[symbol] = response.json()["config"]["run_id"]

    app = client.app.state.container.app
    lineage_by_symbol = {
      "BTC/USDT": {
        "binance:BTC/USDT": MarketDataLineage(
          provider="seeded",
          venue="binance",
          symbols=("BTC/USDT",),
          timeframe="5m",
          issues=("gap:btc", "stale:btc"),
        ),
      },
      "ETH/USDT": {
        "binance:ETH/USDT": MarketDataLineage(
          provider="seeded",
          venue="binance",
          symbols=("ETH/USDT",),
          timeframe="5m",
          issues=("review:eth", "gap:eth"),
        ),
      },
      "SOL/USDT": {
        "binance:SOL/USDT": MarketDataLineage(
          provider="seeded",
          venue="binance",
          symbols=("SOL/USDT",),
          timeframe="5m",
          issues=("stale:sol",),
        ),
      },
    }
    for symbol, market_data_by_symbol in lineage_by_symbol.items():
      run = app.get_run(runs_by_symbol[symbol])
      assert run is not None
      run.provenance.market_data_by_symbol = market_data_by_symbol
      app._runs.save_run(run)

    filter_expression = {
      "predicate_templates": {
        "issue_prefix_for_symbol": {
          "parameters": {
            "symbol_key": {},
            "issue_prefix": {},
          },
          "template": {
            "collection": {
              "path_template": [
                "provenance",
                "market_data_by_symbol",
                "{symbol_key}",
                "issues",
              ],
              "bindings": {
                "symbol_key": {
                  "binding": "symbol_key",
                },
              },
              "quantifier": "any",
            },
            "logic": "and",
            "conditions": [
              {
                "key": "issue_text",
                "operator": "prefix",
                "value": {
                  "binding": "issue_prefix",
                },
              },
            ],
          },
        },
      },
      "root": {
        "logic": "or",
        "children": [
          {
            "predicate_ref": "issue_prefix_for_symbol",
            "bindings": {
              "symbol_key": "binance:BTC/USDT",
              "issue_prefix": "gap:",
            },
          },
          {
            "predicate_ref": "issue_prefix_for_symbol",
            "bindings": {
              "symbol_key": "binance:ETH/USDT",
              "issue_prefix": "review:",
            },
          },
        ],
      },
    }

    response = client.get(
      "/api/runs",
      params=[
        ("filter_expr", json.dumps(filter_expression)),
        ("sort", "config.run_id:asc"),
      ],
    )

    assert response.status_code == 200
    payload = response.json()
    returned_run_ids = [item["config"]["run_id"] for item in payload]
    assert returned_run_ids == sorted(
      [
        runs_by_symbol["BTC/USDT"],
        runs_by_symbol["ETH/USDT"],
      ]
    )
    assert runs_by_symbol["SOL/USDT"] not in returned_run_ids


def test_run_query_contract_supports_quantified_nested_object_collection_predicates(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    runs_by_symbol: dict[str, str] = {}
    for symbol in ("BTC/USDT", "ETH/USDT", "SOL/USDT"):
      response = client.post(
        "/api/runs/backtests",
        json={
          "strategy_id": "ma_cross_v1",
          "symbol": symbol,
          "timeframe": "5m",
        },
      )
      assert response.status_code == 200
      runs_by_symbol[symbol] = response.json()["config"]["run_id"]

    app = client.app.state.container.app
    order_sets = {
      "BTC/USDT": [
        Order(
          run_id=runs_by_symbol["BTC/USDT"],
          instrument_id="binance:BTC/USDT",
          side=OrderSide.BUY,
          quantity=1.0,
          requested_price=101.0,
          order_type=OrderType.LIMIT,
          status=OrderStatus.OPEN,
        ),
        Order(
          run_id=runs_by_symbol["BTC/USDT"],
          instrument_id="binance:BTC/USDT",
          side=OrderSide.SELL,
          quantity=1.0,
          requested_price=102.0,
          order_type=OrderType.MARKET,
          status=OrderStatus.FILLED,
        ),
      ],
      "ETH/USDT": [
        Order(
          run_id=runs_by_symbol["ETH/USDT"],
          instrument_id="binance:ETH/USDT",
          side=OrderSide.BUY,
          quantity=1.0,
          requested_price=201.0,
          order_type=OrderType.LIMIT,
          status=OrderStatus.FILLED,
        ),
      ],
      "SOL/USDT": [
        Order(
          run_id=runs_by_symbol["SOL/USDT"],
          instrument_id="binance:SOL/USDT",
          side=OrderSide.BUY,
          quantity=1.0,
          requested_price=301.0,
          order_type=OrderType.MARKET,
          status=OrderStatus.OPEN,
        ),
      ],
    }
    for symbol, orders in order_sets.items():
      run = app.get_run(runs_by_symbol[symbol])
      assert run is not None
      run.orders = orders
      app._runs.save_run(run)

    filter_expression = {
      "predicates": {
        "open_limit_order": {
          "collection": {
            "path": "orders",
            "quantifier": "any",
          },
          "logic": "and",
          "conditions": [
            {"key": "order_status", "operator": "eq", "value": "open"},
            {"key": "order_type", "operator": "eq", "value": "limit"},
          ],
        },
      },
      "root": {
        "predicate_ref": "open_limit_order",
      },
    }

    response = client.get(
      "/api/runs",
      params=[
        ("filter_expr", json.dumps(filter_expression)),
        ("sort", "config.run_id:asc"),
      ],
    )

    assert response.status_code == 200
    payload = response.json()
    returned_run_ids = [item["config"]["run_id"] for item in payload]
    assert returned_run_ids == [runs_by_symbol["BTC/USDT"]]


def test_run_query_contract_supports_nested_collection_of_collection_paths(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    runs_by_symbol: dict[str, str] = {}
    for symbol in ("BTC/USDT", "ETH/USDT", "SOL/USDT"):
      response = client.post(
        "/api/runs/backtests",
        json={
          "strategy_id": "ma_cross_v1",
          "symbol": symbol,
          "timeframe": "5m",
        },
      )
      assert response.status_code == 200
      runs_by_symbol[symbol] = response.json()["config"]["run_id"]

    app = client.app.state.container.app
    lineage_by_symbol = {
      "BTC/USDT": {
        "binance:BTC/USDT": MarketDataLineage(
          provider="seeded",
          venue="binance",
          symbols=("BTC/USDT",),
          timeframe="5m",
          issues=("gap:btc", "stale:btc"),
        ),
        "binance:ETH/USDT": MarketDataLineage(
          provider="seeded",
          venue="binance",
          symbols=("ETH/USDT",),
          timeframe="5m",
          issues=("review:eth",),
        ),
      },
      "ETH/USDT": {
        "binance:ETH/USDT": MarketDataLineage(
          provider="seeded",
          venue="binance",
          symbols=("ETH/USDT",),
          timeframe="5m",
          issues=("review:eth", "gap:eth"),
        ),
      },
      "SOL/USDT": {
        "binance:SOL/USDT": MarketDataLineage(
          provider="seeded",
          venue="binance",
          symbols=("SOL/USDT",),
          timeframe="5m",
          issues=("stale:sol",),
        ),
      },
    }
    for symbol, market_data_by_symbol in lineage_by_symbol.items():
      run = app.get_run(runs_by_symbol[symbol])
      assert run is not None
      run.provenance.market_data_by_symbol = market_data_by_symbol
      app._runs.save_run(run)

    filter_expression = {
      "collection": {
        "path": "provenance.market_data_by_symbol.issues",
        "quantifier": "any",
      },
      "logic": "and",
      "conditions": [
        {"key": "issue_text", "operator": "prefix", "value": "gap:"},
      ],
    }

    response = client.get(
      "/api/runs",
      params=[
        ("filter_expr", json.dumps(filter_expression)),
        ("sort", "config.run_id:asc"),
      ],
    )

    assert response.status_code == 200
    payload = response.json()
    returned_run_ids = [item["config"]["run_id"] for item in payload]
    assert returned_run_ids == sorted(
      [
        runs_by_symbol["BTC/USDT"],
        runs_by_symbol["ETH/USDT"],
      ]
    )
    assert runs_by_symbol["SOL/USDT"] not in returned_run_ids


def test_run_query_contract_rejects_unknown_collection_shape_paths(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    response = client.post(
      "/api/runs/backtests",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "BTC/USDT",
        "timeframe": "5m",
      },
    )
    assert response.status_code == 200

    filter_expression = {
      "collection": {
        "path": "provenance.market_data_by_symbol.unknown_branch",
        "quantifier": "any",
      },
      "logic": "and",
      "conditions": [
        {"key": "issue_text", "operator": "prefix", "value": "gap:"},
      ],
    }

    response = client.get(
      "/api/runs",
      params=[("filter_expr", json.dumps(filter_expression))],
    )

    assert response.status_code == 400
    assert "Unsupported filter expression collection path" in response.json()["detail"]


def test_compare_query_contract_applies_runtime_sort_to_narratives(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  run_ids: list[str] = []
  for short_window in (5, 8, 13):
    response = client.post(
      "/api/runs/backtests",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "BTC/USDT",
        "timeframe": "5m",
        "parameters": {"short_window": short_window, "long_window": 21},
      },
    )
    assert response.status_code == 200
    run_ids.append(response.json()["config"]["run_id"])

  response = client.get(
    "/api/runs/compare",
    params=[
      ("run_id", run_ids[0]),
      ("run_id", run_ids[1]),
      ("run_id", run_ids[2]),
      ("intent", "strategy_tuning"),
      ("sort", "narrative_score:asc"),
    ],
  )

  assert response.status_code == 200
  payload = response.json()
  scores = [item["insight_score"] for item in payload["narratives"]]
  assert scores == sorted(scores)


def test_compare_query_contract_applies_numeric_range_filter_and_multi_field_sort(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  run_ids: list[str] = []
  for short_window in (5, 8, 13):
    response = client.post(
      "/api/runs/backtests",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "BTC/USDT",
        "timeframe": "5m",
        "parameters": {"short_window": short_window, "long_window": 21},
      },
    )
    assert response.status_code == 200
    run_ids.append(response.json()["config"]["run_id"])

  app = client.app.state.container.app
  app.compare_runs = lambda run_ids, intent=None: RunComparison(
    requested_run_ids=tuple(run_ids),
    baseline_run_id=run_ids[0],
    runs=tuple(
      RunComparisonRun(
        run_id=run_id,
        mode="backtest",
        status="completed",
        lane="native",
        strategy_id="ma_cross_v1",
        strategy_name="MovingAverageCrossStrategy",
        strategy_version="1.0.0",
        symbols=("BTC/USDT",),
        timeframe="5m",
        started_at=datetime(2025, 1, 1, index, 0, tzinfo=UTC),
      )
      for index, run_id in enumerate(run_ids)
    ),
    metric_rows=(),
    intent=intent or "strategy_tuning",
    narratives=(
      RunComparisonNarrative(
        run_id=run_ids[1],
        baseline_run_id=run_ids[0],
        comparison_type="native_vs_native",
        title="Candidate one",
        summary="Candidate one summary",
        insight_score=5.0,
      ),
      RunComparisonNarrative(
        run_id=run_ids[2],
        baseline_run_id=run_ids[0],
        comparison_type="native_vs_native",
        title="Candidate two",
        summary="Candidate two summary",
        insight_score=5.0,
      ),
    ),
  )

  threshold = 5.0

  response = client.get(
    "/api/runs/compare",
    params=[
      ("run_id", run_ids[0]),
      ("run_id", run_ids[1]),
      ("run_id", run_ids[2]),
      ("intent", "strategy_tuning"),
      ("narrative_score__ge", str(threshold)),
      ("sort", "narratives.insight_score:asc"),
      ("sort", "narratives.run_id_order:desc"),
    ],
  )

  assert response.status_code == 200
  payload = response.json()
  assert [item["run_id"] for item in payload["narratives"]] == [run_ids[2], run_ids[1]]
  assert all(item["insight_score"] >= threshold for item in payload["narratives"])


def test_list_references_returns_catalog_entries(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  response = client.get("/api/references")
  assert response.status_code == 200
  payload = response.json()
  assert any(item["reference_id"] == "nautilus-trader" for item in payload)
  assert any(item["reference_id"] == "nostalgia-for-infinity" for item in payload)


def test_presets_endpoint_persists_catalog_entries_across_restart(tmp_path: Path) -> None:
  database_path = tmp_path / "runs.sqlite3"
  client = build_client(database_path)

  created = create_preset(
    client,
    name="Core 5m",
    preset_id="core_5m",
    strategy_id="ma_cross_v1",
    timeframe="5m",
    benchmark_family="native_validation",
    tags=["baseline"],
    parameters={"short_window": 5, "long_window": 13},
  )

  assert created["preset_id"] == "core_5m"
  assert created["strategy_id"] == "ma_cross_v1"
  assert created["benchmark_family"] == "native_validation"
  assert created["tags"] == ["baseline"]
  assert created["parameters"] == {"short_window": 5, "long_window": 13}
  assert created["lifecycle"]["stage"] == "draft"

  restarted_client = build_client(database_path)
  response = restarted_client.get("/api/presets")

  assert response.status_code == 200
  payload = response.json()
  assert any(item["preset_id"] == "core_5m" for item in payload)


def test_preset_lifecycle_action_endpoint_updates_stage(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  create_preset(
    client,
    name="Core 5m",
    preset_id="core_5m",
    strategy_id="ma_cross_v1",
    timeframe="5m",
  )

  promoted = client.post(
    "/api/presets/core_5m/lifecycle",
    json={"action": "promote", "actor": "operator", "reason": "benchmark_candidate_ready"},
  )
  archived = client.post(
    "/api/presets/core_5m/lifecycle",
    json={"action": "archive", "actor": "operator", "reason": "superseded"},
  )

  assert promoted.status_code == 200
  assert promoted.json()["lifecycle"]["stage"] == "benchmark_candidate"
  assert archived.status_code == 200
  assert archived.json()["lifecycle"]["stage"] == "archived"
  assert [event["action"] for event in archived.json()["lifecycle"]["history"]] == [
    "created",
    "promote",
    "archive",
  ]


def test_preset_update_and_revision_endpoints_persist_bundle_history(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  create_preset(
    client,
    name="Core 5m",
    preset_id="core_5m",
    strategy_id="ma_cross_v1",
    timeframe="5m",
    parameters={"short_window": 5, "long_window": 13},
  )

  updated = client.patch(
    "/api/presets/core_5m",
    json={
      "description": "Expanded validation bundle",
      "benchmark_family": "native_validation",
      "tags": ["baseline", "momentum"],
      "parameters": {"short_window": 7, "long_window": 21},
      "actor": "operator",
      "reason": "tighten_signal_bundle",
    },
  )
  revisions = client.get("/api/presets/core_5m/revisions")
  restored = client.post(
    "/api/presets/core_5m/revisions/core_5m:r0001/restore",
    json={"actor": "operator", "reason": "revert_to_baseline"},
  )
  fetched = client.get("/api/presets/core_5m")

  assert updated.status_code == 200
  assert updated.json()["revisions"][-1]["revision_id"] == "core_5m:r0002"
  assert updated.json()["revisions"][-1]["action"] == "updated"
  assert updated.json()["parameters"] == {"short_window": 7, "long_window": 21}
  assert revisions.status_code == 200
  assert [item["revision_id"] for item in revisions.json()] == [
    "core_5m:r0002",
    "core_5m:r0001",
  ]
  assert revisions.json()[0]["reason"] == "tighten_signal_bundle"
  assert restored.status_code == 200
  assert restored.json()["parameters"] == {"short_window": 5, "long_window": 13}
  assert restored.json()["revisions"][-1]["revision_id"] == "core_5m:r0003"
  assert restored.json()["revisions"][-1]["source_revision_id"] == "core_5m:r0001"
  assert fetched.status_code == 200
  assert fetched.json()["parameters"] == {"short_window": 5, "long_window": 13}
  assert [item["action"] for item in fetched.json()["revisions"]] == [
    "created",
    "updated",
    "restored",
  ]


def test_preset_update_endpoint_rejects_empty_patch(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  create_preset(
    client,
    name="Core 5m",
    preset_id="core_5m",
    strategy_id="ma_cross_v1",
    timeframe="5m",
  )

  response = client.patch("/api/presets/core_5m", json={})

  assert response.status_code == 400
  assert response.json()["detail"] == "Preset update requires at least one field."


def test_run_surface_capabilities_endpoint_returns_shared_eligibility_contract(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  response = client.get("/api/capabilities/run-surfaces")

  assert response.status_code == 200
  payload = response.json()
  assert payload["discovery"].keys() == {"shared_contracts"}
  shared_contracts = {
    contract["contract_key"]: contract
    for contract in payload["discovery"]["shared_contracts"]
  }
  assert "families" not in payload
  assert shared_contracts["schema:run-surface-capabilities"]["contract_kind"] == "schema_metadata"
  assert shared_contracts["schema:run-surface-capabilities"]["title"] == "Run-surface capability contract"
  assert shared_contracts["schema:run-surface-capabilities"]["summary"] == (
    "Shared capability surface for comparison boundaries, strategy schema discovery, collection query discovery, "
    "provenance semantics, operational run controls, machine-readable policy enforcement, and surface-level "
    "enforcement rules."
  )
  assert shared_contracts["schema:run-surface-capabilities"]["version"] == "run-surface-capabilities.v14"
  assert shared_contracts["schema:run-surface-capabilities"]["schema_detail"] == {
    "comparison_eligibility_group_order": [
      "eligible_metrics",
      "supporting_identity",
      "operational_workflow",
      "operational_order_actions",
    ],
    "family_order": [
      "comparison_eligibility",
      "strategy_schema",
      "collection_query",
      "provenance_semantics",
      "execution_controls",
    ],
    "run_subresource_contract_keys": [
      "subresource:orders",
      "subresource:positions",
      "subresource:metrics",
    ],
    "collection_query_contract_keys": [
      "query_collection:run_list",
    ],
  }
  assert shared_contracts["query_collection:run_list"]["contract_kind"] == "query_collection_schema"
  assert shared_contracts["query_collection:run_list"]["schema_detail"]["surface_key"] == "run_list"
  assert shared_contracts["query_collection:run_list"]["related_family_keys"] == ["collection_query"]
  assert shared_contracts["query_collection:run_list"]["schema_detail"]["expression_param"] == "filter_expr"
  assert shared_contracts["query_collection:run_list"]["schema_detail"]["expression_authoring"] == {
    "predicate_refs": {
      "registry_field": "predicates",
      "reference_field": "predicate_ref",
    },
    "predicate_templates": {
      "registry_field": "predicate_templates",
      "template_field": "template",
      "parameters_field": "parameters",
      "bindings_field": "bindings",
      "binding_reference_shape": {
        "binding": "<parameter_name>",
      },
    },
    "collection_nodes": {
      "field": "collection",
      "shape": {
        "path": "<collection path>",
        "path_template": "<collection path template>",
        "bindings": {
          "<parameter_key>": "<value or binding reference>",
        },
        "quantifier": "any|all|none",
      },
    },
  }
  assert shared_contracts["query_collection:run_list"]["schema_detail"]["collection_schemas"][1]["path_template"] == [
    "provenance",
    "market_data_by_symbol",
    "{symbol_key}",
    "issues",
  ]
  assert shared_contracts["query_collection:run_list"]["schema_detail"]["collection_schemas"][1]["parameters"][0]["domain"] == {
    "key": "market_data_symbol_key",
    "source": "run.provenance.market_data_by_symbol",
    "values": ["binance:BTC/USDT"],
    "enum_source": {
      "kind": "dynamic_map_keys",
      "surface_key": "run_list",
      "path": ["provenance", "market_data_by_symbol"],
    },
  }
  assert shared_contracts["query_collection:run_list"]["schema_detail"]["parameter_domains"][0]["domain"] == {
    "key": "market_data_symbol_key",
    "source": "run.provenance.market_data_by_symbol",
    "values": ["binance:BTC/USDT"],
    "enum_source": {
      "kind": "dynamic_map_keys",
      "surface_key": "run_list",
      "path": ["provenance", "market_data_by_symbol"],
    },
  }
  assert shared_contracts["family:collection_query"]["contract_kind"] == "capability_family"
  assert shared_contracts["family:collection_query"]["policy"]["policy_key"] == "typed_collection_query_discovery"
  assert shared_contracts["family:collection_query"]["surface_rules"][2]["surface_key"] == (
    "collection_parameter_domain_pickers"
  )
  assert shared_contracts["family:strategy_schema"]["contract_kind"] == "capability_family"
  assert shared_contracts["family:strategy_schema"]["discovery_flow"] == (
    "Strategy catalog and preset editor schema hints."
  )
  assert shared_contracts["family:strategy_schema"]["policy"]["policy_key"] == (
    "typed_strategy_schema_advertisement"
  )
  assert shared_contracts["family:strategy_schema"]["enforcement"]["level"] == "advisory"
  assert shared_contracts["family:strategy_schema"]["surface_rules"][1]["surface_key"] == (
    "preset_parameter_editor"
  )
  assert "preset_parameter_editor" in shared_contracts["family:strategy_schema"]["member_keys"]
  assert shared_contracts["subresource:metrics"]["contract_kind"] == "run_subresource"
  assert shared_contracts["subresource:metrics"]["member_keys"] == [
    "body:metrics",
    "route:get_run_metrics",
  ]
  assert shared_contracts["subresource:metrics"]["schema_detail"] == {
    "body_key": "metrics",
    "route_path": "/runs/{run_id}/metrics",
    "route_name": "get_run_metrics",
  }
  assert shared_contracts["family:comparison_eligibility"]["title"] == "Comparison boundary contract"
  assert "Run-list metric tiles" in shared_contracts["family:comparison_eligibility"]["ui_surfaces"]
  assert shared_contracts["family:comparison_eligibility"]["policy"]["policy_key"] == (
    "comparison_surface_allowlist"
  )
  assert shared_contracts["family:comparison_eligibility"]["policy"]["policy_mode"] == "allowlist"
  assert "metrics" in shared_contracts["family:comparison_eligibility"]["policy"]["applies_to"]
  assert shared_contracts["family:comparison_eligibility"]["enforcement"]["level"] == "hard_gate"
  assert "run_list_metric_gating" in shared_contracts["family:comparison_eligibility"]["enforcement"][
    "enforcement_points"
  ]
  assert shared_contracts["family:comparison_eligibility"]["surface_rules"][0]["rule_key"] == (
    "run_list_metric_tile_gate"
  )
  assert shared_contracts["family:comparison_eligibility"]["surface_rules"][0]["surface_key"] == (
    "run_list_metric_tiles"
  )
  assert shared_contracts["family:comparison_eligibility"]["surface_rules"][0]["enforcement_mode"] == (
    "eligible_only_drillback"
  )
  assert shared_contracts["family:strategy_schema"]["title"] == "Strategy schema discovery"
  assert "Strategy parameter_schema" in shared_contracts["family:strategy_schema"]["schema_sources"]
  assert shared_contracts["family:strategy_schema"]["policy"]["policy_key"] == (
    "typed_strategy_schema_advertisement"
  )
  assert shared_contracts["family:strategy_schema"]["enforcement"]["level"] == "advisory"
  assert shared_contracts["family:strategy_schema"]["surface_rules"][1]["surface_key"] == (
    "preset_parameter_editor"
  )
  assert payload["comparison_eligibility_contract"]["scope"] == "run_list"
  assert payload["comparison_eligibility_contract"]["surfaces"]["return"]["eligibility"] == "eligible"
  assert payload["comparison_eligibility_contract"]["groups"]["supporting_identity"]["surface_ids"] == [
    "mode",
    "lane",
    "lifecycle",
    "version",
  ]


def test_backtest_endpoint_returns_run_payload(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  create_preset(
    client,
    name="Core 5m",
    preset_id="core_5m",
    strategy_id="ma_cross_v1",
    timeframe="5m",
    benchmark_family="native_validation",
    parameters={"short_window": 5, "long_window": 13},
  )
  response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "tags": ["baseline", "momentum"],
      "preset_id": "core_5m",
      "benchmark_family": "native_validation",
    },
  )
  assert response.status_code == 200
  payload = response.json()
  assert payload["status"] == "completed"
  assert payload["config"]["strategy_id"] == "ma_cross_v1"
  assert payload["provenance"]["strategy"]["strategy_id"] == "ma_cross_v1"
  assert payload["provenance"]["strategy"]["lifecycle"]["stage"] == "active"
  assert payload["provenance"]["strategy"]["parameter_snapshot"]["requested"] == {
    "short_window": 5,
    "long_window": 13,
  }
  assert payload["provenance"]["strategy"]["parameter_snapshot"]["resolved"] == {
    "short_window": 5,
    "long_window": 13,
  }
  assert payload["provenance"]["strategy"]["catalog_semantics"]["strategy_kind"] == "standard"
  assert payload["provenance"]["strategy"]["catalog_semantics"]["parameter_contract"] == ""
  assert payload["provenance"]["strategy"]["warmup"]["required_bars"] == 21
  assert payload["provenance"]["strategy"]["warmup"]["timeframes"] == ["5m"]
  assert "eligibility_contract" not in payload
  assert payload["provenance"]["market_data"]["provider"] == "seeded"
  assert payload["provenance"]["market_data"]["dataset_identity"].startswith("dataset-v1:")
  assert payload["provenance"]["market_data"]["dataset_boundary"]["contract_version"] == "dataset_boundary.v1"
  assert payload["provenance"]["market_data"]["dataset_boundary"]["validation_claim"] == "exact_dataset"
  assert (
    payload["provenance"]["market_data"]["dataset_boundary"]["boundary_id"]
    == payload["provenance"]["market_data"]["dataset_identity"]
  )
  assert payload["provenance"]["market_data"]["sync_checkpoint_id"] is None
  assert payload["provenance"]["market_data"]["reproducibility_state"] == "pinned"
  assert payload["provenance"]["market_data"]["sync_status"] == "fixture"
  assert payload["provenance"]["rerun_boundary_id"].startswith("rerun-v1:")
  assert payload["provenance"]["rerun_boundary_state"] == "pinned"
  assert payload["provenance"]["lineage_summary"]["status"] == "clear"
  assert payload["provenance"]["lineage_summary"]["posture"] == "exact-match"
  assert payload["provenance"]["lineage_summary"]["title"] == "Exact dataset boundary"
  assert payload["provenance"]["lineage_summary"]["category"] == "exact_dataset"
  assert payload["provenance"]["experiment"]["tags"] == ["baseline", "momentum"]
  assert payload["provenance"]["experiment"]["preset_id"] == "core_5m"
  assert payload["provenance"]["experiment"]["benchmark_family"] == "native_validation"
  assert payload["surface_enforcement"]["run_strategy_snapshot"]["enabled"] is True
  assert payload["surface_enforcement"]["compare_selection_workflow"]["enabled"] is True
  assert payload["action_availability"]["compare_select"]["allowed"] is True
  assert payload["action_availability"]["rerun_backtest"]["allowed"] is True
  assert payload["action_availability"]["stop_run"]["allowed"] is False
  assert payload["action_availability"]["stop_run"]["reason"] == (
    "Only sandbox, paper, or live runs can be stopped by the operator."
  )
  assert payload["provenance"]["market_data_by_symbol"]["BTC/USDT"]["provider"] == "seeded"
  assert payload["provenance"]["market_data_by_symbol"]["BTC/USDT"]["dataset_identity"].startswith(
    "candles-v1:"
  )
  assert payload["provenance"]["market_data_by_symbol"]["BTC/USDT"]["dataset_boundary"]["validation_claim"] == (
    "exact_dataset"
  )


def test_backtest_endpoint_applies_surface_rule_contract_to_run_payload(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    app = client.app.state.container.app
    base_capabilities = app.get_run_surface_capabilities()
    app.get_run_surface_capabilities = lambda: without_surface_rule(
      without_surface_rule(
        base_capabilities,
        family_key="provenance_semantics",
        surface_key="run_strategy_snapshot",
      ),
      family_key="execution_controls",
      surface_key="compare_selection_workflow",
    )
    response = client.post(
      "/api/runs/backtests",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "BTC/USDT",
        "timeframe": "5m",
        "initial_cash": 10000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
      },
    )

  assert response.status_code == 200
  payload = response.json()
  assert payload["surface_enforcement"]["run_strategy_snapshot"]["enabled"] is False
  assert payload["surface_enforcement"]["compare_selection_workflow"]["enabled"] is False
  assert payload["provenance"]["strategy"]["catalog_semantics"]["strategy_kind"] == ""
  assert payload["provenance"]["strategy"]["catalog_semantics"]["operator_notes"] == []
  assert payload["action_availability"]["compare_select"]["allowed"] is False
  assert payload["action_availability"]["compare_select"]["reason"] == (
    "Surface rule compare_selection_workflow is disabled by the run-surface capability contract."
  )


def test_backtest_endpoint_rejects_unknown_preset(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "preset_id": "unknown_preset",
    },
  )

  assert response.status_code == 400
  assert response.json()["detail"] == "Preset not found: unknown_preset"


def test_backtest_run_survives_app_restart(tmp_path: Path) -> None:
  database_path = tmp_path / "runs.sqlite3"
  client = build_client(database_path)
  response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert response.status_code == 200
  run_id = response.json()["config"]["run_id"]

  restarted_client = build_client(database_path)
  restarted_response = restarted_client.get(f"/api/runs/backtests/{run_id}")

  assert restarted_response.status_code == 200
  assert restarted_response.json()["config"]["run_id"] == run_id


def test_sandbox_endpoint_returns_run_payload(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  response = client.post(
    "/api/runs/sandbox",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "ETH/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "replay_bars": 48,
    },
  )
  assert response.status_code == 200
  payload = response.json()
  assert payload["status"] == "running"
  assert payload["config"]["mode"] == "sandbox"
  assert payload["notes"][0].startswith("Sandbox worker session primed from the latest market snapshot using ")
  assert payload["provenance"]["runtime_session"]["worker_kind"] == "sandbox_native_worker"
  assert payload["provenance"]["runtime_session"]["lifecycle_state"] == "active"
  assert payload["provenance"]["runtime_session"]["primed_candle_count"] == 48
  assert payload["provenance"]["runtime_session"]["processed_tick_count"] == 1
  assert payload["provenance"]["runtime_session"]["recovery_count"] == 0
  assert (
    payload["provenance"]["runtime_session"]["last_processed_candle_at"]
    == payload["provenance"]["market_data"]["effective_end_at"]
  )
  assert (
    payload["provenance"]["runtime_session"]["last_seen_candle_at"]
    == payload["provenance"]["market_data"]["effective_end_at"]
  )


def test_paper_alias_still_works(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  response = client.post(
    "/api/runs/paper",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "ETH/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "replay_bars": 24,
    },
  )
  assert response.status_code == 200
  payload = response.json()
  assert payload["config"]["mode"] == "paper"
  assert payload["notes"][0].startswith("Paper session primed from the latest market snapshot using ")
  assert all("Sandbox preview replayed" not in note for note in payload["notes"])
  assert payload["provenance"]["runtime_session"] is None


def test_sandbox_worker_recovers_running_session_after_app_restart(tmp_path: Path) -> None:
  database_path = tmp_path / "runs.sqlite3"

  with build_client(database_path) as first_client:
    response = first_client.post(
      "/api/runs/sandbox",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
      },
    )
    assert response.status_code == 200
    run_id = response.json()["config"]["run_id"]

  with build_client(database_path) as restarted_client:
    restarted_response = restarted_client.get(f"/api/runs/backtests/{run_id}")

  assert restarted_response.status_code == 200
  payload = restarted_response.json()
  assert payload["config"]["mode"] == "sandbox"
  assert payload["provenance"]["runtime_session"]["recovery_count"] >= 1
  assert payload["provenance"]["runtime_session"]["last_recovery_reason"] == "process_restart"
  assert payload["provenance"]["runtime_session"]["processed_tick_count"] == 1
  assert any("sandbox_worker_recovered | process_restart" in note for note in payload["notes"])


def test_market_data_status_endpoint_returns_status_payload(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  response = client.get("/api/market-data/status")

  assert response.status_code == 200
  payload = response.json()
  assert payload["provider"] == "seeded"
  assert payload["instruments"]
  assert "sync_status" in payload["instruments"][0]
  assert payload["instruments"][0]["sync_checkpoint"] is None
  assert payload["instruments"][0]["recent_failures"] == []
  assert payload["instruments"][0]["failure_count_24h"] == 0
  assert payload["instruments"][0]["backfill_target_candles"] is None
  assert payload["instruments"][0]["backfill_completion_ratio"] is None
  assert payload["instruments"][0]["backfill_complete"] is None
  assert payload["instruments"][0]["backfill_contiguous_completion_ratio"] is None
  assert payload["instruments"][0]["backfill_contiguous_complete"] is None
  assert payload["instruments"][0]["backfill_contiguous_missing_candles"] is None
  assert payload["instruments"][0]["backfill_gap_windows"] == []


def test_market_data_status_endpoint_includes_gap_window_ids(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    app = client.app.state.container.app
    market_data = StatusOverrideSeededMarketDataAdapter()
    market_data.set_status(
      timeframe="5m",
      status=MarketDataStatus(
        provider="binance",
        venue="binance",
        instruments=[
          InstrumentStatus(
            instrument_id="binance:ETH/USDT",
            timeframe="5m",
            candle_count=120,
            first_timestamp=datetime(2025, 1, 3, 0, 0, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 9, 55, tzinfo=UTC),
            sync_status="lagging",
            lag_seconds=300,
            last_sync_at=datetime(2025, 1, 3, 10, 0, tzinfo=UTC),
            backfill_contiguous_missing_candles=2,
            backfill_gap_windows=(
              GapWindow(
                start_at=datetime(2025, 1, 3, 8, 0, tzinfo=UTC),
                end_at=datetime(2025, 1, 3, 8, 5, tzinfo=UTC),
                missing_candles=2,
                gap_window_id="gw|0|2025-01-03T08:00:00+00:00|2025-01-03T08:05:00+00:00|2",
              ),
            ),
          ),
        ],
      ),
    )
    app._market_data = market_data

    response = client.get("/api/market-data/status")

  assert response.status_code == 200
  payload = response.json()
  assert payload["instruments"][0]["backfill_gap_windows"][0]["gap_window_id"].startswith("gw|0|")


def test_market_data_lineage_history_endpoint_returns_normalized_records(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    app = client.app.state.container.app
    market_data = StatusOverrideSeededMarketDataAdapter()
    market_data.set_lineage_history(
      (
        MarketDataLineageHistoryRecord(
          history_id="lineage-2",
          source_job_id="job-2",
          provider="binance",
          venue="binance",
          symbol="BTC/USDT",
          timeframe="5m",
          recorded_at=datetime(2025, 1, 3, 10, 0, tzinfo=UTC),
          sync_status="error",
          validation_claim="checkpoint_window",
          reproducibility_state="range_only",
          boundary_id="checkpoint-v1:binance:BTC/USDT:5m:2025-01-03T09:55:00+00:00",
          checkpoint_id="checkpoint-v1:binance:BTC/USDT:5m:2025-01-03T09:55:00+00:00",
          dataset_boundary=DatasetBoundaryContract(
            provider="binance",
            venue="binance",
            symbols=("BTC/USDT",),
            timeframe="5m",
            reproducibility_state="range_only",
            validation_claim="checkpoint_window",
            boundary_id="checkpoint-v1:binance:BTC/USDT:5m:2025-01-03T09:55:00+00:00",
            sync_checkpoint_id="checkpoint-v1:binance:BTC/USDT:5m:2025-01-03T09:55:00+00:00",
            effective_start_at=datetime(2025, 1, 3, 0, 0, tzinfo=UTC),
            effective_end_at=datetime(2025, 1, 3, 9, 55, tzinfo=UTC),
            candle_count=120,
          ),
          first_timestamp=datetime(2025, 1, 3, 0, 0, tzinfo=UTC),
          last_timestamp=datetime(2025, 1, 3, 9, 55, tzinfo=UTC),
          candle_count=120,
          lag_seconds=300,
          last_sync_at=datetime(2025, 1, 3, 10, 0, tzinfo=UTC),
          failure_count_24h=2,
          contiguous_missing_candles=2,
          gap_window_count=1,
          last_error="upstream fetch failed",
          issues=("last_sync_failed", "gap_windows:1"),
        ),
        MarketDataLineageHistoryRecord(
          history_id="lineage-1",
          source_job_id="job-1",
          provider="binance",
          venue="binance",
          symbol="ETH/USDT",
          timeframe="5m",
          recorded_at=datetime(2025, 1, 3, 9, 0, tzinfo=UTC),
          sync_status="synced",
          validation_claim="checkpoint_window",
          reproducibility_state="range_only",
          boundary_id="checkpoint-v1:binance:ETH/USDT:5m:2025-01-03T08:55:00+00:00",
          checkpoint_id="checkpoint-v1:binance:ETH/USDT:5m:2025-01-03T08:55:00+00:00",
          dataset_boundary=DatasetBoundaryContract(
            provider="binance",
            venue="binance",
            symbols=("ETH/USDT",),
            timeframe="5m",
            reproducibility_state="range_only",
            validation_claim="checkpoint_window",
            boundary_id="checkpoint-v1:binance:ETH/USDT:5m:2025-01-03T08:55:00+00:00",
            sync_checkpoint_id="checkpoint-v1:binance:ETH/USDT:5m:2025-01-03T08:55:00+00:00",
            effective_start_at=datetime(2025, 1, 3, 0, 0, tzinfo=UTC),
            effective_end_at=datetime(2025, 1, 3, 8, 55, tzinfo=UTC),
            candle_count=108,
          ),
          first_timestamp=datetime(2025, 1, 3, 0, 0, tzinfo=UTC),
          last_timestamp=datetime(2025, 1, 3, 8, 55, tzinfo=UTC),
          candle_count=108,
          lag_seconds=0,
          last_sync_at=datetime(2025, 1, 3, 9, 0, tzinfo=UTC),
          failure_count_24h=0,
          contiguous_missing_candles=0,
          gap_window_count=0,
          last_error=None,
          issues=(),
        ),
      )
    )
    app._market_data = market_data

    response = client.get(
      "/api/market-data/lineage-history?timeframe=5m&sync_status=error&sort=recorded_at:desc"
    )

  assert response.status_code == 200
  payload = response.json()
  assert len(payload) == 1
  assert payload[0]["history_id"] == "lineage-2"
  assert payload[0]["dataset_boundary"]["validation_claim"] == "checkpoint_window"
  assert payload[0]["failure_count_24h"] == 2
  assert payload[0]["issues"] == ["last_sync_failed", "gap_windows:1"]


def test_market_data_ingestion_jobs_endpoint_filters_failed_jobs(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    app = client.app.state.container.app
    market_data = StatusOverrideSeededMarketDataAdapter()
    market_data.set_ingestion_jobs(
      (
        MarketDataIngestionJobRecord(
          job_id="job-2",
          provider="binance",
          venue="binance",
          symbol="BTC/USDT",
          timeframe="5m",
          operation="sync_recent",
          status="failed",
          started_at=datetime(2025, 1, 3, 10, 0, tzinfo=UTC),
          finished_at=datetime(2025, 1, 3, 10, 0, 1, tzinfo=UTC),
          duration_ms=1000,
          fetched_candle_count=0,
          validation_claim="checkpoint_window",
          boundary_id="checkpoint-v1:binance:BTC/USDT:5m:2025-01-03T09:55:00+00:00",
          checkpoint_id="checkpoint-v1:binance:BTC/USDT:5m:2025-01-03T09:55:00+00:00",
          lineage_history_id="lineage-2",
          requested_start_at=datetime(2025, 1, 3, 10, 0, tzinfo=UTC),
          requested_end_at=None,
          requested_limit=500,
          last_error="upstream fetch failed",
        ),
        MarketDataIngestionJobRecord(
          job_id="job-1",
          provider="binance",
          venue="binance",
          symbol="BTC/USDT",
          timeframe="5m",
          operation="backfill_history",
          status="succeeded",
          started_at=datetime(2025, 1, 3, 9, 0, tzinfo=UTC),
          finished_at=datetime(2025, 1, 3, 9, 0, 2, tzinfo=UTC),
          duration_ms=2000,
          fetched_candle_count=96,
          validation_claim="checkpoint_window",
          boundary_id="checkpoint-v1:binance:BTC/USDT:5m:2025-01-03T08:55:00+00:00",
          checkpoint_id="checkpoint-v1:binance:BTC/USDT:5m:2025-01-03T08:55:00+00:00",
          lineage_history_id="lineage-1",
          requested_start_at=datetime(2025, 1, 3, 1, 0, tzinfo=UTC),
          requested_end_at=datetime(2025, 1, 3, 8, 55, tzinfo=UTC),
          requested_limit=96,
          last_error=None,
        ),
      )
    )
    app._market_data = market_data

    response = client.get("/api/market-data/ingestion-jobs?status=failed&sort=started_at:desc")

  assert response.status_code == 200
  payload = response.json()
  assert len(payload) == 1
  assert payload[0]["job_id"] == "job-2"
  assert payload[0]["operation"] == "sync_recent"
  assert payload[0]["status"] == "failed"
  assert payload[0]["lineage_history_id"] == "lineage-2"
  assert payload[0]["last_error"] == "upstream fetch failed"


def test_operator_visibility_endpoint_reports_stale_runtime_alerts(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    app = client.app.state.container.app
    clock = lambda: datetime(2025, 1, 3, 13, 0, tzinfo=UTC)
    app._clock = clock
    app._sandbox_worker_heartbeat_timeout_seconds = 15
    app.start_sandbox_run(
      strategy_id="ma_cross_v1",
      symbol="ETH/USDT",
      timeframe="5m",
      initial_cash=10_000,
      fee_rate=0.001,
      slippage_bps=3,
      parameters={},
      replay_bars=24,
    )
    app._clock = lambda: datetime(2025, 1, 3, 13, 0, 20, tzinfo=UTC)

    response = client.get("/api/operator/visibility")

  assert response.status_code == 200
  payload = response.json()
  assert payload["alerts"][0]["category"] == "stale_runtime"
  assert payload["alerts"][0]["severity"] == "warning"
  assert payload["alerts"][0]["symbol"] == "ETH/USDT"
  assert payload["alerts"][0]["symbols"] == ["ETH/USDT"]
  assert payload["alerts"][0]["timeframe"] == "5m"
  assert payload["audit_events"][0]["kind"] == "sandbox_worker_stale"


def test_operator_visibility_endpoint_reports_worker_failures(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    app = client.app.state.container.app
    app.start_sandbox_run(
      strategy_id="ma_cross_v1",
      symbol="ETH/USDT",
      timeframe="5m",
      initial_cash=10_000,
      fee_rate=0.001,
      slippage_bps=3,
      parameters={},
      replay_bars=24,
    )

    def fail_worker(*, run):
      raise RuntimeError("worker crash")

    app._load_sandbox_worker_candles = fail_worker
    app.maintain_sandbox_worker_sessions()

    response = client.get("/api/operator/visibility")

  assert response.status_code == 200
  payload = response.json()
  assert payload["alerts"][0]["category"] == "worker_failure"
  assert payload["alerts"][0]["severity"] == "critical"
  assert payload["alerts"][0]["symbol"] == "ETH/USDT"
  assert payload["alerts"][0]["symbols"] == ["ETH/USDT"]
  assert payload["alerts"][0]["timeframe"] == "5m"
  assert any(event["kind"] == "sandbox_worker_failed" for event in payload["audit_events"])


def test_operator_visibility_endpoint_reports_provider_provenance_scheduler_lag(
  tmp_path: Path,
) -> None:
  class FakeSchedulerExportDeliveryAdapter:
    def __init__(self) -> None:
      self.deliveries: list[tuple[str, tuple[str, ...], str]] = []

    def list_targets(self) -> tuple[str, ...]:
      return ("slack_webhook", "pagerduty_events")

    def list_supported_workflow_providers(self) -> tuple[str, ...]:
      return ("pagerduty",)

    def deliver(
      self,
      *,
      incident: OperatorIncidentEvent,
      targets: tuple[str, ...] | None = None,
      attempt_number: int = 1,
      phase: str = "initial",
    ) -> tuple[OperatorIncidentDelivery, ...]:
      resolved_targets = tuple(targets or ())
      self.deliveries.append((incident.alert_id, resolved_targets, phase))
      attempted_at = incident.timestamp
      return tuple(
        OperatorIncidentDelivery(
          delivery_id=f"{target}:{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=target,
          status="delivered",
          attempted_at=attempted_at,
          detail=f"Delivered to {target}",
          attempt_number=attempt_number,
          phase=phase,
          source=incident.source,
        )
        for target in resolved_targets
      )

    def sync_incident_workflow(
      self,
      *,
      incident: OperatorIncidentEvent,
      provider: str,
      action: str,
      actor: str,
      detail: str,
      payload: dict[str, Any] | None = None,
      attempt_number: int = 1,
    ) -> tuple[OperatorIncidentDelivery, ...]:
      return ()

    def pull_incident_workflow_state(
      self,
      *,
      incident: OperatorIncidentEvent,
      provider: str,
    ) -> OperatorIncidentProviderPullSync | None:
      return None

  with build_client(
    tmp_path / "runs.sqlite3",
    provider_provenance_report_scheduler_enabled=False,
  ) as client:
    app = client.app.state.container.app
    app._operator_alert_delivery = FakeSchedulerExportDeliveryAdapter()
    fixed_time = datetime(2026, 4, 22, 10, 0, tzinfo=UTC)
    app._clock = lambda: fixed_time
    app._provider_provenance_report_scheduler_interval_seconds = 60
    app._provider_provenance_report_scheduler_batch_limit = 1
    app._provider_provenance_scheduler_health_records = {}
    app._provider_provenance_scheduler_health = ProviderProvenanceSchedulerHealth(
      generated_at=fixed_time,
      enabled=True,
      status="starting",
      summary="Background scheduler has not completed a provider provenance automation cycle yet.",
      interval_seconds=60,
      batch_limit=1,
    )

    report_a = app.create_provider_provenance_scheduled_report(name="Drift watch A")
    report_b = app.create_provider_provenance_scheduled_report(name="Drift watch B")
    overdue_at = fixed_time - timedelta(minutes=10)
    app._save_provider_provenance_scheduled_report_record(
      replace(report_a, next_run_at=overdue_at)
    )
    app._save_provider_provenance_scheduled_report_record(
      replace(report_b, next_run_at=overdue_at)
    )
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )

    response = client.get("/api/operator/visibility")
    shared_exports_response = client.get(
      "/api/operator/provider-provenance-exports",
      params={
        "export_scope": "provider_provenance_scheduler_health",
        "requested_by_tab_id": "system:provider-provenance-scheduler-alerts",
        "limit": 10,
      },
    )

  assert response.status_code == 200
  payload = response.json()
  assert payload["provider_provenance_scheduler"]["status"] == "lagging"
  assert payload["provider_provenance_scheduler"]["due_report_count"] == 1
  assert payload["provider_provenance_scheduler"]["alert_workflow_state"] == "escalated_delivered"
  assert payload["provider_provenance_scheduler"]["alert_workflow_job_id"] is not None
  lag_alert = next(
    alert for alert in payload["alerts"]
    if alert["category"] == "scheduler_lag"
  )
  assert lag_alert["severity"] == "critical"
  assert any(
    event["kind"] == "provider_provenance_scheduler_lagging"
    for event in payload["audit_events"]
  )
  assert shared_exports_response.status_code == 200
  shared_exports_payload = shared_exports_response.json()
  assert shared_exports_payload["total"] == 1
  assert shared_exports_payload["items"][0]["job_id"] == (
    payload["provider_provenance_scheduler"]["alert_workflow_job_id"]
  )
  assert shared_exports_payload["items"][0]["last_escalation_reason"] == "scheduler_lag_auto_export"


def test_operator_visibility_endpoint_reconstructs_historical_scheduler_export_for_resolved_alert(
  tmp_path: Path,
) -> None:
  with build_client(
    tmp_path / "runs.sqlite3",
    provider_provenance_report_scheduler_enabled=False,
  ) as client:
    app = client.app.state.container.app
    fixed_time = datetime(2026, 4, 22, 10, 0, tzinfo=UTC)
    app._clock = lambda: fixed_time
    app._provider_provenance_report_scheduler_interval_seconds = 60
    app._provider_provenance_report_scheduler_batch_limit = 1
    app._provider_provenance_scheduler_health_records = {}
    app._provider_provenance_scheduler_health = ProviderProvenanceSchedulerHealth(
      generated_at=fixed_time,
      enabled=True,
      status="starting",
      summary="Background scheduler has not completed a provider provenance automation cycle yet.",
      interval_seconds=60,
      batch_limit=1,
    )

    report_a = app.create_provider_provenance_scheduled_report(name="Drift watch A")
    report_b = app.create_provider_provenance_scheduled_report(name="Drift watch B")
    overdue_at = fixed_time - timedelta(minutes=10)
    app._save_provider_provenance_scheduled_report_record(
      replace(report_a, next_run_at=overdue_at)
    )
    app._save_provider_provenance_scheduled_report_record(
      replace(report_b, next_run_at=overdue_at)
    )
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )
    active_visibility_response = client.get("/api/operator/visibility")
    fixed_time = fixed_time + timedelta(minutes=1)
    app._clock = lambda: fixed_time
    for record in app.list_provider_provenance_scheduled_reports(limit=10):
      app._save_provider_provenance_scheduled_report_record(
        replace(record, next_run_at=fixed_time + timedelta(days=7))
      )
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )
    fixed_time = fixed_time + timedelta(minutes=1)
    app._clock = lambda: fixed_time
    for record in app.list_provider_provenance_scheduled_reports(limit=10):
      app._save_provider_provenance_scheduled_report_record(
        replace(record, next_run_at=fixed_time - timedelta(minutes=10))
      )
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )
    fixed_time = fixed_time + timedelta(minutes=1)
    app._clock = lambda: fixed_time
    for record in app.list_provider_provenance_scheduled_reports(limit=10):
      app._save_provider_provenance_scheduled_report_record(
        replace(record, next_run_at=fixed_time + timedelta(days=7))
      )
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )

    visibility_response = client.get("/api/operator/visibility")
    resolved_alerts = [
      alert
      for alert in visibility_response.json()["alert_history"]
      if alert["category"] == "scheduler_lag" and alert["status"] == "resolved"
    ]
    assert len(resolved_alerts) == 2
    assert len({alert["occurrence_id"] for alert in resolved_alerts}) == 2
    assert [alert["timeline_position"] for alert in sorted(resolved_alerts, key=lambda alert: alert["detected_at"])] == [1, 2]
    resolved_alert = min(
      resolved_alerts,
      key=lambda alert: alert["detected_at"],
    )
    reconstruct_response = client.post(
      "/api/operator/provider-provenance-analytics/scheduler-health/reconstruct-export",
      json={
        "alert_category": resolved_alert["category"],
        "detected_at": resolved_alert["detected_at"],
        "resolved_at": resolved_alert["resolved_at"],
        "format": "json",
        "history_limit": 8,
        "drilldown_history_limit": 12,
      },
    )

  assert active_visibility_response.status_code == 200
  assert visibility_response.status_code == 200
  assert reconstruct_response.status_code == 200
  payload = reconstruct_response.json()
  assert payload["format"] == "json"
  reconstructed = json.loads(payload["content"])
  assert reconstructed["reconstruction"]["mode"] == "resolved_alert_row"
  assert reconstructed["reconstruction"]["alert_category"] == "scheduler_lag"
  assert reconstructed["current"]["status"] == "lagging"
  assert reconstructed["history_page"]["total"] >= 1
  assert reconstructed["analytics"]["query"]["reconstruction_mode"] == "resolved_alert_row"
  assert datetime.fromisoformat(
    reconstructed["analytics"]["query"]["alert_detected_at"]
  ) == datetime.fromisoformat(resolved_alert["detected_at"].replace("Z", "+00:00"))


def test_operator_provider_provenance_scheduler_alert_history_endpoint_paginates_occurrences(
  tmp_path: Path,
) -> None:
  with build_client(
    tmp_path / "runs.sqlite3",
    provider_provenance_report_scheduler_enabled=False,
  ) as client:
    app = client.app.state.container.app
    fixed_time = datetime(2026, 4, 22, 11, 0, tzinfo=UTC)
    app._clock = lambda: fixed_time
    app._provider_provenance_report_scheduler_interval_seconds = 60
    app._provider_provenance_report_scheduler_batch_limit = 1
    app._provider_provenance_scheduler_health_records = {}
    app._provider_provenance_scheduler_health = ProviderProvenanceSchedulerHealth(
      generated_at=fixed_time,
      enabled=True,
      status="starting",
      summary="Background scheduler has not completed a provider provenance automation cycle yet.",
      interval_seconds=60,
      batch_limit=1,
    )

    report_a = app.create_provider_provenance_scheduled_report(name="Timeline A")
    report_b = app.create_provider_provenance_scheduled_report(name="Timeline B")
    overdue_at = fixed_time - timedelta(minutes=10)
    app._save_provider_provenance_scheduled_report_record(replace(report_a, next_run_at=overdue_at))
    app._save_provider_provenance_scheduled_report_record(replace(report_b, next_run_at=overdue_at))

    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )
    fixed_time = fixed_time + timedelta(minutes=1)
    app._clock = lambda: fixed_time
    for record in app.list_provider_provenance_scheduled_reports(limit=10):
      app._save_provider_provenance_scheduled_report_record(
        replace(record, next_run_at=fixed_time + timedelta(days=7))
      )
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )
    fixed_time = fixed_time + timedelta(minutes=1)
    app._clock = lambda: fixed_time
    for record in app.list_provider_provenance_scheduled_reports(limit=10):
      app._save_provider_provenance_scheduled_report_record(
        replace(record, next_run_at=fixed_time - timedelta(minutes=10))
      )
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )
    fixed_time = fixed_time + timedelta(minutes=1)
    app._clock = lambda: fixed_time
    for record in app.list_provider_provenance_scheduled_reports(limit=10):
      app._save_provider_provenance_scheduled_report_record(
        replace(record, next_run_at=fixed_time + timedelta(days=7))
      )
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )

    first_page_response = client.get(
      "/api/operator/provider-provenance-analytics/scheduler-alerts",
      params={"category": "scheduler_lag", "status": "resolved", "limit": 1, "offset": 0},
    )
    second_page_response = client.get(
      "/api/operator/provider-provenance-analytics/scheduler-alerts",
      params={"category": "scheduler_lag", "status": "resolved", "limit": 1, "offset": 1},
    )
    narrative_page_response = client.get(
      "/api/operator/provider-provenance-analytics/scheduler-alerts",
      params={"category": "scheduler_lag", "narrative_facet": "post_resolution_recovery", "limit": 10, "offset": 0},
    )

  assert first_page_response.status_code == 200
  first_page_payload = first_page_response.json()
  assert first_page_payload["query"]["category"] == "scheduler_lag"
  assert first_page_payload["query"]["status"] == "resolved"
  assert first_page_payload["summary"]["total_occurrences"] == 2
  assert first_page_payload["returned"] == 1
  assert first_page_payload["next_offset"] == 1
  assert first_page_payload["items"][0]["timeline_position"] == 2
  assert first_page_payload["items"][0]["timeline_total"] == 2

  assert second_page_response.status_code == 200
  second_page_payload = second_page_response.json()
  assert second_page_payload["returned"] == 1
  assert second_page_payload["previous_offset"] == 0
  assert second_page_payload["items"][0]["timeline_position"] == 1

  assert narrative_page_response.status_code == 200
  narrative_page_payload = narrative_page_response.json()
  assert narrative_page_payload["query"]["narrative_facet"] == "post_resolution_recovery"
  assert narrative_page_payload["returned"] >= 1
  assert all(
    item["narrative"]["has_post_resolution_history"]
    for item in narrative_page_payload["items"]
  )


def test_operator_visibility_endpoint_can_reconstruct_mixed_status_scheduler_narrative(
  tmp_path: Path,
) -> None:
  with build_client(
    tmp_path / "runs.sqlite3",
    provider_provenance_report_scheduler_enabled=False,
  ) as client:
    app = client.app.state.container.app
    fixed_time = datetime(2026, 4, 22, 12, 0, tzinfo=UTC)
    app._clock = lambda: fixed_time
    app._provider_provenance_report_scheduler_interval_seconds = 60
    app._provider_provenance_report_scheduler_batch_limit = 1
    app._provider_provenance_scheduler_health_records = {}
    app._provider_provenance_scheduler_health = ProviderProvenanceSchedulerHealth(
      generated_at=fixed_time,
      enabled=True,
      status="starting",
      summary="Background scheduler has not completed a provider provenance automation cycle yet.",
      interval_seconds=60,
      batch_limit=1,
    )

    report_a = app.create_provider_provenance_scheduled_report(name="Narrative A")
    report_b = app.create_provider_provenance_scheduled_report(name="Narrative B")
    overdue_at = fixed_time - timedelta(minutes=10)
    app._save_provider_provenance_scheduled_report_record(replace(report_a, next_run_at=overdue_at))
    app._save_provider_provenance_scheduled_report_record(replace(report_b, next_run_at=overdue_at))

    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )
    fixed_time = fixed_time + timedelta(minutes=1)
    app._clock = lambda: fixed_time
    for record in app.list_provider_provenance_scheduled_reports(limit=10):
      app._save_provider_provenance_scheduled_report_record(
        replace(record, next_run_at=fixed_time + timedelta(days=7))
      )
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )
    fixed_time = fixed_time + timedelta(minutes=1)
    app._clock = lambda: fixed_time
    for record in app.list_provider_provenance_scheduled_reports(limit=10):
      app._save_provider_provenance_scheduled_report_record(
        replace(record, next_run_at=fixed_time - timedelta(minutes=10))
      )
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )
    fixed_time = fixed_time + timedelta(minutes=1)
    app._clock = lambda: fixed_time
    for record in app.list_provider_provenance_scheduled_reports(limit=10):
      app._save_provider_provenance_scheduled_report_record(
        replace(record, next_run_at=fixed_time + timedelta(days=7))
      )
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )

    resolved_alert = min(
      (
        alert
        for alert in client.get("/api/operator/visibility").json()["alert_history"]
        if alert["category"] == "scheduler_lag" and alert["status"] == "resolved"
      ),
      key=lambda alert: alert["detected_at"],
    )
    reconstruct_response = client.post(
      "/api/operator/provider-provenance-analytics/scheduler-health/reconstruct-export",
      json={
        "alert_category": resolved_alert["category"],
        "detected_at": resolved_alert["detected_at"],
        "resolved_at": resolved_alert["resolved_at"],
        "narrative_mode": "mixed_status_post_resolution",
        "format": "json",
        "history_limit": 8,
        "drilldown_history_limit": 12,
      },
    )

  assert reconstruct_response.status_code == 200
  payload = reconstruct_response.json()
  reconstructed = json.loads(payload["content"])
  assert reconstructed["reconstruction"]["mode"] == "resolved_alert_row"
  assert reconstructed["reconstruction"]["narrative_mode"] == "mixed_status_post_resolution"
  assert reconstructed["current"]["status"] == "healthy"
  assert reconstructed["history_page"]["total"] == 2
  assert reconstructed["mixed_status_narrative"]["post_resolution_history"]["items"][0]["status"] == "healthy"
  assert reconstructed["analytics"]["query"]["narrative_mode"] == "mixed_status_post_resolution"


def test_provider_provenance_scheduler_health_endpoints_expose_history_and_trends(
  monkeypatch,
  tmp_path: Path,
) -> None:
  class FakeSchedulerExportDeliveryAdapter:
    def __init__(self) -> None:
      self.deliveries: list[tuple[str, tuple[str, ...], str]] = []

    def list_targets(self) -> tuple[str, ...]:
      return ("slack_webhook", "pagerduty_events")

    def list_supported_workflow_providers(self) -> tuple[str, ...]:
      return ("pagerduty",)

    def deliver(self, *, incident, targets=None, attempt_number: int = 1, phase: str = "initial"):
      resolved_targets = tuple(targets or self.list_targets())
      self.deliveries.append((incident.alert_id, resolved_targets, phase))
      return tuple(
        OperatorIncidentDelivery(
          delivery_id=f"{incident.event_id}:{target}:attempt-{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=target,
          status="delivered",
          attempted_at=incident.timestamp,
          detail=f"fake_delivery:{target}",
          attempt_number=attempt_number,
          phase=phase,
          external_provider="pagerduty" if target == "pagerduty_events" else None,
          external_reference=incident.external_reference,
          source=incident.source,
        )
        for target in resolved_targets
      )

    def sync_incident_workflow(self, **kwargs):
      return ()

    def pull_incident_workflow_state(self, **kwargs):
      return None

  with build_client(
    tmp_path / "runs.sqlite3",
    provider_provenance_report_scheduler_enabled=False,
  ) as client:
    app = client.app.state.container.app
    delivery = FakeSchedulerExportDeliveryAdapter()
    app._operator_alert_delivery = delivery
    fixed_time = datetime(2026, 4, 22, 10, 0, tzinfo=UTC)
    app._clock = lambda: fixed_time
    app._provider_provenance_report_scheduler_interval_seconds = 60
    app._provider_provenance_report_scheduler_batch_limit = 1
    app._provider_provenance_scheduler_health_records = {}
    app._provider_provenance_scheduler_health = ProviderProvenanceSchedulerHealth(
      generated_at=fixed_time,
      enabled=True,
      status="starting",
      summary="Background scheduler has not completed a provider provenance automation cycle yet.",
      interval_seconds=60,
      batch_limit=1,
    )

    report_a = app.create_provider_provenance_scheduled_report(name="Drift watch A")
    report_b = app.create_provider_provenance_scheduled_report(name="Drift watch B")
    overdue_at = fixed_time - timedelta(minutes=10)
    app._save_provider_provenance_scheduled_report_record(replace(report_a, next_run_at=overdue_at))
    app._save_provider_provenance_scheduled_report_record(replace(report_b, next_run_at=overdue_at))

    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )
    for record in app.list_provider_provenance_scheduled_reports(limit=10):
      app._save_provider_provenance_scheduled_report_record(
        replace(record, next_run_at=fixed_time + timedelta(days=7))
      )
    fixed_time = fixed_time + timedelta(days=1)
    app._clock = lambda: fixed_time
    app.execute_provider_provenance_scheduler_cycle(
      source_tab_id="system:provider-provenance-scheduler",
      source_tab_label="Background scheduler",
    )
    fixed_time = fixed_time + timedelta(days=1)
    app._clock = lambda: fixed_time

    def fail_scheduler(*args, **kwargs):
      raise RuntimeError("scheduler crash")

    monkeypatch.setattr(app, "run_due_provider_provenance_scheduled_reports", fail_scheduler)
    try:
      app.execute_provider_provenance_scheduler_cycle(
        source_tab_id="system:provider-provenance-scheduler",
        source_tab_label="Background scheduler",
      )
    except RuntimeError:
      pass
    else:
      raise AssertionError("expected scheduler failure to be recorded")

    history_response = client.get(
      "/api/operator/provider-provenance-analytics/scheduler-health",
      params={"limit": 2, "offset": 1},
    )
    analytics_response = client.get(
      "/api/operator/provider-provenance-analytics/scheduler-health/analytics",
      params={
        "window_days": 3,
        "history_limit": 5,
        "drilldown_bucket_key": "2026-04-22",
        "drilldown_history_limit": 2,
      },
    )
    export_response = client.get(
      "/api/operator/provider-provenance-analytics/scheduler-health/export",
      params={
        "window_days": 3,
        "history_limit": 5,
        "drilldown_bucket_key": "2026-04-22",
        "drilldown_history_limit": 2,
        "limit": 2,
        "offset": 0,
        "format": "json",
      },
    )
    csv_export_response = client.get(
      "/api/operator/provider-provenance-analytics/scheduler-health/export",
      params={"limit": 2, "offset": 1, "format": "csv"},
    )
    shared_export_create_response = client.post(
      "/api/operator/provider-provenance-exports",
      json={
        "content": export_response.json()["content"],
        "requested_by_tab_id": "tab_scheduler",
        "requested_by_tab_label": "Scheduler panel",
      },
    )
    shared_export_list_response = client.get(
      "/api/operator/provider-provenance-exports",
      params={"export_scope": "provider_provenance_scheduler_health", "limit": 10},
    )
    shared_export_policy_response = client.post(
      f"/api/operator/provider-provenance-exports/{shared_export_create_response.json()['job_id']}/policy",
      json={
        "actor": "operator",
        "routing_policy_id": "paging_only",
        "approval_policy_id": "manual_required",
        "source_tab_id": "tab_scheduler",
        "source_tab_label": "Scheduler panel",
      },
    )
    shared_export_unapproved_escalate_response = client.post(
      f"/api/operator/provider-provenance-exports/{shared_export_create_response.json()['job_id']}/escalate",
      json={
        "actor": "operator",
        "reason": "scheduler_health_export_review",
        "source_tab_id": "tab_scheduler",
        "source_tab_label": "Scheduler panel",
      },
    )
    shared_export_approval_response = client.post(
      f"/api/operator/provider-provenance-exports/{shared_export_create_response.json()['job_id']}/approval",
      json={
        "actor": "operator",
        "note": "manager_review_complete",
        "source_tab_id": "tab_scheduler",
        "source_tab_label": "Scheduler panel",
      },
    )
    shared_export_escalate_response = client.post(
      f"/api/operator/provider-provenance-exports/{shared_export_create_response.json()['job_id']}/escalate",
      json={
        "actor": "operator",
        "reason": "scheduler_health_export_review",
        "source_tab_id": "tab_scheduler",
        "source_tab_label": "Scheduler panel",
      },
    )
    shared_export_history_response = client.get(
      f"/api/operator/provider-provenance-exports/{shared_export_create_response.json()['job_id']}/history",
    )

  assert history_response.status_code == 200
  history_payload = history_response.json()
  assert history_payload["current"]["status"] == "failed"
  assert history_payload["query"]["offset"] == 1
  assert history_payload["returned"] == 2
  assert history_payload["next_offset"] is None
  assert history_payload["previous_offset"] == 0
  assert [entry["status"] for entry in history_payload["items"]] == ["healthy", "lagging"]

  assert analytics_response.status_code == 200
  analytics_payload = analytics_response.json()
  assert analytics_payload["totals"]["record_count"] == 3
  assert analytics_payload["totals"]["peak_lag_seconds"] == 600
  assert analytics_payload["time_series"]["health_status"]["summary"]["latest_status"] == "failed"
  assert analytics_payload["time_series"]["lag_trend"]["summary"]["peak_lag_seconds"] == 600
  assert analytics_payload["drill_down"]["bucket_key"] == "2026-04-22"
  assert analytics_payload["drill_down"]["bucket_size"] == "hour"
  assert analytics_payload["drill_down"]["history_limit"] == 2
  assert analytics_payload["recent_history"][0]["status"] == "failed"

  assert export_response.status_code == 200
  export_payload = export_response.json()
  assert export_payload["format"] == "json"
  assert export_payload["record_count"] == 2
  assert export_payload["total_count"] == 3
  assert "\"history_page\"" in export_payload["content"]
  assert "\"drill_down\"" in export_payload["content"]

  assert csv_export_response.status_code == 200
  csv_export_payload = csv_export_response.json()
  assert csv_export_payload["format"] == "csv"
  assert csv_export_payload["record_count"] == 2
  assert csv_export_payload["total_count"] == 3
  assert "record_id,recorded_at,status,summary" in csv_export_payload["content"]

  assert shared_export_create_response.status_code == 200
  shared_export_payload = shared_export_create_response.json()
  assert shared_export_payload["export_scope"] == "provider_provenance_scheduler_health"
  assert shared_export_payload["focus_key"] == "provider-provenance-scheduler-health"
  assert shared_export_payload["result_count"] == 3
  assert shared_export_payload["routing_policy_id"] == "default_critical"
  assert shared_export_payload["approval_state"] == "approved"
  assert shared_export_payload["routing_targets"] == ["slack_webhook", "pagerduty_events"]

  assert shared_export_list_response.status_code == 200
  shared_export_list_payload = shared_export_list_response.json()
  assert shared_export_list_payload["total"] >= 1
  assert any(
    item["job_id"] == shared_export_payload["job_id"]
    for item in shared_export_list_payload["items"]
  )

  assert shared_export_policy_response.status_code == 200
  shared_export_policy_payload = shared_export_policy_response.json()
  assert shared_export_policy_payload["export_job"]["routing_policy_id"] == "paging_only"
  assert shared_export_policy_payload["export_job"]["routing_targets"] == ["pagerduty_events"]
  assert shared_export_policy_payload["export_job"]["approval_state"] == "pending"
  assert shared_export_policy_payload["audit_record"]["action"] == "policy_updated"

  assert shared_export_unapproved_escalate_response.status_code == 400
  assert "requires approval" in shared_export_unapproved_escalate_response.json()["detail"]

  assert shared_export_approval_response.status_code == 200
  shared_export_approval_payload = shared_export_approval_response.json()
  assert shared_export_approval_payload["export_job"]["approval_state"] == "approved"
  assert shared_export_approval_payload["export_job"]["approved_by"] == "operator"
  assert shared_export_approval_payload["audit_record"]["action"] == "approved"

  assert shared_export_escalate_response.status_code == 200
  shared_export_escalation_payload = shared_export_escalate_response.json()
  assert shared_export_escalation_payload["export_job"]["escalation_count"] == 1
  assert shared_export_escalation_payload["export_job"]["last_delivery_status"] == "delivered"
  assert shared_export_escalation_payload["audit_record"]["action"] == "escalated"
  assert shared_export_escalation_payload["audit_record"]["routing_policy_id"] == "paging_only"
  assert shared_export_escalation_payload["audit_record"]["approval_state"] == "approved"
  assert shared_export_escalation_payload["audit_record"]["delivery_targets"] == ["pagerduty_events"]
  assert len(shared_export_escalation_payload["delivery_history"]) == 1
  assert delivery.deliveries[0][2] == "scheduler_export_escalation"

  assert shared_export_history_response.status_code == 200
  shared_export_history_payload = shared_export_history_response.json()
  assert [record["action"] for record in shared_export_history_payload["history"]] == [
    "escalated",
    "approved",
    "policy_updated",
    "created",
  ]


def test_operator_visibility_endpoint_persists_guarded_live_alert_history(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 13, 15, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="ETH", total=0.4, free=0.4, used=0.0),
        ),
      )
    )

    first_reconcile = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_balance_check"},
    )
    assert first_reconcile.status_code == 200

    active_visibility = client.get("/api/operator/visibility")
    assert active_visibility.status_code == 200
    active_payload = active_visibility.json()
    active_alert = next(
      alert for alert in active_payload["alerts"]
      if alert["alert_id"] == "guarded-live:reconciliation"
    )
    assert active_alert["source"] == "guarded_live"
    assert "guarded_live_status" in active_alert["delivery_targets"]
    active_history = next(
      alert for alert in active_payload["alert_history"]
      if alert["alert_id"] == "guarded-live:reconciliation"
    )
    assert active_history["status"] == "active"
    assert active_payload["incident_events"][0]["kind"] == "incident_opened"
    assert active_payload["incident_events"][0]["alert_id"] == "guarded-live:reconciliation"
    assert active_payload["delivery_history"][0]["target"] == "operator_console"
    assert active_payload["delivery_history"][0]["status"] == "delivered"
    assert active_payload["delivery_history"][0]["attempt_number"] == 1
    assert active_payload["delivery_history"][0]["next_retry_at"] is None
    assert any(event["kind"] == "guarded_live_reconciliation_ran" for event in active_payload["audit_events"])

    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 13, 20, tzinfo=UTC),
      )
    )
    second_reconcile = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "post_fix_balance_check"},
    )
    assert second_reconcile.status_code == 200

    resolved_visibility = client.get("/api/operator/visibility")

  assert resolved_visibility.status_code == 200
  resolved_payload = resolved_visibility.json()
  assert all(
    alert["alert_id"] != "guarded-live:reconciliation"
    for alert in resolved_payload["alerts"]
  )
  resolved_history = next(
    alert for alert in resolved_payload["alert_history"]
    if alert["alert_id"] == "guarded-live:reconciliation"
  )
  assert resolved_history["status"] == "resolved"
  assert resolved_history["resolved_at"] is not None
  assert resolved_payload["incident_events"][0]["kind"] == "incident_resolved"


def test_guarded_live_endpoints_manage_kill_switch_and_block_runtime_starts(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    initial = client.get("/api/guarded-live")
    assert initial.status_code == 200
    assert initial.json()["kill_switch"]["state"] == "released"

    engage_response = client.post(
      "/api/guarded-live/kill-switch/engage",
      json={"actor": "operator", "reason": "manual_safety_drill"},
    )

    assert engage_response.status_code == 200
    payload = engage_response.json()
    assert payload["kill_switch"]["state"] == "engaged"
    assert payload["kill_switch"]["updated_by"] == "operator"
    assert payload["audit_events"][0]["kind"] == "guarded_live_kill_switch_engaged"

    blocked_start = client.post(
      "/api/runs/sandbox",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
      },
    )

    assert blocked_start.status_code == 400
    assert "kill switch" in blocked_start.json()["detail"]

    release_response = client.post(
      "/api/guarded-live/kill-switch/release",
      json={"actor": "operator", "reason": "drill_complete"},
    )

    assert release_response.status_code == 200
    released_payload = release_response.json()
    assert released_payload["kill_switch"]["state"] == "released"
    assert any(
      event["kind"] == "guarded_live_kill_switch_released"
      for event in released_payload["audit_events"]
    )


def test_guarded_live_incident_endpoints_acknowledge_and_escalate(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._operator_alert_escalation_targets = ("pagerduty_events",)
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 13, 15, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="ETH", total=0.4, free=0.4, used=0.0),),
      )
    )
    reconcile = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "incident_actions"},
    )
    assert reconcile.status_code == 200
    incident = next(
      event
      for event in reconcile.json()["incident_events"]
      if event["kind"] == "incident_opened" and event["alert_id"] == "guarded-live:reconciliation"
    )

    acknowledged = client.post(
      f"/api/guarded-live/incidents/{incident['event_id']}/acknowledge",
      json={"actor": "operator", "reason": "on_call_ack"},
    )
    assert acknowledged.status_code == 200
    acknowledged_incident = next(
      event
      for event in acknowledged.json()["incident_events"]
      if event["event_id"] == incident["event_id"]
    )
    assert acknowledged_incident["acknowledgment_state"] == "acknowledged"
    assert acknowledged_incident["acknowledged_by"] == "operator"
    assert acknowledged_incident["acknowledgment_reason"] == "on_call_ack"

    escalated = client.post(
      f"/api/guarded-live/incidents/{incident['event_id']}/escalate",
      json={"actor": "operator", "reason": "manager_page"},
    )
    assert escalated.status_code == 200
    escalated_incident = next(
      event
      for event in escalated.json()["incident_events"]
      if event["event_id"] == incident["event_id"]
    )
    assert escalated_incident["escalation_level"] == 1
    assert escalated_incident["last_escalated_by"] == "operator"
    assert escalated_incident["escalation_reason"] == "manager_page"
    escalation_delivery = next(
      record
      for record in escalated.json()["delivery_history"]
      if record["incident_event_id"] == incident["event_id"] and record["phase"] == "escalation"
    )
    assert escalation_delivery["target"] == "pagerduty_events"


def test_external_incident_sync_endpoint_updates_paging_state_and_requires_token(tmp_path: Path) -> None:
  with build_client(
    tmp_path / "runs.sqlite3",
    guarded_live_execution_enabled=True,
    operator_alert_external_sync_token="shared-token",
  ) as client:
    app = client.app.state.container.app
    app._operator_alert_escalation_targets = ("pagerduty_events",)
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 13, 15, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="ETH", total=0.4, free=0.4, used=0.0),),
      )
    )
    reconcile = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "external_incident_sync"},
    )
    assert reconcile.status_code == 200

    forbidden = client.post(
      "/api/operator/incidents/external-sync",
      json={
        "provider": "pagerduty",
        "event_kind": "acknowledged",
        "actor": "responder-1",
        "detail": "pd_ack",
        "alert_id": "guarded-live:reconciliation",
      },
    )
    assert forbidden.status_code == 403

    synced = client.post(
      "/api/operator/incidents/external-sync",
      headers={"X-Akra-Incident-Sync-Token": "shared-token"},
      json={
        "provider": "pagerduty",
        "event_kind": "acknowledged",
        "actor": "responder-1",
        "detail": "pd_ack",
        "alert_id": "guarded-live:reconciliation",
        "external_reference": "guarded-live:reconciliation",
        "occurred_at": "2025-01-03T13:16:00Z",
      },
    )
    assert synced.status_code == 200
    incident = next(
      event
      for event in synced.json()["incident_events"]
      if event["kind"] == "incident_opened" and event["alert_id"] == "guarded-live:reconciliation"
    )
    assert incident["acknowledgment_state"] == "acknowledged"
    assert incident["acknowledged_by"] == "pagerduty:responder-1"
    assert incident["external_provider"] == "pagerduty"
    assert incident["external_status"] == "acknowledged"
    assert incident["paging_status"] == "acknowledged"


def test_incident_endpoints_surface_provider_workflow_and_paging_policy(tmp_path: Path) -> None:
  class FakeProviderWorkflowDeliveryAdapter:
    def list_targets(self) -> tuple[str, ...]:
      return ("operator_console",)

    def list_supported_workflow_providers(self) -> tuple[str, ...]:
      return ("pagerduty",)

    def deliver(
      self,
      *,
      incident: OperatorIncidentEvent,
      targets: tuple[str, ...] | None = None,
      attempt_number: int = 1,
      phase: str = "initial",
    ) -> tuple[OperatorIncidentDelivery, ...]:
      resolved_targets = targets or self.list_targets()
      return tuple(
        OperatorIncidentDelivery(
          delivery_id=f"{incident.event_id}:{target}:attempt-{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=target,
          status="delivered",
          attempted_at=incident.timestamp,
          detail=f"fake_delivery:{target}",
          attempt_number=attempt_number,
          phase=phase,
          external_provider="pagerduty" if target == "pagerduty_events" else None,
          external_reference=incident.external_reference or incident.alert_id,
          source=incident.source,
        )
        for target in resolved_targets
      )

    def sync_incident_workflow(
      self,
      *,
      incident: OperatorIncidentEvent,
      provider: str,
      action: str,
      actor: str,
      detail: str,
      payload=None,
      attempt_number: int = 1,
    ) -> tuple[OperatorIncidentDelivery, ...]:
      return (
        OperatorIncidentDelivery(
          delivery_id=f"{incident.event_id}:{provider}_workflow:{action}:attempt-{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=f"{provider}_workflow",
          status="delivered",
          attempted_at=incident.timestamp,
          detail=f"fake_provider_workflow:{action}:{detail}",
          attempt_number=attempt_number,
          phase=f"provider_{action}",
          provider_action=action,
          external_provider=provider,
          external_reference=incident.provider_workflow_reference,
          source=incident.source,
        ),
      )

    def pull_incident_workflow_state(
      self,
      *,
      incident: OperatorIncidentEvent,
      provider: str,
    ):
      return None

  with build_client(
    tmp_path / "runs.sqlite3",
    guarded_live_execution_enabled=True,
    operator_alert_external_sync_token="shared-token",
  ) as client:
    app = client.app.state.container.app
    app._operator_alert_delivery = FakeProviderWorkflowDeliveryAdapter()
    app._operator_alert_paging_policy_default_provider = "pagerduty"
    app._operator_alert_paging_policy_warning_targets = ("slack_webhook", "pagerduty_events")
    app._operator_alert_paging_policy_critical_targets = ("slack_webhook", "pagerduty_events")
    app._operator_alert_paging_policy_warning_escalation_targets = ("pagerduty_events",)
    app._operator_alert_paging_policy_critical_escalation_targets = ("pagerduty_events",)
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 14, 0, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="ETH", total=0.4, free=0.4, used=0.0),),
      )
    )

    reconcile = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "provider_workflow_surface"},
    )
    assert reconcile.status_code == 200
    incident = next(
      event
      for event in reconcile.json()["incident_events"]
      if event["kind"] == "incident_opened" and event["alert_id"] == "guarded-live:reconciliation"
    )
    assert incident["paging_provider"] == "pagerduty"
    assert incident["paging_policy_id"] in {"severity:warning", "severity:critical"}

    synced = client.post(
      "/api/operator/incidents/external-sync",
      headers={"X-Akra-Incident-Sync-Token": "shared-token"},
      json={
        "provider": "pagerduty",
        "event_kind": "triggered",
        "actor": "responder-1",
        "detail": "provider_triggered",
        "alert_id": "guarded-live:reconciliation",
        "external_reference": "guarded-live:reconciliation",
        "workflow_reference": "PDINC-901",
        "occurred_at": "2025-01-03T14:01:00Z",
      },
    )
    assert synced.status_code == 200

    acknowledged = client.post(
      f"/api/guarded-live/incidents/{incident['event_id']}/acknowledge",
      json={"actor": "operator", "reason": "provider_ack"},
    )
    assert acknowledged.status_code == 200
    acknowledged_incident = next(
      event
      for event in acknowledged.json()["incident_events"]
      if event["event_id"] == incident["event_id"]
    )
    assert acknowledged_incident["provider_workflow_reference"] == "PDINC-901"
    assert acknowledged_incident["provider_workflow_state"] == "delivered"
    assert acknowledged_incident["provider_workflow_action"] == "acknowledge"
    provider_delivery = next(
      record
      for record in acknowledged.json()["delivery_history"]
      if record["incident_event_id"] == incident["event_id"] and record["phase"] == "provider_acknowledge"
    )
    assert provider_delivery["target"] == "pagerduty_workflow"


def test_guarded_live_status_survives_app_restart(tmp_path: Path) -> None:
  database_path = tmp_path / "runs.sqlite3"

  with build_client(database_path) as client:
    reconcile_response = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "startup_drill"},
    )
    assert reconcile_response.status_code == 200

    engage_response = client.post(
      "/api/guarded-live/kill-switch/engage",
      json={"actor": "operator", "reason": "startup_safety_latch"},
    )
    assert engage_response.status_code == 200

  with build_client(database_path) as restarted_client:
    response = restarted_client.get("/api/guarded-live")

  assert response.status_code == 200
  payload = response.json()
  assert payload["kill_switch"]["state"] == "engaged"
  assert payload["reconciliation"]["checked_by"] == "operator"
  assert payload["reconciliation"]["scope"] == "venue_state"
  assert payload["reconciliation"]["venue_snapshot"]["provider"] == "seeded"
  assert payload["reconciliation"]["venue_snapshot"]["verification_state"] == "verified"
  assert any(event["kind"] == "guarded_live_reconciliation_ran" for event in payload["audit_events"])
  assert any(event["kind"] == "guarded_live_kill_switch_engaged" for event in payload["audit_events"])


def test_guarded_live_reconciliation_endpoint_surfaces_venue_balance_mismatch(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    app = client.app.state.container.app
    run = app.start_sandbox_run(
      strategy_id="ma_cross_v1",
      symbol="ETH/USDT",
      timeframe="5m",
      initial_cash=10_000,
      fee_rate=0.001,
      slippage_bps=3,
      parameters={},
      replay_bars=24,
    )
    run.positions = {
      "binance:ETH/USDT": Position(
        instrument_id="binance:ETH/USDT",
        quantity=1.25,
        average_price=2_000.0,
        opened_at=datetime(2025, 1, 3, 16, 0, tzinfo=UTC),
        updated_at=datetime(2025, 1, 3, 16, 0, tzinfo=UTC),
      )
    }
    app._runs.save_run(run)
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 16, 5, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="ETH", total=0.5, free=0.5, used=0.0),
          GuardedLiveVenueBalance(asset="USDT", total=9_000.0, free=9_000.0, used=0.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id="venue-order-1",
            symbol="ETH/USDT",
            side="buy",
            amount=0.5,
            status="open",
            price=2_100.0,
          ),
        ),
      )
    )

    response = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "venue_state_drill"},
    )

  assert response.status_code == 200
  payload = response.json()
  assert payload["reconciliation"]["venue_snapshot"]["verification_state"] == "verified"
  assert any(
    finding["kind"] == "venue_balance_mismatch"
    for finding in payload["reconciliation"]["findings"]
  )
  assert any(
    finding["kind"] == "venue_open_order_mismatch"
    for finding in payload["reconciliation"]["findings"]
  )


def test_guarded_live_recovery_endpoint_recovers_from_stored_verified_snapshot_after_restart(
  tmp_path: Path,
) -> None:
  database_path = tmp_path / "runs.sqlite3"

  with build_client(database_path) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 17, 0, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="ETH", total=0.6, free=0.4, used=0.2),
          GuardedLiveVenueBalance(asset="USDT", total=9_400.0, free=9_400.0, used=0.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id="venue-order-2",
            symbol="ETH/USDT",
            side="sell",
            amount=0.2,
            status="open",
            price=2_250.0,
          ),
        ),
      )
    )

    reconcile_response = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_restart_snapshot"},
    )
    assert reconcile_response.status_code == 200

    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="binance",
        venue="binance",
        verification_state="unavailable",
        captured_at=datetime(2025, 1, 3, 17, 5, tzinfo=UTC),
        issues=("temporary_venue_fault",),
      )
    )
    recovery_response = client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "post_restart_recovery"},
    )

    assert recovery_response.status_code == 200
    recovery_payload = recovery_response.json()
    assert recovery_payload["recovery"]["state"] == "recovered"
    assert recovery_payload["recovery"]["source_verification_state"] == "verified"
    assert recovery_payload["recovery"]["exposures"][0]["instrument_id"] == "binance:ETH/USDT"
    assert recovery_payload["recovery"]["open_orders"][0]["order_id"] == "venue-order-2"
    assert any(event["kind"] == "guarded_live_runtime_recovered" for event in recovery_payload["audit_events"])

  with build_client(database_path) as restarted_client:
    status_response = restarted_client.get("/api/guarded-live")

  assert status_response.status_code == 200
  payload = status_response.json()
  assert payload["recovery"]["state"] == "recovered"
  assert payload["recovery"]["source_verification_state"] == "verified"
  assert payload["recovery"]["exposures"][0]["symbol"] == "ETH/USDT"


def test_live_endpoints_launch_and_stop_guarded_live_worker_after_gates_clear(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 0, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),
        ),
      )
    )

    blocked_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "pre_gate_attempt",
      },
    )
    assert blocked_response.status_code == 400
    assert "blocked" in blocked_response.json()["detail"]

    reconcile_response = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    assert reconcile_response.status_code == 200

    recovery_response = client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    assert recovery_response.status_code == 200

    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "guarded_live_launch",
      },
    )

    assert live_response.status_code == 200
    payload = live_response.json()
    assert payload["config"]["mode"] == "live"
    assert payload["status"] == "running"
    assert payload["provenance"]["runtime_session"]["worker_kind"] == "guarded_live_native_worker"
    assert payload["notes"][0].startswith("Guarded live worker primed from recovered venue state")

    run_id = payload["config"]["run_id"]
    stop_response = client.post(f"/api/runs/live/{run_id}/stop")

  assert stop_response.status_code == 200
  stopped_payload = stop_response.json()
  assert stopped_payload["status"] == "stopped"
  assert stopped_payload["provenance"]["runtime_session"]["lifecycle_state"] == "stopped"


def test_stop_sandbox_endpoint_rejects_when_control_surface_rule_is_disabled(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    app = client.app.state.container.app
    run_response = client.post(
      "/api/runs/sandbox",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
      },
    )
    run_id = run_response.json()["config"]["run_id"]
    base_capabilities = app.get_run_surface_capabilities()
    app.get_run_surface_capabilities = lambda: without_surface_rule(
      base_capabilities,
      family_key="execution_controls",
      surface_key="rerun_and_stop_controls",
    )

    stop_response = client.post(f"/api/runs/sandbox/{run_id}/stop")

  assert stop_response.status_code == 400
  assert stop_response.json()["detail"] == (
    "Surface rule rerun_and_stop_controls is disabled by the run-surface capability contract."
  )


def test_operator_visibility_endpoint_surfaces_risk_breach_and_live_fault_incidents(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 0, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "risk_fault_visibility",
      },
    )
    assert live_response.status_code == 200
    payload = live_response.json()
    run = app.get_run(payload["config"]["run_id"])
    assert run is not None
    assert run.provenance.runtime_session is not None
    run.provenance.runtime_session.recovery_count = 2
    run.provenance.runtime_session.last_recovered_at = datetime(2025, 1, 3, 18, 1, tzinfo=UTC)
    run.provenance.runtime_session.last_recovery_reason = "heartbeat_timeout"
    run.metrics["max_drawdown_pct"] = 41.0
    run.orders.append(
      Order(
        run_id=run.config.run_id,
        instrument_id="binance:ETH/USDT",
        side=OrderSide.BUY,
        quantity=0.2,
        requested_price=3_150.0,
        order_type=OrderType.LIMIT,
        status=OrderStatus.OPEN,
        order_id="stale-api-live-order-1",
        created_at=datetime(2025, 1, 3, 17, 50, tzinfo=UTC),
        updated_at=datetime(2025, 1, 3, 17, 51, tzinfo=UTC),
        last_synced_at=datetime(2025, 1, 3, 17, 52, tzinfo=UTC),
        remaining_quantity=0.2,
      )
    )
    app._runs.save_run(run)

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    alerts = visibility_response.json()["alerts"]
    categories = {
      alert["category"]
      for alert in alerts
      if alert.get("run_id") == run.config.run_id and alert.get("source") == "guarded_live"
    }
    assert {"risk_breach", "runtime_recovery", "order_sync"} <= categories

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    assert any(event["alert_id"].startswith("guarded-live:risk-breach:") for event in incident_events)
    assert any(event["alert_id"].startswith("guarded-live:order-sync:") for event in incident_events)


def test_operator_visibility_endpoint_surfaces_market_data_freshness_and_wider_risk_incidents(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    market_data = StatusOverrideSeededMarketDataAdapter()
    app._market_data = market_data
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 0, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "market_data_risk_visibility",
      },
    )
    assert live_response.status_code == 200
    run = app.get_run(live_response.json()["config"]["run_id"])
    assert run is not None
    market_data.set_status(
      timeframe="5m",
      status=MarketDataStatus(
        provider="binance",
        venue="binance",
        instruments=[
          InstrumentStatus(
            instrument_id="binance:ETH/USDT",
            timeframe="5m",
            candle_count=288,
            first_timestamp=datetime(2025, 1, 2, 18, 0, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 17, 40, tzinfo=UTC),
            sync_status="stale",
            lag_seconds=1_200,
            last_sync_at=datetime(2025, 1, 3, 17, 45, tzinfo=UTC),
            recent_failures=(
              SyncFailure(
                failed_at=datetime(2025, 1, 3, 17, 51, tzinfo=UTC),
                operation="sync_recent",
                error="exchange timeout",
              ),
            ),
            failure_count_24h=2,
            backfill_target_candles=400,
            backfill_completion_ratio=0.72,
            backfill_complete=False,
            backfill_contiguous_completion_ratio=0.91,
            backfill_contiguous_complete=False,
            backfill_contiguous_missing_candles=3,
            backfill_gap_windows=(
              GapWindow(
                start_at=datetime(2025, 1, 3, 16, 0, tzinfo=UTC),
                end_at=datetime(2025, 1, 3, 16, 10, tzinfo=UTC),
                missing_candles=3,
              ),
            ),
            issues=(
              "lagging",
              "freshness_threshold_exceeded:1200:600",
              "missing_candles:3",
              "backfill_target_incomplete:288:400",
              "contiguous_backfill_incomplete:3",
              "gap_windows:1",
              "repeated_sync_failures:2",
              "binance_timeout",
            ),
          ),
        ],
      ),
    )
    run.metrics["total_return_pct"] = -24.0
    run.orders.append(
      Order(
        run_id=run.config.run_id,
        instrument_id="binance:ETH/USDT",
        side=OrderSide.BUY,
        quantity=4.0,
        requested_price=3_200.0,
        order_type=OrderType.LIMIT,
        status=OrderStatus.OPEN,
        order_id="api-pending-risk-order-1",
        created_at=datetime(2025, 1, 3, 17, 54, tzinfo=UTC),
        updated_at=datetime(2025, 1, 3, 17, 54, tzinfo=UTC),
        last_synced_at=datetime(2025, 1, 3, 17, 59, 30, tzinfo=UTC),
        remaining_quantity=4.0,
      )
    )
    app._runs.save_run(run)

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    alerts = visibility_response.json()["alerts"]
    categories = {alert["category"] for alert in alerts if alert.get("source") == "guarded_live"}
    assert {
      "market_data_freshness",
      "market_data_quality",
      "market_data_candle_continuity",
      "market_data_venue",
      "risk_breach",
    } <= categories
    market_data_alert = next(alert for alert in alerts if alert["category"] == "market_data_freshness")
    assert "ETH/USDT lagged 1200s." in market_data_alert["detail"]
    assert market_data_alert["symbol"] == "ETH/USDT"
    assert market_data_alert["symbols"] == ["ETH/USDT"]
    assert market_data_alert["timeframe"] == "5m"
    market_data_quality_alert = next(alert for alert in alerts if alert["category"] == "market_data_quality")
    assert "backfill target covers 72.00%" in market_data_quality_alert["detail"]
    market_data_continuity_alert = next(alert for alert in alerts if alert["category"] == "market_data_candle_continuity")
    assert "has 3 missing candle(s) across 1 gap window(s)." in market_data_continuity_alert["detail"]
    assert "contiguous backfill quality is 91.00%" in market_data_continuity_alert["detail"]
    market_data_venue_alert = next(alert for alert in alerts if alert["category"] == "market_data_venue")
    assert "recorded 2 sync failure(s)" in market_data_venue_alert["detail"]
    assert "venue semantics: timeout" in market_data_venue_alert["detail"]
    risk_alert = next(
      alert for alert in alerts
      if alert.get("run_id") == run.config.run_id and alert["category"] == "risk_breach"
    )
    assert "total return -24.00%" in risk_alert["detail"]
    assert "gross open risk reached" in risk_alert["detail"]
    assert risk_alert["symbol"] == "ETH/USDT"
    assert risk_alert["symbols"] == ["ETH/USDT"]
    assert risk_alert["timeframe"] == "5m"

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    market_data_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened" and event["alert_id"] == "guarded-live:market-data:5m"
    )
    assert market_data_incident["symbol"] == "ETH/USDT"
    assert market_data_incident["symbols"] == ["ETH/USDT"]
    assert market_data_incident["timeframe"] == "5m"
    assert any(event["alert_id"] == "guarded-live:market-data:5m" for event in incident_events)
    assert any(event["alert_id"] == "guarded-live:market-data-quality:binance:5m" for event in incident_events)
    assert any(event["alert_id"] == "guarded-live:market-data-continuity:binance:5m" for event in incident_events)
    assert any(event["alert_id"] == "guarded-live:market-data-venue:binance:5m" for event in incident_events)
    assert any(event["alert_id"].startswith("guarded-live:risk-breach:") for event in incident_events)


def test_operator_visibility_endpoint_embeds_multi_symbol_primary_focus_metadata(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    market_data = StatusOverrideSeededMarketDataAdapter()
    app._market_data = market_data
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 0, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "api_multi_symbol_primary_focus",
      },
    )
    assert live_response.status_code == 200
    run = app.get_run(live_response.json()["config"]["run_id"])
    assert run is not None
    secondary_run = replace(
      run,
      config=replace(
        run.config,
        run_id="api-live-run-btc-primary-focus",
        symbols=("BTC/USDT",),
      ),
      provenance=replace(
        run.provenance,
        runtime_session=replace(
          run.provenance.runtime_session,
          session_id="worker-live-btc-primary-focus-api",
        ) if run.provenance.runtime_session is not None else None,
      ),
      orders=[],
      fills=[],
      positions={},
      equity_curve=[],
      closed_trades=[],
      metrics={},
      notes=list(run.notes),
    )
    app._runs.save_run(secondary_run)
    market_data.set_status(
      timeframe="5m",
      status=MarketDataStatus(
        provider="binance",
        venue="binance",
        instruments=[
          InstrumentStatus(
            instrument_id="binance:BTC/USDT",
            timeframe="5m",
            candle_count=288,
            first_timestamp=datetime(2025, 1, 2, 18, 0, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 17, 42, tzinfo=UTC),
            sync_status="stale",
            lag_seconds=1_080,
            last_sync_at=datetime(2025, 1, 3, 17, 48, tzinfo=UTC),
            failure_count_24h=2,
            backfill_gap_windows=(
              GapWindow(
                start_at=datetime(2025, 1, 3, 17, 0, tzinfo=UTC),
                end_at=datetime(2025, 1, 3, 17, 10, tzinfo=UTC),
                missing_candles=2,
              ),
            ),
            issues=("freshness_threshold_exceeded:1080:600", "repeated_sync_failures:2"),
          ),
          InstrumentStatus(
            instrument_id="binance:ETH/USDT",
            timeframe="5m",
            candle_count=288,
            first_timestamp=datetime(2025, 1, 2, 18, 0, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 17, 59, tzinfo=UTC),
            sync_status="synced",
            lag_seconds=0,
            last_sync_at=datetime(2025, 1, 3, 17, 59, tzinfo=UTC),
            issues=(),
          ),
        ],
      ),
    )

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    market_data_alert = next(
      alert
      for alert in visibility_response.json()["alerts"]
      if alert["category"] == "market_data_freshness"
    )
    assert market_data_alert["symbol"] is None
    assert market_data_alert["symbols"] == ["BTC/USDT", "ETH/USDT"]
    assert market_data_alert["primary_focus"] == {
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "candidate_symbols": ["BTC/USDT", "ETH/USDT"],
      "candidate_count": 2,
      "policy": "market_data_risk_order",
      "reason": "Selected BTC/USDT as the highest-risk market-data candidate from 2 symbols.",
    }

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    market_data_incident = next(
      event
      for event in guarded_live_response.json()["incident_events"]
      if event["kind"] == "incident_opened" and event["alert_id"] == "guarded-live:market-data:5m"
    )
    assert market_data_incident["symbol"] is None
    assert market_data_incident["symbols"] == ["BTC/USDT", "ETH/USDT"]
    assert market_data_incident["primary_focus"] == market_data_alert["primary_focus"]


def test_market_data_incident_endpoint_surfaces_remediation_and_provider_workflow(
  tmp_path: Path,
) -> None:
  class FakeProviderWorkflowDeliveryAdapter:
    def list_targets(self) -> tuple[str, ...]:
      return ("pagerduty_events",)

    def list_supported_workflow_providers(self) -> tuple[str, ...]:
      return ("pagerduty",)

    def deliver(
      self,
      *,
      incident: OperatorIncidentEvent,
      targets: tuple[str, ...] | None = None,
      attempt_number: int = 1,
      phase: str = "initial",
    ) -> tuple[OperatorIncidentDelivery, ...]:
      resolved_targets = targets or self.list_targets()
      return tuple(
        OperatorIncidentDelivery(
          delivery_id=f"{incident.event_id}:{target}:attempt-{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=target,
          status="delivered",
          attempted_at=incident.timestamp,
          detail=f"fake_delivery:{target}",
          attempt_number=attempt_number,
          phase=phase,
          external_provider="pagerduty",
          external_reference=incident.external_reference or incident.alert_id,
          source=incident.source,
        )
        for target in resolved_targets
      )

    def sync_incident_workflow(
      self,
      *,
      incident: OperatorIncidentEvent,
      provider: str,
      action: str,
      actor: str,
      detail: str,
      payload=None,
      attempt_number: int = 1,
    ) -> tuple[OperatorIncidentDelivery, ...]:
      return (
        OperatorIncidentDelivery(
          delivery_id=f"{incident.event_id}:{provider}_workflow:{action}:attempt-{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=f"{provider}_workflow",
          status="delivered",
          attempted_at=incident.timestamp,
          detail=f"fake_provider_workflow:{action}:{detail}",
          attempt_number=attempt_number,
          phase=f"provider_{action}",
          provider_action=action,
          external_provider=provider,
          external_reference=incident.provider_workflow_reference or incident.external_reference or incident.alert_id,
          source=incident.source,
        ),
      )

    def pull_incident_workflow_state(
      self,
      *,
      incident: OperatorIncidentEvent,
      provider: str,
    ):
      return None

  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._operator_alert_delivery = FakeProviderWorkflowDeliveryAdapter()
    app._operator_alert_paging_policy_default_provider = "pagerduty"
    app._operator_alert_paging_policy_warning_targets = ("pagerduty_events",)
    app._operator_alert_paging_policy_critical_targets = ("pagerduty_events",)
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 30, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "market_data_remediation_surface"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "market_data_remediation_surface"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "market_data_remediation_surface",
      },
    )
    assert live_response.status_code == 200
    market_data = StatusOverrideSeededMarketDataAdapter()
    market_data.set_status(
      timeframe="5m",
      status=MarketDataStatus(
        provider="binance",
        venue="binance",
        instruments=[
          InstrumentStatus(
            instrument_id="binance:ETH/USDT",
            timeframe="5m",
            candle_count=288,
            first_timestamp=datetime(2025, 1, 2, 18, 30, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 18, 10, tzinfo=UTC),
            sync_status="stale",
            lag_seconds=1_200,
            last_sync_at=datetime(2025, 1, 3, 18, 15, tzinfo=UTC),
            issues=("freshness_threshold_exceeded:1200:600",),
          ),
        ],
      ),
    )
    app._market_data = market_data

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident = next(
      event
      for event in guarded_live_response.json()["incident_events"]
      if event["kind"] == "incident_opened" and event["alert_id"] == "guarded-live:market-data:5m"
    )
    assert incident["remediation"]["kind"] == "recent_sync"
    assert incident["remediation"]["state"] == "skipped"
    assert incident["remediation"]["runbook"] == "market_data.sync_recent"
    assert incident["remediation"]["provider"] == "pagerduty"
    assert incident["remediation"]["provider_recovery"]["lifecycle_state"] == "requested"
    assert incident["remediation"]["provider_recovery"]["status_machine"]["state"] == "provider_requested"
    assert incident["remediation"]["provider_recovery"]["status_machine"]["workflow_action"] == "remediate"
    assert "seeded_market_data_provider_has_no_live_remediation_jobs" in incident["remediation"]["detail"]
    assert any(
      record["incident_event_id"] == incident["event_id"] and record["phase"] == "provider_remediate"
      for record in guarded_live_response.json()["delivery_history"]
    )

    market_data.set_remediation_status(
      kind="recent_sync",
      timeframe="5m",
      status=MarketDataStatus(
        provider="binance",
        venue="binance",
        instruments=[
          InstrumentStatus(
            instrument_id="binance:ETH/USDT",
            timeframe="5m",
            candle_count=288,
            first_timestamp=datetime(2025, 1, 2, 18, 30, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 18, 30, tzinfo=UTC),
            sync_status="synced",
            lag_seconds=0,
            last_sync_at=datetime(2025, 1, 3, 18, 30, tzinfo=UTC),
            issues=(),
          ),
        ],
      ),
    )

    remediated = client.post(
      f"/api/guarded-live/incidents/{incident['event_id']}/remediate",
      json={"actor": "operator", "reason": "manual_market_data_resync"},
    )
    assert remediated.status_code == 200
    refreshed = next(
      event
      for event in remediated.json()["incident_events"]
      if event["event_id"] == incident["event_id"]
    )
    assert refreshed["remediation"]["state"] == "executed"
    assert refreshed["remediation"]["requested_by"] == "operator"
    assert "recent_sync:ETH/USDT:5m:status_repaired" in refreshed["remediation"]["detail"]
    assert any(
      event["kind"] == "incident_resolved" and event["alert_id"] == "guarded-live:market-data:5m"
      for event in remediated.json()["incident_events"]
    )
  assert all(
      alert["alert_id"] != "guarded-live:market-data:5m"
      for alert in remediated.json()["active_alerts"]
    )


def test_guarded_live_channel_restore_incidents_auto_run_local_session_job(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._operator_alert_paging_policy_default_provider = "pagerduty"
    app._operator_alert_paging_policy_warning_targets = ("pagerduty_events",)
    app._operator_alert_paging_policy_critical_targets = ("pagerduty_events",)
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 30, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "channel_restore_local_remediation"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "channel_restore_local_remediation"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "channel_restore_local_remediation",
      },
    )
    assert live_response.status_code == 200
    run_id = live_response.json()["config"]["run_id"]

    state = app._guarded_live_state.load_state()
    app._guarded_live_state.save_state(
      replace(
        state,
        session_handoff=replace(
          state.session_handoff,
          coverage=("trade_ticks", "depth_updates", "kline_candles"),
          handed_off_at=datetime(2025, 1, 3, 18, 28, tzinfo=UTC),
          last_sync_at=datetime(2025, 1, 3, 18, 28, tzinfo=UTC),
          last_trade_event_at=datetime(2025, 1, 3, 18, 28, tzinfo=UTC),
          last_depth_event_at=datetime(2025, 1, 3, 18, 28, tzinfo=UTC),
          last_kline_event_at=None,
          channel_restore_state="unavailable",
          channel_restore_count=2,
          channel_last_restored_at=datetime(2025, 1, 3, 18, 29, tzinfo=UTC),
          channel_continuation_state="unavailable",
          channel_continuation_count=2,
          channel_last_continued_at=datetime(2025, 1, 3, 18, 29, tzinfo=UTC),
          issues=("binance_market_channel_restore_failed:ticker:timeout:exchange timeout",),
        ),
      )
    )

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident = next(
      event
      for event in guarded_live_response.json()["incident_events"]
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-channel-restore:{run_id}"
    )
    assert incident["remediation"]["kind"] == "channel_restore"
    assert guarded_live_response.json()["session_handoff"]["channel_restore_state"] == "synthetic"
    assert guarded_live_response.json()["session_handoff"]["channel_continuation_state"] == "synthetic"
    assert any(
      event["kind"] == "incident_resolved"
      and event["alert_id"] == f"guarded-live:market-data-channel-restore:{run_id}"
      for event in guarded_live_response.json()["incident_events"]
    )
    assert all(
      alert["alert_id"] != f"guarded-live:market-data-channel-restore:{run_id}"
      for alert in guarded_live_response.json()["active_alerts"]
    )
    assert any(
      event["kind"] == "guarded_live_incident_local_remediation_executed"
      and "channel_restore:ETH/USDT:5m:channel_restore=synthetic" in event["detail"]
      for event in guarded_live_response.json()["audit_events"]
    )


def test_external_market_data_recovery_sync_endpoint_resolves_incident(
  tmp_path: Path,
) -> None:
  with build_client(
    tmp_path / "runs.sqlite3",
    guarded_live_execution_enabled=True,
    operator_alert_external_sync_token="shared-token",
  ) as client:
    app = client.app.state.container.app
    app._operator_alert_paging_policy_default_provider = "pagerduty"
    app._operator_alert_paging_policy_warning_targets = ("pagerduty_events",)
    app._operator_alert_paging_policy_critical_targets = ("pagerduty_events",)
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 30, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "provider_market_data_recovery_surface"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "provider_market_data_recovery_surface"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "provider_market_data_recovery_surface",
      },
    )
    assert live_response.status_code == 200
    market_data = StatusOverrideSeededMarketDataAdapter()
    market_data.set_status(
      timeframe="5m",
      status=MarketDataStatus(
        provider="binance",
        venue="binance",
        instruments=[
          InstrumentStatus(
            instrument_id="binance:ETH/USDT",
            timeframe="5m",
            candle_count=288,
            first_timestamp=datetime(2025, 1, 2, 18, 30, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 18, 10, tzinfo=UTC),
            sync_status="stale",
            lag_seconds=1_200,
            last_sync_at=datetime(2025, 1, 3, 18, 15, tzinfo=UTC),
            issues=("freshness_threshold_exceeded:1200:600",),
          ),
        ],
      ),
    )
    app._market_data = market_data

    guarded_live_response = client.get("/api/guarded-live")
    incident = next(
      event
      for event in guarded_live_response.json()["incident_events"]
      if event["kind"] == "incident_opened" and event["alert_id"] == "guarded-live:market-data:5m"
    )
    assert incident["remediation"]["state"] == "not_supported"

    market_data.set_remediation_status(
      kind="recent_sync",
      timeframe="5m",
      status=MarketDataStatus(
        provider="binance",
        venue="binance",
        instruments=[
          InstrumentStatus(
            instrument_id="binance:ETH/USDT",
            timeframe="5m",
            candle_count=288,
            first_timestamp=datetime(2025, 1, 2, 18, 30, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 18, 30, tzinfo=UTC),
            sync_status="synced",
            lag_seconds=0,
            last_sync_at=datetime(2025, 1, 3, 18, 30, tzinfo=UTC),
            issues=(),
          ),
        ],
      ),
    )

    synced = client.post(
      "/api/operator/incidents/external-sync",
      headers={"X-Akra-Incident-Sync-Token": "shared-token"},
      json={
        "provider": "pagerduty",
        "event_kind": "remediation_completed",
        "actor": "responder-1",
        "detail": "provider_market_data_recovered",
        "alert_id": "guarded-live:market-data:5m",
        "external_reference": "guarded-live:market-data:5m",
        "workflow_reference": "PDINC-REC-901",
        "occurred_at": "2025-01-03T18:31:00Z",
          "payload": {
            "job_id": "provider-job-901",
            "summary": "provider completed recovery verification",
            "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
            "verification": {"state": "passed"},
            "telemetry": {
              "state": "completed",
              "progress_percent": 100,
              "attempt_count": 2,
              "current_step": "verification",
              "external_run_id": "pd-api-telemetry-901",
            },
          },
        },
      )
    assert synced.status_code == 200
    updated_incident = next(
      event
      for event in synced.json()["incident_events"]
      if event["event_id"] == incident["event_id"]
    )
    assert updated_incident["remediation"]["state"] == "executed"
    assert updated_incident["remediation"]["requested_by"] == "pagerduty:responder-1"
    assert updated_incident["remediation"]["provider_payload"]["job_id"] == "provider-job-901"
    assert updated_incident["remediation"]["provider_recovery"]["job_id"] == "provider-job-901"
    assert updated_incident["remediation"]["provider_recovery"]["provider_schema_kind"] == "pagerduty"
    assert updated_incident["remediation"]["provider_recovery"]["pagerduty"]["incident_id"] == "PDINC-REC-901"
    assert updated_incident["remediation"]["provider_recovery"]["pagerduty"]["incident_status"] == "delivered"
    assert updated_incident["remediation"]["provider_recovery"]["pagerduty"]["phase_graph"]["workflow_phase"] == "verified_pending_resolve"
    assert updated_incident["remediation"]["provider_recovery"]["telemetry"]["state"] == "completed"
    assert updated_incident["remediation"]["provider_recovery"]["telemetry"]["progress_percent"] == 100
    assert updated_incident["remediation"]["provider_recovery"]["telemetry"]["current_step"] == "verification"
    assert updated_incident["remediation"]["provider_recovery"]["symbols"] == ["ETH/USDT"]
    assert updated_incident["remediation"]["provider_recovery"]["timeframe"] == "5m"
    assert updated_incident["remediation"]["provider_recovery"]["verification"]["state"] == "passed"
    assert updated_incident["remediation"]["provider_recovery"]["status_machine"]["state"] == "verified"
    assert updated_incident["remediation"]["provider_recovery"]["status_machine"]["workflow_state"] == "delivered"
    assert updated_incident["remediation"]["provider_recovery"]["status_machine"]["workflow_action"] == "remediate"
    assert updated_incident["remediation"]["provider_recovery"]["status_machine"]["job_state"] == "verified"
    assert updated_incident["remediation"]["provider_recovery"]["status_machine"]["sync_state"] == "bidirectional_synced"
    assert updated_incident["provider_workflow_action"] == "remediate"
    assert updated_incident["provider_workflow_state"] == "delivered"
    assert updated_incident["provider_workflow_reference"] == "PDINC-REC-901"
    resolved_incident = next(
      event
      for event in synced.json()["incident_events"]
      if event["kind"] == "incident_resolved" and event["alert_id"] == "guarded-live:market-data:5m"
    )
    assert resolved_incident["provider_workflow_action"] == "resolve"
    assert resolved_incident["provider_workflow_state"] in {"delivered", "not_supported"}
    assert resolved_incident["remediation"]["provider_payload"]["job_id"] == "provider-job-901"
    assert resolved_incident["remediation"]["provider_recovery"]["job_id"] == "provider-job-901"
    assert resolved_incident["remediation"]["provider_recovery"]["status_machine"]["state"] == "resolved"
    assert resolved_incident["remediation"]["provider_recovery"]["status_machine"]["workflow_action"] == "resolve"
    assert resolved_incident["remediation"]["provider_recovery"]["status_machine"]["job_state"] == "resolved"


def test_guarded_live_endpoint_pull_syncs_provider_authoritative_recovery_state(
  tmp_path: Path,
) -> None:
  class FakeProviderPullSyncAdapter:
    def __init__(self) -> None:
      self.pull_attempts: list[tuple[str, str, str | None]] = []

    def list_targets(self) -> tuple[str, ...]:
      return ("pagerduty_events",)

    def list_supported_workflow_providers(self) -> tuple[str, ...]:
      return ("pagerduty",)

    def deliver(
      self,
      *,
      incident: OperatorIncidentEvent,
      targets: tuple[str, ...] | None = None,
      attempt_number: int = 1,
      phase: str = "initial",
    ) -> tuple[OperatorIncidentDelivery, ...]:
      resolved_targets = targets or self.list_targets()
      return tuple(
        OperatorIncidentDelivery(
          delivery_id=f"{incident.event_id}:{target}:attempt-{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=target,
          status="delivered",
          attempted_at=incident.timestamp,
          detail=f"fake_delivery:{target}",
          attempt_number=attempt_number,
          phase=phase,
          external_provider="pagerduty",
          external_reference=incident.external_reference or incident.alert_id,
          source=incident.source,
        )
        for target in resolved_targets
      )

    def sync_incident_workflow(
      self,
      *,
      incident: OperatorIncidentEvent,
      provider: str,
      action: str,
      actor: str,
      detail: str,
      payload=None,
      attempt_number: int = 1,
    ) -> tuple[OperatorIncidentDelivery, ...]:
      return (
        OperatorIncidentDelivery(
          delivery_id=f"{incident.event_id}:{provider}_workflow:{action}:attempt-{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=f"{provider}_workflow",
          status="delivered",
          attempted_at=incident.timestamp,
          detail=f"fake_provider_workflow:{action}:{detail}",
          attempt_number=attempt_number,
          phase=f"provider_{action}",
          provider_action=action,
          external_provider=provider,
          external_reference=incident.provider_workflow_reference or incident.external_reference or incident.alert_id,
          source=incident.source,
        ),
      )

    def pull_incident_workflow_state(
      self,
      *,
      incident: OperatorIncidentEvent,
      provider: str,
    ):
      reference = incident.provider_workflow_reference or incident.external_reference
      self.pull_attempts.append((incident.event_id, provider, reference))
      if incident.alert_id != "guarded-live:market-data:5m":
        return None
      return OperatorIncidentProviderPullSync(
        provider="pagerduty",
        workflow_reference="PDINC-PULL-API-1",
        external_reference="guarded-live:market-data:5m",
        workflow_state="acknowledged",
        remediation_state="provider_recovered",
        detail="provider authoritatively completed recovery job",
        payload={
          "job_id": "pd-job-api-1",
          "channels": ["kline", "depth"],
          "targets": {"symbols": ["ETH/USDT"], "timeframe": "5m"},
          "market_context_provenance": {
            "provider": "pagerduty",
            "vendor_field": "custom_details",
            "symbols": {
              "scope": "provider_payload",
              "path": "custom_details.market_context.symbols",
            },
            "timeframe": {
              "scope": "provider_payload",
              "path": "custom_details.market_context.timeframe",
            },
          },
          "verification": {"state": "passed"},
          "status_machine": {
            "state": "provider_running",
            "workflow_state": "acknowledged",
            "workflow_action": "remediate",
            "job_state": "completed",
            "sync_state": "provider_authoritative",
          },
        },
        synced_at=datetime(2025, 1, 3, 18, 31, tzinfo=UTC),
      )

  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    pull_adapter = FakeProviderPullSyncAdapter()
    app._operator_alert_delivery = pull_adapter
    app._operator_alert_paging_policy_default_provider = "pagerduty"
    app._operator_alert_paging_policy_warning_targets = ("pagerduty_events",)
    app._operator_alert_paging_policy_critical_targets = ("pagerduty_events",)
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 30, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "provider_pull_sync_surface"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "provider_pull_sync_surface"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "provider_pull_sync_surface",
      },
    )
    assert live_response.status_code == 200
    market_data = StatusOverrideSeededMarketDataAdapter()
    market_data.set_status(
      timeframe="5m",
      status=MarketDataStatus(
        provider="binance",
        venue="binance",
        instruments=[
          InstrumentStatus(
            instrument_id="binance:ETH/USDT",
            timeframe="5m",
            candle_count=288,
            first_timestamp=datetime(2025, 1, 2, 18, 30, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 18, 10, tzinfo=UTC),
            sync_status="stale",
            lag_seconds=1_200,
            last_sync_at=datetime(2025, 1, 3, 18, 15, tzinfo=UTC),
            issues=("freshness_threshold_exceeded:1200:600",),
          ),
        ],
      ),
    )
    market_data.set_remediation_status(
      kind="recent_sync",
      timeframe="5m",
      status=MarketDataStatus(
        provider="binance",
        venue="binance",
        instruments=[
          InstrumentStatus(
            instrument_id="binance:ETH/USDT",
            timeframe="5m",
            candle_count=288,
            first_timestamp=datetime(2025, 1, 2, 18, 30, tzinfo=UTC),
            last_timestamp=datetime(2025, 1, 3, 18, 31, tzinfo=UTC),
            sync_status="synced",
            lag_seconds=0,
            last_sync_at=datetime(2025, 1, 3, 18, 31, tzinfo=UTC),
            issues=(),
          ),
        ],
      ),
    )
    app._market_data = market_data

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    opened_incident = next(
      event
      for event in guarded_live_response.json()["incident_events"]
      if event["kind"] == "incident_opened" and event["alert_id"] == "guarded-live:market-data:5m"
    )
    assert opened_incident["remediation"]["state"] == "executed"
    assert opened_incident["remediation"]["provider_recovery"]["job_id"] == "pd-job-api-1"
    assert opened_incident["remediation"]["provider_recovery"]["provider_schema_kind"] == "pagerduty"
    assert opened_incident["remediation"]["provider_recovery"]["pagerduty"]["incident_id"] == "PDINC-PULL-API-1"
    assert opened_incident["remediation"]["provider_recovery"]["pagerduty"]["incident_status"] == "acknowledged"
    assert opened_incident["remediation"]["provider_recovery"]["status_machine"]["workflow_state"] == "acknowledged"
    assert opened_incident["remediation"]["provider_recovery"]["status_machine"]["sync_state"] == "bidirectional_synced"
    assert opened_incident["remediation"]["provider_recovery"]["market_context_provenance"]["provider"] == "pagerduty"
    assert (
      opened_incident["remediation"]["provider_recovery"]["market_context_provenance"]["symbols"]["path"]
      == "custom_details.market_context.symbols"
    )
    assert any(
      event["kind"] == "incident_resolved" and event["alert_id"] == "guarded-live:market-data:5m"
      for event in guarded_live_response.json()["incident_events"]
    )
    assert all(
      alert["alert_id"] != "guarded-live:market-data:5m"
      for alert in guarded_live_response.json()["active_alerts"]
    )
    assert any(
      event["kind"] == "guarded_live_incident_provider_pull_synced"
      for event in guarded_live_response.json()["audit_events"]
    )
    assert any(
      attempt[0] == opened_incident["event_id"] and attempt[1] == "pagerduty"
      for attempt in pull_adapter.pull_attempts
    )


def test_operator_visibility_endpoint_surfaces_channel_level_market_data_incidents(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 19, 0, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "channel_level_incident_visibility",
      },
    )
    assert live_response.status_code == 200
    run_id = live_response.json()["config"]["run_id"]

    state = app._guarded_live_state.load_state()
    app._guarded_live_state.save_state(
      replace(
        state,
        session_handoff=replace(
          state.session_handoff,
          coverage=("trade_ticks", "depth_updates", "kline_candles"),
          handed_off_at=datetime(2025, 1, 3, 18, 58, tzinfo=UTC),
          last_sync_at=datetime(2025, 1, 3, 18, 58, tzinfo=UTC),
          last_trade_event_at=datetime(2025, 1, 3, 18, 58, tzinfo=UTC),
          last_depth_event_at=datetime(2025, 1, 3, 18, 58, tzinfo=UTC),
          last_kline_event_at=None,
          order_book_state="snapshot_rebuilt",
          order_book_gap_count=1,
          order_book_rebuild_count=2,
          order_book_last_update_id=34,
          order_book_last_rebuilt_at=datetime(2025, 1, 3, 18, 59, tzinfo=UTC),
          channel_restore_state="unavailable",
          channel_restore_count=2,
          channel_last_restored_at=datetime(2025, 1, 3, 18, 59, tzinfo=UTC),
          channel_continuation_state="unavailable",
          channel_continuation_count=2,
          channel_last_continued_at=datetime(2025, 1, 3, 18, 59, tzinfo=UTC),
          issues=(
            "binance_order_book_gap_detected:25:29",
            "binance_market_channel_restore_failed:ticker:timeout:exchange timeout",
          ),
        ),
      )
    )

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    alerts = visibility_response.json()["alerts"]
    categories = {
      alert["category"]
      for alert in alerts
      if alert.get("run_id") == run_id and alert.get("source") == "guarded_live"
    }
    assert not categories

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    consistency_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-channel-consistency:{run_id}"
    )
    assert "trade ticks is stale" in consistency_incident["detail"]
    assert "depth/order-book updates is stale" in consistency_incident["detail"]
    assert "kline candles has not produced any events within 45s" in consistency_incident["detail"]
    restore_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-channel-restore:{run_id}"
    )
    assert "market-channel restore is unavailable." in restore_incident["detail"]
    assert "market-channel continuation is unavailable." in restore_incident["detail"]
    assert "binance ticker restore failed: timeout:exchange timeout." in restore_incident["detail"]
    ladder_integrity_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-ladder-integrity:{run_id}"
    )
    assert "binance ladder integrity recorded 1 depth gap(s)." in ladder_integrity_incident["detail"]
    assert "binance ladder integrity required 2 snapshot rebuild(s)." in ladder_integrity_incident["detail"]
    assert "binance depth stream gap detected between update ids 25 and 29." in ladder_integrity_incident["detail"]


def test_operator_visibility_endpoint_separates_venue_native_ladder_integrity_incidents(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 19, 0, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "BTC/USD",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "venue_native_ladder_integrity_visibility",
      },
    )
    assert live_response.status_code == 200
    run_id = live_response.json()["config"]["run_id"]

    state = app._guarded_live_state.load_state()
    owner_session_id = (
      state.ownership.owner_session_id
      or state.session_handoff.owner_session_id
      or "worker-live-coinbase-market"
    )
    app._guarded_live_state.save_state(
      replace(
        state,
        ownership=replace(
          state.ownership,
          state="owned",
          owner_run_id=run_id,
          owner_session_id=owner_session_id,
        ),
        session_handoff=replace(
          state.session_handoff,
          state="active",
          venue="coinbase",
          owner_run_id=run_id,
          owner_session_id=owner_session_id,
          coverage=("depth_updates",),
          handed_off_at=datetime(2025, 1, 3, 18, 59, tzinfo=UTC),
          last_sync_at=datetime(2025, 1, 3, 18, 59, 40, tzinfo=UTC),
          last_depth_event_at=datetime(2025, 1, 3, 18, 59, 50, tzinfo=UTC),
          order_book_state="snapshot_rebuilt",
          order_book_gap_count=1,
          order_book_rebuild_count=1,
          order_book_last_update_id=34,
          order_book_last_rebuilt_at=datetime(2025, 1, 3, 18, 59, 45, tzinfo=UTC),
          issues=(
            "coinbase_order_book_gap_detected:25:29",
            "coinbase_order_book_snapshot_failed:session_missing:stream timeout",
            "coinbase_order_book_snapshot_crossed:2501.5:2501.2",
            "coinbase_order_book_snapshot_non_monotonic:bids:2:2501.3:2501.0",
          ),
        ),
      )
    )

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    alerts = visibility_response.json()["alerts"]
    categories = {
      alert["category"]
      for alert in alerts
      if alert.get("run_id") == run_id and alert.get("source") == "guarded_live"
    }
    assert not categories

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    ladder_integrity_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-ladder-integrity:{run_id}"
    )
    assert "coinbase ladder integrity recorded 1 depth gap(s)." in ladder_integrity_incident["detail"]
    assert "coinbase ladder integrity required 1 snapshot rebuild(s)." in ladder_integrity_incident["detail"]
    assert "coinbase depth stream gap detected between update ids 25 and 29." in ladder_integrity_incident["detail"]
    assert "snapshot rebuild failed" not in ladder_integrity_incident["detail"]
    venue_ladder_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-venue-ladder-integrity:{run_id}"
    )
    assert "coinbase ladder snapshot rebuild failed during session missing: stream timeout." in venue_ladder_incident["detail"]
    assert "coinbase ladder snapshot is crossed: best bid 2501.50000000 is above best ask 2501.20000000." in venue_ladder_incident["detail"]
    assert "coinbase bid ladder snapshot is not strictly descending at level 2 (2501.30000000 after 2501.00000000)." in venue_ladder_incident["detail"]


def test_operator_visibility_endpoint_separates_ladder_bridge_integrity_incidents(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 19, 5, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "exchange_specific_ladder_integrity_visibility",
      },
    )
    assert live_response.status_code == 200
    run_id = live_response.json()["config"]["run_id"]

    state = app._guarded_live_state.load_state()
    owner_session_id = (
      state.ownership.owner_session_id
      or state.session_handoff.owner_session_id
      or "worker-live-binance-market"
    )
    app._guarded_live_state.save_state(
      replace(
        state,
        ownership=replace(
          state.ownership,
          state="owned",
          owner_run_id=run_id,
          owner_session_id=owner_session_id,
        ),
        session_handoff=replace(
          state.session_handoff,
          state="active",
          venue="binance",
          owner_run_id=run_id,
          owner_session_id=owner_session_id,
          coverage=("depth_updates",),
          handed_off_at=datetime(2025, 1, 3, 19, 4, tzinfo=UTC),
          last_sync_at=datetime(2025, 1, 3, 19, 4, 40, tzinfo=UTC),
          last_depth_event_at=datetime(2025, 1, 3, 19, 4, 50, tzinfo=UTC),
          order_book_state="snapshot_rebuilt",
          order_book_gap_count=1,
          order_book_rebuild_count=1,
          order_book_last_update_id=34,
          order_book_last_rebuilt_at=datetime(2025, 1, 3, 19, 4, 45, tzinfo=UTC),
          issues=(
            "binance_order_book_gap_detected:25:29",
            "binance_order_book_bridge_previous_mismatch:25:29",
            "binance_order_book_bridge_range_mismatch:26:31:34",
          ),
        ),
      )
    )

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    alerts = visibility_response.json()["alerts"]
    categories = {
      alert["category"]
      for alert in alerts
      if alert.get("run_id") == run_id and alert.get("source") == "guarded_live"
    }
    assert not categories

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    ladder_integrity_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-ladder-integrity:{run_id}"
    )
    assert "binance ladder integrity recorded 1 depth gap(s)." in ladder_integrity_incident["detail"]
    assert "binance ladder integrity required 1 snapshot rebuild(s)." in ladder_integrity_incident["detail"]
    assert "binance depth stream gap detected between update ids 25 and 29." in ladder_integrity_incident["detail"]
    assert "bridge expected previous update id" not in ladder_integrity_incident["detail"]
    bridge_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-ladder-bridge:{run_id}"
    )
    assert "binance depth bridge expected previous update id 25 but received 29." in bridge_incident["detail"]
    assert "binance depth bridge range 31-34 does not cover expected next update id 26." in bridge_incident["detail"]


def test_operator_visibility_endpoint_separates_ladder_sequence_and_snapshot_refresh_incidents(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 19, 6, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "BTC/USD",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "ladder_sequence_snapshot_refresh_visibility",
      },
    )
    assert live_response.status_code == 200
    run_id = live_response.json()["config"]["run_id"]

    state = app._guarded_live_state.load_state()
    owner_session_id = (
      state.ownership.owner_session_id
      or state.session_handoff.owner_session_id
      or "worker-live-coinbase-sequence"
    )
    app._guarded_live_state.save_state(
      replace(
        state,
        ownership=replace(
          state.ownership,
          state="owned",
          owner_run_id=run_id,
          owner_session_id=owner_session_id,
        ),
        session_handoff=replace(
          state.session_handoff,
          state="active",
          venue="coinbase",
          owner_run_id=run_id,
          owner_session_id=owner_session_id,
          coverage=("depth_updates",),
          handed_off_at=datetime(2025, 1, 3, 19, 5, tzinfo=UTC),
          last_sync_at=datetime(2025, 1, 3, 19, 5, 40, tzinfo=UTC),
          last_depth_event_at=datetime(2025, 1, 3, 19, 5, 50, tzinfo=UTC),
          order_book_state="snapshot_rebuilt",
          order_book_gap_count=0,
          order_book_rebuild_count=1,
          order_book_last_update_id=704,
          order_book_last_rebuilt_at=datetime(2025, 1, 3, 19, 5, 45, tzinfo=UTC),
          issues=(
            "coinbase_order_book_sequence_mismatch:701:703:704",
            "coinbase_order_book_snapshot_refresh:700:701",
          ),
        ),
      )
    )

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    alerts = visibility_response.json()["alerts"]
    categories = {
      alert["category"]
      for alert in alerts
      if alert.get("run_id") == run_id and alert.get("source") == "guarded_live"
    }
    assert not categories

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    sequence_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-ladder-sequence:{run_id}"
    )
    assert "coinbase ladder sequence expected previous update id 701 but received 703 before update 704." in sequence_incident["detail"]
    snapshot_refresh_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-ladder-snapshot-refresh:{run_id}"
    )
    assert "coinbase ladder snapshot refresh replaced update id 700 with 701." in snapshot_refresh_incident["detail"]


def test_operator_visibility_endpoint_surfaces_book_and_kline_consistency_incidents(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 19, 30, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "book_kline_consistency_visibility",
      },
    )
    assert live_response.status_code == 200
    run_id = live_response.json()["config"]["run_id"]

    state = app._guarded_live_state.load_state()
    app._guarded_live_state.save_state(
      replace(
        state,
        session_handoff=replace(
          state.session_handoff,
          coverage=("book_ticker", "depth_updates", "kline_candles"),
          last_sync_at=datetime(2025, 1, 3, 19, 30, tzinfo=UTC),
          last_depth_event_at=datetime(2025, 1, 3, 19, 29, 55, tzinfo=UTC),
          last_book_ticker_event_at=datetime(2025, 1, 3, 19, 29, 55, tzinfo=UTC),
          last_kline_event_at=datetime(2025, 1, 3, 19, 29, 55, tzinfo=UTC),
          order_book_state="streaming",
          order_book_best_bid_price=2501.2,
          order_book_best_ask_price=2500.8,
          order_book_bid_level_count=2,
          order_book_ask_level_count=2,
          book_ticker_snapshot=GuardedLiveBookTickerChannelSnapshot(
            bid_price=2501.1,
            bid_quantity=1.0,
            ask_price=2500.9,
            ask_quantity=0.9,
            event_at=datetime(2025, 1, 3, 19, 29, 55, tzinfo=UTC),
          ),
          kline_snapshot=GuardedLiveKlineChannelSnapshot(
            timeframe="1m",
            open_at=datetime(2025, 1, 3, 19, 25, tzinfo=UTC),
            close_at=datetime(2025, 1, 3, 19, 24, tzinfo=UTC),
            open_price=2499.5,
            high_price=2500.0,
            low_price=2499.0,
            close_price=2501.0,
            volume=4.2,
            closed=True,
            event_at=datetime(2025, 1, 3, 19, 29, 55, tzinfo=UTC),
          ),
        ),
      )
    )

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    alerts = visibility_response.json()["alerts"]
    categories = {
      alert["category"]
      for alert in alerts
      if alert.get("run_id") == run_id and alert.get("source") == "guarded_live"
    }
    assert not categories

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    book_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-book-consistency:{run_id}"
    )
    assert "binance local order book is crossed: best bid 2501.20000000 is above best ask 2500.80000000." in book_incident["detail"]
    assert "binance book-ticker quote is crossed: bid 2501.10000000 is above ask 2500.90000000." in book_incident["detail"]
    assert "binance local best bid 2501.20000000 is above book-ticker ask 2500.90000000." in book_incident["detail"]
    kline_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-kline-consistency:{run_id}"
    )
    assert "binance kline timeframe 1m does not match the guarded-live timeframe 5m." in kline_incident["detail"]
    assert "binance kline closes at" in kline_incident["detail"]
    assert "binance kline close 2501.00000000 falls outside the high/low range 2499.00000000-2500.00000000." in kline_incident["detail"]


def test_operator_visibility_endpoint_splits_depth_ladder_and_candle_sequence_incidents(
  tmp_path: Path,
) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 20, 0, tzinfo=UTC),
        balances=(GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),),
      )
    )
    client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "depth_ladder_candle_sequence_visibility",
      },
    )
    assert live_response.status_code == 200
    run_id = live_response.json()["config"]["run_id"]

    state = app._guarded_live_state.load_state()
    app._guarded_live_state.save_state(
      replace(
        state,
        session_handoff=replace(
          state.session_handoff,
          coverage=("depth_updates", "kline_candles"),
          last_sync_at=datetime(2025, 1, 3, 20, 0, tzinfo=UTC),
          last_depth_event_at=datetime(2025, 1, 3, 19, 59, 55, tzinfo=UTC),
          last_kline_event_at=datetime(2025, 1, 3, 19, 59, 55, tzinfo=UTC),
          order_book_state="streaming",
          order_book_bid_level_count=3,
          order_book_ask_level_count=2,
          order_book_best_bid_price=2501.2,
          order_book_best_bid_quantity=1.0,
          order_book_best_ask_price=2501.5,
          order_book_best_ask_quantity=0.6,
          order_book_bids=(
            GuardedLiveOrderBookLevel(price=2501.0, quantity=0.5),
            GuardedLiveOrderBookLevel(price=2501.3, quantity=0.4),
          ),
          order_book_asks=(
            GuardedLiveOrderBookLevel(price=2501.5, quantity=0.6),
            GuardedLiveOrderBookLevel(price=2501.7, quantity=0.8),
          ),
          kline_snapshot=GuardedLiveKlineChannelSnapshot(
            timeframe="5m",
            open_at=datetime(2025, 1, 3, 19, 26, tzinfo=UTC),
            close_at=datetime(2025, 1, 3, 19, 29, tzinfo=UTC),
            open_price=2499.2,
            high_price=2500.0,
            low_price=2499.0,
            close_price=2499.6,
            volume=3.2,
            closed=True,
            event_at=datetime(2025, 1, 3, 19, 28, tzinfo=UTC),
          ),
        ),
      )
    )

    visibility_response = client.get("/api/operator/visibility")
    assert visibility_response.status_code == 200
    alerts = visibility_response.json()["alerts"]
    categories = {
      alert["category"]
      for alert in alerts
      if alert.get("run_id") == run_id and alert.get("source") == "guarded_live"
    }
    assert not categories

    guarded_live_response = client.get("/api/guarded-live")
    assert guarded_live_response.status_code == 200
    incident_events = guarded_live_response.json()["incident_events"]
    depth_ladder_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-depth-ladder:{run_id}"
    )
    assert "binance bid ladder count 2 does not match stored bid level count 3." in depth_ladder_incident["detail"]
    assert "binance best bid ladder head 2501.00000000/0.50000000 does not match stored best bid 2501.20000000/1.00000000." in depth_ladder_incident["detail"]
    assert "binance bid ladder is not strictly descending at level 2 (2501.30000000 after 2501.00000000)." in depth_ladder_incident["detail"]
    candle_sequence_incident = next(
      event for event in incident_events
      if event["kind"] == "incident_opened"
      and event["alert_id"] == f"guarded-live:market-data-candle-sequence:{run_id}"
    )
    assert "binance kline open 2025-01-03T19:26:00+00:00 is not aligned to the 5m timeframe boundary." in candle_sequence_incident["detail"]
    assert "binance kline close 2025-01-03T19:29:00+00:00 does not match the expected 5m boundary close 2025-01-03T19:31:00+00:00." in candle_sequence_incident["detail"]
    assert "binance closed kline event arrived at 2025-01-03T19:28:00+00:00 before the candle close 2025-01-03T19:29:00+00:00." in candle_sequence_incident["detail"]


def test_live_endpoints_use_configured_supported_guarded_live_venue(tmp_path: Path) -> None:
  with build_client(
    tmp_path / "runs.sqlite3",
    guarded_live_execution_enabled=True,
    guarded_live_venue="coinbase",
  ) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="coinbase",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 18, 15, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="ETH", total=0.4, free=0.4, used=0.0),
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=10_000.0, used=0.0),
        ),
      )
    )
    app._venue_execution = SeededVenueExecutionAdapter(venue="coinbase")

    reconcile_response = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "coinbase_pre_live_check"},
    )
    assert reconcile_response.status_code == 200
    assert reconcile_response.json()["reconciliation"]["venue_snapshot"]["venue"] == "coinbase"

    recovery_response = client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "coinbase_pre_live_recovery"},
    )
    assert recovery_response.status_code == 200
    recovery_payload = recovery_response.json()
    assert recovery_payload["recovery"]["exposures"][0]["instrument_id"] == "coinbase:ETH/USDT"

    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "coinbase_guarded_live_launch",
      },
    )

  assert live_response.status_code == 200
  payload = live_response.json()
  assert payload["config"]["mode"] == "live"
  assert payload["config"]["venue"] == "coinbase"


def test_live_run_payload_exposes_synced_order_lifecycle(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    venue_execution = app._venue_execution
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 19, 0, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=9_000.0, used=1_000.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id="venue-open-order-1",
            symbol="ETH/USDT",
            side="buy",
            amount=0.5,
            status="open",
            price=2_000.0,
          ),
        ),
      )
    )

    reconcile_response = client.post(
      "/api/guarded-live/reconciliation",
      json={"actor": "operator", "reason": "pre_live_check"},
    )
    assert reconcile_response.status_code == 200

    recovery_response = client.post(
      "/api/guarded-live/recovery",
      json={"actor": "operator", "reason": "pre_live_recovery"},
    )
    assert recovery_response.status_code == 200

    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "sync_payload_test",
      },
    )
    assert live_response.status_code == 200
    run_id = live_response.json()["config"]["run_id"]

    venue_execution.set_order_state(
      "venue-open-order-1",
      symbol="ETH/USDT",
      side="buy",
      amount=0.5,
      status="partially_filled",
      average_fill_price=2_010.0,
      fee_paid=0.2,
      filled_amount=0.2,
      remaining_amount=0.3,
    )
    app.maintain_guarded_live_worker_sessions()

    runs_response = client.get("/api/runs?mode=live")

  assert runs_response.status_code == 200
  payload = runs_response.json()
  assert len(payload) == 1
  live_run = payload[0]
  assert live_run["config"]["run_id"] == run_id
  assert live_run["orders"][0]["status"] == "partially_filled"
  assert live_run["orders"][0]["filled_quantity"] == 0.2
  assert live_run["orders"][0]["remaining_quantity"] == 0.3
  assert live_run["orders"][0]["last_synced_at"] is not None


def test_live_order_cancel_endpoint_marks_active_order_canceled(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 20, 30, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=9_000.0, used=1_000.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id="venue-open-order-1",
            symbol="ETH/USDT",
            side="buy",
            amount=0.5,
            status="open",
            price=2_000.0,
          ),
        ),
      )
    )

    client.post("/api/guarded-live/reconciliation", json={"actor": "operator", "reason": "pre_live_check"})
    client.post("/api/guarded-live/recovery", json={"actor": "operator", "reason": "pre_live_recovery"})
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "cancel_payload_test",
      },
    )
    run_id = live_response.json()["config"]["run_id"]

    cancel_response = client.post(
      f"/api/runs/live/{run_id}/orders/venue-open-order-1/cancel",
      json={"actor": "operator", "reason": "reduce_venue_risk"},
    )

  assert cancel_response.status_code == 200
  payload = cancel_response.json()
  assert payload["orders"][0]["order_id"] == "venue-open-order-1"
  assert payload["orders"][0]["status"] == "canceled"
  assert payload["orders"][0]["action_availability"]["cancel"]["allowed"] is False
  assert payload["orders"][0]["action_availability"]["replace"]["allowed"] is False


def test_live_order_cancel_endpoint_rejects_when_order_surface_rule_is_disabled(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 20, 35, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=9_000.0, used=1_000.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id="venue-open-order-1",
            symbol="ETH/USDT",
            side="buy",
            amount=0.5,
            status="open",
            price=2_000.0,
          ),
        ),
      )
    )

    client.post("/api/guarded-live/reconciliation", json={"actor": "operator", "reason": "pre_live_check"})
    client.post("/api/guarded-live/recovery", json={"actor": "operator", "reason": "pre_live_recovery"})
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "cancel_surface_rule_test",
      },
    )
    run_id = live_response.json()["config"]["run_id"]
    base_capabilities = app.get_run_surface_capabilities()
    app.get_run_surface_capabilities = lambda: without_surface_rule(
      base_capabilities,
      family_key="execution_controls",
      surface_key="order_replace_cancel_actions",
    )

    cancel_response = client.post(
      f"/api/runs/live/{run_id}/orders/venue-open-order-1/cancel",
      json={"actor": "operator", "reason": "reduce_venue_risk"},
    )

  assert cancel_response.status_code == 400
  assert cancel_response.json()["detail"] == (
    "Surface rule order_replace_cancel_actions is disabled by the run-surface capability contract."
  )


def test_live_order_replace_endpoint_appends_repriced_limit_order(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 20, 45, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=9_000.0, used=1_000.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id="venue-open-order-1",
            symbol="ETH/USDT",
            side="buy",
            amount=0.5,
            status="open",
            price=2_000.0,
          ),
        ),
      )
    )

    client.post("/api/guarded-live/reconciliation", json={"actor": "operator", "reason": "pre_live_check"})
    client.post("/api/guarded-live/recovery", json={"actor": "operator", "reason": "pre_live_recovery"})
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "replace_payload_test",
      },
    )
    run_id = live_response.json()["config"]["run_id"]

    replace_response = client.post(
      f"/api/runs/live/{run_id}/orders/venue-open-order-1/replace",
      json={
        "actor": "operator",
        "reason": "reprice_remaining_order",
        "price": 1985.0,
        "quantity": 0.3,
      },
    )

  assert replace_response.status_code == 200
  payload = replace_response.json()
  assert len(payload["orders"]) == 2
  assert payload["orders"][0]["status"] == "canceled"
  assert payload["orders"][1]["order_type"] == "limit"
  assert payload["orders"][1]["status"] == "open"
  assert payload["orders"][1]["requested_price"] == 1985.0
  assert payload["orders"][1]["quantity"] == 0.3


def test_run_orders_endpoint_returns_surface_rule_metadata(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 20, 50, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=9_000.0, used=1_000.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id="venue-open-order-1",
            symbol="ETH/USDT",
            side="buy",
            amount=0.5,
            status="open",
            price=2_000.0,
          ),
        ),
      )
    )

    client.post("/api/guarded-live/reconciliation", json={"actor": "operator", "reason": "pre_live_check"})
    client.post("/api/guarded-live/recovery", json={"actor": "operator", "reason": "pre_live_recovery"})
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "order_list_surface_metadata_test",
      },
    )
    run_id = live_response.json()["config"]["run_id"]

    orders_response = client.get(f"/api/runs/{run_id}/orders")

  assert orders_response.status_code == 200
  payload = orders_response.json()
  assert payload["run_id"] == run_id
  assert payload["run_mode"] == "live"
  assert payload["run_status"] == "running"
  assert payload["surface_enforcement"]["order_replace_cancel_actions"]["enabled"] is True
  assert payload["action_availability"]["stop_run"]["allowed"] is True
  assert len(payload["orders"]) == 1
  assert payload["orders"][0]["order_id"] == "venue-open-order-1"
  assert payload["orders"][0]["action_availability"]["cancel"]["allowed"] is True
  assert payload["orders"][0]["action_availability"]["replace"]["allowed"] is True


def test_run_orders_endpoint_applies_surface_rule_contract_to_order_actions(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3", guarded_live_execution_enabled=True) as client:
    app = client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 20, 55, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=9_000.0, used=1_000.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id="venue-open-order-1",
            symbol="ETH/USDT",
            side="buy",
            amount=0.5,
            status="open",
            price=2_000.0,
          ),
        ),
      )
    )

    client.post("/api/guarded-live/reconciliation", json={"actor": "operator", "reason": "pre_live_check"})
    client.post("/api/guarded-live/recovery", json={"actor": "operator", "reason": "pre_live_recovery"})
    live_response = client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "order_list_surface_rule_override_test",
      },
    )
    run_id = live_response.json()["config"]["run_id"]
    base_capabilities = app.get_run_surface_capabilities()
    app.get_run_surface_capabilities = lambda: without_surface_rule(
      base_capabilities,
      family_key="execution_controls",
      surface_key="order_replace_cancel_actions",
    )

    orders_response = client.get(f"/api/runs/{run_id}/orders")

  assert orders_response.status_code == 200
  payload = orders_response.json()
  assert payload["surface_enforcement"]["order_replace_cancel_actions"]["enabled"] is False
  assert payload["surface_enforcement"]["order_replace_cancel_actions"]["reason"] == (
    "Surface rule order_replace_cancel_actions is disabled by the run-surface capability contract."
  )
  assert payload["orders"][0]["action_availability"]["cancel"]["allowed"] is False
  assert payload["orders"][0]["action_availability"]["replace"]["allowed"] is False
  assert payload["orders"][0]["action_availability"]["cancel"]["reason"] == (
    "Surface rule order_replace_cancel_actions is disabled by the run-surface capability contract."
  )


def test_run_positions_and_metrics_endpoints_return_surface_rule_metadata(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    run_response = client.post(
      "/api/runs/backtests",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "BTC/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
      },
    )
    run_id = run_response.json()["config"]["run_id"]

    positions_response = client.get(f"/api/runs/{run_id}/positions")
    metrics_response = client.get(f"/api/runs/{run_id}/metrics")

  assert positions_response.status_code == 200
  positions_payload = positions_response.json()
  assert positions_payload["run_id"] == run_id
  assert positions_payload["run_mode"] == "backtest"
  assert positions_payload["run_status"] == "completed"
  assert positions_payload["surface_enforcement"]["run_list_metric_tiles"]["enabled"] is True
  assert positions_payload["action_availability"]["compare_select"]["allowed"] is True
  assert positions_payload["action_availability"]["stop_run"]["allowed"] is False
  assert isinstance(positions_payload["positions"], list)

  assert metrics_response.status_code == 200
  metrics_payload = metrics_response.json()
  assert metrics_payload["run_id"] == run_id
  assert metrics_payload["run_mode"] == "backtest"
  assert metrics_payload["run_status"] == "completed"
  assert metrics_payload["surface_enforcement"]["run_list_metric_tiles"]["enabled"] is True
  assert metrics_payload["action_availability"]["rerun_backtest"]["allowed"] is True
  assert "total_return_pct" in metrics_payload["metrics"]


def test_run_positions_and_metrics_endpoints_apply_surface_rule_overrides(tmp_path: Path) -> None:
  with build_client(tmp_path / "runs.sqlite3") as client:
    app = client.app.state.container.app
    run_response = client.post(
      "/api/runs/backtests",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "BTC/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
      },
    )
    run_id = run_response.json()["config"]["run_id"]
    base_capabilities = app.get_run_surface_capabilities()
    app.get_run_surface_capabilities = lambda: without_surface_rule(
      without_surface_rule(
        base_capabilities,
        family_key="comparison_eligibility",
        surface_key="run_list_metric_tiles",
      ),
      family_key="execution_controls",
      surface_key="compare_selection_workflow",
    )

    positions_response = client.get(f"/api/runs/{run_id}/positions")
    metrics_response = client.get(f"/api/runs/{run_id}/metrics")

  assert positions_response.status_code == 200
  positions_payload = positions_response.json()
  assert positions_payload["surface_enforcement"]["run_list_metric_tiles"]["enabled"] is False
  assert positions_payload["surface_enforcement"]["compare_selection_workflow"]["enabled"] is False
  assert positions_payload["action_availability"]["compare_select"]["allowed"] is False
  assert positions_payload["action_availability"]["compare_select"]["reason"] == (
    "Surface rule compare_selection_workflow is disabled by the run-surface capability contract."
  )

  assert metrics_response.status_code == 200
  metrics_payload = metrics_response.json()
  assert metrics_payload["surface_enforcement"]["run_list_metric_tiles"]["enabled"] is False
  assert metrics_payload["surface_enforcement"]["compare_selection_workflow"]["enabled"] is False
  assert metrics_payload["action_availability"]["compare_select"]["allowed"] is False
  assert metrics_payload["metrics"]["trade_count"] >= 0


def test_guarded_live_status_and_resume_expose_ownership_and_order_book(tmp_path: Path) -> None:
  database_path = tmp_path / "runs.sqlite3"

  with build_client(database_path, guarded_live_execution_enabled=True) as first_client:
    app = first_client.app.state.container.app
    app._venue_state = StaticVenueStateAdapter(
      GuardedLiveVenueStateSnapshot(
        provider="seeded",
        venue="binance",
        verification_state="verified",
        captured_at=datetime(2025, 1, 3, 21, 0, tzinfo=UTC),
        balances=(
          GuardedLiveVenueBalance(asset="USDT", total=10_000.0, free=9_000.0, used=1_000.0),
        ),
        open_orders=(
          GuardedLiveVenueOpenOrder(
            order_id="venue-open-order-1",
            symbol="ETH/USDT",
            side="buy",
            amount=0.5,
            status="open",
            price=2_000.0,
          ),
        ),
      )
    )
    first_client.post("/api/guarded-live/reconciliation", json={"actor": "operator", "reason": "pre_live_check"})
    first_client.post("/api/guarded-live/recovery", json={"actor": "operator", "reason": "pre_live_recovery"})
    live_response = first_client.post(
      "/api/runs/live",
      json={
        "strategy_id": "ma_cross_v1",
        "symbol": "ETH/USDT",
        "timeframe": "5m",
        "initial_cash": 10_000,
        "fee_rate": 0.001,
        "slippage_bps": 3,
        "parameters": {},
        "replay_bars": 24,
        "operator_reason": "owned_session_start",
      },
    )
    run_id = live_response.json()["config"]["run_id"]

    status_response = first_client.get("/api/guarded-live")

  assert status_response.status_code == 200
  status_payload = status_response.json()
  assert status_payload["ownership"]["state"] == "owned"
  assert status_payload["ownership"]["owner_run_id"] == run_id
  assert status_payload["order_book"]["open_orders"][0]["order_id"] == "venue-open-order-1"
  assert status_payload["session_handoff"]["state"] == "active"
  assert status_payload["session_handoff"]["transport"] == "seeded_stream"

  with build_client(database_path, guarded_live_execution_enabled=True) as restarted_client:
    restarted_client.app.state.container.app._venue_execution = SeededVenueExecutionAdapter(
      restored_orders=(
        GuardedLiveVenueOrderResult(
          order_id="venue-open-order-1",
          venue="binance",
          symbol="ETH/USDT",
          side="buy",
          amount=0.5,
          status="partially_filled",
          submitted_at=datetime(2025, 1, 3, 21, 0, tzinfo=UTC),
          updated_at=datetime(2025, 1, 3, 21, 5, tzinfo=UTC),
          requested_price=2_000.0,
          average_fill_price=1_998.0,
          fee_paid=0.2,
          requested_amount=0.5,
          filled_amount=0.2,
          remaining_amount=0.3,
        ),
      )
    )
    resume_response = restarted_client.post(
      "/api/guarded-live/resume",
      json={"actor": "operator", "reason": "process_restart_resume"},
    )
    resumed_status_response = restarted_client.get("/api/guarded-live")

  assert resume_response.status_code == 200
  resume_payload = resume_response.json()
  assert resume_payload["config"]["run_id"] == run_id
  assert resume_payload["status"] == "running"
  assert resume_payload["provenance"]["runtime_session"]["recovery_count"] >= 1
  assert resume_payload["orders"][0]["status"] == "partially_filled"
  assert resume_payload["orders"][0]["filled_quantity"] == 0.2
  assert resume_payload["orders"][0]["remaining_quantity"] == 0.3
  assert resumed_status_response.status_code == 200
  resumed_status_payload = resumed_status_response.json()
  assert resumed_status_payload["session_restore"]["state"] == "restored"
  assert resumed_status_payload["session_restore"]["source"] == "seeded_venue_execution"
  assert resumed_status_payload["session_restore"]["owner_run_id"] == run_id
  assert resumed_status_payload["session_handoff"]["state"] == "active"
  assert resumed_status_payload["session_handoff"]["transport"] == "seeded_stream"
  assert resumed_status_payload["session_handoff"]["owner_run_id"] == run_id
  assert resumed_status_payload["order_book"]["open_orders"][0]["amount"] == 0.3


def test_runs_endpoint_can_filter_by_strategy_version(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  native_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert native_response.status_code == 200

  reference_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "nfi_x7_reference",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert reference_response.status_code == 200

  filtered = client.get("/api/runs?mode=backtest&strategy_id=ma_cross_v1&strategy_version=1.0.0")

  assert filtered.status_code == 200
  payload = filtered.json()
  assert len(payload) == 1
  assert "eligibility_contract" not in payload[0]
  assert payload[0]["config"]["strategy_id"] == "ma_cross_v1"
  assert payload[0]["config"]["strategy_version"] == "1.0.0"


def test_runs_endpoint_can_filter_by_experiment_metadata(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  create_preset(
    client,
    name="Core 5m",
    preset_id="core_5m",
    strategy_id="ma_cross_v1",
    timeframe="5m",
    benchmark_family="native_validation",
  )
  create_preset(
    client,
    name="Tuned 5m",
    preset_id="tuned_5m",
    strategy_id="ma_cross_v1",
    timeframe="5m",
    benchmark_family="native_tuning",
  )

  baseline_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "tags": ["baseline", "momentum"],
      "preset_id": "core_5m",
      "benchmark_family": "native_validation",
    },
  )
  assert baseline_response.status_code == 200
  baseline_payload = baseline_response.json()
  dataset_identity = baseline_payload["provenance"]["market_data"]["dataset_identity"]

  alternate_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {"short_window": 13},
      "tags": ["alternate"],
      "preset_id": "tuned_5m",
      "benchmark_family": "native_tuning",
    },
  )
  assert alternate_response.status_code == 200

  filtered = client.get(
    f"/api/runs?mode=backtest&preset_id=core_5m&benchmark_family=native_validation&tag=baseline&tag=momentum&dataset_identity={dataset_identity}"
  )

  assert filtered.status_code == 200
  payload = filtered.json()
  assert len(payload) == 1
  assert payload[0]["config"]["run_id"] == baseline_payload["config"]["run_id"]
  assert payload[0]["provenance"]["experiment"]["preset_id"] == "core_5m"
  assert payload[0]["provenance"]["experiment"]["tags"] == ["baseline", "momentum"]


def test_runs_endpoint_can_filter_by_rerun_boundary_id(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  first_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert first_response.status_code == 200
  rerun_boundary_id = first_response.json()["provenance"]["rerun_boundary_id"]

  second_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert second_response.status_code == 200

  other_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 12000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
    },
  )
  assert other_response.status_code == 200

  filtered = client.get(f"/api/runs?rerun_boundary_id={rerun_boundary_id}")

  assert filtered.status_code == 200
  payload = filtered.json()
  assert len(payload) == 2
  assert all(item["provenance"]["rerun_boundary_id"] == rerun_boundary_id for item in payload)


def test_runs_endpoint_filters_paper_history_separately_from_sandbox(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  sandbox_response = client.post(
    "/api/runs/sandbox",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "ETH/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "replay_bars": 24,
    },
  )
  assert sandbox_response.status_code == 200

  paper_response = client.post(
    "/api/runs/paper",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "ETH/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "replay_bars": 24,
    },
  )
  assert paper_response.status_code == 200

  sandbox_filtered = client.get("/api/runs?mode=sandbox")
  paper_filtered = client.get("/api/runs?mode=paper")

  assert sandbox_filtered.status_code == 200
  assert paper_filtered.status_code == 200
  assert [item["config"]["mode"] for item in sandbox_filtered.json()] == ["sandbox"]
  assert [item["config"]["mode"] for item in paper_filtered.json()] == ["paper"]


def test_rerun_boundary_endpoint_creates_backtest_from_stored_boundary(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  source_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {"short_window": 13},
      "start_at": "2025-01-01T04:00:00Z",
      "end_at": "2025-01-01T12:00:00Z",
    },
  )
  assert source_response.status_code == 200
  source_payload = source_response.json()
  rerun_boundary_id = source_payload["provenance"]["rerun_boundary_id"]

  rerun_response = client.post(f"/api/runs/rerun-boundaries/{rerun_boundary_id}/backtests")

  assert rerun_response.status_code == 200
  rerun_payload = rerun_response.json()
  assert rerun_payload["config"]["run_id"] != source_payload["config"]["run_id"]
  assert rerun_payload["provenance"]["rerun_source_run_id"] == source_payload["config"]["run_id"]
  assert rerun_payload["provenance"]["rerun_target_boundary_id"] == rerun_boundary_id
  assert rerun_payload["provenance"]["rerun_match_status"] == "matched"
  assert rerun_payload["provenance"]["rerun_validation_category"] == "exact_match"
  assert rerun_payload["provenance"]["rerun_validation_summary"] == (
    "Exact dataset boundary matched the stored rerun boundary."
  )
  assert rerun_payload["provenance"]["lineage_summary"]["status"] == "clear"
  assert rerun_payload["provenance"]["lineage_summary"]["posture"] == "exact-match"
  assert rerun_payload["provenance"]["rerun_boundary_id"] == rerun_boundary_id
  assert rerun_payload["provenance"]["market_data"]["effective_start_at"] == source_payload["provenance"]["market_data"]["effective_start_at"]
  assert rerun_payload["provenance"]["market_data"]["effective_end_at"] == source_payload["provenance"]["market_data"]["effective_end_at"]
  assert rerun_payload["provenance"]["strategy"]["parameter_snapshot"]["resolved"] == {
    "short_window": 13,
    "long_window": 21,
  }


def test_rerun_boundary_endpoint_creates_sandbox_run_from_stored_boundary(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  source_response = client.post(
    "/api/runs/sandbox",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "ETH/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "replay_bars": 24,
    },
  )
  assert source_response.status_code == 200
  source_payload = source_response.json()
  rerun_boundary_id = source_payload["provenance"]["rerun_boundary_id"]

  rerun_response = client.post(f"/api/runs/rerun-boundaries/{rerun_boundary_id}/sandbox")

  assert rerun_response.status_code == 200
  rerun_payload = rerun_response.json()
  assert rerun_payload["config"]["run_id"] != source_payload["config"]["run_id"]
  assert rerun_payload["config"]["mode"] == "sandbox"
  assert rerun_payload["status"] == "running"
  assert rerun_payload["provenance"]["rerun_source_run_id"] == source_payload["config"]["run_id"]
  assert rerun_payload["provenance"]["rerun_target_boundary_id"] == rerun_boundary_id
  assert rerun_payload["provenance"]["rerun_match_status"] == "matched"
  assert rerun_payload["provenance"]["rerun_validation_category"] == "exact_match"
  assert rerun_payload["provenance"]["rerun_boundary_id"] == rerun_boundary_id
  assert rerun_payload["provenance"]["market_data"]["effective_start_at"] == source_payload["provenance"]["market_data"]["effective_start_at"]
  assert rerun_payload["provenance"]["market_data"]["effective_end_at"] == source_payload["provenance"]["market_data"]["effective_end_at"]


def test_rerun_boundary_paper_endpoint_replays_boundary_with_expected_mode_drift(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  source_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {"short_window": 13},
      "start_at": "2025-01-01T04:00:00Z",
      "end_at": "2025-01-01T12:00:00Z",
    },
  )
  assert source_response.status_code == 200
  source_payload = source_response.json()
  rerun_boundary_id = source_payload["provenance"]["rerun_boundary_id"]

  rerun_response = client.post(f"/api/runs/rerun-boundaries/{rerun_boundary_id}/paper")

  assert rerun_response.status_code == 200
  rerun_payload = rerun_response.json()
  assert rerun_payload["config"]["mode"] == "paper"
  assert rerun_payload["status"] == "running"
  assert rerun_payload["provenance"]["rerun_source_run_id"] == source_payload["config"]["run_id"]
  assert rerun_payload["provenance"]["rerun_target_boundary_id"] == rerun_boundary_id
  assert rerun_payload["provenance"]["rerun_match_status"] == "drifted"
  assert rerun_payload["provenance"]["rerun_validation_category"] == "mode_translation"
  assert rerun_payload["provenance"]["rerun_validation_summary"] == (
    "Dataset boundary matched, but the rerun translated it into a different execution mode."
  )
  assert rerun_payload["provenance"]["lineage_summary"]["status"] == "review"
  assert rerun_payload["provenance"]["lineage_summary"]["posture"] == "drift-aware"
  assert rerun_payload["provenance"]["lineage_summary"]["title"] == "Expected mode translation"
  assert rerun_payload["provenance"]["market_data"]["effective_start_at"] == source_payload["provenance"]["market_data"]["effective_start_at"]
  assert rerun_payload["provenance"]["market_data"]["effective_end_at"] == source_payload["provenance"]["market_data"]["effective_end_at"]


def test_rerun_boundary_endpoint_returns_not_found_for_unknown_boundary(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")

  response = client.post("/api/runs/rerun-boundaries/rerun-v1:missing/backtests")

  assert response.status_code == 404

  sandbox_response = client.post("/api/runs/rerun-boundaries/rerun-v1:missing/sandbox")

  assert sandbox_response.status_code == 404


def test_compare_runs_endpoint_returns_native_and_reference_benchmark_payload(tmp_path: Path) -> None:
  client = build_client(tmp_path / "runs.sqlite3")
  create_preset(
    client,
    name="Core 5m",
    preset_id="core_5m",
    strategy_id="ma_cross_v1",
    timeframe="5m",
  )
  create_preset(
    client,
    name="NFI baseline",
    preset_id="nfi_baseline",
    strategy_id="nfi_x7_reference",
    timeframe="5m",
  )

  native_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "ma_cross_v1",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "tags": ["baseline"],
      "preset_id": "core_5m",
    },
  )
  assert native_response.status_code == 200
  native_run_id = native_response.json()["config"]["run_id"]

  reference_response = client.post(
    "/api/runs/backtests",
    json={
      "strategy_id": "nfi_x7_reference",
      "symbol": "BTC/USDT",
      "timeframe": "5m",
      "initial_cash": 10000,
      "fee_rate": 0.001,
      "slippage_bps": 3,
      "parameters": {},
      "tags": ["reference"],
      "preset_id": "nfi_baseline",
    },
  )
  assert reference_response.status_code == 200
  reference_run_id = reference_response.json()["config"]["run_id"]

  comparison_response = client.get(
    f"/api/runs/compare?run_id={native_run_id}&run_id={reference_run_id}&intent=strategy_tuning"
  )

  assert comparison_response.status_code == 200
  payload = comparison_response.json()
  assert payload["intent"] == "strategy_tuning"
  assert payload["baseline_run_id"] == native_run_id
  assert [run["lane"] for run in payload["runs"]] == ["native", "reference"]
  assert payload["runs"][0]["experiment"]["preset_id"] == "core_5m"
  assert payload["runs"][0]["experiment"]["tags"] == ["baseline"]
  assert payload["runs"][0]["catalog_semantics"]["strategy_kind"] == "standard"
  assert payload["runs"][0]["dataset_identity"].startswith("dataset-v1:")
  assert payload["runs"][1]["experiment"]["preset_id"] == "nfi_baseline"
  assert payload["runs"][1]["experiment"]["benchmark_family"] == "reference:nostalgia-for-infinity"
  assert payload["runs"][1]["reference_id"] == "nostalgia-for-infinity"
  assert payload["runs"][1]["integration_mode"] == "external_runtime"
  assert payload["runs"][1]["catalog_semantics"]["strategy_kind"] == "reference_delegate"
  assert payload["runs"][1]["catalog_semantics"]["source_descriptor"] == (
    "nostalgia-for-infinity:NostalgiaForInfinityX7"
  )
  assert payload["runs"][1]["catalog_semantics"]["operator_notes"]
  assert payload["runs"][1]["reference"]["title"] == "NostalgiaForInfinity"
  assert payload["runs"][1]["artifact_paths"]
  assert "eligibility_contract" not in payload
  assert len(payload["narratives"]) == 1
  assert payload["narratives"][0]["comparison_type"] == "native_vs_reference"
  assert payload["narratives"][0]["run_id"] == reference_run_id
  assert payload["narratives"][0]["rank"] == 1
  assert payload["narratives"][0]["is_primary"] is True
  assert payload["narratives"][0]["insight_score"] > 0
  assert payload["narratives"][0]["score_breakdown"]["total"] == payload["narratives"][0]["insight_score"]
  assert payload["narratives"][0]["score_breakdown"]["semantics"]["components"]["strategy_kind"][
    "applied"
  ] is True
  assert payload["narratives"][0]["score_breakdown"]["semantics"]["components"]["vocabulary"]["score"] > 0
  assert (
    payload["narratives"][0]["score_breakdown"]["semantics"]["components"]["provenance_richness"][
      "score"
    ] > 0
  )
  assert payload["narratives"][0]["title"].startswith("Strategy tuning")
  assert "reference delegate via external_runtime" in payload["narratives"][0]["summary"]
  artifact_kinds = {artifact["kind"] for artifact in payload["runs"][1]["benchmark_artifacts"]}
  assert "result_snapshot_root" in artifact_kinds
  assert "runtime_log_root" in artifact_kinds
  assert all("summary" in artifact for artifact in payload["runs"][1]["benchmark_artifacts"])
  assert all("sections" in artifact for artifact in payload["runs"][1]["benchmark_artifacts"])
  assert all("summary_source_path" in artifact for artifact in payload["runs"][1]["benchmark_artifacts"])
  assert all("source_locations" in artifact for artifact in payload["runs"][1]["benchmark_artifacts"])
  metric_rows = {row["key"]: row for row in payload["metric_rows"]}
  assert metric_rows["total_return_pct"]["annotation"].startswith(
    "Tuning read: return deltas show optimization edge versus the baseline."
  )
  assert "reference delegate via external_runtime" in metric_rows["total_return_pct"]["annotation"]
  assert metric_rows["total_return_pct"]["delta_annotations"][native_run_id] == "tuning baseline"
  assert metric_rows["total_return_pct"]["values"][native_run_id] is not None
  assert "tuning" in metric_rows["total_return_pct"]["delta_annotations"][reference_run_id]
  assert "reference delegate via external_runtime" in metric_rows["total_return_pct"]["delta_annotations"][
    reference_run_id
  ]
  assert reference_run_id in metric_rows["trade_count"]["values"]
  assert payload["runs"][1]["notes"]
