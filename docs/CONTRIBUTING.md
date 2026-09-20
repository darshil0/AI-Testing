# Contributing to AI-Testing

Thank you for your interest in contributing! This document provides guidelines to help you navigate the process of improving and extending this framework.

---

## Table of Contents

* [Code of Conduct](#code-of-conduct)
* [Development Setup](#development-setup)
* [Making Changes](#making-changes)
* [Coding Standards](#coding-standards)
* [Testing](#testing)
* [Submitting Changes](#submitting-changes)
* [Adding New Features](#adding-new-features)
* [License](#license)

---

## Code of Conduct

By participating in this project, you agree to maintain a respectful, inclusive, and collaborative environment. We value **Respect**, **Collaboration**, **Quality**, and **Openness**.

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork on GitHub, then clone your repository
git clone [https://github.com/YOUR_USERNAME/AI-Testing.git](https://github.com/YOUR_USERNAME/AI-Testing.git)
cd AI-Testing

# Add upstream remote to stay synchronized
git remote add upstream [https://github.com/darshil0/AI-Testing.git](https://github.com/darshil0/AI-Testing.git)

```

### 2. Environment Setup

Use an editable installation so local changes take effect immediately across the environment:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the project and development dependencies in editable mode
pip install -e ".[dev]"

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

### 1. Branching Strategy

Maintain a clean Git timeline by creating dedicated branches off `main`:

```bash
# Sync local main with upstream
git checkout main
git pull upstream main

# Create a topic branch
git checkout -b feature/your-feature-name

```

Use standard branch naming prefixes:

* `feature/` — New features or enhancements
* `fix/` — Bug fixes
* `docs/` — Documentation updates

### 2. Testing Your Changes

```bash
# Run tests with a test coverage report
pytest --cov=ai_evaluation

# Format code before committing
black .

# Run style checks
flake8 .

```

---

## Coding Standards

### Python Style

We follow **PEP 8** standards and enforce formatting with **Black**:

* **Line Length**: Maximum 88 characters.
* **Docstrings**: Google-style docstrings are required for all public classes, functions, and methods.
* **Type Hints**: Type annotations are encouraged for public signatures.

### Commit Messages

Use standard conventional commit prefixes:

* `feat:` New feature for the framework
* `fix:` Bug fix
* `docs:` Documentation updates
* `test:` Adding or updating tests
* `refactor:` Code refactoring without behavioral changes

---

## Testing

### Writing Tests

All test files are located in the `tests/` directory. Unit tests should mock external API endpoints (e.g., OpenAI, Anthropic, Gemini) to prevent unnecessary billing and ensure fast, deterministic CI execution.

```python
def test_pii_scanner():
    """Example test for PII detection logic."""
    from ai_evaluation.run_evaluation import AIEvaluator

    evaluator = AIEvaluator()
    found, pii_types = evaluator._pii_scan("My email is test@example.com")
    
    assert found is True
    assert "email" in pii_types

```

---

## Submitting Changes

### Pull Request Process

1. Push your branch to your fork:
```bash
git push origin feature/your-feature-name

```


2. Open a Pull Request (PR) against the `main` branch of `darshil0/AI-Testing`.
3. Verify that all **GitHub Actions CI/CD workflows** complete successfully.
4. Respond promptly to code review feedback from project maintainers.

---

## Adding New Features

### Adding a New Model Provider

1. **Inherit**: Create a new class in `ai_evaluation/models.py` inheriting from `BaseModel`.
2. **Factory**: Register your provider in the `get_model()` factory function.
3. **Pricing**: Update `ai_evaluation/config.yaml` with the provider's token pricing configuration.

---

## License

By contributing, you agree that your contributions will be licensed under the project's **MIT License**.
