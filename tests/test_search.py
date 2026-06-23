"""
Phase 2 — search and navigation tests against NBS Source.

Still 'flat' (no Page Objects yet). These exercise real user journeys:
typing a query and browsing by category.

Note on this site: NBS Source is an Angular app that updates the page title
*after* navigation, so we never assert on title immediately. We either wait on
the URL or use Playwright's auto-retrying `expect()`.
"""

import re

import pytest
from playwright.sync_api import expect

SEARCH_BOX = "input[name='search']:visible"


@pytest.mark.search
def test_search_returns_results(page, base_url):
    """Searching for a product term lands on a results page with products."""
    page.goto(base_url)

    search = page.locator(SEARCH_BOX)
    search.fill("insulation")
    search.press("Enter")

    # The app navigates client-side; wait for the URL to settle on the result.
    page.wait_for_url("**/insulation/**")

    # Product entries on NBS Source render as <article> elements.
    expect(page.locator("article").first).to_be_visible()
    assert page.locator("article").count() > 0

    # `expect` auto-retries, so it tolerates the async title update.
    expect(page).to_have_title(re.compile("Insulation"))


def test_category_navigation(page, base_url):
    """Browsing by category opens that category's listing page."""
    page.goto(base_url)

    # Categories live in a mega-menu that the "Browse" button reveals.
    page.get_by_role("button", name="Browse").click()
    page.get_by_role("link", name="Doors, windows and hatches").first.click()

    page.wait_for_url("**/category/doors-windows-and-hatches/**")
    assert "/category/" in page.url
