import type {
  ComparisonTooltipConflictSessionSummary,
  ComparisonTooltipConflictSessionSummarySession,
  ComparisonTooltipConflictSessionUiState,
  ComparisonTooltipPresetConflictPreviewRow,
  ComparisonTooltipPresetImportResolution,
} from "../controlRoomDefinitions";

function formatTimestampValue(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  return value;
}

export function formatComparisonTooltipConflictSessionRelativeTime(
  timestamp: number,
  now: Date,
) {
  const elapsedMs = timestamp - now.getTime();
  const absElapsedMs = Math.abs(elapsedMs);
  const minuteMs = 60 * 1000;
  const hourMs = 60 * minuteMs;
  const dayMs = 24 * hourMs;
  const weekMs = 7 * dayMs;
  const monthMs = 30 * dayMs;
  const yearMs = 365 * dayMs;

  const formatRelative = (value: number, unit: Intl.RelativeTimeFormatUnit) =>
    new Intl.RelativeTimeFormat(undefined, { numeric: "auto", style: "short" }).format(
      value,
      unit,
    );

  if (absElapsedMs < minuteMs) {
    return formatRelative(Math.round(elapsedMs / 1000), "second");
  }
  if (absElapsedMs < hourMs) {
    return formatRelative(Math.round(elapsedMs / minuteMs), "minute");
  }
  if (absElapsedMs < dayMs) {
    return formatRelative(Math.round(elapsedMs / hourMs), "hour");
  }
  if (absElapsedMs < weekMs) {
    return formatRelative(Math.round(elapsedMs / dayMs), "day");
  }
  if (absElapsedMs < monthMs) {
    return formatRelative(Math.round(elapsedMs / weekMs), "week");
  }
  if (absElapsedMs < yearMs) {
    return formatRelative(Math.round(elapsedMs / monthMs), "month");
  }
  return formatRelative(Math.round(elapsedMs / yearMs), "year");
}

export function formatRelativeTimestampLabel(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  const timestamp = Date.parse(value);
  if (!Number.isFinite(timestamp)) {
    return formatTimestampValue(value);
  }
  const relative = formatComparisonTooltipConflictSessionRelativeTime(timestamp, new Date());
  return relative ? `${relative} · ${formatTimestampValue(value)}` : formatTimestampValue(value);
}

export function formatComparisonTooltipConflictSessionSummary(
  summary: Omit<ComparisonTooltipConflictSessionSummary, "label">,
) {
  if (summary.session_count === 1) {
    return summary.preset_name;
  }
  return `${summary.preset_name} (${summary.session_count} saved sessions)`;
}

export function formatComparisonTooltipConflictSessionSummarySession(
  session: Omit<ComparisonTooltipConflictSessionSummarySession, "label">,
  index: number,
  totalSessions: number,
) {
  if (totalSessions === 1) {
    return "Saved session";
  }
  return `Saved session ${index + 1}`;
}

export function parseComparisonTooltipConflictSessionUpdatedAt(value: string | null) {
  if (!value) {
    return 0;
  }
  const timestamp = Date.parse(value);
  return Number.isFinite(timestamp) ? timestamp : 0;
}

function formatComparisonTooltipConflictSessionUpdatedAtLabel(
  value: string | null,
  referenceNowMs: number,
) {
  const timestamp = parseComparisonTooltipConflictSessionUpdatedAt(value);
  if (!timestamp) {
    return "updated time unavailable";
  }
  const date = new Date(timestamp);
  const now = new Date(referenceNowMs);
  const absoluteLabel = new Intl.DateTimeFormat(undefined, {
    ...(date.getFullYear() === now.getFullYear() ? {} : { year: "numeric" }),
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    month: "short",
  }).format(date);
  const relativeLabel = formatComparisonTooltipConflictSessionRelativeTime(timestamp, now);
  return relativeLabel
    ? `updated ${relativeLabel} · ${absoluteLabel}`
    : `updated ${absoluteLabel}`;
}

