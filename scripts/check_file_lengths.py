#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_INCLUDE_ROOTS = (
  Path("apps/api/src"),
  Path("apps/api/tests"),
  Path("apps/web/src"),
)
DEFAULT_SUFFIXES = {".py", ".ts", ".tsx"}


def iter_source_files(roots: tuple[Path, ...], suffixes: set[str]) -> list[Path]:
  files: list[Path] = []
  for root in roots:
    if root.is_file() and root.suffix in suffixes:
      files.append(root)
      continue
    if not root.exists():
      continue
    for candidate in root.rglob("*"):
      if candidate.is_file() and candidate.suffix in suffixes:
        files.append(candidate)
  return sorted(files)


def count_lines(path: Path) -> int:
  with path.open("rb") as file:
    return sum(1 for _ in file)


def main() -> int:
  parser = argparse.ArgumentParser(
    description="Fail when source files exceed the configured line limit.",
  )
  parser.add_argument("--max-lines", type=int, default=1000)
  parser.add_argument(
    "paths",
    nargs="*",
    type=Path,
    default=list(DEFAULT_INCLUDE_ROOTS),
    help="Files or directories to scan. Defaults to API and web source/test roots.",
  )
  args = parser.parse_args()

  roots = tuple(args.paths)
  oversized: list[tuple[int, Path]] = []
  for path in iter_source_files(roots, DEFAULT_SUFFIXES):
    line_count = count_lines(path)
    if line_count > args.max_lines:
      oversized.append((line_count, path))
  oversized.sort(reverse=True)

  if not oversized:
    print(f"All scanned source files are <= {args.max_lines} lines.")
    return 0

  print(f"{len(oversized)} scanned source files exceed {args.max_lines} lines:")
  for line_count, path in oversized:
    print(f"{line_count:5} {path}")
  return 1


if __name__ == "__main__":
  raise SystemExit(main())
