"""
Phase 2 — tests for searching and navigating the NBS Source website.

These tests act like a real person using the site: they type a search term and
then click around to browse. The test code is written in a simple, top-to-bottom
style (we haven't introduced the "Page Object" pattern yet, which is a way of
tidying tests once they grow).

One thing to know about this website: NBS Source is built with Angular, which
loads new content without a full page reload. Because of this, the browser tab's
title only updates a moment *after* you navigate. So instead of checking the
title straight away (which could be the old one), we either wait for the URL to
change or use Playwright's `expect()`, which automatically retries for a short
while until the page catches up.
"""

import re

import pytest
from playwright.sync_api import Page, expect

# A "selector" is a piece of text that tells Playwright how to find an element on
# the page (like a button or text box). We store the ones we reuse here as named
# constants. That way each selector is written once, and if the website changes
# we only have to update it in this one place.
SEARCH_BOX = "input[name='search']:visible"
MANUFACTURER_TAB = "role=tab[name='Manufacturers']"
DYSON_TILE = 'a[href^="/en/manufacturer/dyson/"]'
DYSON_URL = (
    "https://source.thenbs.com/en/manufacturer/dyson/nakAxHWxDZprdqkBaCdn4U/overview"
)

# Elements in the site header at the very top of every page: the "NBS Source"
# logo and brand name in the top-left corner.
# The site actually has this branding in two places (the top bar and a slide-out
# side menu). We start each selector with `header ... .brand-primary` so we only
# match the copy in the top bar, never the side-menu copy (which uses a different
# class, .brand-secondary).
BRAND_LINK = "header a.brand-primary"
NBS_LOGO = "header a.brand-primary mat-icon[svgicon='nbs:symbol']"
NBS_NAME = "header a.brand-primary app-name"
# The region/language picker button. The text on it shows "UK" when we run the
# tests on our own machines, but "US" when they run on GitHub's servers (which
# are based in the US). We accept either so the test passes in both places.
LOCALE_LABEL = "header app-region-and-language-picker .mdc-button__label"
HOME_URL = "https://source.thenbs.com/en/"

# --- Main navigation header (the row of tabs shown on every page) -------------
# We anchor every selector below to this main nav using its accessible name
# ("Main navigation links"). As with the logo above, the same links also appear
# in the slide-out side menu, so anchoring here makes sure we only ever match the
# tabs in the main top row.
MAIN_NAV = "nav[aria-label='Main navigation links']"
# The visible text of each tab sits inside an element with the class
# `mdc-button__label`. The items inside the dropdown menus use a different class
# (`menu-panel-link`), so this selector matches exactly the seven top-level tabs
# and nothing else — which is what we want for the "are they in order?" check.
NAV_TAB_LABELS = f"{MAIN_NAV} .mdc-button__label"

# These tabs are simple links, so for each one we check it points to the right
# web address (its "href"). The dictionary maps the tab's visible name to a pair:
# (the selector that finds it, the href we expect it to have).
# Most tabs have a stable `data-cy` attribute that's added specifically for
# testing; the Home tab doesn't, so we find it by its title="Homepage" instead.
HEADER_LINKS = {
    "Home": (f"{MAIN_NAV} a[title='Homepage']", "/en/"),
    "What's new": (f"{MAIN_NAV} a[data-cy='whatsNewNavButton']", "/en/whats-new"),
    "Inspiration": (f"{MAIN_NAV} a[data-cy='inspirationNavButton']", "/en/inspiration"),
    "Collections": (f"{MAIN_NAV} a[data-cy='collectionsNavButton']", "/en/collections"),
    "CPD": (f"{MAIN_NAV} a[data-cy='cpdNavButton']", "/en/cpd"),
}

