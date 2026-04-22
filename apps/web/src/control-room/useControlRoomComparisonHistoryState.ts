// @ts-nocheck
import { useEffect, useMemo, useRef, useState } from "react";

export function useControlRoomComparisonHistoryState({ model }: { model: any }): any {
  const {
    initialComparisonSelectionRef, DEFAULT_COMPARISON_INTENT, initialComparisonHistoryPanelUiStateRef, defaultComparisonHistoryPanelState, initialComparisonHistorySyncAuditTrailRef, providerProvenanceSchedulerNarrativeTemplates,
    providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplates, selectedProviderProvenanceSchedulerStitchedReportViewIds, selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIds, selectedProviderProvenanceSchedulerNarrativeTemplateIds, selectedProviderProvenanceSchedulerNarrativeRegistryIds, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIds,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogIds, selectedProviderProvenanceSchedulerNarrativeGovernancePlanIds, providerProvenanceSchedulerStitchedReportViews, providerProvenanceSchedulerNarrativeRegistryEntries, providerProvenanceSchedulerNarrativeGovernancePolicyTemplates, providerProvenanceSchedulerNarrativeGovernancePolicyCatalogs,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogId, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIds, selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIds, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepId, selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateId, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHistory,
    providerProvenanceSchedulerNarrativeGovernancePlans, selectedProviderProvenanceSchedulerNarrativeGovernancePlanId, providerProvenanceSchedulerNarrativeGovernancePlanListSummary, providerProvenanceSchedulerStitchedReportGovernancePlanListSummary, providerProvenanceSchedulerStitchedReportGovernanceRegistryPlanListSummary, providerProvenanceSchedulerStitchedReportGovernanceCatalogSearch,
    providerProvenanceSchedulerNarrativeGovernancePolicySupportsItemType, providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogSearch, providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogEntries, providerProvenanceSchedulerStitchedReportGovernanceRegistrySearch, providerProvenanceSchedulerStitchedReportGovernanceRegistries, formatProviderProvenanceSchedulerNarrativeGovernanceQueueViewSummary,
    selectedProviderProvenanceSchedulerExportHistory, providerProvenanceSchedulerExports, selectedProviderProvenanceSchedulerExportJobId, normalizeControlRoomComparisonSelection, buildComparisonHistoryStepDescriptor, backtests,
    buildComparisonHistorySyncSignature, buildComparisonHistorySyncWorkspaceState, setStatusText, fetchJson, buildRunsPath, backtestRunFilter,
    sandboxRunFilter, paperRunFilter, liveRunFilter, setRunSurfaceCapabilities, setStrategies, setReferences,
    setPresets, setBacktests, setSandboxRuns, setPaperRuns, setLiveRuns, setMarketStatus,
    resolveAutoLinkedMarketInstrument, resolvePreferredMarketDataInstrument, activeMarketInstrumentKey, setActiveMarketInstrumentKey, buildMarketDataInstrumentFocusKey, setOperatorVisibility,
    setGuardedLive, loadMarketDataWorkflow, strategies, setBacktestForm, setSandboxForm, setLiveForm,
    normalizeRunFormPreset, presets, setBacktestRunFilter, normalizeRunHistoryPresetFilter, setSandboxRunFilter, setPaperRunFilter,
    setLiveRunFilter, editingPresetId, setEditingPresetId, setPresetForm, defaultPresetForm, buildPresetFormFromPreset,
    normalizeRunHistoryFilter, readComparisonHistoryBrowserState, loadComparisonSelectionFromUrl, defaultControlRoomComparisonSelectionState, reconcileComparisonHistoryPanelState, buildComparisonHistoryPanelEntry,
    findComparisonHistoryPanelEntryForSelection, persistComparisonHistorySyncAuditTrail, persistMarketDataProvenanceExportState, marketDataProvenanceExportFilter, marketDataProvenanceExportHistory, CONTROL_ROOM_UI_STATE_STORAGE_KEY,
    readControlRoomUiStateValue, mergeComparisonHistoryPanelState, buildComparisonHistorySyncAuditEntries, isSameComparisonHistoryPanelState, isSameComparisonHistoryPanelSyncState, appendComparisonHistorySyncAuditEntries,
    buildRunComparisonPath, buildComparisonHistoryPanelSyncState, persistControlRoomUiState, buildComparisonSelectionHistoryUrl, buildComparisonHistoryEntryId, buildComparisonHistoryBrowserState,
    isSameComparisonHistoryBrowserState, persistComparisonSelectionToUrl, limitComparisonHistoryPanelEntries, sortComparisonHistoryPanelEntries, buildDefaultComparisonHistorySyncConflictSelectedSources, resolveComparisonHistorySyncConflictReviewEntry,
    formatComparisonHistorySyncConflictResolutionSummary, applyResolvedComparisonHistoryPanelEntry, buildDefaultComparisonHistorySyncPreferenceSelectedSources, resolveComparisonHistorySyncPreferenceReview, formatComparisonHistorySyncPreferenceResolutionSummary, buildDefaultComparisonHistorySyncWorkspaceSelectedSources,
    buildComparisonHistorySyncWorkspaceRecommendedSources, resolveComparisonHistorySyncWorkspaceReview, formatComparisonHistorySyncWorkspaceResolutionSummary, marketStatus, pruneExpandedGapRows, filterExpandedGapRows,
    pruneExpandedGapWindowSelections, filterExpandedGapWindowSelections, isSameComparisonSelection, isSameComparisonHistoryExpandedGapRows, isSameExpandedGapWindowSelections, instrumentGapRowKey,
  } = model;

}

function joinPresetStructuredDiffHints(...parts: Array<string | undefined>) {
  return parts.filter((part): part is string => Boolean(part)).join(" · ") || undefined;
}

function tokenizePresetParameterPath(pathSegments: string[]) {
  return pathSegments
    .flatMap((segment) => segment.toLowerCase().match(/[a-z0-9]+/g) ?? [])
    .filter((token) => !/^\d+$/.test(token));
}

function parsePresetTimeframeToMinutes(value: unknown) {
  if (typeof value !== "string") {
    return null;
  }
  const match = value.trim().match(/^(\d+)([mhdw])$/i);
  if (!match) {
    return null;
  }
  const amount = Number(match[1]);
  const unit = PRESET_TIMEFRAME_UNIT_TO_MINUTES[match[2].toLowerCase()];
  if (!Number.isFinite(amount) || !unit) {
    return null;
  }
  return amount * unit;
}

function buildPresetRankedStringDelta(
  existingRaw: unknown,
  incomingRaw: unknown,
  ranks: Record<string, number>,
  higherLabel: string,
  lowerLabel: string,
): PresetStructuredDiffDeltaValue | undefined {
  if (typeof existingRaw !== "string" || typeof incomingRaw !== "string") {
    return undefined;
  }
  const existingRank = ranks[existingRaw.trim().toLowerCase()];
  const incomingRank = ranks[incomingRaw.trim().toLowerCase()];
  if (existingRank === undefined || incomingRank === undefined || existingRank === incomingRank) {
    return undefined;
  }
  return {
    direction: incomingRank > existingRank ? "higher" : "lower",
    label: incomingRank > existingRank ? higherLabel : lowerLabel,
  };
}

