# LLM Sensitivity

Updated for the repository state as of April 21, 2026.

## Why This Document Exists

This repository is large enough that a weak LLM model can easily lose the flow if the code is
organized around "everything in one file" or "one module knows too many concerns".

This document defines what "LLM sensitivity" means in practical architecture terms.

It is not about making prompts better.
It is about shaping the codebase so one model can understand one behavior without reading the whole
product.

## Short Definition

LLM sensitivity means one flow can be understood and changed from:

- one clear entry module
- a small number of direct collaborators
- obvious boundaries between policy, state, I/O, and presentation

If a model must open unrelated files just to answer "where does this behavior start?" then the code
is not LLM-sensitive enough.

## The Essence

The essence is bounded context at the code level.

A weaker model usually fails in four ways:

1. It cannot find the true entrypoint.
2. It sees one file mixing several concerns and edits the wrong part.
3. It cannot tell which state is authoritative.
4. It must load too much unrelated code before it can act.

LLM sensitivity reduces those failure modes by making each flow answer a few basic questions
quickly.

For any flow, a model should be able to find:

- where the flow starts
- where state is read and written
- where domain or policy decisions happen
- where external I/O happens
- where the UI or API surface is rendered or mapped

If those answers are spread across giant mixed files, the model will drift.

## This Is Not Just "Small Files"

Small files help, but line count is not the real rule.

These are both bad:

- a small file that hides side effects and forwards control to many unrelated places
- a medium file that mixes storage, policy, transport, and rendering in one body

These are better:

- a tiny entry module that points to the real feature modules
- a use-case module with explicit collaborators
- a feature component that delegates storage, parsing, and transport helpers to nearby modules

The goal is not "many files".
The goal is "few files per flow".

## Litmus Test

When a weak LLM model is asked to change one behavior, it should usually be able to work from:

- the entrypoint
- 2 to 4 directly related modules

If it needs to inspect 10 files or scan a 20,000-line module, the design is too broad for that
flow.

## What Counts As One Flow

A flow is one behavior with one main reason to change.

Examples:

- launching a run from the research workspace
- evaluating a standalone query contract
- syncing one incident provider workflow
- rendering and editing replay-link governance for the query-builder
- reconciling guarded-live state after a venue snapshot refresh

A flow is not:

- "the whole control room"
- "all operator delivery"
- "all runtime logic"
- "all query-builder behavior"

Those are systems, not flows.

## Required Architectural Properties

### 1. Clear entrypoint

Every meaningful flow must have one obvious place where a reader starts.

Good:

- route module
- feature entry module
- application use-case module
- registry entry plus provider module

Bad:

- top-level shell file with embedded feature logic
- compatibility facade that still contains the real implementation
- one adapter file that owns many providers inline

### 2. Stable ownership

A model should be able to tell which module owns which concern.

Good ownership split:

- entry or shell
- domain or policy
- storage or persistence
- transport or external I/O
- UI rendering

Bad ownership split:

- one file owns policy, persistence, URL state, rendering, and async transport

### 3. Local reasoning

A flow should be modifiable by local reasoning.

That means:

- changing replay-link governance should not require reopening the whole query-builder
- adding one incident provider should not require editing a giant provider matrix
- changing one route layout should not require touching core feature logic

### 4. Explicit authority

The model must be able to tell which state is authoritative.

Examples:

- route state belongs in route modules or route hooks
- feature-local persistence belongs in feature modules
- provider capability lookup belongs in a registry
- compatibility re-export files must not become the hidden source of truth

### 5. Bounded collaborator count

Each flow should have only a few direct collaborators.

As a practical rule:

- entrypoint plus 2 to 4 collaborators is healthy
- entrypoint plus 5 to 8 collaborators is warning territory
- beyond that, split by concern or by sub-flow

This is a heuristic, not a hard compiler rule.
But the warning should be taken seriously.

## Anti-Patterns

The following patterns are hostile to LLM-sensitive architecture.

### Giant shell files

Example smell:

- `App.tsx` owns routing, feature state, transport helpers, payload formatting, and dense JSX

Why it fails:

- the model cannot isolate one workspace flow
- unrelated edits become likely
- route and feature boundaries collapse

### Giant application facades

