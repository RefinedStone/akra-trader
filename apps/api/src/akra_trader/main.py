from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from akra_trader.api import include_routes
from akra_trader.bootstrap import build_container
from akra_trader.config import load_settings


settings = load_settings()
container = build_container(settings)
app = FastAPI(title=settings.app_name)
app.add_middleware(
  CORSMiddleware,
  allow_origins=[settings.cors_origin],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)
include_routes(app, container, settings.api_prefix)
