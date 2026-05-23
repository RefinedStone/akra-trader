from __future__ import annotations

from datetime import UTC
from datetime import datetime
from datetime import timedelta
import json
from types import SimpleNamespace

import pandas as pd
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from akra_trader.adapters.core_storage import InMemoryCoreRepository
from akra_trader.adapters.in_memory_market_data import SeededMarketDataAdapter
from akra_trader.adapters.mock_llm_judgement import MockLlmJudgementClient
from akra_trader.adapters.openai_llm_judgement import OpenAiLlmJudgementClient
from akra_trader.api import include_routes
from akra_trader.application import TradingApplication
from akra_trader.bootstrap import Container
from akra_trader.bootstrap import build_llm_judgement_adapter
from akra_trader.config import Settings
from akra_trader.domain.models import AssetType
from akra_trader.domain.models import ExecutionPlan
from akra_trader.domain.models import LlmCandidateSignal
from akra_trader.domain.models import LlmCurrentPositionState
from akra_trader.domain.models import LlmJudgementDecision
from akra_trader.domain.models import LlmJudgementRequest
from akra_trader.domain.models import LlmJudgementResponse
from akra_trader.domain.models import LlmMarketRegime
from akra_trader.domain.models import LlmRiskLevel
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import SignalAction
from akra_trader.domain.models import SignalDecision
from akra_trader.domain.models import StrategyDecisionContext
from akra_trader.domain.models import StrategyDecisionEnvelope
from akra_trader.domain.models import StrategyExecutionState
from akra_trader.domain.models import StrategyLifecycle
from akra_trader.domain.models import StrategyMetadata
from akra_trader.domain.models import WarmupSpec
from akra_trader.domain.models import build_safe_llm_judgement_fallback
from akra_trader.domain.models import llm_judgement_request_json_schema
from akra_trader.domain.models import llm_judgement_response_json_schema
from akra_trader.strategies.base import Strategy
from akra_trader.strategies.llm import LlmJudgementVetoStrategy
from akra_trader.strategies.llm import apply_llm_judgement_veto


TIMESTAMP = datetime(2026, 5, 13, 12, 0, tzinfo=UTC)


def test_llm_judgement_contract_round_trips_as_json_schema():
  request = LlmJudgementRequest(
    timestamp=TIMESTAMP,
    instrument_id="binance:BTC/USDT",
    strategy_id="rule_strategy",
    candidate_signal=LlmCandidateSignal(
      action="buy",
      size_fraction=0.5,
      confidence=0.72,
      tags=("entry",),
      reason="rule_entry",
    ),
    market_snapshot={"close": 100.0, "volume": 1000.0},
    selected_features={"rsi": 29.0, "ema_fast": 101.0},
    recent_feature_history=(
      {"timestamp": TIMESTAMP.isoformat(), "close": 100.0, "rsi": 29.0},
    ),
    current_position=LlmCurrentPositionState(
      has_position=False,
      cash=10_000.0,
      position_size=0.0,
    ),
    rule_rationale="rule candidate accepted trend and pullback filters",
  )
  response = LlmJudgementResponse(
    decision=LlmJudgementDecision.APPROVE_BUY,
    confidence=0.9,
    market_regime=LlmMarketRegime.TRENDING,
    risk_level=LlmRiskLevel.LOW,
    risk_flags=(),
    reasons=("trend_confirmed",),
    dimension_reviews={"momentum": "rsi rebound is constructive"},
    invalidation_condition="close below prior swing low",
  )

  request_payload = TypeAdapter(LlmJudgementRequest).dump_python(request, mode="json")
  response_payload = TypeAdapter(LlmJudgementResponse).dump_python(response, mode="json")
  json.dumps(request_payload)
  json.dumps(response_payload)

  assert TypeAdapter(LlmJudgementRequest).validate_python(request_payload) == request
  assert TypeAdapter(LlmJudgementResponse).validate_python(response_payload) == response
  assert "provider" not in request_payload
  assert "model" not in request_payload
  assert "provider" not in response_payload
  assert "model" not in response_payload
  assert "candidate_signal" in llm_judgement_request_json_schema()["properties"]
  assert "recent_feature_history" in llm_judgement_request_json_schema()["properties"]
  assert "invalidation_condition" in llm_judgement_response_json_schema()["properties"]
  assert "dimension_reviews" in llm_judgement_response_json_schema()["properties"]


