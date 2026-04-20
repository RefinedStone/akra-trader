# Backend Architecture Target

Updated for the refactor baseline as of April 21, 2026.

## Summary

The backend target is a compatibility-preserving hexagonal structure where request handling,
application orchestration, port contracts, and adapter/plugin code live in separate modules.

This is not fully complete yet. The current wave introduces the first executable skeleton:

- `ports.py` is now a compatibility shim over `port_contracts/*`
- shared application defaults and comparison policy moved into `application_support/*`
- standalone surface/runtime query types and filter/sort helpers moved into
  `application_support/runtime_queries.py`
- incident delivery dispatch is now driven by `adapters/operator_delivery_registry.py`

## Target Structure

- `domain/`
  - pure models and pure services only
  - no framework, transport, or storage imports
- `application.py`
  - temporary facade and compatibility entrypoint
  - allowed to orchestrate, but should keep shrinking
- `application_support/`
  - shared policy, fallback adapters, and pure helper modules
  - no FastAPI or adapter-specific imports
- `port_contracts/`
  - split protocol definitions by concern
  - `ports.py` re-exports these contracts for compatibility
- `adapters/`
  - storage, venue, market-data, and incident-delivery implementations
  - provider-specific logic should live behind a registry or factory
- `runtime.py`
  - execution-loop primitives only
- `api.py` and `main.py`
  - request/response mapping and dependency wiring only

## Boundary Rules

- `domain/*` must not import `fastapi`, `sqlalchemy`, `ccxt`, `urllib`, or provider SDK logic.
- `application.py` must not contain provider matrices or giant transport switch logic.
- `ports.py` must stay a re-export layer only. New contracts go in `port_contracts/*`.
- provider routing must be declared in a registry, not large `if target == ...` chains.
- request parsing and HTTP shape decisions must stay in `api.py`, not inside domain or adapters.

## First-Wave Move Map

- Port protocols
  - move from single-file `ports.py` into `port_contracts/*`
  - keep import compatibility through re-exports
- Application defaults
  - keep fallback adapters and paging/remediation policy in `application_support/defaults.py`
  - keep comparison scoring policy in `application_support/comparison.py`
- Surface policy and serialization
  - keep run-surface enforcement, action-availability policy, and run serialization helpers in
    `application_support/run_surfaces.py`
  - keep standalone surface/runtime query types plus filter/sort evaluation helpers in
    `application_support/runtime_queries.py`
  - keep `application.py` as the import-compatible facade while these helpers move out
- Incident delivery
  - keep provider implementations in `adapters/operator_delivery.py` for now
  - move alias normalization, capability discovery, and dispatch decisions into `operator_delivery_registry.py`

## Remaining Pressure Points

- `application.py` is still too large and still mixes too many use cases.
- `operator_delivery.py` still contains provider implementation bodies in one file.
- `domain/models.py` remains too broad and should split by bounded feature area.
- binding catalogs and standalone surface executors still need extraction into dedicated modules.

## Done Criteria For This Track

- new ports or shared fallback logic are not added to monolithic files
- new providers register through a registry entry instead of another dispatch branch
- `application.py` keeps shrinking as feature groups move into support/use-case modules
- compatibility remains intact for existing imports and API endpoints
