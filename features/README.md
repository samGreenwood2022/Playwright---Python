# features/ — BDD / Cucumber with pytest-bdd (Phase 4)

This folder will hold Gherkin `.feature` files (Given/When/Then scenarios) and
their Python step definitions (`test_*.py` with `@given`/`@when`/`@then`).

pytest-bdd runs these through pytest, so the steps reuse the same fixtures
(`page`, `base_url`) and Page Objects from earlier phases. We'll populate this
in Phase 4.