@pytest.mark.parametrize(
  ("scenario", "expected_decision", "expected_confidence", "expected_risk_level"),
  [
    ("approve", LlmJudgementDecision.APPROVE_BUY, 0.9, LlmRiskLevel.LOW),
    ("no_trade", LlmJudgementDecision.NO_TRADE, 0.9, LlmRiskLevel.MEDIUM),
    ("low_confidence", LlmJudgementDecision.APPROVE_BUY, 0.2, LlmRiskLevel.LOW),
    ("high_risk", LlmJudgementDecision.APPROVE_BUY, 0.9, LlmRiskLevel.HIGH),
  ],
)
def test_mock_llm_judgement_client_replays_deterministic_scenarios(
  scenario,
  expected_decision,
  expected_confidence,
  expected_risk_level,
):
  client = MockLlmJudgementClient(scenario=scenario)
  request = _request("buy")

  response = client.judge(request)

  assert response.decision == expected_decision
  assert response.confidence == expected_confidence
  assert response.risk_level == expected_risk_level
  assert client.requests == [request]


def test_safe_fallback_never_approves_new_trade():
  response = build_safe_llm_judgement_fallback("schema_parse_failed")

  assert response.decision == LlmJudgementDecision.NO_TRADE
  assert response.confidence == 0.0
  assert response.risk_level == LlmRiskLevel.HIGH
  assert response.used_fallback is True


def test_llm_judgement_approval_keeps_candidate_buy_and_records_trace():
  client = MockLlmJudgementClient(scenario="approve")
  candidate = _candidate(SignalAction.BUY)

  envelope = apply_llm_judgement_veto(
    candidate,
    judgement=client,
    strategy_id="rule_strategy",
    min_confidence=0.7,
  )

  assert envelope.signal.action == SignalAction.BUY
  assert "llm_judgement_approved" in envelope.signal.tags
  assert client.requests[0].candidate_signal.action == "buy"
  assert client.requests[0].instrument_id == "binance:BTC/USDT"
  assert client.requests[0].current_position.has_position is False
  assert len(client.requests[0].recent_feature_history) == 40
  assert client.requests[0].recent_feature_history[-1]["close"] == 100.0
  assert "entry_evaluation" in client.requests[0].trace_context["trace_summary"]
  assert "raw_prompt" not in client.requests[0].trace_context["trace_summary"]
  assert envelope.trace["rule_layer"] == "matched"
  judgement_trace = envelope.trace["llm_judgement"]
  assert judgement_trace["status"] == "approved"
  assert judgement_trace["mode"] == "veto_only"
  assert judgement_trace["min_confidence"] == 0.7
  assert judgement_trace["request"]["strategy_id"] == "rule_strategy"
  assert judgement_trace["request"]["recent_history_rows"] == 40
  assert "rsi" in judgement_trace["request"]["recent_history_keys"]
  assert judgement_trace["response"]["decision"] == "approve_buy"
  assert judgement_trace["veto_reason"] is None


@pytest.mark.parametrize(
  ("scenario", "expected_veto_reason"),
  [
    ("no_trade", "no_trade"),
    ("low_confidence", "confidence_below_threshold"),
    ("high_risk", "high_risk"),
    ("stale_data", "stale_data"),
    ("conflict", "decision_conflict"),
    ("malformed", "fallback"),
    ("provider_error", "fallback"),
  ],
)
def test_llm_judgement_vetoes_unsafe_buy_candidates(scenario, expected_veto_reason):
  client = MockLlmJudgementClient(scenario=scenario)
  candidate = _candidate(SignalAction.BUY)

  envelope = apply_llm_judgement_veto(candidate, judgement=client, min_confidence=0.7)

  assert envelope.signal.action == SignalAction.HOLD
  assert envelope.signal.size_fraction == 0.0
  assert "llm_judgement_veto" in envelope.signal.tags
  assert envelope.execution.size_fraction == 0.0
  judgement_trace = envelope.trace["llm_judgement"]
  assert judgement_trace["status"] == "vetoed"
  assert judgement_trace["veto_reason"] == expected_veto_reason
  assert judgement_trace["candidate"]["action"] == "buy"
  if expected_veto_reason == "fallback":
    assert judgement_trace["fallback"] is True


def test_llm_judgement_skips_hold_candidate_without_upgrading_signal():
  client = MockLlmJudgementClient(scenario="approve")
  candidate = _candidate(SignalAction.HOLD)

  envelope = apply_llm_judgement_veto(candidate, judgement=client)

  assert envelope.signal.action == SignalAction.HOLD
  assert client.requests == []
  assert envelope.trace["llm_judgement"]["status"] == "skipped"
  assert envelope.trace["llm_judgement"]["request"] is None


