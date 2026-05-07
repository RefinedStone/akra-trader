from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import is_dataclass
from dataclasses import replace
import hashlib
import json
from datetime import UTC
from datetime import datetime
from datetime import timedelta

from akra_trader.domain.models import Candle
from akra_trader.domain.models import DatasetBoundaryContract
from akra_trader.domain.models import MarketDataIngestionJobRecord
from akra_trader.domain.models import MarketDataLineage
from akra_trader.domain.models import MarketDataLineageHistoryRecord
from akra_trader.domain.models import OperatorLineageDrillEvidencePack
from akra_trader.domain.models import OperatorLineageEvidenceRetentionPolicy
from akra_trader.domain.models import OperatorLineageEvidenceRetentionResult
from akra_trader.domain.models import RunRecord


OPERATOR_LINEAGE_RETENTION_FLOORS = OperatorLineageEvidenceRetentionPolicy()
OPERATOR_LINEAGE_DRILL_EVIDENCE_PACK_RETENTION_DAYS = 180


def _serialize_optional_datetime(value: datetime | None) -> str | None:
  return value.isoformat() if value is not None else None

def build_operator_lineage_evidence_retention_policy(
  *,
  lineage_history_days: int | None = None,
  lineage_issue_history_days: int | None = None,
  ingestion_job_days: int | None = None,
  ingestion_issue_job_days: int | None = None,
) -> OperatorLineageEvidenceRetentionPolicy:
  floors = OPERATOR_LINEAGE_RETENTION_FLOORS
  return OperatorLineageEvidenceRetentionPolicy(
    lineage_history_days=max(
      lineage_history_days or floors.lineage_history_days,
      floors.lineage_history_days,
    ),
    lineage_issue_history_days=max(
      lineage_issue_history_days or floors.lineage_issue_history_days,
      floors.lineage_issue_history_days,
    ),
    ingestion_job_days=max(
      ingestion_job_days or floors.ingestion_job_days,
      floors.ingestion_job_days,
    ),
    ingestion_issue_job_days=max(
      ingestion_issue_job_days or floors.ingestion_issue_job_days,
      floors.ingestion_issue_job_days,
    ),
  )


def build_operator_lineage_evidence_retention_result(
  *,
  lineage_history: list[MarketDataLineageHistoryRecord],
  ingestion_jobs: list[MarketDataIngestionJobRecord],
  current_time: datetime,
  policy: OperatorLineageEvidenceRetentionPolicy,
  dry_run: bool,
  protected_history_ids: tuple[str, ...] = (),
  protected_job_ids: tuple[str, ...] = (),
) -> OperatorLineageEvidenceRetentionResult:
  retained_job_lineage_history_ids: set[str] = set()
  protected_job_id_set = set(protected_job_ids)
  eligible_job_ids: list[str] = []
  retained_job_ids: list[str] = []
  for job in ingestion_jobs:
    cutoff = _operator_lineage_ingestion_job_cutoff(
      current_time=current_time,
      policy=policy,
      job=job,
    )
    if job.job_id in protected_job_id_set:
      retained_job_ids.append(job.job_id)
      if job.lineage_history_id:
        retained_job_lineage_history_ids.add(job.lineage_history_id)
      continue
    if _operator_lineage_recorded_at(job.finished_at) <= cutoff:
      eligible_job_ids.append(job.job_id)
    else:
      retained_job_ids.append(job.job_id)
      if job.lineage_history_id:
        retained_job_lineage_history_ids.add(job.lineage_history_id)

  protected_history_id_set = set(protected_history_ids)
  eligible_history_ids: list[str] = []
  retained_history_ids: list[str] = []
  for record in lineage_history:
    cutoff = _operator_lineage_history_cutoff(
      current_time=current_time,
      policy=policy,
      record=record,
    )
    if (
      record.history_id in protected_history_id_set
      or record.history_id in retained_job_lineage_history_ids
    ):
      retained_history_ids.append(record.history_id)
      continue
    if _operator_lineage_recorded_at(record.recorded_at) <= cutoff:
      eligible_history_ids.append(record.history_id)
    else:
      retained_history_ids.append(record.history_id)

  return OperatorLineageEvidenceRetentionResult(
    policy=policy,
    current_time=current_time,
    dry_run=dry_run,
    lineage_history_cutoff_at=current_time - timedelta(days=policy.lineage_history_days),
    lineage_issue_history_cutoff_at=current_time - timedelta(days=policy.lineage_issue_history_days),
    ingestion_job_cutoff_at=current_time - timedelta(days=policy.ingestion_job_days),
    ingestion_issue_job_cutoff_at=current_time - timedelta(days=policy.ingestion_issue_job_days),
    eligible_lineage_history_ids=tuple(eligible_history_ids),
    eligible_ingestion_job_ids=tuple(eligible_job_ids),
    retained_lineage_history_floor_ids=tuple(retained_history_ids),
    retained_ingestion_job_floor_ids=tuple(retained_job_ids),
    protected_lineage_history_ids=tuple(protected_history_ids),
    protected_ingestion_job_ids=tuple(protected_job_ids),
  )


