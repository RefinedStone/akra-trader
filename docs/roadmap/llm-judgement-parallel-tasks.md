# LLM Judgement Parallel Tasks

Task list for the isolated LLM judgement research lane. This file expands the
roadmap item for prompt registry, trace storage, replay, evaluation, and
fallback/review controls.

## Baseline

- `DecisionEnginePort`, `ExternalDecisionStrategy`, and `LlmFunctionLayer` already define the
  provider-neutral interface shape.
- The current runtime exposes the LLM lane as `interface_only`; no provider adapter is configured.
- LLM work remains limited to backtest and sandbox research until replay, audit, fallback, and
  review controls exist.
- LLM decisions must continue to emit `StrategyDecisionEnvelope` and flow through the shared risk
  and execution pipeline.

## Parallel Task List

- [ ] LLM-JDG-01: Prompt registry and versioning
  - Define prompt profiles, template versions, prompt digests, schema metadata, and retirement
    rules.
  - Record prompt profile, version, digest, input schema, and output schema in each decision trace.
  - Done when a run can be reproduced against the exact prompt metadata used for every LLM call.

- [ ] LLM-JDG-02: Provider adapter boundary
  - Add provider adapters behind `DecisionEnginePort` or `LlmFunctionLayer` without provider
    branching in domain or application code.
  - Normalize timeout, retry, error, confidence, token, latency, and model metadata.
  - Done when a disabled adapter and at least one configured adapter return the same envelope shape.

- [ ] LLM-JDG-03: Raw trace and artifact storage
  - Persist prompt inputs, provider responses, normalized outputs, fallback state, and redacted
    provider metadata as run artifacts.
  - Store large or sensitive payloads through artifact paths instead of bloating run summaries.
  - Done when decision traces can be browsed from experiment history without payload-only scans.

- [ ] LLM-JDG-04: Replay harness
  - Re-run stored LLM decision inputs through the original prompt metadata and a selected provider
    mode.
  - Support deterministic replay where possible and explicit nondeterminism reporting where not.
  - Done when replay output can be compared with the original decision trace for a completed run.

- [ ] LLM-JDG-05: Evaluation harness
  - Score LLM decisions against deterministic fallback, benchmark strategy decisions, and outcome
    metrics.
  - Track disagreement, fallback frequency, confidence calibration, latency, and cost summaries.
  - Done when a run report shows whether the LLM lane improved, matched, or degraded baseline
    behavior.

- [ ] LLM-JDG-06: Fallback and operator review controls
  - Require deterministic fallback behavior for provider errors, invalid schemas, low confidence, or
    unsupported modes.
  - Add an operator-review state before any guarded-live exploration.
  - Done when no LLM decision can bypass fallback/review gates or shared risk controls.

- [ ] LLM-JDG-07: Backtest and sandbox API surfaces
  - Expose prompt profile selection, provider status, trace summaries, replay links, and evaluation
    summaries through bounded API surfaces.
  - Keep live promotion disabled until audit criteria are satisfied.
  - Done when backtest and sandbox users can inspect LLM judgement results without direct artifact
    digging.

- [ ] LLM-JDG-08: Control-room inspection UI
  - Show isolation state, provider adapter status, prompt version, fallback status, replay status,
    and evaluation summary in the LLM strategy area.
  - Keep active runtime views separate from research-only LLM surfaces.
  - Done when operators can tell whether an LLM judgement came from provider output, fallback, or
    review hold.

- [ ] LLM-JDG-09: Test and governance coverage
  - Cover envelope compatibility, prompt metadata persistence, adapter errors, fallback paths,
    replay comparison, and evaluation summaries.
  - Add docs for allowed modes, data retention, redaction expectations, and live-promotion blockers.
  - Done when the LLM lane can be changed without weakening auditability or provider isolation.

## Suggested Parallelization

- Start `LLM-JDG-01`, `LLM-JDG-02`, and `LLM-JDG-03` together because they define adjacent but
  separable contracts.
- Start `LLM-JDG-04` after trace artifacts exist.
- Start `LLM-JDG-05` after replay comparison has a stable output shape.
- Start `LLM-JDG-06` alongside adapter work, then enforce it before exposing broader UI controls.
- Start `LLM-JDG-07` and `LLM-JDG-08` after the API contracts for traces, replay, and evaluation
  are stable.

## Non-Goals

- No unattended LLM-driven live trading.
- No provider-specific shortcuts around domain, risk, or execution boundaries.
- No prompt or response storage that leaks credentials or unrestricted sensitive payloads.
