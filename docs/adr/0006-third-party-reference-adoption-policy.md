# ADR 0006: Third-Party Reference Adoption Policy

## Status

Accepted

## Context

The project now keeps multiple third-party references locally, including:

- NautilusTrader
- NostalgiaForInfinity
- ccxt
- yfinance

These references serve different purposes. Some are architecture references, some are external runtime
lanes, and some may eventually become direct dependencies. Without an explicit policy, code and design
decisions can become inconsistent or accidentally cross legal and architectural boundaries.

## Decision

All third-party materials will be governed through a reference catalog and explicit integration modes.

The supported integration modes are:

- `ideas_only`
- `external_runtime`
- `direct_dependency_candidate`

Reference adoption rules:

- `ideas_only`: may influence architecture and runtime design, but may not be vendored into the core
- `external_runtime`: may be executed or orchestrated as a separate lane, but may not define native
  platform contracts
- `direct_dependency_candidate`: may be adopted behind adapters after a deliberate implementation choice

Current policy anchors:

- NautilusTrader: `ideas_only`
- NostalgiaForInfinity: `external_runtime`
- ccxt: `direct_dependency_candidate`
- yfinance: `direct_dependency_candidate`

## Consequences

Positive:

- third-party usage becomes explicit and auditable
- reference strategies remain benchmark lanes instead of hidden architecture shortcuts
- licensing and integration posture become part of product design instead of an afterthought

Negative:

- some potentially useful code cannot be copied directly even when it would be faster
- external-runtime lanes require import/provenance plumbing rather than direct in-process reuse

## Implementation notes

- `reference/catalog.toml` is the canonical catalog of reference posture
- directions and backlog planning should treat reference posture as a first-class planning input
- native contracts must remain owned by `akra-trader` even when external references are heavily used
