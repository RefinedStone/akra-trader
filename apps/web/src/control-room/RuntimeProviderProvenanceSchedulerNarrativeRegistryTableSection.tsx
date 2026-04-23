// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerNarrativeRegistryTableViewSection } from "./RuntimeProviderProvenanceSchedulerNarrativeRegistryTableViewSection";

export function RuntimeProviderProvenanceSchedulerNarrativeRegistryTableSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  if (providerProvenanceSchedulerNarrativeRegistryEntriesLoading) {
    return <p className="empty-state">Loading scheduler narrative registry…</p>;
  }

  if (providerProvenanceSchedulerNarrativeRegistryEntriesError) {
    return (
      <p className="market-data-workflow-feedback">
        Scheduler narrative registry load failed: {providerProvenanceSchedulerNarrativeRegistryEntriesError}
      </p>
    );
  }

  return providerProvenanceSchedulerNarrativeRegistryEntries.length ? (
    <RuntimeProviderProvenanceSchedulerNarrativeRegistryTableViewSection model={model} />
  ) : (
    <p className="empty-state">No scheduler narrative registry entries saved yet.</p>
  );
}
