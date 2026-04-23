// @ts-nocheck
import { RuntimeProviderProvenanceAnalyticsWorkspaceSection } from "./RuntimeProviderProvenanceAnalyticsWorkspaceSection";
import { RuntimeProviderProvenanceSchedulerWorkspaceSection } from "./RuntimeProviderProvenanceSchedulerWorkspaceSection";
import { RuntimeProviderProvenanceSharedRegistryAuditSection } from "./RuntimeProviderProvenanceSharedRegistryAuditSection";
import { RuntimeProviderProvenanceWorkspaceCards } from "./RuntimeProviderProvenanceWorkspaceCards";

export function RuntimeProviderProvenanceWorkspaceConsumersSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="provider-provenance-workspace-grid">
        <RuntimeProviderProvenanceWorkspaceCards model={model} />
      </div>
      <RuntimeProviderProvenanceSchedulerWorkspaceSection model={model} />
      <RuntimeProviderProvenanceAnalyticsWorkspaceSection model={model} />
      <RuntimeProviderProvenanceSharedRegistryAuditSection model={model} />
    </>
  );
}
