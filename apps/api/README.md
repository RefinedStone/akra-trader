# Akra Trader API

Python-first backend for strategy registration, market-data access, backtesting, and paper trading.

## Run

```bash
python3 -m pip install -e ".[dev]"
uvicorn akra_trader.main:app --reload
```

## Test

```bash
pytest
```
