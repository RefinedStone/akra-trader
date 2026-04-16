from __future__ import annotations

from pathlib import Path

from pydantic import TypeAdapter
from sqlalchemy import JSON
from sqlalchemy import Column
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.engine import Engine
from sqlalchemy.engine import make_url

from akra_trader.domain.models import GuardedLiveState
from akra_trader.ports import GuardedLiveStatePort


metadata = MetaData()
guarded_live_state_records = Table(
  "guarded_live_state_records",
  metadata,
  Column("state_key", String, primary_key=True),
  Column("payload", JSON, nullable=False),
)


class SqlAlchemyGuardedLiveStateRepository(GuardedLiveStatePort):
  _adapter = TypeAdapter(GuardedLiveState)
  _state_key = "default"

  def __init__(self, database_url: str) -> None:
    self._database_url = database_url
    self._engine = self._build_engine(database_url)
    metadata.create_all(self._engine)

  def load_state(self) -> GuardedLiveState:
    with self._engine.connect() as connection:
      row = connection.execute(
        select(guarded_live_state_records.c.payload).where(
          guarded_live_state_records.c.state_key == self._state_key
        )
      ).mappings().first()
    if row is None:
      return GuardedLiveState()
    return self._adapter.validate_python(row["payload"])

  def save_state(self, state: GuardedLiveState) -> GuardedLiveState:
    payload = self._adapter.dump_python(state, mode="json")
    with self._engine.begin() as connection:
      existing = connection.execute(
        select(guarded_live_state_records.c.state_key).where(
          guarded_live_state_records.c.state_key == self._state_key
        )
      ).first()
      if existing is None:
        connection.execute(
          insert(guarded_live_state_records).values(
            state_key=self._state_key,
            payload=payload,
          )
        )
      else:
        connection.execute(
          update(guarded_live_state_records)
          .where(guarded_live_state_records.c.state_key == self._state_key)
          .values(payload=payload)
        )
    return state

  def _build_engine(self, database_url: str) -> Engine:
    url = make_url(database_url)
    engine_kwargs = {"pool_pre_ping": True}
    if url.get_backend_name() == "sqlite" and url.database not in {None, "", ":memory:"}:
      Path(url.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
      return create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        **engine_kwargs,
      )
    return create_engine(database_url, **engine_kwargs)
