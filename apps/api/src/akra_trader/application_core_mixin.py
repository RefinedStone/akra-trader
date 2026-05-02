from __future__ import annotations

from akra_trader.application_context import *  # noqa: F403
from akra_trader import application_context as _application_context

globals().update({
  name: getattr(_application_context, name)
  for name in dir(_application_context)
  if name.startswith("_") and not name.startswith("__")
})

class TradingApplicationCoreMixin:
  def __init__(
    self,
    *,
    market_data: MarketDataPort,
    strategies: StrategyCatalogPort,
    references: ReferenceCatalogPort,
    runs: RunRepositoryPort,
    presets: ExperimentPresetCatalogPort | None = None,
    provider_provenance_scheduler_search_backend: ProviderProvenanceSchedulerSearchBackendPort | None = None,
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
    provider_provenance_report_scheduler_enabled: bool = True,
    provider_provenance_report_scheduler_interval_seconds: int = 60,
    provider_provenance_report_scheduler_batch_limit: int = 25,
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
    replay_alias_audit_admin_read_token: str | None = None,
    replay_alias_audit_admin_write_token: str | None = None,
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
    self._presets = presets or _EphemeralExperimentPresetCatalog()
    self._strategy_catalog_flow = StrategyCatalogFlow(
      strategies=self._strategies,
      references=self._references,
      presets=self._presets,
      clock=self._clock,
    )
    self._run_execution_flow = RunExecutionFlow(app=self)
    self._runs = runs
    self._provider_provenance_scheduler_search_backend = (
      provider_provenance_scheduler_search_backend
      or EmbeddedProviderProvenanceSchedulerSearchServiceClient(
        ProviderProvenanceSchedulerSearchService(
          store=InMemoryProviderProvenanceSchedulerSearchStore()
        )
      )
    )
    self._guarded_live_state = guarded_live_state or _EphemeralGuardedLiveStateStore()
    self._venue_state = venue_state or UnavailableVenueStateAdapter(self._clock)
    self._venue_execution = venue_execution or UnavailableVenueExecutionAdapter()
    self._operator_alert_delivery = (
      operator_alert_delivery or NoopOperatorAlertDeliveryAdapter()
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
    self._provider_provenance_report_scheduler_enabled = (
      provider_provenance_report_scheduler_enabled
    )
    self._provider_provenance_report_scheduler_interval_seconds = max(
      provider_provenance_report_scheduler_interval_seconds,
      1,
    )
    self._provider_provenance_report_scheduler_batch_limit = max(
      provider_provenance_report_scheduler_batch_limit,
      1,
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
    self._replay_alias_audit_admin_read_token = replay_alias_audit_admin_read_token
    self._replay_alias_audit_admin_write_token = replay_alias_audit_admin_write_token
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
    self._replay_intent_alias_signing_secret = self._load_or_create_replay_intent_alias_signing_secret()
    self._replay_intent_alias_records: dict[str, ReplayIntentAliasRecord] = {}
    self._replay_intent_alias_audit_records: dict[str, ReplayIntentAliasAuditRecord] = {}
    self._replay_intent_alias_audit_export_artifacts: dict[str, ReplayIntentAliasAuditExportArtifactRecord] = {}
    self._replay_intent_alias_audit_export_jobs: dict[str, ReplayIntentAliasAuditExportJobRecord] = {}
    self._replay_intent_alias_audit_export_job_audit_records: dict[str, ReplayIntentAliasAuditExportJobAuditRecord] = {}
    self._provider_provenance_export_artifacts: dict[str, ProviderProvenanceExportArtifactRecord] = {}
    self._provider_provenance_export_jobs: dict[str, ProviderProvenanceExportJobRecord] = {}
    self._provider_provenance_export_job_audit_records: dict[str, ProviderProvenanceExportJobAuditRecord] = {}
    self._provider_provenance_analytics_presets: dict[str, ProviderProvenanceAnalyticsPresetRecord] = {}
    self._provider_provenance_dashboard_views: dict[str, ProviderProvenanceDashboardViewRecord] = {}
    self._provider_provenance_scheduler_stitched_report_views: dict[
      str,
      ProviderProvenanceSchedulerStitchedReportViewRecord,
    ] = {}
    self._provider_provenance_scheduler_stitched_report_view_revisions: dict[
      str,
      ProviderProvenanceSchedulerStitchedReportViewRevisionRecord,
    ] = {}
    self._provider_provenance_scheduler_stitched_report_view_audit_records: dict[
      str,
      ProviderProvenanceSchedulerStitchedReportViewAuditRecord,
    ] = {}
    self._provider_provenance_scheduler_stitched_report_governance_registries: dict[
      str,
      ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord,
    ] = {}
    self._provider_provenance_scheduler_stitched_report_governance_registry_audit_records: dict[
      str,
      ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord,
    ] = {}
    self._provider_provenance_scheduler_stitched_report_governance_registry_revisions: dict[
      str,
      ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord,
    ] = {}
    self._provider_provenance_scheduled_reports: dict[str, ProviderProvenanceScheduledReportRecord] = {}
    self._provider_provenance_scheduler_narrative_templates: dict[
      str,
      ProviderProvenanceSchedulerNarrativeTemplateRecord,
    ] = {}
    self._provider_provenance_scheduler_narrative_template_revisions: dict[
      str,
      ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord,
    ] = {}
    self._provider_provenance_scheduler_narrative_registry: dict[
      str,
      ProviderProvenanceSchedulerNarrativeRegistryRecord,
    ] = {}
    self._provider_provenance_scheduler_narrative_registry_revisions: dict[
      str,
      ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord,
    ] = {}
    self._provider_provenance_scheduler_narrative_governance_policy_templates: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
    ] = {}
    self._provider_provenance_scheduler_narrative_governance_policy_template_revisions: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord,
    ] = {}
    self._provider_provenance_scheduler_narrative_governance_policy_template_audit_records: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord,
    ] = {}
    self._provider_provenance_scheduler_stitched_report_governance_policy_templates: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord,
    ] = {}
    self._provider_provenance_scheduler_stitched_report_governance_policy_template_revisions: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord,
    ] = {}
    self._provider_provenance_scheduler_stitched_report_governance_policy_template_audit_records: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord,
    ] = {}
    self._provider_provenance_scheduler_narrative_governance_hierarchy_step_templates: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord,
    ] = {}
    self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revisions: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord,
    ] = {}
    self._provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_records: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord,
    ] = {}
    self._provider_provenance_scheduler_narrative_governance_policy_catalogs: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
    ] = {}
    self._provider_provenance_scheduler_narrative_governance_policy_catalog_revisions: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord,
    ] = {}
    self._provider_provenance_scheduler_narrative_governance_policy_catalog_audit_records: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord,
    ] = {}
    self._provider_provenance_scheduler_stitched_report_governance_policy_catalogs: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord,
    ] = {}
    self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_revisions: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord,
    ] = {}
    self._provider_provenance_scheduler_stitched_report_governance_policy_catalog_audit_records: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord,
    ] = {}
    self._provider_provenance_scheduler_narrative_governance_plans: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePlanRecord,
    ] = {}
    self._provider_provenance_scheduler_stitched_report_governance_plans: dict[
      str,
      ProviderProvenanceSchedulerNarrativeGovernancePlanRecord,
    ] = {}
    self._provider_provenance_scheduled_report_audit_records: dict[str, ProviderProvenanceScheduledReportAuditRecord] = {}
    self._provider_provenance_scheduler_health_records: dict[str, ProviderProvenanceSchedulerHealthRecord] = {}
    self._provider_provenance_scheduler_health_lock = Lock()
    self._provider_provenance_scheduler_health = ProviderProvenanceSchedulerHealth(
      generated_at=self._clock(),
      enabled=self._provider_provenance_report_scheduler_enabled,
      status="starting" if self._provider_provenance_report_scheduler_enabled else "disabled",
      summary=(
        "Background scheduler has not completed a provider provenance automation cycle yet."
        if self._provider_provenance_report_scheduler_enabled
        else "Background scheduler is disabled for provider provenance automation."
      ),
      interval_seconds=self._provider_provenance_report_scheduler_interval_seconds,
      batch_limit=self._provider_provenance_report_scheduler_batch_limit,
    )
  def list_strategies(
    self,
    *,
    lane: str | None = None,
    lifecycle_stage: str | None = None,
    version: str | None = None,
  ) -> list[StrategyMetadata]:
    return self._strategy_catalog_flow.list_strategies(
      lane=lane,
      lifecycle_stage=lifecycle_stage,
      version=version,
    )
  def list_references(self) -> list[ReferenceSource]:
    return self._strategy_catalog_flow.list_references()
  def register_strategy(self, *, strategy_id: str, module_path: str, class_name: str) -> StrategyMetadata:
    return self._strategy_catalog_flow.register_strategy(
      strategy_id=strategy_id,
      module_path=module_path,
      class_name=class_name,
    )
  def list_presets(
    self,
    *,
    strategy_id: str | None = None,
    timeframe: str | None = None,
    lifecycle_stage: str | None = None,
  ) -> list[ExperimentPreset]:
    return self._strategy_catalog_flow.list_presets(
      strategy_id=strategy_id,
      timeframe=timeframe,
      lifecycle_stage=lifecycle_stage,
    )
  def get_preset(self, *, preset_id: str) -> ExperimentPreset:
    return self._strategy_catalog_flow.get_preset(preset_id=preset_id)
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
    return self._strategy_catalog_flow.create_preset(
      name=name,
      preset_id=preset_id,
      description=description,
      strategy_id=strategy_id,
      timeframe=timeframe,
      tags=tags,
      parameters=parameters,
      benchmark_family=benchmark_family,
    )
  def update_preset(
    self,
    *,
    preset_id: str,
    changes: dict[str, Any],
    actor: str = "operator",
    reason: str = "manual_preset_edit",
  ) -> ExperimentPreset:
    return self._strategy_catalog_flow.update_preset(
      preset_id=preset_id,
      changes=changes,
      actor=actor,
      reason=reason,
    )
  def list_preset_revisions(
    self,
    *,
    preset_id: str,
  ) -> tuple[ExperimentPreset.Revision, ...]:
    return self._strategy_catalog_flow.list_preset_revisions(
      preset_id=preset_id,
    )
  def restore_preset_revision(
    self,
    *,
    preset_id: str,
    revision_id: str,
    actor: str = "operator",
    reason: str = "manual_preset_revision_restore",
  ) -> ExperimentPreset:
    return self._strategy_catalog_flow.restore_preset_revision(
      preset_id=preset_id,
      revision_id=revision_id,
      actor=actor,
      reason=reason,
    )
  def apply_preset_lifecycle_action(
    self,
    *,
    preset_id: str,
    action: str,
    actor: str = "operator",
    reason: str = "manual_preset_lifecycle_action",
    lineage_evidence_pack_id: str | None = None,
    lineage_evidence_retention_expires_at: datetime | None = None,
    lineage_evidence_summary: str | None = None,
  ) -> ExperimentPreset:
    return self._strategy_catalog_flow.apply_preset_lifecycle_action(
      preset_id=preset_id,
      action=action,
      actor=actor,
      reason=reason,
      lineage_evidence_pack_id=lineage_evidence_pack_id,
      lineage_evidence_retention_expires_at=lineage_evidence_retention_expires_at,
      lineage_evidence_summary=lineage_evidence_summary,
    )
  def _get_preset_or_raise(self, preset_id: str) -> ExperimentPreset:
    return self._strategy_catalog_flow.get_preset_or_raise(preset_id)
  def _validate_preset_strategy(self, *, strategy_id: str | None) -> None:
    self._strategy_catalog_flow.validate_preset_strategy(strategy_id=strategy_id)
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
    return self._run_execution_flow.list_runs(
      mode,
      strategy_id=strategy_id,
      strategy_version=strategy_version,
      rerun_boundary_id=rerun_boundary_id,
      preset_id=preset_id,
      benchmark_family=benchmark_family,
      dataset_identity=dataset_identity,
      tags=tags,
    )
  def get_run(self, run_id: str) -> RunRecord | None:
    return self._run_execution_flow.get_run(run_id)
  def rerun_backtest_from_boundary(self, *, rerun_boundary_id: str) -> RunRecord:
    return self._run_execution_flow.rerun_backtest_from_boundary(rerun_boundary_id=rerun_boundary_id)
