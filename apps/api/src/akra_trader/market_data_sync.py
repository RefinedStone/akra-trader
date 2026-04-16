from __future__ import annotations

import asyncio
import logging
from typing import Protocol


logger = logging.getLogger(__name__)


class SyncableMarketData(Protocol):
  def sync_tracked(self, timeframe: str) -> None: ...


class MarketDataSyncJob:
  def __init__(
    self,
    market_data: SyncableMarketData,
    *,
    timeframes: tuple[str, ...],
    interval_seconds: int,
  ) -> None:
    if interval_seconds <= 0:
      raise ValueError("interval_seconds must be greater than zero")
    self._market_data = market_data
    self._timeframes = timeframes
    self._interval_seconds = interval_seconds
    self._stop_event = asyncio.Event()
    self._task: asyncio.Task[None] | None = None

  async def start(self) -> None:
    if self._task is not None and not self._task.done():
      return
    self._stop_event = asyncio.Event()
    self._task = asyncio.create_task(self._run_loop())

  async def stop(self) -> None:
    if self._task is None:
      return
    self._stop_event.set()
    try:
      await self._task
    finally:
      self._task = None

  def sync_once(self) -> None:
    for timeframe in self._timeframes:
      self._market_data.sync_tracked(timeframe)

  async def _run_loop(self) -> None:
    while not self._stop_event.is_set():
      try:
        await asyncio.to_thread(self.sync_once)
      except Exception:
        logger.exception("Market data sync cycle failed.")
      if self._stop_event.is_set():
        break
      try:
        await asyncio.wait_for(self._stop_event.wait(), timeout=self._interval_seconds)
      except TimeoutError:
        continue