function buildPresetParameterStrategyContext(
  existingRaw: unknown,
  incomingRaw: unknown,
  schemaEntry?: ParameterSchema[string],
): {
  delta?: PresetStructuredDiffDeltaValue;
  hint?: string;
} {
  if (!schemaEntry) {
    return {
      delta: undefined,
      hint: undefined,
    };
  }
  const hint =
    typeof schemaEntry.semantic_hint === "string" && schemaEntry.semantic_hint.trim()
      ? `Strategy: ${schemaEntry.semantic_hint.trim()}`
      : undefined;
  const higherLabel =
    typeof schemaEntry.delta_higher_label === "string" && schemaEntry.delta_higher_label.trim()
      ? schemaEntry.delta_higher_label.trim()
      : undefined;
  const lowerLabel =
    typeof schemaEntry.delta_lower_label === "string" && schemaEntry.delta_lower_label.trim()
      ? schemaEntry.delta_lower_label.trim()
      : undefined;
  if (!higherLabel || !lowerLabel) {
    return {
      delta: undefined,
      hint,
    };
  }
  if (
    typeof existingRaw === "number" &&
    Number.isFinite(existingRaw) &&
    typeof incomingRaw === "number" &&
    Number.isFinite(incomingRaw) &&
    existingRaw !== incomingRaw
  ) {
    return {
      delta: {
        direction: incomingRaw > existingRaw ? "higher" : "lower",
        label: incomingRaw > existingRaw ? higherLabel : lowerLabel,
      },
      hint,
    };
  }
  if (typeof existingRaw === "boolean" && typeof incomingRaw === "boolean" && existingRaw !== incomingRaw) {
    return {
      delta: {
        direction: incomingRaw ? "higher" : "lower",
        label: incomingRaw ? higherLabel : lowerLabel,
      },
      hint,
    };
  }
  const existingTimeframe = parsePresetTimeframeToMinutes(existingRaw);
  const incomingTimeframe = parsePresetTimeframeToMinutes(incomingRaw);
  if (
    existingTimeframe !== null &&
    incomingTimeframe !== null &&
    existingTimeframe !== incomingTimeframe
  ) {
    return {
      delta: {
        direction: incomingTimeframe > existingTimeframe ? "higher" : "lower",
        label: incomingTimeframe > existingTimeframe ? higherLabel : lowerLabel,
      },
      hint,
    };
  }
  if (
    typeof existingRaw === "string" &&
    typeof incomingRaw === "string" &&
    schemaEntry.semantic_ranks
  ) {
    return {
      delta: buildPresetRankedStringDelta(
        existingRaw,
        incomingRaw,
        schemaEntry.semantic_ranks,
        higherLabel,
        lowerLabel,
      ),
      hint,
    };
  }
  return {
    delta: undefined,
    hint,
  };
}

function buildPresetParameterDomainContext(
  pathSegments: string[],
  existingRaw: unknown,
  incomingRaw: unknown,
  schemaEntry?: ParameterSchema[string],
): {
  delta?: PresetStructuredDiffDeltaValue;
  hint?: string;
} {
  const tokens = tokenizePresetParameterPath(pathSegments);
  const tokenSet = new Set(tokens);
  const timeframeExisting = parsePresetTimeframeToMinutes(existingRaw);
  const timeframeIncoming = parsePresetTimeframeToMinutes(incomingRaw);
  const existingNumeric = typeof existingRaw === "number" && Number.isFinite(existingRaw);
  const incomingNumeric = typeof incomingRaw === "number" && Number.isFinite(incomingRaw);
  const hasNumericPair = existingNumeric && incomingNumeric;
  const hasTimeframeCue =
    schemaEntry?.unit === "timeframe" ||
    tokenSet.has("timeframe") ||
    tokenSet.has("interval") ||
    tokenSet.has("cadence") ||
    timeframeExisting !== null ||
    timeframeIncoming !== null;
  if (hasTimeframeCue) {
    return {
      delta:
        timeframeExisting !== null &&
        timeframeIncoming !== null &&
        timeframeExisting !== timeframeIncoming
          ? {
              direction: timeframeIncoming > timeframeExisting ? ("higher" as const) : ("lower" as const),
              label: timeframeIncoming > timeframeExisting ? "slower cadence" : "faster cadence",
            }
          : undefined,
      hint: "Domain: timeframe cadence",
    };
  }

  if (tokenSet.has("stop") && tokenSet.has("loss")) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "wider stop" : "tighter stop",
          }
        : undefined,
      hint: "Domain: stop-loss guardrail",
    };
  }
  if ((tokenSet.has("take") && tokenSet.has("profit")) || tokenSet.has("target") || tokenSet.has("tp")) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "farther target" : "closer target",
          }
        : undefined,
      hint: "Domain: profit target",
    };
  }
  if (
    tokenSet.has("window") ||
    tokenSet.has("lookback") ||
    tokenSet.has("period") ||
    tokenSet.has("bars") ||
    tokenSet.has("bar") ||
    tokenSet.has("length")
  ) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "longer lookback" : "shorter lookback",
          }
        : undefined,
      hint: "Domain: lookback window",
    };
  }
  if (tokenSet.has("threshold") || tokenSet.has("trigger")) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "stricter threshold" : "looser threshold",
          }
        : undefined,
      hint: "Domain: decision threshold",
    };
  }
  if (tokenSet.has("confidence")) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "higher confidence gate" : "lower confidence gate",
          }
        : undefined,
      hint: "Domain: confidence gate",
    };
  }
  if (
    tokenSet.has("position") ||
    tokenSet.has("allocation") ||
    tokenSet.has("exposure") ||
    tokenSet.has("leverage") ||
    tokenSet.has("size") ||
    tokenSet.has("notional")
  ) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "higher exposure cap" : "lower exposure cap",
          }
        : undefined,
      hint: "Domain: sizing / exposure",
    };
  }
  if (
    tokenSet.has("risk") ||
    tokenSet.has("drawdown") ||
    tokenSet.has("loss") ||
    tokenSet.has("fraction") ||
    tokenSet.has("ratio") ||
    tokenSet.has("pct") ||
    tokenSet.has("percent")
  ) {
    return {
      delta: hasNumericPair
        ? {
            direction: incomingRaw > existingRaw ? "higher" : "lower",
            label: incomingRaw > existingRaw ? "larger risk budget" : "smaller risk budget",
          }
        : undefined,
      hint: "Domain: risk / ratio budget",
    };
  }

  if (tokenSet.has("profile") || tokenSet.has("mode") || tokenSet.has("style") || tokenSet.has("regime")) {
    return {
      delta:
        typeof existingRaw === "string" && typeof incomingRaw === "string"
          ? buildPresetRankedStringDelta(
              existingRaw,
              incomingRaw,
              PRESET_PROFILE_AGGRESSIVENESS_RANKS,
              "more aggressive profile",
              "more conservative profile",
            ) ??
            buildPresetRankedStringDelta(
              existingRaw,
              incomingRaw,
              PRESET_PROFILE_SPEED_RANKS,
              "faster profile",
              "slower profile",
            ) ??
            buildPresetRankedStringDelta(
              existingRaw,
              incomingRaw,
              PRESET_PROFILE_CONFIDENCE_RANKS,
              "higher confidence profile",
              "lower confidence profile",
            )
          : undefined,
      hint: "Domain: categorical profile",
    };
  }

  if (Array.isArray(schemaEntry?.enum) && schemaEntry.enum.length) {
    return {
      delta: undefined,
      hint: "Domain: categorical selection",
    };
  }

  if (
    tokenSet.has("allow") ||
    tokenSet.has("enable") ||
    tokenSet.has("disable") ||
    tokenSet.has("reduce") ||
    tokenSet.has("exit")
  ) {
    return {
      delta: undefined,
      hint: "Domain: execution guardrail",
    };
  }

  return {
    delta: undefined,
    hint: undefined,
  };
}

