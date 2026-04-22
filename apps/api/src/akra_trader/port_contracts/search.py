from __future__ import annotations

from datetime import datetime
from typing import Protocol

from akra_trader.domain.models import ProviderProvenanceSchedulerSearchDocumentRecord


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
