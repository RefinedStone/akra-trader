from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib

from akra_trader.domain.models import ReferenceSource

class ReferenceCatalog:
  def __init__(self, entries: list[ReferenceSource]) -> None:
    self._entries = {entry.reference_id: entry for entry in entries}

  def list_entries(self) -> list[ReferenceSource]:
    return sorted(self._entries.values(), key=lambda item: item.reference_id)

  def get(self, reference_id: str) -> ReferenceSource:
    return self._entries[reference_id]

  @staticmethod
  def absolute_path(repo_root: Path, reference: ReferenceSource) -> Path | None:
    if reference.local_path is None:
      return None
    return repo_root / reference.local_path


def load_reference_catalog(path: Path) -> ReferenceCatalog:
  with path.open("rb") as handle:
    payload = tomllib.load(handle)

  entries = []
  for item in payload["references"]:
    entries.append(
      ReferenceSource(
        reference_id=item["id"],
        title=item["title"],
        kind=item["kind"],
        homepage=item["homepage"],
        license=item["license"],
        integration_mode=item["integration_mode"],
        local_path=item.get("local_path"),
        runtime=item.get("runtime"),
        summary=item.get("summary", ""),
      )
    )
  return ReferenceCatalog(entries)
