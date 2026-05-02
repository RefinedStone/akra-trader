from __future__ import annotations

import json
import logging
from datetime import UTC
from datetime import datetime
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from akra_trader.domain.models import OperatorAlertPrimaryFocus
from akra_trader.domain.models import OperatorIncidentDelivery
from akra_trader.domain.models import OperatorIncidentEvent
from akra_trader.domain.models import OperatorIncidentProviderPullSync


LOGGER = logging.getLogger("akra_trader.operator_delivery")


class OperatorDeliveryMarketContextHelpersMixin:
  @staticmethod
  def _normalize_market_context_symbol(symbol: Any) -> str | None:
    if not isinstance(symbol, str):
      return None
    normalized = symbol.strip().upper()
    return normalized or None
  @classmethod
  def _normalize_market_context_symbols(cls, *candidates: Any) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
      if isinstance(candidate, str):
        resolved = cls._normalize_market_context_symbol(candidate)
        if resolved is not None and resolved not in seen:
          seen.add(resolved)
          normalized.append(resolved)
        continue
      if not isinstance(candidate, (list, tuple)):
        continue
      for item in candidate:
        resolved = cls._normalize_market_context_symbol(item)
        if resolved is None or resolved in seen:
          continue
        seen.add(resolved)
        normalized.append(resolved)
    return normalized
  @staticmethod
  def _normalize_market_context_timeframe(timeframe: Any) -> str | None:
    if not isinstance(timeframe, str):
      return None
    normalized = timeframe.strip().lower()
    return normalized or None
  @classmethod
  def _build_primary_focus_payload_from_sources(
    cls,
    *candidates: Any,
  ) -> dict[str, Any] | None:
    payload = cls._extract_mapping(*candidates)
    if not payload:
      return None
    symbol = cls._normalize_market_context_symbol(payload.get("symbol"))
    timeframe = cls._normalize_market_context_timeframe(payload.get("timeframe"))
    candidate_symbols = cls._normalize_market_context_symbols(
      payload.get("candidate_symbols"),
      payload.get("candidateSymbols"),
      payload.get("symbols"),
      payload.get("symbol"),
    )
    if symbol is not None and symbol not in candidate_symbols:
      candidate_symbols = [symbol, *[candidate for candidate in candidate_symbols if candidate != symbol]]
    if symbol is None and candidate_symbols:
      symbol = candidate_symbols[0]
    if not candidate_symbols and symbol is not None:
      candidate_symbols = [symbol]
    if symbol is None and timeframe is None and not candidate_symbols:
      return None
    return {
      "symbol": symbol,
      "timeframe": timeframe,
      "candidate_symbols": candidate_symbols,
      "candidate_count": (
        int(payload.get("candidate_count"))
        if isinstance(payload.get("candidate_count"), int)
        else len(candidate_symbols)
      ),
      "policy": (
        cls._first_non_empty_string(payload.get("policy"))
        or ("single_symbol_context" if len(candidate_symbols) <= 1 else "symbol_order")
      ),
      "reason": cls._first_non_empty_string(payload.get("reason")),
    }
  @classmethod
  def _build_primary_focus_payload_with_provenance_from_sources(
    cls,
    *candidates: tuple[Any, str | None, str | None],
  ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    for candidate, scope, path in candidates:
      payload = cls._build_primary_focus_payload_from_sources(candidate)
      if payload is None:
        continue
      return payload, cls._build_market_context_field_provenance_payload(
        scope=scope,
        path=path,
      )
    return None, None
  @staticmethod
  def _build_market_context_field_provenance_payload(
    *,
    scope: str | None,
    path: str | None,
  ) -> dict[str, Any] | None:
    if scope is None and path is None:
      return None
    return {
      "scope": scope,
      "path": path,
    }
  @staticmethod
  def _join_market_context_path(
    root: str | None,
    suffix: str,
  ) -> str | None:
    if not suffix:
      return root
    if root is None or not root.strip():
      return suffix
    return f"{root}.{suffix}"
  @classmethod
  def _resolve_provider_pull_market_context_root_path(
    cls,
    *,
    provider: str,
    source_scope: str,
  ) -> tuple[str | None, str | None]:
    normalized_provider = provider.strip().lower().replace(" ", "_")
    vendor_field = (
      cls._resolve_workflow_market_context_vendor_field(normalized_provider)
      if normalized_provider
      else None
    )
    if source_scope == "provider_payload":
      return vendor_field, vendor_field
    if source_scope == "provider_recovery":
      return vendor_field, (
        f"{vendor_field}.remediation_provider_recovery"
        if vendor_field is not None
        else "remediation_provider_recovery"
      )
    if source_scope == "remediation_payload":
      return vendor_field, (
        f"{vendor_field}.remediation_provider_payload"
        if vendor_field is not None
        else "remediation_provider_payload"
      )
    if source_scope == "targets":
      return None, "targets"
    if source_scope == "target":
      return None, "target"
    return vendor_field, None
  @classmethod
  def _extract_market_context_mapping_from_sources(
    cls,
    *candidates: Any,
  ) -> dict[str, Any]:
    for candidate in candidates:
      payload = cls._extract_mapping(candidate)
      if not payload:
        continue
      market_context = cls._extract_mapping(
        payload.get("market_context"),
        cls._extract_mapping(payload.get("custom_details")).get("market_context"),
        cls._extract_mapping(payload.get("details")).get("market_context"),
        cls._extract_mapping(payload.get("metadata")).get("market_context"),
      )
      if market_context:
        return market_context
    return {}
  @classmethod
  def _extract_provider_pull_market_context_mapping_with_scope(
    cls,
    *,
    remediation_payload: dict[str, Any],
    provider_payload: dict[str, Any],
    provider_recovery: dict[str, Any],
  ) -> tuple[dict[str, Any], str | None]:
    for scope, payload in (
      ("provider_recovery", provider_recovery),
      ("provider_payload", provider_payload),
      ("remediation_payload", remediation_payload),
    ):
      market_context = cls._extract_market_context_mapping_from_sources(payload)
      if market_context:
        return market_context, scope
    return {}, None
  @classmethod
  def _resolve_market_context_symbol_with_provenance(
    cls,
    *candidates: tuple[Any, str | None, str | None],
  ) -> tuple[str | None, dict[str, Any] | None]:
    for value, scope, path in candidates:
      normalized = cls._normalize_market_context_symbol(value)
      if normalized is None:
        continue
      return normalized, cls._build_market_context_field_provenance_payload(
        scope=scope,
        path=path,
      )
    return None, None
  @classmethod
  def _resolve_market_context_symbols_provenance(
    cls,
    *candidates: tuple[Any, str | None, str | None],
  ) -> dict[str, Any] | None:
    for value, scope, path in candidates:
      normalized = cls._normalize_market_context_symbols(value)
      if not normalized:
        continue
      return cls._build_market_context_field_provenance_payload(
        scope=scope,
        path=path,
      )
    return None
  @classmethod
  def _resolve_market_context_timeframe_with_provenance(
    cls,
    *candidates: tuple[Any, str | None, str | None],
  ) -> tuple[str | None, dict[str, Any] | None]:
    for value, scope, path in candidates:
      normalized = cls._normalize_market_context_timeframe(value)
      if normalized is None:
        continue
      return normalized, cls._build_market_context_field_provenance_payload(
        scope=scope,
        path=path,
      )
    return None, None
  @classmethod
  def _build_provider_pull_market_context_payload(
    cls,
    *,
    provider: str,
    remediation_payload: dict[str, Any],
    provider_payload: dict[str, Any],
    provider_recovery: dict[str, Any],
  ) -> dict[str, Any]:
    vendor_market_context, vendor_market_context_scope = (
      cls._extract_provider_pull_market_context_mapping_with_scope(
        remediation_payload=remediation_payload,
        provider_payload=provider_payload,
        provider_recovery=provider_recovery,
      )
    )
    normalized_provider = provider.strip().lower().replace(" ", "_") or None
    vendor_field, provider_recovery_root = cls._resolve_provider_pull_market_context_root_path(
      provider=provider,
      source_scope="provider_recovery",
    )
    _, provider_payload_root = cls._resolve_provider_pull_market_context_root_path(
      provider=provider,
      source_scope="provider_payload",
    )
    _, remediation_payload_root = cls._resolve_provider_pull_market_context_root_path(
      provider=provider,
      source_scope="remediation_payload",
    )
    vendor_market_context_root = (
      cls._join_market_context_path(
        cls._resolve_provider_pull_market_context_root_path(
          provider=provider,
          source_scope=vendor_market_context_scope or "",
        )[1],
        "market_context",
      )
      if vendor_market_context_scope is not None
      else None
    )
    targets_payload = cls._extract_mapping(
      remediation_payload.get("targets"),
      provider_payload.get("targets"),
      provider_recovery.get("targets"),
    )
    target_payload = cls._extract_mapping(
      remediation_payload.get("target"),
      provider_payload.get("target"),
      provider_recovery.get("target"),
    )
    primary_focus, primary_focus_provenance = cls._build_primary_focus_payload_with_provenance_from_sources(
      (
        provider_recovery.get("primary_focus"),
        "provider_recovery",
        cls._join_market_context_path(provider_recovery_root, "primary_focus"),
      ),
      (
        provider_payload.get("primary_focus"),
        "provider_payload",
        cls._join_market_context_path(provider_payload_root, "primary_focus"),
      ),
      (
        vendor_market_context.get("primary_focus"),
        vendor_market_context_scope,
        cls._join_market_context_path(vendor_market_context_root, "primary_focus"),
      ),
      (
        targets_payload.get("primary_focus"),
        "targets",
        "targets.primary_focus",
      ),
      (
        target_payload.get("primary_focus"),
        "target",
        "target.primary_focus",
      ),
    )
    symbols = cls._normalize_market_context_symbols(
      provider_recovery.get("symbols"),
      provider_recovery.get("symbol"),
      provider_payload.get("symbols"),
      provider_payload.get("symbol"),
      vendor_market_context.get("symbols"),
      vendor_market_context.get("symbol"),
      remediation_payload.get("symbols"),
      remediation_payload.get("symbol"),
      targets_payload.get("symbols"),
      targets_payload.get("symbol"),
      target_payload.get("symbols"),
      target_payload.get("symbol"),
      primary_focus.get("candidate_symbols") if primary_focus is not None else (),
      primary_focus.get("symbol") if primary_focus is not None else None,
    )
    symbols_provenance = cls._resolve_market_context_symbols_provenance(
      (
        provider_recovery.get("symbols"),
        "provider_recovery",
        cls._join_market_context_path(provider_recovery_root, "symbols"),
      ),
      (
        provider_recovery.get("symbol"),
        "provider_recovery",
        cls._join_market_context_path(provider_recovery_root, "symbol"),
      ),
      (
        provider_payload.get("symbols"),
        "provider_payload",
        cls._join_market_context_path(provider_payload_root, "symbols"),
      ),
      (
        provider_payload.get("symbol"),
        "provider_payload",
        cls._join_market_context_path(provider_payload_root, "symbol"),
      ),
      (
        vendor_market_context.get("symbols"),
        vendor_market_context_scope,
        cls._join_market_context_path(vendor_market_context_root, "symbols"),
      ),
      (
        vendor_market_context.get("symbol"),
        vendor_market_context_scope,
        cls._join_market_context_path(vendor_market_context_root, "symbol"),
      ),
      (
        remediation_payload.get("symbols"),
        "remediation_payload",
        cls._join_market_context_path(remediation_payload_root, "symbols"),
      ),
      (
        remediation_payload.get("symbol"),
        "remediation_payload",
        cls._join_market_context_path(remediation_payload_root, "symbol"),
      ),
      (
        targets_payload.get("symbols"),
        "targets",
        "targets.symbols",
      ),
      (
        targets_payload.get("symbol"),
        "targets",
        "targets.symbol",
      ),
      (
        target_payload.get("symbols"),
        "target",
        "target.symbols",
      ),
      (
        target_payload.get("symbol"),
        "target",
        "target.symbol",
      ),
      (
        primary_focus.get("candidate_symbols") if primary_focus is not None else (),
        primary_focus_provenance.get("scope") if primary_focus_provenance is not None else None,
        (
          cls._join_market_context_path(primary_focus_provenance.get("path"), "candidate_symbols")
          if primary_focus_provenance is not None
          else None
        ),
      ),
      (
        primary_focus.get("symbol") if primary_focus is not None else None,
        primary_focus_provenance.get("scope") if primary_focus_provenance is not None else None,
        (
          cls._join_market_context_path(primary_focus_provenance.get("path"), "symbol")
          if primary_focus_provenance is not None
          else None
        ),
      ),
    )
    symbol, symbol_provenance = cls._resolve_market_context_symbol_with_provenance(
      (
        provider_recovery.get("symbol"),
        "provider_recovery",
        cls._join_market_context_path(provider_recovery_root, "symbol"),
      ),
      (
        provider_payload.get("symbol"),
        "provider_payload",
        cls._join_market_context_path(provider_payload_root, "symbol"),
      ),
      (
        vendor_market_context.get("symbol"),
        vendor_market_context_scope,
        cls._join_market_context_path(vendor_market_context_root, "symbol"),
      ),
      (
        remediation_payload.get("symbol"),
        "remediation_payload",
        cls._join_market_context_path(remediation_payload_root, "symbol"),
      ),
      (
        targets_payload.get("symbol"),
        "targets",
        "targets.symbol",
      ),
      (
        target_payload.get("symbol"),
        "target",
        "target.symbol",
      ),
      (
        primary_focus.get("symbol") if primary_focus is not None else None,
        primary_focus_provenance.get("scope") if primary_focus_provenance is not None else None,
        (
          cls._join_market_context_path(primary_focus_provenance.get("path"), "symbol")
          if primary_focus_provenance is not None
          else None
        ),
      ),
    )
    if symbol is None and len(symbols) == 1:
      symbol = symbols[0]
      symbol_provenance = symbol_provenance or symbols_provenance
    timeframe, timeframe_provenance = cls._resolve_market_context_timeframe_with_provenance(
      (
        provider_recovery.get("timeframe"),
        "provider_recovery",
        cls._join_market_context_path(provider_recovery_root, "timeframe"),
      ),
      (
        provider_payload.get("timeframe"),
        "provider_payload",
        cls._join_market_context_path(provider_payload_root, "timeframe"),
      ),
      (
        provider_payload.get("target_timeframe"),
        "provider_payload",
        cls._join_market_context_path(provider_payload_root, "target_timeframe"),
      ),
      (
        vendor_market_context.get("timeframe"),
        vendor_market_context_scope,
        cls._join_market_context_path(vendor_market_context_root, "timeframe"),
      ),
      (
        remediation_payload.get("timeframe"),
        "remediation_payload",
        cls._join_market_context_path(remediation_payload_root, "timeframe"),
      ),
      (
        remediation_payload.get("target_timeframe"),
        "remediation_payload",
        cls._join_market_context_path(remediation_payload_root, "target_timeframe"),
      ),
      (
        targets_payload.get("timeframe"),
        "targets",
        "targets.timeframe",
      ),
      (
        target_payload.get("timeframe"),
        "target",
        "target.timeframe",
      ),
      (
        primary_focus.get("timeframe") if primary_focus is not None else None,
        primary_focus_provenance.get("scope") if primary_focus_provenance is not None else None,
        (
          cls._join_market_context_path(primary_focus_provenance.get("path"), "timeframe")
          if primary_focus_provenance is not None
          else None
        ),
      ),
    )
    if primary_focus is None and (symbol is not None or timeframe is not None or symbols):
      primary_focus = cls._build_primary_focus_payload_from_sources(
        {
          "symbol": symbol,
          "timeframe": timeframe,
          "candidate_symbols": symbols,
        }
      )
    market_context_provenance = None
    if any(
      provenance is not None
      for provenance in (
        symbol_provenance,
        symbols_provenance,
        timeframe_provenance,
        primary_focus_provenance,
      )
    ):
      market_context_provenance = {
        "provider": normalized_provider,
        "vendor_field": vendor_field,
        "symbol": symbol_provenance,
        "symbols": symbols_provenance,
        "timeframe": timeframe_provenance,
        "primary_focus": primary_focus_provenance,
      }
    return {
      "symbol": symbol,
      "symbols": symbols,
      "timeframe": timeframe,
      "primary_focus": primary_focus,
      "market_context_provenance": market_context_provenance,
    }
  @staticmethod
  def _build_primary_focus_payload(
    primary_focus: OperatorAlertPrimaryFocus | None,
  ) -> dict[str, Any] | None:
    if primary_focus is None:
      return None
    return {
      "symbol": primary_focus.symbol,
      "timeframe": primary_focus.timeframe,
      "candidate_symbols": primary_focus.candidate_symbols,
      "candidate_count": primary_focus.candidate_count,
      "policy": primary_focus.policy,
      "reason": primary_focus.reason,
    }
  @classmethod
  def _build_incident_market_context_payload(
    cls,
    incident: OperatorIncidentEvent,
  ) -> dict[str, Any]:
    provider_recovery = incident.remediation.provider_recovery
    candidate_symbols = (
      incident.symbols
      or (
        incident.primary_focus.candidate_symbols
        if incident.primary_focus is not None
        else ()
      )
      or provider_recovery.symbols
      or (
        provider_recovery.primary_focus.candidate_symbols
        if provider_recovery.primary_focus is not None
        else ()
      )
    )
    symbol = incident.symbol or (
      incident.primary_focus.symbol
      if incident.primary_focus is not None
      else None
    ) or (
      provider_recovery.primary_focus.symbol
      if provider_recovery.primary_focus is not None
      else None
    )
    if symbol is None and len(candidate_symbols) == 1:
      symbol = candidate_symbols[0]
    timeframe = incident.timeframe or (
      incident.primary_focus.timeframe
      if incident.primary_focus is not None
      else None
    ) or (
      provider_recovery.primary_focus.timeframe
      if provider_recovery.primary_focus is not None
      else provider_recovery.timeframe
    )
    return {
      "symbol": symbol,
      "symbols": candidate_symbols,
      "timeframe": timeframe,
      "primary_focus": cls._build_primary_focus_payload(
        incident.primary_focus or provider_recovery.primary_focus
      ),
    }
  @classmethod
  def _build_generic_webhook_payload(cls, *, incident: OperatorIncidentEvent) -> bytes:
    market_context = cls._build_incident_market_context_payload(incident)
    return json.dumps(
      {
        "event_id": incident.event_id,
        "alert_id": incident.alert_id,
        "kind": incident.kind,
        "timestamp": incident.timestamp.isoformat(),
        "severity": incident.severity,
        "summary": incident.summary,
        "detail": incident.detail,
        "run_id": incident.run_id,
        "session_id": incident.session_id,
        "source": incident.source,
        **market_context,
        "remediation": {
          "state": incident.remediation.state,
          "kind": incident.remediation.kind,
          "owner": incident.remediation.owner,
          "summary": incident.remediation.summary,
          "detail": incident.remediation.detail,
          "runbook": incident.remediation.runbook,
          "provider": incident.remediation.provider,
          "reference": incident.remediation.reference,
          "provider_payload": incident.remediation.provider_payload,
          "provider_payload_updated_at": (
            incident.remediation.provider_payload_updated_at.isoformat()
            if incident.remediation.provider_payload_updated_at is not None
            else None
          ),
          "provider_recovery": cls._build_provider_recovery_payload(incident),
        },
      }
    ).encode("utf-8")
  @staticmethod
  def _build_slack_payload(*, incident: OperatorIncidentEvent) -> bytes:
    return json.dumps(
      {
        "text": f"[{incident.severity.upper()}] {incident.summary}",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": (
                f"*{incident.summary}*\n"
                f"{incident.detail}\n"
                f"`{incident.kind}` • `{incident.alert_id}` • `{incident.source}`"
                + (
                  f"\nRemediation: {incident.remediation.summary} "
                  f"(`{incident.remediation.runbook or 'n/a'}`)"
                  if incident.remediation.state != "not_applicable" and incident.remediation.summary
                  else ""
                )
              ),
            },
          }
        ],
      }
    ).encode("utf-8")
