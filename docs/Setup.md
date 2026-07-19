# Setup Guide for AI-Testing

This guide will walk you through setting up the AI-Testing evaluation framework on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher** (Python 3.10+ recommended) - [Download Python](https://www.python.org/downloads/)
- **pip** (Python package manager) - Usually comes with Python
- **git** - [Download Git](https://git-scm.com/downloads)

### Verify Installations

```bash
python3 --version  # Should show 3.9 or higher
pip3 --version
git --version
```

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/darshil0/AI-Testing.git
cd AI-Testing
```

### 2. Create a Virtual Environment

Creating a virtual environment keeps your project dependencies isolated:

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` appear in your terminal prompt, indicating the virtual environment is active.

### 3. Install Dependencies and CLI Tools

Install the project in editable mode so that you get the command-line interface tools (`run-evaluation` and `view-dashboard`):

```bash
pip install -e .
```

If you plan on running tests or contributing, install the development dependencies as well:

```bash
pip install -e ".[dev]"
```

This will install all necessary Python packages and CLI entry points, including:
- OpenAI API client
- Anthropic API client
- Google Generative AI client
- Ollama local LLM integration
- Pandas and Matplotlib/Seaborn for data analysis and charting
- Streamlit for the visual results dashboard
- Pytest for testing

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your actual API keys:

```bash
# On macOS/Linux
nano .env

# On Windows
notepad .env
```

**Getting API Keys:**

- **OpenAI**: Visit [OpenAI Platform](https://platform.openai.com/api-keys)
- **Anthropic**: Visit [Anthropic Console](https://console.anthropic.com/)
- **Google Gemini**: Visit [Google AI Studio](https://aistudio.google.com/)

Example `.env` configuration:
```env
OPENAI_API_KEY=sk-proj-...your-key...
ANTHROPIC_API_KEY=sk-ant-...your-key...
GEMINI_API_KEY=AIzaSy...your-key...
```

### 5. Create Directory Structure

Ensure the necessary directories exist (these are typically created automatically on startup, but can also be manually created):

```bash
mkdir -p ai_evaluation/test_cases
mkdir -p ai_evaluation/results
```

### 6. Add Test Cases

The framework supports test cases in both simple text `.txt` and rich `.yaml` / `.yml` format.

**YAML Format Example** (`ai_evaluation/test_cases/code_optimization.yaml`):
```yaml
name: code_optimization_task
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
```

**Text Format Example** (`ai_evaluation/test_cases/simple_test.txt`):
```text
Category: reasoning
Difficulty: easy

What is 2 + 2? Explain your answer.
```

### 7. Verify Setup

Test that everything is working using the simulated model provider, which doesn't require any API key or billing setup:

```bash
run-evaluation --models simulated:default
```

You should see an intuitive terminal progress bar indicating test cases are being processed, followed by a beautiful Rich-formatted evaluation summary table showing scores, duration, and estimated cost, then results being exported.

---

## Running Evaluations

The evaluation framework provides the robust `run-evaluation` terminal CLI.

### Basic Usage

**Run with simulated responses** (no API keys needed):
```bash
run-evaluation --models simulated:default
```

**Run with OpenAI:**
```bash
run-evaluation --models openai:gpt-4o
```

**Run with Anthropic Claude:**
```bash
run-evaluation --models anthropic:claude-3-5-sonnet-20241022
```

**Run and Compare Multiple Models Side-by-Side:**
```bash
run-evaluation --models openai:gpt-4o anthropic:claude-3-5-sonnet-20241022 simulated:default
```

### Advanced Options

**Change the Judge Persona:**
By default, the evaluator uses an objective judge. You can choose from standard personas: `default`, `critic`, `helper`, `auditor`:
```bash
run-evaluation --models simulated:default --persona critic
```

**Run Sequentially (useful for debugging):**
To disable parallel execution and evaluate test cases one at a time:
```bash
run-evaluation --models simulated:default --sequential
```

**Specify custom configuration:**
```bash
run-evaluation --models simulated:default --config ai_evaluation/config.yaml
```

**View help:**
```bash
run-evaluation --help
```

---

## Viewing Results & Dashboard

Each evaluation run automatically saves rich, detailed metadata to JSON files inside the `results/` directory configured in `config.yaml`.

### Launching the Dashboard

The framework comes with a Streamlit-based visual dashboard. You can launch it using:

```bash
view-dashboard
```

Alternatively, you can run:
```bash
python -m ai_evaluation.dashboard
```

The dashboard allows you to:
- Compare model scores side-by-side.
- Analyze latency, estimated cost, and token usage.
- Examine detailed model responses, criteria-based judge scoring, and reasoning.
- Scan for PII leaks flag warnings.

### Exploring JSON Files Directly

```bash
# List all results
ls ai_evaluation/results/

# Format and view latest result
cat ai_evaluation/results/latest_results.json | python -m json.tool
```

---

## Troubleshooting

### Common Issues

**Problem: `ModuleNotFoundError: No module named 'yaml'`**
- **Solution**: Ensure your virtual environment is active and the package is correctly installed with `pip install -e .`.

**Problem: `run-evaluation: command not found`**
- **Solution**: The CLI script isn't in your path. Make sure your virtual environment is activated (`source venv/bin/activate`), and you've installed the project with `pip install -e .`. Alternatively, run the package as a module: `python -m ai_evaluation.run_evaluation --models simulated:default`.

**Problem: API authentication error**
- **Solution**: Double-check that your `.env` file exists in the repository root, is formatted correctly, and has correct API keys without spaces or extra quotes.

**Problem: Corrupt dashboard results**
- **Solution**: If a corrupt JSON file in your results directory causes the dashboard to throw warnings, remove or back up the corrupted JSON runs and restart the dashboard.

---

## Next Steps

1. **Add your own test cases** in `ai_evaluation/test_cases/` using `.yaml` or `.txt`.
2. **Configure judge settings** or specialized model pricing in `ai_evaluation/config.yaml`.
3. **Contribute** to the project! Check out [CONTRIBUTING.md](CONTRIBUTING.md) for style standards and test instructions.
