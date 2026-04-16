# Architecture

## Core rule

Domain and application code do not know about FastAPI, ccxt, SQLAlchemy, or Freqtrade internals.

## Layers

### Domain

- Market model: instrument, candle, order, fill, position, trade, run config
- Strategy model: metadata, execution state, decision context, decision envelope
- Pure services: order application, equity curve generation, performance summary

### Application

- Strategy registration
- Backtest execution
- Sandbox replay execution
- Run lookup and status changes
- Market-data status queries

### Ports

- `MarketDataPort`
- `RunRepositoryPort`
- `StrategyCatalogPort`
- `DecisionEnginePort`
- `ReferenceCatalogPort`

## Strategy abstraction

The strategy boundary is split on purpose.

### Feature frame

Transforms raw candles into enriched analysis data.

Examples:

- SMA/EMA/volatility columns
- multi-timeframe joins
- sentiment or regime features

### Decision context

Collects the exact slice of information used to decide.

Examples:

- latest feature values
- current OHLCV view
- open position state
- cash, size, parameter snapshot

### Signal policy

Generates the directional trading decision.

Examples:

- crossover / breakout / regime rules
- delegated LLM choice
- reference strategy placeholder signals

### Execution policy

Transforms a signal into execution intent.

Examples:

- full-notional entry
- scale-in permission
- partial exit permission
- future stop-loss / take-profit directives

### Decision envelope

Wraps the final signal, execution plan, rationale, and trace metadata.

Examples:

- `BUY` / `SELL` / `HOLD`
- size fraction and scaling flags
- human-readable explanation
- future prompt/response traces for LLM strategies

## Strategy families

### Native

- Fully executed by the platform's native simulation engine
- Current example: moving-average crossover

### Freqtrade reference

- Catalog entry points directly to files under `reference/NostalgiaForInfinity`
- Backtest path delegates to a Freqtrade command assembled from upstream NFI config conventions
- Preserves the ability to reuse NFI nearly as-is
- Run records store external provenance such as reference id, version, and command

### External decision engine

- Intended for LLM-based strategies
- Uses the same feature/context contract
- Only the final `decide()` step is delegated to an external engine

## Reference catalog

Third-party repositories are tracked in `reference/catalog.toml`.

Each entry records:

- reference id
- license
- integration mode
- runtime
- local checkout path

This lets the application distinguish between:

- ideas-only references such as NautilusTrader
- external-runtime references such as NostalgiaForInfinity
- direct dependency candidates such as ccxt and yfinance

## Near-term extension points

- Replace in-memory run storage with SQLAlchemy/Postgres adapters
- Replace seeded market data with Binance/ccxt adapters
- Add continuous sandbox/live workers around the same application services
- Add prompt logging and audit trails for decision-engine strategies
- Split the native runtime toward `DataEngine`, `ExecutionEngine`, `RiskEngine`, and `StateCache`
