# LLM sensitivity decomposition

- Direction id: `llm-sensitivity-decomposition`

## Goal

Keep bounded flows understandable from one entrypoint and a few direct collaborators.

## Current status on May 11, 2026

- `App.tsx`, `application.py`, `ports.py`, `domain/models.py`, `controlRoomApi.ts`, and
  `controlRoomDefinitions.ts` are compatibility entrypoints.
- Backend flow ownership is spread across `application_flows/*`, `application_support/*`, mixins,
  bounded domain models, and adapters.
- Frontend route, API, type, query-builder, and run-history ownership has moved into narrower
  modules.

## Immediate gaps

- large provider-provenance scheduler/governance modules
- large operator-delivery provider families
- dense control-room status/catalog/live/provider-provenance panels
- unclear active-session ownership in some runtime and guarded-live flows

## Linked docs

- `docs/status/current-state.md`
- `docs/architecture.md`
- `docs/roadmap/README.md`
