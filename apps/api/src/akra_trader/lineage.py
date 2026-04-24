from __future__ import annotations

from dataclasses import dataclass
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
from akra_trader.domain.models import OperatorLineageEvidenceRetentionPolicy
from akra_trader.domain.models import OperatorLineageEvidenceRetentionResult
from akra_trader.domain.models import RunRecord


@dataclass(frozen=True)
class RerunValidationAssessment:
  status: str
  category: str
  summary: str


@dataclass(frozen=True)
class OperatorLineageSummary:
  status: str
  posture: str
  title: str
  summary: str
  operator_action: str
  category: str
  validation_claim: str | None = None
  boundary_id: str | None = None
  blocking: bool = False


OPERATOR_LINEAGE_RETENTION_FLOORS = OperatorLineageEvidenceRetentionPolicy()


def build_dataset_boundary_contract(*, lineage: MarketDataLineage | None) -> DatasetBoundaryContract | None:
  if lineage is None:
    return None
  validation_claim = _resolve_validation_claim(lineage)
  boundary_id = (
    lineage.dataset_identity
    if validation_claim == "exact_dataset"
    else lineage.sync_checkpoint_id
    if validation_claim == "checkpoint_window"
    else None
  )
  return DatasetBoundaryContract(
    provider=lineage.provider,
    venue=lineage.venue,
    symbols=lineage.symbols,
    timeframe=lineage.timeframe,
    reproducibility_state=lineage.reproducibility_state,
    validation_claim=validation_claim,
    boundary_id=boundary_id,
    dataset_identity=lineage.dataset_identity,
    sync_checkpoint_id=lineage.sync_checkpoint_id,
    requested_start_at=lineage.requested_start_at,
    requested_end_at=lineage.requested_end_at,
    effective_start_at=lineage.effective_start_at,
    effective_end_at=lineage.effective_end_at,
    candle_count=lineage.candle_count,
  )


def serialize_dataset_boundary_contract(
  contract: DatasetBoundaryContract | None,
) -> dict[str, object] | None:
  if contract is None:
    return None
  return {
    "contract_version": contract.contract_version,
    "provider": contract.provider,
    "venue": contract.venue,
    "symbols": list(contract.symbols),
    "timeframe": contract.timeframe,
    "reproducibility_state": contract.reproducibility_state,
    "validation_claim": contract.validation_claim,
    "boundary_id": contract.boundary_id,
    "dataset_identity": contract.dataset_identity,
    "sync_checkpoint_id": contract.sync_checkpoint_id,
    "requested_start_at": _serialize_optional_datetime(contract.requested_start_at),
    "requested_end_at": _serialize_optional_datetime(contract.requested_end_at),
    "effective_start_at": _serialize_optional_datetime(contract.effective_start_at),
    "effective_end_at": _serialize_optional_datetime(contract.effective_end_at),
    "candle_count": contract.candle_count,
  }


def build_operator_lineage_summary(*, run: RunRecord) -> OperatorLineageSummary | None:
  boundary = build_dataset_boundary_contract(lineage=run.provenance.market_data)
  if boundary is None:
    return None
  category = run.provenance.rerun_validation_category
  if category != "not_rerun":
    summary = run.provenance.rerun_validation_summary or _validation_summary(category)
    status, posture, title, operator_action, blocking = _rerun_operator_summary_shape(category)
    return OperatorLineageSummary(
      status=status,
      posture=posture,
      title=title,
      summary=summary,
      operator_action=operator_action,
      category=category,
      validation_claim=boundary.validation_claim,
      boundary_id=boundary.boundary_id,
      blocking=blocking,
    )
  status, posture, title, summary, operator_action, blocking = _boundary_operator_summary_shape(boundary)
  return OperatorLineageSummary(
    status=status,
    posture=posture,
    title=title,
    summary=summary,
    operator_action=operator_action,
    category=boundary.validation_claim,
    validation_claim=boundary.validation_claim,
    boundary_id=boundary.boundary_id,
    blocking=blocking,
  )


