import { describe, expect, test } from "vitest";
import { render, screen } from "@testing-library/react";
import AuditReportView from "../src/components/AuditReportView";
import type { AuditReport } from "../src/lib/api";

const report: AuditReport = {
  url: "https://acme.example",
  company_name: "Acme Corporation",
  overall_score: 73,
  executive_summary: "Acme has a solid foundation with clear quick wins.",
  seo: { score: 82, grade: "A", summary: "Strong metadata.", findings: ["Title is well optimized"] },
  performance: { score: 55, grade: "D", summary: "Slow on mobile.", findings: [] },
  technical: { score: 90, grade: "A", summary: "HTTPS and clean redirects.", findings: [] },
  content: { score: 68, grade: "C", summary: "Thin in places.", findings: [] },
  quick_wins: ["Add a meta description to the pricing page"],
  recommendations: [
    { title: "Compress hero images", impact: "High", effort: "Low", detail: "Serve WebP to cut LCP." },
  ],
  raw_data: {
    url: "https://acme.example",
    seo: {},
    performance: { mobile_vitals: { lcp: 4200 } },
    technical: { is_https: true, has_robots_txt: true, has_sitemap: false, status_code: 200, response_time_ms: 320 },
  },
};

describe("AuditReportView", () => {
  test("renders the headline, scores, recommendation, and quick win", () => {
    render(<AuditReportView report={report} />);
    expect(screen.getByText("Acme Corporation")).toBeInTheDocument();
    expect(screen.getByText("73")).toBeInTheDocument();
    expect(screen.getByText(/solid foundation/)).toBeInTheDocument();
    expect(screen.getByText("Grade D")).toBeInTheDocument();
    expect(screen.getByText("Compress hero images")).toBeInTheDocument();
    expect(screen.getByText("Impact: High")).toBeInTheDocument();
    expect(screen.getByText("Effort: Low")).toBeInTheDocument();
    expect(
      screen.getByText(/Add a meta description to the pricing page/),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /download pdf/i }),
    ).toBeInTheDocument();
  });

  test("links to the audited site", () => {
    render(<AuditReportView report={report} />);
    const link = screen.getByRole("link", { name: "acme.example" });
    expect(link).toHaveAttribute("href", "https://acme.example");
  });
});
