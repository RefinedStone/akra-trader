from __future__ import annotations

from typing import Any

from akra_trader.domain.models import (
  OperatorAlertMarketContextFieldProvenance,
  OperatorAlertMarketContextProvenance,
  OperatorAlertPrimaryFocus,
)


def _extract_operator_alert_market_context_from_workflow_payload(
  app: Any,
  *,
  payload: dict[str, Any],
  existing_symbol: str | None = None,
  existing_symbols: tuple[str, ...] = (),
  existing_timeframe: str | None = None,
  existing_primary_focus: OperatorAlertPrimaryFocus | None = None,
) -> dict[str, str | tuple[str, ...] | OperatorAlertPrimaryFocus | None]:
  market_context_payload = app._extract_payload_mapping(payload.get("market_context"))
  verification_payload = app._extract_payload_mapping(payload.get("verification"))
  target_payload = app._extract_payload_mapping(payload.get("target"))
  targets_payload = app._extract_payload_mapping(payload.get("targets"))
  provider_recovery_payload = app._merge_payload_mappings(
    payload.get("remediation_provider_recovery"),
    payload.get("provider_recovery"),
    payload.get("recovery"),
  )
  primary_focus_payload = app._merge_payload_mappings(
    market_context_payload.get("primary_focus"),
    payload.get("primary_focus"),
    targets_payload.get("primary_focus"),
    target_payload.get("primary_focus"),
    provider_recovery_payload.get("primary_focus"),
  )
  symbols = app._extract_string_tuple(
    market_context_payload.get("symbols"),
    market_context_payload.get("symbol"),
    payload.get("symbols"),
    payload.get("symbol"),
    targets_payload.get("symbols"),
    targets_payload.get("symbol"),
    target_payload.get("symbols"),
    target_payload.get("symbol"),
    provider_recovery_payload.get("symbols"),
    provider_recovery_payload.get("symbol"),
    primary_focus_payload.get("candidate_symbols"),
    primary_focus_payload.get("candidateSymbols"),
    primary_focus_payload.get("symbols"),
    primary_focus_payload.get("symbol"),
    existing_primary_focus.candidate_symbols if existing_primary_focus is not None else (),
    existing_primary_focus.symbol if existing_primary_focus is not None else None,
    existing_symbols,
    existing_symbol,
  )
  candidate_symbols = app._extract_string_tuple(
    primary_focus_payload.get("candidate_symbols"),
    primary_focus_payload.get("candidateSymbols"),
    primary_focus_payload.get("symbols"),
    primary_focus_payload.get("symbol"),
    symbols,
    existing_primary_focus.candidate_symbols if existing_primary_focus is not None else (),
  )
  primary_focus = app._build_operator_alert_primary_focus(
    primary_symbol=app._first_non_empty_string(
      primary_focus_payload.get("symbol"),
      market_context_payload.get("symbol"),
      payload.get("symbol"),
      targets_payload.get("symbol"),
      target_payload.get("symbol"),
      provider_recovery_payload.get("symbol"),
      existing_primary_focus.symbol if existing_primary_focus is not None else None,
      existing_symbol,
    ),
    symbols=symbols,
    candidate_symbols=candidate_symbols,
    timeframe=app._first_non_empty_string(
      primary_focus_payload.get("timeframe"),
      market_context_payload.get("timeframe"),
      payload.get("timeframe"),
      payload.get("target_timeframe"),
      targets_payload.get("timeframe"),
      target_payload.get("timeframe"),
      provider_recovery_payload.get("timeframe"),
      verification_payload.get("timeframe"),
      existing_primary_focus.timeframe if existing_primary_focus is not None else None,
      existing_timeframe,
    ),
    policy=app._first_non_empty_string(
      primary_focus_payload.get("policy"),
    ),
    reason=app._first_non_empty_string(
      primary_focus_payload.get("reason"),
    ),
  )
  return app._build_operator_alert_market_context(
    symbol=app._first_non_empty_string(
      market_context_payload.get("symbol"),
      payload.get("symbol"),
      targets_payload.get("symbol"),
      target_payload.get("symbol"),
      provider_recovery_payload.get("symbol"),
      primary_focus.symbol if primary_focus is not None else None,
      existing_symbol,
    ),
    symbols=symbols,
    timeframe=app._first_non_empty_string(
      market_context_payload.get("timeframe"),
      payload.get("timeframe"),
      payload.get("target_timeframe"),
      targets_payload.get("timeframe"),
      target_payload.get("timeframe"),
      provider_recovery_payload.get("timeframe"),
      verification_payload.get("timeframe"),
      primary_focus.timeframe if primary_focus is not None else None,
      existing_timeframe,
    ),
    primary_focus=primary_focus or existing_primary_focus,
  )


def _build_market_context_field_provenance(
  app: Any,
  value: Any,
) -> OperatorAlertMarketContextFieldProvenance | None:
  mapping = app._extract_payload_mapping(value)
  scope = app._first_non_empty_string(mapping.get("scope"))
  path = app._first_non_empty_string(mapping.get("path"))
  if scope is None and path is None:
    return None
  return OperatorAlertMarketContextFieldProvenance(
    scope=scope,
    path=path,
  )


def _extract_operator_alert_market_context_provenance_from_workflow_payload(
  app: Any,
  *,
  payload: dict[str, Any],
  existing: OperatorAlertMarketContextProvenance | None = None,
) -> OperatorAlertMarketContextProvenance | None:
  provider_recovery_payload = app._merge_payload_mappings(
    payload.get("remediation_provider_recovery"),
    payload.get("provider_recovery"),
    payload.get("recovery"),
  )
  provenance_payload = app._merge_payload_mappings(
    payload.get("market_context_provenance"),
    provider_recovery_payload.get("market_context_provenance"),
  )
  if not provenance_payload:
    return existing

  field_provenance = {
    "symbol": _build_market_context_field_provenance(app, provenance_payload.get("symbol")),
    "symbols": _build_market_context_field_provenance(app, provenance_payload.get("symbols")),
    "timeframe": _build_market_context_field_provenance(app, provenance_payload.get("timeframe")),
    "primary_focus": _build_market_context_field_provenance(app, provenance_payload.get("primary_focus")),
  }
  if (
    app._first_non_empty_string(
      provenance_payload.get("provider"),
      existing.provider if existing is not None else None,
    ) is None
    and app._first_non_empty_string(
      provenance_payload.get("vendor_field"),
      existing.vendor_field if existing is not None else None,
    ) is None
    and all(value is None for value in field_provenance.values())
  ):
    return existing
  return OperatorAlertMarketContextProvenance(
    provider=app._first_non_empty_string(
      provenance_payload.get("provider"),
      existing.provider if existing is not None else None,
    ),
    vendor_field=app._first_non_empty_string(
      provenance_payload.get("vendor_field"),
      existing.vendor_field if existing is not None else None,
    ),
    symbol=field_provenance["symbol"] or (existing.symbol if existing is not None else None),
    symbols=field_provenance["symbols"] or (existing.symbols if existing is not None else None),
    timeframe=field_provenance["timeframe"] or (existing.timeframe if existing is not None else None),
    primary_focus=(
      field_provenance["primary_focus"]
      or (existing.primary_focus if existing is not None else None)
    ),
  )
