from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Mapping

import httpx


BINANCE_RWA_BASE_URL = "https://www.binance.com"
BINANCE_RWA_TOKEN_LIST_PATH = (
  "/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/rwa/stock/detail/list/ai"
)
BINANCE_RWA_KLINE_PATH = (
  "/bapi/defi/v1/public/wallet-direct/buw/wallet/dex/market/token/kline/ai"
)
BINANCE_RWA_USER_AGENT = "binance-web3/1.1 (Skill)"
RWA_MAX_KLINE_LIMIT = 300
SUPPORTED_RWA_INTERVALS = frozenset(("1m", "5m", "15m", "1h", "4h", "12h", "1d"))


class BinanceRwaApiError(RuntimeError):
  pass


@dataclass(frozen=True)
class BinanceRwaToken:
  chain_id: str
  contract_address: str
  symbol: str
  ticker: str
  multiplier: float | None = None


JsonGetter = Callable[[str, Mapping[str, Any]], Mapping[str, Any]]


class BinanceRwaMarketDataClient:
  def __init__(
    self,
    *,
    base_url: str = BINANCE_RWA_BASE_URL,
    timeout_seconds: float = 15.0,
    json_getter: JsonGetter | None = None,
  ) -> None:
    self._base_url = base_url.rstrip("/")
    self._timeout_seconds = timeout_seconds
    self._json_getter = json_getter
    self._token_cache: tuple[BinanceRwaToken, ...] | None = None

  @property
  def max_kline_limit(self) -> int:
    return RWA_MAX_KLINE_LIMIT

  def fetch_ohlcv(
    self,
    symbol: str,
    timeframe: str = "5m",
    since: int | None = None,
    limit: int | None = None,
  ) -> list[list[float]]:
    if timeframe not in SUPPORTED_RWA_INTERVALS:
      raise ValueError(f"Unsupported Binance RWA timeframe: {timeframe}")
    token = self.resolve_token(symbol)
    request_limit = min(max(limit or RWA_MAX_KLINE_LIMIT, 1), RWA_MAX_KLINE_LIMIT)
    params: dict[str, Any] = {
      "chainId": token.chain_id,
      "contractAddress": token.contract_address,
      "interval": timeframe,
      "limit": request_limit,
    }
    if since is not None:
      params["startTime"] = since

    payload = self._get_json(BINANCE_RWA_KLINE_PATH, params)
    if not _is_successful_payload(payload):
      if payload.get("code") == "000002" and since is not None:
        return []
      raise BinanceRwaApiError(
        f"Binance RWA kline failed: {payload.get('code')} {payload.get('message')}"
      )

    data = payload.get("data")
    if not isinstance(data, Mapping):
      return []
    raw_rows = data.get("klineInfos")
    if not isinstance(raw_rows, list):
      return []

    rows: list[list[float]] = []
    for raw in raw_rows:
      if not isinstance(raw, list) or len(raw) < 5:
        continue
      rows.append(
        [
          int(raw[0]),
          float(raw[1]),
          float(raw[2]),
          float(raw[3]),
          float(raw[4]),
          _parse_optional_float(raw[5] if len(raw) > 5 else 0),
        ]
      )
    return rows

  def resolve_token(self, symbol: str) -> BinanceRwaToken:
    requested = _normalize_requested_symbol(symbol)
    requested_ticker = requested[:-2] if requested.lower().endswith("on") else requested
    matches = [
      token
      for token in self.list_tokens()
      if token.symbol.lower() == requested.lower()
      or token.ticker.upper() == requested_ticker.upper()
    ]
    if not matches:
      raise ValueError(f"Unsupported Binance RWA tokenized security: {symbol}")
    return sorted(matches, key=_token_preference_key)[0]

  def list_tokens(self) -> tuple[BinanceRwaToken, ...]:
    if self._token_cache is not None:
      return self._token_cache
    payload = self._get_json(BINANCE_RWA_TOKEN_LIST_PATH, {"type": 1})
    if not _is_successful_payload(payload):
      raise BinanceRwaApiError(
        f"Binance RWA token list failed: {payload.get('code')} {payload.get('message')}"
      )
    data = payload.get("data")
    if not isinstance(data, list):
      self._token_cache = ()
      return self._token_cache

    tokens: list[BinanceRwaToken] = []
    for raw in data:
      if not isinstance(raw, Mapping):
        continue
      chain_id = str(raw.get("chainId") or "").strip()
      contract_address = str(raw.get("contractAddress") or "").strip()
      token_symbol = str(raw.get("symbol") or "").strip()
      ticker = str(raw.get("ticker") or "").strip()
      if not chain_id or not contract_address or not token_symbol or not ticker:
        continue
      tokens.append(
        BinanceRwaToken(
          chain_id=chain_id,
          contract_address=contract_address,
          symbol=token_symbol,
          ticker=ticker,
          multiplier=_parse_nullable_float(raw.get("multiplier")),
        )
      )
    self._token_cache = tuple(tokens)
    return self._token_cache

  def _get_json(self, path: str, params: Mapping[str, Any]) -> Mapping[str, Any]:
    url = f"{self._base_url}{path}"
    if self._json_getter is not None:
      return self._json_getter(url, params)
    headers = {
      "Accept-Encoding": "identity",
      "User-Agent": BINANCE_RWA_USER_AGENT,
    }
    with httpx.Client(timeout=self._timeout_seconds, headers=headers) as client:
      response = client.get(url, params=params)
      response.raise_for_status()
      payload = response.json()
    if not isinstance(payload, Mapping):
      raise BinanceRwaApiError("Binance RWA response was not a JSON object")
    return payload


def is_binance_rwa_symbol(symbol: str) -> bool:
  normalized = _normalize_requested_symbol(symbol)
  return bool(normalized) and "/" not in normalized


def _normalize_requested_symbol(symbol: str) -> str:
  stripped = symbol.strip()
  if ":" in stripped:
    return stripped.split(":", 1)[1].strip()
  return stripped


def _is_successful_payload(payload: Mapping[str, Any]) -> bool:
  return payload.get("success") is True and payload.get("code") == "000000"


def _parse_optional_float(value: Any) -> float:
  try:
    return float(value)
  except (TypeError, ValueError):
    return 0.0


def _parse_nullable_float(value: Any) -> float | None:
  try:
    return float(value)
  except (TypeError, ValueError):
    return None


def _token_preference_key(token: BinanceRwaToken) -> tuple[int, str, str]:
  chain_priority = {"56": 0, "1": 1}
  return (
    chain_priority.get(token.chain_id, 10),
    token.chain_id,
    token.contract_address,
  )
