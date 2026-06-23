# NBS Source — Python Playwright Automation

UI test automation for the [NBS Source](https://source.thenbs.com) website,
built with **Python + Playwright + pytest**. BDD layer via **pytest-bdd**.

This is the Python counterpart to my TypeScript/JavaScript Playwright projects.

## Tech stack

| Purpose            | Tool                          |
| ------------------ | ----------------------------- |
| Language           | Python 3.12                   |
| Browser automation | Playwright                    |
| Test runner        | pytest + pytest-playwright    |
| BDD ("Cucumber")   | pytest-bdd                    |
| Reporting          | pytest-html                   |

## Project structure

```
.
├── tests/          # pytest test files (Phase 2)
├── pages/          # Page Object Model classes (Phase 3)
├── features/       # Gherkin .feature files + step defs (Phase 4)
├── conftest.py     # shared pytest fixtures (browser/page setup)
├── pytest.ini      # pytest + Playwright configuration
├── requirements.txt
└── .gitignore
```

## One-time setup

> Requires Python 3.10+ on your PATH (`python --version`).

```bash
# 1. Create an isolated virtual environment (≈ a project-local node_modules)
python -m venv .venv

# 2. Activate it
#    PowerShell:
.venv\Scripts\Activate.ps1
#    Git Bash:
source .venv/Scripts/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download the browser binaries Playwright drives
playwright install
```

## Running tests

```bash
pytest                       # run everything (uses pytest.ini defaults)
pytest -m smoke              # only tests marked @pytest.mark.smoke
pytest --headed              # watch the browser
pytest -k home_page          # tests whose name matches "home_page"
playwright codegen --target python-pytest https://source.thenbs.com # Print pytest-style Python to the Inspector window
```

An HTML report is written to `report.html` after each run.
