// @ts-nocheck
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSearchInputBindingSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSearchInputBindingSection";
import { RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSearchInputFieldSection } from "./RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSearchInputFieldSection";

export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueQueryInputSection({ model }: { model: any }) {
  return (
    <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSearchInputBindingSection model={model}>
      {({
        onChange,
        value,
      }: {
        onChange: (event: any) => void;
        value: string;
      }) => (
        <RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSearchInputFieldSection
          onChange={onChange}
          value={value}
        />
      )}
    </RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSearchInputBindingSection>
  );
}
