from __future__ import annotations

from datetime import datetime
from typing import Protocol

from akra_trader.domain.models import ProviderProvenanceSchedulerSearchDocumentRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchFeedbackRecord
from akra_trader.domain.models import ProviderProvenanceSchedulerSearchQueryAnalyticsRecord


class ProviderProvenanceSchedulerSearchBackendPort(Protocol):
  @property
  def persistence_mode(self) -> str: ...

  def save_provider_provenance_scheduler_search_document_record(
    self,
    record: ProviderProvenanceSchedulerSearchDocumentRecord,
  ) -> ProviderProvenanceSchedulerSearchDocumentRecord: ...

  def list_provider_provenance_scheduler_search_document_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchDocumentRecord, ...]: ...

  def prune_provider_provenance_scheduler_search_document_records(
    self,
    current_time: datetime,
  ) -> int: ...

  def save_provider_provenance_scheduler_search_query_analytics_record(
    self,
    record: ProviderProvenanceSchedulerSearchQueryAnalyticsRecord,
  ) -> ProviderProvenanceSchedulerSearchQueryAnalyticsRecord: ...

  def list_provider_provenance_scheduler_search_query_analytics_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchQueryAnalyticsRecord, ...]: ...

  def prune_provider_provenance_scheduler_search_query_analytics_records(
    self,
    current_time: datetime,
  ) -> int: ...

  def save_provider_provenance_scheduler_search_feedback_record(
    self,
    record: ProviderProvenanceSchedulerSearchFeedbackRecord,
  ) -> ProviderProvenanceSchedulerSearchFeedbackRecord: ...

  def list_provider_provenance_scheduler_search_feedback_records(
    self,
  ) -> tuple[ProviderProvenanceSchedulerSearchFeedbackRecord, ...]: ...

  def prune_provider_provenance_scheduler_search_feedback_records(
    self,
    current_time: datetime,
  ) -> int: ...
