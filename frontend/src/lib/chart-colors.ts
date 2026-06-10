/** Vibrant bar colors for Recharts (SVG fill does not reliably resolve CSS vars). */
export const CHART_BAR_COLORS = [
  "#2563eb", // blue
  "#059669", // emerald
  "#d97706", // amber
  "#7c3aed", // violet
  "#e11d48", // rose
  "#0891b2", // cyan
  "#65a30d", // lime
  "#db2777", // pink
  "#4f46e5", // indigo
  "#ea580c", // orange
] as const;

export function chartBarColor(index: number): string {
  return CHART_BAR_COLORS[index % CHART_BAR_COLORS.length];
}
