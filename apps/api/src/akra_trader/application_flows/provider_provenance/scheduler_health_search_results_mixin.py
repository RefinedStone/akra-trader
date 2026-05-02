from __future__ import annotations

import csv
from copy import deepcopy
from dataclasses import replace
from datetime import UTC
from datetime import datetime
from datetime import timedelta
import io
import json
import math
import re
from typing import Any
from typing import Iterable
from typing import Mapping

from akra_trader.domain.models import *  # noqa: F403


def _serialize_stitched_scheduler_narrative_json_value(value: Any) -> str:
  if isinstance(value, datetime):
    return value.isoformat()
  raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


class ProviderProvenanceSchedulerHealthSearchResultsMixin:
  @classmethod
  def _score_provider_provenance_scheduler_alert_occurrence_search_match(
    cls,
    *,
    row: Mapping[str, Any],
    parsed_query: Mapping[str, Any],
    index: Mapping[str, Any] | None = None,
    document: Mapping[str, Any] | None = None,
    tuning_profile: Mapping[str, Any] | None = None,
  ) -> dict[str, Any] | None:
    terms = parsed_query["terms"]
    phrases = parsed_query["phrases"]
    operators = parsed_query["operators"]
    semantic_query_concepts = parsed_query["semantic_concepts"]
    if not any((terms, phrases, operators, semantic_query_concepts)):
      return None
    search_fields = cls._build_provider_provenance_scheduler_alert_occurrence_search_fields(row=row)
    row_semantic_concepts = cls._build_provider_provenance_scheduler_alert_occurrence_semantic_concepts(row=row)
    matched_terms: set[str] = set()
    matched_phrases: set[str] = set()
    matched_fields: list[str] = []
    highlights: list[str] = []
    lexical_score = 0
    operator_score = 0
    semantic_score = 0
    phrase_match = False
    exact_match = False
    field_hits = 0
    operator_hits: list[str] = []
    tuning_signals: list[str] = []
    learned_score = 0
    total_documents = int(index.get("document_count", 0)) if isinstance(index, Mapping) else 0
    average_document_length = (
      float(index.get("average_document_length", 0.0))
      if isinstance(index, Mapping)
      else 0.0
    )
    document_term_frequencies = (
      document.get("lexical_term_frequencies", {})
      if isinstance(document, Mapping)
      else {}
    )
    document_length = (
      sum(document_term_frequencies.values())
      if isinstance(document_term_frequencies, dict)
      else 0
    )
    for operator in operators:
      if operator.get("negated"):
        continue
      matched_candidates = cls._match_provider_provenance_scheduler_alert_occurrence_operator(
        row=row,
        operator=operator,
      )
      if not matched_candidates:
        continue
      operator_label = f"{operator['field']}:{operator['value']}"
      operator_hits.append(operator_label)
      operator_score += 160 + (15 * min(len(matched_candidates), 2))
      if len(highlights) < 3:
        highlights.append(
          f"operator {operator_label}: "
          f"{cls._truncate_provider_provenance_scheduler_search_highlight(matched_candidates[0])}"
        )
    for field_name, field_weight, field_values in search_fields:
      best_field_score = 0
      best_field_highlight: str | None = None
      field_matched_terms: set[str] = set()
      field_matched_phrases: set[str] = set()
      field_phrase_match = False
      field_exact_match = False
      for raw_value in field_values:
        normalized_value = cls._normalize_provider_provenance_scheduler_alert_search_text(raw_value)
        if normalized_value is None:
          continue
        value_score = 0
        for phrase in phrases:
          if phrase == normalized_value:
            value_score += field_weight * 4
            field_matched_phrases.add(phrase)
            field_phrase_match = True
            field_exact_match = True
          elif phrase in normalized_value:
            value_score += field_weight * 3
            field_matched_phrases.add(phrase)
            field_phrase_match = True
        for token in terms:
          document_frequency = (
            len(index.get("lexical_postings", {}).get(token, ()))
            if isinstance(index, Mapping)
            else 0
          )
          token_frequency = (
            int(document_term_frequencies.get(token, 0))
            if isinstance(document_term_frequencies, dict)
            else 0
          )
          inverse_document_frequency = (
            1.0 + ((total_documents + 1) / (document_frequency + 1))
            if total_documents > 0
            else 1.0
          )
          tf_bonus = (
            1.0 + min(token_frequency, 4) * 0.15
            if token_frequency > 0
            else 1.0
          )
          length_normalizer = (
            1.0
            if average_document_length <= 0
            else 1.0
            + min(document_length / average_document_length, 3.0) * 0.05
          )
          if token == normalized_value:
            value_score += int(round(field_weight * 3 * inverse_document_frequency * tf_bonus * length_normalizer))
            field_matched_terms.add(token)
            field_exact_match = True
          elif normalized_value.startswith(token):
            value_score += int(round(field_weight * 2 * inverse_document_frequency * tf_bonus))
            field_matched_terms.add(token)
          elif token in normalized_value:
            value_score += int(round(field_weight * inverse_document_frequency * tf_bonus))
            field_matched_terms.add(token)
        if value_score > best_field_score:
          best_field_score = value_score
          best_field_highlight = (
            f"{field_name}: {cls._truncate_provider_provenance_scheduler_search_highlight(raw_value)}"
          )
      if best_field_score <= 0:
        continue
      field_hits += 1
      matched_terms.update(field_matched_terms)
      matched_phrases.update(field_matched_phrases)
      matched_fields.append(field_name)
      if best_field_highlight is not None and best_field_highlight not in highlights:
        highlights.append(best_field_highlight)
      if field_phrase_match:
        phrase_match = True
      if field_exact_match:
        exact_match = True
      lexical_score += best_field_score
    semantic_hits = tuple(
      concept for concept in semantic_query_concepts if concept in row_semantic_concepts
    )
    if semantic_hits:
      semantic_score += 110 * len(semantic_hits)
      if len(highlights) < 3:
        highlights.append(f"semantic: {', '.join(semantic_hits)}")
    if isinstance(tuning_profile, Mapping) and tuning_profile.get("active"):
      field_adjustments = tuning_profile.get("field_adjustments", {}) or {}
      semantic_adjustments = tuning_profile.get("semantic_adjustments", {}) or {}
      operator_adjustments = tuning_profile.get("operator_adjustments", {}) or {}
      channel_adjustments = tuning_profile.get("channel_adjustments", {}) or {}
      for field_name in matched_fields:
        adjustment = int(field_adjustments.get(field_name, 0))
        if adjustment == 0:
          continue
        learned_score += adjustment
        tuning_signals.append(f"field {field_name} {adjustment:+d}")
      for concept in semantic_hits:
        adjustment = int(semantic_adjustments.get(concept, 0))
        if adjustment == 0:
          continue
        learned_score += adjustment
        tuning_signals.append(f"semantic {concept} {adjustment:+d}")
      for operator_hit in operator_hits:
        adjustment = int(operator_adjustments.get(operator_hit, 0))
        if adjustment == 0:
          continue
        learned_score += adjustment
        tuning_signals.append(f"operator {operator_hit} {adjustment:+d}")
      learned_score += int(channel_adjustments.get("lexical", 0)) * max(
        len(matched_terms) + len(matched_phrases),
        1 if lexical_score > 0 else 0,
      )
      learned_score += int(channel_adjustments.get("semantic", 0)) * len(semantic_hits)
      learned_score += int(channel_adjustments.get("operator", 0)) * len(operator_hits)
    score = lexical_score + semantic_score + operator_score
    if score <= 0:
      return None
    lexical_unit_total = len(terms) + len(phrases)
    lexical_units_matched = len(matched_terms) + len(matched_phrases)
    coverage = lexical_units_matched / lexical_unit_total if lexical_unit_total > 0 else 1.0
    coverage_pct = int(round(coverage * 100))
    score += coverage_pct * 2
    score += field_hits * 5
    if phrase_match:
      score += 40
    if exact_match:
      score += 60
    score += learned_score
    ranking_reason_parts = []
    if exact_match:
      ranking_reason_parts.append("exact field match")
    elif phrase_match:
      ranking_reason_parts.append("phrase match")
    if operator_hits:
      ranking_reason_parts.append(f"{len(operator_hits)} operator(s) satisfied")
    if semantic_hits:
      ranking_reason_parts.append(f"semantic hit: {', '.join(semantic_hits)}")
    if lexical_unit_total > 0:
      ranking_reason_parts.append(
        f"{lexical_units_matched} of {lexical_unit_total} lexical unit(s) matched"
      )
    if learned_score != 0:
      ranking_reason_parts.append(f"feedback tuned {learned_score:+d}")
    ranking_reason_parts.append(f"{field_hits} ranked field(s)")
    return {
      "score": score,
      "matched_terms": tuple(sorted(matched_terms)),
      "matched_phrases": tuple(sorted(matched_phrases)),
      "matched_fields": tuple(matched_fields),
      "term_coverage_pct": coverage_pct,
      "phrase_match": phrase_match,
      "exact_match": exact_match,
      "highlights": tuple(highlights[:3]),
      "semantic_concepts": semantic_hits,
      "operator_hits": tuple(operator_hits),
      "lexical_score": lexical_score,
      "semantic_score": semantic_score,
      "operator_score": operator_score,
      "learned_score": learned_score,
      "feedback_signal_count": int(tuning_profile.get("feedback_signal_count", 0))
      if isinstance(tuning_profile, Mapping)
      else 0,
      "tuning_signals": tuple(tuning_signals[:4]),
      "relevance_model": (
        str(tuning_profile.get("version"))
        if isinstance(tuning_profile, Mapping) and isinstance(tuning_profile.get("version"), str)
        else "tfidf_field_weight_v1"
      ),
      "ranking_reason": " · ".join(ranking_reason_parts),
    }

  @staticmethod
  def _humanize_provider_provenance_scheduler_retrieval_feature(
    feature: str,
  ) -> str:
    if not isinstance(feature, str) or not feature.strip():
      return ""
    _, _, raw_value = feature.partition(":")
    normalized_value = raw_value or feature
    return normalized_value.replace("_", " ").replace("->", " -> ").strip()

  @classmethod
  def _build_provider_provenance_scheduler_alert_occurrence_retrieval_vector(
    cls,
    *,
    row: Mapping[str, Any],
    search_match: Mapping[str, Any],
    document: Mapping[str, Any],
  ) -> dict[str, float]:
    alert = row.get("alert")
    narrative = row.get("narrative")
    if not isinstance(alert, OperatorAlert):
      return {}
    vector: dict[str, float] = {}

    def add_feature(feature: str | None, weight: float) -> None:
      if not isinstance(feature, str) or not feature.strip():
        return
      vector[feature] = vector.get(feature, 0.0) + weight

    for concept in document.get("semantic_concepts", ()) or ():
      if isinstance(concept, str):
        add_feature(f"concept:{concept}", 3.0)
    for concept in search_match.get("semantic_concepts", ()) or ():
      if isinstance(concept, str):
        add_feature(f"concept:{concept}", 4.5)
    for term in search_match.get("matched_terms", ()) or ():
      if isinstance(term, str):
        add_feature(f"term:{term}", 3.0)
    for phrase in search_match.get("matched_phrases", ()) or ():
      if isinstance(phrase, str):
        add_feature(f"phrase:{phrase}", 4.0)
        for token in cls._tokenize_provider_provenance_scheduler_alert_search_query(phrase):
          add_feature(f"term:{token}", 1.5)

    add_feature(f"category:{alert.category}", 2.6)
    add_feature(f"status:{alert.status}", 2.2)
    add_feature(f"severity:{alert.severity}", 1.2)
    add_feature(f"source:{alert.source}", 1.0)

    if isinstance(narrative, Mapping):
      facet = narrative.get("facet")
      if isinstance(facet, str) and facet.strip():
        add_feature(f"facet:{facet}", 2.1)
      for flag in narrative.get("facet_flags", ()) or ():
        if isinstance(flag, str) and flag.strip():
          add_feature(f"flag:{flag}", 1.6)
      status_sequence = tuple(
        status
        for status in narrative.get("status_sequence", ()) or ()
        if isinstance(status, str) and status.strip()
      )
      if status_sequence:
        add_feature(f"sequence:{'->'.join(status_sequence)}", 2.8)
        for status in status_sequence:
          add_feature(f"sequence_state:{status}", 1.0)

    primary_focus = alert.primary_focus
    if primary_focus is not None:
      if isinstance(primary_focus.symbol, str) and primary_focus.symbol.strip():
        add_feature(f"focus:{primary_focus.symbol.strip().lower()}", 1.8)
      if isinstance(primary_focus.timeframe, str) and primary_focus.timeframe.strip():
        add_feature(f"focus:{primary_focus.timeframe.strip().lower()}", 1.4)
      if isinstance(primary_focus.policy, str) and primary_focus.policy.strip():
        add_feature(f"focus_policy:{primary_focus.policy.strip().lower()}", 1.2)
      if isinstance(primary_focus.reason, str) and primary_focus.reason.strip():
        for token in cls._tokenize_provider_provenance_scheduler_alert_search_query(
          primary_focus.reason
        ):
          add_feature(f"term:{token}", 0.8)

    for value in document.get("normalized_fields", {}).get("market_context", ()) or ():
      if not isinstance(value, str):
        continue
      for token in cls._tokenize_provider_provenance_scheduler_alert_search_query(value):
        add_feature(f"term:{token}", 0.8)
    for value in document.get("normalized_fields", {}).get("summary", ()) or ():
      if not isinstance(value, str):
        continue
      for token in cls._tokenize_provider_provenance_scheduler_alert_search_query(value):
        if token in search_match.get("matched_terms", ()):
          add_feature(f"term:{token}", 0.6)
    return vector

  @staticmethod
  def _calculate_provider_provenance_scheduler_retrieval_similarity(
    left: Mapping[str, float],
    right: Mapping[str, float],
  ) -> float:
    if not left or not right:
      return 0.0
    if len(left) <= len(right):
      dot_product = sum(weight * right.get(key, 0.0) for key, weight in left.items())
    else:
      dot_product = sum(weight * left.get(key, 0.0) for key, weight in right.items())
    if dot_product <= 0:
      return 0.0
    left_norm = math.sqrt(sum(weight * weight for weight in left.values()))
    right_norm = math.sqrt(sum(weight * weight for weight in right.values()))
    if left_norm <= 0 or right_norm <= 0:
      return 0.0
    return dot_product / (left_norm * right_norm)

  @staticmethod
  def _merge_provider_provenance_scheduler_retrieval_vectors(
    vectors: Iterable[Mapping[str, float]],
  ) -> dict[str, float]:
    merged: dict[str, float] = {}
    for vector in vectors:
      for key, weight in vector.items():
        merged[key] = merged.get(key, 0.0) + float(weight)
    return merged

  @classmethod
  def _build_provider_provenance_scheduler_retrieval_cluster_label(
    cls,
    *,
    semantic_concepts: tuple[str, ...],
    categories: tuple[str, ...],
    statuses: tuple[str, ...],
  ) -> str:
    label_parts: list[str] = []
    if semantic_concepts:
      label_parts.append(" / ".join(cls._humanize_provider_provenance_scheduler_retrieval_feature(f"concept:{concept}") for concept in semantic_concepts[:2]))
    if categories:
      label_parts.append(
        cls._humanize_provider_provenance_scheduler_retrieval_feature(f"category:{categories[0]}")
      )
    if statuses:
      label_parts.append(
        cls._humanize_provider_provenance_scheduler_retrieval_feature(f"status:{statuses[0]}")
      )
    label = " · ".join(part for part in label_parts if part)
    return label or "Cross-occurrence retrieval cluster"

  @classmethod
  def _cluster_provider_provenance_scheduler_alert_occurrence_search_results(
    cls,
    *,
    rows: tuple[Mapping[str, Any], ...],
    index: Mapping[str, Any],
  ) -> tuple[tuple[dict[str, Any], ...], tuple[dict[str, Any], ...]]:
    if not rows:
      return (), ()
    documents_by_id = {
      int(document.get("document_id", -1)): document
      for document in index.get("documents", ()) or ()
      if isinstance(document, Mapping)
    }
    raw_clusters: list[dict[str, Any]] = []
    similarity_threshold = 0.46
    for result_index, row in enumerate(rows):
      search_match = row.get("search_match")
      document_id = row.get("_search_document_id")
      document = documents_by_id.get(int(document_id)) if isinstance(document_id, int) else None
      if not isinstance(search_match, Mapping) or not isinstance(document, Mapping):
        continue
      vector = cls._build_provider_provenance_scheduler_alert_occurrence_retrieval_vector(
        row=row,
        search_match=search_match,
        document=document,
      )
      best_cluster_index: int | None = None
      best_similarity = 0.0
      for cluster_index, cluster in enumerate(raw_clusters):
        similarity = cls._calculate_provider_provenance_scheduler_retrieval_similarity(
          vector,
          cluster["centroid"],
        )
        if similarity > best_similarity:
          best_similarity = similarity
          best_cluster_index = cluster_index
      if best_cluster_index is None or best_similarity < similarity_threshold:
        raw_clusters.append(
          {
            "items": [
              {
                "result_index": result_index,
                "row": row,
                "vector": vector,
                "similarity": 1.0,
              }
            ],
            "centroid": dict(vector),
          }
        )
        continue
      cluster = raw_clusters[best_cluster_index]
      cluster["items"].append(
        {
          "result_index": result_index,
          "row": row,
          "vector": vector,
          "similarity": best_similarity,
        }
      )
      cluster["centroid"] = cls._merge_provider_provenance_scheduler_retrieval_vectors(
        item["vector"] for item in cluster["items"]
      )

    ordered_clusters = sorted(
      raw_clusters,
      key=lambda cluster: (
        max(
          (
            int(item["row"].get("search_match", {}).get("score", 0))
            for item in cluster["items"]
          ),
          default=0,
        ),
        len(cluster["items"]),
      ),
      reverse=True,
    )
    cluster_payloads: list[dict[str, Any]] = []
    retrieval_cluster_by_result_index: dict[int, dict[str, Any]] = {}
    for cluster_rank, cluster in enumerate(ordered_clusters, start=1):
      sorted_items = sorted(
        cluster["items"],
        key=lambda item: (
          int(item["row"].get("search_match", {}).get("score", 0)),
          item["row"]["alert"].resolved_at or item["row"]["alert"].detected_at,
        ),
        reverse=True,
      )
      top_occurrence = sorted_items[0]["row"]["alert"]
      semantic_counts: dict[str, int] = {}
      category_counts: dict[str, int] = {}
      status_counts: dict[str, int] = {}
      facet_counts: dict[str, int] = {}
      for item in sorted_items:
        row = item["row"]
        alert = row.get("alert")
        narrative = row.get("narrative")
        search_match = row.get("search_match", {})
        if isinstance(search_match, Mapping):
          for concept in search_match.get("semantic_concepts", ()) or ():
            if isinstance(concept, str):
              semantic_counts[concept] = semantic_counts.get(concept, 0) + 1
        if isinstance(alert, OperatorAlert):
          category_counts[alert.category] = category_counts.get(alert.category, 0) + 1
          status_counts[alert.status] = status_counts.get(alert.status, 0) + 1
        if isinstance(narrative, Mapping):
          facet = narrative.get("facet")
          if isinstance(facet, str) and facet.strip():
            facet_counts[facet] = facet_counts.get(facet, 0) + 1
      sorted_semantic_concepts = tuple(
        concept
        for concept, _ in sorted(
          semantic_counts.items(),
          key=lambda item: (-item[1], item[0]),
        )
      )
      sorted_categories = tuple(
        category_key
        for category_key, _ in sorted(
          category_counts.items(),
          key=lambda item: (-item[1], item[0]),
        )
      )
      sorted_statuses = tuple(
        status_key
        for status_key, _ in sorted(
          status_counts.items(),
          key=lambda item: (-item[1], item[0]),
        )
      )
      sorted_facets = tuple(
        facet_key
        for facet_key, _ in sorted(
          facet_counts.items(),
          key=lambda item: (-item[1], item[0]),
        )
      )
      top_vector_terms = tuple(
        dict.fromkeys(
          cls._humanize_provider_provenance_scheduler_retrieval_feature(feature)
          for feature, _ in sorted(
            cluster["centroid"].items(),
            key=lambda item: (-item[1], item[0]),
          )
          if feature.startswith(("concept:", "term:", "phrase:", "sequence:", "focus:"))
        )
      )[:5]
      label = cls._build_provider_provenance_scheduler_retrieval_cluster_label(
        semantic_concepts=sorted_semantic_concepts,
        categories=sorted_categories,
        statuses=sorted_statuses,
      )
      cluster_id = f"cluster-{cluster_rank}"
      score_values = [
        int(item["row"].get("search_match", {}).get("score", 0))
        for item in sorted_items
      ]
      similarity_values = [float(item.get("similarity", 0.0)) for item in sorted_items]
      summary = (
        f"{len(sorted_items)} occurrence(s) grouped around {label.lower()}"
      )
      cluster_payload = {
        "cluster_id": cluster_id,
        "rank": cluster_rank,
        "label": label,
        "summary": summary,
        "occurrence_count": len(sorted_items),
        "top_score": max(score_values, default=0),
        "average_score": int(round(sum(score_values) / len(score_values))) if score_values else 0,
        "average_similarity_pct": int(round((sum(similarity_values) / len(similarity_values)) * 100))
        if similarity_values
        else 0,
        "semantic_concepts": sorted_semantic_concepts[:5],
        "vector_terms": top_vector_terms,
        "categories": sorted_categories,
        "statuses": sorted_statuses,
        "narrative_facets": sorted_facets,
        "top_occurrence_id": top_occurrence.occurrence_id,
        "top_occurrence_summary": top_occurrence.summary,
        "occurrence_ids": tuple(
          item["row"]["alert"].occurrence_id
          for item in sorted_items
          if isinstance(item["row"]["alert"].occurrence_id, str)
        ),
      }
      cluster_payloads.append(cluster_payload)
      for item in sorted_items:
        retrieval_cluster_by_result_index[item["result_index"]] = {
          "cluster_id": cluster_id,
          "rank": cluster_rank,
          "label": label,
          "similarity_pct": int(round(float(item.get("similarity", 0.0)) * 100)),
          "semantic_concepts": list(cluster_payload["semantic_concepts"]),
          "vector_terms": list(cluster_payload["vector_terms"]),
        }

    enriched_rows = tuple(
      {
        **row,
        "retrieval_cluster": retrieval_cluster_by_result_index.get(result_index),
      }
      for result_index, row in enumerate(rows)
    )
    return enriched_rows, tuple(cluster_payloads)

  @classmethod
  def _build_provider_provenance_scheduler_alert_occurrence_search_match(
    cls,
    *,
    row: Mapping[str, Any],
    search: str | None,
  ) -> dict[str, Any] | None:
    if not isinstance(search, str) or not search.strip():
      return None
    parsed_query = cls._parse_provider_provenance_scheduler_alert_search_query(search)
    index = cls._build_provider_provenance_scheduler_alert_occurrence_search_index(rows=(row,))
    document = next(iter(index.get("documents", ())), None)
    matched_document_ids = cls._evaluate_provider_provenance_scheduler_alert_search_query(
      index=index,
      parsed_query=parsed_query,
    )
    if 0 not in matched_document_ids:
      return None
    return cls._score_provider_provenance_scheduler_alert_occurrence_search_match(
      row=row,
      parsed_query=parsed_query,
      index=index,
      document=document,
    )

  @staticmethod
  def _build_provider_provenance_scheduler_occurrence_detected_at(
    *,
    target_status: str,
    snapshot: ProviderProvenanceSchedulerHealth,
  ) -> datetime:
    if target_status == "lagging":
      return snapshot.oldest_due_at or snapshot.generated_at
    return (
      snapshot.last_failure_at
      or snapshot.last_cycle_finished_at
      or snapshot.last_cycle_started_at
      or snapshot.generated_at
    )

  @staticmethod
  def _compress_provider_provenance_scheduler_status_sequence(
    records: Iterable[ProviderProvenanceSchedulerHealthRecord],
  ) -> tuple[str, ...]:
    sequence: list[str] = []
    for record in records:
      if not sequence or sequence[-1] != record.status:
        sequence.append(record.status)
    return tuple(sequence)

  def _build_provider_provenance_scheduler_alert_occurrence_rows(
    self,
    *,
    current_time: datetime,
  ) -> tuple[dict[str, Any], ...]:
    self._prune_provider_provenance_scheduler_health_records()
    records = tuple(
      sorted(
        self._list_provider_provenance_scheduler_health_records(),
        key=lambda record: (record.recorded_at, record.record_id),
      )
    )
    if not records:
      return ()
    current_health = self.get_provider_provenance_scheduler_health()
    occurrence_rows: list[dict[str, Any]] = []
    for target_status in ("lagging", "failed"):
      status_rows: list[dict[str, Any]] = []
      index = 0
      while index < len(records):
        if records[index].status != target_status:
          index += 1
          continue
        start_index = index
        end_index = index
        while end_index + 1 < len(records) and records[end_index + 1].status == target_status:
          end_index += 1
        latest_record = records[end_index]
        latest_snapshot = self._provider_provenance_scheduler_health_snapshot_from_record(latest_record)
        alert = self._build_provider_provenance_scheduler_operator_alert(
          health=latest_snapshot,
          current_time=current_time,
        )
        if alert is not None:
          first_snapshot = self._provider_provenance_scheduler_health_snapshot_from_record(
            records[start_index]
          )
          detected_at = self._build_provider_provenance_scheduler_occurrence_detected_at(
            target_status=target_status,
            snapshot=first_snapshot,
          )
          is_active_occurrence = end_index == len(records) - 1 and current_health.status == target_status
          resolved_at = (
            None
            if is_active_occurrence
            else (
              records[end_index + 1].recorded_at
              if end_index + 1 < len(records)
              else current_time
            )
          )
          next_occurrence_start_index: int | None = None
          search_index = end_index + 1
          while search_index < len(records):
            if records[search_index].status == target_status:
              next_occurrence_start_index = search_index
              break
            search_index += 1
          narrative_end_index = (
            next_occurrence_start_index - 1
            if next_occurrence_start_index is not None
            else len(records) - 1
          )
          occurrence_records = tuple(records[start_index:end_index + 1])
          post_resolution_records = (
            tuple(records[end_index + 1:narrative_end_index + 1])
            if resolved_at is not None and end_index + 1 <= narrative_end_index
            else ()
          )
          narrative_records = (*occurrence_records, *post_resolution_records)
          next_occurrence_detected_at = (
            self._build_provider_provenance_scheduler_occurrence_detected_at(
              target_status=target_status,
              snapshot=self._provider_provenance_scheduler_health_snapshot_from_record(
                records[next_occurrence_start_index]
              ),
            )
            if next_occurrence_start_index is not None
            else None
          )
          primary_facet = "current_snapshot" if is_active_occurrence else "resolved_narrative"
          facet_flags: list[str] = [primary_facet]
          if post_resolution_records:
            primary_facet = "post_resolution_recovery"
            if "resolved_narrative" not in facet_flags:
              facet_flags.append("resolved_narrative")
            facet_flags.append("post_resolution_recovery")
          status_rows.append(
            {
              "alert": replace(
                alert,
                detected_at=detected_at,
                occurrence_id=self._build_operator_alert_occurrence_id(
                  alert_id=alert.alert_id,
                  detected_at=detected_at,
                  resolved_at=resolved_at,
                ),
                timeline_key=alert.category,
                timeline_position=len(status_rows) + 1,
                status="active" if is_active_occurrence else "resolved",
                resolved_at=resolved_at,
              ),
              "narrative": {
                "facet": primary_facet,
                "facet_flags": tuple(facet_flags),
                "narrative_mode": (
                  "matched_status"
                  if is_active_occurrence
                  else "mixed_status_post_resolution"
                ),
                "can_reconstruct_narrative": not is_active_occurrence,
                "has_post_resolution_history": bool(post_resolution_records),
                "occurrence_record_count": len(occurrence_records),
                "post_resolution_record_count": len(post_resolution_records),
                "status_sequence": self._compress_provider_provenance_scheduler_status_sequence(
                  narrative_records
                ),
                "post_resolution_status_sequence": (
                  self._compress_provider_provenance_scheduler_status_sequence(
                    post_resolution_records
                  )
                  if post_resolution_records
                  else ()
                ),
                "narrative_window_ended_at": (
                  narrative_records[-1].recorded_at if narrative_records else resolved_at
                ),
                "next_occurrence_detected_at": next_occurrence_detected_at,
              },
              "occurrence_records": occurrence_records,
              "narrative_records": tuple(narrative_records),
              "latest_record": latest_record,
            }
          )
        index = end_index + 1
      total_occurrences = len(status_rows)
      for row in status_rows:
        alert = row["alert"]
        narrative = dict(row["narrative"])
        facet_flags = list(narrative.get("facet_flags", ()))
        if total_occurrences > 1:
          facet_flags.append("recurring_occurrence")
          if (
            narrative.get("facet") == "resolved_narrative"
            and not narrative.get("has_post_resolution_history")
          ):
            narrative["facet"] = "recurring_occurrence"
        narrative["facet_flags"] = tuple(dict.fromkeys(facet_flags))
        row["alert"] = replace(alert, timeline_total=total_occurrences)
        row["narrative"] = narrative
        occurrence_rows.append(row)
    return tuple(
      sorted(
        occurrence_rows,
        key=lambda row: (
          row["alert"].resolved_at or row["alert"].detected_at,
          row["alert"].detected_at,
        ),
        reverse=True,
      )
    )
