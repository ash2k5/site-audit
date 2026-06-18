import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import CoreWebVitals from "../src/components/CoreWebVitals";
import type { PerformanceData } from "../src/lib/api";

const performance: PerformanceData = {
  mobile_score: 45,
  desktop_score: 88,
  mobile_vitals: {
    lcp: 3200,
    cls: 0.05,
    fcp: 1500,
    ttfb: 600,
    fid: 120,
    speed_index: 4000,
  },
  opportunities: [],
  diagnostics: [],
};

describe("CoreWebVitals", () => {
  test("renders PageSpeed scores and rated vitals", () => {
    render(<CoreWebVitals performance={performance} />);
    expect(screen.getByText("Mobile PageSpeed")).toBeInTheDocument();
    expect(screen.getByText("45")).toBeInTheDocument();
    expect(screen.getByText("LCP")).toBeInTheDocument();
    expect(screen.getByText("3.20s")).toBeInTheDocument();
    expect(screen.getByText("0.050")).toBeInTheDocument();
    expect(screen.getAllByText("Good").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Needs work").length).toBeGreaterThan(0);
  });

  test("falls back when PageSpeed data is missing", () => {
    render(
      <CoreWebVitals
        performance={{
          mobile_score: null,
          desktop_score: null,
          mobile_vitals: {},
          opportunities: [],
          diagnostics: [],
        }}
      />,
    );
    expect(
      screen.getByText(/PageSpeed data was unavailable/i),
    ).toBeInTheDocument();
  });
});
