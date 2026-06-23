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

# Constants for selectors used in the tests below. These are kept here to avoid
# duplication and to make it easier to update if the site changes.
SEARCH_BOX = "input[name='search']:visible"
MANUFACTURER_TAB = "role=tab[name='Manufacturers']"
DYSON_TILE = 'a[href^="/en/manufacturer/dyson/"]'
DYSON_URL = (
    "https://source.thenbs.com/en/manufacturer/dyson/nakAxHWxDZprdqkBaCdn4U/overview"
)

# Global site-header elements (the "NBS Source" brand block, top-left).
# Scope to `header ... .brand-primary` so we hit the top-navbar instance and
# not the side-nav copy (which uses .brand-secondary).
BRAND_LINK = "header a.brand-primary"
NBS_LOGO = "header a.brand-primary mat-icon[svgicon='nbs:symbol']"
NBS_NAME = "header a.brand-primary app-name"
# The region/language picker. Its label reads "UK" locally but "US" on the
# US-based GitHub Actions runners, so we accept either.
LOCALE_LABEL = "header app-region-and-language-picker .mdc-button__label"
HOME_URL = "https://source.thenbs.com/en/"


@pytest.fixture
def dyson_page(page, base_url):
    """Navigate to the Dyson manufacturer overview page and hand back the
    Playwright `page`, ready for regression assertions.

    This is the pytest equivalent of a `beforeEach` hook: it performs the
    shared search-and-navigate journey so individual tests can start from the
    Dyson page instead of repeating the setup. The `expect(...).to_have_url`
    call doubles as a precondition guard — if we never land on the Dyson page,
    the fixture errors out and dependent tests are reported as errors (clearly
    a setup problem) rather than confusing assertion failures.

    Note: `test_search_returns_results` deliberately does NOT use this fixture —
    that search journey is the thing it's testing, so it stays inline.
    """
    page.goto(base_url)
    search = page.locator(SEARCH_BOX)
    search.click()
    search.fill("Dyson")
    search.press("Enter")
    page.locator(MANUFACTURER_TAB).click()
    # Target the link by its stable href slug, not the concatenated tile text.
    # `^=` matches "starts with", so the volatile GUID at the end is ignored.
    page.locator(DYSON_TILE).click()
    # expect(...) auto-retries, so it tolerates the client-side navigation.
    expect(page).to_have_url(DYSON_URL)
    return page


@pytest.mark.search
def test_search_returns_results(page, base_url):
    """Searching for 'Dyson' and opening the Manufacturers tab navigates to the
    Dyson manufacturer overview page."""
    page.goto(base_url)
    search = page.locator(SEARCH_BOX)
    search.click()
    search.fill("Dyson")
    search.press("Enter")
    page.locator(MANUFACTURER_TAB).click()
    # Target the link by its stable href slug, not the concatenated tile text.
    # `^=` matches "starts with", so the volatile GUID at the end is ignored.
    page.locator(DYSON_TILE).click()
    # Verify we landed on the Dyson manufacturer overview page.
    # expect(...) auto-retries, so it tolerates the client-side navigation.
    expect(page).to_have_url(DYSON_URL)


def test_category_navigation(dyson_page):
    """After navigating to the Dyson page, the global site header shows the NBS
    logo + 'NBS Source' brand (linking home) and the region/language picker."""
    page = dyson_page

    # --- Header brand block: logo, text, and home link ---
    expect(page.locator(NBS_LOGO)).to_be_visible()
    expect(page.locator(NBS_NAME)).to_be_visible()
    expect(page.locator(NBS_NAME)).to_have_text("NBS Source")

    brand = page.locator(BRAND_LINK)
    # The href ATTRIBUTE is the relative "/en/"; the browser RESOLVES it to the
    # absolute URL. Assert both: the literal attribute and the resolved value.
    expect(brand).to_have_attribute("href", "/en/")
    assert brand.evaluate("el => el.href") == HOME_URL

    # --- Region/language picker: "UK" locally, "US" on GitHub runners ---
    expect(page.locator(LOCALE_LABEL)).to_have_text(re.compile(r"\b(UK|US)\b"))