def apply_operator_lineage_evidence_retention_deletion_counts(
  result: OperatorLineageEvidenceRetentionResult,
  *,
  deleted_lineage_history_count: int,
  deleted_ingestion_job_count: int,
) -> OperatorLineageEvidenceRetentionResult:
  return replace(
    result,
    deleted_lineage_history_count=deleted_lineage_history_count,
    deleted_ingestion_job_count=deleted_ingestion_job_count,
  )


def build_operator_lineage_drill_evidence_pack(
  *,
  lineage_history: list[MarketDataLineageHistoryRecord],
  ingestion_jobs: list[MarketDataIngestionJobRecord],
  generated_at: datetime,
  pack_id: str,
  generated_by: str = "operator",
  export_format: str = "json",
  scenario_key: str | None = None,
  scenario_label: str | None = None,
  incident_id: str | None = None,
  operator_decision: str = "reviewed",
  final_posture: str = "unresolved",
  venue: str | None = None,
  symbol: str | None = None,
  timeframe: str | None = None,
  source_run_id: str | None = None,
  rerun_id: str | None = None,
  dataset_identity: str | None = None,
  sync_checkpoint_id: str | None = None,
  rerun_boundary_id: str | None = None,
  validation_claim: str | None = None,
  rerun_validation_category: str | None = None,
  sync_status: str | None = None,
  operation: str | None = None,
  status: str | None = None,
  lineage_history_limit: int | None = None,
  ingestion_job_limit: int | None = None,
  retention_policy: OperatorLineageEvidenceRetentionPolicy | None = None,
) -> OperatorLineageDrillEvidencePack:
  normalized_format = _normalize_operator_lineage_drill_evidence_pack_format(export_format)
  lineage_records = tuple(lineage_history)
  ingestion_records = tuple(ingestion_jobs)
  policy = retention_policy or build_operator_lineage_evidence_retention_policy()
  pack = OperatorLineageDrillEvidencePack(
    pack_id=pack_id,
    generated_at=generated_at,
    generated_by=generated_by.strip() if generated_by.strip() else "operator",
    retention_policy=policy,
    retention_expires_at=generated_at + timedelta(
      days=OPERATOR_LINEAGE_DRILL_EVIDENCE_PACK_RETENTION_DAYS,
    ),
    export_format=normalized_format,
    scenario_key=scenario_key,
    scenario_label=scenario_label,
    incident_id=incident_id,
    operator_decision=operator_decision.strip() if operator_decision.strip() else "reviewed",
    final_posture=final_posture.strip() if final_posture.strip() else "unresolved",
    venue=_resolve_operator_lineage_pack_value(
      venue,
      *(record.venue for record in lineage_records),
      *(job.venue for job in ingestion_records),
    ),
    symbols=_resolve_operator_lineage_pack_symbols(
      symbol=symbol,
      lineage_history=lineage_records,
      ingestion_jobs=ingestion_records,
    ),
    timeframe=_resolve_operator_lineage_pack_value(
      timeframe,
      *(record.timeframe for record in lineage_records),
      *(job.timeframe for job in ingestion_records),
    ),
    source_run_id=source_run_id,
    rerun_id=rerun_id,
    dataset_identity=_resolve_operator_lineage_pack_value(
      dataset_identity,
      *(
        record.dataset_boundary.dataset_identity
        for record in lineage_records
        if record.dataset_boundary is not None
      ),
    ),
    sync_checkpoint_id=_resolve_operator_lineage_pack_value(
      sync_checkpoint_id,
      *(record.checkpoint_id for record in lineage_records),
      *(job.checkpoint_id for job in ingestion_records),
    ),
    rerun_boundary_id=rerun_boundary_id,
    validation_claim=_resolve_operator_lineage_pack_value(
      validation_claim,
      *(record.validation_claim for record in lineage_records),
      *(job.validation_claim for job in ingestion_records),
    ),
    rerun_validation_category=rerun_validation_category,
    lineage_history_filters=_clean_operator_lineage_pack_filters(
      {
        "symbol": symbol,
        "timeframe": timeframe,
        "sync_status": sync_status,
        "validation_claim": validation_claim,
        "limit": lineage_history_limit,
      }
    ),
    ingestion_job_filters=_clean_operator_lineage_pack_filters(
      {
        "symbol": symbol,
        "timeframe": timeframe,
        "operation": operation,
        "status": status,
        "limit": ingestion_job_limit,
      }
    ),
    lineage_history_count=len(lineage_records),
    ingestion_job_count=len(ingestion_records),
    lineage_history=lineage_records,
    ingestion_jobs=ingestion_records,
  )
  return replace(pack, content=render_operator_lineage_drill_evidence_pack_content(pack))


