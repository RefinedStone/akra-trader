from __future__ import annotations

from pathlib import Path

from akra_trader.bootstrap import build_container
from akra_trader.bootstrap import build_default_runs_database_url
from akra_trader.config import Settings


def test_build_container_uses_configured_runs_database_url(monkeypatch) -> None:
  captured: dict[str, str] = {}

  class FakeRunRepository:
    def __init__(self, database_url: str) -> None:
      captured["database_url"] = database_url

  monkeypatch.setattr("akra_trader.bootstrap.SqlAlchemyRunRepository", FakeRunRepository)

  build_container(Settings(runs_database_url="postgresql+psycopg://akra:akra@postgres:5432/akra_trader"))

  assert captured["database_url"] == "postgresql+psycopg://akra:akra@postgres:5432/akra_trader"


def test_build_default_runs_database_url_points_to_local_sqlite() -> None:
  repo_root = Path(__file__).resolve().parents[2]

  database_url = build_default_runs_database_url(repo_root)

  assert database_url.startswith("sqlite:///")
  assert database_url.endswith("/.local/state/runs.sqlite3")
