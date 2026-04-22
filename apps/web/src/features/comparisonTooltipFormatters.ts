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

export function formatComparisonTooltipTuningValue(value: number) {
  if (Number.isInteger(value)) {
    return String(value);
  }
  return value.toFixed(2).replace(/\.?0+$/, "");
}