def serialize_operator_lineage_drill_evidence_pack(
  pack: OperatorLineageDrillEvidencePack,
) -> dict[str, object]:
  return _serialize_operator_lineage_evidence_value(asdict(pack))


def render_operator_lineage_drill_evidence_pack_content(
  pack: OperatorLineageDrillEvidencePack,
) -> str:
  if pack.export_format == "markdown":
    return _render_operator_lineage_drill_evidence_pack_markdown(pack)
  payload = serialize_operator_lineage_drill_evidence_pack(replace(pack, content=""))
  payload.pop("content", None)
  return json.dumps(payload, indent=2, sort_keys=True)


def build_candle_dataset_identity(
  *,
  provider: str,
  venue: str,
  symbol: str,
  timeframe: str,
  candles: list[Candle],
) -> str:
  payload = {
    "schema_version": 1,
    "provider": provider,
    "venue": venue,
    "symbols": [symbol],
    "timeframe": timeframe,
    "candles": [
      [
        _serialize_datetime(candle.timestamp),
        candle.open,
        candle.high,
        candle.low,
        candle.close,
        candle.volume,
      ]
      for candle in candles
    ],
  }
  return f"candles-v1:{_build_digest(payload)}"


def _build_digest(payload: dict) -> str:
  encoded = json.dumps(
    _normalize_json_value(payload),
    separators=(",", ":"),
    sort_keys=True,
  ).encode("utf-8")
  return hashlib.sha256(encoded).hexdigest()


def _serialize_datetime(value: datetime) -> str:
  if value.tzinfo is None:
    return value.replace(tzinfo=UTC).isoformat()
  return value.astimezone(UTC).isoformat()


def _normalize_json_value(value):
  if isinstance(value, dict):
    return {
      key: _normalize_json_value(item)
      for key, item in value.items()
    }
  if isinstance(value, (list, tuple)):
    return [_normalize_json_value(item) for item in value]
  if isinstance(value, bool):
    return value
  if isinstance(value, float) and value.is_integer():
    return int(value)
  return value


def _operator_lineage_history_cutoff(
  *,
  current_time: datetime,
  policy: OperatorLineageEvidenceRetentionPolicy,
  record: MarketDataLineageHistoryRecord,
) -> datetime:
  days = (
    policy.lineage_issue_history_days
    if _is_operator_lineage_issue_history_record(record)
    else policy.lineage_history_days
  )
  return current_time - timedelta(days=days)


def _operator_lineage_ingestion_job_cutoff(
  *,
  current_time: datetime,
  policy: OperatorLineageEvidenceRetentionPolicy,
  job: MarketDataIngestionJobRecord,
) -> datetime:
  days = (
    policy.ingestion_issue_job_days
    if _is_operator_lineage_issue_ingestion_job(job)
    else policy.ingestion_job_days
  )
  return current_time - timedelta(days=days)


def _is_operator_lineage_issue_history_record(record: MarketDataLineageHistoryRecord) -> bool:
  return (
    record.sync_status != "synced"
    or record.failure_count_24h > 0
    or record.gap_window_count > 0
    or record.last_error is not None
    or bool(record.issues)
  )


def _is_operator_lineage_issue_ingestion_job(job: MarketDataIngestionJobRecord) -> bool:
  return job.status != "succeeded" or job.last_error is not None


def _operator_lineage_recorded_at(value: datetime) -> datetime:
  if value.tzinfo is None:
    return value.replace(tzinfo=UTC)
  return value.astimezone(UTC)


def _normalize_operator_lineage_drill_evidence_pack_format(value: str) -> str:
  normalized = value.strip().lower()
  if normalized not in {"json", "markdown"}:
    raise ValueError("Operator lineage drill evidence packs support json or markdown format.")
  return normalized


def _resolve_operator_lineage_pack_value(
  preferred: str | None,
  *candidates: str | None,
) -> str | None:
  if preferred is not None and preferred.strip():
    return preferred.strip()
  values = sorted({candidate.strip() for candidate in candidates if candidate and candidate.strip()})
  if len(values) == 1:
    return values[0]
  return None


