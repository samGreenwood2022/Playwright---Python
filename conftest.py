"""
conftest.py — shared pytest configuration and fixtures.

This is pytest's equivalent of a global setup/hooks file. Any fixture defined
here is automatically available to every test in the project without importing.

pytest-playwright already gives us ready-made fixtures: `page`, `browser`,
`context`, etc. We add a couple of project-level conveniences on top.
"""

import pytest

# Base URL for the site under test. Override with the BASE_URL env var if needed.
BASE_URL = "https://source.thenbs.com"


@pytest.fixture(scope="session")
def base_url() -> str:
    """The root URL of the application under test (NBS Source)."""
    return BASE_URL


@pytest.fixture
def home_page(page, base_url):
    """
    Opens the NBS Source home page and hands back the Playwright `page`.

    In Phase 3 (Page Object Model) this fixture will instead return a
    `HomePage` object, e.g. `return HomePage(page).load()`.
    """
    page.goto(base_url)
    return page
