// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueSearchInputFieldSection({
  value,
  onChange,
}: {
  value: string;
  onChange: (event: any) => void;
}) {
  return (
    <label>
      <span>Search</span>
      <input
        onChange={onChange}
        placeholder="plan, view, policy"
        type="text"
        value={value}
      />
    </label>
  );
}
