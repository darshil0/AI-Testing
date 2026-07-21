# Developer Release & QA Playbook

This document serves as the official QA, verification, and release playbook for developers and maintainers of the **AI-Testing** evaluation framework. Follow these procedures before merging major changes, tagging releases, or publishing new versions.

---

## 🛡️ Pre-Release Automated Quality Gates

Before any release is signed off, all automated quality gates must pass successfully in a clean virtual environment.

### 1. Recreate a Clean Environment
Verify that the package installs flawlessly without duplicate package warnings or installation conflicts:
```bash
# Deactivate and remove any existing virtual environments
deactivate 2>/dev/null || true
rm -rf venv/

# Create a fresh virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install package with development dependencies in editable mode
pip install -e ".[dev]"
```

### 2. Run the Full Pytest Suite
All unit and integration tests must pass with zero failures:
```bash
python -m pytest
```

### 3. Verify Code Style and Linting
The codebase must comply with the Flake8 configuration (defined in `.flake8`):
```bash
# Check code style
flake8 .

# Apply automatic formatting if needed
black .
```

---

## 💻 Manual Verification Protocol

In addition to automated tests, perform these manual end-to-end checks to guarantee that CLI operations, model interfaces, data parsing, and user dashboard render flawlessly.

### Check 1: Evaluator Run via Installed CLI
Run the standard evaluation command using the simulated provider to verify package entrypoints and terminal Rich displays:
```bash
run-evaluation --models simulated:default
```
* **Expected Outcome**:
  - A real-time Rich progress bar is displayed during the run.
  - A beautiful terminal summary table displays overall statistics (Average Score, Duration, Cost, PII Warnings).
  - The results are successfully exported to a timestamped JSON file inside the `ai_evaluation/results/` directory.

### Check 2: Evaluator Run via Module Invocation
Verify that direct package execution works correctly (essential for container environments):
```bash
python -m ai_evaluation --models simulated:default
```
* **Expected Outcome**: Exactly matches the behavior of the `run-evaluation` CLI.

### Check 3: Check Consolidated Result Exports
Verify that consolidated CSV and JSON formats are correctly generated:
```bash
# Run with CSV output consolidation
run-evaluation --models simulated:default --export-format csv

# Run with JSON output consolidation
run-evaluation --models simulated:default --export-format json
```
* **Expected Outcome**: File exports successfully and reports the output path in the final console logs.

### Check 4: Launching the Streamlit Dashboard
Verify that the dashboard launches correctly and handles results dynamically:
```bash
view-dashboard
```
* **Expected Outcome**:
  - The browser window opens to the Streamlit local server.
  - The user can select runs, compare model performance, select different evaluated models, and inspect responses.
  - No fatal `json.JSONDecodeError` or `KeyError` warnings are raised if empty or partially written runs are present.

---

## 📦 Version and Packaging Validation

Before cutting a release, make sure that package configuration files are synchronized and correct.

### 1. Version Number Check
Ensure that the exact semantic version number (e.g., `2.1.6`) matches across all of the following files:
- [ ] `pyproject.toml` (`version = "X.Y.Z"`)
- [ ] `ai_evaluation/__init__.py` (`__version__ = "X.Y.Z"`)
- [ ] `tests/__init__.py` (`__version__ = "X.Y.Z"`)
- [ ] Banners, logs, or help instructions inside `ai_evaluation/run_evaluation.py` and `ai_evaluation/dashboard.py`

### 2. Dependencies Drift Check
Ensure that all required dependencies are maintained within `pyproject.toml`'s dependencies section. We do **not** use a separate standalone `requirements.txt` to prevent dependency drift.

---

## 🏷️ Release Tagging & Publishing Checklist

When all automated and manual verification steps pass, follow this release process:

- [ ] **Step 1**: Commit any final version or documentation updates.
- [ ] **Step 2**: Create a descriptive section in `CHANGELOG.md` adhering to Keep a Changelog standards.
- [ ] **Step 3**: Tag the commit with the semantic version prefix:
  ```bash
  git tag -a v2.1.6 -m "Release Version 2.1.6"
  ```
- [ ] **Step 4**: Push changes and tags to the main remote branch:
  ```bash
  git push origin main
  git push origin v2.1.6
  ```
- [ ] **Step 5**: Create a draft release on GitHub, copying the relevant version changelog section. Publish the release!
