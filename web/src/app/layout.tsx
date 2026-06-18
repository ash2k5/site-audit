import type { CSSProperties, ReactNode } from "react";
import type { Metadata } from "next";
import { Bodoni_Moda, Inter } from "next/font/google";
import { AuroraBackground } from "@ash2k5/ui";
import SiteHeader from "../components/SiteHeader";
import "./globals.css";

const bodoni = Bodoni_Moda({
  subsets: ["latin"],
  display: "swap",
  weight: ["400", "500", "600", "700"],
});
const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: {
    default: "Site Audit — score any website",
    template: "%s · Site Audit",
  },
  description:
    "Audit any URL: SEO, performance, technical health, and content scored and turned into a prioritized action plan and a print-ready PDF.",
};

// No-flash theme init: set data-theme before paint from storage or system pref.
const themeInit = `(function(){try{var t=localStorage.getItem("ds-theme")||(window.matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light");document.documentElement.setAttribute("data-theme",t);}catch(e){}})();`;

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html
      lang="en"
      data-theme="light"
      suppressHydrationWarning
      style={
        {
          "--font-display": `${bodoni.style.fontFamily}, Georgia, serif`,
          "--font-body": `${inter.style.fontFamily}, system-ui, sans-serif`,
          "--font-label": `${inter.style.fontFamily}, system-ui, sans-serif`,
        } as CSSProperties
      }
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInit }} />
      </head>
      <body
        className="ds-root flex min-h-screen flex-col antialiased"
        suppressHydrationWarning
      >
        <AuroraBackground />
        <SiteHeader />
        <main className="flex-1">{children}</main>
        <footer className="border-t border-outline-variant">
          <div className="ds-container flex flex-col gap-1 py-8 ds-body-sm text-on-surface-variant">
            <span>
              Site Audit — SEO, performance, technical, and content, scored by an
              LLM.
            </span>
            <span className="ds-label-sm">
              Metrics: Google PageSpeed Insights. Analysis: Groq (Llama 3.3).
            </span>
          </div>
        </footer>
      </body>
    </html>
  );
}
