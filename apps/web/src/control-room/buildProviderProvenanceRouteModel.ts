const PROVIDER_PROVENANCE_ROUTE_MODEL_EXTRAS = new Set([
  "ALL_FILTER_VALUE",
  "KEEP_CURRENT_BULK_GOVERNANCE_VALUE",
  "CLEAR_TEMPLATE_LINK_BULK_GOVERNANCE_VALUE",
  "DEFAULT_PROVIDER_PROVENANCE_SCHEDULER_NARRATIVE_GOVERNANCE_QUEUE_SORT",
  "focusMarketInstrumentFromProviderExport",
  "formatFixedNumber",
  "formatLinkedMarketPrimaryFocusNote",
  "formatParameterMap",
  "formatProviderDriftIntensity",
  "formatProviderRecoverySchema",
  "formatProviderRecoveryTelemetry",
  "formatRange",
  "formatSchedulerLagSeconds",
  "formatTimestamp",
  "formatWorkflowToken",
  "linkedOperatorAlertById",
  "linkedOperatorAlertHistoryByOccurrenceId",
  "linkedOperatorIncidentEventById",
  "shortenIdentifier",
  "summarizeProviderRecoveryMarketContextProvenance",
  "truncateLabel",
]);

function isProviderProvenanceRouteModelKey(key: string) {
  return (
    key.includes("ProviderProvenance") ||
    key.includes("providerProvenance") ||
    PROVIDER_PROVENANCE_ROUTE_MODEL_EXTRAS.has(key)
  );
}

export function buildProviderProvenanceRouteModel<T extends Record<string, unknown>>(source: T) {
  return Object.fromEntries(
    Object.entries(source).filter(([key]) => isProviderProvenanceRouteModelKey(key)),
  );
}
