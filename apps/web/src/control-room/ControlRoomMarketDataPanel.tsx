// @ts-nocheck

export function ControlRoomMarketDataPanel({ model }: { model: any }) {
  const {
    marketStatus,
    failureSummary,
    formatTimestamp,
    backfillSummary,
    formatCompletion,
    activeMarketInstrument,
    focusedMarketWorkflowSummary,
    formatWorkflowToken,
    PanelDisclosure,
    buildMarketDataInstrumentFocusKey,
    activeMarketInstrumentKey,
    handleMarketInstrumentFocus,
    isMarketDataInstrumentAtRisk,
    BackfillCountStatus,
    instrumentGapRowKey,
    buildGapWindowKey,
    expandedGapRows = {},
    BackfillQualityStatus,
    activeGapWindowPickerRowKey,
    setExpandedGapWindowSelections,
    resolveGapWindowSelectionList,
    isSameGapWindowSelectionList,
    setActiveGapWindowPickerRowKey,
    setExpandedGapRows,
    toggleExpandedGapRow,
    expandedGapWindowSelections = {},
    SyncCheckpointStatus,
    SyncFailureStatus,
  } = model;

  return (

              <section className="panel panel-wide">
          <p className="kicker">Data plane</p>
          <h2>Market data status</h2>
          {marketStatus ? (
            <div className="status-grid">
              <div className="metric-tile">
                <span>Provider</span>
                <strong>{marketStatus.provider}</strong>
              </div>
              <div className="metric-tile">
                <span>Venue</span>
                <strong>{marketStatus.venue}</strong>
              </div>
              <div className="metric-tile">
                <span>Tracked symbols</span>
                <strong>{marketStatus.instruments.length}</strong>
              </div>
              {failureSummary ? (
                <>
                  <div className="metric-tile">
                    <span>Failures 24h</span>
                    <strong>{failureSummary.failureCount24h}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Affected instruments</span>
                    <strong>{failureSummary.affectedInstrumentCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Latest failure</span>
                    <strong>{formatTimestamp(failureSummary.lastFailureAt)}</strong>
                  </div>
                </>
              ) : null}
              {backfillSummary ? (
                <>
                  <div className="metric-tile">
                    <span>Backfill count</span>
                    <strong>{formatCompletion(backfillSummary.completionRatio)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Count complete</span>
                    <strong>
                      {backfillSummary.completeCount} / {backfillSummary.instrumentCount}
                    </strong>
                  </div>
                  <div className="metric-tile">
                    <span>Contiguous quality</span>
                    <strong>{formatCompletion(backfillSummary.contiguousQualityRatio)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Gap-free spans</span>
                    <strong>
                      {backfillSummary.contiguousInstrumentCount > 0
                        ? `${backfillSummary.contiguousCompleteCount} / ${backfillSummary.contiguousInstrumentCount}`
                        : "n/a"}
                    </strong>
                  </div>
                </>
              ) : null}
              {activeMarketInstrument && focusedMarketWorkflowSummary ? (
                <>
                  <div className="metric-tile">
                    <span>Triage focus</span>
                    <strong>{focusedMarketWorkflowSummary.focusLabel}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Focused sync</span>
                    <strong>{activeMarketInstrument.sync_status}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Lineage claim</span>
                    <strong>{formatWorkflowToken(focusedMarketWorkflowSummary.latestLineage?.validation_claim)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>Latest ingestion</span>
                    <strong>{formatWorkflowToken(focusedMarketWorkflowSummary.latestJob?.status)}</strong>
                  </div>
                </>
              ) : null}
              <PanelDisclosure
                defaultOpen={false}
                summary={`${
                  marketStatus.instruments.length
                } instruments across ${marketStatus.provider} / ${marketStatus.venue}.${activeMarketInstrument ? ` Focused triage: ${activeMarketInstrument.instrument_id} ${activeMarketInstrument.timeframe}.` : ""}`}
                title="Instrument sync ledger"
              >
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Instrument</th>
                      <th>Timeframe</th>
                      <th>Sync</th>
                      <th>Candles</th>
                      <th>Target</th>
                      <th>Count</th>
                      <th>Quality</th>
                      <th>Lag</th>
                      <th>Latest</th>
                      <th>Checkpoint</th>
                      <th>Failures</th>
                      <th>Issues</th>
                    </tr>
                  </thead>
                  <tbody>
                    {marketStatus.instruments.map((instrument) => {
                      const isFocusedInstrument =
                        buildMarketDataInstrumentFocusKey(instrument) === activeMarketInstrumentKey;
                      return (
                      <tr
                        className={isFocusedInstrument ? "market-data-instrument-row is-active" : "market-data-instrument-row"}
                        key={instrument.instrument_id}
                      >
                        <td>
                          <button
                            className={`market-data-instrument-button ${isFocusedInstrument ? "is-active" : ""}`.trim()}
                            onClick={() => {
                              void handleMarketInstrumentFocus(instrument);
                            }}
                            type="button"
                          >
                            <strong>{instrument.instrument_id}</strong>
                            <span>{isMarketDataInstrumentAtRisk(instrument) ? "review" : "clear"}</span>
                          </button>
                        </td>
                        <td>{instrument.timeframe}</td>
                        <td>{instrument.sync_status}</td>
                        <td>{instrument.candle_count}</td>
                        <td>{instrument.backfill_target_candles ?? "n/a"}</td>
                        <td>
                          <BackfillCountStatus instrument={instrument} />
                        </td>
                        <td>
                          {(() => {
                            const rowKey = instrumentGapRowKey(instrument);
                            const gapWindowKeys = instrument.backfill_gap_windows.map((gapWindow) =>
                              buildGapWindowKey(gapWindow),
                            );
                            const expanded = Boolean(expandedGapRows[rowKey]);
                            return (
                              <BackfillQualityStatus
                                expanded={expanded}
                                gapWindowPickerOpen={activeGapWindowPickerRowKey === rowKey}
                                instrument={instrument}
                                onChangeGapWindowSelections={(nextSelectedGapWindowKeys) => {
                                  setExpandedGapWindowSelections((current) => {
                                    const nextSelectedWindows = gapWindowKeys.filter((candidate) =>
                                      nextSelectedGapWindowKeys.includes(candidate),
                                    );
                                    if (!nextSelectedWindows.length) {
                                      return current;
                                    }
                                    const currentSelectedWindows = resolveGapWindowSelectionList(
                                      gapWindowKeys,
                                      current[rowKey] ?? null,
                                    );
                                    if (isSameGapWindowSelectionList(currentSelectedWindows, nextSelectedWindows)) {
                                      return current;
                                    }
                                    return {
                                      ...current,
                                      [rowKey]: nextSelectedWindows,
                                    };
                                  });
                                }}
                                onSelectAllGapWindows={() => {
                                  if (!gapWindowKeys.length) {
                                    return;
                                  }
                                  setExpandedGapWindowSelections((current) => ({
                                    ...current,
                                    [rowKey]: gapWindowKeys,
                                  }));
                                }}
                                onToggle={() => {
                                  const nextExpanded = !expanded;
                                  if (!nextExpanded && activeGapWindowPickerRowKey === rowKey) {
                                    setActiveGapWindowPickerRowKey(null);
                                  }
                                  setExpandedGapRows((current) => toggleExpandedGapRow(current, rowKey));
                                  setExpandedGapWindowSelections((current) => {
                                    if (current[rowKey]?.length) {
                                      return current;
                                    }
                                    return gapWindowKeys.length
                                      ? { ...current, [rowKey]: gapWindowKeys }
                                      : current;
                                  });
                                }}
                                onToggleGapWindowPicker={() => {
                                  if (!gapWindowKeys.length) {
                                    return;
                                  }
                                  if (!expanded) {
                                    setExpandedGapRows((current) =>
                                      current[rowKey] ? current : { ...current, [rowKey]: true },
                                    );
                                  }
                                  setExpandedGapWindowSelections((current) => {
                                    if (current[rowKey]?.length) {
                                      return current;
                                    }
                                    return { ...current, [rowKey]: gapWindowKeys };
                                  });
                                  setActiveGapWindowPickerRowKey((current) =>
                                    current === rowKey ? null : rowKey,
                                  );
                                }}
                                selectedGapWindowKeys={expandedGapWindowSelections[rowKey] ?? null}
                              />
                            );
                          })()}
                        </td>
                        <td>{instrument.lag_seconds ?? "n/a"}</td>
                        <td>{instrument.last_timestamp ?? "n/a"}</td>
                        <td>
                          <SyncCheckpointStatus instrument={instrument} />
                        </td>
                        <td>
                          <SyncFailureStatus instrument={instrument} />
                        </td>
                        <td>{instrument.issues.length ? instrument.issues.join(", ") : "ok"}</td>
                      </tr>
                    );})}
                  </tbody>
                </table>
              </PanelDisclosure>
            </div>
          ) : (
            <p>No data status loaded.</p>
          )}
              </section>

  );
}
