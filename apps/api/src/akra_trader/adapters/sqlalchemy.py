from __future__ import annotations

from akra_trader.adapters.sqlalchemy_schema import *  # noqa: F403
from akra_trader.adapters.sqlalchemy_run_repository_core import SqlAlchemyRunRepositoryCoreMixin
from akra_trader.adapters.sqlalchemy_run_repository_replay_intent import SqlAlchemyRunRepositoryReplayIntentMixin
from akra_trader.adapters.sqlalchemy_run_repository_provider_exports import SqlAlchemyRunRepositoryProviderExportsMixin
from akra_trader.adapters.sqlalchemy_run_repository_stitched_reports import SqlAlchemyRunRepositoryStitchedReportsMixin
from akra_trader.adapters.sqlalchemy_run_repository_narrative_templates import SqlAlchemyRunRepositoryNarrativeTemplatesMixin
from akra_trader.adapters.sqlalchemy_run_repository_governance import SqlAlchemyRunRepositoryGovernanceMixin
from akra_trader.adapters.sqlalchemy_run_repository_maintenance import SqlAlchemyRunRepositoryMaintenanceMixin


class SqlAlchemyRunRepository(
  SqlAlchemyRunRepositoryCoreMixin,
  SqlAlchemyRunRepositoryReplayIntentMixin,
  SqlAlchemyRunRepositoryProviderExportsMixin,
  SqlAlchemyRunRepositoryStitchedReportsMixin,
  SqlAlchemyRunRepositoryNarrativeTemplatesMixin,
  SqlAlchemyRunRepositoryGovernanceMixin,
  SqlAlchemyRunRepositoryMaintenanceMixin,
  RunRepositoryPort,
):
  _terminal_statuses = {RunStatus.COMPLETED, RunStatus.STOPPED, RunStatus.FAILED}
  _adapter = TypeAdapter(RunRecord)
  _replay_alias_adapter = TypeAdapter(ReplayIntentAliasRecord)
  _replay_alias_audit_adapter = TypeAdapter(ReplayIntentAliasAuditRecord)
  _replay_alias_audit_export_artifact_adapter = TypeAdapter(ReplayIntentAliasAuditExportArtifactRecord)
  _replay_alias_audit_export_job_adapter = TypeAdapter(ReplayIntentAliasAuditExportJobRecord)
  _replay_alias_audit_export_job_audit_adapter = TypeAdapter(ReplayIntentAliasAuditExportJobAuditRecord)
  _provider_provenance_export_artifact_adapter = TypeAdapter(ProviderProvenanceExportArtifactRecord)
  _provider_provenance_export_job_adapter = TypeAdapter(ProviderProvenanceExportJobRecord)
  _provider_provenance_export_job_audit_adapter = TypeAdapter(ProviderProvenanceExportJobAuditRecord)
  _provider_provenance_analytics_preset_adapter = TypeAdapter(ProviderProvenanceAnalyticsPresetRecord)
  _provider_provenance_dashboard_view_adapter = TypeAdapter(ProviderProvenanceDashboardViewRecord)
  _provider_provenance_scheduler_stitched_report_view_adapter = TypeAdapter(
    ProviderProvenanceSchedulerStitchedReportViewRecord
  )
  _provider_provenance_scheduler_stitched_report_view_revision_adapter = TypeAdapter(
    ProviderProvenanceSchedulerStitchedReportViewRevisionRecord
  )
  _provider_provenance_scheduler_stitched_report_view_audit_adapter = TypeAdapter(
    ProviderProvenanceSchedulerStitchedReportViewAuditRecord
  )
  _provider_provenance_scheduler_stitched_report_governance_registry_adapter = TypeAdapter(
    ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRecord
  )
  _provider_provenance_scheduler_stitched_report_governance_registry_audit_adapter = TypeAdapter(
    ProviderProvenanceSchedulerStitchedReportGovernanceRegistryAuditRecord
  )
  _provider_provenance_scheduler_stitched_report_governance_registry_revision_adapter = TypeAdapter(
    ProviderProvenanceSchedulerStitchedReportGovernanceRegistryRevisionRecord
  )
  _provider_provenance_scheduled_report_adapter = TypeAdapter(ProviderProvenanceScheduledReportRecord)
  _provider_provenance_scheduler_narrative_template_adapter = TypeAdapter(
    ProviderProvenanceSchedulerNarrativeTemplateRecord
  )
  _provider_provenance_scheduler_narrative_template_revision_adapter = TypeAdapter(
    ProviderProvenanceSchedulerNarrativeTemplateRevisionRecord
  )
  _provider_provenance_scheduler_narrative_registry_adapter = TypeAdapter(
    ProviderProvenanceSchedulerNarrativeRegistryRecord
  )
  _provider_provenance_scheduler_narrative_registry_revision_adapter = TypeAdapter(
    ProviderProvenanceSchedulerNarrativeRegistryRevisionRecord
  )
  _provider_provenance_scheduler_narrative_governance_policy_template_adapter = TypeAdapter(
    ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRecord
  )
  _provider_provenance_scheduler_narrative_governance_policy_template_revision_adapter = TypeAdapter(
    ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateRevisionRecord
  )
  _provider_provenance_scheduler_narrative_governance_policy_template_audit_adapter = TypeAdapter(
    ProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateAuditRecord
  )
  _provider_provenance_scheduler_narrative_governance_policy_catalog_adapter = TypeAdapter(
    ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRecord
  )
  _provider_provenance_scheduler_narrative_governance_policy_catalog_revision_adapter = TypeAdapter(
    ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogRevisionRecord
  )
  _provider_provenance_scheduler_narrative_governance_policy_catalog_audit_adapter = TypeAdapter(
    ProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogAuditRecord
  )
  _provider_provenance_scheduler_narrative_governance_hierarchy_step_template_adapter = TypeAdapter(
    ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRecord
  )
  _provider_provenance_scheduler_narrative_governance_hierarchy_step_template_revision_adapter = TypeAdapter(
    ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateRevisionRecord
  )
  _provider_provenance_scheduler_narrative_governance_hierarchy_step_template_audit_adapter = TypeAdapter(
    ProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateAuditRecord
  )
  _provider_provenance_scheduler_narrative_governance_plan_adapter = TypeAdapter(
    ProviderProvenanceSchedulerNarrativeGovernancePlanRecord
  )
  _provider_provenance_scheduled_report_audit_adapter = TypeAdapter(ProviderProvenanceScheduledReportAuditRecord)
  _provider_provenance_scheduler_health_record_adapter = TypeAdapter(ProviderProvenanceSchedulerHealthRecord)
  _provider_provenance_scheduler_search_document_record_adapter = TypeAdapter(
    ProviderProvenanceSchedulerSearchDocumentRecord
  )