export function formatComparisonTooltipConflictSessionMetadata(
  session: ComparisonTooltipConflictSessionUiState,
  hash: string | null,
  referenceNowMs: number,
) {
  const metadata: string[] = [];
  metadata.push(
    formatComparisonTooltipConflictSessionUpdatedAtLabel(session.updated_at, referenceNowMs),
  );
  metadata.push(
    session.show_unchanged_conflict_rows ? "unchanged rows visible" : "unchanged rows hidden",
  );

  const groupStates = Object.values(session.collapsed_unchanged_groups);
  const collapsedCount = groupStates.filter(Boolean).length;
  const expandedCount = groupStates.length - collapsedCount;

  if (!groupStates.length) {
    metadata.push("default group layout");
    return metadata;
  }

  if (expandedCount && collapsedCount) {
    metadata.push(`${expandedCount} expanded, ${collapsedCount} collapsed`);
    return metadata;
  }
  if (expandedCount) {
    metadata.push(`${expandedCount} expanded group${expandedCount === 1 ? "" : "s"}`);
  } else {
    metadata.push(`${collapsedCount} collapsed group${collapsedCount === 1 ? "" : "s"}`);
  }
  if (hash) {
    metadata.push(`ID ${hash.slice(0, 8)}`);
  }
  return metadata;
}

export function getComparisonTooltipConflictSessionRelativeTimeRefreshMs(
  timestamps: number[],
  referenceNowMs: number,
) {
  if (!timestamps.length) {
    return null;
  }

  const youngestAgeMs = timestamps.reduce((youngest, timestamp) => {
    const ageMs = Math.abs(referenceNowMs - timestamp);
    return Math.min(youngest, ageMs);
  }, Number.POSITIVE_INFINITY);

  const minuteMs = 60 * 1000;
  const hourMs = 60 * minuteMs;
  const dayMs = 24 * hourMs;
  const weekMs = 7 * dayMs;
  const monthMs = 30 * dayMs;

  if (youngestAgeMs < minuteMs) {
    return 5 * 1000;
  }
  if (youngestAgeMs < hourMs) {
    return minuteMs;
  }
  if (youngestAgeMs < dayMs) {
    return 5 * minuteMs;
  }
  if (youngestAgeMs < weekMs) {
    return hourMs;
  }
  if (youngestAgeMs < monthMs) {
    return 6 * hourMs;
  }
  return dayMs;
}

export function hashComparisonTooltipConflictSessionRaw(value: string) {
  let hash = 5381;
  for (let index = 0; index < value.length; index += 1) {
    hash = (hash * 33) ^ value.charCodeAt(index);
  }
  return (hash >>> 0).toString(36);
}

export function formatComparisonTooltipTuningValue(value: number) {
  if (Number.isInteger(value)) {
    return String(value);
  }
  return value.toFixed(2).replace(/\.?0+$/, "");
}

export function formatComparisonTooltipTuningDelta(existingValue: number, incomingValue: number) {
  const delta = incomingValue - existingValue;
  if (delta === 0) {
    return {
      direction: "same" as const,
      label: "match",
    };
  }
  return {
    direction: delta > 0 ? ("higher" as const) : ("lower" as const),
    label: `${delta > 0 ? "higher " : "lower "}${delta > 0 ? "+" : ""}${formatComparisonTooltipTuningValue(delta)}`,
  };
}

export function formatComparisonTooltipPresetConflictGroupSummary(
  rows: ComparisonTooltipPresetConflictPreviewRow[],
) {
  const changedCount = rows.filter((row) => row.changed).length;
  const higherCount = rows.filter((row) => row.delta_direction === "higher").length;
  const lowerCount = rows.filter((row) => row.delta_direction === "lower").length;
  const sameCount = rows.filter((row) => row.delta_direction === "same").length;

  if (!changedCount) {
    return `${sameCount} match${sameCount === 1 ? "" : "es"}`;
  }

  const parts = [`${changedCount} changed`];
  if (higherCount) {
    parts.push(`${higherCount} higher`);
  }
  if (lowerCount) {
    parts.push(`${lowerCount} lower`);
  }
  if (sameCount) {
    parts.push(`${sameCount} match${sameCount === 1 ? "" : "es"}`);
  }
  return parts.join(" · ");
}

export function formatComparisonTooltipPresetImportFeedback(
  resolution: ComparisonTooltipPresetImportResolution,
  options?: { verb?: "Imported" | "Loaded" },
) {
  const verb = options?.verb ?? "Imported";
  if (!resolution.conflicted) {
    return `${verb} preset "${resolution.final_preset_name}" into the current tuning bundle.`;
  }
  if (resolution.renamed) {
    return `${verb} preset "${resolution.imported_preset_name}" as "${resolution.final_preset_name}" because that name already existed.`;
  }
  return `${verb} preset "${resolution.final_preset_name}" and overwrote the existing preset with the same name.`;
}
