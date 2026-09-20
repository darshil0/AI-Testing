# AI-Testing 🤖

![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?logo=openai&logoColor=white)
![Anthropic](https://img.shields.io/badge/Anthropic-Claude%203.5-D97757?logo=anthropic&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google-Gemini%201.5-8E75B2?logo=google-gemini&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLMs-black?logo=ollama&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

> Version 2.1.9 — Professional benchmarking and evaluation tooling for AI models across cloud providers, local LLMs, and custom test suites.

---

## ✨ Key Features

- Universal model support for OpenAI, Anthropic, Google Gemini, Ollama, and simulated/local testing
- LLM-as-a-judge scoring with persona-based evaluation modes
- Custom YAML/text test cases with structured expectations and metadata
- Results export in JSON/CSV with dashboard and analytics generation
- Security checks for PII leakage and automated benchmark reporting
- Docker-ready container setup and CLI-first developer workflow

---

## 📂 Project Structure

```text
AI-Testing/
├── ai_evaluation/
│   ├── __init__.py
│   ├── __main__.py
│   ├── analytics.py
│   ├── config.yaml
│   ├── dashboard.py
│   ├── models.py
│   ├── run_evaluation.py
│   ├── test_cases/
│   └── test_scenarios/
├── docs/
│   ├── Setup.md
│   ├── Quick Reference.md
│   ├── CONTRIBUTING.md
│   ├── migration_guide.md
│   ├── fixes_summary.md
│   └── implementation_checklist.md
├── tests/
├── .env.example
├── .flake8
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.lock
```

---

## 📚 Documentation

Use the local docs in this repository:

- [Setup Guide](docs/Setup.md)
- [Quick Reference](docs/Quick%20Reference.md)
- [Contributing Guide](docs/CONTRIBUTING.md)
- [Migration Guide](docs/migration_guide.md)
- [Fixes Summary](docs/fixes_summary.md)
- [Implementation Checklist](docs/implementation_checklist.md)

---

## 🚀 Getting Started

### 1. Install

```bash
git clone https://github.com/darshil0/AI-Testing.git
cd AI-Testing
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

For only the runtime package:

```bash
pip install -e .
```

For dashboard and analytics support:

```bash
pip install -e ".[dashboard]"
```

### 2. Configure API keys

```bash
cp .env.example .env
```

Then add your credentials to `.env`:

```dotenv
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
LOG_LEVEL=INFO
```

### 3. Run evaluations

```bash
# Simulated model, no API key required
run-evaluation --models simulated:default

# Real model providers
run-evaluation --models openai:gpt-4o
run-evaluation --models anthropic:claude-3-5-sonnet-20241022
run-evaluation --models gemini:gemini-1.5-pro
run-evaluation --models ollama:llama3

# Compare multiple models
run-evaluation --models openai:gpt-4o anthropic:claude-3-5-sonnet-20241022

# Export CSV instead of JSON
run-evaluation --models simulated:default --export-format csv

# Run sequentially (one case at a time)
run-evaluation --models simulated:default --sequential

# Return exit code 0 even when some evaluations fail
run-evaluation --models simulated:default --allow-failures

# Use a custom config file
run-evaluation --models simulated:default --config path/to/config.yaml

# Generate static analytics charts
generate-analytics

# Launch the interactive dashboard
view-dashboard

# Direct module execution
python -m ai_evaluation
python -m ai_evaluation.dashboard
python -m ai_evaluation.analytics
```

---

## 🧪 Test Case Format

### YAML format

```yaml
name: code_optimization
category: Coding
difficulty: Hard
prompt: |
  Optimize this Python function for better time complexity:
  def find_duplicates(arr):
      pass

expectations:
  - Mention using a set for O(n) complexity
  - Provide a working implementation
  - Explain the optimization
```

### Plain text format

```text
Category: Reasoning
Difficulty: Hard

If a train travels 60 mph for 2 hours and then 80 mph for 1 hour, what is the average speed for the whole journey?
```

---

## 🖥️ Usage Notes

### Model identifiers

Use the format `provider:model_name`:

| Provider | Example |
| --- | --- |
| OpenAI | `openai:gpt-4o` |
| Anthropic | `anthropic:claude-3-5-sonnet` |
| Google | `gemini:gemini-1.5-pro` |
| Ollama | `ollama:llama3` |
| Simulated | `simulated:default` |

### Judge personas

- `default`: balanced and objective
- `critic`: strict and detail-oriented
- `helper`: clarity and usability focused
- `auditor`: safety and compliance focused

---

## 🧪 Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=ai_evaluation

# Run linting
flake8 .
```

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

Made with ❤️ by Darshil.

[⬆ Back to Top](#ai-testing-)































































































































































































































 serieus






















































































































































































































































































































































n





























































