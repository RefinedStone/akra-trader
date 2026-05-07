// @ts-nocheck
import type { ReactNode } from "react";

type LiveControlPanelModel = {
  PanelDisclosure?: any;
  activeGuardedLiveAlertIds?: string[];
  acknowledgeGuardedLiveIncident?: (incidentId: string) => Promise<void>;
  engageGuardedLiveKillSwitch?: () => Promise<void>;
  escalateGuardedLiveIncident?: (incidentId: string) => Promise<void>;
  formatFixedNumber?: (value: number | null | undefined) => string;
  formatTimestamp?: (value: string | null | undefined) => string;
  guardedLive?: any;
  guardedLiveReason?: string;
  guardedLiveSummary?: any;
  recoverGuardedLiveRuntime?: () => Promise<void>;
  releaseGuardedLiveKillSwitch?: () => Promise<void>;
  remediateGuardedLiveIncident?: (incidentId: string) => Promise<void>;
  resumeGuardedLiveRun?: () => Promise<void>;
  runGuardedLiveReconciliation?: () => Promise<void>;
  setGuardedLiveReason?: (value: string) => void;
};

function DefaultDisclosure({
  children,
  summary,
  title,
}: {
  children: ReactNode;
  summary: ReactNode;
  title: string;
}) {
  return (
    <section className="runtime-operator-section">
      <div className="run-lineage-head">
        <span>{title}</span>
        <strong>{summary}</strong>
      </div>
      {children}
    </section>
  );
}

function fallbackTimestamp(value: string | null | undefined) {
  return value ?? "n/a";
}

function fallbackNumber(value: number | null | undefined) {
  return value === null || value === undefined ? "n/a" : String(value);
}

