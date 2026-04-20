# Architecture

Updated for the repository state as of April 21, 2026.

## Core Rule

The repository must be understandable in smaller units than it is today.

- domain and application code must not know about FastAPI, SQLAlchemy, ccxt, Freqtrade, or
  provider-specific transport details
- route/shell code must not own dense feature logic forever
- provider/plugin dispatch must not grow through giant condition chains

## Current Refactor Baseline

The first architecture-reset wave is now partially implemented:

- port contracts are split under `apps/api/src/akra_trader/port_contracts/*`
- `apps/api/src/akra_trader/ports.py` is now a compatibility re-export layer
- shared application fallback adapters and comparison policy moved under
  `apps/api/src/akra_trader/application_support/*`
- incident-delivery aliasing and provider dispatch now flow through
  `apps/api/src/akra_trader/adapters/operator_delivery_registry.py`
- frontend workspace routing and shell layout now live under `apps/web/src/app/*`

The product is still not fully decomposed. `application.py`, `operator_delivery.py`, and
`App.tsx` remain the main pressure points.

## Target Documents

- [Backend Architecture Target](architecture-backend-target.md)
- [Frontend Architecture Target](architecture-frontend-target.md)
- [Architecture Refactor Stages](architecture-refactor-stages.md)

## Current Stable Boundaries

- `domain/*`
  - pure models and pure services
- `runtime.py`
  - execution-loop primitives and state helpers
- `port_contracts/*`
  - split external-system contracts by concern
- `ports.py`
  - compatibility shim only
- `adapters/*`
  - infrastructure and provider implementations
- `application.py`
  - temporary orchestration facade that still needs decomposition
- `apps/web/src/app/*`
  - workspace route state, shell composition, and workspace metadata

## Pressure Points Still Open

- `application.py` still mixes too many use cases in one module
- `operator_delivery.py` still contains too many provider implementation bodies in one file
- `domain/models.py` is broader than one bounded feature area should be
- `App.tsx` still holds too much feature state and JSX even after shell extraction
- standalone surface binding catalogs are now isolated from the executor, but the catalog itself is
  still broad and should split by bounded flow
- `operator_delivery.py` now delegates the busiest provider family to a separate mixin, but the
  long tail of provider modules is still concentrated

## Operational Rule

New work should reinforce the split, not re-expand the monoliths.

- add new protocols under `port_contracts/*`
- add new provider routing through the registry layer
- add new workspace-level navigation under `apps/web/src/app/*`
- prefer support/use-case modules over adding more policy to `application.py`