def test_llm_judgement_veto_strategy_wraps_existing_strategy_decision():
  strategy = LlmJudgementVetoStrategy(
    _FixedCandidateStrategy(SignalAction.BUY),
    MockLlmJudgementClient(scenario="approve"),
  )

  envelope = strategy.decide(_context(parameters={"llm_judgement_min_confidence": 0.7}))

  assert envelope.signal.action == SignalAction.BUY
  assert envelope.trace["llm_judgement"]["status"] == "approved"


def test_llm_judgement_strategy_threshold_parameter_can_veto_approval():
  strategy = LlmJudgementVetoStrategy(
    _FixedCandidateStrategy(SignalAction.BUY),
    MockLlmJudgementClient(scenario="approve"),
  )

  envelope = strategy.decide(_context(parameters={"llm_judgement_min_confidence": 0.95}))

  assert envelope.signal.action == SignalAction.HOLD
  assert envelope.trace["llm_judgement"]["veto_reason"] == "confidence_below_threshold"


def test_llm_judgement_recent_history_window_parameter_is_capped():
  client = MockLlmJudgementClient(scenario="approve")
  strategy = LlmJudgementVetoStrategy(_FixedCandidateStrategy(SignalAction.BUY), client)

  envelope = strategy.decide(_context(parameters={"llm_judgement_recent_window": 120}))

  assert envelope.signal.action == SignalAction.BUY
  assert len(client.requests[0].recent_feature_history) == 45
  assert envelope.trace["llm_judgement"]["request"]["recent_history_rows"] == 45
  assert envelope.trace["llm_judgement"]["min_confidence"] == 0.6


def test_application_can_opt_into_mock_backtest_judgement_without_provider_sdk():
  client = MockLlmJudgementClient(scenario="approve")
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=_SingleStrategyCatalog(_FixedCandidateStrategy(SignalAction.BUY)),
    runs=InMemoryCoreRepository(),
    llm_judgement=client,
  )

  run = app.run_backtest(
    strategy_id="fixed_candidate_strategy",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=5,
    parameters={"use_llm_judgement": True, "llm_judgement_min_confidence": 0.95},
  )

  assert run.status.value == "completed"
  assert run.orders == []
  assert client.requests
  assert any("LLM judgement vetoed" in note for note in run.notes)
  judgement_logs = [
    log
    for log in app.get_run_logs(run.config.run_id)
    if log.event_type == "llm_judgement_recorded"
  ]
  assert judgement_logs
  payload = judgement_logs[0].payload
  assert payload["candidate"]["action"] == "buy"
  assert payload["request"]["candidate_action"] == "buy"
  assert payload["response"]["decision"] == "approve_buy"
  assert payload["fallback"] is False
  assert payload["veto_reason"] == "confidence_below_threshold"
  assert payload["final_action"] == "hold"
  assert app.get_run_llm_judgements(run.config.run_id)[0]["final_action"] == "hold"

  fastapi_app = FastAPI()
  include_routes(fastapi_app, Container(app=app), "/api")
  response = TestClient(fastapi_app).get(f"/api/runs/{run.config.run_id}/llm-judgements")
  assert response.status_code == 200
  judgements = response.json()["judgements"]
  assert judgements[0]["veto_reason"] == "confidence_below_threshold"
  assert judgements[0]["final_action"] == "hold"


def test_openai_llm_judgement_adapter_uses_structured_response_and_records_trace():
  client = _FakeOpenAiClient(
    _openai_response(
      {
        "decision": "approve_buy",
        "confidence": 0.88,
        "market_regime": "trending",
        "risk_level": "low",
        "risk_flags": [],
        "reasons": ["rsi_rebound_confirmed"],
        "dimension_reviews": {
          "trend": "ma slope does not block the candidate",
          "momentum": "rsi rebound supports the candidate",
        },
        "invalidation_condition": "close below recent low",
      }
    )
  )
  adapter = OpenAiLlmJudgementClient(api_key="test-key", model="gpt-test", client=client)

  response = adapter.judge(_request("buy"))

  assert response.decision == LlmJudgementDecision.APPROVE_BUY
  assert response.confidence == 0.88
  assert response.risk_level == LlmRiskLevel.LOW
  assert response.dimension_reviews["momentum"] == "rsi rebound supports the candidate"
  assert response.used_fallback is False
  assert response.trace["provider"] == "openai"
  assert response.trace["model"] == "gpt-test"
  assert response.trace["response_id"] == "resp_test"
  assert response.trace["raw_output_stored"] is False
  assert "rsi" in response.trace["request_feature_keys"]
  assert response.trace["recent_history_rows"] == 1
  assert client.calls[0]["model"] == "gpt-test"
  assert client.calls[0]["reasoning"] == {"effort": "low"}
  assert client.calls[0]["input"][0]["content"].startswith(
    "You are a veto-only top-tier discretionary trader"
  )
  payload = json.loads(client.calls[0]["input"][1]["content"].split("\n", 1)[1])
  assert payload["recent_feature_history"][0]["rsi"] == 29.0


