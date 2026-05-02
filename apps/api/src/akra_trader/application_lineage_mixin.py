from __future__ import annotations

from akra_trader.application_context import *  # noqa: F403
from akra_trader import application_context as _application_context

globals().update({
  name: getattr(_application_context, name)
  for name in dir(_application_context)
  if name.startswith("_") and not name.startswith("__")
})

class TradingApplicationLineageMixin:
  def rerun_sandbox_from_boundary(self, *, rerun_boundary_id: str) -> RunRecord:
    return self._run_execution_flow.rerun_sandbox_from_boundary(rerun_boundary_id=rerun_boundary_id)
  def rerun_paper_from_boundary(self, *, rerun_boundary_id: str) -> RunRecord:
    return self._run_execution_flow.rerun_paper_from_boundary(rerun_boundary_id=rerun_boundary_id)
  def compare_runs(self, *, run_ids: list[str], intent: str | None = None) -> RunComparison:
    normalized_run_ids = _normalize_run_ids(run_ids)
    if len(normalized_run_ids) < 2:
      raise ValueError("Run comparison requires at least two unique run IDs.")
    resolved_intent = _normalize_comparison_intent(intent)

    runs = self._runs.compare_runs(normalized_run_ids)
    run_by_id = {run.config.run_id: run for run in runs}
    missing_run_ids = [run_id for run_id in normalized_run_ids if run_id not in run_by_id]
    if missing_run_ids:
      raise LookupError(f"Run not found: {', '.join(missing_run_ids)}")

    ordered_runs = [run_by_id[run_id] for run_id in normalized_run_ids]
    baseline_run = ordered_runs[0]
    metric_rows = tuple(
      _build_comparison_metric_row(
        runs=ordered_runs,
        baseline_run=baseline_run,
        intent=resolved_intent,
        key=key,
        label=label,
        unit=unit,
        higher_is_better=higher_is_better,
      )
      for key, label, unit, higher_is_better in COMPARISON_METRICS
    )
    metric_row_by_key = {row.key: row for row in metric_rows}
    ranked_narratives = _rank_comparison_narratives([
      narrative
      for run in ordered_runs[1:]
      if (
        narrative := _build_comparison_narrative(
          baseline_run=baseline_run,
          run=run,
          intent=resolved_intent,
          metric_row_by_key=metric_row_by_key,
        )
      ) is not None
    ])
    return RunComparison(
      requested_run_ids=tuple(normalized_run_ids),
      intent=resolved_intent,
      baseline_run_id=baseline_run.config.run_id,
      runs=tuple(_serialize_comparison_run(run) for run in ordered_runs),
      metric_rows=metric_rows,
      narratives=tuple(ranked_narratives),
    )
  def get_run_surface_capabilities(self) -> RunSurfaceCapabilities:
    return RunSurfaceCapabilities()
  def require_replay_alias_audit_admin_token(
    self,
    token: str | None,
    *,
    scope: str,
  ) -> None:
    require_replay_alias_audit_admin_token_support(
      token,
      scope=scope,
      read_token=self._replay_alias_audit_admin_read_token,
      write_token=self._replay_alias_audit_admin_write_token,
    )
  def require_operator_alert_external_sync_token(self, token: str | None) -> None:
    require_operator_alert_external_sync_token_support(
      token,
      expected_token=self._operator_alert_external_sync_token,
    )
  @staticmethod
  def _parse_optional_iso_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
      return None
    normalized_value = value.strip().replace("Z", "+00:00")
    try:
      parsed = datetime.fromisoformat(normalized_value)
    except ValueError:
      return None
    if parsed.tzinfo is None:
      return parsed.replace(tzinfo=UTC)
    return parsed
  def get_market_data_status(self, timeframe: str) -> MarketDataStatus:
    return self._market_data.get_status(timeframe)
  def list_market_data_lineage_history(
    self,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    sync_status: str | None = None,
    validation_claim: str | None = None,
    limit: int | None = None,
  ):
    return list(
      self._market_data.list_lineage_history(
        timeframe=timeframe,
        symbol=symbol,
        sync_status=sync_status,
        validation_claim=validation_claim,
        limit=limit,
      )
    )
  def list_market_data_ingestion_jobs(
    self,
    *,
    timeframe: str | None = None,
    symbol: str | None = None,
    operation: str | None = None,
    status: str | None = None,
    limit: int | None = None,
  ):
    return list(
      self._market_data.list_ingestion_jobs(
        timeframe=timeframe,
        symbol=symbol,
        operation=operation,
        status=status,
        limit=limit,
      )
    )
