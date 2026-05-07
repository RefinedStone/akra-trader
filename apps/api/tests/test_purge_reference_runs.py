from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import create_engine, insert, select

from akra_trader.adapters.sqlalchemy_schema import metadata
from akra_trader.adapters.sqlalchemy_schema import run_record_tags
from akra_trader.adapters.sqlalchemy_schema import run_records

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from scripts.purge_reference_runs import purge_reference_runs


def _insert_run(connection, run_id: str, payload: dict) -> None:
  connection.execute(
    insert(run_records).values(
      run_id=run_id,
      mode="backtest",
      status="completed",
      strategy_id=payload["config"]["strategy_id"],
      strategy_version="1.0.0",
      started_at="2026-01-01T00:00:00+00:00",
      payload=payload,
    )
  )
  connection.execute(insert(run_record_tags).values(run_id=run_id, tag="keep-check"))


def test_purge_reference_runs_dry_run_does_not_delete(tmp_path):
  database_url = f"sqlite:///{tmp_path / 'runs.sqlite3'}"
  engine = create_engine(database_url)
  metadata.create_all(engine)
  with engine.begin() as connection:
    _insert_run(
      connection,
      "reference-run",
      {
        "config": {"run_id": "reference-run", "strategy_id": "NostalgiaForInfinityX7"},
        "provenance": {"lane": "reference"},
      },
    )
    _insert_run(
      connection,
      "native-run",
      {
        "config": {"run_id": "native-run", "strategy_id": "ma_cross_v1"},
        "provenance": {"lane": "native"},
      },
    )

  run_ids, deleted_tags = purge_reference_runs(database_url, execute=False)

  assert run_ids == ["reference-run"]
  assert deleted_tags == 0
  with engine.begin() as connection:
    assert set(connection.execute(select(run_records.c.run_id)).scalars().all()) == {
      "reference-run",
      "native-run",
    }


def test_purge_reference_runs_execute_deletes_reference_runs_and_tags_only(tmp_path):
  database_url = f"sqlite:///{tmp_path / 'runs.sqlite3'}"
  engine = create_engine(database_url)
  metadata.create_all(engine)
  with engine.begin() as connection:
    _insert_run(
      connection,
      "legacy-reference-run",
      {
        "config": {"run_id": "legacy-reference-run", "strategy_id": "ma_cross_v1"},
        "provenance": {
          "lane": "native",
          "strategy": {"runtime": "freqtrade_reference"},
        },
      },
    )
    _insert_run(
      connection,
      "native-run",
      {
        "config": {"run_id": "native-run", "strategy_id": "ma_cross_v1"},
        "provenance": {"lane": "native"},
      },
    )

  run_ids, deleted_tags = purge_reference_runs(database_url, execute=True)

  assert run_ids == ["legacy-reference-run"]
  assert deleted_tags == 1
  with engine.begin() as connection:
    assert connection.execute(select(run_records.c.run_id)).scalars().all() == ["native-run"]
    assert connection.execute(select(run_record_tags.c.run_id)).scalars().all() == ["native-run"]


def test_purge_reference_runs_deletes_legacy_nfi_strategy_id_without_provenance_marker(tmp_path):
  database_url = f"sqlite:///{tmp_path / 'runs.sqlite3'}"
  engine = create_engine(database_url)
  metadata.create_all(engine)
  with engine.begin() as connection:
    _insert_run(
      connection,
      "legacy-nfi-run",
      {
        "config": {"run_id": "legacy-nfi-run", "strategy_id": "nfi_x7_reference"},
        "provenance": {"lane": "native", "strategy": {"runtime": "native"}},
      },
    )
    _insert_run(
      connection,
      "native-confidence-run",
      {
        "config": {"run_id": "native-confidence-run", "strategy_id": "ma_cross_v1"},
        "provenance": {
          "lane": "native",
          "strategy": {
            "runtime": "native",
            "name": "Confidence preserving native strategy",
          },
        },
      },
    )

  run_ids, deleted_tags = purge_reference_runs(database_url, execute=True)

  assert run_ids == ["legacy-nfi-run"]
  assert deleted_tags == 1
  with engine.begin() as connection:
    assert connection.execute(select(run_records.c.run_id)).scalars().all() == [
      "native-confidence-run"
    ]
    assert connection.execute(select(run_record_tags.c.run_id)).scalars().all() == [
      "native-confidence-run"
    ]


def test_purge_reference_runs_deletes_null_reference_keys_from_legacy_native_payload(tmp_path):
  database_url = f"sqlite:///{tmp_path / 'runs.sqlite3'}"
  engine = create_engine(database_url)
  metadata.create_all(engine)
  with engine.begin() as connection:
    _insert_run(
      connection,
      "legacy-null-reference-run",
      {
        "config": {"run_id": "legacy-null-reference-run", "strategy_id": "ma_cross_v1"},
        "provenance": {
          "lane": "native",
          "reference_id": None,
          "reference": None,
          "strategy": {
            "runtime": "native",
            "reference_path": None,
          },
        },
      },
    )
    _insert_run(
      connection,
      "native-run",
      {
        "config": {"run_id": "native-run", "strategy_id": "ma_cross_v1"},
        "provenance": {"lane": "native", "strategy": {"runtime": "native"}},
      },
    )

  run_ids, deleted_tags = purge_reference_runs(database_url, execute=True)

  assert run_ids == ["legacy-null-reference-run"]
  assert deleted_tags == 1
  with engine.begin() as connection:
    assert connection.execute(select(run_records.c.run_id)).scalars().all() == ["native-run"]
    assert connection.execute(select(run_record_tags.c.run_id)).scalars().all() == ["native-run"]
