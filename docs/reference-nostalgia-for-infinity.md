# NostalgiaForInfinity Reference Notes

## Summary

- Source checkout: `reference/NostalgiaForInfinity`
- License: `GPL-3.0`
- Role in `akra-trader`: reference strategy lane executed through external Freqtrade tooling

NostalgiaForInfinity is valuable to us less as a code template and more as a record of what a mature,
battle-tested crypto strategy ecosystem needs in practice: config layering, exchange-specific pairlists,
blacklists, strong exit handling, position adjustment, and operational backtest conventions.

## What To Borrow

### Operational conventions

The upstream repository is strong on run conventions:

- layered config files
- exchange-specific pairlists and blacklists
- clear backtest commands
- Docker-based execution patterns
- reference strategy naming and versioning

These are directly useful. Our current `FreqtradeReferenceAdapter` already follows this direction by
assembling upstream-like backtest commands instead of re-implementing the strategy logic.

### Strategy concepts

NFI highlights several capabilities that our native engine must eventually support:

- strong exit-mode separation
- position adjustment / scale-in behavior
- selective hold logic
- stake sizing distinct from entry logic
- exchange-aware warmup and configuration rules

These concepts are more reusable than the monolithic implementation. They are the reason our native
strategy abstraction now needs separate signal and execution layers.

### Benchmark lane

NFI is ideal as a benchmark lane:

- compare native strategy ideas against a known external strategy
- import reference run provenance
- validate orchestration without claiming native feature parity

This is also the safest way to benefit from the repo without collapsing our own boundaries.

## What To Use Carefully

### Freqtrade coupling

NFI is tightly coupled to Freqtrade contracts such as:

- `populate_indicators`
- `populate_entry_trend`
- `custom_exit`
- `adjust_trade_position`

That is acceptable for the reference lane, but those contracts should not become our native strategy API.
Our internal strategy boundary must stay platform-owned.

### Configuration sprawl

The repository contains many exchange, pairlist, and deployment files. This is useful operationally, but
we should import those ideas with discipline rather than copying the entire configuration surface into our
native engine too early.

## What Not To Do

- Do not paste NFI strategy code into native `akra-trader` strategies.
- Do not mix indicator calculation, signal generation, exit logic, and position management into a single
  class the way upstream Freqtrade strategies often do.
- Do not let GPL-covered strategy code cross into our native core without an explicit legal and product
  decision.
- Do not claim native parity with NFI while we are still delegating execution through Freqtrade.

## Acceptable Integration Paths

### External runtime delegation

This is the current and preferred path.

- keep NFI as a third-party checkout
- expose it in the strategy catalog as a `freqtrade_reference` runtime
- prepare and execute upstream-style backtest commands
- record provenance such as reference id, version, and external command

### Temporary dry-run lane

If we need to reuse NFI behavior before native parity exists, a future dry-run or guarded live lane can
also be delegated to Freqtrade. That should still be treated as an external runtime, not a native engine.

## Immediate Actions For `akra-trader`

- Keep NFI in the `reference` catalog as `external_runtime`.
- Continue recording external command provenance for delegated runs.
- Import backtest artifacts and summary metrics into our own run records instead of importing strategy code.
- Use NFI requirements to guide native work on execution policies, exits, scale-in, and operator controls.
