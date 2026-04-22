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
from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter
from akra_trader.adapters.guarded_live import SqlAlchemyGuardedLiveStateRepository
from akra_trader.adapters.in_memory import LocalStrategyCatalog
from akra_trader.adapters.in_memory import SeededMarketDataAdapter
from akra_trader.adapters.references import load_reference_catalog
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


class FakeExchange:
  def __init__(self, series: dict[tuple[str, str], list[list[float]]]) -> None:
    self._series = series

  def fetch_ohlcv(
    self,
    symbol: str,
    timeframe: str = "5m",
    since: int | None = None,
    limit: int | None = None,
  ) -> list[list[float]]:
    values = list(self._series[(symbol, timeframe)])
    if since is not None:
      values = [row for row in values if row[0] >= since]
    if limit is not None:
      values = values[:limit]
    return values


def build_references():
  repo_root = Path(__file__).resolve().parents[3]
  return load_reference_catalog(repo_root / "reference" / "catalog.toml")


def build_runs_repository(tmp_path: Path) -> SqlAlchemyRunRepository:
  return SqlAlchemyRunRepository(f"sqlite:///{tmp_path / 'runs.sqlite3'}")


def build_preset_catalog(tmp_path: Path) -> SqlAlchemyExperimentPresetCatalog:
  return SqlAlchemyExperimentPresetCatalog(f"sqlite:///{tmp_path / 'runs.sqlite3'}")


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


class MutableClock:
  def __init__(self, current: datetime) -> None:
    self.current = current

  def __call__(self) -> datetime:
    return self.current

  def advance(self, delta: timedelta) -> None:
    self.current += delta


class MutableSeededMarketDataAdapter(SeededMarketDataAdapter):
  def append_candle(self, *, symbol: str, candle: Candle) -> None:
    self._candles[symbol].append(candle)


class StatusOverrideSeededMarketDataAdapter(MutableSeededMarketDataAdapter):
  def __init__(self) -> None:
    super().__init__()
    self._status_by_timeframe: dict[str, MarketDataStatus] = {}
    self._remediation_status_by_key: dict[tuple[str, str], MarketDataStatus] = {}
    self._lineage_history: tuple[MarketDataLineageHistoryRecord, ...] = ()
    self._ingestion_jobs: tuple[MarketDataIngestionJobRecord, ...] = ()
    self.remediation_calls: list[tuple[str, str, str]] = []

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
    self.remediation_calls.append((kind, symbol, timeframe))
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


class StaticVenueStateAdapter:
  def __init__(self, snapshot: GuardedLiveVenueStateSnapshot) -> None:
    self._snapshot = snapshot

  def capture_snapshot(self) -> GuardedLiveVenueStateSnapshot:
    return self._snapshot


