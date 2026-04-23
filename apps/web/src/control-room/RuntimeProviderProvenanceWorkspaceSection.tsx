// @ts-nocheck
import { RuntimeProviderProvenanceWorkspaceConsumersSection } from "./RuntimeProviderProvenanceWorkspaceConsumersSection";
import { RuntimeProviderProvenanceWorkspaceQuerySurfaceSection } from "./RuntimeProviderProvenanceWorkspaceQuerySurfaceSection";

export function RuntimeProviderProvenanceWorkspaceSection({ model }: { model: any }) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceWorkspaceQuerySurfaceSection model={model} />
      <RuntimeProviderProvenanceWorkspaceConsumersSection model={model} />
    </>
  );
}
