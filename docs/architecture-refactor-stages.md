# Architecture Refactor Stages

Updated for the current refactor wave as of April 22, 2026.

## Stage 1: Compatibility Skeleton

Goal: introduce real boundaries without breaking the product surface.

- split port contracts out of `ports.py`
- move shared application defaults/policy into support modules
- replace incident provider dispatch chains with a registry
- move workspace routing and shell layout out of `App.tsx`
- convert top-level control-room API/type modules into compatibility barrels
- keep API paths and current UI flows stable

Exit criteria:

- compatibility imports continue to work
- route state and provider dispatch no longer live in giant switch blocks
- docs describe actual executable structure, not just intent

## Stage 2: Use-Case Extraction

Goal: shrink `application.py` into a facade.

- extract preset lifecycle orchestration
- extract comparison/query-contract helpers
- extract comparison serialization into support modules before adding more comparison surface area
- extract guarded-live control use cases
- extract replay-alias and audit surfaces

Exit criteria:

- `application.py` is mostly wiring and coarse orchestration
- new use cases land in dedicated modules by default

## Stage 3: Provider Plugin Decomposition

Goal: make incident delivery provider-specific code independently understandable.

- move provider-specific request/response code out of `operator_delivery.py`
- keep common transport, recovery-engine helpers, and registry metadata shared
- isolate provider capability detection from request execution

Exit criteria:

- adding a provider is mostly registry + provider module work
- removing a provider does not require editing a central dispatch chain

## Stage 4: Route And Feature Decomposition

Goal: move the control room from one giant feature file to route-owned modules.

- extract overview workspace
- extract research workspace
- extract runtime ops workspace
- extract guarded-live workspace
- group feature-local API helpers with their route/features
- keep route smoke tests in place while those extractions land

Exit criteria:

- `App.tsx` is a shell/router composition file
- each workspace can be understood without loading the entire control room
