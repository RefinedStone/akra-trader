// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueueActionDispatchSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueueActionDispatchSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueueActionStatusViewSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueueActionStatusViewSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueueActionSection({
  model,
  plan,
}: {
  model: any;
  plan: any;
}) {
  return (
    <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueueActionDispatchSection
      model={model}
      plan={plan}
    >
      {({ onClick }: { onClick: () => void }) => (
        <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueueActionStatusViewSection
          model={model}
          onClick={onClick}
          plan={plan}
        />
      )}
    </RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueueActionDispatchSection>
  );
}