class FakeOperatorAlertDeliveryAdapter:
  def __init__(
    self,
    *,
    targets: tuple[str, ...] = ("operator_console",),
    failures_before_success: dict[str, int] | None = None,
    workflow_failures_before_success: dict[str, int] | None = None,
    supported_workflow_providers: tuple[str, ...] = ("pagerduty",),
    clock=None,
  ) -> None:
    self._targets = targets
    self._supported_workflow_providers = supported_workflow_providers
    self.delivered_incidents: list[OperatorIncidentEvent] = []
    self.delivery_attempts: list[tuple[str, str, int]] = []
    self.workflow_attempts: list[tuple[str, str, str, int]] = []
    self.workflow_payloads: list[tuple[str, str, str, dict[str, Any] | None]] = []
    self.pull_sync_attempts: list[tuple[str, str, str | None]] = []
    self._failures_before_success = dict(failures_before_success or {})
    self._workflow_failures_before_success = dict(workflow_failures_before_success or {})
    self._attempts_by_target: dict[str, int] = {}
    self._workflow_attempts_by_key: dict[tuple[str, str], int] = {}
    self._pull_sync_by_key: dict[tuple[str, str], OperatorIncidentProviderPullSync] = {}
    self._clock = clock

  def list_targets(self) -> tuple[str, ...]:
    return self._targets

  def list_supported_workflow_providers(self) -> tuple[str, ...]:
    return self._supported_workflow_providers

  def deliver(
    self,
    *,
    incident: OperatorIncidentEvent,
    targets: tuple[str, ...] | None = None,
    attempt_number: int = 1,
    phase: str = "initial",
  ) -> tuple[OperatorIncidentDelivery, ...]:
    self.delivered_incidents.append(incident)
    resolved_targets = targets or self._targets
    records: list[OperatorIncidentDelivery] = []
    for target in resolved_targets:
      self.delivery_attempts.append((incident.event_id, target, attempt_number))
      delivered_attempts = self._attempts_by_target.get(target, 0) + 1
      self._attempts_by_target[target] = delivered_attempts
      should_fail = delivered_attempts <= self._failures_before_success.get(target, 0)
      external_provider = None
      if target == "pagerduty_events":
        external_provider = "pagerduty"
      elif target == "incidentio_incidents":
        external_provider = "incidentio"
      elif target == "firehydrant_incidents":
        external_provider = "firehydrant"
      elif target == "rootly_incidents":
        external_provider = "rootly"
      elif target == "blameless_incidents":
        external_provider = "blameless"
      elif target == "xmatters_incidents":
        external_provider = "xmatters"
      elif target == "servicenow_incidents":
        external_provider = "servicenow"
      elif target == "squadcast_incidents":
        external_provider = "squadcast"
      elif target == "bigpanda_incidents":
        external_provider = "bigpanda"
      elif target == "grafana_oncall_incidents":
        external_provider = "grafana_oncall"
      elif target == "splunk_oncall_incidents":
        external_provider = "splunk_oncall"
      elif target == "jira_service_management_incidents":
        external_provider = "jira_service_management"
      elif target == "pagertree_incidents":
        external_provider = "pagertree"
      elif target == "alertops_incidents":
        external_provider = "alertops"
      elif target == "signl4_incidents":
        external_provider = "signl4"
      elif target == "ilert_incidents":
        external_provider = "ilert"
      elif target == "betterstack_incidents":
        external_provider = "betterstack"
      elif target == "onpage_incidents":
        external_provider = "onpage"
      elif target == "allquiet_incidents":
        external_provider = "allquiet"
      elif target == "moogsoft_incidents":
        external_provider = "moogsoft"
      elif target == "spikesh_incidents":
        external_provider = "spikesh"
      elif target == "dutycalls_incidents":
        external_provider = "dutycalls"
      elif target == "incidenthub_incidents":
        external_provider = "incidenthub"
      elif target == "resolver_incidents":
        external_provider = "resolver"
      elif target == "openduty_incidents":
        external_provider = "openduty"
      elif target == "cabot_incidents":
        external_provider = "cabot"
      elif target == "haloitsm_incidents":
        external_provider = "haloitsm"
      elif target == "incidentmanagerio_incidents":
        external_provider = "incidentmanagerio"
      elif target == "oneuptime_incidents":
        external_provider = "oneuptime"
      elif target == "squzy_incidents":
        external_provider = "squzy"
      elif target == "crisescontrol_incidents":
        external_provider = "crisescontrol"
      elif target == "freshservice_incidents":
        external_provider = "freshservice"
      elif target == "freshdesk_incidents":
        external_provider = "freshdesk"
      elif target == "happyfox_incidents":
        external_provider = "happyfox"
      elif target == "zendesk_incidents":
        external_provider = "zendesk"
      elif target == "zohodesk_incidents":
        external_provider = "zohodesk"
      elif target == "helpscout_incidents":
        external_provider = "helpscout"
      elif target == "kayako_incidents":
        external_provider = "kayako"
      elif target == "intercom_incidents":
        external_provider = "intercom"
      elif target == "front_incidents":
        external_provider = "front"
      elif target == "servicedeskplus_incidents":
        external_provider = "servicedeskplus"
      elif target == "sysaid_incidents":
        external_provider = "sysaid"
      elif target == "bmchelix_incidents":
        external_provider = "bmchelix"
      elif target == "solarwindsservicedesk_incidents":
        external_provider = "solarwindsservicedesk"
      elif target == "topdesk_incidents":
        external_provider = "topdesk"
      elif target == "invgateservicedesk_incidents":
        external_provider = "invgateservicedesk"
      elif target == "opsramp_incidents":
        external_provider = "opsramp"
      elif target == "zenduty_incidents":
        external_provider = "zenduty"
      elif target == "opsgenie_alerts":
        external_provider = "opsgenie"
      records.append(
        OperatorIncidentDelivery(
          delivery_id=f"{incident.event_id}:{target}:attempt-{attempt_number}",
          incident_event_id=incident.event_id,
          alert_id=incident.alert_id,
          incident_kind=incident.kind,
          target=target,
          status="failed" if should_fail else "delivered",
          attempted_at=self._clock() if callable(self._clock) else incident.timestamp,
          detail=(
            f"fake_failure:{target}:attempt-{attempt_number}"
            if should_fail
            else f"fake_delivery:{target}:attempt-{attempt_number}"
          ),
          attempt_number=attempt_number,
          phase=phase,
          external_provider=external_provider,
          external_reference=incident.external_reference or incident.alert_id if external_provider else None,
          source=incident.source,
        )
      )
    return tuple(records)

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
    self.workflow_attempts.append((incident.event_id, provider, action, attempt_number))
    self.workflow_payloads.append((incident.event_id, provider, action, payload))
    target = f"{provider}_workflow"
    key = (provider, action)
    delivered_attempts = self._workflow_attempts_by_key.get(key, 0) + 1
    self._workflow_attempts_by_key[key] = delivered_attempts
    should_fail = delivered_attempts <= self._workflow_failures_before_success.get(action, 0)
    workflow_reference = incident.provider_workflow_reference
    if workflow_reference is None and provider != "pagerduty":
      workflow_reference = incident.external_reference
    if workflow_reference is None and action == "remediate":
      workflow_reference = incident.external_reference or incident.alert_id
    if workflow_reference is None:
      should_fail = True
    return (
      OperatorIncidentDelivery(
        delivery_id=f"{incident.event_id}:{target}:{action}:attempt-{attempt_number}",
        incident_event_id=incident.event_id,
        alert_id=incident.alert_id,
        incident_kind=incident.kind,
        target=target,
        status="failed" if should_fail else "delivered",
        attempted_at=self._clock() if callable(self._clock) else incident.timestamp,
        detail=(
          f"fake_provider_workflow_reference_unavailable:{action}"
          if workflow_reference is None
          else (
            f"fake_provider_workflow_failed:{action}:attempt-{attempt_number}"
            if should_fail
            else f"fake_provider_workflow_delivered:{action}:attempt-{attempt_number}"
          )
        ),
        attempt_number=attempt_number,
        phase=f"provider_{action}",
        provider_action=action,
        external_provider=provider,
        external_reference=workflow_reference,
        source=incident.source,
      ),
    )

  def set_pull_sync(
    self,
    *,
    provider: str,
    reference: str,
    snapshot: OperatorIncidentProviderPullSync,
  ) -> None:
    self._pull_sync_by_key[(provider, reference)] = snapshot

  def pull_incident_workflow_state(
    self,
    *,
    incident: OperatorIncidentEvent,
    provider: str,
  ) -> OperatorIncidentProviderPullSync | None:
    reference = incident.provider_workflow_reference or incident.external_reference
    self.pull_sync_attempts.append((incident.event_id, provider, reference))
    if reference is None:
      return None
    return self._pull_sync_by_key.get((provider, reference))


def build_guarded_live_repository(tmp_path: Path):
  return SqlAlchemyGuardedLiveStateRepository(f"sqlite:///{tmp_path / 'guarded-live.sqlite3'}")


class AlwaysBuyStrategy(Strategy):
  def describe(self) -> StrategyMetadata:
    return StrategyMetadata(
      strategy_id="always_buy_v1",
      name="Always Buy",
      version="1.0.0",
      runtime="native",
      asset_types=(AssetType.CRYPTO,),
      supported_timeframes=("5m",),
      parameter_schema={},
      description="Test helper strategy that always emits a buy signal.",
    )

  def warmup_spec(self) -> WarmupSpec:
    return WarmupSpec(required_bars=2)

  def decide(self, context) -> StrategyDecisionEnvelope:
    return StrategyDecisionEnvelope(
      signal=SignalDecision(
        timestamp=context.timestamp,
        action=SignalAction.BUY,
        size_fraction=0.25,
        reason="always_buy",
      ),
      rationale="always_buy",
      context=context,
    )


