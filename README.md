# AI-Testing 🤖

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: flake8](https://img.shields.io/badge/code%20style-flake8-black.svg)](https://flake8.pycqa.org/en/latest/)

A professional evaluation framework designed to benchmark AI models across various domains. This repository provides a structured environment for testing models like GPT-4, Claude, and Gemini with standardized metrics and reproducible results.

---

## 🚀 Features

- **🔌 Plug-and-Play Architecture**: Easily switch between `OpenAI`, `Anthropic`, and `Simulated` models.
- **📚 Standardized Test Suite**: Over 20+ pre-defined test cases covering Reasoning, Coding, Safety, and Creativity.
- **📊 Professional Reporting**: Automated results generation in `JSON`, `CSV`, and human-readable `TXT` formats.
- **⚡ Developer First**: Fully linted with `flake8`, tested with `pytest`, and documented with clear workflows.
- **⚙️ Environment Driven**: Managed via `.env` for secure API key handling.

---

## 📂 Project Structure

```text
AI-Testing/
├── .env.example              # Template for API keys
├── .flake8                   # Linting configuration
├── requirements.txt           # Project dependencies
├── ai_evaluation/
│   ├── run_evaluation.py     # Main entry point & AIEvaluator class
│   ├── test_cases/           # Standardized test case repository (.txt)
│   ├── test_scenarios/       # Detailed scenario descriptions
│   └── results/              # Evaluation outputs (Auto-generated)
├── tests/                    # Unit tests for the framework
└── docs/                     # Detailed guides (Setup, Contributing, etc.)
```

---

## 📋 Prerequisites

- **Python 3.8+**
- A terminal/command prompt
- (Optional) OpenAI or Anthropic API Keys

---

## 🛠️ Installation

1. **Clone & Enter**:
   ```bash
   git clone https://github.com/darshil0/AI-Testing.git
   cd AI-Testing
   ```

2. **Dependency Setup**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Security Configuration**:
   ```bash
   cp .env.example .env
   # Open .env and add your API keys:
   # OPENAI_API_KEY=sk-...
   # ANTHROPIC_API_KEY=sk-ant-...
   ```

---

## 💻 Usage

### Execute Evaluation
The `AIEvaluator` class handles the logic. Run it directly or specify a model:

```bash
# Default: Simulated mode
python ai_evaluation/run_evaluation.py

# Benchmark OpenAI
python ai_evaluation/run_evaluation.py --model openai

# Benchmark Anthropic
python ai_evaluation/run_evaluation.py --model anthropic
```

### Review Results
Once complete, check the `ai_evaluation/results/` directory for:
- `result_<case>_<timestamp>.txt`: Detailed per-case output.
- `results_export_<timestamp>.json`: Batch data for programmatic analysis.
- `results_export_<timestamp>.csv`: Spreadsheet-ready summary.

---

## 🧪 Development & Quality

We maintain high standards for code quality:

- **Tests**: `python -m pytest`
- **Linting**: `python -m flake8 .`

---

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Please read our [CONTRIBUTING.md](docs/CONTRIBUTING.md) guide.
2. Check the [Roadmap](docs/Implementation%20Summary.md) for planned features.
3. Open a Pull Request!

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**[⬆ Back to Top](#ai-testing-)**
