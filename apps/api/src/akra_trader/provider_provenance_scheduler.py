from __future__ import annotations

import asyncio
import logging
from typing import Any
from typing import Protocol


logger = logging.getLogger(__name__)


class ProviderProvenanceScheduledReportRunner(Protocol):
  def execute_provider_provenance_scheduler_cycle(
    self,
    *,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
    limit: int = 25,
  ) -> dict[str, Any]: ...


class ProviderProvenanceReportSchedulerJob:
  SOURCE_TAB_ID = "system:provider-provenance-scheduler"
  SOURCE_TAB_LABEL = "Background scheduler"

  def __init__(
    self,
    application: ProviderProvenanceScheduledReportRunner,
    *,
    interval_seconds: int,
    batch_limit: int,
  ) -> None:
    if interval_seconds <= 0:
      raise ValueError("interval_seconds must be greater than zero")
    if batch_limit <= 0:
      raise ValueError("batch_limit must be greater than zero")
    self._application = application
    self._interval_seconds = interval_seconds
    self._batch_limit = batch_limit
    self._stop_event = asyncio.Event()
    self._task: asyncio.Task[None] | None = None

  async def start(self) -> None:
    if self._task is not None and not self._task.done():
      return
    self._stop_event = asyncio.Event()
    try:
      await asyncio.to_thread(self.run_due_reports_once)
    except Exception as exc:
      logger.warning("Provider provenance scheduler initial cycle failed: %s", exc)
    self._task = asyncio.create_task(self._run_loop())

  async def stop(self) -> None:
    if self._task is None:
      return
    self._stop_event.set()
    try:
      await self._task
    finally:
      self._task = None

  def run_due_reports_once(self) -> dict[str, Any]:
    result = self._application.execute_provider_provenance_scheduler_cycle(
      source_tab_id=self.SOURCE_TAB_ID,
      source_tab_label=self.SOURCE_TAB_LABEL,
      limit=self._batch_limit,
    )
    executed_count = int(result.get("executed_count", 0))
    if executed_count > 0:
      logger.info(
        "Provider provenance scheduler executed %s due scheduled reports.",
        executed_count,
      )
    return result

  async def _run_loop(self) -> None:
    while not self._stop_event.is_set():
      try:
        await asyncio.to_thread(self.run_due_reports_once)
      except Exception:
        logger.exception("Provider provenance scheduler cycle failed.")
      if self._stop_event.is_set():
        break
      try:
        await asyncio.wait_for(self._stop_event.wait(), timeout=self._interval_seconds)
      except TimeoutError:
        continue
