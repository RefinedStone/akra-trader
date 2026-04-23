// @ts-nocheck
export function RuntimeProviderProvenanceSchedulerStitchedReportApprovalQueueCommitActionMutationTriggerSection({
  disabled,
  label,
  onClick,
}: {
  disabled: boolean;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      className="ghost-button"
      disabled={disabled}
      onClick={onClick}
      type="button"
    >
      {label}
    </button>
  );
}