function formatPresetParameterSchemaHint(schemaEntry?: ParameterSchema[string]) {
  if (!schemaEntry) {
    return undefined;
  }
  const parts: string[] = [];
  if (schemaEntry.type) {
    parts.push(schemaEntry.type);
  }
  if (schemaEntry.default !== undefined) {
    parts.push(`default ${formatParameterValue(schemaEntry.default)}`);
  }
  if (Array.isArray(schemaEntry.enum) && schemaEntry.enum.length) {
    parts.push(`options ${schemaEntry.enum.map((value) => formatParameterValue(value)).join("/")}`);
  }
  if (typeof schemaEntry.minimum === "number") {
    parts.push(`min ${formatComparisonTooltipTuningValue(schemaEntry.minimum)}`);
  }
  if (typeof schemaEntry.maximum === "number") {
    parts.push(`max ${formatComparisonTooltipTuningValue(schemaEntry.maximum)}`);
  }
  if (schemaEntry.unit) {
    parts.push(`unit ${schemaEntry.unit}`);
  }
  if (!parts.length) {
    return undefined;
  }
  return `Schema: ${parts.join(" · ")}`;
}

function getPresetParameterSchemaEntry(
  parameterSchema: ParameterSchema | undefined,
  pathSegments: string[],
) {
  const rootSegment = pathSegments.find((segment) => !segment.startsWith("["));
  if (!rootSegment) {
    return undefined;
  }
  return parameterSchema?.[rootSegment];
}

function buildPresetStructuredDiffDelta(
  existingValue: string,
  incomingValue: string,
  existingRaw: unknown = existingValue,
  incomingRaw: unknown = incomingValue,
  schemaEntry?: ParameterSchema[string],
  domainDelta?: PresetStructuredDiffDeltaValue,
) {
  if (existingValue === incomingValue) {
    return {
      direction: "same" as const,
      label: "match",
    };
  }
  if (schemaEntry?.type) {
    const existingMatchesType = matchesPresetParameterSchemaType(existingRaw, schemaEntry.type);
    const incomingMatchesType = matchesPresetParameterSchemaType(incomingRaw, schemaEntry.type);
    if (incomingRaw !== undefined && !incomingMatchesType) {
      return {
        direction: "lower" as const,
        label: `expected ${schemaEntry.type}`,
      };
    }
    if (existingRaw !== undefined && !existingMatchesType && incomingMatchesType) {
      return {
        direction: "higher" as const,
        label: `matches ${schemaEntry.type}`,
      };
    }
  }
  if (schemaEntry?.default !== undefined) {
    const existingIsDefault = arePresetStructuredDiffValuesEquivalent(existingRaw, schemaEntry.default);
    const incomingIsDefault = arePresetStructuredDiffValuesEquivalent(incomingRaw, schemaEntry.default);
    if (existingRaw === undefined && incomingIsDefault) {
      return {
        direction: "same" as const,
        label: `explicit default ${formatParameterValue(schemaEntry.default)}`,
      };
    }
    if (!existingIsDefault && incomingIsDefault) {
      return {
        direction: "same" as const,
        label: `back to default ${formatParameterValue(schemaEntry.default)}`,
      };
    }
    if (existingIsDefault && !incomingIsDefault) {
      return {
        direction:
          domainDelta?.direction ??
          (typeof incomingRaw === "number" &&
          typeof schemaEntry.default === "number" &&
          Number.isFinite(incomingRaw) &&
          Number.isFinite(schemaEntry.default)
            ? incomingRaw >= schemaEntry.default
              ? ("higher" as const)
              : ("lower" as const)
            : ("higher" as const)),
        label: domainDelta
          ? `${domainDelta.label} vs default ${formatParameterValue(schemaEntry.default)}`
          : `override default ${formatParameterValue(schemaEntry.default)}`,
      };
    }
    if (incomingRaw === undefined && !existingIsDefault) {
      return {
        direction: "lower" as const,
        label: "cleared override",
      };
    }
  }
  if (
    typeof schemaEntry?.minimum === "number" &&
    typeof incomingRaw === "number" &&
    Number.isFinite(incomingRaw)
  ) {
    const existingMeetsMinimum =
      typeof existingRaw === "number" &&
      Number.isFinite(existingRaw) &&
      existingRaw >= schemaEntry.minimum;
    if (incomingRaw < schemaEntry.minimum) {
      return {
        direction: "lower" as const,
        label: `below min ${formatComparisonTooltipTuningValue(schemaEntry.minimum)}`,
      };
    }
    if (!existingMeetsMinimum && incomingRaw >= schemaEntry.minimum) {
      return {
        direction: "higher" as const,
        label: `meets min ${formatComparisonTooltipTuningValue(schemaEntry.minimum)}`,
      };
    }
  }
  if (!existingValue && incomingValue) {
    return {
      direction: "higher" as const,
      label: "added",
    };
  }
  if (existingValue && !incomingValue) {
    return {
      direction: "lower" as const,
      label: "removed",
    };
  }
  if (domainDelta) {
    return domainDelta;
  }
  if (
    typeof existingRaw === "number" &&
    Number.isFinite(existingRaw) &&
    typeof incomingRaw === "number" &&
    Number.isFinite(incomingRaw)
  ) {
    return formatComparisonTooltipTuningDelta(existingRaw, incomingRaw);
  }
  if (typeof existingRaw === "boolean" && typeof incomingRaw === "boolean") {
    return {
      direction: incomingRaw ? ("higher" as const) : ("lower" as const),
      label: incomingRaw ? "enabled" : "disabled",
    };
  }
  if (
    Array.isArray(existingRaw) &&
    Array.isArray(incomingRaw) &&
    existingRaw.every(isPresetStructuredDiffScalar) &&
    incomingRaw.every(isPresetStructuredDiffScalar)
  ) {
    const existingItems = existingRaw.map((item) => formatParameterValue(item));
    const incomingItems = incomingRaw.map((item) => formatParameterValue(item));
    const addedItems = incomingItems.filter((item) => !existingItems.includes(item));
    const removedItems = existingItems.filter((item) => !incomingItems.includes(item));
    if (addedItems.length && !removedItems.length) {
      return {
        direction: "higher" as const,
        label: `${addedItems.length} added`,
      };
    }
    if (removedItems.length && !addedItems.length) {
      return {
        direction: "lower" as const,
        label: `${removedItems.length} removed`,
      };
    }
    if (addedItems.length || removedItems.length) {
      return {
        direction: addedItems.length >= removedItems.length ? ("higher" as const) : ("lower" as const),
        label: `${addedItems.length} added · ${removedItems.length} removed`,
      };
    }
  }
  return {
    direction: "higher" as const,
    label: "changed",
  };
}

function summarizePresetStructuredDiffGroup(group: PresetStructuredDiffGroup) {
  if (!group.changed_count) {
    return `${group.same_count} unchanged`;
  }
  const parts = [`${group.changed_count} changed`];
  if (group.higher_count) {
    parts.push(`${group.higher_count} higher/add`);
  }
  if (group.lower_count) {
    parts.push(`${group.lower_count} lower/remove`);
  }
  if (group.same_count) {
    parts.push(`${group.same_count} unchanged`);
  }
  return parts.join(" · ");
}

