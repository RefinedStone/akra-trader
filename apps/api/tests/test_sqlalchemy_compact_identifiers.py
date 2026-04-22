from __future__ import annotations

import sqlite3
from pathlib import Path

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex
from sqlalchemy.schema import CreateTable

from akra_trader.adapters.sqlalchemy import SqlAlchemyRunRepository
from akra_trader.adapters.sqlalchemy import metadata


def test_sqlalchemy_metadata_identifiers_fit_postgres_limit() -> None:
  dialect = postgresql.dialect()

  for table in metadata.sorted_tables:
    assert len(table.name) <= 63
    CreateTable(table).compile(dialect=dialect)
    for index in table.indexes:
      if index.name is None:
        continue
      assert len(index.name) <= 63
      CreateIndex(index).compile(dialect=dialect)


def test_sqlalchemy_repository_migrates_legacy_compact_identifier_tables(tmp_path: Path) -> None:
  database_path = tmp_path / "legacy_compact_identifiers.sqlite3"
  connection = sqlite3.connect(database_path)
  connection.execute(
    """
    CREATE TABLE provider_provenance_scheduler_stitched_report_view_audit_records (
      audit_id TEXT PRIMARY KEY,
      view_id TEXT NOT NULL,
      action TEXT NOT NULL,
      recorded_at TEXT NOT NULL,
      payload TEXT NOT NULL
    )
    """
  )
  connection.execute(
    """
    CREATE INDEX
    ix_provider_provenance_scheduler_stitched_report_view_audit_records_view_id
    ON provider_provenance_scheduler_stitched_report_view_audit_records (view_id)
    """
  )
  connection.commit()
  connection.close()

  SqlAlchemyRunRepository(f"sqlite:///{database_path}")

  verification = sqlite3.connect(database_path)
  table_names = {
    row[0]
    for row in verification.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
  }
  index_names = {
    row[0]
    for row in verification.execute("SELECT name FROM sqlite_master WHERE type = 'index'")
  }
  verification.close()

  assert "provider_provenance_scheduler_stitched_report_view_audit_records" not in table_names
  assert "pp_sched_stitch_view_audit" in table_names
  assert (
    "ix_provider_provenance_scheduler_stitched_report_view_audit_records_view_id"
    not in index_names
  )
  assert "ix_pp_sched_stitch_view_audit_view_id" in index_names
