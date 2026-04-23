// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueueActionDispatchSection({
  model,
  plan,
  children,
}: {
  model: any;
  plan: any;
  children: any;
}) {
  const { reviewProviderProvenanceSchedulerStitchedReportGovernancePlanInSharedQueue } = model;

  const onClick = () => {
    reviewProviderProvenanceSchedulerStitchedReportGovernancePlanInSharedQueue(plan);
  };

  return children({ onClick });
}
