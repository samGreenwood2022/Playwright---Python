"""
Phase 2 — basic smoke tests against the NBS Source website.

These are deliberately written 'flat' (locators inline, no abstraction) so the
pattern is easy to read. In Phase 3 we'll refactor them onto Page Objects.

Run all tests:      pytest
Run only smoke:     pytest -m smoke
Run a single test:  pytest tests/test_smoke.py::test_home_page_loads
"""

import pytest
from playwright.sync_api import Page

# NBS Source is an Angular Material app. Its search box is a Material text input
# (role "textbox", NOT "searchbox") rendered twice for responsive layouts, so we
# target the single *visible* one with Playwright's ":visible" pseudo-class.
SEARCH_BOX = "input[name='search']:visible"


@pytest.mark.smoke
def test_home_page_loads(page: Page, base_url: str) -> None:
    """The NBS Source home page loads and has the expected title."""
    page.goto(base_url)
    assert "NBS Source" in page.title()


@pytest.mark.smoke
def test_search_box_is_visible(home_page: Page) -> None:
    """A single, visible search box is present on the home page."""
    search = home_page.locator(SEARCH_BOX)
    assert search.count() == 1
    assert search.is_visible()
    assert search.get_attribute("placeholder") == "Search NBS Source..."