# These tabs open dropdown menus when clicked (the menus themselves are tested
# elsewhere), so here we only check that the tab is visible. Note they are
# <button> elements rather than <a> links, which is why they aren't in the
# HEADER_LINKS dictionary above.
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
    """Go to the Dyson manufacturer page and return Playwright's `page` object so
    a test can start its checks from there.

    A pytest "fixture" is reusable setup code. This one does the search-and-click
    journey to reach the Dyson page once, so each test that needs that starting
    point can simply ask for it (by listing `dyson_page` as an argument) instead
    of repeating these same steps. If you've used other test frameworks, this is
    the same idea as a `beforeEach` hook.

    The `expect(...).to_have_url` line at the end is a safety check: it confirms
    we actually arrived on the Dyson page. If we didn't, the fixture fails here,
    and pytest clearly reports it as a *setup* problem rather than letting the
    real test fail later for a confusing reason.

    Note: the search test (`test_search_returns_results`) does NOT use this
    fixture, because searching is the very thing it's testing — so it does those
    steps itself rather than borrowing them from here.
    """
    page.goto(base_url)
    search = page.locator(SEARCH_BOX)
    search.click()
    search.fill("Dyson")
    search.press("Enter")
    page.locator(MANUFACTURER_TAB).click()
    # Find the Dyson link by the start of its web address rather than by its text
    # (the visible tile text is a long run-together string that's easy to get
    # wrong). The `^=` in the selector means "href starts with this", so the
    # random ID on the end of the real URL doesn't matter and won't break this.
    page.locator(DYSON_TILE).click()
    # Because Angular changes the page without a full reload, the URL updates a
    # moment after the click. `expect()` keeps re-checking for a short time, so it
    # waits for that to happen instead of failing instantly.
    expect(page).to_have_url(DYSON_URL)
    return page


#### Regression tests for the Dyson manufacturer page --------------------------------


### Regression tests for the global site logo and locale (the top navbar)
def test_category_navigation(dyson_page: Page) -> None:
    """After navigating to the Dyson page, the global site header shows the NBS
    logo + 'NBS Source' brand (linking home) and the region/language picker."""
    page = dyson_page

    # --- Header brand block: check the logo, the name text, and the home link ---
    expect(page.locator(NBS_LOGO)).to_be_visible()
    expect(page.locator(NBS_NAME)).to_be_visible()
    expect(page.locator(NBS_NAME)).to_have_text("NBS Source")

    brand = page.locator(BRAND_LINK)
    # A link's href can be written two ways. In the HTML it's stored as the short,
    # relative form "/en/". The browser then expands that into the full address,
    # "https://source.thenbs.com/en/". We check both: first the value written in
    # the HTML, then the full address the browser works out (read here by asking
    # the browser for the element's resolved `.href` property).
    expect(brand).to_have_attribute("href", "/en/")
    assert brand.evaluate("el => el.href") == HOME_URL

    # --- Region/language picker: shows "UK" on our machines, "US" on GitHub ---
    # re.compile builds a pattern that allows either word. The `\b` parts mean
    # "word boundary", so we match the whole words UK or US (and not, say, a "US"
    # that happened to be part of a longer word).
    expect(page.locator(LOCALE_LABEL)).to_have_text(re.compile(r"\b(UK|US)\b"))


### Regression tests for the site-wide main navigation header (the tab strip)
def test_common_header_elements(dyson_page: Page) -> None:
    """The site-wide main navigation shows every tab, in the correct order, with
    the link tabs pointing at the right hrefs.

    Three checks:
      1. Link tabs (Home, What's new, Inspiration, Collections, CPD) are visible
         AND carry the expected href.
      2. Dropdown tabs (Browse, BIM Library) are visible by label only — their
         menus open on hover/click and are covered in a separate test.
      3. All seven tabs appear in the expected left-to-right order.
    """
    page = dyson_page

    # --- 1. Link tabs: each one is visible and points to the correct address ---
    # The `message=` text is shown if a check fails. Because we're inside a loop,
    # every tab is checked by the same lines of code, so without this message a
    # failure report couldn't tell you *which* tab was the problem.
    for name, (selector, href) in HEADER_LINKS.items():
        tab = page.locator(selector)
        expect(tab, message=f"'{name}' tab should be visible").to_be_visible()
        expect(tab, message=f"'{name}' tab should link to {href}").to_have_attribute(
            "href", href
        )

    # --- 2. Dropdown tabs: just check the tab is visible (menus tested elsewhere) ---
    for name, selector in HEADER_DROPDOWNS.items():
        expect(
            page.locator(selector), message=f"'{name}' tab should be visible"
        ).to_be_visible()

    # --- 3. Order: the tabs appear left-to-right in the expected sequence ---
    # NAV_TAB_LABELS matches all seven tab labels at once. When we hand `expect()`
    # a list, it checks two things together: that there are exactly that many tabs,
    # and that their text matches in that exact order. `expect()` also trims any
    # stray spaces around each label first (so " Home " is treated as "Home").
    expect(page.locator(NAV_TAB_LABELS)).to_have_text(EXPECTED_TAB_ORDER)
