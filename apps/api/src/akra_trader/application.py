from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from numbers import Number
import re
from typing import Any
from typing import Callable
from typing import Iterable
from uuid import uuid4

from akra_trader.domain.models import RunComparison
from akra_trader.domain.models import RunComparisonNarrative
from akra_trader.domain.models import RunComparisonMetricRow
from akra_trader.domain.models import RunComparisonRun
from akra_trader.domain.models import ComparisonEligibilityContract
from akra_trader.domain.models import default_comparison_eligibility_contract
from akra_trader.domain.models import RunSurfaceCapabilities
from akra_trader.domain.models import GuardedLiveKillSwitch
from akra_trader.domain.models import ClosedTrade
from akra_trader.domain.models import GuardedLiveInternalExposure
from akra_trader.domain.models import GuardedLiveInternalStateSnapshot
from akra_trader.domain.models import GuardedLiveReconciliation
from akra_trader.domain.models import GuardedLiveReconciliationFinding
from akra_trader.domain.models import GuardedLiveRecoveredExposure
from akra_trader.domain.models import GuardedLiveVenueOrderRequest
from akra_trader.domain.models import GuardedLiveVenueOrderResult
from akra_trader.domain.models import GuardedLiveState
from akra_trader.domain.models import GuardedLiveStatus
from akra_trader.domain.models import GuardedLiveVenueBalance
from akra_trader.domain.models import GuardedLiveVenueOpenOrder
from akra_trader.domain.models import GuardedLiveVenueSessionHandoff
from akra_trader.domain.models import GuardedLiveVenueStateSnapshot
from akra_trader.domain.models import GuardedLiveRuntimeRecovery
from akra_trader.domain.models import GuardedLiveOrderBookSync
from akra_trader.domain.models import GuardedLiveSessionOwnership
from akra_trader.domain.models import GuardedLiveVenueSessionRestore
from akra_trader.domain.models import GuardedLiveVenueSessionSync
from akra_trader.domain.models import Fill
from akra_trader.domain.models import ExperimentPreset
from akra_trader.domain.models import Instrument
from akra_trader.domain.models import MarketDataStatus
from akra_trader.domain.models import MarketDataRemediationResult
from akra_trader.domain.models import Order
from akra_trader.domain.models import OrderSide
from akra_trader.domain.models import OrderStatus
from akra_trader.domain.models import OrderType
from akra_trader.domain.models import OperatorAlert
from akra_trader.domain.models import OperatorAuditEvent
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentFireHydrantRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentFireHydrantRecoveryState
from akra_trader.domain.models import OperatorIncidentIncidentIoRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentIncidentIoRecoveryState
from akra_trader.domain.models import OperatorIncidentOpsgenieRecoveryState
from akra_trader.domain.models import OperatorIncidentOpsgenieRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentPagerDutyRecoveryState
from akra_trader.domain.models import OperatorIncidentPagerDutyRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentRootlyRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentRootlyRecoveryState
from akra_trader.domain.models import OperatorIncidentBlamelessRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentBlamelessRecoveryState
from akra_trader.domain.models import OperatorIncidentXmattersRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentXmattersRecoveryState
from akra_trader.domain.models import OperatorIncidentServicenowRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentServicenowRecoveryState
from akra_trader.domain.models import OperatorIncidentSquadcastRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentSquadcastRecoveryState
from akra_trader.domain.models import OperatorIncidentBigPandaRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentBigPandaRecoveryState
from akra_trader.domain.models import OperatorIncidentGrafanaOnCallRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentGrafanaOnCallRecoveryState
from akra_trader.domain.models import OperatorIncidentZendutyRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentZendutyRecoveryState
from akra_trader.domain.models import OperatorIncidentSplunkOnCallRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentSplunkOnCallRecoveryState
from akra_trader.domain.models import OperatorIncidentJiraServiceManagementRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentJiraServiceManagementRecoveryState
from akra_trader.domain.models import OperatorIncidentPagerTreeRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentPagerTreeRecoveryState
from akra_trader.domain.models import OperatorIncidentAlertOpsRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentAlertOpsRecoveryState
from akra_trader.domain.models import OperatorIncidentSignl4RecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentSignl4RecoveryState
from akra_trader.domain.models import OperatorIncidentIlertRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentIlertRecoveryState
from akra_trader.domain.models import OperatorIncidentBetterstackRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentBetterstackRecoveryState
from akra_trader.domain.models import OperatorIncidentOnpageRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentOnpageRecoveryState
from akra_trader.domain.models import OperatorIncidentAllquietRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentAllquietRecoveryState
from akra_trader.domain.models import OperatorIncidentMoogsoftRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentMoogsoftRecoveryState
from akra_trader.domain.models import OperatorIncidentSpikeshRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentSpikeshRecoveryState
from akra_trader.domain.models import OperatorIncidentDutyCallsRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentDutyCallsRecoveryState
from akra_trader.domain.models import OperatorIncidentIncidentHubRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentIncidentHubRecoveryState
from akra_trader.domain.models import OperatorIncidentResolverRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentResolverRecoveryState
from akra_trader.domain.models import OperatorIncidentOpenDutyRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentOpenDutyRecoveryState
from akra_trader.domain.models import OperatorIncidentCabotRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentCabotRecoveryState
from akra_trader.domain.models import OperatorIncidentHaloItsmRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentHaloItsmRecoveryState
from akra_trader.domain.models import OperatorIncidentIncidentManagerIoRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentIncidentManagerIoRecoveryState
from akra_trader.domain.models import OperatorIncidentOneUptimeRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentOneUptimeRecoveryState
from akra_trader.domain.models import OperatorIncidentSquzyRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentSquzyRecoveryState
from akra_trader.domain.models import OperatorIncidentCrisesControlRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentCrisesControlRecoveryState
from akra_trader.domain.models import OperatorIncidentFreshserviceRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentFreshserviceRecoveryState
from akra_trader.domain.models import OperatorIncidentFreshdeskRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentFreshdeskRecoveryState
from akra_trader.domain.models import OperatorIncidentHappyfoxRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentHappyfoxRecoveryState
from akra_trader.domain.models import OperatorIncidentZendeskRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentZendeskRecoveryState
from akra_trader.domain.models import OperatorIncidentZohoDeskRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentZohoDeskRecoveryState
from akra_trader.domain.models import OperatorIncidentHelpScoutRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentHelpScoutRecoveryState
from akra_trader.domain.models import OperatorIncidentFrontRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentFrontRecoveryState
from akra_trader.domain.models import OperatorIncidentIntercomRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentIntercomRecoveryState
from akra_trader.domain.models import OperatorIncidentKayakoRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentKayakoRecoveryState
from akra_trader.domain.models import OperatorIncidentServiceDeskPlusRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentServiceDeskPlusRecoveryState
from akra_trader.domain.models import OperatorIncidentSysAidRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentSysAidRecoveryState
from akra_trader.domain.models import OperatorIncidentBmcHelixRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentBmcHelixRecoveryState
from akra_trader.domain.models import OperatorIncidentSolarWindsServiceDeskRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentSolarWindsServiceDeskRecoveryState
from akra_trader.domain.models import OperatorIncidentInvGateServiceDeskRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentInvGateServiceDeskRecoveryState
from akra_trader.domain.models import OperatorIncidentTopdeskRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentTopdeskRecoveryState
from akra_trader.domain.models import OperatorIncidentOpsRampRecoveryPhaseGraph
from akra_trader.domain.models import OperatorIncidentOpsRampRecoveryState
from akra_trader.domain.models import OperatorIncidentProviderPullSync
from akra_trader.domain.models import OperatorIncidentProviderRecoveryState
from akra_trader.domain.models import OperatorIncidentProviderRecoveryStatusMachine
from akra_trader.domain.models import OperatorIncidentProviderRecoveryTelemetry
from akra_trader.domain.models import OperatorIncidentProviderRecoveryVerification
from akra_trader.domain.models import OperatorIncidentRemediation
from akra_trader.domain.models import OperatorVisibility
from akra_trader.domain.models import Position
from akra_trader.domain.models import ReferenceSource
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunExperimentMetadata
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunProvenance
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunSurfaceSharedContract
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import StrategyLifecycle
from akra_trader.domain.models import StrategyCatalogSemantics
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import StrategyParameterSnapshot
from akra_trader.domain.models import StrategyRegistration
from akra_trader.domain.models import StrategySnapshot
from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter
from akra_trader.domain.services import apply_signal
from akra_trader.domain.services import build_equity_point
from akra_trader.domain.services import summarize_performance
from akra_trader.lineage import build_rerun_boundary_identity
from akra_trader.ports import GuardedLiveStatePort
from akra_trader.ports import ExperimentPresetCatalogPort
from akra_trader.ports import MarketDataPort
from akra_trader.ports import OperatorAlertDeliveryPort
from akra_trader.ports import ReferenceCatalogPort
from akra_trader.ports import RunRepositoryPort
from akra_trader.ports import StrategyCatalogPort
from akra_trader.ports import StrategyRuntime
from akra_trader.ports import VenueExecutionPort
from akra_trader.ports import VenueStatePort
from akra_trader.runtime import DataEngine
from akra_trader.runtime import ExecutionEngine
from akra_trader.runtime import ExecutionModeService
from akra_trader.runtime import RunSupervisor
from akra_trader.runtime import StateCache
from akra_trader.runtime import candles_to_frame


COMPARISON_METRICS: tuple[tuple[str, str, str, bool], ...] = (
  ("total_return_pct", "Total return", "pct", True),
  ("max_drawdown_pct", "Max drawdown", "pct", False),
  ("win_rate_pct", "Win rate", "pct", True),
  ("trade_count", "Trades", "count", True),
)

COMPARISON_INTENT_DEFAULT = "benchmark_validation"
COMPARISON_INTENT_WEIGHTS: dict[str, dict[str, float]] = {
  "benchmark_validation": {
    "return": 0.8,
    "drawdown": 1.5,
    "win_rate": 0.7,
    "trade_count": 0.12,
    "semantic_kind_bonus": 1.2,
    "semantic_execution_bonus": 0.8,
    "semantic_source_bonus": 0.8,
    "semantic_parameter_contract_bonus": 0.4,
    "semantic_vocabulary_unit_bonus": 0.28,
    "provenance_richness_unit_bonus": 0.24,
    "native_reference_bonus": 8.0,
    "reference_bonus": 3.0,
    "status_bonus": 1.5,
    "benchmark_story_bonus": 1.5,
    "reference_floor": 1.0,
  },
  "execution_regression": {
    "return": 0.9,
    "drawdown": 1.9,
    "win_rate": 1.0,
    "trade_count": 0.4,
    "semantic_kind_bonus": 0.8,
    "semantic_execution_bonus": 0.6,
    "semantic_source_bonus": 0.4,
    "semantic_parameter_contract_bonus": 0.3,
    "semantic_vocabulary_unit_bonus": 0.18,
    "provenance_richness_unit_bonus": 0.2,
    "native_reference_bonus": 3.0,
    "reference_bonus": 1.0,
    "status_bonus": 3.0,
    "benchmark_story_bonus": 0.8,
    "reference_floor": 1.0,
  },
  "strategy_tuning": {
    "return": 2.0,
    "drawdown": 0.7,
    "win_rate": 1.3,
    "trade_count": 0.35,
    "semantic_kind_bonus": 1.0,
    "semantic_execution_bonus": 0.7,
    "semantic_source_bonus": 0.6,
    "semantic_parameter_contract_bonus": 0.5,
    "semantic_vocabulary_unit_bonus": 0.38,
    "provenance_richness_unit_bonus": 0.12,
    "native_reference_bonus": 1.5,
    "reference_bonus": 0.5,
    "status_bonus": 0.8,
    "benchmark_story_bonus": 0.4,
    "reference_floor": 0.5,
  },
}


@dataclass(frozen=True)
class _IncidentPagingPolicy:
  policy_id: str
  provider: str | None
  initial_targets: tuple[str, ...]
  escalation_targets: tuple[str, ...]
  resolution_targets: tuple[str, ...]


@dataclass(frozen=True)
class _IncidentRemediationPlan:
  kind: str
  owner: str
  summary: str
  detail: str
  runbook: str

COMPARISON_INTENT_COPY: dict[str, dict[str, str]] = {
  "benchmark_validation": {
    "title_prefix": "Benchmark validation",
    "summary_prefix": "Validation view",
    "partial_summary": (
      "Benchmark validation falls back to persisted reference provenance because direct metric "
      "deltas are partial."
    ),
    "lane_prefix": "Validation context",
    "activity_prefix": "Validation signal",
    "reference_prefix": "Benchmark evidence",
  },
  "execution_regression": {
    "title_prefix": "Execution regression",
    "summary_prefix": "Regression view",
    "partial_summary": (
      "Execution regression falls back to persisted reference provenance because direct execution "
      "deltas are partial."
    ),
    "lane_prefix": "Regression context",
    "activity_prefix": "Execution signal",
    "reference_prefix": "Reference baseline",
  },
  "strategy_tuning": {
    "title_prefix": "Strategy tuning",
    "summary_prefix": "Tuning view",
    "partial_summary": (
      "Strategy tuning falls back to benchmark provenance because direct optimization deltas are partial."
    ),
    "lane_prefix": "Tuning context",
    "activity_prefix": "Tuning signal",
    "reference_prefix": "Benchmark backdrop",
  },
}

COMPARISON_METRIC_COPY: dict[str, dict[str, dict[str, str]]] = {
  "benchmark_validation": {
    "total_return_pct": {
      "annotation": "Validation read: return drift versus the selected benchmark baseline.",
      "positive_delta": "above benchmark",
      "negative_delta": "below benchmark",
      "baseline": "benchmark baseline",
      "missing": "benchmark delta unavailable",
    },
    "max_drawdown_pct": {
      "annotation": "Validation read: downside drift versus the benchmark risk envelope.",
      "positive_delta": "deeper than benchmark",
      "negative_delta": "tighter than benchmark",
      "baseline": "benchmark baseline",
      "missing": "benchmark drawdown delta unavailable",
    },
    "win_rate_pct": {
      "annotation": "Validation read: hit-rate drift versus the benchmark baseline.",
      "positive_delta": "above benchmark",
      "negative_delta": "below benchmark",
      "baseline": "benchmark baseline",
      "missing": "benchmark hit-rate delta unavailable",
    },
    "trade_count": {
      "annotation": "Validation read: participation and pacing drift versus the benchmark.",
      "positive_delta": "above benchmark",
      "negative_delta": "below benchmark",
      "baseline": "benchmark baseline",
      "missing": "benchmark activity delta unavailable",
    },
  },
  "execution_regression": {
    "total_return_pct": {
      "annotation": "Regression read: return movement is treated as execution drift.",
      "positive_delta": "return lift",
      "negative_delta": "return regression",
      "baseline": "regression baseline",
      "missing": "return regression unavailable",
    },
    "max_drawdown_pct": {
      "annotation": "Regression read: higher drawdown is treated as risk regression.",
      "positive_delta": "extra drawdown",
      "negative_delta": "risk improvement",
      "baseline": "regression baseline",
      "missing": "drawdown regression unavailable",
    },
    "win_rate_pct": {
      "annotation": "Regression read: hit-rate movement is treated as execution drift.",
      "positive_delta": "hit-rate lift",
      "negative_delta": "hit-rate regression",
      "baseline": "regression baseline",
      "missing": "hit-rate regression unavailable",
    },
    "trade_count": {
      "annotation": "Regression read: trade-flow changes point to execution behavior drift.",
      "positive_delta": "extra activity",
      "negative_delta": "reduced activity",
      "baseline": "regression baseline",
      "missing": "activity regression unavailable",
    },
  },
  "strategy_tuning": {
    "total_return_pct": {
      "annotation": "Tuning read: return deltas show optimization edge versus the baseline.",
      "positive_delta": "tuning edge",
      "negative_delta": "tuning gap",
      "baseline": "tuning baseline",
      "missing": "tuning delta unavailable",
    },
    "max_drawdown_pct": {
      "annotation": "Tuning read: lower drawdown marks a cleaner optimization tradeoff.",
      "positive_delta": "drawdown penalty",
      "negative_delta": "drawdown improvement",
      "baseline": "tuning baseline",
      "missing": "drawdown tuning delta unavailable",
    },
    "win_rate_pct": {
      "annotation": "Tuning read: hit-rate deltas show signal-quality tradeoffs.",
      "positive_delta": "hit-rate edge",
      "negative_delta": "hit-rate gap",
      "baseline": "tuning baseline",
      "missing": "hit-rate tuning delta unavailable",
    },
    "trade_count": {
      "annotation": "Tuning read: trade-count changes expose activity tradeoffs in the variant.",
      "positive_delta": "activity expansion",
      "negative_delta": "activity reduction",
      "baseline": "tuning baseline",
      "missing": "activity tuning delta unavailable",
    },
  },
}


class TradingApplication:
  _sandbox_worker_kind = "sandbox_native_worker"
  _guarded_live_worker_kind = "guarded_live_native_worker"
  _guarded_live_balance_tolerance = 1e-9
  _guarded_live_market_data_failure_burst_threshold = 2
  _guarded_live_market_data_backfill_completion_floor = 0.9
  _guarded_live_market_data_contiguous_completion_floor = 0.98
  _guarded_live_drawdown_breach_pct = 35.0
  _guarded_live_loss_breach_pct = 20.0
  _guarded_live_gross_open_risk_ratio = 1.1
  _guarded_live_recovery_alert_threshold = 2

  class _EphemeralGuardedLiveStateStore(GuardedLiveStatePort):
    def __init__(self) -> None:
      self._state = GuardedLiveState()

    def load_state(self) -> GuardedLiveState:
      return self._state

    def save_state(self, state: GuardedLiveState) -> GuardedLiveState:
      self._state = state
      return state

  class _EphemeralExperimentPresetCatalog(ExperimentPresetCatalogPort):
    def __init__(self) -> None:
      self._presets: dict[str, ExperimentPreset] = {}

    def list_presets(
      self,
      *,
      strategy_id: str | None = None,
      timeframe: str | None = None,
      lifecycle_stage: str | None = None,
    ) -> list[ExperimentPreset]:
      presets = list(reversed(tuple(self._presets.values())))
      if strategy_id is not None:
        presets = [
          preset
          for preset in presets
          if preset.strategy_id is None or preset.strategy_id == strategy_id
        ]
      if timeframe is not None:
        presets = [
          preset
          for preset in presets
          if preset.timeframe is None or preset.timeframe == timeframe
        ]
      if lifecycle_stage is not None:
        presets = [
          preset
          for preset in presets
          if preset.lifecycle.stage == lifecycle_stage
        ]
      return presets

    def get_preset(self, preset_id: str) -> ExperimentPreset | None:
      return self._presets.get(preset_id)

    def save_preset(self, preset: ExperimentPreset) -> ExperimentPreset:
      self._presets[preset.preset_id] = preset
      return preset

  class _UnavailableVenueStateAdapter(VenueStatePort):
    def __init__(self, clock: Callable[[], datetime]) -> None:
      self._clock = clock

    def capture_snapshot(self) -> GuardedLiveVenueStateSnapshot:
      return GuardedLiveVenueStateSnapshot(
        provider="unconfigured",
        venue="unconfigured",
        verification_state="unavailable",
        captured_at=self._clock(),
        issues=("venue_state_port_unconfigured",),
      )

  class _UnavailableVenueExecutionAdapter(VenueExecutionPort):
    def describe_capability(self) -> tuple[bool, tuple[str, ...]]:
      return False, ("venue_execution_port_unconfigured",)

    def restore_session(
      self,
      *,
      symbol: str,
      owned_order_ids: tuple[str, ...],
    ) -> GuardedLiveVenueSessionRestore:
      raise RuntimeError("Venue execution port is not configured.")

    def handoff_session(
      self,
      *,
      symbol: str,
      timeframe: str,
      owner_run_id: str,
      owner_session_id: str | None,
      owned_order_ids: tuple[str, ...],
    ) -> GuardedLiveVenueSessionHandoff:
      raise RuntimeError("Venue execution port is not configured.")

    def sync_session(
      self,
      *,
      handoff: GuardedLiveVenueSessionHandoff,
      order_ids: tuple[str, ...],
    ) -> GuardedLiveVenueSessionSync:
      raise RuntimeError("Venue execution port is not configured.")

    def release_session(
      self,
      *,
      handoff: GuardedLiveVenueSessionHandoff,
    ) -> GuardedLiveVenueSessionHandoff:
      raise RuntimeError("Venue execution port is not configured.")

    def submit_market_order(
      self,
      request: GuardedLiveVenueOrderRequest,
    ) -> GuardedLiveVenueOrderResult:
      raise RuntimeError("Venue execution port is not configured.")

    def submit_limit_order(
      self,
      request: GuardedLiveVenueOrderRequest,
    ) -> GuardedLiveVenueOrderResult:
      raise RuntimeError("Venue execution port is not configured.")

    def cancel_order(
      self,
      *,
      symbol: str,
      order_id: str,
    ) -> GuardedLiveVenueOrderResult:
      raise RuntimeError("Venue execution port is not configured.")

    def sync_order_states(
      self,
      *,
      symbol: str,
      order_ids: tuple[str, ...],
    ) -> tuple[GuardedLiveVenueOrderResult, ...]:
      raise RuntimeError("Venue execution port is not configured.")

  class _NoopOperatorAlertDeliveryAdapter(OperatorAlertDeliveryPort):
    def list_targets(self) -> tuple[str, ...]:
      return ()

    def list_supported_workflow_providers(self) -> tuple[str, ...]:
      return ()

    def deliver(
      self,
      *,
      incident: OperatorIncidentEvent,
      targets: tuple[str, ...] | None = None,
      attempt_number: int = 1,
      phase: str = "initial",
    ) -> tuple[OperatorIncidentDelivery, ...]:
      return ()

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

  def __init__(
    self,
    *,
    market_data: MarketDataPort,
    strategies: StrategyCatalogPort,
    references: ReferenceCatalogPort,
    runs: RunRepositoryPort,
    presets: ExperimentPresetCatalogPort | None = None,
    guarded_live_state: GuardedLiveStatePort | None = None,
    venue_state: VenueStatePort | None = None,
    venue_execution: VenueExecutionPort | None = None,
    operator_alert_delivery: OperatorAlertDeliveryPort | None = None,
    freqtrade_reference: FreqtradeReferenceAdapter | None = None,
    mode_service: ExecutionModeService | None = None,
    data_engine: DataEngine | None = None,
    execution_engine: ExecutionEngine | None = None,
    run_supervisor: RunSupervisor | None = None,
    guarded_live_venue: str = "binance",
    guarded_live_execution_enabled: bool = False,
    market_data_sync_timeframes: tuple[str, ...] = ("5m",),
    sandbox_worker_heartbeat_interval_seconds: int = 15,
    sandbox_worker_heartbeat_timeout_seconds: int = 45,
    guarded_live_worker_heartbeat_interval_seconds: int = 15,
    guarded_live_worker_heartbeat_timeout_seconds: int = 45,
    operator_alert_delivery_max_attempts: int = 4,
    operator_alert_delivery_initial_backoff_seconds: int = 15,
    operator_alert_delivery_max_backoff_seconds: int = 300,
    operator_alert_delivery_backoff_multiplier: float = 2.0,
    operator_alert_paging_policy_default_provider: str | None = None,
    operator_alert_paging_policy_warning_targets: tuple[str, ...] = (),
    operator_alert_paging_policy_critical_targets: tuple[str, ...] = (),
    operator_alert_paging_policy_warning_escalation_targets: tuple[str, ...] = (),
    operator_alert_paging_policy_critical_escalation_targets: tuple[str, ...] = (),
    operator_alert_external_sync_token: str | None = None,
    operator_alert_escalation_targets: tuple[str, ...] = (),
    operator_alert_incident_ack_timeout_seconds: int = 300,
    operator_alert_incident_max_escalations: int = 2,
    operator_alert_incident_escalation_backoff_multiplier: float = 2.0,
    clock: Callable[[], datetime] | None = None,
  ) -> None:
    self._clock = clock or (lambda: datetime.now(UTC))
    self._market_data = market_data
    self._strategies = strategies
    self._references = references
    self._presets = presets or self._EphemeralExperimentPresetCatalog()
    self._runs = runs
    self._guarded_live_state = guarded_live_state or self._EphemeralGuardedLiveStateStore()
    self._venue_state = venue_state or self._UnavailableVenueStateAdapter(self._clock)
    self._venue_execution = venue_execution or self._UnavailableVenueExecutionAdapter()
    self._operator_alert_delivery = (
      operator_alert_delivery or self._NoopOperatorAlertDeliveryAdapter()
    )
    self._freqtrade_reference = freqtrade_reference
    self._mode_service = mode_service or ExecutionModeService()
    self._data_engine = data_engine or DataEngine(market_data)
    self._execution_engine = execution_engine or ExecutionEngine()
    self._run_supervisor = run_supervisor or RunSupervisor()
    self._guarded_live_venue = guarded_live_venue
    self._guarded_live_execution_enabled = guarded_live_execution_enabled
    self._guarded_live_market_data_timeframes = tuple(
      dict.fromkeys(market_data_sync_timeframes or ("5m",))
    )
    self._sandbox_worker_heartbeat_interval_seconds = sandbox_worker_heartbeat_interval_seconds
    self._sandbox_worker_heartbeat_timeout_seconds = sandbox_worker_heartbeat_timeout_seconds
    self._guarded_live_worker_heartbeat_interval_seconds = (
      guarded_live_worker_heartbeat_interval_seconds
    )
    self._guarded_live_worker_heartbeat_timeout_seconds = (
      guarded_live_worker_heartbeat_timeout_seconds
    )
    self._operator_alert_delivery_max_attempts = max(operator_alert_delivery_max_attempts, 1)
    self._operator_alert_delivery_initial_backoff_seconds = max(
      operator_alert_delivery_initial_backoff_seconds,
      1,
    )
    self._operator_alert_delivery_max_backoff_seconds = max(
      operator_alert_delivery_max_backoff_seconds,
      self._operator_alert_delivery_initial_backoff_seconds,
    )
    self._operator_alert_delivery_backoff_multiplier = max(
      operator_alert_delivery_backoff_multiplier,
      1.0,
    )
    self._operator_alert_paging_policy_default_provider = self._normalize_paging_provider(
      operator_alert_paging_policy_default_provider
    )
    self._operator_alert_paging_policy_warning_targets = self._normalize_targets(
      operator_alert_paging_policy_warning_targets
    )
    self._operator_alert_paging_policy_critical_targets = self._normalize_targets(
      operator_alert_paging_policy_critical_targets
    )
    self._operator_alert_paging_policy_warning_escalation_targets = self._normalize_targets(
      operator_alert_paging_policy_warning_escalation_targets
    )
    self._operator_alert_paging_policy_critical_escalation_targets = self._normalize_targets(
      operator_alert_paging_policy_critical_escalation_targets
    )
    self._operator_alert_external_sync_token = operator_alert_external_sync_token
    self._operator_alert_escalation_targets = tuple(
      dict.fromkeys(operator_alert_escalation_targets)
    )
    self._operator_alert_incident_ack_timeout_seconds = max(
      operator_alert_incident_ack_timeout_seconds,
      1,
    )
    self._operator_alert_incident_max_escalations = max(
      operator_alert_incident_max_escalations,
      1,
    )
    self._operator_alert_incident_escalation_backoff_multiplier = max(
      operator_alert_incident_escalation_backoff_multiplier,
      1.0,
    )

  def list_strategies(
    self,
    *,
    lane: str | None = None,
    lifecycle_stage: str | None = None,
    version: str | None = None,
  ) -> list[StrategyMetadata]:
    return self._strategies.list_strategies(
      runtime=lane,
      lifecycle_stage=lifecycle_stage,
      version=version,
    )

  def list_references(self) -> list[ReferenceSource]:
    return self._references.list_entries()

  def register_strategy(self, *, strategy_id: str, module_path: str, class_name: str) -> StrategyMetadata:
    registration = StrategyRegistration(
      strategy_id=strategy_id,
      module_path=module_path,
      class_name=class_name,
      registered_at=datetime.now(UTC),
    )
    return self._strategies.register(registration)

  def list_presets(
    self,
    *,
    strategy_id: str | None = None,
    timeframe: str | None = None,
    lifecycle_stage: str | None = None,
  ) -> list[ExperimentPreset]:
    return self._presets.list_presets(
      strategy_id=_normalize_experiment_filter_value(strategy_id),
      timeframe=_normalize_experiment_filter_value(timeframe),
      lifecycle_stage=_normalize_preset_lifecycle_stage(lifecycle_stage),
    )

  def get_preset(self, *, preset_id: str) -> ExperimentPreset:
    return self._get_preset_or_raise(preset_id)

  def create_preset(
    self,
    *,
    name: str,
    preset_id: str | None = None,
    description: str = "",
    strategy_id: str | None = None,
    timeframe: str | None = None,
    tags: Iterable[str] = (),
    parameters: dict[str, Any] | None = None,
    benchmark_family: str | None = None,
  ) -> ExperimentPreset:
    normalized_name = name.strip()
    if not normalized_name:
      raise ValueError("Preset name is required.")
    normalized_preset_id = _normalize_experiment_identifier(preset_id or name)
    if normalized_preset_id is None:
      raise ValueError("Preset ID is required.")
    if self._presets.get_preset(normalized_preset_id) is not None:
      raise ValueError(f"Preset already exists: {normalized_preset_id}")
    normalized_strategy_id = _normalize_experiment_filter_value(strategy_id)
    self._validate_preset_strategy(strategy_id=normalized_strategy_id)
    normalized_timeframe = _normalize_experiment_filter_value(timeframe)
    normalized_parameters = deepcopy(parameters or {})
    if normalized_parameters and normalized_strategy_id is None:
      raise ValueError("Preset parameters require a strategy_id.")
    current_time = self._clock()
    preset = ExperimentPreset(
      preset_id=normalized_preset_id,
      name=normalized_name,
      description=description.strip(),
      strategy_id=normalized_strategy_id,
      timeframe=normalized_timeframe,
      benchmark_family=_normalize_experiment_identifier(benchmark_family),
      tags=_normalize_experiment_tags(tags),
      parameters=normalized_parameters,
      lifecycle=ExperimentPreset.Lifecycle(
        stage="draft",
        updated_at=current_time,
        updated_by="operator",
        last_action="created",
        history=(
          ExperimentPreset.LifecycleEvent(
            action="created",
            actor="operator",
            reason="preset_created",
            occurred_at=current_time,
            from_stage=None,
            to_stage="draft",
          ),
        ),
      ),
      revisions=(
        _build_preset_revision(
          preset_id=normalized_preset_id,
          revision_number=1,
          action="created",
          actor="operator",
          reason="preset_created",
          occurred_at=current_time,
          name=normalized_name,
          description=description.strip(),
          strategy_id=normalized_strategy_id,
          timeframe=normalized_timeframe,
          benchmark_family=_normalize_experiment_identifier(benchmark_family),
          tags=_normalize_experiment_tags(tags),
          parameters=normalized_parameters,
        ),
      ),
      created_at=current_time,
      updated_at=current_time,
    )
    return self._presets.save_preset(preset)

  def update_preset(
    self,
    *,
    preset_id: str,
    changes: dict[str, Any],
    actor: str = "operator",
    reason: str = "manual_preset_edit",
  ) -> ExperimentPreset:
    preset = self._get_preset_or_raise(preset_id)
    allowed_fields = {
      "name",
      "description",
      "strategy_id",
      "timeframe",
      "benchmark_family",
      "tags",
      "parameters",
    }
    unexpected_fields = sorted(set(changes) - allowed_fields)
    if unexpected_fields:
      raise ValueError(f"Unsupported preset update fields: {', '.join(unexpected_fields)}")
    if not changes:
      raise ValueError("Preset update requires at least one field.")

    next_name = preset.name
    if "name" in changes:
      candidate_name = str(changes["name"] or "").strip()
      if not candidate_name:
        raise ValueError("Preset name is required.")
      next_name = candidate_name

    next_description = preset.description
    if "description" in changes:
      next_description = str(changes["description"] or "").strip()

    next_strategy_id = preset.strategy_id
    if "strategy_id" in changes:
      next_strategy_id = _normalize_experiment_filter_value(changes["strategy_id"])

    next_timeframe = preset.timeframe
    if "timeframe" in changes:
      next_timeframe = _normalize_experiment_filter_value(changes["timeframe"])

    next_benchmark_family = preset.benchmark_family
    if "benchmark_family" in changes:
      next_benchmark_family = _normalize_experiment_identifier(changes["benchmark_family"])

    next_tags = preset.tags
    if "tags" in changes:
      next_tags = _normalize_experiment_tags(changes["tags"])

    next_parameters = deepcopy(preset.parameters)
    if "parameters" in changes:
      candidate_parameters = changes["parameters"]
      if candidate_parameters is None:
        next_parameters = {}
      elif isinstance(candidate_parameters, dict):
        next_parameters = deepcopy(candidate_parameters)
      else:
        raise ValueError("Preset parameters must be a JSON object.")

    self._validate_preset_strategy(strategy_id=next_strategy_id)
    if next_parameters and next_strategy_id is None:
      raise ValueError("Preset parameters require a strategy_id.")

    if (
      next_name == preset.name
      and next_description == preset.description
      and next_strategy_id == preset.strategy_id
      and next_timeframe == preset.timeframe
      and next_benchmark_family == preset.benchmark_family
      and next_tags == preset.tags
      and next_parameters == preset.parameters
    ):
      return preset

    current_time = self._clock()
    normalized_actor = (actor or "operator").strip() or "operator"
    normalized_reason = (reason or "manual_preset_edit").strip() or "manual_preset_edit"
    updated = replace(
      preset,
      name=next_name,
      description=next_description,
      strategy_id=next_strategy_id,
      timeframe=next_timeframe,
      benchmark_family=next_benchmark_family,
      tags=next_tags,
      parameters=next_parameters,
      updated_at=current_time,
      revisions=(
        *preset.revisions,
        _build_preset_revision(
          preset_id=preset.preset_id,
          revision_number=len(preset.revisions) + 1,
          action="updated",
          actor=normalized_actor,
          reason=normalized_reason,
          occurred_at=current_time,
          name=next_name,
          description=next_description,
          strategy_id=next_strategy_id,
          timeframe=next_timeframe,
          benchmark_family=next_benchmark_family,
          tags=next_tags,
          parameters=next_parameters,
        ),
      ),
    )
    return self._presets.save_preset(updated)

  def list_preset_revisions(
    self,
    *,
    preset_id: str,
  ) -> tuple[ExperimentPreset.Revision, ...]:
    preset = self._get_preset_or_raise(preset_id)
    return tuple(reversed(preset.revisions))

  def restore_preset_revision(
    self,
    *,
    preset_id: str,
    revision_id: str,
    actor: str = "operator",
    reason: str = "manual_preset_revision_restore",
  ) -> ExperimentPreset:
    preset = self._get_preset_or_raise(preset_id)
    target_revision = next(
      (revision for revision in preset.revisions if revision.revision_id == revision_id),
      None,
    )
    if target_revision is None:
      raise LookupError(f"Preset revision not found: {revision_id}")

    current_time = self._clock()
    normalized_actor = (actor or "operator").strip() or "operator"
    normalized_reason = (reason or "manual_preset_revision_restore").strip() or "manual_preset_revision_restore"
    restored = replace(
      preset,
      name=target_revision.name,
      description=target_revision.description,
      strategy_id=target_revision.strategy_id,
      timeframe=target_revision.timeframe,
      benchmark_family=target_revision.benchmark_family,
      tags=target_revision.tags,
      parameters=deepcopy(target_revision.parameters),
      updated_at=current_time,
      revisions=(
        *preset.revisions,
        _build_preset_revision(
          preset_id=preset.preset_id,
          revision_number=len(preset.revisions) + 1,
          action="restored",
          actor=normalized_actor,
          reason=normalized_reason,
          occurred_at=current_time,
          source_revision_id=target_revision.revision_id,
          name=target_revision.name,
          description=target_revision.description,
          strategy_id=target_revision.strategy_id,
          timeframe=target_revision.timeframe,
          benchmark_family=target_revision.benchmark_family,
          tags=target_revision.tags,
          parameters=target_revision.parameters,
        ),
      ),
    )
    self._validate_preset_strategy(strategy_id=restored.strategy_id)
    if restored.parameters and restored.strategy_id is None:
      raise ValueError("Preset parameters require a strategy_id.")
    return self._presets.save_preset(restored)

  def apply_preset_lifecycle_action(
    self,
    *,
    preset_id: str,
    action: str,
    actor: str = "operator",
    reason: str = "manual_preset_lifecycle_action",
  ) -> ExperimentPreset:
    normalized_preset_id = _normalize_experiment_identifier(preset_id)
    if normalized_preset_id is None:
      raise ValueError("Preset ID is required.")
    preset = self._presets.get_preset(normalized_preset_id)
    if preset is None:
      raise LookupError(f"Preset not found: {normalized_preset_id}")
    normalized_action = _normalize_preset_lifecycle_action(action)
    if normalized_action is None:
      raise ValueError(f"Unsupported preset lifecycle action: {action}")
    current_stage = preset.lifecycle.stage
    target_stage = _resolve_preset_lifecycle_target_stage(
      current_stage=current_stage,
      action=normalized_action,
    )
    current_time = self._clock()
    updated = replace(
      preset,
      lifecycle=replace(
        preset.lifecycle,
        stage=target_stage,
        updated_at=current_time,
        updated_by=(actor or "operator").strip() or "operator",
        last_action=normalized_action,
        history=(
          *preset.lifecycle.history,
          ExperimentPreset.LifecycleEvent(
            action=normalized_action,
            actor=(actor or "operator").strip() or "operator",
            reason=(reason or normalized_action).strip() or normalized_action,
            occurred_at=current_time,
            from_stage=current_stage,
            to_stage=target_stage,
          ),
        ),
      ),
      updated_at=current_time,
    )
    return self._presets.save_preset(updated)

  def _get_preset_or_raise(self, preset_id: str) -> ExperimentPreset:
    normalized_preset_id = _normalize_experiment_identifier(preset_id)
    if normalized_preset_id is None:
      raise ValueError("Preset ID is required.")
    preset = self._presets.get_preset(normalized_preset_id)
    if preset is None:
      raise LookupError(f"Preset not found: {normalized_preset_id}")
    return preset

  def _validate_preset_strategy(self, *, strategy_id: str | None) -> None:
    if strategy_id is None:
      return
    available_strategy_ids = {
      strategy.strategy_id
      for strategy in self._strategies.list_strategies()
    }
    if strategy_id not in available_strategy_ids:
      raise ValueError(f"Strategy not found for preset: {strategy_id}")

  def list_runs(
    self,
    mode: str | None = None,
    *,
    strategy_id: str | None = None,
    strategy_version: str | None = None,
    rerun_boundary_id: str | None = None,
    preset_id: str | None = None,
    benchmark_family: str | None = None,
    dataset_identity: str | None = None,
    tags: Iterable[str] = (),
  ) -> list[RunRecord]:
    return self._runs.list_runs(
      mode=self._mode_service.normalize(mode),
      strategy_id=strategy_id,
      strategy_version=strategy_version,
      rerun_boundary_id=rerun_boundary_id,
      preset_id=_normalize_experiment_identifier(preset_id),
      benchmark_family=_normalize_experiment_identifier(benchmark_family),
      dataset_identity=_normalize_experiment_filter_value(dataset_identity),
      tags=_normalize_experiment_tags(tags),
    )

  def get_run(self, run_id: str) -> RunRecord | None:
    return self._runs.get_run(run_id)

  def rerun_backtest_from_boundary(self, *, rerun_boundary_id: str) -> RunRecord:
    return self._rerun_from_boundary(
      rerun_boundary_id=rerun_boundary_id,
      target_mode=RunMode.BACKTEST,
      requested_mode_label=RunMode.BACKTEST.value,
    )

  def rerun_sandbox_from_boundary(self, *, rerun_boundary_id: str) -> RunRecord:
    return self._rerun_from_boundary(
      rerun_boundary_id=rerun_boundary_id,
      target_mode=RunMode.SANDBOX,
      requested_mode_label=RunMode.SANDBOX.value,
    )

  def rerun_paper_from_boundary(self, *, rerun_boundary_id: str) -> RunRecord:
    return self._rerun_from_boundary(
      rerun_boundary_id=rerun_boundary_id,
      target_mode=RunMode.PAPER,
      requested_mode_label=RunMode.PAPER.value,
    )

  def compare_runs(self, *, run_ids: list[str], intent: str | None = None) -> RunComparison:
    normalized_run_ids = _normalize_run_ids(run_ids)
    if len(normalized_run_ids) < 2:
      raise ValueError("Run comparison requires at least two unique run IDs.")
    resolved_intent = _normalize_comparison_intent(intent)

    runs = self._runs.compare_runs(normalized_run_ids)
    run_by_id = {run.config.run_id: run for run in runs}
    missing_run_ids = [run_id for run_id in normalized_run_ids if run_id not in run_by_id]
    if missing_run_ids:
      raise LookupError(f"Run not found: {', '.join(missing_run_ids)}")

    ordered_runs = [run_by_id[run_id] for run_id in normalized_run_ids]
    baseline_run = ordered_runs[0]
    metric_rows = tuple(
      _build_comparison_metric_row(
        runs=ordered_runs,
        baseline_run=baseline_run,
        intent=resolved_intent,
        key=key,
        label=label,
        unit=unit,
        higher_is_better=higher_is_better,
      )
      for key, label, unit, higher_is_better in COMPARISON_METRICS
    )
    metric_row_by_key = {row.key: row for row in metric_rows}
    ranked_narratives = _rank_comparison_narratives([
      narrative
      for run in ordered_runs[1:]
      if (
        narrative := _build_comparison_narrative(
          baseline_run=baseline_run,
          run=run,
          intent=resolved_intent,
          metric_row_by_key=metric_row_by_key,
        )
      ) is not None
    ])
    return RunComparison(
      requested_run_ids=tuple(normalized_run_ids),
      intent=resolved_intent,
      baseline_run_id=baseline_run.config.run_id,
      runs=tuple(_serialize_comparison_run(run) for run in ordered_runs),
      metric_rows=metric_rows,
      narratives=tuple(ranked_narratives),
    )

  def get_run_surface_capabilities(self) -> RunSurfaceCapabilities:
    return RunSurfaceCapabilities()

  def get_market_data_status(self, timeframe: str) -> MarketDataStatus:
    return self._market_data.get_status(timeframe)

  def get_operator_visibility(self) -> OperatorVisibility:
    current_time = self._clock()
    sandbox_alerts, sandbox_audit_events = self._collect_sandbox_operator_visibility(
      current_time=current_time
    )
    guarded_live_state, live_alerts = self._refresh_guarded_live_alert_state(
      current_time=current_time
    )
    alerts = [*sandbox_alerts, *live_alerts]
    audit_events = [*sandbox_audit_events, *guarded_live_state.audit_events]
    incident_events = tuple(
      sorted(guarded_live_state.incident_events, key=lambda event: event.timestamp, reverse=True)
    )
    delivery_history = tuple(
      sorted(
        guarded_live_state.delivery_history,
        key=lambda record: record.attempted_at,
        reverse=True,
      )
    )
    alerts.sort(key=lambda alert: alert.detected_at, reverse=True)
    audit_events.sort(key=lambda event: event.timestamp, reverse=True)
    return OperatorVisibility(
      generated_at=current_time,
      alerts=tuple(alerts),
      alert_history=guarded_live_state.alert_history,
      incident_events=incident_events,
      delivery_history=delivery_history,
      audit_events=tuple(audit_events),
    )

  def get_guarded_live_status(self) -> GuardedLiveStatus:
    current_time = self._clock()
    sandbox_alerts, _ = self._collect_sandbox_operator_visibility(current_time=current_time)
    state, live_alerts = self._refresh_guarded_live_alert_state(current_time=current_time)
    runtime_alerts = [*sandbox_alerts, *live_alerts]
    running_sandbox_count = self._count_running_runs(RunMode.SANDBOX)
    running_paper_count = self._count_running_runs(RunMode.PAPER)
    running_live_count = self._count_running_runs(RunMode.LIVE)
    venue_execution_ready, venue_execution_issues = self._venue_execution.describe_capability()

    blockers: list[str] = []
    if not self._guarded_live_execution_enabled:
      blockers.append("Guarded-live venue execution is disabled in configuration.")
    if state.kill_switch.state == "engaged":
      blockers.append("Kill switch is engaged for operator-controlled runtime sessions.")
    if state.reconciliation.state != "clear":
      blockers.append("Guarded-live reconciliation has not been cleared.")
    if state.recovery.state not in {"recovered", "recovered_with_warnings"}:
      blockers.append("Guarded-live runtime recovery has not been recorded from venue snapshots.")
    if state.recovery.state == "failed":
      blockers.append("Guarded-live runtime recovery failed after the latest restart or fault drill.")
    if not venue_execution_ready:
      blockers.append(
        "Venue order execution is unavailable: "
        + (", ".join(venue_execution_issues) if venue_execution_issues else "adapter not ready")
        + "."
      )
    if state.ownership.state in {"owned", "orphaned"} and state.ownership.owner_run_id is not None:
      blockers.append(
        "Guarded-live session ownership is still held by "
        f"{state.ownership.owner_run_id}. Resume or release it before launching a new live worker."
      )
    if runtime_alerts:
      blockers.append("Unresolved operator alerts remain in runtime operations.")

    audit_events = tuple(
      sorted(state.audit_events, key=lambda event: event.timestamp, reverse=True)
    )
    incident_events = tuple(
      sorted(state.incident_events, key=lambda event: event.timestamp, reverse=True)
    )
    delivery_history = tuple(
      sorted(state.delivery_history, key=lambda record: record.attempted_at, reverse=True)
    )
    return GuardedLiveStatus(
      generated_at=current_time,
      candidacy_status="blocked" if blockers else "candidate",
      blockers=tuple(dict.fromkeys(blockers)),
      active_alerts=tuple(live_alerts),
      alert_history=state.alert_history,
      incident_events=incident_events,
      delivery_history=delivery_history,
      kill_switch=state.kill_switch,
      reconciliation=state.reconciliation,
      recovery=state.recovery,
      ownership=state.ownership,
      order_book=state.order_book,
      session_restore=state.session_restore,
      session_handoff=state.session_handoff,
      audit_events=audit_events,
      active_runtime_alert_count=len(runtime_alerts),
      running_sandbox_count=running_sandbox_count,
      running_paper_count=running_paper_count,
      running_live_count=running_live_count,
    )

  def _collect_sandbox_operator_visibility(
    self,
    *,
    current_time: datetime,
  ) -> tuple[list[OperatorAlert], list[OperatorAuditEvent]]:
    alerts: list[OperatorAlert] = []
    audit_events: list[OperatorAuditEvent] = []
    for run in self._runs.list_runs(mode=RunMode.SANDBOX.value):
      alerts.extend(self._build_operator_alerts_for_run(run=run, current_time=current_time))
      audit_events.extend(self._build_operator_audit_events_for_run(run=run, current_time=current_time))
    return alerts, audit_events

  def _refresh_guarded_live_alert_state(
    self,
    *,
    current_time: datetime,
    allow_post_remediation_recompute: bool = True,
  ) -> tuple[GuardedLiveState, list[OperatorAlert]]:
    state = self._guarded_live_state.load_state()
    active_alerts = self._build_guarded_live_operator_alerts(
      state=state,
      current_time=current_time,
    )
    merged_history = self._merge_operator_alert_history(
      existing=state.alert_history,
      active_alerts=active_alerts,
      current_time=current_time,
    )
    incident_events = self._build_guarded_live_incident_events(
      previous_history=state.alert_history,
      merged_history=merged_history,
      current_time=current_time,
    )
    delivery_records = state.delivery_history
    new_incident_events, new_delivery_records, auto_remediation_executed = self._deliver_guarded_live_incident_events(
      incident_events=incident_events,
      current_time=current_time,
    )
    delivery_records = tuple((*new_delivery_records, *delivery_records))
    provider_synced_incident_events, provider_synced_delivery_history, provider_pull_audit_events, provider_pull_executed = (
      self._pull_sync_guarded_live_provider_recovery(
        incident_events=tuple((*new_incident_events, *state.incident_events)),
        delivery_history=delivery_records,
        current_time=current_time,
      )
    )
    delivery_records = provider_synced_delivery_history
    workflow_incident_events, workflow_delivery_history, workflow_audit_events = (
      self._refresh_guarded_live_incident_workflow(
        incident_events=provider_synced_incident_events,
        delivery_history=delivery_records,
        current_time=current_time,
      )
    )
    delivery_records = workflow_delivery_history
    refreshed_incident_events = self._apply_incident_delivery_state(
      incident_events=workflow_incident_events,
      delivery_history=delivery_records,
    )
    retry_delivery_records = self._retry_guarded_live_incident_deliveries(
      incident_events=refreshed_incident_events,
      delivery_history=delivery_records,
      current_time=current_time,
    )
    if retry_delivery_records:
      delivery_records = tuple((*retry_delivery_records, *delivery_records))
      refreshed_incident_events = self._apply_incident_delivery_state(
        incident_events=refreshed_incident_events,
        delivery_history=delivery_records,
      )
    if (
      merged_history != state.alert_history
      or refreshed_incident_events != state.incident_events
      or delivery_records != state.delivery_history
      or bool(provider_pull_audit_events)
      or bool(workflow_audit_events)
    ):
      latest_state = self._guarded_live_state.load_state()
      state = self._persist_guarded_live_state(
        replace(
          latest_state,
          alert_history=merged_history,
          incident_events=refreshed_incident_events,
          delivery_history=delivery_records,
          audit_events=tuple((*provider_pull_audit_events, *workflow_audit_events, *latest_state.audit_events)),
        )
      )
    if (auto_remediation_executed or provider_pull_executed) and allow_post_remediation_recompute:
      return self._refresh_guarded_live_alert_state(
        current_time=current_time,
        allow_post_remediation_recompute=False,
      )
    return state, active_alerts

  def engage_guarded_live_kill_switch(
    self,
    *,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    stopped_runs = self._stop_runs_for_kill_switch(actor=actor, reason=reason)
    activation_count = state.kill_switch.activation_count
    if state.kill_switch.state != "engaged":
      activation_count += 1
    kill_switch = GuardedLiveKillSwitch(
      state="engaged",
      reason=reason,
      updated_at=current_time,
      updated_by=actor,
      activation_count=activation_count,
      last_engaged_at=current_time,
      last_released_at=state.kill_switch.last_released_at,
    )
    event = OperatorAuditEvent(
      event_id=f"guarded-live-kill-switch-engaged:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_kill_switch_engaged",
      summary="Guarded-live kill switch engaged.",
      detail=(
        f"Reason: {reason}. Stopped {len(stopped_runs)} operator-controlled runtime "
        f"session(s): {', '.join(stopped_runs) if stopped_runs else 'none'}."
      ),
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        state,
        kill_switch=kill_switch,
        audit_events=(event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  def release_guarded_live_kill_switch(
    self,
    *,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    kill_switch = GuardedLiveKillSwitch(
      state="released",
      reason=reason,
      updated_at=current_time,
      updated_by=actor,
      activation_count=state.kill_switch.activation_count,
      last_engaged_at=state.kill_switch.last_engaged_at,
      last_released_at=current_time,
    )
    event = OperatorAuditEvent(
      event_id=f"guarded-live-kill-switch-released:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_kill_switch_released",
      summary="Guarded-live kill switch released.",
      detail=f"Reason: {reason}. Operator-controlled runtime sessions may start again.",
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        state,
        kill_switch=kill_switch,
        audit_events=(event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  def run_guarded_live_reconciliation(
    self,
    *,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    reconciliation = self._build_guarded_live_reconciliation(
      state=state,
      checked_at=current_time,
      checked_by=actor,
    )
    event = OperatorAuditEvent(
      event_id=f"guarded-live-reconciliation-ran:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_reconciliation_ran",
      summary="Guarded-live reconciliation recorded.",
      detail=f"Reason: {reason}. {reconciliation.summary}",
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        state,
        reconciliation=reconciliation,
        audit_events=(event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  def recover_guarded_live_runtime_state(
    self,
    *,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    snapshot = self._select_guarded_live_recovery_snapshot(state)
    recovered_exposures, recovery_issues = self._recover_exposures_from_venue_snapshot(snapshot)
    recovered_open_orders = snapshot.open_orders or state.order_book.open_orders
    if not snapshot.open_orders and state.order_book.open_orders:
      recovery_issues = (*recovery_issues, "using_durable_order_book_sync")

    if snapshot.verification_state == "unavailable":
      recovery_state = GuardedLiveRuntimeRecovery(
        state="failed",
        recovered_at=current_time,
        recovered_by=actor,
        reason=reason,
        source_snapshot_at=snapshot.captured_at,
        source_verification_state=snapshot.verification_state,
        summary="Guarded-live runtime recovery failed because no usable venue snapshot was available.",
        exposures=(),
        open_orders=(),
        issues=tuple(snapshot.issues),
      )
    else:
      recovered_with_warnings = bool(recovery_issues) or snapshot.verification_state != "verified"
      recovery_state = GuardedLiveRuntimeRecovery(
        state="recovered_with_warnings" if recovered_with_warnings else "recovered",
        recovered_at=current_time,
        recovered_by=actor,
        reason=reason,
        source_snapshot_at=snapshot.captured_at,
        source_verification_state=snapshot.verification_state,
        summary=(
          "Guarded-live runtime state recovered from the latest verified venue snapshot."
          if not recovered_with_warnings
          else "Guarded-live runtime state recovered from venue data with follow-up issues to review."
        ),
        exposures=recovered_exposures,
        open_orders=recovered_open_orders,
        issues=tuple(dict.fromkeys((*snapshot.issues, *recovery_issues))),
      )
    projected_state = replace(state, recovery=recovery_state)
    refreshed_reconciliation = self._build_guarded_live_reconciliation(
      state=projected_state,
      checked_at=current_time,
      checked_by=actor,
    )

    event = OperatorAuditEvent(
      event_id=f"guarded-live-runtime-recovered:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_runtime_recovered",
      summary="Guarded-live runtime recovery recorded.",
      detail=(
        f"Reason: {reason}. {recovery_state.summary} "
        f"Recovered {len(recovery_state.exposures)} exposure(s) and {len(recovery_state.open_orders)} open order(s)."
      ),
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        projected_state,
        reconciliation=refreshed_reconciliation,
        recovery=recovery_state,
        audit_events=(event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  def acknowledge_guarded_live_incident(
    self,
    *,
    event_id: str,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state, _ = self._refresh_guarded_live_alert_state(current_time=current_time)
    incident = self._require_active_guarded_live_incident(state=state, event_id=event_id)
    if incident.acknowledgment_state == "acknowledged":
      return self.get_guarded_live_status()

    updated_incident = replace(
      incident,
      acknowledgment_state="acknowledged",
      acknowledged_at=current_time,
      acknowledged_by=actor,
      acknowledgment_reason=reason,
      next_escalation_at=None,
    )
    incident_events = self._replace_incident_event(
      incident_events=state.incident_events,
      updated_incident=updated_incident,
    )
    delivery_history = self._suppress_pending_incident_retries(
      delivery_history=state.delivery_history,
      incident_event_id=event_id,
      reason="acknowledged_by_operator",
    )
    updated_incident, delivery_history = self._sync_incident_provider_workflow(
      incident=updated_incident,
      delivery_history=delivery_history,
      current_time=current_time,
      action="acknowledge",
      actor=actor,
      detail=reason,
    )
    incident_events = self._replace_incident_event(
      incident_events=incident_events,
      updated_incident=updated_incident,
    )
    incident_events = self._apply_incident_delivery_state(
      incident_events=incident_events,
      delivery_history=delivery_history,
    )
    audit_event = OperatorAuditEvent(
      event_id=f"guarded-live-incident-acknowledged:{event_id}:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_incident_acknowledged",
      summary=f"Guarded-live incident acknowledged for {incident.alert_id}.",
      detail=(
        f"Reason: {reason}. Incident {event_id} acknowledged and pending retries suppressed. "
        f"Provider workflow: {updated_incident.provider_workflow_state}."
      ),
      run_id=incident.run_id,
      session_id=incident.session_id,
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        state,
        incident_events=incident_events,
        delivery_history=delivery_history,
        audit_events=(audit_event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  def remediate_guarded_live_incident(
    self,
    *,
    event_id: str,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state, _ = self._refresh_guarded_live_alert_state(current_time=current_time)
    incident = self._require_active_guarded_live_incident(state=state, event_id=event_id)
    if incident.remediation.state == "not_applicable":
      raise ValueError("Guarded-live incident does not expose a remediation workflow")

    incident, local_results = self._execute_local_incident_remediation(
      incident=incident,
      actor=actor,
      current_time=current_time,
    )

    delivery_history = self._suppress_pending_incident_retries(
      delivery_history=state.delivery_history,
      incident_event_id=event_id,
      reason="manual_remediation_requested",
      phase="provider_remediate",
    )
    updated_incident, remediation_records = self._request_incident_remediation(
      incident=incident,
      delivery_history=delivery_history,
      current_time=current_time,
      actor=actor,
      detail=reason,
    )
    delivery_history = tuple((*remediation_records, *delivery_history))
    incident_events = self._replace_incident_event(
      incident_events=state.incident_events,
      updated_incident=updated_incident,
    )
    incident_events = self._apply_incident_delivery_state(
      incident_events=incident_events,
      delivery_history=delivery_history,
    )
    audit_event = OperatorAuditEvent(
      event_id=f"guarded-live-incident-remediation-requested:{event_id}:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_incident_remediation_requested",
      summary=f"Guarded-live remediation requested for {incident.alert_id}.",
      detail=(
        f"Reason: {reason}. Remediation state: {updated_incident.remediation.state}. "
        f"Provider workflow: {updated_incident.provider_workflow_state}. "
        f"Local execution: {self._summarize_local_remediation_results(local_results)}."
      ),
      run_id=incident.run_id,
      session_id=incident.session_id,
      source="guarded_live",
    )
    latest_state = self._guarded_live_state.load_state()
    self._persist_guarded_live_state(
      replace(
        latest_state,
        incident_events=incident_events,
        delivery_history=delivery_history,
        audit_events=(audit_event, *latest_state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  def escalate_guarded_live_incident(
    self,
    *,
    event_id: str,
    actor: str,
    reason: str,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state, _ = self._refresh_guarded_live_alert_state(current_time=current_time)
    incident = self._require_active_guarded_live_incident(state=state, event_id=event_id)
    if incident.escalation_level >= self._operator_alert_incident_max_escalations:
      raise ValueError("incident escalation limit reached")

    (
      updated_incident,
      delivery_history,
      escalation_audit_event,
    ) = self._escalate_incident_event(
      incident=incident,
      delivery_history=state.delivery_history,
      current_time=current_time,
      actor=actor,
      reason=reason,
      trigger="manual_operator_escalation",
    )
    incident_events = self._replace_incident_event(
      incident_events=state.incident_events,
      updated_incident=updated_incident,
    )
    incident_events = self._apply_incident_delivery_state(
      incident_events=incident_events,
      delivery_history=delivery_history,
    )
    self._persist_guarded_live_state(
      replace(
        state,
        incident_events=incident_events,
        delivery_history=delivery_history,
        audit_events=(escalation_audit_event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  def require_operator_alert_external_sync_token(self, token: str | None) -> None:
    if self._operator_alert_external_sync_token is None:
      return
    if token != self._operator_alert_external_sync_token:
      raise PermissionError("invalid operator incident sync token")

  def sync_guarded_live_incident_from_external(
    self,
    *,
    provider: str,
    event_kind: str,
    actor: str,
    detail: str,
    alert_id: str | None = None,
    external_reference: str | None = None,
    workflow_reference: str | None = None,
    occurred_at: datetime | None = None,
    escalation_level: int | None = None,
    payload: dict[str, Any] | None = None,
  ) -> GuardedLiveStatus:
    current_time = self._clock()
    state, _ = self._refresh_guarded_live_alert_state(current_time=current_time)
    synced_at = occurred_at or current_time
    normalized_provider = provider.strip().lower().replace(" ", "_")
    normalized_kind = self._normalize_external_incident_event_kind(event_kind)
    normalized_payload = self._normalize_incident_workflow_payload(payload)
    incident = self._find_guarded_live_incident_for_external_sync(
      state=state,
      alert_id=alert_id,
      external_reference=external_reference,
    )
    payload_reference = self._extract_incident_payload_reference(normalized_payload)
    provider_workflow_reference = (
      workflow_reference
      or self._first_non_empty_string(
        normalized_payload.get("workflow_reference"),
        normalized_payload.get("provider_workflow_reference"),
      )
    )
    effective_reference = (
      external_reference
      or payload_reference
      or incident.external_reference
      or alert_id
      or incident.alert_id
    )
    detail_copy = (
      detail.strip()
      or self._first_non_empty_string(
        normalized_payload.get("detail"),
        normalized_payload.get("remediation_detail"),
        normalized_payload.get("status_detail"),
        normalized_payload.get("summary"),
        normalized_payload.get("message"),
      )
      or f"{normalized_provider}_{normalized_kind}"
    )
    updated_incident = replace(
      incident,
      paging_provider=normalized_provider or incident.paging_provider,
      external_provider=normalized_provider,
      external_reference=effective_reference,
      provider_workflow_reference=provider_workflow_reference or incident.provider_workflow_reference,
      external_last_synced_at=synced_at,
    )
    delivery_history = state.delivery_history
    local_results: tuple[MarketDataRemediationResult, ...] = ()
    workflow_reference_for_delivery = (
      provider_workflow_reference
      or incident.provider_workflow_reference
      or effective_reference
    )

    if normalized_kind == "triggered":
      updated_incident = replace(
        updated_incident,
        external_status="triggered",
        paging_status="triggered",
      )
      delivery_history = self._confirm_external_provider_workflow(
        delivery_history=delivery_history,
        incident=incident,
        provider=normalized_provider,
        event_kind=normalized_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference_for_delivery,
      )
    elif normalized_kind == "acknowledged":
      if updated_incident.acknowledgment_state != "acknowledged":
        updated_incident = replace(
          updated_incident,
          acknowledgment_state="acknowledged",
          acknowledged_at=synced_at,
          acknowledged_by=f"{normalized_provider}:{actor}",
          acknowledgment_reason=detail_copy,
          next_escalation_at=None,
        )
      updated_incident = replace(
        updated_incident,
        external_status="acknowledged",
        paging_status="acknowledged",
      )
      delivery_history = self._suppress_pending_incident_retries(
        delivery_history=delivery_history,
        incident_event_id=incident.event_id,
        reason=f"external_acknowledged:{normalized_provider}",
      )
      delivery_history = self._confirm_external_provider_workflow(
        delivery_history=delivery_history,
        incident=incident,
        provider=normalized_provider,
        event_kind=normalized_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference_for_delivery,
      )
    elif normalized_kind == "escalated":
      next_level = max(updated_incident.escalation_level + 1, escalation_level or 1)
      next_level = min(next_level, self._operator_alert_incident_max_escalations)
      next_escalation_at = None
      if (
        updated_incident.acknowledgment_state != "acknowledged"
        and next_level < self._operator_alert_incident_max_escalations
      ):
        next_escalation_at = synced_at + timedelta(
          seconds=self._resolve_incident_escalation_backoff_seconds(next_level)
        )
      updated_incident = replace(
        updated_incident,
        escalation_level=next_level,
        escalation_state="escalated",
        last_escalated_at=synced_at,
        last_escalated_by=f"{normalized_provider}:{actor}",
        escalation_reason=detail_copy,
        next_escalation_at=next_escalation_at,
        external_status="escalated",
        paging_status="escalated",
      )
      delivery_history = self._confirm_external_provider_workflow(
        delivery_history=delivery_history,
        incident=incident,
        provider=normalized_provider,
        event_kind=normalized_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference_for_delivery,
      )
    elif normalized_kind == "resolved":
      if updated_incident.acknowledgment_state != "acknowledged":
        updated_incident = replace(
          updated_incident,
          acknowledgment_state="acknowledged",
          acknowledged_at=synced_at,
          acknowledged_by=f"{normalized_provider}:{actor}",
          acknowledgment_reason=detail_copy,
        )
      updated_incident = replace(
        updated_incident,
        external_status="resolved",
        paging_status="resolved",
        next_escalation_at=None,
      )
      delivery_history = self._suppress_pending_incident_retries(
        delivery_history=delivery_history,
        incident_event_id=incident.event_id,
        reason=f"external_resolved:{normalized_provider}",
      )
      delivery_history = self._confirm_external_provider_workflow(
        delivery_history=delivery_history,
        incident=incident,
        provider=normalized_provider,
        event_kind=normalized_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference_for_delivery,
      )
    elif normalized_kind == "remediation_requested":
      delivery_history = self._suppress_pending_incident_retries(
        delivery_history=delivery_history,
        incident_event_id=incident.event_id,
        reason=f"external_remediation_synced:{normalized_provider}:{normalized_kind}",
      )
      updated_incident = self._apply_external_remediation_sync(
        incident=updated_incident,
        next_state="requested",
        event_kind=normalized_kind,
        provider=normalized_provider,
        actor=actor,
        detail=detail_copy,
        synced_at=synced_at,
        workflow_reference=workflow_reference_for_delivery,
        payload=normalized_payload,
      )
      delivery_history = self._confirm_external_provider_workflow(
        delivery_history=delivery_history,
        incident=incident,
        provider=normalized_provider,
        event_kind=normalized_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference_for_delivery,
      )
    elif normalized_kind == "remediation_started":
      delivery_history = self._suppress_pending_incident_retries(
        delivery_history=delivery_history,
        incident_event_id=incident.event_id,
        reason=f"external_remediation_synced:{normalized_provider}:{normalized_kind}",
      )
      updated_incident = self._apply_external_remediation_sync(
        incident=updated_incident,
        next_state="provider_recovering",
        event_kind=normalized_kind,
        provider=normalized_provider,
        actor=actor,
        detail=detail_copy,
        synced_at=synced_at,
        workflow_reference=workflow_reference_for_delivery,
        payload=normalized_payload,
      )
      delivery_history = self._confirm_external_provider_workflow(
        delivery_history=delivery_history,
        incident=incident,
        provider=normalized_provider,
        event_kind=normalized_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference_for_delivery,
      )
    elif normalized_kind == "remediation_completed":
      delivery_history = self._suppress_pending_incident_retries(
        delivery_history=delivery_history,
        incident_event_id=incident.event_id,
        reason=f"external_remediation_synced:{normalized_provider}:{normalized_kind}",
      )
      updated_incident = self._apply_external_remediation_sync(
        incident=updated_incident,
        next_state="provider_recovered",
        event_kind=normalized_kind,
        provider=normalized_provider,
        actor=actor,
        detail=detail_copy,
        synced_at=synced_at,
        workflow_reference=workflow_reference_for_delivery,
        payload=normalized_payload,
      )
      updated_incident, local_results = self._execute_local_incident_remediation(
        incident=updated_incident,
        actor=f"{normalized_provider}:{actor}",
        current_time=synced_at,
      )
      delivery_history = self._confirm_external_provider_workflow(
        delivery_history=delivery_history,
        incident=incident,
        provider=normalized_provider,
        event_kind=normalized_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference_for_delivery,
      )
    elif normalized_kind == "remediation_failed":
      delivery_history = self._suppress_pending_incident_retries(
        delivery_history=delivery_history,
        incident_event_id=incident.event_id,
        reason=f"external_remediation_synced:{normalized_provider}:{normalized_kind}",
      )
      updated_incident = self._apply_external_remediation_sync(
        incident=updated_incident,
        next_state="failed",
        event_kind=normalized_kind,
        provider=normalized_provider,
        actor=actor,
        detail=detail_copy,
        synced_at=synced_at,
        workflow_reference=workflow_reference_for_delivery,
        payload=normalized_payload,
      )
      delivery_history = self._confirm_external_provider_workflow(
        delivery_history=delivery_history,
        incident=incident,
        provider=normalized_provider,
        event_kind=normalized_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference_for_delivery,
      )
    else:
      raise ValueError(f"unsupported external incident event kind: {event_kind}")

    provider_phase = self._provider_phase_for_event_kind(normalized_kind)
    if provider_phase is not None:
      updated_incident = replace(
        updated_incident,
        provider_workflow_state="delivered",
        provider_workflow_action=provider_phase.removeprefix("provider_"),
        provider_workflow_reference=workflow_reference_for_delivery,
        provider_workflow_last_attempted_at=synced_at,
      )
      if updated_incident.remediation.state != "not_applicable":
        provider_recovery = updated_incident.remediation.provider_recovery
        generic_workflow_states = {"unknown", "idle", "not_supported", "retrying"}
        aligned_provider_recovery = provider_recovery
        if (
          normalized_provider == "pagerduty"
          and provider_recovery.pagerduty.incident_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            pagerduty=replace(
              aligned_provider_recovery.pagerduty,
              incident_status="delivered",
            ),
          )
        elif (
          normalized_provider == "opsgenie"
          and provider_recovery.opsgenie.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            opsgenie=replace(
              aligned_provider_recovery.opsgenie,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "incidentio"
          and provider_recovery.incidentio.incident_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            incidentio=replace(
              aligned_provider_recovery.incidentio,
              incident_status="delivered",
            ),
          )
        elif (
          normalized_provider == "firehydrant"
          and provider_recovery.firehydrant.incident_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            firehydrant=replace(
              aligned_provider_recovery.firehydrant,
              incident_status="delivered",
            ),
          )
        elif (
          normalized_provider == "rootly"
          and provider_recovery.rootly.incident_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            rootly=replace(
              aligned_provider_recovery.rootly,
              incident_status="delivered",
            ),
          )
        elif (
          normalized_provider == "blameless"
          and provider_recovery.blameless.incident_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            blameless=replace(
              aligned_provider_recovery.blameless,
              incident_status="delivered",
            ),
          )
        elif (
          normalized_provider == "xmatters"
          and provider_recovery.xmatters.incident_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            xmatters=replace(
              aligned_provider_recovery.xmatters,
              incident_status="delivered",
            ),
          )
        elif (
          normalized_provider == "servicenow"
          and provider_recovery.servicenow.incident_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            servicenow=replace(
              aligned_provider_recovery.servicenow,
              incident_status="delivered",
            ),
          )
        elif (
          normalized_provider == "squadcast"
          and provider_recovery.squadcast.incident_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            squadcast=replace(
              aligned_provider_recovery.squadcast,
              incident_status="delivered",
            ),
          )
        elif (
          normalized_provider == "bigpanda"
          and provider_recovery.bigpanda.incident_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            bigpanda=replace(
              aligned_provider_recovery.bigpanda,
              incident_status="delivered",
            ),
          )
        elif (
          normalized_provider == "grafana_oncall"
          and provider_recovery.grafana_oncall.incident_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            grafana_oncall=replace(
              aligned_provider_recovery.grafana_oncall,
              incident_status="delivered",
            ),
          )
        elif (
          normalized_provider == "zenduty"
          and provider_recovery.zenduty.incident_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            zenduty=replace(
              aligned_provider_recovery.zenduty,
              incident_status="delivered",
            ),
          )
        elif (
          normalized_provider == "splunk_oncall"
          and provider_recovery.splunk_oncall.incident_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            splunk_oncall=replace(
              aligned_provider_recovery.splunk_oncall,
              incident_status="delivered",
            ),
          )
        elif (
          normalized_provider == "jira_service_management"
          and provider_recovery.jira_service_management.incident_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            jira_service_management=replace(
              aligned_provider_recovery.jira_service_management,
              incident_status="delivered",
            ),
          )
        elif (
          normalized_provider == "pagertree"
          and provider_recovery.pagertree.incident_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            pagertree=replace(
              aligned_provider_recovery.pagertree,
              incident_status="delivered",
            ),
          )
        elif (
          normalized_provider == "alertops"
          and provider_recovery.alertops.incident_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            alertops=replace(
              aligned_provider_recovery.alertops,
              incident_status="delivered",
            ),
          )
        elif (
          normalized_provider == "signl4"
          and provider_recovery.signl4.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            signl4=replace(
              aligned_provider_recovery.signl4,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "ilert"
          and provider_recovery.ilert.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            ilert=replace(
              aligned_provider_recovery.ilert,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "betterstack"
          and provider_recovery.betterstack.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            betterstack=replace(
              aligned_provider_recovery.betterstack,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "onpage"
          and provider_recovery.onpage.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            onpage=replace(
              aligned_provider_recovery.onpage,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "allquiet"
          and provider_recovery.allquiet.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            allquiet=replace(
              aligned_provider_recovery.allquiet,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "moogsoft"
          and provider_recovery.moogsoft.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            moogsoft=replace(
              aligned_provider_recovery.moogsoft,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "spikesh"
          and provider_recovery.spikesh.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            spikesh=replace(
              aligned_provider_recovery.spikesh,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "dutycalls"
          and provider_recovery.dutycalls.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            dutycalls=replace(
              aligned_provider_recovery.dutycalls,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "incidenthub"
          and provider_recovery.incidenthub.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            incidenthub=replace(
              aligned_provider_recovery.incidenthub,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "resolver"
          and provider_recovery.resolver.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            resolver=replace(
              aligned_provider_recovery.resolver,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "openduty"
          and provider_recovery.openduty.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            openduty=replace(
              aligned_provider_recovery.openduty,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "cabot"
          and provider_recovery.cabot.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            cabot=replace(
              aligned_provider_recovery.cabot,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "haloitsm"
          and provider_recovery.haloitsm.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            haloitsm=replace(
              aligned_provider_recovery.haloitsm,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "incidentmanagerio"
          and provider_recovery.incidentmanagerio.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            incidentmanagerio=replace(
              aligned_provider_recovery.incidentmanagerio,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "oneuptime"
          and provider_recovery.oneuptime.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            oneuptime=replace(
              aligned_provider_recovery.oneuptime,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "squzy"
          and provider_recovery.squzy.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            squzy=replace(
              aligned_provider_recovery.squzy,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "crisescontrol"
          and provider_recovery.crisescontrol.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            crisescontrol=replace(
              aligned_provider_recovery.crisescontrol,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "freshservice"
          and provider_recovery.freshservice.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            freshservice=replace(
              aligned_provider_recovery.freshservice,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "freshdesk"
          and provider_recovery.freshdesk.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            freshdesk=replace(
              aligned_provider_recovery.freshdesk,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "happyfox"
          and provider_recovery.happyfox.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            happyfox=replace(
              aligned_provider_recovery.happyfox,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "zendesk"
          and provider_recovery.zendesk.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            zendesk=replace(
              aligned_provider_recovery.zendesk,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "zohodesk"
          and provider_recovery.zohodesk.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            zohodesk=replace(
              aligned_provider_recovery.zohodesk,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "helpscout"
          and provider_recovery.helpscout.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            helpscout=replace(
              aligned_provider_recovery.helpscout,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "kayako"
          and provider_recovery.kayako.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            kayako=replace(
              aligned_provider_recovery.kayako,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "intercom"
          and provider_recovery.intercom.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            intercom=replace(
              aligned_provider_recovery.intercom,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "front"
          and provider_recovery.front.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            front=replace(
              aligned_provider_recovery.front,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "servicedeskplus"
          and provider_recovery.servicedeskplus.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            servicedeskplus=replace(
              aligned_provider_recovery.servicedeskplus,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "sysaid"
          and provider_recovery.sysaid.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            sysaid=replace(
              aligned_provider_recovery.sysaid,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "bmchelix"
          and provider_recovery.bmchelix.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            bmchelix=replace(
              aligned_provider_recovery.bmchelix,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "solarwindsservicedesk"
          and provider_recovery.solarwindsservicedesk.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            solarwindsservicedesk=replace(
              aligned_provider_recovery.solarwindsservicedesk,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "topdesk"
          and provider_recovery.topdesk.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            topdesk=replace(
              aligned_provider_recovery.topdesk,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "invgateservicedesk"
          and provider_recovery.invgateservicedesk.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            invgateservicedesk=replace(
              aligned_provider_recovery.invgateservicedesk,
              alert_status="delivered",
            ),
          )
        elif (
          normalized_provider == "opsramp"
          and provider_recovery.opsramp.alert_status in generic_workflow_states
        ):
          aligned_provider_recovery = replace(
            aligned_provider_recovery,
            opsramp=replace(
              aligned_provider_recovery.opsramp,
              alert_status="delivered",
            ),
          )
        updated_incident = replace(
          updated_incident,
          remediation=replace(
            updated_incident.remediation,
            provider_recovery=self._refresh_provider_recovery_phase_graphs(
              provider_recovery=replace(
                aligned_provider_recovery,
                status_machine=self._build_provider_recovery_status_machine(
                  existing=aligned_provider_recovery.status_machine,
                  remediation_state=updated_incident.remediation.state,
                  event_kind=aligned_provider_recovery.status_machine.last_event_kind,
                  workflow_state="delivered",
                  workflow_action=provider_phase.removeprefix("provider_"),
                  job_state=aligned_provider_recovery.status_machine.job_state,
                  sync_state=aligned_provider_recovery.status_machine.sync_state,
                  detail=aligned_provider_recovery.status_machine.last_detail,
                  event_at=synced_at,
                  attempt_number=aligned_provider_recovery.status_machine.attempt_number,
                ),
              ),
              synced_at=synced_at,
            ),
          ),
        )

    incident_events = self._replace_incident_event(
      incident_events=state.incident_events,
      updated_incident=updated_incident,
    )
    incident_events = self._apply_incident_delivery_state(
      incident_events=incident_events,
      delivery_history=delivery_history,
    )
    audit_event = OperatorAuditEvent(
      event_id=f"guarded-live-incident-external-sync:{incident.event_id}:{synced_at.isoformat()}",
      timestamp=synced_at,
      actor=f"{normalized_provider}:{actor}",
      kind="guarded_live_incident_external_synced",
      summary=f"Guarded-live incident synced from external paging workflow for {incident.alert_id}.",
      detail=(
        f"External event {normalized_kind} synced from {normalized_provider}. "
        f"Reference: {effective_reference}. Detail: {detail_copy}. "
        f"Local remediation: {self._summarize_local_remediation_results(local_results)}."
      ),
      run_id=incident.run_id,
      session_id=incident.session_id,
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        state,
        incident_events=incident_events,
        delivery_history=delivery_history,
        audit_events=(audit_event, *state.audit_events),
      )
    )
    return self.get_guarded_live_status()

  @staticmethod
  def _normalize_external_incident_event_kind(event_kind: str) -> str:
    normalized = event_kind.strip().lower().replace("-", "_")
    mapping = {
      "recovery_requested": "remediation_requested",
      "recovery_started": "remediation_started",
      "recovered": "remediation_completed",
      "recovery_completed": "remediation_completed",
      "recovery_failed": "remediation_failed",
    }
    return mapping.get(normalized, normalized)

  @staticmethod
  def _first_non_empty_string(*values: Any) -> str | None:
    for value in values:
      if not isinstance(value, str):
        continue
      stripped = value.strip()
      if stripped:
        return stripped
    return None

  @staticmethod
  def _extract_payload_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
      return value
    return {}

  @classmethod
  def _merge_payload_mappings(cls, *values: Any) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for value in values:
      if isinstance(value, dict):
        merged.update(cls._extract_payload_mapping(value))
    return merged

  @classmethod
  def _extract_string_tuple(cls, *values: Any) -> tuple[str, ...]:
    items: list[str] = []
    for value in values:
      if isinstance(value, str):
        stripped = value.strip()
        if stripped and stripped not in items:
          items.append(stripped)
        continue
      if isinstance(value, (list, tuple, set)):
        for item in value:
          if not isinstance(item, str):
            continue
          stripped = item.strip()
          if stripped and stripped not in items:
            items.append(stripped)
    return tuple(items)

  @classmethod
  def _parse_payload_datetime(cls, value: Any) -> datetime | None:
    if isinstance(value, datetime):
      return value
    if not isinstance(value, str):
      return None
    candidate = value.strip()
    if not candidate:
      return None
    if candidate.endswith("Z"):
      candidate = f"{candidate[:-1]}+00:00"
    try:
      return datetime.fromisoformat(candidate)
    except ValueError:
      return None

  @staticmethod
  def _parse_payload_int(*values: Any) -> int | None:
    for value in values:
      if isinstance(value, bool):
        continue
      if isinstance(value, int):
        return value
      if isinstance(value, float) and value.is_integer():
        return int(value)
      if not isinstance(value, str):
        continue
      candidate = value.strip()
      if not candidate:
        continue
      try:
        return int(candidate)
      except ValueError:
        continue
    return None

  @classmethod
  def _normalize_incident_workflow_payload_value(cls, value: Any) -> Any:
    if value is None or isinstance(value, (str, bool)):
      return value
    if isinstance(value, datetime):
      return value.isoformat()
    if isinstance(value, int):
      return value
    if isinstance(value, float):
      return value
    if isinstance(value, Number):
      return float(value)
    if isinstance(value, dict):
      normalized: dict[str, Any] = {}
      for key, nested_value in value.items():
        key_copy = str(key).strip()
        if not key_copy:
          continue
        normalized[key_copy] = cls._normalize_incident_workflow_payload_value(nested_value)
      return normalized
    if isinstance(value, (list, tuple, set)):
      return [cls._normalize_incident_workflow_payload_value(item) for item in value]
    return str(value)

  @classmethod
  def _normalize_incident_workflow_payload(
    cls,
    payload: dict[str, Any] | None,
  ) -> dict[str, Any]:
    if not payload:
      return {}
    return {
      key_copy: cls._normalize_incident_workflow_payload_value(value)
      for key, value in payload.items()
      if (key_copy := str(key).strip())
    }

  @staticmethod
  def _merge_incident_workflow_payload(
    *,
    existing: dict[str, Any],
    incoming: dict[str, Any],
  ) -> dict[str, Any]:
    if not existing:
      return dict(incoming)
    if not incoming:
      return dict(existing)
    merged = dict(existing)
    merged.update(incoming)
    return merged

  def _extract_incident_payload_reference(self, payload: dict[str, Any]) -> str | None:
    return self._first_non_empty_string(
      payload.get("workflow_reference"),
      payload.get("provider_workflow_reference"),
      payload.get("reference"),
      payload.get("job_reference"),
      payload.get("job_id"),
      payload.get("execution_id"),
      payload.get("recovery_id"),
    )

  @staticmethod
  def _provider_recovery_lifecycle_for_remediation_state(remediation_state: str) -> str:
    mapping = {
      "requested": "requested",
      "provider_recovering": "recovering",
      "provider_recovered": "recovered",
      "executed": "verified",
      "completed": "verified",
      "partial": "partially_verified",
      "failed": "failed",
    }
    return mapping.get(remediation_state, remediation_state or "not_synced")

  @staticmethod
  def _provider_recovery_lifecycle_for_event(
    *,
    remediation_state: str,
    event_kind: str | None,
  ) -> str:
    event_mapping = {
      "remediation_requested": "requested",
      "remediation_started": "recovering",
      "remediation_completed": "recovered",
      "remediation_failed": "failed",
      "local_remediation_requested": "requested",
      "local_verification_executed": "verified",
      "local_verification_failed": "failed",
      "provider_resolve_requested": "resolved",
      "provider_resolve_confirmed": "resolved",
    }
    if event_kind is not None and event_kind in event_mapping:
      return event_mapping[event_kind]
    return TradingApplication._provider_recovery_lifecycle_for_remediation_state(remediation_state)

  @staticmethod
  def _provider_recovery_machine_defaults_for_event(
    *,
    remediation_state: str,
    event_kind: str | None = None,
  ) -> tuple[str, str, str]:
    event_mapping = {
      "remediation_requested": ("provider_requested", "requested", "provider_confirmed"),
      "remediation_started": ("provider_running", "running", "provider_confirmed"),
      "remediation_completed": ("local_verification_pending", "completed", "provider_confirmed"),
      "remediation_failed": ("provider_failed", "failed", "provider_confirmed"),
      "local_remediation_requested": ("provider_requested", "requested", "local_dispatched"),
      "local_verification_executed": ("verified", "verified", "bidirectional_synced"),
      "local_verification_failed": ("verification_failed", "failed", "local_failed"),
      "provider_resolve_requested": ("resolved", "resolved", "bidirectional_synced"),
      "provider_resolve_confirmed": ("resolved", "resolved", "provider_confirmed"),
    }
    if event_kind is not None and event_kind in event_mapping:
      return event_mapping[event_kind]
    remediation_mapping = {
      "requested": ("provider_requested", "requested", "local_dispatched"),
      "provider_recovering": ("provider_running", "running", "provider_confirmed"),
      "provider_recovered": ("local_verification_pending", "completed", "provider_confirmed"),
      "executed": ("verified", "verified", "bidirectional_synced"),
      "completed": ("verified", "verified", "bidirectional_synced"),
      "partial": ("partially_verified", "partial", "partially_synced"),
      "failed": ("provider_failed", "failed", "provider_failed"),
      "skipped": ("verification_skipped", "skipped", "local_only"),
      "retrying": ("provider_requested", "requested", "local_retrying"),
      "suppressed": ("provider_requested", "requested", "suppressed"),
      "not_supported": ("provider_unavailable", "not_supported", "not_supported"),
      "not_configured": ("provider_unavailable", "not_configured", "not_configured"),
      "suggested": ("not_requested", "not_started", "not_synced"),
      "operator_review": ("not_requested", "not_started", "not_synced"),
      "not_applicable": ("not_requested", "not_started", "not_synced"),
    }
    return remediation_mapping.get(remediation_state, ("not_requested", "not_started", "not_synced"))

  def _build_provider_recovery_status_machine(
    self,
    *,
    existing: OperatorIncidentProviderRecoveryStatusMachine,
    remediation_state: str,
    event_kind: str | None,
    workflow_state: str | None = None,
    workflow_action: str | None = None,
    job_state: str | None = None,
    sync_state: str | None = None,
    detail: str | None = None,
    event_at: datetime | None = None,
    attempt_number: int | None = None,
    payload: dict[str, Any] | None = None,
  ) -> OperatorIncidentProviderRecoveryStatusMachine:
    payload = payload or {}
    status_payload = self._extract_payload_mapping(payload.get("status_machine"))
    default_state, default_job_state, default_sync_state = self._provider_recovery_machine_defaults_for_event(
      remediation_state=remediation_state,
      event_kind=event_kind,
    )
    return OperatorIncidentProviderRecoveryStatusMachine(
      state=self._first_non_empty_string(
        status_payload.get("state"),
        payload.get("recovery_machine_state"),
        payload.get("machine_state"),
      ) or default_state,
      workflow_state=self._first_non_empty_string(
        status_payload.get("workflow_state"),
        payload.get("workflow_state"),
        workflow_state,
        existing.workflow_state,
      ) or "idle",
      workflow_action=self._first_non_empty_string(
        status_payload.get("workflow_action"),
        payload.get("workflow_action"),
        workflow_action,
        existing.workflow_action,
      ),
      job_state=self._first_non_empty_string(
        status_payload.get("job_state"),
        payload.get("job_state"),
        payload.get("status"),
        job_state,
      ) or default_job_state,
      sync_state=self._first_non_empty_string(
        status_payload.get("sync_state"),
        payload.get("sync_state"),
        sync_state,
      ) or default_sync_state,
      last_event_kind=self._first_non_empty_string(
        status_payload.get("last_event_kind"),
        payload.get("last_event_kind"),
        event_kind,
        existing.last_event_kind,
      ),
      last_event_at=(
        self._parse_payload_datetime(status_payload.get("last_event_at"))
        or self._parse_payload_datetime(payload.get("last_event_at"))
        or event_at
        or existing.last_event_at
      ),
      last_detail=self._first_non_empty_string(
        status_payload.get("last_detail"),
        payload.get("last_detail"),
        payload.get("status_detail"),
        detail,
        existing.last_detail,
      ),
      attempt_number=(
        int(status_payload.get("attempt_number"))
        if isinstance(status_payload.get("attempt_number"), int)
        else (
          int(payload.get("attempt_number"))
          if isinstance(payload.get("attempt_number"), int)
          else (
            attempt_number
            if attempt_number is not None
            else existing.attempt_number
          )
        )
      ),
    )

  @staticmethod
  def _normalize_pagerduty_incident_phase(
    incident_status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (incident_status or "").strip().lower().replace(" ", "_")
    if normalized in {"triggered", "acknowledged", "resolved"}:
      return normalized
    return existing_phase

  @staticmethod
  def _resolve_pagerduty_responder_phase(incident_phase: str) -> str:
    if incident_phase == "triggered":
      return "awaiting_acknowledgment"
    if incident_phase == "acknowledged":
      return "engaged"
    if incident_phase == "resolved":
      return "resolved"
    return "unknown"

  @staticmethod
  def _resolve_pagerduty_urgency_phase(urgency: str | None, existing_phase: str) -> str:
    normalized = (urgency or "").strip().lower().replace(" ", "_")
    if normalized in {"high"}:
      return "high_urgency"
    if normalized in {"low"}:
      return "low_urgency"
    return existing_phase

  @staticmethod
  def _resolve_pagerduty_workflow_phase(
    *,
    lifecycle_state: str,
    workflow_action: str | None,
    incident_phase: str,
    existing_phase: str,
  ) -> str:
    if workflow_action == "resolve" or incident_phase == "resolved" or lifecycle_state == "resolved":
      return "resolved_back_synced"
    if lifecycle_state == "verified":
      return "verified_pending_resolve"
    if lifecycle_state == "recovered":
      return "awaiting_local_verification"
    if lifecycle_state == "recovering":
      return "provider_recovering"
    if lifecycle_state == "requested" or workflow_action == "remediate":
      return "remediation_requested"
    if lifecycle_state == "failed":
      return "recovery_failed"
    if workflow_action == "acknowledge" or incident_phase == "acknowledged":
      return "incident_acknowledged"
    if existing_phase != "unknown":
      return existing_phase
    return "idle"

  def _build_pagerduty_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    incident_status: str,
    urgency: str | None,
    lifecycle_state: str,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentPagerDutyRecoveryState,
  ) -> OperatorIncidentPagerDutyRecoveryPhaseGraph:
    phase_payload = self._extract_payload_mapping(payload.get("phase_graph"))
    incident_phase = self._first_non_empty_string(
      phase_payload.get("incident_phase"),
      self._normalize_pagerduty_incident_phase(incident_status, existing.phase_graph.incident_phase),
      existing.phase_graph.incident_phase,
    ) or "unknown"
    workflow_phase = self._first_non_empty_string(
      phase_payload.get("workflow_phase"),
      self._resolve_pagerduty_workflow_phase(
        lifecycle_state=lifecycle_state,
        workflow_action=status_machine.workflow_action,
        incident_phase=incident_phase,
        existing_phase=existing.phase_graph.workflow_phase,
      ),
      existing.phase_graph.workflow_phase,
    ) or "unknown"
    responder_phase = self._first_non_empty_string(
      phase_payload.get("responder_phase"),
      self._resolve_pagerduty_responder_phase(incident_phase),
      existing.phase_graph.responder_phase,
    ) or "unknown"
    urgency_phase = self._first_non_empty_string(
      phase_payload.get("urgency_phase"),
      self._resolve_pagerduty_urgency_phase(urgency, existing.phase_graph.urgency_phase),
      existing.phase_graph.urgency_phase,
    ) or "unknown"
    last_transition_at = (
      self._parse_payload_datetime(phase_payload.get("last_transition_at"))
      or self._parse_payload_datetime(payload.get("last_status_change_at"))
      or existing.phase_graph.last_transition_at
      or synced_at
    )
    return OperatorIncidentPagerDutyRecoveryPhaseGraph(
      incident_phase=incident_phase,
      workflow_phase=workflow_phase,
      responder_phase=responder_phase,
      urgency_phase=urgency_phase,
      last_transition_at=last_transition_at,
    )

  @staticmethod
  def _normalize_opsgenie_alert_phase(
    alert_status: str | None,
    acknowledged: bool | None,
    existing_phase: str,
  ) -> str:
    normalized = (alert_status or "").strip().lower().replace(" ", "_")
    if normalized in {"open", "acknowledged", "closed"}:
      return normalized
    if acknowledged is True:
      return "acknowledged"
    return existing_phase

  @staticmethod
  def _resolve_opsgenie_acknowledgment_phase(
    alert_phase: str,
    acknowledged: bool | None,
  ) -> str:
    if alert_phase == "closed":
      return "closed"
    if acknowledged is True or alert_phase == "acknowledged":
      return "acknowledged"
    if alert_phase == "open":
      return "pending_acknowledgment"
    return "unknown"

  @staticmethod
  def _resolve_opsgenie_ownership_phase(
    owner: str | None,
    teams: tuple[str, ...],
    existing_phase: str,
  ) -> str:
    if owner:
      return "assigned"
    if teams:
      return "team_routed"
    return existing_phase

  @staticmethod
  def _resolve_opsgenie_visibility_phase(seen: bool | None, existing_phase: str) -> str:
    if seen is True:
      return "seen"
    if seen is False:
      return "unseen"
    return existing_phase

  @staticmethod
  def _resolve_opsgenie_workflow_phase(
    *,
    lifecycle_state: str,
    workflow_action: str | None,
    alert_phase: str,
    existing_phase: str,
  ) -> str:
    if workflow_action == "resolve" or alert_phase == "closed" or lifecycle_state == "resolved":
      return "closed_back_synced"
    if lifecycle_state == "verified":
      return "verified_pending_close"
    if lifecycle_state == "recovered":
      return "awaiting_local_verification"
    if lifecycle_state == "recovering":
      return "provider_recovering"
    if lifecycle_state == "requested" or workflow_action == "remediate":
      return "recovery_requested"
    if lifecycle_state == "failed":
      return "recovery_failed"
    if alert_phase == "acknowledged":
      return "alert_acknowledged"
    if existing_phase != "unknown":
      return existing_phase
    return "idle"

  def _build_opsgenie_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    owner: str | None,
    acknowledged: bool | None,
    seen: bool | None,
    teams: tuple[str, ...],
    lifecycle_state: str,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentOpsgenieRecoveryState,
  ) -> OperatorIncidentOpsgenieRecoveryPhaseGraph:
    phase_payload = self._extract_payload_mapping(payload.get("phase_graph"))
    alert_phase = self._first_non_empty_string(
      phase_payload.get("alert_phase"),
      self._normalize_opsgenie_alert_phase(alert_status, acknowledged, existing.phase_graph.alert_phase),
      existing.phase_graph.alert_phase,
    ) or "unknown"
    workflow_phase = self._first_non_empty_string(
      phase_payload.get("workflow_phase"),
      self._resolve_opsgenie_workflow_phase(
        lifecycle_state=lifecycle_state,
        workflow_action=status_machine.workflow_action,
        alert_phase=alert_phase,
        existing_phase=existing.phase_graph.workflow_phase,
      ),
      existing.phase_graph.workflow_phase,
    ) or "unknown"
    acknowledgment_phase = self._first_non_empty_string(
      phase_payload.get("acknowledgment_phase"),
      self._resolve_opsgenie_acknowledgment_phase(alert_phase, acknowledged),
      existing.phase_graph.acknowledgment_phase,
    ) or "unknown"
    ownership_phase = self._first_non_empty_string(
      phase_payload.get("ownership_phase"),
      self._resolve_opsgenie_ownership_phase(owner, teams, existing.phase_graph.ownership_phase),
      existing.phase_graph.ownership_phase,
    ) or "unknown"
    visibility_phase = self._first_non_empty_string(
      phase_payload.get("visibility_phase"),
      self._resolve_opsgenie_visibility_phase(seen, existing.phase_graph.visibility_phase),
      existing.phase_graph.visibility_phase,
    ) or "unknown"
    last_transition_at = (
      self._parse_payload_datetime(phase_payload.get("last_transition_at"))
      or self._parse_payload_datetime(payload.get("updated_at"))
      or self._parse_payload_datetime(payload.get("updatedAt"))
      or existing.phase_graph.last_transition_at
      or synced_at
    )
    return OperatorIncidentOpsgenieRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      acknowledgment_phase=acknowledgment_phase,
      ownership_phase=ownership_phase,
      visibility_phase=visibility_phase,
      last_transition_at=last_transition_at,
    )

  @staticmethod
  def _normalize_incidentio_incident_phase(
    incident_status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (incident_status or "").strip().lower().replace(" ", "_")
    if normalized in {"active", "acknowledged", "resolved", "closed"}:
      return normalized
    if normalized in {"triaged"}:
      return "acknowledged"
    return existing_phase

  @staticmethod
  def _resolve_incidentio_assignment_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    if existing_phase != "unknown":
      return existing_phase
    return "unassigned"

  @staticmethod
  def _resolve_incidentio_visibility_phase(
    visibility: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (visibility or "").strip().lower().replace(" ", "_")
    if normalized in {"public", "private", "internal"}:
      return normalized
    return existing_phase

  @staticmethod
  def _resolve_incidentio_severity_phase(
    severity: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized in {"critical", "high", "warning", "medium", "low", "info"}:
      return normalized
    return existing_phase

  @staticmethod
  def _resolve_incidentio_workflow_phase(
    *,
    lifecycle_state: str,
    workflow_action: str | None,
    incident_phase: str,
    existing_phase: str,
  ) -> str:
    if workflow_action == "resolve" or incident_phase in {"resolved", "closed"} or lifecycle_state == "resolved":
      return "resolved_back_synced"
    if lifecycle_state == "verified":
      return "verified_pending_resolve"
    if lifecycle_state == "recovered":
      return "awaiting_local_verification"
    if lifecycle_state == "recovering":
      return "provider_recovering"
    if lifecycle_state == "requested" or workflow_action == "remediate":
      return "remediation_requested"
    if lifecycle_state == "failed":
      return "recovery_failed"
    if workflow_action == "acknowledge" or incident_phase == "acknowledged":
      return "incident_acknowledged"
    if existing_phase != "unknown":
      return existing_phase
    return "idle"

  def _build_incidentio_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    incident_status: str,
    severity: str | None,
    mode: str | None,
    visibility: str | None,
    assignee: str | None,
    lifecycle_state: str,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentIncidentIoRecoveryState,
  ) -> OperatorIncidentIncidentIoRecoveryPhaseGraph:
    phase_payload = self._extract_payload_mapping(payload.get("phase_graph"))
    incident_phase = self._first_non_empty_string(
      phase_payload.get("incident_phase"),
      self._normalize_incidentio_incident_phase(incident_status, existing.phase_graph.incident_phase),
      existing.phase_graph.incident_phase,
    ) or "unknown"
    workflow_phase = self._first_non_empty_string(
      phase_payload.get("workflow_phase"),
      self._resolve_incidentio_workflow_phase(
        lifecycle_state=lifecycle_state,
        workflow_action=status_machine.workflow_action,
        incident_phase=incident_phase,
        existing_phase=existing.phase_graph.workflow_phase,
      ),
      existing.phase_graph.workflow_phase,
    ) or "unknown"
    assignment_phase = self._first_non_empty_string(
      phase_payload.get("assignment_phase"),
      self._resolve_incidentio_assignment_phase(assignee, existing.phase_graph.assignment_phase),
      existing.phase_graph.assignment_phase,
    ) or "unknown"
    visibility_phase = self._first_non_empty_string(
      phase_payload.get("visibility_phase"),
      self._resolve_incidentio_visibility_phase(visibility, existing.phase_graph.visibility_phase),
      existing.phase_graph.visibility_phase,
    ) or "unknown"
    severity_phase = self._first_non_empty_string(
      phase_payload.get("severity_phase"),
      self._resolve_incidentio_severity_phase(severity, existing.phase_graph.severity_phase),
      mode,
      existing.phase_graph.severity_phase,
    ) or "unknown"
    last_transition_at = (
      self._parse_payload_datetime(phase_payload.get("last_transition_at"))
      or self._parse_payload_datetime(payload.get("updated_at"))
      or existing.phase_graph.last_transition_at
      or synced_at
    )
    return OperatorIncidentIncidentIoRecoveryPhaseGraph(
      incident_phase=incident_phase,
      workflow_phase=workflow_phase,
      assignment_phase=assignment_phase,
      visibility_phase=visibility_phase,
      severity_phase=severity_phase,
      last_transition_at=last_transition_at,
    )

  @staticmethod
  def _normalize_firehydrant_incident_phase(
    incident_status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (incident_status or "").strip().lower().replace(" ", "_")
    if normalized in {"open", "investigating", "mitigating", "monitoring", "resolved", "closed"}:
      return normalized
    return existing_phase

  @staticmethod
  def _resolve_firehydrant_ownership_phase(
    team: str | None,
    existing_phase: str,
  ) -> str:
    if team:
      return "assigned"
    if existing_phase != "unknown":
      return existing_phase
    return "unassigned"

  @staticmethod
  def _resolve_firehydrant_severity_phase(
    severity: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized in {"sev1", "critical"}:
      return "critical"
    if normalized in {"sev2", "high"}:
      return "high"
    if normalized in {"sev3", "medium"}:
      return "medium"
    if normalized in {"sev4", "low"}:
      return "low"
    return existing_phase

  @staticmethod
  def _resolve_firehydrant_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized in {"p1", "critical"}:
      return "critical"
    if normalized in {"p2", "high"}:
      return "high"
    if normalized in {"p3", "medium"}:
      return "medium"
    if normalized in {"p4", "low"}:
      return "low"
    return existing_phase

  @staticmethod
  def _resolve_firehydrant_workflow_phase(
    *,
    lifecycle_state: str,
    workflow_action: str | None,
    incident_phase: str,
    existing_phase: str,
  ) -> str:
    if workflow_action == "resolve" or incident_phase in {"resolved", "closed"} or lifecycle_state == "resolved":
      return "resolved_back_synced"
    if lifecycle_state == "verified":
      return "verified_pending_resolve"
    if lifecycle_state == "recovered":
      return "awaiting_local_verification"
    if lifecycle_state == "recovering":
      return "provider_recovering"
    if lifecycle_state == "requested" or workflow_action == "remediate":
      return "remediation_requested"
    if lifecycle_state == "failed":
      return "recovery_failed"
    if incident_phase in {"investigating", "mitigating", "monitoring"}:
      return "incident_active"
    if existing_phase != "unknown":
      return existing_phase
    return "idle"

  def _build_firehydrant_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    incident_status: str,
    severity: str | None,
    priority: str | None,
    team: str | None,
    lifecycle_state: str,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentFireHydrantRecoveryState,
  ) -> OperatorIncidentFireHydrantRecoveryPhaseGraph:
    phase_payload = self._extract_payload_mapping(payload.get("phase_graph"))
    incident_phase = self._first_non_empty_string(
      phase_payload.get("incident_phase"),
      self._normalize_firehydrant_incident_phase(incident_status, existing.phase_graph.incident_phase),
      existing.phase_graph.incident_phase,
    ) or "unknown"
    workflow_phase = self._first_non_empty_string(
      phase_payload.get("workflow_phase"),
      self._resolve_firehydrant_workflow_phase(
        lifecycle_state=lifecycle_state,
        workflow_action=status_machine.workflow_action,
        incident_phase=incident_phase,
        existing_phase=existing.phase_graph.workflow_phase,
      ),
      existing.phase_graph.workflow_phase,
    ) or "unknown"
    ownership_phase = self._first_non_empty_string(
      phase_payload.get("ownership_phase"),
      self._resolve_firehydrant_ownership_phase(team, existing.phase_graph.ownership_phase),
      existing.phase_graph.ownership_phase,
    ) or "unknown"
    severity_phase = self._first_non_empty_string(
      phase_payload.get("severity_phase"),
      self._resolve_firehydrant_severity_phase(severity, existing.phase_graph.severity_phase),
      existing.phase_graph.severity_phase,
    ) or "unknown"
    priority_phase = self._first_non_empty_string(
      phase_payload.get("priority_phase"),
      self._resolve_firehydrant_priority_phase(priority, existing.phase_graph.priority_phase),
      existing.phase_graph.priority_phase,
    ) or "unknown"
    last_transition_at = (
      self._parse_payload_datetime(phase_payload.get("last_transition_at"))
      or self._parse_payload_datetime(payload.get("updated_at"))
      or existing.phase_graph.last_transition_at
      or synced_at
    )
    return OperatorIncidentFireHydrantRecoveryPhaseGraph(
      incident_phase=incident_phase,
      workflow_phase=workflow_phase,
      ownership_phase=ownership_phase,
      severity_phase=severity_phase,
      priority_phase=priority_phase,
      last_transition_at=last_transition_at,
    )

  def _build_provider_recovery_telemetry(
    self,
    *,
    payload: dict[str, Any],
    synced_at: datetime,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    existing: OperatorIncidentProviderRecoveryTelemetry,
  ) -> OperatorIncidentProviderRecoveryTelemetry:
    telemetry_payload = self._merge_payload_mappings(
      payload.get("telemetry"),
      payload.get("provider_telemetry"),
      payload.get("remediation_telemetry"),
      payload.get("job_telemetry"),
    )
    return OperatorIncidentProviderRecoveryTelemetry(
      source=self._first_non_empty_string(
        telemetry_payload.get("source"),
        payload.get("telemetry_source"),
        existing.source,
      ) or "unknown",
      state=self._first_non_empty_string(
        telemetry_payload.get("state"),
        telemetry_payload.get("job_state"),
        payload.get("telemetry_state"),
        payload.get("job_state"),
        existing.state,
        status_machine.job_state,
      ) or "unknown",
      progress_percent=self._parse_payload_int(
        telemetry_payload.get("progress_percent"),
        telemetry_payload.get("progressPercent"),
        telemetry_payload.get("percent_complete"),
        telemetry_payload.get("completion_percent"),
        telemetry_payload.get("completionPercent"),
        existing.progress_percent,
      ),
      attempt_count=(
        self._parse_payload_int(
          telemetry_payload.get("attempt_count"),
          telemetry_payload.get("attempts"),
          telemetry_payload.get("retry_count"),
          payload.get("attempt_number"),
          existing.attempt_count,
          status_machine.attempt_number,
        )
        or 0
      ),
      current_step=self._first_non_empty_string(
        telemetry_payload.get("current_step"),
        telemetry_payload.get("step"),
        telemetry_payload.get("phase"),
        payload.get("telemetry_step"),
        existing.current_step,
      ),
      last_message=self._first_non_empty_string(
        telemetry_payload.get("last_message"),
        telemetry_payload.get("message"),
        telemetry_payload.get("summary"),
        existing.last_message,
      ),
      last_error=self._first_non_empty_string(
        telemetry_payload.get("last_error"),
        telemetry_payload.get("error"),
        payload.get("telemetry_error"),
        existing.last_error,
      ),
      external_run_id=self._first_non_empty_string(
        telemetry_payload.get("external_run_id"),
        telemetry_payload.get("run_id"),
        telemetry_payload.get("execution_id"),
        telemetry_payload.get("job_id"),
        payload.get("job_id"),
        existing.external_run_id,
      ),
      job_url=self._first_non_empty_string(
        telemetry_payload.get("job_url"),
        telemetry_payload.get("url"),
        payload.get("job_url"),
        existing.job_url,
      ),
      started_at=(
        self._parse_payload_datetime(telemetry_payload.get("started_at"))
        or self._parse_payload_datetime(telemetry_payload.get("created_at"))
        or existing.started_at
      ),
      finished_at=(
        self._parse_payload_datetime(telemetry_payload.get("finished_at"))
        or self._parse_payload_datetime(telemetry_payload.get("completed_at"))
        or existing.finished_at
      ),
      updated_at=(
        self._parse_payload_datetime(telemetry_payload.get("updated_at"))
        or self._parse_payload_datetime(telemetry_payload.get("last_update_at"))
        or existing.updated_at
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_rootly_incident_phase(status: str | None, existing_phase: str) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "open",
      "started",
      "acknowledged",
      "investigating",
      "mitigating",
      "monitoring",
      "resolved",
      "closed",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_rootly_acknowledgment_phase(
    incident_phase: str,
    acknowledged_at: datetime | None,
    existing_phase: str,
  ) -> str:
    if incident_phase in {"resolved", "closed"}:
      return "closed"
    if acknowledged_at is not None or incident_phase == "acknowledged":
      return "acknowledged"
    if incident_phase in {"open", "started", "investigating", "mitigating", "monitoring"}:
      return "pending_acknowledgment"
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_rootly_visibility_phase(private: bool | None, existing_phase: str) -> str:
    if private is True:
      return "private"
    if private is False:
      return "public"
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_rootly_severity_phase(severity_id: str | None, existing_phase: str) -> str:
    normalized = (severity_id or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_rootly_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"open", "started", "investigating", "mitigating", "monitoring"}:
      return "incident_active"
    return "idle"

  def _build_rootly_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    incident_status: str,
    severity_id: str | None,
    private: bool | None,
    acknowledged_at: datetime | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentRootlyRecoveryState,
  ) -> OperatorIncidentRootlyRecoveryPhaseGraph:
    incident_phase = self._first_non_empty_string(
      payload.get("incident_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
    ) or self._normalize_rootly_incident_phase(
      incident_status,
      existing.phase_graph.incident_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
      status_machine.workflow_state,
    ) or self._resolve_rootly_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=incident_status,
    )
    return OperatorIncidentRootlyRecoveryPhaseGraph(
      incident_phase=incident_phase,
      workflow_phase=workflow_phase,
      acknowledgment_phase=self._first_non_empty_string(
        payload.get("acknowledgment_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("acknowledgment_phase"),
      ) or self._resolve_rootly_acknowledgment_phase(
        incident_phase,
        acknowledged_at,
        existing.phase_graph.acknowledgment_phase,
      ),
      visibility_phase=self._first_non_empty_string(
        payload.get("visibility_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("visibility_phase"),
      ) or self._resolve_rootly_visibility_phase(
        private,
        existing.phase_graph.visibility_phase,
      ),
      severity_phase=self._first_non_empty_string(
        payload.get("severity_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("severity_phase"),
      ) or self._resolve_rootly_severity_phase(
        severity_id,
        existing.phase_graph.severity_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_blameless_incident_phase(status: str | None, existing_phase: str) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "open",
      "started",
      "acknowledged",
      "investigating",
      "mitigating",
      "monitoring",
      "resolved",
      "closed",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_blameless_command_phase(commander: str | None, existing_phase: str) -> str:
    if commander:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_blameless_visibility_phase(visibility: str | None, existing_phase: str) -> str:
    normalized = (visibility or "").strip().lower().replace(" ", "_")
    if normalized in {"public", "private", "internal"}:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_blameless_severity_phase(severity: str | None, existing_phase: str) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_blameless_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"open", "started", "investigating", "mitigating", "monitoring"}:
      return "incident_active"
    return "idle"

  def _build_blameless_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    incident_status: str,
    severity: str | None,
    commander: str | None,
    visibility: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentBlamelessRecoveryState,
  ) -> OperatorIncidentBlamelessRecoveryPhaseGraph:
    incident_phase = self._first_non_empty_string(
      payload.get("incident_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
    ) or self._normalize_blameless_incident_phase(
      incident_status,
      existing.phase_graph.incident_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_blameless_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=incident_status,
    )
    return OperatorIncidentBlamelessRecoveryPhaseGraph(
      incident_phase=incident_phase,
      workflow_phase=workflow_phase,
      command_phase=self._first_non_empty_string(
        payload.get("command_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("command_phase"),
      ) or self._resolve_blameless_command_phase(
        commander,
        existing.phase_graph.command_phase,
      ),
      visibility_phase=self._first_non_empty_string(
        payload.get("visibility_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("visibility_phase"),
      ) or self._resolve_blameless_visibility_phase(
        visibility,
        existing.phase_graph.visibility_phase,
      ),
      severity_phase=self._first_non_empty_string(
        payload.get("severity_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("severity_phase"),
      ) or self._resolve_blameless_severity_phase(
        severity,
        existing.phase_graph.severity_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_xmatters_incident_phase(status: str | None, existing_phase: str) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "open",
      "started",
      "acknowledged",
      "investigating",
      "mitigating",
      "monitoring",
      "resolved",
      "closed",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_xmatters_ownership_phase(assignee: str | None, existing_phase: str) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_xmatters_priority_phase(priority: str | None, existing_phase: str) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_xmatters_response_plan_phase(response_plan: str | None, existing_phase: str) -> str:
    if response_plan:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_xmatters_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"open", "started", "investigating", "mitigating", "monitoring"}:
      return "incident_active"
    return "idle"

  def _build_xmatters_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    incident_status: str,
    priority: str | None,
    assignee: str | None,
    response_plan: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentXmattersRecoveryState,
  ) -> OperatorIncidentXmattersRecoveryPhaseGraph:
    incident_phase = self._first_non_empty_string(
      payload.get("incident_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
    ) or self._normalize_xmatters_incident_phase(
      incident_status,
      existing.phase_graph.incident_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_xmatters_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=incident_status,
    )
    return OperatorIncidentXmattersRecoveryPhaseGraph(
      incident_phase=incident_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_xmatters_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_xmatters_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      response_plan_phase=self._first_non_empty_string(
        payload.get("response_plan_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("response_plan_phase"),
      ) or self._resolve_xmatters_response_plan_phase(
        response_plan,
        existing.phase_graph.response_plan_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_servicenow_incident_phase(status: str | None, existing_phase: str) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "new",
      "open",
      "acknowledged",
      "in_progress",
      "on_hold",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_servicenow_assignment_phase(
    assigned_to: str | None,
    assignment_group: str | None,
    existing_phase: str,
  ) -> str:
    if assigned_to:
      return "assigned_to_user"
    if assignment_group:
      return "assigned_to_group"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_servicenow_priority_phase(priority: str | None, existing_phase: str) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_servicenow_group_phase(assignment_group: str | None, existing_phase: str) -> str:
    if assignment_group:
      return "group_configured"
    return existing_phase or "group_unconfigured"

  @staticmethod
  def _resolve_servicenow_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"new", "open", "in_progress", "on_hold"}:
      return "incident_active"
    return "idle"

  def _build_servicenow_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    incident_status: str,
    priority: str | None,
    assigned_to: str | None,
    assignment_group: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentServicenowRecoveryState,
  ) -> OperatorIncidentServicenowRecoveryPhaseGraph:
    incident_phase = self._first_non_empty_string(
      payload.get("incident_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
    ) or self._normalize_servicenow_incident_phase(
      incident_status,
      existing.phase_graph.incident_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_servicenow_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=incident_status,
    )
    return OperatorIncidentServicenowRecoveryPhaseGraph(
      incident_phase=incident_phase,
      workflow_phase=workflow_phase,
      assignment_phase=self._first_non_empty_string(
        payload.get("assignment_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("assignment_phase"),
      ) or self._resolve_servicenow_assignment_phase(
        assigned_to,
        assignment_group,
        existing.phase_graph.assignment_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_servicenow_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      group_phase=self._first_non_empty_string(
        payload.get("group_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("group_phase"),
      ) or self._resolve_servicenow_group_phase(
        assignment_group,
        existing.phase_graph.group_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_squadcast_incident_phase(status: str | None, existing_phase: str) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "investigating",
      "on_hold",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_squadcast_ownership_phase(assignee: str | None, existing_phase: str) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_squadcast_severity_phase(severity: str | None, existing_phase: str) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_squadcast_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_squadcast_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "investigating", "on_hold"}:
      return "incident_active"
    return "idle"

  def _build_squadcast_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    incident_status: str,
    severity: str | None,
    assignee: str | None,
    escalation_policy: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentSquadcastRecoveryState,
  ) -> OperatorIncidentSquadcastRecoveryPhaseGraph:
    incident_phase = self._first_non_empty_string(
      payload.get("incident_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
    ) or self._normalize_squadcast_incident_phase(
      incident_status,
      existing.phase_graph.incident_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_squadcast_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=incident_status,
    )
    return OperatorIncidentSquadcastRecoveryPhaseGraph(
      incident_phase=incident_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_squadcast_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      severity_phase=self._first_non_empty_string(
        payload.get("severity_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("severity_phase"),
      ) or self._resolve_squadcast_severity_phase(
        severity,
        existing.phase_graph.severity_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_squadcast_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_bigpanda_incident_phase(status: str | None, existing_phase: str) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_bigpanda_ownership_phase(assignee: str | None, existing_phase: str) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_bigpanda_severity_phase(severity: str | None, existing_phase: str) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_bigpanda_team_phase(team: str | None, existing_phase: str) -> str:
    if team:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_bigpanda_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  def _build_bigpanda_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    incident_status: str,
    severity: str | None,
    assignee: str | None,
    team: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentBigPandaRecoveryState,
  ) -> OperatorIncidentBigPandaRecoveryPhaseGraph:
    incident_phase = self._first_non_empty_string(
      payload.get("incident_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
    ) or self._normalize_bigpanda_incident_phase(
      incident_status,
      existing.phase_graph.incident_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_bigpanda_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=incident_status,
    )
    return OperatorIncidentBigPandaRecoveryPhaseGraph(
      incident_phase=incident_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_bigpanda_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      severity_phase=self._first_non_empty_string(
        payload.get("severity_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("severity_phase"),
      ) or self._resolve_bigpanda_severity_phase(
        severity,
        existing.phase_graph.severity_phase,
      ),
      team_phase=self._first_non_empty_string(
        payload.get("team_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("team_phase"),
      ) or self._resolve_bigpanda_team_phase(
        team,
        existing.phase_graph.team_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_grafana_oncall_incident_phase(status: str | None, existing_phase: str) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_grafana_oncall_ownership_phase(assignee: str | None, existing_phase: str) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_grafana_oncall_severity_phase(severity: str | None, existing_phase: str) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_grafana_oncall_escalation_phase(
    escalation_chain: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_chain:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_grafana_oncall_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  def _build_grafana_oncall_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    incident_status: str,
    severity: str | None,
    assignee: str | None,
    escalation_chain: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentGrafanaOnCallRecoveryState,
  ) -> OperatorIncidentGrafanaOnCallRecoveryPhaseGraph:
    incident_phase = self._first_non_empty_string(
      payload.get("incident_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
    ) or self._normalize_grafana_oncall_incident_phase(
      incident_status,
      existing.phase_graph.incident_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_grafana_oncall_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=incident_status,
    )
    return OperatorIncidentGrafanaOnCallRecoveryPhaseGraph(
      incident_phase=incident_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_grafana_oncall_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      severity_phase=self._first_non_empty_string(
        payload.get("severity_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("severity_phase"),
      ) or self._resolve_grafana_oncall_severity_phase(
        severity,
        existing.phase_graph.severity_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_grafana_oncall_escalation_phase(
        escalation_chain,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_zenduty_incident_phase(status: str | None, existing_phase: str) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_zenduty_ownership_phase(assignee: str | None, existing_phase: str) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_zenduty_severity_phase(severity: str | None, existing_phase: str) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_zenduty_service_phase(service: str | None, existing_phase: str) -> str:
    if service:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_zenduty_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  def _build_zenduty_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    incident_status: str,
    severity: str | None,
    assignee: str | None,
    service: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentZendutyRecoveryState,
  ) -> OperatorIncidentZendutyRecoveryPhaseGraph:
    incident_phase = self._first_non_empty_string(
      payload.get("incident_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
    ) or self._normalize_zenduty_incident_phase(
      incident_status,
      existing.phase_graph.incident_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_zenduty_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=incident_status,
    )
    return OperatorIncidentZendutyRecoveryPhaseGraph(
      incident_phase=incident_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_zenduty_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      severity_phase=self._first_non_empty_string(
        payload.get("severity_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("severity_phase"),
      ) or self._resolve_zenduty_severity_phase(
        severity,
        existing.phase_graph.severity_phase,
      ),
      service_phase=self._first_non_empty_string(
        payload.get("service_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("service_phase"),
      ) or self._resolve_zenduty_service_phase(
        service,
        existing.phase_graph.service_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_splunk_oncall_incident_phase(status: str | None, existing_phase: str) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_splunk_oncall_ownership_phase(assignee: str | None, existing_phase: str) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_splunk_oncall_severity_phase(severity: str | None, existing_phase: str) -> str:
    normalized = (severity or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_splunk_oncall_routing_phase(routing_key: str | None, existing_phase: str) -> str:
    if routing_key:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_splunk_oncall_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  def _build_splunk_oncall_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    incident_status: str,
    severity: str | None,
    assignee: str | None,
    routing_key: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentSplunkOnCallRecoveryState,
  ) -> OperatorIncidentSplunkOnCallRecoveryPhaseGraph:
    incident_phase = self._first_non_empty_string(
      payload.get("incident_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
    ) or self._normalize_splunk_oncall_incident_phase(
      incident_status,
      existing.phase_graph.incident_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_splunk_oncall_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=incident_status,
    )
    return OperatorIncidentSplunkOnCallRecoveryPhaseGraph(
      incident_phase=incident_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_splunk_oncall_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      severity_phase=self._first_non_empty_string(
        payload.get("severity_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("severity_phase"),
      ) or self._resolve_splunk_oncall_severity_phase(
        severity,
        existing.phase_graph.severity_phase,
      ),
      routing_phase=self._first_non_empty_string(
        payload.get("routing_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("routing_phase"),
      ) or self._resolve_splunk_oncall_routing_phase(
        routing_key,
        existing.phase_graph.routing_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_jira_service_management_incident_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "in_progress",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_jira_service_management_assignment_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_jira_service_management_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_jira_service_management_project_phase(
    service_project: str | None,
    existing_phase: str,
  ) -> str:
    if service_project:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_jira_service_management_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "in_progress", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  def _build_jira_service_management_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    incident_status: str,
    priority: str | None,
    assignee: str | None,
    service_project: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentJiraServiceManagementRecoveryState,
  ) -> OperatorIncidentJiraServiceManagementRecoveryPhaseGraph:
    incident_phase = self._first_non_empty_string(
      payload.get("incident_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
    ) or self._normalize_jira_service_management_incident_phase(
      incident_status,
      existing.phase_graph.incident_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_jira_service_management_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=incident_status,
    )
    return OperatorIncidentJiraServiceManagementRecoveryPhaseGraph(
      incident_phase=incident_phase,
      workflow_phase=workflow_phase,
      assignment_phase=self._first_non_empty_string(
        payload.get("assignment_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("assignment_phase"),
      ) or self._resolve_jira_service_management_assignment_phase(
        assignee,
        existing.phase_graph.assignment_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_jira_service_management_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      project_phase=self._first_non_empty_string(
        payload.get("project_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("project_phase"),
      ) or self._resolve_jira_service_management_project_phase(
        service_project,
        existing.phase_graph.project_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_pagertree_incident_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "in_progress",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_pagertree_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_pagertree_urgency_phase(
    urgency: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (urgency or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_pagertree_team_phase(
    team: str | None,
    existing_phase: str,
  ) -> str:
    if team:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_pagertree_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "in_progress", "investigating", "monitoring"}:
      return "incident_active"
    return "idle"

  def _build_pagertree_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    incident_status: str,
    urgency: str | None,
    assignee: str | None,
    team: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentPagerTreeRecoveryState,
  ) -> OperatorIncidentPagerTreeRecoveryPhaseGraph:
    incident_phase = self._first_non_empty_string(
      payload.get("incident_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
    ) or self._normalize_pagertree_incident_phase(
      incident_status,
      existing.phase_graph.incident_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_pagertree_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=incident_status,
    )
    return OperatorIncidentPagerTreeRecoveryPhaseGraph(
      incident_phase=incident_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_pagertree_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      urgency_phase=self._first_non_empty_string(
        payload.get("urgency_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("urgency_phase"),
      ) or self._resolve_pagertree_urgency_phase(
        urgency,
        existing.phase_graph.urgency_phase,
      ),
      team_phase=self._first_non_empty_string(
        payload.get("team_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("team_phase"),
      ) or self._resolve_pagertree_team_phase(
        team,
        existing.phase_graph.team_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_alertops_incident_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "in_progress",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_alertops_ownership_phase(
    owner: str | None,
    existing_phase: str,
  ) -> str:
    if owner:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_alertops_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_alertops_service_phase(
    service: str | None,
    existing_phase: str,
  ) -> str:
    if service:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_alertops_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "incident_acknowledged"
    if workflow_state in {"triggered", "open", "in_progress", "investigating", "monitoring", "escalated"}:
      return "incident_active"
    return "idle"

  def _build_alertops_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    incident_status: str,
    priority: str | None,
    owner: str | None,
    service: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentAlertOpsRecoveryState,
  ) -> OperatorIncidentAlertOpsRecoveryPhaseGraph:
    incident_phase = self._first_non_empty_string(
      payload.get("incident_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("incident_phase"),
    ) or self._normalize_alertops_incident_phase(
      incident_status,
      existing.phase_graph.incident_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_alertops_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=incident_status,
    )
    return OperatorIncidentAlertOpsRecoveryPhaseGraph(
      incident_phase=incident_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_alertops_ownership_phase(
        owner,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_alertops_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      service_phase=self._first_non_empty_string(
        payload.get("service_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("service_phase"),
      ) or self._resolve_alertops_service_phase(
        service,
        existing.phase_graph.service_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_signl4_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "acknowledged",
      "in_progress",
      "investigating",
      "monitoring",
      "resolved",
      "closed",
      "canceled",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_signl4_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_signl4_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_signl4_team_phase(
    team: str | None,
    existing_phase: str,
  ) -> str:
    if team:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_signl4_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state == "acknowledged":
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "in_progress", "investigating", "monitoring", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_signl4_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    team: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentSignl4RecoveryState,
  ) -> OperatorIncidentSignl4RecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_signl4_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_signl4_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentSignl4RecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_signl4_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_signl4_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      team_phase=self._first_non_empty_string(
        payload.get("team_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("team_phase"),
      ) or self._resolve_signl4_team_phase(
        team,
        existing.phase_graph.team_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_ilert_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_ilert_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_ilert_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_ilert_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_ilert_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_ilert_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentIlertRecoveryState,
  ) -> OperatorIncidentIlertRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_ilert_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_ilert_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentIlertRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_ilert_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_ilert_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_ilert_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_betterstack_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_betterstack_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_betterstack_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_betterstack_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_betterstack_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_betterstack_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentBetterstackRecoveryState,
  ) -> OperatorIncidentBetterstackRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_betterstack_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_betterstack_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentBetterstackRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_betterstack_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_betterstack_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_betterstack_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_onpage_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_onpage_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_onpage_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_onpage_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_onpage_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_onpage_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentOnpageRecoveryState,
  ) -> OperatorIncidentOnpageRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_onpage_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_onpage_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentOnpageRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_onpage_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_onpage_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_onpage_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_allquiet_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_allquiet_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_allquiet_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_allquiet_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_allquiet_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_allquiet_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentAllquietRecoveryState,
  ) -> OperatorIncidentAllquietRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_allquiet_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_allquiet_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentAllquietRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_allquiet_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_allquiet_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_allquiet_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_moogsoft_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_moogsoft_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_moogsoft_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_moogsoft_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_moogsoft_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_moogsoft_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentMoogsoftRecoveryState,
  ) -> OperatorIncidentMoogsoftRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_moogsoft_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_moogsoft_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentMoogsoftRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_moogsoft_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_moogsoft_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_moogsoft_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_spikesh_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_spikesh_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_spikesh_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_spikesh_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_spikesh_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_spikesh_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentSpikeshRecoveryState,
  ) -> OperatorIncidentSpikeshRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_spikesh_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_spikesh_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentSpikeshRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_spikesh_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_spikesh_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_spikesh_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_dutycalls_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_dutycalls_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_dutycalls_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_dutycalls_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_dutycalls_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_dutycalls_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentDutyCallsRecoveryState,
  ) -> OperatorIncidentDutyCallsRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_dutycalls_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_dutycalls_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentDutyCallsRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_dutycalls_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_dutycalls_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_dutycalls_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_incidenthub_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_incidenthub_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_incidenthub_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_incidenthub_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_incidenthub_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_incidenthub_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentIncidentHubRecoveryState,
  ) -> OperatorIncidentIncidentHubRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_incidenthub_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_incidenthub_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentIncidentHubRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_incidenthub_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_incidenthub_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_incidenthub_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_resolver_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_resolver_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_resolver_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_resolver_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_resolver_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_resolver_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentResolverRecoveryState,
  ) -> OperatorIncidentResolverRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_resolver_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_resolver_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentResolverRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_resolver_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_resolver_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_resolver_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_openduty_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_openduty_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_openduty_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_openduty_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_openduty_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_openduty_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentOpenDutyRecoveryState,
  ) -> OperatorIncidentOpenDutyRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_openduty_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_openduty_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentOpenDutyRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_openduty_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_openduty_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_openduty_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_cabot_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_cabot_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_cabot_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_cabot_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_cabot_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_cabot_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentCabotRecoveryState,
  ) -> OperatorIncidentCabotRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_cabot_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_cabot_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentCabotRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_cabot_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_cabot_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_cabot_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_haloitsm_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_haloitsm_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_haloitsm_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_haloitsm_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_haloitsm_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_haloitsm_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentHaloItsmRecoveryState,
  ) -> OperatorIncidentHaloItsmRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_haloitsm_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_haloitsm_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentHaloItsmRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_haloitsm_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_haloitsm_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_haloitsm_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_incidentmanagerio_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_incidentmanagerio_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_incidentmanagerio_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_incidentmanagerio_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_incidentmanagerio_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_incidentmanagerio_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentIncidentManagerIoRecoveryState,
  ) -> OperatorIncidentIncidentManagerIoRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_incidentmanagerio_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_incidentmanagerio_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentIncidentManagerIoRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_incidentmanagerio_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_incidentmanagerio_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_incidentmanagerio_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_oneuptime_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_oneuptime_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_oneuptime_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_oneuptime_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_oneuptime_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_oneuptime_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentOneUptimeRecoveryState,
  ) -> OperatorIncidentOneUptimeRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_oneuptime_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_oneuptime_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentOneUptimeRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_oneuptime_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_oneuptime_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_oneuptime_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_squzy_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_squzy_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_squzy_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_squzy_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_squzy_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_squzy_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentSquzyRecoveryState,
  ) -> OperatorIncidentSquzyRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_squzy_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_squzy_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentSquzyRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_squzy_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_squzy_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_squzy_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_crisescontrol_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_crisescontrol_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_crisescontrol_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_crisescontrol_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_crisescontrol_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_crisescontrol_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentCrisesControlRecoveryState,
  ) -> OperatorIncidentCrisesControlRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_crisescontrol_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_crisescontrol_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentCrisesControlRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_crisescontrol_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_crisescontrol_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_crisescontrol_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_freshservice_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_freshservice_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_freshservice_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_freshservice_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_freshservice_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_freshservice_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentFreshserviceRecoveryState,
  ) -> OperatorIncidentFreshserviceRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_freshservice_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_freshservice_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentFreshserviceRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_freshservice_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_freshservice_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_freshservice_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_freshdesk_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_freshdesk_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_freshdesk_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_freshdesk_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_freshdesk_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_freshdesk_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentFreshdeskRecoveryState,
  ) -> OperatorIncidentFreshdeskRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_freshdesk_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_freshdesk_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentFreshdeskRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_freshdesk_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_freshdesk_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_freshdesk_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_happyfox_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._normalize_freshdesk_alert_phase(status, existing_phase)

  @staticmethod
  def _resolve_happyfox_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_ownership_phase(assignee, existing_phase)

  @staticmethod
  def _resolve_happyfox_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_priority_phase(priority, existing_phase)

  @staticmethod
  def _resolve_happyfox_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_escalation_phase(
      escalation_policy,
      existing_phase,
    )

  @staticmethod
  def _resolve_happyfox_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=workflow_state,
    )

  def _build_happyfox_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentHappyfoxRecoveryState,
  ) -> OperatorIncidentHappyfoxRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_happyfox_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_happyfox_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentHappyfoxRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_happyfox_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_happyfox_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_happyfox_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_zendesk_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._normalize_freshdesk_alert_phase(status, existing_phase)

  @staticmethod
  def _resolve_zendesk_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_ownership_phase(assignee, existing_phase)

  @staticmethod
  def _resolve_zendesk_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_priority_phase(priority, existing_phase)

  @staticmethod
  def _resolve_zendesk_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_escalation_phase(
      escalation_policy,
      existing_phase,
    )

  @staticmethod
  def _resolve_zendesk_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=workflow_state,
    )

  def _build_zendesk_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentZendeskRecoveryState,
  ) -> OperatorIncidentZendeskRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_zendesk_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_zendesk_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentZendeskRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_zendesk_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_zendesk_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_zendesk_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_zohodesk_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._normalize_freshdesk_alert_phase(status, existing_phase)

  @staticmethod
  def _resolve_zohodesk_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_ownership_phase(assignee, existing_phase)

  @staticmethod
  def _resolve_zohodesk_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_priority_phase(priority, existing_phase)

  @staticmethod
  def _resolve_zohodesk_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_escalation_phase(
      escalation_policy,
      existing_phase,
    )

  @staticmethod
  def _resolve_zohodesk_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=workflow_state,
    )

  def _build_zohodesk_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentZohoDeskRecoveryState,
  ) -> OperatorIncidentZohoDeskRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_zohodesk_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_zohodesk_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentZohoDeskRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_zohodesk_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_zohodesk_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_zohodesk_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_helpscout_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._normalize_freshdesk_alert_phase(status, existing_phase)

  @staticmethod
  def _resolve_helpscout_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_ownership_phase(assignee, existing_phase)

  @staticmethod
  def _resolve_helpscout_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_priority_phase(priority, existing_phase)

  @staticmethod
  def _resolve_helpscout_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_escalation_phase(
      escalation_policy,
      existing_phase,
    )

  @staticmethod
  def _resolve_helpscout_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=workflow_state,
    )

  def _build_helpscout_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentHelpScoutRecoveryState,
  ) -> OperatorIncidentHelpScoutRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_helpscout_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_helpscout_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentHelpScoutRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_helpscout_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_helpscout_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_helpscout_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_kayako_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._normalize_freshdesk_alert_phase(status, existing_phase)

  @staticmethod
  def _resolve_kayako_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_ownership_phase(assignee, existing_phase)

  @staticmethod
  def _resolve_kayako_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_priority_phase(priority, existing_phase)

  @staticmethod
  def _resolve_kayako_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_escalation_phase(
      escalation_policy,
      existing_phase,
    )

  @staticmethod
  def _resolve_kayako_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=workflow_state,
    )

  def _build_kayako_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentKayakoRecoveryState,
  ) -> OperatorIncidentKayakoRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_kayako_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_kayako_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentKayakoRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_kayako_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_kayako_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_kayako_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_intercom_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._normalize_freshdesk_alert_phase(status, existing_phase)

  @staticmethod
  def _resolve_intercom_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_ownership_phase(assignee, existing_phase)

  @staticmethod
  def _resolve_intercom_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_priority_phase(priority, existing_phase)

  @staticmethod
  def _resolve_intercom_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_escalation_phase(
      escalation_policy,
      existing_phase,
    )

  @staticmethod
  def _resolve_intercom_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=workflow_state,
    )

  def _build_intercom_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentIntercomRecoveryState,
  ) -> OperatorIncidentIntercomRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_intercom_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_intercom_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentIntercomRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_intercom_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_intercom_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_intercom_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_front_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._normalize_freshdesk_alert_phase(status, existing_phase)

  @staticmethod
  def _resolve_front_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_ownership_phase(assignee, existing_phase)

  @staticmethod
  def _resolve_front_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_priority_phase(priority, existing_phase)

  @staticmethod
  def _resolve_front_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_escalation_phase(
      escalation_policy,
      existing_phase,
    )

  @staticmethod
  def _resolve_front_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    return TradingApplication._resolve_freshdesk_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=workflow_state,
    )

  def _build_front_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentFrontRecoveryState,
  ) -> OperatorIncidentFrontRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_front_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_front_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentFrontRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_front_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_front_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_front_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_servicedeskplus_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_servicedeskplus_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_servicedeskplus_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_servicedeskplus_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_servicedeskplus_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_servicedeskplus_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentServiceDeskPlusRecoveryState,
  ) -> OperatorIncidentServiceDeskPlusRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_servicedeskplus_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_servicedeskplus_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentServiceDeskPlusRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_servicedeskplus_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_servicedeskplus_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_servicedeskplus_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_sysaid_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_sysaid_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_sysaid_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_sysaid_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_sysaid_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_sysaid_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentSysAidRecoveryState,
  ) -> OperatorIncidentSysAidRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_sysaid_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_sysaid_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentSysAidRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_sysaid_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_sysaid_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_sysaid_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_bmchelix_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_bmchelix_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_bmchelix_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_bmchelix_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_bmchelix_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_bmchelix_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentBmcHelixRecoveryState,
  ) -> OperatorIncidentBmcHelixRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_bmchelix_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_bmchelix_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentBmcHelixRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_bmchelix_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_bmchelix_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_bmchelix_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_solarwindsservicedesk_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_solarwindsservicedesk_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_solarwindsservicedesk_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_solarwindsservicedesk_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_solarwindsservicedesk_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_solarwindsservicedesk_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentSolarWindsServiceDeskRecoveryState,
  ) -> OperatorIncidentSolarWindsServiceDeskRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_solarwindsservicedesk_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_solarwindsservicedesk_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentSolarWindsServiceDeskRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_solarwindsservicedesk_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_solarwindsservicedesk_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_solarwindsservicedesk_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_topdesk_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_topdesk_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_topdesk_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_topdesk_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_topdesk_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_topdesk_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentTopdeskRecoveryState,
  ) -> OperatorIncidentTopdeskRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_topdesk_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_topdesk_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentTopdeskRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_topdesk_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_topdesk_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_topdesk_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_invgateservicedesk_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_invgateservicedesk_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_invgateservicedesk_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_invgateservicedesk_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_invgateservicedesk_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_invgateservicedesk_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentInvGateServiceDeskRecoveryState,
  ) -> OperatorIncidentInvGateServiceDeskRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_invgateservicedesk_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_invgateservicedesk_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentInvGateServiceDeskRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_invgateservicedesk_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_invgateservicedesk_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_invgateservicedesk_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  @staticmethod
  def _normalize_opsramp_alert_phase(
    status: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (status or "").strip().lower().replace(" ", "_")
    if normalized in {
      "triggered",
      "open",
      "pending",
      "accepted",
      "acknowledged",
      "in_progress",
      "resolved",
      "closed",
      "escalated",
    }:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_opsramp_ownership_phase(
    assignee: str | None,
    existing_phase: str,
  ) -> str:
    if assignee:
      return "assigned"
    return existing_phase or "unassigned"

  @staticmethod
  def _resolve_opsramp_priority_phase(
    priority: str | None,
    existing_phase: str,
  ) -> str:
    normalized = (priority or "").strip().lower().replace(" ", "_")
    if normalized:
      return normalized
    return existing_phase or "unknown"

  @staticmethod
  def _resolve_opsramp_escalation_phase(
    escalation_policy: str | None,
    existing_phase: str,
  ) -> str:
    if escalation_policy:
      return "configured"
    return existing_phase or "unconfigured"

  @staticmethod
  def _resolve_opsramp_workflow_phase(
    *,
    lifecycle_state: str | None,
    workflow_state: str,
  ) -> str:
    normalized_lifecycle = (lifecycle_state or "").strip().lower().replace(" ", "_")
    if workflow_state in {"resolved", "closed", "canceled"}:
      return "resolved_back_synced"
    if normalized_lifecycle == "verified":
      return "verified_pending_resolve"
    if normalized_lifecycle == "recovered":
      return "awaiting_local_verification"
    if normalized_lifecycle == "recovering":
      return "provider_recovering"
    if normalized_lifecycle == "requested":
      return "remediation_requested"
    if normalized_lifecycle == "failed":
      return "recovery_failed"
    if workflow_state in {"accepted", "acknowledged"}:
      return "alert_acknowledged"
    if workflow_state in {"triggered", "open", "pending", "in_progress", "escalated"}:
      return "alert_active"
    return "idle"

  def _build_opsramp_recovery_phase_graph(
    self,
    *,
    payload: dict[str, Any],
    alert_status: str,
    priority: str | None,
    escalation_policy: str | None,
    assignee: str | None,
    lifecycle_state: str | None,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    existing: OperatorIncidentOpsRampRecoveryState,
  ) -> OperatorIncidentOpsRampRecoveryPhaseGraph:
    alert_phase = self._first_non_empty_string(
      payload.get("alert_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("alert_phase"),
    ) or self._normalize_opsramp_alert_phase(
      alert_status,
      existing.phase_graph.alert_phase,
    )
    workflow_phase = self._first_non_empty_string(
      payload.get("workflow_phase"),
      self._extract_payload_mapping(payload.get("phase_graph")).get("workflow_phase"),
    ) or self._resolve_opsramp_workflow_phase(
      lifecycle_state=lifecycle_state,
      workflow_state=alert_status,
    )
    return OperatorIncidentOpsRampRecoveryPhaseGraph(
      alert_phase=alert_phase,
      workflow_phase=workflow_phase,
      ownership_phase=self._first_non_empty_string(
        payload.get("ownership_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("ownership_phase"),
      ) or self._resolve_opsramp_ownership_phase(
        assignee,
        existing.phase_graph.ownership_phase,
      ),
      priority_phase=self._first_non_empty_string(
        payload.get("priority_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("priority_phase"),
      ) or self._resolve_opsramp_priority_phase(
        priority,
        existing.phase_graph.priority_phase,
      ),
      escalation_phase=self._first_non_empty_string(
        payload.get("escalation_phase"),
        self._extract_payload_mapping(payload.get("phase_graph")).get("escalation_phase"),
      ) or self._resolve_opsramp_escalation_phase(
        escalation_policy,
        existing.phase_graph.escalation_phase,
      ),
      last_transition_at=(
        self._parse_payload_datetime(payload.get("updated_at"))
        or self._parse_payload_datetime(
          self._extract_payload_mapping(payload.get("phase_graph")).get("last_transition_at")
        )
        or synced_at
      ),
    )

  def _build_provider_recovery_provider_schema(
    self,
    *,
    provider: str,
    payload: dict[str, Any],
    lifecycle_state: str,
    status_machine: OperatorIncidentProviderRecoveryStatusMachine,
    synced_at: datetime,
    workflow_state: str | None,
    workflow_reference: str | None,
    reference: str | None,
    existing: OperatorIncidentProviderRecoveryState,
  ) -> tuple[
    str | None,
    OperatorIncidentPagerDutyRecoveryState,
    OperatorIncidentOpsgenieRecoveryState,
    OperatorIncidentIncidentIoRecoveryState,
    OperatorIncidentFireHydrantRecoveryState,
    OperatorIncidentRootlyRecoveryState,
    OperatorIncidentBlamelessRecoveryState,
    OperatorIncidentXmattersRecoveryState,
    OperatorIncidentServicenowRecoveryState,
    OperatorIncidentSquadcastRecoveryState,
    OperatorIncidentBigPandaRecoveryState,
    OperatorIncidentGrafanaOnCallRecoveryState,
    OperatorIncidentZendutyRecoveryState,
    OperatorIncidentSplunkOnCallRecoveryState,
    OperatorIncidentJiraServiceManagementRecoveryState,
    OperatorIncidentPagerTreeRecoveryState,
    OperatorIncidentAlertOpsRecoveryState,
    OperatorIncidentSignl4RecoveryState,
    OperatorIncidentIlertRecoveryState,
  ]:
    normalized_provider = self._normalize_paging_provider(provider)
    schema_payload = self._extract_payload_mapping(payload.get("provider_schema"))

    pagerduty_payload = self._merge_payload_mappings(
      schema_payload.get("pagerduty"),
      payload.get("pagerduty"),
      payload.get("pagerduty_incident"),
    )
    pagerduty_status = self._first_non_empty_string(
      pagerduty_payload.get("incident_status"),
      pagerduty_payload.get("status"),
      workflow_state,
      payload.get("workflow_state"),
      existing.pagerduty.incident_status,
    ) or "unknown"
    pagerduty = OperatorIncidentPagerDutyRecoveryState(
      incident_id=self._first_non_empty_string(
        pagerduty_payload.get("incident_id"),
        pagerduty_payload.get("id"),
        workflow_reference,
        existing.pagerduty.incident_id,
      ),
      incident_key=self._first_non_empty_string(
        pagerduty_payload.get("incident_key"),
        pagerduty_payload.get("dedup_key"),
        reference,
        existing.pagerduty.incident_key,
      ),
      incident_status=pagerduty_status,
      urgency=self._first_non_empty_string(
        pagerduty_payload.get("urgency"),
        existing.pagerduty.urgency,
      ),
      service_id=self._first_non_empty_string(
        pagerduty_payload.get("service_id"),
        existing.pagerduty.service_id,
      ),
      service_summary=self._first_non_empty_string(
        pagerduty_payload.get("service_summary"),
        pagerduty_payload.get("service_name"),
        existing.pagerduty.service_summary,
      ),
      escalation_policy_id=self._first_non_empty_string(
        pagerduty_payload.get("escalation_policy_id"),
        existing.pagerduty.escalation_policy_id,
      ),
      escalation_policy_summary=self._first_non_empty_string(
        pagerduty_payload.get("escalation_policy_summary"),
        pagerduty_payload.get("escalation_policy_name"),
        existing.pagerduty.escalation_policy_summary,
      ),
      html_url=self._first_non_empty_string(
        pagerduty_payload.get("html_url"),
        existing.pagerduty.html_url,
      ),
      last_status_change_at=(
        self._parse_payload_datetime(pagerduty_payload.get("last_status_change_at"))
        or existing.pagerduty.last_status_change_at
      ),
      phase_graph=self._build_pagerduty_recovery_phase_graph(
        payload=pagerduty_payload,
        incident_status=pagerduty_status,
        urgency=self._first_non_empty_string(
          pagerduty_payload.get("urgency"),
          existing.pagerduty.urgency,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.pagerduty,
      ),
    )

    opsgenie_payload = self._merge_payload_mappings(
      schema_payload.get("opsgenie"),
      payload.get("opsgenie"),
      payload.get("opsgenie_alert"),
    )
    opsgenie_status = self._first_non_empty_string(
      opsgenie_payload.get("alert_status"),
      opsgenie_payload.get("status"),
      workflow_state,
      payload.get("workflow_state"),
      existing.opsgenie.alert_status,
    ) or "unknown"
    opsgenie = OperatorIncidentOpsgenieRecoveryState(
      alert_id=self._first_non_empty_string(
        opsgenie_payload.get("alert_id"),
        opsgenie_payload.get("id"),
        workflow_reference,
        existing.opsgenie.alert_id,
      ),
      alias=self._first_non_empty_string(
        opsgenie_payload.get("alias"),
        reference,
        existing.opsgenie.alias,
      ),
      alert_status=opsgenie_status,
      priority=self._first_non_empty_string(
        opsgenie_payload.get("priority"),
        existing.opsgenie.priority,
      ),
      owner=self._first_non_empty_string(
        opsgenie_payload.get("owner"),
        existing.opsgenie.owner,
      ),
      acknowledged=(
        opsgenie_payload.get("acknowledged")
        if isinstance(opsgenie_payload.get("acknowledged"), bool)
        else existing.opsgenie.acknowledged
      ),
      seen=(
        opsgenie_payload.get("seen")
        if isinstance(opsgenie_payload.get("seen"), bool)
        else existing.opsgenie.seen
      ),
      tiny_id=self._first_non_empty_string(
        opsgenie_payload.get("tiny_id"),
        opsgenie_payload.get("tinyId"),
        existing.opsgenie.tiny_id,
      ),
      teams=self._extract_string_tuple(
        opsgenie_payload.get("teams"),
        opsgenie_payload.get("team"),
        existing.opsgenie.teams,
      ),
      updated_at=(
        self._parse_payload_datetime(opsgenie_payload.get("updated_at"))
        or self._parse_payload_datetime(opsgenie_payload.get("updatedAt"))
        or existing.opsgenie.updated_at
      ),
      phase_graph=self._build_opsgenie_recovery_phase_graph(
        payload=opsgenie_payload,
        alert_status=opsgenie_status,
        owner=self._first_non_empty_string(
          opsgenie_payload.get("owner"),
          existing.opsgenie.owner,
        ),
        acknowledged=(
          opsgenie_payload.get("acknowledged")
          if isinstance(opsgenie_payload.get("acknowledged"), bool)
          else existing.opsgenie.acknowledged
        ),
        seen=(
          opsgenie_payload.get("seen")
          if isinstance(opsgenie_payload.get("seen"), bool)
          else existing.opsgenie.seen
        ),
        teams=self._extract_string_tuple(
          opsgenie_payload.get("teams"),
          opsgenie_payload.get("team"),
          existing.opsgenie.teams,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.opsgenie,
      ),
    )

    incidentio_payload = self._merge_payload_mappings(
      schema_payload.get("incidentio"),
      schema_payload.get("incident_io"),
      payload.get("incidentio"),
      payload.get("incidentio_incident"),
      payload.get("incident_io"),
    )
    incidentio_status = self._first_non_empty_string(
      incidentio_payload.get("incident_status"),
      incidentio_payload.get("status"),
      workflow_state,
      payload.get("workflow_state"),
      existing.incidentio.incident_status,
    ) or "unknown"
    incidentio = OperatorIncidentIncidentIoRecoveryState(
      incident_id=self._first_non_empty_string(
        incidentio_payload.get("incident_id"),
        incidentio_payload.get("id"),
        workflow_reference,
        existing.incidentio.incident_id,
      ),
      external_reference=self._first_non_empty_string(
        incidentio_payload.get("external_reference"),
        incidentio_payload.get("reference"),
        reference,
        existing.incidentio.external_reference,
      ),
      incident_status=incidentio_status,
      severity=self._first_non_empty_string(
        incidentio_payload.get("severity"),
        existing.incidentio.severity,
      ),
      mode=self._first_non_empty_string(
        incidentio_payload.get("mode"),
        existing.incidentio.mode,
      ),
      visibility=self._first_non_empty_string(
        incidentio_payload.get("visibility"),
        existing.incidentio.visibility,
      ),
      assignee=self._first_non_empty_string(
        incidentio_payload.get("assignee"),
        incidentio_payload.get("owner"),
        existing.incidentio.assignee,
      ),
      url=self._first_non_empty_string(
        incidentio_payload.get("url"),
        incidentio_payload.get("html_url"),
        existing.incidentio.url,
      ),
      updated_at=(
        self._parse_payload_datetime(incidentio_payload.get("updated_at"))
        or existing.incidentio.updated_at
      ),
      phase_graph=self._build_incidentio_recovery_phase_graph(
        payload=incidentio_payload,
        incident_status=incidentio_status,
        severity=self._first_non_empty_string(
          incidentio_payload.get("severity"),
          existing.incidentio.severity,
        ),
        mode=self._first_non_empty_string(
          incidentio_payload.get("mode"),
          existing.incidentio.mode,
        ),
        visibility=self._first_non_empty_string(
          incidentio_payload.get("visibility"),
          existing.incidentio.visibility,
        ),
        assignee=self._first_non_empty_string(
          incidentio_payload.get("assignee"),
          incidentio_payload.get("owner"),
          existing.incidentio.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.incidentio,
      ),
    )

    firehydrant_payload = self._merge_payload_mappings(
      schema_payload.get("firehydrant"),
      schema_payload.get("fire_hydrant"),
      payload.get("firehydrant"),
      payload.get("firehydrant_incident"),
      payload.get("fire_hydrant"),
    )
    firehydrant_status = self._first_non_empty_string(
      firehydrant_payload.get("incident_status"),
      firehydrant_payload.get("status"),
      workflow_state,
      payload.get("workflow_state"),
      existing.firehydrant.incident_status,
    ) or "unknown"
    firehydrant = OperatorIncidentFireHydrantRecoveryState(
      incident_id=self._first_non_empty_string(
        firehydrant_payload.get("incident_id"),
        firehydrant_payload.get("id"),
        workflow_reference,
        existing.firehydrant.incident_id,
      ),
      external_reference=self._first_non_empty_string(
        firehydrant_payload.get("external_reference"),
        firehydrant_payload.get("reference"),
        reference,
        existing.firehydrant.external_reference,
      ),
      incident_status=firehydrant_status,
      severity=self._first_non_empty_string(
        firehydrant_payload.get("severity"),
        existing.firehydrant.severity,
      ),
      priority=self._first_non_empty_string(
        firehydrant_payload.get("priority"),
        existing.firehydrant.priority,
      ),
      team=self._first_non_empty_string(
        firehydrant_payload.get("team"),
        firehydrant_payload.get("owner"),
        existing.firehydrant.team,
      ),
      runbook=self._first_non_empty_string(
        firehydrant_payload.get("runbook"),
        firehydrant_payload.get("runbook_name"),
        existing.firehydrant.runbook,
      ),
      url=self._first_non_empty_string(
        firehydrant_payload.get("url"),
        firehydrant_payload.get("html_url"),
        existing.firehydrant.url,
      ),
      updated_at=(
        self._parse_payload_datetime(firehydrant_payload.get("updated_at"))
        or existing.firehydrant.updated_at
      ),
      phase_graph=self._build_firehydrant_recovery_phase_graph(
        payload=firehydrant_payload,
        incident_status=firehydrant_status,
        severity=self._first_non_empty_string(
          firehydrant_payload.get("severity"),
          existing.firehydrant.severity,
        ),
        priority=self._first_non_empty_string(
          firehydrant_payload.get("priority"),
          existing.firehydrant.priority,
        ),
        team=self._first_non_empty_string(
          firehydrant_payload.get("team"),
          firehydrant_payload.get("owner"),
          existing.firehydrant.team,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.firehydrant,
      ),
    )

    rootly_payload = self._merge_payload_mappings(
      schema_payload.get("rootly"),
      schema_payload.get("root_ly"),
      payload.get("rootly"),
      payload.get("rootly_incident"),
      payload.get("root_ly"),
    )
    rootly_status = self._first_non_empty_string(
      rootly_payload.get("incident_status"),
      rootly_payload.get("status"),
      workflow_state,
      payload.get("workflow_state"),
      existing.rootly.incident_status,
    ) or "unknown"
    rootly_private = (
      rootly_payload.get("private")
      if isinstance(rootly_payload.get("private"), bool)
      else existing.rootly.private
    )
    rootly_acknowledged_at = (
      self._parse_payload_datetime(rootly_payload.get("acknowledged_at"))
      or existing.rootly.acknowledged_at
    )
    rootly = OperatorIncidentRootlyRecoveryState(
      incident_id=self._first_non_empty_string(
        rootly_payload.get("incident_id"),
        rootly_payload.get("id"),
        workflow_reference,
        existing.rootly.incident_id,
      ),
      external_reference=self._first_non_empty_string(
        rootly_payload.get("external_reference"),
        rootly_payload.get("reference"),
        reference,
        existing.rootly.external_reference,
      ),
      incident_status=rootly_status,
      severity_id=self._first_non_empty_string(
        rootly_payload.get("severity_id"),
        existing.rootly.severity_id,
      ),
      private=rootly_private,
      slug=self._first_non_empty_string(
        rootly_payload.get("slug"),
        rootly_payload.get("short_id"),
        existing.rootly.slug,
      ),
      url=self._first_non_empty_string(
        rootly_payload.get("url"),
        rootly_payload.get("html_url"),
        existing.rootly.url,
      ),
      acknowledged_at=rootly_acknowledged_at,
      updated_at=(
        self._parse_payload_datetime(rootly_payload.get("updated_at"))
        or existing.rootly.updated_at
      ),
      phase_graph=self._build_rootly_recovery_phase_graph(
        payload=rootly_payload,
        incident_status=rootly_status,
        severity_id=self._first_non_empty_string(
          rootly_payload.get("severity_id"),
          existing.rootly.severity_id,
        ),
        private=rootly_private,
        acknowledged_at=rootly_acknowledged_at,
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.rootly,
      ),
    )

    blameless_payload = self._merge_payload_mappings(
      schema_payload.get("blameless"),
      schema_payload.get("blame_less"),
      payload.get("blameless"),
      payload.get("blameless_incident"),
      payload.get("blame_less"),
    )
    blameless_status = self._first_non_empty_string(
      blameless_payload.get("incident_status"),
      blameless_payload.get("status"),
      workflow_state,
      payload.get("workflow_state"),
      existing.blameless.incident_status,
    ) or "unknown"
    blameless = OperatorIncidentBlamelessRecoveryState(
      incident_id=self._first_non_empty_string(
        blameless_payload.get("incident_id"),
        blameless_payload.get("id"),
        workflow_reference,
        existing.blameless.incident_id,
      ),
      external_reference=self._first_non_empty_string(
        blameless_payload.get("external_reference"),
        blameless_payload.get("reference"),
        reference,
        existing.blameless.external_reference,
      ),
      incident_status=blameless_status,
      severity=self._first_non_empty_string(
        blameless_payload.get("severity"),
        existing.blameless.severity,
      ),
      commander=self._first_non_empty_string(
        blameless_payload.get("commander"),
        blameless_payload.get("owner"),
        existing.blameless.commander,
      ),
      visibility=self._first_non_empty_string(
        blameless_payload.get("visibility"),
        blameless_payload.get("visibility_mode"),
        existing.blameless.visibility,
      ),
      url=self._first_non_empty_string(
        blameless_payload.get("url"),
        blameless_payload.get("html_url"),
        existing.blameless.url,
      ),
      updated_at=(
        self._parse_payload_datetime(blameless_payload.get("updated_at"))
        or existing.blameless.updated_at
      ),
      phase_graph=self._build_blameless_recovery_phase_graph(
        payload=blameless_payload,
        incident_status=blameless_status,
        severity=self._first_non_empty_string(
          blameless_payload.get("severity"),
          existing.blameless.severity,
        ),
        commander=self._first_non_empty_string(
          blameless_payload.get("commander"),
          blameless_payload.get("owner"),
          existing.blameless.commander,
        ),
        visibility=self._first_non_empty_string(
          blameless_payload.get("visibility"),
          blameless_payload.get("visibility_mode"),
          existing.blameless.visibility,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.blameless,
      ),
    )

    xmatters_payload = self._merge_payload_mappings(
      schema_payload.get("xmatters"),
      schema_payload.get("x_matters"),
      payload.get("xmatters"),
      payload.get("xmatters_incident"),
      payload.get("x_matters"),
    )
    xmatters_status = self._first_non_empty_string(
      xmatters_payload.get("incident_status"),
      xmatters_payload.get("status"),
      workflow_state,
      payload.get("workflow_state"),
      existing.xmatters.incident_status,
    ) or "unknown"
    xmatters = OperatorIncidentXmattersRecoveryState(
      incident_id=self._first_non_empty_string(
        xmatters_payload.get("incident_id"),
        xmatters_payload.get("id"),
        workflow_reference,
        existing.xmatters.incident_id,
      ),
      external_reference=self._first_non_empty_string(
        xmatters_payload.get("external_reference"),
        xmatters_payload.get("reference"),
        reference,
        existing.xmatters.external_reference,
      ),
      incident_status=xmatters_status,
      priority=self._first_non_empty_string(
        xmatters_payload.get("priority"),
        existing.xmatters.priority,
      ),
      assignee=self._first_non_empty_string(
        xmatters_payload.get("assignee"),
        xmatters_payload.get("owner"),
        existing.xmatters.assignee,
      ),
      response_plan=self._first_non_empty_string(
        xmatters_payload.get("response_plan"),
        xmatters_payload.get("plan"),
        existing.xmatters.response_plan,
      ),
      url=self._first_non_empty_string(
        xmatters_payload.get("url"),
        xmatters_payload.get("html_url"),
        existing.xmatters.url,
      ),
      updated_at=(
        self._parse_payload_datetime(xmatters_payload.get("updated_at"))
        or existing.xmatters.updated_at
      ),
      phase_graph=self._build_xmatters_recovery_phase_graph(
        payload=xmatters_payload,
        incident_status=xmatters_status,
        priority=self._first_non_empty_string(
          xmatters_payload.get("priority"),
          existing.xmatters.priority,
        ),
        assignee=self._first_non_empty_string(
          xmatters_payload.get("assignee"),
          xmatters_payload.get("owner"),
          existing.xmatters.assignee,
        ),
        response_plan=self._first_non_empty_string(
          xmatters_payload.get("response_plan"),
          xmatters_payload.get("plan"),
          existing.xmatters.response_plan,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.xmatters,
      ),
    )

    servicenow_payload = self._merge_payload_mappings(
      schema_payload.get("servicenow"),
      schema_payload.get("service_now"),
      payload.get("servicenow"),
      payload.get("servicenow_incident"),
      payload.get("service_now"),
    )
    servicenow_status = self._first_non_empty_string(
      servicenow_payload.get("incident_status"),
      servicenow_payload.get("status"),
      servicenow_payload.get("state"),
      workflow_state,
      payload.get("workflow_state"),
      existing.servicenow.incident_status,
    ) or "unknown"
    servicenow = OperatorIncidentServicenowRecoveryState(
      incident_number=self._first_non_empty_string(
        servicenow_payload.get("incident_number"),
        servicenow_payload.get("number"),
        workflow_reference,
        existing.servicenow.incident_number,
      ),
      external_reference=self._first_non_empty_string(
        servicenow_payload.get("external_reference"),
        servicenow_payload.get("reference"),
        reference,
        existing.servicenow.external_reference,
      ),
      incident_status=servicenow_status,
      priority=self._first_non_empty_string(
        servicenow_payload.get("priority"),
        existing.servicenow.priority,
      ),
      assigned_to=self._first_non_empty_string(
        servicenow_payload.get("assigned_to"),
        servicenow_payload.get("owner"),
        existing.servicenow.assigned_to,
      ),
      assignment_group=self._first_non_empty_string(
        servicenow_payload.get("assignment_group"),
        servicenow_payload.get("group"),
        existing.servicenow.assignment_group,
      ),
      url=self._first_non_empty_string(
        servicenow_payload.get("url"),
        servicenow_payload.get("html_url"),
        existing.servicenow.url,
      ),
      updated_at=(
        self._parse_payload_datetime(servicenow_payload.get("updated_at"))
        or existing.servicenow.updated_at
      ),
      phase_graph=self._build_servicenow_recovery_phase_graph(
        payload=servicenow_payload,
        incident_status=servicenow_status,
        priority=self._first_non_empty_string(
          servicenow_payload.get("priority"),
          existing.servicenow.priority,
        ),
        assigned_to=self._first_non_empty_string(
          servicenow_payload.get("assigned_to"),
          servicenow_payload.get("owner"),
          existing.servicenow.assigned_to,
        ),
        assignment_group=self._first_non_empty_string(
          servicenow_payload.get("assignment_group"),
          servicenow_payload.get("group"),
          existing.servicenow.assignment_group,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.servicenow,
      ),
    )

    squadcast_payload = self._merge_payload_mappings(
      schema_payload.get("squadcast"),
      schema_payload.get("squad_cast"),
      payload.get("squadcast"),
      payload.get("squadcast_incident"),
      payload.get("squad_cast"),
    )
    squadcast_status = self._first_non_empty_string(
      squadcast_payload.get("incident_status"),
      squadcast_payload.get("status"),
      squadcast_payload.get("state"),
      workflow_state,
      payload.get("workflow_state"),
      existing.squadcast.incident_status,
    ) or "unknown"
    squadcast = OperatorIncidentSquadcastRecoveryState(
      incident_id=self._first_non_empty_string(
        squadcast_payload.get("incident_id"),
        squadcast_payload.get("id"),
        workflow_reference,
        existing.squadcast.incident_id,
      ),
      external_reference=self._first_non_empty_string(
        squadcast_payload.get("external_reference"),
        squadcast_payload.get("reference"),
        reference,
        existing.squadcast.external_reference,
      ),
      incident_status=squadcast_status,
      severity=self._first_non_empty_string(
        squadcast_payload.get("severity"),
        squadcast_payload.get("priority"),
        existing.squadcast.severity,
      ),
      assignee=self._first_non_empty_string(
        squadcast_payload.get("assignee"),
        squadcast_payload.get("owner"),
        existing.squadcast.assignee,
      ),
      escalation_policy=self._first_non_empty_string(
        squadcast_payload.get("escalation_policy"),
        squadcast_payload.get("escalation_policy_name"),
        squadcast_payload.get("policy"),
        existing.squadcast.escalation_policy,
      ),
      url=self._first_non_empty_string(
        squadcast_payload.get("url"),
        squadcast_payload.get("html_url"),
        existing.squadcast.url,
      ),
      updated_at=(
        self._parse_payload_datetime(squadcast_payload.get("updated_at"))
        or existing.squadcast.updated_at
      ),
      phase_graph=self._build_squadcast_recovery_phase_graph(
        payload=squadcast_payload,
        incident_status=squadcast_status,
        severity=self._first_non_empty_string(
          squadcast_payload.get("severity"),
          squadcast_payload.get("priority"),
          existing.squadcast.severity,
        ),
        assignee=self._first_non_empty_string(
          squadcast_payload.get("assignee"),
          squadcast_payload.get("owner"),
          existing.squadcast.assignee,
        ),
        escalation_policy=self._first_non_empty_string(
          squadcast_payload.get("escalation_policy"),
          squadcast_payload.get("escalation_policy_name"),
          squadcast_payload.get("policy"),
          existing.squadcast.escalation_policy,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.squadcast,
      ),
    )

    bigpanda_payload = self._merge_payload_mappings(
      schema_payload.get("bigpanda"),
      schema_payload.get("big_panda"),
      payload.get("bigpanda"),
      payload.get("bigpanda_incident"),
      payload.get("big_panda"),
    )
    bigpanda_status = self._first_non_empty_string(
      bigpanda_payload.get("incident_status"),
      bigpanda_payload.get("status"),
      bigpanda_payload.get("state"),
      workflow_state,
      payload.get("workflow_state"),
      existing.bigpanda.incident_status,
    ) or "unknown"
    bigpanda = OperatorIncidentBigPandaRecoveryState(
      incident_id=self._first_non_empty_string(
        bigpanda_payload.get("incident_id"),
        bigpanda_payload.get("id"),
        workflow_reference,
        existing.bigpanda.incident_id,
      ),
      external_reference=self._first_non_empty_string(
        bigpanda_payload.get("external_reference"),
        bigpanda_payload.get("reference"),
        reference,
        existing.bigpanda.external_reference,
      ),
      incident_status=bigpanda_status,
      severity=self._first_non_empty_string(
        bigpanda_payload.get("severity"),
        bigpanda_payload.get("priority"),
        existing.bigpanda.severity,
      ),
      assignee=self._first_non_empty_string(
        bigpanda_payload.get("assignee"),
        bigpanda_payload.get("owner"),
        existing.bigpanda.assignee,
      ),
      team=self._first_non_empty_string(
        bigpanda_payload.get("team"),
        bigpanda_payload.get("team_name"),
        existing.bigpanda.team,
      ),
      url=self._first_non_empty_string(
        bigpanda_payload.get("url"),
        bigpanda_payload.get("html_url"),
        existing.bigpanda.url,
      ),
      updated_at=(
        self._parse_payload_datetime(bigpanda_payload.get("updated_at"))
        or existing.bigpanda.updated_at
      ),
      phase_graph=self._build_bigpanda_recovery_phase_graph(
        payload=bigpanda_payload,
        incident_status=bigpanda_status,
        severity=self._first_non_empty_string(
          bigpanda_payload.get("severity"),
          bigpanda_payload.get("priority"),
          existing.bigpanda.severity,
        ),
        assignee=self._first_non_empty_string(
          bigpanda_payload.get("assignee"),
          bigpanda_payload.get("owner"),
          existing.bigpanda.assignee,
        ),
        team=self._first_non_empty_string(
          bigpanda_payload.get("team"),
          bigpanda_payload.get("team_name"),
          existing.bigpanda.team,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.bigpanda,
      ),
    )

    grafana_oncall_payload = self._merge_payload_mappings(
      schema_payload.get("grafana_oncall"),
      schema_payload.get("grafanaoncall"),
      payload.get("grafana_oncall"),
      payload.get("grafana_oncall_incident"),
      payload.get("grafanaoncall"),
    )
    grafana_oncall_status = self._first_non_empty_string(
      grafana_oncall_payload.get("incident_status"),
      grafana_oncall_payload.get("status"),
      grafana_oncall_payload.get("state"),
      workflow_state,
      payload.get("workflow_state"),
      existing.grafana_oncall.incident_status,
    ) or "unknown"
    grafana_oncall = OperatorIncidentGrafanaOnCallRecoveryState(
      incident_id=self._first_non_empty_string(
        grafana_oncall_payload.get("incident_id"),
        grafana_oncall_payload.get("id"),
        workflow_reference,
        existing.grafana_oncall.incident_id,
      ),
      external_reference=self._first_non_empty_string(
        grafana_oncall_payload.get("external_reference"),
        grafana_oncall_payload.get("reference"),
        reference,
        existing.grafana_oncall.external_reference,
      ),
      incident_status=grafana_oncall_status,
      severity=self._first_non_empty_string(
        grafana_oncall_payload.get("severity"),
        grafana_oncall_payload.get("priority"),
        existing.grafana_oncall.severity,
      ),
      assignee=self._first_non_empty_string(
        grafana_oncall_payload.get("assignee"),
        grafana_oncall_payload.get("owner"),
        existing.grafana_oncall.assignee,
      ),
      escalation_chain=self._first_non_empty_string(
        grafana_oncall_payload.get("escalation_chain"),
        grafana_oncall_payload.get("escalation_chain_name"),
        existing.grafana_oncall.escalation_chain,
      ),
      url=self._first_non_empty_string(
        grafana_oncall_payload.get("url"),
        grafana_oncall_payload.get("html_url"),
        existing.grafana_oncall.url,
      ),
      updated_at=(
        self._parse_payload_datetime(grafana_oncall_payload.get("updated_at"))
        or existing.grafana_oncall.updated_at
      ),
      phase_graph=self._build_grafana_oncall_recovery_phase_graph(
        payload=grafana_oncall_payload,
        incident_status=grafana_oncall_status,
        severity=self._first_non_empty_string(
          grafana_oncall_payload.get("severity"),
          grafana_oncall_payload.get("priority"),
          existing.grafana_oncall.severity,
        ),
        assignee=self._first_non_empty_string(
          grafana_oncall_payload.get("assignee"),
          grafana_oncall_payload.get("owner"),
          existing.grafana_oncall.assignee,
        ),
        escalation_chain=self._first_non_empty_string(
          grafana_oncall_payload.get("escalation_chain"),
          grafana_oncall_payload.get("escalation_chain_name"),
          existing.grafana_oncall.escalation_chain,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.grafana_oncall,
      ),
    )

    zenduty_payload = self._merge_payload_mappings(
      schema_payload.get("zenduty"),
      payload.get("zenduty"),
      payload.get("zenduty_incident"),
    )
    zenduty_status = self._first_non_empty_string(
      zenduty_payload.get("incident_status"),
      zenduty_payload.get("status"),
      zenduty_payload.get("state"),
      workflow_state,
      payload.get("workflow_state"),
      existing.zenduty.incident_status,
    ) or "unknown"
    zenduty = OperatorIncidentZendutyRecoveryState(
      incident_id=self._first_non_empty_string(
        zenduty_payload.get("incident_id"),
        zenduty_payload.get("id"),
        workflow_reference,
        existing.zenduty.incident_id,
      ),
      external_reference=self._first_non_empty_string(
        zenduty_payload.get("external_reference"),
        zenduty_payload.get("reference"),
        reference,
        existing.zenduty.external_reference,
      ),
      incident_status=zenduty_status,
      severity=self._first_non_empty_string(
        zenduty_payload.get("severity"),
        zenduty_payload.get("priority"),
        existing.zenduty.severity,
      ),
      assignee=self._first_non_empty_string(
        zenduty_payload.get("assignee"),
        zenduty_payload.get("owner"),
        existing.zenduty.assignee,
      ),
      service=self._first_non_empty_string(
        zenduty_payload.get("service"),
        zenduty_payload.get("service_name"),
        existing.zenduty.service,
      ),
      url=self._first_non_empty_string(
        zenduty_payload.get("url"),
        zenduty_payload.get("html_url"),
        existing.zenduty.url,
      ),
      updated_at=(
        self._parse_payload_datetime(zenduty_payload.get("updated_at"))
        or existing.zenduty.updated_at
      ),
      phase_graph=self._build_zenduty_recovery_phase_graph(
        payload=zenduty_payload,
        incident_status=zenduty_status,
        severity=self._first_non_empty_string(
          zenduty_payload.get("severity"),
          zenduty_payload.get("priority"),
          existing.zenduty.severity,
        ),
        assignee=self._first_non_empty_string(
          zenduty_payload.get("assignee"),
          zenduty_payload.get("owner"),
          existing.zenduty.assignee,
        ),
        service=self._first_non_empty_string(
          zenduty_payload.get("service"),
          zenduty_payload.get("service_name"),
          existing.zenduty.service,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.zenduty,
      ),
    )

    splunk_oncall_payload = self._merge_payload_mappings(
      schema_payload.get("splunk_oncall"),
      schema_payload.get("splunkoncall"),
      schema_payload.get("victorops"),
      payload.get("splunk_oncall"),
      payload.get("splunk_oncall_incident"),
      payload.get("splunkoncall"),
      payload.get("victorops"),
    )
    splunk_oncall_status = self._first_non_empty_string(
      splunk_oncall_payload.get("incident_status"),
      splunk_oncall_payload.get("status"),
      splunk_oncall_payload.get("state"),
      workflow_state,
      payload.get("workflow_state"),
      existing.splunk_oncall.incident_status,
    ) or "unknown"
    splunk_oncall = OperatorIncidentSplunkOnCallRecoveryState(
      incident_id=self._first_non_empty_string(
        splunk_oncall_payload.get("incident_id"),
        splunk_oncall_payload.get("id"),
        workflow_reference,
        existing.splunk_oncall.incident_id,
      ),
      external_reference=self._first_non_empty_string(
        splunk_oncall_payload.get("external_reference"),
        splunk_oncall_payload.get("reference"),
        reference,
        existing.splunk_oncall.external_reference,
      ),
      incident_status=splunk_oncall_status,
      severity=self._first_non_empty_string(
        splunk_oncall_payload.get("severity"),
        splunk_oncall_payload.get("priority"),
        existing.splunk_oncall.severity,
      ),
      assignee=self._first_non_empty_string(
        splunk_oncall_payload.get("assignee"),
        splunk_oncall_payload.get("owner"),
        existing.splunk_oncall.assignee,
      ),
      routing_key=self._first_non_empty_string(
        splunk_oncall_payload.get("routing_key"),
        splunk_oncall_payload.get("routingKey"),
        existing.splunk_oncall.routing_key,
      ),
      url=self._first_non_empty_string(
        splunk_oncall_payload.get("url"),
        splunk_oncall_payload.get("html_url"),
        existing.splunk_oncall.url,
      ),
      updated_at=(
        self._parse_payload_datetime(splunk_oncall_payload.get("updated_at"))
        or existing.splunk_oncall.updated_at
      ),
      phase_graph=self._build_splunk_oncall_recovery_phase_graph(
        payload=splunk_oncall_payload,
        incident_status=splunk_oncall_status,
        severity=self._first_non_empty_string(
          splunk_oncall_payload.get("severity"),
          splunk_oncall_payload.get("priority"),
          existing.splunk_oncall.severity,
        ),
        assignee=self._first_non_empty_string(
          splunk_oncall_payload.get("assignee"),
          splunk_oncall_payload.get("owner"),
          existing.splunk_oncall.assignee,
        ),
        routing_key=self._first_non_empty_string(
          splunk_oncall_payload.get("routing_key"),
          splunk_oncall_payload.get("routingKey"),
          existing.splunk_oncall.routing_key,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.splunk_oncall,
      ),
    )

    jira_service_management_payload = self._merge_payload_mappings(
      schema_payload.get("jira_service_management"),
      schema_payload.get("jira_service_desk"),
      schema_payload.get("jsm"),
      payload.get("jira_service_management"),
      payload.get("jira_service_management_incident"),
      payload.get("jira_service_desk"),
      payload.get("jsm"),
    )
    jira_service_management_status = self._first_non_empty_string(
      jira_service_management_payload.get("incident_status"),
      jira_service_management_payload.get("status"),
      jira_service_management_payload.get("state"),
      workflow_state,
      payload.get("workflow_state"),
      existing.jira_service_management.incident_status,
    ) or "unknown"
    jira_service_management = OperatorIncidentJiraServiceManagementRecoveryState(
      incident_id=self._first_non_empty_string(
        jira_service_management_payload.get("incident_id"),
        jira_service_management_payload.get("id"),
        workflow_reference,
        existing.jira_service_management.incident_id,
      ),
      external_reference=self._first_non_empty_string(
        jira_service_management_payload.get("external_reference"),
        jira_service_management_payload.get("reference"),
        reference,
        existing.jira_service_management.external_reference,
      ),
      incident_status=jira_service_management_status,
      priority=self._first_non_empty_string(
        jira_service_management_payload.get("priority"),
        jira_service_management_payload.get("severity"),
        existing.jira_service_management.priority,
      ),
      assignee=self._first_non_empty_string(
        jira_service_management_payload.get("assignee"),
        jira_service_management_payload.get("owner"),
        existing.jira_service_management.assignee,
      ),
      service_project=self._first_non_empty_string(
        jira_service_management_payload.get("service_project"),
        jira_service_management_payload.get("project"),
        jira_service_management_payload.get("service_desk"),
        existing.jira_service_management.service_project,
      ),
      url=self._first_non_empty_string(
        jira_service_management_payload.get("url"),
        jira_service_management_payload.get("html_url"),
        existing.jira_service_management.url,
      ),
      updated_at=(
        self._parse_payload_datetime(jira_service_management_payload.get("updated_at"))
        or existing.jira_service_management.updated_at
      ),
      phase_graph=self._build_jira_service_management_recovery_phase_graph(
        payload=jira_service_management_payload,
        incident_status=jira_service_management_status,
        priority=self._first_non_empty_string(
          jira_service_management_payload.get("priority"),
          jira_service_management_payload.get("severity"),
          existing.jira_service_management.priority,
        ),
        assignee=self._first_non_empty_string(
          jira_service_management_payload.get("assignee"),
          jira_service_management_payload.get("owner"),
          existing.jira_service_management.assignee,
        ),
        service_project=self._first_non_empty_string(
          jira_service_management_payload.get("service_project"),
          jira_service_management_payload.get("project"),
          jira_service_management_payload.get("service_desk"),
          existing.jira_service_management.service_project,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.jira_service_management,
      ),
    )

    pagertree_payload = self._merge_payload_mappings(
      schema_payload.get("pagertree"),
      schema_payload.get("pager_tree"),
      payload.get("pagertree"),
      payload.get("pagertree_incident"),
      payload.get("pager_tree"),
    )
    pagertree_status = self._first_non_empty_string(
      pagertree_payload.get("incident_status"),
      pagertree_payload.get("status"),
      pagertree_payload.get("state"),
      workflow_state,
      payload.get("workflow_state"),
      existing.pagertree.incident_status,
    ) or "unknown"
    pagertree = OperatorIncidentPagerTreeRecoveryState(
      incident_id=self._first_non_empty_string(
        pagertree_payload.get("incident_id"),
        pagertree_payload.get("id"),
        workflow_reference,
        existing.pagertree.incident_id,
      ),
      external_reference=self._first_non_empty_string(
        pagertree_payload.get("external_reference"),
        pagertree_payload.get("reference"),
        reference,
        existing.pagertree.external_reference,
      ),
      incident_status=pagertree_status,
      urgency=self._first_non_empty_string(
        pagertree_payload.get("urgency"),
        pagertree_payload.get("priority"),
        pagertree_payload.get("severity"),
        existing.pagertree.urgency,
      ),
      assignee=self._first_non_empty_string(
        pagertree_payload.get("assignee"),
        pagertree_payload.get("owner"),
        existing.pagertree.assignee,
      ),
      team=self._first_non_empty_string(
        pagertree_payload.get("team"),
        pagertree_payload.get("service"),
        existing.pagertree.team,
      ),
      url=self._first_non_empty_string(
        pagertree_payload.get("url"),
        pagertree_payload.get("html_url"),
        existing.pagertree.url,
      ),
      updated_at=(
        self._parse_payload_datetime(pagertree_payload.get("updated_at"))
        or existing.pagertree.updated_at
      ),
      phase_graph=self._build_pagertree_recovery_phase_graph(
        payload=pagertree_payload,
        incident_status=pagertree_status,
        urgency=self._first_non_empty_string(
          pagertree_payload.get("urgency"),
          pagertree_payload.get("priority"),
          pagertree_payload.get("severity"),
          existing.pagertree.urgency,
        ),
        assignee=self._first_non_empty_string(
          pagertree_payload.get("assignee"),
          pagertree_payload.get("owner"),
          existing.pagertree.assignee,
        ),
        team=self._first_non_empty_string(
          pagertree_payload.get("team"),
          pagertree_payload.get("service"),
          existing.pagertree.team,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.pagertree,
      ),
    )

    alertops_payload = self._merge_payload_mappings(
      schema_payload.get("alertops"),
      schema_payload.get("alert_ops"),
      payload.get("alertops"),
      payload.get("alertops_incident"),
      payload.get("alert_ops"),
    )
    alertops_status = self._first_non_empty_string(
      alertops_payload.get("incident_status"),
      alertops_payload.get("status"),
      alertops_payload.get("state"),
      workflow_state,
      payload.get("workflow_state"),
      existing.alertops.incident_status,
    ) or "unknown"
    alertops = OperatorIncidentAlertOpsRecoveryState(
      incident_id=self._first_non_empty_string(
        alertops_payload.get("incident_id"),
        alertops_payload.get("id"),
        workflow_reference,
        existing.alertops.incident_id,
      ),
      external_reference=self._first_non_empty_string(
        alertops_payload.get("external_reference"),
        alertops_payload.get("reference"),
        reference,
        existing.alertops.external_reference,
      ),
      incident_status=alertops_status,
      priority=self._first_non_empty_string(
        alertops_payload.get("priority"),
        alertops_payload.get("severity"),
        alertops_payload.get("urgency"),
        existing.alertops.priority,
      ),
      owner=self._first_non_empty_string(
        alertops_payload.get("owner"),
        alertops_payload.get("assignee"),
        existing.alertops.owner,
      ),
      service=self._first_non_empty_string(
        alertops_payload.get("service"),
        alertops_payload.get("team"),
        existing.alertops.service,
      ),
      url=self._first_non_empty_string(
        alertops_payload.get("url"),
        alertops_payload.get("html_url"),
        existing.alertops.url,
      ),
      updated_at=(
        self._parse_payload_datetime(alertops_payload.get("updated_at"))
        or existing.alertops.updated_at
      ),
      phase_graph=self._build_alertops_recovery_phase_graph(
        payload=alertops_payload,
        incident_status=alertops_status,
        priority=self._first_non_empty_string(
          alertops_payload.get("priority"),
          alertops_payload.get("severity"),
          alertops_payload.get("urgency"),
          existing.alertops.priority,
        ),
        owner=self._first_non_empty_string(
          alertops_payload.get("owner"),
          alertops_payload.get("assignee"),
          existing.alertops.owner,
        ),
        service=self._first_non_empty_string(
          alertops_payload.get("service"),
          alertops_payload.get("team"),
          existing.alertops.service,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.alertops,
      ),
    )

    signl4_payload = self._merge_payload_mappings(
      schema_payload.get("signl4"),
      schema_payload.get("signl_4"),
      payload.get("signl4"),
      payload.get("signl4_alert"),
      payload.get("signl_4"),
    )
    signl4_status = self._first_non_empty_string(
      signl4_payload.get("alert_status"),
      signl4_payload.get("status"),
      signl4_payload.get("state"),
      workflow_state,
      payload.get("workflow_state"),
      existing.signl4.alert_status,
    ) or "unknown"
    signl4 = OperatorIncidentSignl4RecoveryState(
      alert_id=self._first_non_empty_string(
        signl4_payload.get("alert_id"),
        signl4_payload.get("id"),
        workflow_reference,
        existing.signl4.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        signl4_payload.get("external_reference"),
        signl4_payload.get("reference"),
        reference,
        existing.signl4.external_reference,
      ),
      alert_status=signl4_status,
      priority=self._first_non_empty_string(
        signl4_payload.get("priority"),
        signl4_payload.get("severity"),
        signl4_payload.get("urgency"),
        existing.signl4.priority,
      ),
      team=self._first_non_empty_string(
        signl4_payload.get("team"),
        signl4_payload.get("service"),
        existing.signl4.team,
      ),
      assignee=self._first_non_empty_string(
        signl4_payload.get("assignee"),
        signl4_payload.get("owner"),
        existing.signl4.assignee,
      ),
      url=self._first_non_empty_string(
        signl4_payload.get("url"),
        signl4_payload.get("html_url"),
        existing.signl4.url,
      ),
      updated_at=(
        self._parse_payload_datetime(signl4_payload.get("updated_at"))
        or existing.signl4.updated_at
      ),
      phase_graph=self._build_signl4_recovery_phase_graph(
        payload=signl4_payload,
        alert_status=signl4_status,
        priority=self._first_non_empty_string(
          signl4_payload.get("priority"),
          signl4_payload.get("severity"),
          signl4_payload.get("urgency"),
          existing.signl4.priority,
        ),
        team=self._first_non_empty_string(
          signl4_payload.get("team"),
          signl4_payload.get("service"),
          existing.signl4.team,
        ),
        assignee=self._first_non_empty_string(
          signl4_payload.get("assignee"),
          signl4_payload.get("owner"),
          existing.signl4.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.signl4,
      ),
    )

    ilert_payload = self._merge_payload_mappings(
      schema_payload.get("ilert"),
      schema_payload.get("i_lert"),
      payload.get("ilert"),
      payload.get("ilert_alert"),
      payload.get("i_lert"),
    )
    ilert_status = self._first_non_empty_string(
      ilert_payload.get("alert_status"),
      ilert_payload.get("status"),
      ilert_payload.get("state"),
      workflow_state,
      payload.get("workflow_state"),
      existing.ilert.alert_status,
    ) or "unknown"
    ilert = OperatorIncidentIlertRecoveryState(
      alert_id=self._first_non_empty_string(
        ilert_payload.get("alert_id"),
        ilert_payload.get("id"),
        ilert_payload.get("alertId"),
        workflow_reference,
        existing.ilert.alert_id,
      ),
      external_reference=self._first_non_empty_string(
        ilert_payload.get("external_reference"),
        ilert_payload.get("reference"),
        reference,
        existing.ilert.external_reference,
      ),
      alert_status=ilert_status,
      priority=self._first_non_empty_string(
        ilert_payload.get("priority"),
        ilert_payload.get("severity"),
        ilert_payload.get("urgency"),
        existing.ilert.priority,
      ),
      escalation_policy=self._first_non_empty_string(
        ilert_payload.get("escalation_policy"),
        ilert_payload.get("escalationPolicy"),
        ilert_payload.get("policy"),
        ilert_payload.get("source"),
        existing.ilert.escalation_policy,
      ),
      assignee=self._first_non_empty_string(
        ilert_payload.get("assignee"),
        ilert_payload.get("owner"),
        ilert_payload.get("assigned_to"),
        existing.ilert.assignee,
      ),
      url=self._first_non_empty_string(
        ilert_payload.get("url"),
        ilert_payload.get("html_url"),
        ilert_payload.get("link"),
        existing.ilert.url,
      ),
      updated_at=(
        self._parse_payload_datetime(ilert_payload.get("updated_at"))
        or existing.ilert.updated_at
      ),
      phase_graph=self._build_ilert_recovery_phase_graph(
        payload=ilert_payload,
        alert_status=ilert_status,
        priority=self._first_non_empty_string(
          ilert_payload.get("priority"),
          ilert_payload.get("severity"),
          ilert_payload.get("urgency"),
          existing.ilert.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          ilert_payload.get("escalation_policy"),
          ilert_payload.get("escalationPolicy"),
          ilert_payload.get("policy"),
          ilert_payload.get("source"),
          existing.ilert.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          ilert_payload.get("assignee"),
          ilert_payload.get("owner"),
          ilert_payload.get("assigned_to"),
          existing.ilert.assignee,
        ),
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        existing=existing.ilert,
      ),
    )

    if normalized_provider == "pagerduty":
      return (
        "pagerduty",
        pagerduty,
        existing.opsgenie,
        existing.incidentio,
        existing.firehydrant,
        existing.rootly,
        existing.blameless,
        existing.xmatters,
        existing.servicenow,
        existing.squadcast,
        existing.bigpanda,
        existing.grafana_oncall,
        existing.zenduty,
        existing.splunk_oncall,
        existing.jira_service_management,
        existing.pagertree,
        existing.alertops,
        existing.signl4,
        existing.ilert,
      )
    if normalized_provider == "opsgenie":
      return (
        "opsgenie",
        existing.pagerduty,
        opsgenie,
        existing.incidentio,
        existing.firehydrant,
        existing.rootly,
        existing.blameless,
        existing.xmatters,
        existing.servicenow,
        existing.squadcast,
        existing.bigpanda,
        existing.grafana_oncall,
        existing.zenduty,
        existing.splunk_oncall,
        existing.jira_service_management,
        existing.pagertree,
        existing.alertops,
        existing.signl4,
        existing.ilert,
      )
    if normalized_provider == "incidentio":
      return (
        "incidentio",
        existing.pagerduty,
        existing.opsgenie,
        incidentio,
        existing.firehydrant,
        existing.rootly,
        existing.blameless,
        existing.xmatters,
        existing.servicenow,
        existing.squadcast,
        existing.bigpanda,
        existing.grafana_oncall,
        existing.zenduty,
        existing.splunk_oncall,
        existing.jira_service_management,
        existing.pagertree,
        existing.alertops,
        existing.signl4,
        existing.ilert,
      )
    if normalized_provider == "firehydrant":
      return (
        "firehydrant",
        existing.pagerduty,
        existing.opsgenie,
        existing.incidentio,
        firehydrant,
        existing.rootly,
        existing.blameless,
        existing.xmatters,
        existing.servicenow,
        existing.squadcast,
        existing.bigpanda,
        existing.grafana_oncall,
        existing.zenduty,
        existing.splunk_oncall,
        existing.jira_service_management,
        existing.pagertree,
        existing.alertops,
        existing.signl4,
        existing.ilert,
      )
    if normalized_provider == "rootly":
      return (
        "rootly",
        existing.pagerduty,
        existing.opsgenie,
        existing.incidentio,
        existing.firehydrant,
        rootly,
        existing.blameless,
        existing.xmatters,
        existing.servicenow,
        existing.squadcast,
        existing.bigpanda,
        existing.grafana_oncall,
        existing.zenduty,
        existing.splunk_oncall,
        existing.jira_service_management,
        existing.pagertree,
        existing.alertops,
        existing.signl4,
        existing.ilert,
      )
    if normalized_provider == "blameless":
      return (
        "blameless",
        existing.pagerduty,
        existing.opsgenie,
        existing.incidentio,
        existing.firehydrant,
        existing.rootly,
        blameless,
        existing.xmatters,
        existing.servicenow,
        existing.squadcast,
        existing.bigpanda,
        existing.grafana_oncall,
        existing.zenduty,
        existing.splunk_oncall,
        existing.jira_service_management,
        existing.pagertree,
        existing.alertops,
        existing.signl4,
        existing.ilert,
      )
    if normalized_provider == "xmatters":
      return (
        "xmatters",
        existing.pagerduty,
        existing.opsgenie,
        existing.incidentio,
        existing.firehydrant,
        existing.rootly,
        existing.blameless,
        xmatters,
        existing.servicenow,
        existing.squadcast,
        existing.bigpanda,
        existing.grafana_oncall,
        existing.zenduty,
        existing.splunk_oncall,
        existing.jira_service_management,
        existing.pagertree,
        existing.alertops,
        existing.signl4,
        existing.ilert,
      )
    if normalized_provider == "servicenow":
      return (
        "servicenow",
        existing.pagerduty,
        existing.opsgenie,
        existing.incidentio,
        existing.firehydrant,
        existing.rootly,
        existing.blameless,
        existing.xmatters,
        servicenow,
        existing.squadcast,
        existing.bigpanda,
        existing.grafana_oncall,
        existing.zenduty,
        existing.splunk_oncall,
        existing.jira_service_management,
        existing.pagertree,
        existing.alertops,
        existing.signl4,
        existing.ilert,
      )
    if normalized_provider == "squadcast":
      return (
        "squadcast",
        existing.pagerduty,
        existing.opsgenie,
        existing.incidentio,
        existing.firehydrant,
        existing.rootly,
        existing.blameless,
        existing.xmatters,
        existing.servicenow,
        squadcast,
        existing.bigpanda,
        existing.grafana_oncall,
        existing.zenduty,
        existing.splunk_oncall,
        existing.jira_service_management,
        existing.pagertree,
        existing.alertops,
        existing.signl4,
        existing.ilert,
      )
    if normalized_provider == "bigpanda":
      return (
        "bigpanda",
        existing.pagerduty,
        existing.opsgenie,
        existing.incidentio,
        existing.firehydrant,
        existing.rootly,
        existing.blameless,
        existing.xmatters,
        existing.servicenow,
        existing.squadcast,
        bigpanda,
        existing.grafana_oncall,
        existing.zenduty,
        existing.splunk_oncall,
        existing.jira_service_management,
        existing.pagertree,
        existing.alertops,
        existing.signl4,
        existing.ilert,
      )
    if normalized_provider == "grafana_oncall":
      return (
        "grafana_oncall",
        existing.pagerduty,
        existing.opsgenie,
        existing.incidentio,
        existing.firehydrant,
        existing.rootly,
        existing.blameless,
        existing.xmatters,
        existing.servicenow,
        existing.squadcast,
        existing.bigpanda,
        grafana_oncall,
        existing.zenduty,
        existing.splunk_oncall,
        existing.jira_service_management,
        existing.pagertree,
        existing.alertops,
        existing.signl4,
        existing.ilert,
      )
    if normalized_provider == "zenduty":
      return (
        "zenduty",
        existing.pagerduty,
        existing.opsgenie,
        existing.incidentio,
        existing.firehydrant,
        existing.rootly,
        existing.blameless,
        existing.xmatters,
        existing.servicenow,
        existing.squadcast,
        existing.bigpanda,
        existing.grafana_oncall,
        zenduty,
        existing.splunk_oncall,
        existing.jira_service_management,
        existing.pagertree,
        existing.alertops,
        existing.signl4,
        existing.ilert,
      )
    if normalized_provider == "splunk_oncall":
      return (
        "splunk_oncall",
        existing.pagerduty,
        existing.opsgenie,
        existing.incidentio,
        existing.firehydrant,
        existing.rootly,
        existing.blameless,
        existing.xmatters,
        existing.servicenow,
        existing.squadcast,
        existing.bigpanda,
        existing.grafana_oncall,
        existing.zenduty,
        splunk_oncall,
        existing.jira_service_management,
        existing.pagertree,
        existing.alertops,
        existing.signl4,
        existing.ilert,
      )
    if normalized_provider == "jira_service_management":
      return (
        "jira_service_management",
        existing.pagerduty,
        existing.opsgenie,
        existing.incidentio,
        existing.firehydrant,
        existing.rootly,
        existing.blameless,
        existing.xmatters,
        existing.servicenow,
        existing.squadcast,
        existing.bigpanda,
        existing.grafana_oncall,
        existing.zenduty,
        existing.splunk_oncall,
        jira_service_management,
        existing.pagertree,
        existing.alertops,
        existing.signl4,
        existing.ilert,
      )
    if normalized_provider == "pagertree":
      return (
        "pagertree",
        existing.pagerduty,
        existing.opsgenie,
        existing.incidentio,
        existing.firehydrant,
        existing.rootly,
        existing.blameless,
        existing.xmatters,
        existing.servicenow,
        existing.squadcast,
        existing.bigpanda,
        existing.grafana_oncall,
        existing.zenduty,
        existing.splunk_oncall,
        existing.jira_service_management,
        pagertree,
        existing.alertops,
        existing.signl4,
        existing.ilert,
      )
    if normalized_provider == "alertops":
      return (
        "alertops",
        existing.pagerduty,
        existing.opsgenie,
        existing.incidentio,
        existing.firehydrant,
        existing.rootly,
        existing.blameless,
        existing.xmatters,
        existing.servicenow,
        existing.squadcast,
        existing.bigpanda,
        existing.grafana_oncall,
        existing.zenduty,
        existing.splunk_oncall,
        existing.jira_service_management,
        existing.pagertree,
        alertops,
        existing.signl4,
        existing.ilert,
      )
    if normalized_provider == "signl4":
      return (
        "signl4",
        existing.pagerduty,
        existing.opsgenie,
        existing.incidentio,
        existing.firehydrant,
        existing.rootly,
        existing.blameless,
        existing.xmatters,
        existing.servicenow,
        existing.squadcast,
        existing.bigpanda,
        existing.grafana_oncall,
        existing.zenduty,
        existing.splunk_oncall,
        existing.jira_service_management,
        existing.pagertree,
        existing.alertops,
        signl4,
        existing.ilert,
      )
    if normalized_provider == "ilert":
      return (
        "ilert",
        existing.pagerduty,
        existing.opsgenie,
        existing.incidentio,
        existing.firehydrant,
        existing.rootly,
        existing.blameless,
        existing.xmatters,
        existing.servicenow,
        existing.squadcast,
        existing.bigpanda,
        existing.grafana_oncall,
        existing.zenduty,
        existing.splunk_oncall,
        existing.jira_service_management,
        existing.pagertree,
        existing.alertops,
        existing.signl4,
        ilert,
      )
    return (
      existing.provider_schema_kind,
      existing.pagerduty,
      existing.opsgenie,
      existing.incidentio,
      existing.firehydrant,
      existing.rootly,
      existing.blameless,
      existing.xmatters,
      existing.servicenow,
      existing.squadcast,
      existing.bigpanda,
      existing.grafana_oncall,
      existing.zenduty,
      existing.splunk_oncall,
      existing.jira_service_management,
      existing.pagertree,
      existing.alertops,
      existing.signl4,
      existing.ilert,
    )

  def _build_provider_recovery_state(
    self,
    *,
    remediation: OperatorIncidentRemediation,
    next_state: str,
    provider: str,
    detail: str,
    synced_at: datetime,
    workflow_reference: str | None,
    payload: dict[str, Any],
    event_kind: str | None = None,
  ) -> OperatorIncidentProviderRecoveryState:
    existing = remediation.provider_recovery
    verification_payload = self._extract_payload_mapping(payload.get("verification"))
    target_payload = self._extract_payload_mapping(payload.get("target"))
    targets_payload = self._extract_payload_mapping(payload.get("targets"))
    lifecycle_state = self._first_non_empty_string(
      payload.get("recovery_state"),
      payload.get("recovery_phase"),
      payload.get("job_state"),
      payload.get("status"),
    ) or self._provider_recovery_lifecycle_for_event(
      remediation_state=next_state,
      event_kind=event_kind,
    )
    verification = OperatorIncidentProviderRecoveryVerification(
      state=self._first_non_empty_string(
        verification_payload.get("state"),
        payload.get("verification_state"),
        existing.verification.state,
      ) or "unknown",
      checked_at=(
        self._parse_payload_datetime(verification_payload.get("checked_at"))
        or self._parse_payload_datetime(payload.get("verified_at"))
        or self._parse_payload_datetime(payload.get("checked_at"))
        or existing.verification.checked_at
      ),
      summary=self._first_non_empty_string(
        verification_payload.get("summary"),
        verification_payload.get("message"),
        payload.get("verification_summary"),
        existing.verification.summary,
      ),
      issues=self._extract_string_tuple(
        verification_payload.get("issues"),
        payload.get("verification_issues"),
        existing.verification.issues,
      ),
    )
    status_machine = self._build_provider_recovery_status_machine(
      existing=existing.status_machine,
      remediation_state=next_state,
      event_kind=event_kind,
      workflow_state=existing.status_machine.workflow_state,
      workflow_action=existing.status_machine.workflow_action,
      detail=detail,
      event_at=synced_at,
      payload=payload,
    )
    telemetry = self._build_provider_recovery_telemetry(
      payload=payload,
      synced_at=synced_at,
      status_machine=status_machine,
      existing=existing.telemetry,
    )
    reference = self._first_non_empty_string(
      payload.get("reference"),
      payload.get("job_reference"),
      payload.get("recovery_reference"),
      existing.reference,
      remediation.reference,
    )
    (
      provider_schema_kind,
      pagerduty_schema,
      opsgenie_schema,
      incidentio_schema,
      firehydrant_schema,
      rootly_schema,
      blameless_schema,
      xmatters_schema,
      servicenow_schema,
      squadcast_schema,
      bigpanda_schema,
      grafana_oncall_schema,
      zenduty_schema,
      splunk_oncall_schema,
      jira_service_management_schema,
      pagertree_schema,
      alertops_schema,
      signl4_schema,
      ilert_schema,
    ) = (
      self._build_provider_recovery_provider_schema(
        provider=provider or existing.provider or remediation.provider or "",
        payload=payload,
        lifecycle_state=lifecycle_state,
        status_machine=status_machine,
        synced_at=synced_at,
        workflow_state=status_machine.workflow_state,
        workflow_reference=self._first_non_empty_string(
          workflow_reference,
          payload.get("workflow_reference"),
          payload.get("provider_workflow_reference"),
          existing.workflow_reference,
        ),
        reference=reference,
        existing=existing,
      )
    )
    betterstack_schema = existing.betterstack
    normalized_provider = self._normalize_paging_provider(
      provider or existing.provider or remediation.provider or ""
    )
    betterstack_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("betterstack"),
      self._extract_payload_mapping(payload.get("provider_schema")).get("better_stack"),
      payload.get("betterstack"),
      payload.get("betterstack_alert"),
      payload.get("better_stack"),
    )
    if normalized_provider == "betterstack" or betterstack_payload:
      betterstack_status = self._first_non_empty_string(
        betterstack_payload.get("alert_status"),
        betterstack_payload.get("status"),
        betterstack_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.betterstack.alert_status,
      ) or "unknown"
      betterstack_schema = OperatorIncidentBetterstackRecoveryState(
        alert_id=self._first_non_empty_string(
          betterstack_payload.get("alert_id"),
          betterstack_payload.get("id"),
          betterstack_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.betterstack.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          betterstack_payload.get("external_reference"),
          betterstack_payload.get("reference"),
          reference,
          existing.betterstack.external_reference,
        ),
        alert_status=betterstack_status,
        priority=self._first_non_empty_string(
          betterstack_payload.get("priority"),
          betterstack_payload.get("severity"),
          betterstack_payload.get("urgency"),
          existing.betterstack.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          betterstack_payload.get("escalation_policy"),
          betterstack_payload.get("escalationPolicy"),
          betterstack_payload.get("policy"),
          betterstack_payload.get("source"),
          existing.betterstack.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          betterstack_payload.get("assignee"),
          betterstack_payload.get("owner"),
          betterstack_payload.get("assigned_to"),
          existing.betterstack.assignee,
        ),
        url=self._first_non_empty_string(
          betterstack_payload.get("url"),
          betterstack_payload.get("html_url"),
          betterstack_payload.get("link"),
          existing.betterstack.url,
        ),
        updated_at=(
          self._parse_payload_datetime(betterstack_payload.get("updated_at"))
          or existing.betterstack.updated_at
        ),
        phase_graph=self._build_betterstack_recovery_phase_graph(
          payload=betterstack_payload,
          alert_status=betterstack_status,
          priority=self._first_non_empty_string(
            betterstack_payload.get("priority"),
            betterstack_payload.get("severity"),
            betterstack_payload.get("urgency"),
            existing.betterstack.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            betterstack_payload.get("escalation_policy"),
            betterstack_payload.get("escalationPolicy"),
            betterstack_payload.get("policy"),
            betterstack_payload.get("source"),
            existing.betterstack.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            betterstack_payload.get("assignee"),
            betterstack_payload.get("owner"),
            betterstack_payload.get("assigned_to"),
            existing.betterstack.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.betterstack,
        ),
      )
      provider_schema_kind = "betterstack"
    onpage_schema = existing.onpage
    onpage_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("onpage"),
      self._extract_payload_mapping(payload.get("provider_schema")).get("on_page"),
      payload.get("onpage"),
      payload.get("onpage_alert"),
      payload.get("on_page"),
    )
    if normalized_provider == "onpage" or onpage_payload:
      onpage_status = self._first_non_empty_string(
        onpage_payload.get("alert_status"),
        onpage_payload.get("status"),
        onpage_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.onpage.alert_status,
      ) or "unknown"
      onpage_schema = OperatorIncidentOnpageRecoveryState(
        alert_id=self._first_non_empty_string(
          onpage_payload.get("alert_id"),
          onpage_payload.get("id"),
          onpage_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.onpage.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          onpage_payload.get("external_reference"),
          onpage_payload.get("reference"),
          reference,
          existing.onpage.external_reference,
        ),
        alert_status=onpage_status,
        priority=self._first_non_empty_string(
          onpage_payload.get("priority"),
          onpage_payload.get("severity"),
          onpage_payload.get("urgency"),
          existing.onpage.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          onpage_payload.get("escalation_policy"),
          onpage_payload.get("escalationPolicy"),
          onpage_payload.get("policy"),
          onpage_payload.get("source"),
          existing.onpage.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          onpage_payload.get("assignee"),
          onpage_payload.get("owner"),
          onpage_payload.get("assigned_to"),
          existing.onpage.assignee,
        ),
        url=self._first_non_empty_string(
          onpage_payload.get("url"),
          onpage_payload.get("html_url"),
          onpage_payload.get("link"),
          existing.onpage.url,
        ),
        updated_at=(
          self._parse_payload_datetime(onpage_payload.get("updated_at"))
          or existing.onpage.updated_at
        ),
        phase_graph=self._build_onpage_recovery_phase_graph(
          payload=onpage_payload,
          alert_status=onpage_status,
          priority=self._first_non_empty_string(
            onpage_payload.get("priority"),
            onpage_payload.get("severity"),
            onpage_payload.get("urgency"),
            existing.onpage.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            onpage_payload.get("escalation_policy"),
            onpage_payload.get("escalationPolicy"),
            onpage_payload.get("policy"),
            onpage_payload.get("source"),
            existing.onpage.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            onpage_payload.get("assignee"),
            onpage_payload.get("owner"),
            onpage_payload.get("assigned_to"),
            existing.onpage.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.onpage,
        ),
      )
      provider_schema_kind = "onpage"
    allquiet_schema = existing.allquiet
    allquiet_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("allquiet"),
      self._extract_payload_mapping(payload.get("provider_schema")).get("all_quiet"),
      payload.get("allquiet"),
      payload.get("allquiet_alert"),
      payload.get("all_quiet"),
    )
    if normalized_provider == "allquiet" or allquiet_payload:
      allquiet_status = self._first_non_empty_string(
        allquiet_payload.get("alert_status"),
        allquiet_payload.get("status"),
        allquiet_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.allquiet.alert_status,
      ) or "unknown"
      allquiet_schema = OperatorIncidentAllquietRecoveryState(
        alert_id=self._first_non_empty_string(
          allquiet_payload.get("alert_id"),
          allquiet_payload.get("id"),
          allquiet_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.allquiet.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          allquiet_payload.get("external_reference"),
          allquiet_payload.get("reference"),
          reference,
          existing.allquiet.external_reference,
        ),
        alert_status=allquiet_status,
        priority=self._first_non_empty_string(
          allquiet_payload.get("priority"),
          allquiet_payload.get("severity"),
          allquiet_payload.get("urgency"),
          existing.allquiet.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          allquiet_payload.get("escalation_policy"),
          allquiet_payload.get("escalationPolicy"),
          allquiet_payload.get("policy"),
          allquiet_payload.get("source"),
          existing.allquiet.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          allquiet_payload.get("assignee"),
          allquiet_payload.get("owner"),
          allquiet_payload.get("assigned_to"),
          existing.allquiet.assignee,
        ),
        url=self._first_non_empty_string(
          allquiet_payload.get("url"),
          allquiet_payload.get("html_url"),
          allquiet_payload.get("link"),
          existing.allquiet.url,
        ),
        updated_at=(
          self._parse_payload_datetime(allquiet_payload.get("updated_at"))
          or existing.allquiet.updated_at
        ),
        phase_graph=self._build_allquiet_recovery_phase_graph(
          payload=allquiet_payload,
          alert_status=allquiet_status,
          priority=self._first_non_empty_string(
            allquiet_payload.get("priority"),
            allquiet_payload.get("severity"),
            allquiet_payload.get("urgency"),
            existing.allquiet.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            allquiet_payload.get("escalation_policy"),
            allquiet_payload.get("escalationPolicy"),
            allquiet_payload.get("policy"),
            allquiet_payload.get("source"),
            existing.allquiet.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            allquiet_payload.get("assignee"),
            allquiet_payload.get("owner"),
            allquiet_payload.get("assigned_to"),
            existing.allquiet.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.allquiet,
        ),
      )
      provider_schema_kind = "allquiet"
    moogsoft_schema = existing.moogsoft
    moogsoft_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("moogsoft"),
      payload.get("moogsoft"),
      payload.get("moogsoft_alert"),
    )
    if normalized_provider == "moogsoft" or moogsoft_payload:
      moogsoft_status = self._first_non_empty_string(
        moogsoft_payload.get("alert_status"),
        moogsoft_payload.get("status"),
        moogsoft_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.moogsoft.alert_status,
      ) or "unknown"
      moogsoft_schema = OperatorIncidentMoogsoftRecoveryState(
        alert_id=self._first_non_empty_string(
          moogsoft_payload.get("alert_id"),
          moogsoft_payload.get("id"),
          moogsoft_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.moogsoft.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          moogsoft_payload.get("external_reference"),
          moogsoft_payload.get("reference"),
          reference,
          existing.moogsoft.external_reference,
        ),
        alert_status=moogsoft_status,
        priority=self._first_non_empty_string(
          moogsoft_payload.get("priority"),
          moogsoft_payload.get("severity"),
          moogsoft_payload.get("urgency"),
          existing.moogsoft.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          moogsoft_payload.get("escalation_policy"),
          moogsoft_payload.get("escalationPolicy"),
          moogsoft_payload.get("policy"),
          moogsoft_payload.get("source"),
          existing.moogsoft.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          moogsoft_payload.get("assignee"),
          moogsoft_payload.get("owner"),
          moogsoft_payload.get("assigned_to"),
          existing.moogsoft.assignee,
        ),
        url=self._first_non_empty_string(
          moogsoft_payload.get("url"),
          moogsoft_payload.get("html_url"),
          moogsoft_payload.get("link"),
          existing.moogsoft.url,
        ),
        updated_at=(
          self._parse_payload_datetime(moogsoft_payload.get("updated_at"))
          or existing.moogsoft.updated_at
        ),
        phase_graph=self._build_moogsoft_recovery_phase_graph(
          payload=moogsoft_payload,
          alert_status=moogsoft_status,
          priority=self._first_non_empty_string(
            moogsoft_payload.get("priority"),
            moogsoft_payload.get("severity"),
            moogsoft_payload.get("urgency"),
            existing.moogsoft.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            moogsoft_payload.get("escalation_policy"),
            moogsoft_payload.get("escalationPolicy"),
            moogsoft_payload.get("policy"),
            moogsoft_payload.get("source"),
            existing.moogsoft.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            moogsoft_payload.get("assignee"),
            moogsoft_payload.get("owner"),
            moogsoft_payload.get("assigned_to"),
            existing.moogsoft.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.moogsoft,
        ),
      )
      provider_schema_kind = "moogsoft"
    spikesh_schema = existing.spikesh
    spikesh_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("spikesh"),
      payload.get("spikesh"),
      payload.get("spikesh_alert"),
    )
    if normalized_provider == "spikesh" or spikesh_payload:
      spikesh_status = self._first_non_empty_string(
        spikesh_payload.get("alert_status"),
        spikesh_payload.get("status"),
        spikesh_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.spikesh.alert_status,
      ) or "unknown"
      spikesh_schema = OperatorIncidentSpikeshRecoveryState(
        alert_id=self._first_non_empty_string(
          spikesh_payload.get("alert_id"),
          spikesh_payload.get("id"),
          spikesh_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.spikesh.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          spikesh_payload.get("external_reference"),
          spikesh_payload.get("reference"),
          reference,
          existing.spikesh.external_reference,
        ),
        alert_status=spikesh_status,
        priority=self._first_non_empty_string(
          spikesh_payload.get("priority"),
          spikesh_payload.get("severity"),
          spikesh_payload.get("urgency"),
          existing.spikesh.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          spikesh_payload.get("escalation_policy"),
          spikesh_payload.get("escalationPolicy"),
          spikesh_payload.get("policy"),
          spikesh_payload.get("source"),
          existing.spikesh.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          spikesh_payload.get("assignee"),
          spikesh_payload.get("owner"),
          spikesh_payload.get("assigned_to"),
          existing.spikesh.assignee,
        ),
        url=self._first_non_empty_string(
          spikesh_payload.get("url"),
          spikesh_payload.get("html_url"),
          spikesh_payload.get("link"),
          existing.spikesh.url,
        ),
        updated_at=(
          self._parse_payload_datetime(spikesh_payload.get("updated_at"))
          or existing.spikesh.updated_at
        ),
        phase_graph=self._build_spikesh_recovery_phase_graph(
          payload=spikesh_payload,
          alert_status=spikesh_status,
          priority=self._first_non_empty_string(
            spikesh_payload.get("priority"),
            spikesh_payload.get("severity"),
            spikesh_payload.get("urgency"),
            existing.spikesh.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            spikesh_payload.get("escalation_policy"),
            spikesh_payload.get("escalationPolicy"),
            spikesh_payload.get("policy"),
            spikesh_payload.get("source"),
            existing.spikesh.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            spikesh_payload.get("assignee"),
            spikesh_payload.get("owner"),
            spikesh_payload.get("assigned_to"),
            existing.spikesh.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.spikesh,
        ),
      )
      provider_schema_kind = "spikesh"
    dutycalls_schema = existing.dutycalls
    dutycalls_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("dutycalls"),
      payload.get("dutycalls"),
      payload.get("dutycalls_alert"),
    )
    if normalized_provider == "dutycalls" or dutycalls_payload:
      dutycalls_status = self._first_non_empty_string(
        dutycalls_payload.get("alert_status"),
        dutycalls_payload.get("status"),
        dutycalls_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.dutycalls.alert_status,
      ) or "unknown"
      dutycalls_schema = OperatorIncidentDutyCallsRecoveryState(
        alert_id=self._first_non_empty_string(
          dutycalls_payload.get("alert_id"),
          dutycalls_payload.get("id"),
          dutycalls_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.dutycalls.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          dutycalls_payload.get("external_reference"),
          dutycalls_payload.get("reference"),
          reference,
          existing.dutycalls.external_reference,
        ),
        alert_status=dutycalls_status,
        priority=self._first_non_empty_string(
          dutycalls_payload.get("priority"),
          dutycalls_payload.get("severity"),
          dutycalls_payload.get("urgency"),
          existing.dutycalls.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          dutycalls_payload.get("escalation_policy"),
          dutycalls_payload.get("escalationPolicy"),
          dutycalls_payload.get("policy"),
          dutycalls_payload.get("source"),
          existing.dutycalls.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          dutycalls_payload.get("assignee"),
          dutycalls_payload.get("owner"),
          dutycalls_payload.get("assigned_to"),
          existing.dutycalls.assignee,
        ),
        url=self._first_non_empty_string(
          dutycalls_payload.get("url"),
          dutycalls_payload.get("html_url"),
          dutycalls_payload.get("link"),
          existing.dutycalls.url,
        ),
        updated_at=(
          self._parse_payload_datetime(dutycalls_payload.get("updated_at"))
          or existing.dutycalls.updated_at
        ),
        phase_graph=self._build_dutycalls_recovery_phase_graph(
          payload=dutycalls_payload,
          alert_status=dutycalls_status,
          priority=self._first_non_empty_string(
            dutycalls_payload.get("priority"),
            dutycalls_payload.get("severity"),
            dutycalls_payload.get("urgency"),
            existing.dutycalls.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            dutycalls_payload.get("escalation_policy"),
            dutycalls_payload.get("escalationPolicy"),
            dutycalls_payload.get("policy"),
            dutycalls_payload.get("source"),
            existing.dutycalls.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            dutycalls_payload.get("assignee"),
            dutycalls_payload.get("owner"),
            dutycalls_payload.get("assigned_to"),
            existing.dutycalls.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.dutycalls,
        ),
      )
      provider_schema_kind = "dutycalls"
    incidenthub_schema = existing.incidenthub
    incidenthub_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("incidenthub"),
      payload.get("incidenthub"),
      payload.get("incidenthub_alert"),
    )
    if normalized_provider == "incidenthub" or incidenthub_payload:
      incidenthub_status = self._first_non_empty_string(
        incidenthub_payload.get("alert_status"),
        incidenthub_payload.get("status"),
        incidenthub_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.incidenthub.alert_status,
      ) or "unknown"
      incidenthub_schema = OperatorIncidentIncidentHubRecoveryState(
        alert_id=self._first_non_empty_string(
          incidenthub_payload.get("alert_id"),
          incidenthub_payload.get("id"),
          incidenthub_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.incidenthub.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          incidenthub_payload.get("external_reference"),
          incidenthub_payload.get("reference"),
          reference,
          existing.incidenthub.external_reference,
        ),
        alert_status=incidenthub_status,
        priority=self._first_non_empty_string(
          incidenthub_payload.get("priority"),
          incidenthub_payload.get("severity"),
          incidenthub_payload.get("urgency"),
          existing.incidenthub.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          incidenthub_payload.get("escalation_policy"),
          incidenthub_payload.get("escalationPolicy"),
          incidenthub_payload.get("policy"),
          incidenthub_payload.get("source"),
          existing.incidenthub.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          incidenthub_payload.get("assignee"),
          incidenthub_payload.get("owner"),
          incidenthub_payload.get("assigned_to"),
          existing.incidenthub.assignee,
        ),
        url=self._first_non_empty_string(
          incidenthub_payload.get("url"),
          incidenthub_payload.get("html_url"),
          incidenthub_payload.get("link"),
          existing.incidenthub.url,
        ),
        updated_at=(
          self._parse_payload_datetime(incidenthub_payload.get("updated_at"))
          or existing.incidenthub.updated_at
        ),
        phase_graph=self._build_incidenthub_recovery_phase_graph(
          payload=incidenthub_payload,
          alert_status=incidenthub_status,
          priority=self._first_non_empty_string(
            incidenthub_payload.get("priority"),
            incidenthub_payload.get("severity"),
            incidenthub_payload.get("urgency"),
            existing.incidenthub.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            incidenthub_payload.get("escalation_policy"),
            incidenthub_payload.get("escalationPolicy"),
            incidenthub_payload.get("policy"),
            incidenthub_payload.get("source"),
            existing.incidenthub.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            incidenthub_payload.get("assignee"),
            incidenthub_payload.get("owner"),
            incidenthub_payload.get("assigned_to"),
            existing.incidenthub.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.incidenthub,
        ),
      )
      provider_schema_kind = "incidenthub"
    resolver_schema = existing.resolver
    resolver_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("resolver"),
      payload.get("resolver"),
      payload.get("resolver_alert"),
    )
    if normalized_provider == "resolver" or resolver_payload:
      resolver_status = self._first_non_empty_string(
        resolver_payload.get("alert_status"),
        resolver_payload.get("status"),
        resolver_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.resolver.alert_status,
      ) or "unknown"
      resolver_schema = OperatorIncidentResolverRecoveryState(
        alert_id=self._first_non_empty_string(
          resolver_payload.get("alert_id"),
          resolver_payload.get("id"),
          resolver_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.resolver.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          resolver_payload.get("external_reference"),
          resolver_payload.get("reference"),
          reference,
          existing.resolver.external_reference,
        ),
        alert_status=resolver_status,
        priority=self._first_non_empty_string(
          resolver_payload.get("priority"),
          resolver_payload.get("severity"),
          resolver_payload.get("urgency"),
          existing.resolver.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          resolver_payload.get("escalation_policy"),
          resolver_payload.get("escalationPolicy"),
          resolver_payload.get("policy"),
          resolver_payload.get("source"),
          existing.resolver.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          resolver_payload.get("assignee"),
          resolver_payload.get("owner"),
          resolver_payload.get("assigned_to"),
          existing.resolver.assignee,
        ),
        url=self._first_non_empty_string(
          resolver_payload.get("url"),
          resolver_payload.get("html_url"),
          resolver_payload.get("link"),
          existing.resolver.url,
        ),
        updated_at=(
          self._parse_payload_datetime(resolver_payload.get("updated_at"))
          or existing.resolver.updated_at
        ),
        phase_graph=self._build_resolver_recovery_phase_graph(
          payload=resolver_payload,
          alert_status=resolver_status,
          priority=self._first_non_empty_string(
            resolver_payload.get("priority"),
            resolver_payload.get("severity"),
            resolver_payload.get("urgency"),
            existing.resolver.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            resolver_payload.get("escalation_policy"),
            resolver_payload.get("escalationPolicy"),
            resolver_payload.get("policy"),
            resolver_payload.get("source"),
            existing.resolver.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            resolver_payload.get("assignee"),
            resolver_payload.get("owner"),
            resolver_payload.get("assigned_to"),
            existing.resolver.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.resolver,
        ),
      )
      provider_schema_kind = "resolver"
    openduty_schema = existing.openduty
    openduty_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("openduty"),
      payload.get("openduty"),
      payload.get("openduty_alert"),
    )
    if normalized_provider == "openduty" or openduty_payload:
      openduty_status = self._first_non_empty_string(
        openduty_payload.get("alert_status"),
        openduty_payload.get("status"),
        openduty_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.openduty.alert_status,
      ) or "unknown"
      openduty_schema = OperatorIncidentOpenDutyRecoveryState(
        alert_id=self._first_non_empty_string(
          openduty_payload.get("alert_id"),
          openduty_payload.get("id"),
          openduty_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.openduty.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          openduty_payload.get("external_reference"),
          openduty_payload.get("reference"),
          reference,
          existing.openduty.external_reference,
        ),
        alert_status=openduty_status,
        priority=self._first_non_empty_string(
          openduty_payload.get("priority"),
          openduty_payload.get("severity"),
          openduty_payload.get("urgency"),
          existing.openduty.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          openduty_payload.get("escalation_policy"),
          openduty_payload.get("escalationPolicy"),
          openduty_payload.get("policy"),
          openduty_payload.get("source"),
          existing.openduty.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          openduty_payload.get("assignee"),
          openduty_payload.get("owner"),
          openduty_payload.get("assigned_to"),
          existing.openduty.assignee,
        ),
        url=self._first_non_empty_string(
          openduty_payload.get("url"),
          openduty_payload.get("html_url"),
          openduty_payload.get("link"),
          existing.openduty.url,
        ),
        updated_at=(
          self._parse_payload_datetime(openduty_payload.get("updated_at"))
          or existing.openduty.updated_at
        ),
        phase_graph=self._build_openduty_recovery_phase_graph(
          payload=openduty_payload,
          alert_status=openduty_status,
          priority=self._first_non_empty_string(
            openduty_payload.get("priority"),
            openduty_payload.get("severity"),
            openduty_payload.get("urgency"),
            existing.openduty.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            openduty_payload.get("escalation_policy"),
            openduty_payload.get("escalationPolicy"),
            openduty_payload.get("policy"),
            openduty_payload.get("source"),
            existing.openduty.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            openduty_payload.get("assignee"),
            openduty_payload.get("owner"),
            openduty_payload.get("assigned_to"),
            existing.openduty.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.openduty,
        ),
      )
      provider_schema_kind = "openduty"
    cabot_schema = existing.cabot
    cabot_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("cabot"),
      payload.get("cabot"),
      payload.get("cabot_alert"),
    )
    if normalized_provider == "cabot" or cabot_payload:
      cabot_status = self._first_non_empty_string(
        cabot_payload.get("alert_status"),
        cabot_payload.get("status"),
        cabot_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.cabot.alert_status,
      ) or "unknown"
      cabot_schema = OperatorIncidentCabotRecoveryState(
        alert_id=self._first_non_empty_string(
          cabot_payload.get("alert_id"),
          cabot_payload.get("id"),
          cabot_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.cabot.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          cabot_payload.get("external_reference"),
          cabot_payload.get("reference"),
          reference,
          existing.cabot.external_reference,
        ),
        alert_status=cabot_status,
        priority=self._first_non_empty_string(
          cabot_payload.get("priority"),
          cabot_payload.get("severity"),
          cabot_payload.get("urgency"),
          existing.cabot.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          cabot_payload.get("escalation_policy"),
          cabot_payload.get("escalationPolicy"),
          cabot_payload.get("policy"),
          cabot_payload.get("source"),
          existing.cabot.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          cabot_payload.get("assignee"),
          cabot_payload.get("owner"),
          cabot_payload.get("assigned_to"),
          existing.cabot.assignee,
        ),
        url=self._first_non_empty_string(
          cabot_payload.get("url"),
          cabot_payload.get("html_url"),
          cabot_payload.get("link"),
          existing.cabot.url,
        ),
        updated_at=(
          self._parse_payload_datetime(cabot_payload.get("updated_at"))
          or existing.cabot.updated_at
        ),
        phase_graph=self._build_cabot_recovery_phase_graph(
          payload=cabot_payload,
          alert_status=cabot_status,
          priority=self._first_non_empty_string(
            cabot_payload.get("priority"),
            cabot_payload.get("severity"),
            cabot_payload.get("urgency"),
            existing.cabot.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            cabot_payload.get("escalation_policy"),
            cabot_payload.get("escalationPolicy"),
            cabot_payload.get("policy"),
            cabot_payload.get("source"),
            existing.cabot.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            cabot_payload.get("assignee"),
            cabot_payload.get("owner"),
            cabot_payload.get("assigned_to"),
            existing.cabot.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.cabot,
        ),
      )
      provider_schema_kind = "cabot"
    haloitsm_schema = existing.haloitsm
    haloitsm_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("haloitsm"),
      payload.get("haloitsm"),
      payload.get("haloitsm_alert"),
    )
    if normalized_provider == "haloitsm" or haloitsm_payload:
      haloitsm_status = self._first_non_empty_string(
        haloitsm_payload.get("alert_status"),
        haloitsm_payload.get("status"),
        haloitsm_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.haloitsm.alert_status,
      ) or "unknown"
      haloitsm_schema = OperatorIncidentHaloItsmRecoveryState(
        alert_id=self._first_non_empty_string(
          haloitsm_payload.get("alert_id"),
          haloitsm_payload.get("id"),
          haloitsm_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.haloitsm.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          haloitsm_payload.get("external_reference"),
          haloitsm_payload.get("reference"),
          reference,
          existing.haloitsm.external_reference,
        ),
        alert_status=haloitsm_status,
        priority=self._first_non_empty_string(
          haloitsm_payload.get("priority"),
          haloitsm_payload.get("severity"),
          haloitsm_payload.get("urgency"),
          existing.haloitsm.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          haloitsm_payload.get("escalation_policy"),
          haloitsm_payload.get("escalationPolicy"),
          haloitsm_payload.get("policy"),
          haloitsm_payload.get("source"),
          existing.haloitsm.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          haloitsm_payload.get("assignee"),
          haloitsm_payload.get("owner"),
          haloitsm_payload.get("assigned_to"),
          existing.haloitsm.assignee,
        ),
        url=self._first_non_empty_string(
          haloitsm_payload.get("url"),
          haloitsm_payload.get("html_url"),
          haloitsm_payload.get("link"),
          existing.haloitsm.url,
        ),
        updated_at=(
          self._parse_payload_datetime(haloitsm_payload.get("updated_at"))
          or existing.haloitsm.updated_at
        ),
        phase_graph=self._build_haloitsm_recovery_phase_graph(
          payload=haloitsm_payload,
          alert_status=haloitsm_status,
          priority=self._first_non_empty_string(
            haloitsm_payload.get("priority"),
            haloitsm_payload.get("severity"),
            haloitsm_payload.get("urgency"),
            existing.haloitsm.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            haloitsm_payload.get("escalation_policy"),
            haloitsm_payload.get("escalationPolicy"),
            haloitsm_payload.get("policy"),
            haloitsm_payload.get("source"),
            existing.haloitsm.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            haloitsm_payload.get("assignee"),
            haloitsm_payload.get("owner"),
            haloitsm_payload.get("assigned_to"),
            existing.haloitsm.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.haloitsm,
        ),
      )
      provider_schema_kind = "haloitsm"
    incidentmanagerio_schema = existing.incidentmanagerio
    incidentmanagerio_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("incidentmanagerio"),
      payload.get("incidentmanagerio"),
      payload.get("incidentmanagerio_alert"),
    )
    if normalized_provider == "incidentmanagerio" or incidentmanagerio_payload:
      incidentmanagerio_status = self._first_non_empty_string(
        incidentmanagerio_payload.get("alert_status"),
        incidentmanagerio_payload.get("status"),
        incidentmanagerio_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.incidentmanagerio.alert_status,
      ) or "unknown"
      incidentmanagerio_schema = OperatorIncidentIncidentManagerIoRecoveryState(
        alert_id=self._first_non_empty_string(
          incidentmanagerio_payload.get("alert_id"),
          incidentmanagerio_payload.get("id"),
          incidentmanagerio_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.incidentmanagerio.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          incidentmanagerio_payload.get("external_reference"),
          incidentmanagerio_payload.get("reference"),
          reference,
          existing.incidentmanagerio.external_reference,
        ),
        alert_status=incidentmanagerio_status,
        priority=self._first_non_empty_string(
          incidentmanagerio_payload.get("priority"),
          incidentmanagerio_payload.get("severity"),
          incidentmanagerio_payload.get("urgency"),
          existing.incidentmanagerio.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          incidentmanagerio_payload.get("escalation_policy"),
          incidentmanagerio_payload.get("escalationPolicy"),
          incidentmanagerio_payload.get("policy"),
          incidentmanagerio_payload.get("source"),
          existing.incidentmanagerio.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          incidentmanagerio_payload.get("assignee"),
          incidentmanagerio_payload.get("owner"),
          incidentmanagerio_payload.get("assigned_to"),
          existing.incidentmanagerio.assignee,
        ),
        url=self._first_non_empty_string(
          incidentmanagerio_payload.get("url"),
          incidentmanagerio_payload.get("html_url"),
          incidentmanagerio_payload.get("link"),
          existing.incidentmanagerio.url,
        ),
        updated_at=(
          self._parse_payload_datetime(incidentmanagerio_payload.get("updated_at"))
          or existing.incidentmanagerio.updated_at
        ),
        phase_graph=self._build_incidentmanagerio_recovery_phase_graph(
          payload=incidentmanagerio_payload,
          alert_status=incidentmanagerio_status,
          priority=self._first_non_empty_string(
            incidentmanagerio_payload.get("priority"),
            incidentmanagerio_payload.get("severity"),
            incidentmanagerio_payload.get("urgency"),
            existing.incidentmanagerio.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            incidentmanagerio_payload.get("escalation_policy"),
            incidentmanagerio_payload.get("escalationPolicy"),
            incidentmanagerio_payload.get("policy"),
            incidentmanagerio_payload.get("source"),
            existing.incidentmanagerio.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            incidentmanagerio_payload.get("assignee"),
            incidentmanagerio_payload.get("owner"),
            incidentmanagerio_payload.get("assigned_to"),
            existing.incidentmanagerio.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.incidentmanagerio,
        ),
      )
      provider_schema_kind = "incidentmanagerio"
    oneuptime_schema = existing.oneuptime
    oneuptime_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("oneuptime"),
      payload.get("oneuptime"),
      payload.get("oneuptime_alert"),
    )
    if normalized_provider == "oneuptime" or oneuptime_payload:
      oneuptime_status = self._first_non_empty_string(
        oneuptime_payload.get("alert_status"),
        oneuptime_payload.get("status"),
        oneuptime_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.oneuptime.alert_status,
      ) or "unknown"
      oneuptime_schema = OperatorIncidentOneUptimeRecoveryState(
        alert_id=self._first_non_empty_string(
          oneuptime_payload.get("alert_id"),
          oneuptime_payload.get("id"),
          oneuptime_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.oneuptime.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          oneuptime_payload.get("external_reference"),
          oneuptime_payload.get("reference"),
          reference,
          existing.oneuptime.external_reference,
        ),
        alert_status=oneuptime_status,
        priority=self._first_non_empty_string(
          oneuptime_payload.get("priority"),
          oneuptime_payload.get("severity"),
          oneuptime_payload.get("urgency"),
          existing.oneuptime.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          oneuptime_payload.get("escalation_policy"),
          oneuptime_payload.get("escalationPolicy"),
          oneuptime_payload.get("policy"),
          oneuptime_payload.get("source"),
          existing.oneuptime.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          oneuptime_payload.get("assignee"),
          oneuptime_payload.get("owner"),
          oneuptime_payload.get("assigned_to"),
          existing.oneuptime.assignee,
        ),
        url=self._first_non_empty_string(
          oneuptime_payload.get("url"),
          oneuptime_payload.get("html_url"),
          oneuptime_payload.get("link"),
          existing.oneuptime.url,
        ),
        updated_at=(
          self._parse_payload_datetime(oneuptime_payload.get("updated_at"))
          or existing.oneuptime.updated_at
        ),
        phase_graph=self._build_oneuptime_recovery_phase_graph(
          payload=oneuptime_payload,
          alert_status=oneuptime_status,
          priority=self._first_non_empty_string(
            oneuptime_payload.get("priority"),
            oneuptime_payload.get("severity"),
            oneuptime_payload.get("urgency"),
            existing.oneuptime.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            oneuptime_payload.get("escalation_policy"),
            oneuptime_payload.get("escalationPolicy"),
            oneuptime_payload.get("policy"),
            oneuptime_payload.get("source"),
            existing.oneuptime.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            oneuptime_payload.get("assignee"),
            oneuptime_payload.get("owner"),
            oneuptime_payload.get("assigned_to"),
            existing.oneuptime.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.oneuptime,
        ),
      )
      provider_schema_kind = "oneuptime"
    squzy_schema = existing.squzy
    squzy_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("squzy"),
      payload.get("squzy"),
      payload.get("squzy_alert"),
    )
    if normalized_provider == "squzy" or squzy_payload:
      squzy_status = self._first_non_empty_string(
        squzy_payload.get("alert_status"),
        squzy_payload.get("status"),
        squzy_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.squzy.alert_status,
      ) or "unknown"
      squzy_schema = OperatorIncidentSquzyRecoveryState(
        alert_id=self._first_non_empty_string(
          squzy_payload.get("alert_id"),
          squzy_payload.get("id"),
          squzy_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.squzy.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          squzy_payload.get("external_reference"),
          squzy_payload.get("reference"),
          reference,
          existing.squzy.external_reference,
        ),
        alert_status=squzy_status,
        priority=self._first_non_empty_string(
          squzy_payload.get("priority"),
          squzy_payload.get("severity"),
          squzy_payload.get("urgency"),
          existing.squzy.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          squzy_payload.get("escalation_policy"),
          squzy_payload.get("escalationPolicy"),
          squzy_payload.get("policy"),
          squzy_payload.get("source"),
          existing.squzy.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          squzy_payload.get("assignee"),
          squzy_payload.get("owner"),
          squzy_payload.get("assigned_to"),
          existing.squzy.assignee,
        ),
        url=self._first_non_empty_string(
          squzy_payload.get("url"),
          squzy_payload.get("html_url"),
          squzy_payload.get("link"),
          existing.squzy.url,
        ),
        updated_at=(
          self._parse_payload_datetime(squzy_payload.get("updated_at"))
          or existing.squzy.updated_at
        ),
        phase_graph=self._build_squzy_recovery_phase_graph(
          payload=squzy_payload,
          alert_status=squzy_status,
          priority=self._first_non_empty_string(
            squzy_payload.get("priority"),
            squzy_payload.get("severity"),
            squzy_payload.get("urgency"),
            existing.squzy.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            squzy_payload.get("escalation_policy"),
            squzy_payload.get("escalationPolicy"),
            squzy_payload.get("policy"),
            squzy_payload.get("source"),
            existing.squzy.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            squzy_payload.get("assignee"),
            squzy_payload.get("owner"),
            squzy_payload.get("assigned_to"),
            existing.squzy.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.squzy,
        ),
      )
      provider_schema_kind = "squzy"
    crisescontrol_schema = existing.crisescontrol
    crisescontrol_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("crisescontrol"),
      payload.get("crisescontrol"),
      payload.get("crisescontrol_alert"),
    )
    if normalized_provider == "crisescontrol" or crisescontrol_payload:
      crisescontrol_status = self._first_non_empty_string(
        crisescontrol_payload.get("alert_status"),
        crisescontrol_payload.get("status"),
        crisescontrol_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.crisescontrol.alert_status,
      ) or "unknown"
      crisescontrol_schema = OperatorIncidentCrisesControlRecoveryState(
        alert_id=self._first_non_empty_string(
          crisescontrol_payload.get("alert_id"),
          crisescontrol_payload.get("id"),
          crisescontrol_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.crisescontrol.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          crisescontrol_payload.get("external_reference"),
          crisescontrol_payload.get("reference"),
          reference,
          existing.crisescontrol.external_reference,
        ),
        alert_status=crisescontrol_status,
        priority=self._first_non_empty_string(
          crisescontrol_payload.get("priority"),
          crisescontrol_payload.get("severity"),
          crisescontrol_payload.get("urgency"),
          existing.crisescontrol.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          crisescontrol_payload.get("escalation_policy"),
          crisescontrol_payload.get("escalationPolicy"),
          crisescontrol_payload.get("policy"),
          crisescontrol_payload.get("source"),
          existing.crisescontrol.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          crisescontrol_payload.get("assignee"),
          crisescontrol_payload.get("owner"),
          crisescontrol_payload.get("assigned_to"),
          existing.crisescontrol.assignee,
        ),
        url=self._first_non_empty_string(
          crisescontrol_payload.get("url"),
          crisescontrol_payload.get("html_url"),
          crisescontrol_payload.get("link"),
          existing.crisescontrol.url,
        ),
        updated_at=(
          self._parse_payload_datetime(crisescontrol_payload.get("updated_at"))
          or existing.crisescontrol.updated_at
        ),
        phase_graph=self._build_crisescontrol_recovery_phase_graph(
          payload=crisescontrol_payload,
          alert_status=crisescontrol_status,
          priority=self._first_non_empty_string(
            crisescontrol_payload.get("priority"),
            crisescontrol_payload.get("severity"),
            crisescontrol_payload.get("urgency"),
            existing.crisescontrol.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            crisescontrol_payload.get("escalation_policy"),
            crisescontrol_payload.get("escalationPolicy"),
            crisescontrol_payload.get("policy"),
            crisescontrol_payload.get("source"),
            existing.crisescontrol.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            crisescontrol_payload.get("assignee"),
            crisescontrol_payload.get("owner"),
            crisescontrol_payload.get("assigned_to"),
            existing.crisescontrol.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.crisescontrol,
        ),
      )
      provider_schema_kind = "crisescontrol"
    freshservice_schema = existing.freshservice
    freshservice_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("freshservice"),
      payload.get("freshservice"),
      payload.get("freshservice_alert"),
    )
    if normalized_provider == "freshservice" or freshservice_payload:
      freshservice_status = self._first_non_empty_string(
        freshservice_payload.get("alert_status"),
        freshservice_payload.get("status"),
        freshservice_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.freshservice.alert_status,
      ) or "unknown"
      freshservice_schema = OperatorIncidentFreshserviceRecoveryState(
        alert_id=self._first_non_empty_string(
          freshservice_payload.get("alert_id"),
          freshservice_payload.get("id"),
          freshservice_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.freshservice.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          freshservice_payload.get("external_reference"),
          freshservice_payload.get("reference"),
          reference,
          existing.freshservice.external_reference,
        ),
        alert_status=freshservice_status,
        priority=self._first_non_empty_string(
          freshservice_payload.get("priority"),
          freshservice_payload.get("severity"),
          freshservice_payload.get("urgency"),
          existing.freshservice.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          freshservice_payload.get("escalation_policy"),
          freshservice_payload.get("escalationPolicy"),
          freshservice_payload.get("policy"),
          freshservice_payload.get("source"),
          existing.freshservice.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          freshservice_payload.get("assignee"),
          freshservice_payload.get("owner"),
          freshservice_payload.get("assigned_to"),
          existing.freshservice.assignee,
        ),
        url=self._first_non_empty_string(
          freshservice_payload.get("url"),
          freshservice_payload.get("html_url"),
          freshservice_payload.get("link"),
          existing.freshservice.url,
        ),
        updated_at=(
          self._parse_payload_datetime(freshservice_payload.get("updated_at"))
          or existing.freshservice.updated_at
        ),
        phase_graph=self._build_freshservice_recovery_phase_graph(
          payload=freshservice_payload,
          alert_status=freshservice_status,
          priority=self._first_non_empty_string(
            freshservice_payload.get("priority"),
            freshservice_payload.get("severity"),
            freshservice_payload.get("urgency"),
            existing.freshservice.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            freshservice_payload.get("escalation_policy"),
            freshservice_payload.get("escalationPolicy"),
            freshservice_payload.get("policy"),
            freshservice_payload.get("source"),
            existing.freshservice.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            freshservice_payload.get("assignee"),
            freshservice_payload.get("owner"),
            freshservice_payload.get("assigned_to"),
            existing.freshservice.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.freshservice,
        ),
      )
      provider_schema_kind = "freshservice"
    freshdesk_schema = existing.freshdesk
    freshdesk_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("freshdesk"),
      payload.get("freshdesk"),
      payload.get("freshdesk_alert"),
    )
    if normalized_provider == "freshdesk" or freshdesk_payload:
      freshdesk_status = self._first_non_empty_string(
        freshdesk_payload.get("alert_status"),
        freshdesk_payload.get("status"),
        freshdesk_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.freshdesk.alert_status,
      ) or "unknown"
      freshdesk_schema = OperatorIncidentFreshdeskRecoveryState(
        alert_id=self._first_non_empty_string(
          freshdesk_payload.get("alert_id"),
          freshdesk_payload.get("id"),
          freshdesk_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.freshdesk.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          freshdesk_payload.get("external_reference"),
          freshdesk_payload.get("reference"),
          reference,
          existing.freshdesk.external_reference,
        ),
        alert_status=freshdesk_status,
        priority=self._first_non_empty_string(
          freshdesk_payload.get("priority"),
          freshdesk_payload.get("severity"),
          freshdesk_payload.get("urgency"),
          existing.freshdesk.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          freshdesk_payload.get("escalation_policy"),
          freshdesk_payload.get("escalationPolicy"),
          freshdesk_payload.get("policy"),
          freshdesk_payload.get("source"),
          existing.freshdesk.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          freshdesk_payload.get("assignee"),
          freshdesk_payload.get("owner"),
          freshdesk_payload.get("assigned_to"),
          existing.freshdesk.assignee,
        ),
        url=self._first_non_empty_string(
          freshdesk_payload.get("url"),
          freshdesk_payload.get("html_url"),
          freshdesk_payload.get("link"),
          existing.freshdesk.url,
        ),
        updated_at=(
          self._parse_payload_datetime(freshdesk_payload.get("updated_at"))
          or existing.freshdesk.updated_at
        ),
        phase_graph=self._build_freshdesk_recovery_phase_graph(
          payload=freshdesk_payload,
          alert_status=freshdesk_status,
          priority=self._first_non_empty_string(
            freshdesk_payload.get("priority"),
            freshdesk_payload.get("severity"),
            freshdesk_payload.get("urgency"),
            existing.freshdesk.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            freshdesk_payload.get("escalation_policy"),
            freshdesk_payload.get("escalationPolicy"),
            freshdesk_payload.get("policy"),
            freshdesk_payload.get("source"),
            existing.freshdesk.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            freshdesk_payload.get("assignee"),
            freshdesk_payload.get("owner"),
            freshdesk_payload.get("assigned_to"),
            existing.freshdesk.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.freshdesk,
        ),
      )
      provider_schema_kind = "freshdesk"
    happyfox_schema = existing.happyfox
    happyfox_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("happyfox"),
      payload.get("happyfox"),
      payload.get("happyfox_alert"),
      payload.get("happyfox_ticket"),
    )
    if normalized_provider == "happyfox" or happyfox_payload:
      happyfox_status = self._first_non_empty_string(
        happyfox_payload.get("alert_status"),
        happyfox_payload.get("status"),
        happyfox_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.happyfox.alert_status,
      ) or "unknown"
      happyfox_schema = OperatorIncidentHappyfoxRecoveryState(
        alert_id=self._first_non_empty_string(
          happyfox_payload.get("alert_id"),
          happyfox_payload.get("id"),
          happyfox_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.happyfox.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          happyfox_payload.get("external_reference"),
          happyfox_payload.get("reference"),
          reference,
          existing.happyfox.external_reference,
        ),
        alert_status=happyfox_status,
        priority=self._first_non_empty_string(
          happyfox_payload.get("priority"),
          happyfox_payload.get("severity"),
          happyfox_payload.get("urgency"),
          existing.happyfox.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          happyfox_payload.get("escalation_policy"),
          happyfox_payload.get("escalationPolicy"),
          happyfox_payload.get("policy"),
          happyfox_payload.get("source"),
          existing.happyfox.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          happyfox_payload.get("assignee"),
          happyfox_payload.get("owner"),
          happyfox_payload.get("assigned_to"),
          existing.happyfox.assignee,
        ),
        url=self._first_non_empty_string(
          happyfox_payload.get("url"),
          happyfox_payload.get("html_url"),
          happyfox_payload.get("link"),
          existing.happyfox.url,
        ),
        updated_at=(
          self._parse_payload_datetime(happyfox_payload.get("updated_at"))
          or existing.happyfox.updated_at
        ),
        phase_graph=self._build_happyfox_recovery_phase_graph(
          payload=happyfox_payload,
          alert_status=happyfox_status,
          priority=self._first_non_empty_string(
            happyfox_payload.get("priority"),
            happyfox_payload.get("severity"),
            happyfox_payload.get("urgency"),
            existing.happyfox.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            happyfox_payload.get("escalation_policy"),
            happyfox_payload.get("escalationPolicy"),
            happyfox_payload.get("policy"),
            happyfox_payload.get("source"),
            existing.happyfox.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            happyfox_payload.get("assignee"),
            happyfox_payload.get("owner"),
            happyfox_payload.get("assigned_to"),
            existing.happyfox.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.happyfox,
        ),
      )
      provider_schema_kind = "happyfox"
    zendesk_schema = existing.zendesk
    zendesk_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("zendesk"),
      payload.get("zendesk"),
      payload.get("zendesk_alert"),
      payload.get("zendesk_ticket"),
    )
    if normalized_provider == "zendesk" or zendesk_payload:
      zendesk_status = self._first_non_empty_string(
        zendesk_payload.get("alert_status"),
        zendesk_payload.get("status"),
        zendesk_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.zendesk.alert_status,
      ) or "unknown"
      zendesk_schema = OperatorIncidentZendeskRecoveryState(
        alert_id=self._first_non_empty_string(
          zendesk_payload.get("alert_id"),
          zendesk_payload.get("id"),
          zendesk_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.zendesk.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          zendesk_payload.get("external_reference"),
          zendesk_payload.get("reference"),
          reference,
          existing.zendesk.external_reference,
        ),
        alert_status=zendesk_status,
        priority=self._first_non_empty_string(
          zendesk_payload.get("priority"),
          zendesk_payload.get("severity"),
          zendesk_payload.get("urgency"),
          existing.zendesk.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          zendesk_payload.get("escalation_policy"),
          zendesk_payload.get("escalationPolicy"),
          zendesk_payload.get("policy"),
          zendesk_payload.get("source"),
          existing.zendesk.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          zendesk_payload.get("assignee"),
          zendesk_payload.get("owner"),
          zendesk_payload.get("assigned_to"),
          existing.zendesk.assignee,
        ),
        url=self._first_non_empty_string(
          zendesk_payload.get("url"),
          zendesk_payload.get("html_url"),
          zendesk_payload.get("link"),
          existing.zendesk.url,
        ),
        updated_at=(
          self._parse_payload_datetime(zendesk_payload.get("updated_at"))
          or existing.zendesk.updated_at
        ),
        phase_graph=self._build_zendesk_recovery_phase_graph(
          payload=zendesk_payload,
          alert_status=zendesk_status,
          priority=self._first_non_empty_string(
            zendesk_payload.get("priority"),
            zendesk_payload.get("severity"),
            zendesk_payload.get("urgency"),
            existing.zendesk.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            zendesk_payload.get("escalation_policy"),
            zendesk_payload.get("escalationPolicy"),
            zendesk_payload.get("policy"),
            zendesk_payload.get("source"),
            existing.zendesk.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            zendesk_payload.get("assignee"),
            zendesk_payload.get("owner"),
            zendesk_payload.get("assigned_to"),
            existing.zendesk.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.zendesk,
        ),
      )
      provider_schema_kind = "zendesk"
    zohodesk_schema = existing.zohodesk
    zohodesk_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("zohodesk"),
      payload.get("zohodesk"),
      payload.get("zohodesk_alert"),
      payload.get("zohodesk_ticket"),
    )
    if normalized_provider == "zohodesk" or zohodesk_payload:
      zohodesk_status = self._first_non_empty_string(
        zohodesk_payload.get("alert_status"),
        zohodesk_payload.get("status"),
        zohodesk_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.zohodesk.alert_status,
      ) or "unknown"
      zohodesk_schema = OperatorIncidentZohoDeskRecoveryState(
        alert_id=self._first_non_empty_string(
          zohodesk_payload.get("alert_id"),
          zohodesk_payload.get("id"),
          zohodesk_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.zohodesk.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          zohodesk_payload.get("external_reference"),
          zohodesk_payload.get("reference"),
          reference,
          existing.zohodesk.external_reference,
        ),
        alert_status=zohodesk_status,
        priority=self._first_non_empty_string(
          zohodesk_payload.get("priority"),
          zohodesk_payload.get("severity"),
          zohodesk_payload.get("urgency"),
          existing.zohodesk.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          zohodesk_payload.get("escalation_policy"),
          zohodesk_payload.get("escalationPolicy"),
          zohodesk_payload.get("policy"),
          zohodesk_payload.get("source"),
          existing.zohodesk.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          zohodesk_payload.get("assignee"),
          zohodesk_payload.get("owner"),
          zohodesk_payload.get("assigned_to"),
          existing.zohodesk.assignee,
        ),
        url=self._first_non_empty_string(
          zohodesk_payload.get("url"),
          zohodesk_payload.get("html_url"),
          zohodesk_payload.get("link"),
          existing.zohodesk.url,
        ),
        updated_at=(
          self._parse_payload_datetime(zohodesk_payload.get("updated_at"))
          or existing.zohodesk.updated_at
        ),
        phase_graph=self._build_zohodesk_recovery_phase_graph(
          payload=zohodesk_payload,
          alert_status=zohodesk_status,
          priority=self._first_non_empty_string(
            zohodesk_payload.get("priority"),
            zohodesk_payload.get("severity"),
            zohodesk_payload.get("urgency"),
            existing.zohodesk.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            zohodesk_payload.get("escalation_policy"),
            zohodesk_payload.get("escalationPolicy"),
            zohodesk_payload.get("policy"),
            zohodesk_payload.get("source"),
            existing.zohodesk.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            zohodesk_payload.get("assignee"),
            zohodesk_payload.get("owner"),
            zohodesk_payload.get("assigned_to"),
            existing.zohodesk.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.zohodesk,
        ),
      )
      provider_schema_kind = "zohodesk"
    helpscout_schema = existing.helpscout
    helpscout_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("helpscout"),
      payload.get("helpscout"),
      payload.get("helpscout_alert"),
      payload.get("helpscout_conversation"),
    )
    if normalized_provider == "helpscout" or helpscout_payload:
      helpscout_status = self._first_non_empty_string(
        helpscout_payload.get("alert_status"),
        helpscout_payload.get("status"),
        helpscout_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.helpscout.alert_status,
      ) or "unknown"
      helpscout_schema = OperatorIncidentHelpScoutRecoveryState(
        alert_id=self._first_non_empty_string(
          helpscout_payload.get("alert_id"),
          helpscout_payload.get("id"),
          helpscout_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.helpscout.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          helpscout_payload.get("external_reference"),
          helpscout_payload.get("reference"),
          reference,
          existing.helpscout.external_reference,
        ),
        alert_status=helpscout_status,
        priority=self._first_non_empty_string(
          helpscout_payload.get("priority"),
          helpscout_payload.get("severity"),
          helpscout_payload.get("urgency"),
          existing.helpscout.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          helpscout_payload.get("escalation_policy"),
          helpscout_payload.get("escalationPolicy"),
          helpscout_payload.get("policy"),
          helpscout_payload.get("source"),
          existing.helpscout.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          helpscout_payload.get("assignee"),
          helpscout_payload.get("owner"),
          helpscout_payload.get("assigned_to"),
          existing.helpscout.assignee,
        ),
        url=self._first_non_empty_string(
          helpscout_payload.get("url"),
          helpscout_payload.get("html_url"),
          helpscout_payload.get("link"),
          existing.helpscout.url,
        ),
        updated_at=(
          self._parse_payload_datetime(helpscout_payload.get("updated_at"))
          or existing.helpscout.updated_at
        ),
        phase_graph=self._build_helpscout_recovery_phase_graph(
          payload=helpscout_payload,
          alert_status=helpscout_status,
          priority=self._first_non_empty_string(
            helpscout_payload.get("priority"),
            helpscout_payload.get("severity"),
            helpscout_payload.get("urgency"),
            existing.helpscout.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            helpscout_payload.get("escalation_policy"),
            helpscout_payload.get("escalationPolicy"),
            helpscout_payload.get("policy"),
            helpscout_payload.get("source"),
            existing.helpscout.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            helpscout_payload.get("assignee"),
            helpscout_payload.get("owner"),
            helpscout_payload.get("assigned_to"),
            existing.helpscout.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.helpscout,
        ),
      )
      provider_schema_kind = "helpscout"
    kayako_schema = existing.kayako
    kayako_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("kayako"),
      payload.get("kayako"),
      payload.get("kayako_alert"),
      payload.get("kayako_case"),
    )
    if normalized_provider == "kayako" or kayako_payload:
      kayako_status = self._first_non_empty_string(
        kayako_payload.get("alert_status"),
        kayako_payload.get("status"),
        kayako_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.kayako.alert_status,
      ) or "unknown"
      kayako_schema = OperatorIncidentKayakoRecoveryState(
        alert_id=self._first_non_empty_string(
          kayako_payload.get("alert_id"),
          kayako_payload.get("id"),
          kayako_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.kayako.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          kayako_payload.get("external_reference"),
          kayako_payload.get("reference"),
          reference,
          existing.kayako.external_reference,
        ),
        alert_status=kayako_status,
        priority=self._first_non_empty_string(
          kayako_payload.get("priority"),
          kayako_payload.get("severity"),
          kayako_payload.get("urgency"),
          existing.kayako.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          kayako_payload.get("escalation_policy"),
          kayako_payload.get("escalationPolicy"),
          kayako_payload.get("policy"),
          kayako_payload.get("source"),
          existing.kayako.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          kayako_payload.get("assignee"),
          kayako_payload.get("owner"),
          kayako_payload.get("assigned_to"),
          existing.kayako.assignee,
        ),
        url=self._first_non_empty_string(
          kayako_payload.get("url"),
          kayako_payload.get("html_url"),
          kayako_payload.get("link"),
          existing.kayako.url,
        ),
        updated_at=(
          self._parse_payload_datetime(kayako_payload.get("updated_at"))
          or existing.kayako.updated_at
        ),
        phase_graph=self._build_kayako_recovery_phase_graph(
          payload=kayako_payload,
          alert_status=kayako_status,
          priority=self._first_non_empty_string(
            kayako_payload.get("priority"),
            kayako_payload.get("severity"),
            kayako_payload.get("urgency"),
            existing.kayako.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            kayako_payload.get("escalation_policy"),
            kayako_payload.get("escalationPolicy"),
            kayako_payload.get("policy"),
            kayako_payload.get("source"),
            existing.kayako.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            kayako_payload.get("assignee"),
            kayako_payload.get("owner"),
            kayako_payload.get("assigned_to"),
            existing.kayako.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.kayako,
        ),
      )
      provider_schema_kind = "kayako"
    intercom_schema = existing.intercom
    intercom_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("intercom"),
      payload.get("intercom"),
      payload.get("intercom_alert"),
      payload.get("intercom_conversation"),
    )
    if normalized_provider == "intercom" or intercom_payload:
      intercom_status = self._first_non_empty_string(
        intercom_payload.get("alert_status"),
        intercom_payload.get("status"),
        intercom_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.intercom.alert_status,
      ) or "unknown"
      intercom_schema = OperatorIncidentIntercomRecoveryState(
        alert_id=self._first_non_empty_string(
          intercom_payload.get("alert_id"),
          intercom_payload.get("id"),
          intercom_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.intercom.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          intercom_payload.get("external_reference"),
          intercom_payload.get("reference"),
          reference,
          existing.intercom.external_reference,
        ),
        alert_status=intercom_status,
        priority=self._first_non_empty_string(
          intercom_payload.get("priority"),
          intercom_payload.get("severity"),
          intercom_payload.get("urgency"),
          existing.intercom.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          intercom_payload.get("escalation_policy"),
          intercom_payload.get("escalationPolicy"),
          intercom_payload.get("policy"),
          intercom_payload.get("source"),
          existing.intercom.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          intercom_payload.get("assignee"),
          intercom_payload.get("owner"),
          intercom_payload.get("assigned_to"),
          existing.intercom.assignee,
        ),
        url=self._first_non_empty_string(
          intercom_payload.get("url"),
          intercom_payload.get("html_url"),
          intercom_payload.get("link"),
          existing.intercom.url,
        ),
        updated_at=(
          self._parse_payload_datetime(intercom_payload.get("updated_at"))
          or existing.intercom.updated_at
        ),
        phase_graph=self._build_intercom_recovery_phase_graph(
          payload=intercom_payload,
          alert_status=intercom_status,
          priority=self._first_non_empty_string(
            intercom_payload.get("priority"),
            intercom_payload.get("severity"),
            intercom_payload.get("urgency"),
            existing.intercom.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            intercom_payload.get("escalation_policy"),
            intercom_payload.get("escalationPolicy"),
            intercom_payload.get("policy"),
            intercom_payload.get("source"),
            existing.intercom.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            intercom_payload.get("assignee"),
            intercom_payload.get("owner"),
            intercom_payload.get("assigned_to"),
            existing.intercom.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.intercom,
        ),
      )
      provider_schema_kind = "intercom"
    front_schema = existing.front
    front_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("front"),
      payload.get("front"),
      payload.get("front_alert"),
      payload.get("front_conversation"),
    )
    if normalized_provider == "front" or front_payload:
      front_status = self._first_non_empty_string(
        front_payload.get("alert_status"),
        front_payload.get("status"),
        front_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.front.alert_status,
      ) or "unknown"
      front_schema = OperatorIncidentFrontRecoveryState(
        alert_id=self._first_non_empty_string(
          front_payload.get("alert_id"),
          front_payload.get("id"),
          front_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.front.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          front_payload.get("external_reference"),
          front_payload.get("reference"),
          reference,
          existing.front.external_reference,
        ),
        alert_status=front_status,
        priority=self._first_non_empty_string(
          front_payload.get("priority"),
          front_payload.get("severity"),
          front_payload.get("urgency"),
          existing.front.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          front_payload.get("escalation_policy"),
          front_payload.get("escalationPolicy"),
          front_payload.get("policy"),
          front_payload.get("source"),
          existing.front.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          front_payload.get("assignee"),
          front_payload.get("owner"),
          front_payload.get("assigned_to"),
          existing.front.assignee,
        ),
        url=self._first_non_empty_string(
          front_payload.get("url"),
          front_payload.get("html_url"),
          front_payload.get("link"),
          existing.front.url,
        ),
        updated_at=(
          self._parse_payload_datetime(front_payload.get("updated_at"))
          or existing.front.updated_at
        ),
        phase_graph=self._build_front_recovery_phase_graph(
          payload=front_payload,
          alert_status=front_status,
          priority=self._first_non_empty_string(
            front_payload.get("priority"),
            front_payload.get("severity"),
            front_payload.get("urgency"),
            existing.front.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            front_payload.get("escalation_policy"),
            front_payload.get("escalationPolicy"),
            front_payload.get("policy"),
            front_payload.get("source"),
            existing.front.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            front_payload.get("assignee"),
            front_payload.get("owner"),
            front_payload.get("assigned_to"),
            existing.front.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.front,
        ),
      )
      provider_schema_kind = "front"
    servicedeskplus_schema = existing.servicedeskplus
    servicedeskplus_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("servicedeskplus"),
      payload.get("servicedeskplus"),
      payload.get("servicedeskplus_alert"),
    )
    if normalized_provider == "servicedeskplus" or servicedeskplus_payload:
      servicedeskplus_status = self._first_non_empty_string(
        servicedeskplus_payload.get("alert_status"),
        servicedeskplus_payload.get("status"),
        servicedeskplus_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.servicedeskplus.alert_status,
      ) or "unknown"
      servicedeskplus_schema = OperatorIncidentServiceDeskPlusRecoveryState(
        alert_id=self._first_non_empty_string(
          servicedeskplus_payload.get("alert_id"),
          servicedeskplus_payload.get("id"),
          servicedeskplus_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.servicedeskplus.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          servicedeskplus_payload.get("external_reference"),
          servicedeskplus_payload.get("reference"),
          reference,
          existing.servicedeskplus.external_reference,
        ),
        alert_status=servicedeskplus_status,
        priority=self._first_non_empty_string(
          servicedeskplus_payload.get("priority"),
          servicedeskplus_payload.get("severity"),
          servicedeskplus_payload.get("urgency"),
          existing.servicedeskplus.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          servicedeskplus_payload.get("escalation_policy"),
          servicedeskplus_payload.get("escalationPolicy"),
          servicedeskplus_payload.get("policy"),
          servicedeskplus_payload.get("source"),
          existing.servicedeskplus.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          servicedeskplus_payload.get("assignee"),
          servicedeskplus_payload.get("owner"),
          servicedeskplus_payload.get("assigned_to"),
          existing.servicedeskplus.assignee,
        ),
        url=self._first_non_empty_string(
          servicedeskplus_payload.get("url"),
          servicedeskplus_payload.get("html_url"),
          servicedeskplus_payload.get("link"),
          existing.servicedeskplus.url,
        ),
        updated_at=(
          self._parse_payload_datetime(servicedeskplus_payload.get("updated_at"))
          or existing.servicedeskplus.updated_at
        ),
        phase_graph=self._build_servicedeskplus_recovery_phase_graph(
          payload=servicedeskplus_payload,
          alert_status=servicedeskplus_status,
          priority=self._first_non_empty_string(
            servicedeskplus_payload.get("priority"),
            servicedeskplus_payload.get("severity"),
            servicedeskplus_payload.get("urgency"),
            existing.servicedeskplus.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            servicedeskplus_payload.get("escalation_policy"),
            servicedeskplus_payload.get("escalationPolicy"),
            servicedeskplus_payload.get("policy"),
            servicedeskplus_payload.get("source"),
            existing.servicedeskplus.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            servicedeskplus_payload.get("assignee"),
            servicedeskplus_payload.get("owner"),
            servicedeskplus_payload.get("assigned_to"),
            existing.servicedeskplus.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.servicedeskplus,
        ),
      )
      provider_schema_kind = "servicedeskplus"
    sysaid_schema = existing.sysaid
    sysaid_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("sysaid"),
      payload.get("sysaid"),
      payload.get("sysaid_alert"),
    )
    if normalized_provider == "sysaid" or sysaid_payload:
      sysaid_status = self._first_non_empty_string(
        sysaid_payload.get("alert_status"),
        sysaid_payload.get("status"),
        sysaid_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.sysaid.alert_status,
      ) or "unknown"
      sysaid_schema = OperatorIncidentSysAidRecoveryState(
        alert_id=self._first_non_empty_string(
          sysaid_payload.get("alert_id"),
          sysaid_payload.get("id"),
          sysaid_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.sysaid.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          sysaid_payload.get("external_reference"),
          sysaid_payload.get("reference"),
          reference,
          existing.sysaid.external_reference,
        ),
        alert_status=sysaid_status,
        priority=self._first_non_empty_string(
          sysaid_payload.get("priority"),
          sysaid_payload.get("severity"),
          sysaid_payload.get("urgency"),
          existing.sysaid.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          sysaid_payload.get("escalation_policy"),
          sysaid_payload.get("escalationPolicy"),
          sysaid_payload.get("policy"),
          sysaid_payload.get("source"),
          existing.sysaid.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          sysaid_payload.get("assignee"),
          sysaid_payload.get("owner"),
          sysaid_payload.get("assigned_to"),
          existing.sysaid.assignee,
        ),
        url=self._first_non_empty_string(
          sysaid_payload.get("url"),
          sysaid_payload.get("html_url"),
          sysaid_payload.get("link"),
          existing.sysaid.url,
        ),
        updated_at=(
          self._parse_payload_datetime(sysaid_payload.get("updated_at"))
          or existing.sysaid.updated_at
        ),
        phase_graph=self._build_sysaid_recovery_phase_graph(
          payload=sysaid_payload,
          alert_status=sysaid_status,
          priority=self._first_non_empty_string(
            sysaid_payload.get("priority"),
            sysaid_payload.get("severity"),
            sysaid_payload.get("urgency"),
            existing.sysaid.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            sysaid_payload.get("escalation_policy"),
            sysaid_payload.get("escalationPolicy"),
            sysaid_payload.get("policy"),
            sysaid_payload.get("source"),
            existing.sysaid.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            sysaid_payload.get("assignee"),
            sysaid_payload.get("owner"),
            sysaid_payload.get("assigned_to"),
            existing.sysaid.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.sysaid,
        ),
      )
      provider_schema_kind = "sysaid"
    bmchelix_schema = existing.bmchelix
    bmchelix_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("bmchelix"),
      payload.get("bmchelix"),
      payload.get("bmchelix_alert"),
    )
    if normalized_provider == "bmchelix" or bmchelix_payload:
      bmchelix_status = self._first_non_empty_string(
        bmchelix_payload.get("alert_status"),
        bmchelix_payload.get("status"),
        bmchelix_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.bmchelix.alert_status,
      ) or "unknown"
      bmchelix_schema = OperatorIncidentBmcHelixRecoveryState(
        alert_id=self._first_non_empty_string(
          bmchelix_payload.get("alert_id"),
          bmchelix_payload.get("id"),
          bmchelix_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.bmchelix.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          bmchelix_payload.get("external_reference"),
          bmchelix_payload.get("reference"),
          reference,
          existing.bmchelix.external_reference,
        ),
        alert_status=bmchelix_status,
        priority=self._first_non_empty_string(
          bmchelix_payload.get("priority"),
          bmchelix_payload.get("severity"),
          bmchelix_payload.get("urgency"),
          existing.bmchelix.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          bmchelix_payload.get("escalation_policy"),
          bmchelix_payload.get("escalationPolicy"),
          bmchelix_payload.get("policy"),
          bmchelix_payload.get("source"),
          existing.bmchelix.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          bmchelix_payload.get("assignee"),
          bmchelix_payload.get("owner"),
          bmchelix_payload.get("assigned_to"),
          existing.bmchelix.assignee,
        ),
        url=self._first_non_empty_string(
          bmchelix_payload.get("url"),
          bmchelix_payload.get("html_url"),
          bmchelix_payload.get("link"),
          existing.bmchelix.url,
        ),
        updated_at=(
          self._parse_payload_datetime(bmchelix_payload.get("updated_at"))
          or existing.bmchelix.updated_at
        ),
        phase_graph=self._build_bmchelix_recovery_phase_graph(
          payload=bmchelix_payload,
          alert_status=bmchelix_status,
          priority=self._first_non_empty_string(
            bmchelix_payload.get("priority"),
            bmchelix_payload.get("severity"),
            bmchelix_payload.get("urgency"),
            existing.bmchelix.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            bmchelix_payload.get("escalation_policy"),
            bmchelix_payload.get("escalationPolicy"),
            bmchelix_payload.get("policy"),
            bmchelix_payload.get("source"),
            existing.bmchelix.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            bmchelix_payload.get("assignee"),
            bmchelix_payload.get("owner"),
            bmchelix_payload.get("assigned_to"),
            existing.bmchelix.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.bmchelix,
        ),
      )
      provider_schema_kind = "bmchelix"
    solarwindsservicedesk_schema = existing.solarwindsservicedesk
    solarwindsservicedesk_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("solarwindsservicedesk"),
      payload.get("solarwindsservicedesk"),
      payload.get("solarwindsservicedesk_alert"),
    )
    if normalized_provider == "solarwindsservicedesk" or solarwindsservicedesk_payload:
      solarwindsservicedesk_status = self._first_non_empty_string(
        solarwindsservicedesk_payload.get("alert_status"),
        solarwindsservicedesk_payload.get("status"),
        solarwindsservicedesk_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.solarwindsservicedesk.alert_status,
      ) or "unknown"
      solarwindsservicedesk_schema = OperatorIncidentSolarWindsServiceDeskRecoveryState(
        alert_id=self._first_non_empty_string(
          solarwindsservicedesk_payload.get("alert_id"),
          solarwindsservicedesk_payload.get("id"),
          solarwindsservicedesk_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.solarwindsservicedesk.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          solarwindsservicedesk_payload.get("external_reference"),
          solarwindsservicedesk_payload.get("reference"),
          reference,
          existing.solarwindsservicedesk.external_reference,
        ),
        alert_status=solarwindsservicedesk_status,
        priority=self._first_non_empty_string(
          solarwindsservicedesk_payload.get("priority"),
          solarwindsservicedesk_payload.get("severity"),
          solarwindsservicedesk_payload.get("urgency"),
          existing.solarwindsservicedesk.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          solarwindsservicedesk_payload.get("escalation_policy"),
          solarwindsservicedesk_payload.get("escalationPolicy"),
          solarwindsservicedesk_payload.get("policy"),
          solarwindsservicedesk_payload.get("source"),
          existing.solarwindsservicedesk.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          solarwindsservicedesk_payload.get("assignee"),
          solarwindsservicedesk_payload.get("owner"),
          solarwindsservicedesk_payload.get("assigned_to"),
          existing.solarwindsservicedesk.assignee,
        ),
        url=self._first_non_empty_string(
          solarwindsservicedesk_payload.get("url"),
          solarwindsservicedesk_payload.get("html_url"),
          solarwindsservicedesk_payload.get("link"),
          existing.solarwindsservicedesk.url,
        ),
        updated_at=(
          self._parse_payload_datetime(solarwindsservicedesk_payload.get("updated_at"))
          or existing.solarwindsservicedesk.updated_at
        ),
        phase_graph=self._build_solarwindsservicedesk_recovery_phase_graph(
          payload=solarwindsservicedesk_payload,
          alert_status=solarwindsservicedesk_status,
          priority=self._first_non_empty_string(
            solarwindsservicedesk_payload.get("priority"),
            solarwindsservicedesk_payload.get("severity"),
            solarwindsservicedesk_payload.get("urgency"),
            existing.solarwindsservicedesk.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            solarwindsservicedesk_payload.get("escalation_policy"),
            solarwindsservicedesk_payload.get("escalationPolicy"),
            solarwindsservicedesk_payload.get("policy"),
            solarwindsservicedesk_payload.get("source"),
            existing.solarwindsservicedesk.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            solarwindsservicedesk_payload.get("assignee"),
            solarwindsservicedesk_payload.get("owner"),
            solarwindsservicedesk_payload.get("assigned_to"),
            existing.solarwindsservicedesk.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.solarwindsservicedesk,
        ),
      )
      provider_schema_kind = "solarwindsservicedesk"
    topdesk_schema = existing.topdesk
    topdesk_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("topdesk"),
      payload.get("topdesk"),
      payload.get("topdesk_alert"),
    )
    if normalized_provider == "topdesk" or topdesk_payload:
      topdesk_status = self._first_non_empty_string(
        topdesk_payload.get("alert_status"),
        topdesk_payload.get("status"),
        topdesk_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.topdesk.alert_status,
      ) or "unknown"
      topdesk_schema = OperatorIncidentTopdeskRecoveryState(
        alert_id=self._first_non_empty_string(
          topdesk_payload.get("alert_id"),
          topdesk_payload.get("id"),
          topdesk_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.topdesk.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          topdesk_payload.get("external_reference"),
          topdesk_payload.get("reference"),
          reference,
          existing.topdesk.external_reference,
        ),
        alert_status=topdesk_status,
        priority=self._first_non_empty_string(
          topdesk_payload.get("priority"),
          topdesk_payload.get("severity"),
          topdesk_payload.get("urgency"),
          existing.topdesk.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          topdesk_payload.get("escalation_policy"),
          topdesk_payload.get("escalationPolicy"),
          topdesk_payload.get("policy"),
          topdesk_payload.get("source"),
          existing.topdesk.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          topdesk_payload.get("assignee"),
          topdesk_payload.get("owner"),
          topdesk_payload.get("assigned_to"),
          existing.topdesk.assignee,
        ),
        url=self._first_non_empty_string(
          topdesk_payload.get("url"),
          topdesk_payload.get("html_url"),
          topdesk_payload.get("link"),
          existing.topdesk.url,
        ),
        updated_at=(
          self._parse_payload_datetime(topdesk_payload.get("updated_at"))
          or existing.topdesk.updated_at
        ),
        phase_graph=self._build_topdesk_recovery_phase_graph(
          payload=topdesk_payload,
          alert_status=topdesk_status,
          priority=self._first_non_empty_string(
            topdesk_payload.get("priority"),
            topdesk_payload.get("severity"),
            topdesk_payload.get("urgency"),
            existing.topdesk.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            topdesk_payload.get("escalation_policy"),
            topdesk_payload.get("escalationPolicy"),
            topdesk_payload.get("policy"),
            topdesk_payload.get("source"),
            existing.topdesk.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            topdesk_payload.get("assignee"),
            topdesk_payload.get("owner"),
            topdesk_payload.get("assigned_to"),
            existing.topdesk.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.topdesk,
        ),
      )
      provider_schema_kind = "topdesk"
    invgateservicedesk_schema = existing.invgateservicedesk
    invgateservicedesk_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("invgateservicedesk"),
      payload.get("invgateservicedesk"),
      payload.get("invgateservicedesk_alert"),
    )
    if normalized_provider == "invgateservicedesk" or invgateservicedesk_payload:
      invgateservicedesk_status = self._first_non_empty_string(
        invgateservicedesk_payload.get("alert_status"),
        invgateservicedesk_payload.get("status"),
        invgateservicedesk_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.invgateservicedesk.alert_status,
      ) or "unknown"
      invgateservicedesk_schema = OperatorIncidentInvGateServiceDeskRecoveryState(
        alert_id=self._first_non_empty_string(
          invgateservicedesk_payload.get("alert_id"),
          invgateservicedesk_payload.get("id"),
          invgateservicedesk_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.invgateservicedesk.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          invgateservicedesk_payload.get("external_reference"),
          invgateservicedesk_payload.get("reference"),
          reference,
          existing.invgateservicedesk.external_reference,
        ),
        alert_status=invgateservicedesk_status,
        priority=self._first_non_empty_string(
          invgateservicedesk_payload.get("priority"),
          invgateservicedesk_payload.get("severity"),
          invgateservicedesk_payload.get("urgency"),
          existing.invgateservicedesk.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          invgateservicedesk_payload.get("escalation_policy"),
          invgateservicedesk_payload.get("escalationPolicy"),
          invgateservicedesk_payload.get("policy"),
          invgateservicedesk_payload.get("source"),
          existing.invgateservicedesk.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          invgateservicedesk_payload.get("assignee"),
          invgateservicedesk_payload.get("owner"),
          invgateservicedesk_payload.get("assigned_to"),
          existing.invgateservicedesk.assignee,
        ),
        url=self._first_non_empty_string(
          invgateservicedesk_payload.get("url"),
          invgateservicedesk_payload.get("html_url"),
          invgateservicedesk_payload.get("link"),
          existing.invgateservicedesk.url,
        ),
        updated_at=(
          self._parse_payload_datetime(invgateservicedesk_payload.get("updated_at"))
          or existing.invgateservicedesk.updated_at
        ),
        phase_graph=self._build_invgateservicedesk_recovery_phase_graph(
          payload=invgateservicedesk_payload,
          alert_status=invgateservicedesk_status,
          priority=self._first_non_empty_string(
            invgateservicedesk_payload.get("priority"),
            invgateservicedesk_payload.get("severity"),
            invgateservicedesk_payload.get("urgency"),
            existing.invgateservicedesk.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            invgateservicedesk_payload.get("escalation_policy"),
            invgateservicedesk_payload.get("escalationPolicy"),
            invgateservicedesk_payload.get("policy"),
            invgateservicedesk_payload.get("source"),
            existing.invgateservicedesk.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            invgateservicedesk_payload.get("assignee"),
            invgateservicedesk_payload.get("owner"),
            invgateservicedesk_payload.get("assigned_to"),
            existing.invgateservicedesk.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.invgateservicedesk,
        ),
      )
      provider_schema_kind = "invgateservicedesk"
    opsramp_schema = existing.opsramp
    opsramp_payload = self._merge_payload_mappings(
      self._extract_payload_mapping(payload.get("provider_schema")).get("opsramp"),
      payload.get("opsramp"),
      payload.get("opsramp_alert"),
    )
    if normalized_provider == "opsramp" or opsramp_payload:
      opsramp_status = self._first_non_empty_string(
        opsramp_payload.get("alert_status"),
        opsramp_payload.get("status"),
        opsramp_payload.get("state"),
        status_machine.workflow_state,
        payload.get("workflow_state"),
        existing.opsramp.alert_status,
      ) or "unknown"
      opsramp_schema = OperatorIncidentOpsRampRecoveryState(
        alert_id=self._first_non_empty_string(
          opsramp_payload.get("alert_id"),
          opsramp_payload.get("id"),
          opsramp_payload.get("alertId"),
          self._first_non_empty_string(
            workflow_reference,
            payload.get("workflow_reference"),
            payload.get("provider_workflow_reference"),
            existing.workflow_reference,
          ),
          existing.opsramp.alert_id,
        ),
        external_reference=self._first_non_empty_string(
          opsramp_payload.get("external_reference"),
          opsramp_payload.get("reference"),
          reference,
          existing.opsramp.external_reference,
        ),
        alert_status=opsramp_status,
        priority=self._first_non_empty_string(
          opsramp_payload.get("priority"),
          opsramp_payload.get("severity"),
          opsramp_payload.get("urgency"),
          existing.opsramp.priority,
        ),
        escalation_policy=self._first_non_empty_string(
          opsramp_payload.get("escalation_policy"),
          opsramp_payload.get("escalationPolicy"),
          opsramp_payload.get("policy"),
          opsramp_payload.get("source"),
          existing.opsramp.escalation_policy,
        ),
        assignee=self._first_non_empty_string(
          opsramp_payload.get("assignee"),
          opsramp_payload.get("owner"),
          opsramp_payload.get("assigned_to"),
          existing.opsramp.assignee,
        ),
        url=self._first_non_empty_string(
          opsramp_payload.get("url"),
          opsramp_payload.get("html_url"),
          opsramp_payload.get("link"),
          existing.opsramp.url,
        ),
        updated_at=(
          self._parse_payload_datetime(opsramp_payload.get("updated_at"))
          or existing.opsramp.updated_at
        ),
        phase_graph=self._build_opsramp_recovery_phase_graph(
          payload=opsramp_payload,
          alert_status=opsramp_status,
          priority=self._first_non_empty_string(
            opsramp_payload.get("priority"),
            opsramp_payload.get("severity"),
            opsramp_payload.get("urgency"),
            existing.opsramp.priority,
          ),
          escalation_policy=self._first_non_empty_string(
            opsramp_payload.get("escalation_policy"),
            opsramp_payload.get("escalationPolicy"),
            opsramp_payload.get("policy"),
            opsramp_payload.get("source"),
            existing.opsramp.escalation_policy,
          ),
          assignee=self._first_non_empty_string(
            opsramp_payload.get("assignee"),
            opsramp_payload.get("owner"),
            opsramp_payload.get("assigned_to"),
            existing.opsramp.assignee,
          ),
          lifecycle_state=lifecycle_state,
          status_machine=status_machine,
          synced_at=synced_at,
          existing=existing.opsramp,
        ),
      )
      provider_schema_kind = "opsramp"
    return OperatorIncidentProviderRecoveryState(
      lifecycle_state=lifecycle_state,
      provider=provider or existing.provider or remediation.provider,
      job_id=self._first_non_empty_string(
        payload.get("job_id"),
        payload.get("recovery_id"),
        payload.get("execution_id"),
        existing.job_id,
      ),
      reference=reference,
      workflow_reference=self._first_non_empty_string(
        workflow_reference,
        payload.get("workflow_reference"),
        payload.get("provider_workflow_reference"),
        existing.workflow_reference,
      ),
      summary=self._first_non_empty_string(
        payload.get("summary"),
        payload.get("remediation_summary"),
        payload.get("message"),
        existing.summary,
        remediation.summary,
      ),
      detail=self._first_non_empty_string(
        payload.get("detail"),
        payload.get("remediation_detail"),
        payload.get("status_detail"),
        payload.get("result_detail"),
        existing.detail,
        detail,
      ),
      channels=self._extract_string_tuple(
        payload.get("channels"),
        payload.get("channel"),
        target_payload.get("channels"),
        existing.channels,
      ),
      symbols=self._extract_string_tuple(
        payload.get("symbols"),
        payload.get("symbol"),
        targets_payload.get("symbols"),
        target_payload.get("symbols"),
        target_payload.get("symbol"),
        existing.symbols,
      ),
      timeframe=self._first_non_empty_string(
        payload.get("timeframe"),
        payload.get("target_timeframe"),
        targets_payload.get("timeframe"),
        target_payload.get("timeframe"),
        verification_payload.get("timeframe"),
        existing.timeframe,
      ),
      verification=verification,
      telemetry=telemetry,
      status_machine=status_machine,
      provider_schema_kind=provider_schema_kind,
      pagerduty=pagerduty_schema,
      opsgenie=opsgenie_schema,
      incidentio=incidentio_schema,
      firehydrant=firehydrant_schema,
      rootly=rootly_schema,
      blameless=blameless_schema,
      xmatters=xmatters_schema,
      servicenow=servicenow_schema,
      squadcast=squadcast_schema,
      bigpanda=bigpanda_schema,
      grafana_oncall=grafana_oncall_schema,
      zenduty=zenduty_schema,
      splunk_oncall=splunk_oncall_schema,
      jira_service_management=jira_service_management_schema,
      pagertree=pagertree_schema,
      alertops=alertops_schema,
      signl4=signl4_schema,
      ilert=ilert_schema,
      betterstack=betterstack_schema,
      onpage=onpage_schema,
      allquiet=allquiet_schema,
      moogsoft=moogsoft_schema,
      spikesh=spikesh_schema,
      dutycalls=dutycalls_schema,
      incidenthub=incidenthub_schema,
      resolver=resolver_schema,
      openduty=openduty_schema,
      cabot=cabot_schema,
      haloitsm=haloitsm_schema,
      incidentmanagerio=incidentmanagerio_schema,
      oneuptime=oneuptime_schema,
      squzy=squzy_schema,
      crisescontrol=crisescontrol_schema,
      freshservice=freshservice_schema,
      freshdesk=freshdesk_schema,
      happyfox=happyfox_schema,
      zendesk=zendesk_schema,
      zohodesk=zohodesk_schema,
      helpscout=helpscout_schema,
      kayako=kayako_schema,
      intercom=intercom_schema,
      front=front_schema,
      servicedeskplus=servicedeskplus_schema,
      sysaid=sysaid_schema,
      bmchelix=bmchelix_schema,
      solarwindsservicedesk=solarwindsservicedesk_schema,
      topdesk=topdesk_schema,
      invgateservicedesk=invgateservicedesk_schema,
      opsramp=opsramp_schema,
      updated_at=synced_at,
    )

  def _refresh_provider_recovery_phase_graphs(
    self,
    *,
    provider_recovery: OperatorIncidentProviderRecoveryState,
    synced_at: datetime,
  ) -> OperatorIncidentProviderRecoveryState:
    return replace(
      provider_recovery,
      pagerduty=replace(
        provider_recovery.pagerduty,
        phase_graph=self._build_pagerduty_recovery_phase_graph(
          payload={},
          incident_status=provider_recovery.pagerduty.incident_status,
          urgency=provider_recovery.pagerduty.urgency,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.pagerduty,
        ),
      ),
      opsgenie=replace(
        provider_recovery.opsgenie,
        phase_graph=self._build_opsgenie_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.opsgenie.alert_status,
          owner=provider_recovery.opsgenie.owner,
          acknowledged=provider_recovery.opsgenie.acknowledged,
          seen=provider_recovery.opsgenie.seen,
          teams=provider_recovery.opsgenie.teams,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.opsgenie,
        ),
      ),
      incidentio=replace(
        provider_recovery.incidentio,
        phase_graph=self._build_incidentio_recovery_phase_graph(
          payload={},
          incident_status=provider_recovery.incidentio.incident_status,
          severity=provider_recovery.incidentio.severity,
          mode=provider_recovery.incidentio.mode,
          visibility=provider_recovery.incidentio.visibility,
          assignee=provider_recovery.incidentio.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.incidentio,
        ),
      ),
      firehydrant=replace(
        provider_recovery.firehydrant,
        phase_graph=self._build_firehydrant_recovery_phase_graph(
          payload={},
          incident_status=provider_recovery.firehydrant.incident_status,
          severity=provider_recovery.firehydrant.severity,
          priority=provider_recovery.firehydrant.priority,
          team=provider_recovery.firehydrant.team,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.firehydrant,
        ),
      ),
      rootly=replace(
        provider_recovery.rootly,
        phase_graph=self._build_rootly_recovery_phase_graph(
          payload={},
          incident_status=provider_recovery.rootly.incident_status,
          severity_id=provider_recovery.rootly.severity_id,
          private=provider_recovery.rootly.private,
          acknowledged_at=provider_recovery.rootly.acknowledged_at,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.rootly,
        ),
      ),
      blameless=replace(
        provider_recovery.blameless,
        phase_graph=self._build_blameless_recovery_phase_graph(
          payload={},
          incident_status=provider_recovery.blameless.incident_status,
          severity=provider_recovery.blameless.severity,
          commander=provider_recovery.blameless.commander,
          visibility=provider_recovery.blameless.visibility,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.blameless,
        ),
      ),
      xmatters=replace(
        provider_recovery.xmatters,
        phase_graph=self._build_xmatters_recovery_phase_graph(
          payload={},
          incident_status=provider_recovery.xmatters.incident_status,
          priority=provider_recovery.xmatters.priority,
          assignee=provider_recovery.xmatters.assignee,
          response_plan=provider_recovery.xmatters.response_plan,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.xmatters,
        ),
      ),
      servicenow=replace(
        provider_recovery.servicenow,
        phase_graph=self._build_servicenow_recovery_phase_graph(
          payload={},
          incident_status=provider_recovery.servicenow.incident_status,
          priority=provider_recovery.servicenow.priority,
          assigned_to=provider_recovery.servicenow.assigned_to,
          assignment_group=provider_recovery.servicenow.assignment_group,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.servicenow,
        ),
      ),
      squadcast=replace(
        provider_recovery.squadcast,
        phase_graph=self._build_squadcast_recovery_phase_graph(
          payload={},
          incident_status=provider_recovery.squadcast.incident_status,
          severity=provider_recovery.squadcast.severity,
          assignee=provider_recovery.squadcast.assignee,
          escalation_policy=provider_recovery.squadcast.escalation_policy,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.squadcast,
        ),
      ),
      bigpanda=replace(
        provider_recovery.bigpanda,
        phase_graph=self._build_bigpanda_recovery_phase_graph(
          payload={},
          incident_status=provider_recovery.bigpanda.incident_status,
          severity=provider_recovery.bigpanda.severity,
          assignee=provider_recovery.bigpanda.assignee,
          team=provider_recovery.bigpanda.team,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.bigpanda,
        ),
      ),
      grafana_oncall=replace(
        provider_recovery.grafana_oncall,
        phase_graph=self._build_grafana_oncall_recovery_phase_graph(
          payload={},
          incident_status=provider_recovery.grafana_oncall.incident_status,
          severity=provider_recovery.grafana_oncall.severity,
          assignee=provider_recovery.grafana_oncall.assignee,
          escalation_chain=provider_recovery.grafana_oncall.escalation_chain,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.grafana_oncall,
        ),
      ),
      zenduty=replace(
        provider_recovery.zenduty,
        phase_graph=self._build_zenduty_recovery_phase_graph(
          payload={},
          incident_status=provider_recovery.zenduty.incident_status,
          severity=provider_recovery.zenduty.severity,
          assignee=provider_recovery.zenduty.assignee,
          service=provider_recovery.zenduty.service,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.zenduty,
        ),
      ),
      splunk_oncall=replace(
        provider_recovery.splunk_oncall,
        phase_graph=self._build_splunk_oncall_recovery_phase_graph(
          payload={},
          incident_status=provider_recovery.splunk_oncall.incident_status,
          severity=provider_recovery.splunk_oncall.severity,
          assignee=provider_recovery.splunk_oncall.assignee,
          routing_key=provider_recovery.splunk_oncall.routing_key,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.splunk_oncall,
        ),
      ),
      jira_service_management=replace(
        provider_recovery.jira_service_management,
        phase_graph=self._build_jira_service_management_recovery_phase_graph(
          payload={},
          incident_status=provider_recovery.jira_service_management.incident_status,
          priority=provider_recovery.jira_service_management.priority,
          assignee=provider_recovery.jira_service_management.assignee,
          service_project=provider_recovery.jira_service_management.service_project,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.jira_service_management,
        ),
      ),
      pagertree=replace(
        provider_recovery.pagertree,
        phase_graph=self._build_pagertree_recovery_phase_graph(
          payload={},
          incident_status=provider_recovery.pagertree.incident_status,
          urgency=provider_recovery.pagertree.urgency,
          assignee=provider_recovery.pagertree.assignee,
          team=provider_recovery.pagertree.team,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.pagertree,
        ),
      ),
      alertops=replace(
        provider_recovery.alertops,
        phase_graph=self._build_alertops_recovery_phase_graph(
          payload={},
          incident_status=provider_recovery.alertops.incident_status,
          priority=provider_recovery.alertops.priority,
          owner=provider_recovery.alertops.owner,
          service=provider_recovery.alertops.service,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.alertops,
        ),
      ),
      signl4=replace(
        provider_recovery.signl4,
        phase_graph=self._build_signl4_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.signl4.alert_status,
          priority=provider_recovery.signl4.priority,
          team=provider_recovery.signl4.team,
          assignee=provider_recovery.signl4.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.signl4,
        ),
      ),
      ilert=replace(
        provider_recovery.ilert,
        phase_graph=self._build_ilert_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.ilert.alert_status,
          priority=provider_recovery.ilert.priority,
          escalation_policy=provider_recovery.ilert.escalation_policy,
          assignee=provider_recovery.ilert.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.ilert,
        ),
      ),
      betterstack=replace(
        provider_recovery.betterstack,
        phase_graph=self._build_betterstack_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.betterstack.alert_status,
          priority=provider_recovery.betterstack.priority,
          escalation_policy=provider_recovery.betterstack.escalation_policy,
          assignee=provider_recovery.betterstack.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.betterstack,
        ),
      ),
      onpage=replace(
        provider_recovery.onpage,
        phase_graph=self._build_onpage_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.onpage.alert_status,
          priority=provider_recovery.onpage.priority,
          escalation_policy=provider_recovery.onpage.escalation_policy,
          assignee=provider_recovery.onpage.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.onpage,
        ),
      ),
      allquiet=replace(
        provider_recovery.allquiet,
        phase_graph=self._build_allquiet_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.allquiet.alert_status,
          priority=provider_recovery.allquiet.priority,
          escalation_policy=provider_recovery.allquiet.escalation_policy,
          assignee=provider_recovery.allquiet.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.allquiet,
        ),
      ),
      moogsoft=replace(
        provider_recovery.moogsoft,
        phase_graph=self._build_moogsoft_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.moogsoft.alert_status,
          priority=provider_recovery.moogsoft.priority,
          escalation_policy=provider_recovery.moogsoft.escalation_policy,
          assignee=provider_recovery.moogsoft.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.moogsoft,
        ),
      ),
      spikesh=replace(
        provider_recovery.spikesh,
        phase_graph=self._build_spikesh_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.spikesh.alert_status,
          priority=provider_recovery.spikesh.priority,
          escalation_policy=provider_recovery.spikesh.escalation_policy,
          assignee=provider_recovery.spikesh.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.spikesh,
        ),
      ),
      dutycalls=replace(
        provider_recovery.dutycalls,
        phase_graph=self._build_dutycalls_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.dutycalls.alert_status,
          priority=provider_recovery.dutycalls.priority,
          escalation_policy=provider_recovery.dutycalls.escalation_policy,
          assignee=provider_recovery.dutycalls.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.dutycalls,
        ),
      ),
      incidenthub=replace(
        provider_recovery.incidenthub,
        phase_graph=self._build_incidenthub_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.incidenthub.alert_status,
          priority=provider_recovery.incidenthub.priority,
          escalation_policy=provider_recovery.incidenthub.escalation_policy,
          assignee=provider_recovery.incidenthub.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.incidenthub,
        ),
      ),
      resolver=replace(
        provider_recovery.resolver,
        phase_graph=self._build_resolver_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.resolver.alert_status,
          priority=provider_recovery.resolver.priority,
          escalation_policy=provider_recovery.resolver.escalation_policy,
          assignee=provider_recovery.resolver.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.resolver,
        ),
      ),
      openduty=replace(
        provider_recovery.openduty,
        phase_graph=self._build_openduty_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.openduty.alert_status,
          priority=provider_recovery.openduty.priority,
          escalation_policy=provider_recovery.openduty.escalation_policy,
          assignee=provider_recovery.openduty.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.openduty,
        ),
      ),
      cabot=replace(
        provider_recovery.cabot,
        phase_graph=self._build_cabot_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.cabot.alert_status,
          priority=provider_recovery.cabot.priority,
          escalation_policy=provider_recovery.cabot.escalation_policy,
          assignee=provider_recovery.cabot.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.cabot,
        ),
      ),
      haloitsm=replace(
        provider_recovery.haloitsm,
        phase_graph=self._build_haloitsm_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.haloitsm.alert_status,
          priority=provider_recovery.haloitsm.priority,
          escalation_policy=provider_recovery.haloitsm.escalation_policy,
          assignee=provider_recovery.haloitsm.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.haloitsm,
        ),
      ),
      incidentmanagerio=replace(
        provider_recovery.incidentmanagerio,
        phase_graph=self._build_incidentmanagerio_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.incidentmanagerio.alert_status,
          priority=provider_recovery.incidentmanagerio.priority,
          escalation_policy=provider_recovery.incidentmanagerio.escalation_policy,
          assignee=provider_recovery.incidentmanagerio.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.incidentmanagerio,
        ),
      ),
      oneuptime=replace(
        provider_recovery.oneuptime,
        phase_graph=self._build_oneuptime_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.oneuptime.alert_status,
          priority=provider_recovery.oneuptime.priority,
          escalation_policy=provider_recovery.oneuptime.escalation_policy,
          assignee=provider_recovery.oneuptime.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.oneuptime,
        ),
      ),
      squzy=replace(
        provider_recovery.squzy,
        phase_graph=self._build_squzy_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.squzy.alert_status,
          priority=provider_recovery.squzy.priority,
          escalation_policy=provider_recovery.squzy.escalation_policy,
          assignee=provider_recovery.squzy.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.squzy,
        ),
      ),
      crisescontrol=replace(
        provider_recovery.crisescontrol,
        phase_graph=self._build_crisescontrol_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.crisescontrol.alert_status,
          priority=provider_recovery.crisescontrol.priority,
          escalation_policy=provider_recovery.crisescontrol.escalation_policy,
          assignee=provider_recovery.crisescontrol.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.crisescontrol,
        ),
      ),
      freshservice=replace(
        provider_recovery.freshservice,
        phase_graph=self._build_freshservice_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.freshservice.alert_status,
          priority=provider_recovery.freshservice.priority,
          escalation_policy=provider_recovery.freshservice.escalation_policy,
          assignee=provider_recovery.freshservice.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.freshservice,
        ),
      ),
      freshdesk=replace(
        provider_recovery.freshdesk,
        phase_graph=self._build_freshdesk_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.freshdesk.alert_status,
          priority=provider_recovery.freshdesk.priority,
          escalation_policy=provider_recovery.freshdesk.escalation_policy,
          assignee=provider_recovery.freshdesk.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.freshdesk,
        ),
      ),
      happyfox=replace(
        provider_recovery.happyfox,
        phase_graph=self._build_happyfox_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.happyfox.alert_status,
          priority=provider_recovery.happyfox.priority,
          escalation_policy=provider_recovery.happyfox.escalation_policy,
          assignee=provider_recovery.happyfox.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.happyfox,
        ),
      ),
      zendesk=replace(
        provider_recovery.zendesk,
        phase_graph=self._build_zendesk_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.zendesk.alert_status,
          priority=provider_recovery.zendesk.priority,
          escalation_policy=provider_recovery.zendesk.escalation_policy,
          assignee=provider_recovery.zendesk.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.zendesk,
        ),
      ),
      zohodesk=replace(
        provider_recovery.zohodesk,
        phase_graph=self._build_zohodesk_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.zohodesk.alert_status,
          priority=provider_recovery.zohodesk.priority,
          escalation_policy=provider_recovery.zohodesk.escalation_policy,
          assignee=provider_recovery.zohodesk.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.zohodesk,
        ),
      ),
      helpscout=replace(
        provider_recovery.helpscout,
        phase_graph=self._build_helpscout_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.helpscout.alert_status,
          priority=provider_recovery.helpscout.priority,
          escalation_policy=provider_recovery.helpscout.escalation_policy,
          assignee=provider_recovery.helpscout.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.helpscout,
        ),
      ),
      kayako=replace(
        provider_recovery.kayako,
        phase_graph=self._build_kayako_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.kayako.alert_status,
          priority=provider_recovery.kayako.priority,
          escalation_policy=provider_recovery.kayako.escalation_policy,
          assignee=provider_recovery.kayako.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.kayako,
        ),
      ),
      intercom=replace(
        provider_recovery.intercom,
        phase_graph=self._build_intercom_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.intercom.alert_status,
          priority=provider_recovery.intercom.priority,
          escalation_policy=provider_recovery.intercom.escalation_policy,
          assignee=provider_recovery.intercom.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.intercom,
        ),
      ),
      front=replace(
        provider_recovery.front,
        phase_graph=self._build_front_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.front.alert_status,
          priority=provider_recovery.front.priority,
          escalation_policy=provider_recovery.front.escalation_policy,
          assignee=provider_recovery.front.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.front,
        ),
      ),
      servicedeskplus=replace(
        provider_recovery.servicedeskplus,
        phase_graph=self._build_servicedeskplus_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.servicedeskplus.alert_status,
          priority=provider_recovery.servicedeskplus.priority,
          escalation_policy=provider_recovery.servicedeskplus.escalation_policy,
          assignee=provider_recovery.servicedeskplus.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.servicedeskplus,
        ),
      ),
      sysaid=replace(
        provider_recovery.sysaid,
        phase_graph=self._build_sysaid_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.sysaid.alert_status,
          priority=provider_recovery.sysaid.priority,
          escalation_policy=provider_recovery.sysaid.escalation_policy,
          assignee=provider_recovery.sysaid.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.sysaid,
        ),
      ),
      bmchelix=replace(
        provider_recovery.bmchelix,
        phase_graph=self._build_bmchelix_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.bmchelix.alert_status,
          priority=provider_recovery.bmchelix.priority,
          escalation_policy=provider_recovery.bmchelix.escalation_policy,
          assignee=provider_recovery.bmchelix.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.bmchelix,
        ),
      ),
      solarwindsservicedesk=replace(
        provider_recovery.solarwindsservicedesk,
        phase_graph=self._build_solarwindsservicedesk_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.solarwindsservicedesk.alert_status,
          priority=provider_recovery.solarwindsservicedesk.priority,
          escalation_policy=provider_recovery.solarwindsservicedesk.escalation_policy,
          assignee=provider_recovery.solarwindsservicedesk.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.solarwindsservicedesk,
        ),
      ),
      invgateservicedesk=replace(
        provider_recovery.invgateservicedesk,
        phase_graph=self._build_invgateservicedesk_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.invgateservicedesk.alert_status,
          priority=provider_recovery.invgateservicedesk.priority,
          escalation_policy=provider_recovery.invgateservicedesk.escalation_policy,
          assignee=provider_recovery.invgateservicedesk.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.invgateservicedesk,
        ),
      ),
      topdesk=replace(
        provider_recovery.topdesk,
        phase_graph=self._build_topdesk_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.topdesk.alert_status,
          priority=provider_recovery.topdesk.priority,
          escalation_policy=provider_recovery.topdesk.escalation_policy,
          assignee=provider_recovery.topdesk.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.topdesk,
        ),
      ),
      opsramp=replace(
        provider_recovery.opsramp,
        phase_graph=self._build_opsramp_recovery_phase_graph(
          payload={},
          alert_status=provider_recovery.opsramp.alert_status,
          priority=provider_recovery.opsramp.priority,
          escalation_policy=provider_recovery.opsramp.escalation_policy,
          assignee=provider_recovery.opsramp.assignee,
          lifecycle_state=provider_recovery.lifecycle_state,
          status_machine=provider_recovery.status_machine,
          synced_at=synced_at,
          existing=provider_recovery.opsramp,
        ),
      ),
    )

  def _apply_external_remediation_sync(
    self,
    *,
    incident: OperatorIncidentEvent,
    next_state: str,
    event_kind: str,
    provider: str,
    actor: str,
    detail: str,
    synced_at: datetime,
    workflow_reference: str | None,
    payload: dict[str, Any],
  ) -> OperatorIncidentEvent:
    remediation = incident.remediation
    merged_payload = self._merge_incident_workflow_payload(
      existing=remediation.provider_payload,
      incoming=payload,
    )
    payload_reference = self._extract_incident_payload_reference(payload)
    provider_recovery = self._build_provider_recovery_state(
      remediation=remediation,
      next_state=next_state,
      provider=provider,
      detail=detail,
      synced_at=synced_at,
      workflow_reference=workflow_reference,
      payload=merged_payload,
      event_kind=event_kind,
    )
    next_remediation = replace(
      remediation,
      state=next_state,
      kind=self._first_non_empty_string(
        payload.get("remediation_kind"),
        payload.get("kind"),
      ) or remediation.kind,
      owner=self._first_non_empty_string(
        payload.get("remediation_owner"),
        payload.get("owner"),
      ) or remediation.owner,
      summary=self._first_non_empty_string(
        payload.get("remediation_summary"),
        payload.get("summary"),
        payload.get("message"),
      ) or remediation.summary,
      detail=self._first_non_empty_string(
        payload.get("remediation_detail"),
        payload.get("detail"),
        payload.get("status_detail"),
        payload.get("result_detail"),
        payload.get("message"),
      ) or detail,
      runbook=self._first_non_empty_string(
        payload.get("remediation_runbook"),
        payload.get("runbook"),
      ) or remediation.runbook,
      requested_at=remediation.requested_at or synced_at,
      requested_by=f"{provider}:{actor}",
      last_attempted_at=synced_at,
      provider=provider or remediation.provider,
      reference=workflow_reference or payload_reference or remediation.reference,
      provider_payload=merged_payload,
      provider_payload_updated_at=(
        synced_at if merged_payload != remediation.provider_payload else remediation.provider_payload_updated_at
      ),
      provider_recovery=provider_recovery,
    )
    return replace(incident, remediation=next_remediation)

  def _build_incident_provider_workflow_payload(
    self,
    *,
    incident: OperatorIncidentEvent,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None = None,
  ) -> dict[str, Any]:
    remediation = incident.remediation
    workflow_payload: dict[str, Any] = {
      "action": action,
      "actor": actor,
      "detail": detail,
      "alert": {
        "alert_id": incident.alert_id,
        "event_id": incident.event_id,
        "kind": incident.kind,
        "severity": incident.severity,
        "source": incident.source,
        "summary": incident.summary,
        "run_id": incident.run_id,
        "session_id": incident.session_id,
      },
    }
    if remediation.state != "not_applicable":
      workflow_payload["remediation"] = {
        "state": remediation.state,
        "kind": remediation.kind,
        "owner": remediation.owner,
        "summary": remediation.summary,
        "detail": remediation.detail,
        "runbook": remediation.runbook,
        "requested_at": remediation.requested_at.isoformat() if remediation.requested_at is not None else None,
        "requested_by": remediation.requested_by,
        "last_attempted_at": (
          remediation.last_attempted_at.isoformat()
          if remediation.last_attempted_at is not None
          else None
        ),
        "provider": remediation.provider,
        "reference": remediation.reference,
        "provider_payload": remediation.provider_payload,
        "provider_payload_updated_at": (
          remediation.provider_payload_updated_at.isoformat()
          if remediation.provider_payload_updated_at is not None
          else None
        ),
        "provider_recovery": asdict(remediation.provider_recovery),
      }
    if payload:
      workflow_payload["provider_context"] = self._normalize_incident_workflow_payload(payload)
    return workflow_payload

  def run_backtest(
    self,
    *,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    preset = self._resolve_experiment_preset(
      preset_id=preset_id,
      strategy_id=strategy_id,
      timeframe=timeframe,
    )
    resolved_parameters = _merge_preset_parameters(preset=preset, requested_parameters=parameters)
    strategy, metadata, strategy_snapshot = self._prepare_strategy(
      strategy_id=strategy_id,
      parameters=resolved_parameters,
    )
    experiment_metadata = _build_run_experiment_metadata(
      tags=tags,
      preset=preset,
      benchmark_family=benchmark_family,
      strategy_metadata=metadata,
    )
    config = RunConfig(
      run_id=str(uuid4()),
      mode=RunMode.BACKTEST,
      strategy_id=metadata.strategy_id,
      strategy_version=metadata.version,
      venue="binance",
      symbols=(symbol,),
      timeframe=timeframe,
      parameters=resolved_parameters,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      start_at=start_at,
      end_at=end_at,
    )
    if metadata.runtime == "freqtrade_reference":
      run = RunRecord(
        config=config,
        status=RunStatus.PENDING,
        provenance=RunProvenance(
          lane="reference",
          strategy=strategy_snapshot,
          experiment=experiment_metadata,
        ),
      )
      if self._freqtrade_reference is None:
        run.status = RunStatus.FAILED
        run.notes.append("Freqtrade reference adapter is not configured.")
      else:
        run = self._freqtrade_reference.execute_backtest(run, metadata)
      self._attach_rerun_boundary(run)
      return self._runs.save_run(run)
    run = self._simulate_run(
      config=config,
      strategy=strategy,
      strategy_snapshot=strategy_snapshot,
      active_bars=None,
    )
    run.provenance.experiment = experiment_metadata
    if run.status != RunStatus.FAILED:
      self._run_supervisor.complete(run)
    return self._runs.save_run(run)

  def start_sandbox_run(
    self,
    *,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict,
    replay_bars: int | None = 96,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    return self._start_sandbox_session(
      strategy_id=strategy_id,
      symbol=symbol,
      timeframe=timeframe,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      replay_bars=replay_bars,
      start_at=start_at,
      end_at=end_at,
      tags=tags,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
    )

  def start_paper_run(
    self,
    *,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict,
    replay_bars: int | None = 96,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    return self._start_paper_session(
      strategy_id=strategy_id,
      symbol=symbol,
      timeframe=timeframe,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      replay_bars=replay_bars,
      start_at=start_at,
      end_at=end_at,
      tags=tags,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
    )

  def start_live_run(
    self,
    *,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict,
    replay_bars: int | None = 96,
    operator_reason: str = "guarded_live_launch",
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    return self._start_live_session(
      strategy_id=strategy_id,
      symbol=symbol,
      timeframe=timeframe,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      replay_bars=replay_bars,
      operator_reason=operator_reason,
      start_at=start_at,
      end_at=end_at,
      tags=tags,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
    )

  def _start_sandbox_session(
    self,
    *,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict,
    replay_bars: int | None = 96,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    return self._start_native_session(
      target_mode=RunMode.SANDBOX,
      reference_failure_copy="Sandbox worker sessions remain on the native engine for now.",
      primed_note_prefix="Sandbox worker session primed from the latest market snapshot",
      insufficient_candles_copy="Sandbox worker session requires at least",
      attach_runtime_session=True,
      strategy_id=strategy_id,
      symbol=symbol,
      timeframe=timeframe,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      replay_bars=replay_bars,
      start_at=start_at,
      end_at=end_at,
      tags=tags,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
    )

  def _start_paper_session(
    self,
    *,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict,
    replay_bars: int | None = 96,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    return self._start_native_session(
      target_mode=RunMode.PAPER,
      reference_failure_copy="Paper trading remains on the native engine for now.",
      primed_note_prefix="Paper session primed from the latest market snapshot",
      insufficient_candles_copy="Paper session requires at least",
      attach_runtime_session=False,
      strategy_id=strategy_id,
      symbol=symbol,
      timeframe=timeframe,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      parameters=parameters,
      replay_bars=replay_bars,
      start_at=start_at,
      end_at=end_at,
      tags=tags,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
    )

  def _start_live_session(
    self,
    *,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict,
    replay_bars: int | None = 96,
    operator_reason: str,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    self._ensure_guarded_live_worker_start_allowed()
    state = self._guarded_live_state.load_state()
    preset = self._resolve_experiment_preset(
      preset_id=preset_id,
      strategy_id=strategy_id,
      timeframe=timeframe,
    )
    resolved_parameters = _merge_preset_parameters(preset=preset, requested_parameters=parameters)
    strategy, metadata, strategy_snapshot = self._prepare_strategy(
      strategy_id=strategy_id,
      parameters=resolved_parameters,
    )
    experiment_metadata = _build_run_experiment_metadata(
      tags=tags,
      preset=preset,
      benchmark_family=benchmark_family,
      strategy_metadata=metadata,
    )
    config = RunConfig(
      run_id=str(uuid4()),
      mode=RunMode.LIVE,
      strategy_id=metadata.strategy_id,
      strategy_version=metadata.version,
      venue=self._guarded_live_venue,
      symbols=(symbol,),
      timeframe=timeframe,
      parameters=resolved_parameters,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      start_at=start_at,
      end_at=end_at,
    )
    if metadata.runtime == "freqtrade_reference":
      run = RunRecord(
        config=config,
        status=RunStatus.FAILED,
        provenance=RunProvenance(
          lane="reference",
          strategy=strategy_snapshot,
          experiment=experiment_metadata,
        ),
      )
      run.notes.append(
        "Reference Freqtrade strategies are exposed for cataloging and backtest delegation. "
        "Guarded live remains on the native venue-backed worker path."
      )
      return self._runs.save_run(run)

    loaded = self._data_engine.load_frame(config=config, active_bars=replay_bars)
    run = self._run_supervisor.create_native_run(config=config, strategy=strategy_snapshot)
    run.provenance.experiment = experiment_metadata
    run.provenance.market_data = loaded.lineage
    run.provenance.market_data_by_symbol = loaded.lineage_by_symbol
    self._attach_rerun_boundary(run)
    data = loaded.frame
    if data.empty:
      run.notes.append("No candles available for the requested range.")
      run.status = RunStatus.FAILED
      return self._runs.save_run(run)

    enriched = strategy.build_feature_frame(data, config.parameters)
    required_bars = max(strategy.warmup_spec().required_bars, 2)
    if len(enriched) < required_bars:
      run.status = RunStatus.FAILED
      run.notes.append(
        f"Guarded live worker requires at least {required_bars} candles to prime the current strategy state."
      )
      return self._runs.save_run(run)

    latest_row = enriched.iloc[-1]
    latest_timestamp = latest_row["timestamp"].to_pydatetime()
    latest_market_price = float(latest_row["close"])
    cache = self._build_guarded_live_cache(
      config=config,
      state=state,
      fallback_cash=initial_cash,
      latest_market_price=latest_market_price,
    )
    self._seed_guarded_live_runtime_state(
      run=run,
      state=state,
      cache=cache,
      timestamp=latest_timestamp,
      market_price=latest_market_price,
    )
    run.metrics = summarize_performance(
      initial_cash=run.config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    self._run_supervisor.start_mode(
      run=run,
      mode=RunMode.LIVE,
      mode_service=self._mode_service,
      replay_bars=None,
    )
    primed_candle_count = run.provenance.market_data.candle_count if run.provenance.market_data is not None else 0
    self._run_supervisor.start_worker_session(
      run=run,
      worker_kind=self._guarded_live_worker_kind,
      heartbeat_interval_seconds=self._guarded_live_worker_heartbeat_interval_seconds,
      heartbeat_timeout_seconds=self._guarded_live_worker_heartbeat_timeout_seconds,
      now=self._clock(),
      primed_candle_count=primed_candle_count,
      processed_tick_count=0,
      last_processed_candle_at=latest_timestamp,
      last_seen_candle_at=latest_timestamp,
    )
    run.notes.insert(
      0,
      (
        "Guarded live worker primed from recovered venue state and the latest market snapshot "
        f"using {primed_candle_count} candles."
      ),
    )
    saved_run = self._runs.save_run(run)
    session_handoff = self._activate_guarded_live_venue_session(
      run=saved_run,
      reason=operator_reason,
    )
    saved_run = self._runs.save_run(saved_run)
    self._claim_guarded_live_session_ownership(
      run=saved_run,
      actor="operator",
      reason=operator_reason,
      session_handoff=session_handoff,
    )
    self._append_guarded_live_audit_event(
      kind="guarded_live_worker_started",
      actor="operator",
      summary=f"Guarded-live worker started for {symbol}.",
      detail=(
        f"Reason: {operator_reason}. Strategy {strategy_id} launched with "
        f"{len(saved_run.orders)} recovered/open order(s)."
      ),
      run_id=saved_run.config.run_id,
      session_id=saved_run.provenance.runtime_session.session_id if saved_run.provenance.runtime_session else None,
    )
    return saved_run

  def _start_native_session(
    self,
    *,
    target_mode: RunMode,
    reference_failure_copy: str,
    primed_note_prefix: str,
    insufficient_candles_copy: str,
    attach_runtime_session: bool,
    strategy_id: str,
    symbol: str,
    timeframe: str,
    initial_cash: float,
    fee_rate: float,
    slippage_bps: float,
    parameters: dict,
    replay_bars: int | None = 96,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    tags: Iterable[str] = (),
    preset_id: str | None = None,
    benchmark_family: str | None = None,
  ) -> RunRecord:
    preset = self._resolve_experiment_preset(
      preset_id=preset_id,
      strategy_id=strategy_id,
      timeframe=timeframe,
    )
    resolved_parameters = _merge_preset_parameters(preset=preset, requested_parameters=parameters)
    strategy, metadata, strategy_snapshot = self._prepare_strategy(
      strategy_id=strategy_id,
      parameters=resolved_parameters,
    )
    experiment_metadata = _build_run_experiment_metadata(
      tags=tags,
      preset=preset,
      benchmark_family=benchmark_family,
      strategy_metadata=metadata,
    )
    config = RunConfig(
      run_id=str(uuid4()),
      mode=target_mode,
      strategy_id=metadata.strategy_id,
      strategy_version=metadata.version,
      venue="binance",
      symbols=(symbol,),
      timeframe=timeframe,
      parameters=resolved_parameters,
      initial_cash=initial_cash,
      fee_rate=fee_rate,
      slippage_bps=slippage_bps,
      start_at=start_at,
      end_at=end_at,
    )
    self._ensure_operator_control_runtime_allowed(target_mode)
    if metadata.runtime == "freqtrade_reference":
      run = RunRecord(
        config=config,
        status=RunStatus.FAILED,
        provenance=RunProvenance(
          lane="reference",
          strategy=strategy_snapshot,
          experiment=experiment_metadata,
        ),
      )
      run.notes.append(
        "Reference Freqtrade strategies are exposed for cataloging and backtest delegation. "
        + reference_failure_copy
      )
      return self._runs.save_run(run)

    loaded = self._data_engine.load_frame(config=config, active_bars=replay_bars)
    run = self._run_supervisor.create_native_run(config=config, strategy=strategy_snapshot)
    run.provenance.experiment = experiment_metadata
    run.provenance.market_data = loaded.lineage
    run.provenance.market_data_by_symbol = loaded.lineage_by_symbol
    self._attach_rerun_boundary(run)
    data = loaded.frame
    if data.empty:
      run.notes.append("No candles available for the requested range.")
      run.status = RunStatus.FAILED
      return self._runs.save_run(run)

    enriched = strategy.build_feature_frame(data, config.parameters)
    required_bars = max(strategy.warmup_spec().required_bars, 2)
    if len(enriched) < required_bars:
      run.status = RunStatus.FAILED
      run.notes.append(
        f"{insufficient_candles_copy} {required_bars} candles to prime the current strategy state."
      )
      return self._runs.save_run(run)

    cache = StateCache(
      instrument_id=f"{config.venue}:{config.symbols[0]}",
      cash=config.initial_cash,
    )
    history = enriched.iloc[:]
    latest_row = history.iloc[-1]
    state = cache.snapshot(
      timestamp=latest_row["timestamp"].to_pydatetime(),
      parameters=config.parameters,
    )
    decision = strategy.evaluate(history, config.parameters, state)
    self._execution_engine.apply_decision(
      run=run,
      config=config,
      decision=decision,
      cache=cache,
      market_price=float(latest_row["close"]),
    )
    run.metrics = summarize_performance(
      initial_cash=config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    self._run_supervisor.start_mode(
      run=run,
      mode=target_mode,
      mode_service=self._mode_service,
      replay_bars=replay_bars if target_mode == RunMode.SANDBOX else None,
    )
    if attach_runtime_session:
      primed_timestamp = latest_row["timestamp"].to_pydatetime()
      primed_candle_count = run.provenance.market_data.candle_count if run.provenance.market_data is not None else 0
      self._run_supervisor.start_worker_session(
        run=run,
        worker_kind=self._sandbox_worker_kind,
        heartbeat_interval_seconds=self._sandbox_worker_heartbeat_interval_seconds,
        heartbeat_timeout_seconds=self._sandbox_worker_heartbeat_timeout_seconds,
        now=self._clock(),
        primed_candle_count=primed_candle_count,
        processed_tick_count=1,
        last_processed_candle_at=primed_timestamp,
        last_seen_candle_at=primed_timestamp,
      )
    primed_candle_count = run.provenance.market_data.candle_count if run.provenance.market_data is not None else 0
    run.notes.insert(
      0,
      f"{primed_note_prefix} using {primed_candle_count} candles.",
    )
    return self._runs.save_run(run)

  def stop_sandbox_run(self, run_id: str) -> RunRecord | None:
    run = self._runs.get_run(run_id)
    if run is None:
      return None
    _ensure_run_action_allowed(
      run=run,
      capabilities=self.get_run_surface_capabilities(),
      action_key="stop_run",
    )
    self._run_supervisor.stop(run, reason="Sandbox run stopped by operator.")
    return self._runs.save_run(run)

  def stop_paper_run(self, run_id: str) -> RunRecord | None:
    run = self._runs.get_run(run_id)
    if run is None:
      return None
    _ensure_run_action_allowed(
      run=run,
      capabilities=self.get_run_surface_capabilities(),
      action_key="stop_run",
    )
    self._run_supervisor.stop(run, reason="Paper run stopped by operator.")
    return self._runs.save_run(run)

  def stop_live_run(self, run_id: str) -> RunRecord | None:
    run = self._runs.get_run(run_id)
    if run is None:
      return None
    _ensure_run_action_allowed(
      run=run,
      capabilities=self.get_run_surface_capabilities(),
      action_key="stop_run",
    )
    self._run_supervisor.stop(
      run,
      reason="Guarded-live worker stopped by operator. Venue open orders remain operator-managed.",
    )
    saved_run = self._runs.save_run(run)
    session_handoff = self._release_guarded_live_venue_session(run=saved_run)
    saved_run = self._runs.save_run(saved_run)
    self._release_guarded_live_session_ownership(
      run=saved_run,
      actor="operator",
      reason="operator_stop",
      ownership_state="released",
      session_handoff=session_handoff,
    )
    self._append_guarded_live_audit_event(
      kind="guarded_live_worker_stopped",
      actor="operator",
      summary=f"Guarded-live worker stopped for {run.config.symbols[0]}.",
      detail="Operator stop requested for the guarded-live worker session.",
      run_id=saved_run.config.run_id,
      session_id=saved_run.provenance.runtime_session.session_id if saved_run.provenance.runtime_session else None,
    )
    return saved_run

  def resume_guarded_live_run(
    self,
    *,
    actor: str,
    reason: str,
  ) -> RunRecord:
    self._ensure_guarded_live_resume_allowed()
    state = self._guarded_live_state.load_state()
    if state.ownership.owner_run_id is None:
      raise ValueError("No guarded-live session ownership is available to resume.")
    run = self._runs.get_run(state.ownership.owner_run_id)
    if run is None:
      raise LookupError("Owned guarded-live run not found")
    if run.config.mode != RunMode.LIVE:
      raise ValueError("Guarded-live ownership does not point to a live run.")
    if run.status in {RunStatus.STOPPED, RunStatus.COMPLETED}:
      raise ValueError("Terminal guarded-live runs cannot be resumed.")

    current_time = self._clock()
    if run.status == RunStatus.FAILED:
      run.status = RunStatus.RUNNING
      run.ended_at = None
    last_processed_candle_at = self._infer_last_processed_candle_at(run)
    self._run_supervisor.recover_worker_session(
      run=run,
      worker_kind=self._guarded_live_worker_kind,
      heartbeat_interval_seconds=self._guarded_live_worker_heartbeat_interval_seconds,
      heartbeat_timeout_seconds=self._guarded_live_worker_heartbeat_timeout_seconds,
      reason="operator_resume",
      now=current_time,
      started_at=run.started_at,
      primed_candle_count=self._infer_sandbox_primed_candle_count(run),
      processed_tick_count=run.provenance.runtime_session.processed_tick_count if run.provenance.runtime_session else 0,
      last_processed_candle_at=last_processed_candle_at,
      last_seen_candle_at=last_processed_candle_at,
    )
    session_restore = self._restore_guarded_live_venue_session(
      run=run,
      state=state,
      reason=reason,
    )
    if session_restore.state == "fallback_snapshot":
      try:
        self._sync_guarded_live_orders(run)
      except Exception as exc:
        run.notes.append(
          f"{current_time.isoformat()} | guarded_live_order_book_resume_warning | {exc}"
        )
    session_handoff = self._activate_guarded_live_venue_session(
      run=run,
      reason=reason,
    )
    self._run_supervisor.heartbeat_worker_session(run=run, now=current_time)
    run.notes.append(
      f"{current_time.isoformat()} | guarded_live_worker_resumed | {reason}"
    )
    run.metrics = summarize_performance(
      initial_cash=run.config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    saved_run = self._runs.save_run(run)
    self._claim_guarded_live_session_ownership(
      run=saved_run,
      actor=actor,
      reason=reason,
      resumed=True,
      session_restore=session_restore,
      session_handoff=session_handoff,
    )
    self._append_guarded_live_audit_event(
      kind="guarded_live_worker_resumed",
      actor=actor,
      summary=f"Guarded-live worker resumed for {saved_run.config.symbols[0]}.",
      detail=f"Reason: {reason}.",
      run_id=saved_run.config.run_id,
      session_id=saved_run.provenance.runtime_session.session_id if saved_run.provenance.runtime_session else None,
    )
    return saved_run

  def cancel_live_order(
    self,
    *,
    run_id: str,
    order_id: str,
    actor: str,
    reason: str,
  ) -> RunRecord:
    run, order = self._prepare_guarded_live_order_action(
      run_id=run_id,
      order_id=order_id,
      require_active=True,
    )
    _ensure_order_action_allowed(
      run=run,
      order=order,
      capabilities=self.get_run_surface_capabilities(),
      action_key="cancel",
    )
    venue_result = self._venue_execution.cancel_order(
      symbol=run.config.symbols[0],
      order_id=order.order_id,
    )
    self._apply_guarded_live_synced_order_state(run=run, order=order, synced_state=venue_result)
    run.metrics = summarize_performance(
      initial_cash=run.config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    run.notes.append(
      f"{self._clock().isoformat()} | guarded_live_order_canceled | "
      f"Reason: {reason}. Operator requested cancel for {order.order_id} and venue returned {order.status.value}."
    )
    saved_run = self._runs.save_run(run)
    self._claim_guarded_live_session_ownership(
      run=saved_run,
      actor=actor,
      reason=reason,
    )
    self._append_guarded_live_audit_event(
      kind="guarded_live_order_canceled",
      actor=actor,
      summary=f"Guarded-live order canceled for {run.config.symbols[0]}.",
      detail=(
        f"Reason: {reason}. Operator canceled {order.order_id}; "
        f"remaining quantity is {self._resolve_guarded_live_order_remaining_quantity(order):.8f} "
        f"and venue state is {order.status.value}."
      ),
      run_id=saved_run.config.run_id,
      session_id=saved_run.provenance.runtime_session.session_id if saved_run.provenance.runtime_session else None,
    )
    return saved_run

  def replace_live_order(
    self,
    *,
    run_id: str,
    order_id: str,
    price: float,
    quantity: float | None,
    actor: str,
    reason: str,
  ) -> RunRecord:
    if price <= 0:
      raise ValueError("Replacement price must be positive.")
    self._ensure_guarded_live_live_order_replace_allowed()
    run, order = self._prepare_guarded_live_order_action(
      run_id=run_id,
      order_id=order_id,
      require_active=True,
    )
    _ensure_order_action_allowed(
      run=run,
      order=order,
      capabilities=self.get_run_surface_capabilities(),
      action_key="replace",
    )
    remaining_quantity = self._resolve_guarded_live_order_remaining_quantity(order)
    replacement_quantity = quantity if quantity is not None else remaining_quantity
    if replacement_quantity <= self._guarded_live_balance_tolerance:
      raise ValueError("Replacement quantity resolved to zero.")
    if replacement_quantity - remaining_quantity > self._guarded_live_balance_tolerance:
      raise ValueError("Replacement quantity cannot exceed the current remaining order quantity.")

    cancel_result = self._venue_execution.cancel_order(
      symbol=run.config.symbols[0],
      order_id=order.order_id,
    )
    self._apply_guarded_live_synced_order_state(run=run, order=order, synced_state=cancel_result)
    if order.status in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}:
      raise RuntimeError(
        f"Guarded-live order replacement requires the current order to be canceled first: {order.order_id}"
      )
    run.metrics = summarize_performance(
      initial_cash=run.config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    run = self._runs.save_run(run)
    order = self._get_guarded_live_order(run=run, order_id=order_id)

    replacement_order = Order(
      run_id=run.config.run_id,
      instrument_id=order.instrument_id,
      side=order.side,
      quantity=replacement_quantity,
      requested_price=price,
      order_type=OrderType.LIMIT,
    )
    venue_result = self._submit_guarded_live_limit_order(
      run=run,
      order=replacement_order,
      limit_price=price,
    )
    replacement_order.order_id = venue_result.order_id
    replacement_order.created_at = venue_result.submitted_at
    replacement_order.updated_at = venue_result.updated_at or venue_result.submitted_at
    replacement_order.last_synced_at = venue_result.updated_at or venue_result.submitted_at
    replacement_order.status = self._map_guarded_live_order_status(
      venue_result.status,
      filled_quantity=venue_result.filled_amount or 0.0,
      remaining_quantity=venue_result.remaining_amount or 0.0,
    )
    if venue_result.average_fill_price is not None:
      replacement_order.average_fill_price = venue_result.average_fill_price
    replacement_order.fee_paid = venue_result.fee_paid or 0.0
    replacement_order.filled_quantity = venue_result.filled_amount or 0.0
    replacement_order.remaining_quantity = (
      venue_result.remaining_amount
      if venue_result.remaining_amount is not None
      else max(replacement_order.quantity - replacement_order.filled_quantity, 0.0)
    )
    if replacement_order.status == OrderStatus.FILLED:
      replacement_order.filled_at = venue_result.updated_at or venue_result.submitted_at
    run.orders.append(replacement_order)
    if replacement_order.filled_quantity > self._guarded_live_balance_tolerance:
      self._materialize_guarded_live_fill_delta(
        run=run,
        order=replacement_order,
        fill_quantity=replacement_order.filled_quantity,
        fee_paid=replacement_order.fee_paid,
        fill_price=venue_result.average_fill_price or replacement_order.requested_price,
        fill_timestamp=replacement_order.filled_at or venue_result.submitted_at,
      )
    run.metrics = summarize_performance(
      initial_cash=run.config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    run.notes.append(
      f"{self._clock().isoformat()} | guarded_live_order_replaced | "
      f"Reason: {reason}. Replaced {order.order_id} with {replacement_order.order_id} "
      f"for {replacement_quantity:.8f} at {price:.8f}."
    )
    saved_run = self._runs.save_run(run)
    self._claim_guarded_live_session_ownership(
      run=saved_run,
      actor=actor,
      reason=reason,
    )
    self._append_guarded_live_audit_event(
      kind="guarded_live_order_replaced",
      actor=actor,
      summary=f"Guarded-live order replaced for {run.config.symbols[0]}.",
      detail=(
        f"Reason: {reason}. Operator replaced {order.order_id} with {replacement_order.order_id} "
        f"for {replacement_quantity:.8f} at {price:.8f}; new venue state is {replacement_order.status.value}."
      ),
      run_id=saved_run.config.run_id,
      session_id=saved_run.provenance.runtime_session.session_id if saved_run.provenance.runtime_session else None,
    )
    return saved_run

  def _ensure_operator_control_runtime_allowed(self, mode: RunMode) -> None:
    if mode not in {RunMode.SANDBOX, RunMode.PAPER, RunMode.LIVE}:
      return
    state = self._guarded_live_state.load_state()
    if state.kill_switch.state == "engaged":
      raise ValueError(
        "Guarded-live kill switch is engaged. Release it before starting operator-controlled runtime sessions."
      )

  def _ensure_guarded_live_worker_start_allowed(self) -> None:
    self._ensure_operator_control_runtime_allowed(RunMode.LIVE)
    status = self.get_guarded_live_status()
    if status.running_live_count > 0:
      raise ValueError("A guarded-live worker is already running. Stop it before launching another.")
    if status.blockers:
      raise ValueError("Guarded-live launch is blocked: " + " ".join(status.blockers))

  def _ensure_guarded_live_live_order_replace_allowed(self) -> None:
    state = self._guarded_live_state.load_state()
    if state.kill_switch.state == "engaged":
      raise ValueError("Guarded-live kill switch is engaged. Cancel venue orders instead of replacing them.")
    ready, issues = self._venue_execution.describe_capability()
    if not ready:
      raise RuntimeError(
        "Venue order execution is unavailable: "
        + (", ".join(issues) if issues else "adapter not ready")
        + "."
      )

  def _ensure_guarded_live_resume_allowed(self) -> None:
    state = self._guarded_live_state.load_state()
    if state.kill_switch.state == "engaged":
      raise ValueError("Guarded-live kill switch is engaged. Release it before resuming live execution.")
    if state.recovery.state not in {"recovered", "recovered_with_warnings"}:
      raise ValueError("Guarded-live runtime recovery must be recorded before resume.")
    ready, issues = self._venue_execution.describe_capability()
    if not ready:
      raise RuntimeError(
        "Venue order execution is unavailable: "
        + (", ".join(issues) if issues else "adapter not ready")
        + "."
      )
    if state.ownership.state not in {"owned", "orphaned"}:
      raise ValueError("No guarded-live session ownership is available to resume.")

  def _persist_guarded_live_state(self, state: GuardedLiveState) -> GuardedLiveState:
    return self._guarded_live_state.save_state(state)

  def _claim_guarded_live_session_ownership(
    self,
    *,
    run: RunRecord,
    actor: str,
    reason: str,
    resumed: bool = False,
    session_restore: GuardedLiveVenueSessionRestore | None = None,
    session_handoff: GuardedLiveVenueSessionHandoff | None = None,
  ) -> None:
    session = run.provenance.runtime_session
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    existing = state.ownership
    self._persist_guarded_live_state(
      replace(
        state,
        ownership=GuardedLiveSessionOwnership(
          state="owned",
          owner_run_id=run.config.run_id,
          owner_session_id=session.session_id if session is not None else None,
          symbol=run.config.symbols[0] if run.config.symbols else None,
          claimed_at=existing.claimed_at if existing.owner_run_id == run.config.run_id else current_time,
          claimed_by=existing.claimed_by if existing.owner_run_id == run.config.run_id else actor,
          last_heartbeat_at=session.last_heartbeat_at if session is not None else current_time,
          last_order_sync_at=current_time,
          last_resumed_at=current_time if resumed else existing.last_resumed_at,
          last_reason=reason,
          last_released_at=None,
        ),
        order_book=self._build_guarded_live_order_book_sync(run=run),
        session_restore=self._resolve_guarded_live_session_restore_state(
          run=run,
          existing=state.session_restore,
          session_restore=session_restore,
        ),
        session_handoff=self._resolve_guarded_live_session_handoff_state(
          run=run,
          existing=state.session_handoff,
          session_handoff=session_handoff,
        ),
      )
    )

  def _release_guarded_live_session_ownership(
    self,
    *,
    run: RunRecord,
    actor: str,
    reason: str,
    ownership_state: str,
    session_handoff: GuardedLiveVenueSessionHandoff | None = None,
  ) -> None:
    session = run.provenance.runtime_session
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    existing = state.ownership
    self._persist_guarded_live_state(
      replace(
        state,
        ownership=GuardedLiveSessionOwnership(
          state=ownership_state,
          owner_run_id=run.config.run_id,
          owner_session_id=session.session_id if session is not None else existing.owner_session_id,
          symbol=run.config.symbols[0] if run.config.symbols else existing.symbol,
          claimed_at=existing.claimed_at or run.started_at,
          claimed_by=existing.claimed_by or actor,
          last_heartbeat_at=session.last_heartbeat_at if session is not None else existing.last_heartbeat_at,
          last_order_sync_at=current_time,
          last_resumed_at=existing.last_resumed_at,
          last_reason=reason,
          last_released_at=current_time if ownership_state == "released" else existing.last_released_at,
        ),
        order_book=self._build_guarded_live_order_book_sync(run=run),
        session_restore=self._resolve_guarded_live_session_restore_state(
          run=run,
          existing=state.session_restore,
        ),
        session_handoff=self._resolve_guarded_live_session_handoff_state(
          run=run,
          existing=state.session_handoff,
          session_handoff=session_handoff,
        ),
      )
    )

  def _resolve_guarded_live_session_restore_state(
    self,
    *,
    run: RunRecord,
    existing: GuardedLiveVenueSessionRestore,
    session_restore: GuardedLiveVenueSessionRestore | None = None,
  ) -> GuardedLiveVenueSessionRestore:
    session = run.provenance.runtime_session
    session_id = session.session_id if session is not None else existing.owner_session_id
    symbol = run.config.symbols[0] if run.config.symbols else existing.symbol
    if session_restore is not None:
      return replace(
        session_restore,
        venue=session_restore.venue or run.config.venue,
        symbol=session_restore.symbol or symbol,
        owner_run_id=run.config.run_id,
        owner_session_id=session_id,
      )
    if existing.owner_run_id == run.config.run_id:
      return replace(
        existing,
        venue=existing.venue or run.config.venue,
        symbol=existing.symbol or symbol,
        owner_run_id=run.config.run_id,
        owner_session_id=session_id,
      )
    return GuardedLiveVenueSessionRestore(
      state="not_restored",
      source="live_start",
      venue=run.config.venue,
      symbol=symbol,
      owner_run_id=run.config.run_id,
      owner_session_id=session_id,
    )

  def _resolve_guarded_live_session_handoff_state(
    self,
    *,
    run: RunRecord,
    existing: GuardedLiveVenueSessionHandoff,
    session_handoff: GuardedLiveVenueSessionHandoff | None = None,
  ) -> GuardedLiveVenueSessionHandoff:
    session = run.provenance.runtime_session
    session_id = session.session_id if session is not None else existing.owner_session_id
    symbol = run.config.symbols[0] if run.config.symbols else existing.symbol
    if session_handoff is not None:
      return replace(
        session_handoff,
        venue=session_handoff.venue or run.config.venue,
        symbol=session_handoff.symbol or symbol,
        timeframe=session_handoff.timeframe or run.config.timeframe,
        owner_run_id=run.config.run_id,
        owner_session_id=session_id,
      )
    if existing.owner_run_id == run.config.run_id:
      return replace(
        existing,
        venue=existing.venue or run.config.venue,
        symbol=existing.symbol or symbol,
        timeframe=existing.timeframe or run.config.timeframe,
        owner_run_id=run.config.run_id,
        owner_session_id=session_id,
      )
    return GuardedLiveVenueSessionHandoff(
      state="inactive",
      source="live_start",
      venue=run.config.venue,
      symbol=symbol,
      timeframe=run.config.timeframe,
      owner_run_id=run.config.run_id,
      owner_session_id=session_id,
    )

  def _activate_guarded_live_venue_session(
    self,
    *,
    run: RunRecord,
    reason: str,
  ) -> GuardedLiveVenueSessionHandoff:
    session = run.provenance.runtime_session
    handoff = self._venue_execution.handoff_session(
      symbol=run.config.symbols[0],
      timeframe=run.config.timeframe,
      owner_run_id=run.config.run_id,
      owner_session_id=session.session_id if session is not None else None,
      owned_order_ids=tuple(order.order_id for order in run.orders),
    )
    current_time = self._clock()
    run.notes.append(
      f"{current_time.isoformat()} | guarded_live_venue_session_handed_off | "
      f"source={handoff.source}; transport={handoff.transport}; state={handoff.state}; "
      f"supervision={handoff.supervision_state}; order_book={handoff.order_book_state}; "
      f"continuation={handoff.channel_continuation_state}; "
      f"failovers={handoff.failover_count}; reason={reason}"
    )
    self._append_guarded_live_audit_event(
      kind="guarded_live_venue_session_handed_off",
      actor="system",
      summary=f"Guarded-live venue session handed off for {run.config.symbols[0]}.",
      detail=(
        f"Reason: {reason}. Source {handoff.source} activated transport {handoff.transport} "
        f"with session {handoff.venue_session_id or 'n/a'}. Supervision "
        f"{handoff.supervision_state} with coverage {', '.join(handoff.coverage) or 'none'} "
        f"and order-book state {handoff.order_book_state}."
      ),
      run_id=run.config.run_id,
      session_id=session.session_id if session is not None else None,
    )
    return handoff

  def _release_guarded_live_venue_session(
    self,
    *,
    run: RunRecord,
  ) -> GuardedLiveVenueSessionHandoff:
    state = self._guarded_live_state.load_state()
    current_handoff = state.session_handoff
    if current_handoff.owner_run_id != run.config.run_id:
      return current_handoff
    released = self._venue_execution.release_session(handoff=current_handoff)
    current_time = self._clock()
    run.notes.append(
      f"{current_time.isoformat()} | guarded_live_venue_session_released | "
      f"source={released.source}; transport={released.transport}; state={released.state}; "
      f"supervision={released.supervision_state}; failovers={released.failover_count}"
    )
    self._append_guarded_live_audit_event(
      kind="guarded_live_venue_session_released",
      actor="system",
      summary=f"Guarded-live venue session released for {run.config.symbols[0]}.",
      detail=(
        f"Source {released.source} released transport {released.transport} "
        f"for session {released.venue_session_id or 'n/a'} after "
        f"{released.failover_count} failover(s)."
      ),
      run_id=run.config.run_id,
      session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
    )
    return released

  def _restore_guarded_live_venue_session(
    self,
    *,
    run: RunRecord,
    state: GuardedLiveState,
    reason: str,
  ) -> GuardedLiveVenueSessionRestore:
    current_time = self._clock()
    symbol = run.config.symbols[0]
    session = run.provenance.runtime_session
    session_id = session.session_id if session is not None else None
    owned_order_ids = tuple(order.order_id for order in run.orders)
    try:
      venue_restore = self._venue_execution.restore_session(
        symbol=symbol,
        owned_order_ids=owned_order_ids,
      )
    except Exception as exc:
      venue_restore = GuardedLiveVenueSessionRestore(
        state="unavailable",
        restored_at=current_time,
        source="venue_execution",
        venue=run.config.venue,
        symbol=symbol,
        owner_run_id=run.config.run_id,
        owner_session_id=session_id,
        issues=(f"venue_session_restore_failed:{exc}",),
      )
    venue_restore = replace(
      venue_restore,
      restored_at=venue_restore.restored_at or current_time,
      venue=venue_restore.venue or run.config.venue,
      symbol=venue_restore.symbol or symbol,
      owner_run_id=run.config.run_id,
      owner_session_id=session_id,
    )
    if self._guarded_live_venue_restore_has_state(venue_restore):
      self._apply_guarded_live_restored_session(
        run=run,
        session_restore=venue_restore,
      )
      run.notes.append(
        f"{current_time.isoformat()} | guarded_live_venue_session_restored | "
        f"source={venue_restore.source}; open_orders={len(venue_restore.open_orders)}; "
        f"tracked_orders={len(venue_restore.synced_orders)}; reason={reason}"
      )
      self._append_guarded_live_audit_event(
        kind="guarded_live_venue_session_restored",
        actor="system",
        summary=f"Guarded-live venue session restored for {symbol}.",
        detail=(
          f"Resume reason: {reason}. Source {venue_restore.source} restored "
          f"{len(venue_restore.synced_orders)} tracked order state(s) and "
          f"{len(venue_restore.open_orders)} open venue order(s)."
        ),
        run_id=run.config.run_id,
        session_id=session_id,
      )
      return venue_restore

    self._seed_guarded_live_execution_order_book(state.order_book)
    fallback_issues = tuple(dict.fromkeys((*venue_restore.issues, "venue_session_restore_unavailable")))
    fallback_restore = GuardedLiveVenueSessionRestore(
      state="fallback_snapshot",
      restored_at=current_time,
      source="durable_order_book_snapshot",
      venue=run.config.venue,
      symbol=symbol,
      owner_run_id=run.config.run_id,
      owner_session_id=session_id,
      open_orders=state.order_book.open_orders,
      synced_orders=(),
      issues=fallback_issues,
    )
    run.notes.append(
      f"{current_time.isoformat()} | guarded_live_venue_session_restore_fallback | "
      f"source={fallback_restore.source}; issues={', '.join(fallback_issues) if fallback_issues else 'none'}; "
      f"reason={reason}"
    )
    self._append_guarded_live_audit_event(
      kind="guarded_live_venue_session_restore_fallback",
      actor="system",
      summary=f"Guarded-live session restore fell back to persisted order book for {symbol}.",
      detail=(
        f"Resume reason: {reason}. Venue-native restore was unavailable, so the persisted "
        f"order-book snapshot was reseeded instead. Issues: "
        f"{', '.join(fallback_issues) if fallback_issues else 'none'}."
      ),
      run_id=run.config.run_id,
      session_id=session_id,
    )
    return fallback_restore

  @staticmethod
  def _guarded_live_venue_restore_has_state(
    session_restore: GuardedLiveVenueSessionRestore,
  ) -> bool:
    if session_restore.open_orders:
      return True
    return any(result.status != "unknown" for result in session_restore.synced_orders)

  def _apply_guarded_live_restored_session(
    self,
    *,
    run: RunRecord,
    session_restore: GuardedLiveVenueSessionRestore,
  ) -> int:
    existing_orders = {order.order_id: order for order in run.orders}
    open_orders_by_id = {
      order.order_id: order
      for order in session_restore.open_orders
    }
    state_changes = 0
    for synced_state in session_restore.synced_orders:
      if synced_state.status == "unknown":
        continue
      order = existing_orders.get(synced_state.order_id)
      if order is None:
        order = self._materialize_guarded_live_restored_order(
          run=run,
          synced_state=synced_state,
          open_order=open_orders_by_id.get(synced_state.order_id),
        )
        existing_orders[order.order_id] = order
        state_changes += 1
      state_changes += self._apply_guarded_live_synced_order_state(
        run=run,
        order=order,
        synced_state=synced_state,
      )

    for open_order in session_restore.open_orders:
      if open_order.order_id in existing_orders:
        continue
      order = self._materialize_guarded_live_restored_order(
        run=run,
        synced_state=None,
        open_order=open_order,
      )
      existing_orders[order.order_id] = order
      state_changes += 1

    if state_changes > 0:
      run.metrics = summarize_performance(
        initial_cash=run.config.initial_cash,
        equity_curve=run.equity_curve,
        closed_trades=run.closed_trades,
      )
    return state_changes

  def _materialize_guarded_live_restored_order(
    self,
    *,
    run: RunRecord,
    synced_state: GuardedLiveVenueOrderResult | None,
    open_order: GuardedLiveVenueOpenOrder | None,
  ) -> Order:
    symbol = run.config.symbols[0]
    restored_at = synced_state.submitted_at if synced_state is not None else self._clock()
    explicit_price = None
    if synced_state is not None:
      explicit_price = synced_state.requested_price
    if explicit_price is None and open_order is not None:
      explicit_price = open_order.price
    quantity = (
      (synced_state.requested_amount if synced_state is not None else None)
      or (synced_state.amount if synced_state is not None and synced_state.amount > 0 else None)
      or (open_order.amount if open_order is not None else None)
      or 0.0
    )
    restored_order = Order(
      run_id=run.config.run_id,
      instrument_id=f"{run.config.venue}:{symbol}",
      side=self._resolve_order_side(
        synced_state.side if synced_state is not None else open_order.side if open_order is not None else "buy"
      ),
      quantity=quantity,
      requested_price=(
        explicit_price
        if explicit_price is not None
        else (synced_state.average_fill_price if synced_state is not None and synced_state.average_fill_price is not None else 0.0)
      ),
      order_type=OrderType.LIMIT if explicit_price is not None else OrderType.MARKET,
      status=(
        self._map_guarded_live_order_status(
          open_order.status,
          filled_quantity=0.0,
          remaining_quantity=quantity,
        )
        if open_order is not None
        else OrderStatus.OPEN
      ),
      order_id=synced_state.order_id if synced_state is not None else open_order.order_id,
      created_at=restored_at,
      updated_at=synced_state.updated_at if synced_state is not None else restored_at,
      last_synced_at=synced_state.updated_at if synced_state is not None else restored_at,
      remaining_quantity=quantity,
    )
    run.orders.append(restored_order)
    return restored_order

  def _build_guarded_live_order_book_sync(self, *, run: RunRecord) -> GuardedLiveOrderBookSync:
    session = run.provenance.runtime_session
    open_orders = self._build_guarded_live_open_orders_from_run(run)
    current_time = self._clock()
    return GuardedLiveOrderBookSync(
      state="synced" if open_orders else "empty",
      synced_at=current_time,
      owner_run_id=run.config.run_id,
      owner_session_id=session.session_id if session is not None else None,
      symbol=run.config.symbols[0] if run.config.symbols else None,
      open_orders=open_orders,
      issues=(),
    )

  def _build_guarded_live_open_orders_from_run(
    self,
    run: RunRecord,
  ) -> tuple[GuardedLiveVenueOpenOrder, ...]:
    symbol = run.config.symbols[0] if run.config.symbols else None
    open_orders: list[GuardedLiveVenueOpenOrder] = []
    for order in run.orders:
      if order.status not in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}:
        continue
      open_orders.append(
        GuardedLiveVenueOpenOrder(
          order_id=order.order_id,
          symbol=symbol or order.instrument_id.split(":", 1)[-1],
          side=order.side.value,
          amount=self._resolve_guarded_live_order_remaining_quantity(order),
          status=order.status.value,
          price=order.requested_price,
        )
      )
    open_orders.sort(key=lambda item: (item.symbol, item.order_id))
    return tuple(open_orders)

  def _seed_guarded_live_execution_order_book(
    self,
    order_book: GuardedLiveOrderBookSync,
  ) -> None:
    if not order_book.open_orders:
      return
    setter = getattr(self._venue_execution, "set_order_state", None)
    if not callable(setter):
      return
    for order in order_book.open_orders:
      setter(
        order.order_id,
        symbol=order.symbol,
        side=order.side,
        amount=order.amount,
        requested_price=order.price,
        status=order.status,
        updated_at=order_book.synced_at or self._clock(),
        filled_amount=0.0,
        remaining_amount=order.amount,
      )

  def _prepare_guarded_live_order_action(
    self,
    *,
    run_id: str,
    order_id: str,
    require_active: bool,
  ) -> tuple[RunRecord, Order]:
    run = self._runs.get_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    if run.config.mode != RunMode.LIVE:
      raise ValueError("Guarded-live order controls are available only for live runs.")
    if self._sync_guarded_live_orders(run) > 0:
      run = self._runs.save_run(run)
    order = self._get_guarded_live_order(run=run, order_id=order_id)
    if require_active and order.status not in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}:
      raise ValueError("Only active guarded-live venue orders can be controlled.")
    return run, order

  @staticmethod
  def _get_guarded_live_order(
    *,
    run: RunRecord,
    order_id: str,
  ) -> Order:
    for order in run.orders:
      if order.order_id == order_id:
        return order
    raise LookupError("Order not found")

  @staticmethod
  def _resolve_guarded_live_order_remaining_quantity(order: Order) -> float:
    if order.remaining_quantity is not None:
      return max(order.remaining_quantity, 0.0)
    return max(order.quantity - order.filled_quantity, 0.0)

  def _select_guarded_live_recovery_snapshot(
    self,
    state: GuardedLiveState,
  ) -> GuardedLiveVenueStateSnapshot:
    snapshot = state.reconciliation.venue_snapshot
    if (
      snapshot is not None
      and snapshot.verification_state != "unavailable"
      and snapshot.venue == self._guarded_live_venue
    ):
      return snapshot
    return self._venue_state.capture_snapshot()

  def _recover_exposures_from_venue_snapshot(
    self,
    snapshot: GuardedLiveVenueStateSnapshot,
  ) -> tuple[tuple[GuardedLiveRecoveredExposure, ...], tuple[str, ...]]:
    tolerance = self._guarded_live_balance_tolerance
    instruments = self._market_data.list_instruments()
    quote_assets = {instrument.quote_currency for instrument in instruments}
    recovered: list[GuardedLiveRecoveredExposure] = []
    issues: list[str] = []

    for balance in snapshot.balances:
      if abs(balance.total) <= tolerance:
        continue
      if balance.asset in quote_assets:
        continue
      instrument = self._resolve_recovery_instrument(balance.asset, snapshot.open_orders, instruments)
      if instrument is None:
        issues.append(f"unmapped_recovery_asset:{balance.asset}")
        recovered.append(
          GuardedLiveRecoveredExposure(
            instrument_id=f"{self._guarded_live_venue}:{balance.asset}",
            symbol=balance.asset,
            asset=balance.asset,
            quantity=balance.total,
          )
        )
        continue
      recovered.append(
        GuardedLiveRecoveredExposure(
          instrument_id=f"{self._guarded_live_venue}:{instrument.symbol}",
          symbol=instrument.symbol,
          asset=balance.asset,
          quantity=balance.total,
        )
      )
    recovered.sort(key=lambda exposure: (exposure.symbol, exposure.asset))
    return tuple(recovered), tuple(issues)

  def _resolve_recovery_instrument(
    self,
    asset: str,
    open_orders: tuple[GuardedLiveVenueOpenOrder, ...],
    instruments: list[Instrument],
  ) -> Instrument | None:
    for order in open_orders:
      if order.symbol.split("/", 1)[0] != asset:
        continue
      for instrument in instruments:
        if instrument.symbol == order.symbol:
          return instrument

    candidates = [instrument for instrument in instruments if instrument.base_currency == asset]
    if not candidates:
      return None
    if len(candidates) == 1:
      return candidates[0]
    candidates.sort(key=lambda instrument: (instrument.quote_currency != "USDT", instrument.symbol))
    return candidates[0]

  def _append_guarded_live_audit_event(
    self,
    *,
    kind: str,
    actor: str,
    summary: str,
    detail: str,
    run_id: str | None = None,
    session_id: str | None = None,
  ) -> None:
    current_time = self._clock()
    state = self._guarded_live_state.load_state()
    event = OperatorAuditEvent(
      event_id=f"{kind}:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind=kind,
      summary=summary,
      detail=detail,
      run_id=run_id,
      session_id=session_id,
      source="guarded_live",
    )
    self._persist_guarded_live_state(
      replace(
        state,
        audit_events=(event, *state.audit_events),
      )
    )

  def _build_guarded_live_cache(
    self,
    *,
    config: RunConfig,
    state: GuardedLiveState,
    fallback_cash: float,
    latest_market_price: float,
  ) -> StateCache:
    instrument_id = f"{config.venue}:{config.symbols[0]}"
    quote_asset = config.symbols[0].split("/", 1)[1] if "/" in config.symbols[0] else "USDT"
    cash = self._resolve_guarded_live_cash_balance(
      state=state,
      quote_asset=quote_asset,
      fallback_cash=fallback_cash,
    )
    cache = StateCache(instrument_id=instrument_id, cash=cash)
    recovered_exposure = next(
      (exposure for exposure in state.recovery.exposures if exposure.instrument_id == instrument_id),
      None,
    )
    if recovered_exposure is not None and recovered_exposure.quantity > self._guarded_live_balance_tolerance:
      recovered_at = state.recovery.recovered_at or self._clock()
      cache.apply(
        cash=cash,
        position=Position(
          instrument_id=instrument_id,
          quantity=recovered_exposure.quantity,
          average_price=latest_market_price,
          opened_at=recovered_at,
          updated_at=recovered_at,
        ),
      )
    return cache

  def _resolve_guarded_live_cash_balance(
    self,
    *,
    state: GuardedLiveState,
    quote_asset: str,
    fallback_cash: float,
  ) -> float:
    snapshot = state.reconciliation.venue_snapshot
    if snapshot is None:
      return fallback_cash
    for balance in snapshot.balances:
      if balance.asset == quote_asset:
        return balance.free if balance.free is not None else balance.total
    return fallback_cash

  def _seed_guarded_live_runtime_state(
    self,
    *,
    run: RunRecord,
    state: GuardedLiveState,
    cache: StateCache,
    timestamp: datetime,
    market_price: float,
  ) -> None:
    if cache.position is not None and cache.position.is_open:
      run.positions[cache.position.instrument_id] = cache.position

    symbol = run.config.symbols[0]
    recovered_order_count = 0
    for recovered_order in state.recovery.open_orders:
      if recovered_order.symbol != symbol:
        continue
      if recovered_order.status.lower() in {"closed", "filled", "canceled", "cancelled", "rejected"}:
        continue
      recovered_order_count += 1
      run.orders.append(
        Order(
          run_id=run.config.run_id,
          instrument_id=f"{run.config.venue}:{symbol}",
          side=self._resolve_order_side(recovered_order.side),
          quantity=recovered_order.amount,
          requested_price=recovered_order.price or market_price,
          order_type=OrderType.LIMIT if recovered_order.price is not None else OrderType.MARKET,
          status=OrderStatus.OPEN,
          order_id=recovered_order.order_id,
          created_at=state.recovery.recovered_at or self._clock(),
          updated_at=state.recovery.recovered_at or self._clock(),
          filled_quantity=0.0,
          remaining_quantity=recovered_order.amount,
          last_synced_at=state.recovery.recovered_at or self._clock(),
        )
      )
      self._seed_guarded_live_execution_order_state(
        order=run.orders[-1],
        symbol=symbol,
      )

    run.equity_curve.append(
      build_equity_point(
        timestamp=timestamp,
        cash=cache.cash,
        position=cache.position if cache.position and cache.position.is_open else None,
        market_price=market_price,
      )
    )
    run.notes.append(
      "Recovered guarded-live runtime state with "
      f"{1 if cache.position is not None and cache.position.is_open else 0} exposure(s) "
      f"and {recovered_order_count} open venue order(s)."
    )

  def _seed_guarded_live_execution_order_state(
    self,
    *,
    order: Order,
    symbol: str,
  ) -> None:
    setter = getattr(self._venue_execution, "set_order_state", None)
    if not callable(setter):
      return
    setter(
      order.order_id,
      symbol=symbol,
      side=order.side.value,
      amount=order.quantity,
      requested_price=order.requested_price,
      status=order.status.value,
      updated_at=order.updated_at or order.created_at,
      average_fill_price=order.average_fill_price,
      fee_paid=order.fee_paid,
      filled_amount=order.filled_quantity,
      remaining_amount=self._resolve_guarded_live_order_remaining_quantity(order),
    )

  @staticmethod
  def _resolve_order_side(side: str) -> OrderSide:
    return OrderSide.SELL if side.lower() == OrderSide.SELL.value else OrderSide.BUY

  def _count_running_runs(self, mode: RunMode) -> int:
    return sum(
      1
      for run in self._runs.list_runs(mode=mode.value)
      if run.status == RunStatus.RUNNING
    )

  def _stop_runs_for_kill_switch(self, *, actor: str, reason: str) -> list[str]:
    stopped_runs: list[str] = []
    for mode, label in (
      (RunMode.SANDBOX, "Sandbox worker"),
      (RunMode.PAPER, "Paper session"),
      (RunMode.LIVE, "Guarded-live worker"),
    ):
      for run in self._runs.list_runs(mode=mode.value):
        if run.status != RunStatus.RUNNING:
          continue
        self._run_supervisor.stop(
          run,
          reason=f"{label} stopped by guarded-live kill switch ({actor}: {reason}).",
        )
        self._runs.save_run(run)
        stopped_runs.append(run.config.run_id)
    return stopped_runs

  def _build_guarded_live_reconciliation_findings(self) -> list[GuardedLiveReconciliationFinding]:
    _, _, findings = self._build_guarded_live_reconciliation_result()
    return findings

  def _build_guarded_live_reconciliation(
    self,
    *,
    state: GuardedLiveState,
    checked_at: datetime,
    checked_by: str,
  ) -> GuardedLiveReconciliation:
    internal_snapshot, venue_snapshot, findings = self._build_guarded_live_reconciliation_result(state=state)
    return GuardedLiveReconciliation(
      state="clear" if not findings else "issues_detected",
      checked_at=checked_at,
      checked_by=checked_by,
      scope="venue_state",
      summary=(
        "Guarded-live reconciliation verified venue state against local runtime state."
        if not findings
        else f"Guarded-live reconciliation found {len(findings)} venue-state issue(s)."
      ),
      findings=tuple(findings),
      internal_snapshot=internal_snapshot,
      venue_snapshot=venue_snapshot,
    )

  def _build_guarded_live_reconciliation_result(
    self,
    *,
    state: GuardedLiveState | None = None,
  ) -> tuple[
    GuardedLiveInternalStateSnapshot,
    GuardedLiveVenueStateSnapshot,
    list[GuardedLiveReconciliationFinding],
  ]:
    findings: list[GuardedLiveReconciliationFinding] = []
    effective_state = state or self._guarded_live_state.load_state()
    internal_snapshot = self._build_guarded_live_internal_snapshot(state=effective_state)
    venue_snapshot = self._venue_state.capture_snapshot()

    if venue_snapshot.venue != self._guarded_live_venue:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="guarded_live_venue_mismatch",
          severity="critical",
          summary="Venue-state snapshot does not match the configured guarded-live venue.",
          detail=(
            f"Guarded-live is configured for {self._guarded_live_venue}, "
            f"but venue-state reconciliation captured {venue_snapshot.venue}."
          ),
        )
      )

    sandbox_alerts, _ = self._collect_sandbox_operator_visibility(current_time=self._clock())
    if sandbox_alerts:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="runtime_alerts_present",
          severity="warning",
          summary=f"{len(sandbox_alerts)} unresolved runtime alert(s) remain active.",
          detail="Guarded-live candidacy stays blocked while sandbox runtime alerts remain unresolved.",
        )
      )

    inconsistent_sandbox_runs = [
      run
      for run in self._runs.list_runs(mode=RunMode.SANDBOX.value)
      if run.status == RunStatus.RUNNING and run.provenance.runtime_session is None
    ]
    if inconsistent_sandbox_runs:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="sandbox_runtime_session_missing",
          severity="critical",
          summary=(
            f"{len(inconsistent_sandbox_runs)} sandbox run(s) are missing persisted runtime session state."
          ),
          detail="Continuous sandbox workers must keep runtime-session state for restart safety and auditability.",
        )
      )

    inconsistent_live_runs = [
      run
      for run in self._runs.list_runs(mode=RunMode.LIVE.value)
      if run.status == RunStatus.RUNNING and run.provenance.runtime_session is None
    ]
    if inconsistent_live_runs:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="live_runtime_session_missing",
          severity="critical",
          summary=(
            f"{len(inconsistent_live_runs)} live run(s) are missing persisted runtime session state."
          ),
          detail="Guarded-live workers must keep runtime-session state for restart safety and venue auditability.",
        )
      )

    stale_terminal_sessions = [
      run
      for run in self._runs.list_runs(mode=RunMode.SANDBOX.value)
      if (
        run.status in {RunStatus.STOPPED, RunStatus.FAILED, RunStatus.COMPLETED}
        and run.provenance.runtime_session is not None
        and run.provenance.runtime_session.lifecycle_state == "active"
      )
    ]
    if stale_terminal_sessions:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="terminal_runtime_session_active",
          severity="warning",
          summary=(
            f"{len(stale_terminal_sessions)} terminal sandbox run(s) still report an active runtime session."
          ),
          detail="Terminal runs should not keep active worker-session state after stop, failure, or completion.",
        )
      )

    stale_terminal_live_sessions = [
      run
      for run in self._runs.list_runs(mode=RunMode.LIVE.value)
      if (
        run.status in {RunStatus.STOPPED, RunStatus.FAILED, RunStatus.COMPLETED}
        and run.provenance.runtime_session is not None
        and run.provenance.runtime_session.lifecycle_state == "active"
      )
    ]
    if stale_terminal_live_sessions:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="terminal_live_runtime_session_active",
          severity="warning",
          summary=(
            f"{len(stale_terminal_live_sessions)} terminal live run(s) still report an active runtime session."
          ),
          detail="Terminal guarded-live runs should not keep active worker-session state after stop or failure.",
        )
      )

    if venue_snapshot.verification_state != "verified":
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="venue_snapshot_unavailable",
          severity="critical" if venue_snapshot.verification_state == "unavailable" else "warning",
          summary=(
            "Venue-state verification is unavailable."
            if venue_snapshot.verification_state == "unavailable"
            else "Venue-state verification completed with partial data."
          ),
          detail=(
            ", ".join(venue_snapshot.issues)
            if venue_snapshot.issues
            else "The venue adapter did not return a fully verified account snapshot."
          ),
        )
      )

    findings.extend(
      self._build_guarded_live_venue_mismatch_findings(
        internal_snapshot=internal_snapshot,
        venue_snapshot=venue_snapshot,
      )
    )
    return internal_snapshot, venue_snapshot, findings

  def _build_guarded_live_internal_snapshot(
    self,
    *,
    state: GuardedLiveState | None = None,
  ) -> GuardedLiveInternalStateSnapshot:
    captured_at = self._clock()
    exposures: list[GuardedLiveInternalExposure] = []
    open_order_count = 0
    running_run_ids: list[str] = []
    running_live_count = 0

    for mode in (RunMode.SANDBOX, RunMode.PAPER, RunMode.LIVE):
      for run in self._runs.list_runs(mode=mode.value):
        if run.status == RunStatus.RUNNING:
          running_run_ids.append(run.config.run_id)
          if mode == RunMode.LIVE:
            running_live_count += 1
        open_order_count += sum(
          1
          for order in run.orders
          if order.status in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}
        )
        for position in run.positions.values():
          if not position.is_open:
            continue
          exposures.append(
            GuardedLiveInternalExposure(
              run_id=run.config.run_id,
              mode=run.config.mode.value,
              instrument_id=position.instrument_id,
              quantity=position.quantity,
            )
          )

    if (
      running_live_count == 0
      and state is not None
      and state.recovery.state in {"recovered", "recovered_with_warnings"}
    ):
      for exposure in state.recovery.exposures:
        exposures.append(
          GuardedLiveInternalExposure(
            run_id="guarded_live_recovery_projection",
            mode=RunMode.LIVE.value,
            instrument_id=exposure.instrument_id,
            quantity=exposure.quantity,
          )
        )
      open_order_count += sum(
        1
        for order in state.recovery.open_orders
        if order.status.lower() not in {"closed", "filled", "canceled", "cancelled", "rejected"}
      )

    return GuardedLiveInternalStateSnapshot(
      captured_at=captured_at,
      running_run_ids=tuple(sorted(running_run_ids)),
      exposures=tuple(sorted(exposures, key=lambda exposure: (exposure.instrument_id, exposure.run_id))),
      open_order_count=open_order_count,
    )

  def _build_guarded_live_venue_mismatch_findings(
    self,
    *,
    internal_snapshot: GuardedLiveInternalStateSnapshot,
    venue_snapshot: GuardedLiveVenueStateSnapshot,
  ) -> list[GuardedLiveReconciliationFinding]:
    findings: list[GuardedLiveReconciliationFinding] = []
    if venue_snapshot.verification_state == "unavailable":
      return findings
    tolerance = self._guarded_live_balance_tolerance

    internal_exposure_by_asset = self._aggregate_internal_exposure_by_asset(internal_snapshot.exposures)
    quote_assets = self._collect_internal_quote_assets(internal_snapshot.exposures)
    venue_balance_by_asset = {
      balance.asset: balance.total
      for balance in venue_snapshot.balances
      if abs(balance.total) > tolerance
    }

    for asset, expected_quantity in sorted(internal_exposure_by_asset.items()):
      actual_quantity = venue_balance_by_asset.get(asset, 0.0)
      if abs(actual_quantity - expected_quantity) <= tolerance:
        continue
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="venue_balance_mismatch",
          severity="critical",
          summary=f"Venue balance for {asset} does not match local open exposure.",
          detail=(
            f"Internal runtime exposure expects {expected_quantity:.8f} {asset}, "
            f"but venue snapshot reported {actual_quantity:.8f}."
          ),
        )
      )

    ignored_quote_assets = {"USD", "USDT", "USDC", "BUSD", *quote_assets}
    for asset, venue_quantity in sorted(venue_balance_by_asset.items()):
      if asset in internal_exposure_by_asset or asset in ignored_quote_assets:
        continue
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="unexpected_venue_balance_exposure",
          severity="critical",
          summary=f"Venue snapshot contains unexpected {asset} exposure.",
          detail=(
            f"Venue snapshot reported {venue_quantity:.8f} {asset} with no matching local runtime exposure."
          ),
        )
      )

    venue_open_order_count = len(venue_snapshot.open_orders)
    if internal_snapshot.open_order_count != venue_open_order_count:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="venue_open_order_mismatch",
          severity="critical",
          summary="Venue open-order count does not match local runtime expectations.",
          detail=(
            f"Local runtime expects {internal_snapshot.open_order_count} open orders, "
            f"but venue snapshot reported {venue_open_order_count}."
          ),
        )
      )

    return findings

  def _aggregate_internal_exposure_by_asset(
    self,
    exposures: tuple[GuardedLiveInternalExposure, ...],
  ) -> dict[str, float]:
    aggregated: dict[str, float] = {}
    for exposure in exposures:
      asset = self._base_asset_from_instrument_id(exposure.instrument_id)
      aggregated[asset] = aggregated.get(asset, 0.0) + exposure.quantity
    return aggregated

  def _collect_internal_quote_assets(
    self,
    exposures: tuple[GuardedLiveInternalExposure, ...],
  ) -> set[str]:
    quote_assets: set[str] = set()
    for exposure in exposures:
      quote_assets.add(self._quote_asset_from_instrument_id(exposure.instrument_id))
    return quote_assets

  @staticmethod
  def _base_asset_from_instrument_id(instrument_id: str) -> str:
    symbol = instrument_id.split(":", 1)[1] if ":" in instrument_id else instrument_id
    return symbol.split("/", 1)[0]

  @staticmethod
  def _quote_asset_from_instrument_id(instrument_id: str) -> str:
    symbol = instrument_id.split(":", 1)[1] if ":" in instrument_id else instrument_id
    parts = symbol.split("/", 1)
    return parts[1] if len(parts) == 2 else "unknown"

  def maintain_sandbox_worker_sessions(
    self,
    *,
    force_recovery: bool = False,
    recovery_reason: str = "heartbeat_timeout",
  ) -> dict[str, int]:
    maintained = 0
    recovered = 0
    ticks_processed = 0
    current_time = self._clock()
    for run in self._runs.list_runs(mode=RunMode.SANDBOX.value):
      if run.status != RunStatus.RUNNING:
        continue
      try:
        if force_recovery or self._run_supervisor.needs_worker_recovery(run=run, now=current_time):
          self._run_supervisor.recover_worker_session(
            run=run,
            worker_kind=self._sandbox_worker_kind,
            heartbeat_interval_seconds=self._sandbox_worker_heartbeat_interval_seconds,
            heartbeat_timeout_seconds=self._sandbox_worker_heartbeat_timeout_seconds,
            reason=recovery_reason,
            now=current_time,
            started_at=run.started_at,
            primed_candle_count=self._infer_sandbox_primed_candle_count(run),
            processed_tick_count=len(run.equity_curve),
            last_processed_candle_at=self._infer_last_processed_candle_at(run),
            last_seen_candle_at=self._infer_last_processed_candle_at(run),
          )
          run.notes.append(
            f"{current_time.isoformat()} | sandbox_worker_recovered | {recovery_reason}"
          )
          recovered += 1

        ticks_processed += self._advance_sandbox_worker_run(run)
        self._run_supervisor.heartbeat_worker_session(run=run, now=current_time)
      except Exception as exc:
        self._run_supervisor.fail(
          run,
          reason=f"{current_time.isoformat()} | sandbox_worker_failed | {exc}",
          now=current_time,
        )
      self._runs.save_run(run)
      maintained += 1
    return {
      "maintained": maintained,
      "recovered": recovered,
      "ticks_processed": ticks_processed,
    }

  def _advance_sandbox_worker_run(self, run: RunRecord) -> int:
    session = run.provenance.runtime_session
    if session is None:
      return 0

    strategy = self._strategies.load(run.config.strategy_id)
    parameters = self._resolve_execution_parameters(run)
    candles = self._load_sandbox_worker_candles(run=run)
    if not candles:
      return 0

    latest_seen_candle_at = candles[-1].timestamp
    self._run_supervisor.record_worker_market_progress(
      run=run,
      last_seen_candle_at=latest_seen_candle_at,
    )
    if (
      session.last_processed_candle_at is not None
      and latest_seen_candle_at <= session.last_processed_candle_at
    ):
      return 0

    enriched = strategy.build_feature_frame(candles_to_frame(candles), parameters)
    warmup = strategy.warmup_spec().required_bars
    if len(enriched) < max(warmup, 2):
      return 0

    cache = self._restore_state_cache(run)
    latest_processed_candle_at = session.last_processed_candle_at
    processed_ticks = 0
    for index in range(max(warmup, 2), len(enriched)):
      history = enriched.iloc[: index + 1]
      latest_row = history.iloc[-1]
      latest_timestamp = latest_row["timestamp"].to_pydatetime()
      if latest_processed_candle_at is not None and latest_timestamp <= latest_processed_candle_at:
        continue
      state = cache.snapshot(
        timestamp=latest_timestamp,
        parameters=parameters,
      )
      decision = strategy.evaluate(history, parameters, state)
      self._execution_engine.apply_decision(
        run=run,
        config=run.config,
        decision=decision,
        cache=cache,
        market_price=float(latest_row["close"]),
      )
      processed_ticks += 1
      latest_processed_candle_at = latest_timestamp

    if processed_ticks == 0:
      return 0

    self._run_supervisor.record_worker_market_progress(
      run=run,
      last_seen_candle_at=latest_seen_candle_at,
      last_processed_candle_at=latest_processed_candle_at,
      processed_tick_count_increment=processed_ticks,
    )
    run.metrics = summarize_performance(
      initial_cash=run.config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    return processed_ticks

  def _load_sandbox_worker_candles(self, *, run: RunRecord) -> list:
    symbol = run.config.symbols[0]
    history_start_at = self._resolve_sandbox_worker_history_start_at(run)
    return self._market_data.get_candles(
      symbol=symbol,
      timeframe=run.config.timeframe,
      start_at=history_start_at,
      end_at=run.config.end_at,
      limit=None,
    )

  def _resolve_sandbox_worker_history_start_at(self, run: RunRecord) -> datetime | None:
    market_data = run.provenance.market_data
    return (
      run.config.start_at
      or (market_data.effective_start_at if market_data is not None else None)
      or (market_data.requested_start_at if market_data is not None else None)
    )

  def _resolve_execution_parameters(self, run: RunRecord) -> dict:
    strategy_snapshot = run.provenance.strategy
    if strategy_snapshot is None:
      return deepcopy(run.config.parameters)
    return deepcopy(strategy_snapshot.parameter_snapshot.resolved or run.config.parameters)

  def _restore_state_cache(self, run: RunRecord) -> StateCache:
    instrument_id = f"{run.config.venue}:{run.config.symbols[0]}"
    cash = run.equity_curve[-1].cash if run.equity_curve else run.config.initial_cash
    cache = StateCache(instrument_id=instrument_id, cash=cash)
    position = run.positions.get(instrument_id)
    cache.apply(
      cash=cash,
      position=position if position is not None and position.is_open else None,
    )
    return cache

  def _infer_last_processed_candle_at(self, run: RunRecord) -> datetime | None:
    if run.equity_curve:
      return run.equity_curve[-1].timestamp
    market_data = run.provenance.market_data
    return market_data.effective_end_at if market_data is not None else None

  def _infer_sandbox_primed_candle_count(self, run: RunRecord) -> int:
    session = run.provenance.runtime_session
    if session is not None and session.primed_candle_count > 0:
      return session.primed_candle_count
    market_data = run.provenance.market_data
    if market_data is None:
      return 0
    return market_data.candle_count

  def maintain_guarded_live_worker_sessions(
    self,
    *,
    force_recovery: bool = False,
    recovery_reason: str = "heartbeat_timeout",
  ) -> dict[str, int]:
    if not self._guarded_live_execution_enabled:
      return {
        "maintained": 0,
        "recovered": 0,
        "ticks_processed": 0,
        "orders_submitted": 0,
        "orders_synced": 0,
      }

    maintained = 0
    recovered = 0
    ticks_processed = 0
    orders_submitted = 0
    orders_synced = 0
    current_time = self._clock()
    for run in self._runs.list_runs(mode=RunMode.LIVE.value):
      if run.status != RunStatus.RUNNING:
        continue
      try:
        state = self._guarded_live_state.load_state()
        if force_recovery or self._run_supervisor.needs_worker_recovery(run=run, now=current_time):
          self._run_supervisor.recover_worker_session(
            run=run,
            worker_kind=self._guarded_live_worker_kind,
            heartbeat_interval_seconds=self._guarded_live_worker_heartbeat_interval_seconds,
            heartbeat_timeout_seconds=self._guarded_live_worker_heartbeat_timeout_seconds,
            reason=recovery_reason,
            now=current_time,
            started_at=run.started_at,
            primed_candle_count=self._infer_sandbox_primed_candle_count(run),
            processed_tick_count=run.provenance.runtime_session.processed_tick_count if run.provenance.runtime_session else 0,
            last_processed_candle_at=self._infer_last_processed_candle_at(run),
            last_seen_candle_at=self._infer_last_processed_candle_at(run),
          )
          run.notes.append(
            f"{current_time.isoformat()} | guarded_live_worker_recovered | {recovery_reason}"
          )
          self._append_guarded_live_audit_event(
            kind="guarded_live_worker_recovered",
            actor="system",
            summary=f"Guarded-live worker recovered for {run.config.symbols[0]}.",
            detail=f"Recovery reason: {recovery_reason}.",
            run_id=run.config.run_id,
            session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
          )
          recovered += 1

        session_handoff = state.session_handoff
        if session_handoff.owner_run_id == run.config.run_id and session_handoff.state == "active":
          session_sync = self._sync_guarded_live_session(run=run, handoff=session_handoff)
          orders_synced += session_sync["synced"]
          session_handoff = session_sync["handoff"]
        else:
          orders_synced += self._sync_guarded_live_orders(run)
          session_handoff = self._activate_guarded_live_venue_session(
            run=run,
            reason=recovery_reason if force_recovery else "worker_heartbeat",
          )
        advance = self._advance_guarded_live_worker_run(run)
        ticks_processed += advance["ticks_processed"]
        orders_submitted += advance["orders_submitted"]
        self._run_supervisor.heartbeat_worker_session(run=run, now=current_time)
        self._claim_guarded_live_session_ownership(
          run=run,
          actor="system",
          reason=recovery_reason if force_recovery else "worker_heartbeat",
          resumed=force_recovery,
          session_handoff=session_handoff,
        )
      except Exception as exc:
        self._run_supervisor.fail(
          run,
          reason=f"{current_time.isoformat()} | guarded_live_worker_failed | {exc}",
          now=current_time,
        )
        session_handoff = self._release_guarded_live_venue_session(run=run)
        self._release_guarded_live_session_ownership(
          run=run,
          actor="system",
          reason=str(exc),
          ownership_state="orphaned",
          session_handoff=session_handoff,
        )
        self._append_guarded_live_audit_event(
          kind="guarded_live_worker_failed",
          actor="system",
          summary=f"Guarded-live worker failed for {run.config.symbols[0]}.",
          detail=str(exc),
          run_id=run.config.run_id,
          session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
        )
      self._runs.save_run(run)
      maintained += 1

    return {
      "maintained": maintained,
      "recovered": recovered,
      "ticks_processed": ticks_processed,
      "orders_submitted": orders_submitted,
      "orders_synced": orders_synced,
    }

  def _sync_guarded_live_orders(self, run: RunRecord) -> int:
    tracked_orders = [
      order
      for order in run.orders
      if order.status in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}
    ]
    if not tracked_orders:
      return 0

    synced_states = {
      state.order_id: state
      for state in self._venue_execution.sync_order_states(
        symbol=run.config.symbols[0],
        order_ids=tuple(order.order_id for order in tracked_orders),
      )
    }
    synced_count = 0
    for order in tracked_orders:
      synced_state = synced_states.get(order.order_id)
      if synced_state is None:
        continue
      synced_count += self._apply_guarded_live_synced_order_state(
        run=run,
        order=order,
        synced_state=synced_state,
      )
    if synced_count > 0:
      run.metrics = summarize_performance(
        initial_cash=run.config.initial_cash,
        equity_curve=run.equity_curve,
        closed_trades=run.closed_trades,
      )
    return synced_count

  def _sync_guarded_live_session(
    self,
    *,
    run: RunRecord,
    handoff: GuardedLiveVenueSessionHandoff,
  ) -> dict[str, object]:
    session_sync = self._venue_execution.sync_session(
      handoff=handoff,
      order_ids=tuple(order.order_id for order in run.orders),
    )
    restore_view = GuardedLiveVenueSessionRestore(
      state="restored" if session_sync.state == "active" else session_sync.state,
      restored_at=session_sync.synced_at,
      source=session_sync.handoff.source,
      venue=session_sync.handoff.venue,
      symbol=session_sync.handoff.symbol,
      owner_run_id=session_sync.handoff.owner_run_id,
      owner_session_id=session_sync.handoff.owner_session_id,
      open_orders=session_sync.open_orders,
      synced_orders=session_sync.synced_orders,
      issues=session_sync.issues,
    )
    synced_count = self._apply_guarded_live_restored_session(
      run=run,
      session_restore=restore_view,
    )
    next_handoff = session_sync.handoff
    if synced_count > 0 or session_sync.issues or next_handoff.last_event_at != handoff.last_event_at:
      sync_time = session_sync.synced_at or self._clock()
      detail = (
        f"source={next_handoff.source}; transport={next_handoff.transport}; "
        f"state={next_handoff.state}; active_orders={next_handoff.active_order_count}; "
        f"cursor={next_handoff.cursor or 'n/a'}; supervision={next_handoff.supervision_state}; "
        f"order_book={next_handoff.order_book_state}; failovers={next_handoff.failover_count}; "
        f"coverage={','.join(next_handoff.coverage) or 'none'}; "
        f"continuation={next_handoff.channel_continuation_state}"
      )
      if (
        next_handoff.order_book_best_bid_price is not None
        or next_handoff.order_book_best_ask_price is not None
      ):
        detail += (
          f"; top_of_book={next_handoff.order_book_best_bid_price or 0.0:.8f}/"
          f"{next_handoff.order_book_best_ask_price or 0.0:.8f}"
        )
      if next_handoff.order_book_last_update_id is not None:
        detail += f"; depth_update_id={next_handoff.order_book_last_update_id}"
      if next_handoff.order_book_gap_count > 0:
        detail += f"; depth_gaps={next_handoff.order_book_gap_count}"
      if next_handoff.order_book_rebuild_count > 0:
        detail += f"; depth_rebuilds={next_handoff.order_book_rebuild_count}"
      if next_handoff.order_book_last_rebuilt_at is not None:
        detail += f"; last_depth_rebuild={next_handoff.order_book_last_rebuilt_at.isoformat()}"
      if session_sync.issues:
        detail += f"; issues={', '.join(session_sync.issues)}"
      run.notes.append(
        f"{sync_time.isoformat()} | guarded_live_venue_session_synced | {detail}"
      )
      self._append_guarded_live_audit_event(
        kind="guarded_live_venue_session_synced",
        actor="system",
        summary=f"Guarded-live venue session synced for {run.config.symbols[0]}.",
        detail=detail,
        run_id=run.config.run_id,
        session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
      )
    return {
      "synced": synced_count,
      "handoff": next_handoff,
    }

  def _apply_guarded_live_synced_order_state(
    self,
    *,
    run: RunRecord,
    order: Order,
    synced_state: GuardedLiveVenueOrderResult,
  ) -> int:
    status_changed = False
    fill_recorded = False
    previous_status = order.status
    previous_filled_quantity = order.filled_quantity
    sync_time = synced_state.updated_at or synced_state.submitted_at or self._clock()
    order.last_synced_at = sync_time
    order.updated_at = sync_time
    if synced_state.average_fill_price is not None:
      order.average_fill_price = synced_state.average_fill_price

    total_fee = synced_state.fee_paid if synced_state.fee_paid is not None else order.fee_paid
    total_filled = synced_state.filled_amount
    if total_filled is None:
      if synced_state.status == OrderStatus.FILLED.value:
        total_filled = order.quantity
      elif synced_state.status == OrderStatus.PARTIALLY_FILLED.value:
        total_filled = order.filled_quantity
      else:
        total_filled = order.filled_quantity
    remaining_quantity = synced_state.remaining_amount
    if remaining_quantity is None:
      remaining_quantity = max(order.quantity - total_filled, 0.0)

    incremental_fill = max(total_filled - order.filled_quantity, 0.0)
    if incremental_fill > self._guarded_live_balance_tolerance:
      incremental_fee = max(total_fee - order.fee_paid, 0.0)
      self._materialize_guarded_live_fill_delta(
        run=run,
        order=order,
        fill_quantity=incremental_fill,
        fee_paid=incremental_fee,
        fill_price=synced_state.average_fill_price or order.average_fill_price or order.requested_price,
        fill_timestamp=sync_time,
      )
      fill_recorded = True

    order.fee_paid = total_fee
    order.filled_quantity = total_filled
    order.remaining_quantity = remaining_quantity
    mapped_status = self._map_guarded_live_order_status(
      synced_state.status,
      filled_quantity=total_filled,
      remaining_quantity=remaining_quantity,
    )
    if mapped_status != order.status:
      order.status = mapped_status
      status_changed = True
    if order.status == OrderStatus.FILLED and order.filled_at is None:
      order.filled_at = sync_time

    if status_changed or fill_recorded or synced_state.issues:
      transition_copy = (
        f"{previous_status.value}->{order.status.value}"
        if status_changed
        else f"{order.status.value}"
      )
      detail = (
        f"Order {order.order_id} synced as {transition_copy}. "
        f"filled {previous_filled_quantity:.8f}->{order.filled_quantity:.8f}, "
        f"remaining {order.remaining_quantity or 0.0:.8f}."
      )
      if synced_state.issues:
        detail += " Issues: " + ", ".join(synced_state.issues) + "."
      run.notes.append(f"{sync_time.isoformat()} | guarded_live_order_synced | {detail}")
      self._append_guarded_live_audit_event(
        kind="guarded_live_order_synced",
        actor="system",
        summary=f"Guarded-live order synced for {run.config.symbols[0]}.",
        detail=detail,
        run_id=run.config.run_id,
        session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
      )
      return 1
    return 0

  def _materialize_guarded_live_fill_delta(
    self,
    *,
    run: RunRecord,
    order: Order,
    fill_quantity: float,
    fee_paid: float,
    fill_price: float,
    fill_timestamp: datetime,
  ) -> None:
    cache = self._restore_state_cache(run)
    active_position = cache.position if cache.position is not None and cache.position.is_open else None
    if order.side == OrderSide.BUY:
      gross_cost = fill_quantity * fill_price
      next_cash = cache.cash - gross_cost - fee_paid
      if active_position is None:
        next_position = Position(
          instrument_id=order.instrument_id,
          quantity=fill_quantity,
          average_price=fill_price,
          opened_at=fill_timestamp,
          updated_at=fill_timestamp,
        )
      else:
        total_quantity = active_position.quantity + fill_quantity
        average_price = (
          (active_position.quantity * active_position.average_price) + (fill_quantity * fill_price)
        ) / total_quantity
        next_position = replace(
          active_position,
          quantity=total_quantity,
          average_price=average_price,
          updated_at=fill_timestamp,
        )
      cache.apply(cash=next_cash, position=next_position)
      run.positions[order.instrument_id] = next_position
    else:
      if active_position is None or not active_position.is_open:
        raise RuntimeError(f"guarded_live_sell_sync_without_position:{order.order_id}")
      sell_quantity = min(fill_quantity, active_position.quantity)
      gross_value = sell_quantity * fill_price
      proceeds = gross_value - fee_paid
      pnl = proceeds - (sell_quantity * active_position.average_price)
      remaining_quantity = max(active_position.quantity - sell_quantity, 0.0)
      next_position = replace(
        active_position,
        quantity=remaining_quantity,
        updated_at=fill_timestamp,
        realized_pnl=active_position.realized_pnl + pnl,
      )
      cache.apply(
        cash=cache.cash + proceeds,
        position=next_position if next_position.is_open else None,
      )
      run.positions[order.instrument_id] = next_position
      run.closed_trades.append(
        ClosedTrade(
          instrument_id=order.instrument_id,
          entry_price=active_position.average_price,
          exit_price=fill_price,
          quantity=sell_quantity,
          fee_paid=fee_paid,
          pnl=pnl,
          opened_at=active_position.opened_at or fill_timestamp,
          closed_at=fill_timestamp,
        )
      )

    run.fills.append(
      Fill(
        order_id=order.order_id,
        quantity=fill_quantity,
        price=fill_price,
        fee_paid=fee_paid,
        timestamp=fill_timestamp,
      )
    )
    run.equity_curve.append(
      build_equity_point(
        timestamp=fill_timestamp,
        cash=cache.cash,
        position=cache.position if cache.position and cache.position.is_open else None,
        market_price=fill_price,
      )
    )

  @staticmethod
  def _map_guarded_live_order_status(
    status: str,
    *,
    filled_quantity: float,
    remaining_quantity: float,
  ) -> OrderStatus:
    normalized = status.lower()
    if normalized in {"canceled", "cancelled", "expired"}:
      return OrderStatus.CANCELED
    if normalized == "rejected":
      return OrderStatus.REJECTED
    if normalized in {"filled", "closed"} or (filled_quantity > 0 and remaining_quantity <= 0):
      return OrderStatus.FILLED
    if normalized in {"partially_filled", "partial"} or (filled_quantity > 0 and remaining_quantity > 0):
      return OrderStatus.PARTIALLY_FILLED
    return OrderStatus.OPEN

  def _advance_guarded_live_worker_run(self, run: RunRecord) -> dict[str, int]:
    session = run.provenance.runtime_session
    if session is None:
      return {"ticks_processed": 0, "orders_submitted": 0}

    strategy = self._strategies.load(run.config.strategy_id)
    parameters = self._resolve_execution_parameters(run)
    candles = self._load_sandbox_worker_candles(run=run)
    if not candles:
      return {"ticks_processed": 0, "orders_submitted": 0}

    latest_seen_candle_at = candles[-1].timestamp
    self._run_supervisor.record_worker_market_progress(
      run=run,
      last_seen_candle_at=latest_seen_candle_at,
    )
    if (
      session.last_processed_candle_at is not None
      and latest_seen_candle_at <= session.last_processed_candle_at
    ):
      return {"ticks_processed": 0, "orders_submitted": 0}

    enriched = strategy.build_feature_frame(candles_to_frame(candles), parameters)
    warmup = strategy.warmup_spec().required_bars
    if len(enriched) < max(warmup, 2):
      return {"ticks_processed": 0, "orders_submitted": 0}

    cache = self._restore_state_cache(run)
    latest_processed_candle_at = session.last_processed_candle_at
    processed_ticks = 0
    orders_submitted = 0
    for index in range(max(warmup, 2), len(enriched)):
      history = enriched.iloc[: index + 1]
      latest_row = history.iloc[-1]
      latest_timestamp = latest_row["timestamp"].to_pydatetime()
      if latest_processed_candle_at is not None and latest_timestamp <= latest_processed_candle_at:
        continue
      state = cache.snapshot(
        timestamp=latest_timestamp,
        parameters=parameters,
      )
      decision = strategy.evaluate(history, parameters, state)
      orders_submitted += self._apply_guarded_live_decision(
        run=run,
        decision=decision,
        cache=cache,
        market_price=float(latest_row["close"]),
      )
      processed_ticks += 1
      latest_processed_candle_at = latest_timestamp

    if processed_ticks == 0:
      return {"ticks_processed": 0, "orders_submitted": 0}

    self._run_supervisor.record_worker_market_progress(
      run=run,
      last_seen_candle_at=latest_seen_candle_at,
      last_processed_candle_at=latest_processed_candle_at,
      processed_tick_count_increment=processed_ticks,
    )
    run.metrics = summarize_performance(
      initial_cash=run.config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    return {"ticks_processed": processed_ticks, "orders_submitted": orders_submitted}

  def _apply_guarded_live_decision(
    self,
    *,
    run: RunRecord,
    decision,
    cache: StateCache,
    market_price: float,
  ) -> int:
    reviewed = self._execution_engine.review_decision(decision)
    _, _, order, _, _ = apply_signal(
      run_id=run.config.run_id,
      instrument_id=cache.instrument_id,
      signal=reviewed.signal,
      execution=reviewed.execution,
      market_price=market_price,
      position=cache.position,
      cash=cache.cash,
      fee_rate=run.config.fee_rate,
      slippage_bps=run.config.slippage_bps,
    )

    submitted_orders = 0
    effective_price = market_price
    fill_materialized = False
    if order is not None:
      venue_result = self._submit_guarded_live_market_order(
        run=run,
        order=order,
        market_price=market_price,
      )
      order.order_id = venue_result.order_id
      order.created_at = venue_result.submitted_at
      order.updated_at = venue_result.updated_at or venue_result.submitted_at
      order.last_synced_at = venue_result.updated_at or venue_result.submitted_at
      order.status = self._map_guarded_live_order_status(
        venue_result.status,
        filled_quantity=venue_result.filled_amount or 0.0,
        remaining_quantity=venue_result.remaining_amount or 0.0,
      )
      if venue_result.average_fill_price is not None:
        order.average_fill_price = venue_result.average_fill_price
        effective_price = venue_result.average_fill_price
      order.fee_paid = venue_result.fee_paid or 0.0
      order.filled_quantity = venue_result.filled_amount or 0.0
      order.remaining_quantity = (
        venue_result.remaining_amount
        if venue_result.remaining_amount is not None
        else max(order.quantity - order.filled_quantity, 0.0)
      )
      if order.status == OrderStatus.FILLED:
        order.filled_at = venue_result.updated_at or venue_result.submitted_at
      run.orders.append(order)
      submitted_orders = 1
      if order.filled_quantity > self._guarded_live_balance_tolerance:
        self._materialize_guarded_live_fill_delta(
          run=run,
          order=order,
          fill_quantity=order.filled_quantity,
          fee_paid=order.fee_paid,
          fill_price=effective_price,
          fill_timestamp=order.filled_at or venue_result.submitted_at,
        )
        fill_materialized = True
      self._append_guarded_live_audit_event(
        kind="guarded_live_order_submitted",
        actor="system",
        summary=f"Guarded-live venue order submitted for {run.config.symbols[0]}.",
        detail=(
          f"{reviewed.signal.action.value} {order.quantity:.8f} {run.config.symbols[0]} "
          f"via {venue_result.order_id} ({order.status.value})."
        ),
        run_id=run.config.run_id,
        session_id=run.provenance.runtime_session.session_id if run.provenance.runtime_session else None,
      )

    cache = self._restore_state_cache(run)
    cache.mark_price(effective_price)
    if not fill_materialized:
      run.equity_curve.append(
        build_equity_point(
          timestamp=reviewed.signal.timestamp,
          cash=cache.cash,
          position=cache.position if cache.position and cache.position.is_open else None,
          market_price=effective_price,
        )
      )
    run.notes.append(
      f"{reviewed.context.timestamp.isoformat()} | {reviewed.signal.action.value} | {reviewed.rationale}"
    )
    return submitted_orders

  def _submit_guarded_live_market_order(
    self,
    *,
    run: RunRecord,
    order: Order,
    market_price: float,
  ) -> GuardedLiveVenueOrderResult:
    session = run.provenance.runtime_session
    if session is None:
      raise RuntimeError("guarded_live_runtime_session_missing")
    request = GuardedLiveVenueOrderRequest(
      run_id=run.config.run_id,
      session_id=session.session_id,
      venue=run.config.venue,
      symbol=run.config.symbols[0],
      side=order.side.value,
      amount=order.quantity,
      order_type=OrderType.MARKET.value,
      reference_price=market_price,
    )
    return self._venue_execution.submit_market_order(request)

  def _submit_guarded_live_limit_order(
    self,
    *,
    run: RunRecord,
    order: Order,
    limit_price: float,
  ) -> GuardedLiveVenueOrderResult:
    session = run.provenance.runtime_session
    if session is None:
      raise RuntimeError("guarded_live_runtime_session_missing")
    request = GuardedLiveVenueOrderRequest(
      run_id=run.config.run_id,
      session_id=session.session_id,
      venue=run.config.venue,
      symbol=run.config.symbols[0],
      side=order.side.value,
      amount=order.quantity,
      order_type=OrderType.LIMIT.value,
      reference_price=limit_price,
    )
    return self._venue_execution.submit_limit_order(request)

  def _guarded_live_delivery_targets(self) -> tuple[str, ...]:
    return (
      "operator_visibility",
      "guarded_live_status",
      "control_room",
      *self._operator_alert_delivery.list_targets(),
    )

  def _build_guarded_live_operator_alerts(
    self,
    *,
    state: GuardedLiveState,
    current_time: datetime,
  ) -> list[OperatorAlert]:
    alerts: list[OperatorAlert] = []
    delivery_targets = self._guarded_live_delivery_targets()
    live_runs = self._runs.list_runs(mode=RunMode.LIVE.value)
    live_context_active = bool(live_runs) or state.ownership.state in {"owned", "orphaned"}

    alerts.extend(
      self._build_guarded_live_market_data_alerts(
        live_runs=live_runs,
        current_time=current_time,
      )
    )

    if state.kill_switch.state == "engaged":
      detected_at = state.kill_switch.last_engaged_at or state.kill_switch.updated_at
      alerts.append(
        OperatorAlert(
          alert_id="guarded-live:kill-switch",
          severity="warning",
          category="kill_switch",
          summary="Guarded-live kill switch is engaged.",
          detail=(
            f"{state.kill_switch.reason} Updated by {state.kill_switch.updated_by} at "
            f"{state.kill_switch.updated_at.isoformat()}."
          ),
          detected_at=detected_at,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if state.reconciliation.state == "issues_detected":
      finding_copy = "; ".join(finding.summary for finding in state.reconciliation.findings[:3])
      alerts.append(
        OperatorAlert(
          alert_id="guarded-live:reconciliation",
          severity=(
            "critical"
            if any(finding.severity == "critical" for finding in state.reconciliation.findings)
            else "warning"
          ),
          category="reconciliation",
          summary="Guarded-live reconciliation has unresolved findings.",
          detail=(
            f"{state.reconciliation.summary} "
            f"{finding_copy if finding_copy else 'Review the guarded-live venue snapshot and internal exposure state.'}"
          ),
          detected_at=state.reconciliation.checked_at or current_time,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if state.recovery.state == "failed":
      alerts.append(
        OperatorAlert(
          alert_id="guarded-live:recovery-failed",
          severity="critical",
          category="runtime_recovery",
          summary="Guarded-live runtime recovery failed.",
          detail=(
            f"{state.recovery.summary} Issues: "
            f"{', '.join(state.recovery.issues) if state.recovery.issues else 'none'}."
          ),
          detected_at=state.recovery.recovered_at or current_time,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if state.ownership.state == "orphaned":
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:ownership:{state.ownership.owner_run_id or 'unknown'}",
          severity="critical",
          category="session_ownership",
          summary="Guarded-live session ownership is orphaned.",
          detail=(
            f"Run {state.ownership.owner_run_id or 'n/a'} still owns the guarded-live session, "
            f"but the live worker is not healthy. Last reason: {state.ownership.last_reason or 'n/a'}."
          ),
          detected_at=(
            state.ownership.last_heartbeat_at
            or state.ownership.last_resumed_at
            or state.ownership.claimed_at
            or current_time
          ),
          run_id=state.ownership.owner_run_id,
          session_id=state.ownership.owner_session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if live_context_active and state.session_handoff.state == "unavailable":
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:session-transport:{state.ownership.owner_run_id or 'unknown'}",
          severity="critical",
          category="session_transport",
          summary="Guarded-live venue session transport is unavailable.",
          detail=(
            "Venue-native session supervision could not be maintained. Issues: "
            f"{', '.join(state.session_handoff.issues) if state.session_handoff.issues else 'none'}."
          ),
          detected_at=state.session_handoff.last_sync_at or state.session_handoff.handed_off_at or current_time,
          run_id=state.ownership.owner_run_id,
          session_id=state.ownership.owner_session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )
    elif live_context_active and state.session_handoff.issues:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:session-issues:{state.ownership.owner_run_id or 'unknown'}",
          severity="warning",
          category="session_transport",
          summary="Guarded-live venue session requires operator review.",
          detail=", ".join(state.session_handoff.issues),
          detected_at=state.session_handoff.last_sync_at or state.session_handoff.handed_off_at or current_time,
          run_id=state.ownership.owner_run_id,
          session_id=state.ownership.owner_session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    order_book_issue_copy: list[str] = []
    if state.session_handoff.order_book_state == "unavailable":
      order_book_issue_copy.append("venue order-book supervision is unavailable")
    if state.order_book.issues:
      order_book_issue_copy.extend(state.order_book.issues)
    if live_context_active and order_book_issue_copy:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:order-book:{state.ownership.owner_run_id or 'unknown'}",
          severity="warning",
          category="order_book",
          summary="Guarded-live order-book supervision requires review.",
          detail="; ".join(order_book_issue_copy),
          detected_at=(
            state.order_book.synced_at
            or state.session_handoff.last_sync_at
            or state.session_handoff.handed_off_at
            or current_time
          ),
          run_id=state.ownership.owner_run_id,
          session_id=state.ownership.owner_session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    alerts.extend(
      self._build_guarded_live_channel_operator_alerts(
        state=state,
        current_time=current_time,
        live_context_active=live_context_active,
        delivery_targets=delivery_targets,
      )
    )

    for run in live_runs:
      alerts.extend(self._build_live_operator_alerts_for_run(run=run, current_time=current_time))

    alerts.sort(key=lambda alert: alert.detected_at, reverse=True)
    return alerts

  def _build_guarded_live_market_data_alerts(
    self,
    *,
    live_runs: list[RunRecord],
    current_time: datetime,
  ) -> list[OperatorAlert]:
    alerts: list[OperatorAlert] = []
    delivery_targets = self._guarded_live_delivery_targets()
    live_symbols = {
      symbol
      for run in live_runs
      for symbol in run.config.symbols
    }
    for timeframe in self._resolve_guarded_live_market_data_timeframes(live_runs=live_runs):
      try:
        status = self._market_data.get_status(timeframe)
      except Exception as exc:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data:{timeframe}",
            severity="critical",
            category="market_data_freshness",
            summary=f"Guarded-live market-data freshness policy could not be evaluated for {timeframe}.",
            detail=f"Market-data status query failed: {exc}.",
            detected_at=current_time,
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
        continue
      if status.provider == "seeded":
        continue

      relevant_instruments = [
        instrument
        for instrument in status.instruments
        if not live_symbols or self._symbol_from_instrument_id(instrument.instrument_id) in live_symbols
      ]
      if live_symbols and not relevant_instruments:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data:{timeframe}",
            severity="critical",
            category="market_data_freshness",
            summary=f"Guarded-live market-data freshness policy is uncovered for {timeframe}.",
            detail=(
              "No tracked market-data status covered the active live symbol set: "
              f"{', '.join(sorted(live_symbols))}."
            ),
            detected_at=current_time,
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
        continue

      critical_details: list[str] = []
      quality_details: list[str] = []
      continuity_details: list[str] = []
      venue_details: list[str] = []
      quality_has_critical = False
      continuity_has_critical = False
      venue_has_critical = False
      detected_candidates: list[datetime] = []
      for instrument in relevant_instruments:
        symbol = self._symbol_from_instrument_id(instrument.instrument_id)
        if instrument.last_sync_at is not None:
          detected_candidates.append(instrument.last_sync_at)
        if instrument.last_timestamp is not None:
          detected_candidates.append(instrument.last_timestamp)
        if instrument.recent_failures:
          detected_candidates.extend(failure.failed_at for failure in instrument.recent_failures)

        if instrument.sync_status == "error":
          critical_details.append(f"{symbol} last sync failed.")
        elif instrument.sync_status == "empty":
          critical_details.append(f"{symbol} has no persisted candles for {timeframe}.")
        elif instrument.sync_status == "stale":
          lag_detail = (
            f" lagged {instrument.lag_seconds}s"
            if instrument.lag_seconds is not None
            else " breached the freshness window"
          )
          critical_details.append(f"{symbol}{lag_detail}.")

        missing_candles = instrument.backfill_contiguous_missing_candles
        if missing_candles is None and instrument.backfill_gap_windows:
          missing_candles = sum(window.missing_candles for window in instrument.backfill_gap_windows)
        if missing_candles and missing_candles > 0:
          continuity_details.append(
            f"{symbol} has {missing_candles} missing candle(s) across "
            f"{len(instrument.backfill_gap_windows)} gap window(s)."
          )
        if (
          instrument.backfill_target_candles is not None
          and instrument.backfill_completion_ratio is not None
          and instrument.backfill_complete is False
        ):
          quality_details.append(
            f"{symbol} backfill target covers {instrument.backfill_completion_ratio * 100:.2f}% "
            f"of {instrument.backfill_target_candles} candles."
          )
          if instrument.backfill_completion_ratio < self._guarded_live_market_data_backfill_completion_floor:
            quality_has_critical = True
        if (
          instrument.backfill_contiguous_completion_ratio is not None
          and instrument.backfill_contiguous_complete is False
        ):
          continuity_details.append(
            f"{symbol} contiguous backfill quality is "
            f"{instrument.backfill_contiguous_completion_ratio * 100:.2f}%."
          )
          if (
            instrument.backfill_contiguous_completion_ratio
            < self._guarded_live_market_data_contiguous_completion_floor
          ):
            continuity_has_critical = True
        if instrument.failure_count_24h > 0:
          venue_details.append(
            f"{symbol} recorded {instrument.failure_count_24h} sync failure(s) in the last 24h."
          )
          if instrument.failure_count_24h >= self._guarded_live_market_data_failure_burst_threshold:
            venue_has_critical = True
        elif instrument.recent_failures:
          latest_failure = instrument.recent_failures[0]
          venue_details.append(
            f"{symbol} last failure was {latest_failure.operation}: {latest_failure.error}."
          )
        venue_semantics = self._extract_market_data_venue_semantics(
          venue=status.venue,
          issues=instrument.issues,
        )
        if venue_semantics:
          venue_details.append(
            f"{symbol} venue semantics: {', '.join(venue_semantics)}."
          )
          if any(
            semantic in {"authentication fault", "symbol unavailable"}
            for semantic in venue_semantics
          ):
            venue_has_critical = True

      detail_copy = list(dict.fromkeys(critical_details))
      detected_at = max(detected_candidates) if detected_candidates else current_time
      if detail_copy:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data:{timeframe}",
            severity="critical" if critical_details else "warning",
            category="market_data_freshness",
            summary=f"Guarded-live market-data freshness policy is degraded for {timeframe}.",
            detail=(
              " ".join(detail_copy[:3])
              + (f" Additional issues: {len(detail_copy) - 3}." if len(detail_copy) > 3 else "")
            ),
            detected_at=detected_at,
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
      quality_detail_copy = list(dict.fromkeys(quality_details))
      if quality_detail_copy:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data-quality:{status.venue}:{timeframe}",
            severity="critical" if quality_has_critical else "warning",
            category="market_data_quality",
            summary=f"Guarded-live market-data quality policy is degraded for {status.venue} {timeframe}.",
            detail=(
              " ".join(quality_detail_copy[:3])
              + (f" Additional issues: {len(quality_detail_copy) - 3}." if len(quality_detail_copy) > 3 else "")
            ),
            detected_at=detected_at,
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
      continuity_detail_copy = list(dict.fromkeys(continuity_details))
      if continuity_detail_copy:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data-continuity:{status.venue}:{timeframe}",
            severity="critical" if continuity_has_critical else "warning",
            category="market_data_candle_continuity",
            summary=f"Guarded-live multi-candle continuity requires review for {status.venue} {timeframe}.",
            detail=(
              " ".join(continuity_detail_copy[:3])
              + (f" Additional issues: {len(continuity_detail_copy) - 3}." if len(continuity_detail_copy) > 3 else "")
            ),
            detected_at=detected_at,
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
      venue_detail_copy = list(dict.fromkeys(venue_details))
      if venue_detail_copy:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data-venue:{status.venue}:{timeframe}",
            severity="critical" if venue_has_critical else "warning",
            category="market_data_venue",
            summary=f"Guarded-live market-data venue semantics require review for {status.venue} {timeframe}.",
            detail=(
              " ".join(venue_detail_copy[:3])
              + (f" Additional issues: {len(venue_detail_copy) - 3}." if len(venue_detail_copy) > 3 else "")
            ),
            detected_at=detected_at,
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
    return alerts

  def _resolve_guarded_live_market_data_timeframes(
    self,
    *,
    live_runs: list[RunRecord],
  ) -> tuple[str, ...]:
    timeframes = list(self._guarded_live_market_data_timeframes)
    for run in live_runs:
      if run.config.timeframe not in timeframes:
        timeframes.append(run.config.timeframe)
    return tuple(timeframes or ("5m",))

  def _build_guarded_live_channel_operator_alerts(
    self,
    *,
    state: GuardedLiveState,
    current_time: datetime,
    live_context_active: bool,
    delivery_targets: tuple[str, ...],
  ) -> list[OperatorAlert]:
    if not live_context_active:
      return []

    handoff = state.session_handoff
    if handoff.state in {"inactive", "released"}:
      return []

    run_id = state.ownership.owner_run_id or handoff.owner_run_id
    session_id = state.ownership.owner_session_id or handoff.owner_session_id
    alerts: list[OperatorAlert] = []

    consistency_details, consistency_detected_at, consistency_has_critical = (
      self._collect_guarded_live_channel_consistency_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if consistency_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-channel-consistency:{run_id or 'unknown'}",
          severity="critical" if consistency_has_critical else "warning",
          category="market_data_channel_consistency",
          summary=(
            f"Guarded-live market-data channel consistency is degraded for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(consistency_details),
          detected_at=consistency_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    ladder_integrity_details, ladder_integrity_detected_at, ladder_integrity_has_critical = (
      self._collect_guarded_live_ladder_integrity_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if ladder_integrity_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-ladder-integrity:{run_id or 'unknown'}",
          severity="critical" if ladder_integrity_has_critical else "warning",
          category="market_data_ladder_integrity",
          summary=(
            f"Guarded-live exchange ladder integrity requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(ladder_integrity_details),
          detected_at=ladder_integrity_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    venue_ladder_integrity_details, venue_ladder_integrity_detected_at, venue_ladder_integrity_has_critical = (
      self._collect_guarded_live_venue_ladder_integrity_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if venue_ladder_integrity_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-venue-ladder-integrity:{run_id or 'unknown'}",
          severity="critical" if venue_ladder_integrity_has_critical else "warning",
          category="market_data_venue_ladder_integrity",
          summary=(
            f"Guarded-live venue-native ladder integrity requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(venue_ladder_integrity_details),
          detected_at=venue_ladder_integrity_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    ladder_bridge_details, ladder_bridge_detected_at, ladder_bridge_has_critical = (
      self._collect_guarded_live_ladder_bridge_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if ladder_bridge_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-ladder-bridge:{run_id or 'unknown'}",
          severity="critical" if ladder_bridge_has_critical else "warning",
          category="market_data_ladder_bridge_integrity",
          summary=(
            f"Guarded-live ladder bridge rules require review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(ladder_bridge_details),
          detected_at=ladder_bridge_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    ladder_sequence_details, ladder_sequence_detected_at, ladder_sequence_has_critical = (
      self._collect_guarded_live_ladder_sequence_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if ladder_sequence_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-ladder-sequence:{run_id or 'unknown'}",
          severity="critical" if ladder_sequence_has_critical else "warning",
          category="market_data_ladder_sequence_integrity",
          summary=(
            f"Guarded-live ladder sequence rules require review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(ladder_sequence_details),
          detected_at=ladder_sequence_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    ladder_snapshot_refresh_details, ladder_snapshot_refresh_detected_at, ladder_snapshot_refresh_has_critical = (
      self._collect_guarded_live_ladder_snapshot_refresh_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if ladder_snapshot_refresh_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-ladder-snapshot-refresh:{run_id or 'unknown'}",
          severity="critical" if ladder_snapshot_refresh_has_critical else "warning",
          category="market_data_ladder_snapshot_refresh",
          summary=(
            f"Guarded-live ladder snapshot refresh rules require review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(ladder_snapshot_refresh_details),
          detected_at=ladder_snapshot_refresh_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    restore_details, restore_detected_at, restore_has_critical = (
      self._collect_guarded_live_channel_restore_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if restore_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-channel-restore:{run_id or 'unknown'}",
          severity="critical" if restore_has_critical else "warning",
          category="market_data_channel_restore",
          summary=(
            f"Guarded-live market-data channel restore requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(restore_details),
          detected_at=restore_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    book_details, book_detected_at, book_has_critical = self._collect_guarded_live_book_consistency_findings(
      handoff=handoff,
      current_time=current_time,
    )
    if book_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-book-consistency:{run_id or 'unknown'}",
          severity="critical" if book_has_critical else "warning",
          category="market_data_book_consistency",
          summary=(
            f"Guarded-live book consistency requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(book_details),
          detected_at=book_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    kline_details, kline_detected_at, kline_has_critical = self._collect_guarded_live_kline_consistency_findings(
      handoff=handoff,
      current_time=current_time,
    )
    if kline_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-kline-consistency:{run_id or 'unknown'}",
          severity="critical" if kline_has_critical else "warning",
          category="market_data_kline_consistency",
          summary=(
            f"Guarded-live kline consistency requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(kline_details),
          detected_at=kline_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    depth_ladder_details, depth_ladder_detected_at, depth_ladder_has_critical = (
      self._collect_guarded_live_depth_ladder_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if depth_ladder_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-depth-ladder:{run_id or 'unknown'}",
          severity="critical" if depth_ladder_has_critical else "warning",
          category="market_data_depth_ladder",
          summary=(
            f"Guarded-live depth ladder semantics require review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(depth_ladder_details),
          detected_at=depth_ladder_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    candle_sequence_details, candle_sequence_detected_at, candle_sequence_has_critical = (
      self._collect_guarded_live_candle_sequence_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if candle_sequence_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-candle-sequence:{run_id or 'unknown'}",
          severity="critical" if candle_sequence_has_critical else "warning",
          category="market_data_candle_sequence",
          summary=(
            f"Guarded-live candle sequencing requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(candle_sequence_details),
          detected_at=candle_sequence_detected_at,
          run_id=run_id,
          session_id=session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )
    return alerts

  def _collect_guarded_live_channel_consistency_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    threshold_seconds = max(self._guarded_live_worker_heartbeat_timeout_seconds, 1)
    threshold = timedelta(seconds=threshold_seconds)
    handoff_anchor = handoff.last_sync_at or handoff.handed_off_at or current_time
    has_critical = False

    def add_finding(detail: str, *, detected_at: datetime | None, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if handoff.order_book_state == "unavailable":
      add_finding(
        "depth/order-book supervision is unavailable.",
        detected_at=handoff.last_sync_at or handoff.handed_off_at or current_time,
        critical=True,
      )
    elif handoff.order_book_state == "resync_required":
      add_finding(
        "depth/order-book continuity requires a resync before the local book is trustworthy.",
        detected_at=handoff.last_sync_at or handoff.handed_off_at or current_time,
        critical=True,
      )

    for channel_name, event_at, critical_channel in self._resolve_guarded_live_market_channel_activity(
      handoff=handoff
    ):
      if event_at is None:
        if current_time - handoff_anchor >= threshold:
          add_finding(
            f"{channel_name} has not produced any events within {threshold_seconds}s of the active venue handoff.",
            detected_at=handoff_anchor,
            critical=critical_channel,
          )
        continue
      if current_time - event_at > threshold:
        add_finding(
          f"{channel_name} is stale; last event at {event_at.isoformat()}.",
          detected_at=event_at,
          critical=critical_channel,
        )

    detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), detected_at, has_critical

  def _collect_guarded_live_ladder_integrity_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    venue = handoff.venue or "venue"
    detected_at = handoff.order_book_last_rebuilt_at or handoff.last_depth_event_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if handoff.order_book_gap_count > 0:
      gap_detail = f"{venue} ladder integrity recorded {handoff.order_book_gap_count} depth gap(s)."
      if handoff.order_book_last_update_id is not None:
        gap_detail += f" Last update id: {handoff.order_book_last_update_id}."
      add_finding(gap_detail, critical=True)

    if handoff.order_book_rebuild_count > 0:
      add_finding(
        f"{venue} ladder integrity required {handoff.order_book_rebuild_count} snapshot rebuild(s).",
      )

    for issue_detail in self._extract_guarded_live_ladder_integrity_semantics(issues=handoff.issues):
      add_finding(issue_detail, critical=True)

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical

  def _collect_guarded_live_venue_ladder_integrity_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    detected_at = handoff.order_book_last_rebuilt_at or handoff.last_depth_event_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if handoff.order_book_state == "rebuild_failed":
      add_finding(
        f"{handoff.venue or 'venue'} ladder snapshot rebuild is currently failing.",
        critical=True,
      )

    for issue_detail in self._extract_guarded_live_venue_ladder_integrity_semantics(issues=handoff.issues):
      add_finding(issue_detail, critical=True)

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical

  def _collect_guarded_live_ladder_bridge_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    detected_at = handoff.last_depth_event_at or handoff.order_book_last_rebuilt_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    for issue_detail in self._extract_guarded_live_ladder_bridge_semantics(issues=handoff.issues):
      add_finding(issue_detail, critical=True)

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical

  def _collect_guarded_live_ladder_sequence_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    detected_at = handoff.last_depth_event_at or handoff.order_book_last_rebuilt_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    for issue_detail in self._extract_guarded_live_ladder_sequence_semantics(issues=handoff.issues):
      add_finding(issue_detail, critical=True)

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical

  def _collect_guarded_live_ladder_snapshot_refresh_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    detected_at = handoff.last_depth_event_at or handoff.order_book_last_rebuilt_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    for issue_detail in self._extract_guarded_live_ladder_snapshot_refresh_semantics(issues=handoff.issues):
      add_finding(issue_detail, critical=True)

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical

  def _collect_guarded_live_channel_restore_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    restore_anchor = handoff.channel_last_restored_at or handoff.last_sync_at or handoff.handed_off_at or current_time
    has_critical = False

    def add_finding(detail: str, *, detected_at: datetime | None, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if handoff.channel_restore_state == "partial":
      add_finding(
        "market-channel restore completed only partially.",
        detected_at=restore_anchor,
      )
    elif handoff.channel_restore_state == "unavailable":
      add_finding(
        "market-channel restore is unavailable.",
        detected_at=restore_anchor,
        critical=True,
      )

    if handoff.channel_continuation_state == "partial":
      add_finding(
        "market-channel continuation is only partially supervised.",
        detected_at=handoff.channel_last_continued_at or restore_anchor,
      )
    elif handoff.channel_continuation_state == "unavailable":
      add_finding(
        "market-channel continuation is unavailable.",
        detected_at=handoff.channel_last_continued_at or restore_anchor,
        critical=True,
      )

    for issue_detail in self._extract_guarded_live_channel_restore_semantics(issues=handoff.issues):
      add_finding(
        issue_detail,
        detected_at=restore_anchor,
        critical=True,
      )

    detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), detected_at, has_critical

  def _collect_guarded_live_book_consistency_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    snapshot = handoff.book_ticker_snapshot
    if (
      handoff.order_book_state in {"inactive", "released"}
      and snapshot is None
    ):
      return [], current_time, False

    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    venue = handoff.venue or "venue"
    tolerance = self._guarded_live_balance_tolerance

    def add_finding(detail: str, *, detected_at: datetime | None, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    best_bid = handoff.order_book_best_bid_price
    best_ask = handoff.order_book_best_ask_price
    if best_bid is not None and best_ask is not None and best_bid > (best_ask + tolerance):
      add_finding(
        f"{venue} local order book is crossed: best bid {best_bid:.8f} is above best ask {best_ask:.8f}.",
        detected_at=handoff.last_depth_event_at or handoff.order_book_last_rebuilt_at or handoff.last_sync_at,
        critical=True,
      )

    if snapshot is not None:
      if (
        snapshot.bid_price is not None
        and snapshot.ask_price is not None
        and snapshot.bid_price > (snapshot.ask_price + tolerance)
      ):
        add_finding(
          f"{venue} book-ticker quote is crossed: bid {snapshot.bid_price:.8f} is above ask {snapshot.ask_price:.8f}.",
          detected_at=snapshot.event_at or handoff.last_book_ticker_event_at or handoff.last_sync_at,
          critical=True,
        )
      if (
        best_bid is not None
        and snapshot.ask_price is not None
        and best_bid > (snapshot.ask_price + tolerance)
      ):
        add_finding(
          f"{venue} local best bid {best_bid:.8f} is above book-ticker ask {snapshot.ask_price:.8f}.",
          detected_at=snapshot.event_at or handoff.last_book_ticker_event_at or handoff.last_sync_at,
          critical=True,
        )
      if (
        snapshot.bid_price is not None
        and best_ask is not None
        and snapshot.bid_price > (best_ask + tolerance)
      ):
        add_finding(
          f"{venue} book-ticker bid {snapshot.bid_price:.8f} is above local best ask {best_ask:.8f}.",
          detected_at=snapshot.event_at or handoff.last_book_ticker_event_at or handoff.last_sync_at,
          critical=True,
        )

    detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), detected_at, has_critical

  def _collect_guarded_live_kline_consistency_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    snapshot = handoff.kline_snapshot
    if snapshot is None:
      return [], current_time, False

    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    venue = handoff.venue or "venue"
    tolerance = self._guarded_live_balance_tolerance

    def add_finding(detail: str, *, detected_at: datetime | None, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if (
      snapshot.timeframe is not None
      and handoff.timeframe is not None
      and snapshot.timeframe != handoff.timeframe
    ):
      add_finding(
        f"{venue} kline timeframe {snapshot.timeframe} does not match the guarded-live timeframe {handoff.timeframe}.",
        detected_at=snapshot.event_at or handoff.last_kline_event_at or handoff.last_sync_at,
      )

    if (
      snapshot.open_at is not None
      and snapshot.close_at is not None
      and snapshot.close_at <= snapshot.open_at
    ):
      add_finding(
        f"{venue} kline closes at {snapshot.close_at.isoformat()} before or at its open {snapshot.open_at.isoformat()}.",
        detected_at=snapshot.event_at or snapshot.close_at or handoff.last_kline_event_at,
        critical=True,
      )

    if (
      snapshot.high_price is not None
      and snapshot.low_price is not None
      and snapshot.high_price + tolerance < snapshot.low_price
    ):
      add_finding(
        f"{venue} kline high {snapshot.high_price:.8f} is below low {snapshot.low_price:.8f}.",
        detected_at=snapshot.event_at or handoff.last_kline_event_at or handoff.last_sync_at,
        critical=True,
      )
    elif snapshot.high_price is not None and snapshot.low_price is not None:
      if (
        snapshot.open_price is not None
        and (
          snapshot.open_price > snapshot.high_price + tolerance
          or snapshot.open_price + tolerance < snapshot.low_price
        )
      ):
        add_finding(
          f"{venue} kline open {snapshot.open_price:.8f} falls outside the high/low range "
          f"{snapshot.low_price:.8f}-{snapshot.high_price:.8f}.",
          detected_at=snapshot.event_at or handoff.last_kline_event_at or handoff.last_sync_at,
          critical=True,
        )
      if (
        snapshot.close_price is not None
        and (
          snapshot.close_price > snapshot.high_price + tolerance
          or snapshot.close_price + tolerance < snapshot.low_price
        )
      ):
        add_finding(
          f"{venue} kline close {snapshot.close_price:.8f} falls outside the high/low range "
          f"{snapshot.low_price:.8f}-{snapshot.high_price:.8f}.",
          detected_at=snapshot.event_at or handoff.last_kline_event_at or handoff.last_sync_at,
          critical=True,
        )

    detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), detected_at, has_critical

  def _collect_guarded_live_depth_ladder_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    if not handoff.order_book_bids and not handoff.order_book_asks:
      return [], current_time, False

    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    venue = handoff.venue or "venue"
    tolerance = self._guarded_live_balance_tolerance
    detected_at = handoff.last_depth_event_at or handoff.order_book_last_rebuilt_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if handoff.order_book_bid_level_count and handoff.order_book_bid_level_count != len(handoff.order_book_bids):
      add_finding(
        f"{venue} bid ladder count {len(handoff.order_book_bids)} does not match stored bid level count "
        f"{handoff.order_book_bid_level_count}.",
        critical=True,
      )
    if handoff.order_book_ask_level_count and handoff.order_book_ask_level_count != len(handoff.order_book_asks):
      add_finding(
        f"{venue} ask ladder count {len(handoff.order_book_asks)} does not match stored ask level count "
        f"{handoff.order_book_ask_level_count}.",
        critical=True,
      )

    if handoff.order_book_bids and (
      handoff.order_book_best_bid_price is not None or handoff.order_book_best_bid_quantity is not None
    ):
      head = handoff.order_book_bids[0]
      if (
        (handoff.order_book_best_bid_price is not None and abs(head.price - handoff.order_book_best_bid_price) > tolerance)
        or (
          handoff.order_book_best_bid_quantity is not None
          and abs(head.quantity - handoff.order_book_best_bid_quantity) > tolerance
        )
      ):
        add_finding(
          f"{venue} best bid ladder head {head.price:.8f}/{head.quantity:.8f} does not match stored "
          f"best bid {handoff.order_book_best_bid_price or 0.0:.8f}/"
          f"{handoff.order_book_best_bid_quantity or 0.0:.8f}.",
          critical=True,
        )
    if handoff.order_book_asks and (
      handoff.order_book_best_ask_price is not None or handoff.order_book_best_ask_quantity is not None
    ):
      head = handoff.order_book_asks[0]
      if (
        (handoff.order_book_best_ask_price is not None and abs(head.price - handoff.order_book_best_ask_price) > tolerance)
        or (
          handoff.order_book_best_ask_quantity is not None
          and abs(head.quantity - handoff.order_book_best_ask_quantity) > tolerance
        )
      ):
        add_finding(
          f"{venue} best ask ladder head {head.price:.8f}/{head.quantity:.8f} does not match stored "
          f"best ask {handoff.order_book_best_ask_price or 0.0:.8f}/"
          f"{handoff.order_book_best_ask_quantity or 0.0:.8f}.",
          critical=True,
        )

    previous_price: float | None = None
    for index, level in enumerate(handoff.order_book_bids, start=1):
      if level.quantity <= tolerance:
        add_finding(
          f"{venue} bid ladder level {index} has non-positive quantity {level.quantity:.8f}.",
          critical=True,
        )
      if previous_price is not None and level.price >= (previous_price - tolerance):
        add_finding(
          f"{venue} bid ladder is not strictly descending at level {index} "
          f"({level.price:.8f} after {previous_price:.8f}).",
          critical=True,
        )
      previous_price = level.price

    previous_price = None
    for index, level in enumerate(handoff.order_book_asks, start=1):
      if level.quantity <= tolerance:
        add_finding(
          f"{venue} ask ladder level {index} has non-positive quantity {level.quantity:.8f}.",
          critical=True,
        )
      if previous_price is not None and level.price <= (previous_price + tolerance):
        add_finding(
          f"{venue} ask ladder is not strictly ascending at level {index} "
          f"({level.price:.8f} after {previous_price:.8f}).",
          critical=True,
        )
      previous_price = level.price

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical

  def _collect_guarded_live_candle_sequence_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    snapshot = handoff.kline_snapshot
    if snapshot is None:
      return [], current_time, False

    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    venue = handoff.venue or "venue"
    timeframe = snapshot.timeframe or handoff.timeframe
    timeframe_delta = self._guarded_live_timeframe_to_timedelta(timeframe)
    detected_at = snapshot.event_at or handoff.last_kline_event_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if timeframe_delta is not None and snapshot.open_at is not None:
      if not self._datetime_is_aligned_to_interval(snapshot.open_at, timeframe_delta):
        add_finding(
          f"{venue} kline open {snapshot.open_at.isoformat()} is not aligned to the {timeframe} timeframe boundary."
        )

    if timeframe_delta is not None and snapshot.open_at is not None and snapshot.close_at is not None:
      expected_close_at = snapshot.open_at + timeframe_delta
      if snapshot.close_at != expected_close_at:
        add_finding(
          f"{venue} kline close {snapshot.close_at.isoformat()} does not match the expected {timeframe} boundary close "
          f"{expected_close_at.isoformat()}.",
          critical=True,
        )

    if snapshot.closed and snapshot.event_at is not None and snapshot.close_at is not None and snapshot.event_at < snapshot.close_at:
      add_finding(
        f"{venue} closed kline event arrived at {snapshot.event_at.isoformat()} before the candle close "
        f"{snapshot.close_at.isoformat()}.",
        critical=True,
      )

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical

  @staticmethod
  def _guarded_live_timeframe_to_timedelta(timeframe: str | None) -> timedelta | None:
    if not timeframe or len(timeframe) < 2:
      return None
    unit = timeframe[-1]
    try:
      amount = int(timeframe[:-1])
    except ValueError:
      return None
    if amount <= 0:
      return None
    return {
      "m": timedelta(minutes=amount),
      "h": timedelta(hours=amount),
      "d": timedelta(days=amount),
      "w": timedelta(weeks=amount),
    }.get(unit)

  @staticmethod
  def _datetime_is_aligned_to_interval(value: datetime, interval: timedelta) -> bool:
    if interval.total_seconds() <= 0:
      return False
    epoch = datetime(1970, 1, 1, tzinfo=UTC)
    return ((value - epoch).total_seconds() % interval.total_seconds()) == 0

  @staticmethod
  def _resolve_guarded_live_market_channel_activity(
    *,
    handoff: GuardedLiveVenueSessionHandoff,
  ) -> tuple[tuple[str, datetime | None, bool], ...]:
    coverage = set(handoff.coverage)
    activity: list[tuple[str, datetime | None, bool]] = []
    if "trade_ticks" in coverage:
      activity.append(("trade ticks", handoff.last_trade_event_at, False))
    if "aggregate_trade_ticks" in coverage:
      activity.append(("aggregate-trade ticks", handoff.last_aggregate_trade_event_at, False))
    if "book_ticker" in coverage:
      activity.append(("book-ticker updates", handoff.last_book_ticker_event_at, False))
    if "mini_ticker" in coverage:
      activity.append(("mini-ticker updates", handoff.last_mini_ticker_event_at, False))
    if "depth_updates" in coverage or "order_book_lifecycle" in coverage:
      activity.append(("depth/order-book updates", handoff.last_depth_event_at, True))
    if "kline_candles" in coverage:
      activity.append(("kline candles", handoff.last_kline_event_at, False))
    return tuple(activity)

  @staticmethod
  def _extract_guarded_live_channel_gap_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_order_book_gap_detected:" not in issue:
        continue
      venue, payload = issue.split("_order_book_gap_detected:", 1)
      previous_update_id, _, next_update_id = payload.partition(":")
      if previous_update_id and next_update_id:
        findings.append(
          f"{venue} depth stream gap detected between update ids {previous_update_id} and {next_update_id}."
        )
      else:
        findings.append(f"{venue} depth stream gap detected.")
    return tuple(dict.fromkeys(findings))

  @staticmethod
  def _extract_guarded_live_ladder_integrity_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    return TradingApplication._extract_guarded_live_channel_gap_semantics(issues=issues)

  @staticmethod
  def _extract_guarded_live_venue_ladder_integrity_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_order_book_snapshot_failed:" in issue:
        venue, payload = issue.split("_order_book_snapshot_failed:", 1)
        reason, _, detail = payload.partition(":")
        reason_label = reason.replace("_", " ") if reason else "unknown"
        if detail:
          findings.append(f"{venue} ladder snapshot rebuild failed during {reason_label}: {detail}.")
        else:
          findings.append(f"{venue} ladder snapshot rebuild failed during {reason_label}.")
        continue
      if "_order_book_snapshot_missing_side:" in issue:
        venue, payload = issue.split("_order_book_snapshot_missing_side:", 1)
        side = payload.replace("_", " ") if payload else "unknown side"
        findings.append(f"{venue} ladder snapshot returned no {side} levels.")
        continue
      if "_order_book_snapshot_crossed:" in issue:
        venue, payload = issue.split("_order_book_snapshot_crossed:", 1)
        bid, _, ask = payload.partition(":")
        if bid and ask:
          try:
            bid_value = f"{float(bid):.8f}"
            ask_value = f"{float(ask):.8f}"
          except ValueError:
            bid_value = bid
            ask_value = ask
          findings.append(
            f"{venue} ladder snapshot is crossed: best bid {bid_value} is above best ask {ask_value}."
          )
        else:
          findings.append(f"{venue} ladder snapshot is crossed.")
        continue
      if "_order_book_snapshot_non_monotonic:" not in issue:
        continue
      venue, payload = issue.split("_order_book_snapshot_non_monotonic:", 1)
      side, _, remainder = payload.partition(":")
      index, _, price_payload = remainder.partition(":")
      price, _, previous_price = price_payload.partition(":")
      side_label = side[:-1] if side.endswith("s") else side
      ordering = "descending" if side == "bids" else "ascending"
      if index and price and previous_price:
        try:
          price_value = f"{float(price):.8f}"
          previous_price_value = f"{float(previous_price):.8f}"
        except ValueError:
          price_value = price
          previous_price_value = previous_price
        findings.append(
          f"{venue} {side_label} ladder snapshot is not strictly {ordering} at level {index} "
          f"({price_value} after {previous_price_value})."
        )
      else:
        findings.append(f"{venue} {side_label} ladder snapshot is not strictly {ordering}.")
    return tuple(dict.fromkeys(findings))

  @staticmethod
  def _extract_guarded_live_ladder_bridge_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_order_book_bridge_previous_mismatch:" in issue:
        venue, payload = issue.split("_order_book_bridge_previous_mismatch:", 1)
        expected_previous, _, actual_previous = payload.partition(":")
        findings.append(
          f"{venue} depth bridge expected previous update id {expected_previous or 'unknown'} "
          f"but received {actual_previous or 'unknown'}."
        )
        continue
      if "_order_book_bridge_range_mismatch:" in issue:
        venue, payload = issue.split("_order_book_bridge_range_mismatch:", 1)
        expected_next, _, remainder = payload.partition(":")
        first_update_id, _, last_update_id = remainder.partition(":")
        findings.append(
          f"{venue} depth bridge range {first_update_id or 'unknown'}-{last_update_id or 'unknown'} "
          f"does not cover expected next update id {expected_next or 'unknown'}."
        )
        continue
    return tuple(dict.fromkeys(findings))

  @staticmethod
  def _extract_guarded_live_ladder_sequence_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_order_book_sequence_mismatch:" not in issue:
        continue
      venue, payload = issue.split("_order_book_sequence_mismatch:", 1)
      expected_previous, _, remainder = payload.partition(":")
      actual_previous, _, current_update_id = remainder.partition(":")
      findings.append(
        f"{venue} ladder sequence expected previous update id {expected_previous or 'unknown'} "
        f"but received {actual_previous or 'unknown'} before update {current_update_id or 'unknown'}."
      )
    return tuple(dict.fromkeys(findings))

  @staticmethod
  def _extract_guarded_live_ladder_snapshot_refresh_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_order_book_snapshot_refresh:" not in issue:
        continue
      venue, payload = issue.split("_order_book_snapshot_refresh:", 1)
      previous_update_id, _, next_update_id = payload.partition(":")
      findings.append(
        f"{venue} ladder snapshot refresh replaced update id {previous_update_id or 'unknown'} "
        f"with {next_update_id or 'unknown'}."
      )
    return tuple(dict.fromkeys(findings))

  @staticmethod
  def _extract_guarded_live_channel_restore_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_market_channel_restore_failed:" not in issue:
        continue
      venue, payload = issue.split("_market_channel_restore_failed:", 1)
      channel, _, remainder = payload.partition(":")
      reason = remainder.replace("_", " ") if remainder else "unknown"
      channel_label = channel.replace("_", " ") if channel else "market channel"
      findings.append(
        f"{venue} {channel_label} restore failed: {reason}."
      )
    return tuple(dict.fromkeys(findings))

  @staticmethod
  def _summarize_guarded_live_issue_copy(details: list[str]) -> str:
    unique_details = list(dict.fromkeys(details))
    return " ".join(unique_details[:3]) + (
      f" Additional issues: {len(unique_details) - 3}."
      if len(unique_details) > 3
      else ""
    )

  def _build_guarded_live_incident_events(
    self,
    *,
    previous_history: tuple[OperatorAlert, ...],
    merged_history: tuple[OperatorAlert, ...],
    current_time: datetime,
  ) -> tuple[OperatorIncidentEvent, ...]:
    previous_by_id = {alert.alert_id: alert for alert in previous_history}
    incident_events: list[OperatorIncidentEvent] = []

    for alert in merged_history:
      policy = self._resolve_incident_paging_policy(alert=alert)
      remediation = self._build_incident_remediation(alert=alert, policy=policy)
      previous = previous_by_id.get(alert.alert_id)
      if alert.status == "active" and (previous is None or previous.status != "active"):
        incident_events.append(
          OperatorIncidentEvent(
            event_id=f"incident_opened:{alert.alert_id}:{alert.detected_at.isoformat()}",
            alert_id=alert.alert_id,
            timestamp=alert.detected_at,
            kind="incident_opened",
            severity=alert.severity,
            summary=alert.summary,
            detail=alert.detail,
            run_id=alert.run_id,
            session_id=alert.session_id,
            source=alert.source,
            paging_policy_id=policy.policy_id,
            paging_provider=policy.provider,
            delivery_targets=policy.initial_targets,
            escalation_targets=policy.escalation_targets,
            acknowledgment_state="unacknowledged",
            escalation_state=(
              "pending" if policy.escalation_targets else "not_configured"
            ),
            next_escalation_at=(
              alert.detected_at + timedelta(seconds=self._operator_alert_incident_ack_timeout_seconds)
              if policy.escalation_targets
              else None
            ),
            paging_status="pending" if policy.provider else "not_configured",
            provider_workflow_state="idle" if policy.provider else "not_configured",
            remediation=remediation,
          )
        )
        continue
      if alert.status == "resolved" and previous is not None and previous.status == "active":
        resolved_at = alert.resolved_at or current_time
        incident_events.append(
          OperatorIncidentEvent(
            event_id=f"incident_resolved:{alert.alert_id}:{resolved_at.isoformat()}",
            alert_id=alert.alert_id,
            timestamp=resolved_at,
            kind="incident_resolved",
            severity=alert.severity,
            summary=f"Resolved: {alert.summary}",
            detail=alert.detail,
            run_id=alert.run_id,
            session_id=alert.session_id,
            source=alert.source,
            paging_policy_id=policy.policy_id,
            paging_provider=policy.provider,
            delivery_targets=policy.resolution_targets,
            acknowledgment_state="not_applicable",
            escalation_state="not_applicable",
            paging_status="pending" if policy.provider else "not_configured",
            remediation=remediation,
          )
        )

    incident_events.sort(key=lambda event: event.timestamp, reverse=True)
    return tuple(incident_events)

  @staticmethod
  def _normalize_targets(targets: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(targets))

  @staticmethod
  def _normalize_paging_provider(provider: str | None) -> str | None:
    if provider is None:
      return None
    normalized = provider.strip().lower().replace("-", "_").replace(".", "_")
    if normalized == "incident_io":
      return "incidentio"
    if normalized == "fire_hydrant":
      return "firehydrant"
    if normalized == "root_ly":
      return "rootly"
    if normalized == "blame_less":
      return "blameless"
    if normalized == "x_matters":
      return "xmatters"
    if normalized == "service_now":
      return "servicenow"
    if normalized == "squad_cast":
      return "squadcast"
    if normalized == "big_panda":
      return "bigpanda"
    if normalized == "zen_duty":
      return "zenduty"
    if normalized == "victorops":
      return "splunk_oncall"
    if normalized in {"jsm", "jira_service_desk"}:
      return "jira_service_management"
    if normalized == "pager_tree":
      return "pagertree"
    if normalized == "alert_ops":
      return "alertops"
    if normalized == "signl_4":
      return "signl4"
    if normalized in {"i_lert", "ilert_alerts", "operator_ilert"}:
      return "ilert"
    if normalized in {"better_stack", "betterstack_alerts", "operator_betterstack"}:
      return "betterstack"
    if normalized in {"grafana_oncall_incidents", "grafanaoncall", "operator_grafana_oncall"}:
      return "grafana_oncall"
    if normalized in {"zenduty_incidents", "operator_zenduty"}:
      return "zenduty"
    if normalized in {"splunk_oncall_incidents", "splunkoncall", "operator_splunk_oncall"}:
      return "splunk_oncall"
    if normalized in {
      "jira_service_management_incidents",
      "jira_service_desk_incidents",
      "operator_jira_service_management",
      "jsm_incidents",
    }:
      return "jira_service_management"
    if normalized in {"pagertree_incidents", "operator_pagertree"}:
      return "pagertree"
    if normalized in {"alertops_incidents", "operator_alertops"}:
      return "alertops"
    if normalized in {"signl4_incidents", "operator_signl4"}:
      return "signl4"
    if normalized in {"ilert_incidents", "ilert_alerts", "operator_ilert"}:
      return "ilert"
    if normalized in {"betterstack_incidents", "betterstack_alerts", "operator_betterstack"}:
      return "betterstack"
    if normalized in {"on_page", "onpage_alerts", "operator_onpage"}:
      return "onpage"
    if normalized in {"onpage_incidents", "operator_onpage"}:
      return "onpage"
    if normalized in {"all_quiet", "allquiet_alerts", "operator_allquiet"}:
      return "allquiet"
    if normalized in {"allquiet_incidents", "operator_allquiet"}:
      return "allquiet"
    if normalized in {"moogsoft_alerts", "operator_moogsoft"}:
      return "moogsoft"
    if normalized in {"moogsoft_incidents", "operator_moogsoft"}:
      return "moogsoft"
    if normalized in {"spikesh_alerts", "spike_sh", "operator_spikesh"}:
      return "spikesh"
    if normalized in {"spikesh_incidents", "operator_spikesh"}:
      return "spikesh"
    if normalized in {"dutycalls_alerts", "duty_calls", "operator_dutycalls"}:
      return "dutycalls"
    if normalized in {"dutycalls_incidents", "operator_dutycalls"}:
      return "dutycalls"
    if normalized in {"incidenthub_alerts", "incident_hub", "operator_incidenthub"}:
      return "incidenthub"
    if normalized in {"incidenthub_incidents", "operator_incidenthub"}:
      return "incidenthub"
    if normalized in {"resolver_alerts", "operator_resolver"}:
      return "resolver"
    if normalized in {"resolver_incidents", "operator_resolver"}:
      return "resolver"
    if normalized in {"openduty_alerts", "open_duty", "operator_openduty"}:
      return "openduty"
    if normalized in {"openduty_incidents", "operator_openduty"}:
      return "openduty"
    if normalized in {"cabot_alerts", "operator_cabot"}:
      return "cabot"
    if normalized in {"cabot_incidents", "operator_cabot"}:
      return "cabot"
    if normalized in {"haloitsm_alerts", "halo_itsm", "operator_haloitsm"}:
      return "haloitsm"
    if normalized in {"haloitsm_incidents", "operator_haloitsm"}:
      return "haloitsm"
    if normalized in {
      "incidentmanagerio_alerts",
      "incidentmanagerio",
      "incidentmanager_io",
      "operator_incidentmanagerio",
    }:
      return "incidentmanagerio"
    if normalized in {"incidentmanagerio_incidents", "operator_incidentmanagerio"}:
      return "incidentmanagerio"
    if normalized in {"oneuptime_alerts", "one_uptime", "operator_oneuptime"}:
      return "oneuptime"
    if normalized in {"oneuptime_incidents", "operator_oneuptime"}:
      return "oneuptime"
    if normalized in {"squzy_alerts", "operator_squzy"}:
      return "squzy"
    if normalized in {"squzy_incidents", "operator_squzy"}:
      return "squzy"
    if normalized in {
      "crisescontrol_alerts",
      "crises_control",
      "crisescontrol",
      "operator_crisescontrol",
    }:
      return "crisescontrol"
    if normalized in {"crisescontrol_incidents", "operator_crisescontrol"}:
      return "crisescontrol"
    if normalized in {"freshservice_alerts", "fresh_service", "freshservice", "operator_freshservice"}:
      return "freshservice"
    if normalized in {"freshservice_incidents", "operator_freshservice"}:
      return "freshservice"
    if normalized in {"freshdesk_alerts", "freshdesk", "operator_freshdesk"}:
      return "freshdesk"
    if normalized in {"freshdesk_incidents", "operator_freshdesk"}:
      return "freshdesk"
    if normalized in {"happyfox_alerts", "happyfox", "operator_happyfox"}:
      return "happyfox"
    if normalized in {"happyfox_incidents", "operator_happyfox"}:
      return "happyfox"
    if normalized in {"zendesk_alerts", "zendesk", "operator_zendesk"}:
      return "zendesk"
    if normalized in {"zendesk_incidents", "operator_zendesk"}:
      return "zendesk"
    if normalized in {"zohodesk_alerts", "zohodesk", "zoho_desk", "operator_zohodesk"}:
      return "zohodesk"
    if normalized in {"zohodesk_incidents", "operator_zohodesk"}:
      return "zohodesk"
    if normalized in {"helpscout_alerts", "helpscout", "help_scout", "operator_helpscout"}:
      return "helpscout"
    if normalized in {"helpscout_incidents", "operator_helpscout"}:
      return "helpscout"
    if normalized in {"kayako_alerts", "kayako", "operator_kayako"}:
      return "kayako"
    if normalized in {"kayako_incidents", "operator_kayako"}:
      return "kayako"
    if normalized in {"intercom_alerts", "intercom", "operator_intercom"}:
      return "intercom"
    if normalized in {"intercom_incidents", "operator_intercom"}:
      return "intercom"
    if normalized in {"front_alerts", "front", "operator_front"}:
      return "front"
    if normalized in {"front_incidents", "operator_front"}:
      return "front"
    if normalized in {
      "servicedeskplus_alerts",
      "servicedeskplus",
      "service_desk_plus",
      "manageengine_servicedesk_plus",
      "operator_servicedeskplus",
    }:
      return "servicedeskplus"
    if normalized in {"servicedeskplus_incidents", "operator_servicedeskplus"}:
      return "servicedeskplus"
    if normalized in {"bmchelix_alerts", "bmchelix", "bmc_helix", "operator_bmchelix"}:
      return "bmchelix"
    if normalized in {"bmchelix_incidents", "operator_bmchelix"}:
      return "bmchelix"
    if normalized in {
      "solarwindsservicedesk_alerts",
      "solarwindsservicedesk",
      "solarwinds_service_desk",
      "operator_solarwindsservicedesk",
    }:
      return "solarwindsservicedesk"
    if normalized in {"solarwindsservicedesk_incidents", "operator_solarwindsservicedesk"}:
      return "solarwindsservicedesk"
    if normalized in {
      "invgateservicedesk_alerts",
      "invgateservicedesk",
      "invgate_service_desk",
      "invgate_servicedesk",
      "operator_invgateservicedesk",
    }:
      return "invgateservicedesk"
    if normalized in {"invgateservicedesk_incidents", "operator_invgateservicedesk"}:
      return "invgateservicedesk"
    if normalized in {"topdesk_alerts", "topdesk", "operator_topdesk"}:
      return "topdesk"
    if normalized in {"topdesk_incidents", "operator_topdesk"}:
      return "topdesk"
    if normalized in {"sysaid_alerts", "sysaid", "sys_aid", "operator_sysaid"}:
      return "sysaid"
    if normalized in {"sysaid_incidents", "operator_sysaid"}:
      return "sysaid"
    if normalized in {"opsramp_alerts", "ops_ramp", "operator_opsramp"}:
      return "opsramp"
    if normalized in {"opsramp_incidents", "operator_opsramp"}:
      return "opsramp"
    return normalized or None

  @staticmethod
  def _alert_supports_remediation(*, alert: OperatorAlert) -> bool:
    return alert.source == "guarded_live" and alert.category.startswith("market_data_")

  @staticmethod
  def _market_data_remediation_plan(*, category: str) -> _IncidentRemediationPlan:
    if category == "market_data_freshness":
      return _IncidentRemediationPlan(
        kind="recent_sync",
        owner="provider",
        summary="Refresh the live timeframe sync window and verify freshness thresholds.",
        detail=(
          "Trigger provider-owned recent sync for the affected timeframe, then confirm the "
          "latest checkpoint, sync timestamp, and freshness window have recovered."
        ),
        runbook="market_data.sync_recent",
      )
    if category == "market_data_quality":
      return _IncidentRemediationPlan(
        kind="historical_backfill",
        owner="provider",
        summary="Backfill the historical window to the configured target coverage.",
        detail=(
          "Run provider-owned historical backfill, then verify target coverage and completion "
          "ratio against the guarded-live backfill policy."
        ),
        runbook="market_data.backfill_history",
      )
    if category in {"market_data_candle_continuity", "market_data_candle_sequence", "market_data_kline_consistency"}:
      return _IncidentRemediationPlan(
        kind="candle_repair",
        owner="provider",
        summary="Repair candle continuity and restore the affected kline sequence.",
        detail=(
          "Backfill the affected candle range, verify contiguous candle boundaries, and confirm "
          "the kline stream has resumed with valid ordering."
        ),
        runbook="market_data.repair_candles",
      )
    if category == "market_data_venue":
      return _IncidentRemediationPlan(
        kind="venue_fault_review",
        owner="provider",
        summary="Review upstream venue faults and re-run the affected sync path.",
        detail=(
          "Escalate the venue-specific upstream fault, then retry provider-owned market-data sync "
          "for the affected instrument and timeframe."
        ),
        runbook="market_data.review_venue_fault",
      )
    if category in {"market_data_channel_consistency", "market_data_channel_restore"}:
      return _IncidentRemediationPlan(
        kind="channel_restore",
        owner="provider",
        summary="Restore stale or missing guarded-live market-data channels.",
        detail=(
          "Restart or resubscribe the affected market-data channels, then confirm the guarded-live "
          "handoff is receiving fresh events for every covered channel."
        ),
        runbook="market_data.restore_channels",
      )
    if category in {
      "market_data_ladder_integrity",
      "market_data_venue_ladder_integrity",
      "market_data_ladder_bridge_integrity",
      "market_data_ladder_sequence_integrity",
      "market_data_ladder_snapshot_refresh",
      "market_data_depth_ladder",
      "market_data_book_consistency",
    }:
      return _IncidentRemediationPlan(
        kind="order_book_rebuild",
        owner="provider",
        summary="Rebuild the venue ladder and restore order-book integrity checks.",
        detail=(
          "Trigger provider-owned depth snapshot rebuild, replay the exchange bridge rules, and "
          "verify the local ladder, top-of-book, and snapshot refresh state are healthy again."
        ),
        runbook="market_data.rebuild_order_book",
      )
    return _IncidentRemediationPlan(
      kind="market_data_review",
      owner="provider",
      summary="Review the affected market-data policy path and restore normal coverage.",
      detail=(
        "Inspect the degraded guarded-live market-data path, trigger the provider-owned recovery "
        "workflow, and verify the affected policy has recovered."
      ),
      runbook="market_data.review_policy_fault",
    )

  def _build_incident_remediation(
    self,
    *,
    alert: OperatorAlert,
    policy: _IncidentPagingPolicy,
  ) -> OperatorIncidentRemediation:
    if not self._alert_supports_remediation(alert=alert):
      return OperatorIncidentRemediation()
    plan = self._market_data_remediation_plan(category=alert.category)
    owner = "provider" if policy.provider and plan.owner == "provider" else "operator"
    if alert.status == "resolved":
      state = "completed"
    elif owner == "provider":
      state = "suggested"
    else:
      state = "operator_review"
    return OperatorIncidentRemediation(
      state=state,
      kind=plan.kind,
      owner=owner,
      summary=plan.summary,
      detail=plan.detail,
      runbook=plan.runbook,
      provider=self._normalize_paging_provider(policy.provider),
    )

  def _resolve_incident_paging_policy(self, *, alert: OperatorAlert) -> _IncidentPagingPolicy:
    severity = alert.severity.strip().lower()
    policy_id = "default"
    initial_targets = self._operator_alert_delivery.list_targets()
    escalation_targets = self._operator_alert_escalation_targets or initial_targets
    if severity in {"critical", "error"}:
      policy_id = "severity:critical"
      if self._operator_alert_paging_policy_critical_targets:
        initial_targets = self._operator_alert_paging_policy_critical_targets
      if self._operator_alert_paging_policy_critical_escalation_targets:
        escalation_targets = self._operator_alert_paging_policy_critical_escalation_targets
    elif severity in {"warning", "warn"}:
      policy_id = "severity:warning"
      if self._operator_alert_paging_policy_warning_targets:
        initial_targets = self._operator_alert_paging_policy_warning_targets
      if self._operator_alert_paging_policy_warning_escalation_targets:
        escalation_targets = self._operator_alert_paging_policy_warning_escalation_targets

    initial_targets = self._normalize_targets(initial_targets)
    escalation_targets = self._normalize_targets(escalation_targets)
    resolution_targets = self._normalize_targets((*initial_targets, *escalation_targets))
    provider = self._operator_alert_paging_policy_default_provider or self._infer_paging_provider(
      initial_targets=initial_targets,
      escalation_targets=escalation_targets,
    )
    return _IncidentPagingPolicy(
      policy_id=policy_id,
      provider=provider,
      initial_targets=initial_targets,
      escalation_targets=escalation_targets,
      resolution_targets=resolution_targets,
    )

  @staticmethod
  def _infer_paging_provider(
    *,
    initial_targets: tuple[str, ...],
    escalation_targets: tuple[str, ...],
  ) -> str | None:
    combined = {target.strip().lower().replace("-", "_") for target in (*initial_targets, *escalation_targets)}
    if "pagerduty_events" in combined:
      return "pagerduty"
    if "incidentio_incidents" in combined:
      return "incidentio"
    if "firehydrant_incidents" in combined:
      return "firehydrant"
    if "rootly_incidents" in combined:
      return "rootly"
    if "blameless_incidents" in combined:
      return "blameless"
    if "xmatters_incidents" in combined:
      return "xmatters"
    if "servicenow_incidents" in combined:
      return "servicenow"
    if "squadcast_incidents" in combined:
      return "squadcast"
    if "bigpanda_incidents" in combined:
      return "bigpanda"
    if "grafana_oncall_incidents" in combined:
      return "grafana_oncall"
    if "zenduty_incidents" in combined:
      return "zenduty"
    if "splunk_oncall_incidents" in combined:
      return "splunk_oncall"
    if "jira_service_management_incidents" in combined or "jsm_incidents" in combined:
      return "jira_service_management"
    if "pagertree_incidents" in combined:
      return "pagertree"
    if "alertops_incidents" in combined:
      return "alertops"
    if "signl4_incidents" in combined:
      return "signl4"
    if "ilert_incidents" in combined or "ilert_alerts" in combined:
      return "ilert"
    if "betterstack_incidents" in combined or "betterstack_alerts" in combined:
      return "betterstack"
    if "onpage_incidents" in combined or "onpage_alerts" in combined:
      return "onpage"
    if "allquiet_incidents" in combined or "allquiet_alerts" in combined:
      return "allquiet"
    if "moogsoft_incidents" in combined or "moogsoft_alerts" in combined:
      return "moogsoft"
    if "spikesh_incidents" in combined or "spikesh_alerts" in combined:
      return "spikesh"
    if "dutycalls_incidents" in combined or "dutycalls_alerts" in combined:
      return "dutycalls"
    if "incidenthub_incidents" in combined or "incidenthub_alerts" in combined:
      return "incidenthub"
    if "resolver_incidents" in combined or "resolver_alerts" in combined:
      return "resolver"
    if "openduty_incidents" in combined or "openduty_alerts" in combined:
      return "openduty"
    if "cabot_incidents" in combined or "cabot_alerts" in combined:
      return "cabot"
    if "haloitsm_incidents" in combined or "haloitsm_alerts" in combined:
      return "haloitsm"
    if "incidentmanagerio_incidents" in combined or "incidentmanagerio_alerts" in combined:
      return "incidentmanagerio"
    if "oneuptime_incidents" in combined or "oneuptime_alerts" in combined:
      return "oneuptime"
    if "squzy_incidents" in combined or "squzy_alerts" in combined:
      return "squzy"
    if "crisescontrol_incidents" in combined or "crisescontrol_alerts" in combined:
      return "crisescontrol"
    if "freshservice_incidents" in combined or "freshservice_alerts" in combined:
      return "freshservice"
    if "freshdesk_incidents" in combined or "freshdesk_alerts" in combined:
      return "freshdesk"
    if "happyfox_incidents" in combined or "happyfox_alerts" in combined:
      return "happyfox"
    if "zendesk_incidents" in combined or "zendesk_alerts" in combined:
      return "zendesk"
    if "zohodesk_incidents" in combined or "zohodesk_alerts" in combined:
      return "zohodesk"
    if "helpscout_incidents" in combined or "helpscout_alerts" in combined:
      return "helpscout"
    if "kayako_incidents" in combined or "kayako_alerts" in combined:
      return "kayako"
    if "intercom_incidents" in combined or "intercom_alerts" in combined:
      return "intercom"
    if "front_incidents" in combined or "front_alerts" in combined:
      return "front"
    if "servicedeskplus_incidents" in combined or "servicedeskplus_alerts" in combined:
      return "servicedeskplus"
    if "bmchelix_incidents" in combined or "bmchelix_alerts" in combined:
      return "bmchelix"
    if (
      "solarwindsservicedesk_incidents" in combined
      or "solarwindsservicedesk_alerts" in combined
    ):
      return "solarwindsservicedesk"
    if "invgateservicedesk_incidents" in combined or "invgateservicedesk_alerts" in combined:
      return "invgateservicedesk"
    if "topdesk_incidents" in combined or "topdesk_alerts" in combined:
      return "topdesk"
    if "sysaid_incidents" in combined or "sysaid_alerts" in combined:
      return "sysaid"
    if "opsramp_incidents" in combined or "opsramp_alerts" in combined:
      return "opsramp"
    if "opsgenie_alerts" in combined:
      return "opsgenie"
    return None

  def _deliver_guarded_live_incident_events(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    current_time: datetime,
  ) -> tuple[
    tuple[OperatorIncidentEvent, ...],
    tuple[OperatorIncidentDelivery, ...],
    bool,
  ]:
    persisted_events: list[OperatorIncidentEvent] = []
    delivery_records: list[OperatorIncidentDelivery] = []
    auto_remediation_executed = False
    for incident in incident_events:
      records = self._operator_alert_delivery.deliver(
        incident=incident,
        targets=incident.delivery_targets,
        attempt_number=1,
        phase="initial",
      )
      records = self._apply_delivery_retry_policy(
        records=records,
        current_time=current_time,
      )
      delivery_state = self._resolve_incident_delivery_state(records=records)
      external_record = next((record for record in records if record.external_provider is not None), None)
      paging_status = incident.paging_status
      external_status = incident.external_status
      if external_record is not None and delivery_state in {"delivered", "partial"}:
        if incident.kind == "incident_opened":
          paging_status = "triggered"
          external_status = "triggered"
        elif incident.kind == "incident_resolved":
          paging_status = "resolved"
          external_status = "resolved"
      persisted_events.append(
        replace(
          incident,
          delivery_state=delivery_state,
          delivery_targets=incident.delivery_targets or self._operator_alert_delivery.list_targets(),
          paging_provider=(
            external_record.external_provider if external_record is not None else incident.paging_provider
          ),
          external_provider=(
            external_record.external_provider if external_record is not None else incident.external_provider
          ),
          external_reference=(
            external_record.external_reference if external_record is not None else incident.external_reference
          ),
          external_status=external_status,
          paging_status=paging_status,
        )
      )
      delivery_records.extend(records)
      if incident.kind == "incident_opened":
        persisted_events[-1], auto_results = self._execute_local_incident_remediation(
          incident=persisted_events[-1],
          actor="system",
          current_time=current_time,
        )
        auto_remediation_executed = auto_remediation_executed or bool(auto_results)
        persisted_events[-1], remediation_records = self._request_incident_remediation(
          incident=persisted_events[-1],
          delivery_history=tuple(delivery_records),
          current_time=current_time,
          actor="system",
          detail="incident_opened",
        )
        if remediation_records:
          delivery_records.extend(remediation_records)
    return tuple(persisted_events), tuple(delivery_records), auto_remediation_executed

  def _retry_guarded_live_incident_deliveries(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
  ) -> tuple[OperatorIncidentDelivery, ...]:
    retries: list[OperatorIncidentDelivery] = []
    incidents_by_id = {incident.event_id: incident for incident in incident_events}
    for incident_event_id, target, attempt_number in self._collect_due_incident_retries(
      incident_events=incident_events,
      delivery_history=delivery_history,
      current_time=current_time,
    ):
      incident = incidents_by_id.get(incident_event_id)
      if incident is None:
        continue
      latest = self._latest_incident_delivery_record(
        delivery_history=delivery_history,
        incident_event_id=incident_event_id,
        target=target,
      )
      if latest is None:
        continue
      if latest.phase.startswith("provider_"):
        provider = latest.external_provider or incident.paging_provider or incident.external_provider
        action = latest.provider_action or latest.phase.removeprefix("provider_")
        if provider is None:
          continue
        records = self._operator_alert_delivery.sync_incident_workflow(
          incident=incident,
          provider=provider,
          action=action,
          actor="system",
          detail=f"retry:{latest.phase}",
          payload=self._build_incident_provider_workflow_payload(
            incident=incident,
            action=action,
            actor="system",
            detail=f"retry:{latest.phase}",
          ),
          attempt_number=attempt_number,
        )
      else:
        records = self._operator_alert_delivery.deliver(
          incident=incident,
          targets=(target,),
          attempt_number=attempt_number,
          phase=latest.phase,
        )
      retries.extend(
        self._apply_delivery_retry_policy(
          records=records,
          current_time=current_time,
        )
      )
    return tuple(retries)

  def _collect_due_incident_retries(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
  ) -> tuple[tuple[str, str, int], ...]:
    due_retries: list[tuple[str, str, int]] = []
    incidents_by_id = {incident.event_id: incident for incident in incident_events}
    latest_by_key = self._latest_delivery_records_by_key(delivery_history=delivery_history)

    for latest in latest_by_key.values():
      incident = incidents_by_id.get(latest.incident_event_id)
      if incident is None:
        continue
      if incident.kind == "incident_opened" and not self._incident_is_still_active(
        incident=incident,
        incident_events=incident_events,
      ):
        continue
      if (
        incident.kind == "incident_opened"
        and incident.acknowledgment_state == "acknowledged"
        and not latest.phase.startswith("provider_")
      ):
        continue
      if latest.status != "retry_scheduled" or latest.next_retry_at is None:
        continue
      if latest.next_retry_at > current_time:
        continue
      if latest.attempt_number >= self._operator_alert_delivery_max_attempts:
        continue
      due_retries.append((latest.incident_event_id, latest.target, latest.attempt_number + 1))
    due_retries.sort()
    return tuple(due_retries)

  def _apply_incident_delivery_state(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    delivery_history: tuple[OperatorIncidentDelivery, ...],
  ) -> tuple[OperatorIncidentEvent, ...]:
    latest_by_key = self._latest_delivery_records_by_key(delivery_history=delivery_history)

    refreshed: list[OperatorIncidentEvent] = []
    for incident in incident_events:
      delivery_records = tuple(
        record
        for key, record in latest_by_key.items()
        if key[0] == incident.event_id
        and not key[2].startswith("provider_")
      )
      provider_records = tuple(
        record
        for key, record in latest_by_key.items()
        if key[0] == incident.event_id
        and key[2].startswith("provider_")
      )
      latest_provider_record = self._latest_provider_workflow_record(records=provider_records)
      prefer_provider_authoritative = (
        incident.external_last_synced_at is not None
        and (
          latest_provider_record is None
          or latest_provider_record.attempted_at <= incident.external_last_synced_at
        )
      )
      refreshed.append(
        replace(
          incident,
          delivery_state=self._resolve_incident_delivery_state(records=delivery_records),
          provider_workflow_state=(
            incident.provider_workflow_state
            if prefer_provider_authoritative
            else (
              self._resolve_incident_delivery_state(records=provider_records)
              if provider_records
              else incident.provider_workflow_state
            )
          ),
          provider_workflow_action=(
            incident.provider_workflow_action
            if prefer_provider_authoritative
            else (
              latest_provider_record.provider_action
              if latest_provider_record is not None
              else incident.provider_workflow_action
            )
          ),
          provider_workflow_last_attempted_at=(
            incident.provider_workflow_last_attempted_at
            if prefer_provider_authoritative
            else (
              latest_provider_record.attempted_at
              if latest_provider_record is not None
              else incident.provider_workflow_last_attempted_at
            )
          ),
          provider_workflow_reference=(
            incident.provider_workflow_reference
            if prefer_provider_authoritative
            else (
              latest_provider_record.external_reference
              if latest_provider_record is not None and latest_provider_record.external_reference is not None
              else incident.provider_workflow_reference
            )
          ),
          remediation=self._refresh_incident_remediation_state(
            incident=incident,
            latest_by_key=latest_by_key,
          ),
        )
      )
    refreshed.sort(key=lambda event: event.timestamp, reverse=True)
    return tuple(refreshed)

  def _refresh_incident_remediation_state(
    self,
    *,
    incident: OperatorIncidentEvent,
    latest_by_key: dict[tuple[str, str, str], OperatorIncidentDelivery],
  ) -> OperatorIncidentRemediation:
    remediation = incident.remediation
    if remediation.state == "not_applicable":
      return remediation
    remediation_records = tuple(
      record
      for key, record in latest_by_key.items()
      if key[0] == incident.event_id and key[2] == "provider_remediate"
    )
    if not remediation_records:
      return remediation
    latest_record = self._latest_provider_workflow_record(records=remediation_records)
    prefer_provider_authoritative = (
      incident.external_last_synced_at is not None
      and (
        latest_record is None
        or latest_record.attempted_at <= incident.external_last_synced_at
      )
    )
    if prefer_provider_authoritative:
      return remediation
    next_state = self._resolve_remediation_delivery_state(
      records=remediation_records,
      current_state=remediation.state,
    )
    return replace(
      remediation,
      state=next_state,
      last_attempted_at=(
        latest_record.attempted_at if latest_record is not None else remediation.last_attempted_at
      ),
      provider=(
        latest_record.external_provider
        if latest_record is not None and latest_record.external_provider is not None
        else remediation.provider
      ),
      reference=(
        latest_record.external_reference
        if latest_record is not None and latest_record.external_reference is not None
        else remediation.reference
      ),
      provider_recovery=self._refresh_provider_recovery_phase_graphs(
        provider_recovery=replace(
          remediation.provider_recovery,
          status_machine=self._build_provider_recovery_status_machine(
            existing=remediation.provider_recovery.status_machine,
            remediation_state=next_state,
            event_kind=remediation.provider_recovery.status_machine.last_event_kind,
            workflow_state=self._resolve_incident_delivery_state(records=remediation_records),
            workflow_action=(
              latest_record.provider_action if latest_record is not None else remediation.provider_recovery.status_machine.workflow_action
            ),
            attempt_number=latest_record.attempt_number if latest_record is not None else remediation.provider_recovery.status_machine.attempt_number,
            detail=latest_record.detail if latest_record is not None else remediation.provider_recovery.status_machine.last_detail,
            event_at=latest_record.attempted_at if latest_record is not None else remediation.provider_recovery.status_machine.last_event_at,
          ),
        ),
        synced_at=latest_record.attempted_at if latest_record is not None else self._clock(),
      ),
    )

  def _request_incident_remediation(
    self,
    *,
    incident: OperatorIncidentEvent,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
    actor: str,
    detail: str,
  ) -> tuple[OperatorIncidentEvent, tuple[OperatorIncidentDelivery, ...]]:
    remediation = incident.remediation
    if incident.kind != "incident_opened" or remediation.state in {"not_applicable", "completed"}:
      return incident, ()

    detail_copy = detail.strip() or remediation.detail or remediation.summary or "remediation_requested"
    requested_remediation = replace(
      remediation,
      requested_at=current_time,
      requested_by=actor,
      last_attempted_at=current_time,
    )
    if remediation.owner != "provider":
      return replace(incident, remediation=requested_remediation), ()

    provider = requested_remediation.provider or incident.paging_provider or incident.external_provider
    if provider is None:
      return (
        replace(
          incident,
          remediation=replace(
            requested_remediation,
            state="not_configured",
          ),
        ),
        (),
      )
    normalized_provider = self._normalize_paging_provider(provider)
    supported_providers = {
      self._normalize_paging_provider(candidate)
      for candidate in self._operator_alert_delivery.list_supported_workflow_providers()
    }
    if normalized_provider not in supported_providers:
      return (
        replace(
          incident,
          remediation=replace(
            requested_remediation,
            state="not_supported",
            provider=normalized_provider,
          ),
        ),
        (),
      )

    requested_incident = replace(incident, remediation=requested_remediation)
    records = self._operator_alert_delivery.sync_incident_workflow(
      incident=requested_incident,
      provider=normalized_provider or provider,
      action="remediate",
      actor=actor,
      detail=detail_copy,
      payload=self._build_incident_provider_workflow_payload(
        incident=requested_incident,
        action="remediate",
        actor=actor,
        detail=detail_copy,
      ),
      attempt_number=1,
    )
    records = self._apply_delivery_retry_policy(
      records=records,
      current_time=current_time,
    )
    latest = self._latest_provider_workflow_record(records=records)
    requested_provider_recovery = self._build_provider_recovery_state(
      remediation=requested_remediation,
      next_state=requested_remediation.state,
      provider=normalized_provider or provider,
      detail=detail_copy,
      synced_at=current_time,
      workflow_reference=(
        latest.external_reference
        if latest is not None and latest.external_reference is not None
        else requested_remediation.reference
      ),
      payload={},
      event_kind="local_remediation_requested",
    )
    requested_provider_recovery = replace(
      requested_provider_recovery,
      status_machine=self._build_provider_recovery_status_machine(
        existing=requested_provider_recovery.status_machine,
        remediation_state=requested_remediation.state,
        event_kind="local_remediation_requested",
        workflow_state=(
          self._resolve_incident_delivery_state(records=records)
          if records
          else requested_provider_recovery.status_machine.workflow_state
        ),
        workflow_action="remediate",
        attempt_number=latest.attempt_number if latest is not None else 1,
        detail=detail_copy,
        event_at=latest.attempted_at if latest is not None else current_time,
      ),
    )
    updated_incident = replace(
      incident,
      remediation=replace(
        requested_remediation,
        state=self._resolve_remediation_delivery_state(
          records=records,
          current_state=requested_remediation.state,
        ),
        provider=normalized_provider,
        reference=(
          latest.external_reference
          if latest is not None and latest.external_reference is not None
          else requested_remediation.reference
        ),
        provider_recovery=requested_provider_recovery,
      ),
    )
    return updated_incident, records

  def _resolve_remediation_delivery_state(
    self,
    *,
    records: tuple[OperatorIncidentDelivery, ...],
    current_state: str,
  ) -> str:
    if current_state in {
      "executed",
      "partial",
      "failed",
      "skipped",
      "completed",
      "provider_recovering",
      "provider_recovered",
    }:
      return current_state
    delivery_state = self._resolve_incident_delivery_state(records=records)
    mapping = {
      "delivered": "requested",
      "partial": "requested",
      "retrying": "retrying",
      "failed": "failed",
      "suppressed": "suppressed",
      "not_configured": current_state,
    }
    return mapping.get(delivery_state, current_state)

  def _execute_local_incident_remediation(
    self,
    *,
    incident: OperatorIncidentEvent,
    actor: str,
    current_time: datetime,
  ) -> tuple[OperatorIncidentEvent, tuple[MarketDataRemediationResult, ...]]:
    remediation = incident.remediation
    if remediation.kind in {
      "recent_sync",
      "historical_backfill",
      "candle_repair",
      "venue_fault_review",
      "market_data_review",
    }:
      timeframe, symbols = self._resolve_market_data_remediation_targets(incident=incident)
      if timeframe is None or not symbols:
        return incident, ()

      results_list: list[MarketDataRemediationResult] = []
      for symbol in symbols:
        try:
          results_list.append(
            self._market_data.remediate(
              kind=remediation.kind,
              symbol=symbol,
              timeframe=timeframe,
            )
          )
        except Exception as exc:
          results_list.append(
            MarketDataRemediationResult(
              kind=remediation.kind,
              symbol=symbol,
              timeframe=timeframe,
              status="failed",
              started_at=current_time,
              finished_at=current_time,
              detail=f"market_data_remediation_failed:{exc}",
            )
          )
      results = tuple(results_list)
    elif remediation.kind in {"channel_restore", "order_book_rebuild"}:
      results = self._execute_local_guarded_live_session_remediation(
        incident=incident,
        actor=actor,
        current_time=current_time,
      )
    else:
      return incident, ()
    if not results:
      return incident, ()

    last_attempted_at = max((result.finished_at for result in results), default=current_time)
    local_state = self._resolve_local_remediation_state(results=results)
    local_detail = self._summarize_local_remediation_results(results)
    updated_remediation = replace(
      remediation,
      state=local_state,
      requested_at=current_time,
      requested_by=actor,
      last_attempted_at=last_attempted_at,
      detail=local_detail,
      provider_recovery=self._refresh_provider_recovery_phase_graphs(
        provider_recovery=replace(
          remediation.provider_recovery,
          lifecycle_state=self._provider_recovery_lifecycle_for_remediation_state(local_state),
          detail=local_detail,
          status_machine=self._build_provider_recovery_status_machine(
            existing=remediation.provider_recovery.status_machine,
            remediation_state=local_state,
            event_kind=(
              "local_verification_executed"
              if local_state in {"executed", "completed", "partial", "skipped"}
              else "local_verification_failed"
            ),
            workflow_state=remediation.provider_recovery.status_machine.workflow_state,
            workflow_action=remediation.provider_recovery.status_machine.workflow_action,
            job_state=(
              "verified"
              if local_state in {"executed", "completed"}
              else ("partial" if local_state == "partial" else ("skipped" if local_state == "skipped" else "failed"))
            ),
            sync_state=(
              "bidirectional_synced"
              if remediation.provider_recovery.provider is not None
              and local_state in {"executed", "completed", "partial", "skipped"}
              else ("local_failed" if local_state == "failed" else "local_only")
            ),
            detail=local_detail,
            event_at=last_attempted_at,
            attempt_number=remediation.provider_recovery.status_machine.attempt_number,
          ),
          updated_at=last_attempted_at,
        ),
        synced_at=last_attempted_at,
      ),
    )
    return replace(incident, remediation=updated_remediation), results

  def _execute_local_guarded_live_session_remediation(
    self,
    *,
    incident: OperatorIncidentEvent,
    actor: str,
    current_time: datetime,
  ) -> tuple[MarketDataRemediationResult, ...]:
    state = self._guarded_live_state.load_state()
    run = self._resolve_guarded_live_remediation_run(incident=incident, state=state)
    symbol, timeframe = self._resolve_guarded_live_remediation_identity(
      run=run,
      state=state,
    )
    remediation_kind = incident.remediation.kind
    if run is None:
      return (
        MarketDataRemediationResult(
          kind=remediation_kind,
          symbol=symbol,
          timeframe=timeframe,
          status="failed",
          started_at=current_time,
          finished_at=current_time,
          detail=f"{remediation_kind}:{symbol}:{timeframe}:guarded_live_run_unavailable",
        ),
      )

    session = run.provenance.runtime_session
    remediation_reason = f"incident_remediation:{remediation_kind}"
    try:
      handoff = self._activate_guarded_live_venue_session(
        run=run,
        reason=remediation_reason,
      )
      session_sync = self._sync_guarded_live_session(run=run, handoff=handoff)
      next_handoff = session_sync["handoff"]
      run = self._runs.save_run(run)
      refreshed_state = self._build_guarded_live_state_for_local_session_remediation(
        state=self._guarded_live_state.load_state(),
        run=run,
        actor=actor,
        reason=remediation_reason,
        session_handoff=next_handoff,
      )
      self._persist_guarded_live_state(refreshed_state)
      detail = self._summarize_guarded_live_session_remediation_result(
        remediation_kind=remediation_kind,
        handoff=next_handoff,
      )
      self._append_guarded_live_audit_event(
        kind="guarded_live_incident_local_remediation_executed",
        actor=actor,
        summary=f"Guarded-live local remediation executed for {incident.alert_id}.",
        detail=detail,
        run_id=run.config.run_id,
        session_id=session.session_id if session is not None else None,
      )
      return (
        MarketDataRemediationResult(
          kind=remediation_kind,
          symbol=symbol,
          timeframe=timeframe,
          status="executed",
          started_at=current_time,
          finished_at=self._clock(),
          detail=detail,
        ),
      )
    except Exception as exc:
      detail = f"{remediation_kind}:{symbol}:{timeframe}:guarded_live_session_remediation_failed:{exc}"
      self._append_guarded_live_audit_event(
        kind="guarded_live_incident_local_remediation_failed",
        actor=actor,
        summary=f"Guarded-live local remediation failed for {incident.alert_id}.",
        detail=detail,
        run_id=run.config.run_id,
        session_id=session.session_id if session is not None else None,
      )
      return (
        MarketDataRemediationResult(
          kind=remediation_kind,
          symbol=symbol,
          timeframe=timeframe,
          status="failed",
          started_at=current_time,
          finished_at=self._clock(),
          detail=detail,
        ),
      )

  def _resolve_guarded_live_remediation_run(
    self,
    *,
    incident: OperatorIncidentEvent,
    state: GuardedLiveState,
  ) -> RunRecord | None:
    if incident.run_id is not None and (run := self._runs.get_run(incident.run_id)) is not None:
      return run
    owner_run_id = state.session_handoff.owner_run_id or state.ownership.owner_run_id
    if owner_run_id is None:
      return None
    return self._runs.get_run(owner_run_id)

  @staticmethod
  def _resolve_guarded_live_remediation_identity(
    *,
    run: RunRecord | None,
    state: GuardedLiveState,
  ) -> tuple[str, str]:
    if run is not None:
      symbol = run.config.symbols[0] if run.config.symbols else "unknown"
      timeframe = run.config.timeframe or "unknown"
      return symbol, timeframe
    symbol = state.session_handoff.symbol or state.ownership.symbol or "unknown"
    timeframe = state.session_handoff.timeframe or "unknown"
    return symbol, timeframe

  def _build_guarded_live_state_for_local_session_remediation(
    self,
    *,
    state: GuardedLiveState,
    run: RunRecord,
    actor: str,
    reason: str,
    session_handoff: GuardedLiveVenueSessionHandoff,
  ) -> GuardedLiveState:
    session = run.provenance.runtime_session
    current_time = self._clock()
    existing = state.ownership
    return replace(
      state,
      ownership=GuardedLiveSessionOwnership(
        state="owned",
        owner_run_id=run.config.run_id,
        owner_session_id=session.session_id if session is not None else existing.owner_session_id,
        symbol=run.config.symbols[0] if run.config.symbols else existing.symbol,
        claimed_at=existing.claimed_at if existing.owner_run_id == run.config.run_id else current_time,
        claimed_by=existing.claimed_by if existing.owner_run_id == run.config.run_id else actor,
        last_heartbeat_at=session.last_heartbeat_at if session is not None else existing.last_heartbeat_at,
        last_order_sync_at=current_time,
        last_resumed_at=existing.last_resumed_at,
        last_reason=reason,
        last_released_at=None,
      ),
      order_book=self._build_guarded_live_order_book_sync(run=run),
      session_restore=self._resolve_guarded_live_session_restore_state(
        run=run,
        existing=state.session_restore,
      ),
      session_handoff=self._resolve_guarded_live_session_handoff_state(
        run=run,
        existing=state.session_handoff,
        session_handoff=session_handoff,
      ),
    )

  @staticmethod
  def _summarize_guarded_live_session_remediation_result(
    *,
    remediation_kind: str,
    handoff: GuardedLiveVenueSessionHandoff,
  ) -> str:
    symbol = handoff.symbol or "unknown"
    timeframe = handoff.timeframe or "unknown"
    if remediation_kind == "channel_restore":
      detail = (
        f"{remediation_kind}:{symbol}:{timeframe}:channel_restore={handoff.channel_restore_state};"
        f"continuation={handoff.channel_continuation_state};"
        f"transport={handoff.transport};source={handoff.source};state={handoff.state}"
      )
      if handoff.channel_last_restored_at is not None:
        detail += f";restored_at={handoff.channel_last_restored_at.isoformat()}"
      if handoff.channel_last_continued_at is not None:
        detail += f";continued_at={handoff.channel_last_continued_at.isoformat()}"
      if handoff.issues:
        detail += f";issues={','.join(handoff.issues[:3])}"
      return detail
    detail = (
      f"{remediation_kind}:{symbol}:{timeframe}:order_book={handoff.order_book_state};"
      f"transport={handoff.transport};source={handoff.source};state={handoff.state};"
      f"rebuilds={handoff.order_book_rebuild_count};gaps={handoff.order_book_gap_count}"
    )
    if handoff.order_book_last_rebuilt_at is not None:
      detail += f";rebuilt_at={handoff.order_book_last_rebuilt_at.isoformat()}"
    if handoff.order_book_best_bid_price is not None or handoff.order_book_best_ask_price is not None:
      detail += (
        f";top_of_book={handoff.order_book_best_bid_price or 0.0:.8f}/"
        f"{handoff.order_book_best_ask_price or 0.0:.8f}"
      )
    if handoff.issues:
      detail += f";issues={','.join(handoff.issues[:3])}"
    return detail

  def _resolve_market_data_remediation_targets(
    self,
    *,
    incident: OperatorIncidentEvent,
  ) -> tuple[str | None, tuple[str, ...]]:
    remediation = incident.remediation
    timeframe: str | None = None
    venue: str | None = None
    alert_parts = incident.alert_id.split(":")
    if remediation.kind == "recent_sync" and len(alert_parts) == 3 and alert_parts[1] == "market-data":
      timeframe = alert_parts[2]
    elif remediation.kind in {
      "historical_backfill",
      "candle_repair",
      "venue_fault_review",
      "market_data_review",
    } and len(alert_parts) == 4 and alert_parts[1].startswith("market-data-"):
      venue = alert_parts[2]
      timeframe = alert_parts[3]

    symbols: list[str] = []
    if incident.run_id is not None and (run := self._runs.get_run(incident.run_id)) is not None:
      timeframe = timeframe or run.config.timeframe
      venue = venue or run.config.venue
      return timeframe, tuple(dict.fromkeys(run.config.symbols))

    if timeframe is None:
      return None, ()

    try:
      status = self._market_data.get_status(timeframe)
    except Exception:
      status = None
    if status is not None:
      venue = venue or status.venue
      for instrument in status.instruments:
        symbol = self._symbol_from_instrument_id(instrument.instrument_id)
        if symbol not in symbols:
          symbols.append(symbol)

    if venue is not None and incident.run_id is None:
      live_runs = [
        run
        for run in self._runs.list_runs(mode=RunMode.LIVE.value)
        if run.config.timeframe == timeframe and run.config.venue == venue
      ]
      if live_runs:
        live_symbols = [
          symbol
          for run in live_runs
          for symbol in run.config.symbols
          if symbol in symbols or not symbols
        ]
        if live_symbols:
          symbols = list(dict.fromkeys(live_symbols))

    return timeframe, tuple(dict.fromkeys(symbols))

  @staticmethod
  def _resolve_local_remediation_state(
    *,
    results: tuple[MarketDataRemediationResult, ...],
  ) -> str:
    executed = sum(result.status in {"executed", "skipped"} for result in results)
    failed = sum(result.status == "failed" for result in results)
    if failed and executed:
      return "partial"
    if failed:
      return "failed"
    if results and all(result.status == "skipped" for result in results):
      return "skipped"
    return "executed"

  @staticmethod
  def _summarize_local_remediation_results(
    results: tuple[MarketDataRemediationResult, ...],
  ) -> str:
    if not results:
      return "not_executed"
    detail_copy = [result.detail for result in results if result.detail]
    summary = " ".join(detail_copy[:2]) if detail_copy else "local_remediation_executed"
    if len(detail_copy) > 2:
      summary += f" Additional jobs: {len(detail_copy) - 2}."
    return summary

  def _pull_sync_guarded_live_provider_recovery(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
  ) -> tuple[
    tuple[OperatorIncidentEvent, ...],
    tuple[OperatorIncidentDelivery, ...],
    tuple[OperatorAuditEvent, ...],
    bool,
  ]:
    updated_incidents = incident_events
    effective_delivery_history = delivery_history
    audit_events: list[OperatorAuditEvent] = []
    local_remediation_executed = False

    for incident in tuple(updated_incidents):
      if incident.kind not in {"incident_opened", "incident_resolved"}:
        continue
      provider = self._normalize_paging_provider(
        incident.remediation.provider or incident.paging_provider or incident.external_provider
      )
      if provider is None:
        continue
      if not any((
        incident.provider_workflow_reference,
        incident.external_reference,
        incident.remediation.reference,
      )):
        continue
      try:
        pull_sync = self._operator_alert_delivery.pull_incident_workflow_state(
          incident=incident,
          provider=provider,
        )
      except Exception as exc:
        audit_events.append(
          OperatorAuditEvent(
            event_id=f"guarded-live-incident-provider-pull-sync-failed:{incident.event_id}:{current_time.isoformat()}",
            timestamp=current_time,
            actor="system",
            kind="guarded_live_incident_provider_pull_sync_failed",
            summary=f"Guarded-live provider pull-sync failed for {incident.alert_id}.",
            detail=(
              f"Provider-authoritative pull-sync failed via {provider}. "
              f"Reference: {incident.provider_workflow_reference or incident.external_reference or incident.alert_id}. "
              f"Error: {exc}."
            ),
            run_id=incident.run_id,
            session_id=incident.session_id,
            source="guarded_live",
          )
        )
        continue
      if pull_sync is None:
        continue
      previous_incident = incident
      previous_history = effective_delivery_history
      updated_incident, effective_delivery_history, executed = self._apply_provider_pull_sync(
        incident=incident,
        pull_sync=pull_sync,
        delivery_history=effective_delivery_history,
        current_time=current_time,
      )
      if updated_incident == previous_incident and effective_delivery_history == previous_history:
        continue
      updated_incidents = self._replace_incident_event(
        incident_events=updated_incidents,
        updated_incident=updated_incident,
      )
      local_remediation_executed = local_remediation_executed or executed
      audit_events.append(
        OperatorAuditEvent(
          event_id=f"guarded-live-incident-provider-pull-sync:{updated_incident.event_id}:{pull_sync.synced_at.isoformat()}",
          timestamp=pull_sync.synced_at,
          actor=f"{provider}:pull_sync",
          kind="guarded_live_incident_provider_pull_synced",
          summary=f"Guarded-live provider recovery reconciled for {updated_incident.alert_id}.",
          detail=(
            f"Provider-authoritative pull-sync via {provider}. "
            f"Workflow state: {pull_sync.workflow_state}. "
            f"Recovery state: {pull_sync.remediation_state or 'n/a'}. "
            f"Reference: {pull_sync.workflow_reference or updated_incident.provider_workflow_reference or updated_incident.external_reference or updated_incident.alert_id}. "
            f"Local remediation: {'executed' if executed else 'not_executed'}."
          ),
          run_id=updated_incident.run_id,
          session_id=updated_incident.session_id,
          source="guarded_live",
        )
      )

    return updated_incidents, effective_delivery_history, tuple(audit_events), local_remediation_executed

  def _apply_provider_pull_sync(
    self,
    *,
    incident: OperatorIncidentEvent,
    pull_sync: OperatorIncidentProviderPullSync,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
  ) -> tuple[OperatorIncidentEvent, tuple[OperatorIncidentDelivery, ...], bool]:
    provider = self._normalize_paging_provider(pull_sync.provider) or pull_sync.provider
    synced_at = pull_sync.synced_at or current_time
    payload = self._normalize_incident_workflow_payload(pull_sync.payload)
    detail_copy = (
      pull_sync.detail
      or self._first_non_empty_string(
        payload.get("detail"),
        payload.get("remediation_detail"),
        payload.get("status_detail"),
        payload.get("summary"),
        payload.get("message"),
      )
      or f"{provider}_pull_synced"
    )
    workflow_reference = (
      pull_sync.workflow_reference
      or self._first_non_empty_string(
        payload.get("workflow_reference"),
        payload.get("provider_workflow_reference"),
      )
      or incident.provider_workflow_reference
      or incident.remediation.provider_recovery.workflow_reference
      or incident.external_reference
    )
    external_reference = (
      pull_sync.external_reference
      or incident.external_reference
      or incident.remediation.reference
      or incident.alert_id
    )
    event_kind = self._resolve_provider_pull_sync_event_kind(
      incident=incident,
      pull_sync=pull_sync,
      payload=payload,
    )
    provider_action = (
      self._provider_phase_for_event_kind(event_kind).removeprefix("provider_")
      if event_kind is not None and self._provider_phase_for_event_kind(event_kind) is not None
      else incident.provider_workflow_action
    )
    updated_incident = replace(
      incident,
      paging_provider=provider or incident.paging_provider,
      external_provider=provider or incident.external_provider,
      external_reference=external_reference,
      provider_workflow_reference=workflow_reference,
      external_last_synced_at=synced_at,
      provider_workflow_state=pull_sync.workflow_state or incident.provider_workflow_state,
      provider_workflow_action=provider_action,
      provider_workflow_last_attempted_at=synced_at,
    )
    effective_delivery_history = delivery_history
    executed = False
    incident_changed = updated_incident != incident

    if event_kind == "triggered":
      updated_incident = replace(
        updated_incident,
        external_status="triggered",
        paging_status="triggered",
      )
      incident_changed = updated_incident != incident
    elif event_kind == "acknowledged":
      updated_incident = replace(
        updated_incident,
        acknowledgment_state="acknowledged",
        acknowledged_at=synced_at,
        acknowledged_by=f"{provider}:pull_sync",
        acknowledgment_reason=detail_copy,
        next_escalation_at=None,
        external_status="acknowledged",
        paging_status="acknowledged",
      )
      effective_delivery_history = self._suppress_pending_incident_retries(
        delivery_history=effective_delivery_history,
        incident_event_id=incident.event_id,
        reason=f"provider_pull_synced:{provider}:{event_kind}",
      )
      incident_changed = updated_incident != incident or effective_delivery_history != delivery_history
    elif event_kind == "escalated":
      updated_incident = replace(
        updated_incident,
        escalation_state="escalated",
        last_escalated_at=synced_at,
        last_escalated_by=f"{provider}:pull_sync",
        escalation_reason=detail_copy,
        external_status="escalated",
        paging_status="escalated",
      )
      incident_changed = updated_incident != incident
    elif event_kind == "resolved":
      updated_incident = replace(
        updated_incident,
        external_status="resolved",
        paging_status="resolved",
        next_escalation_at=None,
      )
      effective_delivery_history = self._suppress_pending_incident_retries(
        delivery_history=effective_delivery_history,
        incident_event_id=incident.event_id,
        reason=f"provider_pull_synced:{provider}:{event_kind}",
      )
      incident_changed = updated_incident != incident or effective_delivery_history != delivery_history
    elif event_kind in {
      "remediation_requested",
      "remediation_started",
      "remediation_completed",
      "remediation_failed",
    }:
      next_state = {
        "remediation_requested": "requested",
        "remediation_started": "provider_recovering",
        "remediation_completed": "provider_recovered",
        "remediation_failed": "failed",
      }[event_kind]
      status_machine_payload = self._extract_payload_mapping(payload.get("status_machine"))
      provider_payload = dict(payload)
      provider_payload["status_machine"] = {
        **status_machine_payload,
        "workflow_state": self._first_non_empty_string(
          status_machine_payload.get("workflow_state"),
          pull_sync.workflow_state,
        ),
        "workflow_action": self._first_non_empty_string(
          status_machine_payload.get("workflow_action"),
          "remediate",
        ),
        "sync_state": self._first_non_empty_string(
          status_machine_payload.get("sync_state"),
          "provider_authoritative",
        ),
      }
      updated_incident = self._apply_external_remediation_sync(
        incident=updated_incident,
        next_state=next_state,
        event_kind=event_kind,
        provider=provider,
        actor="pull_sync",
        detail=detail_copy,
        synced_at=synced_at,
        workflow_reference=workflow_reference,
        payload=provider_payload,
      )
      effective_delivery_history = self._suppress_pending_incident_retries(
        delivery_history=effective_delivery_history,
        incident_event_id=incident.event_id,
        reason=f"provider_pull_synced:{provider}:{event_kind}",
        phase="provider_remediate",
      )
      if (
        event_kind == "remediation_completed"
        and incident.remediation.state not in {"executed", "completed", "partial", "failed"}
      ):
        updated_incident, local_results = self._execute_local_incident_remediation(
          incident=updated_incident,
          actor=f"{provider}:pull_sync",
          current_time=synced_at,
        )
        executed = bool(local_results)
      incident_changed = (
        updated_incident != incident
        or effective_delivery_history != delivery_history
        or executed
      )

    if incident_changed and event_kind is not None:
      effective_delivery_history = self._confirm_external_provider_workflow(
        delivery_history=effective_delivery_history,
        incident=incident,
        provider=provider,
        event_kind=event_kind,
        detail=detail_copy,
        occurred_at=synced_at,
        external_reference=workflow_reference or external_reference,
      )

    return updated_incident, effective_delivery_history, executed

  def _resolve_provider_pull_sync_event_kind(
    self,
    *,
    incident: OperatorIncidentEvent,
    pull_sync: OperatorIncidentProviderPullSync,
    payload: dict[str, Any],
  ) -> str | None:
    explicit_event = self._first_non_empty_string(
      payload.get("event_kind"),
      payload.get("recovery_event_kind"),
      payload.get("last_event_kind"),
      self._extract_payload_mapping(payload.get("status_machine")).get("last_event_kind"),
    )
    if explicit_event is not None:
      return self._normalize_external_incident_event_kind(explicit_event)

    remediation_state = self._first_non_empty_string(
      pull_sync.remediation_state,
      payload.get("recovery_state"),
      payload.get("status"),
    )
    if remediation_state is not None:
      normalized_state = remediation_state.strip().lower().replace("-", "_")
      remediation_mapping = {
        "requested": "remediation_requested",
        "provider_requested": "remediation_requested",
        "recovering": "remediation_started",
        "running": "remediation_started",
        "in_progress": "remediation_started",
        "provider_recovering": "remediation_started",
        "recovered": "remediation_completed",
        "provider_recovered": "remediation_completed",
        "completed": "remediation_completed",
        "verified": "remediation_completed",
        "resolved": "resolved",
        "failed": "remediation_failed",
        "provider_failed": "remediation_failed",
      }
      if normalized_state in remediation_mapping:
        return remediation_mapping[normalized_state]

    workflow_state = self._first_non_empty_string(
      pull_sync.workflow_state,
      payload.get("workflow_state"),
    )
    if workflow_state is None:
      return None
    normalized_workflow_state = workflow_state.strip().lower().replace("-", "_")
    workflow_mapping = {
      "triggered": "triggered",
      "open": "triggered",
      "active": "triggered",
      "acknowledged": "acknowledged",
      "escalated": "escalated",
      "resolved": "resolved",
      "closed": "resolved",
    }
    resolved = workflow_mapping.get(normalized_workflow_state)
    if resolved == "resolved" and incident.kind == "incident_opened" and incident.remediation.state != "not_applicable":
      return None
    return resolved

  def _refresh_guarded_live_incident_workflow(
    self,
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
  ) -> tuple[
    tuple[OperatorIncidentEvent, ...],
    tuple[OperatorIncidentDelivery, ...],
    tuple[OperatorAuditEvent, ...],
  ]:
    updated_incidents = incident_events
    effective_delivery_history = delivery_history
    audit_events: list[OperatorAuditEvent] = []

    for incident in incident_events:
      if incident.kind != "incident_opened":
        continue
      if (
        not self._incident_is_still_active(
          incident=incident,
          incident_events=updated_incidents,
        )
        or incident.acknowledgment_state == "acknowledged"
      ):
        continue
      if incident.escalation_level >= self._operator_alert_incident_max_escalations:
        continue

      trigger: str | None = None
      reason: str | None = None
      if self._incident_has_exhausted_initial_delivery(
        incident=incident,
        delivery_history=effective_delivery_history,
      ):
        trigger = "delivery_exhausted"
        reason = "retry_budget_exhausted"
      elif incident.next_escalation_at is not None and incident.next_escalation_at <= current_time:
        trigger = "ack_timeout"
        reason = "ack_timeout_elapsed"
      if trigger is None or reason is None:
        continue

      updated_incident, effective_delivery_history, audit_event = self._escalate_incident_event(
        incident=incident,
        delivery_history=effective_delivery_history,
        current_time=current_time,
        actor="system",
        reason=reason,
        trigger=trigger,
      )
      updated_incidents = self._replace_incident_event(
        incident_events=updated_incidents,
        updated_incident=updated_incident,
      )
      audit_events.append(audit_event)

    for incident in tuple(updated_incidents):
      if incident.kind != "incident_resolved":
        continue
      source_incident = self._find_latest_open_incident_for_alert(
        incident_events=updated_incidents,
        alert_id=incident.alert_id,
        resolved_at=incident.timestamp,
      )
      if source_incident is None:
        continue
      resolved_incident = replace(
        incident,
        paging_provider=source_incident.paging_provider or incident.paging_provider,
        external_provider=source_incident.external_provider or incident.external_provider,
        external_reference=source_incident.external_reference or incident.external_reference,
        provider_workflow_reference=(
          source_incident.provider_workflow_reference or incident.provider_workflow_reference
        ),
        external_status=(
          source_incident.external_status
          if source_incident.external_status != "not_synced"
          else incident.external_status
        ),
        paging_status=(
          source_incident.paging_status
          if source_incident.paging_status != "not_configured"
          else incident.paging_status
        ),
        remediation=source_incident.remediation,
      )
      if resolved_incident != incident:
        updated_incidents = self._replace_incident_event(
          incident_events=updated_incidents,
          updated_incident=resolved_incident,
        )
      if source_incident.external_status == "resolved" or source_incident.paging_status == "resolved":
        continue
      if self._incident_has_provider_workflow_phase(
        incident_event_id=resolved_incident.event_id,
        delivery_history=effective_delivery_history,
        phase="provider_resolve",
      ):
        continue
      resolve_detail = resolved_incident.detail
      remediation_detail = (
        resolved_incident.remediation.detail
        or resolved_incident.remediation.summary
      )
      if remediation_detail:
        resolve_detail = f"{resolve_detail}. Remediation: {remediation_detail}"
      resolved_incident, effective_delivery_history = self._sync_incident_provider_workflow(
        incident=resolved_incident,
        delivery_history=effective_delivery_history,
        current_time=current_time,
        action="resolve",
        actor="system",
        detail=resolve_detail,
        payload=resolved_incident.remediation.provider_payload,
      )
      resolved_incident = replace(
        resolved_incident,
        remediation=replace(
          resolved_incident.remediation,
          provider_recovery=replace(
            resolved_incident.remediation.provider_recovery,
            lifecycle_state="resolved",
            status_machine=self._build_provider_recovery_status_machine(
              existing=resolved_incident.remediation.provider_recovery.status_machine,
              remediation_state="completed",
              event_kind="provider_resolve_requested",
              workflow_state=resolved_incident.provider_workflow_state,
              workflow_action="resolve",
              job_state="resolved",
              sync_state="bidirectional_synced",
              detail=resolve_detail,
              event_at=current_time,
              attempt_number=resolved_incident.remediation.provider_recovery.status_machine.attempt_number,
            ),
            updated_at=current_time,
          ),
        ),
      )
      updated_incidents = self._replace_incident_event(
        incident_events=updated_incidents,
        updated_incident=resolved_incident,
      )
      audit_events.append(
        OperatorAuditEvent(
          event_id=(
            f"guarded-live-incident-provider-resolve:{resolved_incident.event_id}:{current_time.isoformat()}"
          ),
          timestamp=current_time,
          actor="system",
          kind="guarded_live_incident_provider_resolved",
          summary=f"Guarded-live provider workflow resolve synced for {resolved_incident.alert_id}.",
          detail=(
            f"Provider workflow resolve synced via "
            f"{resolved_incident.paging_provider or resolved_incident.external_provider or 'unknown'}. "
            f"Reference: {resolved_incident.provider_workflow_reference or resolved_incident.external_reference or 'n/a'}. "
            f"State: {resolved_incident.provider_workflow_state}."
          ),
          run_id=resolved_incident.run_id,
          session_id=resolved_incident.session_id,
          source="guarded_live",
        )
      )
    return updated_incidents, effective_delivery_history, tuple(audit_events)

  def _apply_delivery_retry_policy(
    self,
    *,
    records: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
  ) -> tuple[OperatorIncidentDelivery, ...]:
    updated: list[OperatorIncidentDelivery] = []
    for record in records:
      if record.status != "failed":
        updated.append(record)
        continue
      if record.attempt_number >= self._operator_alert_delivery_max_attempts:
        updated.append(record)
        continue
      updated.append(
        replace(
          record,
          status="retry_scheduled",
          next_retry_at=current_time + timedelta(
            seconds=self._resolve_delivery_backoff_seconds(record.attempt_number)
          ),
        )
      )
    return tuple(updated)

  def _resolve_delivery_backoff_seconds(self, attempt_number: int) -> int:
    multiplier = self._operator_alert_delivery_backoff_multiplier ** max(attempt_number - 1, 0)
    backoff = int(self._operator_alert_delivery_initial_backoff_seconds * multiplier)
    return min(backoff, self._operator_alert_delivery_max_backoff_seconds)

  @staticmethod
  def _resolve_incident_delivery_state(
    *,
    records: tuple[OperatorIncidentDelivery, ...],
  ) -> str:
    if not records:
      return "not_configured"
    statuses = {record.status for record in records}
    if statuses <= {"delivered", "retry_suppressed"} and "delivered" in statuses:
      return "delivered"
    if "retry_scheduled" in statuses:
      return "retrying"
    if statuses == {"retry_suppressed"}:
      return "suppressed"
    if "delivered" in statuses:
      return "partial"
    return "failed"

  @staticmethod
  def _latest_delivery_records_by_key(
    *,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
  ) -> dict[tuple[str, str, str], OperatorIncidentDelivery]:
    latest_by_key: dict[tuple[str, str, str], OperatorIncidentDelivery] = {}
    for record in delivery_history:
      key = (record.incident_event_id, record.target, record.phase)
      existing = latest_by_key.get(key)
      if existing is None or record.attempt_number > existing.attempt_number:
        latest_by_key[key] = record
    return latest_by_key

  def _latest_incident_delivery_record(
    self,
    *,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    incident_event_id: str,
    target: str,
  ) -> OperatorIncidentDelivery | None:
    latest_by_key = self._latest_delivery_records_by_key(delivery_history=delivery_history)
    candidates = [
      record
      for key, record in latest_by_key.items()
      if key[0] == incident_event_id and key[1] == target
    ]
    if not candidates:
      return None
    candidates.sort(key=lambda record: (record.phase == "escalation", record.attempt_number), reverse=True)
    return candidates[0]

  @staticmethod
  def _latest_provider_workflow_record(
    *,
    records: tuple[OperatorIncidentDelivery, ...],
  ) -> OperatorIncidentDelivery | None:
    if not records:
      return None
    return max(
      records,
      key=lambda record: (
        record.attempted_at,
        record.attempt_number,
      ),
    )

  @staticmethod
  def _replace_incident_event(
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    updated_incident: OperatorIncidentEvent,
  ) -> tuple[OperatorIncidentEvent, ...]:
    replaced = [
      updated_incident if incident.event_id == updated_incident.event_id else incident
      for incident in incident_events
    ]
    replaced.sort(key=lambda event: event.timestamp, reverse=True)
    return tuple(replaced)

  @staticmethod
  def _incident_is_still_active(
    *,
    incident: OperatorIncidentEvent,
    incident_events: tuple[OperatorIncidentEvent, ...],
  ) -> bool:
    if incident.kind != "incident_opened":
      return False
    for candidate in incident_events:
      if candidate.alert_id != incident.alert_id or candidate.kind != "incident_resolved":
        continue
      if candidate.timestamp >= incident.timestamp:
        return False
    return True

  @staticmethod
  def _find_latest_open_incident_for_alert(
    *,
    incident_events: tuple[OperatorIncidentEvent, ...],
    alert_id: str,
    resolved_at: datetime,
  ) -> OperatorIncidentEvent | None:
    candidates = [
      incident
      for incident in incident_events
      if incident.kind == "incident_opened"
      and incident.alert_id == alert_id
      and incident.timestamp <= resolved_at
    ]
    if not candidates:
      return None
    candidates.sort(key=lambda incident: incident.timestamp, reverse=True)
    return candidates[0]

  @staticmethod
  def _incident_has_provider_workflow_phase(
    *,
    incident_event_id: str,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    phase: str,
  ) -> bool:
    latest_by_key = TradingApplication._latest_delivery_records_by_key(
      delivery_history=delivery_history,
    )
    return any(key[0] == incident_event_id and key[2] == phase for key in latest_by_key)

  def _require_active_guarded_live_incident(
    self,
    *,
    state: GuardedLiveState,
    event_id: str,
  ) -> OperatorIncidentEvent:
    incident = next((event for event in state.incident_events if event.event_id == event_id), None)
    if incident is None:
      raise LookupError("Guarded-live incident not found")
    if incident.kind != "incident_opened":
      raise ValueError("Only active incident_opened records can be acknowledged or escalated")
    if not self._incident_is_still_active(incident=incident, incident_events=state.incident_events):
      raise ValueError("Guarded-live incident is no longer active")
    return incident

  def _find_guarded_live_incident_for_external_sync(
    self,
    *,
    state: GuardedLiveState,
    alert_id: str | None,
    external_reference: str | None,
  ) -> OperatorIncidentEvent:
    candidates = [
      incident
      for incident in state.incident_events
      if incident.kind == "incident_opened"
      and (
        (alert_id is not None and incident.alert_id == alert_id)
        or (
          external_reference is not None
          and (
            incident.external_reference == external_reference
            or incident.provider_workflow_reference == external_reference
            or incident.alert_id == external_reference
          )
        )
      )
    ]
    if not candidates:
      raise LookupError("Guarded-live incident not found for external sync")
    candidates.sort(
      key=lambda incident: (
        self._incident_is_still_active(incident=incident, incident_events=state.incident_events),
        incident.timestamp,
      ),
      reverse=True,
    )
    return candidates[0]

  @staticmethod
  def _suppress_pending_incident_retries(
    *,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    incident_event_id: str,
    reason: str,
    phase: str | None = None,
  ) -> tuple[OperatorIncidentDelivery, ...]:
    updated: list[OperatorIncidentDelivery] = []
    for record in delivery_history:
      if record.incident_event_id != incident_event_id:
        updated.append(record)
        continue
      if phase is not None and record.phase != phase:
        updated.append(record)
        continue
      if record.status != "retry_scheduled":
        updated.append(record)
        continue
      updated.append(
        replace(
          record,
          status="retry_suppressed",
          next_retry_at=None,
          detail=f"{record.detail}; retry_suppressed:{reason}",
        )
      )
    return tuple(updated)

  def _sync_incident_provider_workflow(
    self,
    *,
    incident: OperatorIncidentEvent,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
    action: str,
    actor: str,
    detail: str,
    payload: dict[str, Any] | None = None,
  ) -> tuple[OperatorIncidentEvent, tuple[OperatorIncidentDelivery, ...]]:
    provider = incident.paging_provider or incident.external_provider
    if provider is None:
      return (
        replace(
          incident,
          provider_workflow_state="not_configured",
          provider_workflow_action=action,
        ),
        delivery_history,
      )
    normalized_provider = self._normalize_paging_provider(provider)
    supported_providers = {
      self._normalize_paging_provider(candidate)
      for candidate in self._operator_alert_delivery.list_supported_workflow_providers()
    }
    if normalized_provider not in supported_providers:
      return (
        replace(
          incident,
          paging_provider=normalized_provider,
          provider_workflow_state="not_supported",
          provider_workflow_action=action,
          provider_workflow_last_attempted_at=current_time,
        ),
        delivery_history,
      )

    records = self._operator_alert_delivery.sync_incident_workflow(
      incident=incident,
      provider=normalized_provider or provider,
      action=action,
      actor=actor,
      detail=detail,
      payload=self._build_incident_provider_workflow_payload(
        incident=incident,
        action=action,
        actor=actor,
        detail=detail,
        payload=payload,
      ),
      attempt_number=1,
    )
    records = self._apply_delivery_retry_policy(
      records=records,
      current_time=current_time,
    )
    latest = self._latest_provider_workflow_record(records=records)
    updated_incident = replace(
      incident,
      paging_provider=normalized_provider,
      external_provider=normalized_provider or incident.external_provider,
      provider_workflow_action=action,
      provider_workflow_last_attempted_at=(
        latest.attempted_at if latest is not None else current_time
      ),
      provider_workflow_reference=(
        latest.external_reference
        if latest is not None and latest.external_reference is not None
        else incident.provider_workflow_reference
      ),
    )
    return updated_incident, tuple((*records, *delivery_history))

  def _confirm_external_provider_workflow(
    self,
    *,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    incident: OperatorIncidentEvent,
    provider: str,
    event_kind: str,
    detail: str,
    occurred_at: datetime,
    external_reference: str | None,
  ) -> tuple[OperatorIncidentDelivery, ...]:
    phase = self._provider_phase_for_event_kind(event_kind)
    if phase is None:
      return delivery_history
    provider_prefix = self._normalize_paging_provider(provider) or provider
    updated_history = self._suppress_pending_incident_retries(
      delivery_history=delivery_history,
      incident_event_id=incident.event_id,
      reason=f"external_confirmed:{provider_prefix}:{event_kind}",
      phase=phase,
    )
    confirmation = OperatorIncidentDelivery(
      delivery_id=f"{incident.event_id}:{provider_prefix}_external:{event_kind}:{occurred_at.isoformat()}",
      incident_event_id=incident.event_id,
      alert_id=incident.alert_id,
      incident_kind=incident.kind,
      target=f"{provider_prefix}_external_sync",
      status="delivered",
      attempted_at=occurred_at,
      detail=f"external_provider_confirmed:{event_kind}:{detail}",
      phase=phase,
      provider_action=phase.removeprefix("provider_"),
      external_provider=provider_prefix,
      external_reference=external_reference,
      source=incident.source,
    )
    return (confirmation, *updated_history)

  @staticmethod
  def _provider_phase_for_event_kind(event_kind: str) -> str | None:
    mapping = {
      "triggered": "provider_trigger",
      "acknowledged": "provider_acknowledge",
      "escalated": "provider_escalate",
      "resolved": "provider_resolve",
      "remediation_requested": "provider_remediate",
      "remediation_started": "provider_remediate",
      "remediation_completed": "provider_remediate",
      "remediation_failed": "provider_remediate",
    }
    return mapping.get(event_kind)

  def _incident_has_exhausted_initial_delivery(
    self,
    *,
    incident: OperatorIncidentEvent,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
  ) -> bool:
    latest_by_key = self._latest_delivery_records_by_key(delivery_history=delivery_history)
    initial_records = [
      record
      for key, record in latest_by_key.items()
      if key[0] == incident.event_id and key[2] == "initial"
    ]
    return any(record.status == "failed" for record in initial_records)

  def _escalate_incident_event(
    self,
    *,
    incident: OperatorIncidentEvent,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
    actor: str,
    reason: str,
    trigger: str,
  ) -> tuple[OperatorIncidentEvent, tuple[OperatorIncidentDelivery, ...], OperatorAuditEvent]:
    escalation_targets = incident.escalation_targets or incident.delivery_targets
    if not escalation_targets:
      raise ValueError("incident escalation has no configured delivery targets")

    updated_delivery_history = self._suppress_pending_incident_retries(
      delivery_history=delivery_history,
      incident_event_id=incident.event_id,
      reason=f"escalated:{trigger}",
      phase="initial",
    )
    next_level = incident.escalation_level + 1
    next_escalation_at = None
    if (
      incident.acknowledgment_state != "acknowledged"
      and next_level < self._operator_alert_incident_max_escalations
    ):
      next_escalation_at = current_time + timedelta(
        seconds=self._resolve_incident_escalation_backoff_seconds(next_level)
      )

    updated_incident = replace(
      incident,
      escalation_level=next_level,
      escalation_state="escalated",
      last_escalated_at=current_time,
      last_escalated_by=actor,
      escalation_reason=reason,
      next_escalation_at=next_escalation_at,
    )
    escalation_deliveries = self._operator_alert_delivery.deliver(
      incident=updated_incident,
      targets=escalation_targets,
      attempt_number=1,
      phase="escalation",
    )
    escalation_deliveries = self._apply_delivery_retry_policy(
      records=escalation_deliveries,
      current_time=current_time,
    )
    updated_delivery_history = tuple((*escalation_deliveries, *updated_delivery_history))
    updated_incident, updated_delivery_history = self._sync_incident_provider_workflow(
      incident=updated_incident,
      delivery_history=updated_delivery_history,
      current_time=current_time,
      action="escalate",
      actor=actor,
      detail=reason,
    )
    audit_event = OperatorAuditEvent(
      event_id=f"guarded-live-incident-escalated:{incident.event_id}:{current_time.isoformat()}",
      timestamp=current_time,
      actor=actor,
      kind="guarded_live_incident_escalated",
      summary=f"Guarded-live incident escalated for {incident.alert_id}.",
      detail=(
        f"Trigger: {trigger}. Reason: {reason}. Escalation level {next_level} "
        f"sent via {', '.join(escalation_targets)}. "
        f"Provider workflow: {updated_incident.provider_workflow_state}."
      ),
      run_id=incident.run_id,
      session_id=incident.session_id,
      source="guarded_live",
    )
    return updated_incident, updated_delivery_history, audit_event

  def _resolve_incident_escalation_backoff_seconds(self, escalation_level: int) -> int:
    multiplier = self._operator_alert_incident_escalation_backoff_multiplier ** max(escalation_level - 1, 0)
    backoff = int(self._operator_alert_incident_ack_timeout_seconds * multiplier)
    return min(backoff, self._operator_alert_delivery_max_backoff_seconds)

  def _build_live_operator_alerts_for_run(
    self,
    *,
    run: RunRecord,
    current_time: datetime,
  ) -> list[OperatorAlert]:
    session = run.provenance.runtime_session
    if session is None:
      return []

    alerts: list[OperatorAlert] = []
    symbol = run.config.symbols[0] if run.config.symbols else run.config.run_id
    delivery_targets = self._guarded_live_delivery_targets()
    failed_event = self._latest_runtime_note_event(run=run, kind="guarded_live_worker_failed")
    if failed_event is not None or session.lifecycle_state == "failed" or run.status == RunStatus.FAILED:
      detected_at = (
        failed_event["timestamp"]
        or run.ended_at
        or session.last_heartbeat_at
        or run.started_at
      )
      detail = failed_event["detail"] if failed_event is not None else (
        run.notes[-1] if run.notes else "Guarded-live worker entered a failed runtime state."
      )
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:worker-failed:{run.config.run_id}:{session.session_id}",
          severity="critical",
          category="worker_failure",
          summary=f"Guarded-live worker failed for {symbol}.",
          detail=detail,
          detected_at=detected_at,
          run_id=run.config.run_id,
          session_id=session.session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    heartbeat_at = session.last_heartbeat_at or session.started_at
    heartbeat_age_seconds = (current_time - heartbeat_at).total_seconds()
    if (
      run.status == RunStatus.RUNNING
      and session.lifecycle_state == "active"
      and heartbeat_age_seconds > session.heartbeat_timeout_seconds
    ):
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:worker-stale:{run.config.run_id}:{session.session_id}",
          severity="warning",
          category="stale_runtime",
          summary=f"Guarded-live worker heartbeat is stale for {symbol}.",
          detail=(
            f"Last heartbeat at {heartbeat_at.isoformat()} exceeded the "
            f"{session.heartbeat_timeout_seconds}s timeout while the live run remains active."
          ),
          detected_at=heartbeat_at,
          run_id=run.config.run_id,
          session_id=session.session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    risk_issues: list[str] = []
    latest_equity = run.equity_curve[-1] if run.equity_curve else None
    max_drawdown_pct = run.metrics.get("max_drawdown_pct")
    if isinstance(max_drawdown_pct, Number) and float(max_drawdown_pct) >= self._guarded_live_drawdown_breach_pct:
      risk_issues.append(
        f"max drawdown {float(max_drawdown_pct):.2f}% breached the "
        f"{self._guarded_live_drawdown_breach_pct:.2f}% guardrail"
      )
    total_return_pct = run.metrics.get("total_return_pct")
    if isinstance(total_return_pct, Number) and float(total_return_pct) <= -self._guarded_live_loss_breach_pct:
      risk_issues.append(
        f"total return {float(total_return_pct):.2f}% breached the "
        f"-{self._guarded_live_loss_breach_pct:.2f}% loss guardrail"
      )
    if latest_equity is not None and latest_equity.cash < -self._guarded_live_balance_tolerance:
      risk_issues.append(
        f"cash balance fell below zero to {latest_equity.cash:.2f}"
      )
    if latest_equity is not None and latest_equity.equity > self._guarded_live_balance_tolerance:
      pending_buy_notional = self._estimate_guarded_live_open_buy_notional(run)
      gross_open_risk = max(latest_equity.exposure, 0.0) + pending_buy_notional
      gross_open_risk_ratio = gross_open_risk / latest_equity.equity
      if gross_open_risk_ratio > self._guarded_live_gross_open_risk_ratio:
        risk_issues.append(
          f"gross open risk reached {gross_open_risk_ratio:.2f}x equity "
          f"({gross_open_risk:.2f} notional including {pending_buy_notional:.2f} pending buy notional)"
        )
    if risk_issues:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:risk-breach:{run.config.run_id}:{session.session_id}",
          severity="critical",
          category="risk_breach",
          summary=f"Guarded-live risk guardrail breached for {symbol}.",
          detail=(
            "; ".join(risk_issues)
            + (
              f". Latest equity {latest_equity.equity:.2f}."
              if latest_equity is not None
              else ""
            )
          ),
          detected_at=(
            latest_equity.timestamp
            if latest_equity is not None
            else heartbeat_at
          ),
          run_id=run.config.run_id,
          session_id=session.session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if run.status == RunStatus.RUNNING and session.recovery_count >= self._guarded_live_recovery_alert_threshold:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:recovery-loop:{run.config.run_id}:{session.session_id}",
          severity="critical" if session.recovery_count >= self._guarded_live_recovery_alert_threshold + 1 else "warning",
          category="runtime_recovery",
          summary=f"Guarded-live worker recovery loop detected for {symbol}.",
          detail=(
            f"Runtime session recovered {session.recovery_count} times. "
            f"Last recovery: {session.last_recovery_reason or 'unknown'} at "
            f"{session.last_recovered_at.isoformat() if session.last_recovered_at is not None else 'n/a'}."
          ),
          detected_at=session.last_recovered_at or heartbeat_at,
          run_id=run.config.run_id,
          session_id=session.session_id,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if run.status == RunStatus.RUNNING:
      stale_orders = []
      for order in run.orders:
        if order.status not in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}:
          continue
        synced_at = order.last_synced_at or order.updated_at or order.created_at
        if (current_time - synced_at).total_seconds() <= session.heartbeat_timeout_seconds:
          continue
        stale_orders.append((order, synced_at))
      if stale_orders:
        stale_order_ids = ", ".join(order.order_id for order, _ in stale_orders[:3])
        oldest_sync_at = min(synced_at for _, synced_at in stale_orders)
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:order-sync:{run.config.run_id}:{session.session_id}",
            severity="warning",
            category="order_sync",
            summary=f"Guarded-live venue order sync is stale for {symbol}.",
            detail=(
              f"{len(stale_orders)} active order(s) have not synced within "
              f"{session.heartbeat_timeout_seconds}s. Orders: {stale_order_ids}."
            ),
            detected_at=oldest_sync_at,
            run_id=run.config.run_id,
            session_id=session.session_id,
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
    return alerts

  def _estimate_guarded_live_open_buy_notional(self, run: RunRecord) -> float:
    pending_buy_notional = 0.0
    for order in run.orders:
      if order.side != OrderSide.BUY:
        continue
      if order.status not in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}:
        continue
      remaining_quantity = self._resolve_guarded_live_order_remaining_quantity(order)
      if remaining_quantity <= self._guarded_live_balance_tolerance:
        continue
      reference_price = order.requested_price or order.average_fill_price or 0.0
      if reference_price <= self._guarded_live_balance_tolerance:
        continue
      pending_buy_notional += remaining_quantity * reference_price
    return pending_buy_notional

  @staticmethod
  def _symbol_from_instrument_id(instrument_id: str) -> str:
    return instrument_id.split(":", 1)[1] if ":" in instrument_id else instrument_id

  @staticmethod
  def _extract_market_data_venue_semantics(
    *,
    venue: str,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    prefix = f"{venue}_"
    semantics: list[str] = []
    for issue in issues:
      if not issue.startswith(prefix):
        continue
      semantic = issue.removeprefix(prefix)
      semantics.append(
        {
          "timeout": "timeout",
          "rate_limited": "rate limit",
          "network_fault": "network fault",
          "auth_fault": "authentication fault",
          "symbol_unavailable": "symbol unavailable",
          "maintenance": "maintenance",
          "upstream_fault": "upstream fault",
        }.get(semantic, semantic.replace("_", " "))
      )
    return tuple(dict.fromkeys(semantics))

  @staticmethod
  def _merge_operator_alert_history(
    *,
    existing: tuple[OperatorAlert, ...],
    active_alerts: list[OperatorAlert],
    current_time: datetime,
  ) -> tuple[OperatorAlert, ...]:
    history_by_id = {alert.alert_id: alert for alert in existing}
    active_ids = {alert.alert_id for alert in active_alerts}

    for alert in active_alerts:
      previous = history_by_id.get(alert.alert_id)
      detected_at = (
        previous.detected_at
        if previous is not None and previous.status == "active"
        else alert.detected_at
      )
      history_by_id[alert.alert_id] = replace(
        alert,
        detected_at=detected_at,
        status="active",
        resolved_at=None,
        delivery_targets=alert.delivery_targets or (previous.delivery_targets if previous is not None else ()),
      )

    for alert_id, previous in tuple(history_by_id.items()):
      if alert_id in active_ids or previous.status != "active":
        continue
      history_by_id[alert_id] = replace(
        previous,
        status="resolved",
        resolved_at=current_time,
      )

    merged = sorted(
      history_by_id.values(),
      key=lambda alert: (alert.resolved_at or alert.detected_at, alert.detected_at),
      reverse=True,
    )
    return tuple(merged)

  def _build_operator_alerts_for_run(
    self,
    *,
    run: RunRecord,
    current_time: datetime,
  ) -> list[OperatorAlert]:
    session = run.provenance.runtime_session
    if session is None:
      return []

    alerts: list[OperatorAlert] = []
    symbol = run.config.symbols[0] if run.config.symbols else run.config.run_id
    failed_event = self._latest_runtime_note_event(run=run, kind="sandbox_worker_failed")
    if failed_event is not None or session.lifecycle_state == "failed" or run.status == RunStatus.FAILED:
      detected_at = (
        failed_event["timestamp"]
        or run.ended_at
        or session.last_heartbeat_at
        or run.started_at
      )
      detail = failed_event["detail"] if failed_event is not None else (
        run.notes[-1] if run.notes else "Sandbox worker entered a failed runtime state."
      )
      alerts.append(
        OperatorAlert(
          alert_id=f"runtime-failed:{run.config.run_id}:{detected_at.isoformat()}",
          severity="critical",
          category="worker_failure",
          summary=f"Sandbox worker failed for {symbol}.",
          detail=detail,
          detected_at=detected_at,
          run_id=run.config.run_id,
          session_id=session.session_id,
        )
      )

    heartbeat_at = session.last_heartbeat_at or session.started_at
    heartbeat_age_seconds = (current_time - heartbeat_at).total_seconds()
    if (
      run.status == RunStatus.RUNNING
      and session.lifecycle_state == "active"
      and heartbeat_age_seconds > session.heartbeat_timeout_seconds
    ):
      alerts.append(
        OperatorAlert(
          alert_id=f"runtime-stale:{run.config.run_id}:{current_time.isoformat()}",
          severity="warning",
          category="stale_runtime",
          summary=f"Sandbox worker heartbeat is stale for {symbol}.",
          detail=(
            f"Last heartbeat at {heartbeat_at.isoformat()} exceeded the "
            f"{session.heartbeat_timeout_seconds}s timeout while the run remains active."
          ),
          detected_at=current_time,
          run_id=run.config.run_id,
          session_id=session.session_id,
        )
      )
    return alerts

  def _build_operator_audit_events_for_run(
    self,
    *,
    run: RunRecord,
    current_time: datetime,
  ) -> list[OperatorAuditEvent]:
    session = run.provenance.runtime_session
    if session is None:
      return []

    events: list[OperatorAuditEvent] = [
      OperatorAuditEvent(
        event_id=f"runtime-started:{run.config.run_id}:{session.started_at.isoformat()}",
        timestamp=session.started_at,
        actor="system",
        kind="sandbox_worker_started",
        summary=f"Sandbox worker started for {run.config.symbols[0]}.",
        detail=(
          f"Session {session.session_id} started with {session.primed_candle_count} primed candles "
          f"and {session.processed_tick_count} processed ticks."
        ),
        run_id=run.config.run_id,
        session_id=session.session_id,
      )
    ]

    for note in run.notes:
      if note == "Sandbox run stopped by operator.":
        timestamp = run.ended_at or current_time
        events.append(
          OperatorAuditEvent(
            event_id=f"audit:sandbox_worker_stopped:{run.config.run_id}:{timestamp.isoformat()}",
            timestamp=timestamp,
            actor="operator",
            kind="sandbox_worker_stopped",
            summary=self._build_runtime_audit_summary(run=run, kind="sandbox_worker_stopped"),
            detail=note,
            run_id=run.config.run_id,
            session_id=session.session_id,
          )
        )
        continue
      if parsed := self._parse_runtime_note_event(note):
        events.append(
          OperatorAuditEvent(
            event_id=f"audit:{parsed['kind']}:{run.config.run_id}:{parsed['timestamp'].isoformat()}",
            timestamp=parsed["timestamp"],
            actor="system",
            kind=parsed["kind"],
            summary=self._build_runtime_audit_summary(run=run, kind=parsed["kind"]),
            detail=parsed["detail"],
            run_id=run.config.run_id,
            session_id=session.session_id,
          )
        )

    heartbeat_at = session.last_heartbeat_at or session.started_at
    if (
      run.status == RunStatus.RUNNING
      and session.lifecycle_state == "active"
      and (current_time - heartbeat_at).total_seconds() > session.heartbeat_timeout_seconds
    ):
      events.append(
        OperatorAuditEvent(
          event_id=f"audit:sandbox_worker_stale:{run.config.run_id}:{current_time.isoformat()}",
          timestamp=current_time,
          actor="system",
          kind="sandbox_worker_stale",
          summary=f"Sandbox worker stale state detected for {run.config.symbols[0]}.",
          detail=(
            f"Heartbeat timeout exceeded after {session.heartbeat_timeout_seconds}s without an update."
          ),
          run_id=run.config.run_id,
          session_id=session.session_id,
        )
      )
    return events

  def _latest_runtime_note_event(
    self,
    *,
    run: RunRecord,
    kind: str,
  ) -> dict[str, datetime | str] | None:
    for note in reversed(run.notes):
      parsed = self._parse_runtime_note_event(note)
      if parsed is not None and parsed["kind"] == kind:
        return parsed
    return None

  def _parse_runtime_note_event(self, note: str) -> dict[str, datetime | str] | None:
    parts = note.split(" | ", 2)
    if len(parts) == 3:
      timestamp_raw, kind, detail = parts
      if kind.startswith("sandbox_worker_") or kind.startswith("guarded_live_worker_"):
        return {
          "timestamp": datetime.fromisoformat(timestamp_raw),
          "kind": kind,
          "detail": detail,
        }
    return None

  @staticmethod
  def _build_runtime_audit_summary(*, run: RunRecord, kind: str) -> str:
    symbol = run.config.symbols[0] if run.config.symbols else run.config.run_id
    summary_by_kind = {
      "guarded_live_worker_failed": f"Guarded-live worker failed for {symbol}.",
      "guarded_live_worker_recovered": f"Guarded-live worker recovered for {symbol}.",
      "sandbox_worker_recovered": f"Sandbox worker recovered for {symbol}.",
      "sandbox_worker_failed": f"Sandbox worker failed for {symbol}.",
      "sandbox_worker_stopped": f"Sandbox worker stopped by operator for {symbol}.",
    }
    return summary_by_kind.get(kind, f"Sandbox worker runtime event for {symbol}.")

  def _simulate_run(
    self,
    *,
    config: RunConfig,
    active_bars: int | None,
    strategy: StrategyRuntime | None = None,
    strategy_snapshot: StrategySnapshot | None = None,
  ) -> RunRecord:
    if strategy is None:
      strategy, _, strategy_snapshot = self._prepare_strategy(
        strategy_id=config.strategy_id,
        parameters=config.parameters,
      )
    loaded = self._data_engine.load_frame(config=config, active_bars=active_bars)
    run = self._run_supervisor.create_native_run(config=config, strategy=strategy_snapshot)
    run.provenance.market_data = loaded.lineage
    run.provenance.market_data_by_symbol = loaded.lineage_by_symbol
    self._attach_rerun_boundary(run)
    data = loaded.frame
    if data.empty:
      run.notes.append("No candles available for the requested range.")
      run.status = RunStatus.FAILED
      return run

    enriched = strategy.build_feature_frame(data, config.parameters)
    warmup = strategy.warmup_spec().required_bars
    cache = StateCache(
      instrument_id=f"{config.venue}:{config.symbols[0]}",
      cash=config.initial_cash,
    )

    for index in range(max(warmup, 2), len(enriched)):
      history = enriched.iloc[: index + 1]
      latest_row = history.iloc[-1]
      state = cache.snapshot(
        timestamp=latest_row["timestamp"].to_pydatetime(),
        parameters=config.parameters,
      )
      decision = strategy.evaluate(history, config.parameters, state)
      latest_row = history.iloc[-1]
      self._execution_engine.apply_decision(
        run=run,
        config=config,
        decision=decision,
        cache=cache,
        market_price=float(latest_row["close"]),
      )

    run.metrics = summarize_performance(
      initial_cash=config.initial_cash,
      equity_curve=run.equity_curve,
      closed_trades=run.closed_trades,
    )
    return run

  def _prepare_strategy(
    self,
    *,
    strategy_id: str,
    parameters: dict,
  ) -> tuple[StrategyRuntime, StrategyMetadata, StrategySnapshot]:
    strategy = self._strategies.load(strategy_id)
    metadata = strategy.describe()
    registration = self._strategies.get_registration(metadata.strategy_id)
    return strategy, metadata, self._build_strategy_snapshot(
      strategy=strategy,
      metadata=metadata,
      parameters=parameters,
      registration=registration,
    )

  def _build_strategy_snapshot(
    self,
    *,
    strategy: StrategyRuntime,
    metadata: StrategyMetadata,
    parameters: dict,
    registration: StrategyRegistration | None,
  ) -> StrategySnapshot:
    metadata = _apply_registration_snapshot_metadata(
      metadata=metadata,
      registration=registration,
    )
    schema = deepcopy(metadata.parameter_schema)
    requested = deepcopy(parameters)
    resolved = self._resolve_parameters(schema=schema, requested=requested)
    return StrategySnapshot(
      strategy_id=metadata.strategy_id,
      name=metadata.name,
      version=metadata.version,
      runtime=metadata.runtime,
      lifecycle=metadata.lifecycle,
      catalog_semantics=deepcopy(metadata.catalog_semantics),
      version_lineage=metadata.version_lineage or (metadata.version,),
      parameter_snapshot=StrategyParameterSnapshot(
        requested=requested,
        resolved=resolved,
        schema=schema,
      ),
      supported_timeframes=metadata.supported_timeframes,
      warmup=strategy.warmup_spec(),
      reference_id=metadata.reference_id,
      reference_path=metadata.reference_path,
      entrypoint=metadata.entrypoint,
    )

  @staticmethod
  def _resolve_parameters(*, schema: dict, requested: dict) -> dict:
    resolved: dict = {}
    for name, definition in schema.items():
      if isinstance(definition, dict) and "default" in definition:
        resolved[name] = deepcopy(definition["default"])
    for name, value in requested.items():
      resolved[name] = deepcopy(value)
    return resolved

  def _attach_rerun_boundary(self, run: RunRecord) -> None:
    market_data = run.provenance.market_data
    if market_data is None:
      run.provenance.rerun_boundary_id = None
      run.provenance.rerun_boundary_state = "range_only"
      return

    strategy = run.provenance.strategy
    symbol_checkpoint_ids = {
      symbol: lineage.sync_checkpoint_id
      for symbol, lineage in sorted(run.provenance.market_data_by_symbol.items())
      if lineage.sync_checkpoint_id is not None
    }
    resolved_parameters = (
      deepcopy(strategy.parameter_snapshot.resolved)
      if strategy is not None
      else deepcopy(run.config.parameters)
    )
    run.provenance.rerun_boundary_id = build_rerun_boundary_identity(
      lane=run.provenance.lane,
      mode=run.config.mode.value,
      strategy_id=run.config.strategy_id,
      strategy_version=run.config.strategy_version,
      resolved_parameters=resolved_parameters,
      venue=run.config.venue,
      symbols=run.config.symbols,
      timeframe=run.config.timeframe,
      initial_cash=run.config.initial_cash,
      fee_rate=run.config.fee_rate,
      slippage_bps=run.config.slippage_bps,
      market_data_reproducibility_state=market_data.reproducibility_state,
      market_data_dataset_identity=market_data.dataset_identity,
      market_data_sync_checkpoint_id=market_data.sync_checkpoint_id,
      market_data_symbol_checkpoint_ids=symbol_checkpoint_ids,
      requested_start_at=market_data.requested_start_at,
      requested_end_at=market_data.requested_end_at,
      effective_start_at=market_data.effective_start_at,
      effective_end_at=market_data.effective_end_at,
      candle_count=market_data.candle_count,
      reference_id=run.provenance.reference_id,
      reference_version=run.provenance.reference_version,
      integration_mode=run.provenance.integration_mode,
      external_command=run.provenance.external_command,
    )
    run.provenance.rerun_boundary_state = market_data.reproducibility_state

  def _resolve_experiment_preset(
    self,
    *,
    preset_id: str | None,
    strategy_id: str,
    timeframe: str,
  ) -> ExperimentPreset | None:
    normalized_preset_id = _normalize_experiment_identifier(preset_id)
    if normalized_preset_id is None:
      return None
    preset = self._presets.get_preset(normalized_preset_id)
    if preset is None:
      raise ValueError(f"Preset not found: {normalized_preset_id}")
    if preset.lifecycle.stage == "archived":
      raise ValueError(f"Preset {normalized_preset_id} is archived and cannot be launched.")
    if preset.strategy_id is not None and preset.strategy_id != strategy_id:
      raise ValueError(
        f"Preset {normalized_preset_id} is pinned to strategy {preset.strategy_id}, not {strategy_id}."
      )
    if preset.timeframe is not None and preset.timeframe != timeframe:
      raise ValueError(
        f"Preset {normalized_preset_id} is pinned to timeframe {preset.timeframe}, not {timeframe}."
      )
    return preset

  def _migrate_legacy_preset_from_run(self, run: RunRecord) -> ExperimentPreset | None:
    preset_id = _normalize_experiment_identifier(run.provenance.experiment.preset_id)
    if preset_id is None:
      return None
    existing = self._presets.get_preset(preset_id)
    if existing is not None:
      return existing
    preset = ExperimentPreset(
      preset_id=preset_id,
      name=preset_id,
      description="Migrated from legacy run metadata.",
      strategy_id=run.config.strategy_id,
      timeframe=run.config.timeframe,
      benchmark_family=_normalize_experiment_identifier(
        run.provenance.experiment.benchmark_family
      ),
      tags=_normalize_experiment_tags(run.provenance.experiment.tags),
      parameters=deepcopy(run.config.parameters),
      lifecycle=ExperimentPreset.Lifecycle(
        stage="draft",
        updated_at=run.started_at,
        updated_by="system",
        last_action="migrated",
        history=(
          ExperimentPreset.LifecycleEvent(
            action="migrated",
            actor="system",
            reason="legacy_run_metadata_migration",
            occurred_at=run.started_at,
            from_stage=None,
            to_stage="draft",
          ),
        ),
      ),
      revisions=(
        _build_preset_revision(
          preset_id=preset_id,
          revision_number=1,
          action="migrated",
          actor="system",
          reason="legacy_run_metadata_migration",
          occurred_at=run.started_at,
          name=preset_id,
          description="Migrated from legacy run metadata.",
          strategy_id=run.config.strategy_id,
          timeframe=run.config.timeframe,
          benchmark_family=_normalize_experiment_identifier(
            run.provenance.experiment.benchmark_family
          ),
          tags=_normalize_experiment_tags(run.provenance.experiment.tags),
          parameters=run.config.parameters,
        ),
      ),
      created_at=run.started_at,
      updated_at=run.started_at,
    )
    return self._presets.save_preset(preset)

  def _resolve_rerun_source(self, *, rerun_boundary_id: str) -> RunRecord:
    candidates = self._runs.list_runs(rerun_boundary_id=rerun_boundary_id)
    if not candidates:
      raise LookupError(f"Rerun boundary not found: {rerun_boundary_id}")
    completed = [run for run in candidates if run.status == RunStatus.COMPLETED]
    return completed[0] if completed else candidates[0]

  def _rerun_from_boundary(
    self,
    *,
    rerun_boundary_id: str,
    target_mode: RunMode,
    requested_mode_label: str,
  ) -> RunRecord:
    source_run = self._resolve_rerun_source(rerun_boundary_id=rerun_boundary_id)
    _ensure_run_action_allowed(
      run=source_run,
      capabilities=self.get_run_surface_capabilities(),
      action_key=f"rerun_{target_mode.value}",
    )
    if len(source_run.config.symbols) != 1:
      raise ValueError(f"Explicit rerun currently supports only single-symbol {requested_mode_label} runs.")
    self._migrate_legacy_preset_from_run(source_run)

    rerun_start_at = self._resolve_rerun_start_at(source_run)
    rerun_end_at = self._resolve_rerun_end_at(source_run)
    rerun_parameters = self._resolve_rerun_parameters(source_run)
    symbol = source_run.config.symbols[0]
    session_window_note: str | None = None

    if target_mode == RunMode.BACKTEST:
      rerun = self.run_backtest(
        strategy_id=source_run.config.strategy_id,
        symbol=symbol,
        timeframe=source_run.config.timeframe,
        initial_cash=source_run.config.initial_cash,
        fee_rate=source_run.config.fee_rate,
        slippage_bps=source_run.config.slippage_bps,
        parameters=rerun_parameters,
        start_at=rerun_start_at,
        end_at=rerun_end_at,
        tags=source_run.provenance.experiment.tags,
        preset_id=source_run.provenance.experiment.preset_id,
        benchmark_family=source_run.provenance.experiment.benchmark_family,
      )
    elif target_mode in {RunMode.SANDBOX, RunMode.PAPER}:
      preview_start_at, preview_end_at, preview_replay_bars = self._resolve_preview_rerun_window(source_run)
      if target_mode == RunMode.SANDBOX:
        if preview_replay_bars is None:
          session_window_note = (
            "Sandbox rerun restored the worker session from the stored effective market-data window."
          )
        else:
          session_window_note = (
            "Sandbox rerun restored the stored worker-session priming window."
          )
        rerun = self._start_sandbox_session(
          strategy_id=source_run.config.strategy_id,
          symbol=symbol,
          timeframe=source_run.config.timeframe,
          initial_cash=source_run.config.initial_cash,
          fee_rate=source_run.config.fee_rate,
          slippage_bps=source_run.config.slippage_bps,
          parameters=rerun_parameters,
          replay_bars=preview_replay_bars,
          start_at=preview_start_at,
          end_at=preview_end_at,
          tags=source_run.provenance.experiment.tags,
          preset_id=source_run.provenance.experiment.preset_id,
          benchmark_family=source_run.provenance.experiment.benchmark_family,
        )
      else:
        if preview_replay_bars is None:
          session_window_note = "Paper rerun seeded the current paper session from the stored effective market-data window."
        else:
          session_window_note = "Paper rerun seeded the current paper session from the stored priming window."
        rerun = self._start_paper_session(
          strategy_id=source_run.config.strategy_id,
          symbol=symbol,
          timeframe=source_run.config.timeframe,
          initial_cash=source_run.config.initial_cash,
          fee_rate=source_run.config.fee_rate,
          slippage_bps=source_run.config.slippage_bps,
          parameters=rerun_parameters,
          replay_bars=preview_replay_bars,
          start_at=preview_start_at,
          end_at=preview_end_at,
          tags=source_run.provenance.experiment.tags,
          preset_id=source_run.provenance.experiment.preset_id,
          benchmark_family=source_run.provenance.experiment.benchmark_family,
        )
    else:
      raise ValueError(f"Unsupported rerun target mode: {target_mode.value}")

    return self._persist_explicit_rerun(
      rerun=rerun,
      source_run=source_run,
      rerun_boundary_id=rerun_boundary_id,
      requested_mode_label=requested_mode_label,
      preview_window_note=session_window_note,
    )

  def _persist_explicit_rerun(
    self,
    *,
    rerun: RunRecord,
    source_run: RunRecord,
    rerun_boundary_id: str,
    requested_mode_label: str,
    preview_window_note: str | None = None,
  ) -> RunRecord:
    rerun.provenance.rerun_source_run_id = source_run.config.run_id
    rerun.provenance.rerun_target_boundary_id = rerun_boundary_id
    rerun.provenance.rerun_match_status = (
      "matched"
      if rerun.provenance.rerun_boundary_id == rerun_boundary_id
      else "drifted"
    )
    rerun.notes.insert(
      0,
      f"Explicit {requested_mode_label} rerun from boundary {rerun_boundary_id} using source run {source_run.config.run_id}.",
    )
    if rerun.config.mode in {RunMode.SANDBOX, RunMode.PAPER} and preview_window_note is not None:
      rerun.notes.insert(
        1,
        preview_window_note,
      )
    if rerun.provenance.rerun_match_status == "matched":
      rerun.notes.append("Explicit rerun matched the stored rerun boundary.")
    else:
      rerun.notes.append(
        "Explicit rerun drifted from the stored rerun boundary. "
        f"Expected {rerun_boundary_id}, got {rerun.provenance.rerun_boundary_id or 'unavailable'}."
      )
      if source_run.config.mode != rerun.config.mode:
        rerun.notes.append(
          "Mode-specific rerun boundary drift is expected when replaying a stored boundary into a different execution mode."
        )
    return self._runs.save_run(rerun)

  def _resolve_rerun_parameters(self, run: RunRecord) -> dict:
    strategy = run.provenance.strategy
    if strategy is not None:
      return deepcopy(strategy.parameter_snapshot.resolved)
    return deepcopy(run.config.parameters)

  @staticmethod
  def _resolve_rerun_start_at(run: RunRecord) -> datetime | None:
    market_data = run.provenance.market_data
    if market_data is None:
      return run.config.start_at
    return (
      market_data.effective_start_at
      or market_data.requested_start_at
      or run.config.start_at
    )

  @staticmethod
  def _resolve_rerun_end_at(run: RunRecord) -> datetime | None:
    market_data = run.provenance.market_data
    if market_data is None:
      return run.config.end_at
    return (
      market_data.effective_end_at
      or market_data.requested_end_at
      or run.config.end_at
    )

  @staticmethod
  def _resolve_preview_rerun_window(run: RunRecord) -> tuple[datetime | None, datetime | None, int | None]:
    market_data = run.provenance.market_data
    if (
      run.config.mode in {RunMode.SANDBOX, RunMode.PAPER}
      and run.config.start_at is None
      and run.config.end_at is None
      and market_data is not None
      and market_data.candle_count > 0
    ):
      return None, None, market_data.candle_count
    return (
      TradingApplication._resolve_rerun_start_at(run),
      TradingApplication._resolve_rerun_end_at(run),
      None,
    )


def _normalize_experiment_filter_value(value: str | None) -> str | None:
  if value is None:
    return None
  candidate = value.strip()
  return candidate or None


def _apply_registration_snapshot_metadata(
  *,
  metadata: StrategyMetadata,
  registration: StrategyRegistration | None,
) -> StrategyMetadata:
  if registration is None or metadata.lifecycle.registered_at is not None:
    return metadata
  base_semantics = metadata.catalog_semantics
  parameter_contract = (
    base_semantics.parameter_contract
    or (
      "Publishes a typed parameter schema for presets and semantic diffs."
      if metadata.parameter_schema
      else "Does not advertise a typed parameter schema; presets can only store freeform parameters."
    )
  )
  operator_notes = tuple(
    dict.fromkeys((*base_semantics.operator_notes, "Imported from a locally registered module path."))
  )
  return replace(
    metadata,
    lifecycle=StrategyLifecycle(
      stage=metadata.lifecycle.stage,
      registered_at=registration.registered_at,
    ),
    catalog_semantics=StrategyCatalogSemantics(
      strategy_kind="imported_module",
      execution_model=(
        base_semantics.execution_model
        or "Loaded from a locally registered module and executed through the declared runtime."
      ),
      parameter_contract=parameter_contract,
      source_descriptor=f"{registration.module_path}:{registration.class_name}",
      operator_notes=operator_notes,
    ),
  )


def _normalize_experiment_identifier(value: str | None) -> str | None:
  candidate = _normalize_experiment_filter_value(value)
  if candidate is None:
    return None
  normalized = re.sub(r"[^a-z0-9._:-]+", "_", candidate.lower())
  normalized = re.sub(r"_+", "_", normalized).strip("_")
  return normalized or None


def _normalize_experiment_tags(tags: Iterable[str] | None) -> tuple[str, ...]:
  if tags is None:
    return ()
  normalized: list[str] = []
  seen: set[str] = set()
  for tag in tags:
    normalized_tag = _normalize_experiment_identifier(tag)
    if normalized_tag is None or normalized_tag in seen:
      continue
    seen.add(normalized_tag)
    normalized.append(normalized_tag)
  return tuple(normalized)


def _normalize_preset_lifecycle_stage(stage: str | None) -> str | None:
  candidate = _normalize_experiment_filter_value(stage)
  if candidate is None:
    return None
  normalized = candidate.lower().replace(" ", "_")
  if normalized not in {"draft", "benchmark_candidate", "sandbox_candidate", "live_candidate", "archived"}:
    return None
  return normalized


def _normalize_preset_lifecycle_action(action: str | None) -> str | None:
  candidate = _normalize_experiment_filter_value(action)
  if candidate is None:
    return None
  normalized = candidate.lower().replace(" ", "_")
  if normalized not in {"promote", "archive", "restore"}:
    return None
  return normalized


def _resolve_preset_lifecycle_target_stage(*, current_stage: str, action: str) -> str:
  normalized_stage = _normalize_preset_lifecycle_stage(current_stage)
  if normalized_stage is None:
    raise ValueError(f"Unsupported preset lifecycle stage: {current_stage}")
  if action == "archive":
    if normalized_stage == "archived":
      raise ValueError("Preset is already archived.")
    return "archived"
  if action == "restore":
    if normalized_stage != "archived":
      raise ValueError("Only archived presets can be restored.")
    return "draft"
  promotion_order = ("draft", "benchmark_candidate", "sandbox_candidate", "live_candidate")
  if normalized_stage == "archived":
    raise ValueError("Archived presets must be restored before promotion.")
  if normalized_stage == promotion_order[-1]:
    raise ValueError("Preset is already at the live_candidate stage.")
  current_index = promotion_order.index(normalized_stage)
  return promotion_order[current_index + 1]


def _merge_preset_parameters(
  *,
  preset: ExperimentPreset | None,
  requested_parameters: dict[str, Any] | None,
) -> dict[str, Any]:
  merged = deepcopy(preset.parameters) if preset is not None else {}
  for key, value in deepcopy(requested_parameters or {}).items():
    merged[key] = value
  return merged


def _build_run_experiment_metadata(
  *,
  tags: Iterable[str] = (),
  preset: ExperimentPreset | None = None,
  benchmark_family: str | None = None,
  strategy_metadata: StrategyMetadata,
) -> RunExperimentMetadata:
  normalized_benchmark_family = _normalize_experiment_identifier(
    benchmark_family or (preset.benchmark_family if preset is not None else None)
  )
  if normalized_benchmark_family is None and strategy_metadata.runtime == "freqtrade_reference":
    normalized_benchmark_family = _normalize_experiment_identifier(
      f"reference:{strategy_metadata.reference_id or strategy_metadata.strategy_id}"
    )
  merged_tags = tuple(tags)
  if preset is not None:
    merged_tags = (*preset.tags, *merged_tags)
  return RunExperimentMetadata(
    tags=_normalize_experiment_tags(merged_tags),
    preset_id=preset.preset_id if preset is not None else None,
    benchmark_family=normalized_benchmark_family,
  )


def _build_preset_revision(
  *,
  preset_id: str,
  revision_number: int,
  action: str,
  actor: str,
  reason: str,
  occurred_at: datetime,
  name: str,
  description: str,
  strategy_id: str | None,
  timeframe: str | None,
  benchmark_family: str | None,
  tags: tuple[str, ...],
  parameters: dict[str, Any],
  source_revision_id: str | None = None,
) -> ExperimentPreset.Revision:
  normalized_actor = (actor or "operator").strip() or "operator"
  normalized_reason = (reason or action).strip() or action
  return ExperimentPreset.Revision(
    revision_id=f"{preset_id}:r{revision_number:04d}",
    actor=normalized_actor,
    reason=normalized_reason,
    created_at=occurred_at,
    action=action,
    source_revision_id=source_revision_id,
    name=name,
    description=description,
    strategy_id=strategy_id,
    timeframe=timeframe,
    benchmark_family=benchmark_family,
    tags=tuple(tags),
    parameters=deepcopy(parameters),
  )


def _serialize_preset_lifecycle_event(event: ExperimentPreset.LifecycleEvent) -> dict[str, Any]:
  payload = asdict(event)
  payload["occurred_at"] = event.occurred_at.isoformat()
  return payload


def serialize_preset_revision(revision: ExperimentPreset.Revision) -> dict[str, Any]:
  payload = asdict(revision)
  payload["tags"] = list(revision.tags)
  payload["created_at"] = revision.created_at.isoformat()
  return payload


def _get_run_surface_capability_family(
  capabilities: RunSurfaceCapabilities,
  family_key: str,
) -> RunSurfaceSharedContract | None:
  contract_key = f"family:{family_key}"
  for contract in capabilities.shared_contracts:
    if contract.contract_kind == "capability_family" and contract.contract_key == contract_key:
      return contract
  return None


def _get_run_surface_capability_surface_rule(
  capabilities: RunSurfaceCapabilities,
  family_key: str,
  surface_key: str,
) -> RunSurfaceCapabilities.SurfaceRule | None:
  family = _get_run_surface_capability_family(capabilities, family_key)
  if family is None:
    return None
  for rule in family.surface_rules:
    if rule.surface_key == surface_key:
      return rule
  return None


def _surface_rule_disabled_reason(surface_key: str) -> str:
  return f"Surface rule {surface_key} is disabled by the run-surface capability contract."


def _serialize_surface_rule_state(
  *,
  capabilities: RunSurfaceCapabilities,
  family_key: str,
  surface_key: str,
) -> dict[str, Any]:
  family = _get_run_surface_capability_family(capabilities, family_key)
  rule = _get_run_surface_capability_surface_rule(capabilities, family_key, surface_key)
  return {
    "enabled": rule is not None,
    "family_key": family_key,
    "family_title": family.title if family is not None else None,
    "surface_key": surface_key,
    "surface_label": rule.surface_label if rule is not None else None,
    "rule_key": rule.rule_key if rule is not None else None,
    "enforcement_point": rule.enforcement_point if rule is not None else None,
    "enforcement_mode": rule.enforcement_mode if rule is not None else None,
    "level": rule.level if rule is not None else None,
    "fallback_behavior": rule.fallback_behavior if rule is not None else None,
    "source_of_truth": rule.source_of_truth if rule is not None else None,
    "reason": None if rule is not None else _surface_rule_disabled_reason(surface_key),
  }


def _build_run_surface_enforcement(capabilities: RunSurfaceCapabilities) -> dict[str, dict[str, Any]]:
  surface_specs = (
    ("comparison_eligibility", "run_list_metric_tiles"),
    ("comparison_eligibility", "boundary_note_panels"),
    ("comparison_eligibility", "order_workflow_gates"),
    ("provenance_semantics", "run_strategy_snapshot"),
    ("provenance_semantics", "reference_provenance_panels"),
    ("provenance_semantics", "benchmark_artifact_summaries"),
    ("execution_controls", "rerun_and_stop_controls"),
    ("execution_controls", "compare_selection_workflow"),
    ("execution_controls", "order_replace_cancel_actions"),
  )
  return {
    surface_key: _serialize_surface_rule_state(
      capabilities=capabilities,
      family_key=family_key,
      surface_key=surface_key,
    )
    for family_key, surface_key in surface_specs
  }


def _serialize_action_availability_entry(
  *,
  capabilities: RunSurfaceCapabilities,
  family_key: str,
  surface_key: str,
  allowed: bool,
  reason: str | None,
) -> dict[str, Any]:
  rule = _get_run_surface_capability_surface_rule(capabilities, family_key, surface_key)
  if rule is None:
    return {
      "allowed": False,
      "reason": _surface_rule_disabled_reason(surface_key),
      "family_key": family_key,
      "surface_key": surface_key,
      "rule_key": None,
      "enforcement_mode": None,
      "level": None,
    }
  return {
    "allowed": allowed,
    "reason": None if allowed else reason,
    "family_key": family_key,
    "surface_key": surface_key,
    "rule_key": rule.rule_key,
    "enforcement_mode": rule.enforcement_mode,
    "level": rule.level,
  }


def _resolve_run_action_unavailability_reason(run: RunRecord, action_key: str) -> str | None:
  if action_key == "compare_select":
    return None
  if action_key.startswith("rerun_"):
    if run.provenance.rerun_boundary_id is None:
      return "Run has no rerun boundary to replay."
    return None
  if action_key == "stop_run":
    if run.config.mode not in {RunMode.SANDBOX, RunMode.PAPER, RunMode.LIVE}:
      return "Only sandbox, paper, or live runs can be stopped by the operator."
    if run.status != RunStatus.RUNNING:
      return f"Run status {run.status.value} is not stoppable."
    return None
  raise ValueError(f"Unsupported run action availability key: {action_key}")


def _build_run_action_availability(
  *,
  run: RunRecord,
  capabilities: RunSurfaceCapabilities,
) -> dict[str, dict[str, Any]]:
  rerun_reason = _resolve_run_action_unavailability_reason(run, "rerun_backtest")
  stop_reason = _resolve_run_action_unavailability_reason(run, "stop_run")
  return {
    "compare_select": _serialize_action_availability_entry(
      capabilities=capabilities,
      family_key="execution_controls",
      surface_key="compare_selection_workflow",
      allowed=True,
      reason=None,
    ),
    "rerun_backtest": _serialize_action_availability_entry(
      capabilities=capabilities,
      family_key="execution_controls",
      surface_key="rerun_and_stop_controls",
      allowed=rerun_reason is None,
      reason=rerun_reason,
    ),
    "rerun_sandbox": _serialize_action_availability_entry(
      capabilities=capabilities,
      family_key="execution_controls",
      surface_key="rerun_and_stop_controls",
      allowed=rerun_reason is None,
      reason=rerun_reason,
    ),
    "rerun_paper": _serialize_action_availability_entry(
      capabilities=capabilities,
      family_key="execution_controls",
      surface_key="rerun_and_stop_controls",
      allowed=rerun_reason is None,
      reason=rerun_reason,
    ),
    "stop_run": _serialize_action_availability_entry(
      capabilities=capabilities,
      family_key="execution_controls",
      surface_key="rerun_and_stop_controls",
      allowed=stop_reason is None,
      reason=stop_reason,
    ),
  }


def _resolve_order_action_unavailability_reason(
  *,
  run: RunRecord,
  order: Order,
  action_key: str,
) -> str | None:
  if run.config.mode != RunMode.LIVE:
    return "Guarded-live order controls are available only for live runs."
  if order.status not in {OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED}:
    return "Only active guarded-live venue orders can be controlled."
  if action_key in {"cancel", "replace"}:
    return None
  raise ValueError(f"Unsupported order action availability key: {action_key}")


def _build_order_action_availability(
  *,
  run: RunRecord,
  order: Order,
  capabilities: RunSurfaceCapabilities,
) -> dict[str, dict[str, Any]]:
  cancel_reason = _resolve_order_action_unavailability_reason(run=run, order=order, action_key="cancel")
  replace_reason = _resolve_order_action_unavailability_reason(run=run, order=order, action_key="replace")
  return {
    "cancel": _serialize_action_availability_entry(
      capabilities=capabilities,
      family_key="execution_controls",
      surface_key="order_replace_cancel_actions",
      allowed=cancel_reason is None,
      reason=cancel_reason,
    ),
    "replace": _serialize_action_availability_entry(
      capabilities=capabilities,
      family_key="execution_controls",
      surface_key="order_replace_cancel_actions",
      allowed=replace_reason is None,
      reason=replace_reason,
    ),
  }


def _ensure_run_action_allowed(
  *,
  run: RunRecord,
  capabilities: RunSurfaceCapabilities,
  action_key: str,
) -> None:
  entry = _build_run_action_availability(run=run, capabilities=capabilities)[action_key]
  if entry["allowed"]:
    return
  raise ValueError(entry["reason"] or f"Run action {action_key} is unavailable.")


def _ensure_order_action_allowed(
  *,
  run: RunRecord,
  order: Order,
  capabilities: RunSurfaceCapabilities,
  action_key: str,
) -> None:
  entry = _build_order_action_availability(
    run=run,
    order=order,
    capabilities=capabilities,
  )[action_key]
  if entry["allowed"]:
    return
  raise ValueError(entry["reason"] or f"Order action {action_key} is unavailable.")


def serialize_run(run: RunRecord, *, capabilities: RunSurfaceCapabilities | None = None) -> dict:
  resolved_capabilities = capabilities or RunSurfaceCapabilities()
  payload = asdict(run)
  payload["config"]["mode"] = run.config.mode.value
  payload["status"] = run.status.value
  payload["provenance"]["external_command"] = list(run.provenance.external_command)
  payload["provenance"]["artifact_paths"] = list(run.provenance.artifact_paths)
  payload["provenance"]["experiment"]["tags"] = list(run.provenance.experiment.tags)
  payload["provenance"]["benchmark_artifacts"] = [
    asdict(artifact)
    for artifact in run.provenance.benchmark_artifacts
  ]
  strategy_snapshot = payload["provenance"].get("strategy")
  if strategy_snapshot is not None:
    strategy_snapshot["version_lineage"] = list(
      run.provenance.strategy.version_lineage or (run.provenance.strategy.version,)
    )
    run_snapshot_rule = _get_run_surface_capability_surface_rule(
      resolved_capabilities,
      "provenance_semantics",
      "run_strategy_snapshot",
    )
    if run_snapshot_rule is None:
      strategy_snapshot["catalog_semantics"] = {
        "strategy_kind": "",
        "execution_model": "",
        "parameter_contract": "",
        "source_descriptor": None,
        "operator_notes": [],
      }
    else:
      strategy_snapshot["catalog_semantics"]["operator_notes"] = list(
        run.provenance.strategy.catalog_semantics.operator_notes
      )
    strategy_snapshot["supported_timeframes"] = list(run.provenance.strategy.supported_timeframes)
    strategy_snapshot["warmup"]["timeframes"] = list(run.provenance.strategy.warmup.timeframes)
  payload["surface_enforcement"] = _build_run_surface_enforcement(resolved_capabilities)
  payload["action_availability"] = _build_run_action_availability(
    run=run,
    capabilities=resolved_capabilities,
  )
  for order_payload, order in zip(payload["orders"], run.orders, strict=True):
    order_payload["action_availability"] = _build_order_action_availability(
      run=run,
      order=order,
      capabilities=resolved_capabilities,
    )
  return payload


def _serialize_run_subresource_envelope(
  run: RunRecord,
  *,
  capabilities: RunSurfaceCapabilities,
  body_key: str,
  body_value: Any,
) -> dict[str, Any]:
  return {
    "run_id": run.config.run_id,
    "run_mode": run.config.mode.value,
    "run_status": run.status.value,
    "surface_enforcement": _build_run_surface_enforcement(capabilities),
    "action_availability": _build_run_action_availability(
      run=run,
      capabilities=capabilities,
    ),
    body_key: body_value,
  }


@dataclass(frozen=True)
class RunSubresourceContract:
  subresource_key: str
  body_key: str
  response_title: str
  route_path: str
  route_name: str


@dataclass(frozen=True)
class RunSubresourceRuntimeBinding:
  contract: RunSubresourceContract
  body_serializer: Callable[[RunRecord, RunSurfaceCapabilities], Any]


@dataclass(frozen=True)
class StandaloneSurfaceRuntimeBinding:
  surface_key: str
  route_path: str
  route_name: str
  response_title: str
  scope: str
  binding_kind: str
  methods: tuple[str, ...] = ("GET",)
  subresource_key: str | None = None
  filter_keys: tuple[str, ...] = ()
  filter_param_specs: tuple["StandaloneSurfaceFilterParamSpec", ...] = ()
  sort_field_specs: tuple["StandaloneSurfaceSortFieldSpec", ...] = ()
  path_param_keys: tuple[str, ...] = ()
  header_keys: tuple[str, ...] = ()
  request_payload_kind: str | None = None


@dataclass(frozen=True)
class StandaloneSurfaceFilterConstraintSpec:
  min_length: int | None = None
  max_length: int | None = None
  ge: float | None = None
  le: float | None = None
  pattern: str | None = None


@dataclass(frozen=True)
class StandaloneSurfaceFilterOpenAPISpec:
  alias: str | None = None
  title: str | None = None
  description: str | None = None
  deprecated: bool = False
  examples: tuple[Any, ...] = ()


@dataclass(frozen=True)
class StandaloneSurfaceFilterOperatorSpec:
  key: str
  label: str
  description: str
  value_shape: str = "scalar"


@dataclass(frozen=True)
class StandaloneSurfaceSortFieldSpec:
  key: str
  label: str
  description: str
  default_direction: str = "asc"
  value_type: str = "string"
  value_path: tuple[str, ...] = ()


@dataclass(frozen=True)
class StandaloneSurfaceFilterParamSpec:
  key: str
  annotation: Any
  default: Any = None
  default_factory: Callable[[], Any] | None = None
  constraints: StandaloneSurfaceFilterConstraintSpec | None = None
  openapi: StandaloneSurfaceFilterOpenAPISpec | None = None
  operators: tuple[StandaloneSurfaceFilterOperatorSpec, ...] = ()
  value_path: tuple[str, ...] = ()


@dataclass(frozen=True)
class StandaloneSurfaceFilterCondition:
  key: str
  operator: str
  value: Any
  group: str | None = None


@dataclass(frozen=True)
class StandaloneSurfaceSortTerm:
  key: str
  direction: str = "asc"


def _build_numeric_range_filter_operators(
  subject: str,
) -> tuple[StandaloneSurfaceFilterOperatorSpec, ...]:
  return (
    StandaloneSurfaceFilterOperatorSpec(
      key="eq",
      label="Equals",
      description=f"Matches {subject} exactly.",
    ),
    StandaloneSurfaceFilterOperatorSpec(
      key="gt",
      label="Greater than",
      description=f"Matches {subject} values greater than the requested threshold.",
    ),
    StandaloneSurfaceFilterOperatorSpec(
      key="ge",
      label="Greater than or equal",
      description=f"Matches {subject} values greater than or equal to the requested threshold.",
    ),
    StandaloneSurfaceFilterOperatorSpec(
      key="lt",
      label="Less than",
      description=f"Matches {subject} values lower than the requested threshold.",
    ),
    StandaloneSurfaceFilterOperatorSpec(
      key="le",
      label="Less than or equal",
      description=f"Matches {subject} values lower than or equal to the requested threshold.",
    ),
  )


def _build_datetime_range_filter_operators(
  subject: str,
) -> tuple[StandaloneSurfaceFilterOperatorSpec, ...]:
  return (
    StandaloneSurfaceFilterOperatorSpec(
      key="eq",
      label="Equals",
      description=f"Matches {subject} exactly.",
    ),
    StandaloneSurfaceFilterOperatorSpec(
      key="gt",
      label="After",
      description=f"Matches {subject} values after the requested timestamp.",
    ),
    StandaloneSurfaceFilterOperatorSpec(
      key="ge",
      label="On or after",
      description=f"Matches {subject} values on or after the requested timestamp.",
    ),
    StandaloneSurfaceFilterOperatorSpec(
      key="lt",
      label="Before",
      description=f"Matches {subject} values before the requested timestamp.",
    ),
    StandaloneSurfaceFilterOperatorSpec(
      key="le",
      label="On or before",
      description=f"Matches {subject} values on or before the requested timestamp.",
    ),
  )


def _extract_runtime_filter_conditions(
  filters: dict[str, Any] | None,
) -> tuple[StandaloneSurfaceFilterCondition, ...]:
  if not filters:
    return ()
  value = filters.get("__filter_conditions__")
  if not isinstance(value, tuple):
    return ()
  return tuple(
    condition
    for condition in value
    if isinstance(condition, StandaloneSurfaceFilterCondition)
  )


def _extract_runtime_sort_terms(
  filters: dict[str, Any] | None,
) -> tuple[StandaloneSurfaceSortTerm, ...]:
  if not filters:
    return ()
  value = filters.get("__sort_terms__")
  if not isinstance(value, tuple):
    return ()
  return tuple(
    term
    for term in value
    if isinstance(term, StandaloneSurfaceSortTerm)
  )


def _normalize_runtime_sort_value(value: Any) -> tuple[int, Any]:
  if value is None:
    return (1, "")
  enum_value = getattr(value, "value", None)
  if isinstance(enum_value, (str, int, float)):
    value = enum_value
  if isinstance(value, datetime):
    return (0, value)
  if isinstance(value, str):
    return (0, value.lower())
  if isinstance(value, (tuple, list, set)):
    return (0, tuple(str(item) for item in value))
  return (0, value)


def _normalize_runtime_numeric_filter_value(value: Any) -> float | int | None:
  if isinstance(value, bool) or not isinstance(value, Number):
    return None
  if isinstance(value, int):
    return value
  return float(value)


def _normalize_runtime_datetime_filter_value(value: Any) -> datetime | None:
  if not isinstance(value, datetime):
    return None
  if value.tzinfo is None:
    return value.replace(tzinfo=UTC)
  return value.astimezone(UTC)


_RUNTIME_QUERY_MISSING = object()


def _default_runtime_query_value_path(
  key: str,
  explicit_path: tuple[str, ...] = (),
) -> tuple[str, ...]:
  if explicit_path:
    return explicit_path
  return tuple(segment for segment in key.split(".") if segment)


def _resolve_runtime_query_path_value(
  item: Any,
  path: tuple[str, ...],
) -> Any:
  current = item
  for segment in path:
    if current is None:
      return None
    if isinstance(current, dict):
      if segment not in current:
        return _RUNTIME_QUERY_MISSING
      current = current[segment]
      continue
    if not hasattr(current, segment):
      return _RUNTIME_QUERY_MISSING
    current = getattr(current, segment)
  return current


def _build_runtime_filter_getters(
  filter_specs: tuple[StandaloneSurfaceFilterParamSpec, ...],
  *,
  overrides: dict[str, Callable[[Any], Any]] | None = None,
) -> dict[str, Callable[[Any], Any]]:
  getters: dict[str, Callable[[Any], Any]] = {}
  for spec in filter_specs:
    path = _default_runtime_query_value_path(spec.key, spec.value_path)
    if not path:
      continue
    getters[spec.key] = lambda item, path=path: _resolve_runtime_query_path_value(item, path)
  if overrides:
    getters.update(overrides)
  return getters


def _build_runtime_sort_getters(
  sort_specs: tuple[StandaloneSurfaceSortFieldSpec, ...],
  *,
  overrides: dict[str, Callable[[Any], Any]] | None = None,
) -> dict[str, Callable[[Any], Any]]:
  getters: dict[str, Callable[[Any], Any]] = {}
  for spec in sort_specs:
    path = _default_runtime_query_value_path(spec.key, spec.value_path)
    if not path:
      continue
    getters[spec.key] = lambda item, path=path: _resolve_runtime_query_path_value(item, path)
  if overrides:
    getters.update(overrides)
  return getters


def _evaluate_runtime_filter_condition(
  candidate_value: Any,
  *,
  operator: str,
  operand: Any,
) -> bool:
  if operator == "eq":
    return candidate_value == operand
  if operator == "prefix":
    return isinstance(candidate_value, str) and isinstance(operand, str) and candidate_value.startswith(operand)
  if operator == "contains_all":
    candidate_values = set(candidate_value or ())
    operand_values = set(operand or ())
    return operand_values.issubset(candidate_values)
  if operator == "contains_any":
    candidate_values = set(candidate_value or ())
    operand_values = set(operand or ())
    return not candidate_values.isdisjoint(operand_values)
  if operator == "include":
    operand_values = tuple(operand or ())
    return candidate_value in operand_values
  if operator in {"gt", "ge", "lt", "le"}:
    candidate_datetime = _normalize_runtime_datetime_filter_value(candidate_value)
    operand_datetime = _normalize_runtime_datetime_filter_value(operand)
    if candidate_datetime is not None and operand_datetime is not None:
      candidate_comparable: float | int | datetime = candidate_datetime
      operand_comparable: float | int | datetime = operand_datetime
    else:
      candidate_number = _normalize_runtime_numeric_filter_value(candidate_value)
      operand_number = _normalize_runtime_numeric_filter_value(operand)
      if candidate_number is None or operand_number is None:
        return False
      candidate_comparable = candidate_number
      operand_comparable = operand_number
    if operator == "gt":
      return candidate_comparable > operand_comparable
    if operator == "ge":
      return candidate_comparable >= operand_comparable
    if operator == "lt":
      return candidate_comparable < operand_comparable
    return candidate_comparable <= operand_comparable
  raise ValueError(f"Unsupported runtime filter operator: {operator}")


def _evaluate_runtime_filter_conditions(
  item: Any,
  conditions: tuple[StandaloneSurfaceFilterCondition, ...] | list[StandaloneSurfaceFilterCondition],
  *,
  filter_getters: dict[str, Callable[[Any], Any]],
  require_known_conditions: bool,
) -> bool:
  known_conditions = 0
  for condition in conditions:
    getter = filter_getters.get(condition.key)
    if getter is None:
      continue
    candidate_value = getter(item)
    if candidate_value is _RUNTIME_QUERY_MISSING:
      continue
    known_conditions += 1
    if not _evaluate_runtime_filter_condition(
      candidate_value,
      operator=condition.operator,
      operand=condition.value,
    ):
      return False
  if require_known_conditions and known_conditions == 0:
    return False
  return True


def _apply_runtime_query_contract(
  items: list[Any],
  *,
  filters: dict[str, Any] | None,
  filter_specs: tuple[StandaloneSurfaceFilterParamSpec, ...] = (),
  sort_specs: tuple[StandaloneSurfaceSortFieldSpec, ...] = (),
  filter_getter_overrides: dict[str, Callable[[Any], Any]] | None = None,
  sort_getter_overrides: dict[str, Callable[[Any], Any]] | None = None,
) -> list[Any]:
  conditions = _extract_runtime_filter_conditions(filters)
  sort_terms = _extract_runtime_sort_terms(filters)
  filter_getters = _build_runtime_filter_getters(
    filter_specs,
    overrides=filter_getter_overrides,
  )
  sort_getters = _build_runtime_sort_getters(
    sort_specs,
    overrides=sort_getter_overrides,
  )
  resolved = list(items)
  if conditions:
    ungrouped_conditions = tuple(
      condition
      for condition in conditions
      if condition.group is None
    )
    grouped_conditions: dict[str, list[StandaloneSurfaceFilterCondition]] = {}
    for condition in conditions:
      if condition.group is None:
        continue
      grouped_conditions.setdefault(condition.group, []).append(condition)
    resolved = [
      item
      for item in resolved
      if _evaluate_runtime_filter_conditions(
        item,
        ungrouped_conditions,
        filter_getters=filter_getters,
        require_known_conditions=False,
      ) and (
        not grouped_conditions
        or any(
          _evaluate_runtime_filter_conditions(
            item,
            group_conditions,
            filter_getters=filter_getters,
            require_known_conditions=True,
          )
          for group_conditions in grouped_conditions.values()
        )
      )
    ]
  for term in reversed(sort_terms):
    getter = sort_getters.get(term.key)
    if getter is None:
      continue
    resolved.sort(
      key=lambda item: _normalize_runtime_sort_value(getter(item)),
      reverse=term.direction == "desc",
    )
  return resolved


def _run_effective_updated_at(run: RunRecord) -> datetime:
  return run.ended_at or run.started_at


def _run_metric_query_value(run: RunRecord, key: str) -> float | int | None:
  return _coerce_metric_value(run.metrics.get(key))


def _apply_runtime_query_to_strategies(
  strategies: list[StrategyMetadata],
  filters: dict[str, Any] | None,
  *,
  binding: StandaloneSurfaceRuntimeBinding,
) -> list[StrategyMetadata]:
  return _apply_runtime_query_contract(
    strategies,
    filters=filters,
    filter_specs=binding.filter_param_specs,
    sort_specs=binding.sort_field_specs,
  )


def _apply_runtime_query_to_presets(
  presets: list[ExperimentPreset],
  filters: dict[str, Any] | None,
  *,
  binding: StandaloneSurfaceRuntimeBinding,
) -> list[ExperimentPreset]:
  return _apply_runtime_query_contract(
    presets,
    filters=filters,
    filter_specs=binding.filter_param_specs,
    sort_specs=binding.sort_field_specs,
  )


def _apply_runtime_query_to_runs(
  runs: list[RunRecord],
  filters: dict[str, Any] | None,
  *,
  binding: StandaloneSurfaceRuntimeBinding,
) -> list[RunRecord]:
  return _apply_runtime_query_contract(
    runs,
    filters=filters,
    filter_specs=binding.filter_param_specs,
    sort_specs=binding.sort_field_specs,
    filter_getter_overrides={
      "updated_at": _run_effective_updated_at,
      "timing.updated_at": _run_effective_updated_at,
    },
    sort_getter_overrides={
      "updated_at": _run_effective_updated_at,
      "timing.updated_at": _run_effective_updated_at,
    },
  )


def _apply_runtime_query_to_comparison(
  comparison: RunComparison,
  filters: dict[str, Any] | None,
  *,
  binding: StandaloneSurfaceRuntimeBinding,
) -> RunComparison:
  run_order_index = {
    run_id: index
    for index, run_id in enumerate(comparison.requested_run_ids)
  }
  narratives = _apply_runtime_query_contract(
    list(comparison.narratives),
    filters=filters,
    filter_specs=binding.filter_param_specs,
    sort_specs=binding.sort_field_specs,
    filter_getter_overrides={
      "narrative_score": lambda narrative: narrative.insight_score,
    },
    sort_getter_overrides={
      "run_id_order": lambda narrative: run_order_index.get(
        narrative.run_id,
        len(run_order_index),
      ),
      "narratives.run_id_order": lambda narrative: run_order_index.get(
        narrative.run_id,
        len(run_order_index),
      ),
      "narrative_score": lambda narrative: narrative.insight_score,
      "narratives.insight_score": lambda narrative: narrative.insight_score,
    },
  )
  return replace(comparison, narratives=tuple(narratives))


def _serialize_run_order_subresource_item(
  run: RunRecord,
  *,
  order: Order,
  capabilities: RunSurfaceCapabilities,
) -> dict[str, Any]:
  return {
    **asdict(order),
    "action_availability": _build_order_action_availability(
      run=run,
      order=order,
      capabilities=capabilities,
    ),
  }


def _serialize_run_orders_subresource_body(
  run: RunRecord,
  *,
  capabilities: RunSurfaceCapabilities,
) -> list[dict[str, Any]]:
  return [
    _serialize_run_order_subresource_item(
      run,
      order=order,
      capabilities=capabilities,
    )
    for order in run.orders
  ]


def _serialize_run_positions_subresource_body(
  run: RunRecord,
  *,
  capabilities: RunSurfaceCapabilities,
) -> list[dict[str, Any]]:
  _ = capabilities
  return [
    asdict(position)
    for position in run.positions.values()
  ]


def _serialize_run_metrics_subresource_body(
  run: RunRecord,
  *,
  capabilities: RunSurfaceCapabilities,
) -> dict[str, Any]:
  _ = capabilities
  return deepcopy(run.metrics)


def _resolve_run_subresource_body_serializer(
  body_key: str,
) -> Callable[[RunRecord, RunSurfaceCapabilities], Any]:
  if body_key == "orders":
    return lambda run, capabilities: _serialize_run_orders_subresource_body(
      run,
      capabilities=capabilities,
    )
  if body_key == "positions":
    return lambda run, capabilities: _serialize_run_positions_subresource_body(
      run,
      capabilities=capabilities,
    )
  if body_key == "metrics":
    return lambda run, capabilities: _serialize_run_metrics_subresource_body(
      run,
      capabilities=capabilities,
    )
  raise ValueError(f"Unsupported run subresource serializer body: {body_key}")


def list_run_subresource_runtime_bindings(
  capabilities: RunSurfaceCapabilities | None = None,
) -> tuple[RunSubresourceRuntimeBinding, ...]:
  resolved_capabilities = capabilities or RunSurfaceCapabilities()
  bindings: list[RunSubresourceRuntimeBinding] = []
  for shared_contract in resolved_capabilities.shared_contracts:
    if shared_contract.contract_kind != "run_subresource":
      continue
    subresource_key = shared_contract.contract_key.removeprefix("subresource:")
    body_key = shared_contract.schema_detail.get("body_key")
    route_path = shared_contract.schema_detail.get("route_path")
    route_name = shared_contract.schema_detail.get("route_name")
    if not all(isinstance(value, str) and value for value in (body_key, route_path, route_name)):
      raise ValueError(f"Invalid run subresource contract metadata: {shared_contract.contract_key}")
    bindings.append(
      RunSubresourceRuntimeBinding(
        contract=RunSubresourceContract(
          subresource_key=subresource_key,
          body_key=body_key,
          response_title=shared_contract.title,
          route_path=route_path,
          route_name=route_name,
        ),
        body_serializer=_resolve_run_subresource_body_serializer(body_key),
      )
    )
  return tuple(bindings)


def list_run_subresource_contracts(
  capabilities: RunSurfaceCapabilities | None = None,
) -> tuple[RunSubresourceContract, ...]:
  return tuple(
    binding.contract
    for binding in list_run_subresource_runtime_bindings(capabilities)
  )


def get_run_subresource_contract(
  subresource_key: str,
  capabilities: RunSurfaceCapabilities | None = None,
) -> RunSubresourceContract:
  for binding in list_run_subresource_runtime_bindings(capabilities):
    if binding.contract.subresource_key == subresource_key:
      return binding.contract
  raise ValueError(f"Unsupported run subresource serializer: {subresource_key}")


def get_run_subresource_runtime_binding(
  subresource_key: str,
  capabilities: RunSurfaceCapabilities | None = None,
) -> RunSubresourceRuntimeBinding:
  for binding in list_run_subresource_runtime_bindings(capabilities):
    if binding.contract.subresource_key == subresource_key:
      return binding
  raise ValueError(f"Unsupported run subresource serializer: {subresource_key}")


def list_standalone_surface_runtime_bindings(
  capabilities: RunSurfaceCapabilities | None = None,
) -> tuple[StandaloneSurfaceRuntimeBinding, ...]:
  resolved_capabilities = capabilities or RunSurfaceCapabilities()
  health_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="health_status",
    route_path="/health",
    route_name="health",
    response_title="Health",
    scope="app",
    binding_kind="health_status",
  )
  capability_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_surface_capabilities",
    route_path="/capabilities/run-surfaces",
    route_name="get_run_surface_capabilities",
    response_title="Run surface capabilities",
    scope="app",
    binding_kind="run_surface_capabilities",
  )
  market_data_status_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="market_data_status",
    route_path="/market-data/status",
    route_name="get_market_data_status",
    response_title="Market data status",
    scope="app",
    binding_kind="market_data_status",
    filter_keys=("timeframe",),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "timeframe",
        str,
        default="5m",
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=2, max_length=10),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Timeframe",
          description="Candlestick timeframe to inspect in market-data status.",
          examples=("5m",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches exactly one timeframe value.",
          ),
        ),
      ),
    ),
  )
  operator_visibility_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_visibility",
    route_path="/operator/visibility",
    route_name="get_operator_visibility",
    response_title="Operator visibility",
    scope="app",
    binding_kind="operator_visibility",
  )
  guarded_live_status_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_status",
    route_path="/guarded-live",
    route_name="get_guarded_live_status",
    response_title="Guarded live status",
    scope="app",
    binding_kind="guarded_live_status",
  )
  strategy_discovery_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="strategy_catalog_discovery",
    route_path="/strategies",
    route_name="list_strategies",
    response_title="Strategy catalog discovery",
    scope="app",
    binding_kind="strategy_catalog_discovery",
    filter_keys=("lane", "lifecycle_stage", "version", "registered_at"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "lane",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Lane",
          description="Filter strategies by runtime lane.",
          examples=("native",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single runtime lane value.",
          ),
        ),
        value_path=("runtime",),
      ),
      StandaloneSurfaceFilterParamSpec(
        "lifecycle_stage",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Lifecycle stage",
          description="Filter strategies by lifecycle stage.",
          examples=("active",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single lifecycle stage.",
          ),
        ),
        value_path=("lifecycle", "stage"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "version",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Version",
          description="Filter strategies by declared version string.",
          examples=("1.0.0",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches one declared version value.",
          ),
          StandaloneSurfaceFilterOperatorSpec(
            key="prefix",
            label="Version prefix",
            description="Matches a version prefix such as a major or minor line.",
          ),
        ),
        value_path=("version",),
      ),
      StandaloneSurfaceFilterParamSpec(
        "registered_at",
        datetime | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Registered at",
          description="Filter imported strategies by registration timestamp.",
          examples=("2025-01-01T00:00:00+00:00",),
        ),
        operators=_build_datetime_range_filter_operators("strategy registration time"),
        value_path=("lifecycle", "registered_at"),
      ),
    ),
    sort_field_specs=(
      StandaloneSurfaceSortFieldSpec(
        key="strategy_id",
        label="Strategy ID",
        description="Sorts by strategy identifier.",
        value_path=("strategy_id",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="runtime",
        label="Runtime lane",
        description="Sorts by runtime lane grouping.",
        value_path=("runtime",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="registered_at",
        label="Registration time",
        description="Sorts imported strategies by registration timestamp.",
        default_direction="desc",
        value_type="datetime",
        value_path=("lifecycle", "registered_at"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="lifecycle.registered_at",
        label="Lifecycle registration time",
        description="Sorts imported strategies by the nested lifecycle registration timestamp.",
        default_direction="desc",
        value_type="datetime",
        value_path=("lifecycle", "registered_at"),
      ),
    ),
  )
  reference_discovery_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="reference_catalog_discovery",
    route_path="/references",
    route_name="list_references",
    response_title="Reference catalog discovery",
    scope="app",
    binding_kind="reference_catalog_discovery",
  )
  preset_discovery_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="preset_catalog_discovery",
    route_path="/presets",
    route_name="list_presets",
    response_title="Preset catalog discovery",
    scope="app",
    binding_kind="preset_catalog_discovery",
    filter_keys=("strategy_id", "timeframe", "lifecycle_stage", "created_at", "updated_at"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "strategy_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Strategy ID",
          description="Filter presets by strategy identifier.",
          examples=("ma_cross_v1",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single strategy identifier.",
          ),
        ),
        value_path=("strategy_id",),
      ),
      StandaloneSurfaceFilterParamSpec(
        "timeframe",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=2, max_length=10),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Timeframe",
          description="Filter presets by configured timeframe.",
          examples=("5m",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single configured timeframe.",
          ),
        ),
        value_path=("timeframe",),
      ),
      StandaloneSurfaceFilterParamSpec(
        "lifecycle_stage",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Lifecycle stage",
          description="Filter presets by lifecycle stage.",
          examples=("draft",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single lifecycle stage.",
          ),
        ),
        value_path=("lifecycle", "stage"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "created_at",
        datetime | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Created at",
          description="Filter presets by creation timestamp.",
          examples=("2025-01-01T00:00:00+00:00",),
        ),
        operators=_build_datetime_range_filter_operators("preset creation time"),
        value_path=("created_at",),
      ),
      StandaloneSurfaceFilterParamSpec(
        "updated_at",
        datetime | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Updated at",
          description="Filter presets by last update timestamp.",
          examples=("2025-01-02T00:00:00+00:00",),
        ),
        operators=_build_datetime_range_filter_operators("preset update time"),
        value_path=("updated_at",),
      ),
    ),
    sort_field_specs=(
      StandaloneSurfaceSortFieldSpec(
        key="updated_at",
        label="Updated at",
        description="Sorts presets by most recent update time.",
        default_direction="desc",
        value_type="datetime",
        value_path=("updated_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="created_at",
        label="Created at",
        description="Sorts presets by creation time.",
        default_direction="desc",
        value_type="datetime",
        value_path=("created_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="preset_id",
        label="Preset ID",
        description="Sorts presets by preset identifier.",
        value_path=("preset_id",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="timestamps.updated_at",
        label="Nested updated at",
        description="Sorts presets by the nested update timestamp contract.",
        default_direction="desc",
        value_type="datetime",
        value_path=("updated_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="timestamps.created_at",
        label="Nested created at",
        description="Sorts presets by the nested creation timestamp contract.",
        default_direction="desc",
        value_type="datetime",
        value_path=("created_at",),
      ),
    ),
  )
  preset_create_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="preset_catalog_create",
    route_path="/presets",
    route_name="create_preset",
    response_title="Create preset",
    scope="app",
    binding_kind="preset_catalog_create",
    methods=("POST",),
    request_payload_kind="preset_create",
  )
  preset_item_get_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="preset_catalog_item_get",
    route_path="/presets/{preset_id}",
    route_name="get_preset",
    response_title="Get preset",
    scope="app",
    binding_kind="preset_catalog_item_get",
    path_param_keys=("preset_id",),
  )
  preset_item_update_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="preset_catalog_item_update",
    route_path="/presets/{preset_id}",
    route_name="update_preset",
    response_title="Update preset",
    scope="app",
    binding_kind="preset_catalog_item_update",
    methods=("PATCH",),
    path_param_keys=("preset_id",),
    request_payload_kind="preset_update",
  )
  preset_revision_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="preset_catalog_revision_list",
    route_path="/presets/{preset_id}/revisions",
    route_name="list_preset_revisions",
    response_title="List preset revisions",
    scope="app",
    binding_kind="preset_catalog_revision_list",
    path_param_keys=("preset_id",),
  )
  preset_revision_restore_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="preset_catalog_revision_restore",
    route_path="/presets/{preset_id}/revisions/{revision_id}/restore",
    route_name="restore_preset_revision",
    response_title="Restore preset revision",
    scope="app",
    binding_kind="preset_catalog_revision_restore",
    methods=("POST",),
    path_param_keys=("preset_id", "revision_id"),
    request_payload_kind="preset_revision_restore",
  )
  preset_lifecycle_apply_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="preset_catalog_lifecycle_apply",
    route_path="/presets/{preset_id}/lifecycle",
    route_name="apply_preset_lifecycle_action",
    response_title="Apply preset lifecycle action",
    scope="app",
    binding_kind="preset_catalog_lifecycle_apply",
    methods=("POST",),
    path_param_keys=("preset_id",),
    request_payload_kind="preset_lifecycle_action",
  )
  strategy_register_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="strategy_catalog_register",
    route_path="/strategies/register",
    route_name="register_strategy",
    response_title="Register strategy",
    scope="app",
    binding_kind="strategy_catalog_register",
    methods=("POST",),
    request_payload_kind="strategy_register",
  )
  run_list_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_list",
    route_path="/runs",
    route_name="list_runs",
    response_title="List runs",
    scope="app",
    binding_kind="run_list",
    filter_keys=(
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
    ),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "mode",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Run mode",
          description="Filter runs by execution mode.",
          examples=("backtest",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single run mode.",
          ),
        ),
        value_path=("config", "mode", "value"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "strategy_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Strategy ID",
          description="Filter runs by strategy identifier.",
          examples=("ma_cross_v1",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single strategy identifier.",
          ),
        ),
        value_path=("config", "strategy_id"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "strategy_version",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Strategy version",
          description="Filter runs by strategy version.",
          examples=("1.0.0",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches one strategy version.",
          ),
          StandaloneSurfaceFilterOperatorSpec(
            key="prefix",
            label="Version prefix",
            description="Matches a strategy version prefix.",
          ),
        ),
        value_path=("config", "strategy_version"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "rerun_boundary_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Rerun boundary ID",
          description="Filter runs by rerun boundary identifier.",
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single rerun boundary identifier.",
          ),
        ),
        value_path=("provenance", "rerun_boundary_id"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "preset_id",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Preset ID",
          description="Filter runs by preset identifier.",
          examples=("core_5m",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single preset identifier.",
          ),
        ),
        value_path=("provenance", "experiment", "preset_id"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "benchmark_family",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Benchmark family",
          description="Filter runs by benchmark family tag.",
          examples=("native_validation",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single benchmark family tag.",
          ),
        ),
        value_path=("provenance", "experiment", "benchmark_family"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "dataset_identity",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Dataset identity",
          description="Filter runs by dataset identity.",
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Matches a single dataset identity.",
          ),
          StandaloneSurfaceFilterOperatorSpec(
            key="prefix",
            label="Prefix",
            description="Matches a dataset identity prefix.",
          ),
        ),
        value_path=("provenance", "market_data", "dataset_identity"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "started_at",
        datetime | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Started at",
          description="Filter runs by start timestamp.",
          examples=("2025-01-01T00:00:00+00:00",),
        ),
        operators=_build_datetime_range_filter_operators("run start time"),
        value_path=("started_at",),
      ),
      StandaloneSurfaceFilterParamSpec(
        "updated_at",
        datetime | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Updated at",
          description="Filter runs by effective update timestamp.",
          examples=("2025-01-01T00:05:00+00:00",),
        ),
        operators=_build_datetime_range_filter_operators("run update time"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "initial_cash",
        float | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=0),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Initial cash",
          description="Filter runs by initial cash baseline.",
          examples=(10000.0,),
        ),
        operators=_build_numeric_range_filter_operators("run initial cash"),
        value_path=("metrics", "initial_cash"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "ending_equity",
        float | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=0),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Ending equity",
          description="Filter runs by ending equity.",
          examples=(11250.0,),
        ),
        operators=_build_numeric_range_filter_operators("run ending equity"),
        value_path=("metrics", "ending_equity"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "exposure_pct",
        float | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=0, le=100),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Exposure %",
          description="Filter runs by exposure percentage.",
          examples=(45.0,),
        ),
        operators=_build_numeric_range_filter_operators("run exposure percentage"),
        value_path=("metrics", "exposure_pct"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "total_return_pct",
        float | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Total return %",
          description="Filter runs by realized total return percentage.",
          examples=(10.0,),
        ),
        operators=_build_numeric_range_filter_operators("run total return percentage"),
        value_path=("metrics", "total_return_pct"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "max_drawdown_pct",
        float | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=0),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Max drawdown %",
          description="Filter runs by realized max drawdown percentage.",
          examples=(15.0,),
        ),
        operators=_build_numeric_range_filter_operators("run max drawdown percentage"),
        value_path=("metrics", "max_drawdown_pct"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "win_rate_pct",
        float | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=0, le=100),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Win rate %",
          description="Filter runs by realized win-rate percentage.",
          examples=(60.0,),
        ),
        operators=_build_numeric_range_filter_operators("run win-rate percentage"),
        value_path=("metrics", "win_rate_pct"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "trade_count",
        int | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(ge=0),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Trade count",
          description="Filter runs by realized trade count.",
          examples=(10,),
        ),
        operators=_build_numeric_range_filter_operators("run trade count"),
        value_path=("metrics", "trade_count"),
      ),
      StandaloneSurfaceFilterParamSpec(
        "tag",
        list[str],
        default_factory=list,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Tags",
          description="Filter runs by experiment tags.",
          examples=(["baseline"],),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="contains_all",
            label="Contains all",
            description="Requires all requested tags to be present on the run.",
            value_shape="list",
          ),
          StandaloneSurfaceFilterOperatorSpec(
            key="contains_any",
            label="Contains any",
            description="Matches if any requested tag is present on the run.",
            value_shape="list",
          ),
        ),
        value_path=("provenance", "experiment", "tags"),
      ),
    ),
    sort_field_specs=(
      StandaloneSurfaceSortFieldSpec(
        key="updated_at",
        label="Updated at",
        description="Sorts runs by most recent update time.",
        default_direction="desc",
        value_type="datetime",
        value_path=("updated_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="started_at",
        label="Started at",
        description="Sorts runs by start timestamp.",
        default_direction="desc",
        value_type="datetime",
        value_path=("started_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="run_id",
        label="Run ID",
        description="Sorts runs by run identifier.",
        value_path=("config", "run_id"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="initial_cash",
        label="Initial cash",
        description="Sorts runs by initial cash baseline.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "initial_cash"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="ending_equity",
        label="Ending equity",
        description="Sorts runs by ending equity.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "ending_equity"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="exposure_pct",
        label="Exposure %",
        description="Sorts runs by exposure percentage.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "exposure_pct"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="total_return_pct",
        label="Total return %",
        description="Sorts runs by realized total return percentage.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "total_return_pct"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="max_drawdown_pct",
        label="Max drawdown %",
        description="Sorts runs by realized max drawdown percentage.",
        value_type="number",
        value_path=("metrics", "max_drawdown_pct"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="win_rate_pct",
        label="Win rate %",
        description="Sorts runs by realized win-rate percentage.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "win_rate_pct"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="trade_count",
        label="Trade count",
        description="Sorts runs by realized trade count.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "trade_count"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="config.run_id",
        label="Nested run ID",
        description="Sorts runs by the nested config run identifier.",
        value_path=("config", "run_id"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="timing.started_at",
        label="Nested started at",
        description="Sorts runs by the nested timing start timestamp.",
        default_direction="desc",
        value_type="datetime",
        value_path=("started_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="timing.updated_at",
        label="Nested updated at",
        description="Sorts runs by the nested timing update timestamp.",
        default_direction="desc",
        value_type="datetime",
        value_path=("updated_at",),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="metrics.initial_cash",
        label="Nested initial cash",
        description="Sorts runs by the nested initial cash metric.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "initial_cash"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="metrics.ending_equity",
        label="Nested ending equity",
        description="Sorts runs by the nested ending equity metric.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "ending_equity"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="metrics.exposure_pct",
        label="Nested exposure %",
        description="Sorts runs by the nested exposure percentage metric.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "exposure_pct"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="metrics.total_return_pct",
        label="Nested total return %",
        description="Sorts runs by the nested total return metric.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "total_return_pct"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="metrics.max_drawdown_pct",
        label="Nested max drawdown %",
        description="Sorts runs by the nested max drawdown metric.",
        value_type="number",
        value_path=("metrics", "max_drawdown_pct"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="metrics.win_rate_pct",
        label="Nested win rate %",
        description="Sorts runs by the nested win-rate metric.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "win_rate_pct"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="metrics.trade_count",
        label="Nested trade count",
        description="Sorts runs by the nested trade-count metric.",
        default_direction="desc",
        value_type="number",
        value_path=("metrics", "trade_count"),
      ),
    ),
  )
  run_compare_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_compare",
    route_path="/runs/compare",
    route_name="compare_runs",
    response_title="Compare runs",
    scope="app",
    binding_kind="run_compare",
    filter_keys=("run_id", "intent", "narrative_score"),
    filter_param_specs=(
      StandaloneSurfaceFilterParamSpec(
        "run_id",
        list[str],
        default_factory=list,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Run IDs",
          description="Run identifiers to include in the comparison set.",
          examples=(["run-001", "run-002"],),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="include",
            label="Include set",
            description="Preserves the explicit set and order of compared run IDs.",
            value_shape="list",
          ),
        ),
        value_path=("run_id",),
      ),
      StandaloneSurfaceFilterParamSpec(
        "intent",
        str | None,
        default=None,
        constraints=StandaloneSurfaceFilterConstraintSpec(min_length=1),
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Comparison intent",
          description="Narrative intent used for run comparison scoring.",
          examples=("strategy_tuning",),
        ),
        operators=(
          StandaloneSurfaceFilterOperatorSpec(
            key="eq",
            label="Equals",
            description="Uses a single comparison intent profile.",
          ),
        ),
      ),
      StandaloneSurfaceFilterParamSpec(
        "narrative_score",
        float | None,
        default=None,
        openapi=StandaloneSurfaceFilterOpenAPISpec(
          title="Narrative score",
          description="Filter comparison narratives by computed insight score.",
          examples=(5.0,),
        ),
        operators=_build_numeric_range_filter_operators("comparison narrative score"),
        value_path=("insight_score",),
      ),
    ),
    sort_field_specs=(
      StandaloneSurfaceSortFieldSpec(
        key="run_id_order",
        label="Input run order",
        description="Keeps the compared runs in the explicit query order.",
        value_type="integer",
      ),
      StandaloneSurfaceSortFieldSpec(
        key="narrative_score",
        label="Narrative score",
        description="Ranks comparison narratives by computed score.",
        default_direction="desc",
        value_type="number",
        value_path=("narratives", "insight_score"),
      ),
      StandaloneSurfaceSortFieldSpec(
        key="narratives.run_id_order",
        label="Nested narrative input order",
        description="Sorts comparison narratives by their nested requested run order.",
        value_type="integer",
      ),
      StandaloneSurfaceSortFieldSpec(
        key="narratives.insight_score",
        label="Nested narrative score",
        description="Sorts comparison narratives by the nested insight score field.",
        default_direction="desc",
        value_type="number",
        value_path=("narratives", "insight_score"),
      ),
    ),
  )
  run_backtest_launch_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_backtest_launch",
    route_path="/runs/backtests",
    route_name="run_backtest",
    response_title="Run backtest",
    scope="app",
    binding_kind="run_backtest_launch",
    methods=("POST",),
    request_payload_kind="backtest_launch",
  )
  run_backtest_item_get_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_backtest_item_get",
    route_path="/runs/backtests/{run_id}",
    route_name="get_backtest_run",
    response_title="Get backtest run",
    scope="run",
    binding_kind="run_backtest_item_get",
  )
  run_rerun_backtest_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_rerun_backtest",
    route_path="/runs/rerun-boundaries/{rerun_boundary_id}/backtests",
    route_name="rerun_backtest_from_boundary",
    response_title="Rerun backtest from boundary",
    scope="app",
    binding_kind="run_rerun_backtest",
    methods=("POST",),
    path_param_keys=("rerun_boundary_id",),
  )
  run_rerun_sandbox_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_rerun_sandbox",
    route_path="/runs/rerun-boundaries/{rerun_boundary_id}/sandbox",
    route_name="rerun_sandbox_from_boundary",
    response_title="Rerun sandbox from boundary",
    scope="app",
    binding_kind="run_rerun_sandbox",
    methods=("POST",),
    path_param_keys=("rerun_boundary_id",),
  )
  run_rerun_paper_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_rerun_paper",
    route_path="/runs/rerun-boundaries/{rerun_boundary_id}/paper",
    route_name="rerun_paper_from_boundary",
    response_title="Rerun paper from boundary",
    scope="app",
    binding_kind="run_rerun_paper",
    methods=("POST",),
    path_param_keys=("rerun_boundary_id",),
  )
  run_sandbox_launch_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_sandbox_launch",
    route_path="/runs/sandbox",
    route_name="start_sandbox_run",
    response_title="Start sandbox run",
    scope="app",
    binding_kind="run_sandbox_launch",
    methods=("POST",),
    request_payload_kind="sandbox_launch",
  )
  run_paper_launch_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_paper_launch",
    route_path="/runs/paper",
    route_name="start_paper_run",
    response_title="Start paper run",
    scope="app",
    binding_kind="run_paper_launch",
    methods=("POST",),
    request_payload_kind="paper_launch",
  )
  run_live_launch_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_live_launch",
    route_path="/runs/live",
    route_name="start_live_run",
    response_title="Start live run",
    scope="app",
    binding_kind="run_live_launch",
    methods=("POST",),
    request_payload_kind="live_launch",
  )
  operator_incident_external_sync_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="operator_incident_external_sync",
    route_path="/operator/incidents/external-sync",
    route_name="sync_external_incident",
    response_title="External incident sync",
    scope="app",
    binding_kind="operator_incident_external_sync",
    methods=("POST",),
    header_keys=("x_akra_incident_sync_token",),
    request_payload_kind="external_incident_sync",
  )
  guarded_live_kill_switch_engage_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_kill_switch_engage",
    route_path="/guarded-live/kill-switch/engage",
    route_name="engage_guarded_live_kill_switch",
    response_title="Engage guarded-live kill switch",
    scope="app",
    binding_kind="guarded_live_kill_switch_engage",
    methods=("POST",),
    request_payload_kind="guarded_live_action",
  )
  guarded_live_kill_switch_release_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_kill_switch_release",
    route_path="/guarded-live/kill-switch/release",
    route_name="release_guarded_live_kill_switch",
    response_title="Release guarded-live kill switch",
    scope="app",
    binding_kind="guarded_live_kill_switch_release",
    methods=("POST",),
    request_payload_kind="guarded_live_action",
  )
  guarded_live_reconciliation_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_reconciliation",
    route_path="/guarded-live/reconciliation",
    route_name="run_guarded_live_reconciliation",
    response_title="Run guarded-live reconciliation",
    scope="app",
    binding_kind="guarded_live_reconciliation",
    methods=("POST",),
    request_payload_kind="guarded_live_action",
  )
  guarded_live_recovery_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_recovery",
    route_path="/guarded-live/recovery",
    route_name="recover_guarded_live_runtime_state",
    response_title="Recover guarded-live runtime state",
    scope="app",
    binding_kind="guarded_live_recovery",
    methods=("POST",),
    request_payload_kind="guarded_live_action",
  )
  guarded_live_incident_acknowledge_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_incident_acknowledge",
    route_path="/guarded-live/incidents/{event_id}/acknowledge",
    route_name="acknowledge_guarded_live_incident",
    response_title="Acknowledge guarded-live incident",
    scope="app",
    binding_kind="guarded_live_incident_acknowledge",
    methods=("POST",),
    path_param_keys=("event_id",),
    request_payload_kind="guarded_live_action",
  )
  guarded_live_incident_remediate_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_incident_remediate",
    route_path="/guarded-live/incidents/{event_id}/remediate",
    route_name="remediate_guarded_live_incident",
    response_title="Remediate guarded-live incident",
    scope="app",
    binding_kind="guarded_live_incident_remediate",
    methods=("POST",),
    path_param_keys=("event_id",),
    request_payload_kind="guarded_live_action",
  )
  guarded_live_incident_escalate_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_incident_escalate",
    route_path="/guarded-live/incidents/{event_id}/escalate",
    route_name="escalate_guarded_live_incident",
    response_title="Escalate guarded-live incident",
    scope="app",
    binding_kind="guarded_live_incident_escalate",
    methods=("POST",),
    path_param_keys=("event_id",),
    request_payload_kind="guarded_live_action",
  )
  guarded_live_resume_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="guarded_live_resume",
    route_path="/guarded-live/resume",
    route_name="resume_guarded_live_run",
    response_title="Resume guarded-live run",
    scope="app",
    binding_kind="guarded_live_resume",
    methods=("POST",),
    request_payload_kind="guarded_live_action",
  )
  stop_sandbox_run_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_stop_sandbox",
    route_path="/runs/sandbox/{run_id}/stop",
    route_name="stop_sandbox_run",
    response_title="Stop sandbox run",
    scope="run",
    binding_kind="run_stop_sandbox",
    methods=("POST",),
  )
  stop_paper_run_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_stop_paper",
    route_path="/runs/paper/{run_id}/stop",
    route_name="stop_paper_run",
    response_title="Stop paper run",
    scope="run",
    binding_kind="run_stop_paper",
    methods=("POST",),
  )
  stop_live_run_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_stop_live",
    route_path="/runs/live/{run_id}/stop",
    route_name="stop_live_run",
    response_title="Stop live run",
    scope="run",
    binding_kind="run_stop_live",
    methods=("POST",),
  )
  cancel_live_order_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_live_order_cancel",
    route_path="/runs/live/{run_id}/orders/{order_id}/cancel",
    route_name="cancel_live_order",
    response_title="Cancel live order",
    scope="run",
    binding_kind="run_live_order_cancel",
    methods=("POST",),
    path_param_keys=("order_id",),
    request_payload_kind="guarded_live_action",
  )
  replace_live_order_binding = StandaloneSurfaceRuntimeBinding(
    surface_key="run_live_order_replace",
    route_path="/runs/live/{run_id}/orders/{order_id}/replace",
    route_name="replace_live_order",
    response_title="Replace live order",
    scope="run",
    binding_kind="run_live_order_replace",
    methods=("POST",),
    path_param_keys=("order_id",),
    request_payload_kind="guarded_live_order_replace",
  )
  run_subresource_bindings = tuple(
    StandaloneSurfaceRuntimeBinding(
      surface_key=f"run_subresource:{binding.contract.subresource_key}",
      route_path=binding.contract.route_path,
      route_name=binding.contract.route_name,
      response_title=binding.contract.response_title,
      scope="run",
      binding_kind="run_subresource",
      subresource_key=binding.contract.subresource_key,
    )
    for binding in list_run_subresource_runtime_bindings(resolved_capabilities)
  )
  return (
    health_binding,
    capability_binding,
    market_data_status_binding,
    operator_visibility_binding,
    guarded_live_status_binding,
    strategy_discovery_binding,
    reference_discovery_binding,
    preset_discovery_binding,
    preset_create_binding,
    preset_item_get_binding,
    preset_item_update_binding,
    preset_revision_list_binding,
    preset_revision_restore_binding,
    preset_lifecycle_apply_binding,
    strategy_register_binding,
    run_list_binding,
    run_compare_binding,
    run_backtest_launch_binding,
    run_backtest_item_get_binding,
    run_rerun_backtest_binding,
    run_rerun_sandbox_binding,
    run_rerun_paper_binding,
    run_sandbox_launch_binding,
    run_paper_launch_binding,
    run_live_launch_binding,
    operator_incident_external_sync_binding,
    guarded_live_kill_switch_engage_binding,
    guarded_live_kill_switch_release_binding,
    guarded_live_reconciliation_binding,
    guarded_live_recovery_binding,
    guarded_live_incident_acknowledge_binding,
    guarded_live_incident_remediate_binding,
    guarded_live_incident_escalate_binding,
    guarded_live_resume_binding,
    stop_sandbox_run_binding,
    stop_paper_run_binding,
    stop_live_run_binding,
    cancel_live_order_binding,
    replace_live_order_binding,
    *run_subresource_bindings,
  )


def get_standalone_surface_runtime_binding(
  surface_key: str,
  capabilities: RunSurfaceCapabilities | None = None,
) -> StandaloneSurfaceRuntimeBinding:
  for binding in list_standalone_surface_runtime_bindings(capabilities):
    if binding.surface_key == surface_key:
      return binding
  raise ValueError(f"Unsupported standalone surface binding: {surface_key}")


def execute_standalone_surface_binding(
  *,
  binding: StandaloneSurfaceRuntimeBinding,
  app: TradingApplication,
  run_id: str | None = None,
  filters: dict[str, Any] | None = None,
  request_payload: dict[str, Any] | None = None,
  path_params: dict[str, Any] | None = None,
  headers: dict[str, Any] | None = None,
) -> Any:
  resolved_filters = filters or {}
  resolved_payload = request_payload or {}
  resolved_path_params = path_params or {}
  resolved_headers = headers or {}
  if binding.binding_kind == "health_status":
    return {"status": "ok"}
  if binding.binding_kind == "run_surface_capabilities":
    return serialize_run_surface_capabilities(app.get_run_surface_capabilities())
  if binding.binding_kind == "market_data_status":
    return asdict(app.get_market_data_status(resolved_filters.get("timeframe") or "5m"))
  if binding.binding_kind == "operator_visibility":
    return asdict(app.get_operator_visibility())
  if binding.binding_kind == "guarded_live_status":
    return asdict(app.get_guarded_live_status())
  if binding.binding_kind == "strategy_catalog_discovery":
    return [
      serialize_strategy(strategy)
      for strategy in _apply_runtime_query_to_strategies(
        app.list_strategies(
          lane=resolved_filters.get("lane"),
          lifecycle_stage=resolved_filters.get("lifecycle_stage"),
          version=resolved_filters.get("version"),
        ),
        resolved_filters,
        binding=binding,
      )
    ]
  if binding.binding_kind == "reference_catalog_discovery":
    return [asdict(reference) for reference in app.list_references()]
  if binding.binding_kind == "preset_catalog_discovery":
    return [
      serialize_preset(preset)
      for preset in _apply_runtime_query_to_presets(
        app.list_presets(
          strategy_id=resolved_filters.get("strategy_id"),
          timeframe=resolved_filters.get("timeframe"),
          lifecycle_stage=resolved_filters.get("lifecycle_stage"),
        ),
        resolved_filters,
        binding=binding,
      )
    ]
  if binding.binding_kind == "preset_catalog_create":
    preset = app.create_preset(
      name=resolved_payload["name"],
      preset_id=resolved_payload.get("preset_id"),
      description=resolved_payload.get("description") or "",
      strategy_id=resolved_payload.get("strategy_id"),
      timeframe=resolved_payload.get("timeframe"),
      tags=resolved_payload.get("tags") or [],
      parameters=resolved_payload.get("parameters") or {},
      benchmark_family=resolved_payload.get("benchmark_family"),
    )
    return serialize_preset(preset)
  if binding.binding_kind == "preset_catalog_item_get":
    preset = app.get_preset(
      preset_id=resolved_path_params["preset_id"],
    )
    return serialize_preset(preset)
  if binding.binding_kind == "preset_catalog_item_update":
    changes = {
      key: value
      for key, value in resolved_payload.items()
      if key not in {"actor", "reason"}
    }
    preset = app.update_preset(
      preset_id=resolved_path_params["preset_id"],
      changes=changes,
      actor=resolved_payload.get("actor", "operator"),
      reason=resolved_payload.get("reason", "manual_preset_edit"),
    )
    return serialize_preset(preset)
  if binding.binding_kind == "preset_catalog_revision_list":
    return [
      serialize_preset_revision(revision)
      for revision in app.list_preset_revisions(
        preset_id=resolved_path_params["preset_id"],
      )
    ]
  if binding.binding_kind == "preset_catalog_revision_restore":
    preset = app.restore_preset_revision(
      preset_id=resolved_path_params["preset_id"],
      revision_id=resolved_path_params["revision_id"],
      actor=resolved_payload.get("actor", "operator"),
      reason=resolved_payload.get("reason", "manual_preset_revision_restore"),
    )
    return serialize_preset(preset)
  if binding.binding_kind == "preset_catalog_lifecycle_apply":
    preset = app.apply_preset_lifecycle_action(
      preset_id=resolved_path_params["preset_id"],
      action=resolved_payload["action"],
      actor=resolved_payload.get("actor", "operator"),
      reason=resolved_payload.get("reason", "manual_preset_lifecycle_action"),
    )
    return serialize_preset(preset)
  if binding.binding_kind == "strategy_catalog_register":
    metadata = app.register_strategy(
      strategy_id=resolved_payload["strategy_id"],
      module_path=resolved_payload["module_path"],
      class_name=resolved_payload["class_name"],
    )
    return serialize_strategy(metadata)
  if binding.binding_kind == "run_list":
    return [
      serialize_run(run, capabilities=app.get_run_surface_capabilities())
      for run in _apply_runtime_query_to_runs(
        app.list_runs(
          mode=resolved_filters.get("mode"),
          strategy_id=resolved_filters.get("strategy_id"),
          strategy_version=resolved_filters.get("strategy_version"),
          rerun_boundary_id=resolved_filters.get("rerun_boundary_id"),
          preset_id=resolved_filters.get("preset_id"),
          benchmark_family=resolved_filters.get("benchmark_family"),
          dataset_identity=resolved_filters.get("dataset_identity"),
          tags=resolved_filters.get("tag") or [],
        ),
        resolved_filters,
        binding=binding,
      )
    ]
  if binding.binding_kind == "run_compare":
    comparison = _apply_runtime_query_to_comparison(
      app.compare_runs(
        run_ids=resolved_filters.get("run_id") or [],
        intent=resolved_filters.get("intent"),
      ),
      resolved_filters,
      binding=binding,
    )
    return serialize_run_comparison(
      comparison,
      capabilities=app.get_run_surface_capabilities(),
    )
  if binding.binding_kind == "run_backtest_launch":
    run = app.run_backtest(
      strategy_id=resolved_payload["strategy_id"],
      symbol=resolved_payload["symbol"],
      timeframe=resolved_payload.get("timeframe", "5m"),
      initial_cash=resolved_payload.get("initial_cash", 10_000),
      fee_rate=resolved_payload.get("fee_rate", 0.001),
      slippage_bps=resolved_payload.get("slippage_bps", 3),
      parameters=resolved_payload.get("parameters") or {},
      start_at=resolved_payload.get("start_at"),
      end_at=resolved_payload.get("end_at"),
      tags=resolved_payload.get("tags") or [],
      preset_id=resolved_payload.get("preset_id"),
      benchmark_family=resolved_payload.get("benchmark_family"),
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_backtest_item_get":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.get_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_rerun_backtest":
    run = app.rerun_backtest_from_boundary(
      rerun_boundary_id=resolved_path_params["rerun_boundary_id"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_rerun_sandbox":
    run = app.rerun_sandbox_from_boundary(
      rerun_boundary_id=resolved_path_params["rerun_boundary_id"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_rerun_paper":
    run = app.rerun_paper_from_boundary(
      rerun_boundary_id=resolved_path_params["rerun_boundary_id"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_sandbox_launch":
    run = app.start_sandbox_run(
      strategy_id=resolved_payload["strategy_id"],
      symbol=resolved_payload["symbol"],
      timeframe=resolved_payload.get("timeframe", "5m"),
      initial_cash=resolved_payload.get("initial_cash", 10_000),
      fee_rate=resolved_payload.get("fee_rate", 0.001),
      slippage_bps=resolved_payload.get("slippage_bps", 3),
      parameters=resolved_payload.get("parameters") or {},
      replay_bars=resolved_payload.get("replay_bars", 96),
      tags=resolved_payload.get("tags") or [],
      preset_id=resolved_payload.get("preset_id"),
      benchmark_family=resolved_payload.get("benchmark_family"),
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_paper_launch":
    run = app.start_paper_run(
      strategy_id=resolved_payload["strategy_id"],
      symbol=resolved_payload["symbol"],
      timeframe=resolved_payload.get("timeframe", "5m"),
      initial_cash=resolved_payload.get("initial_cash", 10_000),
      fee_rate=resolved_payload.get("fee_rate", 0.001),
      slippage_bps=resolved_payload.get("slippage_bps", 3),
      parameters=resolved_payload.get("parameters") or {},
      replay_bars=resolved_payload.get("replay_bars", 96),
      tags=resolved_payload.get("tags") or [],
      preset_id=resolved_payload.get("preset_id"),
      benchmark_family=resolved_payload.get("benchmark_family"),
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_live_launch":
    run = app.start_live_run(
      strategy_id=resolved_payload["strategy_id"],
      symbol=resolved_payload["symbol"],
      timeframe=resolved_payload.get("timeframe", "5m"),
      initial_cash=resolved_payload.get("initial_cash", 10_000),
      fee_rate=resolved_payload.get("fee_rate", 0.001),
      slippage_bps=resolved_payload.get("slippage_bps", 3),
      parameters=resolved_payload.get("parameters") or {},
      replay_bars=resolved_payload.get("replay_bars", 96),
      operator_reason=resolved_payload.get("operator_reason", "guarded_live_launch"),
      tags=resolved_payload.get("tags") or [],
      preset_id=resolved_payload.get("preset_id"),
      benchmark_family=resolved_payload.get("benchmark_family"),
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "operator_incident_external_sync":
    app.require_operator_alert_external_sync_token(
      resolved_headers.get("x_akra_incident_sync_token"),
    )
    status = app.sync_guarded_live_incident_from_external(
      provider=resolved_payload["provider"],
      event_kind=resolved_payload["event_kind"],
      actor=resolved_payload["actor"],
      detail=resolved_payload["detail"],
      alert_id=resolved_payload.get("alert_id"),
      external_reference=resolved_payload.get("external_reference"),
      workflow_reference=resolved_payload.get("workflow_reference"),
      occurred_at=resolved_payload.get("occurred_at"),
      escalation_level=resolved_payload.get("escalation_level"),
      payload=resolved_payload.get("payload"),
    )
    return asdict(status)
  if binding.binding_kind == "guarded_live_kill_switch_engage":
    return asdict(
      app.engage_guarded_live_kill_switch(
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )
  if binding.binding_kind == "guarded_live_kill_switch_release":
    return asdict(
      app.release_guarded_live_kill_switch(
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )
  if binding.binding_kind == "guarded_live_reconciliation":
    return asdict(
      app.run_guarded_live_reconciliation(
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )
  if binding.binding_kind == "guarded_live_recovery":
    return asdict(
      app.recover_guarded_live_runtime_state(
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )
  if binding.binding_kind == "guarded_live_incident_acknowledge":
    return asdict(
      app.acknowledge_guarded_live_incident(
        event_id=resolved_path_params["event_id"],
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )
  if binding.binding_kind == "guarded_live_incident_remediate":
    return asdict(
      app.remediate_guarded_live_incident(
        event_id=resolved_path_params["event_id"],
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )
  if binding.binding_kind == "guarded_live_incident_escalate":
    return asdict(
      app.escalate_guarded_live_incident(
        event_id=resolved_path_params["event_id"],
        actor=resolved_payload["actor"],
        reason=resolved_payload["reason"],
      )
    )
  if binding.binding_kind == "guarded_live_resume":
    run = app.resume_guarded_live_run(
      actor=resolved_payload["actor"],
      reason=resolved_payload["reason"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_stop_sandbox":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.stop_sandbox_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_stop_paper":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.stop_paper_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_stop_live":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.stop_live_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_live_order_cancel":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.cancel_live_order(
      run_id=run_id,
      order_id=resolved_path_params["order_id"],
      actor=resolved_payload["actor"],
      reason=resolved_payload["reason"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_live_order_replace":
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.replace_live_order(
      run_id=run_id,
      order_id=resolved_path_params["order_id"],
      price=resolved_payload["price"],
      quantity=resolved_payload.get("quantity"),
      actor=resolved_payload["actor"],
      reason=resolved_payload["reason"],
    )
    return serialize_run(run, capabilities=app.get_run_surface_capabilities())
  if binding.binding_kind == "run_subresource":
    if binding.subresource_key is None:
      raise ValueError(f"Standalone surface binding is missing subresource metadata: {binding.surface_key}")
    if run_id is None:
      raise ValueError(f"Standalone surface {binding.surface_key} requires a run_id.")
    run = app.get_run(run_id)
    if run is None:
      raise LookupError("Run not found")
    return serialize_run_subresource_response(
      run,
      subresource_key=binding.subresource_key,
      capabilities=app.get_run_surface_capabilities(),
    )
  raise ValueError(f"Unsupported standalone surface binding: {binding.binding_kind}")


def serialize_standalone_surface_response(
  *,
  binding: StandaloneSurfaceRuntimeBinding,
  app: TradingApplication,
  run_id: str | None = None,
  filters: dict[str, Any] | None = None,
) -> Any:
  return execute_standalone_surface_binding(
    binding=binding,
    app=app,
    run_id=run_id,
    filters=filters,
  )


def list_run_surface_shared_contracts(
  capabilities: RunSurfaceCapabilities | None = None,
) -> tuple[RunSurfaceSharedContract, ...]:
  resolved_capabilities = capabilities or RunSurfaceCapabilities()
  return resolved_capabilities.shared_contracts


def serialize_run_surface_shared_contracts(
  capabilities: RunSurfaceCapabilities | None = None,
) -> list[dict[str, Any]]:
  def normalize_schema_detail(value: Any) -> Any:
    if isinstance(value, tuple):
      return [
        normalize_schema_detail(item)
        for item in value
      ]
    if isinstance(value, list):
      return [
        normalize_schema_detail(item)
        for item in value
      ]
    if isinstance(value, dict):
      return {
        key: normalize_schema_detail(item)
        for key, item in value.items()
      }
    return value

  return [
    {
      **asdict(contract),
      "ui_surfaces": list(contract.ui_surfaces),
      "schema_sources": list(contract.schema_sources),
      "policy": (
        {
          **asdict(contract.policy),
          "applies_to": list(contract.policy.applies_to),
        }
        if contract.policy is not None
        else None
      ),
      "enforcement": (
        {
          **asdict(contract.enforcement),
          "enforcement_points": list(contract.enforcement.enforcement_points),
        }
        if contract.enforcement is not None
        else None
      ),
      "surface_rules": [
        asdict(rule)
        for rule in contract.surface_rules
      ],
      "related_family_keys": list(contract.related_family_keys),
      "member_keys": list(contract.member_keys),
      "schema_detail": normalize_schema_detail(contract.schema_detail),
    }
    for contract in list_run_surface_shared_contracts(capabilities)
  ]


def serialize_run_subresource_response(
  run: RunRecord,
  *,
  subresource_key: str,
  capabilities: RunSurfaceCapabilities | None = None,
) -> dict[str, Any]:
  resolved_capabilities = capabilities or RunSurfaceCapabilities()
  binding = get_run_subresource_runtime_binding(subresource_key, resolved_capabilities)
  return _serialize_run_subresource_envelope(
    run,
    capabilities=resolved_capabilities,
    body_key=binding.contract.body_key,
    body_value=binding.body_serializer(run, resolved_capabilities),
  )


def serialize_run_orders_response(
  run: RunRecord,
  *,
  capabilities: RunSurfaceCapabilities | None = None,
) -> dict[str, Any]:
  return serialize_run_subresource_response(
    run,
    subresource_key="orders",
    capabilities=capabilities,
  )


def serialize_run_positions_response(
  run: RunRecord,
  *,
  capabilities: RunSurfaceCapabilities | None = None,
) -> dict[str, Any]:
  return serialize_run_subresource_response(
    run,
    subresource_key="positions",
    capabilities=capabilities,
  )


def serialize_run_metrics_response(
  run: RunRecord,
  *,
  capabilities: RunSurfaceCapabilities | None = None,
) -> dict[str, Any]:
  return serialize_run_subresource_response(
    run,
    subresource_key="metrics",
    capabilities=capabilities,
  )


def serialize_preset(preset: ExperimentPreset) -> dict:
  payload = asdict(preset)
  payload["tags"] = list(preset.tags)
  payload["lifecycle"]["history"] = [
    _serialize_preset_lifecycle_event(event)
    for event in preset.lifecycle.history
  ]
  payload["revisions"] = [
    serialize_preset_revision(revision)
    for revision in preset.revisions
  ]
  payload["created_at"] = preset.created_at.isoformat()
  payload["updated_at"] = preset.updated_at.isoformat()
  return payload


def serialize_strategy(strategy: StrategyMetadata) -> dict:
  payload = asdict(strategy)
  payload["asset_types"] = [asset_type.value for asset_type in strategy.asset_types]
  payload["supported_timeframes"] = list(strategy.supported_timeframes)
  payload["version_lineage"] = list(strategy.version_lineage or (strategy.version,))
  payload["catalog_semantics"]["operator_notes"] = list(strategy.catalog_semantics.operator_notes)
  return payload


def serialize_run_comparison(
  comparison: RunComparison,
  *,
  capabilities: RunSurfaceCapabilities | None = None,
) -> dict:
  resolved_capabilities = capabilities or RunSurfaceCapabilities()
  payload = asdict(comparison)
  payload["requested_run_ids"] = list(comparison.requested_run_ids)
  payload["runs"] = [
    {
      **run_payload,
      "experiment": {
        **run_payload["experiment"],
        "tags": list(run.experiment.tags),
      },
      "symbols": list(run.symbols),
      "external_command": list(run.external_command),
      "artifact_paths": list(run.artifact_paths),
      "benchmark_artifacts": [asdict(artifact) for artifact in run.benchmark_artifacts],
      "catalog_semantics": {
        **run_payload["catalog_semantics"],
        "operator_notes": list(run.catalog_semantics.operator_notes),
      },
      "notes": list(run.notes),
    }
    for run_payload, run in zip(payload["runs"], comparison.runs, strict=True)
  ]
  payload["surface_enforcement"] = _build_run_surface_enforcement(resolved_capabilities)
  return payload


def serialize_run_surface_capabilities(capabilities: RunSurfaceCapabilities) -> dict[str, Any]:
  return {
    "discovery": {
      "shared_contracts": serialize_run_surface_shared_contracts(capabilities),
    },
    "comparison_eligibility_contract": serialize_comparison_eligibility_contract(
      capabilities.comparison_eligibility_contract
    )
  }


def serialize_comparison_eligibility_contract(
  contract: ComparisonEligibilityContract | None = None,
) -> dict[str, Any]:
  resolved_contract = contract or default_comparison_eligibility_contract()
  payload = asdict(resolved_contract)
  payload["groups"] = {
    key: {
      **group_payload,
      "surface_ids": list(resolved_contract.groups[key].surface_ids),
    }
    for key, group_payload in payload["groups"].items()
  }
  return payload


def _normalize_run_ids(run_ids: list[str]) -> list[str]:
  normalized_run_ids: list[str] = []
  seen_run_ids: set[str] = set()
  for run_id in run_ids:
    if run_id in seen_run_ids:
      continue
    seen_run_ids.add(run_id)
    normalized_run_ids.append(run_id)
  return normalized_run_ids


def _serialize_comparison_run(run: RunRecord) -> RunComparisonRun:
  return RunComparisonRun(
    run_id=run.config.run_id,
    mode=run.config.mode.value,
    status=run.status.value,
    lane=run.provenance.lane,
    strategy_id=run.config.strategy_id,
    strategy_name=run.provenance.strategy.name if run.provenance.strategy is not None else None,
    strategy_version=run.config.strategy_version,
    catalog_semantics=deepcopy(
      run.provenance.strategy.catalog_semantics
      if run.provenance.strategy is not None
      else StrategyCatalogSemantics()
    ),
    symbols=run.config.symbols,
    timeframe=run.config.timeframe,
    started_at=run.started_at,
    ended_at=run.ended_at,
    reference_id=run.provenance.reference_id,
    reference_version=run.provenance.reference_version,
    integration_mode=run.provenance.integration_mode,
    reference=deepcopy(run.provenance.reference),
    working_directory=run.provenance.working_directory,
    rerun_boundary_id=run.provenance.rerun_boundary_id,
    rerun_boundary_state=run.provenance.rerun_boundary_state,
    dataset_identity=(
      run.provenance.market_data.dataset_identity
      if run.provenance.market_data is not None
      else None
    ),
    experiment=deepcopy(run.provenance.experiment),
    external_command=tuple(run.provenance.external_command),
    artifact_paths=tuple(run.provenance.artifact_paths),
    benchmark_artifacts=tuple(run.provenance.benchmark_artifacts),
    metrics=deepcopy(run.metrics),
    notes=tuple(run.notes),
  )


def _build_comparison_metric_row(
  *,
  runs: list[RunRecord],
  baseline_run: RunRecord,
  intent: str,
  key: str,
  label: str,
  unit: str,
  higher_is_better: bool,
) -> RunComparisonMetricRow:
  baseline_value = _resolve_run_metric_value(baseline_run, key)
  values = {
    run.config.run_id: _resolve_run_metric_value(run, key)
    for run in runs
  }
  deltas_vs_baseline = {
    run_id: _calculate_metric_delta(value, baseline_value)
    for run_id, value in values.items()
  }
  delta_annotations = {
    run_id: _build_metric_delta_annotation(
      intent=intent,
      key=key,
      unit=unit,
      is_baseline=run_id == baseline_run.config.run_id,
      baseline_run=baseline_run,
      run=run,
      higher_is_better=higher_is_better,
      delta=deltas_vs_baseline[run_id],
      value=values[run_id],
    )
    for run_id, run in ((candidate.config.run_id, candidate) for candidate in runs)
  }
  comparable_values = {
    run_id: value
    for run_id, value in values.items()
    if value is not None
  }
  best_run_id: str | None = None
  if comparable_values:
    best_run_id = (
      max(comparable_values, key=comparable_values.get)
      if higher_is_better
      else min(comparable_values, key=comparable_values.get)
    )
  return RunComparisonMetricRow(
    key=key,
    label=label,
    unit=unit,
    higher_is_better=higher_is_better,
    values=values,
    deltas_vs_baseline=deltas_vs_baseline,
    delta_annotations=delta_annotations,
    annotation=_build_metric_annotation(
      intent=intent,
      key=key,
      baseline_run=baseline_run,
      runs=runs,
    ),
    best_run_id=best_run_id,
  )


def _build_metric_annotation(
  *,
  intent: str,
  key: str,
  baseline_run: RunRecord,
  runs: list[RunRecord],
) -> str | None:
  annotation = COMPARISON_METRIC_COPY.get(intent, {}).get(key, {}).get("annotation")
  semantic_suffix = _build_metric_semantic_annotation_suffix(
    baseline_run=baseline_run,
    runs=runs,
  )
  if annotation is None:
    return f"Semantic context: {semantic_suffix}." if semantic_suffix else None
  if semantic_suffix is None:
    return annotation
  return f"{annotation} Semantic context: {semantic_suffix}."


def _build_metric_delta_annotation(
  *,
  intent: str,
  key: str,
  unit: str,
  is_baseline: bool,
  baseline_run: RunRecord,
  run: RunRecord,
  higher_is_better: bool,
  delta: float | int | None,
  value: float | int | None,
) -> str:
  copy = COMPARISON_METRIC_COPY.get(intent, {}).get(key, {})
  semantic_suffix = _build_metric_delta_semantic_suffix(
    baseline_run=baseline_run,
    run=run,
  )
  if is_baseline:
    return copy.get("baseline", "baseline")
  if value is None or delta is None:
    missing = copy.get("missing", "delta unavailable")
    return f"{missing} for {semantic_suffix}" if semantic_suffix else missing
  if delta == 0:
    return f"aligned with baseline for {semantic_suffix}" if semantic_suffix else "aligned with baseline"

  magnitude = _format_metric_delta_magnitude(delta=delta, unit=unit)
  positive_phrase = copy.get("positive_delta", "above baseline")
  negative_phrase = copy.get("negative_delta", "below baseline")

  if higher_is_better:
    phrase = positive_phrase if delta > 0 else negative_phrase
  else:
    phrase = positive_phrase if delta > 0 else negative_phrase
  annotation = f"{magnitude} {phrase}"
  return f"{annotation} for {semantic_suffix}" if semantic_suffix else annotation


def _format_metric_delta_magnitude(
  *,
  delta: float | int,
  unit: str,
) -> str:
  magnitude = abs(float(delta))
  if unit == "pct":
    rounded = round(magnitude, 2)
    return f"{rounded:g} pts"
  rounded = round(magnitude, 2)
  if rounded.is_integer():
    return str(int(rounded))
  return f"{rounded:g}"


def _build_comparison_narrative(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
  intent: str,
  metric_row_by_key: dict[str, RunComparisonMetricRow],
) -> RunComparisonNarrative | None:
  comparison_type = _classify_comparison_type(baseline_run, run)
  target_label = _comparison_run_label(run)
  baseline_label = _comparison_run_label(baseline_run)
  target_subject = _comparison_subject_label(run)

  total_return_delta = _metric_row_delta(metric_row_by_key, "total_return_pct", run.config.run_id)
  max_drawdown_delta = _metric_row_delta(metric_row_by_key, "max_drawdown_pct", run.config.run_id)
  win_rate_delta = _metric_row_delta(metric_row_by_key, "win_rate_pct", run.config.run_id)
  trade_count_delta = _metric_row_delta(metric_row_by_key, "trade_count", run.config.run_id)

  title = _build_comparison_narrative_title(
    intent=intent,
    comparison_type=comparison_type,
    target_subject=target_subject,
    baseline_label=baseline_label,
    total_return_delta=total_return_delta,
    max_drawdown_delta=max_drawdown_delta,
  )
  summary = _build_comparison_narrative_summary(
    intent=intent,
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
    baseline_label=baseline_label,
    total_return_delta=total_return_delta,
    max_drawdown_delta=max_drawdown_delta,
    win_rate_delta=win_rate_delta,
    trade_count_delta=trade_count_delta,
  )
  bullets = _build_comparison_narrative_bullets(
    intent=intent,
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
    target_label=target_label,
    baseline_label=baseline_label,
    win_rate_delta=win_rate_delta,
    trade_count_delta=trade_count_delta,
  )

  if not title and not summary and not bullets:
    return None

  insight_score, score_breakdown = _score_comparison_narrative(
    intent=intent,
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
    total_return_delta=total_return_delta,
    max_drawdown_delta=max_drawdown_delta,
    win_rate_delta=win_rate_delta,
    trade_count_delta=trade_count_delta,
  )

  return RunComparisonNarrative(
    run_id=run.config.run_id,
    baseline_run_id=baseline_run.config.run_id,
    comparison_type=comparison_type,
    title=title or f"{target_subject} diverged from {baseline_label}.",
    summary=summary or f"{target_label} is being compared against {baseline_label}.",
    bullets=tuple(bullets),
    score_breakdown=score_breakdown,
    insight_score=insight_score,
  )


def _rank_comparison_narratives(
  narratives: list[RunComparisonNarrative],
) -> list[RunComparisonNarrative]:
  ordered = sorted(
    narratives,
    key=lambda narrative: (-narrative.insight_score, narrative.run_id),
  )
  return [
    replace(
      narrative,
      rank=index + 1,
      is_primary=index == 0,
    )
    for index, narrative in enumerate(ordered)
  ]


def _score_comparison_narrative(
  *,
  intent: str,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
  total_return_delta: float | int | None,
  max_drawdown_delta: float | int | None,
  win_rate_delta: float | int | None,
  trade_count_delta: float | int | None,
) -> tuple[float, dict[str, Any]]:
  weights = COMPARISON_INTENT_WEIGHTS[intent]
  metric_components = {
    "total_return_pct": _build_metric_score_component(
      delta=total_return_delta,
      weight=weights["return"],
    ),
    "max_drawdown_pct": _build_metric_score_component(
      delta=max_drawdown_delta,
      weight=weights["drawdown"],
    ),
    "win_rate_pct": _build_metric_score_component(
      delta=win_rate_delta,
      weight=weights["win_rate"],
    ),
    "trade_count": _build_metric_score_component(
      delta=trade_count_delta,
      weight=weights["trade_count"],
      cap=50.0,
    ),
  }
  semantic_components = _build_comparison_semantic_delta_breakdown(
    baseline_run=baseline_run,
    run=run,
    weights=weights,
  )
  semantic_components["vocabulary"] = _build_comparison_semantic_vocabulary_breakdown(
    baseline_run=baseline_run,
    run=run,
    weights=weights,
  )
  semantic_components["provenance_richness"] = _build_comparison_provenance_richness_breakdown(
    baseline_run=baseline_run,
    run=run,
    weights=weights,
  )
  context_components = _build_comparison_context_score_breakdown(
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
    weights=weights,
  )

  metric_total = round(
    sum(component["score"] for component in metric_components.values()),
    2,
  )
  semantic_total = round(
    sum(component["score"] for component in semantic_components.values()),
    2,
  )
  context_total = _context_subtotal(context_components)
  if metric_total + semantic_total + context_total == 0.0 and _has_reference_context(run, baseline_run):
    context_components["reference_floor"] = {
      "applied": True,
      "score": weights["reference_floor"],
    }
    context_total = _context_subtotal(context_components)
  score = round(metric_total + semantic_total + context_total, 2)

  breakdown = {
    "metrics": {
      "total": metric_total,
      "components": metric_components,
    },
    "semantics": {
      "total": semantic_total,
      "components": semantic_components,
    },
    "context": {
      "total": context_total,
      "components": context_components,
    },
    "total": score,
  }
  return score, breakdown


def _build_metric_score_component(
  *,
  delta: float | int | None,
  weight: float,
  cap: float | None = None,
) -> dict[str, Any]:
  raw_delta = abs(float(delta or 0.0))
  effective_delta = min(raw_delta, cap) if cap is not None else raw_delta
  score = round(effective_delta * weight, 2)
  return {
    "delta": 0.0 if delta is None else float(delta),
    "effective_delta": effective_delta,
    "weight": weight,
    "score": score,
  }


def _build_comparison_semantic_delta_breakdown(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
  weights: dict[str, float],
) -> dict[str, dict[str, Any]]:
  baseline_semantics = _strategy_semantics(baseline_run)
  run_semantics = _strategy_semantics(run)
  strategy_kind_applied = baseline_semantics.strategy_kind != run_semantics.strategy_kind
  execution_applied = _normalized_semantic_text(
    baseline_semantics.execution_model
  ) != _normalized_semantic_text(run_semantics.execution_model) and _normalized_semantic_text(
    run_semantics.execution_model
  ) is not None
  source_applied = _normalized_semantic_text(
    baseline_semantics.source_descriptor
  ) != _normalized_semantic_text(run_semantics.source_descriptor) and _normalized_semantic_text(
    run_semantics.source_descriptor
  ) is not None
  parameter_contract_applied = _normalized_semantic_text(
    baseline_semantics.parameter_contract
  ) != _normalized_semantic_text(run_semantics.parameter_contract) and _normalized_semantic_text(
    run_semantics.parameter_contract
  ) is not None
  return {
    "strategy_kind": {
      "applied": strategy_kind_applied,
      "baseline": baseline_semantics.strategy_kind,
      "target": run_semantics.strategy_kind,
      "weight": weights["semantic_kind_bonus"],
      "score": weights["semantic_kind_bonus"] if strategy_kind_applied else 0.0,
    },
    "execution_model": {
      "applied": execution_applied,
      "baseline": _normalized_semantic_text(baseline_semantics.execution_model),
      "target": _normalized_semantic_text(run_semantics.execution_model),
      "weight": weights["semantic_execution_bonus"],
      "score": weights["semantic_execution_bonus"] if execution_applied else 0.0,
    },
    "source_descriptor": {
      "applied": source_applied,
      "baseline": _normalized_semantic_text(baseline_semantics.source_descriptor),
      "target": _normalized_semantic_text(run_semantics.source_descriptor),
      "weight": weights["semantic_source_bonus"],
      "score": weights["semantic_source_bonus"] if source_applied else 0.0,
    },
    "parameter_contract": {
      "applied": parameter_contract_applied,
      "baseline": _normalized_semantic_text(baseline_semantics.parameter_contract),
      "target": _normalized_semantic_text(run_semantics.parameter_contract),
      "weight": weights["semantic_parameter_contract_bonus"],
      "score": (
        weights["semantic_parameter_contract_bonus"]
        if parameter_contract_applied
        else 0.0
      ),
    },
  }


def _normalized_semantic_text(value: str | None) -> str | None:
  if value is None:
    return None
  normalized = value.strip()
  return normalized or None


def _build_comparison_semantic_vocabulary_breakdown(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
  weights: dict[str, float],
) -> dict[str, Any]:
  baseline_schema = _strategy_parameter_schema(baseline_run)
  run_schema = _strategy_parameter_schema(run)
  baseline_parameters = _strategy_parameter_values(baseline_run)
  run_parameters = _strategy_parameter_values(run)

  changed_keys = sorted(
    key
    for key in set(baseline_parameters) | set(run_parameters)
    if baseline_parameters.get(key) != run_parameters.get(key)
  )

  richness_units = 0.0
  for key in changed_keys:
    schema_entry = run_schema.get(key)
    if not isinstance(schema_entry, dict):
      schema_entry = baseline_schema.get(key)
    richness_units += _parameter_semantic_descriptor_score(schema_entry)

  schema_richness_delta = max(
    _semantic_schema_richness(run_schema) - _semantic_schema_richness(baseline_schema),
    0.0,
  )
  richness_units += min(schema_richness_delta, 4.0) * 0.35
  capped_units = min(richness_units, 8.0)
  score = round(capped_units * weights["semantic_vocabulary_unit_bonus"], 2)
  return {
    "changed_keys": changed_keys,
    "schema_richness_delta": round(schema_richness_delta, 2),
    "units": round(richness_units, 2),
    "capped_units": round(capped_units, 2),
    "weight": weights["semantic_vocabulary_unit_bonus"],
    "score": score,
  }


def _build_comparison_provenance_richness_breakdown(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
  weights: dict[str, float],
) -> dict[str, Any]:
  baseline_richness = _benchmark_provenance_richness(baseline_run)
  target_richness = _benchmark_provenance_richness(run)
  richness_delta = max(target_richness - baseline_richness, 0.0)
  capped_units = min(richness_delta, 10.0)
  score = round(capped_units * weights["provenance_richness_unit_bonus"], 2)
  return {
    "baseline_units": round(baseline_richness, 2),
    "target_units": round(target_richness, 2),
    "units": round(richness_delta, 2),
    "capped_units": round(capped_units, 2),
    "weight": weights["provenance_richness_unit_bonus"],
    "score": score,
  }


def _build_comparison_context_score_breakdown(
  *,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
  weights: dict[str, float],
) -> dict[str, dict[str, Any]]:
  native_reference_applied = comparison_type == "native_vs_reference"
  reference_applied = comparison_type == "reference_vs_reference"
  status_applied = run.status != baseline_run.status
  benchmark_story_applied = bool(_extract_benchmark_story(run) or _extract_benchmark_story(baseline_run))
  context_components = {
    "native_reference_bonus": {
      "applied": native_reference_applied,
      "score": weights["native_reference_bonus"] if native_reference_applied else 0.0,
    },
    "reference_bonus": {
      "applied": reference_applied,
      "score": weights["reference_bonus"] if reference_applied else 0.0,
    },
    "status_bonus": {
      "applied": status_applied,
      "score": weights["status_bonus"] if status_applied else 0.0,
    },
    "benchmark_story_bonus": {
      "applied": benchmark_story_applied,
      "score": weights["benchmark_story_bonus"] if benchmark_story_applied else 0.0,
    },
    "reference_floor": {
      "applied": False,
      "score": 0.0,
    },
  }
  return context_components


def _context_subtotal(components: dict[str, dict[str, Any]]) -> float:
  return round(sum(float(component["score"]) for component in components.values()), 2)


def _strategy_parameter_schema(run: RunRecord) -> dict[str, Any]:
  strategy_snapshot = run.provenance.strategy
  if strategy_snapshot is None:
    return {}
  return strategy_snapshot.parameter_snapshot.schema


def _strategy_parameter_values(run: RunRecord) -> dict[str, Any]:
  strategy_snapshot = run.provenance.strategy
  if strategy_snapshot is None:
    return run.config.parameters
  return strategy_snapshot.parameter_snapshot.resolved or run.config.parameters


def _parameter_semantic_descriptor_score(schema_entry: object) -> float:
  if not isinstance(schema_entry, dict):
    return 0.0
  score = 0.0
  if _normalized_semantic_text(schema_entry.get("semantic_hint")) is not None:
    score += 1.0
  if (
    _normalized_semantic_text(schema_entry.get("delta_higher_label")) is not None
    or _normalized_semantic_text(schema_entry.get("delta_lower_label")) is not None
  ):
    score += 0.75
  semantic_ranks = schema_entry.get("semantic_ranks")
  if isinstance(semantic_ranks, dict) and semantic_ranks:
    score += 0.5
  if _normalized_semantic_text(schema_entry.get("unit")) is not None:
    score += 0.25
  return score


def _semantic_schema_richness(schema: dict[str, Any]) -> float:
  return sum(
    _parameter_semantic_descriptor_score(schema_entry)
    for schema_entry in schema.values()
  )


def _benchmark_provenance_richness(run: RunRecord) -> float:
  score = 0.0
  for artifact in run.provenance.benchmark_artifacts:
    if artifact.exists:
      score += 0.2
    score += 0.8
    score += min(len(artifact.summary), 6) * 0.2
    score += min(len(artifact.sections), 8) * 0.3
    if artifact.summary_source_path:
      score += 0.5
    benchmark_story = artifact.sections.get("benchmark_story")
    if isinstance(benchmark_story, dict):
      score += min(len(benchmark_story), 6) * 0.25
  return score


def _normalize_comparison_intent(intent: str | None) -> str:
  if intent in (None, ""):
    return COMPARISON_INTENT_DEFAULT
  if intent not in COMPARISON_INTENT_WEIGHTS:
    supported = ", ".join(sorted(COMPARISON_INTENT_WEIGHTS))
    raise ValueError(f"Unsupported comparison intent: {intent}. Expected one of: {supported}.")
  return intent


def _build_comparison_narrative_title(
  *,
  intent: str,
  comparison_type: str,
  target_subject: str,
  baseline_label: str,
  total_return_delta: float | int | None,
  max_drawdown_delta: float | int | None,
) -> str | None:
  copy = COMPARISON_INTENT_COPY[intent]
  versus_baseline = "the baseline" if comparison_type != "native_vs_reference" else f"the native/reference baseline {baseline_label}"
  if total_return_delta is not None and max_drawdown_delta is not None:
    if intent == "benchmark_validation":
      if total_return_delta > 0 and max_drawdown_delta <= 0:
        return f"{copy['title_prefix']} favors {target_subject}: higher return without extra drawdown versus {versus_baseline}."
      if total_return_delta > 0 and max_drawdown_delta > 0:
        return f"{copy['title_prefix']} shows {target_subject} running hotter than {versus_baseline}: more return, but deeper drawdown."
      if total_return_delta < 0 and max_drawdown_delta <= 0:
        return f"{copy['title_prefix']} shows {target_subject} staying safer than {versus_baseline}, but giving up return."
      if total_return_delta < 0 and max_drawdown_delta > 0:
        return f"{copy['title_prefix']} flags {target_subject} as off-benchmark versus {versus_baseline}."
      return f"{copy['title_prefix']} shows {target_subject} holding close to {versus_baseline}."
    if intent == "execution_regression":
      if total_return_delta > 0 and max_drawdown_delta <= 0:
        return f"{copy['title_prefix']} sees {target_subject} diverging from {versus_baseline}, but not as a degradation."
      if total_return_delta > 0 and max_drawdown_delta > 0:
        return f"{copy['title_prefix']} shows {target_subject} changing risk behavior versus {versus_baseline}."
      if total_return_delta < 0 and max_drawdown_delta <= 0:
        return f"{copy['title_prefix']} shows {target_subject} throttling risk versus {versus_baseline}."
      if total_return_delta < 0 and max_drawdown_delta > 0:
        return f"{copy['title_prefix']} flags {target_subject} as a clear degradation versus {versus_baseline}."
      return f"{copy['title_prefix']} sees only limited drift in {target_subject} versus {versus_baseline}."
    if total_return_delta > 0 and max_drawdown_delta <= 0:
      return f"{copy['title_prefix']} clearly prefers {target_subject} over {versus_baseline}."
    if total_return_delta > 0 and max_drawdown_delta > 0:
      return f"{copy['title_prefix']} treats {target_subject} as the higher-upside variant versus {versus_baseline}, with a drawdown tradeoff."
    if total_return_delta < 0 and max_drawdown_delta <= 0:
      return f"{copy['title_prefix']} treats {target_subject} as the more defensive variant versus {versus_baseline}."
    if total_return_delta < 0 and max_drawdown_delta > 0:
      return f"{copy['title_prefix']} finds little upside in {target_subject} versus {versus_baseline}."
    return f"{copy['title_prefix']} keeps {target_subject} near-neutral against {versus_baseline}."
  if total_return_delta is not None:
    if intent == "strategy_tuning":
      if total_return_delta > 0:
        return f"{copy['title_prefix']} prefers {target_subject} for return potential versus {versus_baseline}."
      if total_return_delta < 0:
        return f"{copy['title_prefix']} sees {target_subject} as lower-upside than {versus_baseline}."
      return f"{copy['title_prefix']} sees no return edge between {target_subject} and {versus_baseline}."
    if total_return_delta > 0:
      return f"{copy['title_prefix']} shows {target_subject} ahead of {versus_baseline} on total return."
    if total_return_delta < 0:
      return f"{copy['title_prefix']} shows {target_subject} trailing {versus_baseline} on total return."
    return f"{copy['title_prefix']} shows {target_subject} matching {versus_baseline} on total return."
  if max_drawdown_delta is not None:
    if max_drawdown_delta < 0:
      return f"{copy['title_prefix']} shows {target_subject} containing drawdown better than {versus_baseline}."
    if max_drawdown_delta > 0:
      return f"{copy['title_prefix']} shows {target_subject} running with deeper drawdown than {versus_baseline}."
    return f"{copy['title_prefix']} shows {target_subject} matching {versus_baseline} on drawdown."
  if comparison_type == "native_vs_reference":
    return f"{copy['title_prefix']} frames {target_subject} as the comparison counterpart to {baseline_label}."
  return f"{copy['title_prefix']} reads {target_subject} against {baseline_label}."


def _build_comparison_narrative_summary(
  *,
  intent: str,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
  baseline_label: str,
  total_return_delta: float | int | None,
  max_drawdown_delta: float | int | None,
  win_rate_delta: float | int | None,
  trade_count_delta: float | int | None,
) -> str | None:
  copy = COMPARISON_INTENT_COPY[intent]
  semantic_context = _build_comparison_semantic_context_sentence(
    baseline_run=baseline_run,
    run=run,
    comparison_type=comparison_type,
  )
  metric_shifts: list[str] = []
  if total_return_delta is not None:
    metric_shifts.append(f"return {_format_metric_delta(total_return_delta, 'pct_points')}")
  if max_drawdown_delta is not None:
    metric_shifts.append(f"drawdown {_format_metric_delta(max_drawdown_delta, 'pct_points')}")
  if win_rate_delta is not None:
    metric_shifts.append(f"win rate {_format_metric_delta(win_rate_delta, 'pct_points')}")
  if trade_count_delta is not None:
    metric_shifts.append(f"trades {_format_metric_delta(trade_count_delta, 'count')}")
  if metric_shifts:
    if intent == "benchmark_validation":
      summary = (
        f"{copy['summary_prefix']} treats these shifts as benchmark drift against "
        f"{baseline_label}: {', '.join(metric_shifts)}."
      )
      return f"{summary} {semantic_context}" if semantic_context else summary
    if intent == "execution_regression":
      summary = (
        f"{copy['summary_prefix']} interprets these changes as execution drift against "
        f"{baseline_label}: {', '.join(metric_shifts)}."
      )
      return f"{summary} {semantic_context}" if semantic_context else summary
    summary = (
      f"{copy['summary_prefix']} reads these changes as optimization tradeoffs against "
      f"{baseline_label}: {', '.join(metric_shifts)}."
    )
    return f"{summary} {semantic_context}" if semantic_context else summary

  if comparison_type == "native_vs_reference" and _has_reference_context(run, baseline_run):
    summary = copy["partial_summary"]
    return f"{summary} {semantic_context}" if semantic_context else summary
  if run.status != baseline_run.status:
    summary = (
      f"{copy['summary_prefix']} also notes a status split: {run.status} versus "
      f"{baseline_run.status}."
    )
    return f"{summary} {semantic_context}" if semantic_context else summary
  return semantic_context


def _build_comparison_narrative_bullets(
  *,
  intent: str,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
  target_label: str,
  baseline_label: str,
  win_rate_delta: float | int | None,
  trade_count_delta: float | int | None,
) -> list[str]:
  bullets: list[str] = []

  lane_context = _build_lane_context_bullet(
    intent=intent,
    comparison_type=comparison_type,
    baseline_run=baseline_run,
    run=run,
  )
  if lane_context is not None:
    bullets.append(lane_context)

  activity_context = _build_activity_context_bullet(
    intent=intent,
    run=run,
    trade_count_delta=trade_count_delta,
    win_rate_delta=win_rate_delta,
  )
  if activity_context is not None:
    bullets.append(activity_context)

  reference_story = _build_reference_story_bullet(intent=intent, baseline_run=baseline_run, run=run)
  if reference_story is not None:
    bullets.append(reference_story)

  if not bullets and comparison_type == "native_vs_reference":
    bullets.append(f"{COMPARISON_INTENT_COPY[intent]['lane_prefix']}: {target_label} is the reference/native counterpart to {baseline_label}.")
  return bullets[:3]


def _build_lane_context_bullet(
  *,
  intent: str,
  comparison_type: str,
  baseline_run: RunRecord,
  run: RunRecord,
) -> str | None:
  if comparison_type != "native_vs_reference":
    return None
  copy = COMPARISON_INTENT_COPY[intent]
  reference_run = run if run.provenance.lane == "reference" else baseline_run
  native_run = baseline_run if reference_run is run else run
  reference_label = _comparison_run_label(reference_run)
  native_role = _format_comparison_semantic_role(native_run)
  reference_role = _format_comparison_semantic_role(reference_run, include_execution=True)
  reference_source = _strategy_semantics(reference_run).source_descriptor
  source_suffix = f" / source {reference_source}" if reference_source else ""
  return (
    f"{copy['lane_prefix']}: {native_role} engine {_comparison_run_label(native_run)} is being "
    f"read against {reference_role} benchmark {reference_label}{source_suffix}."
  )


def _build_activity_context_bullet(
  *,
  intent: str,
  run: RunRecord,
  trade_count_delta: float | int | None,
  win_rate_delta: float | int | None,
) -> str | None:
  copy = COMPARISON_INTENT_COPY[intent]
  trade_count = _resolve_run_metric_value(run, "trade_count")
  win_rate = _resolve_run_metric_value(run, "win_rate_pct")
  segments: list[str] = []
  if trade_count is not None:
    segment = f"trade flow landed at {trade_count}"
    if trade_count_delta is not None:
      segment += f" ({_format_metric_delta(trade_count_delta, 'count')} vs baseline)"
    segments.append(segment)
  if win_rate is not None:
    segment = f"win rate closed at {win_rate}%"
    if win_rate_delta is not None:
      segment += f" ({_format_metric_delta(win_rate_delta, 'pct_points')} vs baseline)"
    segments.append(segment)
  if not segments:
    return None
  return f"{copy['activity_prefix']}: " + "; ".join(segments) + "."


def _build_reference_story_bullet(
  *,
  intent: str,
  baseline_run: RunRecord,
  run: RunRecord,
) -> str | None:
  copy = COMPARISON_INTENT_COPY[intent]
  reference_run = None
  if run.provenance.lane == "reference":
    reference_run = run
  elif baseline_run.provenance.lane == "reference":
    reference_run = baseline_run
  if reference_run is None:
    return None
  benchmark_story = _extract_benchmark_story(reference_run)
  if not benchmark_story:
    return None
  for key in ("headline", "signal_context", "exit_context", "market_context", "pair_context", "portfolio_context"):
    value = benchmark_story.get(key)
    if isinstance(value, str) and value:
      return f"{copy['reference_prefix']}: {value}"
  return None


def _classify_comparison_type(baseline_run: RunRecord, run: RunRecord) -> str:
  lanes = {baseline_run.provenance.lane, run.provenance.lane}
  if lanes == {"native", "reference"}:
    return "native_vs_reference"
  if lanes == {"reference"}:
    return "reference_vs_reference"
  if lanes == {"native"}:
    return "native_vs_native"
  return "run_vs_baseline"


def _comparison_run_label(run: RunRecord) -> str:
  if run.provenance.reference is not None and run.provenance.reference.title:
    return run.provenance.reference.title
  if run.provenance.strategy is not None and run.provenance.strategy.name:
    return run.provenance.strategy.name
  return run.config.strategy_id


def _comparison_subject_label(run: RunRecord) -> str:
  label = _comparison_run_label(run)
  semantics = _strategy_semantics(run)
  role = _format_comparison_semantic_role(run)
  if run.provenance.lane == "reference":
    return f"{role} benchmark {label}"
  if semantics.strategy_kind == "imported_module":
    return f"{role} strategy {label}"
  if run.provenance.lane == "native":
    return f"{role} run {label}"
  return label


def _has_reference_context(run: RunRecord, baseline_run: RunRecord) -> bool:
  return any(candidate.provenance.lane == "reference" for candidate in (run, baseline_run))


def _build_metric_semantic_annotation_suffix(
  *,
  baseline_run: RunRecord,
  runs: list[RunRecord],
) -> str | None:
  baseline_role = _format_comparison_semantic_role(baseline_run, include_execution=True)
  comparison_roles = [
    role
    for role in dict.fromkeys(
      _build_metric_annotation_role_label(baseline_run=baseline_run, run=run)
      for run in runs
      if run.config.run_id != baseline_run.config.run_id
    )
    if role is not None
  ]
  if not comparison_roles:
    return None
  if len(comparison_roles) == 1:
    return f"baseline {baseline_role}; compared against {comparison_roles[0]}"
  listed_roles = ", ".join(comparison_roles[:2])
  if len(comparison_roles) > 2:
    listed_roles = f"{listed_roles}, +{len(comparison_roles) - 2} more"
  return f"baseline {baseline_role}; compared against {listed_roles}"


def _build_metric_annotation_role_label(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
) -> str | None:
  baseline_role = _format_comparison_semantic_role(baseline_run, include_execution=True)
  run_role = _format_comparison_semantic_role(run, include_execution=True)
  if run_role == baseline_role:
    return None
  return run_role


def _build_metric_delta_semantic_suffix(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
) -> str | None:
  role = _build_metric_annotation_role_label(baseline_run=baseline_run, run=run)
  if role is None:
    return None
  source_descriptor = _strategy_semantics(run).source_descriptor
  if source_descriptor is None:
    return role
  return f"{role} ({source_descriptor})"


def _build_comparison_semantic_context_sentence(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
  comparison_type: str,
) -> str | None:
  if not _comparison_has_semantic_signal(baseline_run=baseline_run, run=run):
    return None
  baseline_role = _format_comparison_semantic_role(baseline_run, include_execution=True)
  run_role = _format_comparison_semantic_role(run, include_execution=True)
  run_source = _strategy_semantics(run).source_descriptor
  if comparison_type == "native_vs_reference":
    summary = f"Semantic context compares {baseline_role} execution to {run_role}"
  else:
    summary = f"Semantic context compares {run_role} against {baseline_role}"
  if run_source:
    summary = f"{summary} (source {run_source})"
  return f"{summary}."


def _comparison_has_semantic_signal(
  *,
  baseline_run: RunRecord,
  run: RunRecord,
) -> bool:
  baseline_semantics = _strategy_semantics(baseline_run)
  run_semantics = _strategy_semantics(run)
  return (
    baseline_run.provenance.lane != run.provenance.lane
    or baseline_semantics.strategy_kind != run_semantics.strategy_kind
    or baseline_semantics.execution_model != run_semantics.execution_model
    or baseline_semantics.source_descriptor != run_semantics.source_descriptor
    or baseline_semantics.parameter_contract != run_semantics.parameter_contract
  )


def _strategy_semantics(run: RunRecord) -> StrategyCatalogSemantics:
  if run.provenance.strategy is not None:
    return run.provenance.strategy.catalog_semantics
  return StrategyCatalogSemantics()


def _format_comparison_semantic_role(
  run: RunRecord,
  *,
  include_execution: bool = False,
) -> str:
  semantics = _strategy_semantics(run)
  lane = run.provenance.lane or "run"
  if semantics.strategy_kind == "reference_delegate":
    role = "reference delegate"
  elif semantics.strategy_kind == "imported_module":
    role = "imported module"
  elif semantics.strategy_kind in ("", "standard"):
    role = f"{lane} standard"
  else:
    normalized_kind = semantics.strategy_kind.replace("_", " ")
    role = normalized_kind if lane in normalized_kind else f"{lane} {normalized_kind}"
  execution_label = _format_comparison_execution_label(run)
  if include_execution and execution_label:
    return f"{role} via {execution_label}"
  return role


def _format_comparison_execution_label(run: RunRecord) -> str | None:
  if run.provenance.integration_mode:
    return run.provenance.integration_mode
  execution_model = _strategy_semantics(run).execution_model.strip()
  if execution_model and len(execution_model) <= 40:
    return execution_model
  return None


def _metric_row_delta(
  metric_row_by_key: dict[str, RunComparisonMetricRow],
  key: str,
  run_id: str,
) -> float | int | None:
  metric_row = metric_row_by_key.get(key)
  if metric_row is None:
    return None
  return metric_row.deltas_vs_baseline.get(run_id)


def _resolve_run_metric_value(run: RunRecord, key: str) -> float | int | None:
  direct_value = _coerce_metric_value(run.metrics.get(key))
  if direct_value is not None:
    return direct_value
  return _extract_benchmark_metric_value(run, key)


def _extract_benchmark_metric_value(run: RunRecord, key: str) -> float | int | None:
  summary_key_map = {
    "total_return_pct": "profit_total_pct",
    "max_drawdown_pct": "max_drawdown_pct",
    "trade_count": "trade_count",
    "win_rate_pct": "win_rate_pct",
  }
  summary_key = summary_key_map.get(key)
  if summary_key is None:
    return None

  artifacts = sorted(
    run.provenance.benchmark_artifacts,
    key=lambda artifact: _benchmark_artifact_priority(artifact.kind),
  )
  for artifact in artifacts:
    value = _coerce_metric_value(artifact.summary.get(summary_key))
    if value is not None:
      return value
    if key == "win_rate_pct":
      for section_name, row_key in (
        ("strategy_comparison", "best"),
        ("pair_metrics", "total"),
      ):
        section = artifact.sections.get(section_name)
        if not isinstance(section, dict):
          continue
        candidate_row = section.get(row_key)
        if isinstance(candidate_row, dict):
          value = _coerce_metric_value(candidate_row.get(summary_key))
          if value is not None:
            return value
        preview = section.get("preview")
        if isinstance(preview, list) and preview:
          first_row = preview[0]
          if isinstance(first_row, dict):
            value = _coerce_metric_value(first_row.get(summary_key))
            if value is not None:
              return value
  return None


def _extract_benchmark_story(run: RunRecord) -> dict[str, str]:
  artifacts = sorted(
    run.provenance.benchmark_artifacts,
    key=lambda artifact: _benchmark_artifact_priority(artifact.kind),
  )
  for artifact in artifacts:
    story = artifact.sections.get("benchmark_story")
    if not isinstance(story, dict):
      continue
    normalized_story = {
      key: value
      for key, value in story.items()
      if isinstance(value, str) and value
    }
    if normalized_story:
      return normalized_story
  return {}


def _benchmark_artifact_priority(kind: str) -> int:
  priorities = {
    "result_snapshot": 0,
    "result_snapshot_root": 1,
    "result_manifest": 2,
  }
  return priorities.get(kind, 100)


def _format_metric_delta(value: float | int | None, unit: str) -> str:
  if value is None:
    return "n/a"
  prefix = "+" if value > 0 else ""
  if unit == "pct_points":
    return f"{prefix}{value} pts"
  if unit == "count":
    suffix = "trade" if value in {-1, 1} else "trades"
    return f"{prefix}{value} {suffix}"
  return f"{prefix}{value}"


def _coerce_metric_value(value: object) -> float | int | None:
  if isinstance(value, bool) or not isinstance(value, Number):
    return None
  if isinstance(value, int):
    return value
  return round(float(value), 2)


def _calculate_metric_delta(
  value: float | int | None,
  baseline_value: float | int | None,
) -> float | int | None:
  if value is None or baseline_value is None:
    return None
  delta = value - baseline_value
  if isinstance(value, int) and isinstance(baseline_value, int):
    return int(delta)
  return round(float(delta), 2)
