from __future__ import annotations

from typing import Any
from typing import Mapping

from akra_trader.adapters.binance_rwa import BINANCE_RWA_KLINE_PATH
from akra_trader.adapters.binance_rwa import BINANCE_RWA_TOKEN_LIST_PATH
from akra_trader.adapters.binance_rwa import BinanceRwaMarketDataClient


def test_binance_rwa_client_resolves_preferred_chain_and_normalizes_kline_rows():
  calls: list[tuple[str, Mapping[str, Any]]] = []

  def fake_getter(url: str, params: Mapping[str, Any]) -> Mapping[str, Any]:
    calls.append((url, dict(params)))
    if url.endswith(BINANCE_RWA_TOKEN_LIST_PATH):
      return {
        "code": "000000",
        "success": True,
        "data": [
          {
            "chainId": "1",
            "contractAddress": "0xeth",
            "symbol": "QQQon",
            "ticker": "QQQ",
            "type": 1,
            "multiplier": "1.0",
          },
          {
            "chainId": "56",
            "contractAddress": "0xbsc",
            "symbol": "QQQon",
            "ticker": "QQQ",
            "type": 1,
            "multiplier": "1.0",
          },
        ],
      }
    if url.endswith(BINANCE_RWA_KLINE_PATH):
      return {
        "code": "000000",
        "success": True,
        "data": {
          "klineInfos": [
            [1_775_001_600_000, "581.39", "582.04", "580.98", "581.96", "0", 1],
          ],
          "decimals": 5,
        },
      }
    raise AssertionError(f"unexpected URL: {url}")

  client = BinanceRwaMarketDataClient(json_getter=fake_getter)

  rows = client.fetch_ohlcv("QQQ", timeframe="5m", since=1_775_001_600_000, limit=500)

  assert rows == [[1_775_001_600_000, 581.39, 582.04, 580.98, 581.96, 0.0]]
  assert calls[-1][1] == {
    "chainId": "56",
    "contractAddress": "0xbsc",
    "interval": "5m",
    "limit": 300,
    "startTime": 1_775_001_600_000,
  }


def test_binance_rwa_client_treats_too_old_start_as_empty_result():
  def fake_getter(url: str, params: Mapping[str, Any]) -> Mapping[str, Any]:
    if url.endswith(BINANCE_RWA_TOKEN_LIST_PATH):
      return {
        "code": "000000",
        "success": True,
        "data": [
          {
            "chainId": "56",
            "contractAddress": "0xbsc",
            "symbol": "QQQon",
            "ticker": "QQQ",
          },
        ],
      }
    return {"code": "000002", "success": False, "message": "illegal parameter"}

  client = BinanceRwaMarketDataClient(json_getter=fake_getter)

  assert client.fetch_ohlcv("QQQon", since=1_683_936_000_000) == []
