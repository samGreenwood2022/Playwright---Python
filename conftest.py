"""
conftest.py — shared pytest configuration and fixtures.

This is pytest's equivalent of a global setup/hooks file. Any fixture defined
here is automatically available to every test in the project without importing.

pytest-playwright already gives us ready-made fixtures: `page`, `browser`,
`context`, etc. We add a couple of project-level conveniences on top.
"""

import pytest

# NOTE: there is deliberately NO `base_url` fixture here anymore.
# It now comes from the pytest-base-url plugin, configured by the
# `base_url = ...` line in pytest.ini. Tests still request it the same way —
# by naming a `base_url` parameter — pytest just resolves it from the plugin.


@pytest.fixture
def home_page(page, base_url):
    """
    Opens the NBS Source home page and hands back the Playwright `page`.

    In Phase 3 (Page Object Model) this fixture will instead return a
    `HomePage` object, e.g. `return HomePage(page).load()`.
    """
    page.goto(base_url)
    return page