def serialize_operator_lineage_summary(
  summary: OperatorLineageSummary | None,
) -> dict[str, object] | None:
  if summary is None:
    return None
  return {
    "status": summary.status,
    "posture": summary.posture,
    "title": summary.title,
    "summary": summary.summary,
    "operator_action": summary.operator_action,
    "category": summary.category,
    "validation_claim": summary.validation_claim,
    "boundary_id": summary.boundary_id,
    "blocking": summary.blocking,
  }


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


def build_aggregate_dataset_identity(
  *,
  provider: str,
  venue: str,
  timeframe: str,
  symbol_identities: dict[str, str],
) -> str:
  payload = {
    "schema_version": 1,
    "provider": provider,
    "venue": venue,
    "timeframe": timeframe,
    "symbol_identities": [
      {
        "symbol": symbol,
        "dataset_identity": symbol_identities[symbol],
      }
      for symbol in sorted(symbol_identities)
    ],
  }
  return f"dataset-v1:{_build_digest(payload)}"


def build_sync_checkpoint_identity(
  *,
  provider: str,
  venue: str,
  symbol: str,
  timeframe: str,
  candle_count: int,
  first_timestamp: datetime | None,
  last_timestamp: datetime | None,
  latest_ingested_at: datetime | None,
  contiguous_missing_candles: int,
) -> str:
  payload = {
    "schema_version": 1,
    "provider": provider,
    "venue": venue,
    "symbol": symbol,
    "timeframe": timeframe,
    "candle_count": candle_count,
    "first_timestamp": _serialize_optional_datetime(first_timestamp),
    "last_timestamp": _serialize_optional_datetime(last_timestamp),
    "latest_ingested_at": _serialize_optional_datetime(latest_ingested_at),
    "contiguous_missing_candles": contiguous_missing_candles,
  }
  return f"checkpoint-v1:{_build_digest(payload)}"


def build_aggregate_sync_checkpoint_identity(
  *,
  provider: str,
  venue: str,
  timeframe: str,
  symbol_checkpoint_ids: dict[str, str],
) -> str:
  payload = {
    "schema_version": 1,
    "provider": provider,
    "venue": venue,
    "timeframe": timeframe,
    "symbol_checkpoints": [
      {
        "symbol": symbol,
        "sync_checkpoint_id": symbol_checkpoint_ids[symbol],
      }
      for symbol in sorted(symbol_checkpoint_ids)
    ],
  }
  return f"checkpoint-group-v1:{_build_digest(payload)}"


def build_rerun_boundary_identity(
  *,
  lane: str,
  mode: str,
  strategy_id: str,
  strategy_version: str,
  resolved_parameters: dict,
  venue: str,
  symbols: tuple[str, ...],
  timeframe: str,
  initial_cash: float,
  fee_rate: float,
  slippage_bps: float,
  market_data_boundary: DatasetBoundaryContract,
  market_data_symbol_boundaries: dict[str, DatasetBoundaryContract],
  requested_start_at: datetime | None,
  requested_end_at: datetime | None,
  effective_start_at: datetime | None,
  effective_end_at: datetime | None,
  candle_count: int,
  reference_id: str | None = None,
  reference_version: str | None = None,
  integration_mode: str | None = None,
  external_command: tuple[str, ...] = (),
) -> str:
  payload = {
    "schema_version": 1,
    "lane": lane,
    "mode": mode,
    "strategy_id": strategy_id,
    "strategy_version": strategy_version,
    "resolved_parameters": resolved_parameters,
    "venue": venue,
    "symbols": list(symbols),
    "timeframe": timeframe,
    "initial_cash": initial_cash,
    "fee_rate": fee_rate,
    "slippage_bps": slippage_bps,
    "market_data": {
      "boundary": serialize_dataset_boundary_contract(market_data_boundary),
      "symbol_boundaries": [
        {
          "symbol": symbol,
          "boundary": serialize_dataset_boundary_contract(market_data_symbol_boundaries[symbol]),
        }
        for symbol in sorted(market_data_symbol_boundaries)
      ],
      "requested_start_at": _serialize_optional_datetime(requested_start_at),
      "requested_end_at": _serialize_optional_datetime(requested_end_at),
      "effective_start_at": _serialize_optional_datetime(effective_start_at),
      "effective_end_at": _serialize_optional_datetime(effective_end_at),
      "candle_count": candle_count,
    },
    "reference": {
      "reference_id": reference_id,
      "reference_version": reference_version,
      "integration_mode": integration_mode,
      "external_command": list(external_command),
    },
  }
  return f"rerun-v1:{_build_digest(payload)}"


