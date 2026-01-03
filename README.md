# AI-Testing 🤖

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: flake8](https://img.shields.io/badge/code%20style-flake8-black.svg)](https://flake8.pycqa.org/en/latest/)

A professional evaluation framework designed to benchmark AI models across various domains. This repository provides a structured environment for testing models like GPT-4, Claude, and Gemini with standardized metrics and reproducible results.

---

## 🚀 Features

- **🔌 Plug-and-Play Architecture**: Easily switch between `OpenAI` (GPT-4), `Anthropic` (Claude 3), and `Simulated` models.
- **⚡ Parallel Computing**: Built-in multi-threading to process batch test cases concurrently for maximum speed.
- **🛡️ High Reliability**: Automatic **retries with exponential backoff** via `tenacity` to handle transient API or network failures.
- **📊 Professional Reporting**: 
  - Automated generation of `JSON` and `CSV` export summaries.
  - Tracking of **performance latency** (duration per request).
- **🪵 Advanced Logging**: Full logging system that records evaluation telemetry to `evaluation.log`.
- **⚙️ Environment Driven**: Seamless configuration via `.env` for secure API key and log level management.

---

## 📂 Project Structure

```text
AI-Testing/
├── .env.example              # Template for API keys
├── .flake8                   # Linting configuration
├── CHANGELOG.md               # Detailed version history
├── requirements.txt           # Project dependencies
├── ai_evaluation/
│   ├── run_evaluation.py     # Core AIEvaluator engine (supports CLI)
│   ├── test_cases/           # Standardized .txt test cases
│   └── results/              # Auto-generated reports & exports
├── tests/                    # Robust unit test suite
└── docs/                     # Guides and setup documentation
```

---

## 📋 Prerequisites

- **Python 3.8+**
- A terminal/command prompt
- OpenAI or Anthropic API Keys (for live model benchmarking)

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
   # Edit .env to add your API keys:
   # OPENAI_API_KEY=sk-...
   ```

---

## 💻 Usage

The `AIEvaluator` supports both programmatic use and a powerful Command Line Interface.

### Execute Evaluation
Run the engine from the project root:

```bash
# Basic run (Simulated mode, Parallel)
python ai_evaluation/run_evaluation.py

# Benchmark OpenAI models with Parallel execution
python ai_evaluation/run_evaluation.py --model openai

# Run benchmarking sequentially (disables multi-threading)
python ai_evaluation/run_evaluation.py --model anthropic --sequential
```

### Review Results
Outputs are generated in the `ai_evaluation/results/` directory:
- **Latencies**: Check the `CSV` export for the `duration` column to analyze model speed.
- **Programmatic Data**: Use the `JSON` export for integration with other tools.
- **Telemetry**: Review `evaluation.log` in the root directory for execution logs and any retry events.

---

## 🧪 Development & Quality

We maintain high standards for code quality:

- **Tests**: `python -m pytest`
- **Linting**: `python -m flake8 .`

---

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Please read our [CONTRIBUTING.md](docs/CONTRIBUTING.md) guide.
2. Check the [CHANGELOG.md](CHANGELOG.md) for version details.
3. Open a Pull Request!

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**[⬆ Back to Top](#ai-testing-)**
