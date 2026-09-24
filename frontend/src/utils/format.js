// Small formatting helpers shared across pages.

/** Format a number with thousands separators and optional decimals. */
export function formatNumber(value, decimals = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value)))
    return "—";
  return Number(value).toLocaleString("en-US", {
    minimumFractionDigits: 0,
    maximumFractionDigits: decimals,
  });
}

/** Format a fraction (0-1) or percentage value as a "xx.x%" string. */
export function formatPercent(value, decimals = 1) {
  if (value === null || value === undefined || Number.isNaN(Number(value)))
    return "—";
  const num = Number(value);
  const pct = num <= 1 ? num * 100 : num;
  return `${pct.toFixed(decimals)}%`;
}

/** Human-readable byte size. */
export function formatBytes(bytes) {
  if (!bytes && bytes !== 0) return "—";
  const units = ["B", "KB", "MB", "GB"];
  let v = bytes;
  let i = 0;
  while (v >= 1024 && i < units.length - 1) {
    v /= 1024;
    i += 1;
  }
  return `${v.toFixed(1)} ${units[i]}`;
}

/** Pick a colour for a safety / confidence score (0-100). */
export function scoreColor(score) {
  if (score >= 70) return "#22c55e";
  if (score >= 45) return "#eab308";
  return "#ef4444";
}

/** Chart palette used across Recharts components. */
export const CHART_COLORS = [
  "#4f8cff",
  "#a855f7",
  "#22d3ee",
  "#f97316",
  "#22c55e",
  "#eab308",
  "#ef4444",
];
