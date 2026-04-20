# Product Roadmap

Rebased to the repository state as of April 21, 2026.

## Objective

Move `akra-trader` from a feature-dense internal platform into a maintainable single-operator
trading workstation for crypto research first, then controlled runtime operations, and only then
more mature guarded-live work.

## Current Product Checkpoint

One operator can already:

1. inspect market-data health
2. launch durable native backtests
3. compare native and reference runs
4. reuse presets and rerun stored execution boundaries
5. start and stop sandbox workers
6. inspect guarded-live blockers, incidents, and recovery state

The main product gaps are no longer "does the feature exist" but rather:

- can the feature be trusted as an operator workflow
- is the capability durably modeled and queryable
- is the control room understandable at product level
- is the live path complete enough to be treated as operational instead of experimental

## Phase 1: Research Trust And Experiment OS

### Current baseline

- dataset identity, sync-checkpoint linkage, and rerun boundaries already exist
- native vs reference comparison is already a normal workflow
- presets, preset lifecycle, revisions, and restore flows already exist
- run and strategy query/filter surfaces are richer than a simple history list

### Still missing

- deterministic proof posture for repeated identical inputs
- durable custom strategy registration and promotion lifecycle
- normalized experiment summaries, artifact retrieval, and export posture
- clearer benchmark-pack and promotion review workflow

### Exit condition

`akra-trader` should behave like an experiment operating system rather than a durable run archive.

## Phase 2: Control Room Productization

### Current baseline

- the control room already includes launch forms, histories, comparison, alerts, incidents, and
  guarded-live panels
- sandbox workers already have heartbeat and recovery semantics
- operator visibility already captures worker failures, stale runtime, and guarded-live history

### Still missing

- active-session-first workflows for positions, fills, lag, and recent decisions
- clearer separation between research inspection and operational action flows
- UI decomposition away from the current monolithic single-screen implementation
- operator guidance and runbook-linked actionability

### Exit condition

One operator should be able to answer what is running, what changed, whether it is safe, and what
to do next without leaving the control room.

## Phase 3: Guarded-Live Safety Completion

### Current baseline

- guarded-live kill switch, reconciliation, recovery, incidents, and venue-backed launch gates are
  already implemented
- live order cancel and replace controls already exist
- partial multi-venue continuation and venue-session handoff baseline already exists

### Still missing

- fuller venue-native session lifecycle recovery
- broader order-management coverage beyond cancel and replace
- clearer operator packaging for credentials, deployment, and incident drill workflows
- stronger product-level live candidacy criteria

### Exit condition

The live path should be judged by safety completeness and operational drill success, not by whether
the adapter can submit orders.

## Phase 4: Intelligence Research Lane

### Current baseline

- `DecisionEnginePort`
- template external-decision strategy shape
- shared decision envelope that can carry trace metadata later

### Still missing

- prompt version registry
- raw trace persistence
- replay harness
- provider adapters
- mandatory fallback or review workflow

### Exit condition

LLM-assisted strategy work remains isolated until trace, replay, and fallback are real platform
features.

## Success Measures

The next meaningful product checkpoint should satisfy these conditions:

- repeated runs can be defended against a stable data boundary
- experiment lifecycle is durable enough for promotion decisions
- active sandbox operation is clearer than replay preview semantics
- guarded-live readiness is explained by product gates, not hidden implementation detail
- roadmap and current-state stay aligned after feature work lands

## Explicit Deferrals

- equal-weight support for stocks and crypto
- multi-user RBAC or organization workflows
- multi-node distributed execution
- unattended autonomous live behavior
- public-facing self-service polish before operator-grade workflows are stable
