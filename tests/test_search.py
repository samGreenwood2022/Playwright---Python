"""
Phase 2 — search and navigation tests against NBS Source.

Still 'flat' (no Page Objects yet). These exercise real user journeys:
typing a query and browsing by category.

Note on this site: NBS Source is an Angular app that updates the page title
*after* navigation, so we never assert on title immediately. We either wait on
the URL or use Playwright's auto-retrying `expect()`.
"""

import pytest
from playwright.sync_api import expect

SEARCH_BOX = "input[name='search']:visible"


@pytest.mark.search
def test_search_returns_results(page, base_url):
    """Searching for 'Dyson' and opening the Manufacturers tab navigates to the
    Dyson manufacturer overview page."""
    page.goto(base_url)

    search = page.locator(SEARCH_BOX)

    search.click()
    search.fill("Dyson")
    search.press("Enter")

    page.get_by_role("tab", name="Manufacturers").click()
    # Target the link by its stable href slug, not the concatenated tile text.
    # `^=` matches "starts with", so the volatile GUID at the end is ignored.
    page.locator('a[href^="/en/manufacturer/dyson/"]').click()

    # Verify we landed on the Dyson manufacturer overview page.
    # expect(...) auto-retries, so it tolerates the client-side navigation.
    expect(page).to_have_url(
        "https://source.thenbs.com/en/manufacturer/dyson/nakAxHWxDZprdqkBaCdn4U/overview"
    )


def test_category_navigation(page, base_url):
    """Browsing by category opens that category's listing page."""
    page.goto(base_url)

    # Categories live in a mega-menu that the "Browse" button reveals.
    page.get_by_role("button", name="Browse").click()
    page.get_by_role("link", name="Doors, windows and hatches").first.click()

    page.wait_for_url("**/category/doors-windows-and-hatches/**")
    assert "/category/" in page.url
