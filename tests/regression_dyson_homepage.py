"""
Phase 2 — search and navigation tests for the NBS Source website.

Written top-to-bottom (no Page Object pattern yet). NBS Source is an Angular app
that updates content without a full reload, so the tab title and URL change a
moment after navigation. We rely on `expect()`, which auto-retries, rather than
checking state immediately.
"""

import re

import pytest
from playwright.sync_api import Page, expect

# Reused selectors, defined once so a site change only needs updating here.
SEARCH_BOX = "input[name='search']:visible"
MANUFACTURER_TAB = "role=tab[name='Manufacturers']"
DYSON_TILE = 'a[href^="/en/manufacturer/dyson/"]'
DYSON_URL = (
    "https://source.thenbs.com/en/manufacturer/dyson/nakAxHWxDZprdqkBaCdn4U/overview"
)

# Top-bar branding. Branding also appears in the slide-out side menu, so anchor
# to `header ... .brand-primary` to match the top bar only (not .brand-secondary).
BRAND_LINK = "header a.brand-primary"
NBS_LOGO = "header a.brand-primary mat-icon[svgicon='nbs:symbol']"
NBS_NAME = "header a.brand-primary app-name"
# Region/language picker. Reads "UK" locally and "US" on GitHub's US servers.
LOCALE_LABEL = "header app-region-and-language-picker .mdc-button__label"
HOME_URL = "https://source.thenbs.com/en/"

# --- Main navigation header (the tab row on every page) -----------------------
# Anchored to the main nav by accessible name so we never match the side-menu copy.
MAIN_NAV = "nav[aria-label='Main navigation links']"
# Tab labels use `mdc-button__label`; dropdown items use `menu-panel-link`, so
# this matches exactly the seven top-level tabs (used for the order check).
NAV_TAB_LABELS = f"{MAIN_NAV} .mdc-button__label"

# Link tabs, mapping name -> (selector, expected href). Most have a stable
# `data-cy` test attribute; Home doesn't, so it's found by title="Homepage".
HEADER_LINKS = {
    "Home": (f"{MAIN_NAV} a[title='Homepage']", "/en/"),
    "What's new": (f"{MAIN_NAV} a[data-cy='whatsNewNavButton']", "/en/whats-new"),
    "Inspiration": (f"{MAIN_NAV} a[data-cy='inspirationNavButton']", "/en/inspiration"),
    "Collections": (f"{MAIN_NAV} a[data-cy='collectionsNavButton']", "/en/collections"),
    "CPD": (f"{MAIN_NAV} a[data-cy='cpdNavButton']", "/en/cpd"),
}

# Dropdown tabs (<button>, not <a>). Menus are tested elsewhere; here we only
# check the tab is visible.
HEADER_DROPDOWNS = {
    "Browse": f"{MAIN_NAV} button[title='Browse']",
    "BIM Library": f"{MAIN_NAV} button[title='BIM Library']",
}

# The complete list of tabs in the left-to-right order we expect to see them.
EXPECTED_TAB_ORDER = [
    "Home",
    "What's new",
    "Browse",
    "BIM Library",
    "Inspiration",
    "Collections",
    "CPD",
]


@pytest.fixture
def dyson_page(page: Page, base_url: str) -> Page:
    """Search for Dyson, open its manufacturer page, and return the `page` so
    tests can start from there. The final `to_have_url` is a setup guard: if we
    didn't reach the page, the failure is reported here rather than in the test.
    """
    page.goto(base_url)
    search = page.locator(SEARCH_BOX)
    search.click()
    search.fill("Dyson")
    search.press("Enter")
    page.locator(MANUFACTURER_TAB).click()
    # Match by href prefix (`^=`) so the random ID suffix doesn't matter; the
    # visible tile text is a brittle run-together string.
    page.locator(DYSON_TILE).click()
    expect(page).to_have_url(DYSON_URL)
    return page


# --- Regression tests for the Dyson manufacturer page -------------------------


def test_category_navigation(dyson_page: Page) -> None:
    """Global header shows the NBS logo + 'NBS Source' brand (linking home) and
    the region/language picker."""
    page = dyson_page

    expect(page.locator(NBS_LOGO)).to_be_visible()
    expect(page.locator(NBS_NAME)).to_be_visible()
    expect(page.locator(NBS_NAME)).to_have_text("NBS Source")

    brand = page.locator(BRAND_LINK)
    # Check both the relative href in the HTML and the browser-resolved full URL.
    expect(brand).to_have_attribute("href", "/en/")
    assert brand.evaluate("el => el.href") == HOME_URL

    # Locale reads "UK" locally / "US" on GitHub; \b matches whole words only.
    expect(page.locator(LOCALE_LABEL)).to_have_text(re.compile(r"\b(UK|US)\b"))


def test_common_header_elements(dyson_page: Page) -> None:
    """Main navigation shows every tab in the correct order, with link tabs
    pointing at the right hrefs and dropdown tabs visible by label."""
    page = dyson_page

    # Link tabs: visible and pointing at the right href. `message=` identifies
    # which tab failed, since the loop checks them all with the same lines.
    for name, (selector, href) in HEADER_LINKS.items():
        tab = page.locator(selector)
        expect(tab, message=f"'{name}' tab should be visible").to_be_visible()
        expect(tab, message=f"'{name}' tab should link to {href}").to_have_attribute(
            "href", href
        )

    # Dropdown tabs: visibility only (menus tested elsewhere).
    for name, selector in HEADER_DROPDOWNS.items():
        expect(
            page.locator(selector), message=f"'{name}' tab should be visible"
        ).to_be_visible()

    # Order: passing a list asserts both the count and the exact left-to-right
    # sequence (labels are trimmed before comparison).
    expect(page.locator(NAV_TAB_LABELS)).to_have_text(EXPECTED_TAB_ORDER)
