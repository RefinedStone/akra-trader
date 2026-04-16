from __future__ import annotations

from pathlib import Path

from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter


def test_reference_adapter_builds_nfi_command() -> None:
  adapter = FreqtradeReferenceAdapter(Path("/tmp/project"))
  prepared = adapter.prepare_backtest(
    config=type(
      "Config",
      (),
      {
        "start_at": None,
        "end_at": None,
        "venue": "binance",
      },
    )(),
    metadata=type(
      "Metadata",
      (),
      {
        "entrypoint": "NostalgiaForInfinityX7",
      },
    )(),
  )

  assert prepared.command[0] == "freqtrade"
  assert "--strategy=NostalgiaForInfinityX7" in prepared.command
  assert prepared.working_directory.endswith("reference/NostalgiaForInfinity")
