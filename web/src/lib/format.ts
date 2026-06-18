import type { CoreWebVitals } from "./api";

export type Tone = "default" | "success" | "warning" | "danger" | "info";

// Text-color utility per tone, for big numerals that carry their own meaning.
export const TONE_TEXT: Record<Tone, string> = {
  default: "text-on-surface",
  success: "text-success",
  warning: "text-warning",
  danger: "text-error",
  info: "text-info",
};

// Prepend https:// when the user types a bare host, and trim surrounding space.
export function normalizeUrl(raw: string): string {
  const trimmed = raw.trim();
  if (!trimmed) return "";
  return /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
}

// Strip scheme and trailing slash for a compact on-screen label.
export function displayUrl(url: string): string {
  return url.replace(/^https?:\/\//i, "").replace(/\/+$/, "");
}

// Score thresholds mirror the PDF report (_score_color): 80+ good, 60+ fair.
export function scoreTone(score: number): Tone {
  if (score >= 80) return "success";
  if (score >= 60) return "warning";
  return "danger";
}

// Grade mapping mirrors the PDF report (_grade_color).
export function gradeTone(grade: string): Tone {
  if (grade === "A" || grade === "B") return "success";
  if (grade === "C" || grade === "D") return "warning";
  if (grade === "F") return "danger";
  return "default";
}

// Impact/effort intensity mirrors the PDF report (_level_color).
export function levelTone(level: string): Tone {
  if (level === "High") return "danger";
  if (level === "Medium") return "warning";
  if (level === "Low") return "success";
  return "default";
}

export type VitalKey = keyof CoreWebVitals;
export type Rating = "good" | "needs-improvement" | "poor";

interface VitalSpec {
  label: string;
  name: string;
  unit: "s" | "ms" | "";
  good: number;
  poor: number;
}

// Lighthouse numericValues are milliseconds (CLS is unitless). Thresholds are
// Google's good / needs-improvement boundaries.
export const VITALS: Record<VitalKey, VitalSpec> = {
  lcp: { label: "LCP", name: "Largest Contentful Paint", unit: "s", good: 2500, poor: 4000 },
  cls: { label: "CLS", name: "Cumulative Layout Shift", unit: "", good: 0.1, poor: 0.25 },
  fcp: { label: "FCP", name: "First Contentful Paint", unit: "s", good: 1800, poor: 3000 },
  ttfb: { label: "TTFB", name: "Time to First Byte", unit: "ms", good: 800, poor: 1800 },
  fid: { label: "FID", name: "Max Potential FID", unit: "ms", good: 100, poor: 300 },
  speed_index: { label: "SI", name: "Speed Index", unit: "s", good: 3400, poor: 5800 },
};

export const VITAL_ORDER: VitalKey[] = ["lcp", "cls", "fcp", "ttfb", "fid", "speed_index"];

export function formatVital(key: VitalKey, value: number): string {
  const { unit } = VITALS[key];
  if (unit === "s") return `${(value / 1000).toFixed(2)}s`;
  if (unit === "ms") return `${Math.round(value)} ms`;
  return value.toFixed(3);
}

export function vitalRating(key: VitalKey, value: number): Rating {
  const { good, poor } = VITALS[key];
  if (value <= good) return "good";
  if (value <= poor) return "needs-improvement";
  return "poor";
}

export function ratingTone(rating: Rating): Tone {
  if (rating === "good") return "success";
  if (rating === "needs-improvement") return "warning";
  return "danger";
}
