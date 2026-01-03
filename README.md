# AI-Testing 🤖

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: flake8](https://img.shields.io/badge/code%20style-flake8-black.svg)](https://flake8.pycqa.org/en/latest/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)

A professional evaluation framework designed to benchmark AI models across various domains. This repository provides a structured environment for testing models like GPT-4, Claude, and Gemini with standardized metrics, automated scoring, and reproducible results.

---

## 🚀 Features

- **🔌 Multi-Model Benchmarking**: Native support for `OpenAI`, `Anthropic`, and **`Google Gemini 1.5`**.
- **⚖️ LLM-as-a-Judge**: Automated quality scoring using SOTA models (GPT-4o/Claude 3 Opus) as evaluators.
- **⚡ High-Throughput Parallelism**: Concurrent test execution for rapid batch processing.
- **💰 Economics & Telemetry**: Integrated token counting, cost estimation, and latency tracking.
- **🐳 Multi-Platform Ready**: Fully containerized with **Docker** for zero-setup deployment.
- **✨ Rich CLI Experience**: Real-time progress tracking and aesthetic result summaries.
- **📊 Comparison Reports**: Generate side-by-side performance analytics in CSV and JSON.

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
