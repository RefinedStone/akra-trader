// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerAlertTimelineSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
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
