# Quick Reference Guide

A cheat sheet for common tasks in the AI-Testing repository.

## Installation & Setup

```bash
# Clone the repository
git clone https://github.com/darshil0/AI-Testing.git
cd AI-Testing

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package in editable mode with development dependencies
pip install -e ".[dev]"

# Set up environment variables
cp .env.example .env
nano .env # Set your API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY)
```

---

## Command Reference

### Running Evaluations
```bash
# Run with simulated default model (no API key/cost)
run-evaluation --models simulated:default

# Run with a single cloud API model
run-evaluation --models openai:gpt-4o

# Run and compare multiple models side-by-side
run-evaluation --models openai:gpt-4o anthropic:claude-3-5-sonnet-20241022

# Run with specialized judge persona (choices: default, critic, helper, auditor)
run-evaluation --models simulated:default --persona critic

# Run sequentially (one test case at a time, for debugging)
run-evaluation --models simulated:default --sequential

# Specify custom configuration file path
run-evaluation --models simulated:default --config ai_evaluation/config.yaml
```

### Results & Interactive Dashboard
```bash
# Launch the Streamlit visualization dashboard
view-dashboard

# Alternatively, run the dashboard module directly
python -m ai_evaluation.dashboard
```

---

## Test Case Formats

The framework automatically loads and processes test cases from the `ai_evaluation/test_cases/` directory. Files ending in `.txt`, `.yaml`, or `.yml` are supported.

### 1. YAML / YML Format (Recommended)

```yaml
name: code_optimization
category: Coding
difficulty: Hard
prompt: |
  Optimize this Python function for better time complexity:
  def find_duplicates(arr):
      # inefficient code here
      pass

expectations:
  - "Mention using a set for O(n) complexity"
  - "Provide working implementation"
  - "Explain the optimization"
```

### 2. Plain Text Format (`.txt`)

Optional `Category:` and `Difficulty:` header lines can be specified at the start of the file. The framework automatically parses them as metadata and **strips them from the prompt** before sending it to the model.

```text
Category: Reasoning
Difficulty: Hard

If a train travels 60 mph for 2 hours and then 80 mph for 1 hour, what is the average speed for the whole journey?
```

### 3. Test Cases with Expected Answers

Test cases can contain an expected answer for scoring. The expected answer is separated from the prompt using `--- Expected Answer ---`:

```yaml
name: capital_of_france
category: Factual
difficulty: Easy
prompt: "What is the capital of France?"
expectations:
  - "Mention Paris"
--- Expected Answer ---
Paris is the capital of France.
```

---

## File Structure

```text
AI-Testing/
├── ai_evaluation/
│   ├── test_cases/         # Test prompts (.txt, .yaml, .yml)
│   ├── test_scenarios/     # Comprehensive markdown test descriptions
│   ├── results/            # Run result output files (.json)
│   ├── __init__.py         # Package initialization
│   ├── run_evaluation.py    # CLI runner
│   ├── dashboard.py         # Streamlit dashboard
│   ├── models.py            # Model abstraction layer
│   ├── analytics.py         # Visual chart generation
│   └── config.yaml          # Config (personas, pricing, PII regex patterns)
├── docs/                   # Detailed documentation
├── tests/                  # Pytest unit tests
├── pyproject.toml          # Packaging and package scripts
├── requirements.txt        # Top-level dependencies
└── requirements.lock       # Pin-locked compile specifications
```

---

## Model Specification

Models are formatted as `provider:model_name`. Standard configurations are handled in `ai_evaluation/models.py`.

| Provider | Prefix Syntax | Example Specification |
| :--- | :--- | :--- |
| **Simulated** | `simulated:*` | `simulated:default` |
| **OpenAI** | `openai:*` | `openai:gpt-4o` |
| **Anthropic** | `anthropic:*` | `anthropic:claude-3-5-sonnet-20241022` |
| **Google** | `gemini:*` | `gemini:gemini-1.5-pro` |
| **Ollama** | `ollama:*` | `ollama:llama3` |

---

## Developer Workflows

### Running Code Quality Checkers
```bash
# Run pytest unit tests with mock structures
python3 -m pytest

# Run style checks with Flake8
flake8 .

# Apply Black code formatter
black .
```

### Managing Results Programmatically
```python
import json
from pathlib import Path

# Load and print average scores of latest evaluation
results_file = Path("ai_evaluation/results/latest_results.json")
if results_file.exists():
    with open(results_file, "r") as f:
        results = json.load(f)
        for r in results:
            print(f"Test: {r['test_case_name']} | Model: {r['model_type']} | Score: {r['judge_score']}")
```
