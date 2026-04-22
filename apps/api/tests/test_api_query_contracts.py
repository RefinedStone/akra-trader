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
    provider_provenance_scheduler_search_database_url=(
      f"sqlite:///{database_path.with_name(f'{database_path.stem}-scheduler-search.sqlite3')}"
    ),
    provider_provenance_scheduler_search_service_url="embedded://provider-provenance-scheduler-search",
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


