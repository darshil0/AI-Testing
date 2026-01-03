# Contributing to AI-Testing

Thank you for your interest in contributing to AI-Testing! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Adding New Features](#adding-new-features)
- [Documentation](#documentation)
- [Questions and Support](#questions-and-support)

---

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. We value:

- **Respect**: Treat all contributors with respect
- **Collaboration**: Work together constructively
- **Quality**: Strive for excellence in all contributions
- **Openness**: Be transparent about your work and intentions

---

## Getting Started

### Before You Start

1. **Check existing issues**: Browse [GitHub Issues](https://github.com/darshil0/AI-Testing/issues) to see if your idea or bug is already being discussed
2. **Open an issue first**: For major changes, open an issue to discuss your proposal before writing code
3. **Read the documentation**: Familiarize yourself with the project structure and existing code

### Finding Something to Work On

- Look for issues labeled `good first issue` for beginner-friendly tasks
- Check `help wanted` labels for areas where we need assistance
- Browse the [roadmap](https://github.com/darshil0/AI-Testing/issues) for planned features

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/AI-Testing.git
cd AI-Testing

# Add upstream remote
git remote add upstream https://github.com/darshil0/AI-Testing.git
```

### 2. Create Virtual Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Add your API keys for testing (optional)
nano .env
```

### 4. Verify Setup

```bash
# Run tests to ensure everything works
pytest

# Run a sample evaluation
python ai_evaluation/run_evaluation.py --models simulated:default
```

---

## Making Changes

### 1. Create a Branch

```bash
# Sync with upstream
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications

### 2. Make Your Changes

- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_evaluation

# Run specific test file
pytest tests/test_run_evaluation.py -v

# Test your changes manually
python ai_evaluation/run_evaluation.py --models simulated:default
```

---

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

```bash
# Format code with black (line length: 88)
black ai_evaluation/

# Check with flake8
flake8 ai_evaluation/

# Type checking (optional but encouraged)
mypy ai_evaluation/
```

### Code Quality Checklist

- [ ] Code is formatted with `black`
- [ ] No `flake8` warnings
- [ ] All tests pass
- [ ] New code has tests
- [ ] Documentation is updated
- [ ] Commit messages are clear

### Writing Good Commit Messages

```
# Good commit message format:
Type: Brief description (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain the problem this commit solves and why this approach.

Fixes #123
```

Types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance tasks

Examples:
```bash
git commit -m "feat: Add support for Cohere API"
git commit -m "fix: Handle missing config file gracefully"
git commit -m "docs: Update Quick Reference with new examples"
```

---

## Testing

### Writing Tests

Tests are located in `tests/` directory. We use `pytest`.

```python
# Example test structure
import pytest
from ai_evaluation.run_evaluation import AIEvaluator

def test_evaluator_initialization(mock_config):
    """Test that AIEvaluator initializes correctly."""
    evaluator = AIEvaluator(config_path="test_config.yaml")
    assert evaluator is not None
    assert evaluator.config is not None

def test_pii_scanner():
    """Test PII detection."""
    evaluator = AIEvaluator()
    text = "Contact me at john@example.com"
    found, types = evaluator._pii_scan(text)
    assert found == True
    assert "email" in types
```

### Test Coverage

We aim for >80% code coverage. Check coverage with:

```bash
# Generate coverage report
pytest --cov=ai_evaluation --cov-report=html

# View report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Running Specific Tests

```bash
# Run single test file
pytest tests/test_run_evaluation.py

# Run specific test
pytest tests/test_run_evaluation.py::test_evaluator_initialization

# Run with verbose output
pytest -v

# Run with print statements
pytest -s
```

---

## Submitting Changes

### 1. Push to Your Fork

```bash
# Make sure all tests pass
pytest

# Format code
black .
flake8 .

# Commit your changes
git add .
git commit -m "feat: Add your feature description"

# Push to your fork
git push origin feature/your-feature-name
```

### 2. Create Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select your feature branch
4. Fill out the PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] All tests pass
- [ ] Added new tests for changes
- [ ] Manually tested changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### 3. Review Process

- Maintainers will review your PR
- Address any requested changes
- Once approved, your PR will be merged

### Keeping Your PR Updated

```bash
# Sync with upstream main
git checkout main
git pull upstream main

# Rebase your feature branch
git checkout feature/your-feature-name
git rebase main

# Force push if needed
git push origin feature/your-feature-name --force
```

---

## Adding New Features

### Adding a New Model Provider

1. **Create Model Class** in `ai_evaluation/models.py`:

```python
class NewProviderModel(BaseModel):
    def __init__(self, model_name: str, config: Dict[str, Any]):
        super().__init__(model_name, config)
        # Initialize API client
        self.client = NewProviderClient(api_key=os.getenv("NEWPROVIDER_API_KEY"))
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def call(self, prompt: str) -> Tuple[str, int, int]:
        resp = self.client.generate(
            model=self.model_name,
            prompt=prompt,
            max_tokens=self.config.get("max_tokens", 2000)
        )
        return resp.text, resp.input_tokens, resp.output_tokens
```

2. **Register in Factory** in `get_model()`:

```python
def get_model(model_identifier: str, config: Dict[str, Any]) -> BaseModel:
    provider, model_name = model_identifier.split(":", 1)
    
    if provider == "newprovider":
        return NewProviderModel(model_name, config)
    # ... existing providers
```

3. **Add Pricing** to `config.yaml`:

```yaml
pricing:
  "newprovider-model": { "input": 5.0, "output": 15.0 }
```

4. **Update Documentation**:
   - Add to README.md model support section
   - Add example usage
   - Update CHANGELOG.md

5. **Add Tests**:

```python
def test_newprovider_model(mocker):
    mock_client = mocker.Mock()
    mocker.patch("newprovider.Client", return_value=mock_client)
    
    model = NewProviderModel("model-name", config)
    response, inp, out = model.call("test prompt")
    
    assert response is not None
    mock_client.generate.assert_called_once()
```

### Adding a New Test Category

1. Create test case file in `ai_evaluation/test_cases/`
2. Use appropriate category name
3. Add to documentation
4. Consider adding category-specific evaluation criteria

---

## Documentation

### Documentation Standards

- Keep README.md updated with new features
- Update CHANGELOG.md for all changes
- Add docstrings to all functions and classes
- Include examples for new features

### Docstring Format

We use Google-style docstrings:

```python
def process_one(self, file_path: Path, model_id: str, persona: str = "default") -> EvaluationResult:
    """Process a single test case with a given model.
    
    Args:
        file_path: Path to the test case file
        model_id: Model identifier in format 'provider:model_name'
        persona: Judge persona to use for evaluation
        
    Returns:
        EvaluationResult object containing all metrics
        
    Raises:
        FileNotFoundError: If test case file doesn't exist
        ValueError: If model_id format is invalid
    """
```

### Documentation Files to Update

When adding features, update:
- `README.md` - Main documentation
- `CHANGELOG.md` - Version history
- `docs/Setup.md` - Setup instructions (if applicable)
- `docs/Quick Reference.md` - Command examples
- Inline code comments and docstrings

---

## Questions and Support

### Getting Help

- **Documentation**: Check existing docs first
- **Issues**: Search [GitHub Issues](https://github.com/darshil0/AI-Testing/issues)
- **Discussions**: Use [GitHub Discussions](https://github.com/darshil0/AI-Testing/discussions) for questions
- **Discord/Slack**: (Add if you have community channels)

### Reporting Bugs

When reporting bugs, include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Minimal steps to reproduce
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: 
   - Python version
   - OS
   - Relevant dependencies
6. **Logs**: Include error messages and logs

Bug report template:
```markdown
**Description**
Brief description of the bug

**To Reproduce**
1. Run command...
2. Observe error...

**Expected Behavior**
Should work correctly

**Environment**
- Python: 3.11
- OS: macOS 14.0
- AI-Testing version: 2.0.1

**Additional Context**
Logs, screenshots, etc.
```

---

## Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes
- Project acknowledgments

Thank you for contributing to AI-Testing! 🎉

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