export function ControlRoomLiveControlPanel({ model }: { model: LiveControlPanelModel }) {
  const {
    PanelDisclosure = DefaultDisclosure,
    activeGuardedLiveAlertIds = [],
    acknowledgeGuardedLiveIncident,
    engageGuardedLiveKillSwitch,
    escalateGuardedLiveIncident,
    formatFixedNumber = fallbackNumber,
    formatTimestamp = fallbackTimestamp,
    guardedLive,
    guardedLiveReason = "",
    guardedLiveSummary,
    recoverGuardedLiveRuntime,
    releaseGuardedLiveKillSwitch,
    remediateGuardedLiveIncident,
    resumeGuardedLiveRun,
    runGuardedLiveReconciliation,
    setGuardedLiveReason,
  } = model;

  if (!guardedLive) {
    return (
      <section className="panel panel-wide">
        <p className="kicker">실전 보호</p>
        <h2>중지 스위치와 거래소 확인</h2>
        <p>실전 보호 상태를 불러오지 못했습니다.</p>
      </section>
    );
  }

  const blockers = guardedLive.blockers ?? [];
  const findings = guardedLive.reconciliation?.findings ?? [];
  const openOrders = guardedLive.order_book?.open_orders ?? [];
  const incidents = guardedLive.incident_events ?? [];
  const exposures = guardedLive.reconciliation?.venue_snapshot?.exposures ?? [];

  return (
    <section className="panel panel-wide">
      <p className="kicker">실전 보호</p>
      <h2>중지 스위치와 거래소 확인</h2>

      <div className="status-grid">
        <div className="metric-tile">
          <span>실전 가능 상태</span>
          <strong>{guardedLive.candidacy_status}</strong>
        </div>
        <div className="metric-tile">
          <span>중지 스위치</span>
          <strong>{guardedLive.kill_switch?.state ?? "n/a"}</strong>
        </div>
        <div className="metric-tile">
          <span>운영 알림</span>
          <strong>{guardedLive.active_runtime_alert_count ?? activeGuardedLiveAlertIds.length}</strong>
        </div>
        <div className="metric-tile">
          <span>거래소 확인</span>
          <strong>{guardedLive.reconciliation?.venue_snapshot?.verification_state ?? "n/a"}</strong>
        </div>
        <div className="metric-tile">
          <span>최근 확인</span>
          <strong>{formatTimestamp(guardedLiveSummary?.latestReconciliationAt ?? null)}</strong>
        </div>
        <div className="metric-tile">
          <span>차단 사유</span>
          <strong>{guardedLiveSummary?.blockerCount ?? blockers.length}</strong>
        </div>
        <div className="metric-tile">
          <span>실전 실행</span>
          <strong>{guardedLive.ownership?.state ?? "n/a"}</strong>
        </div>
        <div className="metric-tile">
          <span>미체결 주문</span>
          <strong>{openOrders.length}</strong>
        </div>
      </div>

      <div className="control-action-row">
        <label className="control-action-field">
          <span>처리 사유</span>
          <input
            onChange={(event) => setGuardedLiveReason?.(event.target.value)}
            placeholder="operator_safety_drill"
            type="text"
            value={guardedLiveReason}
          />
        </label>
        <button className="ghost-button" onClick={() => void runGuardedLiveReconciliation?.()} type="button">
          거래소 확인
        </button>
        <button className="ghost-button" onClick={() => void recoverGuardedLiveRuntime?.()} type="button">
          실행 상태 복구
        </button>
        <button className="ghost-button" onClick={() => void resumeGuardedLiveRun?.()} type="button">
          실전 실행 재개
        </button>
        <button className="ghost-button" onClick={() => void engageGuardedLiveKillSwitch?.()} type="button">
          중지 스위치 켜기
        </button>
        <button className="ghost-button" onClick={() => void releaseGuardedLiveKillSwitch?.()} type="button">
          중지 스위치 해제
        </button>
      </div>

      <div className="panel-disclosure-grid">
        <PanelDisclosure
          defaultOpen={true}
          summary={`중지 스위치 ${guardedLive.kill_switch?.state ?? "n/a"} · 차단 ${blockers.length}개 · 실행 ${guardedLive.ownership?.state ?? "n/a"}`}
          title="실전 보호 장치"
        >
          <div className="panel-disclosure-stack">
            <table className="data-table">
              <tbody>
                <tr>
                  <th>중지 스위치</th>
                  <td>{guardedLive.kill_switch?.state ?? "n/a"}</td>
                </tr>
                <tr>
                  <th>사유</th>
                  <td>{guardedLive.kill_switch?.reason ?? "n/a"}</td>
                </tr>
                <tr>
                  <th>실행 ID</th>
                  <td>{guardedLive.ownership?.owner_run_id ?? "n/a"}</td>
                </tr>
                <tr>
                  <th>세션</th>
                  <td>{guardedLive.ownership?.owner_session_id ?? "n/a"}</td>
                </tr>
                <tr>
                  <th>종목</th>
                  <td>{guardedLive.ownership?.symbol ?? "n/a"}</td>
                </tr>
                <tr>
                  <th>최근 주문 확인</th>
                  <td>{formatTimestamp(guardedLive.ownership?.last_order_sync_at ?? null)}</td>
                </tr>
                <tr>
                  <th>세션 복구</th>
                  <td>{guardedLive.session_restore?.state ?? "n/a"}</td>
                </tr>
                <tr>
                  <th>세션 인계</th>
                  <td>{guardedLive.session_handoff?.state ?? "n/a"}</td>
                </tr>
              </tbody>
            </table>

            <h3>차단 사유</h3>
            {blockers.length ? (
              <table className="data-table">
                <tbody>
                  {blockers.map((blocker: string) => (
                    <tr key={blocker}>
                      <td>{blocker}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-state">현재 실전 차단 사유가 없습니다.</p>
            )}
          </div>
        </PanelDisclosure>

        <PanelDisclosure
          defaultOpen={false}
          summary={`확인 결과 ${findings.length}개 · 미체결 주문 ${openOrders.length}개 · 사고 ${incidents.length}개`}
          title="거래소 상태와 사고"
        >
          <div className="panel-disclosure-stack panel-disclosure-scroll">
            <h3>거래소 확인 결과</h3>
            {findings.length ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>심각도</th>
                    <th>항목</th>
                    <th>내용</th>
                  </tr>
                </thead>
                <tbody>
                  {findings.map((finding: any) => (
                    <tr key={`${finding.kind}-${finding.summary}`}>
                      <td>{finding.severity}</td>
                      <td>{finding.kind}</td>
                      <td>
                        <strong>{finding.summary}</strong>
                        {finding.detail ? <p className="run-lineage-symbol-copy">{finding.detail}</p> : null}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-state">{guardedLive.reconciliation?.summary ?? "거래소 확인 결과가 없습니다."}</p>
            )}

            <h3>미체결 주문</h3>
            {openOrders.length ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>주문</th>
                    <th>방향</th>
                    <th>수량</th>
                    <th>가격</th>
                    <th>상태</th>
                  </tr>
                </thead>
                <tbody>
                  {openOrders.slice(0, 10).map((order: any) => (
                    <tr key={order.order_id}>
                      <td>{order.order_id}</td>
                      <td>{order.side}</td>
                      <td>{formatFixedNumber(order.quantity)}</td>
                      <td>{formatFixedNumber(order.price)}</td>
                      <td>{order.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-state">미체결 주문이 없습니다.</p>
            )}

            <h3>보유 현황</h3>
            {exposures.length ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>자산</th>
                    <th>사용 가능</th>
                    <th>묶임</th>
                    <th>합계</th>
                  </tr>
                </thead>
                <tbody>
                  {exposures.map((exposure: any) => (
                    <tr key={exposure.asset}>
                      <td>{exposure.asset}</td>
                      <td>{formatFixedNumber(exposure.free)}</td>
                      <td>{formatFixedNumber(exposure.locked)}</td>
                      <td>{formatFixedNumber(exposure.total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-state">거래소 보유 현황이 없습니다.</p>
            )}

            <h3>사고</h3>
            {incidents.length ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>상태</th>
                    <th>심각도</th>
                    <th>내용</th>
                    <th>갱신</th>
                    <th>처리</th>
                  </tr>
                </thead>
                <tbody>
                  {incidents.slice(0, 8).map((incident: any) => (
                    <tr key={incident.incident_id}>
                      <td>{incident.status}</td>
                      <td>{incident.severity}</td>
                      <td>{incident.summary}</td>
                      <td>{formatTimestamp(incident.updated_at ?? null)}</td>
                      <td>
                        <div className="control-action-row">
                          <button
                            className="ghost-button"
                            onClick={() => void acknowledgeGuardedLiveIncident?.(incident.incident_id)}
                            type="button"
                          >
                            확인
                          </button>
                          <button
                            className="ghost-button"
                            onClick={() => void remediateGuardedLiveIncident?.(incident.incident_id)}
                            type="button"
                          >
                            조치
                          </button>
                          <button
                            className="ghost-button"
                            onClick={() => void escalateGuardedLiveIncident?.(incident.incident_id)}
                            type="button"
                          >
                            전달
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-state">현재 실전 사고가 없습니다.</p>
            )}
          </div>
        </PanelDisclosure>
      </div>
    </section>
  );
}
