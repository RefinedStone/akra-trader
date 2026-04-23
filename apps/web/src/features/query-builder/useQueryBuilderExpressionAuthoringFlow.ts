import { useCallback, type Dispatch, type RefObject, type SetStateAction, useMemo } from "react";

import type {
  RunSurfaceCollectionQueryContract,
  RunSurfaceCollectionQueryElementField,
  RunSurfaceCollectionQueryExpressionAuthoring,
  RunSurfaceCollectionQuerySchema,
} from "../../controlRoomDefinitions";
import type {
  HydratedRunSurfaceCollectionQueryBuilderState,
  RunSurfaceCollectionQueryBuilderApplyPayload,
  RunSurfaceCollectionQueryBuilderChildState,
  RunSurfaceCollectionQueryBuilderClauseState,
  RunSurfaceCollectionQueryBuilderEditorTarget,
  RunSurfaceCollectionQueryBuilderGroupState,
  RunSurfaceCollectionQueryBuilderPredicateRefState,
  RunSurfaceCollectionQueryBuilderPredicateState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState,
  RunSurfaceCollectionQueryBuilderPredicateTemplateState,
} from "./model";
import {
  addRunSurfaceCollectionQueryBuilderChildToGroup,
  buildRunSurfaceCollectionQueryBuilderEntityId,
  buildRunSurfaceCollectionQueryBuilderNodeFromChild,
  buildRunSurfaceCollectionQueryBuilderNodeFromClause,
  cloneRunSurfaceCollectionQueryBuilderChildState,
  coerceCollectionQueryBuilderValue,
  collectRunSurfaceCollectionQueryBuilderTemplateParameters,
  countRunSurfaceCollectionQueryBuilderChildren,
  getCollectionQuerySchemaId,
  groupRunSurfaceCollectionQueryBuilderTemplateParameters,
  mergeRunSurfaceCollectionQueryBuilderTemplateGroups,
  mergeRunSurfaceCollectionQueryBuilderTemplateParameters,
  removeRunSurfaceCollectionQueryBuilderChild,
  removeRunSurfaceCollectionQueryBuilderPredicateRefs,
  replaceRunSurfaceCollectionQueryBuilderPredicateRefs,
  resolveCollectionQueryPath,
  RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID,
  toRunSurfaceCollectionQueryBindingReferenceValue,
  updateRunSurfaceCollectionQueryBuilderClause,
} from "./model";

type UseQueryBuilderExpressionAuthoringFlowArgs = {
  activeField: RunSurfaceCollectionQueryElementField | null;
  activeOperator: RunSurfaceCollectionQueryElementField["operators"][number] | null;
  activeSchema: RunSurfaceCollectionQuerySchema | null;
  builderEditorCardRef: RefObject<HTMLDivElement | null>;
  builderValue: string;
  clauseEditableTemplateParameterGroups: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState[];
  clauseEditableTemplateParameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
  contracts: RunSurfaceCollectionQueryContract[];
  editorClauseState: HydratedRunSurfaceCollectionQueryBuilderState | null;
  editorNegated: boolean;
  editorTarget: RunSurfaceCollectionQueryBuilderEditorTarget;
  expressionAuthoring: RunSurfaceCollectionQueryExpressionAuthoring;
  expressionChildren: RunSurfaceCollectionQueryBuilderChildState[];
  expressionMode: "grouped" | "single";
  groupLogic: "and" | "or";
  onApplyExpression?: (payload: RunSurfaceCollectionQueryBuilderApplyPayload) => void;
  parameterBindingKeys: Record<string, string>;
  parameterValues: Record<string, string>;
  predicateDraftKey: string;
  predicateRefDraftBindings: Record<string, string>;
  predicateRefDraftKey: string;
  predicateTemplates: RunSurfaceCollectionQueryBuilderPredicateTemplateState[];
  predicates: RunSurfaceCollectionQueryBuilderPredicateState[];
  quantifier: "any" | "all" | "none";
  rootNegated: boolean;
  selectedGroupId: string;
  selectedPredicate: RunSurfaceCollectionQueryBuilderPredicateState | null;
  selectedRefTemplate: RunSurfaceCollectionQueryBuilderPredicateTemplateState | null;
  selectedSubtreeNode: RunSurfaceCollectionQueryBuilderChildState | null;
  selectedTemplate: RunSurfaceCollectionQueryBuilderPredicateTemplateState | null;
  setActiveContractKey: (value: string) => void;
  setClauseReevaluationPreviewSelection: (value: {
    diffItemKey: string | null;
    groupKey: string | null;
    traceKey: string | null;
  }) => void;
  setEditorTarget: (value: RunSurfaceCollectionQueryBuilderEditorTarget) => void;
  setExpressionChildren: Dispatch<SetStateAction<RunSurfaceCollectionQueryBuilderChildState[]>>;
  setExpressionMode: (value: "grouped" | "single") => void;
  setPendingHydratedState: (value: HydratedRunSurfaceCollectionQueryBuilderState | null) => void;
  setPinnedRuntimeCandidateClauseOriginKey: (value: string | null) => void;
  setPredicateDraftKey: (value: string) => void;
  setPredicateTemplates: Dispatch<SetStateAction<RunSurfaceCollectionQueryBuilderPredicateTemplateState[]>>;
  setPredicates: Dispatch<SetStateAction<RunSurfaceCollectionQueryBuilderPredicateState[]>>;
  setSelectedGroupId: (value: string) => void;
  setTemplateDraftKey: (value: string) => void;
  subtreeEditableTemplateParameterGroups: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState[];
  subtreeEditableTemplateParameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[];
  templateDraftKey: string;
  valueBindingKey: string;
};

