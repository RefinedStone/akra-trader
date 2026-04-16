from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from akra_trader.api import include_routes
from akra_trader.bootstrap import build_container
from akra_trader.config import Settings
from akra_trader.config import load_settings


def create_app(settings: Settings | None = None) -> FastAPI:
  app_settings = settings or load_settings()
  container = build_container(app_settings)

  @asynccontextmanager
  async def lifespan(_: FastAPI):
    started_jobs = []
    try:
      for job in container.background_jobs:
        await job.start()
        started_jobs.append(job)
      yield
    finally:
      for job in reversed(started_jobs):
        await job.stop()

  app = FastAPI(title=app_settings.app_name, lifespan=lifespan)
  app.state.container = container
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
