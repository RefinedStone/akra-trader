# Product Roadmap

## Objective

Over the next 6 months, `akra-trader` should evolve from an architectural skeleton into a usable single-operator trading research platform for crypto markets, with guarded progression from research to sandbox trading and then to controlled live execution.

The primary user is a solo developer or quant who needs:

- reproducible backtests
- fast strategy iteration
- an operations view for running sandbox and live sessions
- a safe path to test LLM-assisted decision systems

## Product north star

The platform should let one operator do the following without ad hoc scripts:

1. ingest and inspect market data
2. register or update a strategy version
3. run backtests with stored parameters and reproducible results
4. compare runs and understand why results differ
5. monitor a sandbox run in near real time
6. enable guarded live trading with explicit risk limits
7. evaluate LLM-driven decisions alongside deterministic strategies

## Release stages

## Stage 0: Baseline

Current state:

- architecture and strategy abstraction exist
- seeded market data drives the demo engines
- runs are stored in memory
- the UI is suitable for inspection, not operations
- NFI reference strategies can be cataloged and backtest commands can be prepared

Exit signal:

- roadmap and ADR set is published
- priorities and acceptance criteria are fixed

## Stage 1: Research Foundation

Target window:

- Weeks 1-4

User outcome:

- a user can load real Binance OHLCV data, run a backtest, and retrieve the run later with the exact config that produced it

Required outcomes:

- persistent run storage
- real market data ingestion
- strategy version and parameter snapshot storage
- reproducible run metadata
- basic historical run listing in UI

Release criteria:

- backtest results survive restart
- market data can be resynced without corrupting stored candles
- identical run inputs reproduce identical results

## Stage 2: Research Workflow

Target window:

- Weeks 5-8

User outcome:

- a user can treat backtesting as an experiment workflow rather than a one-off action

Required outcomes:

- strategy version lifecycle
- run tags and scenario presets
- metric comparison across runs
- benchmark runs for native strategies and NFI reference strategies
- artifact links for logs, signal traces, and result snapshots

Release criteria:

- a user can compare at least two runs in the UI or API
- each run stores strategy version, parameters, venue, timeframe, and dataset lineage
- NFI reference runs and native runs are visibly separated but comparable

## Stage 3: Real-Time Sandbox Operations

Target window:

- Weeks 9-12

User outcome:

- a user can keep sandbox strategies running continuously and inspect operational health from one dashboard

Required outcomes:

- continuous market-data stream or polling worker
- long-running sandbox execution worker
- alerts for worker failure, stale data, and risk breaches
- run heartbeat, status transitions, and restart behavior
- richer control-room views for positions, orders, fills, and lag

Release criteria:

- sandbox runs can stay active without manual replay triggering
- operator can stop, restart, and inspect runs from the platform
- alerting is generated for stale data and worker failure

## Stage 4: Controlled Live Trading

Target window:

- Weeks 13-18

User outcome:

- a user can run very limited live trading with strict guardrails and full auditability

Required outcomes:

- live execution adapter for the first exchange
- secret management for exchange credentials
- exposure limits, loss limits, kill switch, and operator approval paths
- order reconciliation and exchange state synchronization
- execution audit log and operator event log

Release criteria:

- live orders are blocked if risk controls are not configured
- order and position state can be reconciled after restart
- every live action has an audit record

## Stage 5: LLM Decision Research Lane

Target window:

- Parallel from Weeks 9-24

User outcome:

- a user can test LLM-assisted decision making without letting prompt-driven behavior leak into deterministic execution paths

Required outcomes:

- decision-engine contract finalized
- prompt template versioning
- prompt and response trace storage
- replay harness for evaluating LLM decisions against historical contexts
- operator review mode before any live usage

Release criteria:

- LLM strategies can be evaluated in backtest and sandbox modes through the same decision envelope
- every LLM decision stores rationale, prompt version, and raw response trace
- a deterministic fallback path exists for every promoted LLM strategy

## Success measures

By the end of the 6-month roadmap, the platform should satisfy these product checks:

- one-click backtest history is available for all recent runs
- at least one exchange is supported end-to-end for data, sandbox, and guarded live execution
- NFI reference strategies remain usable as a benchmark lane
- the UI can answer "what is running, what changed, and why" without shell access
- LLM strategy research is supported as a first-class but gated lane

## Explicit deferrals

The following are intentionally not first-line priorities in this roadmap:

- equal-weight support for stocks and crypto
- multi-user RBAC or organization workflows
- multi-node distributed execution
- optimization for broad public/self-service use