function groupPresetStructuredDiffRows(rows: PresetStructuredDiffRow[]) {
  const groups = rows.reduce<Record<string, PresetStructuredDiffGroup>>((accumulator, row) => {
    const existing = accumulator[row.group_key] ?? {
      changed_count: 0,
      higher_count: 0,
      key: row.group_key,
      label: row.group_label,
      lower_count: 0,
      rows: [],
      same_count: 0,
      summary_label: "",
    };
    existing.rows.push(row);
    if (row.changed) {
      existing.changed_count += 1;
      if (row.delta_direction === "higher") {
        existing.higher_count += 1;
      } else if (row.delta_direction === "lower") {
        existing.lower_count += 1;
      }
    } else {
      existing.same_count += 1;
    }
    accumulator[row.group_key] = existing;
    return accumulator;
  }, {});
  return Object.values(groups)
    .map((group) => ({
      ...group,
      rows: group.rows.sort((left, right) => left.label.localeCompare(right.label)),
      summary_label: summarizePresetStructuredDiffGroup(group),
    }))
    .sort((left, right) => {
      const leftOrder = left.rows[0]?.group_order ?? Number.MAX_SAFE_INTEGER;
      const rightOrder = right.rows[0]?.group_order ?? Number.MAX_SAFE_INTEGER;
      return leftOrder - rightOrder || left.label.localeCompare(right.label);
    });
}

function buildPresetStructuredDiffRows(
  existing: ExperimentPresetRevision,
  incoming: ExperimentPresetRevision,
  parameterSchema?: ParameterSchema,
) {
  const rows: PresetStructuredDiffRow[] = [];
  const pushRow = (
    key: string,
    label: string,
    existingValue: string,
    incomingValue: string,
    groupKey: string,
    groupLabel: string,
    groupOrder: number,
    existingRaw: unknown = existingValue,
    incomingRaw: unknown = incomingValue,
    semanticHint?: string,
    schemaEntry?: ParameterSchema[string],
    domainDelta?: PresetStructuredDiffDeltaValue,
  ) => {
    const delta = buildPresetStructuredDiffDelta(
      existingValue,
      incomingValue,
      existingRaw,
      incomingRaw,
      schemaEntry,
      domainDelta,
    );
    rows.push({
      changed: existingValue !== incomingValue,
      delta_direction: delta.direction,
      delta_label: delta.label,
      existing_value: formatPresetStructuredDiffDisplayValue(existingValue),
      group_key: groupKey,
      group_label: groupLabel,
      group_order: groupOrder,
      incoming_value: formatPresetStructuredDiffDisplayValue(incomingValue),
      key,
      label,
      semantic_hint: semanticHint,
    });
  };
  const formatParameterPathLabel = (segments: string[]) =>
    segments.reduce((label, segment) => {
      if (!label) {
        return segment;
      }
      if (segment.startsWith("[")) {
        return `${label}${segment}`;
      }
      return `${label}.${segment}`;
    }, "");
  const pushParameterRow = (
    pathSegments: string[],
    existingParameter: unknown,
    incomingParameter: unknown,
  ) => {
    const label = formatParameterPathLabel(pathSegments) || "Parameter bundle";
    const existingValue = existingParameter === undefined ? "" : formatParameterValue(existingParameter);
    const incomingValue = incomingParameter === undefined ? "" : formatParameterValue(incomingParameter);
    const schemaEntry = getPresetParameterSchemaEntry(parameterSchema, pathSegments);
    const strategyContext = buildPresetParameterStrategyContext(
      existingParameter,
      incomingParameter,
      schemaEntry,
    );
    const domainContext = buildPresetParameterDomainContext(
      pathSegments,
      existingParameter,
      incomingParameter,
      schemaEntry,
    );
    pushRow(
      `parameter:${label}`,
      label,
      existingValue,
      incomingValue,
      "parameters",
      "Parameters",
      3,
      existingParameter,
      incomingParameter,
      joinPresetStructuredDiffHints(
        formatPresetParameterSchemaHint(schemaEntry),
        strategyContext.hint,
        domainContext.hint,
      ),
      schemaEntry,
      strategyContext.delta ?? domainContext.delta,
    );
  };
  const appendParameterRows = (
    existingParameter: unknown,
    incomingParameter: unknown,
    pathSegments: string[] = [],
  ) => {
    if (isPresetStructuredDiffObject(existingParameter) && incomingParameter === undefined) {
      appendParameterRows(existingParameter, {}, pathSegments);
      return;
    }
    if (existingParameter === undefined && isPresetStructuredDiffObject(incomingParameter)) {
      appendParameterRows({}, incomingParameter, pathSegments);
      return;
    }
    if (Array.isArray(existingParameter) && incomingParameter === undefined) {
      if (existingParameter.every(isPresetStructuredDiffScalar)) {
        pushParameterRow(pathSegments, existingParameter, incomingParameter);
      } else {
        appendParameterRows(existingParameter, [], pathSegments);
      }
      return;
    }
    if (existingParameter === undefined && Array.isArray(incomingParameter)) {
      if (incomingParameter.every(isPresetStructuredDiffScalar)) {
        pushParameterRow(pathSegments, existingParameter, incomingParameter);
      } else {
        appendParameterRows([], incomingParameter, pathSegments);
      }
      return;
    }
    if (
      Array.isArray(existingParameter) &&
      Array.isArray(incomingParameter) &&
      existingParameter.every(isPresetStructuredDiffScalar) &&
      incomingParameter.every(isPresetStructuredDiffScalar)
    ) {
      pushParameterRow(pathSegments, existingParameter, incomingParameter);
      return;
    }
    if (Array.isArray(existingParameter) && Array.isArray(incomingParameter)) {
      const length = Math.max(existingParameter.length, incomingParameter.length);
      for (let index = 0; index < length; index += 1) {
        appendParameterRows(existingParameter[index], incomingParameter[index], [...pathSegments, `[${index}]`]);
      }
      return;
    }
    if (isPresetStructuredDiffObject(existingParameter) && isPresetStructuredDiffObject(incomingParameter)) {
      const keys = Array.from(
        new Set([...Object.keys(existingParameter), ...Object.keys(incomingParameter)]),
      ).sort();
      if (!keys.length) {
        pushParameterRow(pathSegments, existingParameter, incomingParameter);
        return;
      }
      keys.forEach((key) => {
        appendParameterRows(existingParameter[key], incomingParameter[key], [...pathSegments, key]);
      });
      return;
    }
    pushParameterRow(pathSegments, existingParameter, incomingParameter);
  };

  pushRow("name", "Name", existing.name, incoming.name, "identity", "Identity", 0);
  pushRow(
    "description",
    "Description",
    existing.description,
    incoming.description,
    "identity",
    "Identity",
    0,
  );
  pushRow(
    "strategy",
    "Strategy",
    existing.strategy_id ?? "",
    incoming.strategy_id ?? "",
    "scope",
    "Scope",
    1,
  );
  pushRow(
    "timeframe",
    "Timeframe",
    existing.timeframe ?? "",
    incoming.timeframe ?? "",
    "scope",
    "Scope",
    1,
  );
  pushRow(
    "benchmark_family",
    "Benchmark family",
    existing.benchmark_family ?? "",
    incoming.benchmark_family ?? "",
    "scope",
    "Scope",
    1,
  );
  pushRow(
    "tags",
    "Tags",
    existing.tags.join(", "),
    incoming.tags.join(", "),
    "metadata",
    "Metadata",
    2,
  );

  const parameterKeys = Array.from(
    new Set([...Object.keys(existing.parameters), ...Object.keys(incoming.parameters)]),
  ).sort();
  if (!parameterKeys.length) {
    pushRow("parameters", "Parameter bundle", "", "", "parameters", "Parameters", 3);
  } else {
    parameterKeys.forEach((key) => {
      appendParameterRows(existing.parameters[key], incoming.parameters[key], [key]);
    });
  }
  return rows;
}

