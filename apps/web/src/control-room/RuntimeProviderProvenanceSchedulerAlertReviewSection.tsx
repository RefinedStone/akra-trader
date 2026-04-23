// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerAlertReviewSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-history-head">
              <strong>Scheduler alert occurrence timeline</strong>
              <p>
                Review paginated lag/failure occurrences without mixing them into the broader
                operator alert history.
              </p>
            </div>
            <div className="run-filter-summary-chip-row">
              <span className="run-filter-summary-chip">
                Total {providerProvenanceSchedulerAlertHistory?.summary.total_occurrences ?? 0} occurrence(s)
              </span>
              <span className="run-filter-summary-chip">
                Active {providerProvenanceSchedulerAlertHistory?.summary.active_count ?? 0} · resolved {" "}
                {providerProvenanceSchedulerAlertHistory?.summary.resolved_count ?? 0}
              </span>
              {(providerProvenanceSchedulerAlertHistory?.summary.by_category ?? []).map((entry) => (
                <span
                  className="run-filter-summary-chip"
                  key={`provider-scheduler-alert-summary-${entry.category}`}
                >
                  {formatWorkflowToken(entry.category)} {entry.total} total · {entry.resolved_count} resolved
                </span>
              ))}
              <span className="run-filter-summary-chip">
                Facet {formatProviderProvenanceSchedulerNarrativeFacet(
                  providerProvenanceAnalyticsQuery.scheduler_alert_narrative_facet,
                )}
              </span>
              {providerProvenanceSchedulerAlertHistory?.search_summary ? (
                <span className="run-filter-summary-chip">
                  Search ranked · {providerProvenanceSchedulerAlertHistory.search_summary.matched_occurrences} match(es) · top {providerProvenanceSchedulerAlertHistory.search_summary.top_score}
                </span>
              ) : null}
              {providerProvenanceSchedulerAlertHistory?.search_summary?.operator_count ? (
                <span className="run-filter-summary-chip">
                  Field ops {providerProvenanceSchedulerAlertHistory.search_summary.operator_count} · boolean {providerProvenanceSchedulerAlertHistory.search_summary.boolean_operator_count} · semantic {providerProvenanceSchedulerAlertHistory.search_summary.semantic_concept_count}
                </span>
              ) : null}
              {providerProvenanceSchedulerAlertHistory?.search_summary ? (
                <span className="run-filter-summary-chip">
                  Index {providerProvenanceSchedulerAlertHistory.search_summary.indexed_occurrence_count} occurrence(s) · {providerProvenanceSchedulerAlertHistory.search_summary.indexed_term_count} term(s)
                </span>
              ) : null}
              {providerProvenanceSchedulerAlertHistory?.search_summary?.relevance_model ? (
                <span className="run-filter-summary-chip">
                  {providerProvenanceSchedulerAlertHistory.search_summary.persistence_mode === "external_scheduler_search_service"
                    ? "External search service"
                    : providerProvenanceSchedulerAlertHistory.search_summary.persistence_mode === "standalone_persistent_scheduler_search_store"
                      ? "Standalone persistent index"
                      : providerProvenanceSchedulerAlertHistory.search_summary.persistence_mode === "embedded_scheduler_search_service"
                        ? "Embedded search service"
                        : providerProvenanceSchedulerAlertHistory.search_summary.persistence_mode === "record_backed_scheduler_search_projection"
                          ? "Persistent index"
                          : "Ephemeral index"} · {providerProvenanceSchedulerAlertHistory.search_summary.relevance_model}
                </span>
              ) : null}
              {providerProvenanceSchedulerAlertHistory?.search_summary?.retrieval_cluster_count ? (
                <span className="run-filter-summary-chip">
                  Clustered {providerProvenanceSchedulerAlertHistory.search_summary.retrieval_cluster_count} group(s)
                  {providerProvenanceSchedulerAlertHistory.search_summary.top_cluster_label
                    ? ` · top ${providerProvenanceSchedulerAlertHistory.search_summary.top_cluster_label}`
                    : ""}
                </span>
              ) : null}
              {providerProvenanceSchedulerAlertHistory?.search_analytics ? (
                <span className="run-filter-summary-chip">
                  Feedback {providerProvenanceSchedulerAlertHistory.search_analytics.feedback_count} · pending {providerProvenanceSchedulerAlertHistory.search_analytics.pending_feedback_count} · approved {providerProvenanceSchedulerAlertHistory.search_analytics.approved_feedback_count} · tuned {providerProvenanceSchedulerAlertHistory.search_analytics.tuned_feature_count}
                </span>
              ) : null}
            </div>
            <div className="market-data-provenance-history-actions">
              <label className="run-form-field">
                <span>Category</span>
                <select
                  value={providerProvenanceAnalyticsQuery.scheduler_alert_category}
                  onChange={(event) => {
                    setProviderProvenanceAnalyticsQuery((current) => ({
                      ...current,
                      scheduler_alert_category: event.target.value,
                    }));
                    setProviderProvenanceSchedulerAlertHistoryOffset(0);
                  }}
                >
                  <option value={ALL_FILTER_VALUE}>All categories</option>
                  {providerProvenanceSchedulerAlertCategoryOptions.map((value) => (
                    <option key={`provider-scheduler-alert-category-${value}`} value={value}>
                      {formatWorkflowToken(value)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="run-form-field">
                <span>Status</span>
                <select
                  value={providerProvenanceAnalyticsQuery.scheduler_alert_status}
                  onChange={(event) => {
                    setProviderProvenanceAnalyticsQuery((current) => ({
                      ...current,
                      scheduler_alert_status: event.target.value,
                    }));
                    setProviderProvenanceSchedulerAlertHistoryOffset(0);
                  }}
                >
                  <option value={ALL_FILTER_VALUE}>All statuses</option>
                  {providerProvenanceSchedulerAlertStatusOptions.map((value) => (
                    <option key={`provider-scheduler-alert-status-${value}`} value={value}>
                      {formatWorkflowToken(value)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="run-form-field">
                <span>Narrative facet</span>
                <select
                  value={providerProvenanceAnalyticsQuery.scheduler_alert_narrative_facet}
                  onChange={(event) => {
                    setProviderProvenanceAnalyticsQuery((current) => ({
                      ...current,
                      scheduler_alert_narrative_facet:
                        event.target.value === "resolved_narratives"
                        || event.target.value === "post_resolution_recovery"
                        || event.target.value === "recurring_occurrences"
                          ? event.target.value
                          : "all_occurrences",
                    }));
                    setProviderProvenanceSchedulerAlertHistoryOffset(0);
                  }}
                >
                  {providerProvenanceSchedulerAlertNarrativeFacetOptions.map((value) => (
                    <option key={`provider-scheduler-alert-facet-${value}`} value={value}>
                      {formatProviderProvenanceSchedulerNarrativeFacet(
                        value as ProviderProvenanceSchedulerOccurrenceNarrativeFacet,
                      )}
                    </option>
                  ))}
                </select>
              </label>
              <label className="run-form-field">
                <span>Search</span>
                <input
                  onChange={(event) => {
                    setProviderProvenanceAnalyticsQuery((current) => ({
                      ...current,
                      search_query: event.target.value,
                    }));
                    setProviderProvenanceSchedulerAlertHistoryOffset(0);
                  }}
                  placeholder='status:resolved AND (recovered OR healthy) AND NOT category:failure'
                  type="search"
                  value={providerProvenanceAnalyticsQuery.search_query}
                />
              </label>
              {providerProvenanceSchedulerAlertHistory?.search_summary?.query_plan.length ? (
                <span className="run-lineage-symbol-copy">
                  Query plan {providerProvenanceSchedulerAlertHistory.search_summary.query_plan.join(" ")}
                </span>
              ) : null}
              <button
                className="ghost-button"
                disabled={!providerProvenanceSchedulerAlertTimelineItems.length}
                onClick={() => {
                  void copyProviderProvenanceSchedulerStitchedNarrativeReport();
                }}
                type="button"
              >
                Copy stitched report
              </button>
              <button
                className="ghost-button"
                disabled={!providerProvenanceSchedulerAlertTimelineItems.length}
                onClick={() => {
                  void downloadProviderProvenanceSchedulerStitchedNarrativeCsv();
                }}
                type="button"
              >
                Download stitched CSV
              </button>
              <button
                className="ghost-button"
                disabled={!providerProvenanceSchedulerAlertTimelineItems.length}
                onClick={() => {
                  void shareProviderProvenanceSchedulerStitchedNarrativeReport();
                }}
                type="button"
              >
                Share stitched report
              </button>
              <button
                className="ghost-button"
                onClick={() => {
                  stageProviderProvenanceSchedulerNarrativeDrafts();
                }}
                type="button"
              >
                Stage narrative drafts
              </button>
              <button
                className="ghost-button"
                disabled={!providerProvenanceSchedulerAlertHistory?.previous_offset && providerProvenanceSchedulerAlertHistoryOffset === 0}
                onClick={() => {
                  setProviderProvenanceSchedulerAlertHistoryOffset(
                    providerProvenanceSchedulerAlertHistory?.previous_offset ?? 0,
                  );
                }}
                type="button"
              >
                Previous page
              </button>
              <button
                className="ghost-button"
                disabled={!(providerProvenanceSchedulerAlertHistory?.has_more ?? false)}
                onClick={() => {
                  if (typeof providerProvenanceSchedulerAlertHistory?.next_offset === "number") {
                    setProviderProvenanceSchedulerAlertHistoryOffset(
                      providerProvenanceSchedulerAlertHistory.next_offset,
                    );
                  }
                }}
                type="button"
              >
                Next page
              </button>
              <span className="run-lineage-symbol-copy">
                {providerProvenanceSchedulerAlertHistory
                  ? `${providerProvenanceSchedulerAlertHistory.query.offset + 1}-${providerProvenanceSchedulerAlertHistory.query.offset + providerProvenanceSchedulerAlertHistory.returned} of ${providerProvenanceSchedulerAlertHistory.total}`
                  : "Page 1"}
              </span>
            </div>
            {providerProvenanceSchedulerAlertHistory?.search_analytics ? (
              <>
                <div className="market-data-provenance-history-head">
                  <strong>Scheduler search analytics</strong>
                  <p>
                    Query analytics, operator feedback, and learned tuning for the active
                    scheduler narrative retrieval slice.
                  </p>
                </div>
                <div className="run-filter-summary-chip-row">
                  <span className="run-filter-summary-chip">
                    Query {providerProvenanceSchedulerAlertHistory.search_analytics.query_id}
                  </span>
                  <span className="run-filter-summary-chip">
                    Recent runs {providerProvenanceSchedulerAlertHistory.search_analytics.recent_query_count}
                  </span>
                  <span className="run-filter-summary-chip">
                    Feedback {providerProvenanceSchedulerAlertHistory.search_analytics.relevant_feedback_count} relevant · {providerProvenanceSchedulerAlertHistory.search_analytics.not_relevant_feedback_count} not relevant
                  </span>
                  <span className="run-filter-summary-chip">
                    Moderation pending {providerProvenanceSchedulerAlertHistory.search_analytics.pending_feedback_count} · approved {providerProvenanceSchedulerAlertHistory.search_analytics.approved_feedback_count} · rejected {providerProvenanceSchedulerAlertHistory.search_analytics.rejected_feedback_count}
                  </span>
                  <span className="run-filter-summary-chip">
                    Learned {providerProvenanceSchedulerAlertHistory.search_analytics.learned_relevance_active ? "active" : "cold"} · {providerProvenanceSchedulerAlertHistory.search_analytics.tuning_profile_version ?? "n/a"}
                  </span>
                  <span className="run-filter-summary-chip">
                    Channel Δ lexical {providerProvenanceSchedulerAlertHistory.search_analytics.channel_adjustments.lexical} · semantic {providerProvenanceSchedulerAlertHistory.search_analytics.channel_adjustments.semantic} · operator {providerProvenanceSchedulerAlertHistory.search_analytics.channel_adjustments.operator}
                  </span>
                </div>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Tuning</th>
                      <th>Recent queries</th>
                      <th>Recent feedback</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>
                        <strong>Field tuning</strong>
                        <p className="run-lineage-symbol-copy">
                          {providerProvenanceSchedulerAlertHistory.search_analytics.top_field_adjustments.length
                            ? providerProvenanceSchedulerAlertHistory.search_analytics.top_field_adjustments
                                .map((entry) => `${entry.field} ${entry.score > 0 ? "+" : ""}${entry.score}`)
                                .join(" · ")
                            : "No learned field adjustments yet."}
                        </p>
                        <p className="run-lineage-symbol-copy">
                          {providerProvenanceSchedulerAlertHistory.search_analytics.top_semantic_adjustments.length
                            ? providerProvenanceSchedulerAlertHistory.search_analytics.top_semantic_adjustments
                                .map((entry) => `${entry.concept} ${entry.score > 0 ? "+" : ""}${entry.score}`)
                                .join(" · ")
                            : "No learned semantic adjustments yet."}
                        </p>
                        <p className="run-lineage-symbol-copy">
                          {providerProvenanceSchedulerAlertHistory.search_analytics.top_operator_adjustments.length
                            ? providerProvenanceSchedulerAlertHistory.search_analytics.top_operator_adjustments
                                .map((entry) => `${entry.operator} ${entry.score > 0 ? "+" : ""}${entry.score}`)
                                .join(" · ")
                            : "No learned operator adjustments yet."}
                        </p>
                      </td>
                      <td>
                        <strong>Recent queries</strong>
                        {providerProvenanceSchedulerAlertHistory.search_analytics.recent_queries.length ? (
                          providerProvenanceSchedulerAlertHistory.search_analytics.recent_queries.map((entry) => (
                            <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-analytics-query-${entry.query_id}`}>
                              {entry.query} · top {entry.top_score} · {entry.matched_occurrences} match(es)
                            </p>
                          ))
                        ) : (
                          <p className="run-lineage-symbol-copy">No persisted query analytics yet.</p>
                        )}
                      </td>
                      <td>
                        <strong>Recent feedback</strong>
                        {providerProvenanceSchedulerAlertHistory.search_analytics.recent_feedback.length ? (
                          providerProvenanceSchedulerAlertHistory.search_analytics.recent_feedback.map((entry) => (
                            <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-feedback-${entry.feedback_id}`}>
                              {entry.occurrence_id} · {formatWorkflowToken(entry.signal)} · {formatWorkflowToken(entry.moderation_status)} · {entry.matched_fields.join(", ") || "ranked fields"}
                            </p>
                          ))
                        ) : (
                          <p className="run-lineage-symbol-copy">No feedback recorded for this query yet.</p>
                        )}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </>
            ) : null}
            <div className="market-data-provenance-history-head">
              <strong>Scheduler query analytics dashboard</strong>
              <p>
                Moderate feedback before it influences learned ranking and inspect which
                scheduler search slices operators are using most often.
              </p>
            </div>
            <div className="market-data-provenance-history-actions">
              <label className="run-form-field">
                <span>Dashboard search</span>
                <input
                  onChange={(event) => {
                    setProviderProvenanceSchedulerSearchDashboardFilter((current) => ({
                      ...current,
                      search: event.target.value,
                    }));
                  }}
                  placeholder="query, occurrence id, actor, moderated by"
                  type="search"
                  value={providerProvenanceSchedulerSearchDashboardFilter.search}
                />
              </label>
              <label className="run-form-field">
                <span>Moderation</span>
                <select
                  value={providerProvenanceSchedulerSearchDashboardFilter.moderation_status}
                  onChange={(event) => {
                    setProviderProvenanceSchedulerSearchDashboardFilter((current) => ({
                      ...current,
                      moderation_status: event.target.value,
                    }));
                  }}
                >
                  <option value={ALL_FILTER_VALUE}>All states</option>
                  <option value="pending">Pending</option>
                  <option value="approved">Approved</option>
                  <option value="rejected">Rejected</option>
                </select>
              </label>
              <label className="run-form-field">
                <span>Signal</span>
                <select
                  value={providerProvenanceSchedulerSearchDashboardFilter.signal}
                  onChange={(event) => {
                    setProviderProvenanceSchedulerSearchDashboardFilter((current) => ({
                      ...current,
                      signal: event.target.value,
                    }));
                  }}
                >
                  <option value={ALL_FILTER_VALUE}>All signals</option>
                  <option value="relevant">Relevant</option>
                  <option value="not_relevant">Not relevant</option>
                </select>
              </label>
              <label className="run-form-field">
                <span>Governance view</span>
                <select
                  value={providerProvenanceSchedulerSearchDashboardFilter.governance_view}
                  onChange={(event) => {
                    setProviderProvenanceSchedulerSearchDashboardFilter((current) => ({
                      ...current,
                      governance_view: event.target.value,
                    }));
                    setSelectedProviderProvenanceSchedulerSearchFeedbackIds([]);
                  }}
                >
                  <option value="all_feedback">All feedback</option>
                  <option value="pending_queue">Pending queue</option>
                  <option value="stale_pending">Stale pending</option>
                  <option value="high_score_pending">High-score pending</option>
                  <option value="moderated">Moderated</option>
                  <option value="conflicting_queries">Conflicting queries</option>
                </select>
              </label>
              <label className="run-form-field">
                <span>Window</span>
                <select
                  value={providerProvenanceSchedulerSearchDashboardFilter.window_days}
                  onChange={(event) => {
                    setProviderProvenanceSchedulerSearchDashboardFilter((current) => ({
                      ...current,
                      window_days: Number.parseInt(event.target.value, 10) || 30,
                    }));
                  }}
                >
                  {[14, 30, 60, 90].map((value) => (
                    <option key={`provider-scheduler-search-window-${value}`} value={value}>
                      {value}d
                    </option>
                  ))}
                </select>
              </label>
              <label className="run-form-field">
                <span>Stale pending</span>
                <select
                  value={providerProvenanceSchedulerSearchDashboardFilter.stale_pending_hours}
                  onChange={(event) => {
                    setProviderProvenanceSchedulerSearchDashboardFilter((current) => ({
                      ...current,
                      stale_pending_hours: Number.parseInt(event.target.value, 10) || 24,
                    }));
                  }}
                >
                  {[12, 24, 48, 72].map((value) => (
                    <option key={`provider-scheduler-search-stale-${value}`} value={value}>
                      {value}h
                    </option>
                  ))}
                </select>
              </label>
              {providerProvenanceSchedulerSearchDashboard?.query.search ? (
                <span className="run-lineage-symbol-copy">
                  Dashboard search {providerProvenanceSchedulerSearchDashboard.query.search}
                </span>
              ) : null}
            </div>
            {providerProvenanceSchedulerSearchDashboard ? (
              <>
                <div className="run-filter-summary-chip-row">
                  <span className="run-filter-summary-chip">
                    Queries {providerProvenanceSchedulerSearchDashboard.summary.query_count} · distinct {providerProvenanceSchedulerSearchDashboard.summary.distinct_query_count}
                  </span>
                  <span className="run-filter-summary-chip">
                    Feedback {providerProvenanceSchedulerSearchDashboard.summary.feedback_count} · pending {providerProvenanceSchedulerSearchDashboard.summary.pending_feedback_count}
                  </span>
                  <span className="run-filter-summary-chip">
                    Approved {providerProvenanceSchedulerSearchDashboard.summary.approved_feedback_count} · rejected {providerProvenanceSchedulerSearchDashboard.summary.rejected_feedback_count}
                  </span>
                  <span className="run-filter-summary-chip">
                    Signals {providerProvenanceSchedulerSearchDashboard.summary.relevant_feedback_count} relevant · {providerProvenanceSchedulerSearchDashboard.summary.not_relevant_feedback_count} not relevant
                  </span>
                  <span className="run-filter-summary-chip">
                    Governance stale {providerProvenanceSchedulerSearchDashboard.moderation_governance.stale_pending_count} · high-score {providerProvenanceSchedulerSearchDashboard.moderation_governance.high_score_pending_count}
                  </span>
                  <span className="run-filter-summary-chip">
                    Approval rate {providerProvenanceSchedulerSearchDashboard.moderation_governance.approval_rate_pct}% · conflicting queries {providerProvenanceSchedulerSearchDashboard.moderation_governance.conflicting_query_count}
                  </span>
                </div>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Long-horizon quality</th>
                      <th>Actor rollup</th>
                      <th>Moderator rollup</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>
                        <strong>
                          {providerProvenanceSchedulerSearchDashboard.quality_dashboard.window_days} day trend
                        </strong>
                        {providerProvenanceSchedulerSearchDashboard.quality_dashboard.time_series.length ? (
                          providerProvenanceSchedulerSearchDashboard.quality_dashboard.time_series
                            .slice(-6)
                            .map((entry) => (
                              <p
                                className="run-lineage-symbol-copy"
                                key={`provider-scheduler-search-quality-${entry.bucket_key}`}
                              >
                                {entry.bucket_label} · q {entry.query_count} · fb {entry.feedback_count} · pending {entry.pending_feedback_count} · approved {entry.approved_feedback_count}
                              </p>
                            ))
                        ) : (
                          <p className="run-lineage-symbol-copy">No long-horizon scheduler search activity in the selected window.</p>
                        )}
                      </td>
                      <td>
                        <strong>Actors</strong>
                        {providerProvenanceSchedulerSearchDashboard.quality_dashboard.actor_rollups.length ? (
                          providerProvenanceSchedulerSearchDashboard.quality_dashboard.actor_rollups.map((entry) => (
                            <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-actor-${entry.actor}`}>
                              {entry.actor} · {entry.feedback_count} feedback · pending {entry.pending_feedback_count} · relevant {entry.relevant_feedback_count}
                            </p>
                          ))
                        ) : (
                          <p className="run-lineage-symbol-copy">No actor rollups for the current filter.</p>
                        )}
                      </td>
                      <td>
                        <strong>Moderators</strong>
                        {providerProvenanceSchedulerSearchDashboard.quality_dashboard.moderator_rollups.length ? (
                          providerProvenanceSchedulerSearchDashboard.quality_dashboard.moderator_rollups.map((entry) => (
                            <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-moderator-${entry.moderated_by}`}>
                              {entry.moderated_by} · {entry.feedback_count} decisions · approved {entry.approved_feedback_count} · rejected {entry.rejected_feedback_count}
                            </p>
                          ))
                        ) : (
                          <p className="run-lineage-symbol-copy">No moderator decisions recorded in the selected window.</p>
                        )}
                      </td>
                    </tr>
                  </tbody>
                </table>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Top queries</th>
                      <th>Coverage</th>
                      <th>Moderation</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>
                        <strong>Frequent searches</strong>
                        {providerProvenanceSchedulerSearchDashboard.top_queries.length ? (
                          providerProvenanceSchedulerSearchDashboard.top_queries.map((entry) => (
                            <div key={`provider-scheduler-search-dashboard-query-${entry.query_ids.join("-")}`}>
                              <p className="run-lineage-symbol-copy">
                                {entry.query} · {entry.search_count} run(s) · top {entry.top_score}
                              </p>
                              <div className="market-data-provenance-history-actions">
                                <button
                                  className="ghost-button"
                                  onClick={() => {
                                    setProviderProvenanceAnalyticsQuery((current) => ({
                                      ...current,
                                      search_query: entry.query,
                                    }));
                                    setProviderProvenanceSchedulerAlertHistoryOffset(0);
                                  }}
                                  type="button"
                                >
                                  Use query
                                </button>
                              </div>
                            </div>
                          ))
                        ) : (
                          <p className="run-lineage-symbol-copy">No persisted scheduler search queries match the current dashboard filter.</p>
                        )}
                      </td>
                      <td>
                        <strong>Search footprint</strong>
                        {providerProvenanceSchedulerSearchDashboard.top_queries.length ? (
                          providerProvenanceSchedulerSearchDashboard.top_queries.map((entry) => (
                            <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-dashboard-coverage-${entry.query_ids.join("-")}`}>
                              {entry.matched_occurrences_total} occurrence hit(s) · {entry.semantic_concepts.join(" · ") || "no semantic concepts"} · {entry.parsed_operators.join(" · ") || "no operators"}
                            </p>
                          ))
                        ) : (
                          <p className="run-lineage-symbol-copy">Coverage rolls up here once operators run scheduler searches.</p>
                        )}
                      </td>
                      <td>
                        <strong>Feedback counts</strong>
                        {providerProvenanceSchedulerSearchDashboard.top_queries.length ? (
                          providerProvenanceSchedulerSearchDashboard.top_queries.map((entry) => (
                            <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-dashboard-feedback-${entry.query_ids.join("-")}`}>
                              pending {entry.pending_feedback_count} · approved {entry.approved_feedback_count} · rejected {entry.rejected_feedback_count}
                            </p>
                          ))
                        ) : (
                          <p className="run-lineage-symbol-copy">No moderation queue activity for the current filter yet.</p>
                        )}
                      </td>
                    </tr>
                  </tbody>
                </table>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>
                        <input
                          checked={
                            providerProvenanceSchedulerSearchDashboard.feedback_items.length > 0
                            && providerProvenanceSchedulerSearchDashboard.feedback_items.every((entry) =>
                              selectedProviderProvenanceSchedulerSearchFeedbackIds.includes(entry.feedback_id),
                            )
                          }
                          onChange={(event) => {
                            setSelectedProviderProvenanceSchedulerSearchFeedbackIds(
                              event.target.checked
                                ? providerProvenanceSchedulerSearchDashboard.feedback_items.map((entry) => entry.feedback_id)
                                : [],
                            );
                          }}
                          type="checkbox"
                        />
                      </th>
                      <th>Feedback item</th>
                      <th>Signals</th>
                      <th>Moderation</th>
                    </tr>
                  </thead>
                  <tbody>
                    {providerProvenanceSchedulerSearchDashboard.feedback_items.length ? (
                      providerProvenanceSchedulerSearchDashboard.feedback_items.map((entry) => (
                        <tr key={`provider-scheduler-search-dashboard-feedback-item-${entry.feedback_id}`}>
                          <td>
                            <input
                              checked={selectedProviderProvenanceSchedulerSearchFeedbackIds.includes(entry.feedback_id)}
                              onChange={(event) => {
                                setSelectedProviderProvenanceSchedulerSearchFeedbackIds((current) =>
                                  event.target.checked
                                    ? [...current, entry.feedback_id]
                                    : current.filter((feedbackId) => feedbackId !== entry.feedback_id),
                                );
                              }}
                              type="checkbox"
                            />
                          </td>
                          <td>
                            <strong>{entry.query}</strong>
                            <p className="run-lineage-symbol-copy">
                              {entry.occurrence_id} · {formatWorkflowToken(entry.signal)} · score {entry.score}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              {entry.matched_fields.join(" · ") || "ranked fields"} · {entry.semantic_concepts.join(" · ") || "no semantic concepts"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Age {entry.age_hours}h · query runs {entry.query_run_count}
                            </p>
                            {entry.note ? (
                              <p className="run-lineage-symbol-copy">{entry.note}</p>
                            ) : null}
                          </td>
                          <td>
                            <strong>{formatWorkflowToken(entry.moderation_status)}</strong>
                            <p className="run-lineage-symbol-copy">
                              Recorded {formatTimestamp(entry.recorded_at)} · actor {entry.actor ?? "operator"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              Moderated {formatTimestamp(entry.moderated_at ?? null)} · by {entry.moderated_by ?? "n/a"}
                            </p>
                            <p className="run-lineage-symbol-copy">
                              {entry.stale_pending ? "Stale pending" : "Fresh queue"} · {entry.high_score_pending ? "high-score" : "normal-score"}
                            </p>
                            {entry.moderation_note ? (
                              <p className="run-lineage-symbol-copy">{entry.moderation_note}</p>
                            ) : null}
                          </td>
                          <td>
                            <div className="market-data-provenance-history-actions">
                              <button
                                className="ghost-button"
                                disabled={providerProvenanceSchedulerSearchFeedbackModerationPendingId === entry.feedback_id}
                                onClick={() => {
                                  void moderateProviderProvenanceSchedulerSearchFeedbackEntry(entry.feedback_id, "approved");
                                }}
                                type="button"
                              >
                                Approve
                              </button>
                              <button
                                className="ghost-button"
                                disabled={providerProvenanceSchedulerSearchFeedbackModerationPendingId === entry.feedback_id}
                                onClick={() => {
                                  void moderateProviderProvenanceSchedulerSearchFeedbackEntry(entry.feedback_id, "rejected");
                                }}
                                type="button"
                              >
                                Reject
                              </button>
                              <button
                                className="ghost-button"
                                disabled={providerProvenanceSchedulerSearchFeedbackModerationPendingId === entry.feedback_id}
                                onClick={() => {
                                  void moderateProviderProvenanceSchedulerSearchFeedbackEntry(entry.feedback_id, "pending");
                                }}
                                type="button"
                              >
                                Queue
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={4}>
                          <p className="empty-state">
                            No scheduler search feedback matches the current moderation filter.
                          </p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
                <div className="market-data-provenance-history-actions">
                  <button
                    className="ghost-button"
                    disabled={
                      !selectedProviderProvenanceSchedulerSearchFeedbackIds.length
                      || providerProvenanceSchedulerSearchFeedbackModerationPendingId !== null
                    }
                    onClick={() => {
                      void moderateProviderProvenanceSchedulerSearchFeedbackSelection("approved");
                    }}
                    type="button"
                  >
                    Approve selected
                  </button>
                  <button
                    className="ghost-button"
                    disabled={
                      !selectedProviderProvenanceSchedulerSearchFeedbackIds.length
                      || providerProvenanceSchedulerSearchFeedbackModerationPendingId !== null
                    }
                    onClick={() => {
                      void moderateProviderProvenanceSchedulerSearchFeedbackSelection("rejected");
                    }}
                    type="button"
                  >
                    Reject selected
                  </button>
                  <button
                    className="ghost-button"
                    disabled={
                      !selectedProviderProvenanceSchedulerSearchFeedbackIds.length
                      || providerProvenanceSchedulerSearchFeedbackModerationPendingId !== null
                    }
                    onClick={() => {
                      void moderateProviderProvenanceSchedulerSearchFeedbackSelection("pending");
                    }}
                    type="button"
                  >
                    Queue selected
                  </button>
                  <span className="run-lineage-symbol-copy">
                    {selectedProviderProvenanceSchedulerSearchFeedbackIds.length} selected
                  </span>
                </div>
              </>
            ) : null}
    </>
  );
}
