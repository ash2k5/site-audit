import { describe, expect, test } from "vitest";
import {
  displayUrl,
  formatVital,
  gradeTone,
  levelTone,
  normalizeUrl,
  ratingTone,
  scoreTone,
  vitalRating,
} from "../src/lib/format";

describe("normalizeUrl", () => {
  test("prepends https:// to a bare host", () => {
    expect(normalizeUrl("example.com")).toBe("https://example.com");
  });
  test("keeps an existing scheme and trims", () => {
    expect(normalizeUrl("  http://example.com  ")).toBe("http://example.com");
  });
  test("returns empty for blank input", () => {
    expect(normalizeUrl("   ")).toBe("");
  });
});

describe("displayUrl", () => {
  test("strips scheme and trailing slash", () => {
    expect(displayUrl("https://example.com/")).toBe("example.com");
  });
});

describe("scoreTone", () => {
  test.each([
    [100, "success"],
    [80, "success"],
    [79, "warning"],
    [60, "warning"],
    [59, "danger"],
    [0, "danger"],
  ])("score %i -> %s", (score, tone) => {
    expect(scoreTone(score)).toBe(tone);
  });
});

describe("gradeTone", () => {
  test.each([
    ["A", "success"],
    ["B", "success"],
    ["C", "warning"],
    ["D", "warning"],
    ["F", "danger"],
    ["?", "default"],
  ])("grade %s -> %s", (grade, tone) => {
    expect(gradeTone(grade)).toBe(tone);
  });
});

describe("levelTone", () => {
  test.each([
    ["High", "danger"],
    ["Medium", "warning"],
    ["Low", "success"],
  ])("level %s -> %s", (level, tone) => {
    expect(levelTone(level)).toBe(tone);
  });
});

describe("formatVital", () => {
  test("renders seconds metrics with two decimals", () => {
    expect(formatVital("lcp", 2500)).toBe("2.50s");
    expect(formatVital("speed_index", 3400)).toBe("3.40s");
  });
  test("rounds millisecond metrics", () => {
    expect(formatVital("ttfb", 812.4)).toBe("812 ms");
    expect(formatVital("fid", 90)).toBe("90 ms");
  });
  test("renders CLS unitless with three decimals", () => {
    expect(formatVital("cls", 0.0523)).toBe("0.052");
  });
});

describe("vitalRating", () => {
  test("LCP boundaries", () => {
    expect(vitalRating("lcp", 2500)).toBe("good");
    expect(vitalRating("lcp", 3000)).toBe("needs-improvement");
    expect(vitalRating("lcp", 4001)).toBe("poor");
  });
  test("CLS boundaries", () => {
    expect(vitalRating("cls", 0.1)).toBe("good");
    expect(vitalRating("cls", 0.25)).toBe("needs-improvement");
    expect(vitalRating("cls", 0.3)).toBe("poor");
  });
});

describe("ratingTone", () => {
  test.each([
    ["good", "success"],
    ["needs-improvement", "warning"],
    ["poor", "danger"],
  ] as const)("rating %s -> %s", (rating, tone) => {
    expect(ratingTone(rating)).toBe(tone);
  });
});