function describePresetRevisionDiff(
  revision: ExperimentPresetRevision,
  reference: ExperimentPresetRevision | null,
  basisLabel: string,
  parameterSchema?: ParameterSchema,
): PresetRevisionDiff {
  const rows = buildPresetStructuredDiffRows(
    reference ?? buildEmptyPresetRevisionSnapshot(),
    revision,
    parameterSchema,
  );
  const changedGroups = groupPresetStructuredDiffRows(rows.filter((row) => row.changed));
  const unchangedGroups = groupPresetStructuredDiffRows(rows.filter((row) => !row.changed));
  const searchTexts = rows.map(
    (row) =>
      `${row.label} ${row.semantic_hint ?? ""} ${row.existing_value} ${row.incoming_value} ${row.delta_label}`,
  );
  const changeCount = changedGroups.reduce((total, group) => total + group.changed_count, 0);

  return {
    basisLabel,
    changeCount,
    changedGroups,
    unchangedGroups,
    searchTexts,
    summary: changeCount
      ? `${changeCount} change${changeCount === 1 ? "" : "s"} vs ${basisLabel}.`
      : `Matches ${basisLabel}.`,
  };
}

function describePresetDraftConflict(
  preset: ExperimentPreset,
  form: typeof defaultPresetForm,
  parameterSchema?: ParameterSchema,
): PresetDraftConflict {
  const savedForm = buildPresetFormFromPreset(preset);
  let normalizedDraftParameters = form.parameters_text.trim();
  let parsedDraftParameters: Record<string, unknown> = {};
  let hasInvalidParameters = false;
  if (normalizedDraftParameters) {
    try {
      parsedDraftParameters = parseJsonObjectInput(form.parameters_text);
      normalizedDraftParameters = JSON.stringify(parsedDraftParameters, null, 2);
    } catch {
      hasInvalidParameters = true;
    }
  }
  const rows: PresetStructuredDiffRow[] = [];
  const pushRow = (
    key: string,
    label: string,
    existingValue: string,
    incomingValue: string,
    groupKey: string,
    groupLabel: string,
    groupOrder: number,
  ) => {
    const delta = buildPresetStructuredDiffDelta(existingValue, incomingValue);
    rows.push({
      changed: existingValue !== incomingValue,
      delta_direction: delta.direction,
      delta_label: delta.label,
      existing_value: formatPresetStructuredDiffDisplayValue(existingValue),
      group_key: groupKey,
      group_label: groupLabel,
      group_order: groupOrder,
      incoming_value: formatPresetStructuredDiffDisplayValue(incomingValue),
      key,
      label,
    });
  };
  pushRow("name", "Name", savedForm.name, form.name, "identity", "Draft fields", 0);
  pushRow(
    "description",
    "Description",
    savedForm.description,
    form.description,
    "identity",
    "Draft fields",
    0,
  );
  pushRow("strategy", "Strategy", savedForm.strategy_id, form.strategy_id, "scope", "Scope", 1);
  pushRow(
    "timeframe",
    "Timeframe",
    savedForm.timeframe.trim(),
    form.timeframe.trim(),
    "scope",
    "Scope",
    1,
  );
  pushRow(
    "benchmark_family",
    "Benchmark family",
    savedForm.benchmark_family.trim(),
    form.benchmark_family.trim(),
    "scope",
    "Scope",
    1,
  );
  pushRow(
    "tags",
    "Tags",
    parseExperimentTags(savedForm.tags_text).join(", "),
    parseExperimentTags(form.tags_text).join(", "),
    "metadata",
    "Metadata",
    2,
  );
  if (hasInvalidParameters) {
    pushRow(
      "parameters_json",
      "Parameters JSON (invalid draft)",
      savedForm.parameters_text.trim(),
      normalizedDraftParameters,
      "parameters",
      "Parameters",
      3,
    );
  } else {
    const revisionRows = buildPresetStructuredDiffRows(
      buildCurrentPresetRevisionSnapshot(preset),
      {
        ...buildCurrentPresetRevisionSnapshot(preset),
        name: form.name,
        description: form.description,
        strategy_id: form.strategy_id || null,
        timeframe: form.timeframe.trim() || null,
        benchmark_family: form.benchmark_family.trim() || null,
        tags: parseExperimentTags(form.tags_text),
        parameters: parsedDraftParameters,
      },
      parameterSchema,
    );
    rows.push(...revisionRows.filter((row) => row.group_key === "parameters"));
  }
  const groups = groupPresetStructuredDiffRows(rows.filter((row) => row.changed));
  const changeCount = groups.reduce((total, group) => total + group.changed_count, 0);
  return {
    changeCount,
    groups,
    hasInvalidParameters,
    summary: changeCount
      ? `${changeCount} unsaved draft field${changeCount === 1 ? "" : "s"} differ from the saved bundle.`
      : "Current draft matches the saved bundle.",
  };
}

function matchesPresetRevisionFilter(
  revision: ExperimentPresetRevision,
  diff: PresetRevisionDiff,
  filter: PresetRevisionFilterState,
) {
  if (filter.action !== "all" && revision.action !== filter.action) {
    return false;
  }
  const query = filter.query.trim().toLowerCase();
  if (!query) {
    return true;
  }
  const searchable = [
    revision.revision_id,
    revision.actor,
    revision.reason,
    revision.action,
    revision.name,
    revision.description,
    revision.strategy_id ?? "",
    revision.timeframe ?? "",
    revision.benchmark_family ?? "",
    revision.tags.join(" "),
    Object.keys(revision.parameters).join(" "),
    diff.summary,
    ...diff.searchTexts,
  ]
    .join(" ")
    .toLowerCase();
  return searchable.includes(query);
}

const defaultRunHistoryFilter: RunHistoryFilter = {
  strategy_id: ALL_FILTER_VALUE,
  strategy_version: ALL_FILTER_VALUE,
  preset_id: "",
  benchmark_family: "",
  tag: "",
  dataset_identity: "",
  filter_expr: "",
  collection_query_label: "",
};

function sanitizeRunHistoryFilter(filter: RunHistoryFilter): RunHistoryFilter {
  return {
    strategy_id: filter.strategy_id || ALL_FILTER_VALUE,
    strategy_version: filter.strategy_version || ALL_FILTER_VALUE,
    preset_id: filter.preset_id.trim(),
    benchmark_family: filter.benchmark_family.trim(),
    tag: filter.tag.trim(),
    dataset_identity: filter.dataset_identity.trim(),
    filter_expr: filter.filter_expr.trim(),
    collection_query_label: filter.collection_query_label.trim(),
  };
}

function cloneRunHistoryFilter(filter: RunHistoryFilter): RunHistoryFilter {
  return sanitizeRunHistoryFilter({ ...filter });
}

