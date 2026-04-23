// @ts-nocheck
import { RuntimeProviderProvenanceAnalyticsRecentExportsSection } from "./RuntimeProviderProvenanceAnalyticsRecentExportsSection";
import { RuntimeProviderProvenanceAnalyticsRollupsSection } from "./RuntimeProviderProvenanceAnalyticsRollupsSection";
import { RuntimeProviderProvenanceAnalyticsSummarySection } from "./RuntimeProviderProvenanceAnalyticsSummarySection";
import { RuntimeProviderProvenanceAnalyticsTimeSeriesSection } from "./RuntimeProviderProvenanceAnalyticsTimeSeriesSection";

export function RuntimeProviderProvenanceAnalyticsWorkspaceSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      {providerProvenanceAnalyticsLoading ? (
        <p className="empty-state">Loading provider provenance analytics…</p>
      ) : null}
      {providerProvenanceAnalyticsError ? (
        <p className="market-data-workflow-feedback">
          Provider provenance analytics failed: {providerProvenanceAnalyticsError}
        </p>
      ) : null}
      {providerProvenanceAnalytics ? (
        <>
          <RuntimeProviderProvenanceAnalyticsSummarySection model={model} />
          <RuntimeProviderProvenanceAnalyticsTimeSeriesSection model={model} />
          <RuntimeProviderProvenanceAnalyticsRollupsSection model={model} />
          <RuntimeProviderProvenanceAnalyticsRecentExportsSection model={model} />
        </>
      ) : null}
    </>
  );
}
