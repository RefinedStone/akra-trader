# Experiment OS

- Direction id: `experiment-os`

## Goal

Turn run history into a durable experiment operating system with strategy lifecycle, presets, tags,
benchmark packs, and queryable metadata that support promotion decisions instead of one-off
inspection.

## Current status on April 21, 2026

- presets, preset lifecycle, revisions, comparison, rerun boundaries, and richer query/filter
  contracts already exist
- the remaining work is centered on durable custom strategy registration, normalized experiment
  storage, and promotion workflow completion

## Immediate gaps

- durable custom strategy registry
- promotion/lifecycle workflow durability
- artifact and export registry
- normalized experiment summaries for common query paths

## Linked docs

- `docs/status/current-state.md`
- `docs/roadmap/product-roadmap.md`
- `docs/roadmap/technical-roadmap.md`

## Success criteria

- strategy registration and lifecycle state are durable and queryable across restarts
- runs can be filtered and compared by dataset, preset, tag, benchmark family, and strategy version
  without relying on payload-only scans for common paths
- native and reference runs share one experiment model with consistent provenance, artifact, and
  export posture
