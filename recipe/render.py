"""HTML → PNG via Playwright (headless Chromium).

Used at generation time to produce the reference screenshot. The same render
parameters (viewport, full_page, deviceScaleFactor) MUST be used by the
verifier when rendering the agent's output, otherwise the grader is comparing
two different layouts of the same HTML.

Contract: caller has already written the HTML to `html_path` on disk. We
navigate to it via file://, screenshot, and return. We do not write the
HTML ourselves — that's the caller's responsibility (the pipeline already
needs the HTML on disk for the oracle solution; the verifier already has the
agent's output on disk).
"""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

from recipe.synthesise import VIEWPORT_HEIGHT, VIEWPORT_WIDTH

# Render constants. If you change these, change them in the verifier too.
DEVICE_SCALE_FACTOR = 1
NETWORK_IDLE_TIMEOUT_MS = 8000


def render_html_to_png(html_path: Path, png_path: Path) -> None:
    """Render the HTML at `html_path` to `png_path`, full-page, canonical viewport.

    Loads via file:// rather than set_content / data: URL — see PLAN.md
    discussion. file:// gives a clean URL in traces, predictable cross-origin
    behaviour for Google Fonts, and a normal load/networkidle lifecycle.
    """
    if not html_path.is_file():
        raise FileNotFoundError(f"HTML not found at {html_path}")

    png_path = png_path.resolve()
    png_path.parent.mkdir(parents=True, exist_ok=True)
    html_uri = html_path.resolve().as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context(
                viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
                device_scale_factor=DEVICE_SCALE_FACTOR,
            )
            page = context.new_page()
            page.goto(html_uri, wait_until="load")
            try:
                page.wait_for_load_state(
                    "networkidle", timeout=NETWORK_IDLE_TIMEOUT_MS
                )
            except Exception:
                # Some pages keep a slow connection alive (analytics-style).
                # Fall through; the load event already fired.
                pass
            page.screenshot(path=str(png_path), full_page=True)
        finally:
            browser.close()
