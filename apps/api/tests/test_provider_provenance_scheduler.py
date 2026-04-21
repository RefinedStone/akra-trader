from __future__ import annotations

import asyncio
from threading import Event
from typing import Any

from akra_trader.provider_provenance_scheduler import ProviderProvenanceReportSchedulerJob


class FakeScheduledReportRunner:
  def __init__(self) -> None:
    self.calls: list[dict[str, Any]] = []
    self.executed = Event()

  def execute_provider_provenance_scheduler_cycle(
    self,
    *,
    source_tab_id: str | None = None,
    source_tab_label: str | None = None,
    limit: int = 25,
  ) -> dict[str, Any]:
    self.calls.append(
      {
        "source_tab_id": source_tab_id,
        "source_tab_label": source_tab_label,
        "limit": limit,
      }
    )
    if len(self.calls) >= 2:
      self.executed.set()
    return {
      "executed_count": len(self.calls),
      "items": (),
    }


def test_provider_provenance_scheduler_runs_startup_and_periodic_cycles() -> None:
  runner = FakeScheduledReportRunner()

  async def exercise() -> tuple[bool, list[dict[str, Any]]]:
    job = ProviderProvenanceReportSchedulerJob(
      runner,
      interval_seconds=1,
      batch_limit=7,
    )
    await job.start()
    executed = await asyncio.to_thread(runner.executed.wait, 1.5)
    await job.stop()
    return executed, runner.calls

  executed, calls = asyncio.run(exercise())

  assert executed is True
  assert len(calls) >= 2
  assert calls[0]["source_tab_id"] == "system:provider-provenance-scheduler"
  assert calls[0]["source_tab_label"] == "Background scheduler"
  assert calls[0]["limit"] == 7


def test_provider_provenance_scheduler_requires_positive_batch_limit() -> None:
  runner = FakeScheduledReportRunner()

  try:
    ProviderProvenanceReportSchedulerJob(
      runner,
      interval_seconds=60,
      batch_limit=0,
    )
  except ValueError as exc:
    assert str(exc) == "batch_limit must be greater than zero"
  else:
    raise AssertionError("expected ValueError for non-positive batch_limit")
