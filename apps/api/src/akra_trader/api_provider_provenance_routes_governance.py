from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from akra_trader.application import TradingApplication
from akra_trader.api_request_payload_models import *

def register_provider_provenance_governance_routes(router: APIRouter, get_app) -> None:
  def create_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyCreateRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.create_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
        name=request.name,
        description=request.description,
        action_scope=request.action_scope,
        require_approval_note=request.require_approval_note,
        guidance=request.guidance,
        name_prefix=request.name_prefix,
        name_suffix=request.name_suffix,
        description_append=request.description_append,
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
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies",
    create_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy,
    methods=["POST"],
    name="create_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy",
    summary="Create a reusable governance policy for moderation policy catalogs",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policies(
    action_scope: str | None = None,
    search: str | None = None,
    limit: int = 50,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return app.list_provider_provenance_scheduler_search_moderation_catalog_governance_policies(
      action_scope=action_scope,
      search=search,
      limit=limit,
    )

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies",
    list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policies,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policies",
    summary="List reusable governance policies for moderation policy catalogs",
  )

  def update_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
    governance_policy_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyUpdateRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.update_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
        governance_policy_id,
        name=request.name,
        description=request.description,
        action_scope=request.action_scope,
        require_approval_note=request.require_approval_note,
        guidance=request.guidance,
        name_prefix=request.name_prefix,
        name_suffix=request.name_suffix,
        description_append=request.description_append,
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
          else "scheduler_search_moderation_catalog_governance_policy_updated"
        ),
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/{governance_policy_id}",
    update_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy,
    methods=["PATCH"],
    name="update_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy",
    summary="Update a reusable governance policy for moderation policy catalogs",
  )

  def delete_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
    governance_policy_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDeleteRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.delete_provider_provenance_scheduler_search_moderation_catalog_governance_policy(
        governance_policy_id,
        actor_tab_id=request.actor_tab_id,
        actor_tab_label=request.actor_tab_label,
        reason=(
          request.reason
          if isinstance(request.reason, str) and request.reason.strip()
          else "scheduler_search_moderation_catalog_governance_policy_deleted"
        ),
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/{governance_policy_id}/delete",
    delete_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy,
    methods=["POST"],
    name="delete_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy",
    summary="Delete a reusable governance policy for moderation policy catalogs",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions(
    governance_policy_id: str,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions(
        governance_policy_id
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/{governance_policy_id}/revisions",
    list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions",
    summary="List moderation catalog governance policy revisions",
  )

  def restore_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
    governance_policy_id: str,
    revision_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRestoreRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.restore_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision(
        governance_policy_id,
        revision_id,
        actor_tab_id=request.actor_tab_id,
        actor_tab_label=request.actor_tab_label,
        reason=(
          request.reason
          if isinstance(request.reason, str) and request.reason.strip()
          else "scheduler_search_moderation_catalog_governance_policy_revision_restored"
        ),
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/{governance_policy_id}/revisions/{revision_id}/restore",
    restore_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision,
    methods=["POST"],
    name="restore_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revision",
    summary="Restore a moderation catalog governance policy revision",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits(
    governance_policy_id: str | None = None,
    action: str | None = None,
    actor_tab_id: str | None = None,
    search: str | None = None,
    limit: int = 50,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return app.list_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits(
      governance_policy_id=governance_policy_id,
      action=action,
      actor_tab_id=actor_tab_id,
      search=search,
      limit=limit,
    )

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/audits",
    list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
    summary="List moderation catalog governance policy audit records",
  )

  def bulk_govern_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policies(
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkGovernanceRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      result = app.bulk_govern_provider_provenance_scheduler_search_moderation_catalog_governance_policies(
        governance_policy_ids=request.governance_policy_ids,
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
        action_scope=request.action_scope,
        require_approval_note=request.require_approval_note,
        guidance=request.guidance,
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
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-policies/bulk-governance",
    bulk_govern_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policies,
    methods=["POST"],
    name="bulk_govern_operator_provider_provenance_scheduler_search_moderation_catalog_governance_policies",
    summary="Bulk govern moderation catalog governance policies",
  )

  def stage_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanStageRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.stage_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
        catalog_ids=request.catalog_ids,
        action=request.action,
        governance_policy_id=request.governance_policy_id,
        name_prefix=request.name_prefix,
        name_suffix=request.name_suffix,
        description_append=request.description_append,
        default_moderation_status=request.default_moderation_status,
        governance_view=request.governance_view,
        window_days=request.window_days,
        stale_pending_hours=request.stale_pending_hours,
        minimum_score=request.minimum_score,
        require_note=request.require_note,
        actor=request.actor,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-plans",
    stage_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan,
    methods=["POST"],
    name="stage_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan",
    summary="Stage moderation policy catalog governance changes into an approval queue plan",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plans(
    queue_state: str | None = None,
    governance_policy_id: str | None = None,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return app.list_provider_provenance_scheduler_search_moderation_catalog_governance_plans(
      queue_state=queue_state,
      governance_policy_id=governance_policy_id,
    )

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-plans",
    list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plans,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plans",
    summary="List staged moderation policy catalog governance plans",
  )

  def approve_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
    plan_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanApprovalRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.approve_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
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
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-plans/{plan_id}/approve",
    approve_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan,
    methods=["POST"],
    name="approve_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan",
    summary="Approve a staged moderation policy catalog governance plan",
  )

  def apply_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
    plan_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanApplyRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.apply_provider_provenance_scheduler_search_moderation_catalog_governance_plan(
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
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-plans/{plan_id}/apply",
    apply_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan,
    methods=["POST"],
    name="apply_operator_provider_provenance_scheduler_search_moderation_catalog_governance_plan",
    summary="Apply an approved moderation policy catalog governance plan",
  )

  def create_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy(
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyCreateRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.create_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy(
        name=request.name,
        description=request.description,
        action_scope=request.action_scope,
        require_approval_note=request.require_approval_note,
        guidance=request.guidance,
        name_prefix=request.name_prefix,
        name_suffix=request.name_suffix,
        description_append=request.description_append,
        policy_action_scope=request.policy_action_scope,
        policy_require_approval_note=request.policy_require_approval_note,
        policy_guidance=request.policy_guidance,
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
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-policies",
    create_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy,
    methods=["POST"],
    name="create_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policy",
    summary="Create a reusable meta policy for moderation governance policies",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies(
    action_scope: str | None = None,
    search: str | None = None,
    limit: int = 50,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return app.list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies(
      action_scope=action_scope,
      search=search,
      limit=limit,
    )

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-policies",
    list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies",
    summary="List reusable meta policies for moderation governance policies",
  )

  def stage_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanStageRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.stage_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
        governance_policy_ids=request.governance_policy_ids,
        action=request.action,
        meta_policy_id=request.meta_policy_id,
        name_prefix=request.name_prefix,
        name_suffix=request.name_suffix,
        description_append=request.description_append,
        action_scope=request.action_scope,
        require_approval_note=request.require_approval_note,
        guidance=request.guidance,
        default_moderation_status=request.default_moderation_status,
        governance_view=request.governance_view,
        window_days=request.window_days,
        stale_pending_hours=request.stale_pending_hours,
        minimum_score=request.minimum_score,
        require_note=request.require_note,
        actor=request.actor,
        source_tab_id=request.source_tab_id,
        source_tab_label=request.source_tab_label,
      )
    except LookupError as exc:
      raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
      raise HTTPException(status_code=400, detail=str(exc)) from exc

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-plans",
    stage_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan,
    methods=["POST"],
    name="stage_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan",
    summary="Stage moderation governance policy changes into an approval queue plan",
  )

  def list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans(
    queue_state: str | None = None,
    meta_policy_id: str | None = None,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    return app.list_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans(
      queue_state=queue_state,
      meta_policy_id=meta_policy_id,
    )

  router.add_api_route(
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-plans",
    list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans,
    methods=["GET"],
    name="list_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans",
    summary="List staged moderation governance policy plans",
  )

  def approve_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
    plan_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanApprovalRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.approve_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
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
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-plans/{plan_id}/approve",
    approve_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan,
    methods=["POST"],
    name="approve_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan",
    summary="Approve a staged moderation governance policy plan",
  )

  def apply_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
    plan_id: str,
    request: OperatorProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanApplyRequest,
    app: TradingApplication = Depends(get_app),
  ) -> dict[str, Any]:
    try:
      return app.apply_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan(
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
    "/operator/provider-provenance-analytics/scheduler-search/moderation-catalog-governance-meta-plans/{plan_id}/apply",
    apply_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan,
    methods=["POST"],
    name="apply_operator_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plan",
    summary="Apply an approved moderation governance policy plan",
  )
