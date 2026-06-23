# pages/ — Page Object Model (Phase 3)

This folder will hold one class per page/component of NBS Source, e.g.
`home_page.py` (`HomePage`), `search_results_page.py` (`SearchResultsPage`).

Each Page Object wraps a Playwright `page`, exposes locators as properties and
user actions as methods, so tests read like plain English and locators live in
one place. We'll populate this in Phase 3 by refactoring the Phase 2 tests.
