"""
conftest.py — shared pytest configuration and fixtures.

This is pytest's equivalent of a global setup/hooks file. Any fixture defined
here is automatically available to every test in the project without importing.

pytest-playwright already gives us ready-made fixtures: `page`, `browser`,
`context`, etc. We add a couple of project-level conveniences on top.
"""

import base64
from pathlib import Path

import pytest
from playwright.sync_api import Page
from pytest_playwright.pytest_playwright import _truncate_file_name
from slugify import slugify


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """On a test failure, embed a screenshot in the HTML report and link the
    Playwright trace (if tracing is configured to retain on failure).

    The `page` fixture is still alive during the 'call' phase report — its
    teardown (which is also where pytest-playwright writes the trace) runs
    afterwards — so we can grab a live screenshot here.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    pytest_html = item.config.pluginmanager.getplugin("html")
    if pytest_html is None:
        return
    extras = getattr(report, "extras", [])

    # 1. Live screenshot of the page at the moment of failure.
    page = item.funcargs.get("page")
    if page is not None:
        try:
            png = page.screenshot(full_page=True)
            extras.append(
                pytest_html.extras.image(
                    base64.b64encode(png).decode(), name="Screenshot on failure"
                )
            )
        except Exception:
            # A page that already crashed/closed shouldn't break reporting.
            pass

    # 2. Link to the trace.zip pytest-playwright will write during teardown.
    #    Path is rebuilt with the plugin's own helpers so it matches exactly.
    if item.config.getoption("--tracing") in ("on", "retain-on-failure"):
        output_dir = item.config.getoption("--output")
        slug = _truncate_file_name(slugify(item.nodeid))
        # Forward slashes so the href resolves in a browser on Windows and Linux.
        trace_rel = (Path(output_dir) / slug / "trace.zip").as_posix()
        extras.append(
            pytest_html.extras.url(trace_rel, name="Playwright trace (trace.zip)")
        )

    report.extras = extras


# NOTE: there is deliberately NO `base_url` fixture here anymore.
# It now comes from the pytest-base-url plugin, configured by the
# `base_url = ...` line in pytest.ini. Tests still request it the same way —
# by naming a `base_url` parameter — pytest just resolves it from the plugin.


@pytest.fixture
def home_page(page: Page, base_url: str) -> Page:
    """
    Opens the NBS Source home page and hands back the Playwright `page`.

    In Phase 3 (Page Object Model) this fixture will instead return a
    `HomePage` object, e.g. `return HomePage(page).load()`.
    """
    page.goto(base_url)
    return page
