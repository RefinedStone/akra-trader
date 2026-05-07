// @ts-nocheck

function formatMarketStatusToken(value: string | null | undefined) {
  if (!value) {
    return "-";
  }
  const labels: Record<string, string> = {
    backfilling: "수집 중",
    failed: "오류",
    invalid: "검증 실패",
    ok: "정상",
    pending: "대기",
    stale: "지연",
    synced: "동기화됨",
    valid: "검증 완료",
    warning: "확인 필요",
  };
  return labels[value] ?? value.replaceAll("_", " ");
}

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
          <p className="kicker">시장 데이터</p>
          <h2>데이터 상태</h2>
          {marketStatus ? (
            <div className="status-grid">
              <div className="metric-tile">
                <span>데이터 제공처</span>
                <strong>{marketStatus.provider}</strong>
              </div>
              <div className="metric-tile">
                <span>거래소</span>
                <strong>{marketStatus.venue}</strong>
              </div>
              <div className="metric-tile">
                <span>관리 종목</span>
                <strong>{marketStatus.instruments.length}</strong>
              </div>
              {failureSummary ? (
                <>
                  <div className="metric-tile">
                    <span>24시간 오류</span>
                    <strong>{failureSummary.failureCount24h}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>영향 종목</span>
                    <strong>{failureSummary.affectedInstrumentCount}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>최근 오류</span>
                    <strong>{formatTimestamp(failureSummary.lastFailureAt)}</strong>
                  </div>
                </>
              ) : null}
              {backfillSummary ? (
                <>
                  <div className="metric-tile">
                    <span>수집 진행</span>
                    <strong>{formatCompletion(backfillSummary.completionRatio)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>완료 종목</span>
                    <strong>
                      {backfillSummary.completeCount} / {backfillSummary.instrumentCount}
                    </strong>
                  </div>
                  <div className="metric-tile">
                    <span>데이터 품질</span>
                    <strong>{formatCompletion(backfillSummary.contiguousQualityRatio)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>빈 구간 없음</span>
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
                    <span>확인 대상</span>
                    <strong>{focusedMarketWorkflowSummary.focusLabel}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>동기화 상태</span>
                    <strong>{formatMarketStatusToken(activeMarketInstrument.sync_status)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>검증 상태</span>
                    <strong>{formatWorkflowToken(focusedMarketWorkflowSummary.latestLineage?.validation_claim)}</strong>
                  </div>
                  <div className="metric-tile">
                    <span>최근 수집</span>
                    <strong>{formatWorkflowToken(focusedMarketWorkflowSummary.latestJob?.status)}</strong>
                  </div>
                </>
              ) : null}
              <PanelDisclosure
                defaultOpen={false}
                summary={`${
                  marketStatus.instruments.length
                }개 종목을 ${marketStatus.venue}에서 관리합니다.${activeMarketInstrument ? ` 확인 중: ${activeMarketInstrument.instrument_id} ${activeMarketInstrument.timeframe}.` : ""}`}
                title="종목별 수집 상태"
              >
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>종목</th>
                      <th>주기</th>
                      <th>상태</th>
                      <th>캔들</th>
                      <th>목표</th>
                      <th>수집</th>
                      <th>품질</th>
                      <th>지연</th>
                      <th>최근</th>
                      <th>저장 지점</th>
                      <th>오류</th>
                      <th>메모</th>
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
                            <span>{isMarketDataInstrumentAtRisk(instrument) ? "확인 필요" : "정상"}</span>
                          </button>
                        </td>
                        <td>{instrument.timeframe}</td>
                        <td>{formatMarketStatusToken(instrument.sync_status)}</td>
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
                        <td>{instrument.issues.length ? instrument.issues.map(formatMarketStatusToken).join(", ") : "정상"}</td>
                      </tr>
                    );})}
                  </tbody>
                </table>
              </PanelDisclosure>
            </div>
          ) : (
            <p>데이터 상태를 불러오지 못했습니다.</p>
          )}
              </section>

  );
}
