from __future__ import annotations

import asyncio
import logging
from typing import Protocol


logger = logging.getLogger(__name__)


class GuardedLiveWorkerMaintainer(Protocol):
  def maintain_guarded_live_worker_sessions(
    self,
    *,
    force_recovery: bool = False,
    recovery_reason: str = "heartbeat_timeout",
  ) -> dict[str, int]: ...


class GuardedLiveWorkerSessionsJob:
  def __init__(
    self,
    application: GuardedLiveWorkerMaintainer,
    *,
    interval_seconds: int,
  ) -> None:
    if interval_seconds <= 0:
      raise ValueError("interval_seconds must be greater than zero")
    self._application = application
    self._interval_seconds = interval_seconds
    self._stop_event = asyncio.Event()
    self._task: asyncio.Task[None] | None = None

  async def start(self) -> None:
    if self._task is not None and not self._task.done():
      return
    self._stop_event = asyncio.Event()
    await asyncio.to_thread(
      self._application.maintain_guarded_live_worker_sessions,
      force_recovery=True,
      recovery_reason="process_restart",
    )
    self._task = asyncio.create_task(self._run_loop())

  async def stop(self) -> None:
    if self._task is None:
      return
    self._stop_event.set()
    try:
      await self._task
    finally:
      self._task = None

  def maintain_once(self) -> dict[str, int]:
    return self._application.maintain_guarded_live_worker_sessions()

  async def _run_loop(self) -> None:
    while not self._stop_event.is_set():
      try:
        await asyncio.to_thread(self.maintain_once)
      except Exception:
        logger.exception("Guarded-live worker maintenance cycle failed.")
      if self._stop_event.is_set():
        break
      try:
        await asyncio.wait_for(self._stop_event.wait(), timeout=self._interval_seconds)
      except TimeoutError:
        continue
