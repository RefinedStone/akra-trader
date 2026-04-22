from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from akra_trader.adapters.provider_provenance_search import (
  ProviderProvenanceSchedulerSearchService,
)
from akra_trader.adapters.provider_provenance_search import (
  SqlAlchemyProviderProvenanceSchedulerSearchStore,
)
from akra_trader.adapters.provider_provenance_search import (
  create_provider_provenance_scheduler_search_service_app,
)
from akra_trader.bootstrap import build_default_provider_provenance_scheduler_search_database_url
from akra_trader.config import Settings
from akra_trader.config import load_settings


def create_app(settings: Settings | None = None) -> FastAPI:
  app_settings = settings or load_settings()
  repo_root = Path(__file__).resolve().parents[4]
  store = SqlAlchemyProviderProvenanceSchedulerSearchStore(
    app_settings.provider_provenance_scheduler_search_database_url
    or build_default_provider_provenance_scheduler_search_database_url(repo_root)
  )
  return create_provider_provenance_scheduler_search_service_app(
    service=ProviderProvenanceSchedulerSearchService(store=store),
    auth_token=app_settings.provider_provenance_scheduler_search_service_auth_token,
  )


app = create_app()