def combine_reproducibility_states(states: list[str]) -> str:
  if not states:
    return "range_only"
  unique_states = set(states)
  if unique_states == {"pinned"}:
    return "pinned"
  if unique_states == {"delegated"}:
    return "delegated"
  if unique_states == {"range_only"}:
    return "range_only"
  return "partial"


def assess_rerun_validation(
  *,
  source_run: RunRecord,
  rerun: RunRecord,
  expected_boundary_id: str,
) -> RerunValidationAssessment:
  source_boundary = build_dataset_boundary_contract(lineage=source_run.provenance.market_data)
  target_boundary = build_dataset_boundary_contract(lineage=rerun.provenance.market_data)
  if rerun.provenance.rerun_boundary_id is None:
    return RerunValidationAssessment(
      status="unavailable",
      category="target_boundary_unavailable",
      summary="Rerun could not build a comparable boundary for validation.",
    )
  if rerun.provenance.rerun_boundary_id == expected_boundary_id:
    category = _matched_validation_category(
      target_boundary.validation_claim if target_boundary is not None else "window_only"
    )
    return RerunValidationAssessment(
      status="matched",
      category=category,
      summary=_validation_summary(category),
    )
  if source_boundary is None:
    return RerunValidationAssessment(
      status="unavailable",
      category="source_boundary_unavailable",
      summary="Source run does not expose a dataset-boundary contract for rerun validation.",
    )
  if target_boundary is None:
    return RerunValidationAssessment(
      status="unavailable",
      category="target_boundary_unavailable",
      summary="Rerun does not expose a dataset-boundary contract for validation.",
    )
  if (
    source_boundary.dataset_identity is not None
    and target_boundary.dataset_identity is not None
    and source_boundary.dataset_identity != target_boundary.dataset_identity
  ):
    return RerunValidationAssessment(
      status="drifted",
      category="dataset_changed",
      summary=_validation_summary("dataset_changed"),
    )
  if (
    source_boundary.sync_checkpoint_id is not None
    and target_boundary.sync_checkpoint_id is not None
    and source_boundary.sync_checkpoint_id != target_boundary.sync_checkpoint_id
  ):
    return RerunValidationAssessment(
      status="drifted",
      category="checkpoint_changed",
      summary=_validation_summary("checkpoint_changed"),
    )
  if source_boundary.validation_claim != target_boundary.validation_claim:
    category = (
      "validation_downgrade"
      if _claim_rank(target_boundary.validation_claim) < _claim_rank(source_boundary.validation_claim)
      else "validation_claim_changed"
    )
    return RerunValidationAssessment(
      status="drifted",
      category=category,
      summary=_validation_summary(category),
    )
  if not _boundary_windows_match(source_boundary, target_boundary):
    return RerunValidationAssessment(
      status="drifted",
      category="window_changed",
      summary=_validation_summary("window_changed"),
    )
  if source_run.config.mode != rerun.config.mode and _execution_contract_matches(source_run, rerun):
    return RerunValidationAssessment(
      status="drifted",
      category="mode_translation",
      summary=_validation_summary("mode_translation"),
    )
  if not _execution_contract_matches(source_run, rerun):
    return RerunValidationAssessment(
      status="drifted",
      category="execution_contract_changed",
      summary=_validation_summary("execution_contract_changed"),
    )
  return RerunValidationAssessment(
    status="drifted",
    category="boundary_mismatch",
    summary=_validation_summary("boundary_mismatch"),
  )


def _build_digest(payload: dict) -> str:
  encoded = json.dumps(_normalize_json_value(payload), separators=(",", ":"), sort_keys=True).encode("utf-8")
  return hashlib.sha256(encoded).hexdigest()


def _serialize_datetime(value: datetime) -> str:
  if value.tzinfo is None:
    return value.replace(tzinfo=UTC).isoformat()
  return value.astimezone(UTC).isoformat()


