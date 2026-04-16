from __future__ import annotations

from pathlib import Path

from akra_trader.adapters.freqtrade import FreqtradeReferenceAdapter
from akra_trader.adapters.references import load_reference_catalog


def test_reference_adapter_builds_nfi_command() -> None:
  repo_root = Path(__file__).resolve().parents[3]
  references = load_reference_catalog(repo_root / "reference" / "catalog.toml")
  adapter = FreqtradeReferenceAdapter(repo_root, references)
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
        "reference_id": "nostalgia-for-infinity",
        "entrypoint": "NostalgiaForInfinityX7",
        "version": "reference",
      },
    )(),
  )

  assert prepared.command[0] == "freqtrade"
  assert "--strategy=NostalgiaForInfinityX7" in prepared.command
  assert prepared.working_directory.endswith("reference/NostalgiaForInfinity")
  assert prepared.reference_id == "nostalgia-for-infinity"
  assert prepared.reference.title == "NostalgiaForInfinity"
  assert prepared.integration_mode == "external_runtime"
  assert any(path.endswith("user_data/backtest_results") for path in prepared.artifact_roots)
  assert any(path.endswith("user_data/logs") for path in prepared.artifact_roots)
