import asyncio
import base64
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template

from models import AuditReport

TEMPLATE_DIR = Path(__file__).parent / "templates"


def _score_color(score: int) -> str:
    if score >= 80:
        return "#22c55e"
    if score >= 60:
        return "#f59e0b"
    if score >= 40:
        return "#f97316"
    return "#ef4444"


def _grade_color(grade: str) -> str:
    return {"A": "#22c55e", "B": "#84cc16", "C": "#f59e0b", "D": "#f97316", "F": "#ef4444"}.get(grade, "#6b7280")


def _level_color(level: str) -> str:
    return {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"}.get(level, "#6b7280")


def generate_pdf(report: AuditReport, output_path: str, skip_screenshot: bool = False) -> None:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    env.filters["score_color"] = _score_color
    env.filters["grade_color"] = _grade_color
    env.filters["level_color"] = _level_color
    template = env.get_template("report.html")

    asyncio.run(_capture_and_render(report, template, output_path, skip_screenshot))
    print(f"  PDF written: {output_path}")


async def _capture_and_render(
    report: AuditReport,
    template: Template,
    output_path: str,
    skip_screenshot: bool,
) -> None:
    from playwright.async_api import async_playwright

    perf = report.raw_data.performance if report.raw_data else None
    mv = perf.mobile_vitals if perf else None

    async with async_playwright() as p:
        browser = await p.chromium.launch()

        screenshot_b64 = ""
        if not skip_screenshot:
            page = await browser.new_page(viewport={"width": 1280, "height": 800})
            try:
                await page.goto(report.url, timeout=30000, wait_until="networkidle")
                data = await page.screenshot(full_page=False)
                screenshot_b64 = base64.b64encode(data).decode()
            except Exception as e:
                print(f"  Warning: screenshot failed — {e}")
            finally:
                await page.close()

        html_content = template.render(
            report=report,
            perf=perf,
            mv=mv,
            screenshot_b64=screenshot_b64,
        )

        page = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle")
        await page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        await browser.close()
