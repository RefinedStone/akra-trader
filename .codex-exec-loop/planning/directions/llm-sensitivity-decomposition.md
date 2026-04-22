# LLM sensitivity decomposition

- Direction id: `llm-sensitivity-decomposition`

## Goal

Reduce the giant compatibility files so one operator or research flow can be changed from one
entrypoint plus a few nearby collaborators instead of reopening `App.tsx`, `application.py`, or
the full control-room type/api surface.

## Current status on April 22, 2026

- active cross-cutting lane
- compatibility barrels now exist for `controlRoomApi.ts` and `controlRoomDefinitions.ts`
- provider-provenance control-room types moved under `apps/web/src/controlRoomDefinitions/*`
- comparison serialization moved under `apps/api/src/akra_trader/application_support/comparison_serialization.py`
- provider-provenance domain records moved under
  `apps/api/src/akra_trader/domain/model_types/provider_provenance.py`
- route smoke tests now exist for `WorkspaceRouteContent` and the workspace route shells

## Primary pressure points

- `apps/web/src/App.tsx` still owns too much feature state and dense JSX
- `apps/api/src/akra_trader/application.py` is smaller on the comparison path, but still too broad
- `apps/api/src/akra_trader/domain/models.py` is still wider than one bounded feature area
- `apps/web/src/controlRoomDefinitions.ts` and `apps/web/src/controlRoomApi.ts` are now barrels,
  but the remaining feature consumers still need direct ownership modules

## Work packages

- keep shrinking compatibility entrypoints by moving serializer/model families into dedicated
  support modules
- move query-builder and provider-provenance consumers toward feature-owned modules instead of the
  top-level compatibility barrels
- extract route-owned workspace modules from `App.tsx` with real state/data ownership
- keep route smoke tests and build/type gates in place as each extraction lands

## Done criteria

- giant compatibility files mostly delegate or re-export instead of owning policy or dense
  presentation
- one bounded flow is usually understandable from an entry module plus 2 to 4 collaborators
- new work no longer defaults to `App.tsx`, `application.py`, `controlRoomApi.ts`,
  `controlRoomDefinitions.ts`, or `domain/models.py`

## Non-goals

- changing public API paths, payload schemas, or operator-facing route semantics just to enable the
  split
- treating this lane as a final cleanup phase after product work is complete
