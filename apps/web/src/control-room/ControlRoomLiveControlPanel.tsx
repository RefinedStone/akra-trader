// @ts-nocheck

import { ControlRoomLiveIncidentHistory } from "./ControlRoomLiveIncidentHistory";

export function ControlRoomLiveControlPanel({ model }: { model: any }) {
  const {
    formatTimestamp,
    PanelDisclosure,
    summarizeProviderRecoveryMarketContextProvenance,
    formatParameterMap,
    formatProviderRecoveryTelemetry,
    formatProviderRecoverySchema,
    guardedLive,
    guardedLiveSummary,
    setGuardedLiveReason,
    guardedLiveReason,
    runGuardedLiveReconciliation,
    recoverGuardedLiveRuntime,
    resumeGuardedLiveRun,
    engageGuardedLiveKillSwitch,
    releaseGuardedLiveKillSwitch,
    formatFixedNumber,
    activeGuardedLiveAlertIds,
    remediateGuardedLiveIncident,
    acknowledgeGuardedLiveIncident,
    escalateGuardedLiveIncident,
  } = model;

  return (

              <section className="panel panel-wide">
          <p className="kicker">Guarded live</p>
          <h2>Kill switch and reconciliation</h2>
          {guardedLive ? (
            <div className="status-grid">
              {guardedLiveSummary ? (
                <>
                  <div className="metric-tile">
                    <span>Candidacy</span>
                    <strong>{guardedLive.candidacy_status}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Kill switch</span>
                    <strong>{guardedLive.kill_switch.state}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Runtime alerts</span>
                    <strong>{guardedLive.active_runtime_alert_count}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Venue verification</span>
                    <strong>{guardedLive.reconciliation.venue_snapshot?.verification_state ?? "n/a"}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Last reconciliation</span>
                    <strong>{formatTimestamp(guardedLiveSummary.latestReconciliationAt)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Last recovery</span>
                    <strong>{formatTimestamp(guardedLiveSummary.latestRecoveryAt)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Blockers</span>
                    <strong>{guardedLiveSummary.blockerCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Live owner</span>
                    <strong>{guardedLive.ownership.state}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Order-book sync</span>
                    <strong>{formatTimestamp(guardedLiveSummary.latestOrderSyncAt)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Session restore</span>
                    <strong>{guardedLive.session_restore.state}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Session handoff</span>
                    <strong>{guardedLive.session_handoff.state}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Latest audit</span>
                    <strong>{formatTimestamp(guardedLiveSummary.latestAuditAt)}</strong>
                  </div>
                </>
              ) : null}
              <div className="control-action-row">
                <label className="control-action-field">
                  <span>Operator reason</span>
                  <input
                    onChange={(event) => setGuardedLiveReason(event.target.value)}
                    placeholder="operator_safety_drill"
                    type="text"
                    value={guardedLiveReason}
                  />
                </label>
                <button className="ghost-button" onClick={() => void runGuardedLiveReconciliation()} type="button">
                  Run reconciliation
                </button>
                <button className="ghost-button" onClick={() => void recoverGuardedLiveRuntime()} type="button">
                  Recover runtime state
                </button>
                <button className="ghost-button" onClick={() => void resumeGuardedLiveRun()} type="button">
                  Resume live owner
                </button>
                <button className="ghost-button" onClick={() => void engageGuardedLiveKillSwitch()} type="button">
                  Engage kill switch
                </button>
                <button className="ghost-button" onClick={() => void releaseGuardedLiveKillSwitch()} type="button">
                  Release kill switch
                </button>
              </div>
              <div className="panel-disclosure-grid">
                <PanelDisclosure
                  defaultOpen={true}
                  summary={`${guardedLive.kill_switch.state} kill switch · ${guardedLive.blockers.length} blockers · owner ${guardedLive.ownership.state}.`}
                  title="Control guardrails"
                >
                  <div className="panel-disclosure-stack">
                  <h3>Current guardrails</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>Kill switch</th>
                        <td>{guardedLive.kill_switch.state}</td>
                      </tr>
                      <tr>
                        <th>Updated by</th>
                        <td>{guardedLive.kill_switch.updated_by}</td>
                      </tr>
                      <tr>
                        <th>Updated at</th>
                        <td>{formatTimestamp(guardedLive.kill_switch.updated_at)}</td>
                      </tr>
                      <tr>
                        <th>Reason</th>
                        <td>{guardedLive.kill_switch.reason}</td>
                      </tr>
                      <tr>
                        <th>Running sandbox</th>
                        <td>{guardedLive.running_sandbox_count}</td>
                      </tr>
                      <tr>
                        <th>Running paper</th>
                        <td>{guardedLive.running_paper_count}</td>
                      </tr>
                      <tr>
                        <th>Running live</th>
                        <td>{guardedLive.running_live_count}</td>
                      </tr>
                      <tr>
                        <th>Owner state</th>
                        <td>{guardedLive.ownership.state}</td>
                      </tr>
                      <tr>
                        <th>Owner run</th>
                        <td>{guardedLive.ownership.owner_run_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner session</th>
                        <td>{guardedLive.ownership.owner_session_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner symbol</th>
                        <td>{guardedLive.ownership.symbol ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Claimed at</th>
                        <td>{formatTimestamp(guardedLive.ownership.claimed_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last resume</th>
                        <td>{formatTimestamp(guardedLive.ownership.last_resumed_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last order sync</th>
                        <td>{formatTimestamp(guardedLive.ownership.last_order_sync_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Restore state</th>
                        <td>{guardedLive.session_restore.state}</td>
                      </tr>
                      <tr>
                        <th>Restore source</th>
                        <td>{guardedLive.session_restore.source}</td>
                      </tr>
                      <tr>
                        <th>Restored at</th>
                        <td>{formatTimestamp(guardedLiveSummary?.latestSessionRestoreAt ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Handoff state</th>
                        <td>{guardedLive.session_handoff.state}</td>
                      </tr>
                      <tr>
                        <th>Handoff transport</th>
                        <td>{guardedLive.session_handoff.transport}</td>
                      </tr>
                      <tr>
                        <th>Last handoff sync</th>
                        <td>{formatTimestamp(guardedLiveSummary?.latestSessionHandoffAt ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Reconciliation scope</th>
                        <td>{guardedLive.reconciliation.scope}</td>
                      </tr>
                      <tr>
                        <th>Venue snapshot</th>
                        <td>
                          {guardedLive.reconciliation.venue_snapshot
                            ? `${guardedLive.reconciliation.venue_snapshot.provider} / ${guardedLive.reconciliation.venue_snapshot.venue}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Venue verified</th>
                        <td>{guardedLive.reconciliation.venue_snapshot?.verification_state ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Venue captured</th>
                        <td>{formatTimestamp(guardedLive.reconciliation.venue_snapshot?.captured_at ?? null)}</td>
                      </tr>
                    </tbody>
                  </table>
                  <h3>Candidate blockers</h3>
                  {guardedLive.blockers.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Blocker</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.blockers.map((blocker) => (
                          <tr key={blocker}>
                            <td>{blocker}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No guarded-live blockers recorded.</p>
                  )}
                  </div>
                </PanelDisclosure>
                <PanelDisclosure
                  defaultOpen={false}
                  summary={`${guardedLive.reconciliation.findings.length} findings · ${guardedLive.incident_events.length} incidents · ${guardedLive.order_book.open_orders.length} durable orders.`}
                  title="Venue state, recovery, and incidents"
                >
                  <div className="panel-disclosure-stack panel-disclosure-scroll">
                  <h3>Reconciliation findings</h3>
                  {guardedLive.reconciliation.findings.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Severity</th>
                          <th>Finding</th>
                          <th>Summary</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.reconciliation.findings.map((finding) => (
                          <tr key={`${finding.kind}-${finding.summary}`}>
                            <td>{finding.severity}</td>
                            <td>{finding.kind}</td>
                            <td>
                              <strong>{finding.summary}</strong>
                              <p className="run-lineage-symbol-copy">{finding.detail}</p>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">{guardedLive.reconciliation.summary}</p>
                  )}
                  <h3>Venue snapshot</h3>
                  {guardedLive.reconciliation.venue_snapshot ? (
                    <table className="data-table">
                      <tbody>
                        <tr>
                          <th>Provider</th>
                          <td>{guardedLive.reconciliation.venue_snapshot.provider}</td>
                        </tr>
                        <tr>
                          <th>Venue</th>
                          <td>{guardedLive.reconciliation.venue_snapshot.venue}</td>
                        </tr>
                        <tr>
                          <th>State</th>
                          <td>{guardedLive.reconciliation.venue_snapshot.verification_state}</td>
                        </tr>
                        <tr>
                          <th>Captured</th>
                          <td>{formatTimestamp(guardedLive.reconciliation.venue_snapshot.captured_at ?? null)}</td>
                        </tr>
                        <tr>
                          <th>Issues</th>
                          <td>
                            {guardedLive.reconciliation.venue_snapshot.issues.length
                              ? guardedLive.reconciliation.venue_snapshot.issues.join(", ")
                              : "none"}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No venue snapshot recorded yet.</p>
                  )}
                  <h3>Internal exposures</h3>
                  {guardedLive.reconciliation.internal_snapshot?.exposures?.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Run</th>
                          <th>Mode</th>
                          <th>Instrument</th>
                          <th>Quantity</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.reconciliation.internal_snapshot.exposures.map((exposure) => (
                          <tr key={`${exposure.run_id}-${exposure.instrument_id}`}>
                            <td>{exposure.run_id}</td>
                            <td>{exposure.mode}</td>
                            <td>{exposure.instrument_id}</td>
                            <td>{exposure.quantity.toFixed(8)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No internal open exposures recorded.</p>
                  )}
                  <h3>Venue balances</h3>
                  {guardedLive.reconciliation.venue_snapshot?.balances?.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Asset</th>
                          <th>Total</th>
                          <th>Free</th>
                          <th>Used</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.reconciliation.venue_snapshot.balances.map((balance) => (
                          <tr key={balance.asset}>
                            <td>{balance.asset}</td>
                            <td>{balance.total.toFixed(8)}</td>
                            <td>{balance.free === null || balance.free === undefined ? "n/a" : balance.free.toFixed(8)}</td>
                            <td>{balance.used === null || balance.used === undefined ? "n/a" : balance.used.toFixed(8)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No venue balances captured.</p>
                  )}
                  <h3>Venue open orders</h3>
                  {guardedLive.reconciliation.venue_snapshot?.open_orders?.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Order</th>
                          <th>Symbol</th>
                          <th>Side</th>
                          <th>Amount</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.reconciliation.venue_snapshot.open_orders.map((order) => (
                          <tr key={order.order_id}>
                            <td>{order.order_id}</td>
                            <td>{order.symbol}</td>
                            <td>{order.side}</td>
                            <td>{order.amount.toFixed(8)}</td>
                            <td>{order.status}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No venue open orders captured.</p>
                  )}
                  <h3>Recovered runtime</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>Recovery state</th>
                        <td>{guardedLive.recovery.state}</td>
                      </tr>
                      <tr>
                        <th>Recovered at</th>
                        <td>{formatTimestamp(guardedLive.recovery.recovered_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Recovered by</th>
                        <td>{guardedLive.recovery.recovered_by ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Source snapshot</th>
                        <td>{formatTimestamp(guardedLive.recovery.source_snapshot_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Source state</th>
                        <td>{guardedLive.recovery.source_verification_state}</td>
                      </tr>
                      <tr>
                        <th>Summary</th>
                        <td>{guardedLive.recovery.summary}</td>
                      </tr>
                      <tr>
                        <th>Issues</th>
                        <td>{guardedLive.recovery.issues.length ? guardedLive.recovery.issues.join(", ") : "none"}</td>
                      </tr>
                    </tbody>
                  </table>
                  <h3>Recovered exposures</h3>
                  {guardedLive.recovery.exposures.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Instrument</th>
                          <th>Asset</th>
                          <th>Quantity</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.recovery.exposures.map((exposure) => (
                          <tr key={`${exposure.instrument_id}-${exposure.asset}`}>
                            <td>{exposure.instrument_id}</td>
                            <td>{exposure.asset}</td>
                            <td>{exposure.quantity.toFixed(8)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No recovered venue exposures recorded.</p>
                  )}
                  <h3>Recovered open orders</h3>
                  {guardedLive.recovery.open_orders.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Order</th>
                          <th>Symbol</th>
                          <th>Side</th>
                          <th>Amount</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.recovery.open_orders.map((order) => (
                          <tr key={order.order_id}>
                            <td>{order.order_id}</td>
                            <td>{order.symbol}</td>
                            <td>{order.side}</td>
                            <td>{order.amount.toFixed(8)}</td>
                            <td>{order.status}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No recovered venue orders recorded.</p>
                  )}
                  <h3>Venue-native session restore</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>State</th>
                        <td>{guardedLive.session_restore.state}</td>
                      </tr>
                      <tr>
                        <th>Source</th>
                        <td>{guardedLive.session_restore.source}</td>
                      </tr>
                      <tr>
                        <th>Restored at</th>
                        <td>{formatTimestamp(guardedLive.session_restore.restored_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Venue</th>
                        <td>{guardedLive.session_restore.venue ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Symbol</th>
                        <td>{guardedLive.session_restore.symbol ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner run</th>
                        <td>{guardedLive.session_restore.owner_run_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner session</th>
                        <td>{guardedLive.session_restore.owner_session_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Issues</th>
                        <td>{guardedLive.session_restore.issues.length ? guardedLive.session_restore.issues.join(", ") : "none"}</td>
                      </tr>
                    </tbody>
                  </table>
                  {guardedLive.session_restore.synced_orders.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Order</th>
                          <th>Status</th>
                          <th>Filled</th>
                          <th>Remaining</th>
                          <th>Updated</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.session_restore.synced_orders.map((order) => (
                          <tr key={`restored-${order.order_id}`}>
                            <td>{order.order_id}</td>
                            <td>{order.status}</td>
                            <td>{(order.filled_amount ?? 0).toFixed(8)}</td>
                            <td>{(order.remaining_amount ?? 0).toFixed(8)}</td>
                            <td>{formatTimestamp(order.updated_at ?? null)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No venue-native session lifecycle rows restored yet.</p>
                  )}
                  <h3>Venue-native session stream</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>State</th>
                        <td>{guardedLive.session_handoff.state}</td>
                      </tr>
                      <tr>
                        <th>Source</th>
                        <td>{guardedLive.session_handoff.source}</td>
                      </tr>
                      <tr>
                        <th>Transport</th>
                        <td>{guardedLive.session_handoff.transport}</td>
                      </tr>
                      <tr>
                        <th>Stream started at</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.handed_off_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Released at</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.released_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last event</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last stream sync</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_sync_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Supervision</th>
                        <td>{guardedLive.session_handoff.supervision_state}</td>
                      </tr>
                      <tr>
                        <th>Failovers</th>
                        <td>{guardedLive.session_handoff.failover_count}</td>
                      </tr>
                      <tr>
                        <th>Last failover</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_failover_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Coverage</th>
                        <td>{guardedLive.session_handoff.coverage.length ? guardedLive.session_handoff.coverage.join(", ") : "none"}</td>
                      </tr>
                      <tr>
                        <th>Order book state</th>
                        <td>{guardedLive.session_handoff.order_book_state}</td>
                      </tr>
                      <tr>
                        <th>Last depth update ID</th>
                        <td>{guardedLive.session_handoff.order_book_last_update_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Depth gap count</th>
                        <td>{guardedLive.session_handoff.order_book_gap_count}</td>
                      </tr>
                      <tr>
                        <th>Rebuild count</th>
                        <td>{guardedLive.session_handoff.order_book_rebuild_count}</td>
                      </tr>
                      <tr>
                        <th>Last rebuilt at</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.order_book_last_rebuilt_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Bid levels</th>
                        <td>{guardedLive.session_handoff.order_book_bid_level_count}</td>
                      </tr>
                      <tr>
                        <th>Ask levels</th>
                        <td>{guardedLive.session_handoff.order_book_ask_level_count}</td>
                      </tr>
                      <tr>
                        <th>Channel restore</th>
                        <td>{guardedLive.session_handoff.channel_restore_state}</td>
                      </tr>
                      <tr>
                        <th>Channel restore count</th>
                        <td>{guardedLive.session_handoff.channel_restore_count}</td>
                      </tr>
                      <tr>
                        <th>Last channel restore</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.channel_last_restored_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Channel continuation</th>
                        <td>{guardedLive.session_handoff.channel_continuation_state}</td>
                      </tr>
                      <tr>
                        <th>Continuation count</th>
                        <td>{guardedLive.session_handoff.channel_continuation_count}</td>
                      </tr>
                      <tr>
                        <th>Last continued at</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.channel_last_continued_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Best bid</th>
                        <td>
                          {guardedLive.session_handoff.order_book_best_bid_price != null
                            ? `${guardedLive.session_handoff.order_book_best_bid_price.toFixed(8)}`
                              + ` @ ${guardedLive.session_handoff.order_book_best_bid_quantity?.toFixed(8) ?? "n/a"}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Best ask</th>
                        <td>
                          {guardedLive.session_handoff.order_book_best_ask_price != null
                            ? `${guardedLive.session_handoff.order_book_best_ask_price.toFixed(8)}`
                              + ` @ ${guardedLive.session_handoff.order_book_best_ask_quantity?.toFixed(8) ?? "n/a"}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Last market event</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_market_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last aggregate trade</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_aggregate_trade_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last mini ticker</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_mini_ticker_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last depth update</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_depth_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last kline update</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_kline_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last account event</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_account_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last balance event</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_balance_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last order-list event</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_order_list_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last trade tick</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_trade_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Last book ticker</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.last_book_ticker_event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Venue session</th>
                        <td>{guardedLive.session_handoff.venue_session_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Cursor</th>
                        <td>{guardedLive.session_handoff.cursor ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Active orders</th>
                        <td>{guardedLive.session_handoff.active_order_count}</td>
                      </tr>
                      <tr>
                        <th>Owner run</th>
                        <td>{guardedLive.session_handoff.owner_run_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner session</th>
                        <td>{guardedLive.session_handoff.owner_session_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Issues</th>
                        <td>{guardedLive.session_handoff.issues.length ? guardedLive.session_handoff.issues.join(", ") : "none"}</td>
                      </tr>
                    </tbody>
                  </table>
                  <h3>Recovered venue order book</h3>
                  {guardedLive.session_handoff.order_book_bids.length
                    || guardedLive.session_handoff.order_book_asks.length ? (
                      <div className="status-grid-two-column">
                        <section>
                          <h4>Recovered bids</h4>
                          <table className="data-table">
                            <thead>
                              <tr>
                                <th>Price</th>
                                <th>Quantity</th>
                              </tr>
                            </thead>
                            <tbody>
                              {guardedLive.session_handoff.order_book_bids.slice(0, 5).map((level) => (
                                <tr key={`handoff-bid-${level.price}`}>
                                  <td>{level.price.toFixed(8)}</td>
                                  <td>{level.quantity.toFixed(8)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </section>
                        <section>
                          <h4>Recovered asks</h4>
                          <table className="data-table">
                            <thead>
                              <tr>
                                <th>Price</th>
                                <th>Quantity</th>
                              </tr>
                            </thead>
                            <tbody>
                              {guardedLive.session_handoff.order_book_asks.slice(0, 5).map((level) => (
                                <tr key={`handoff-ask-${level.price}`}>
                                  <td>{level.price.toFixed(8)}</td>
                                  <td>{level.quantity.toFixed(8)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </section>
                      </div>
                    ) : (
                      <p className="empty-state">No recovered venue order-book levels recorded.</p>
                    )}
                  <h3>Recovered market channels</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>Trade tick</th>
                        <td>
                          {guardedLive.session_handoff.trade_snapshot
                            ? `${formatFixedNumber(guardedLive.session_handoff.trade_snapshot.price)} @ ${formatFixedNumber(guardedLive.session_handoff.trade_snapshot.quantity)}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Aggregate trade</th>
                        <td>
                          {guardedLive.session_handoff.aggregate_trade_snapshot
                            ? `${formatFixedNumber(guardedLive.session_handoff.aggregate_trade_snapshot.price)} @ ${formatFixedNumber(guardedLive.session_handoff.aggregate_trade_snapshot.quantity)}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Book ticker</th>
                        <td>
                          {guardedLive.session_handoff.book_ticker_snapshot
                            ? `${formatFixedNumber(guardedLive.session_handoff.book_ticker_snapshot.bid_price)} @ ${formatFixedNumber(guardedLive.session_handoff.book_ticker_snapshot.bid_quantity)} / ${formatFixedNumber(guardedLive.session_handoff.book_ticker_snapshot.ask_price)} @ ${formatFixedNumber(guardedLive.session_handoff.book_ticker_snapshot.ask_quantity)}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Mini ticker</th>
                        <td>
                          {guardedLive.session_handoff.mini_ticker_snapshot
                            ? `open ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.open_price)}, close ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.close_price)}, high ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.high_price)}, low ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.low_price)}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Mini ticker volume</th>
                        <td>
                          {guardedLive.session_handoff.mini_ticker_snapshot
                            ? `base ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.base_volume)}, quote ${formatFixedNumber(guardedLive.session_handoff.mini_ticker_snapshot.quote_volume)}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Kline snapshot</th>
                        <td>
                          {guardedLive.session_handoff.kline_snapshot
                            ? `${guardedLive.session_handoff.kline_snapshot.timeframe ?? "n/a"} | o ${formatFixedNumber(guardedLive.session_handoff.kline_snapshot.open_price)}, h ${formatFixedNumber(guardedLive.session_handoff.kline_snapshot.high_price)}, l ${formatFixedNumber(guardedLive.session_handoff.kline_snapshot.low_price)}, c ${formatFixedNumber(guardedLive.session_handoff.kline_snapshot.close_price)}, v ${formatFixedNumber(guardedLive.session_handoff.kline_snapshot.volume)}, closed ${guardedLive.session_handoff.kline_snapshot.closed ? "yes" : "no"}`
                            : "n/a"}
                        </td>
                      </tr>
                      <tr>
                        <th>Trade snapshot time</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.trade_snapshot?.event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Aggregate trade time</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.aggregate_trade_snapshot?.event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Book ticker time</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.book_ticker_snapshot?.event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Mini ticker time</th>
                        <td>{formatTimestamp(guardedLive.session_handoff.mini_ticker_snapshot?.event_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Kline open / close</th>
                        <td>
                          {guardedLive.session_handoff.kline_snapshot
                            ? `${formatTimestamp(guardedLive.session_handoff.kline_snapshot.open_at ?? null)} -> ${formatTimestamp(guardedLive.session_handoff.kline_snapshot.close_at ?? null)}`
                            : "n/a"}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <h3>Durable order book</h3>
                  <table className="data-table">
                    <tbody>
                      <tr>
                        <th>Sync state</th>
                        <td>{guardedLive.order_book.state}</td>
                      </tr>
                      <tr>
                        <th>Synced at</th>
                        <td>{formatTimestamp(guardedLive.order_book.synced_at ?? null)}</td>
                      </tr>
                      <tr>
                        <th>Owner run</th>
                        <td>{guardedLive.order_book.owner_run_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Owner session</th>
                        <td>{guardedLive.order_book.owner_session_id ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Symbol</th>
                        <td>{guardedLive.order_book.symbol ?? "n/a"}</td>
                      </tr>
                      <tr>
                        <th>Issues</th>
                        <td>{guardedLive.order_book.issues.length ? guardedLive.order_book.issues.join(", ") : "none"}</td>
                      </tr>
                    </tbody>
                  </table>
                  {guardedLive.order_book.open_orders.length ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Order</th>
                          <th>Symbol</th>
                          <th>Side</th>
                          <th>Amount</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guardedLive.order_book.open_orders.map((order) => (
                          <tr key={`durable-${order.order_id}`}>
                            <td>{order.order_id}</td>
                            <td>{order.symbol}</td>
                            <td>{order.side}</td>
                            <td>{order.amount.toFixed(8)}</td>
                            <td>{order.status}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-state">No durable guarded-live open orders recorded.</p>
                  )}
                  <ControlRoomLiveIncidentHistory model={model} />
                  </div>
                </PanelDisclosure>
              </div>
            </div>
          ) : (
            <p>No guarded-live status loaded.</p>
          )}
              </section>

  );
}
