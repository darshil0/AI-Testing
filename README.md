# AI-Testing 🤖

A professional, enterprise-ready evaluation framework for benchmarking AI models across various domains. Test and compare models from OpenAI, Anthropic, Google, and local LLMs with standardized metrics, automated judging, and professional analytics.

---

## ✨ Key Features

### 🔌 Universal Model Support

* **Cloud APIs**: OpenAI (GPT-4o), Anthropic (Claude), Google (Gemini).
* **Local Models**: Ollama integration for Llama, Mistral, and other open-source models.
* **Simulated Mode**: Test workflows without consuming API credits during development.

### ⚖️ Intelligent Evaluation

* **LLM-as-a-Judge**: Automated scoring using state-of-the-art models.
* **Specialized Personas**: Evaluate from different perspectives (Critic, Helper, Auditor).
* **Custom Criteria**: Define specific expectations for each test case.

### 📊 Professional Analytics

* **Automated Charts**: Generate publication-ready performance visualizations.
* **Interactive Dashboard**: Explore results with a Streamlit web interface.
* **Cost Tracking**: Real-time token usage and API cost estimation.
* **Performance Metrics**: Latency, accuracy, and quality scoring.

### 🛡️ Security & Quality

* **PII Detection**: Automatic scanning for privacy leaks.
* **Multi-dimensional Testing**: Categories include reasoning, coding, creativity, and safety.
* **Reproducible Results**: Timestamped JSON exports for all evaluations.

### 🚀 Developer Experience

* **Rich CLI**: Intuitive terminal interface with real-time progress bars.
* **Parallel Processing**: Fast evaluation with concurrent execution.
* **Docker Ready**: Containerized environment for cross-platform consistency.
* **CI/CD Integration**: GitHub Actions ready for automated regression testing.

---

## 📂 Project Structure

```text
AI-Testing/
├── ai_evaluation/
│   ├── __init__.py
│   ├── run_evaluation.py    # Main evaluation engine
│   ├── dashboard.py         # Streamlit dashboard
│   ├── models.py            # Model adapters (OpenAI, Anthropic, etc.)
│   ├── config.yaml          # Centralized configuration
│   └── test_cases/          # Test prompts and scenarios
├── tests/                   # Unit and integration tests
├── pyproject.toml           # Project definition and dependencies
├── Dockerfile               # Container definition
└── docs/                    # Detailed documentation

```

---

## 🚀 Getting Started

### 1. Installation

Clone the repository and install the project in editable mode:

```bash
# Clone the repository
git clone https://github.com/darshil0/AI-Testing.git
cd AI-Testing

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the project and its dependencies
pip install -e .

```

### 2. API Configuration

Configure your API keys in the environment file:

```bash
# Copy the template
cp .env.example .env

# Add your API keys (DO NOT commit this file to version control)
nano .env 

```

### 3. Running an Evaluation

The framework provides two primary entry points:

```bash
# Run a test with the simulated model (no API key needed)
run-evaluation --models simulated:default

# Evaluate a real model
run-evaluation --models openai:gpt-4o

# Compare multiple models side-by-side
run-evaluation --models openai:gpt-4o anthropic:claude-sonnet-3.5

```

---

## 💻 Usage Guide

### Model Format

Models are specified as `provider:model_name`:

| Provider | Example |
| --- | --- |
| OpenAI | `openai:gpt-4o` |
| Anthropic | `anthropic:claude-3-5-sonnet` |
| Google | `gemini:gemini-1.5-pro` |
| Ollama | `ollama:llama3` |
| Simulated | `simulated:default` |

### Judge Personas

* `default`: Objective and balanced evaluation.
* `critic`: Strict scoring; penalizes minor errors or verbosity.
* `helper`: Focuses on clarity, tone, and helpfulness.
* `auditor`: Security-focused; checks for safety and policy violations.

---

## 📝 Creating Test Cases

### YAML Format (Recommended)

Create a file in `ai_evaluation/test_cases/code_opt.yaml`:

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

---

## 🧪 Development

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=ai_evaluation

```

### Adding a New Model Provider

1. Define a new class in `ai_evaluation/models.py` inheriting from `BaseModel`.
2. Register the provider in the `get_model()` factory function.
3. Update `config.yaml` with the provider's pricing.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](https://www.google.com/search?q=LICENSE) for details.

---

**Made with ❤️ by Darshil**

[⬆ Back to Top](https://www.google.com/search?q=%23ai-testing-)

---