def _resolve_operator_lineage_pack_symbols(
  *,
  symbol: str | None,
  lineage_history: tuple[MarketDataLineageHistoryRecord, ...],
  ingestion_jobs: tuple[MarketDataIngestionJobRecord, ...],
) -> tuple[str, ...]:
  if symbol is not None and symbol.strip():
    return (symbol.strip(),)
  symbols = {
    record.symbol.strip()
    for record in lineage_history
    if record.symbol.strip()
  }
  symbols.update(
    job.symbol.strip()
    for job in ingestion_jobs
    if job.symbol.strip()
  )
  return tuple(sorted(symbols))


def _clean_operator_lineage_pack_filters(filters: dict[str, object | None]) -> dict[str, object]:
  return {
    key: value
    for key, value in filters.items()
    if value is not None and (not isinstance(value, str) or bool(value.strip()))
  }


def _serialize_operator_lineage_evidence_value(value):
  if isinstance(value, datetime):
    return _serialize_datetime(_operator_lineage_recorded_at(value))
  if is_dataclass(value):
    return _serialize_operator_lineage_evidence_value(asdict(value))
  if isinstance(value, dict):
    return {
      key: _serialize_operator_lineage_evidence_value(item)
      for key, item in value.items()
    }
  if isinstance(value, (list, tuple)):
    return [
      _serialize_operator_lineage_evidence_value(item)
      for item in value
    ]
  return value


def _render_operator_lineage_drill_evidence_pack_markdown(
  pack: OperatorLineageDrillEvidencePack,
) -> str:
  lines = [
    "# Operator Lineage Drill Evidence Pack",
    "",
    f"- Pack ID: {pack.pack_id}",
    f"- Generated at: {_serialize_optional_datetime(pack.generated_at)}",
    f"- Generated by: {pack.generated_by}",
    f"- Retention expires at: {_serialize_optional_datetime(pack.retention_expires_at)}",
    f"- Scenario: {_format_operator_lineage_pack_label(pack.scenario_key, pack.scenario_label)}",
    f"- Incident ID: {pack.incident_id or 'none'}",
    f"- Final posture: {pack.final_posture}",
    f"- Operator decision: {pack.operator_decision}",
    f"- Venue: {pack.venue or 'unknown'}",
    f"- Symbols: {', '.join(pack.symbols) if pack.symbols else 'unknown'}",
    f"- Timeframe: {pack.timeframe or 'unknown'}",
    f"- Source run ID: {pack.source_run_id or 'none'}",
    f"- Rerun ID: {pack.rerun_id or 'none'}",
    f"- Dataset identity: {pack.dataset_identity or 'none'}",
    f"- Sync checkpoint ID: {pack.sync_checkpoint_id or 'none'}",
    f"- Rerun boundary ID: {pack.rerun_boundary_id or 'none'}",
    f"- Validation claim: {pack.validation_claim or 'unknown'}",
    f"- Rerun validation category: {pack.rerun_validation_category or 'none'}",
    "",
    "## Query Filters",
    "",
    f"- Lineage history: {json.dumps(pack.lineage_history_filters, sort_keys=True)}",
    f"- Ingestion jobs: {json.dumps(pack.ingestion_job_filters, sort_keys=True)}",
    "",
    "## Evidence Counts",
    "",
    f"- Lineage history records: {pack.lineage_history_count}",
    f"- Ingestion jobs: {pack.ingestion_job_count}",
    "",
    "## Lineage History",
    "",
  ]
  if pack.lineage_history:
    lines.extend(
      _format_operator_lineage_pack_history_record(record)
      for record in pack.lineage_history
    )
  else:
    lines.append("- none")
  lines.extend(["", "## Ingestion Jobs", ""])
  if pack.ingestion_jobs:
    lines.extend(
      _format_operator_lineage_pack_ingestion_job(job)
      for job in pack.ingestion_jobs
    )
  else:
    lines.append("- none")
  return "\n".join(lines)


def _format_operator_lineage_pack_label(
  scenario_key: str | None,
  scenario_label: str | None,
) -> str:
  if scenario_key and scenario_label:
    return f"{scenario_key} - {scenario_label}"
  return scenario_label or scenario_key or "none"


def _format_operator_lineage_pack_history_record(
  record: MarketDataLineageHistoryRecord,
) -> str:
  return (
    f"- {record.history_id}: {record.symbol} {record.timeframe} "
    f"{record.sync_status} {record.validation_claim} "
    f"recorded_at={_serialize_optional_datetime(record.recorded_at)}"
  )


def _format_operator_lineage_pack_ingestion_job(
  job: MarketDataIngestionJobRecord,
) -> str:
  return (
    f"- {job.job_id}: {job.symbol} {job.timeframe} "
    f"{job.operation} {job.status} "
    f"finished_at={_serialize_optional_datetime(job.finished_at)}"
  )
