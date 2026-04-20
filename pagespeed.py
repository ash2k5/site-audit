import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import requests

from models import CoreWebVitals, PerformanceData

PAGESPEED_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def get_pagespeed_data(url: str, api_key: Optional[str] = None) -> PerformanceData:
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(_fetch, url, strategy, api_key): strategy
            for strategy in ("mobile", "desktop")
        }
        results = {futures[f]: f.result() for f in as_completed(futures)}

    mobile = results.get("mobile")
    desktop = results.get("desktop")

    opportunities: list[str] = []
    diagnostics: list[str] = []

    if mobile:
        audits = mobile.get("lighthouseResult", {}).get("audits", {})
        for audit_id, audit in audits.items():
            if audit.get("score") is not None and audit["score"] < 0.9:
                title = audit.get("title", "")
                desc = audit.get("displayValue", "")
                if audit.get("details", {}).get("type") == "opportunity":
                    opportunities.append(f"{title}: {desc}".strip(": "))
                elif audit_id in (
                    "uses-long-cache-ttl", "unminified-css", "unminified-javascript",
                    "render-blocking-resources", "unused-css-rules",
                    "unused-javascript", "uses-optimized-images",
                    "uses-webp-images", "efficient-animated-content",
                ):
                    diagnostics.append(f"{title}: {desc}".strip(": "))

    return PerformanceData(
        mobile_score=_score(mobile),
        desktop_score=_score(desktop),
        mobile_vitals=_vitals(mobile),
        opportunities=opportunities[:6],
        diagnostics=diagnostics[:6],
    )


def _fetch(url: str, strategy: str, api_key: Optional[str]) -> Optional[dict]:
    params = {"url": url, "strategy": strategy}
    if api_key:
        params["key"] = api_key
    for attempt in range(3):
        try:
            resp = requests.get(PAGESPEED_API, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            if attempt == 2:
                print(f"  Warning: PageSpeed {strategy} failed — {e}")
                return None
            time.sleep(attempt + 1)
    return None


def _score(data: Optional[dict]) -> Optional[int]:
    if not data:
        return None
    score = (
        data.get("lighthouseResult", {})
        .get("categories", {})
        .get("performance", {})
        .get("score")
    )
    return int(score * 100) if score is not None else None


def _vitals(data: Optional[dict]) -> CoreWebVitals:
    if not data:
        return CoreWebVitals()

    audits = data.get("lighthouseResult", {}).get("audits", {})

    def num(audit_id: str) -> Optional[float]:
        val = audits.get(audit_id, {}).get("numericValue")
        return round(val, 3) if val is not None else None

    return CoreWebVitals(
        lcp=num("largest-contentful-paint"),
        cls=num("cumulative-layout-shift"),
        fid=num("max-potential-fid"),
        fcp=num("first-contentful-paint"),
        ttfb=num("server-response-time"),
        speed_index=num("speed-index"),
    )
