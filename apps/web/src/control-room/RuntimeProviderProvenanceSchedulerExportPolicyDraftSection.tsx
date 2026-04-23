// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerExportPolicyDraftFormSection } from "./RuntimeProviderProvenanceSchedulerExportPolicyDraftFormSection";
import { RuntimeProviderProvenanceSchedulerExportPolicyDraftTargetsSection } from "./RuntimeProviderProvenanceSchedulerExportPolicyDraftTargetsSection";

export function RuntimeProviderProvenanceSchedulerExportPolicyDraftSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceSchedulerExportPolicyDraftFormSection model={model} />
      <RuntimeProviderProvenanceSchedulerExportPolicyDraftTargetsSection model={model} />
    </>
  );
}
