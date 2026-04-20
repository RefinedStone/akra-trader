# Product Position

Updated for the repository state as of April 21, 2026.

## What This Product Is

`akra-trader` is currently a crypto-first, single-operator research and runtime control workstation.

Its strongest current posture is:

- durable research execution
- benchmark comparison across native and reference lanes
- sandbox worker supervision
- guarded-live safety gating and operator visibility

## What This Product Is Not

It is not yet:

- a consumer-facing trading application
- a multi-user platform with RBAC and approvals
- a fully hardened live-trading system with complete venue-native lifecycle recovery
- a finished experiment operating system with durable custom strategy registration and normalized
  artifact storage
- an LLM-native research platform

## Current Readiness By Area

### Research

Strong.

Backtests, provenance, reruns, presets, comparison, and query/filter surfaces are already useful in
daily research.

### Experiment Operations

Partial.

The product can already manage presets, comparisons, and reruns, but strategy lifecycle, durable
registration, and normalized experiment storage still need completion.

### Runtime Operations

Partial but real.

Sandbox workers, heartbeat, recovery, and operator alerts exist. The remaining work is less about
whether the runtime exists and more about making daily operation clearer and less fragile.

### Guarded Live

Early but meaningful.

Kill switch, reconciliation, recovery, and venue-backed guarded-live launch gates already exist.
The missing work is in fuller venue lifecycle handling, deployment discipline, and clearer product
readiness gates.

### Intelligence Research

Not productized.

The `DecisionEnginePort` and template strategy shapes exist, but trace, replay, fallback, and
provider adapters do not.

## Operator Promise Today

One operator can already do the following without ad hoc scripts:

- inspect market-data health
- run native or reference-backed research flows
- compare runs and inspect provenance
- start and stop sandbox workers
- inspect guarded-live blockers, incidents, and reconciliation state

One operator still cannot safely rely on the product alone for:

- durable custom strategy promotion workflows
- production-grade live venue lifecycle management
- fully documented day-2 operations and incident response
- LLM-assisted strategy research with replay and fallback guarantees

## Document Contract

If another document implies a different product position, `current-state.md` wins and the other
document should be corrected.
