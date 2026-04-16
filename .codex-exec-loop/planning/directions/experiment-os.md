# Experiment OS

- Direction id: `experiment-os`

## Goal

Turn run history into a durable experiment operating system with strategy lifecycle, presets, tags, benchmark packs, and queryable metadata that support promotion decisions instead of one-off backtest inspection.

## Success criteria

- Strategy registration and lifecycle state are durable and queryable across restarts.
- Runs can be filtered and compared by dataset, preset, tag, benchmark family, and strategy version without relying on payload-only scans for common paths.
- Native and reference runs share one experiment model with consistent provenance, artifact, and export posture.

## Scope hints

- Use docs/blueprint/platform-program.md Workstream B, docs/blueprint/product-program.md Program Phase 1 and Program Phase 2, and docs/blueprint/backlog-map.md Program 1 as the target shape.
- Prioritize reproducibility, presets, tags, lifecycle, and benchmark promotion flows before optimization automation or collaboration features.
- Keep reference strategies visible as benchmark lanes and do not let external-runtime behavior define core experiment contracts.
