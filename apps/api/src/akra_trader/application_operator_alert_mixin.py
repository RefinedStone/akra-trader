from __future__ import annotations

from akra_trader.application_context import *  # noqa: F403
from akra_trader import application_context as _application_context

globals().update({
  name: getattr(_application_context, name)
  for name in dir(_application_context)
  if name.startswith("_") and not name.startswith("__")
})

class TradingApplicationOperatorAlertMixin:
  @staticmethod
  def _suppress_pending_incident_retries(
    *,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    incident_event_id: str,
    reason: str,
    phase: str | None = None,
  ) -> tuple[OperatorIncidentDelivery, ...]:
    return guarded_live_incident_support._suppress_pending_incident_retries(delivery_history=delivery_history, incident_event_id=incident_event_id, reason=reason, phase=phase)
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
    return guarded_live_incident_workflow_orchestration_support._sync_incident_provider_workflow(
      self,
      incident=incident,
      delivery_history=delivery_history,
      current_time=current_time,
      action=action,
      actor=actor,
      detail=detail,
      payload=payload,
    )
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
    return guarded_live_incident_support._confirm_external_provider_workflow(self, delivery_history=delivery_history, incident=incident, provider=provider, event_kind=event_kind, detail=detail, occurred_at=occurred_at, external_reference=external_reference)
  @staticmethod
  def _provider_phase_for_event_kind(event_kind: str) -> str | None:
    return guarded_live_incident_support._provider_phase_for_event_kind(event_kind)
  def _incident_has_exhausted_initial_delivery(
    self,
    *,
    incident: OperatorIncidentEvent,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
  ) -> bool:
    return guarded_live_incident_support._incident_has_exhausted_initial_delivery(self, incident=incident, delivery_history=delivery_history)
  def _escalate_incident_event(
    self,
    *,
    incident: OperatorIncidentEvent,
    delivery_history: tuple[OperatorIncidentDelivery, ...],
    current_time: datetime,
    actor: str,
    reason: str,
    trigger: str,
    lineage_evidence_pack_id: str | None = None,
    lineage_evidence_retention_expires_at: datetime | None = None,
    lineage_evidence_summary: str | None = None,
  ) -> tuple[OperatorIncidentEvent, tuple[OperatorIncidentDelivery, ...], OperatorAuditEvent]:
    return guarded_live_incident_workflow_orchestration_support._escalate_incident_event(
      self,
      incident=incident,
      delivery_history=delivery_history,
      current_time=current_time,
      actor=actor,
      reason=reason,
      trigger=trigger,
      lineage_evidence_pack_id=lineage_evidence_pack_id,
      lineage_evidence_retention_expires_at=lineage_evidence_retention_expires_at,
      lineage_evidence_summary=lineage_evidence_summary,
    )
  def _resolve_incident_escalation_backoff_seconds(self, escalation_level: int) -> int:
    return guarded_live_incident_support._resolve_incident_escalation_backoff_seconds(self, escalation_level)
  def _build_live_operator_alerts_for_run(
    self,
    *,
    run: RunRecord,
    current_time: datetime,
  ) -> list[OperatorAlert]:
    return guarded_live_run_alert_builder_support._build_live_operator_alerts_for_run(
      self,
      run=run,
      current_time=current_time,
    )
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
  def _normalize_operator_alert_symbol(symbol: str | None) -> str | None:
    normalized = (symbol or "").strip().upper()
    return normalized or None
  @classmethod
  def _normalize_operator_alert_symbols(cls, symbols: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    normalized: list[str] = []
    seen: set[str] = set()
    for symbol in symbols:
      candidate = cls._normalize_operator_alert_symbol(symbol)
      if candidate is None or candidate in seen:
        continue
      seen.add(candidate)
      normalized.append(candidate)
    return tuple(normalized)
  @staticmethod
  def _normalize_operator_alert_timeframe(timeframe: str | None) -> str | None:
    normalized = (timeframe or "").strip().lower()
    return normalized or None
  @staticmethod
  def _operator_market_data_sync_severity_rank(sync_status: str) -> int:
    normalized = sync_status.strip().lower()
    if normalized == "error":
      return 4
    if normalized == "stale":
      return 3
    if normalized == "lagging":
      return 2
    if normalized == "syncing":
      return 1
    if normalized == "synced":
      return 0
    return 1 if normalized else 0
  @classmethod
  def _score_operator_market_data_instrument(cls, instrument: InstrumentStatus) -> int:
    return (
      cls._operator_market_data_sync_severity_rank(instrument.sync_status) * 1000
      + min(instrument.failure_count_24h, 99) * 100
      + len(instrument.backfill_gap_windows) * 40
      + len(instrument.issues) * 35
      + (20 if (instrument.backfill_contiguous_missing_candles or 0) > 0 else 0)
      + (10 if instrument.backfill_target_candles is not None and instrument.backfill_complete is False else 0)
      + min(int((instrument.lag_seconds or 0) / 60), 15)
    )
  @classmethod
  def _build_operator_alert_primary_focus(
    cls,
    *,
    primary_symbol: str | None = None,
    symbols: tuple[str, ...] | list[str] = (),
    candidate_symbols: tuple[str, ...] | list[str] | None = None,
    timeframe: str | None = None,
    policy: str | None = None,
    reason: str | None = None,
  ) -> OperatorAlertPrimaryFocus | None:
    normalized_symbols = cls._normalize_operator_alert_symbols(symbols)
    normalized_candidate_symbols = cls._normalize_operator_alert_symbols(
      candidate_symbols if candidate_symbols is not None else normalized_symbols
    )
    normalized_primary_symbol = cls._normalize_operator_alert_symbol(primary_symbol)
    normalized_timeframe = cls._normalize_operator_alert_timeframe(timeframe)

    if normalized_primary_symbol is None and normalized_candidate_symbols:
      normalized_primary_symbol = normalized_candidate_symbols[0]
    if normalized_primary_symbol is None and len(normalized_symbols) == 1:
      normalized_primary_symbol = normalized_symbols[0]
    if (
      normalized_primary_symbol is not None
      and normalized_primary_symbol not in normalized_candidate_symbols
    ):
      normalized_candidate_symbols = (
        normalized_primary_symbol,
        *tuple(
          symbol
          for symbol in normalized_candidate_symbols
          if symbol != normalized_primary_symbol
        ),
      )
    if not normalized_candidate_symbols and normalized_primary_symbol is not None:
      normalized_candidate_symbols = (normalized_primary_symbol,)
    if (
      normalized_primary_symbol is None
      and normalized_timeframe is None
      and not normalized_candidate_symbols
    ):
      return None

    candidate_count = len(normalized_candidate_symbols)
    resolved_policy = policy
    resolved_reason = reason
    if resolved_policy is None:
      if candidate_count > 1:
        resolved_policy = "explicit_symbol" if cls._normalize_operator_alert_symbol(primary_symbol) else "symbol_order"
      else:
        resolved_policy = "single_symbol_context"
    if resolved_reason is None:
      if candidate_count > 1:
        if cls._normalize_operator_alert_symbol(primary_symbol) is not None:
          resolved_reason = "Runtime context supplied the primary symbol for a multi-symbol alert."
        else:
          resolved_reason = "Primary focus follows the normalized alert symbol order."
      else:
        resolved_reason = "Alert context resolved to one market-data instrument."

    return OperatorAlertPrimaryFocus(
      symbol=normalized_primary_symbol,
      timeframe=normalized_timeframe,
      candidate_symbols=normalized_candidate_symbols,
      candidate_count=candidate_count,
      policy=resolved_policy,
      reason=resolved_reason,
    )
  @classmethod
  def _resolve_market_data_alert_primary_focus(
    cls,
    *,
    instruments: list[InstrumentStatus],
    timeframe: str,
    symbol_order: tuple[str, ...] | list[str] = (),
  ) -> OperatorAlertPrimaryFocus | None:
    if not instruments:
      return None
    normalized_order = cls._normalize_operator_alert_symbols(symbol_order)
    order_index = {symbol: index for index, symbol in enumerate(normalized_order)}
    ranked_candidates = sorted(
      instruments,
      key=lambda instrument: (
        -cls._score_operator_market_data_instrument(instrument),
        order_index.get(cls._symbol_from_instrument_id(instrument.instrument_id), float("inf")),
        cls._symbol_from_instrument_id(instrument.instrument_id),
      ),
    )
    candidate_symbols = tuple(
      cls._symbol_from_instrument_id(instrument.instrument_id)
      for instrument in ranked_candidates
    )
    primary_symbol = candidate_symbols[0] if candidate_symbols else None
    if len(candidate_symbols) <= 1:
      reason = "Alert context resolved to one market-data instrument."
    else:
      primary_instrument = ranked_candidates[0]
      second_instrument = ranked_candidates[1]
      primary_score = cls._score_operator_market_data_instrument(primary_instrument)
      second_score = cls._score_operator_market_data_instrument(second_instrument)
      if primary_score != second_score:
        reason = (
          f"Selected {primary_symbol} as the highest-risk market-data candidate from "
          f"{len(candidate_symbols)} symbols."
        )
      elif order_index.get(primary_symbol, float("inf")) != order_index.get(
        cls._symbol_from_instrument_id(second_instrument.instrument_id),
        float("inf"),
      ):
        reason = "Risk tied, so the live symbol order broke the tie."
      else:
        reason = "Risk and live order tied, so lexical ordering kept focus stable."
    return cls._build_operator_alert_primary_focus(
      primary_symbol=primary_symbol,
      symbols=normalized_order or candidate_symbols,
      candidate_symbols=candidate_symbols,
      timeframe=timeframe,
      policy="market_data_risk_order",
      reason=reason,
    )
  @classmethod
  def _build_operator_alert_market_context(
    cls,
    *,
    symbol: str | None = None,
    symbols: tuple[str, ...] | list[str] = (),
    timeframe: str | None = None,
    primary_focus: OperatorAlertPrimaryFocus | None = None,
  ) -> dict[str, str | tuple[str, ...] | OperatorAlertPrimaryFocus | None]:
    symbol_candidates = list(symbols)
    if symbol is not None:
      symbol_candidates.insert(0, symbol)
    normalized_symbols = cls._normalize_operator_alert_symbols(symbol_candidates)
    normalized_symbol = cls._normalize_operator_alert_symbol(symbol)
    if normalized_symbol is None and len(normalized_symbols) == 1:
      normalized_symbol = normalized_symbols[0]
    normalized_timeframe = cls._normalize_operator_alert_timeframe(timeframe)
    return {
      "symbol": normalized_symbol,
      "symbols": normalized_symbols,
      "timeframe": normalized_timeframe,
      "primary_focus": primary_focus or cls._build_operator_alert_primary_focus(
        primary_symbol=normalized_symbol,
        symbols=normalized_symbols,
        timeframe=normalized_timeframe,
      ),
    }
  @staticmethod
  def _serialize_operator_alert_primary_focus_payload(
    primary_focus: OperatorAlertPrimaryFocus | None,
  ) -> dict[str, Any] | None:
    if primary_focus is None:
      return None
    return {
      "symbol": primary_focus.symbol,
      "timeframe": primary_focus.timeframe,
      "candidate_symbols": list(primary_focus.candidate_symbols),
      "candidate_count": primary_focus.candidate_count,
      "policy": primary_focus.policy,
      "reason": primary_focus.reason,
    }
  @classmethod
  def _serialize_operator_alert_market_context_payload(
    cls,
    *,
    symbol: str | None = None,
    symbols: tuple[str, ...] | list[str] = (),
    timeframe: str | None = None,
    primary_focus: OperatorAlertPrimaryFocus | None = None,
  ) -> dict[str, Any]:
    market_context = cls._build_operator_alert_market_context(
      symbol=symbol,
      symbols=symbols,
      timeframe=timeframe,
      primary_focus=primary_focus,
    )
    return {
      "symbol": market_context["symbol"],
      "symbols": list(market_context["symbols"]),
      "timeframe": market_context["timeframe"],
      "primary_focus": cls._serialize_operator_alert_primary_focus_payload(
        market_context["primary_focus"]
      ),
    }
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
