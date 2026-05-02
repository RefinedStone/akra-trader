// @ts-nocheck
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
