// @ts-nocheck
import { RuntimeProviderProvenanceGovernancePolicyCatalogBulkDefaultTemplateStageSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogBulkDefaultTemplateStageSection";
import { RuntimeProviderProvenanceGovernancePolicyCatalogBulkDescriptionStageSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogBulkDescriptionStageSection";
import { RuntimeProviderProvenanceGovernancePolicyCatalogBulkNameStageSection } from "./RuntimeProviderProvenanceGovernancePolicyCatalogBulkNameStageSection";

export function RuntimeProviderProvenanceGovernancePolicyCatalogBulkMetadataStageSection({
  model,
}: {
  model: any;
}) {
  const {} = model;

  return (
    <>
      <RuntimeProviderProvenanceGovernancePolicyCatalogBulkNameStageSection model={model} />
      <RuntimeProviderProvenanceGovernancePolicyCatalogBulkDescriptionStageSection model={model} />
      <RuntimeProviderProvenanceGovernancePolicyCatalogBulkDefaultTemplateStageSection model={model} />
    </>
  );
}
