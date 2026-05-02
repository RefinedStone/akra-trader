import type {
  RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode,
  RunSurfaceCollectionQueryBuilderReplayLinkShareMode,
} from "./model";
import type {
  RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy,
  RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
} from "../../controlRoomDefinitions";
import type { QueryBuilderReplayGovernanceSectionProps } from "./QueryBuilderReplayGovernanceSection.types";

export type { QueryBuilderReplayGovernanceSectionProps } from "./QueryBuilderReplayGovernanceSection.types";

export function QueryBuilderReplayGovernanceSection(props: QueryBuilderReplayGovernanceSectionProps) {
  const {
    governance: { currentReplayIntentGovernancePayloadValue, currentReplayIntentGovernanceSnapshot, predicateRefReplayApplyHistoryTabIdentity,
    redactedRunSurfaceCollectionQueryBuilderReplayIntentCompactValue, replayIntentGovernanceAuditTrail, replayIntentGovernanceConflicts, replayIntentGovernancePayloadDraft,
    replayIntentGovernanceStatus, replayIntentGovernanceSyncMode, replayIntentRedactionPolicy, replayIntentRetentionPolicy,
    replayIntentShareMode, replayIntentShareStatus, visibleReplayIntentLinkAliases, visibleReplayIntentLinkAuditTrail,
    }, serverAudit: { replayIntentServerAuditActionFilter, replayIntentServerAuditAliasFilter,
    replayIntentServerAuditExportJobHistory, replayIntentServerAuditExportJobLoading, replayIntentServerAuditExportJobStatus, replayIntentServerAuditExportJobTotal,
    replayIntentServerAuditExportJobs, replayIntentServerAuditIncludeManual, replayIntentServerAuditItems, replayIntentServerAuditLimit,
    replayIntentServerAuditLoading, replayIntentServerAuditReadToken, replayIntentServerAuditRecordedBefore, replayIntentServerAuditRetentionFilter,
    replayIntentServerAuditSearch, replayIntentServerAuditSourceTabFilter, replayIntentServerAuditStatus, replayIntentServerAuditTemplateFilter,
    replayIntentServerAuditTotal, replayIntentServerAuditWriteToken, }, callbacks: {
    appendReplayIntentGovernanceAuditEntry, applyReplayIntentGovernanceSnapshot, applyRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload, copyRunSurfaceCollectionQueryBuilderReplayIntentLink,
    copyRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload, createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord, dismissReplayIntentGovernanceConflict, downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord,
    exportRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords, loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory, loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs, loadRunSurfaceCollectionQueryBuilderServerReplayLinkAudits,
    pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecords, pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords, revokeRunSurfaceCollectionQueryBuilderReplayIntentAlias, setReplayIntentGovernanceAuditTrail,
    setReplayIntentGovernancePayloadDraft, setReplayIntentGovernanceStatus, setReplayIntentGovernanceSyncMode, setReplayIntentLinkAliases,
    setReplayIntentLinkAuditTrail, setReplayIntentRedactionPolicy, setReplayIntentRetentionPolicy, setReplayIntentServerAuditActionFilter,
    setReplayIntentServerAuditAliasFilter, setReplayIntentServerAuditIncludeManual, setReplayIntentServerAuditLimit, setReplayIntentServerAuditReadToken,
    setReplayIntentServerAuditRecordedBefore, setReplayIntentServerAuditRetentionFilter, setReplayIntentServerAuditSearch, setReplayIntentServerAuditSourceTabFilter,
    setReplayIntentServerAuditTemplateFilter, setReplayIntentServerAuditWriteToken, setReplayIntentShareMode, setReplayIntentShareStatus,
    shareRunSurfaceCollectionQueryBuilderReplayIntentLink, }, helpers: { buildRunSurfaceCollectionQueryBuilderReplayLinkAliasToken,
    formatRelativeTimestampLabel, formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue, getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys, },
  } = props;

  return (
    <>
                        <div className="run-surface-query-builder-actions">
                          <label className="run-surface-query-builder-control">
                            <span>Share mode</span>
                            <select
                              value={replayIntentShareMode}
                              onChange={(event) =>
                                setReplayIntentShareMode(
                                  event.target.value as RunSurfaceCollectionQueryBuilderReplayLinkShareMode,
                                )}
                            >
                              <option value="portable">Portable deep link</option>
                              <option value="indirect">Local alias link</option>
                            </select>
                          </label>
                          <label className="run-surface-query-builder-control">
                            <span>Redaction</span>
                            <select
                              value={replayIntentRedactionPolicy}
                              onChange={(event) =>
                                setReplayIntentRedactionPolicy(
                                  event.target.value as RunSurfaceCollectionQueryBuilderReplayLinkRedactionPolicy,
                                )}
                            >
                              <option value="full">Full replay intent</option>
                              <option value="omit_preview">Remove preview focus</option>
                              <option value="summary_only">Summary only</option>
                            </select>
                          </label>
                          <label className="run-surface-query-builder-control">
                            <span>Retention</span>
                            <select
                              value={replayIntentRetentionPolicy}
                              onChange={(event) =>
                                setReplayIntentRetentionPolicy(
                                  event.target.value as RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
                                )}
                            >
                              <option value="1d">1 day</option>
                              <option value="7d">7 days</option>
                              <option value="30d">30 days</option>
                              <option value="manual">Keep until cleared</option>
                            </select>
                          </label>
                          <label className="run-surface-query-builder-control">
                            <span>Sync mode</span>
                            <select
                              value={replayIntentGovernanceSyncMode}
                              onChange={(event) =>
                                setReplayIntentGovernanceSyncMode(
                                  event.target.value as RunSurfaceCollectionQueryBuilderReplayLinkGovernanceSyncMode,
                                )}
                            >
                              <option value="live">Live sync</option>
                              <option value="review">Review remote changes</option>
                              <option value="opt_out">Ignore remote changes</option>
                            </select>
                          </label>
                          <button
                            className="ghost-button"
                            onClick={() => {
                              setReplayIntentLinkAliases([]);
                              setReplayIntentLinkAuditTrail([]);
                              setReplayIntentGovernanceAuditTrail([]);
                              setReplayIntentGovernanceStatus({
                                message: "Cleared replay short links and governance history for this browser.",
                                tone: "muted",
                              });
                            }}
                            type="button"
                          >
                            Clear retained records
                          </button>
                          <button
                            className="ghost-button"
                            onClick={() => {
                              void copyRunSurfaceCollectionQueryBuilderReplayIntentLink();
                            }}
                            type="button"
                          >
                            Copy replay link
                          </button>
                          {typeof navigator !== "undefined" && typeof navigator.share === "function" ? (
                            <button
                              className="ghost-button"
                              onClick={() => {
                                void shareRunSurfaceCollectionQueryBuilderReplayIntentLink();
                              }}
                              type="button"
                            >
                              Share replay link
                            </button>
                          ) : null}
                        </div>
                        <p className="run-note">
                          {replayIntentShareMode === "indirect"
                            ? "Indirect alias links prefer server-backed resolution and revocation, with local alias fallback if the server is unavailable."
                            : (
                                redactedRunSurfaceCollectionQueryBuilderReplayIntentCompactValue
                                  ? `Compact replay payload · ${redactedRunSurfaceCollectionQueryBuilderReplayIntentCompactValue.length} chars`
                                  : "Replay deep link is currently at default state."
                              )}
                        </p>
                        <p className="run-note">
                          {replayIntentRedactionPolicy === "full"
                            ? "Full links preserve filters, preview focus, and replay step."
                            : replayIntentRedactionPolicy === "omit_preview"
                              ? "Preview redaction keeps filters and replay step but drops preview trace/diff focus."
                              : "Summary redaction keeps high-level replay scope and filters while dropping step, edge, and preview focus."}
                        </p>
                        <p className="run-note">
                          {replayIntentGovernanceSyncMode === "live"
                            ? "Remote tab governance changes apply immediately in this tab."
                            : replayIntentGovernanceSyncMode === "review"
                              ? "Remote governance changes queue for review before this tab adopts them."
                              : "This tab keeps its own replay link governance and ignores remote tab updates."}
                        </p>
                        <p className="run-note">
                          {replayIntentRetentionPolicy === "manual"
                            ? "Indirect short links and governance records stay until you explicitly clear them."
                            : `Indirect short links, replay link audit, and governance audit older than ${formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue(
                              "retentionPolicy",
                              currentReplayIntentGovernanceSnapshot,
                            ).toLowerCase()} are pruned automatically.`}
                        </p>
                        <div className="run-surface-query-builder-trace-chip-list">
                          <span className="run-surface-query-builder-trace-chip is-active">
                            {`Current tab · ${predicateRefReplayApplyHistoryTabIdentity.label}`}
                          </span>
                          <span className="run-surface-query-builder-trace-chip">
                            {replayIntentGovernanceConflicts.length
                              ? `${replayIntentGovernanceConflicts.length} pending governance review${replayIntentGovernanceConflicts.length === 1 ? "" : "s"}`
                              : "No pending governance conflicts"}
                          </span>
                        </div>
                        {replayIntentShareStatus ? (
                          <p className={`run-note run-surface-query-builder-note is-${replayIntentShareStatus.tone}`}>
                            {replayIntentShareStatus.message}
                          </p>
                        ) : null}
                        {replayIntentGovernanceStatus ? (
                          <p className={`run-note run-surface-query-builder-note is-${replayIntentGovernanceStatus.tone}`}>
                            {replayIntentGovernanceStatus.message}
                          </p>
                        ) : null}
                        {visibleReplayIntentLinkAliases.length ? (
                          <div className="run-surface-query-builder-trace-panel is-nested">
                            <div className="run-surface-query-builder-card-head">
                              <strong>Replay alias registry</strong>
                              <span>{`${visibleReplayIntentLinkAliases.length} aliases`}</span>
                            </div>
                            <div className="run-surface-query-builder-trace-list">
                              {visibleReplayIntentLinkAliases.slice(0, 5).map((entry) => {
                                const aliasToken = buildRunSurfaceCollectionQueryBuilderReplayLinkAliasToken(
                                  entry.aliasId,
                                  entry.signature ?? "",
                                );
                                const isExpired = entry.expiresAt ? Date.parse(entry.expiresAt) <= Date.now() : false;
                                const isRevoked = Boolean(entry.revokedAt);
                                return (
                                  <div
                                    className={`run-surface-query-builder-trace-step is-${
                                      isRevoked ? "warning" : entry.resolutionSource === "server" ? "success" : "muted"
                                    }`}
                                    key={`replay-alias:${entry.aliasId}`}
                                  >
                                    <strong>
                                      {`${entry.resolutionSource === "server" ? "Server" : "Local"} alias · ${entry.templateLabel}`}
                                    </strong>
                                    <p>
                                      {`${entry.aliasId.slice(0, 8)} · ${entry.createdByTabLabel} · ${formatRelativeTimestampLabel(entry.createdAt)}`}
                                    </p>
                                    <div className="run-surface-query-builder-trace-chip-list">
                                      <span className={`run-surface-query-builder-trace-chip${
                                        entry.resolutionSource === "server" && !isRevoked ? " is-active" : ""
                                      }`}>
                                        {entry.resolutionSource}
                                      </span>
                                      <span className="run-surface-query-builder-trace-chip">
                                        {isRevoked ? "revoked" : isExpired ? "expired" : "active"}
                                      </span>
                                      <span className="run-surface-query-builder-trace-chip">
                                        {`${aliasToken.length} chars`}
                                      </span>
                                    </div>
                                    {entry.expiresAt ? (
                                      <p className="run-note">
                                        {`Expires ${formatRelativeTimestampLabel(entry.expiresAt)}`}
                                      </p>
                                    ) : null}
                                    {entry.revokedAt ? (
                                      <p className="run-note">
                                        {`Revoked ${formatRelativeTimestampLabel(entry.revokedAt)} by ${entry.revokedByTabLabel ?? "server"}.`}
                                      </p>
                                    ) : null}
                                    {entry.resolutionSource === "server" && !isRevoked ? (
                                      <div className="run-surface-query-builder-actions">
                                        <button
                                          className="ghost-button"
                                          onClick={() => {
                                            void revokeRunSurfaceCollectionQueryBuilderReplayIntentAlias(entry);
                                          }}
                                          type="button"
                                        >
                                          Revoke alias
                                        </button>
                                      </div>
                                    ) : null}
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        ) : null}
                        <div className="run-surface-query-builder-trace-panel is-nested">
                          <div className="run-surface-query-builder-card-head">
                            <strong>Server replay alias audit admin</strong>
                            <span>{replayIntentServerAuditTotal
                              ? `${replayIntentServerAuditTotal} loaded`
                              : "Scoped access"}</span>
                          </div>
                          <p className="run-note">
                            List and prune persisted server replay alias audits with separate read and write admin tokens.
                            If your server uses a single shared token, the write token field alone is enough.
                          </p>
                          {replayIntentServerAuditStatus ? (
                            <p className={`run-note run-surface-query-builder-note is-${replayIntentServerAuditStatus.tone}`}>
                              {replayIntentServerAuditStatus.message}
                            </p>
                          ) : null}
                          <div className="run-surface-query-builder-inline-grid">
                            <label className="run-surface-query-builder-control">
                              <span>Read admin token</span>
                              <input
                                onChange={(event) => setReplayIntentServerAuditReadToken(event.target.value)}
                                placeholder="Optional read token"
                                type="password"
                                value={replayIntentServerAuditReadToken}
                              />
                            </label>
                            <label className="run-surface-query-builder-control">
                              <span>Write admin token</span>
                              <input
                                onChange={(event) => setReplayIntentServerAuditWriteToken(event.target.value)}
                                placeholder="Optional write token"
                                type="password"
                                value={replayIntentServerAuditWriteToken}
                              />
                            </label>
                          </div>
                          <div className="run-surface-query-builder-inline-grid">
                            <label className="run-surface-query-builder-control">
                              <span>Template key</span>
                              <input
                                onChange={(event) => setReplayIntentServerAuditTemplateFilter(event.target.value)}
                                placeholder="template key"
                                value={replayIntentServerAuditTemplateFilter}
                              />
                            </label>
                            <label className="run-surface-query-builder-control">
                              <span>Alias ID</span>
                              <input
                                onChange={(event) => setReplayIntentServerAuditAliasFilter(event.target.value)}
                                placeholder="alias id"
                                value={replayIntentServerAuditAliasFilter}
                              />
                            </label>
                          </div>
                          <div className="run-surface-query-builder-inline-grid">
                            <label className="run-surface-query-builder-control">
                              <span>Action</span>
                              <select
                                value={replayIntentServerAuditActionFilter}
                                onChange={(event) =>
                                  setReplayIntentServerAuditActionFilter(
                                    event.target.value as "all" | "created" | "resolved" | "revoked",
                                  )}
                              >
                                <option value="all">All actions</option>
                                <option value="created">Created</option>
                                <option value="resolved">Resolved</option>
                                <option value="revoked">Revoked</option>
                              </select>
                            </label>
                            <label className="run-surface-query-builder-control">
                              <span>Retention</span>
                              <select
                                value={replayIntentServerAuditRetentionFilter}
                                onChange={(event) =>
                                  setReplayIntentServerAuditRetentionFilter(
                                    event.target.value as "all" | RunSurfaceCollectionQueryBuilderReplayLinkRetentionPolicy,
                                  )}
                              >
                                <option value="all">All retention</option>
                                <option value="1d">1 day</option>
                                <option value="7d">7 days</option>
                                <option value="30d">30 days</option>
                                <option value="manual">Keep until cleared</option>
                              </select>
                            </label>
                            <label className="run-surface-query-builder-control">
                              <span>Source tab ID</span>
                              <input
                                onChange={(event) => setReplayIntentServerAuditSourceTabFilter(event.target.value)}
                                placeholder="tab id"
                                value={replayIntentServerAuditSourceTabFilter}
                              />
                            </label>
                          </div>
                          <div className="run-surface-query-builder-inline-grid">
                            <label className="run-surface-query-builder-control">
                              <span>Search</span>
                              <input
                                onChange={(event) => setReplayIntentServerAuditSearch(event.target.value)}
                                placeholder="search ids, labels, or details"
                                value={replayIntentServerAuditSearch}
                              />
                            </label>
                            <label className="run-surface-query-builder-control">
                              <span>Limit</span>
                              <input
                                inputMode="numeric"
                                onChange={(event) => setReplayIntentServerAuditLimit(event.target.value)}
                                placeholder="25"
                                value={replayIntentServerAuditLimit}
                              />
                            </label>
                            <label className="run-surface-query-builder-control">
                              <span>Recorded before</span>
                              <input
                                onChange={(event) => setReplayIntentServerAuditRecordedBefore(event.target.value)}
                                placeholder="2026-04-20T12:00:00+09:00"
                                value={replayIntentServerAuditRecordedBefore}
                              />
                            </label>
                          </div>
                          <label className="run-surface-query-builder-control">
                            <span>Matched prune options</span>
                            <label className="run-surface-query-builder-checkbox">
                              <input
                                checked={replayIntentServerAuditIncludeManual}
                                onChange={(event) => setReplayIntentServerAuditIncludeManual(event.target.checked)}
                                type="checkbox"
                              />
                              <span>Include manual retention entries when pruning matched records</span>
                            </label>
                          </label>
                          <div className="run-surface-query-builder-actions">
                            <button
                              className="ghost-button"
                              disabled={replayIntentServerAuditLoading}
                              onClick={() => {
                                void loadRunSurfaceCollectionQueryBuilderServerReplayLinkAudits();
                              }}
                              type="button"
                            >
                              {replayIntentServerAuditLoading ? "Loading…" : "Load server audits"}
                            </button>
                            <button
                              className="ghost-button"
                              disabled={replayIntentServerAuditLoading}
                              onClick={() => {
                                void pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords("expired");
                              }}
                              type="button"
                            >
                              Prune expired audits
                            </button>
                            <button
                              className="ghost-button"
                              disabled={replayIntentServerAuditLoading}
                              onClick={() => {
                                void pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords("matched");
                              }}
                              type="button"
                            >
                              Prune matched audits
                            </button>
                            <button
                              className="ghost-button"
                              disabled={replayIntentServerAuditLoading}
                              onClick={() => {
                                void exportRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords("json");
                              }}
                              type="button"
                            >
                              Export JSON
                            </button>
                            <button
                              className="ghost-button"
                              disabled={replayIntentServerAuditLoading}
                              onClick={() => {
                                void exportRunSurfaceCollectionQueryBuilderServerReplayLinkAuditRecords("csv");
                              }}
                              type="button"
                            >
                              Export CSV
                            </button>
                          </div>
                          {replayIntentServerAuditItems.length ? (
                            <div className="run-surface-query-builder-trace-list">
                              {replayIntentServerAuditItems.map((entry) => (
                                <div
                                  className={`run-surface-query-builder-trace-step is-${
                                    entry.action === "revoked"
                                      ? "warning"
                                      : entry.action === "resolved"
                                        ? "success"
                                        : "info"
                                  }`}
                                  key={`server-replay-audit:${entry.audit_id}`}
                                >
                                  <strong>{`${entry.action.replaceAll("_", " ")} · ${entry.template_label}`}</strong>
                                  <p>
                                    {`${entry.alias_id.slice(0, 8)} · ${entry.source_tab_label ?? "Server"} · ${formatRelativeTimestampLabel(entry.recorded_at)}`}
                                  </p>
                                  <div className="run-surface-query-builder-trace-chip-list">
                                    <span className="run-surface-query-builder-trace-chip">
                                      {entry.redaction_policy.replaceAll("_", " ")}
                                    </span>
                                    <span className="run-surface-query-builder-trace-chip">
                                      {formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue("retentionPolicy", {
                                        redactionPolicy: entry.redaction_policy,
                                        retentionPolicy: entry.retention_policy,
                                        shareMode: "indirect",
                                        syncMode: replayIntentGovernanceSyncMode,
                                      })}
                                    </span>
                                    <span className="run-surface-query-builder-trace-chip">
                                      {entry.alias_revoked_at ? "revoked alias" : "active alias"}
                                    </span>
                                    <span className="run-surface-query-builder-trace-chip">
                                      {entry.audit_id.slice(0, 8)}
                                    </span>
                                  </div>
                                  <p className="run-note">{entry.detail}</p>
                                  {entry.alias_created_at ? (
                                    <p className="run-note">
                                      {`Alias created ${formatRelativeTimestampLabel(entry.alias_created_at)}.`}
                                    </p>
                                  ) : null}
                                  {entry.alias_expires_at ? (
                                    <p className="run-note">
                                      {`Alias expires ${formatRelativeTimestampLabel(entry.alias_expires_at)}.`}
                                    </p>
                                  ) : null}
                                  {entry.alias_revoked_at ? (
                                    <p className="run-note">
                                      {`Alias revoked ${formatRelativeTimestampLabel(entry.alias_revoked_at)}.`}
                                    </p>
                                  ) : null}
                                </div>
                              ))}
                            </div>
                          ) : replayIntentServerAuditStatus ? (
                            <p className="empty-state">No server replay alias audits match the current admin filter.</p>
                          ) : null}
                        </div>
                        <div className="run-surface-query-builder-trace-panel is-nested">
                          <div className="run-surface-query-builder-card-head">
                            <strong>Managed audit export jobs</strong>
                            <span>{replayIntentServerAuditExportJobTotal
                              ? `${replayIntentServerAuditExportJobTotal} loaded`
                              : "Server snapshots"}</span>
                          </div>
                          <p className="run-note">
                            Create persisted server-side export jobs from the current replay alias audit filters, then
                            download their captured payloads and inspect created/downloaded history.
                          </p>
                          {replayIntentServerAuditExportJobStatus ? (
                            <p className={`run-note run-surface-query-builder-note is-${replayIntentServerAuditExportJobStatus.tone}`}>
                              {replayIntentServerAuditExportJobStatus.message}
                            </p>
                          ) : null}
                          <div className="run-surface-query-builder-actions">
                            <button
                              className="ghost-button"
                              disabled={replayIntentServerAuditExportJobLoading}
                              onClick={() => {
                                void createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord("json");
                              }}
                              type="button"
                            >
                              Create JSON job
                            </button>
                            <button
                              className="ghost-button"
                              disabled={replayIntentServerAuditExportJobLoading}
                              onClick={() => {
                                void createRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord("csv");
                              }}
                              type="button"
                            >
                              Create CSV job
                            </button>
                            <button
                              className="ghost-button"
                              disabled={replayIntentServerAuditExportJobLoading}
                              onClick={() => {
                                void loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobs();
                              }}
                              type="button"
                            >
                              {replayIntentServerAuditExportJobLoading ? "Loading…" : "Load export jobs"}
                            </button>
                            <button
                              className="ghost-button"
                              disabled={replayIntentServerAuditExportJobLoading}
                              onClick={() => {
                                void pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecords("expired");
                              }}
                              type="button"
                            >
                              Prune expired jobs
                            </button>
                            <button
                              className="ghost-button"
                              disabled={replayIntentServerAuditExportJobLoading}
                              onClick={() => {
                                void pruneRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecords("matched");
                              }}
                              type="button"
                            >
                              Prune matched jobs
                            </button>
                          </div>
                          {replayIntentServerAuditExportJobs.length ? (
                            <div className="run-surface-query-builder-trace-list">
                              {replayIntentServerAuditExportJobs.map((job) => (
                                <div
                                  className="run-surface-query-builder-trace-step is-info"
                                  key={`server-replay-audit-export-job:${job.job_id}`}
                                >
                                  <strong>{`${job.export_format.toUpperCase()} · ${job.filename}`}</strong>
                                  <p>
                                    {`${job.job_id.slice(0, 8)} · ${job.requested_by_tab_label ?? "Server"} · ${formatRelativeTimestampLabel(job.created_at)}`}
                                  </p>
                                  <div className="run-surface-query-builder-trace-chip-list">
                                    <span className="run-surface-query-builder-trace-chip">
                                      {job.status}
                                    </span>
                                    <span className="run-surface-query-builder-trace-chip">
                                      {`${job.record_count} record${job.record_count === 1 ? "" : "s"}`}
                                    </span>
                                    <span className="run-surface-query-builder-trace-chip">
                                      {`${job.content_length} bytes`}
                                    </span>
                                    {job.template_key ? (
                                      <span className="run-surface-query-builder-trace-chip">
                                        {job.template_key}
                                      </span>
                                    ) : null}
                                    {job.artifact_id ? (
                                      <span className="run-surface-query-builder-trace-chip">
                                        {`artifact ${job.artifact_id.slice(0, 8)}`}
                                      </span>
                                    ) : null}
                                  </div>
                                  <p className="run-note">{`${job.content_type} · ${job.export_format.toUpperCase()} export`}</p>
                                  {job.completed_at ? (
                                    <p className="run-note">
                                      {`Completed ${formatRelativeTimestampLabel(job.completed_at)}.`}
                                    </p>
                                  ) : null}
                                  {job.expires_at ? (
                                    <p className="run-note">
                                      {`Expires ${formatRelativeTimestampLabel(job.expires_at)}.`}
                                    </p>
                                  ) : null}
                                  <div className="run-surface-query-builder-actions">
                                    <button
                                      className="ghost-button"
                                      disabled={replayIntentServerAuditExportJobLoading}
                                      onClick={() => {
                                        void downloadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobRecord(job.job_id);
                                      }}
                                      type="button"
                                    >
                                      Download job
                                    </button>
                                    <button
                                      className="ghost-button"
                                      disabled={replayIntentServerAuditExportJobLoading}
                                      onClick={() => {
                                        void loadRunSurfaceCollectionQueryBuilderServerReplayLinkAuditExportJobHistory(job.job_id);
                                      }}
                                      type="button"
                                    >
                                      Load history
                                    </button>
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : replayIntentServerAuditExportJobStatus ? (
                            <p className="empty-state">No managed replay audit export jobs match the current admin filter.</p>
                          ) : null}
                          {replayIntentServerAuditExportJobHistory ? (
                            <div className="run-surface-query-builder-trace-panel is-nested">
                              <div className="run-surface-query-builder-card-head">
                                <strong>Export job history</strong>
                                <span>{replayIntentServerAuditExportJobHistory.job.filename}</span>
                              </div>
                              <p className="run-note">
                                {`${replayIntentServerAuditExportJobHistory.job.job_id.slice(0, 8)} · ${replayIntentServerAuditExportJobHistory.history.length} event${replayIntentServerAuditExportJobHistory.history.length === 1 ? "" : "s"}`}
                              </p>
                              <div className="run-surface-query-builder-trace-list">
                                {replayIntentServerAuditExportJobHistory.history.map((entry) => (
                                  <div
                                    className={`run-surface-query-builder-trace-step is-${
                                      entry.action === "downloaded" ? "success" : "info"
                                    }`}
                                    key={`server-replay-audit-export-job-history:${entry.audit_id}`}
                                  >
                                    <strong>{entry.action.replaceAll("_", " ")}</strong>
                                    <p>
                                      {`${entry.source_tab_label ?? "Server"} · ${formatRelativeTimestampLabel(entry.recorded_at)}`}
                                    </p>
                                    <div className="run-surface-query-builder-trace-chip-list">
                                      {entry.template_key ? (
                                        <span className="run-surface-query-builder-trace-chip">
                                          {entry.template_key}
                                        </span>
                                      ) : null}
                                      {entry.export_format ? (
                                        <span className="run-surface-query-builder-trace-chip">
                                          {entry.export_format.toUpperCase()}
                                        </span>
                                      ) : null}
                                      <span className="run-surface-query-builder-trace-chip">
                                        {entry.audit_id.slice(0, 8)}
                                      </span>
                                    </div>
                                    <p className="run-note">{entry.detail}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ) : null}
                        </div>
                        {replayIntentGovernanceConflicts.length ? (
                          <div className="run-surface-query-builder-trace-panel is-nested">
                            <div className="run-surface-query-builder-card-head">
                              <strong>Pending governance sync conflicts</strong>
                              <span>{`${replayIntentGovernanceConflicts.length} pending`}</span>
                            </div>
                            <p className="run-note">
                              Remote tabs changed replay link share governance while this tab stayed on a different configuration.
                              Review each change to decide whether this tab keeps its local policy or adopts the remote one.
                            </p>
                            <div className="run-surface-query-builder-trace-list">
                              {replayIntentGovernanceConflicts.map((conflict) => (
                                <div
                                  className="run-surface-query-builder-trace-step is-warning"
                                  key={`replay-link-governance-conflict:${conflict.conflictKey}`}
                                >
                                  <strong>{conflict.sourceTabLabel}</strong>
                                  <p>
                                    {`Detected ${formatRelativeTimestampLabel(conflict.detectedAt)} · remote ${conflict.remoteShareMode} / ${conflict.remoteRedactionPolicy.replaceAll("_", " ")} / ${formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue("retentionPolicy", {
                                      redactionPolicy: conflict.remoteRedactionPolicy,
                                      retentionPolicy: conflict.remoteRetentionPolicy,
                                      shareMode: conflict.remoteShareMode,
                                      syncMode: replayIntentGovernanceSyncMode,
                                    })} · local ${conflict.localShareMode} / ${conflict.localRedactionPolicy.replaceAll("_", " ")} / ${formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue("retentionPolicy", {
                                      redactionPolicy: conflict.localRedactionPolicy,
                                      retentionPolicy: conflict.localRetentionPolicy,
                                      shareMode: conflict.localShareMode,
                                      syncMode: replayIntentGovernanceSyncMode,
                                    })}.`}
                                  </p>
                                  <div className="run-surface-query-builder-trace-chip-list">
                                    <span className="run-surface-query-builder-trace-chip">
                                      {`Local · ${conflict.localShareMode} · ${conflict.localRedactionPolicy.replaceAll("_", " ")} · ${formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue("retentionPolicy", {
                                        redactionPolicy: conflict.localRedactionPolicy,
                                        retentionPolicy: conflict.localRetentionPolicy,
                                        shareMode: conflict.localShareMode,
                                        syncMode: replayIntentGovernanceSyncMode,
                                      })}`}
                                    </span>
                                    <span className="run-surface-query-builder-trace-chip is-active">
                                      {`Remote · ${conflict.remoteShareMode} · ${conflict.remoteRedactionPolicy.replaceAll("_", " ")} · ${formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue("retentionPolicy", {
                                        redactionPolicy: conflict.remoteRedactionPolicy,
                                        retentionPolicy: conflict.remoteRetentionPolicy,
                                        shareMode: conflict.remoteShareMode,
                                        syncMode: replayIntentGovernanceSyncMode,
                                      })}`}
                                    </span>
                                    <span className="run-surface-query-builder-trace-chip">
                                      {`Diff · ${getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys(
                                        {
                                          redactionPolicy: conflict.localRedactionPolicy,
                                          retentionPolicy: conflict.localRetentionPolicy,
                                          shareMode: conflict.localShareMode,
                                          syncMode: replayIntentGovernanceSyncMode,
                                        },
                                        {
                                          redactionPolicy: conflict.remoteRedactionPolicy,
                                          retentionPolicy: conflict.remoteRetentionPolicy,
                                          shareMode: conflict.remoteShareMode,
                                          syncMode: replayIntentGovernanceSyncMode,
                                        },
                                      ).map((fieldKey) =>
                                        fieldKey === "shareMode"
                                          ? "share mode"
                                          : fieldKey === "redactionPolicy"
                                            ? "redaction"
                                            : fieldKey === "retentionPolicy"
                                              ? "retention"
                                            : "sync mode",
                                      ).join(", ")}`}
                                    </span>
                                  </div>
                                  <div className="run-surface-query-builder-actions">
                                    <button
                                      className="ghost-button"
                                      onClick={() => {
                                        appendReplayIntentGovernanceAuditEntry({
                                          at: new Date().toISOString(),
                                          detail: `${predicateRefReplayApplyHistoryTabIdentity.label} kept local replay link governance after reviewing ${conflict.sourceTabLabel}'s update.`,
                                          diffKeys: getRunSurfaceCollectionQueryBuilderReplayLinkGovernanceDiffKeys(
                                            {
                                              redactionPolicy: conflict.remoteRedactionPolicy,
                                              retentionPolicy: conflict.remoteRetentionPolicy,
                                              shareMode: conflict.remoteShareMode,
                                              syncMode: replayIntentGovernanceSyncMode,
                                            },
                                            currentReplayIntentGovernanceSnapshot,
                                          ),
                                          fromState: {
                                            redactionPolicy: conflict.remoteRedactionPolicy,
                                            retentionPolicy: conflict.remoteRetentionPolicy,
                                            shareMode: conflict.remoteShareMode,
                                            syncMode: replayIntentGovernanceSyncMode,
                                          },
                                          kind: "conflict_resolved_local",
                                          remoteSourceTabId: conflict.sourceTabId,
                                          remoteSourceTabLabel: conflict.sourceTabLabel,
                                          sourceTabId: predicateRefReplayApplyHistoryTabIdentity.tabId,
                                          sourceTabLabel: predicateRefReplayApplyHistoryTabIdentity.label,
                                          toState: currentReplayIntentGovernanceSnapshot,
                                        });
                                        dismissReplayIntentGovernanceConflict(conflict.conflictKey);
                                        setReplayIntentShareStatus({
                                          message: `Kept local replay link governance for ${predicateRefReplayApplyHistoryTabIdentity.label} instead of ${conflict.sourceTabLabel}.`,
                                          tone: "muted",
                                        });
                                      }}
                                      type="button"
                                    >
                                      Keep local governance
                                    </button>
                                    <button
                                      className="ghost-button"
                                      onClick={() => {
                                        applyReplayIntentGovernanceSnapshot({
                                          redactionPolicy: conflict.remoteRedactionPolicy,
                                          retentionPolicy: conflict.remoteRetentionPolicy,
                                          shareMode: conflict.remoteShareMode,
                                          syncMode: replayIntentGovernanceSyncMode,
                                        }, {
                                          detail: `Applied ${conflict.sourceTabLabel}'s replay link governance after review.`,
                                          kind: "conflict_resolved_remote",
                                          remoteSourceTabId: conflict.sourceTabId,
                                          remoteSourceTabLabel: conflict.sourceTabLabel,
                                        });
                                        dismissReplayIntentGovernanceConflict(conflict.conflictKey);
                                        setReplayIntentShareStatus({
                                          message: `Applied ${conflict.sourceTabLabel}'s replay link governance in this tab.`,
                                          tone: "success",
                                        });
                                      }}
                                      type="button"
                                    >
                                      Apply remote governance
                                    </button>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : null}
                        <div className="run-surface-query-builder-trace-panel is-nested">
                          <div className="run-surface-query-builder-card-head">
                            <strong>Cross-device governance resolution</strong>
                            <span>
                              {currentReplayIntentGovernancePayloadValue
                                ? `${currentReplayIntentGovernancePayloadValue.length} chars`
                                : "Payload unavailable"}
                            </span>
                          </div>
                          <p className="run-note">
                            Export the current replay link governance as a compact payload, then paste it into another
                            device or browser to apply the same share mode, redaction, sync policy, and retention there.
                          </p>
                          <div className="run-surface-query-builder-actions">
                            <button
                              className="ghost-button"
                              onClick={() => {
                                void copyRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload();
                              }}
                              type="button"
                            >
                              Copy governance payload
                            </button>
                            <button
                              className="ghost-button"
                              disabled={!replayIntentGovernancePayloadDraft.trim()}
                              onClick={() => {
                                applyRunSurfaceCollectionQueryBuilderReplayLinkGovernancePayload();
                              }}
                              type="button"
                            >
                              Apply governance payload
                            </button>
                          </div>
                          <label className="run-surface-query-builder-control">
                            <span>Paste payload</span>
                            <textarea
                              onChange={(event) => setReplayIntentGovernancePayloadDraft(event.target.value)}
                              placeholder="Paste a replay governance payload from another device"
                              rows={3}
                              value={replayIntentGovernancePayloadDraft}
                            />
                          </label>
                        </div>
                        {replayIntentGovernanceAuditTrail.length ? (
                          <div className="run-surface-query-builder-trace-panel is-nested">
                            <div className="run-surface-query-builder-card-head">
                              <strong>Governance audit trail</strong>
                              <span>{`${replayIntentGovernanceAuditTrail.length} entries`}</span>
                            </div>
                            <div className="run-surface-query-builder-trace-list">
                              {replayIntentGovernanceAuditTrail.slice(0, 6).map((entry) => (
                                <div
                                  className={`run-surface-query-builder-trace-step is-${
                                    entry.kind === "conflict_detected"
                                      ? "warning"
                                      : entry.kind === "remote_ignored"
                                        ? "muted"
                                        : "success"
                                  }`}
                                  key={`replay-link-governance-audit:${entry.id}`}
                                >
                                  <strong>
                                    {`${entry.kind.replaceAll("_", " ")} · ${entry.sourceTabLabel}`}
                                  </strong>
                                  <p>{`${entry.at} · ${entry.detail}`}</p>
                                  <div className="run-surface-query-builder-trace-chip-list">
                                    {entry.diffKeys.length ? entry.diffKeys.map((fieldKey) => (
                                      <span className="run-surface-query-builder-trace-chip" key={`${entry.id}:${fieldKey}`}>
                                        {`${fieldKey === "shareMode"
                                          ? "Share mode"
                                          : fieldKey === "redactionPolicy"
                                            ? "Redaction"
                                            : fieldKey === "retentionPolicy"
                                              ? "Retention"
                                              : "Sync mode"}: ${
                                          formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue(fieldKey, entry.fromState)
                                        } → ${
                                          formatRunSurfaceCollectionQueryBuilderReplayLinkGovernanceFieldValue(fieldKey, entry.toState)
                                        }`}
                                      </span>
                                    )) : (
                                      <span className="run-surface-query-builder-trace-chip">
                                        No field delta
                                      </span>
                                    )}
                                    {entry.remoteSourceTabLabel ? (
                                      <span className="run-surface-query-builder-trace-chip">
                                        {`Remote source · ${entry.remoteSourceTabLabel}`}
                                      </span>
                                    ) : null}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : null}
                        {visibleReplayIntentLinkAuditTrail.length ? (
                          <div className="run-surface-query-builder-trace-panel is-nested">
                            <div className="run-surface-query-builder-card-head">
                              <strong>Replay link audit trail</strong>
                              <span>{`${visibleReplayIntentLinkAuditTrail.length} entries`}</span>
                            </div>
                            <div className="run-surface-query-builder-trace-list">
                              {visibleReplayIntentLinkAuditTrail.slice(0, 5).map((entry) => (
                                <div
                                  className={`run-surface-query-builder-trace-step is-${
                                    entry.status === "success"
                                      ? "success"
                                      : entry.status === "cancelled"
                                        ? "muted"
                                        : "warning"
                                  }`}
                                  key={`replay-link-audit:${entry.id}`}
                                >
                                  <strong>
                                    {`${entry.action === "copy" ? "Copied" : entry.action === "share" ? "Shared" : "Revoked"} · ${
                                      entry.mode === "indirect" ? "alias" : "portable"
                                    } · ${entry.redactionPolicy.replaceAll("_", " ")}`}
                                  </strong>
                                  <p>
                                    {`${entry.sourceTabLabel} · ${entry.at} · ${entry.linkLength} chars`}
                                  </p>
                                  <div className="run-surface-query-builder-trace-chip-list">
                                    <span className={`run-surface-query-builder-trace-chip${
                                      entry.status === "success" ? " is-active" : ""
                                    }`}>
                                      {entry.status}
                                    </span>
                                    {entry.aliasId ? (
                                      <span className="run-surface-query-builder-trace-chip">
                                        {`alias ${entry.aliasId.slice(0, 8)}`}
                                      </span>
                                    ) : null}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : null}
    </>
  );
}
