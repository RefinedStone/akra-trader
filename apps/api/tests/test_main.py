from __future__ import annotations

from fastapi.testclient import TestClient

from akra_trader.bootstrap import Container
from akra_trader.config import Settings
from akra_trader.main import create_app


class FakeBackgroundJob:
  def __init__(self) -> None:
    self.started = False
    self.stopped = False

  async def start(self) -> None:
    self.started = True

  async def stop(self) -> None:
    self.stopped = True


def test_create_app_runs_background_job_lifecycle(monkeypatch) -> None:
  job = FakeBackgroundJob()
  container = Container(app=object(), background_jobs=(job,))

  monkeypatch.setattr("akra_trader.main.build_container", lambda settings: container)

  with TestClient(create_app(Settings(market_data_provider="seeded"))) as client:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert job.started is True

  assert job.stopped is True
