from __future__ import annotations

import asyncio
from threading import Event

from akra_trader.market_data_sync import MarketDataSyncJob


class FakeSyncableMarketData:
  def __init__(self) -> None:
    self.calls: list[str] = []
    self.synced = Event()

  def sync_tracked(self, timeframe: str) -> None:
    self.calls.append(timeframe)
    if len(self.calls) >= 2:
      self.synced.set()


def test_market_data_sync_job_runs_initial_sync_cycle() -> None:
  target = FakeSyncableMarketData()

  async def exercise() -> tuple[bool, list[str]]:
    job = MarketDataSyncJob(
      target,
      timeframes=("5m", "1h"),
      interval_seconds=3600,
    )
    await job.start()
    synced = await asyncio.to_thread(target.synced.wait, 1.0)
    await job.stop()
    return synced, target.calls

  synced, calls = asyncio.run(exercise())

  assert synced is True
  assert calls[:2] == ["5m", "1h"]