def _serialize_optional_datetime(value: datetime | None) -> str | None:
  if value is None:
    return None
  return _serialize_datetime(value)


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


def _resolve_validation_claim(lineage: MarketDataLineage) -> str:
  if lineage.reproducibility_state == "delegated":
    return "delegated"
  if lineage.dataset_identity is not None:
    return "exact_dataset"
  if lineage.sync_checkpoint_id is not None:
    return "checkpoint_window"
  return "window_only"


def _matched_validation_category(validation_claim: str) -> str:
  return {
    "exact_dataset": "exact_match",
    "checkpoint_window": "checkpoint_match",
    "delegated": "delegated_match",
    "window_only": "window_match",
  }.get(validation_claim, "window_match")


def _validation_summary(category: str) -> str:
  return {
    "exact_match": "Exact dataset boundary matched the stored rerun boundary.",
    "checkpoint_match": "Checkpoint-anchored dataset boundary matched the stored rerun boundary.",
    "delegated_match": "Delegated dataset boundary matched, but exact market-data validation remains external.",
    "window_match": "Stored market-data window matched, but validation remains limited to the captured range.",
    "mode_translation": "Dataset boundary matched, but the rerun translated it into a different execution mode.",
    "dataset_changed": "Dataset identity changed between the source run and the rerun.",
    "checkpoint_changed": "Sync checkpoint changed between the source run and the rerun.",
    "window_changed": "Requested or effective market-data window changed between the source run and the rerun.",
    "validation_downgrade": "Rerun fell back to a weaker dataset-boundary claim than the source run.",
    "validation_claim_changed": "Rerun used a different dataset-boundary claim than the source run.",
    "execution_contract_changed": "Execution inputs changed outside the dataset-boundary contract.",
    "boundary_mismatch": "Rerun boundary drifted for an uncategorized reason.",
  }.get(category, "Rerun validation finished with an uncategorized boundary result.")


def _boundary_windows_match(
  source: DatasetBoundaryContract,
  target: DatasetBoundaryContract,
) -> bool:
  return (
    source.requested_start_at == target.requested_start_at
    and source.requested_end_at == target.requested_end_at
    and source.effective_start_at == target.effective_start_at
    and source.effective_end_at == target.effective_end_at
    and source.candle_count == target.candle_count
  )


def _execution_contract_matches(source_run: RunRecord, rerun: RunRecord) -> bool:
  return (
    source_run.provenance.lane == rerun.provenance.lane
    and source_run.config.strategy_id == rerun.config.strategy_id
    and source_run.config.strategy_version == rerun.config.strategy_version
    and source_run.config.venue == rerun.config.venue
    and source_run.config.symbols == rerun.config.symbols
    and source_run.config.timeframe == rerun.config.timeframe
    and source_run.config.initial_cash == rerun.config.initial_cash
    and source_run.config.fee_rate == rerun.config.fee_rate
    and source_run.config.slippage_bps == rerun.config.slippage_bps
    and _resolved_parameters(source_run) == _resolved_parameters(rerun)
    and source_run.provenance.reference_id == rerun.provenance.reference_id
    and source_run.provenance.reference_version == rerun.provenance.reference_version
    and source_run.provenance.integration_mode == rerun.provenance.integration_mode
    and source_run.provenance.external_command == rerun.provenance.external_command
  )


def _resolved_parameters(run: RunRecord) -> dict:
  if run.provenance.strategy is not None:
    return run.provenance.strategy.parameter_snapshot.resolved
  return run.config.parameters


def _claim_rank(validation_claim: str) -> int:
  return {
    "delegated": 0,
    "window_only": 1,
    "checkpoint_window": 2,
    "exact_dataset": 3,
  }.get(validation_claim, -1)


