import { useMemo, useRef, useState } from "react";

import type { RunSurfaceCollectionQueryContract } from "../../controlRoomDefinitions";
import {
  RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID,
  getCollectionQuerySchemaId,
  getRunSurfaceCollectionQueryExpressionAuthoring,
  getRunSurfaceCollectionQueryParameterDomains,
  getRunSurfaceCollectionQuerySchemas,
} from "./model";
import type {
  HydratedRunSurfaceCollectionQueryBuilderState,
  RunSurfaceCollectionQueryBuilderChildState,
  RunSurfaceCollectionQueryBuilderEditorTarget,
  RunSurfaceCollectionQueryBuilderPredicateState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateState,
} from "./model";

export function useQueryBuilderAuthoringState(contracts: RunSurfaceCollectionQueryContract[]) {
  const [activeContractKey, setActiveContractKey] = useState<string>(contracts[0]?.contract_key ?? "");
  const lastHydratedExpressionRef = useRef<string | null>(null);
  const [pendingHydratedState, setPendingHydratedState] =
    useState<HydratedRunSurfaceCollectionQueryBuilderState | null>(null);
  const [expressionMode, setExpressionMode] = useState<"single" | "grouped">("single");
  const [groupLogic, setGroupLogic] = useState<"and" | "or">("and");
  const [rootNegated, setRootNegated] = useState(false);
  const [expressionChildren, setExpressionChildren] = useState<RunSurfaceCollectionQueryBuilderChildState[]>([]);
  const [predicates, setPredicates] = useState<RunSurfaceCollectionQueryBuilderPredicateState[]>([]);
  const [predicateTemplates, setPredicateTemplates] = useState<RunSurfaceCollectionQueryBuilderPredicateTemplateState[]>([]);
  const [selectedGroupId, setSelectedGroupId] = useState<string>(RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID);
  const [editorTarget, setEditorTarget] = useState<RunSurfaceCollectionQueryBuilderEditorTarget>({ kind: "draft" });
  const [predicateDraftKey, setPredicateDraftKey] = useState("");
  const [templateDraftKey, setTemplateDraftKey] = useState("");
  const [predicateRefDraftKey, setPredicateRefDraftKey] = useState("");
  const [predicateRefDraftBindings, setPredicateRefDraftBindings] = useState<Record<string, string>>({});
  const [templateDraftAuthoringTarget, setTemplateDraftAuthoringTarget] = useState<"clause" | "subtree">("clause");
  const [templateParameterDraftDefaultsByContext, setTemplateParameterDraftDefaultsByContext] =
    useState<Record<string, Record<string, string>>>({});
  const [templateParameterDraftLabelsByContext, setTemplateParameterDraftLabelsByContext] =
    useState<Record<string, Record<string, string>>>({});
  const [templateParameterDraftGroupsByContext, setTemplateParameterDraftGroupsByContext] =
    useState<Record<string, Record<string, string>>>({});
  const [templateParameterDraftHelpNotesByContext, setTemplateParameterDraftHelpNotesByContext] =
    useState<Record<string, Record<string, string>>>({});
  const [templateParameterGroupDraftMetadataByContext, setTemplateParameterGroupDraftMetadataByContext] =
    useState<Record<string, Record<string, Omit<RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState, "key">>>>({});
  const [templateParameterDraftBindingPresetsByContext, setTemplateParameterDraftBindingPresetsByContext] =
    useState<Record<string, Record<string, string>>>({});
  const [templateParameterDraftOrderByContext, setTemplateParameterDraftOrderByContext] =
    useState<Record<string, string[]>>({});
  const [templateGroupExpansionByKey, setTemplateGroupExpansionByKey] = useState<Record<string, boolean>>({});
  const [predicateRefGroupBundleSelections, setPredicateRefGroupBundleSelections] =
    useState<Record<string, string>>({});
  const [predicateRefGroupAutoBundleSelections, setPredicateRefGroupAutoBundleSelections] =
    useState<Record<string, string>>({});
  const [bundleCoordinationSimulationScope, setBundleCoordinationSimulationScope] =
    useState<"all" | string>("all");
  const [bundleCoordinationSimulationPolicy, setBundleCoordinationSimulationPolicy] =
    useState<RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState["coordinationPolicy"] | "current">("current");
  const [bundleCoordinationSimulationReplayIndex, setBundleCoordinationSimulationReplayIndex] =
    useState(0);
  const [bundleCoordinationSimulationReplayGroupFilter, setBundleCoordinationSimulationReplayGroupFilter] =
    useState<"all" | string>("all");
  const [bundleCoordinationSimulationReplayActionTypeFilter, setBundleCoordinationSimulationReplayActionTypeFilter] =
    useState<"all" | "manual_anchor" | "dependency_selection" | "direct_auto_selection" | "conflict_blocked" | "idle">("all");
  const [bundleCoordinationSimulationReplayEdgeFilter, setBundleCoordinationSimulationReplayEdgeFilter] =
    useState<"all" | string>("all");
  const [bundleCoordinationSimulationPromotionDecisionsByGroupKey, setBundleCoordinationSimulationPromotionDecisionsByGroupKey] =
    useState<Record<string, boolean>>({});
  const [bundleCoordinationSimulationApprovalOpen, setBundleCoordinationSimulationApprovalOpen] =
    useState(false);
  const [bundleCoordinationSimulationApprovalDiffOnly, setBundleCoordinationSimulationApprovalDiffOnly] =
    useState(true);
  const [bundleCoordinationSimulationApprovalDecisionsByGroupKey, setBundleCoordinationSimulationApprovalDecisionsByGroupKey] =
    useState<Record<string, boolean>>({});
  const [bundleCoordinationSimulationFinalSummaryOpen, setBundleCoordinationSimulationFinalSummaryOpen] =
    useState(false);
  const [activeSchemaId, setActiveSchemaId] = useState<string>("");
  const [parameterValues, setParameterValues] = useState<Record<string, string>>({});
  const [parameterBindingKeys, setParameterBindingKeys] = useState<Record<string, string>>({});
  const [quantifier, setQuantifier] = useState<"any" | "all" | "none">("any");
  const [activeFieldKey, setActiveFieldKey] = useState<string>("");
  const [activeOperatorKey, setActiveOperatorKey] = useState<string>("");
  const [builderValue, setBuilderValue] = useState<string>("");
  const [valueBindingKey, setValueBindingKey] = useState("");
  const [editorNegated, setEditorNegated] = useState(false);

  const activeContract = useMemo(
    () => contracts.find((contract) => contract.contract_key === activeContractKey) ?? contracts[0] ?? null,
    [activeContractKey, contracts],
  );
  const expressionAuthoring = useMemo(
    () => getRunSurfaceCollectionQueryExpressionAuthoring(activeContract),
    [activeContract],
  );
  const collectionSchemas = useMemo(
    () => getRunSurfaceCollectionQuerySchemas(activeContract),
    [activeContract],
  );
  const parameterDomains = useMemo(
    () => getRunSurfaceCollectionQueryParameterDomains(activeContract),
    [activeContract],
  );
  const activeSchema = useMemo(
    () =>
      collectionSchemas.find((schema) => getCollectionQuerySchemaId(schema) === activeSchemaId) ??
      collectionSchemas[0] ??
      null,
    [activeSchemaId, collectionSchemas],
  );
  const activeField = useMemo(
    () => activeSchema?.elementSchema.find((field) => field.key === activeFieldKey) ?? activeSchema?.elementSchema[0] ?? null,
    [activeFieldKey, activeSchema],
  );
  const activeOperator = useMemo(
    () => activeField?.operators.find((operator) => operator.key === activeOperatorKey) ?? activeField?.operators[0] ?? null,
    [activeField, activeOperatorKey],
  );

  return {
    activeContract,
    activeContractKey,
    activeField,
    activeFieldKey,
    activeOperator,
    activeOperatorKey,
    activeSchema,
    activeSchemaId,
    builderValue,
    bundleCoordinationSimulationApprovalDecisionsByGroupKey,
    bundleCoordinationSimulationApprovalDiffOnly,
    bundleCoordinationSimulationApprovalOpen,
    bundleCoordinationSimulationFinalSummaryOpen,
    bundleCoordinationSimulationPolicy,
    bundleCoordinationSimulationPromotionDecisionsByGroupKey,
    bundleCoordinationSimulationReplayActionTypeFilter,
    bundleCoordinationSimulationReplayEdgeFilter,
    bundleCoordinationSimulationReplayGroupFilter,
    bundleCoordinationSimulationReplayIndex,
    bundleCoordinationSimulationScope,
    editorNegated,
    editorTarget,
    expressionAuthoring,
    expressionChildren,
    expressionMode,
    groupLogic,
    lastHydratedExpressionRef,
    parameterBindingKeys,
    parameterDomains,
    parameterValues,
    pendingHydratedState,
    predicateDraftKey,
    predicateRefGroupAutoBundleSelections,
    predicateRefGroupBundleSelections,
    predicateRefDraftBindings,
    predicateRefDraftKey,
    predicateTemplates,
    predicates,
    quantifier,
    rootNegated,
    selectedGroupId,
    setActiveContractKey,
    setActiveFieldKey,
    setActiveOperatorKey,
    setActiveSchemaId,
    setBuilderValue,
    setBundleCoordinationSimulationApprovalDecisionsByGroupKey,
    setBundleCoordinationSimulationApprovalDiffOnly,
    setBundleCoordinationSimulationApprovalOpen,
    setBundleCoordinationSimulationFinalSummaryOpen,
    setBundleCoordinationSimulationPolicy,
    setBundleCoordinationSimulationPromotionDecisionsByGroupKey,
    setBundleCoordinationSimulationReplayActionTypeFilter,
    setBundleCoordinationSimulationReplayEdgeFilter,
    setBundleCoordinationSimulationReplayGroupFilter,
    setBundleCoordinationSimulationReplayIndex,
    setBundleCoordinationSimulationScope,
    setEditorNegated,
    setEditorTarget,
    setExpressionChildren,
    setExpressionMode,
    setGroupLogic,
    setParameterBindingKeys,
    setParameterValues,
    setPendingHydratedState,
    setPredicateDraftKey,
    setPredicateRefGroupAutoBundleSelections,
    setPredicateRefGroupBundleSelections,
    setPredicateRefDraftBindings,
    setPredicateRefDraftKey,
    setPredicateTemplates,
    setPredicates,
    setQuantifier,
    setRootNegated,
    setSelectedGroupId,
    setTemplateDraftAuthoringTarget,
    setTemplateParameterDraftBindingPresetsByContext,
    setTemplateParameterDraftDefaultsByContext,
    setTemplateParameterDraftGroupsByContext,
    setTemplateParameterDraftHelpNotesByContext,
    setTemplateDraftKey,
    setTemplateParameterDraftLabelsByContext,
    setTemplateParameterDraftOrderByContext,
    setTemplateGroupExpansionByKey,
    setTemplateParameterGroupDraftMetadataByContext,
    templateDraftAuthoringTarget,
    templateDraftKey,
    templateGroupExpansionByKey,
    templateParameterDraftBindingPresetsByContext,
    templateParameterDraftDefaultsByContext,
    templateParameterDraftGroupsByContext,
    templateParameterDraftHelpNotesByContext,
    templateParameterDraftLabelsByContext,
    templateParameterDraftOrderByContext,
    templateParameterGroupDraftMetadataByContext,
  };
}
