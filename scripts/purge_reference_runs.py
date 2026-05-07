#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, delete, select

from akra_trader.adapters.sqlalchemy_schema import metadata
from akra_trader.adapters.sqlalchemy_schema import run_record_tags
from akra_trader.adapters.sqlalchemy_schema import run_records


LEGACY_NFI_MARKERS = (
  "nostalgiaforinfinity",
  "nostalgia-for-infinity",
  "nfi_",
  "nfi-",
)


def _payload_matches(payload: dict[str, Any]) -> bool:
  provenance = payload.get("provenance") or {}
  strategy = provenance.get("strategy") or {}
  if provenance.get("lane") == "reference":
    return True
  if "reference_id" in provenance or "reference" in provenance:
    return True
  if "reference_path" in strategy or "reference_id" in strategy:
    return True
  if strategy.get("runtime") == "freqtrade_reference":
    return True
  legacy_text = json.dumps(
    {
      "strategy_id": payload.get("config", {}).get("strategy_id"),
      "strategy_runtime": strategy.get("runtime"),
      "strategy_entrypoint": strategy.get("entrypoint"),
      "strategy_name": strategy.get("name"),
    },
    sort_keys=True,
  )
  return any(marker in legacy_text.lower() for marker in LEGACY_NFI_MARKERS)


def purge_reference_runs(database_url: str, *, execute: bool) -> tuple[list[str], int]:
  engine = create_engine(database_url)
  metadata.create_all(engine)
  with engine.begin() as connection:
    rows = connection.execute(select(run_records.c.run_id, run_records.c.payload)).all()
    run_ids = [
      row.run_id
      for row in rows
      if isinstance(row.payload, dict) and _payload_matches(row.payload)
    ]
    deleted_tags = 0
    if execute and run_ids:
      deleted_tags = (
        connection.execute(
          delete(run_record_tags).where(run_record_tags.c.run_id.in_(run_ids))
        ).rowcount
        or 0
      )
      connection.execute(delete(run_records).where(run_records.c.run_id.in_(run_ids)))
    return run_ids, deleted_tags


def main() -> int:
  parser = argparse.ArgumentParser(
    description="Delete legacy third-party/reference-lane run records from the runs database."
  )
  parser.add_argument("database_url", help="SQLAlchemy database URL, e.g. sqlite:////path/runs.sqlite3")
  parser.add_argument("--execute", action="store_true", help="Actually delete matched runs and tags.")
  args = parser.parse_args()

  run_ids, deleted_tags = purge_reference_runs(args.database_url, execute=args.execute)
  mode = "execute" if args.execute else "dry-run"
  print(json.dumps({
    "mode": mode,
    "matched_count": len(run_ids),
    "matched_run_ids": run_ids,
    "deleted_tag_count": deleted_tags if args.execute else 0,
  }, indent=2, sort_keys=True))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