@pytest.mark.parametrize("scenario", ["malformed", "refusal"])
def test_openai_llm_judgement_adapter_fails_closed(scenario):
  response = (
    _openai_response(
      {
        "decision": "not_a_decision",
        "confidence": "invalid",
      }
    )
    if scenario == "malformed"
    else SimpleNamespace(
      id="resp_refusal",
      output=[
        SimpleNamespace(
          type="message",
          content=[SimpleNamespace(type="refusal", refusal="cannot judge")],
        )
      ],
    )
  )
  adapter = OpenAiLlmJudgementClient(
    api_key="test-key",
    model="gpt-test",
    client=_FakeOpenAiClient(response),
  )

  result = adapter.judge(_request("buy"))

  assert result.decision == LlmJudgementDecision.NO_TRADE
  assert result.confidence == 0.0
  assert result.risk_level == LlmRiskLevel.HIGH
  assert result.used_fallback is True
  assert result.trace["provider"] == "openai"
  assert result.trace["status"] == "fallback_after_provider_error"


def test_bootstrap_builds_configured_llm_judgement_provider_without_startup_failure():
  assert build_llm_judgement_adapter(Settings(llm_judgement_provider="disabled")) is None
  assert build_llm_judgement_adapter(Settings(llm_judgement_provider="openai")) is None

  mock = build_llm_judgement_adapter(
    Settings(llm_judgement_provider="mock", llm_judgement_mock_scenario="no_trade")
  )
  assert isinstance(mock, MockLlmJudgementClient)
  assert mock.judge(_request("buy")).decision == LlmJudgementDecision.NO_TRADE

  openai = build_llm_judgement_adapter(
    Settings(
      llm_judgement_provider="openai",
      openai_api_key="test-key",
      llm_judgement_model="gpt-test",
    )
  )
  assert isinstance(openai, OpenAiLlmJudgementClient)


def test_live_run_ignores_llm_judgement_even_when_requested():
  client = MockLlmJudgementClient(scenario="no_trade")
  app = TradingApplication(
    market_data=SeededMarketDataAdapter(),
    strategies=_SingleStrategyCatalog(_FixedCandidateStrategy(SignalAction.BUY)),
    runs=InMemoryCoreRepository(),
    llm_judgement=client,
    guarded_live_execution_enabled=True,
  )

  run = app.start_live_run(
    strategy_id="fixed_candidate_strategy",
    symbol="BTC/USDT",
    timeframe="5m",
    initial_cash=10_000,
    fee_rate=0.001,
    slippage_bps=5,
    parameters={"use_llm_judgement": True},
    replay_bars=2,
  )

  assert run.status == RunStatus.RUNNING
  assert client.requests == []
  logs = app.get_run_logs(run.config.run_id)
  assert any(log.event_type == "llm_judgement_live_ignored" for log in logs)
  assert not any(log.event_type == "llm_judgement_recorded" for log in logs)