export function useQueryBuilderExpressionAuthoringFlow({
  activeField,
  activeOperator,
  activeSchema,
  builderEditorCardRef,
  builderValue,
  clauseEditableTemplateParameterGroups,
  clauseEditableTemplateParameters,
  contracts,
  editorClauseState,
  editorNegated,
  editorTarget,
  expressionAuthoring,
  expressionChildren,
  expressionMode,
  groupLogic,
  onApplyExpression,
  parameterBindingKeys,
  parameterValues,
  predicateDraftKey,
  predicateRefDraftBindings,
  predicateRefDraftKey,
  predicateTemplates,
  predicates,
  quantifier,
  rootNegated,
  selectedGroupId,
  selectedPredicate,
  selectedRefTemplate,
  selectedSubtreeNode,
  selectedTemplate,
  setActiveContractKey,
  setClauseReevaluationPreviewSelection,
  setEditorTarget,
  setExpressionChildren,
  setExpressionMode,
  setPendingHydratedState,
  setPinnedRuntimeCandidateClauseOriginKey,
  setPredicateDraftKey,
  setPredicateTemplates,
  setPredicates,
  setSelectedGroupId,
  setTemplateDraftKey,
  subtreeEditableTemplateParameterGroups,
  subtreeEditableTemplateParameters,
  templateDraftKey,
  valueBindingKey,
}: UseQueryBuilderExpressionAuthoringFlowArgs) {
  const resolvedCollectionPath = useMemo(
    () => (activeSchema ? resolveCollectionQueryPath(activeSchema.pathTemplate, parameterValues) : []),
    [activeSchema, parameterValues],
  );
  const expressionLabel = useMemo(() => {
    if (!activeSchema || !activeField || !activeOperator) {
      return "";
    }
    const templateMarkers = [
      ...Object.values(parameterBindingKeys).filter(Boolean).map((bindingKey) => `$${bindingKey}`),
      ...(valueBindingKey ? [`$${valueBindingKey}`] : []),
    ];
    return `${editorNegated ? "not " : ""}${activeSchema.label} · ${quantifier} ${activeField.title ?? activeField.key} ${activeOperator.label || activeOperator.key}${templateMarkers.length ? ` · binds ${templateMarkers.join(", ")}` : ""}`;
  }, [
    activeField,
    activeOperator,
    activeSchema,
    editorNegated,
    parameterBindingKeys,
    quantifier,
    valueBindingKey,
  ]);
  const singleExpressionPreview = useMemo(() => {
    if (!editorClauseState) {
      return "";
    }
    const node = buildRunSurfaceCollectionQueryBuilderNodeFromClause(editorClauseState, contracts);
    return node ? JSON.stringify(node, null, 2) : "";
  }, [contracts, editorClauseState]);
  const groupedExpressionPreview = useMemo(() => {
    const predicateRegistry = Object.fromEntries(
      predicates.flatMap((predicate) => {
        const node = buildRunSurfaceCollectionQueryBuilderNodeFromChild(
          predicate.node,
          contracts,
          expressionAuthoring,
          predicateTemplates,
        );
        return node ? [[predicate.key, node]] : [];
      }),
    );
    const predicateTemplateRegistry = Object.fromEntries(
      predicateTemplates.flatMap((template) => {
        const node = buildRunSurfaceCollectionQueryBuilderNodeFromChild(
          template.node,
          contracts,
          expressionAuthoring,
          predicateTemplates,
        );
        if (!node) {
          return [];
        }
        const serializedParameters = template.parameters.some(
          (parameter) =>
            parameter.defaultValue.trim()
            || parameter.customLabel.trim()
            || parameter.groupName.trim()
            || parameter.helpNote.trim()
            || parameter.bindingPreset.trim(),
        )
          ? Object.fromEntries(
              template.parameters.map((parameter) => [
                parameter.key,
                {
                  ...(parameter.defaultValue.trim()
                    ? {
                        default: coerceCollectionQueryBuilderValue(
                          parameter.defaultValue,
                          parameter.valueType,
                        ),
                      }
                    : {}),
                  ...(parameter.customLabel.trim()
                    ? { label: parameter.customLabel.trim() }
                    : {}),
                  ...(parameter.groupName.trim()
                    ? { group: parameter.groupName.trim() }
                    : {}),
                  ...(parameter.helpNote.trim()
                    ? { help_note: parameter.helpNote.trim() }
                    : {}),
                  ...(parameter.bindingPreset.trim()
                    ? { binding_preset: parameter.bindingPreset.trim() }
                    : {}),
                },
              ]),
            )
          : template.parameters.map((parameter) => parameter.key);
        const serializedParameterGroups = template.parameterGroups.length
          ? Object.fromEntries(
              template.parameterGroups.map((group) => [
                group.key,
                {
                  label: group.label,
                  ...(group.helpNote.trim()
                    ? { help_note: group.helpNote.trim() }
                    : {}),
                  ...(group.collapsedByDefault ? { collapsed: true } : {}),
                  ...(group.visibilityRule !== "always"
                    ? { visibility_rule: group.visibilityRule }
                    : {}),
                  ...(group.coordinationPolicy !== "manual_source_priority"
                    ? { coordination_policy: group.coordinationPolicy }
                    : {}),
                  ...(group.presetBundles.length
                    ? {
                        preset_bundles: Object.fromEntries(
                          group.presetBundles.map((bundle) => [
                            bundle.key,
                            {
                              label: bundle.label,
                              ...(bundle.helpNote.trim()
                                ? { help_note: bundle.helpNote.trim() }
                                : {}),
                              ...(bundle.priority
                                ? { priority: bundle.priority }
                                : {}),
                              ...(bundle.autoSelectRule !== "manual"
                                ? { auto_select_rule: bundle.autoSelectRule }
                                : {}),
                              ...(bundle.dependencies.length
                                ? {
                                    depends_on: Object.fromEntries(
                                      bundle.dependencies.flatMap((dependency) =>
                                        dependency.groupKey.trim() && dependency.bundleKey.trim()
                                          ? [[dependency.key, {
                                              group_key: dependency.groupKey.trim(),
                                              bundle_key: dependency.bundleKey.trim(),
                                            }]]
                                          : [],
                                      ),
                                    ),
                                  }
                                : {}),
                              ...(Object.keys(bundle.parameterValues).length
                                ? {
                                    values: Object.fromEntries(
                                      Object.entries(bundle.parameterValues).map(([parameterKey, value]) => [
                                        parameterKey,
                                        coerceCollectionQueryBuilderValue(value, "string"),
                                      ]),
                                    ),
                                  }
                                : {}),
                              ...(Object.keys(bundle.parameterBindingPresets).length
                                ? {
                                    binding_presets: Object.fromEntries(
                                      Object.entries(bundle.parameterBindingPresets).flatMap(([parameterKey, value]) =>
                                        value.trim() ? [[parameterKey, value.trim()]] : [],
                                      ),
                                    ),
                                  }
                                : {}),
                            },
                          ]),
                        ),
                      }
                    : {}),
                },
              ]),
            )
          : undefined;
        return [[template.key, {
          [expressionAuthoring.predicateTemplates.templateField]: node,
          [expressionAuthoring.predicateTemplates.parametersField]: serializedParameters,
          ...(serializedParameterGroups
            ? { parameter_groups: serializedParameterGroups }
            : {}),
        }]];
      }),
    );
    const rootChildren = expressionChildren.reduce<Record<string, unknown>[]>((accumulator, child) => {
      const node = buildRunSurfaceCollectionQueryBuilderNodeFromChild(
        child,
        contracts,
        expressionAuthoring,
        predicateTemplates,
      );
      if (node) {
        accumulator.push(node);
      }
      return accumulator;
    }, []);
    if (!rootChildren.length) {
      return "";
    }
    const rootNode = {
      ...(rootNegated ? { negated: true } : {}),
      logic: groupLogic,
      children: rootChildren,
    };
    const payload = (
      Object.keys(predicateRegistry).length
      || Object.keys(predicateTemplateRegistry).length
    )
      ? {
          ...(Object.keys(predicateRegistry).length
            ? { [expressionAuthoring.predicateRefs.registryField]: predicateRegistry }
            : {}),
          ...(Object.keys(predicateTemplateRegistry).length
            ? { [expressionAuthoring.predicateTemplates.registryField]: predicateTemplateRegistry }
            : {}),
          root: rootNode,
        }
      : rootNode;
    return JSON.stringify(payload, null, 2);
  }, [
    contracts,
    expressionAuthoring,
    expressionChildren,
    groupLogic,
    predicateTemplates,
    predicates,
    rootNegated,
  ]);
  const filterExpressionPreview =
    expressionMode === "grouped" ? groupedExpressionPreview : singleExpressionPreview;
  const activeEditorTargetLabel = useMemo(() => {
    if (editorTarget.kind === "expression_clause") {
      return "Editing expression clause";
    }
    if (editorTarget.kind === "predicate") {
      const predicate = predicates.find((entry) => entry.id === editorTarget.predicateId);
      return predicate ? `Editing predicate ${predicate.key}` : "Editing predicate";
    }
    if (editorTarget.kind === "template") {
      const template = predicateTemplates.find((entry) => entry.id === editorTarget.templateId);
      return template ? `Editing template ${template.key}` : "Editing template";
    }
    return expressionMode === "grouped" ? "Draft clause" : "Single-node clause";
  }, [editorTarget, expressionMode, predicateTemplates, predicates]);
  const groupedExpressionLabel = useMemo(() => {
    const counts = countRunSurfaceCollectionQueryBuilderChildren(expressionChildren);
    const parts = [`${rootNegated ? "NOT " : ""}${groupLogic.toUpperCase()} expression`];
    if (counts.clauses) {
      parts.push(`${counts.clauses} clause${counts.clauses === 1 ? "" : "s"}`);
    }
    if (counts.predicateRefs) {
      parts.push(`${counts.predicateRefs} predicate ref${counts.predicateRefs === 1 ? "" : "s"}`);
    }
    if (counts.groups) {
      parts.push(`${counts.groups} subgroup${counts.groups === 1 ? "" : "s"}`);
    }
    if (predicates.length) {
      parts.push(`${predicates.length} predicate definition${predicates.length === 1 ? "" : "s"}`);
    }
    if (predicateTemplates.length) {
      parts.push(`${predicateTemplates.length} template${predicateTemplates.length === 1 ? "" : "s"}`);
    }
    return parts.join(" · ");
  }, [expressionChildren, groupLogic, predicateTemplates.length, predicates.length, rootNegated]);
  const canApplyExpression = expressionMode === "grouped"
    ? Boolean(groupedExpressionPreview)
    : (builderValue.trim().length > 0 || Boolean(valueBindingKey.trim())) && Boolean(singleExpressionPreview);
  const setEditorFromClause = useCallback(
    (clause: HydratedRunSurfaceCollectionQueryBuilderState) => {
      setActiveContractKey(clause.contractKey);
      setPendingHydratedState(clause);
    },
    [setActiveContractKey, setPendingHydratedState],
  );
  const focusRuntimeCandidateClauseEditor = useCallback(
    (
      clause: HydratedRunSurfaceCollectionQueryBuilderState | null,
      originTraceKey?: string | null,
      previewGroupKey?: string | null,
    ) => {
      if (!clause) {
        return;
      }
      setEditorTarget({ kind: "draft" });
      setPredicateDraftKey("");
      setTemplateDraftKey("");
      setPinnedRuntimeCandidateClauseOriginKey(originTraceKey ?? null);
      setClauseReevaluationPreviewSelection({
        diffItemKey: null,
        groupKey: previewGroupKey ?? null,
        traceKey: originTraceKey ?? null,
      });
      setEditorFromClause(clause);
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          builderEditorCardRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        });
      });
    },
    [
      builderEditorCardRef,
      setClauseReevaluationPreviewSelection,
      setEditorFromClause,
      setEditorTarget,
      setPinnedRuntimeCandidateClauseOriginKey,
      setPredicateDraftKey,
      setTemplateDraftKey,
    ],
  );
  const applyCurrentExpression = useCallback(() => {
    if (!onApplyExpression || !filterExpressionPreview) {
      return;
    }
    onApplyExpression({
      expression: filterExpressionPreview,
      expressionLabel: expressionMode === "grouped" ? groupedExpressionLabel : expressionLabel,
      resolvedPath: resolvedCollectionPath,
      quantifier,
      fieldKey: activeField?.key ?? "",
      operatorKey: activeOperator?.key ?? "",
    });
  }, [
    activeField?.key,
    activeOperator?.key,
    expressionLabel,
    expressionMode,
    filterExpressionPreview,
    groupedExpressionLabel,
    onApplyExpression,
    quantifier,
    resolvedCollectionPath,
  ]);
  const addClauseToExpression = useCallback(() => {
    if (!editorClauseState) {
      return;
    }
    const nextChild: RunSurfaceCollectionQueryBuilderClauseState = {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
      kind: "clause",
      clause: editorClauseState,
    };
    setExpressionChildren((current) =>
      selectedGroupId === RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID
        ? [...current, nextChild]
        : addRunSurfaceCollectionQueryBuilderChildToGroup(current, selectedGroupId, nextChild),
    );
    setExpressionMode("grouped");
    setEditorTarget({ kind: "draft" });
  }, [
    editorClauseState,
    selectedGroupId,
    setEditorTarget,
    setExpressionChildren,
    setExpressionMode,
  ]);
  const addGroupToExpression = useCallback(() => {
    const nextGroup: RunSurfaceCollectionQueryBuilderGroupState = {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("group"),
      kind: "group",
      logic: "and",
      negated: false,
      children: [],
    };
    setExpressionChildren((current) =>
      selectedGroupId === RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID
        ? [...current, nextGroup]
        : addRunSurfaceCollectionQueryBuilderChildToGroup(current, selectedGroupId, nextGroup),
    );
    setExpressionMode("grouped");
    setSelectedGroupId(nextGroup.id);
  }, [
    selectedGroupId,
    setExpressionChildren,
    setExpressionMode,
    setSelectedGroupId,
  ]);
  const buildTemplateStateFromNode = useCallback((
    key: string,
    node: RunSurfaceCollectionQueryBuilderChildState,
    existingParameters: RunSurfaceCollectionQueryBuilderPredicateTemplateParameterState[] = [],
    existingParameterGroups: RunSurfaceCollectionQueryBuilderPredicateTemplateGroupState[] = [],
  ): RunSurfaceCollectionQueryBuilderPredicateTemplateState => {
    const mergedParameters = mergeRunSurfaceCollectionQueryBuilderTemplateParameters(
      collectRunSurfaceCollectionQueryBuilderTemplateParameters(node, contracts, predicateTemplates),
      existingParameters,
    );
    return {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("template"),
      key,
      parameters: mergedParameters,
      parameterGroups: mergeRunSurfaceCollectionQueryBuilderTemplateGroups(
        mergedParameters,
        existingParameterGroups,
      ),
      node: cloneRunSurfaceCollectionQueryBuilderChildState(node),
    };
  }, [contracts, predicateTemplates]);
  const trimmedPredicateDraftKey = predicateDraftKey.trim();
  const predicateKeyConflict = Boolean(
    trimmedPredicateDraftKey
    && [...predicates, ...predicateTemplates].some((entry) =>
      entry.key === trimmedPredicateDraftKey
      && !(editorTarget.kind === "predicate" && "id" in entry && entry.id === editorTarget.predicateId),
    ),
  );
  const trimmedTemplateDraftKey = templateDraftKey.trim();
  const templateKeyConflict = Boolean(
    trimmedTemplateDraftKey
    && [...predicates, ...predicateTemplates].some((entry) =>
      entry.key === trimmedTemplateDraftKey
      && !(editorTarget.kind === "template" && "id" in entry && entry.id === editorTarget.templateId),
    ),
  );
  const predicateSaveLabel =
    editorTarget.kind === "predicate" ? "Update predicate" : "Save as predicate";
  const subtreePromotionLabel =
    editorTarget.kind === "predicate" ? "Overwrite from target subtree" : "Promote target subtree";
  const templateSaveLabel =
    editorTarget.kind === "template" ? "Update template" : "Save as template";
  const templatePromotionLabel =
    editorTarget.kind === "template" ? "Overwrite template subtree" : "Promote subtree as template";
  const canAddPredicateRef = Boolean(
    predicateRefDraftKey
    && (
      !selectedRefTemplate
      || selectedRefTemplate.parameters.every(
        (parameter) =>
          Boolean(predicateRefDraftBindings[parameter.key]?.trim())
          || Boolean(parameter.bindingPreset.trim())
          || Boolean(parameter.defaultValue.trim()),
      )
    ),
  );
  const saveSelectedSubtreeAsPredicate = useCallback(() => {
    if (!trimmedPredicateDraftKey || predicateKeyConflict || !selectedSubtreeNode) {
      return;
    }
    if (editorTarget.kind === "predicate") {
      const previousPredicate = predicates.find((predicate) => predicate.id === editorTarget.predicateId) ?? null;
      setPredicates((current) =>
        current.map((predicate) =>
          predicate.id === editorTarget.predicateId
            ? {
                ...predicate,
                key: trimmedPredicateDraftKey,
                node: cloneRunSurfaceCollectionQueryBuilderChildState(selectedSubtreeNode),
              }
            : predicate,
        ),
      );
      if (previousPredicate && previousPredicate.key !== trimmedPredicateDraftKey) {
        setExpressionChildren((current) =>
          replaceRunSurfaceCollectionQueryBuilderPredicateRefs(
            current,
            previousPredicate.key,
            trimmedPredicateDraftKey,
          ),
        );
      }
      return;
    }
    setPredicates((current) => [
      ...current,
      {
        id: buildRunSurfaceCollectionQueryBuilderEntityId("predicate"),
        key: trimmedPredicateDraftKey,
        node: cloneRunSurfaceCollectionQueryBuilderChildState(selectedSubtreeNode),
      },
    ]);
    setPredicateDraftKey("");
  }, [
    editorTarget,
    predicateKeyConflict,
    predicates,
    selectedSubtreeNode,
    setExpressionChildren,
    setPredicateDraftKey,
    setPredicates,
    trimmedPredicateDraftKey,
  ]);
  const saveSelectedSubtreeAsTemplate = useCallback(() => {
    if (!trimmedTemplateDraftKey || templateKeyConflict || !selectedSubtreeNode) {
      return;
    }
    const nextTemplate = buildTemplateStateFromNode(
      trimmedTemplateDraftKey,
      selectedSubtreeNode,
      subtreeEditableTemplateParameters,
      subtreeEditableTemplateParameterGroups,
    );
    if (editorTarget.kind === "template") {
      const previousTemplate = predicateTemplates.find((template) => template.id === editorTarget.templateId) ?? null;
      setPredicateTemplates((current) =>
        current.map((template) =>
          template.id === editorTarget.templateId
            ? {
                ...nextTemplate,
                id: template.id,
              }
            : template,
        ),
      );
      if (previousTemplate && previousTemplate.key !== trimmedTemplateDraftKey) {
        setExpressionChildren((current) =>
          replaceRunSurfaceCollectionQueryBuilderPredicateRefs(
            current,
            previousTemplate.key,
            trimmedTemplateDraftKey,
          ),
        );
      }
      return;
    }
    setPredicateTemplates((current) => [...current, nextTemplate]);
    setTemplateDraftKey("");
  }, [
    buildTemplateStateFromNode,
    editorTarget,
    predicateTemplates,
    selectedSubtreeNode,
    setExpressionChildren,
    setPredicateTemplates,
    setTemplateDraftKey,
    subtreeEditableTemplateParameterGroups,
    subtreeEditableTemplateParameters,
    templateKeyConflict,
    trimmedTemplateDraftKey,
  ]);
  const updateSelectedExpressionTarget = useCallback(() => {
    if (!editorClauseState) {
      return;
    }
    if (editorTarget.kind === "expression_clause") {
      setExpressionChildren((current) =>
        updateRunSurfaceCollectionQueryBuilderClause(current, editorTarget.childId, editorClauseState),
      );
      return;
    }
    if (editorTarget.kind === "predicate") {
      setPredicates((current) =>
        current.map((predicate) =>
          predicate.id === editorTarget.predicateId
            ? {
                ...predicate,
                node: {
                  id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
                  kind: "clause",
                  clause: editorClauseState,
                },
              }
            : predicate,
        ),
      );
      return;
    }
    if (editorTarget.kind === "template") {
      setPredicateTemplates((current) =>
        current.map((template) =>
          template.id === editorTarget.templateId
            ? {
                ...buildTemplateStateFromNode(
                  template.key,
                  {
                    id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
                    kind: "clause",
                    clause: editorClauseState,
                  },
                  clauseEditableTemplateParameters,
                  clauseEditableTemplateParameterGroups,
                ),
                id: template.id,
              }
            : template,
        ),
      );
    }
  }, [
    buildTemplateStateFromNode,
    clauseEditableTemplateParameterGroups,
    clauseEditableTemplateParameters,
    editorClauseState,
    editorTarget,
    setExpressionChildren,
    setPredicates,
    setPredicateTemplates,
  ]);
  const savePredicateFromEditor = useCallback(() => {
    if (!editorClauseState || !trimmedPredicateDraftKey) {
      return;
    }
    if (editorTarget.kind === "predicate") {
      const previousPredicate = predicates.find((predicate) => predicate.id === editorTarget.predicateId) ?? null;
      setPredicates((current) =>
        current.map((predicate) =>
          predicate.id === editorTarget.predicateId
            ? {
                ...predicate,
                key: trimmedPredicateDraftKey,
                node: {
                  id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
                  kind: "clause",
                  clause: editorClauseState,
                },
              }
            : predicate,
        ),
      );
      if (previousPredicate && previousPredicate.key !== trimmedPredicateDraftKey) {
        setExpressionChildren((current) =>
          replaceRunSurfaceCollectionQueryBuilderPredicateRefs(
            current,
            previousPredicate.key,
            trimmedPredicateDraftKey,
          ),
        );
      }
      return;
    }
    setPredicates((current) => [
      ...current,
      {
        id: buildRunSurfaceCollectionQueryBuilderEntityId("predicate"),
        key: trimmedPredicateDraftKey,
        node: {
          id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
          kind: "clause",
          clause: editorClauseState,
        },
      },
    ]);
    setPredicateDraftKey("");
  }, [
    editorClauseState,
    editorTarget,
    predicates,
    setExpressionChildren,
    setPredicateDraftKey,
    setPredicates,
    trimmedPredicateDraftKey,
  ]);
  const saveTemplateFromEditor = useCallback(() => {
    if (!editorClauseState || !trimmedTemplateDraftKey || templateKeyConflict) {
      return;
    }
    const nextNode: RunSurfaceCollectionQueryBuilderClauseState = {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("clause"),
      kind: "clause",
      clause: editorClauseState,
    };
    if (editorTarget.kind === "template") {
      const previousTemplate = predicateTemplates.find((template) => template.id === editorTarget.templateId) ?? null;
      setPredicateTemplates((current) =>
        current.map((template) =>
          template.id === editorTarget.templateId
            ? {
                ...buildTemplateStateFromNode(
                  trimmedTemplateDraftKey,
                  nextNode,
                  clauseEditableTemplateParameters,
                  clauseEditableTemplateParameterGroups,
                ),
                id: template.id,
              }
            : template,
        ),
      );
      if (previousTemplate && previousTemplate.key !== trimmedTemplateDraftKey) {
        setExpressionChildren((current) =>
          replaceRunSurfaceCollectionQueryBuilderPredicateRefs(
            current,
            previousTemplate.key,
            trimmedTemplateDraftKey,
          ),
        );
      }
      return;
    }
    setPredicateTemplates((current) => [
      ...current,
      buildTemplateStateFromNode(
        trimmedTemplateDraftKey,
        nextNode,
        clauseEditableTemplateParameters,
        clauseEditableTemplateParameterGroups,
      ),
    ]);
    setTemplateDraftKey("");
  }, [
    buildTemplateStateFromNode,
    clauseEditableTemplateParameterGroups,
    clauseEditableTemplateParameters,
    editorClauseState,
    editorTarget,
    predicateTemplates,
    setExpressionChildren,
    setPredicateTemplates,
    setTemplateDraftKey,
    templateKeyConflict,
    trimmedTemplateDraftKey,
  ]);
  const addPredicateRefToExpression = useCallback(() => {
    if (!predicateRefDraftKey) {
      return;
    }
    const referencedTemplate =
      predicateTemplates.find((template) => template.key === predicateRefDraftKey) ?? null;
    const nextChild: RunSurfaceCollectionQueryBuilderPredicateRefState = {
      id: buildRunSurfaceCollectionQueryBuilderEntityId("predicate-ref"),
      kind: "predicate_ref",
      predicateKey: predicateRefDraftKey,
      bindings: referencedTemplate
        ? Object.fromEntries(
            referencedTemplate.parameters.flatMap((parameter) => {
              const value = (
                predicateRefDraftBindings[parameter.key]?.trim()
                || (
                  parameter.bindingPreset.trim()
                    ? toRunSurfaceCollectionQueryBindingReferenceValue(parameter.bindingPreset.trim())
                    : ""
                )
              );
              return value ? [[parameter.key, value]] : [];
            }),
          )
        : {},
      negated: false,
    };
    setExpressionChildren((current) =>
      selectedGroupId === RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID
        ? [...current, nextChild]
        : addRunSurfaceCollectionQueryBuilderChildToGroup(current, selectedGroupId, nextChild),
    );
    setExpressionMode("grouped");
  }, [
    predicateRefDraftBindings,
    predicateRefDraftKey,
    predicateTemplates,
    selectedGroupId,
    setExpressionChildren,
    setExpressionMode,
  ]);
  const removeExpressionChild = useCallback((childId: string) => {
    setExpressionChildren((current) => removeRunSurfaceCollectionQueryBuilderChild(current, childId));
    if (editorTarget.kind === "expression_clause" && editorTarget.childId === childId) {
      setEditorTarget({ kind: "draft" });
    }
    if (selectedGroupId === childId) {
      setSelectedGroupId(RUN_SURFACE_COLLECTION_QUERY_ROOT_GROUP_ID);
    }
  }, [editorTarget, selectedGroupId, setEditorTarget, setExpressionChildren, setSelectedGroupId]);
  const removePredicate = useCallback((predicateId: string) => {
    const predicate = predicates.find((entry) => entry.id === predicateId);
    setPredicates((current) => current.filter((entry) => entry.id !== predicateId));
    if (predicate) {
      setExpressionChildren((current) =>
        removeRunSurfaceCollectionQueryBuilderPredicateRefs(current, predicate.key),
      );
    }
    if (editorTarget.kind === "predicate" && editorTarget.predicateId === predicateId) {
      setEditorTarget({ kind: "draft" });
    }
  }, [editorTarget, predicates, setEditorTarget, setExpressionChildren, setPredicates]);
  const removeTemplate = useCallback((templateId: string) => {
    const template = predicateTemplates.find((entry) => entry.id === templateId);
    setPredicateTemplates((current) => current.filter((entry) => entry.id !== templateId));
    if (template) {
      setExpressionChildren((current) =>
        removeRunSurfaceCollectionQueryBuilderPredicateRefs(current, template.key),
      );
    }
    if (editorTarget.kind === "template" && editorTarget.templateId === templateId) {
      setEditorTarget({ kind: "draft" });
    }
  }, [editorTarget, predicateTemplates, setEditorTarget, setExpressionChildren, setPredicateTemplates]);
  const togglePredicateRefNegation = useCallback((childId: string) => {
    const toggleChildren = (
      children: RunSurfaceCollectionQueryBuilderChildState[],
    ): RunSurfaceCollectionQueryBuilderChildState[] =>
      children.map((child) => {
        if (child.kind === "predicate_ref" && child.id === childId) {
          return {
            ...child,
            negated: !child.negated,
          };
        }
        if (child.kind === "group") {
          return {
            ...child,
            children: toggleChildren(child.children),
          };
        }
        return child;
      });
    setExpressionChildren((current) => toggleChildren(current));
  }, [setExpressionChildren]);

  return {
    activeEditorTargetLabel,
    addClauseToExpression,
    addGroupToExpression,
    addPredicateRefToExpression,
    applyCurrentExpression,
    canAddPredicateRef,
    canApplyExpression,
    expressionLabel,
    filterExpressionPreview,
    focusRuntimeCandidateClauseEditor,
    groupedExpressionLabel,
    predicateKeyConflict,
    predicateSaveLabel,
    removeExpressionChild,
    removePredicate,
    removeTemplate,
    resolvedCollectionPath,
    savePredicateFromEditor,
    saveSelectedSubtreeAsPredicate,
    saveSelectedSubtreeAsTemplate,
    saveTemplateFromEditor,
    setEditorFromClause,
    subtreePromotionLabel,
    templateKeyConflict,
    templatePromotionLabel,
    templateSaveLabel,
    togglePredicateRefNegation,
    trimmedPredicateDraftKey,
    trimmedTemplateDraftKey,
    updateSelectedExpressionTarget,
  };
}
