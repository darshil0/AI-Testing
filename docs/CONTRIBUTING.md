This **Contributing Guide** is comprehensive and sets exactly the right tone for an open-source project. I have polished the document to remove hidden formatting issues (like non-breaking spaces in bash scripts) and enhanced the technical sections to reflect the **v2.1.0** architectural standards.

---

# Contributing to AI-Testing

Thank you for your interest in contributing! This document provides guidelines to help you through the process of improving this framework.

## Table of Contents

* [Code of Conduct](https://www.google.com/search?q=%23code-of-conduct)
* [Development Setup](https://www.google.com/search?q=%23development-setup)
* [Making Changes](https://www.google.com/search?q=%23making-changes)
* [Coding Standards](https://www.google.com/search?q=%23coding-standards)
* [Testing](https://www.google.com/search?q=%23testing)
* [Submitting Changes](https://www.google.com/search?q=%23submitting-changes)

---

## Code of Conduct

By participating, you agree to maintain a respectful and inclusive environment. We value **Respect**, **Collaboration**, **Quality**, and **Openness**.

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/AI-Testing.git
cd AI-Testing

# Add upstream remote to stay synced
git remote add upstream https://github.com/darshil0/AI-Testing.git

```

### 2. Environment Setup

We use an editable installation to ensure changes are reflected immediately.

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install the project in editable mode with dev dependencies
pip install -e .
pip install pytest pytest-cov black flake8 mypy

```

### 3. Verify Setup

```bash
# Run tests to ensure baseline stability
pytest

# Run a sample evaluation using the simulated model
run-evaluation --models simulated:default

```

---

## Making Changes

### 1. Branching

```bash
# Sync with upstream
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name

```

* `feature/` - New features
* `fix/` - Bug fixes
* `docs/` - Documentation changes

### 2. Testing Your Changes

```bash
# Run with coverage report
pytest --cov=ai_evaluation

# Format code before committing
black ai_evaluation/

```

---

## Coding Standards

### Python Style

We follow **PEP 8** and use **Black** for formatting.

* **Line Length**: 88 characters.
* **Docstrings**: Google-style docstrings are required for all public methods.

### Commit Messages

We follow conventional commits:

* `feat:` New feature for the user.
* `fix:` Bug fix for the user.
* `docs:` Changes to the documentation.
* `test:` Adding missing tests or correcting existing tests.

---

## Testing

### Writing Tests

Tests are located in `tests/`. We prioritize unit tests that mock external API calls to keep the suite fast and cost-effective.

```python
def test_pii_scanner():
    """Example test for PII detection."""
    from ai_evaluation.run_evaluation import AIEvaluator
    evaluator = AIEvaluator()
    found, types = evaluator._pii_scan("My email is test@example.com")
    assert found is True
    assert "email" in types

```

---

## Submitting Changes

### 1. Pull Request Process

1. Push your branch: `git push origin feature/your-feature-name`
2. Open a Pull Request (PR) against the `main` branch.
3. Ensure the **CI/CD pipeline** (GitHub Actions) passes.
4. Address any feedback from maintainers.

---

## Adding New Features

### Adding a New Model Provider

1. **Inherit**: Create a new class in `ai_evaluation/models.py` inheriting from `BaseModel`.
2. **Factory**: Register your provider in the `get_model()` function.
3. **Pricing**: Update `ai_evaluation/config.yaml` with the model's cost per 1M tokens.

---

## License

By contributing, you agree that your contributions will be licensed under the project's **MIT License**.
