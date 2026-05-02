from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from akra_trader.application import TradingApplication
from akra_trader.api_request_payload_models import *

def register_provider_provenance_export_and_search_routes(router: APIRouter, get_app) -> None:
  def reconstruct_operator_provider_provenance_scheduler_health_export(
    request: OperatorProviderProvenanceSchedulerHistoricalExportRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.reconstruct_provider_provenance_scheduler_health_export(
        alert_category=request.alert_category,
        detected_at=request.detected_at,
        resolved_at=request.resolved_at,
        narrative_mode=request.narrative_mode,
        export_format=request.format,
        history_limit=request.history_limit,
        drilldown_history_limit=request.drilldown_history_limit,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, RuntimeError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-health/reconstruct-export",
    reconstruct_operator_provider_provenance_scheduler_health_export,
    methods=["POST"],
    name="reconstruct_operator_provider_provenance_scheduler_health_export",
    summary="Reconstruct provider provenance scheduler health export for a historical alert row",
  )

  def export_operator_provider_provenance_scheduler_stitched_narrative_report(
    request: OperatorProviderProvenanceSchedulerNarrativeReportRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.export_provider_provenance_scheduler_stitched_narrative_report(
        category=request.alert_category,
        status=request.status,
        narrative_facet=request.narrative_facet,
        search=request.search,
        offset=request.offset,
        occurrence_limit=request.occurrence_limit,
        export_format=request.format,
        history_limit=request.history_limit,
        drilldown_history_limit=request.drilldown_history_limit,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, RuntimeError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-alerts/report-export",
    export_operator_provider_provenance_scheduler_stitched_narrative_report,
    methods=["POST"],
    name="export_operator_provider_provenance_scheduler_stitched_narrative_report",
    summary="Export a stitched multi-occurrence scheduler narrative report",
  )

  def record_operator_provider_provenance_scheduler_search_feedback(
    request: OperatorProviderProvenanceSchedulerSearchFeedbackRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.record_provider_provenance_scheduler_alert_search_feedback(
        query_id=request.query_id,
        query=request.query,
        occurrence_id=request.occurrence_id,
        signal=request.signal,
        matched_fields=tuple(request.matched_fields),
        semantic_concepts=tuple(request.semantic_concepts),
        operator_hits=tuple(request.operator_hits),
        lexical_score=request.lexical_score,
        semantic_score=request.semantic_score,
        operator_score=request.operator_score,
        score=request.score,
        ranking_reason=request.ranking_reason,
        note=request.note,
        actor=request.actor,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-alerts/search-feedback",
    record_operator_provider_provenance_scheduler_search_feedback,
    methods=["POST"],
    name="record_operator_provider_provenance_scheduler_search_feedback",
    summary="Record operator feedback for scheduler search ranking",
  )

  def get_operator_provider_provenance_scheduler_search_dashboard(
    search: str | None = None,
    moderation_status: str | None = None,
    signal: str | None = None,
    governance_view: str | None = None,
    window_days: int = 30,
    stale_pending_hours: int = 24,
    query_limit: int = 12,
    feedback_limit: int = 20,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.get_provider_provenance_scheduler_search_dashboard(
        search=search,
        moderation_status=moderation_status,
        signal=signal,
        governance_view=governance_view,
        window_days=window_days,
        stale_pending_hours=stale_pending_hours,
        query_limit=query_limit,
        feedback_limit=feedback_limit,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/dashboard",
    get_operator_provider_provenance_scheduler_search_dashboard,
    methods=["GET"],
    name="get_operator_provider_provenance_scheduler_search_dashboard",
    summary="List scheduler query analytics and feedback moderation data",
  )

  def moderate_operator_provider_provenance_scheduler_search_feedback(
    feedback_id: str,
    request: OperatorProviderProvenanceSchedulerSearchFeedbackModerationRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.moderate_provider_provenance_scheduler_search_feedback(
        feedback_id=feedback_id,
        moderation_status=request.moderation_status,
        actor=request.actor,
        note=request.note,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/feedback/{feedback_id}/moderate",
    moderate_operator_provider_provenance_scheduler_search_feedback,
    methods=["POST"],
    name="moderate_operator_provider_provenance_scheduler_search_feedback",
    summary="Moderate scheduler search feedback before it influences ranking",
  )

  def moderate_operator_provider_provenance_scheduler_search_feedback_batch(
    request: OperatorProviderProvenanceSchedulerSearchFeedbackBatchModerationRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.moderate_provider_provenance_scheduler_search_feedback_batch(
        feedback_ids=tuple(request.feedback_ids),
        moderation_status=request.moderation_status,
        actor=request.actor,
        note=request.note,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/feedback/batch-moderate",
    moderate_operator_provider_provenance_scheduler_search_feedback_batch,
    methods=["POST"],
    name="moderate_operator_provider_provenance_scheduler_search_feedback_batch",
    summary="Moderate scheduler search feedback in batch",
  )

  def create_operator_provider_provenance_scheduler_search_moderation_policy_catalog(
    request: OperatorProviderProvenanceSchedulerSearchModerationPolicyCatalogCreateRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.create_provider_provenance_scheduler_search_moderation_policy_catalog(
        name=request.name,
        description=request.description,
        default_moderation_status=request.default_moderation_status,
        governance_view=request.governance_view,
        window_days=request.window_days,
        stale_pending_hours=request.stale_pending_hours,
        minimum_score=request.minimum_score,
        require_note=request.require_note,
        created_by_tab_id=request.created_by_tab_id,
        created_by_tab_label=request.created_by_tab_label,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs",
    create_operator_provider_provenance_scheduler_search_moderation_policy_catalog,
    methods=["POST"],
    name="create_operator_provider_provenance_scheduler_search_moderation_policy_catalog",
    summary="Create a reusable moderation policy catalog for scheduler search governance",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_policy_catalogs(
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return app.list_provider_provenance_scheduler_search_moderation_policy_catalogs()

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs",
    list_operator_provider_provenance_scheduler_search_moderation_policy_catalogs,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_policy_catalogs",
    summary="List scheduler search moderation policy catalogs",
  )

  def update_operator_provider_provenance_scheduler_search_moderation_policy_catalog(
    catalog_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationPolicyCatalogUpdateRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.update_provider_provenance_scheduler_search_moderation_policy_catalog(
        catalog_id,
        name=request.name,
        description=request.description,
        default_moderation_status=request.default_moderation_status,
        governance_view=request.governance_view,
        window_days=request.window_days,
        stale_pending_hours=request.stale_pending_hours,
        minimum_score=request.minimum_score,
        require_note=request.require_note,
        actor_tab_id=request.actor_tab_id,
        actor_tab_label=request.actor_tab_label,
        reason=(
          request.reason
          if isinstance(request.reason, str) and request.reason.strip()
          else "scheduler_search_moderation_policy_catalog_updated"
        ),
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/{catalog_id}",
    update_operator_provider_provenance_scheduler_search_moderation_policy_catalog,
    methods=["PATCH"],
    name="update_operator_provider_provenance_scheduler_search_moderation_policy_catalog",
    summary="Update a scheduler search moderation policy catalog",
  )

  def delete_operator_provider_provenance_scheduler_search_moderation_policy_catalog(
    catalog_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationPolicyCatalogDeleteRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.delete_provider_provenance_scheduler_search_moderation_policy_catalog(
        catalog_id,
        actor_tab_id=request.actor_tab_id,
        actor_tab_label=request.actor_tab_label,
        reason=(
          request.reason
          if isinstance(request.reason, str) and request.reason.strip()
          else "scheduler_search_moderation_policy_catalog_deleted"
        ),
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/{catalog_id}/delete",
    delete_operator_provider_provenance_scheduler_search_moderation_policy_catalog,
    methods=["POST"],
    name="delete_operator_provider_provenance_scheduler_search_moderation_policy_catalog",
    summary="Delete a scheduler search moderation policy catalog",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_policy_catalog_revisions(
    catalog_id: str,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.list_provider_provenance_scheduler_search_moderation_policy_catalog_revisions(
        catalog_id
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/{catalog_id}/revisions",
    list_operator_provider_provenance_scheduler_search_moderation_policy_catalog_revisions,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_policy_catalog_revisions",
    summary="List scheduler search moderation policy catalog revisions",
  )

  def restore_operator_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
    catalog_id: str,
    revision_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRestoreRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.restore_provider_provenance_scheduler_search_moderation_policy_catalog_revision(
        catalog_id,
        revision_id,
        actor_tab_id=request.actor_tab_id,
        actor_tab_label=request.actor_tab_label,
        reason=(
          request.reason
          if isinstance(request.reason, str) and request.reason.strip()
          else "scheduler_search_moderation_policy_catalog_revision_restored"
        ),
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/{catalog_id}/revisions/{revision_id}/restore",
    restore_operator_provider_provenance_scheduler_search_moderation_policy_catalog_revision,
    methods=["POST"],
    name="restore_operator_provider_provenance_scheduler_search_moderation_policy_catalog_revision",
    summary="Restore a scheduler search moderation policy catalog revision",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_policy_catalog_audits(
    catalog_id: str | None = None,
    action: str | None = None,
    actor_tab_id: str | None = None,
    search: str | None = None,
    limit: int = 50,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return app.list_provider_provenance_scheduler_search_moderation_policy_catalog_audits(
      catalog_id=catalog_id,
      action=action,
      actor_tab_id=actor_tab_id,
      search=search,
      limit=limit,
    )

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/audits",
    list_operator_provider_provenance_scheduler_search_moderation_policy_catalog_audits,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_policy_catalog_audits",
    summary="List scheduler search moderation policy catalog audit records",
  )

  def bulk_govern_operator_provider_provenance_scheduler_search_moderation_policy_catalogs(
    request: OperatorProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkGovernanceRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      result = app.bulk_govern_provider_provenance_scheduler_search_moderation_policy_catalogs(
        catalog_ids=request.catalog_ids,
        action=request.action,
        actor_tab_id=request.actor_tab_id,
        actor_tab_label=request.actor_tab_label,
        reason=request.reason,
        name_prefix=request.name_prefix,
        name_suffix=request.name_suffix,
        description_append=request.description_append,
        default_moderation_status=request.default_moderation_status,
        governance_view=request.governance_view,
        window_days=request.window_days,
        stale_pending_hours=request.stale_pending_hours,
        minimum_score=request.minimum_score,
        require_note=request.require_note,
      )
    except ValueError as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
      "item_type": result.item_type,
      "action": result.action,
      "reason": result.reason,
      "requested_count": result.requested_count,
      "applied_count": result.applied_count,
      "skipped_count": result.skipped_count,
      "failed_count": result.failed_count,
      "results": tuple(
        {
          "item_id": entry.item_id,
          "item_name": entry.item_name,
          "outcome": entry.outcome,
          "status": entry.status,
          "current_revision_id": entry.current_revision_id,
          "message": entry.message,
        }
        for entry in result.results
      ),
    }

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-policy-catalogs/bulk-governance",
    bulk_govern_operator_provider_provenance_scheduler_search_moderation_policy_catalogs,
    methods=["POST"],
    name="bulk_govern_operator_provider_provenance_scheduler_search_moderation_policy_catalogs",
    summary="Bulk govern scheduler search moderation policy catalogs",
  )

  def stage_operator_provider_provenance_scheduler_search_moderation_plan(
    request: OperatorProviderProvenanceSchedulerSearchModerationPlanStageRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.stage_provider_provenance_scheduler_search_moderation_plan(
        feedback_ids=tuple(request.feedback_ids),
        policy_catalog_id=request.policy_catalog_id,
        moderation_status=request.moderation_status,
        actor=request.actor,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-plans",
    stage_operator_provider_provenance_scheduler_search_moderation_plan,
    methods=["POST"],
    name="stage_operator_provider_provenance_scheduler_search_moderation_plan",
    summary="Stage scheduler search moderation feedback into an approval queue plan",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_plans(
    queue_state: str | None = None,
    policy_catalog_id: str | None = None,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return app.list_provider_provenance_scheduler_search_moderation_plans(
      queue_state=queue_state,
      policy_catalog_id=policy_catalog_id,
    )

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-plans",
    list_operator_provider_provenance_scheduler_search_moderation_plans,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_plans",
    summary="List staged scheduler search moderation approval queue plans",
  )

  def approve_operator_provider_provenance_scheduler_search_moderation_plan(
    plan_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationPlanApprovalRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.approve_provider_provenance_scheduler_search_moderation_plan(
        plan_id=plan_id,
        actor=request.actor,
        note=request.note,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-plans/{plan_id}/approve",
    approve_operator_provider_provenance_scheduler_search_moderation_plan,
    methods=["POST"],
    name="approve_operator_provider_provenance_scheduler_search_moderation_plan",
    summary="Approve a staged scheduler search moderation plan",
  )

  def apply_operator_provider_provenance_scheduler_search_moderation_plan(
    plan_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationPlanApplyRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.apply_provider_provenance_scheduler_search_moderation_plan(
        plan_id=plan_id,
        actor=request.actor,
        note=request.note,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-plans/{plan_id}/apply",
    apply_operator_provider_provenance_scheduler_search_moderation_plan,
    methods=["POST"],
    name="apply_operator_provider_provenance_scheduler_search_moderation_plan",
    summary="Apply an approved scheduler search moderation plan",
  )
