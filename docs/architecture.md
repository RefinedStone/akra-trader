# Architecture

Updated for the repository state as of April 22, 2026.

## Core Rule

The repository must be understandable in smaller units than it is today.

- domain and application code must not know about FastAPI, SQLAlchemy, ccxt, Freqtrade, or
  provider-specific transport details
- route/shell code must not own dense feature logic forever
- provider/plugin dispatch must not grow through giant condition chains

## LLM Sensitivity

In this repository, "LLM sensitivity" means the codebase is shaped so an AI agent can understand and
change one flow without loading unrelated flows.

This is a structure rule, not a prompt trick.

- one primary behavior should have one entry module and a small set of direct collaborators
- a route, use case, or provider should usually be understandable from the entrypoint plus 2 to 4
  directly related modules
- feature entry modules should stay tiny and mostly re-export or compose smaller modules
- shell, route, and adapter-facade files must not silently absorb parser, storage, policy, or dense
  rendering logic
- when one feature starts mixing model, storage, transport, governance, and view logic in one
  place, it must split by those concerns before new work continues there

The goal is not only smaller files. The goal is bounded reading context, so both humans and agents
can modify one behavior without reopening the rest of the product.

Use [LLM Sensitivity](architecture-llm-sensitivity.md) for the full definition, anti-patterns,
review questions, and repository-specific examples.

## Current Refactor Baseline

The first architecture-reset wave is now partially implemented:

- port contracts are split under `apps/api/src/akra_trader/port_contracts/*`
- `apps/api/src/akra_trader/ports.py` is now a compatibility re-export layer
- shared application fallback adapters and comparison policy moved under
  `apps/api/src/akra_trader/application_support/*`
- comparison serialization helpers now live under
  `apps/api/src/akra_trader/application_support/comparison_serialization.py`
- provider-provenance domain records now live under
  `apps/api/src/akra_trader/domain/model_types/provider_provenance.py`
- incident-delivery aliasing and provider dispatch now flow through
  `apps/api/src/akra_trader/adapters/operator_delivery_registry.py`
- frontend workspace routing and shell layout now live under `apps/web/src/app/*`
- control-room compatibility barrels now fan out to `apps/web/src/controlRoomApi/*` and
  `apps/web/src/controlRoomDefinitions/*`

The product is still not fully decomposed. `application.py`, `operator_delivery.py`, and
`App.tsx` remain the main pressure points.

## Target Documents

- [LLM Sensitivity](architecture-llm-sensitivity.md)
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
- `domain/model_types/*`
  - extracted bounded model families behind `domain/models.py` compatibility imports
- `apps/web/src/app/*`
  - workspace route state, shell composition, and workspace metadata
- `apps/web/src/controlRoomApi/*`
  - feature-scoped transport helpers behind the compatibility barrel
- `apps/web/src/controlRoomDefinitions/*`
  - feature-scoped type families behind the compatibility barrel

## Pressure Points Still Open

- `application.py` still mixes too many use cases in one module
- `operator_delivery.py` still contains too many provider implementation bodies in one file
- `domain/models.py` is broader than one bounded feature area should be
- `App.tsx` still holds too much feature state and JSX even after shell extraction
- standalone surface binding catalogs are now isolated from the executor, but the catalog itself is
  still broad and should split by bounded flow
- `operator_delivery.py` now delegates the busiest provider family to a separate mixin, but the
  long tail of provider modules is still concentrated
- `llm-sensitivity-decomposition` is now an active cross-cutting lane and should land with feature
  work rather than after it

## Operational Rule

New work should reinforce the split, not re-expand the monoliths.

- add new protocols under `port_contracts/*`
- add new provider routing through the registry layer
- add new workspace-level navigation under `apps/web/src/app/*`
- prefer support/use-case modules over adding more policy to `application.py`
- when a module can no longer be understood as one flow with a few direct collaborators, split it
  before adding more behavior