function hasRunHistoryFilterCriteria(filter: RunHistoryFilter) {
  const candidate = sanitizeRunHistoryFilter(filter);
  return Boolean(
    candidate.strategy_id !== ALL_FILTER_VALUE
    || candidate.strategy_version !== ALL_FILTER_VALUE
    || candidate.preset_id
    || candidate.benchmark_family
    || candidate.tag
    || candidate.dataset_identity
    || candidate.filter_expr,
  );
}

function areRunHistoryFiltersEquivalent(left: RunHistoryFilter, right: RunHistoryFilter) {
  const normalizedLeft = sanitizeRunHistoryFilter(left);
  const normalizedRight = sanitizeRunHistoryFilter(right);
  return (
    normalizedLeft.strategy_id === normalizedRight.strategy_id
    && normalizedLeft.strategy_version === normalizedRight.strategy_version
    && normalizedLeft.preset_id === normalizedRight.preset_id
    && normalizedLeft.benchmark_family === normalizedRight.benchmark_family
    && normalizedLeft.tag === normalizedRight.tag
    && normalizedLeft.dataset_identity === normalizedRight.dataset_identity
    && normalizedLeft.filter_expr === normalizedRight.filter_expr
  );
}

function buildRunHistorySavedFilterStorageKey(surfaceKey: RunHistorySurfaceKey) {
  return `${RUN_HISTORY_SAVED_FILTER_STORAGE_KEY_PREFIX}:${surfaceKey}`;
}

function normalizeSavedRunHistoryFilterPreset(value: unknown): SavedRunHistoryFilterPreset | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const candidate = value as Partial<SavedRunHistoryFilterPreset>;
  if (
    typeof candidate.filter_id !== "string"
    || typeof candidate.label !== "string"
    || typeof candidate.created_at !== "string"
    || typeof candidate.updated_at !== "string"
    || !candidate.filter
    || typeof candidate.filter !== "object"
  ) {
    return null;
  }
  const filterCandidate = candidate.filter as Partial<RunHistoryFilter>;
  return {
    filter_id: candidate.filter_id,
    label: candidate.label,
    created_at: candidate.created_at,
    updated_at: candidate.updated_at,
    filter: sanitizeRunHistoryFilter({
      ...defaultRunHistoryFilter,
      strategy_id:
        typeof filterCandidate.strategy_id === "string"
          ? filterCandidate.strategy_id
          : defaultRunHistoryFilter.strategy_id,
      strategy_version:
        typeof filterCandidate.strategy_version === "string"
          ? filterCandidate.strategy_version
          : defaultRunHistoryFilter.strategy_version,
      preset_id:
        typeof filterCandidate.preset_id === "string"
          ? filterCandidate.preset_id
          : defaultRunHistoryFilter.preset_id,
      benchmark_family:
        typeof filterCandidate.benchmark_family === "string"
          ? filterCandidate.benchmark_family
          : defaultRunHistoryFilter.benchmark_family,
      tag: typeof filterCandidate.tag === "string" ? filterCandidate.tag : defaultRunHistoryFilter.tag,
      dataset_identity:
        typeof filterCandidate.dataset_identity === "string"
          ? filterCandidate.dataset_identity
          : defaultRunHistoryFilter.dataset_identity,
      filter_expr:
        typeof filterCandidate.filter_expr === "string"
          ? filterCandidate.filter_expr
          : defaultRunHistoryFilter.filter_expr,
      collection_query_label:
        typeof filterCandidate.collection_query_label === "string"
          ? filterCandidate.collection_query_label
          : defaultRunHistoryFilter.collection_query_label,
    }),
  };
}

function loadSavedRunHistoryFilterPresets(surfaceKey: RunHistorySurfaceKey): SavedRunHistoryFilterPreset[] {
  if (typeof window === "undefined") {
    return [];
  }
  try {
    const raw = window.localStorage.getItem(buildRunHistorySavedFilterStorageKey(surfaceKey));
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as Partial<SavedRunHistoryFilterPresetStateV1> | null;
    if (parsed?.version !== 1 || !Array.isArray(parsed.filters)) {
      return [];
    }
    return parsed.filters
      .map((entry) => normalizeSavedRunHistoryFilterPreset(entry))
      .filter((entry): entry is SavedRunHistoryFilterPreset => entry !== null);
  } catch {
    return [];
  }
}

function persistSavedRunHistoryFilterPresets(
  surfaceKey: RunHistorySurfaceKey,
  presets: SavedRunHistoryFilterPreset[],
) {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(
      buildRunHistorySavedFilterStorageKey(surfaceKey),
      JSON.stringify({
        version: 1,
        filters: presets.map((entry) => ({
          ...entry,
          filter: sanitizeRunHistoryFilter(entry.filter),
        })),
      } satisfies SavedRunHistoryFilterPresetStateV1),
    );
  } catch {
    // Ignore localStorage failures for saved run-history filters.
  }
}

function describeRunHistoryFilter(filter: RunHistoryFilter, presets: ExperimentPreset[], strategies: Strategy[]) {
  const candidate = sanitizeRunHistoryFilter(filter);
  const parts: string[] = [];
  if (candidate.strategy_id !== ALL_FILTER_VALUE) {
    const strategy = strategies.find((item) => item.strategy_id === candidate.strategy_id);
    parts.push(`Strategy ${strategy?.name ?? candidate.strategy_id}`);
  }
  if (candidate.strategy_version !== ALL_FILTER_VALUE) {
    parts.push(`Version ${candidate.strategy_version}`);
  }
  if (candidate.preset_id) {
    const preset = presets.find((item) => item.preset_id === candidate.preset_id);
    parts.push(`Preset ${preset?.name ?? candidate.preset_id}`);
  }
  if (candidate.benchmark_family) {
    parts.push(`Benchmark ${candidate.benchmark_family}`);
  }
  if (candidate.tag) {
    parts.push(`Tag ${candidate.tag}`);
  }
  if (candidate.dataset_identity) {
    parts.push(`Dataset ${candidate.dataset_identity}`);
  }
  if (candidate.filter_expr) {
    parts.push(
      candidate.collection_query_label
        ? `Collection ${candidate.collection_query_label}`
        : "Collection expression",
    );
  }
  return parts;
}

const DEFAULT_COMPARISON_INTENT: ComparisonIntent = "benchmark_validation";
const comparisonIntentOptions: ComparisonIntent[] = [
  "benchmark_validation",
  "execution_regression",
  "strategy_tuning",
];

function parseExperimentTags(value: string) {
  return Array.from(
    new Set(
      value
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean),
    ),
  );
}

function parseJsonObjectInput(value: string) {
  const trimmed = value.trim();
  if (!trimmed) {
    return {};
  }
  const parsed = JSON.parse(trimmed) as unknown;
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error("Parameter bundle must be a JSON object.");
  }
  return parsed as Record<string, unknown>;
}

function formatPresetLifecycleStage(stage: string) {
  return stage.replaceAll("_", " ");
}

function buildRunSubmissionPayload(form: typeof defaultRunForm, extras: Record<string, unknown> = {}) {
  const presetId = form.preset_id.trim();
  const benchmarkFamily = form.benchmark_family.trim();
  return {
    strategy_id: form.strategy_id,
    symbol: form.symbol,
    timeframe: form.timeframe,
    initial_cash: form.initial_cash,
    fee_rate: form.fee_rate,
    slippage_bps: form.slippage_bps,
    parameters: {},
    tags: parseExperimentTags(form.tags_text),
    preset_id: presetId || null,
    benchmark_family: benchmarkFamily || null,
    ...extras,
  };
}