Example smell:

- `application.py` is a compatibility entrypoint and also the real implementation for many use
  cases

Why it fails:

- one backend change requires broad context
- use-case ownership becomes ambiguous
- policy and orchestration blur together

### Giant provider adapters

Example smell:

- `operator_delivery.py` owns many provider-specific request builders and workflow sync branches

Why it fails:

- provider behavior is not locally understandable
- adding one provider risks breaking others
- registry and adapter boundaries become decorative only

### Mixed feature modules

Example smell:

- one query-builder component owns parser logic, replay persistence, governance UI, trace rendering,
  transport calls, and state mutation

Why it fails:

- the model cannot tell which change belongs to which sub-flow
- storage and presentation bugs become intertwined

## Good Patterns

### Tiny entry modules

Good entry modules should mostly do one of these:

- re-export the public feature surface
- compose route-level children
- wire a use case to explicit collaborators

If an entrypoint starts accumulating parsing, storage, or dense rendering, it is no longer an
entrypoint.

### Registry-driven extension

When a family of implementations grows, use:

- registry for discovery
- narrow module per provider or per capability family
- compatibility shim only when needed

This keeps extension local.

### Concern split inside one feature

When one feature becomes large, split by concerns that map to how a reader thinks:

- model and types
- persistence or storage
- transport or server API
- view sections
- policy helpers

This is better than random splitting by line count.

## Repository-Specific Interpretation

### Frontend

For this repository, frontend LLM sensitivity means:

- `App.tsx` should be shell composition, not feature ownership
- route modules should group panels, not contain deep feature internals
- each feature package should have a tiny public entry
- dense feature sections should split when they become separate operator sub-flows

Concrete example:

- moving replay-link governance out of the main query-builder body is good because replay
  governance is a separate sub-flow with its own state, actions, and review logic

### Backend

For this repository, backend LLM sensitivity means:

- `application.py` shrinks toward facade status
- use-case logic moves into support or use-case modules
- `ports.py` stays a compatibility shim, not a dumping ground
- provider logic moves behind registries and provider-owned modules

Concrete example:

- moving standalone surface execution helpers and binding catalog out of `application.py` improves
  local reasoning for query execution flows

## Review Questions

Before adding new code, ask:

1. What is the single flow I am changing?
2. Where is the real entrypoint for that flow?
3. Which module should own state?
4. Which module should own policy?
5. Which module should own I/O?
6. Can this change be understood from the entrypoint plus a few direct collaborators?
7. Am I about to put unrelated logic into a shell, facade, or adapter file?

If those questions do not have obvious answers, stop and split first.

## Practical Rules For This Repository

- do not add new dense feature logic to `App.tsx`
- do not add new provider-specific branches to giant adapter files when a registry path exists
- do not add new use-case policy into compatibility shim modules
- do not let one feature component become the place where storage, transport, policy, and dense UI
  all meet permanently
- split by sub-flow before adding more behavior when a module becomes hard to explain in one short
  paragraph

## Concrete Good/Bad Examples

### Better

- `apps/web/src/features/query-builder/index.tsx`
  - tiny public entrypoint
- `apps/web/src/features/query-builder/QueryBuilderReplayGovernanceSection.tsx`
  - separate replay-governance sub-flow view
- `apps/api/src/akra_trader/adapters/operator_delivery_registry.py`
  - explicit provider dispatch boundary
- `apps/api/src/akra_trader/application_support/standalone_surfaces.py`
  - standalone surface execution logic separated from facade code

### Still Risky

- `apps/web/src/features/query-builder/RunSurfaceCollectionQueryBuilder.tsx`
  - still too broad for one reader pass
- `apps/web/src/App.tsx`
  - still larger than a shell should be
- `apps/api/src/akra_trader/application.py`
  - still too broad as a facade
- `apps/api/src/akra_trader/adapters/operator_delivery.py`
  - still carries too much provider body

## Success Condition

This repository is LLM-sensitive enough when a weaker model can:

- find the right entrypoint quickly
- understand one flow without reading the whole product
- make a local change without drifting into unrelated code
- identify the owner of state, policy, I/O, and rendering without guesswork

That is the standard.
Not "the model is smart enough to figure it out anyway".
