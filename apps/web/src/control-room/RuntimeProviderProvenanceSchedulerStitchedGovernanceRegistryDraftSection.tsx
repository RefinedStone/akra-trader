// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftActionSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftActionSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftDefaultPolicyStageSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftDefaultPolicyStageSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftIdentityStageSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftIdentityStageSection";
import { RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftSearchSection } from "./RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftSearchSection";

export function RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <div className="market-data-provenance-history-head">
        <strong>Stitched report governance registries</strong>
        <p>
          Save the stitched-report-only approval queue slice and default policy layer as
          a dedicated lifecycle object, then reapply or restore it without reopening the
          shared governance workspace.
        </p>
      </div>
      <div className="filter-bar">
        <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftIdentityStageSection
          model={model}
        />
        <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftDefaultPolicyStageSection
          model={model}
        />
        <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftActionSection
          model={model}
        />
      </div>
      <div className="filter-bar">
        <RuntimeProviderProvenanceSchedulerStitchedGovernanceRegistryDraftSearchSection
          model={model}
        />
      </div>
    </>
  );
}
