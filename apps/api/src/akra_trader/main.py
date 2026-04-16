from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from akra_trader.api import include_routes
from akra_trader.bootstrap import build_container
from akra_trader.config import Settings
from akra_trader.config import load_settings


def create_app(settings: Settings | None = None) -> FastAPI:
  app_settings = settings or load_settings()
  container = build_container(app_settings)
  app = FastAPI(title=app_settings.app_name)
  app.add_middleware(
    CORSMiddleware,
    allow_origins=[app_settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )
  include_routes(app, container, app_settings.api_prefix)
  return app


app = create_app()
