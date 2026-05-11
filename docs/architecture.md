# Architecture

Current boundary summary as of May 11, 2026.

## Core Rule

One behavior should be understandable from one entrypoint and a small set of nearby collaborators.
Compatibility files may exist, but they should delegate or re-export rather than own feature logic.

## Backend Shape

- `domain/*`: pure models and services.
- `domain/model_types/*`: bounded model families behind `domain/models.py`.
- `port_contracts/*`: protocol definitions behind the compatibility `ports.py` barrel.
- `application.py`: compatibility facade composed from mixins and flow classes.
- `application_flows/*`: use-case flow owners.
- `application_support/*`: shared helpers, serialization, policies, and orchestration support.
- `adapters/*`: storage, venues, market data, and operator-delivery implementations.
- `api.py`, `api_*`, `main.py`: HTTP shape and dependency wiring.

## Frontend Shape

- `src/App.tsx`: compatibility entrypoint to the control room.
- `src/app/*`: workspace route state, shell, and workspace metadata.
- `src/routes/*`: route-owned workspace composition.
- `src/features/*`: feature-owned flows such as query-builder and run-history.
- `src/controlRoomApi/*`: transport helpers behind `controlRoomApi.ts`.
- `src/controlRoomDefinitions/*`: type families behind `controlRoomDefinitions.ts`.
- `src/control-room/*`: current control-room panels and shared sections.

## Decomposition Rules

- Do not add new behavior to compatibility barrels when a bounded module can own it.
- Keep provider routing registry-driven instead of adding large dispatch branches.
- Keep request parsing out of domain and adapters.
- Split a module when it combines state, transport, policy, serialization, and dense rendering for
  unrelated flows.
- Preserve public API paths and payload compatibility unless the feature explicitly requires a
  contract change.

## Current Pressure Points

- Provider-provenance scheduler/governance flows are split, but several mixins and support modules
  remain large.
- Operator-delivery support has registries and grouped provider modules, but provider families still
  need smaller ownership boundaries.
- Control-room panels are route-aware, but large status/catalog/live/provider-provenance sections
  still carry dense JSX and state.
- Runtime and guarded-live operator flows need clearer active-session ownership before more UI is
  added.

## Done Criteria For New Work

- New backend behavior lands in a flow/support/adapter/domain module with a clear owner.
- New frontend behavior lands behind a route or feature owner, not in the shell.
- Tests cover the route, flow, or adapter boundary being changed.
- Documentation updates `current-state`, `roadmap`, or `operations` only when the meaning changed.
