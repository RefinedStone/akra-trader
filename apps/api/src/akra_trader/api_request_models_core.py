from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import Field

class StrategyRegistrationRequest(BaseModel):
  strategy_id: str
  module_path: str
  class_name: str


class ExperimentPresetRequest(BaseModel):
  name: str
  preset_id: str | None = None
  description: str = ""
  strategy_id: str | None = None
  timeframe: str | None = None
  tags: list[str] = Field(default_factory=list)
  parameters: dict[str, Any] = Field(default_factory=dict)
  benchmark_family: str | None = None


class ExperimentPresetLifecycleActionRequest(BaseModel):
  action: str
  actor: str = "operator"
  reason: str = "manual_preset_lifecycle_action"
  lineage_evidence_pack_id: str | None = None
  lineage_evidence_retention_expires_at: datetime | None = None
  lineage_evidence_summary: str | None = None


class ExperimentPresetUpdateRequest(BaseModel):
  name: str | None = None
  description: str | None = None
  strategy_id: str | None = None
  timeframe: str | None = None
  tags: list[str] | None = None
  parameters: dict[str, Any] | None = None
  benchmark_family: str | None = None
  actor: str = "operator"
  reason: str = "manual_preset_edit"


class ExperimentPresetRevisionRestoreRequest(BaseModel):
  actor: str = "operator"
  reason: str = "manual_preset_revision_restore"


class BacktestRequest(BaseModel):
  strategy_id: str
  symbol: str
  timeframe: str = "5m"
  initial_cash: float = 10_000
  fee_rate: float = 0.001
  slippage_bps: float = 3
  parameters: dict[str, Any] = Field(default_factory=dict)
  start_at: datetime | None = None
  end_at: datetime | None = None
  tags: list[str] = Field(default_factory=list)
  preset_id: str | None = None
  benchmark_family: str | None = None


class SandboxRunRequest(BaseModel):
  strategy_id: str
  symbol: str
  timeframe: str = "5m"
  initial_cash: float = 10_000
  fee_rate: float = 0.001
  slippage_bps: float = 3
  replay_bars: int = 96
  parameters: dict[str, Any] = Field(default_factory=dict)
  tags: list[str] = Field(default_factory=list)
  preset_id: str | None = None
  benchmark_family: str | None = None


class LiveRunRequest(BaseModel):
  strategy_id: str
  symbol: str
  timeframe: str = "5m"
  initial_cash: float = 10_000
  fee_rate: float = 0.001
  slippage_bps: float = 3
  replay_bars: int = 96
  operator_reason: str = "guarded_live_launch"
  parameters: dict[str, Any] = Field(default_factory=dict)
  tags: list[str] = Field(default_factory=list)
  preset_id: str | None = None
  benchmark_family: str | None = None


class GuardedLiveActionRequest(BaseModel):
  actor: str = "operator"
  reason: str = "manual_operator_action"
  lineage_evidence_pack_id: str | None = None
  lineage_evidence_retention_expires_at: datetime | None = None
  lineage_evidence_summary: str | None = None


class GuardedLiveOrderReplaceRequest(GuardedLiveActionRequest):
  price: float = Field(gt=0)
  quantity: float | None = Field(default=None, gt=0)


class ExternalIncidentSyncRequest(BaseModel):
  provider: str
  event_kind: str
  actor: str = "external"
  detail: str = "external_incident_sync"
  alert_id: str | None = None
  external_reference: str | None = None
  workflow_reference: str | None = None
  occurred_at: datetime | None = None
  escalation_level: int | None = Field(default=None, ge=1)
  payload: dict[str, Any] = Field(default_factory=dict)


class ReplayLinkAliasCreateRequest(BaseModel):
  template_key: str
  template_label: str | None = None
  intent: dict[str, Any]
  redaction_policy: str = "full"
  retention_policy: str = "30d"
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class ReplayLinkAliasRevokeRequest(BaseModel):
  source_tab_id: str | None = None
  source_tab_label: str | None = None


class ReplayLinkAliasAuditPruneRequest(BaseModel):
  prune_mode: str = "expired"
  alias_id: str | None = None
  template_key: str | None = None
  action: str | None = None
  retention_policy: str | None = None
  source_tab_id: str | None = None
  search: str | None = None
  recorded_before: datetime | None = None
  include_manual: bool = False


class ReplayLinkAliasAuditExportJobCreateRequest(BaseModel):
  format: str = "json"
  alias_id: str | None = None
  template_key: str | None = None
  action: str | None = None
  retention_policy: str | None = None
  source_tab_id: str | None = None
  search: str | None = None
  requested_by_tab_id: str | None = None
  requested_by_tab_label: str | None = None


class ReplayLinkAliasAuditExportJobPruneRequest(BaseModel):
  prune_mode: str = "expired"
  template_key: str | None = None
  format: str | None = None
  status: str | None = None
  requested_by_tab_id: str | None = None
  search: str | None = None
  created_before: datetime | None = None


class MarketDataLineageEvidenceRetentionPruneRequest(BaseModel):
  dry_run: bool = False
  lineage_history_days: int | None = Field(default=None, ge=1)
  lineage_issue_history_days: int | None = Field(default=None, ge=1)
  ingestion_job_days: int | None = Field(default=None, ge=1)
  ingestion_issue_job_days: int | None = Field(default=None, ge=1)
  protected_history_ids: list[str] = Field(default_factory=list)
  protected_job_ids: list[str] = Field(default_factory=list)


class MarketDataLineageDrillEvidencePackExportRequest(BaseModel):
  format: str = "json"
  scenario_key: str | None = None
  scenario_label: str | None = None
  incident_id: str | None = None
  operator_decision: str = "reviewed"
  final_posture: str = "unresolved"
  venue: str | None = None
  symbol: str | None = None
  timeframe: str | None = None
  sync_status: str | None = None
  validation_claim: str | None = None
  operation: str | None = None
  status: str | None = None
  source_run_id: str | None = None
  rerun_id: str | None = None
  dataset_identity: str | None = None
  sync_checkpoint_id: str | None = None
  rerun_boundary_id: str | None = None
  rerun_validation_category: str | None = None
  generated_by: str = "operator"
  lineage_history_limit: int = Field(default=100, ge=1, le=500)
  ingestion_job_limit: int = Field(default=100, ge=1, le=500)