function normalizeRunFormPreset(
  current: typeof defaultRunForm,
  presets: ExperimentPreset[],
) {
  if (!current.preset_id) {
    return current;
  }
  const matchingPreset = presets.find((preset) => preset.preset_id === current.preset_id);
  if (
    matchingPreset &&
    matchingPreset.lifecycle.stage !== "archived" &&
    (!matchingPreset.strategy_id || matchingPreset.strategy_id === current.strategy_id) &&
    (!matchingPreset.timeframe || matchingPreset.timeframe === current.timeframe)
  ) {
    return current;
  }
  return {
    ...current,
    preset_id: "",
  };
}

function resolveMarketDataSymbol(instrumentId: string) {
  const separatorIndex = instrumentId.indexOf(":");
  return separatorIndex >= 0 ? instrumentId.slice(separatorIndex + 1) : instrumentId;
}

function buildMarketDataInstrumentFocusKey(
  instrument: MarketDataStatus["instruments"][number],
) {
  return `${instrument.instrument_id}|${instrument.timeframe}`;
}

function isMarketDataInstrumentAtRisk(
  instrument: MarketDataStatus["instruments"][number],
) {
  return (
    instrument.sync_status !== "synced"
    || instrument.failure_count_24h > 0
    || (instrument.lag_seconds ?? 0) > 0
    || instrument.backfill_gap_windows.length > 0
    || instrument.issues.length > 0
  );
}

function resolvePreferredMarketDataInstrument(
  marketStatus: MarketDataStatus,
  preferredKey: string | null,
) {
  if (preferredKey) {
    const preferredInstrument = marketStatus.instruments.find(
      (instrument) => buildMarketDataInstrumentFocusKey(instrument) === preferredKey,
    );
    if (preferredInstrument) {
      return preferredInstrument;
    }
  }
  return (
    marketStatus.instruments.find((instrument) => isMarketDataInstrumentAtRisk(instrument))
    ?? marketStatus.instruments[0]
    ?? null
  );
}

function formatWorkflowToken(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  return value.replaceAll("_", " ");
}

type LinkedMarketInstrumentContext = {
  instrument: MarketDataStatus["instruments"][number];
  focusKey: string;
  symbol: string;
  timeframe: string;
  matchReason: string;
  candidateCount: number;
  candidateLabels: string[];
  primaryFocusPolicy: string;
  primaryFocusReason: string;
};

type MarketDataLinkableAlertRecord = {
  alert_id?: string | null;
  category?: string | null;
  summary: string;
  detail: string;
  run_id?: string | null;
  session_id?: string | null;
  symbol?: string | null;
  symbols?: string[];
  timeframe?: string | null;
  primary_focus?: OperatorAlertPrimaryFocus | null;
  source?: string | null;
  provider_recovery_symbols?: string[];
  provider_recovery_timeframe?: string | null;
};

type MarketDataIncidentHistoryEntry = {
  entryId: string;
  occurredAt: string;
  sourceLabel: string;
  statusLabel: string;
  summary: string;
  detail: string;
  tone: "critical" | "warning" | "neutral";
};

type ProviderRecoveryMarketContextSummary = {
  summary: string;
  fieldSummaries: string[];
};

type MarketDataProviderProvenanceEventRecord = {
  event: OperatorVisibility["incident_events"][number];
  link: LinkedMarketInstrumentContext | null;
  provider: string;
  vendorField: string;
  provenanceSummary: string;
  fieldSummaries: string[];
  severityRank: number;
  occurredAtMs: number;
  searchText: string;
};

type MarketDataPrimaryFocusSelection = {
  instrument: MarketDataStatus["instruments"][number];
  candidateCount: number;
  candidateLabels: string[];
  primaryFocusPolicy: string;
  primaryFocusReason: string;
};

function formatMarketContextFieldProvenance(
  label: string,
  provenance?: OperatorAlertMarketContextProvenance["symbol"] | null,
) {
  if (!provenance) {
    return null;
  }
  const scope = provenance.scope?.trim() || null;
  const path = provenance.path?.trim() || null;
  if (!scope && !path) {
    return null;
  }
  return `${label} ${scope && path ? `${scope} -> ${path}` : scope ?? path}`;
}

function summarizeProviderRecoveryMarketContextProvenance(providerRecovery: {
  provider?: string | null;
  market_context_provenance?: OperatorAlertMarketContextProvenance | null;
}): ProviderRecoveryMarketContextSummary | null {
  const provenance = providerRecovery.market_context_provenance;
  if (!provenance) {
    return null;
  }
  const fieldSummaries = [
    formatMarketContextFieldProvenance("symbol", provenance.symbol),
    formatMarketContextFieldProvenance("symbols", provenance.symbols),
    formatMarketContextFieldProvenance("timeframe", provenance.timeframe),
    formatMarketContextFieldProvenance("primary focus", provenance.primary_focus),
  ].filter((value): value is string => Boolean(value));
  const summaryLead = [
    provenance.provider?.trim() || providerRecovery.provider?.trim() || null,
    provenance.vendor_field?.trim() ? `via ${provenance.vendor_field.trim()}` : null,
  ].filter(Boolean);
  const parts = [
    summaryLead.length ? summaryLead.join(" ") : null,
    ...fieldSummaries,
  ].filter((value): value is string => Boolean(value));
  if (!parts.length) {
    return null;
  }
  return {
    summary: `Market-context provenance: ${parts.join(" / ")}`,
    fieldSummaries,
  };
}

function serializeLinkedMarketInstrumentContext(link: LinkedMarketInstrumentContext | null) {
  if (!link) {
    return null;
  }
  return {
    symbol: link.symbol,
    timeframe: link.timeframe,
    match_reason: link.matchReason,
    candidate_count: link.candidateCount,
    candidate_labels: link.candidateLabels,
    primary_focus_policy: link.primaryFocusPolicy,
    primary_focus_reason: link.primaryFocusReason,
  };
}

function getOperatorSeverityRank(severity: string) {
  switch (severity) {
    case "critical":
      return 3;
    case "warning":
      return 2;
    case "info":
      return 1;
    default:
      return 0;
  }
}

function normalizeMarketDataProvenanceExportSort(
  value: unknown,
): MarketDataProvenanceExportSort {
  return value === "oldest" || value === "provider" || value === "severity" || value === "newest"
    ? value
    : defaultMarketDataProvenanceExportFilterState.sort;
}

function normalizeMarketDataProvenanceExportFilterState(
  value: unknown,
): MarketDataProvenanceExportFilterState {
  if (!value || typeof value !== "object") {
    return { ...defaultMarketDataProvenanceExportFilterState };
  }
  const candidate = value as Partial<MarketDataProvenanceExportFilterState>;
  return {
    provider:
      typeof candidate.provider === "string" && candidate.provider.trim().length
        ? candidate.provider
        : defaultMarketDataProvenanceExportFilterState.provider,
    vendor_field:
      typeof candidate.vendor_field === "string" && candidate.vendor_field.trim().length
        ? candidate.vendor_field
        : defaultMarketDataProvenanceExportFilterState.vendor_field,
    search_query:
      typeof candidate.search_query === "string"
        ? candidate.search_query
        : defaultMarketDataProvenanceExportFilterState.search_query,
    sort: normalizeMarketDataProvenanceExportSort(candidate.sort),
  };
}