class SqlAlchemyExperimentPresetCatalog(ExperimentPresetCatalogPort):
  _adapter = TypeAdapter(ExperimentPreset)

  def __init__(self, database_url: str) -> None:
    self._database_url = database_url
    self._engine = _build_engine(database_url)
    metadata.create_all(self._engine)
    self._ensure_schema()
    self._backfill_legacy_presets()
    self._upgrade_existing_presets()

  def list_presets(
    self,
    *,
    strategy_id: str | None = None,
    timeframe: str | None = None,
    lifecycle_stage: str | None = None,
  ) -> list[ExperimentPreset]:
    statement = select(experiment_presets.c.payload).order_by(
      experiment_presets.c.updated_at.desc(),
      experiment_presets.c.preset_id.asc(),
    )
    if strategy_id is not None:
      statement = statement.where(experiment_presets.c.strategy_id == strategy_id)
    if timeframe is not None:
      statement = statement.where(experiment_presets.c.timeframe == timeframe)
    if lifecycle_stage is not None:
      statement = statement.where(experiment_presets.c.lifecycle_stage == lifecycle_stage)
    with self._engine.connect() as connection:
      rows = connection.execute(statement).mappings().all()
    return [self._adapter.validate_python(row["payload"]) for row in rows]

  def get_preset(self, preset_id: str) -> ExperimentPreset | None:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(experiment_presets.c.payload).where(experiment_presets.c.preset_id == preset_id)
      ).mappings().first()
    if row is None:
      return None
    return self._adapter.validate_python(row["payload"])

  def save_preset(self, preset: ExperimentPreset) -> ExperimentPreset:
    payload = self._adapter.dump_python(preset, mode="json")
    row = {
      "preset_id": preset.preset_id,
      "strategy_id": preset.strategy_id,
      "timeframe": preset.timeframe,
      "lifecycle_stage": preset.lifecycle.stage,
      "updated_at": preset.updated_at.isoformat(),
      "payload": payload,
    }
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(experiment_presets.c.preset_id).where(experiment_presets.c.preset_id == preset.preset_id)
      ).first()
      if existing is None:
        connection.execute(insert(experiment_presets).values(**row))
      else:
        connection.execute(
          update(experiment_presets)
          .where(experiment_presets.c.preset_id == preset.preset_id)
          .values(**row)
        )
    return preset

  def _ensure_schema(self) -> None:
    with self._engine.begin() as connection:
      existing_columns = {
        column["name"]
        for column in inspect(self._engine).get_columns("experiment_presets")
      }
      if "lifecycle_stage" not in existing_columns:
        connection.exec_driver_sql(
          "ALTER TABLE experiment_presets ADD COLUMN lifecycle_stage TEXT NOT NULL DEFAULT 'draft'"
        )
      for index_name, column_name in (
        ("ix_experiment_presets_strategy_id", "strategy_id"),
        ("ix_experiment_presets_timeframe", "timeframe"),
        ("ix_experiment_presets_lifecycle_stage", "lifecycle_stage"),
        ("ix_experiment_presets_updated_at", "updated_at"),
      ):
        connection.exec_driver_sql(
          f"CREATE INDEX IF NOT EXISTS {index_name} ON experiment_presets ({column_name})"
        )

  def _backfill_legacy_presets(self) -> None:
    with self._engine.begin() as connection:
      existing_ids = {
        row["preset_id"]
        for row in connection.execute(select(experiment_presets.c.preset_id)).mappings().all()
      }
      rows = connection.execute(
        select(
          run_records.c.preset_id,
          run_records.c.strategy_id,
          run_records.c.benchmark_family,
          run_records.c.payload,
        )
        .where(run_records.c.preset_id.is_not(None))
        .order_by(run_records.c.started_at.desc(), run_records.c.run_id.desc())
      ).mappings().all()
      for row in rows:
        preset_id = row["preset_id"]
        if preset_id in existing_ids:
          continue
        payload = row["payload"] or {}
        config_payload = payload.get("config") or {}
        provenance_payload = payload.get("provenance") or {}
        experiment_payload = provenance_payload.get("experiment") or {}
        preset = ExperimentPreset(
          preset_id=preset_id,
          name=preset_id,
          description="Migrated from legacy run metadata.",
          strategy_id=row["strategy_id"] or config_payload.get("strategy_id"),
          timeframe=config_payload.get("timeframe"),
          benchmark_family=row["benchmark_family"] or experiment_payload.get("benchmark_family"),
          tags=tuple(
            tag
            for tag in experiment_payload.get("tags", ())
            if isinstance(tag, str) and tag
          ),
          parameters={},
          lifecycle=ExperimentPreset.Lifecycle(
            stage="draft",
            updated_at=_coerce_datetime(payload.get("started_at")) or datetime.now(UTC),
            updated_by="system",
            last_action="migrated",
            history=(
              ExperimentPreset.LifecycleEvent(
                action="migrated",
                actor="system",
                reason="legacy_run_metadata_migration",
                occurred_at=_coerce_datetime(payload.get("started_at")) or datetime.now(UTC),
                from_stage=None,
                to_stage="draft",
              ),
            ),
          ),
          revisions=(
            _build_preset_revision(
              preset_id=preset_id,
              revision_number=1,
              action="migrated",
              actor="system",
              reason="legacy_run_metadata_migration",
              occurred_at=_coerce_datetime(payload.get("started_at")) or datetime.now(UTC),
              name=preset_id,
              description="Migrated from legacy run metadata.",
              strategy_id=row["strategy_id"] or config_payload.get("strategy_id"),
              timeframe=config_payload.get("timeframe"),
              benchmark_family=row["benchmark_family"] or experiment_payload.get("benchmark_family"),
              tags=tuple(
                tag
                for tag in experiment_payload.get("tags", ())
                if isinstance(tag, str) and tag
              ),
              parameters=(
                deepcopy(config_payload.get("parameters"))
                if isinstance(config_payload.get("parameters"), dict)
                else {}
              ),
            ),
          ),
          created_at=_coerce_datetime(payload.get("started_at")) or datetime.now(UTC),
          updated_at=_coerce_datetime(payload.get("started_at")) or datetime.now(UTC),
        )
        connection.execute(
          insert(experiment_presets).values(
            preset_id=preset.preset_id,
            strategy_id=preset.strategy_id,
            timeframe=preset.timeframe,
            lifecycle_stage=preset.lifecycle.stage,
            updated_at=preset.updated_at.isoformat(),
            payload=self._adapter.dump_python(preset, mode="json"),
          )
        )
        existing_ids.add(preset_id)

  def _upgrade_existing_presets(self) -> None:
    with self._engine.begin() as connection:
      rows = connection.execute(
        select(
          experiment_presets.c.preset_id,
          experiment_presets.c.payload,
          experiment_presets.c.updated_at,
        )
      ).mappings().all()
      for row in rows:
        payload = row["payload"] or {}
        if "parameters" in payload and "lifecycle" in payload and "revisions" in payload:
          continue
        preset = self._adapter.validate_python(payload)
        updated_at = _coerce_datetime(payload.get("updated_at")) or _coerce_datetime(row["updated_at"]) or datetime.now(UTC)
        created_at = _coerce_datetime(payload.get("created_at")) or updated_at
        parameters = deepcopy(payload.get("parameters", preset.parameters))
        if "lifecycle" in payload:
          lifecycle = preset.lifecycle
        else:
          lifecycle = ExperimentPreset.Lifecycle(
            stage="draft",
            updated_at=updated_at,
            updated_by="system",
            last_action="migrated",
            history=(
              ExperimentPreset.LifecycleEvent(
                action="migrated",
                actor="system",
                reason="preset_catalog_schema_upgrade",
                occurred_at=updated_at,
                from_stage=None,
                to_stage="draft",
              ),
            ),
          )
        revisions = preset.revisions
        if not revisions:
          lifecycle_event = lifecycle.history[0] if lifecycle.history else None
          revisions = (
            _build_preset_revision(
              preset_id=preset.preset_id,
              revision_number=1,
              action=(lifecycle_event.action if lifecycle_event is not None else "migrated"),
              actor=(lifecycle_event.actor if lifecycle_event is not None else "system"),
              reason=(
                lifecycle_event.reason
                if lifecycle_event is not None
                else "preset_catalog_schema_upgrade"
              ),
              occurred_at=(
                lifecycle_event.occurred_at
                if lifecycle_event is not None
                else created_at
              ),
              name=preset.name,
              description=preset.description,
              strategy_id=preset.strategy_id,
              timeframe=preset.timeframe,
              benchmark_family=preset.benchmark_family,
              tags=preset.tags,
              parameters=parameters,
            ),
          )
        upgraded = replace(
          preset,
          parameters=parameters,
          lifecycle=lifecycle,
          revisions=revisions,
          created_at=created_at,
          updated_at=updated_at,
        )
        connection.execute(
          update(experiment_presets)
          .where(experiment_presets.c.preset_id == row["preset_id"])
          .values(
            strategy_id=upgraded.strategy_id,
            timeframe=upgraded.timeframe,
            lifecycle_stage=upgraded.lifecycle.stage,
            updated_at=upgraded.updated_at.isoformat(),
            payload=self._adapter.dump_python(upgraded, mode="json"),
          )
        )


def _coerce_datetime(value: str | None) -> datetime | None:
  if not value:
    return None
  try:
    return datetime.fromisoformat(value)
  except ValueError:
    return None


def _build_preset_revision(
  *,
  preset_id: str,
  revision_number: int,
  action: str,
  actor: str,
  reason: str,
  occurred_at: datetime,
  name: str,
  description: str,
  strategy_id: str | None,
  timeframe: str | None,
  benchmark_family: str | None,
  tags: tuple[str, ...],
  parameters: dict,
) -> ExperimentPreset.Revision:
  return ExperimentPreset.Revision(
    revision_id=f"{preset_id}:r{revision_number:04d}",
    actor=(actor or "system").strip() or "system",
    reason=(reason or action).strip() or action,
    created_at=occurred_at,
    action=action,
    name=name,
    description=description,
    strategy_id=strategy_id,
    timeframe=timeframe,
    benchmark_family=benchmark_family,
    tags=tuple(tags),
    parameters=deepcopy(parameters),
  )