def _rerun_operator_summary_shape(category: str) -> tuple[str, str, str, str, bool]:
  mapping = {
    "exact_match": (
      "clear",
      "exact-match",
      "Exact dataset boundary",
      "Safe to use for exact rerun and benchmark claims against this boundary.",
      False,
    ),
    "checkpoint_match": (
      "clear",
      "exact-match",
      "Checkpoint-anchored match",
      "Safe to use for checkpoint-based rerun claims when exact candle digests are not recorded.",
      False,
    ),
    "window_match": (
      "review",
      "drift-aware",
      "Window-only replay",
      "Treat this as drift-aware research. Do not claim an identical replay from this boundary alone.",
      False,
    ),
    "delegated_match": (
      "review",
      "drift-aware",
      "Delegated validation",
      "Keep this in the benchmark lane until the external runtime can prove its dataset boundary.",
      False,
    ),
    "mode_translation": (
      "review",
      "drift-aware",
      "Expected mode translation",
      "Compare behavior as a mode translation, not as an identical rerun.",
      False,
    ),
    "dataset_changed": (
      "blocked",
      "drift-aware",
      "Dataset changed",
      "Block promotion and exact rerun claims until the intended dataset boundary is explicit again.",
      True,
    ),
    "checkpoint_changed": (
      "blocked",
      "drift-aware",
      "Checkpoint changed",
      "Resync or rerun against the intended checkpoint before treating results as comparable.",
      True,
    ),
    "window_changed": (
      "blocked",
      "drift-aware",
      "Window changed",
      "Use the same requested and effective window before comparing results.",
      True,
    ),
    "validation_downgrade": (
      "blocked",
      "drift-aware",
      "Validation downgraded",
      "Do not promote this rerun until it regains the source boundary claim.",
      True,
    ),
    "validation_claim_changed": (
      "blocked",
      "drift-aware",
      "Validation claim changed",
      "Hold promotion and benchmark work until the source and target runs share one boundary claim.",
      True,
    ),
    "execution_contract_changed": (
      "blocked",
      "drift-aware",
      "Execution inputs changed",
      "Use the same execution mode, cash, fees, slippage, strategy version, and resolved params for rerun validation.",
      True,
    ),
    "boundary_mismatch": (
      "blocked",
      "drift-aware",
      "Unclassified boundary drift",
      "Pause promotion and inspect lineage details before continuing.",
      True,
    ),
    "source_boundary_unavailable": (
      "blocked",
      "unresolved",
      "Source boundary unavailable",
      "Pause rerun and promotion work until the source run exposes an explicit dataset boundary.",
      True,
    ),
    "target_boundary_unavailable": (
      "blocked",
      "unresolved",
      "Rerun boundary unavailable",
      "Pause rerun and promotion work until the rerun exposes an explicit dataset boundary.",
      True,
    ),
  }
  return mapping.get(
    category,
    (
      "blocked",
      "unresolved",
      "Unresolved lineage state",
      "Keep the run blocked until the lineage posture is explicit again.",
      True,
    ),
  )


def _boundary_operator_summary_shape(
  boundary: DatasetBoundaryContract,
) -> tuple[str, str, str, str, str, bool]:
  mapping = {
    "exact_dataset": (
      "clear",
      "exact-match",
      "Exact dataset boundary",
      "Run carries an exact dataset identity for its captured market-data window.",
      "Use this run for exact rerun and benchmark claims.",
      False,
    ),
    "checkpoint_window": (
      "clear",
      "exact-match",
      "Checkpoint boundary",
      "Run is anchored to a stable sync checkpoint even though an exact candle digest is not recorded.",
      "Use checkpoint-based reruns when you need a defendable data boundary.",
      False,
    ),
    "window_only": (
      "review",
      "drift-aware",
      "Window-only boundary",
      "Run records the requested and effective window but not a stable dataset identity or checkpoint.",
      "Treat comparisons as drift-aware and avoid identical replay claims.",
      False,
    ),
    "delegated": (
      "review",
      "drift-aware",
      "Delegated boundary",
      "Exact dataset validation remains with the external runtime.",
      "Use this lane for benchmark context until the external runtime can prove its boundary.",
      False,
    ),
  }
  return mapping.get(
    boundary.validation_claim,
    (
      "blocked",
      "unresolved",
      "Unresolved boundary",
      "Run does not expose a defendable dataset boundary.",
      "Pause promotion and rerun work until the boundary is explicit again.",
      True,
    ),
  )
