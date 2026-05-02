from __future__ import annotations

from akra_trader.application_context import *  # noqa: F403
from akra_trader import application_context as _application_context

globals().update({
  name: getattr(_application_context, name)
  for name in dir(_application_context)
  if name.startswith("_") and not name.startswith("__")
})

class TradingApplicationGuardedLiveConsistencyMixin:
  def _collect_guarded_live_ladder_integrity_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    venue = handoff.venue or "venue"
    detected_at = handoff.order_book_last_rebuilt_at or handoff.last_depth_event_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if handoff.order_book_gap_count > 0:
      gap_detail = f"{venue} ladder integrity recorded {handoff.order_book_gap_count} depth gap(s)."
      if handoff.order_book_last_update_id is not None:
        gap_detail += f" Last update id: {handoff.order_book_last_update_id}."
      add_finding(gap_detail, critical=True)

    if handoff.order_book_rebuild_count > 0:
      add_finding(
        f"{venue} ladder integrity required {handoff.order_book_rebuild_count} snapshot rebuild(s).",
      )

    for issue_detail in self._extract_guarded_live_ladder_integrity_semantics(issues=handoff.issues):
      add_finding(issue_detail, critical=True)

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical
  def _collect_guarded_live_venue_ladder_integrity_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    detected_at = handoff.order_book_last_rebuilt_at or handoff.last_depth_event_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if handoff.order_book_state == "rebuild_failed":
      add_finding(
        f"{handoff.venue or 'venue'} ladder snapshot rebuild is currently failing.",
        critical=True,
      )

    for issue_detail in self._extract_guarded_live_venue_ladder_integrity_semantics(issues=handoff.issues):
      add_finding(issue_detail, critical=True)

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical
  def _collect_guarded_live_ladder_bridge_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    detected_at = handoff.last_depth_event_at or handoff.order_book_last_rebuilt_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    for issue_detail in self._extract_guarded_live_ladder_bridge_semantics(issues=handoff.issues):
      add_finding(issue_detail, critical=True)

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical
  def _collect_guarded_live_ladder_sequence_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    detected_at = handoff.last_depth_event_at or handoff.order_book_last_rebuilt_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    for issue_detail in self._extract_guarded_live_ladder_sequence_semantics(issues=handoff.issues):
      add_finding(issue_detail, critical=True)

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical
  def _collect_guarded_live_ladder_snapshot_refresh_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    detected_at = handoff.last_depth_event_at or handoff.order_book_last_rebuilt_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    for issue_detail in self._extract_guarded_live_ladder_snapshot_refresh_semantics(issues=handoff.issues):
      add_finding(issue_detail, critical=True)

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical
  def _collect_guarded_live_channel_restore_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    findings: list[str] = []
    detected_candidates: list[datetime] = []
    restore_anchor = handoff.channel_last_restored_at or handoff.last_sync_at or handoff.handed_off_at or current_time
    has_critical = False

    def add_finding(detail: str, *, detected_at: datetime | None, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if handoff.channel_restore_state == "partial":
      add_finding(
        "market-channel restore completed only partially.",
        detected_at=restore_anchor,
      )
    elif handoff.channel_restore_state == "unavailable":
      add_finding(
        "market-channel restore is unavailable.",
        detected_at=restore_anchor,
        critical=True,
      )

    if handoff.channel_continuation_state == "partial":
      add_finding(
        "market-channel continuation is only partially supervised.",
        detected_at=handoff.channel_last_continued_at or restore_anchor,
      )
    elif handoff.channel_continuation_state == "unavailable":
      add_finding(
        "market-channel continuation is unavailable.",
        detected_at=handoff.channel_last_continued_at or restore_anchor,
        critical=True,
      )

    for issue_detail in self._extract_guarded_live_channel_restore_semantics(issues=handoff.issues):
      add_finding(
        issue_detail,
        detected_at=restore_anchor,
        critical=True,
      )

    detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), detected_at, has_critical
  def _collect_guarded_live_book_consistency_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    snapshot = handoff.book_ticker_snapshot
    if (
      handoff.order_book_state in {"inactive", "released"}
      and snapshot is None
    ):
      return [], current_time, False

    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    venue = handoff.venue or "venue"
    tolerance = self._guarded_live_balance_tolerance

    def add_finding(detail: str, *, detected_at: datetime | None, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    best_bid = handoff.order_book_best_bid_price
    best_ask = handoff.order_book_best_ask_price
    if best_bid is not None and best_ask is not None and best_bid > (best_ask + tolerance):
      add_finding(
        f"{venue} local order book is crossed: best bid {best_bid:.8f} is above best ask {best_ask:.8f}.",
        detected_at=handoff.last_depth_event_at or handoff.order_book_last_rebuilt_at or handoff.last_sync_at,
        critical=True,
      )

    if snapshot is not None:
      if (
        snapshot.bid_price is not None
        and snapshot.ask_price is not None
        and snapshot.bid_price > (snapshot.ask_price + tolerance)
      ):
        add_finding(
          f"{venue} book-ticker quote is crossed: bid {snapshot.bid_price:.8f} is above ask {snapshot.ask_price:.8f}.",
          detected_at=snapshot.event_at or handoff.last_book_ticker_event_at or handoff.last_sync_at,
          critical=True,
        )
      if (
        best_bid is not None
        and snapshot.ask_price is not None
        and best_bid > (snapshot.ask_price + tolerance)
      ):
        add_finding(
          f"{venue} local best bid {best_bid:.8f} is above book-ticker ask {snapshot.ask_price:.8f}.",
          detected_at=snapshot.event_at or handoff.last_book_ticker_event_at or handoff.last_sync_at,
          critical=True,
        )
      if (
        snapshot.bid_price is not None
        and best_ask is not None
        and snapshot.bid_price > (best_ask + tolerance)
      ):
        add_finding(
          f"{venue} book-ticker bid {snapshot.bid_price:.8f} is above local best ask {best_ask:.8f}.",
          detected_at=snapshot.event_at or handoff.last_book_ticker_event_at or handoff.last_sync_at,
          critical=True,
        )

    detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), detected_at, has_critical
  def _collect_guarded_live_kline_consistency_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    snapshot = handoff.kline_snapshot
    if snapshot is None:
      return [], current_time, False

    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    venue = handoff.venue or "venue"
    tolerance = self._guarded_live_balance_tolerance

    def add_finding(detail: str, *, detected_at: datetime | None, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if (
      snapshot.timeframe is not None
      and handoff.timeframe is not None
      and snapshot.timeframe != handoff.timeframe
    ):
      add_finding(
        f"{venue} kline timeframe {snapshot.timeframe} does not match the guarded-live timeframe {handoff.timeframe}.",
        detected_at=snapshot.event_at or handoff.last_kline_event_at or handoff.last_sync_at,
      )

    if (
      snapshot.open_at is not None
      and snapshot.close_at is not None
      and snapshot.close_at <= snapshot.open_at
    ):
      add_finding(
        f"{venue} kline closes at {snapshot.close_at.isoformat()} before or at its open {snapshot.open_at.isoformat()}.",
        detected_at=snapshot.event_at or snapshot.close_at or handoff.last_kline_event_at,
        critical=True,
      )

    if (
      snapshot.high_price is not None
      and snapshot.low_price is not None
      and snapshot.high_price + tolerance < snapshot.low_price
    ):
      add_finding(
        f"{venue} kline high {snapshot.high_price:.8f} is below low {snapshot.low_price:.8f}.",
        detected_at=snapshot.event_at or handoff.last_kline_event_at or handoff.last_sync_at,
        critical=True,
      )
    elif snapshot.high_price is not None and snapshot.low_price is not None:
      if (
        snapshot.open_price is not None
        and (
          snapshot.open_price > snapshot.high_price + tolerance
          or snapshot.open_price + tolerance < snapshot.low_price
        )
      ):
        add_finding(
          f"{venue} kline open {snapshot.open_price:.8f} falls outside the high/low range "
          f"{snapshot.low_price:.8f}-{snapshot.high_price:.8f}.",
          detected_at=snapshot.event_at or handoff.last_kline_event_at or handoff.last_sync_at,
          critical=True,
        )
      if (
        snapshot.close_price is not None
        and (
          snapshot.close_price > snapshot.high_price + tolerance
          or snapshot.close_price + tolerance < snapshot.low_price
        )
      ):
        add_finding(
          f"{venue} kline close {snapshot.close_price:.8f} falls outside the high/low range "
          f"{snapshot.low_price:.8f}-{snapshot.high_price:.8f}.",
          detected_at=snapshot.event_at or handoff.last_kline_event_at or handoff.last_sync_at,
          critical=True,
        )

    detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), detected_at, has_critical
  def _collect_guarded_live_candle_sequence_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    snapshot = handoff.kline_snapshot
    if snapshot is None:
      return [], current_time, False

    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    venue = handoff.venue or "venue"
    timeframe = snapshot.timeframe or handoff.timeframe
    timeframe_delta = self._guarded_live_timeframe_to_timedelta(timeframe)
    detected_at = snapshot.event_at or handoff.last_kline_event_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if timeframe_delta is not None and snapshot.open_at is not None:
      if not self._datetime_is_aligned_to_interval(snapshot.open_at, timeframe_delta):
        add_finding(
          f"{venue} kline open {snapshot.open_at.isoformat()} is not aligned to the {timeframe} timeframe boundary."
        )

    if timeframe_delta is not None and snapshot.open_at is not None and snapshot.close_at is not None:
      expected_close_at = snapshot.open_at + timeframe_delta
      if snapshot.close_at != expected_close_at:
        add_finding(
          f"{venue} kline close {snapshot.close_at.isoformat()} does not match the expected {timeframe} boundary close "
          f"{expected_close_at.isoformat()}.",
          critical=True,
        )

    if snapshot.closed and snapshot.event_at is not None and snapshot.close_at is not None and snapshot.event_at < snapshot.close_at:
      add_finding(
        f"{venue} closed kline event arrived at {snapshot.event_at.isoformat()} before the candle close "
        f"{snapshot.close_at.isoformat()}.",
        critical=True,
      )

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical
  @staticmethod
  def _guarded_live_timeframe_to_timedelta(timeframe: str | None) -> timedelta | None:
    if not timeframe or len(timeframe) < 2:
      return None
    unit = timeframe[-1]
    try:
      amount = int(timeframe[:-1])
    except ValueError:
      return None
    if amount <= 0:
      return None
    return {
      "m": timedelta(minutes=amount),
      "h": timedelta(hours=amount),
      "d": timedelta(days=amount),
      "w": timedelta(weeks=amount),
    }.get(unit)
  @staticmethod
  def _datetime_is_aligned_to_interval(value: datetime, interval: timedelta) -> bool:
    if interval.total_seconds() <= 0:
      return False
    epoch = datetime(1970, 1, 1, tzinfo=UTC)
    return ((value - epoch).total_seconds() % interval.total_seconds()) == 0
  @staticmethod
  def _resolve_guarded_live_market_channel_activity(
    *,
    handoff: GuardedLiveVenueSessionHandoff,
  ) -> tuple[tuple[str, datetime | None, bool], ...]:
    coverage = set(handoff.coverage)
    activity: list[tuple[str, datetime | None, bool]] = []
    if "trade_ticks" in coverage:
      activity.append(("trade ticks", handoff.last_trade_event_at, False))
    if "aggregate_trade_ticks" in coverage:
      activity.append(("aggregate-trade ticks", handoff.last_aggregate_trade_event_at, False))
    if "book_ticker" in coverage:
      activity.append(("book-ticker updates", handoff.last_book_ticker_event_at, False))
    if "mini_ticker" in coverage:
      activity.append(("mini-ticker updates", handoff.last_mini_ticker_event_at, False))
    if "depth_updates" in coverage or "order_book_lifecycle" in coverage:
      activity.append(("depth/order-book updates", handoff.last_depth_event_at, True))
    if "kline_candles" in coverage:
      activity.append(("kline candles", handoff.last_kline_event_at, False))
    return tuple(activity)
  @staticmethod
  def _extract_guarded_live_channel_gap_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_order_book_gap_detected:" not in issue:
        continue
      venue, payload = issue.split("_order_book_gap_detected:", 1)
      previous_update_id, _, next_update_id = payload.partition(":")
      if previous_update_id and next_update_id:
        findings.append(
          f"{venue} depth stream gap detected between update ids {previous_update_id} and {next_update_id}."
        )
      else:
        findings.append(f"{venue} depth stream gap detected.")
    return tuple(dict.fromkeys(findings))
  @classmethod
  def _extract_guarded_live_ladder_integrity_semantics(
    cls,
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    return cls._extract_guarded_live_channel_gap_semantics(issues=issues)
  @staticmethod
  def _extract_guarded_live_venue_ladder_integrity_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_order_book_snapshot_failed:" in issue:
        venue, payload = issue.split("_order_book_snapshot_failed:", 1)
        reason, _, detail = payload.partition(":")
        reason_label = reason.replace("_", " ") if reason else "unknown"
        if detail:
          findings.append(f"{venue} ladder snapshot rebuild failed during {reason_label}: {detail}.")
        else:
          findings.append(f"{venue} ladder snapshot rebuild failed during {reason_label}.")
        continue
      if "_order_book_snapshot_missing_side:" in issue:
        venue, payload = issue.split("_order_book_snapshot_missing_side:", 1)
        side = payload.replace("_", " ") if payload else "unknown side"
        findings.append(f"{venue} ladder snapshot returned no {side} levels.")
        continue
      if "_order_book_snapshot_crossed:" in issue:
        venue, payload = issue.split("_order_book_snapshot_crossed:", 1)
        bid, _, ask = payload.partition(":")
        if bid and ask:
          try:
            bid_value = f"{float(bid):.8f}"
            ask_value = f"{float(ask):.8f}"
          except ValueError:
            bid_value = bid
            ask_value = ask
          findings.append(
            f"{venue} ladder snapshot is crossed: best bid {bid_value} is above best ask {ask_value}."
          )
        else:
          findings.append(f"{venue} ladder snapshot is crossed.")
        continue
      if "_order_book_snapshot_non_monotonic:" not in issue:
        continue
      venue, payload = issue.split("_order_book_snapshot_non_monotonic:", 1)
      side, _, remainder = payload.partition(":")
      index, _, price_payload = remainder.partition(":")
      price, _, previous_price = price_payload.partition(":")
      side_label = side[:-1] if side.endswith("s") else side
      ordering = "descending" if side == "bids" else "ascending"
      if index and price and previous_price:
        try:
          price_value = f"{float(price):.8f}"
          previous_price_value = f"{float(previous_price):.8f}"
        except ValueError:
          price_value = price
          previous_price_value = previous_price
        findings.append(
          f"{venue} {side_label} ladder snapshot is not strictly {ordering} at level {index} "
          f"({price_value} after {previous_price_value})."
        )
      else:
        findings.append(f"{venue} {side_label} ladder snapshot is not strictly {ordering}.")
    return tuple(dict.fromkeys(findings))
  @staticmethod
  def _extract_guarded_live_ladder_bridge_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_order_book_bridge_previous_mismatch:" in issue:
        venue, payload = issue.split("_order_book_bridge_previous_mismatch:", 1)
        expected_previous, _, actual_previous = payload.partition(":")
        findings.append(
          f"{venue} depth bridge expected previous update id {expected_previous or 'unknown'} "
          f"but received {actual_previous or 'unknown'}."
        )
        continue
      if "_order_book_bridge_range_mismatch:" in issue:
        venue, payload = issue.split("_order_book_bridge_range_mismatch:", 1)
        expected_next, _, remainder = payload.partition(":")
        first_update_id, _, last_update_id = remainder.partition(":")
        findings.append(
          f"{venue} depth bridge range {first_update_id or 'unknown'}-{last_update_id or 'unknown'} "
          f"does not cover expected next update id {expected_next or 'unknown'}."
        )
        continue
    return tuple(dict.fromkeys(findings))
  @staticmethod
  def _extract_guarded_live_ladder_sequence_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_order_book_sequence_mismatch:" not in issue:
        continue
      venue, payload = issue.split("_order_book_sequence_mismatch:", 1)
      expected_previous, _, remainder = payload.partition(":")
      actual_previous, _, current_update_id = remainder.partition(":")
      findings.append(
        f"{venue} ladder sequence expected previous update id {expected_previous or 'unknown'} "
        f"but received {actual_previous or 'unknown'} before update {current_update_id or 'unknown'}."
      )
    return tuple(dict.fromkeys(findings))
  @staticmethod
  def _extract_guarded_live_ladder_snapshot_refresh_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_order_book_snapshot_refresh:" not in issue:
        continue
      venue, payload = issue.split("_order_book_snapshot_refresh:", 1)
      previous_update_id, _, next_update_id = payload.partition(":")
      findings.append(
        f"{venue} ladder snapshot refresh replaced update id {previous_update_id or 'unknown'} "
        f"with {next_update_id or 'unknown'}."
      )
    return tuple(dict.fromkeys(findings))
  @staticmethod
  def _extract_guarded_live_channel_restore_semantics(
    *,
    issues: tuple[str, ...],
  ) -> tuple[str, ...]:
    findings: list[str] = []
    for issue in issues:
      if "_market_channel_restore_failed:" not in issue:
        continue
      venue, payload = issue.split("_market_channel_restore_failed:", 1)
      channel, _, remainder = payload.partition(":")
      reason = remainder.replace("_", " ") if remainder else "unknown"
      channel_label = channel.replace("_", " ") if channel else "market channel"
      findings.append(
        f"{venue} {channel_label} restore failed: {reason}."
      )
    return tuple(dict.fromkeys(findings))
