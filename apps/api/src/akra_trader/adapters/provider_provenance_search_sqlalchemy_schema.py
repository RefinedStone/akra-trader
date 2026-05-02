from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
import json
from urllib import error as urllib_error
from urllib import request as urllib_request

from fastapi import FastAPI
from fastapi import Header
from fastapi import HTTPException
from pydantic import TypeAdapter
from sqlalchemy import delete
from sqlalchemy import inspect
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update

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
from akra_trader.adapters.provider_provenance_search_schema import *

class SqlAlchemyProviderProvenanceSchedulerSearchSchemaMixin:
  def _ensure_schema(self) -> None:
    inspector = inspect(self._engine)
    existing_indexes_by_table = {
      table_name: {
        index["name"]
        for index in inspector.get_indexes(table_name)
      }
      for table_name in (
        "provider_provenance_scheduler_search_documents",
        "provider_provenance_scheduler_search_query_analytics",
        "provider_provenance_scheduler_search_feedback",
        "provider_provenance_scheduler_search_moderation_policy_catalogs",
        "provider_provenance_scheduler_search_moderation_policy_catalog_revisions",
        "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
        "provider_provenance_scheduler_search_moderation_plans",
        "provider_provenance_scheduler_search_moderation_catalog_governance_policies",
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions",
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
        "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
        "provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies",
        "provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans",
      )
    }
    index_specs = (
      (
        "provider_provenance_scheduler_search_documents",
        "ix_provider_provenance_scheduler_search_documents_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_documents",
        "ix_provider_provenance_scheduler_search_documents_recorded_at",
        "recorded_at",
      ),
      (
        "provider_provenance_scheduler_search_documents",
        "ix_provider_provenance_scheduler_search_documents_expires_at",
        "expires_at",
      ),
      (
        "provider_provenance_scheduler_search_query_analytics",
        "ix_provider_provenance_scheduler_search_query_analytics_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_query_analytics",
        "ix_provider_provenance_scheduler_search_query_analytics_recorded_at",
        "recorded_at",
      ),
      (
        "provider_provenance_scheduler_search_query_analytics",
        "ix_provider_provenance_scheduler_search_query_analytics_expires_at",
        "expires_at",
      ),
      (
        "provider_provenance_scheduler_search_query_analytics",
        "ix_provider_provenance_scheduler_search_query_analytics_query",
        "query",
      ),
      (
        "provider_provenance_scheduler_search_feedback",
        "ix_provider_provenance_scheduler_search_feedback_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_feedback",
        "ix_provider_provenance_scheduler_search_feedback_recorded_at",
        "recorded_at",
      ),
      (
        "provider_provenance_scheduler_search_feedback",
        "ix_provider_provenance_scheduler_search_feedback_expires_at",
        "expires_at",
      ),
      (
        "provider_provenance_scheduler_search_feedback",
        "ix_provider_provenance_scheduler_search_feedback_query_id",
        "query_id",
      ),
      (
        "provider_provenance_scheduler_search_feedback",
        "ix_provider_provenance_scheduler_search_feedback_query",
        "query",
      ),
      (
        "provider_provenance_scheduler_search_feedback",
        "ix_provider_provenance_scheduler_search_feedback_occurrence_id",
        "occurrence_id",
      ),
      (
        "provider_provenance_scheduler_search_feedback",
        "ix_provider_provenance_scheduler_search_feedback_signal",
        "signal",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalogs",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalogs_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalogs",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalogs_created_at",
        "created_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalogs",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalogs_updated_at",
        "updated_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalogs",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalogs_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalogs",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalogs_name",
        "name",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_revisions",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_revisions_catalog_id",
        "catalog_id",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_revisions",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_revisions_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_revisions",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_revisions_recorded_at",
        "recorded_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_revisions",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_revisions_action",
        "action",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_revisions",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_revisions_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_audits_catalog_id",
        "catalog_id",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_audits_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_audits_recorded_at",
        "recorded_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_audits_action",
        "action",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_audits_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_audits_actor_tab_id",
        "actor_tab_id",
      ),
      (
        "provider_provenance_scheduler_search_moderation_policy_catalog_audits",
        "ix_provider_provenance_scheduler_search_moderation_policy_catalog_audits_name",
        "name",
      ),
      (
        "provider_provenance_scheduler_search_moderation_plans",
        "ix_provider_provenance_scheduler_search_moderation_plans_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_plans",
        "ix_provider_provenance_scheduler_search_moderation_plans_created_at",
        "created_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_plans",
        "ix_provider_provenance_scheduler_search_moderation_plans_updated_at",
        "updated_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_plans",
        "ix_provider_provenance_scheduler_search_moderation_plans_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_plans",
        "ix_provider_provenance_scheduler_search_moderation_plans_queue_state",
        "queue_state",
      ),
      (
        "provider_provenance_scheduler_search_moderation_plans",
        "ix_provider_provenance_scheduler_search_moderation_plans_policy_catalog_id",
        "policy_catalog_id",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policies_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policies_created_at",
        "created_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policies_updated_at",
        "updated_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policies_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policies_action_scope",
        "action_scope",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policies_name",
        "name",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions_governance_policy_id",
        "governance_policy_id",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions_recorded_at",
        "recorded_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions_action",
        "action",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_revisions_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_governance_policy_id",
        "governance_policy_id",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_recorded_at",
        "recorded_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_action",
        "action",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_actor_tab_id",
        "actor_tab_id",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_policy_audits_name",
        "name",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_plans_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_plans_created_at",
        "created_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_plans_updated_at",
        "updated_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_plans_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_plans_queue_state",
        "queue_state",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_plans_action",
        "action",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_plans_governance_policy_id",
        "governance_policy_id",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies_created_at",
        "created_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies_updated_at",
        "updated_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies_action_scope",
        "action_scope",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_meta_policies_name",
        "name",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans_scheduler_key",
        "scheduler_key",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans_created_at",
        "created_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans_updated_at",
        "updated_at",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans_status",
        "status",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans_queue_state",
        "queue_state",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans_action",
        "action",
      ),
      (
        "provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans",
        "ix_provider_provenance_scheduler_search_moderation_catalog_governance_meta_plans_meta_policy_id",
        "meta_policy_id",
      ),
    )
    with self._engine.begin() as connection:
      for table_name, index_name, column_name in index_specs:
        if index_name in existing_indexes_by_table.get(table_name, set()):
          continue
        connection.exec_driver_sql(
          "CREATE INDEX IF NOT EXISTS "
          f"{index_name} ON {table_name} ({column_name})"
        )
