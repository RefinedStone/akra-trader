// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerAutomationDailyTrendsSection } from "./RuntimeProviderProvenanceSchedulerAutomationDailyTrendsSection";
import { RuntimeProviderProvenanceSchedulerAutomationDrillDownSection } from "./RuntimeProviderProvenanceSchedulerAutomationDrillDownSection";
import { RuntimeProviderProvenanceSchedulerAutomationOverviewSection } from "./RuntimeProviderProvenanceSchedulerAutomationOverviewSection";
import { RuntimeProviderProvenanceSchedulerAutomationRecentHistorySection } from "./RuntimeProviderProvenanceSchedulerAutomationRecentHistorySection";

export function RuntimeProviderProvenanceSchedulerAutomationSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerAutomationOverviewSection model={model} />
      <RuntimeProviderProvenanceSchedulerAutomationDailyTrendsSection model={model} />
      <RuntimeProviderProvenanceSchedulerAutomationDrillDownSection model={model} />
      <RuntimeProviderProvenanceSchedulerAutomationRecentHistorySection model={model} />
    </>
  );
}
