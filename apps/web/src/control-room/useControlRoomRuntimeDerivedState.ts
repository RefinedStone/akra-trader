// @ts-nocheck
import { useEffect, useMemo } from "react";

export function useControlRoomRuntimeDerivedState({ model }: { model: any }): any {
  const {
    strategies, marketStatus, isMarketDataInstrumentAtRisk, sandboxRuns, paperRuns, liveRuns,
    operatorVisibility, resolveMarketDataInstrumentLink, guardedLive, getOperatorAlertOccurrenceKey, isProviderProvenanceSchedulerAlertCategory, resolveAutoLinkedMarketInstrument,
    resolvePreferredMarketDataInstrument, activeMarketInstrumentKey, buildMarketDataInstrumentFocusKey, loadProviderProvenanceAnalytics, providerProvenanceAnalyticsQuery, loadProviderProvenanceSchedulerSurfaces,
    providerProvenanceSchedulerAlertHistoryOffset, providerProvenanceSchedulerHistoryOffset, providerProvenanceSchedulerDrilldownBucketKey, providerProvenanceSchedulerSearchDashboardFilter, providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter, providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter, providerProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter, providerProvenanceSchedulerSearchModerationQueueFilter, providerProvenanceSchedulerStitchedReportViewAuditFilter, setProviderProvenanceSchedulerExportPolicyDraft, buildProviderProvenanceSchedulerExportPolicyDraft,
    selectedProviderProvenanceSchedulerExportEntry, loadProviderProvenanceWorkspaceRegistry, providerProvenanceAnalytics, providerProvenanceSchedulerAnalytics, providerProvenanceSchedulerHistory, providerProvenanceSchedulerAlertHistory,
    formatLinkedMarketPrimaryFocusNote, formatWorkflowToken, formatTimestamp, summarizeProviderRecoveryMarketContextProvenance, marketDataLineageHistory, formatRange,
    marketDataIngestionJobs, getOperatorSeverityRank, setMarketDataProvenanceExportFilter, ALL_FILTER_VALUE, marketDataProvenanceExportFilter, formatMarketDataProvenanceExportFilterSummary,
    resolveMarketDataSymbol, serializeLinkedMarketInstrumentContext, backtests, formatCompletion, buildControlWorkspaceDescriptors, presets,
    references, activeWorkspace,
  } = model;

  const strategyGroups = useMemo(() => {
    return {
      native: strategies.filter((strategy) => strategy.runtime === "native"),
      reference: strategies.filter((strategy) => strategy.runtime === "freqtrade_reference"),
      future: strategies.filter((strategy) => strategy.runtime === "decision_engine"),
    };
  }, [strategies]);

  const backfillSummary = useMemo(() => {
    if (!marketStatus) {
      return null;
    }
    const tracked = marketStatus.instruments.filter(
      (instrument) => instrument.backfill_target_candles !== null,
    );
    if (!tracked.length) {
      return null;
    }
    const contiguousTracked = tracked.filter(
      (instrument) => instrument.backfill_contiguous_completion_ratio !== null,
    );
    const targetCandles = tracked.reduce(
      (total, instrument) => total + (instrument.backfill_target_candles ?? 0),
      0,
    );
    const coveredCandles = tracked.reduce(
      (total, instrument) =>
        total +
        Math.min(
          instrument.candle_count,
          instrument.backfill_target_candles ?? instrument.candle_count,
        ),
      0,
    );
    const completeCount = tracked.filter((instrument) => instrument.backfill_complete).length;
    return {
      targetCandles,
      coveredCandles,
      completeCount,
      instrumentCount: tracked.length,
      completionRatio: targetCandles > 0 ? coveredCandles / targetCandles : null,
      contiguousQualityRatio:
        contiguousTracked.length > 0
          ? contiguousTracked.reduce(
              (total, instrument) =>
                total + (instrument.backfill_contiguous_completion_ratio ?? 0),
              0,
            ) / contiguousTracked.length
          : null,
      contiguousCompleteCount: contiguousTracked.filter(
        (instrument) => instrument.backfill_contiguous_complete,
      ).length,
      contiguousInstrumentCount: contiguousTracked.length,
    };
  }, [marketStatus]);

  const failureSummary = useMemo(() => {
    if (!marketStatus) {
      return null;
    }
    const instrumentsWithFailures = marketStatus.instruments.filter(
      (instrument) => instrument.failure_count_24h > 0,
    );
    return {
      failureCount24h: marketStatus.instruments.reduce(
        (total, instrument) => total + instrument.failure_count_24h,
        0,
      ),
      affectedInstrumentCount: instrumentsWithFailures.length,
      lastFailureAt:
        instrumentsWithFailures
          .flatMap((instrument) => instrument.recent_failures.map((failure) => failure.failed_at))
          .sort()
          .at(-1) ?? null,
    };
  }, [marketStatus]);

  const incidentFocusedInstruments = useMemo(
    () => marketStatus?.instruments.filter((instrument) => isMarketDataInstrumentAtRisk(instrument)) ?? [],
    [marketStatus],
  );

  const runtimeRunById = useMemo(
    () =>
      new Map(
        [...sandboxRuns, ...paperRuns, ...liveRuns].map((run) => [run.config.run_id, run]),
      ),
    [liveRuns, paperRuns, sandboxRuns],
  );

  const operatorAlertById = useMemo(() => {
    const alertMap = new Map<
      string,
      OperatorVisibility["alerts"][number] | OperatorVisibility["alert_history"][number]
    >();
    if (!operatorVisibility) {
      return alertMap;
    }
    operatorVisibility.alert_history.forEach((alert) => {
      if (!alertMap.has(alert.alert_id)) {
        alertMap.set(alert.alert_id, alert);
      }
    });
    operatorVisibility.alerts.forEach((alert) => {
      alertMap.set(alert.alert_id, alert);
    });
    return alertMap;
  }, [operatorVisibility]);

  const linkedOperatorAlerts = useMemo(
    () =>
      operatorVisibility?.alerts.map((alert) => ({
        alert,
        link: resolveMarketDataInstrumentLink({
          guardedLive,
          liveRuns,
          marketStatus,
          record: alert,
          runById: runtimeRunById,
        }),
      })) ?? [],
    [guardedLive, liveRuns, marketStatus, operatorVisibility, runtimeRunById],
  );

  const linkedOperatorAlertHistory = useMemo(
    () =>
      operatorVisibility?.alert_history.map((alert) => ({
        alert,
        link: resolveMarketDataInstrumentLink({
          guardedLive,
          liveRuns,
          marketStatus,
          record: alert,
          runById: runtimeRunById,
        }),
      })) ?? [],
    [guardedLive, liveRuns, marketStatus, operatorVisibility, runtimeRunById],
  );

  const linkedOperatorIncidentEvents = useMemo(
    () =>
      operatorVisibility?.incident_events.map((event) => {
        const alertContext = operatorAlertById.get(event.alert_id);
        return {
          event,
          link: resolveMarketDataInstrumentLink({
            guardedLive,
            liveRuns,
            marketStatus,
            record: {
              alert_id: event.alert_id,
              category: alertContext?.category ?? null,
              summary: event.summary,
              detail: event.detail,
              run_id: event.run_id ?? alertContext?.run_id ?? null,
              session_id: event.session_id ?? alertContext?.session_id ?? null,
              symbol: event.symbol ?? alertContext?.symbol ?? null,
              symbols: event.symbols.length ? event.symbols : (alertContext?.symbols ?? []),
              timeframe: event.timeframe ?? alertContext?.timeframe ?? null,
              primary_focus: event.primary_focus ?? alertContext?.primary_focus ?? null,
              source: event.source ?? alertContext?.source ?? null,
              provider_recovery_symbols: event.remediation.provider_recovery.symbols,
              provider_recovery_timeframe: event.remediation.provider_recovery.timeframe,
            },
            runById: runtimeRunById,
          }),
        };
      }) ?? [],
    [guardedLive, liveRuns, marketStatus, operatorAlertById, operatorVisibility, runtimeRunById],
  );

  const linkedOperatorAlertById = useMemo(
    () => new Map(linkedOperatorAlerts.map((entry) => [entry.alert.alert_id, entry.link])),
    [linkedOperatorAlerts],
  );

  const linkedOperatorAlertHistoryByOccurrenceId = useMemo(
    () =>
      new Map(
        linkedOperatorAlertHistory.map((entry) => [
          getOperatorAlertOccurrenceKey(entry.alert),
          entry.link,
        ]),
      ),
    [linkedOperatorAlertHistory],
  );

  const providerProvenanceSchedulerAlertHistoryTimelineByCategory = useMemo(() => {
    const timelineMap = new Map<
      string,
      {
        alert: OperatorVisibility["alert_history"][number];
        link: ReturnType<typeof resolveMarketDataInstrumentLink>;
      }[]
    >();
    linkedOperatorAlertHistory.forEach((entry) => {
      if (!isProviderProvenanceSchedulerAlertCategory(entry.alert.category)) {
        return;
      }
      const existing = timelineMap.get(entry.alert.category) ?? [];
      existing.push(entry);
      existing.sort((left, right) => left.alert.detected_at.localeCompare(right.alert.detected_at));
      timelineMap.set(entry.alert.category, existing);
    });
    return timelineMap;
  }, [linkedOperatorAlertHistory]);

  const linkedOperatorIncidentEventById = useMemo(
    () => new Map(linkedOperatorIncidentEvents.map((entry) => [entry.event.event_id, entry.link])),
    [linkedOperatorIncidentEvents],
  );

  const autoLinkedMarketInstrumentLink = useMemo(
    () =>
      resolveAutoLinkedMarketInstrument({
        guardedLive,
        liveRuns,
        marketStatus,
        operatorVisibility,
        runById: runtimeRunById,
      }),
    [guardedLive, liveRuns, marketStatus, operatorVisibility, runtimeRunById],
  );

  const activeMarketInstrument = useMemo(() => {
    if (!marketStatus) {
      return null;
    }
    return resolvePreferredMarketDataInstrument(marketStatus, activeMarketInstrumentKey);
  }, [activeMarketInstrumentKey, marketStatus]);

  const activeMarketInstrumentFocusKey = activeMarketInstrument
    ? buildMarketDataInstrumentFocusKey(activeMarketInstrument)
    : null;

  const focusedLinkedOperatorAlerts = useMemo(
    () =>
      activeMarketInstrumentFocusKey
        ? linkedOperatorAlerts.filter((entry) => entry.link?.focusKey === activeMarketInstrumentFocusKey)
        : [],
    [activeMarketInstrumentFocusKey, linkedOperatorAlerts],
  );

  const focusedLinkedOperatorAlertHistory = useMemo(
    () =>
      activeMarketInstrumentFocusKey
        ? linkedOperatorAlertHistory.filter((entry) => entry.link?.focusKey === activeMarketInstrumentFocusKey)
        : [],
    [activeMarketInstrumentFocusKey, linkedOperatorAlertHistory],
  );

  const focusedLinkedOperatorIncidentEvents = useMemo(
    () =>
      activeMarketInstrumentFocusKey
        ? linkedOperatorIncidentEvents.filter((entry) => entry.link?.focusKey === activeMarketInstrumentFocusKey)
        : [],
    [activeMarketInstrumentFocusKey, linkedOperatorIncidentEvents],
  );

  const focusedMultiSymbolPrimaryLink = useMemo(
    () =>
      focusedLinkedOperatorAlerts.find((entry) => (entry.link?.candidateCount ?? 0) > 1)?.link
      ?? focusedLinkedOperatorIncidentEvents.find((entry) => (entry.link?.candidateCount ?? 0) > 1)?.link
      ?? focusedLinkedOperatorAlertHistory.find((entry) => (entry.link?.candidateCount ?? 0) > 1)?.link
      ?? (
        autoLinkedMarketInstrumentLink?.focusKey === activeMarketInstrumentFocusKey
        && autoLinkedMarketInstrumentLink.candidateCount > 1
          ? autoLinkedMarketInstrumentLink
          : null
      ),
    [
      activeMarketInstrumentFocusKey,
      autoLinkedMarketInstrumentLink,
      focusedLinkedOperatorAlertHistory,
      focusedLinkedOperatorAlerts,
      focusedLinkedOperatorIncidentEvents,
    ],
  );

  useEffect(() => {
    void loadProviderProvenanceAnalytics(activeMarketInstrument);
  }, [activeMarketInstrument, marketStatus, providerProvenanceAnalyticsQuery]);

  useEffect(() => {
    void loadProviderProvenanceSchedulerSurfaces();
  }, [
    providerProvenanceAnalyticsQuery.window_days,
    providerProvenanceSchedulerAlertHistoryOffset,
    providerProvenanceAnalyticsQuery.search_query,
    providerProvenanceAnalyticsQuery.scheduler_alert_category,
    providerProvenanceAnalyticsQuery.scheduler_alert_narrative_facet,
    providerProvenanceAnalyticsQuery.scheduler_alert_status,
    providerProvenanceSchedulerHistoryOffset,
    providerProvenanceSchedulerDrilldownBucketKey,
    providerProvenanceSchedulerSearchDashboardFilter.search,
    providerProvenanceSchedulerSearchDashboardFilter.moderation_status,
    providerProvenanceSchedulerSearchDashboardFilter.signal,
    providerProvenanceSchedulerSearchDashboardFilter.governance_view,
    providerProvenanceSchedulerSearchDashboardFilter.window_days,
    providerProvenanceSchedulerSearchDashboardFilter.stale_pending_hours,
    providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter.catalog_id,
    providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter.action,
    providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter.actor_tab_id,
    providerProvenanceSchedulerSearchModerationPolicyCatalogAuditFilter.search,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter.governance_policy_id,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter.action,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter.actor_tab_id,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditFilter.search,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter.queue_state,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaQueueFilter.meta_policy_id,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter.queue_state,
    providerProvenanceSchedulerSearchModerationCatalogGovernanceQueueFilter.governance_policy_id,
    providerProvenanceSchedulerSearchModerationQueueFilter.queue_state,
    providerProvenanceSchedulerSearchModerationQueueFilter.policy_catalog_id,
    providerProvenanceSchedulerStitchedReportViewAuditFilter.view_id,
    providerProvenanceSchedulerStitchedReportViewAuditFilter.action,
    providerProvenanceSchedulerStitchedReportViewAuditFilter.actor_tab_id,
    providerProvenanceSchedulerStitchedReportViewAuditFilter.search,
  ]);

  useEffect(() => {
    setProviderProvenanceSchedulerExportPolicyDraft(
      buildProviderProvenanceSchedulerExportPolicyDraft(selectedProviderProvenanceSchedulerExportEntry),
    );
  }, [selectedProviderProvenanceSchedulerExportEntry]);

  useEffect(() => {
    void loadProviderProvenanceWorkspaceRegistry();
  }, []);

  const providerProvenanceDriftBarMax = useMemo(
    () =>
      Math.max(
        0,
        ...(providerProvenanceAnalytics?.time_series.provider_drift.series ?? []).map((bucket) =>
          Math.max(bucket.provider_provenance_count, bucket.export_count),
        ),
      ),
    [providerProvenanceAnalytics],
  );

  const providerProvenanceBurnUpBarMax = useMemo(
    () =>
      Math.max(
        0,
        ...(providerProvenanceAnalytics?.time_series.export_burn_up.series ?? []).map((bucket) =>
          Math.max(
            bucket.cumulative_export_count,
            bucket.cumulative_download_count,
            bucket.cumulative_provider_provenance_count,
          ),
        ),
      ),
    [providerProvenanceAnalytics],
  );

  const providerProvenanceSchedulerLagBarMax = useMemo(
    () =>
      Math.max(
        0,
        ...(providerProvenanceSchedulerAnalytics?.time_series.lag_trend.series ?? []).map((bucket) =>
          Math.max(bucket.peak_lag_seconds, bucket.latest_lag_seconds),
        ),
      ),
    [providerProvenanceSchedulerAnalytics],
  );

  const providerProvenanceSchedulerCurrent = useMemo(
    () => providerProvenanceSchedulerAnalytics?.current ?? providerProvenanceSchedulerHistory?.current ?? null,
    [providerProvenanceSchedulerAnalytics, providerProvenanceSchedulerHistory],
  );

  const providerProvenanceSchedulerRecentHistory = useMemo(
    () =>
      providerProvenanceSchedulerHistory?.items.length
        ? providerProvenanceSchedulerHistory.items
        : (providerProvenanceSchedulerAnalytics?.recent_history ?? []),
    [providerProvenanceSchedulerAnalytics, providerProvenanceSchedulerHistory],
  );

  const providerProvenanceSchedulerAlertTimelineItems = useMemo(
    () => providerProvenanceSchedulerAlertHistory?.items ?? [],
    [providerProvenanceSchedulerAlertHistory],
  );

  const providerProvenanceSchedulerAlertRetrievalClusters = useMemo(
    () => providerProvenanceSchedulerAlertHistory?.retrieval_clusters ?? [],
    [providerProvenanceSchedulerAlertHistory],
  );

  const providerProvenanceSchedulerAlertCategoryOptions = useMemo(
    () =>
      providerProvenanceSchedulerAlertHistory?.available_filters.categories.length
        ? providerProvenanceSchedulerAlertHistory.available_filters.categories
        : ["scheduler_lag", "scheduler_failure"],
    [providerProvenanceSchedulerAlertHistory],
  );

  const providerProvenanceSchedulerAlertStatusOptions = useMemo(
    () =>
      providerProvenanceSchedulerAlertHistory?.available_filters.statuses.length
        ? providerProvenanceSchedulerAlertHistory.available_filters.statuses
        : ["active", "resolved"],
    [providerProvenanceSchedulerAlertHistory],
  );

  const providerProvenanceSchedulerAlertNarrativeFacetOptions = useMemo(
    () =>
      providerProvenanceSchedulerAlertHistory?.available_filters.narrative_facets.length
        ? providerProvenanceSchedulerAlertHistory.available_filters.narrative_facets
        : [
            "all_occurrences",
            "resolved_narratives",
            "post_resolution_recovery",
            "recurring_occurrences",
          ],
    [providerProvenanceSchedulerAlertHistory],
  );

  const providerProvenanceSchedulerDrillDown = providerProvenanceSchedulerAnalytics?.drill_down ?? null;

  const focusedMarketIncidentHistory = useMemo(() => {
    if (!activeMarketInstrument) {
      return [] as MarketDataIncidentHistoryEntry[];
    }

    const entries: MarketDataIncidentHistoryEntry[] = [];

    focusedLinkedOperatorAlerts.forEach(({ alert, link }) => {
      const primaryFocusNote = formatLinkedMarketPrimaryFocusNote(link);
      entries.push({
        entryId: `alert:${alert.alert_id}`,
        occurredAt: alert.detected_at,
        sourceLabel: "Active alert",
        statusLabel: `${formatWorkflowToken(alert.severity)} / ${formatWorkflowToken(alert.category)}`,
        summary: alert.summary,
        detail: `${alert.detail} Delivery: ${alert.delivery_targets.length ? alert.delivery_targets.join(", ") : "n/a"}.${primaryFocusNote ? ` ${primaryFocusNote}` : ""}`,
        tone: alert.severity === "critical" ? "critical" : "warning",
      });
    });

    focusedLinkedOperatorAlertHistory.forEach(({ alert, link }) => {
      const primaryFocusNote = formatLinkedMarketPrimaryFocusNote(link);
      entries.push({
        entryId: `alert-history:${getOperatorAlertOccurrenceKey(alert)}`,
        occurredAt: alert.resolved_at ?? alert.detected_at,
        sourceLabel: alert.status === "resolved" ? "Resolved alert" : "Alert history",
        statusLabel: `${formatWorkflowToken(alert.status)} / ${formatWorkflowToken(alert.category)}`,
        summary: alert.summary,
        detail: `${alert.detail} Detected ${formatTimestamp(alert.detected_at)}.${primaryFocusNote ? ` ${primaryFocusNote}` : ""}`,
        tone:
          alert.status === "resolved"
            ? "neutral"
            : alert.severity === "critical"
              ? "critical"
              : "warning",
      });
    });

    focusedLinkedOperatorIncidentEvents.forEach(({ event, link }) => {
      const remediationDetail =
        event.remediation.state !== "not_applicable"
          ? ` Remediation: ${formatWorkflowToken(event.remediation.state)}${event.remediation.summary ? ` / ${event.remediation.summary}` : ""}.`
          : "";
      const providerProvenanceSummary = summarizeProviderRecoveryMarketContextProvenance(
        event.remediation.provider_recovery,
      )?.summary;
      const primaryFocusNote = formatLinkedMarketPrimaryFocusNote(link);
      entries.push({
        entryId: `incident:${event.event_id}`,
        occurredAt: event.timestamp,
        sourceLabel: "Incident event",
        statusLabel: `${formatWorkflowToken(event.kind)} / ${formatWorkflowToken(event.severity)}`,
        summary: event.summary,
        detail: `${event.detail} Ack: ${formatWorkflowToken(event.acknowledgment_state)}. Escalation: level ${event.escalation_level} / ${formatWorkflowToken(event.escalation_state)}.${remediationDetail}${providerProvenanceSummary ? ` ${providerProvenanceSummary}.` : ""}${primaryFocusNote ? ` ${primaryFocusNote}` : ""}`,
        tone: event.severity === "critical" ? "critical" : "warning",
      });
    });

    marketDataLineageHistory.forEach((record, index) => {
      const isReviewSignal =
        index === 0
        || record.sync_status !== "synced"
        || record.failure_count_24h > 0
        || record.gap_window_count > 0
        || record.issues.length > 0;
      if (!isReviewSignal) {
        return;
      }
      const issueSummary = record.issues.length
        ? record.issues.join(", ")
        : `${record.failure_count_24h} failures / 24h${record.gap_window_count ? ` · ${record.gap_window_count} gaps` : ""}`;
      entries.push({
        entryId: `lineage:${record.history_id}`,
        occurredAt: record.recorded_at,
        sourceLabel: "Lineage snapshot",
        statusLabel: `${formatWorkflowToken(record.sync_status)} / ${formatWorkflowToken(record.validation_claim)}`,
        summary: `${record.symbol} ${record.timeframe} lineage snapshot recorded.`,
        detail: `${issueSummary || "No lineage issues recorded."} Window: ${formatRange(record.first_timestamp, record.last_timestamp)}.`,
        tone:
          record.sync_status === "error" || record.failure_count_24h > 0
            ? "critical"
            : record.sync_status !== "synced" || record.gap_window_count > 0 || record.issues.length > 0
              ? "warning"
              : "neutral",
      });
    });

    marketDataIngestionJobs.forEach((job, index) => {
      const isWorkflowSignal = index === 0 || job.status !== "succeeded" || Boolean(job.last_error);
      if (!isWorkflowSignal) {
        return;
      }
      entries.push({
        entryId: `ingestion:${job.job_id}`,
        occurredAt: job.finished_at,
        sourceLabel: "Ingestion job",
        statusLabel: `${formatWorkflowToken(job.status)} / ${formatWorkflowToken(job.operation)}`,
        summary: `${job.symbol} ${job.timeframe} ingestion ${formatWorkflowToken(job.operation)} completed.`,
        detail: `${job.fetched_candle_count} candles fetched in ${job.duration_ms} ms.${job.last_error ? ` Error: ${job.last_error}.` : ""}`,
        tone: job.status === "succeeded" ? "neutral" : "warning",
      });
    });

    return entries
      .sort((left, right) => {
        const leftTimestamp = Date.parse(left.occurredAt);
        const rightTimestamp = Date.parse(right.occurredAt);
        return (
          (Number.isFinite(rightTimestamp) ? rightTimestamp : Number.NEGATIVE_INFINITY)
          - (Number.isFinite(leftTimestamp) ? leftTimestamp : Number.NEGATIVE_INFINITY)
        );
      })
      .slice(0, 10);
  }, [
      activeMarketInstrument,
      focusedMultiSymbolPrimaryLink,
      focusedLinkedOperatorAlertHistory,
      focusedLinkedOperatorAlerts,
      focusedLinkedOperatorIncidentEvents,
      marketDataIngestionJobs,
      marketDataLineageHistory,
  ]);

  const focusedMarketWorkflowSummary = useMemo(() => {
    if (!activeMarketInstrument) {
      return null;
    }
    const latestLineage = marketDataLineageHistory[0] ?? null;
    const latestJob = marketDataIngestionJobs[0] ?? null;
    const failedJobCount = marketDataIngestionJobs.filter((job) => job.status !== "succeeded").length;
    const reviewSnapshotCount = marketDataLineageHistory.filter(
      (record) =>
        record.sync_status !== "synced"
        || record.failure_count_24h > 0
        || record.gap_window_count > 0
        || record.issues.length > 0,
    ).length;
    return {
      focusLabel: `${activeMarketInstrument.instrument_id} / ${activeMarketInstrument.timeframe}`,
      lineageCount: marketDataLineageHistory.length,
      ingestionJobCount: marketDataIngestionJobs.length,
      failedJobCount,
      reviewSnapshotCount,
      linkedAlertCount: focusedLinkedOperatorAlerts.length,
      linkedHistoryCount: focusedLinkedOperatorAlertHistory.length,
      linkedIncidentCount: focusedLinkedOperatorIncidentEvents.length,
      incidentHistoryCount: focusedMarketIncidentHistory.length,
      latestLineage,
      latestJob,
    };
  }, [
    activeMarketInstrument,
    focusedLinkedOperatorAlertHistory.length,
    focusedLinkedOperatorAlerts.length,
    focusedLinkedOperatorIncidentEvents.length,
    focusedMarketIncidentHistory.length,
    marketDataIngestionJobs,
    marketDataLineageHistory,
  ]);

  const focusedMarketProviderProvenanceEvents = useMemo(
    () =>
      focusedLinkedOperatorIncidentEvents.flatMap(({ event, link }) => {
        const provenanceSummary = summarizeProviderRecoveryMarketContextProvenance(
          event.remediation.provider_recovery,
        );
        if (!provenanceSummary) {
          return [];
        }
        const provider =
          event.remediation.provider_recovery.market_context_provenance?.provider?.trim()
          || event.remediation.provider_recovery.provider?.trim()
          || event.external_provider?.trim()
          || "unknown";
        const vendorField =
          event.remediation.provider_recovery.market_context_provenance?.vendor_field?.trim()
          || "unknown";
        const occurredAtMs = Date.parse(event.timestamp);
        return [
          {
            event,
            link,
            provider,
            vendorField,
            provenanceSummary: provenanceSummary.summary,
            fieldSummaries: provenanceSummary.fieldSummaries,
            severityRank: getOperatorSeverityRank(event.severity),
            occurredAtMs: Number.isFinite(occurredAtMs) ? occurredAtMs : Number.NEGATIVE_INFINITY,
            searchText: [
              provider,
              vendorField,
              event.kind,
              event.severity,
              event.summary,
              event.detail,
              event.source,
              event.external_provider ?? "",
              event.external_reference ?? "",
              event.provider_workflow_reference ?? "",
              event.remediation.provider_recovery.symbols.join(" "),
              event.remediation.provider_recovery.timeframe ?? "",
              provenanceSummary.summary,
              provenanceSummary.fieldSummaries.join(" "),
            ]
              .join(" ")
              .toLowerCase(),
          } satisfies MarketDataProviderProvenanceEventRecord,
        ];
      }),
    [focusedLinkedOperatorIncidentEvents],
  );

  const focusedMarketProviderProvenanceCount = focusedMarketProviderProvenanceEvents.length;

  const marketDataProvenanceExportProviderOptions = useMemo(
    () => Array.from(new Set(focusedMarketProviderProvenanceEvents.map((record) => record.provider))).sort(),
    [focusedMarketProviderProvenanceEvents],
  );

  const marketDataProvenanceExportVendorFieldOptions = useMemo(
    () => Array.from(new Set(focusedMarketProviderProvenanceEvents.map((record) => record.vendorField))).sort(),
    [focusedMarketProviderProvenanceEvents],
  );

  useEffect(() => {
    setMarketDataProvenanceExportFilter((current) => {
      const nextProvider =
        current.provider !== ALL_FILTER_VALUE
        && !marketDataProvenanceExportProviderOptions.includes(current.provider)
          ? ALL_FILTER_VALUE
          : current.provider;
      const nextVendorField =
        current.vendor_field !== ALL_FILTER_VALUE
        && !marketDataProvenanceExportVendorFieldOptions.includes(current.vendor_field)
          ? ALL_FILTER_VALUE
          : current.vendor_field;
      if (nextProvider === current.provider && nextVendorField === current.vendor_field) {
        return current;
      }
      return {
        ...current,
        provider: nextProvider,
        vendor_field: nextVendorField,
      };
    });
  }, [
    marketDataProvenanceExportProviderOptions,
    marketDataProvenanceExportVendorFieldOptions,
  ]);

  const filteredFocusedMarketProviderProvenanceEvents = useMemo(() => {
    const normalizedSearch = marketDataProvenanceExportFilter.search_query.trim().toLowerCase();
    return focusedMarketProviderProvenanceEvents
      .filter((record) => {
        if (
          marketDataProvenanceExportFilter.provider !== ALL_FILTER_VALUE
          && record.provider !== marketDataProvenanceExportFilter.provider
        ) {
          return false;
        }
        if (
          marketDataProvenanceExportFilter.vendor_field !== ALL_FILTER_VALUE
          && record.vendorField !== marketDataProvenanceExportFilter.vendor_field
        ) {
          return false;
        }
        if (normalizedSearch && !record.searchText.includes(normalizedSearch)) {
          return false;
        }
        return true;
      })
      .slice()
      .sort((left, right) => {
        switch (marketDataProvenanceExportFilter.sort) {
          case "oldest":
            return left.occurredAtMs - right.occurredAtMs || left.event.event_id.localeCompare(right.event.event_id);
          case "provider":
            return (
              left.provider.localeCompare(right.provider)
              || right.occurredAtMs - left.occurredAtMs
              || left.event.event_id.localeCompare(right.event.event_id)
            );
          case "severity":
            return (
              right.severityRank - left.severityRank
              || right.occurredAtMs - left.occurredAtMs
              || left.provider.localeCompare(right.provider)
            );
          case "newest":
          default:
            return right.occurredAtMs - left.occurredAtMs || left.event.event_id.localeCompare(right.event.event_id);
        }
      });
  }, [focusedMarketProviderProvenanceEvents, marketDataProvenanceExportFilter]);

  const focusedMarketWorkflowExportPayload = useMemo(() => {
    if (!activeMarketInstrument || !marketStatus) {
      return null;
    }
    return {
      export_scope: "provider_market_context_provenance",
      export_filter: marketDataProvenanceExportFilter,
      export_filter_summary: formatMarketDataProvenanceExportFilterSummary(
        marketDataProvenanceExportFilter,
      ),
      export_result_count: filteredFocusedMarketProviderProvenanceEvents.length,
      focus: {
        provider: marketStatus.provider,
        venue: marketStatus.venue,
        instrument_id: activeMarketInstrument.instrument_id,
        symbol: resolveMarketDataSymbol(activeMarketInstrument.instrument_id),
        timeframe: activeMarketInstrument.timeframe,
        sync_status: activeMarketInstrument.sync_status,
        linked_alert_count: focusedLinkedOperatorAlerts.length,
        linked_alert_history_count: focusedLinkedOperatorAlertHistory.length,
        linked_incident_count: focusedLinkedOperatorIncidentEvents.length,
        provider_provenance_incident_count: focusedMarketProviderProvenanceCount,
        filtered_provider_provenance_incident_count: filteredFocusedMarketProviderProvenanceEvents.length,
        lineage_snapshot_count: marketDataLineageHistory.length,
        ingestion_job_count: marketDataIngestionJobs.length,
      },
      provider_provenance_available_filters: {
        providers: marketDataProvenanceExportProviderOptions,
        vendor_fields: marketDataProvenanceExportVendorFieldOptions,
      },
      alerts: focusedLinkedOperatorAlerts.map(({ alert, link }) => ({
        alert_id: alert.alert_id,
        severity: alert.severity,
        category: alert.category,
        summary: alert.summary,
        detail: alert.detail,
        detected_at: alert.detected_at,
        status: alert.status,
        source: alert.source,
        delivery_targets: alert.delivery_targets,
        symbol: alert.symbol ?? null,
        symbols: alert.symbols,
        timeframe: alert.timeframe ?? null,
        primary_focus: alert.primary_focus ?? null,
        triage_focus_link: serializeLinkedMarketInstrumentContext(link),
      })),
      alert_history: focusedLinkedOperatorAlertHistory.map(({ alert, link }) => ({
        alert_id: alert.alert_id,
        occurrence_id: alert.occurrence_id ?? null,
        severity: alert.severity,
        category: alert.category,
        summary: alert.summary,
        detail: alert.detail,
        detected_at: alert.detected_at,
        timeline_key: alert.timeline_key ?? null,
        timeline_position: alert.timeline_position ?? null,
        timeline_total: alert.timeline_total ?? null,
        resolved_at: alert.resolved_at ?? null,
        status: alert.status,
        source: alert.source,
        delivery_targets: alert.delivery_targets,
        symbol: alert.symbol ?? null,
        symbols: alert.symbols,
        timeframe: alert.timeframe ?? null,
        primary_focus: alert.primary_focus ?? null,
        triage_focus_link: serializeLinkedMarketInstrumentContext(link),
      })),
      incident_events: focusedLinkedOperatorIncidentEvents.map(({ event, link }) => ({
        event_id: event.event_id,
        alert_id: event.alert_id,
        timestamp: event.timestamp,
        kind: event.kind,
        severity: event.severity,
        summary: event.summary,
        detail: event.detail,
        source: event.source,
        external_provider: event.external_provider ?? null,
        external_reference: event.external_reference ?? null,
        provider_workflow_reference: event.provider_workflow_reference ?? null,
        acknowledgment_state: event.acknowledgment_state,
        escalation_state: event.escalation_state,
        escalation_level: event.escalation_level,
        remediation_state: event.remediation.state,
        triage_focus_link: serializeLinkedMarketInstrumentContext(link),
        provider_recovery: {
          lifecycle_state: event.remediation.provider_recovery.lifecycle_state,
          provider: event.remediation.provider_recovery.provider ?? null,
          job_id: event.remediation.provider_recovery.job_id ?? null,
          reference: event.remediation.provider_recovery.reference ?? null,
          workflow_reference: event.remediation.provider_recovery.workflow_reference ?? null,
          channels: event.remediation.provider_recovery.channels,
          symbols: event.remediation.provider_recovery.symbols,
          timeframe: event.remediation.provider_recovery.timeframe ?? null,
          verification_state: event.remediation.provider_recovery.verification.state,
          market_context_provenance:
            event.remediation.provider_recovery.market_context_provenance ?? null,
          market_context_provenance_fields:
            summarizeProviderRecoveryMarketContextProvenance(event.remediation.provider_recovery)?.fieldSummaries
            ?? [],
          market_context_provenance_summary:
            summarizeProviderRecoveryMarketContextProvenance(event.remediation.provider_recovery)?.summary
            ?? null,
        },
      })),
      provider_provenance_incidents: filteredFocusedMarketProviderProvenanceEvents.map((record) => ({
        event_id: record.event.event_id,
        alert_id: record.event.alert_id,
        timestamp: record.event.timestamp,
        kind: record.event.kind,
        severity: record.event.severity,
        summary: record.event.summary,
        detail: record.event.detail,
        source: record.event.source,
        external_provider: record.event.external_provider ?? null,
        external_reference: record.event.external_reference ?? null,
        provider_workflow_reference: record.event.provider_workflow_reference ?? null,
        triage_focus_link: serializeLinkedMarketInstrumentContext(record.link),
        provider: record.provider,
        vendor_field: record.vendorField,
        provenance_summary: record.provenanceSummary,
        provenance_fields: record.fieldSummaries,
        remediation_provider_recovery: {
          lifecycle_state: record.event.remediation.provider_recovery.lifecycle_state,
          reference: record.event.remediation.provider_recovery.reference ?? null,
          workflow_reference: record.event.remediation.provider_recovery.workflow_reference ?? null,
          symbols: record.event.remediation.provider_recovery.symbols,
          timeframe: record.event.remediation.provider_recovery.timeframe ?? null,
          channels: record.event.remediation.provider_recovery.channels,
        },
      })),
      lineage_history: marketDataLineageHistory,
      ingestion_jobs: marketDataIngestionJobs,
      merged_incident_history: focusedMarketIncidentHistory,
    };
  }, [
    activeMarketInstrument,
    focusedLinkedOperatorAlertHistory,
    focusedLinkedOperatorAlerts,
    focusedLinkedOperatorIncidentEvents,
    filteredFocusedMarketProviderProvenanceEvents,
    focusedMarketIncidentHistory,
    focusedMarketProviderProvenanceCount,
    marketDataProvenanceExportFilter,
    marketDataProvenanceExportProviderOptions,
    marketDataProvenanceExportVendorFieldOptions,
    marketDataIngestionJobs,
    marketDataLineageHistory,
    marketStatus,
  ]);

  const operatorSummary = useMemo(() => {
    if (!operatorVisibility) {
      return null;
    }
    const criticalCount = operatorVisibility.alerts.filter((alert) => alert.severity === "critical").length;
    const warningCount = operatorVisibility.alerts.filter((alert) => alert.severity === "warning").length;
    return {
      alertCount: operatorVisibility.alerts.length,
      criticalCount,
      warningCount,
      historyCount: operatorVisibility.alert_history.length,
      incidentCount: operatorVisibility.incident_events.length,
      deliveryCount: operatorVisibility.delivery_history.length,
      latestAuditAt: operatorVisibility.audit_events[0]?.timestamp ?? null,
    };
  }, [operatorVisibility]);

  const guardedLiveSummary = useMemo(() => {
    if (!guardedLive) {
      return null;
    }
    return {
      blockerCount: guardedLive.blockers.length,
      latestAuditAt: guardedLive.audit_events[0]?.timestamp ?? null,
      latestReconciliationAt: guardedLive.reconciliation.checked_at ?? null,
      latestRecoveryAt: guardedLive.recovery.recovered_at ?? null,
      latestOrderSyncAt: guardedLive.order_book.synced_at ?? guardedLive.ownership.last_order_sync_at ?? null,
      latestSessionRestoreAt: guardedLive.session_restore.restored_at ?? null,
      latestSessionHandoffAt: guardedLive.session_handoff.last_sync_at ?? guardedLive.session_handoff.handed_off_at ?? null,
    };
  }, [guardedLive]);

  const totalTrackedRunCount =
    backtests.length + sandboxRuns.length + paperRuns.length + liveRuns.length;

  const controlStripMetrics = useMemo<ControlStripMetric[]>(
    () => [
      {
        label: "Strategy catalog",
        value: `${strategies.length}`,
        detail: `${strategyGroups.native.length} native · ${strategyGroups.reference.length} reference`,
        tone: "research",
      },
      {
        label: "Tracked runs",
        value: `${totalTrackedRunCount}`,
        detail: `${backtests.length} backtests · ${sandboxRuns.length + paperRuns.length + liveRuns.length} runtime sessions`,
        tone: "runtime",
      },
      {
        label: "Data health",
        value: formatCompletion(backfillSummary?.completionRatio ?? null),
        detail: `${marketStatus?.instruments.length ?? 0} instruments · ${failureSummary?.failureCount24h ?? 0} failures / 24h`,
        tone: (failureSummary?.failureCount24h ?? 0) > 0 ? "warning" : "runtime",
      },
      {
        label: "Guarded live",
        value: guardedLive?.kill_switch.state ?? "n/a",
        detail: `${guardedLiveSummary?.blockerCount ?? 0} blockers · ${operatorSummary?.criticalCount ?? 0} critical alerts`,
        tone: "live",
      },
    ],
    [
      backfillSummary?.completionRatio,
      backtests.length,
      failureSummary?.failureCount24h,
      guardedLive?.kill_switch.state,
      guardedLiveSummary?.blockerCount,
      marketStatus?.instruments.length,
      operatorSummary?.criticalCount,
      paperRuns.length,
      sandboxRuns.length,
      strategies.length,
      strategyGroups.native.length,
      strategyGroups.reference.length,
      totalTrackedRunCount,
      liveRuns.length,
    ],
  );

  const workspaceDescriptors = useMemo<ControlWorkspaceDescriptor[]>(
    () => buildControlWorkspaceDescriptors({
      alertCount: operatorSummary?.alertCount ?? 0,
      backtestsCount: backtests.length,
      blockerCount: guardedLiveSummary?.blockerCount ?? 0,
      instrumentsCount: marketStatus?.instruments.length ?? 0,
      killSwitchState: guardedLive?.kill_switch.state ?? "n/a",
      liveRunsCount: liveRuns.length,
      paperRunsCount: paperRuns.length,
      presetsCount: presets.length,
      referencesCount: references.length,
      sandboxRunsCount: sandboxRuns.length,
      strategiesCount: strategies.length,
      totalTrackedRunCount,
    }),
    [
      backtests.length,
      guardedLive?.kill_switch.state,
      guardedLiveSummary?.blockerCount,
      liveRuns.length,
      marketStatus?.instruments.length,
      operatorSummary?.alertCount,
      paperRuns.length,
      presets.length,
      references.length,
      sandboxRuns.length,
      strategies.length,
      totalTrackedRunCount,
    ],
  );

  const activeWorkspaceDescriptor =
    workspaceDescriptors.find((workspace) => workspace.id === activeWorkspace)
    ?? workspaceDescriptors[0];


  return {
    activeMarketInstrument, focusedMarketWorkflowExportPayload, focusedMarketWorkflowSummary, filteredFocusedMarketProviderProvenanceEvents, focusedMarketProviderProvenanceCount, activeWorkspaceDescriptor,
    controlStripMetrics, workspaceDescriptors, strategyGroups, failureSummary, backfillSummary, operatorSummary,
    autoLinkedMarketInstrumentLink, focusedMultiSymbolPrimaryLink, incidentFocusedInstruments, focusedMarketIncidentHistory, marketDataProvenanceExportProviderOptions, marketDataProvenanceExportVendorFieldOptions,
    providerProvenanceSchedulerCurrent, providerProvenanceSchedulerLagBarMax, providerProvenanceSchedulerDrillDown, providerProvenanceSchedulerRecentHistory, providerProvenanceSchedulerAlertCategoryOptions, providerProvenanceSchedulerAlertStatusOptions,
    providerProvenanceSchedulerAlertNarrativeFacetOptions, providerProvenanceSchedulerAlertTimelineItems, providerProvenanceSchedulerAlertRetrievalClusters, providerProvenanceDriftBarMax, providerProvenanceBurnUpBarMax, linkedOperatorAlertById,
    linkedOperatorIncidentEventById, linkedOperatorAlertHistoryByOccurrenceId, providerProvenanceSchedulerAlertHistoryTimelineByCategory, guardedLiveSummary,
  };
}
