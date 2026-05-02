from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
import json
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request

from fastapi import FastAPI
from fastapi import Header
from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import TypeAdapter
from sqlalchemy import JSON
from sqlalchemy import Column
from sqlalchemy import delete
from sqlalchemy import inspect
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.engine import Engine
from sqlalchemy.engine import make_url

from akra_trader.domain.models import ProviderProvenanceSchedulerSearchDocumentRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchFeedbackRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPlanRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchQueryAnalyticsRecord
from akra_trader.port_contracts.search import ProviderProvenanceSchedulerSearchBackendPort


def _build_engine(database_url: str) -> Engine:
  url = make_url(database_url)
  engine_kwargs = {"pool_pre_ping": True}
  if url.get_backend_name() == "sqlite" and url.database not in {None, "", ":memory:"}:
    Path(url.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
      database_url,
      connect_args={"check_same_thread": False},
      **engine_kwargs,
    )
  return create_engine(database_url, **engine_kwargs)


metadata = MetaData()
provider_provenance_scheduler_search_documents = Table(
  "provider_provenance_scheduler_search_documents",
  metadata,
  Column("record_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_query_analytics = Table(
  "provider_provenance_scheduler_search_query_analytics",
  metadata,
  Column("query_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("query", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_feedback = Table(
  "provider_provenance_scheduler_search_feedback",
  metadata,
  Column("feedback_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("expires_at", String, nullable=True, index=True),
  Column("query_id", String, nullable=False, index=True),
  Column("query", String, nullable=False, index=True),
  Column("occurrence_id", String, nullable=False, index=True),
  Column("signal", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_policy_catalogs = Table(
  "provider_provenance_scheduler_search_moderation_policy_catalogs",
  metadata,
  Column("catalog_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("name", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_policy_catalog_revisions = Table(
  "provider_provenance_scheduler_search_moderation_policy_catalog_revisions",
  metadata,
  Column("revision_id", String, primary_key=True),
  Column("catalog_id", String, nullable=False, index=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_policy_catalog_audits = Table(
  "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("catalog_id", String, nullable=False, index=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("actor_tab_id", String, nullable=True, index=True),
  Column("name", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_plans = Table(
  "provider_provenance_scheduler_search_moderation_plans",
  metadata,
  Column("plan_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("queue_state", String, nullable=False, index=True),
  Column("policy_catalog_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_catalog_governance_policies = Table(
  "provider_provenance_scheduler_search_moderation_catalog_governance_policies",
  metadata,
  Column("governance_policy_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("action_scope", String, nullable=False, index=True),
  Column("name", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions = Table(
  "provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions",
  metadata,
  Column("revision_id", String, primary_key=True),
  Column("governance_policy_id", String, nullable=False, index=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits = Table(
  "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
  metadata,
  Column("audit_id", String, primary_key=True),
  Column("governance_policy_id", String, nullable=False, index=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("recorded_at", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("actor_tab_id", String, nullable=True, index=True),
  Column("name", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_catalog_governance_plans = Table(
  "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
  metadata,
  Column("plan_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("queue_state", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("governance_policy_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies = Table(
  "provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies",
  metadata,
  Column("meta_policy_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("action_scope", String, nullable=False, index=True),
  Column("name", String, nullable=False, index=True),
  Column("payload", JSON, nullable=False),
)
provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans = Table(
  "provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans",
  metadata,
  Column("plan_id", String, primary_key=True),
  Column("scheduler_key", String, nullable=False, index=True),
  Column("created_at", String, nullable=False, index=True),
  Column("updated_at", String, nullable=False, index=True),
  Column("status", String, nullable=False, index=True),
  Column("queue_state", String, nullable=False, index=True),
  Column("action", String, nullable=False, index=True),
  Column("meta_policy_id", String, nullable=True, index=True),
  Column("payload", JSON, nullable=False),
)


class _SchedulerSearchDocumentPruneRequest(BaseModel):
  current_time: datetime


class _SchedulerSearchDocumentPruneResponse(BaseModel):
  deleted_count: int


class _SchedulerSearchDocumentListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchDocumentRecord]


class _SchedulerSearchAnalyticsPruneRequest(BaseModel):
  current_time: datetime


class _SchedulerSearchAnalyticsPruneResponse(BaseModel):
  deleted_count: int


class _SchedulerSearchAnalyticsListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchQueryAnalyticsRecord]


class _SchedulerSearchFeedbackPruneRequest(BaseModel):
  current_time: datetime


class _SchedulerSearchFeedbackPruneResponse(BaseModel):
  deleted_count: int


class _SchedulerSearchFeedbackListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchFeedbackRecord]


class _SchedulerSearchModerationPolicyCatalogListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRecord]


class _SchedulerSearchModerationPolicyCatalogRevisionListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationPolicyCatalogRevisionRecord]


class _SchedulerSearchModerationPolicyCatalogAuditListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditRecord]


class _SchedulerSearchModerationPlanListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationPlanRecord]


class _SchedulerSearchModerationCatalogGovernancePolicyListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRecord]


class _SchedulerSearchModerationCatalogGovernancePolicyRevisionListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyRevisionRecord]


class _SchedulerSearchModerationCatalogGovernancePolicyAuditListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRecord]


class _SchedulerSearchModerationCatalogGovernancePlanListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationCatalogGovernancePlanRecord]


class _SchedulerSearchModerationCatalogGovernanceMetaPolicyListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRecord]


class _SchedulerSearchModerationCatalogGovernanceMetaPlanListResponse(BaseModel):
  items: list[ProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRecord]


def _normalize_service_auth_token(value: str | None) -> str | None:
  if not isinstance(value, str):
    return None
  normalized = value.strip()
  return normalized or None