class _FixedCandidateStrategy(Strategy):
  def __init__(self, action: SignalAction) -> None:
    self._action = action

  def describe(self) -> StrategyMetadata:
    return StrategyMetadata(
      strategy_id="fixed_candidate_strategy",
      name="Fixed Candidate Strategy",
      version="0.1.0",
      runtime="test",
      asset_types=(AssetType.CRYPTO,),
      supported_timeframes=("5m",),
      parameter_schema={},
      description="Fixed candidate strategy for LLM judgement tests.",
      lifecycle=StrategyLifecycle(stage="experimental"),
    )

  def warmup_spec(self) -> WarmupSpec:
    return WarmupSpec(required_bars=2)

  def build_feature_frame(self, candles: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    return candles

  def decide(self, context: StrategyDecisionContext) -> StrategyDecisionEnvelope:
    return _candidate(self._action, context=context)


class _SingleStrategyCatalog:
  def __init__(self, strategy: Strategy) -> None:
    self._strategy = strategy

  def list_strategies(self) -> list[StrategyMetadata]:
    return [self._strategy.describe()]

  def load(self, strategy_id: str) -> Strategy:
    if strategy_id != self._strategy.describe().strategy_id:
      raise KeyError(strategy_id)
    return self._strategy

  def register(self, registration):
    raise NotImplementedError

  def get_registration(self, strategy_id: str):
    return None


class _FakeOpenAiClient:
  def __init__(self, response) -> None:
    self._response = response
    self.responses = self
    self.calls: list[dict] = []

  def parse(self, **kwargs):
    self.calls.append(kwargs)
    return self._response


def _openai_response(parsed):
  return SimpleNamespace(
    id="resp_test",
    output=[
      SimpleNamespace(
        type="message",
        content=[
          SimpleNamespace(
            type="output_text",
            parsed=parsed,
          )
        ],
      )
    ],
  )


def _request(action: str) -> LlmJudgementRequest:
  return LlmJudgementRequest(
    timestamp=TIMESTAMP,
    instrument_id="binance:BTC/USDT",
    candidate_signal=LlmCandidateSignal(
      action=action,
      size_fraction=0.5,
      confidence=0.72,
      reason="rule_entry",
    ),
    market_snapshot={"close": 100.0},
    selected_features={"rsi": 29.0},
    recent_feature_history=(
      {"timestamp": TIMESTAMP.isoformat(), "close": 100.0, "rsi": 29.0},
    ),
    current_position=LlmCurrentPositionState(
      has_position=False,
      cash=10_000.0,
      position_size=0.0,
    ),
    rule_rationale="rule rationale",
  )


def _candidate(
  action: SignalAction,
  *,
  context: StrategyDecisionContext | None = None,
) -> StrategyDecisionEnvelope:
  context = context or _context()
  signal = SignalDecision(
    timestamp=context.timestamp,
    action=action,
    size_fraction=0.5 if action != SignalAction.HOLD else 0.0,
    confidence=0.72,
    tags=("rule_candidate",),
    reason="rule_entry" if action != SignalAction.HOLD else "rule_hold",
  )
  return StrategyDecisionEnvelope(
    signal=signal,
    rationale=f"rule candidate {action.value}",
    context=context,
    execution=ExecutionPlan(size_fraction=signal.size_fraction),
    trace={
      "rule_layer": "matched",
      "entry_evaluation": {
        "filters": {
          "momentum": {"passed": True, "value": 29.0},
          "structure": {"passed": True, "recent_lower_lows": False},
        }
      },
      "raw_prompt": "must_not_be_forwarded",
    },
  )


def _context(parameters: dict | None = None) -> StrategyDecisionContext:
  return StrategyDecisionContext(
    timestamp=TIMESTAMP,
    instrument_id="binance:BTC/USDT",
    features={
      "timestamp": TIMESTAMP,
      "close": 100.0,
      "rsi": 29.0,
      "ema_fast": 101.0,
      "ema_slow": 99.0,
    },
    market={"open": 99.0, "high": 101.0, "low": 98.0, "close": 100.0, "volume": 1000.0},
    state=StrategyExecutionState(
      timestamp=TIMESTAMP,
      instrument_id="binance:BTC/USDT",
      has_position=False,
      cash=10_000.0,
      position_size=0.0,
      parameters=parameters or {},
    ),
    recent_features=_recent_features(),
  )


def _recent_features() -> tuple[dict[str, object], ...]:
  rows: list[dict[str, object]] = []
  for index in range(45):
    rows.append(
      {
        "timestamp": (TIMESTAMP - timedelta(minutes=5 * (44 - index))).isoformat(),
        "open": 95.0 + index * 0.1,
        "high": 96.0 + index * 0.1,
        "low": 94.0 + index * 0.1,
        "close": 95.6 + index * 0.1,
        "volume": 1000.0 + index,
        "rsi": 25.0 + index * 0.1,
        "atr": 2.1,
        "ma20": 97.0,
        "ma60": 99.0,
        "ma20_slope": 0.02,
        "ma60_slope": -0.01,
        "recent_lower_lows": False,
      }
    )
  rows[-1]["close"] = 100.0
  rows[-1]["rsi"] = 29.0
  return tuple(rows)
