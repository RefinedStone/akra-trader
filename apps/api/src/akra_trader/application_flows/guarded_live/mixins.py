from __future__ import annotations

from datetime import datetime

from akra_trader.domain.models import GuardedLiveReconciliationFinding
from akra_trader.domain.models import OperatorAlert
from akra_trader.domain.models import RunMode
from akra_trader.domain.models import RunStatus


class GuardedLiveAlertCompatibilityMixin:
  def _build_guarded_live_reconciliation_result(
    self,
    *,
    state: GuardedLiveState | None = None,
  ) -> tuple[
    GuardedLiveInternalStateSnapshot,
    GuardedLiveVenueStateSnapshot,
    list[GuardedLiveReconciliationFinding],
  ]:
    findings: list[GuardedLiveReconciliationFinding] = []
    effective_state = state or self._guarded_live_state.load_state()
    internal_snapshot = self._build_guarded_live_internal_snapshot(state=effective_state)
    venue_snapshot = self._venue_state.capture_snapshot()

    if venue_snapshot.venue != self._guarded_live_venue:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="guarded_live_venue_mismatch",
          severity="critical",
          summary="Venue-state snapshot does not match the configured guarded-live venue.",
          detail=(
            f"Guarded-live is configured for {self._guarded_live_venue}, "
            f"but venue-state reconciliation captured {venue_snapshot.venue}."
          ),
        )
      )

    sandbox_alerts, _ = self._collect_sandbox_operator_visibility(current_time=self._clock())
    if sandbox_alerts:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="runtime_alerts_present",
          severity="warning",
          summary=f"{len(sandbox_alerts)} unresolved runtime alert(s) remain active.",
          detail="Guarded-live candidacy stays blocked while sandbox runtime alerts remain unresolved.",
        )
      )

    inconsistent_sandbox_runs = [
      run
      for run in self._runs.list_runs(mode=RunMode.SANDBOX.value)
      if run.status == RunStatus.RUNNING and run.provenance.runtime_session is None
    ]
    if inconsistent_sandbox_runs:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="sandbox_runtime_session_missing",
          severity="critical",
          summary=(
            f"{len(inconsistent_sandbox_runs)} sandbox run(s) are missing persisted runtime session state."
          ),
          detail="Continuous sandbox workers must keep runtime-session state for restart safety and auditability.",
        )
      )

    inconsistent_live_runs = [
      run
      for run in self._runs.list_runs(mode=RunMode.LIVE.value)
      if run.status == RunStatus.RUNNING and run.provenance.runtime_session is None
    ]
    if inconsistent_live_runs:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="live_runtime_session_missing",
          severity="critical",
          summary=(
            f"{len(inconsistent_live_runs)} live run(s) are missing persisted runtime session state."
          ),
          detail="Guarded-live workers must keep runtime-session state for restart safety and venue auditability.",
        )
      )

    stale_terminal_sessions = [
      run
      for run in self._runs.list_runs(mode=RunMode.SANDBOX.value)
      if (
        run.status in {RunStatus.STOPPED, RunStatus.FAILED, RunStatus.COMPLETED}
        and run.provenance.runtime_session is not None
        and run.provenance.runtime_session.lifecycle_state == "active"
      )
    ]
    if stale_terminal_sessions:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="terminal_runtime_session_active",
          severity="warning",
          summary=(
            f"{len(stale_terminal_sessions)} terminal sandbox run(s) still report an active runtime session."
          ),
          detail="Terminal runs should not keep active worker-session state after stop, failure, or completion.",
        )
      )

    stale_terminal_live_sessions = [
      run
      for run in self._runs.list_runs(mode=RunMode.LIVE.value)
      if (
        run.status in {RunStatus.STOPPED, RunStatus.FAILED, RunStatus.COMPLETED}
        and run.provenance.runtime_session is not None
        and run.provenance.runtime_session.lifecycle_state == "active"
      )
    ]
    if stale_terminal_live_sessions:
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="terminal_live_runtime_session_active",
          severity="warning",
          summary=(
            f"{len(stale_terminal_live_sessions)} terminal live run(s) still report an active runtime session."
          ),
          detail="Terminal guarded-live runs should not keep active worker-session state after stop or failure.",
        )
      )

    if venue_snapshot.verification_state != "verified":
      findings.append(
        GuardedLiveReconciliationFinding(
          kind="venue_snapshot_unavailable",
          severity="critical" if venue_snapshot.verification_state == "unavailable" else "warning",
          summary=(
            "Venue-state verification is unavailable."
            if venue_snapshot.verification_state == "unavailable"
            else "Venue-state verification completed with partial data."
          ),
          detail=(
            ", ".join(venue_snapshot.issues)
            if venue_snapshot.issues
            else "The venue adapter did not return a fully verified account snapshot."
          ),
        )
      )

    findings.extend(
      self._build_guarded_live_venue_mismatch_findings(
        internal_snapshot=internal_snapshot,
        venue_snapshot=venue_snapshot,
      )
    )
    return internal_snapshot, venue_snapshot, findings

  def _build_guarded_live_operator_alerts(
    self,
    *,
    state: GuardedLiveState,
    current_time: datetime,
  ) -> list[OperatorAlert]:
    alerts: list[OperatorAlert] = []
    delivery_targets = self._guarded_live_delivery_targets()
    live_runs = self._runs.list_runs(mode=RunMode.LIVE.value)
    live_context_active = bool(live_runs) or state.ownership.state in {"owned", "orphaned"}
    guarded_live_context_symbol = self._first_non_empty_string(
      state.ownership.symbol,
      state.session_handoff.symbol,
      state.session_restore.symbol,
      state.order_book.symbol,
    )
    guarded_live_context_timeframe = self._first_non_empty_string(
      state.session_handoff.timeframe,
      state.session_restore.timeframe,
    )

    alerts.extend(
      self._build_guarded_live_market_data_alerts(
        live_runs=live_runs,
        current_time=current_time,
      )
    )

    if state.kill_switch.state == "engaged":
      detected_at = state.kill_switch.last_engaged_at or state.kill_switch.updated_at
      alerts.append(
        OperatorAlert(
          alert_id="guarded-live:kill-switch",
          severity="warning",
          category="kill_switch",
          summary="Guarded-live kill switch is engaged.",
          detail=(
            f"{state.kill_switch.reason} Updated by {state.kill_switch.updated_by} at "
            f"{state.kill_switch.updated_at.isoformat()}."
          ),
          detected_at=detected_at,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if state.reconciliation.state == "issues_detected":
      finding_copy = "; ".join(finding.summary for finding in state.reconciliation.findings[:3])
      alerts.append(
        OperatorAlert(
          alert_id="guarded-live:reconciliation",
          severity=(
            "critical"
            if any(finding.severity == "critical" for finding in state.reconciliation.findings)
            else "warning"
          ),
          category="reconciliation",
          summary="Guarded-live reconciliation has unresolved findings.",
          detail=(
            f"{state.reconciliation.summary} "
            f"{finding_copy if finding_copy else 'Review the guarded-live venue snapshot and internal exposure state.'}"
          ),
          detected_at=state.reconciliation.checked_at or current_time,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if state.recovery.state == "failed":
      alerts.append(
        OperatorAlert(
          alert_id="guarded-live:recovery-failed",
          severity="critical",
          category="runtime_recovery",
          summary="Guarded-live runtime recovery failed.",
          detail=(
            f"{state.recovery.summary} Issues: "
            f"{', '.join(state.recovery.issues) if state.recovery.issues else 'none'}."
          ),
          detected_at=state.recovery.recovered_at or current_time,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if state.ownership.state == "orphaned":
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:ownership:{state.ownership.owner_run_id or 'unknown'}",
          severity="critical",
          category="session_ownership",
          summary="Guarded-live session ownership is orphaned.",
          detail=(
            f"Run {state.ownership.owner_run_id or 'n/a'} still owns the guarded-live session, "
            f"but the live worker is not healthy. Last reason: {state.ownership.last_reason or 'n/a'}."
          ),
          detected_at=(
            state.ownership.last_heartbeat_at
            or state.ownership.last_resumed_at
            or state.ownership.claimed_at
            or current_time
          ),
          run_id=state.ownership.owner_run_id,
          session_id=state.ownership.owner_session_id,
          **self._build_operator_alert_market_context(
            symbol=state.ownership.symbol,
            timeframe=guarded_live_context_timeframe,
          ),
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    if live_context_active and state.session_handoff.state == "unavailable":
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:session-transport:{state.ownership.owner_run_id or 'unknown'}",
          severity="critical",
          category="session_transport",
          summary="Guarded-live venue session transport is unavailable.",
          detail=(
            "Venue-native session supervision could not be maintained. Issues: "
            f"{', '.join(state.session_handoff.issues) if state.session_handoff.issues else 'none'}."
          ),
          detected_at=state.session_handoff.last_sync_at or state.session_handoff.handed_off_at or current_time,
          run_id=state.ownership.owner_run_id,
          session_id=state.ownership.owner_session_id,
          **self._build_operator_alert_market_context(
            symbol=guarded_live_context_symbol,
            timeframe=guarded_live_context_timeframe,
          ),
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )
    elif live_context_active and state.session_handoff.issues:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:session-issues:{state.ownership.owner_run_id or 'unknown'}",
          severity="warning",
          category="session_transport",
          summary="Guarded-live venue session requires operator review.",
          detail=", ".join(state.session_handoff.issues),
          detected_at=state.session_handoff.last_sync_at or state.session_handoff.handed_off_at or current_time,
          run_id=state.ownership.owner_run_id,
          session_id=state.ownership.owner_session_id,
          **self._build_operator_alert_market_context(
            symbol=guarded_live_context_symbol,
            timeframe=guarded_live_context_timeframe,
          ),
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    order_book_issue_copy: list[str] = []
    if state.session_handoff.order_book_state == "unavailable":
      order_book_issue_copy.append("venue order-book supervision is unavailable")
    if state.order_book.issues:
      order_book_issue_copy.extend(state.order_book.issues)
    if live_context_active and order_book_issue_copy:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:order-book:{state.ownership.owner_run_id or 'unknown'}",
          severity="warning",
          category="order_book",
          summary="Guarded-live order-book supervision requires review.",
          detail="; ".join(order_book_issue_copy),
          detected_at=(
            state.order_book.synced_at
            or state.session_handoff.last_sync_at
            or state.session_handoff.handed_off_at
            or current_time
          ),
          run_id=state.ownership.owner_run_id,
          session_id=state.ownership.owner_session_id,
          **self._build_operator_alert_market_context(
            symbol=guarded_live_context_symbol,
            timeframe=guarded_live_context_timeframe,
          ),
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    alerts.extend(
      self._build_guarded_live_channel_operator_alerts(
        state=state,
        current_time=current_time,
        live_context_active=live_context_active,
        delivery_targets=delivery_targets,
      )
    )

    for run in live_runs:
      alerts.extend(self._build_live_operator_alerts_for_run(run=run, current_time=current_time))

    alerts.sort(key=lambda alert: alert.detected_at, reverse=True)
    return alerts

  def _build_guarded_live_market_data_alerts(
    self,
    *,
    live_runs: list[RunRecord],
    current_time: datetime,
  ) -> list[OperatorAlert]:
    alerts: list[OperatorAlert] = []
    delivery_targets = self._guarded_live_delivery_targets()
    live_symbol_order = self._normalize_operator_alert_symbols(
      [
        symbol
        for run in live_runs
        for symbol in run.config.symbols
      ]
    )
    live_symbols = {
      symbol
      for run in live_runs
      for symbol in run.config.symbols
    }
    for timeframe in self._resolve_guarded_live_market_data_timeframes(live_runs=live_runs):
      try:
        status = self._market_data.get_status(timeframe)
      except Exception as exc:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data:{timeframe}",
            severity="critical",
            category="market_data_freshness",
            summary=f"Guarded-live market-data freshness policy could not be evaluated for {timeframe}.",
            detail=f"Market-data status query failed: {exc}.",
            detected_at=current_time,
            **self._build_operator_alert_market_context(
              symbols=sorted(live_symbols),
              timeframe=timeframe,
              primary_focus=self._build_operator_alert_primary_focus(
                symbols=live_symbol_order or sorted(live_symbols),
                timeframe=timeframe,
                policy="live_symbol_order",
                reason=(
                  "Primary focus follows the active live symbol order because "
                  "market-data status could not be scored."
                ),
              ),
            ),
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
        continue
      if status.provider == "seeded":
        continue

      relevant_instruments = [
        instrument
        for instrument in status.instruments
        if not live_symbols or self._symbol_from_instrument_id(instrument.instrument_id) in live_symbols
      ]
      relevant_symbols = sorted(
        {
          self._symbol_from_instrument_id(instrument.instrument_id)
          for instrument in relevant_instruments
        }
      )
      primary_focus = self._resolve_market_data_alert_primary_focus(
        instruments=relevant_instruments,
        timeframe=timeframe,
        symbol_order=live_symbol_order or relevant_symbols,
      )
      if live_symbols and not relevant_instruments:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data:{timeframe}",
            severity="critical",
            category="market_data_freshness",
            summary=f"Guarded-live market-data freshness policy is uncovered for {timeframe}.",
            detail=(
              "No tracked market-data status covered the active live symbol set: "
              f"{', '.join(sorted(live_symbols))}."
            ),
            detected_at=current_time,
            **self._build_operator_alert_market_context(
              symbols=sorted(live_symbols),
              timeframe=timeframe,
              primary_focus=self._build_operator_alert_primary_focus(
                symbols=live_symbol_order or sorted(live_symbols),
                timeframe=timeframe,
                policy="live_symbol_order",
                reason=(
                  "Primary focus follows the active live symbol order because "
                  "no market-data status covered the live symbol set."
                ),
              ),
            ),
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
        continue

      critical_details: list[str] = []
      quality_details: list[str] = []
      continuity_details: list[str] = []
      venue_details: list[str] = []
      quality_has_critical = False
      continuity_has_critical = False
      venue_has_critical = False
      detected_candidates: list[datetime] = []
      for instrument in relevant_instruments:
        symbol = self._symbol_from_instrument_id(instrument.instrument_id)
        if instrument.last_sync_at is not None:
          detected_candidates.append(instrument.last_sync_at)
        if instrument.last_timestamp is not None:
          detected_candidates.append(instrument.last_timestamp)
        if instrument.recent_failures:
          detected_candidates.extend(failure.failed_at for failure in instrument.recent_failures)

        if instrument.sync_status == "error":
          critical_details.append(f"{symbol} last sync failed.")
        elif instrument.sync_status == "empty":
          critical_details.append(f"{symbol} has no persisted candles for {timeframe}.")
        elif instrument.sync_status == "stale":
          lag_detail = (
            f" lagged {instrument.lag_seconds}s"
            if instrument.lag_seconds is not None
            else " breached the freshness window"
          )
          critical_details.append(f"{symbol}{lag_detail}.")

        missing_candles = instrument.backfill_contiguous_missing_candles
        if missing_candles is None and instrument.backfill_gap_windows:
          missing_candles = sum(window.missing_candles for window in instrument.backfill_gap_windows)
        if missing_candles and missing_candles > 0:
          continuity_details.append(
            f"{symbol} has {missing_candles} missing candle(s) across "
            f"{len(instrument.backfill_gap_windows)} gap window(s)."
          )
        if (
          instrument.backfill_target_candles is not None
          and instrument.backfill_completion_ratio is not None
          and instrument.backfill_complete is False
        ):
          quality_details.append(
            f"{symbol} backfill target covers {instrument.backfill_completion_ratio * 100:.2f}% "
            f"of {instrument.backfill_target_candles} candles."
          )
          if instrument.backfill_completion_ratio < self._guarded_live_market_data_backfill_completion_floor:
            quality_has_critical = True
        if (
          instrument.backfill_contiguous_completion_ratio is not None
          and instrument.backfill_contiguous_complete is False
        ):
          continuity_details.append(
            f"{symbol} contiguous backfill quality is "
            f"{instrument.backfill_contiguous_completion_ratio * 100:.2f}%."
          )
          if (
            instrument.backfill_contiguous_completion_ratio
            < self._guarded_live_market_data_contiguous_completion_floor
          ):
            continuity_has_critical = True
        if instrument.failure_count_24h > 0:
          venue_details.append(
            f"{symbol} recorded {instrument.failure_count_24h} sync failure(s) in the last 24h."
          )
          if instrument.failure_count_24h >= self._guarded_live_market_data_failure_burst_threshold:
            venue_has_critical = True
        elif instrument.recent_failures:
          latest_failure = instrument.recent_failures[0]
          venue_details.append(
            f"{symbol} last failure was {latest_failure.operation}: {latest_failure.error}."
          )
        venue_semantics = self._extract_market_data_venue_semantics(
          venue=status.venue,
          issues=instrument.issues,
        )
        if venue_semantics:
          venue_details.append(
            f"{symbol} venue semantics: {', '.join(venue_semantics)}."
          )
          if any(
            semantic in {"authentication fault", "symbol unavailable"}
            for semantic in venue_semantics
          ):
            venue_has_critical = True

      detail_copy = list(dict.fromkeys(critical_details))
      detected_at = max(detected_candidates) if detected_candidates else current_time
      if detail_copy:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data:{timeframe}",
            severity="critical" if critical_details else "warning",
            category="market_data_freshness",
            summary=f"Guarded-live market-data freshness policy is degraded for {timeframe}.",
            detail=(
              " ".join(detail_copy[:3])
              + (f" Additional issues: {len(detail_copy) - 3}." if len(detail_copy) > 3 else "")
            ),
            detected_at=detected_at,
            **self._build_operator_alert_market_context(
              symbols=relevant_symbols,
              timeframe=timeframe,
              primary_focus=primary_focus,
            ),
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
      quality_detail_copy = list(dict.fromkeys(quality_details))
      if quality_detail_copy:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data-quality:{status.venue}:{timeframe}",
            severity="critical" if quality_has_critical else "warning",
            category="market_data_quality",
            summary=f"Guarded-live market-data quality policy is degraded for {status.venue} {timeframe}.",
            detail=(
              " ".join(quality_detail_copy[:3])
              + (f" Additional issues: {len(quality_detail_copy) - 3}." if len(quality_detail_copy) > 3 else "")
            ),
            detected_at=detected_at,
            **self._build_operator_alert_market_context(
              symbols=relevant_symbols,
              timeframe=timeframe,
              primary_focus=primary_focus,
            ),
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
      continuity_detail_copy = list(dict.fromkeys(continuity_details))
      if continuity_detail_copy:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data-continuity:{status.venue}:{timeframe}",
            severity="critical" if continuity_has_critical else "warning",
            category="market_data_candle_continuity",
            summary=f"Guarded-live multi-candle continuity requires review for {status.venue} {timeframe}.",
            detail=(
              " ".join(continuity_detail_copy[:3])
              + (f" Additional issues: {len(continuity_detail_copy) - 3}." if len(continuity_detail_copy) > 3 else "")
            ),
            detected_at=detected_at,
            **self._build_operator_alert_market_context(
              symbols=relevant_symbols,
              timeframe=timeframe,
              primary_focus=primary_focus,
            ),
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
      venue_detail_copy = list(dict.fromkeys(venue_details))
      if venue_detail_copy:
        alerts.append(
          OperatorAlert(
            alert_id=f"guarded-live:market-data-venue:{status.venue}:{timeframe}",
            severity="critical" if venue_has_critical else "warning",
            category="market_data_venue",
            summary=f"Guarded-live market-data venue semantics require review for {status.venue} {timeframe}.",
            detail=(
              " ".join(venue_detail_copy[:3])
              + (f" Additional issues: {len(venue_detail_copy) - 3}." if len(venue_detail_copy) > 3 else "")
            ),
            detected_at=detected_at,
            **self._build_operator_alert_market_context(
              symbols=relevant_symbols,
              timeframe=timeframe,
              primary_focus=primary_focus,
            ),
            source="guarded_live",
            delivery_targets=delivery_targets,
          )
        )
    return alerts

  def _build_guarded_live_channel_operator_alerts(
    self,
    *,
    state: GuardedLiveState,
    current_time: datetime,
    live_context_active: bool,
    delivery_targets: tuple[str, ...],
  ) -> list[OperatorAlert]:
    if not live_context_active:
      return []

    handoff = state.session_handoff
    if handoff.state in {"inactive", "released"}:
      return []

    run_id = state.ownership.owner_run_id or handoff.owner_run_id
    session_id = state.ownership.owner_session_id or handoff.owner_session_id
    market_context = self._build_operator_alert_market_context(
      symbol=handoff.symbol,
      timeframe=handoff.timeframe,
    )
    alerts: list[OperatorAlert] = []

    consistency_details, consistency_detected_at, consistency_has_critical = (
      self._collect_guarded_live_channel_consistency_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if consistency_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-channel-consistency:{run_id or 'unknown'}",
          severity="critical" if consistency_has_critical else "warning",
          category="market_data_channel_consistency",
          summary=(
            f"Guarded-live market-data channel consistency is degraded for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(consistency_details),
          detected_at=consistency_detected_at,
          run_id=run_id,
          session_id=session_id,
          **market_context,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    ladder_integrity_details, ladder_integrity_detected_at, ladder_integrity_has_critical = (
      self._collect_guarded_live_ladder_integrity_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if ladder_integrity_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-ladder-integrity:{run_id or 'unknown'}",
          severity="critical" if ladder_integrity_has_critical else "warning",
          category="market_data_ladder_integrity",
          summary=(
            f"Guarded-live exchange ladder integrity requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(ladder_integrity_details),
          detected_at=ladder_integrity_detected_at,
          run_id=run_id,
          session_id=session_id,
          **market_context,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    venue_ladder_integrity_details, venue_ladder_integrity_detected_at, venue_ladder_integrity_has_critical = (
      self._collect_guarded_live_venue_ladder_integrity_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if venue_ladder_integrity_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-venue-ladder-integrity:{run_id or 'unknown'}",
          severity="critical" if venue_ladder_integrity_has_critical else "warning",
          category="market_data_venue_ladder_integrity",
          summary=(
            f"Guarded-live venue-native ladder integrity requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(venue_ladder_integrity_details),
          detected_at=venue_ladder_integrity_detected_at,
          run_id=run_id,
          session_id=session_id,
          **market_context,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    ladder_bridge_details, ladder_bridge_detected_at, ladder_bridge_has_critical = (
      self._collect_guarded_live_ladder_bridge_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if ladder_bridge_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-ladder-bridge:{run_id or 'unknown'}",
          severity="critical" if ladder_bridge_has_critical else "warning",
          category="market_data_ladder_bridge_integrity",
          summary=(
            f"Guarded-live ladder bridge rules require review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(ladder_bridge_details),
          detected_at=ladder_bridge_detected_at,
          run_id=run_id,
          session_id=session_id,
          **market_context,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    ladder_sequence_details, ladder_sequence_detected_at, ladder_sequence_has_critical = (
      self._collect_guarded_live_ladder_sequence_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if ladder_sequence_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-ladder-sequence:{run_id or 'unknown'}",
          severity="critical" if ladder_sequence_has_critical else "warning",
          category="market_data_ladder_sequence_integrity",
          summary=(
            f"Guarded-live ladder sequence rules require review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(ladder_sequence_details),
          detected_at=ladder_sequence_detected_at,
          run_id=run_id,
          session_id=session_id,
          **market_context,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    ladder_snapshot_refresh_details, ladder_snapshot_refresh_detected_at, ladder_snapshot_refresh_has_critical = (
      self._collect_guarded_live_ladder_snapshot_refresh_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if ladder_snapshot_refresh_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-ladder-snapshot-refresh:{run_id or 'unknown'}",
          severity="critical" if ladder_snapshot_refresh_has_critical else "warning",
          category="market_data_ladder_snapshot_refresh",
          summary=(
            f"Guarded-live ladder snapshot refresh rules require review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(ladder_snapshot_refresh_details),
          detected_at=ladder_snapshot_refresh_detected_at,
          run_id=run_id,
          session_id=session_id,
          **market_context,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    restore_details, restore_detected_at, restore_has_critical = (
      self._collect_guarded_live_channel_restore_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if restore_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-channel-restore:{run_id or 'unknown'}",
          severity="critical" if restore_has_critical else "warning",
          category="market_data_channel_restore",
          summary=(
            f"Guarded-live market-data channel restore requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(restore_details),
          detected_at=restore_detected_at,
          run_id=run_id,
          session_id=session_id,
          **market_context,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    book_details, book_detected_at, book_has_critical = self._collect_guarded_live_book_consistency_findings(
      handoff=handoff,
      current_time=current_time,
    )
    if book_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-book-consistency:{run_id or 'unknown'}",
          severity="critical" if book_has_critical else "warning",
          category="market_data_book_consistency",
          summary=(
            f"Guarded-live book consistency requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(book_details),
          detected_at=book_detected_at,
          run_id=run_id,
          session_id=session_id,
          **market_context,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    kline_details, kline_detected_at, kline_has_critical = self._collect_guarded_live_kline_consistency_findings(
      handoff=handoff,
      current_time=current_time,
    )
    if kline_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-kline-consistency:{run_id or 'unknown'}",
          severity="critical" if kline_has_critical else "warning",
          category="market_data_kline_consistency",
          summary=(
            f"Guarded-live kline consistency requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(kline_details),
          detected_at=kline_detected_at,
          run_id=run_id,
          session_id=session_id,
          **market_context,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    depth_ladder_details, depth_ladder_detected_at, depth_ladder_has_critical = (
      self._collect_guarded_live_depth_ladder_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if depth_ladder_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-depth-ladder:{run_id or 'unknown'}",
          severity="critical" if depth_ladder_has_critical else "warning",
          category="market_data_depth_ladder",
          summary=(
            f"Guarded-live depth ladder semantics require review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(depth_ladder_details),
          detected_at=depth_ladder_detected_at,
          run_id=run_id,
          session_id=session_id,
          **market_context,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )

    candle_sequence_details, candle_sequence_detected_at, candle_sequence_has_critical = (
      self._collect_guarded_live_candle_sequence_findings(
        handoff=handoff,
        current_time=current_time,
      )
    )
    if candle_sequence_details:
      alerts.append(
        OperatorAlert(
          alert_id=f"guarded-live:market-data-candle-sequence:{run_id or 'unknown'}",
          severity="critical" if candle_sequence_has_critical else "warning",
          category="market_data_candle_sequence",
          summary=(
            f"Guarded-live candle sequencing requires review for "
            f"{handoff.symbol or 'the active live session'}."
          ),
          detail=self._summarize_guarded_live_issue_copy(candle_sequence_details),
          detected_at=candle_sequence_detected_at,
          run_id=run_id,
          session_id=session_id,
          **market_context,
          source="guarded_live",
          delivery_targets=delivery_targets,
        )
      )
    return alerts

  def _collect_guarded_live_depth_ladder_findings(
    self,
    *,
    handoff: GuardedLiveVenueSessionHandoff,
    current_time: datetime,
  ) -> tuple[list[str], datetime, bool]:
    if not handoff.order_book_bids and not handoff.order_book_asks:
      return [], current_time, False

    findings: list[str] = []
    detected_candidates: list[datetime] = []
    has_critical = False
    venue = handoff.venue or "venue"
    tolerance = self._guarded_live_balance_tolerance
    detected_at = handoff.last_depth_event_at or handoff.order_book_last_rebuilt_at or handoff.last_sync_at

    def add_finding(detail: str, *, critical: bool = False) -> None:
      nonlocal has_critical
      findings.append(detail)
      has_critical = has_critical or critical
      if detected_at is not None:
        detected_candidates.append(detected_at)

    if handoff.order_book_bid_level_count and handoff.order_book_bid_level_count != len(handoff.order_book_bids):
      add_finding(
        f"{venue} bid ladder count {len(handoff.order_book_bids)} does not match stored bid level count "
        f"{handoff.order_book_bid_level_count}.",
        critical=True,
      )
    if handoff.order_book_ask_level_count and handoff.order_book_ask_level_count != len(handoff.order_book_asks):
      add_finding(
        f"{venue} ask ladder count {len(handoff.order_book_asks)} does not match stored ask level count "
        f"{handoff.order_book_ask_level_count}.",
        critical=True,
      )

    if handoff.order_book_bids and (
      handoff.order_book_best_bid_price is not None or handoff.order_book_best_bid_quantity is not None
    ):
      head = handoff.order_book_bids[0]
      if (
        (handoff.order_book_best_bid_price is not None and abs(head.price - handoff.order_book_best_bid_price) > tolerance)
        or (
          handoff.order_book_best_bid_quantity is not None
          and abs(head.quantity - handoff.order_book_best_bid_quantity) > tolerance
        )
      ):
        add_finding(
          f"{venue} best bid ladder head {head.price:.8f}/{head.quantity:.8f} does not match stored "
          f"best bid {handoff.order_book_best_bid_price or 0.0:.8f}/"
          f"{handoff.order_book_best_bid_quantity or 0.0:.8f}.",
          critical=True,
        )
    if handoff.order_book_asks and (
      handoff.order_book_best_ask_price is not None or handoff.order_book_best_ask_quantity is not None
    ):
      head = handoff.order_book_asks[0]
      if (
        (handoff.order_book_best_ask_price is not None and abs(head.price - handoff.order_book_best_ask_price) > tolerance)
        or (
          handoff.order_book_best_ask_quantity is not None
          and abs(head.quantity - handoff.order_book_best_ask_quantity) > tolerance
        )
      ):
        add_finding(
          f"{venue} best ask ladder head {head.price:.8f}/{head.quantity:.8f} does not match stored "
          f"best ask {handoff.order_book_best_ask_price or 0.0:.8f}/"
          f"{handoff.order_book_best_ask_quantity or 0.0:.8f}.",
          critical=True,
        )

    previous_price: float | None = None
    for index, level in enumerate(handoff.order_book_bids, start=1):
      if level.quantity <= tolerance:
        add_finding(
          f"{venue} bid ladder level {index} has non-positive quantity {level.quantity:.8f}.",
          critical=True,
        )
      if previous_price is not None and level.price >= (previous_price - tolerance):
        add_finding(
          f"{venue} bid ladder is not strictly descending at level {index} "
          f"({level.price:.8f} after {previous_price:.8f}).",
          critical=True,
        )
      previous_price = level.price

    previous_price = None
    for index, level in enumerate(handoff.order_book_asks, start=1):
      if level.quantity <= tolerance:
        add_finding(
          f"{venue} ask ladder level {index} has non-positive quantity {level.quantity:.8f}.",
          critical=True,
        )
      if previous_price is not None and level.price <= (previous_price + tolerance):
        add_finding(
          f"{venue} ask ladder is not strictly ascending at level {index} "
          f"({level.price:.8f} after {previous_price:.8f}).",
          critical=True,
        )
      previous_price = level.price

    resolved_detected_at = max(detected_candidates) if detected_candidates else current_time
    return list(dict.fromkeys(findings)), resolved_detected_at, has_critical

