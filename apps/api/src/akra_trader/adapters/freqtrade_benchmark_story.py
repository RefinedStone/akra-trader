from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from io import BytesIO
import json
from pathlib import Path
import os
import re
import shutil
import subprocess
from typing import Any
from zipfile import BadZipFile
from zipfile import ZipFile

from akra_trader.adapters.references import ReferenceCatalog
from akra_trader.domain.models import BENCHMARK_ARTIFACT_RUNTIME_CANDIDATE_ID_METADATA_KEY
from akra_trader.domain.models import BenchmarkArtifact
from akra_trader.domain.models import extract_benchmark_artifact_runtime_candidate_id
from akra_trader.domain.models import is_benchmark_artifact_metadata_key
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import ReferenceSource
from akra_trader.domain.models import RunConfig
from akra_trader.domain.models import RunRecord
from akra_trader.domain.models import RunStatus
from akra_trader.domain.models import StrategyMetadata



class FreqtradeBenchmarkStoryMixin:
  def _build_benchmark_story(
    self,
    summary: dict[str, Any],
    sections: dict[str, Any],
  ) -> dict[str, Any]:
    story: dict[str, Any] = {}
    for key, value in (
      ("headline", self._describe_benchmark_headline(summary)),
      ("market_context", self._describe_market_context(sections.get("zip_market_change"))),
      (
        "portfolio_context",
        self._describe_portfolio_context(
          sections.get("zip_wallet_exports"),
        ),
      ),
      ("signal_context", self._describe_signal_context(sections.get("zip_signal_exports"))),
      ("rejection_context", self._describe_rejection_context(sections.get("zip_rejected_exports"))),
      (
        "exit_context",
        self._describe_exit_context(
          sections.get("zip_exited_exports"),
          sections.get("exit_reason_metrics"),
        ),
      ),
      (
        "pair_context",
        self._describe_pair_context(
          sections.get("pair_metrics"),
          sections.get("pair_extremes"),
        ),
      ),
    ):
      self._set_summary_entry(story, key, value)
    return story

  def _describe_benchmark_headline(self, summary: dict[str, Any]) -> str | None:
    strategy_name = summary.get("strategy_name")
    profit_total_pct = self._format_pct_text(summary.get("profit_total_pct"))
    trade_count = self._format_count_phrase(summary.get("trade_count"), "trade")
    max_drawdown_pct = self._format_pct_text(summary.get("max_drawdown_pct"))
    market_change_pct = self._format_pct_text(summary.get("market_change_pct"))

    if strategy_name is None and profit_total_pct is None and trade_count is None:
      return None

    subject = str(strategy_name) if strategy_name is not None else "Benchmark run"
    sentence = subject
    if profit_total_pct is not None:
      sentence += f" returned {profit_total_pct}"
    if trade_count is not None:
      connector = " across " if profit_total_pct is not None else " recorded "
      sentence += f"{connector}{trade_count}"
    if max_drawdown_pct is not None:
      connector = " with " if profit_total_pct is not None or trade_count is not None else " had "
      sentence += f"{connector}{max_drawdown_pct} max drawdown"
    if market_change_pct is not None:
      connector = " against " if profit_total_pct is not None or trade_count is not None else " with "
      sentence += f"{connector}a {market_change_pct} market move"
    return sentence + "."

  def _describe_market_context(self, market_section: Any) -> str | None:
    if not isinstance(market_section, dict):
      return None
    pair_count = self._coerce_count(market_section.get("pair_count"))
    if pair_count is None:
      return None

    positive_pair_count = self._coerce_count(market_section.get("positive_pair_count"))
    negative_pair_count = self._coerce_count(market_section.get("negative_pair_count"))
    if positive_pair_count == pair_count:
      opening = f"Breadth stayed positive across {pair_count} tracked pairs"
    elif negative_pair_count == pair_count:
      opening = f"Breadth stayed negative across {pair_count} tracked pairs"
    elif positive_pair_count is not None and negative_pair_count is not None:
      opening = (
        f"Breadth was mixed across {pair_count} tracked pairs "
        f"({positive_pair_count} positive / {negative_pair_count} negative)"
      )
    else:
      opening = f"Tracked market breadth covered {pair_count} pairs"

    best_pair = market_section.get("best_pair")
    best_pair_change_pct = self._format_signed_pct_text(market_section.get("best_pair_change_pct"))
    worst_pair = market_section.get("worst_pair")
    worst_pair_change_pct = self._format_signed_pct_text(market_section.get("worst_pair_change_pct"))
    if best_pair is None or best_pair_change_pct is None:
      return opening + "."
    if worst_pair is None or worst_pair_change_pct is None:
      return f"{opening}; {best_pair} led at {best_pair_change_pct}."
    return (
      f"{opening}; {best_pair} led at {best_pair_change_pct} "
      f"while {worst_pair} lagged at {worst_pair_change_pct}."
    )

  def _describe_portfolio_context(self, wallet_section: Any) -> str | None:
    if not isinstance(wallet_section, dict):
      return None
    start_value = self._coerce_float(wallet_section.get("total_quote_start"))
    end_value = self._coerce_float(wallet_section.get("total_quote_end"))
    high_value = self._format_number_text(wallet_section.get("total_quote_high"))
    low_value = self._format_number_text(wallet_section.get("total_quote_low"))
    if start_value is None or end_value is None:
      return None

    start_text = self._format_number_text(start_value)
    end_text = self._format_number_text(end_value)
    if start_text is None or end_text is None:
      return None

    if end_value > start_value:
      sentence = f"Wallet quote value rose from {start_text} to {end_text}"
    elif end_value < start_value:
      sentence = f"Wallet quote value fell from {start_text} to {end_text}"
    else:
      sentence = f"Wallet quote value held flat at {start_text}"
    if low_value is not None and high_value is not None:
      sentence += f", ranging between {low_value} and {high_value}"

    currency_preview = wallet_section.get("currency_quote_preview")
    if isinstance(currency_preview, list) and currency_preview:
      leading_currency = currency_preview[0]
      if isinstance(leading_currency, dict):
        currency = leading_currency.get("currency")
        latest_quote_value = self._format_number_text(leading_currency.get("latest_quote_value"))
        if currency is not None and latest_quote_value is not None:
          sentence += f"; {currency} finished as the largest tracked balance at {latest_quote_value}"
    return sentence + "."

  def _describe_signal_context(self, signal_section: Any) -> str | None:
    if not isinstance(signal_section, dict):
      return None
    row_count = self._format_count_phrase(signal_section.get("row_count"), "row")
    if row_count is None:
      return None
    pair_count = self._format_count_phrase(signal_section.get("pair_count"), "pair")
    sentence = f"Signal exports captured {row_count}"
    if pair_count is not None:
      sentence += f" across {pair_count}"

    details: list[str] = []
    dominant_tag = self._first_ranked_section_entry(signal_section.get("enter_tag_counts"))
    if dominant_tag is not None:
      details.append(
        f"{dominant_tag['label']} was the dominant entry tag ({dominant_tag['count']})"
      )
    dominant_pair = self._first_ranked_section_entry(
      signal_section.get("pair_row_preview"),
      label_key="pair",
    )
    if dominant_pair is not None:
      details.append(
        f"{dominant_pair['label']} generated the most rows ({dominant_pair['count']})"
      )
    if details:
      sentence += "; " + " and ".join(details)
    return sentence + "."

  def _describe_rejection_context(self, rejection_section: Any) -> str | None:
    if not isinstance(rejection_section, dict):
      return None
    row_count = self._coerce_count(rejection_section.get("row_count"))
    if row_count is None:
      return None
    leading_reason = self._first_ranked_section_entry(rejection_section.get("reason_counts"))
    if row_count == 0:
      return "Rejected entries were not captured in the embedded export."
    if leading_reason is None:
      return f"Rejected entries accounted for {row_count} rows."
    if row_count == 1:
      return f"Rejected entries were limited to 1 row, entirely driven by {leading_reason['label']}."
    return (
      f"Rejected entries accounted for {row_count} rows, led by "
      f"{leading_reason['label']} ({leading_reason['count']})."
    )

  def _describe_exit_context(
    self,
    exit_section: Any,
    exit_reason_metrics: Any,
  ) -> str | None:
    if not isinstance(exit_section, dict):
      return None
    row_count = self._coerce_count(exit_section.get("row_count"))
    leading_exit = self._first_ranked_section_entry(exit_section.get("exit_reason_counts"))
    if row_count is None or leading_exit is None:
      return None

    sentence = (
      f"Exit exports were dominated by {leading_exit['label']} "
      f"({self._format_count_phrase(leading_exit['count'], 'row')})."
    )
    if isinstance(exit_reason_metrics, dict):
      preview_rows = exit_reason_metrics.get("preview")
      if isinstance(preview_rows, list):
        matching_row = next(
          (
            row
            for row in preview_rows
            if isinstance(row, dict) and row.get("label") == leading_exit["label"]
          ),
          None,
        )
        if isinstance(matching_row, dict):
          trade_count = self._format_count_phrase(matching_row.get("trade_count"), "trade")
          profit_total_pct = self._format_pct_text(matching_row.get("profit_total_pct"))
          if trade_count is not None and profit_total_pct is not None:
            sentence = (
              sentence[:-1]
              + f", matching the benchmark summary where {leading_exit['label']} "
              f"closed {trade_count} for {profit_total_pct}."
            )
    return sentence

  def _describe_pair_context(
    self,
    pair_metrics: Any,
    pair_extremes: Any,
  ) -> str | None:
    best_label: str | None = None
    total_trade_count: str | None = None
    total_return: str | None = None

    if isinstance(pair_metrics, dict):
      best_row = pair_metrics.get("best")
      if isinstance(best_row, dict) and isinstance(best_row.get("label"), str):
        best_label = best_row["label"]
      total_row = pair_metrics.get("total")
      if isinstance(total_row, dict):
        total_trade_count = self._format_count_phrase(total_row.get("trade_count"), "trade")
        total_return = self._format_pct_text(total_row.get("profit_total_pct"))

    if best_label is None and isinstance(pair_extremes, dict):
      best_row = pair_extremes.get("best")
      if isinstance(best_row, dict) and isinstance(best_row.get("label"), str):
        best_label = best_row["label"]

    if best_label is None and total_trade_count is None and total_return is None:
      return None

    opening = (
      f"Pair metrics stayed concentrated in {best_label}"
      if best_label is not None
      else "Pair metrics remained available in the embedded result tables"
    )
    details: list[str] = []
    if total_trade_count is not None:
      details.append(f"the aggregate row logged {total_trade_count}")
    if total_return is not None:
      details.append(f"{total_return} total return")
    if not details:
      return opening + "."
    if len(details) == 1:
      return f"{opening}; {details[0]}."
    return f"{opening}; {details[0]} and {details[1]}."

  @staticmethod
  def _first_ranked_section_entry(
    value: Any,
    *,
    label_key: str = "label",
  ) -> dict[str, Any] | None:
    if not isinstance(value, list) or not value:
      return None
    entry = value[0]
    if not isinstance(entry, dict):
      return None
    label = entry.get(label_key)
    count = FreqtradeReferenceAdapter._coerce_count(entry.get("count"))
    if not isinstance(label, str) or count is None:
      return None
    return {
      "label": label,
      "count": count,
    }

  @staticmethod
  def _format_number_text(value: Any) -> str | None:
    number = FreqtradeReferenceAdapter._coerce_float(value)
    if number is None:
      return None
    rounded = round(number, 4)
    if float(rounded).is_integer():
      return str(int(rounded))
    return f"{rounded:.4f}".rstrip("0").rstrip(".")

  @staticmethod
  def _format_pct_text(value: Any) -> str | None:
    number_text = FreqtradeReferenceAdapter._format_number_text(value)
    if number_text is None:
      return None
    return f"{number_text}%"

  @staticmethod
  def _format_signed_pct_text(value: Any) -> str | None:
    number = FreqtradeReferenceAdapter._coerce_float(value)
    if number is None:
      return None
    pct_text = FreqtradeReferenceAdapter._format_pct_text(number)
    if pct_text is None:
      return None
    if number > 0:
      return f"+{pct_text}"
    return pct_text

  @staticmethod
  def _format_count_phrase(value: Any, singular: str) -> str | None:
    count = FreqtradeReferenceAdapter._coerce_count(value)
    if count is None:
      return None
    suffix = singular if count == 1 else f"{singular}s"
    return f"{count} {suffix}"

  def _summarize_metric_row(self, row: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    runtime_candidate_id = extract_benchmark_artifact_runtime_candidate_id(row)
    if runtime_candidate_id is not None:
      summary[BENCHMARK_ARTIFACT_RUNTIME_CANDIDATE_ID_METADATA_KEY] = runtime_candidate_id
    self._set_summary_entry(
      summary,
      "label",
      row.get("key") or row.get("date") or row.get("strategy_name") or row.get("name"),
    )
    self._set_summary_entry(summary, "date", row.get("date"))
    self._set_summary_entry(
      summary,
      "trade_count",
      row.get("trades") if row.get("trades") is not None else row.get("trade_count"),
    )
    self._set_summary_entry(
      summary,
      "profit_total_pct",
      self._lookup_pct_value(
        [row],
        pct_keys=("profit_total_pct", "profit_mean_pct"),
        ratio_keys=("profit_total", "profit_mean"),
      ),
    )
    self._set_summary_entry(summary, "profit_total_abs", row.get("profit_total_abs") or row.get("profit_abs"))
    self._set_summary_entry(
      summary,
      "win_rate_pct",
      self._lookup_pct_value(
        [row],
        pct_keys=("win_rate_pct",),
        ratio_keys=("winrate",),
      ),
    )
    self._set_summary_entry(
      summary,
      "max_drawdown_pct",
      self._lookup_pct_value(
        [row],
        pct_keys=("max_drawdown_pct",),
        ratio_keys=("max_drawdown_account",),
      ),
    )
    self._set_summary_entry(summary, "duration", row.get("duration_avg"))
    return summary

  def _select_best_and_worst_rows(
    self,
    rows: list[dict[str, Any]],
  ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    comparable_rows = [
      row for row in rows
      if self._coerce_float(row.get("profit_total_abs")) is not None
    ]
    if not comparable_rows:
      return None, None
    best_row = max(comparable_rows, key=lambda row: self._coerce_float(row.get("profit_total_abs")) or 0.0)
    worst_row = min(comparable_rows, key=lambda row: self._coerce_float(row.get("profit_total_abs")) or 0.0)
    return best_row, worst_row

  @staticmethod
  def _select_strategy_name(payload: dict[str, Any]) -> str | None:
    strategy = payload.get("strategy")
    if isinstance(strategy, str):
      return strategy
    if isinstance(strategy, dict):
      nested_name = next(
        (
          name
          for name, details in strategy.items()
          if isinstance(name, str) and isinstance(details, dict)
        ),
        None,
      )
      if nested_name is not None:
        return nested_name
    metadata = payload.get("metadata")
    if isinstance(metadata, dict):
      metadata_name = next(
        (
          name
          for name, details in metadata.items()
          if isinstance(name, str) and isinstance(details, dict)
        ),
        None,
      )
      if metadata_name is not None:
        return metadata_name
    strategy_comparison = payload.get("strategy_comparison")
    if isinstance(strategy_comparison, list):
      comparison_name = next(
        (
          row.get("key")
          for row in strategy_comparison
          if isinstance(row, dict) and isinstance(row.get("key"), str)
        ),
        None,
      )
      if isinstance(comparison_name, str):
        return comparison_name
    return None

  @staticmethod
  def _select_nested_strategy_payload(payload: Any, strategy_name: str | None) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
      return None
    if strategy_name is not None and isinstance(payload.get(strategy_name), dict):
      return payload[strategy_name]
    nested_payload = next(
      (
        value
        for value in payload.values()
        if isinstance(value, dict)
      ),
      None,
    )
    if isinstance(nested_payload, dict):
      return nested_payload
    return payload

  @staticmethod
  def _select_comparison_entry(rows: Any, strategy_name: str | None) -> dict[str, Any] | None:
    if not isinstance(rows, list):
      return None
    dict_rows = [row for row in rows if isinstance(row, dict)]
    if not dict_rows:
      return None
    if strategy_name is not None:
      matched_row = next(
        (
          row for row in dict_rows
          if row.get("key") == strategy_name or row.get("strategy_name") == strategy_name
        ),
        None,
      )
      if matched_row is not None:
        return matched_row
    return dict_rows[0]

  @staticmethod
  def _extract_strategy_name(
    payload: dict[str, Any],
    candidates: list[dict[str, Any]],
  ) -> str | None:
    direct_value = FreqtradeReferenceAdapter._lookup_value(
      candidates,
      "strategy_name",
      "strategy",
      "key",
      "name",
    )
    if isinstance(direct_value, str):
      return direct_value
    strategy = payload.get("strategy")
    if isinstance(strategy, str):
      return strategy
    if isinstance(strategy, dict):
      nested_name = next(
        (
          name
          for name, details in strategy.items()
          if isinstance(name, str) and isinstance(details, dict)
        ),
        None,
      )
      if nested_name is not None:
        return nested_name
    return None

  @staticmethod
  def _lookup_value(candidates: list[dict[str, Any]], *keys: str) -> Any:
    for candidate in candidates:
      for key in keys:
        if key not in candidate:
          continue
        value = candidate[key]
        if value in (None, "", [], {}):
          continue
        return value
    return None

  @staticmethod
  def _lookup_pct_value(
    candidates: list[dict[str, Any]],
    *,
    pct_keys: tuple[str, ...],
    ratio_keys: tuple[str, ...],
  ) -> float | int | None:
    direct_value = FreqtradeReferenceAdapter._lookup_value(candidates, *pct_keys)
    if isinstance(direct_value, (int, float)):
      return direct_value
    ratio_value = FreqtradeReferenceAdapter._lookup_value(candidates, *ratio_keys)
    if isinstance(ratio_value, (int, float)):
      return round(ratio_value * 100, 4)
    return None

  @staticmethod
  def _merge_sections(target: dict[str, Any], source: dict[str, Any]) -> None:
    for key, value in source.items():
      target[key] = value
