// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerModerationSection({ model }: { model: any }) {
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
          <div className="market-data-provenance-history-head">
            <strong>Scheduler moderation policy catalogs</strong>
            <p>
              Save reusable moderation defaults and route selected feedback through a staged
              approval queue before it changes learned ranking.
            </p>
          </div>
          <div className="market-data-provenance-history-actions">
            <label className="run-form-field">
              <span>Name</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                    ...current,
                    name: event.target.value,
                  }));
                }}
                placeholder="Pending scheduler approvals"
                type="text"
                value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.name}
              />
            </label>
            <label className="run-form-field">
              <span>Description</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                    ...current,
                    description: event.target.value,
                  }));
                }}
                placeholder="Moderate high-signal scheduler feedback before tuning"
                type="text"
                value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.description}
              />
            </label>
            <label className="run-form-field">
              <span>Default outcome</span>
              <select
                value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.default_moderation_status}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                    ...current,
                    default_moderation_status: event.target.value,
                  }));
                }}
              >
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="pending">Pending</option>
              </select>
            </label>
            <label className="run-form-field">
              <span>Governance view</span>
              <select
                value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.governance_view}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                    ...current,
                    governance_view: event.target.value,
                  }));
                }}
              >
                <option value="pending_queue">Pending queue</option>
                <option value="stale_pending">Stale pending</option>
                <option value="high_score_pending">High-score pending</option>
                <option value="conflicting_queries">Conflicting queries</option>
                <option value="all_feedback">All feedback</option>
              </select>
            </label>
            <label className="run-form-field">
              <span>Window</span>
              <select
                value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.window_days}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                    ...current,
                    window_days: Number.parseInt(event.target.value, 10) || 30,
                  }));
                }}
              >
                {[14, 30, 60, 90].map((value) => (
                  <option key={`provider-scheduler-search-policy-window-${value}`} value={value}>
                    {value}d
                  </option>
                ))}
              </select>
            </label>
            <label className="run-form-field">
              <span>Stale pending</span>
              <select
                value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.stale_pending_hours}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                    ...current,
                    stale_pending_hours: Number.parseInt(event.target.value, 10) || 24,
                  }));
                }}
              >
                {[12, 24, 48, 72].map((value) => (
                  <option key={`provider-scheduler-search-policy-stale-${value}`} value={value}>
                    {value}h
                  </option>
                ))}
              </select>
            </label>
            <label className="run-form-field">
              <span>Minimum score</span>
              <input
                min={0}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                    ...current,
                    minimum_score: Math.max(Number.parseInt(event.target.value, 10) || 0, 0),
                  }));
                }}
                type="number"
                value={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.minimum_score}
              />
            </label>
            <label className="run-form-field checkbox-field">
              <span>Require note</span>
              <input
                checked={providerProvenanceSchedulerSearchModerationPolicyCatalogDraft.require_note}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationPolicyCatalogDraft((current) => ({
                    ...current,
                    require_note: event.target.checked,
                  }));
                }}
                type="checkbox"
              />
            </label>
            <button
              className="ghost-button"
              disabled={providerProvenanceSchedulerSearchModerationPolicyCatalogsLoading}
              onClick={() => {
                void createProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry();
              }}
              type="button"
            >
              {editingProviderProvenanceSchedulerSearchModerationPolicyCatalogId ? "Update policy catalog" : "Save policy catalog"}
            </button>
            {editingProviderProvenanceSchedulerSearchModerationPolicyCatalogId ? (
              <button
                className="ghost-button"
                onClick={() => {
                  resetProviderProvenanceSchedulerSearchModerationPolicyCatalogEditor();
                  setProviderProvenanceWorkspaceFeedback("Moderation policy catalog editor reset.");
                }}
                type="button"
              >
                Cancel edit
              </button>
            ) : null}
          </div>
          <div className="market-data-provenance-history-actions">
            <span className="run-lineage-symbol-copy">
              {selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length} selected
            </span>
            <button
              className="ghost-button"
              disabled={
                !selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length
                || providerProvenanceSchedulerSearchModerationPolicyCatalogBulkAction !== null
              }
              onClick={() => {
                void runProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkGovernance("delete");
              }}
              type="button"
            >
              Delete selected
            </button>
            <button
              className="ghost-button"
              disabled={
                !selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length
                || providerProvenanceSchedulerSearchModerationPolicyCatalogBulkAction !== null
              }
              onClick={() => {
                void runProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkGovernance("restore");
              }}
              type="button"
            >
              Restore selected
            </button>
            <button
              className="ghost-button"
              disabled={
                !selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length
                || providerProvenanceSchedulerSearchModerationPolicyCatalogBulkAction !== null
              }
              onClick={() => {
                void runProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkGovernance("update");
              }}
              type="button"
            >
              Bulk edit
            </button>
            <label className="run-form-field">
              <span>Name prefix</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft((current) => ({
                    ...current,
                    name_prefix: event.target.value,
                  }));
                }}
                placeholder="[Ops] "
                type="text"
                value={providerProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft.name_prefix}
              />
            </label>
            <label className="run-form-field">
              <span>Name suffix</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft((current) => ({
                    ...current,
                    name_suffix: event.target.value,
                  }));
                }}
                placeholder=" / reviewed"
                type="text"
                value={providerProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft.name_suffix}
              />
            </label>
            <label className="run-form-field">
              <span>Description append</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft((current) => ({
                    ...current,
                    description_append: event.target.value,
                  }));
                }}
                placeholder="Bulk-governed in control room"
                type="text"
                value={providerProvenanceSchedulerSearchModerationPolicyCatalogBulkDraft.description_append}
              />
            </label>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>
                  <input
                    aria-label="Select all moderation policy catalogs"
                    checked={
                      (providerProvenanceSchedulerSearchModerationPolicyCatalogs?.items.length ?? 0) > 0
                      && selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length
                        === (providerProvenanceSchedulerSearchModerationPolicyCatalogs?.items.length ?? 0)
                    }
                    onChange={toggleAllProviderProvenanceSchedulerSearchModerationPolicyCatalogSelections}
                    type="checkbox"
                  />
                </th>
                <th>Catalog</th>
                <th>Defaults</th>
                <th>Governance</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {providerProvenanceSchedulerSearchModerationPolicyCatalogs?.items.length ? (
                providerProvenanceSchedulerSearchModerationPolicyCatalogs.items.map((entry) => (
                  <tr key={`provider-scheduler-search-policy-catalog-${entry.catalog_id}`}>
                    <td className="provider-provenance-selection-cell">
                      <input
                        aria-label={`Select moderation policy catalog ${entry.name}`}
                        checked={selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.includes(entry.catalog_id)}
                        onChange={() => {
                          toggleProviderProvenanceSchedulerSearchModerationPolicyCatalogSelection(entry.catalog_id);
                        }}
                        type="checkbox"
                      />
                    </td>
                    <td>
                      <strong>{entry.name}</strong>
                      <p className="run-lineage-symbol-copy">
                        {entry.description || "No description"}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        {shortenIdentifier(entry.catalog_id, 10)} · created {formatTimestamp(entry.created_at)}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        {formatWorkflowToken(entry.status)} · {entry.revision_count} revision(s)
                        {entry.deleted_at ? ` · deleted ${formatTimestamp(entry.deleted_at)}` : ""}
                      </p>
                    </td>
                    <td>
                      <p className="run-lineage-symbol-copy">
                        Outcome {formatWorkflowToken(entry.default_moderation_status)}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        Minimum score {entry.minimum_score} · note {entry.require_note ? "required" : "optional"}
                      </p>
                    </td>
                    <td>
                      <p className="run-lineage-symbol-copy">
                        View {formatWorkflowToken(entry.governance_view)}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        Window {entry.window_days}d · stale {entry.stale_pending_hours}h
                      </p>
                    </td>
                    <td>
                      <div className="market-data-provenance-history-actions">
                        <button
                          className="ghost-button"
                          disabled={entry.status !== "active"}
                          onClick={() => {
                            void editProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry(entry);
                          }}
                          type="button"
                        >
                          Edit
                        </button>
                        <button
                          className="ghost-button"
                          disabled={entry.status !== "active"}
                          onClick={() => {
                            void deleteProviderProvenanceSchedulerSearchModerationPolicyCatalogEntry(entry);
                          }}
                          type="button"
                        >
                          Delete
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => {
                            if (
                              selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogId === entry.catalog_id
                              && selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory
                            ) {
                              setSelectedProviderProvenanceSchedulerSearchModerationPolicyCatalogId(null);
                              setSelectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory(null);
                              setProviderProvenanceSchedulerSearchModerationPolicyCatalogHistoryError(null);
                            } else {
                              void loadProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory(entry.catalog_id);
                            }
                          }}
                          type="button"
                        >
                          {selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogId === entry.catalog_id
                            && selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory
                            ? "Hide versions"
                            : "Versions"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5}>
                    <p className="empty-state">
                      No scheduler moderation policy catalogs saved yet.
                    </p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          {selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogId ? (
            <div className="market-data-provenance-shared-history">
              <div className="market-data-provenance-history-head">
                <strong>Scheduler moderation policy catalog revisions</strong>
                <p>Inspect immutable catalog snapshots and restore a previous moderation governance revision.</p>
              </div>
              {providerProvenanceSchedulerSearchModerationPolicyCatalogHistoryLoading ? (
                <p className="empty-state">Loading moderation policy catalog revisions…</p>
              ) : null}
              {providerProvenanceSchedulerSearchModerationPolicyCatalogHistoryError ? (
                <p className="market-data-workflow-feedback">
                  Moderation policy catalog revisions failed: {providerProvenanceSchedulerSearchModerationPolicyCatalogHistoryError}
                </p>
              ) : null}
              {selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory ? (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>When</th>
                      <th>Snapshot</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogHistory.history.map((entry) => (
                      <tr key={entry.revision_id}>
                        <td>
                          <strong>{formatTimestamp(entry.recorded_at)}</strong>
                          <p className="run-lineage-symbol-copy">
                            {entry.recorded_by_tab_label ?? entry.recorded_by_tab_id ?? "unknown tab"}
                          </p>
                        </td>
                        <td>
                          <strong>{formatWorkflowToken(entry.action)} · {formatWorkflowToken(entry.status)}</strong>
                          <p className="run-lineage-symbol-copy">{entry.name}</p>
                          <p className="run-lineage-symbol-copy">
                            Outcome {formatWorkflowToken(entry.default_moderation_status)} · view {formatWorkflowToken(entry.governance_view)}
                          </p>
                          <p className="run-lineage-symbol-copy">
                            Window {entry.window_days}d · stale {entry.stale_pending_hours}h · minimum {entry.minimum_score}
                          </p>
                          <p className="run-lineage-symbol-copy">{entry.reason}</p>
                        </td>
                        <td>
                          <button
                            className="ghost-button"
                            onClick={() => {
                              void restoreProviderProvenanceSchedulerSearchModerationPolicyCatalogHistoryRevision(entry.revision_id);
                            }}
                            type="button"
                          >
                            Restore revision
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : null}
            </div>
          ) : null}
          <div className="market-data-provenance-shared-history">
            <div className="market-data-provenance-history-head">
              <strong>Scheduler moderation policy catalog team audit</strong>
              <p>Filter lifecycle and bulk-governance events by catalog, action, actor, or search text.</p>
            </div>
            <div className="filter-bar">
              <label>
                <span>Catalog</span>
                <select
                  onChange={(event) =>
                    setProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter((current) => ({
                      ...current,
                      catalog_id: event.target.value,
                    }))
                  }
                  value={providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter.catalog_id}
                >
                  <option value="">All catalogs</option>
                  {(providerProvenanceSchedulerSearchModerationPolicyCatalogs?.items ?? []).map((entry) => (
                    <option key={entry.catalog_id} value={entry.catalog_id}>
                      {entry.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span>Action</span>
                <select
                  onChange={(event) =>
                    setProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter((current) => ({
                      ...current,
                      action: event.target.value,
                    }))
                  }
                  value={providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter.action}
                >
                  <option value={ALL_FILTER_VALUE}>All actions</option>
                  <option value="created">Created</option>
                  <option value="updated">Updated</option>
                  <option value="deleted">Deleted</option>
                  <option value="restored">Restored</option>
                  <option value="bulk_updated">Bulk updated</option>
                  <option value="bulk_deleted">Bulk deleted</option>
                  <option value="bulk_restored">Bulk restored</option>
                </select>
              </label>
              <label>
                <span>Actor tab</span>
                <input
                  onChange={(event) =>
                    setProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter((current) => ({
                      ...current,
                      actor_tab_id: event.target.value,
                    }))
                  }
                  placeholder="control-room"
                  type="text"
                  value={providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter.actor_tab_id}
                />
              </label>
              <label>
                <span>Search</span>
                <input
                  onChange={(event) =>
                    setProviderProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter((current) => ({
                      ...current,
                      search: event.target.value,
                    }))
                  }
                  placeholder="high-score pending"
                  type="text"
                  value={providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter.search}
                />
              </label>
            </div>
            {providerProvenanceSchedulerSearchModerationPolicyCatalogAuditsLoading ? (
              <p className="empty-state">Loading scheduler moderation policy catalog audit…</p>
            ) : null}
            {providerProvenanceSchedulerSearchModerationPolicyCatalogAuditsError ? (
              <p className="market-data-workflow-feedback">
                Scheduler moderation policy catalog audit failed: {providerProvenanceSchedulerSearchModerationPolicyCatalogAuditsError}
              </p>
            ) : null}
            {providerProvenanceSchedulerSearchModerationPolicyCatalogAudits.length ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>When</th>
                    <th>Action</th>
                    <th>Detail</th>
                  </tr>
                </thead>
                <tbody>
                  {providerProvenanceSchedulerSearchModerationPolicyCatalogAudits.map((entry) => (
                    <tr key={entry.audit_id}>
                      <td>
                        <strong>{formatTimestamp(entry.recorded_at)}</strong>
                        <p className="run-lineage-symbol-copy">
                          {entry.actor_tab_label ?? entry.actor_tab_id ?? "unknown tab"}
                        </p>
                      </td>
                      <td>
                        <strong>{formatWorkflowToken(entry.action)}</strong>
                        <p className="run-lineage-symbol-copy">{entry.name}</p>
                        <p className="run-lineage-symbol-copy">
                          {formatWorkflowToken(entry.status)} · {formatWorkflowToken(entry.default_moderation_status)}
                        </p>
                      </td>
                      <td>
                        <p className="run-lineage-symbol-copy">{entry.detail}</p>
                        <p className="run-lineage-symbol-copy">
                          View {formatWorkflowToken(entry.governance_view)} · window {entry.window_days}d · stale {entry.stale_pending_hours}h · minimum {entry.minimum_score}
                        </p>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              !providerProvenanceSchedulerSearchModerationPolicyCatalogAuditsLoading ? (
                <p className="empty-state">No moderation policy catalog audit rows match the current filter.</p>
              ) : null
            )}
          </div>
          <div className="market-data-provenance-history-head">
            <strong>Moderation catalog governance policies</strong>
            <p>
              Save reusable approval requirements and update defaults, then stage
              selected moderation policy catalogs through a dedicated governance queue.
            </p>
          </div>
          <div className="market-data-provenance-history-actions">
            <label className="run-form-field">
              <span>Name</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                    ...current,
                    name: event.target.value,
                  }));
                }}
                placeholder="Catalog cleanup with approval"
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.name}
              />
            </label>
            <label className="run-form-field">
              <span>Action scope</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.action_scope}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                    ...current,
                    action_scope: event.target.value,
                  }));
                }}
              >
                <option value="any">Any action</option>
                <option value="update">Update only</option>
                <option value="delete">Delete only</option>
                <option value="restore">Restore only</option>
              </select>
            </label>
            <label className="run-form-field checkbox-field">
              <span>Require approval note</span>
              <input
                checked={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.require_approval_note}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                    ...current,
                    require_approval_note: event.target.checked,
                  }));
                }}
                type="checkbox"
              />
            </label>
            <label className="run-form-field">
              <span>Description</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                    ...current,
                    description: event.target.value,
                  }));
                }}
                placeholder="Stage policy-catalog changes behind explicit approval."
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.description}
              />
            </label>
            <label className="run-form-field">
              <span>Guidance</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                    ...current,
                    guidance: event.target.value,
                  }));
                }}
                placeholder="Require note before catalog lifecycle changes."
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.guidance}
              />
            </label>
            <label className="run-form-field">
              <span>Name prefix</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                    ...current,
                    name_prefix: event.target.value,
                  }));
                }}
                placeholder="[Ops] "
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.name_prefix}
              />
            </label>
            <label className="run-form-field">
              <span>Name suffix</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                    ...current,
                    name_suffix: event.target.value,
                  }));
                }}
                placeholder=" / reviewed"
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.name_suffix}
              />
            </label>
            <label className="run-form-field">
              <span>Description append</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                    ...current,
                    description_append: event.target.value,
                  }));
                }}
                placeholder=" Escalate stale pending rows before applying."
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.description_append}
              />
            </label>
            <label className="run-form-field">
              <span>Default outcome</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.default_moderation_status}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                    ...current,
                    default_moderation_status: event.target.value,
                  }));
                }}
              >
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="pending">Pending</option>
              </select>
            </label>
            <label className="run-form-field">
              <span>Governance view</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.governance_view}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                    ...current,
                    governance_view: event.target.value,
                  }));
                }}
              >
                <option value="pending_queue">Pending queue</option>
                <option value="stale_pending">Stale pending</option>
                <option value="high_score_pending">High-score pending</option>
                <option value="conflicting_queries">Conflicting queries</option>
                <option value="all_feedback">All feedback</option>
              </select>
            </label>
            <label className="run-form-field">
              <span>Window</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.window_days}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                    ...current,
                    window_days: Number.parseInt(event.target.value, 10) || 30,
                  }));
                }}
              >
                {[14, 30, 60, 90].map((value) => (
                  <option key={`provider-scheduler-search-governance-policy-window-${value}`} value={value}>
                    {value}d
                  </option>
                ))}
              </select>
            </label>
            <label className="run-form-field">
              <span>Stale pending</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.stale_pending_hours}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                    ...current,
                    stale_pending_hours: Number.parseInt(event.target.value, 10) || 24,
                  }));
                }}
              >
                {[12, 24, 48, 72].map((value) => (
                  <option key={`provider-scheduler-search-governance-policy-stale-${value}`} value={value}>
                    {value}h
                  </option>
                ))}
              </select>
            </label>
            <label className="run-form-field">
              <span>Minimum score</span>
              <input
                min={0}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                    ...current,
                    minimum_score: Math.max(Number.parseInt(event.target.value, 10) || 0, 0),
                  }));
                }}
                type="number"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.minimum_score}
              />
            </label>
            <label className="run-form-field checkbox-field">
              <span>Require moderation note</span>
              <input
                checked={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft.require_note}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyDraft((current) => ({
                    ...current,
                    require_note: event.target.checked,
                  }));
                }}
                type="checkbox"
              />
            </label>
            <button
              className="ghost-button"
              disabled={providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesLoading}
              onClick={() => {
                void createProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry();
              }}
              type="button"
            >
              {editingProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId ? "Update governance policy" : "Save governance policy"}
            </button>
            {editingProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId ? (
              <button
                className="ghost-button"
                onClick={() => {
                  resetProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEditor();
                  setProviderProvenanceWorkspaceFeedback("Moderation governance policy editor reset.");
                }}
                type="button"
              >
                Cancel edit
              </button>
            ) : null}
          </div>
          <div className="market-data-provenance-history-actions">
            <span className="run-lineage-symbol-copy">
              {selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length} selected
            </span>
            <button
              className="ghost-button"
              disabled={
                !selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length
                || providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkAction !== null
              }
              onClick={() => {
                void runProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkGovernance("delete");
              }}
              type="button"
            >
              Delete selected
            </button>
            <button
              className="ghost-button"
              disabled={
                !selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length
                || providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkAction !== null
              }
              onClick={() => {
                void runProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkGovernance("restore");
              }}
              type="button"
            >
              Restore selected
            </button>
            <button
              className="ghost-button"
              disabled={
                !selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length
                || providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkAction !== null
              }
              onClick={() => {
                void runProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkGovernance("update");
              }}
              type="button"
            >
              Bulk edit
            </button>
            <label className="run-form-field">
              <span>Name prefix</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft((current) => ({
                    ...current,
                    name_prefix: event.target.value,
                  }));
                }}
                placeholder="[Ops] "
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft.name_prefix}
              />
            </label>
            <label className="run-form-field">
              <span>Name suffix</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft((current) => ({
                    ...current,
                    name_suffix: event.target.value,
                  }));
                }}
                placeholder=" / reviewed"
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft.name_suffix}
              />
            </label>
            <label className="run-form-field">
              <span>Guidance</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft((current) => ({
                    ...current,
                    guidance: event.target.value,
                  }));
                }}
                placeholder="Require explicit review before apply."
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyBulkDraft.guidance}
              />
            </label>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>
                  <input
                    aria-label="Select all moderation governance policies"
                    checked={
                      (providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies?.items.length ?? 0) > 0
                      && selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length
                        === (providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies?.items.length ?? 0)
                    }
                    onChange={toggleAllProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicySelections}
                    type="checkbox"
                  />
                </th>
                <th>Policy</th>
                <th>Defaults</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies?.items.length ? (
                providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies.items.map((entry) => (
                  <tr key={`provider-scheduler-search-moderation-governance-policy-${entry.governance_policy_id}`}>
                    <td className="provider-provenance-selection-cell">
                      <input
                        aria-label={`Select moderation governance policy ${entry.name}`}
                        checked={selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.includes(entry.governance_policy_id)}
                        onChange={() => {
                          toggleProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicySelection(entry.governance_policy_id);
                        }}
                        type="checkbox"
                      />
                    </td>
                    <td>
                      <strong>{entry.name}</strong>
                      <p className="run-lineage-symbol-copy">
                        {formatWorkflowToken(entry.action_scope)} · approval note {entry.require_approval_note ? "required" : "optional"}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        {entry.guidance || entry.description || "No governance guidance"}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        {formatWorkflowToken(entry.status)} · {entry.revision_count} revision(s)
                        {entry.deleted_at ? ` · deleted ${formatTimestamp(entry.deleted_at)}` : ""}
                      </p>
                    </td>
                    <td>
                      <p className="run-lineage-symbol-copy">
                        {entry.name_prefix || entry.name_suffix
                          ? `name ${entry.name_prefix ?? ""}…${entry.name_suffix ?? ""}`
                          : "No name affixes"}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        Outcome {formatWorkflowToken(entry.default_moderation_status)} · view {formatWorkflowToken(entry.governance_view)}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        Window {entry.window_days}d · stale {entry.stale_pending_hours}h · minimum {entry.minimum_score}
                      </p>
                    </td>
                    <td>
                      <div className="market-data-provenance-history-actions">
                        <button
                          className="ghost-button"
                          disabled={entry.status !== "active"}
                          onClick={() => {
                            void editProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry(entry);
                          }}
                          type="button"
                        >
                          Edit
                        </button>
                        <button
                          className="ghost-button"
                          disabled={entry.status !== "active"}
                          onClick={() => {
                            void deleteProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyEntry(entry);
                          }}
                          type="button"
                        >
                          Delete
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => {
                            if (
                              selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId === entry.governance_policy_id
                              && selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory
                            ) {
                              setSelectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId(null);
                              setSelectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory(null);
                              setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryError(null);
                            } else {
                              void loadProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory(entry.governance_policy_id);
                            }
                          }}
                          type="button"
                        >
                          {selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId === entry.governance_policy_id
                            && selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory
                            ? "Hide versions"
                            : "Versions"}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => {
                            setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft((current) => ({
                              ...current,
                              governance_policy_id: entry.governance_policy_id,
                              action:
                                entry.action_scope === "update"
                                || entry.action_scope === "delete"
                                || entry.action_scope === "restore"
                                  ? entry.action_scope
                                  : current.action,
                            }));
                            setProviderProvenanceWorkspaceFeedback(
                              `Selected moderation catalog governance policy ${entry.name}.`,
                            );
                          }}
                          type="button"
                        >
                          Use policy
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4}>
                    <p className="empty-state">No moderation catalog governance policies saved yet.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          {selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyId ? (
            <div className="market-data-provenance-shared-history">
              <div className="market-data-provenance-history-head">
                <strong>Moderation governance policy revisions</strong>
                <p>Inspect immutable policy snapshots and restore a previous governance default set.</p>
              </div>
              {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryLoading ? (
                <p className="empty-state">Loading moderation governance policy revisions…</p>
              ) : null}
              {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryError ? (
                <p className="market-data-workflow-feedback">
                  Moderation governance policy revisions failed: {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryError}
                </p>
              ) : null}
              {selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory ? (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>When</th>
                      <th>Snapshot</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistory.history.map((entry) => (
                      <tr key={entry.revision_id}>
                        <td>
                          <strong>{formatTimestamp(entry.recorded_at)}</strong>
                          <p className="run-lineage-symbol-copy">
                            {entry.recorded_by_tab_label ?? entry.recorded_by_tab_id ?? "unknown tab"}
                          </p>
                        </td>
                        <td>
                          <strong>{formatWorkflowToken(entry.action)} · {formatWorkflowToken(entry.status)}</strong>
                          <p className="run-lineage-symbol-copy">{entry.name}</p>
                          <p className="run-lineage-symbol-copy">
                            {formatWorkflowToken(entry.action_scope)} · approval note {entry.require_approval_note ? "required" : "optional"}
                          </p>
                          <p className="run-lineage-symbol-copy">
                            Outcome {formatWorkflowToken(entry.default_moderation_status)} · view {formatWorkflowToken(entry.governance_view)}
                          </p>
                          <p className="run-lineage-symbol-copy">{entry.reason}</p>
                        </td>
                        <td>
                          <button
                            className="ghost-button"
                            onClick={() => {
                              void restoreProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryRevision(entry.revision_id);
                            }}
                            type="button"
                          >
                            Restore revision
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : null}
            </div>
          ) : null}
          <div className="market-data-provenance-shared-history">
            <div className="market-data-provenance-history-head">
              <strong>Moderation governance policy team audit</strong>
              <p>Filter lifecycle and bulk governance events by policy, action, actor, or search text.</p>
            </div>
            <div className="filter-bar">
              <label>
                <span>Policy</span>
                <select
                  onChange={(event) =>
                    setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter((current) => ({
                      ...current,
                      governance_policy_id: event.target.value,
                    }))
                  }
                  value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter.governance_policy_id}
                >
                  <option value="">All policies</option>
                  {(providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies?.items ?? []).map((entry) => (
                    <option key={entry.governance_policy_id} value={entry.governance_policy_id}>
                      {entry.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span>Action</span>
                <select
                  onChange={(event) =>
                    setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter((current) => ({
                      ...current,
                      action: event.target.value,
                    }))
                  }
                  value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter.action}
                >
                  <option value={ALL_FILTER_VALUE}>All actions</option>
                  <option value="created">Created</option>
                  <option value="updated">Updated</option>
                  <option value="deleted">Deleted</option>
                  <option value="restored">Restored</option>
                  <option value="bulk_updated">Bulk updated</option>
                  <option value="bulk_deleted">Bulk deleted</option>
                  <option value="bulk_restored">Bulk restored</option>
                </select>
              </label>
              <label>
                <span>Actor tab</span>
                <input
                  onChange={(event) =>
                    setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter((current) => ({
                      ...current,
                      actor_tab_id: event.target.value,
                    }))
                  }
                  placeholder="control-room"
                  type="text"
                  value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter.actor_tab_id}
                />
              </label>
              <label>
                <span>Search</span>
                <input
                  onChange={(event) =>
                    setProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter((current) => ({
                      ...current,
                      search: event.target.value,
                    }))
                  }
                  placeholder="approval note"
                  type="text"
                  value={providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter.search}
                />
              </label>
            </div>
            {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditsLoading ? (
              <p className="empty-state">Loading moderation governance policy audit…</p>
            ) : null}
            {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditsError ? (
              <p className="market-data-workflow-feedback">
                Moderation governance policy audit failed: {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditsError}
              </p>
            ) : null}
            {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAudits.length ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>When</th>
                    <th>Action</th>
                    <th>Detail</th>
                  </tr>
                </thead>
                <tbody>
                  {providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAudits.map((entry) => (
                    <tr key={entry.audit_id}>
                      <td>
                        <strong>{formatTimestamp(entry.recorded_at)}</strong>
                        <p className="run-lineage-symbol-copy">
                          {entry.actor_tab_label ?? entry.actor_tab_id ?? "unknown tab"}
                        </p>
                      </td>
                      <td>
                        <strong>{formatWorkflowToken(entry.action)}</strong>
                        <p className="run-lineage-symbol-copy">{entry.name}</p>
                        <p className="run-lineage-symbol-copy">
                          {formatWorkflowToken(entry.status)} · {formatWorkflowToken(entry.action_scope)}
                        </p>
                      </td>
                      <td>
                        <p className="run-lineage-symbol-copy">{entry.detail}</p>
                        <p className="run-lineage-symbol-copy">
                          View {formatWorkflowToken(entry.governance_view)} · window {entry.window_days}d · stale {entry.stale_pending_hours}h · minimum {entry.minimum_score}
                        </p>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              !providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditsLoading ? (
                <p className="empty-state">No moderation governance policy audit rows match the current filter.</p>
              ) : null
            )}
          </div>
          <div className="market-data-provenance-history-head">
            <strong>Moderation governance meta-policies</strong>
            <p>
              Save reusable review defaults for moderation governance policies, then
              stage selected policy updates through a dedicated approval queue.
            </p>
          </div>
          <div className="market-data-provenance-history-actions">
            <label className="run-form-field">
              <span>Name</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    name: event.target.value,
                  }));
                }}
                placeholder="Review moderation governance defaults"
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.name}
              />
            </label>
            <label className="run-form-field">
              <span>Queue action</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.action_scope}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    action_scope: event.target.value,
                  }));
                }}
              >
                <option value="any">Any action</option>
                <option value="update">Update only</option>
                <option value="delete">Delete only</option>
                <option value="restore">Restore only</option>
              </select>
            </label>
            <label className="run-form-field">
              <span>Policy action</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.policy_action_scope}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    policy_action_scope: event.target.value,
                  }));
                }}
              >
                <option value="any">Any action</option>
                <option value="update">Update only</option>
                <option value="delete">Delete only</option>
                <option value="restore">Restore only</option>
              </select>
            </label>
            <label className="run-form-field checkbox-field">
              <span>Approval note</span>
              <input
                checked={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.require_approval_note}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    require_approval_note: event.target.checked,
                  }));
                }}
                type="checkbox"
              />
            </label>
            <label className="run-form-field checkbox-field">
              <span>Policy note</span>
              <input
                checked={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.policy_require_approval_note}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    policy_require_approval_note: event.target.checked,
                  }));
                }}
                type="checkbox"
              />
            </label>
            <label className="run-form-field">
              <span>Description</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    description: event.target.value,
                  }));
                }}
                placeholder="Reusable defaults for moderation governance policy review."
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.description}
              />
            </label>
            <label className="run-form-field">
              <span>Queue guidance</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    guidance: event.target.value,
                  }));
                }}
                placeholder="Require an explicit note before approval."
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.guidance}
              />
            </label>
            <label className="run-form-field">
              <span>Policy guidance</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    policy_guidance: event.target.value,
                  }));
                }}
                placeholder="Apply these defaults to selected governance policies."
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.policy_guidance}
              />
            </label>
            <label className="run-form-field">
              <span>Name prefix</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    name_prefix: event.target.value,
                  }));
                }}
                placeholder="[Reviewed] "
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.name_prefix}
              />
            </label>
            <label className="run-form-field">
              <span>Name suffix</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    name_suffix: event.target.value,
                  }));
                }}
                placeholder=" / approved"
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.name_suffix}
              />
            </label>
            <label className="run-form-field">
              <span>Description append</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    description_append: event.target.value,
                  }));
                }}
                placeholder=" Reviewed in moderation governance queue."
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.description_append}
              />
            </label>
            <label className="run-form-field">
              <span>Outcome</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.default_moderation_status}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    default_moderation_status: event.target.value,
                  }));
                }}
              >
                <option value="approved">Approved</option>
                <option value="pending">Pending</option>
                <option value="rejected">Rejected</option>
              </select>
            </label>
            <label className="run-form-field">
              <span>Governance view</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.governance_view}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    governance_view: event.target.value,
                  }));
                }}
              >
                <option value="all_feedback">All feedback</option>
                <option value="pending_queue">Pending queue</option>
                <option value="high_score_pending">High-score pending</option>
              </select>
            </label>
            <label className="run-form-field">
              <span>Window days</span>
              <input
                min={7}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    window_days: Number(event.target.value) || 0,
                  }));
                }}
                type="number"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.window_days}
              />
            </label>
            <label className="run-form-field">
              <span>Stale pending hours</span>
              <input
                min={1}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    stale_pending_hours: Number(event.target.value) || 0,
                  }));
                }}
                type="number"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.stale_pending_hours}
              />
            </label>
            <label className="run-form-field">
              <span>Minimum score</span>
              <input
                min={0}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    minimum_score: Number(event.target.value) || 0,
                  }));
                }}
                type="number"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.minimum_score}
              />
            </label>
            <label className="run-form-field checkbox-field">
              <span>Require moderator note</span>
              <input
                checked={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft.require_note}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDraft((current) => ({
                    ...current,
                    require_note: event.target.checked,
                  }));
                }}
                type="checkbox"
              />
            </label>
            <button
              className="ghost-button"
              disabled={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPoliciesLoading}
              onClick={() => {
                void createProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyEntry();
              }}
              type="button"
            >
              Save meta-policy
            </button>
          </div>
          {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPoliciesError ? (
            <p className="market-data-workflow-feedback">
              Moderation governance meta-policies failed: {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPoliciesError}
            </p>
          ) : null}
          <table className="data-table">
            <thead>
              <tr>
                <th>Meta-policy</th>
                <th>Defaults</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies?.items.length ? (
                providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies.items.map((entry) => (
                  <tr key={`provider-scheduler-search-moderation-governance-meta-policy-${entry.meta_policy_id}`}>
                    <td>
                      <strong>{entry.name}</strong>
                      <p className="run-lineage-symbol-copy">
                        Queue {formatWorkflowToken(entry.action_scope)} · note {entry.require_approval_note ? "required" : "optional"}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        {entry.guidance || entry.description || "No meta-governance guidance"}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        Saved {formatTimestamp(entry.updated_at)} · {entry.created_by_tab_label ?? entry.created_by_tab_id ?? "unknown tab"}
                      </p>
                    </td>
                    <td>
                      <p className="run-lineage-symbol-copy">
                        Policy {formatWorkflowToken(entry.policy_action_scope ?? "any")} · note {entry.policy_require_approval_note ? "required" : "optional"}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        Outcome {formatWorkflowToken(entry.default_moderation_status ?? "approved")} · view {formatWorkflowToken(entry.governance_view ?? "pending_queue")}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        Window {entry.window_days ?? 0}d · stale {entry.stale_pending_hours ?? 0}h · minimum {entry.minimum_score ?? 0}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        {entry.name_prefix || entry.name_suffix
                          ? `name ${entry.name_prefix ?? ""}…${entry.name_suffix ?? ""}`
                          : "No name affixes"}
                      </p>
                    </td>
                    <td>
                      <div className="market-data-provenance-history-actions">
                        <button
                          className="ghost-button"
                          onClick={() => {
                            applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyDefaults(entry);
                          }}
                          type="button"
                        >
                          Use defaults
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={3}>
                    <p className="empty-state">No moderation governance meta-policies saved yet.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          <div className="market-data-provenance-history-head">
            <strong>Moderation governance approval queue</strong>
            <p>
              Stage selected moderation governance policies, preview the exact policy diffs,
              then approve and apply the change set.
            </p>
          </div>
          <div className="market-data-provenance-history-actions">
            <label className="run-form-field">
              <span>Action</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft.action}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft((current) => ({
                    ...current,
                    action: event.target.value,
                  }));
                }}
              >
                <option value="update">Update</option>
                <option value="delete">Delete</option>
                <option value="restore">Restore</option>
              </select>
            </label>
            <label className="run-form-field">
              <span>Reusable meta-policy</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft.meta_policy_id}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft((current) => ({
                    ...current,
                    meta_policy_id: event.target.value,
                  }));
                }}
              >
                <option value={ALL_FILTER_VALUE}>Inline policy patch</option>
                {(providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicies?.items ?? []).map((entry) => (
                  <option key={`provider-scheduler-search-moderation-governance-meta-policy-option-${entry.meta_policy_id}`} value={entry.meta_policy_id}>
                    {entry.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="run-form-field">
              <span>Approval/apply note</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft((current) => ({
                    ...current,
                    note: event.target.value,
                  }));
                }}
                placeholder="required when the meta-policy gates approval on notes"
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaStageDraft.note}
              />
            </label>
            <button
              className="ghost-button"
              disabled={
                !selectedProviderProvenanceSchedulerSearchModerationCatalogGovernancePolicyIds.length
                || providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPendingId !== null
              }
              onClick={() => {
                void stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaSelection();
              }}
              type="button"
            >
              Stage selected policies
            </button>
            <label className="run-form-field">
              <span>Queue state</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter.queue_state}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter((current) => ({
                    ...current,
                    queue_state: event.target.value,
                  }));
                }}
              >
                <option value={ALL_FILTER_VALUE}>All states</option>
                <option value="pending_approval">Pending approval</option>
                <option value="ready_to_apply">Ready to apply</option>
                <option value="completed">Completed</option>
              </select>
            </label>
            <label className="run-form-field">
              <span>Meta-policy</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter.meta_policy_id}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter((current) => ({
                    ...current,
                    meta_policy_id: event.target.value,
                  }));
                }}
              >
                <option value={ALL_FILTER_VALUE}>All meta-policies</option>
                {(providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.available_filters.meta_policies ?? []).map((entry) => (
                  <option key={`provider-scheduler-search-moderation-governance-meta-plan-policy-${entry.meta_policy_id}`} value={entry.meta_policy_id}>
                    {entry.name}
                  </option>
                ))}
              </select>
            </label>
            <span className="run-lineage-symbol-copy">
              {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.summary.pending_approval_count ?? 0} pending · {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.summary.ready_to_apply_count ?? 0} ready · {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.summary.completed_count ?? 0} completed
            </span>
          </div>
          {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlansError ? (
            <p className="market-data-workflow-feedback">
              Moderation governance approval queue failed: {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlansError}
            </p>
          ) : null}
          <table className="data-table">
            <thead>
              <tr>
                <th>Plan</th>
                <th>Preview</th>
                <th>Queue</th>
              </tr>
            </thead>
            <tbody>
              {providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans?.items.length ? (
                providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlans.items.map((entry) => (
                  <tr key={`provider-scheduler-search-moderation-governance-meta-plan-${entry.plan_id}`}>
                    <td>
                      <strong>{shortenIdentifier(entry.plan_id, 10)}</strong>
                      <p className="run-lineage-symbol-copy">
                        {formatWorkflowToken(entry.action)} · {entry.meta_policy_name ?? "Inline defaults"}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        Created {formatTimestamp(entry.created_at)} · by {entry.created_by}
                      </p>
                      {entry.guidance ? (
                        <p className="run-lineage-symbol-copy">{entry.guidance}</p>
                      ) : null}
                    </td>
                    <td>
                      <strong>{entry.preview_count} preview item(s)</strong>
                      {entry.preview_items.slice(0, 4).map((preview) => (
                        <div key={`provider-scheduler-search-moderation-governance-meta-preview-${entry.plan_id}-${preview.governance_policy_id}`}>
                          <p className="run-lineage-symbol-copy">
                            {preview.governance_policy_name} · {formatWorkflowToken(preview.outcome)}
                            {preview.changed_fields.length ? ` · ${preview.changed_fields.join(" · ")}` : ""}
                            {preview.message ? ` · ${preview.message}` : ""}
                          </p>
                          {Object.entries(preview.field_diffs).slice(0, 2).map(([field, diff]) => (
                            <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-moderation-governance-meta-diff-${entry.plan_id}-${preview.governance_policy_id}-${field}`}>
                              {field}: {formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue(diff.before)} → {formatProviderProvenanceSchedulerNarrativeGovernanceDiffValue(diff.after)}
                            </p>
                          ))}
                        </div>
                      ))}
                    </td>
                    <td>
                      <strong>{formatWorkflowToken(entry.queue_state)}</strong>
                      <p className="run-lineage-symbol-copy">
                        Approved {formatTimestamp(entry.approved_at ?? null)} · by {entry.approved_by ?? "n/a"}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        Applied {formatTimestamp(entry.applied_at ?? null)} · by {entry.applied_by ?? "n/a"}
                      </p>
                      <div className="market-data-provenance-history-actions">
                        <button
                          className="ghost-button"
                          disabled={
                            entry.queue_state !== "pending_approval"
                            || providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPendingId === entry.plan_id
                          }
                          onClick={() => {
                            void approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry(entry.plan_id);
                          }}
                          type="button"
                        >
                          Approve
                        </button>
                        <button
                          className="ghost-button"
                          disabled={
                            entry.queue_state !== "ready_to_apply"
                            || providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanPendingId === entry.plan_id
                          }
                          onClick={() => {
                            void applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanEntry(entry.plan_id);
                          }}
                          type="button"
                        >
                          Apply
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={3}>
                    <p className="empty-state">No moderation governance meta-plans match the current filter.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          <div className="market-data-provenance-history-head">
            <strong>Moderation catalog governance queue</strong>
            <p>
              Stage selected moderation policy catalogs, preview the exact catalog diffs,
              then approve and apply the change set.
            </p>
          </div>
          <div className="market-data-provenance-history-actions">
            <label className="run-form-field">
              <span>Action</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft.action}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft((current) => ({
                    ...current,
                    action: event.target.value,
                  }));
                }}
              >
                <option value="update">Update</option>
                <option value="delete">Delete</option>
                <option value="restore">Restore</option>
              </select>
            </label>
            <label className="run-form-field">
              <span>Governance policy</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft.governance_policy_id}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft((current) => ({
                    ...current,
                    governance_policy_id: event.target.value,
                  }));
                }}
              >
                <option value={ALL_FILTER_VALUE}>No reusable policy</option>
                {(providerProvenanceSchedulerSearchModerationCatalogGovernancePolicies?.items ?? []).map((entry) => (
                  <option key={`provider-scheduler-search-moderation-governance-policy-option-${entry.governance_policy_id}`} value={entry.governance_policy_id}>
                    {entry.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="run-form-field">
              <span>Approval/apply note</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft((current) => ({
                    ...current,
                    note: event.target.value,
                  }));
                }}
                placeholder="required when the governance policy gates approval on notes"
                type="text"
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceStageDraft.note}
              />
            </label>
            <button
              className="ghost-button"
              disabled={
                !selectedProviderProvenanceSchedulerSearchModerationPolicyCatalogIds.length
                || providerProvenanceSchedulerSearchModerationCatalogGovernancePlanPendingId !== null
              }
              onClick={() => {
                void stageProviderProvenanceSchedulerSearchModerationCatalogGovernanceSelection();
              }}
              type="button"
            >
              Stage selected catalogs
            </button>
            <label className="run-form-field">
              <span>Queue state</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter.queue_state}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter((current) => ({
                    ...current,
                    queue_state: event.target.value,
                  }));
                }}
              >
                <option value={ALL_FILTER_VALUE}>All states</option>
                <option value="pending_approval">Pending approval</option>
                <option value="ready_to_apply">Ready to apply</option>
                <option value="completed">Completed</option>
              </select>
            </label>
            <label className="run-form-field">
              <span>Governance policy</span>
              <select
                value={providerProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter.governance_policy_id}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter((current) => ({
                    ...current,
                    governance_policy_id: event.target.value,
                  }));
                }}
              >
                <option value={ALL_FILTER_VALUE}>All policies</option>
                {(providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.available_filters.governance_policies ?? []).map((entry) => (
                  <option key={`provider-scheduler-search-moderation-governance-queue-policy-${entry.governance_policy_id}`} value={entry.governance_policy_id}>
                    {entry.name}
                  </option>
                ))}
              </select>
            </label>
            <span className="run-lineage-symbol-copy">
              {providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.summary.pending_approval_count ?? 0} pending · {providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.summary.ready_to_apply_count ?? 0} ready · {providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.summary.completed_count ?? 0} completed
            </span>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Plan</th>
                <th>Preview</th>
                <th>Queue</th>
              </tr>
            </thead>
            <tbody>
              {providerProvenanceSchedulerSearchModerationCatalogGovernancePlans?.items.length ? (
                providerProvenanceSchedulerSearchModerationCatalogGovernancePlans.items.map((entry) => (
                  <tr key={`provider-scheduler-search-moderation-catalog-governance-plan-${entry.plan_id}`}>
                    <td>
                      <strong>{shortenIdentifier(entry.plan_id, 10)}</strong>
                      <p className="run-lineage-symbol-copy">
                        {formatWorkflowToken(entry.action)} · {entry.governance_policy_name ?? "No policy"}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        Created {formatTimestamp(entry.created_at)} · by {entry.created_by}
                      </p>
                      {entry.guidance ? (
                        <p className="run-lineage-symbol-copy">{entry.guidance}</p>
                      ) : null}
                    </td>
                    <td>
                      <strong>{entry.preview_count} preview item(s)</strong>
                      {entry.preview_items.slice(0, 4).map((preview) => (
                        <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-moderation-catalog-governance-preview-${entry.plan_id}-${preview.catalog_id}`}>
                          {preview.catalog_name} · {formatWorkflowToken(preview.outcome)}{preview.changed_fields.length ? ` · ${preview.changed_fields.join(" · ")}` : ""}
                          {preview.message ? ` · ${preview.message}` : ""}
                        </p>
                      ))}
                    </td>
                    <td>
                      <strong>{formatWorkflowToken(entry.queue_state)}</strong>
                      <p className="run-lineage-symbol-copy">
                        Approved {formatTimestamp(entry.approved_at ?? null)} · by {entry.approved_by ?? "n/a"}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        Applied {formatTimestamp(entry.applied_at ?? null)} · by {entry.applied_by ?? "n/a"}
                      </p>
                      <div className="market-data-provenance-history-actions">
                        <button
                          className="ghost-button"
                          disabled={
                            entry.queue_state !== "pending_approval"
                            || providerProvenanceSchedulerSearchModerationCatalogGovernancePlanPendingId === entry.plan_id
                          }
                          onClick={() => {
                            void approveProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueuePlan(entry.plan_id);
                          }}
                          type="button"
                        >
                          Approve
                        </button>
                        <button
                          className="ghost-button"
                          disabled={
                            entry.queue_state !== "ready_to_apply"
                            || providerProvenanceSchedulerSearchModerationCatalogGovernancePlanPendingId === entry.plan_id
                          }
                          onClick={() => {
                            void applyProviderProvenanceSchedulerSearchModerationCatalogGovernanceQueuePlan(entry.plan_id);
                          }}
                          type="button"
                        >
                          Apply
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={3}>
                    <p className="empty-state">No moderation catalog governance plans match the current filter.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          <div className="market-data-provenance-history-head">
            <strong>Scheduler moderation approval queue</strong>
            <p>
              Stage selected feedback, review the plan preview, then approve and apply it
              as a governed moderation batch.
            </p>
          </div>
          <div className="market-data-provenance-history-actions">
            <label className="run-form-field">
              <span>Stage policy catalog</span>
              <select
                value={providerProvenanceSchedulerSearchModerationStageDraft.policy_catalog_id}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationStageDraft((current) => ({
                    ...current,
                    policy_catalog_id: event.target.value,
                  }));
                }}
              >
                <option value={ALL_FILTER_VALUE}>No catalog</option>
                {(providerProvenanceSchedulerSearchModerationPolicyCatalogs?.items ?? []).map((entry) => (
                  <option key={`provider-scheduler-search-stage-policy-${entry.catalog_id}`} value={entry.catalog_id}>
                    {entry.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="run-form-field">
              <span>Fallback outcome</span>
              <select
                value={providerProvenanceSchedulerSearchModerationStageDraft.moderation_status}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationStageDraft((current) => ({
                    ...current,
                    moderation_status: event.target.value,
                  }));
                }}
              >
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="pending">Pending</option>
              </select>
            </label>
            <label className="run-form-field">
              <span>Approval/apply note</span>
              <input
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationStageDraft((current) => ({
                    ...current,
                    note: event.target.value,
                  }));
                }}
                placeholder="required by policy catalogs that gate approval on notes"
                type="text"
                value={providerProvenanceSchedulerSearchModerationStageDraft.note}
              />
            </label>
            <button
              className="ghost-button"
              disabled={
                !selectedProviderProvenanceSchedulerSearchFeedbackIds.length
                || providerProvenanceSchedulerSearchModerationPlanPendingId !== null
              }
              onClick={() => {
                void stageProviderProvenanceSchedulerSearchModerationSelection();
              }}
              type="button"
            >
              Stage selected feedback
            </button>
            <label className="run-form-field">
              <span>Queue state</span>
              <select
                value={providerProvenanceSchedulerSearchModerationQueueFilter.queue_state}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationQueueFilter((current) => ({
                    ...current,
                    queue_state: event.target.value,
                  }));
                }}
              >
                <option value={ALL_FILTER_VALUE}>All states</option>
                <option value="pending_approval">Pending approval</option>
                <option value="ready_to_apply">Ready to apply</option>
                <option value="completed">Completed</option>
              </select>
            </label>
            <label className="run-form-field">
              <span>Policy catalog</span>
              <select
                value={providerProvenanceSchedulerSearchModerationQueueFilter.policy_catalog_id}
                onChange={(event) => {
                  setProviderProvenanceSchedulerSearchModerationQueueFilter((current) => ({
                    ...current,
                    policy_catalog_id: event.target.value,
                  }));
                }}
              >
                <option value={ALL_FILTER_VALUE}>All catalogs</option>
                {(providerProvenanceSchedulerSearchModerationPlans?.available_filters.policy_catalogs ?? []).map((entry) => (
                  <option key={`provider-scheduler-search-queue-policy-${entry.catalog_id}`} value={entry.catalog_id}>
                    {entry.name}
                  </option>
                ))}
              </select>
            </label>
            <span className="run-lineage-symbol-copy">
              {providerProvenanceSchedulerSearchModerationPlans?.summary.pending_approval_count ?? 0} pending · {providerProvenanceSchedulerSearchModerationPlans?.summary.ready_to_apply_count ?? 0} ready · {providerProvenanceSchedulerSearchModerationPlans?.summary.completed_count ?? 0} completed
            </span>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Plan</th>
                <th>Preview</th>
                <th>Queue</th>
              </tr>
            </thead>
            <tbody>
              {providerProvenanceSchedulerSearchModerationPlans?.items.length ? (
                providerProvenanceSchedulerSearchModerationPlans.items.map((entry) => (
                  <tr key={`provider-scheduler-search-moderation-plan-${entry.plan_id}`}>
                    <td>
                      <strong>{shortenIdentifier(entry.plan_id, 10)}</strong>
                      <p className="run-lineage-symbol-copy">
                        {entry.policy_catalog_name ?? "No catalog"} · {formatWorkflowToken(entry.proposed_moderation_status)}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        Created {formatTimestamp(entry.created_at)} · by {entry.created_by}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        View {formatWorkflowToken(entry.governance_view)} · window {entry.window_days}d · stale {entry.stale_pending_hours}h
                      </p>
                      <p className="run-lineage-symbol-copy">
                        Eligible {entry.feedback_ids.length}/{entry.requested_feedback_ids.length} · minimum score {entry.minimum_score}
                      </p>
                    </td>
                    <td>
                      <strong>{entry.preview_count} preview item(s)</strong>
                      {entry.preview_items.slice(0, 4).map((preview) => (
                        <p className="run-lineage-symbol-copy" key={`provider-scheduler-search-moderation-preview-${entry.plan_id}-${preview.feedback_id}`}>
                          {preview.occurrence_id} · {formatWorkflowToken(preview.current_moderation_status)} → {formatWorkflowToken(preview.proposed_moderation_status)} · score {preview.score} · {preview.eligible ? "eligible" : "skipped"}
                          {preview.reason_tags.length ? ` · ${preview.reason_tags.join(" · ")}` : ""}
                        </p>
                      ))}
                      {entry.missing_feedback_ids.length ? (
                        <p className="run-lineage-symbol-copy">
                          Missing {entry.missing_feedback_ids.join(" · ")}
                        </p>
                      ) : null}
                    </td>
                    <td>
                      <strong>{formatWorkflowToken(entry.queue_state)}</strong>
                      <p className="run-lineage-symbol-copy">
                        Approved {formatTimestamp(entry.approved_at ?? null)} · by {entry.approved_by ?? "n/a"}
                      </p>
                      <p className="run-lineage-symbol-copy">
                        Applied {formatTimestamp(entry.applied_at ?? null)} · by {entry.applied_by ?? "n/a"}
                      </p>
                      {entry.approval_note ? (
                        <p className="run-lineage-symbol-copy">{entry.approval_note}</p>
                      ) : null}
                      <div className="market-data-provenance-history-actions">
                        <button
                          className="ghost-button"
                          disabled={
                            entry.queue_state !== "pending_approval"
                            || providerProvenanceSchedulerSearchModerationPlanPendingId === entry.plan_id
                          }
                          onClick={() => {
                            void approveProviderProvenanceSchedulerSearchModerationQueuePlan(entry.plan_id);
                          }}
                          type="button"
                        >
                          Approve
                        </button>
                        <button
                          className="ghost-button"
                          disabled={
                            entry.queue_state !== "ready_to_apply"
                            || providerProvenanceSchedulerSearchModerationPlanPendingId === entry.plan_id
                          }
                          onClick={() => {
                            void applyProviderProvenanceSchedulerSearchModerationQueuePlan(entry.plan_id);
                          }}
                          type="button"
                        >
                          Apply
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={3}>
                    <p className="empty-state">
                      No staged scheduler moderation plans match the current queue filter.
                    </p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </>
      ) : null}
      {providerProvenanceSchedulerSearchDashboardLoading ? (
        <p className="empty-state">Loading scheduler search dashboard…</p>
      ) : null}
      {providerProvenanceSchedulerSearchDashboardError ? (
        <p className="market-data-workflow-feedback">
          Scheduler search dashboard failed: {providerProvenanceSchedulerSearchDashboardError}
        </p>
      ) : null}
      {providerProvenanceSchedulerSearchModerationPolicyCatalogsLoading
      || providerProvenanceSchedulerSearchModerationPlansLoading
      || providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesLoading
      || providerProvenanceSchedulerSearchModerationCatalogGovernancePlansLoading ? (
        <p className="empty-state">Loading scheduler moderation governance…</p>
      ) : null}
      {providerProvenanceSchedulerSearchModerationPolicyCatalogsError ? (
        <p className="market-data-workflow-feedback">
          Scheduler moderation policy catalogs failed: {providerProvenanceSchedulerSearchModerationPolicyCatalogsError}
        </p>
      ) : null}
      {providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesError ? (
        <p className="market-data-workflow-feedback">
          Scheduler moderation catalog governance policies failed: {providerProvenanceSchedulerSearchModerationCatalogGovernancePoliciesError}
        </p>
      ) : null}
      {providerProvenanceSchedulerSearchModerationCatalogGovernancePlansError ? (
        <p className="market-data-workflow-feedback">
          Scheduler moderation catalog governance queue failed: {providerProvenanceSchedulerSearchModerationCatalogGovernancePlansError}
        </p>
      ) : null}
      {providerProvenanceSchedulerSearchModerationPlansError ? (
        <p className="market-data-workflow-feedback">
          Scheduler moderation approval queue failed: {providerProvenanceSchedulerSearchModerationPlansError}
        </p>
      ) : null}
      {providerProvenanceSchedulerAlertRetrievalClusters.length ? (
        <>
          <div className="market-data-provenance-history-head">
            <strong>Cross-occurrence retrieval clusters</strong>
            <p>
              Semantic/vector clustering groups related scheduler occurrences across the
              current search slice so review can start from recovery or failure narratives
              instead of single rows.
            </p>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Cluster</th>
                <th>Coverage</th>
                <th>Signals</th>
              </tr>
            </thead>
            <tbody>
              {providerProvenanceSchedulerAlertRetrievalClusters.map((cluster) => (
                <tr key={`provider-scheduler-retrieval-cluster-${cluster.cluster_id ?? cluster.rank}`}>
                  <td>
                    <strong>{cluster.label ?? `Cluster ${cluster.rank}`}</strong>
                    <p className="run-lineage-symbol-copy">
                      Rank {cluster.rank} · {cluster.occurrence_count} occurrence(s)
                    </p>
                    {cluster.top_occurrence_summary ? (
                      <p className="run-lineage-symbol-copy">
                        Top occurrence {cluster.top_occurrence_summary}
                      </p>
                    ) : null}
                  </td>
                  <td>
                    <strong>Top {cluster.top_score}</strong>
                    <p className="run-lineage-symbol-copy">
                      Avg {cluster.average_score} · similarity {cluster.average_similarity_pct}%
                    </p>
                    <p className="run-lineage-symbol-copy">
                      {cluster.summary ?? "Cross-occurrence retrieval cluster"}
                    </p>
                  </td>
                  <td>
                    <strong>
                      {cluster.semantic_concepts.length
                        ? cluster.semantic_concepts.join(" · ")
                        : "No dominant semantic concept"}
                    </strong>
                    <p className="run-lineage-symbol-copy">
                      Vector {cluster.vector_terms.join(" · ") || "n/a"}
                    </p>
                    <p className="run-lineage-symbol-copy">
                      {cluster.categories.join(" · ") || "n/a"} · {cluster.statuses.join(" · ") || "n/a"}
                    </p>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      ) : null}
      {providerProvenanceSchedulerAlertHistoryLoading && !providerProvenanceSchedulerAlertTimelineItems.length ? (
        <p className="empty-state">Loading scheduler alert timeline…</p>
      ) : null}
      {providerProvenanceSchedulerAlertHistoryError ? (
        <p className="market-data-workflow-feedback">
          Scheduler alert timeline failed: {providerProvenanceSchedulerAlertHistoryError}
        </p>
      ) : null}
      {providerProvenanceSchedulerAlertTimelineItems.length ? (
        <table className="data-table">
          <thead>
            <tr>
              <th>Occurrence</th>
              <th>Window</th>
              <th>Summary</th>
            </tr>
          </thead>
          <tbody>
            {providerProvenanceSchedulerAlertTimelineItems.map((alert) => {
              const timelineSummary = formatProviderProvenanceSchedulerTimelineSummary(alert);
              const narrativeFacetLabel = formatProviderProvenanceSchedulerNarrativeFacet(
                alert.narrative.facet ?? "all_occurrences",
              );
              return (
                <tr key={`provider-scheduler-alert-timeline-${getOperatorAlertOccurrenceKey(alert)}`}>
                  <td>
                    <strong>{formatWorkflowToken(alert.category)}</strong>
                    <p className="run-lineage-symbol-copy">
                      {formatWorkflowToken(alert.status)} · {alert.severity}
                    </p>
                    {timelineSummary ? (
                      <p className="run-lineage-symbol-copy">{timelineSummary}</p>
                    ) : null}
                    <p className="run-lineage-symbol-copy">
                      Narrative {narrativeFacetLabel} · {alert.narrative.occurrence_record_count} occurrence record(s)
                    </p>
                  </td>
                  <td>
                    <strong>{formatTimestamp(alert.detected_at)}</strong>
                    <p className="run-lineage-symbol-copy">
                      Resolved {formatTimestamp(alert.resolved_at ?? null)}
                    </p>
                    {alert.occurrence_id ? (
                      <p className="run-lineage-symbol-copy">{alert.occurrence_id}</p>
                    ) : null}
                    {alert.search_match ? (
                      <p className="run-lineage-symbol-copy">
                        {formatProviderProvenanceSchedulerSearchMatchSummary(alert.search_match)}
                      </p>
                    ) : null}
                    {alert.retrieval_cluster ? (
                      <p className="run-lineage-symbol-copy">
                        {formatProviderProvenanceSchedulerRetrievalClusterSummary(alert.retrieval_cluster)}
                      </p>
                    ) : null}
                    {alert.narrative.can_reconstruct_narrative ? (
                      <p className="run-lineage-symbol-copy">
                        Sequence {alert.narrative.status_sequence.join(" → ") || "n/a"}
                      </p>
                    ) : null}
                  </td>
                  <td>
                    <strong>{alert.summary}</strong>
                    <p className="run-lineage-symbol-copy">{alert.detail}</p>
                    <p className="run-lineage-symbol-copy">
                      Delivery: {alert.delivery_targets.length ? alert.delivery_targets.join(", ") : "n/a"}
                    </p>
                    <p className="run-lineage-symbol-copy">
                      {alert.narrative.can_reconstruct_narrative
                        ? `Narrative mode ${formatWorkflowToken(alert.narrative.narrative_mode ?? "mixed_status_post_resolution")} · post-resolution ${alert.narrative.post_resolution_record_count} record(s)`
                        : "Active occurrence uses the current scheduler snapshot until it resolves."}
                    </p>
                    {alert.narrative.has_post_resolution_history ? (
                      <p className="run-lineage-symbol-copy">
                        Post-resolution sequence {alert.narrative.post_resolution_status_sequence.join(" → ") || "n/a"} · window ended {formatTimestamp(alert.narrative.narrative_window_ended_at ?? null)}
                      </p>
                    ) : null}
                    {alert.narrative.next_occurrence_detected_at ? (
                      <p className="run-lineage-symbol-copy">
                        Next recurrence detected {formatTimestamp(alert.narrative.next_occurrence_detected_at)}
                      </p>
                    ) : null}
                    {alert.search_match?.highlights.length ? (
                      <p className="run-lineage-symbol-copy">
                        Match {alert.search_match.highlights.join(" · ")}
                      </p>
                    ) : null}
                    {alert.search_match?.operator_hits.length ? (
                      <p className="run-lineage-symbol-copy">
                        Operators {alert.search_match.operator_hits.join(" · ")}
                      </p>
                    ) : null}
                    {alert.search_match?.semantic_concepts.length ? (
                      <p className="run-lineage-symbol-copy">
                        Semantic {alert.search_match.semantic_concepts.join(" · ")}
                      </p>
                    ) : null}
                    {alert.search_match?.ranking_reason ? (
                      <p className="run-lineage-symbol-copy">{alert.search_match.ranking_reason}</p>
                    ) : null}
                    {alert.search_match?.relevance_model ? (
                      <p className="run-lineage-symbol-copy">
                        Relevance {alert.search_match.relevance_model} · lexical {alert.search_match.lexical_score} · semantic {alert.search_match.semantic_score} · operator {alert.search_match.operator_score} · learned {alert.search_match.learned_score}
                      </p>
                    ) : null}
                    {alert.search_match?.tuning_signals.length ? (
                      <p className="run-lineage-symbol-copy">
                        Learned signals {alert.search_match.tuning_signals.join(" · ")}
                      </p>
                    ) : null}
                    {alert.retrieval_cluster?.vector_terms.length ? (
                      <p className="run-lineage-symbol-copy">
                        Cluster vector {alert.retrieval_cluster.vector_terms.join(" · ")}
                      </p>
                    ) : null}
                    <div className="market-data-provenance-history-actions">
                      {alert.search_match && providerProvenanceSchedulerAlertHistory?.search_summary?.query_id ? (
                        <>
                          <button
                            className="ghost-button"
                            disabled={
                              providerProvenanceSchedulerSearchFeedbackPendingOccurrenceKey === getOperatorAlertOccurrenceKey(alert)
                            }
                            onClick={() => {
                              void submitProviderProvenanceSchedulerSearchFeedback(alert, "relevant");
                            }}
                            type="button"
                          >
                            Relevant
                          </button>
                          <button
                            className="ghost-button"
                            disabled={
                              providerProvenanceSchedulerSearchFeedbackPendingOccurrenceKey === getOperatorAlertOccurrenceKey(alert)
                            }
                            onClick={() => {
                              void submitProviderProvenanceSchedulerSearchFeedback(alert, "not_relevant");
                            }}
                            type="button"
                          >
                            Not relevant
                          </button>
                        </>
                      ) : null}
                      <button
                        className="ghost-button"
                        onClick={() => {
                          void triggerProviderProvenanceSchedulerAlertExportWorkflow(alert, {
                            sourceLabel: `${alert.summary} scheduler timeline row`,
                          });
                        }}
                        type="button"
                      >
                        {alert.status === "resolved" ? "Reconstruct narrative export" : "Start current workflow"}
                      </button>
                      <button
                        className="ghost-button"
                        onClick={() => {
                          void triggerProviderProvenanceSchedulerAlertExportWorkflow(alert, {
                            escalate: true,
                            sourceLabel: `${alert.summary} scheduler timeline row`,
                          });
                        }}
                        type="button"
                      >
                        {alert.status === "resolved"
                          ? "Escalate narrative export"
                          : "Escalate current snapshot"}
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      ) : (
        <p className="empty-state">No scheduler alert occurrences match the selected filters.</p>
      )}
    </>
  );
}