function normalizeMarketDataProvenanceExportHistoryEntry(
  value: unknown,
): MarketDataProvenanceExportHistoryEntry | null {
  if (!value || typeof value !== "object") {
    return null;
  }

  return {
    selectedProviderProvenanceSchedulerExportEntry, providerProvenanceAnalyticsRequestIdRef, providerProvenanceSchedulerAnalyticsRequestIdRef, providerProvenanceSchedulerHistoryRequestIdRef, providerProvenanceSchedulerAlertHistoryRequestIdRef, providerProvenanceSchedulerSearchDashboardRequestIdRef,
    providerProvenanceSchedulerSearchModerationPolicyCatalogRequestIdRef, providerProvenanceSchedulerSearchModerationPolicyCatalogAuditRequestIdRef, providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyRequestIdRef, providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyAuditRequestIdRef, providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPolicyRequestIdRef, providerProvenanceSchedulerSearchModerationCatalogGovernanceMetaPlanRequestIdRef,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePlanRequestIdRef, providerProvenanceSchedulerSearchModerationPlanRequestIdRef, providerProvenanceSchedulerExportRequestIdRef, providerProvenanceSchedulerStitchedReportViewRequestIdRef, providerProvenanceSchedulerStitchedReportViewAuditRequestIdRef, providerProvenanceSchedulerSearchModerationPolicyCatalogHistoryRequestIdRef,
    providerProvenanceSchedulerSearchModerationCatalogGovernancePolicyHistoryRequestIdRef, comparisonHistoryTabIdentity, providerProvenanceSchedulerNarrativeGovernancePlanRequestIdRef, providerProvenanceSchedulerStitchedReportGovernancePlanRequestIdRef, providerProvenanceSchedulerStitchedReportGovernanceRegistryPlanRequestIdRef, providerProvenanceWorkspaceRegistryLoadedRef,
    marketDataWorkflowRequestIdRef, providerProvenanceSchedulerAutomationRef, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchySteps, filteredProviderProvenanceSchedulerNarrativeGovernancePlans, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateEntries, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalog,
    selectedProviderProvenanceSchedulerNarrativeGovernancePlan, selectedFilteredProviderProvenanceSchedulerNarrativeGovernancePlans, providerProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateNameMap, loadAll, setSelectedComparisonRunIds, queueComparisonHistoryWriteMode,
    setSelectedComparisonScoreLink, setComparisonIntent, selectedComparisonRunIds, comparisonHistoryStep, comparisonHistorySharedSyncState, comparisonHistorySyncAuditTrail,
    comparisonHistoryPanel, visibleComparisonHistoryEntries, comparisonHistoryPanelOpen, comparisonHistorySearchQuery, comparisonHistoryShowPinnedOnly, comparisonHistoryAuditFilter,
    comparisonHistoryShowResolvedAuditEntries, visibleComparisonHistoryActiveIndex, selectedComparisonScoreLink, runComparison, runComparisonLoading, runComparisonError,
    handleComparisonIntentChange, handleSelectedComparisonScoreLinkChange, setComparisonHistoryPanelOpen, setComparisonHistorySearchQuery, setComparisonHistoryShowPinnedOnly, setComparisonHistoryAuditFilter,
    setComparisonHistoryShowResolvedAuditEntries, setExpandedHistoryConflictReviewIds, setExpandedWorkspaceScoreDetailIds, setFocusedWorkspaceScoreDetailSources, setFocusedWorkspaceScoreDetailSignalKeys, setExpandedWorkspaceScoreSignalDetailIds,
    setCollapsedWorkspaceScoreSignalSubviewIds, setCollapsedWorkspaceScoreSignalNestedSubviewIds, setFocusedWorkspaceScoreSignalMicroViews, setFocusedWorkspaceScoreSignalMicroInteractions, setHoveredWorkspaceScoreSignalMicroTargets, setScrubbedWorkspaceScoreSignalMicroSteps,
    setSelectedWorkspaceScoreSignalMicroNotePages, setActiveWorkspaceOverviewRowId, handleNavigateComparisonHistoryEntry, handleNavigateComparisonHistoryRelative, handleToggleComparisonHistoryEntryPinned, handleTrimComparisonHistoryEntries,
    handleSetComparisonHistoryConflictFieldSource, handleSetComparisonHistoryConflictFieldSourceAll, handleApplyComparisonHistoryConflictResolution, handleSetComparisonHistoryPreferenceFieldSource, handleSetComparisonHistoryPreferenceFieldSourceAll, handleApplyComparisonHistoryPreferenceResolution,
    handleSetComparisonHistoryWorkspaceFieldSource, handleSetComparisonHistoryWorkspaceFieldSourceAll, handleUseComparisonHistoryWorkspaceRankedSources, handleApplyComparisonHistoryWorkspaceResolution, comparisonIntent, latestWorkspaceSyncState,
    expandedHistoryConflictReviewIds, expandedWorkspaceScoreDetailIds, focusedWorkspaceScoreDetailSources, focusedWorkspaceScoreDetailSignalKeys, expandedWorkspaceScoreSignalDetailIds, collapsedWorkspaceScoreSignalSubviewIds,
    collapsedWorkspaceScoreSignalNestedSubviewIds, focusedWorkspaceScoreSignalMicroViews, focusedWorkspaceScoreSignalMicroInteractions, hoveredWorkspaceScoreSignalMicroTargets, scrubbedWorkspaceScoreSignalMicroSteps, selectedWorkspaceScoreSignalMicroNotePages,
    activeWorkspaceOverviewRowId, expandedGapRows, activeGapWindowPickerRowKey, setExpandedGapWindowSelections, setActiveGapWindowPickerRowKey, setExpandedGapRows,
    expandedGapWindowSelections, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyTemplateIdSet, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogEntries, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogIdSet, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepIdSet, selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStep,
    selectedProviderProvenanceSchedulerNarrativeGovernancePolicyCatalogHierarchyStepVersions, selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplate, selectedProviderProvenanceSchedulerNarrativeGovernanceHierarchyStepTemplateIdSet, selectedProviderProvenanceSchedulerNarrativeTemplateEntries, selectedProviderProvenanceSchedulerNarrativeTemplateIdSet, selectedProviderProvenanceSchedulerNarrativeRegistryEntries,
    selectedProviderProvenanceSchedulerNarrativeRegistryIdSet, providerProvenanceSchedulerNarrativeTemplateNameMap, providerProvenanceSchedulerNarrativeGovernanceQueueSummary, selectedProviderProvenanceSchedulerNarrativeGovernancePlanIdSet, selectedProviderProvenanceSchedulerStitchedReportViewEntries, selectedProviderProvenanceSchedulerStitchedReportViewIdSet,
    providerProvenanceSchedulerStitchedReportGovernanceQueueSummary, providerProvenanceSchedulerStitchedReportGovernancePolicyCatalogs, providerProvenanceSchedulerStitchedReportGovernanceRegistryQueueSummary, providerProvenanceSchedulerStitchedReportGovernanceRegistryPolicyCatalogs, selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryEntries, filteredProviderProvenanceSchedulerStitchedReportGovernanceRegistries,
    selectedProviderProvenanceSchedulerStitchedReportGovernanceRegistryIdSet,
  };
}
