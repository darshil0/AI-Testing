# AI-Testing 🤖

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![CI](https://github.com/darshil0/AI-Testing/actions/workflows/ci.yml/badge.svg)](https://github.com/darshil0/AI-Testing/actions/workflows/ci.yml)

A professional evaluation framework designed to benchmark AI models across various domains. This repository provides an enterprise-ready environment for testing models like GPT-4, Claude, Gemini, and **local LLMs via Ollama** with standardized metrics, automated judging, and professional analytics.

---

## 🚀 Features

- **🔌 Global Model Support**: Benchmark `OpenAI`, `Anthropic`, `Google Gemini`, and **Local Ollama** models in one run.
- **⚖️ Specialized Judge Personas**: Evaluate responses through the lens of a **Critic**, **Helper**, or **Security Auditor**.
- **📊 Professional Analytics**: Automated generation of latency, cost, and score charts via `analytics.py`.
- **🕹️ Interactive Dashboard**: Explore your results in a rich, web-based UI using **Streamlit**.
- **🛡️ Security Layer**: Built-in **PII scanning** to detect privacy leaks in model outputs.
- **🧪 Dataset Pipeline**: Pull test cases directly from **HuggingFace** for industry-standard benchmarking.
- **🐳 DevOps Ready**: Standardized with **Docker** and **GitHub Actions** CI/CD.

---

## 📂 Project Structure

```text
AI-Testing/
├── .github/workflows/        # CI/CD pipelines
├── ai_evaluation/
│   ├── models.py             # Modular model handlers
│   ├── run_evaluation.py     # Main engine (V2.0)
│   ├── analytics.py          # Chart generation module
│   ├── config.yaml           # Centralized configuration
│   ├── test_cases/           # Standardized .txt and .yaml cases
│   └── results/              # Auto-generated reports & charts
├── dashboard.py              # Streamlit interactive UI
├── Dockerfile                # Container definitions
└── requirements.txt           # Project dependencies
```

---

## 🛠️ Setup & Installation

1. **Quick Install**:
   ```bash
   pip install -r requirements.txt
   ```

2. **API Keys**: Configure `.env` using `.env.example`.
   - `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` (Optional)

---

## 💻 Usage

### 1. Execute Benchmarking
Run evaluations on multiple models simultaneously using the `provider:model_name` format.

```bash
# Benchmark OpenAI's GPT-4o and a local Llama 3 model
python ai_evaluation/run_evaluation.py --models openai:gpt-4o ollama:llama3

# Run with a specialized Persona (e.g., 'auditor')
python ai_evaluation/run_evaluation.py --models simulated:default --persona auditor
```

### 2. Generate Analytics
To create professional charts and comparison reports:

```bash
python ai_evaluation/analytics.py
```
Check `ai_evaluation/results/benchmark_report.png` for the visual output.

### 3. Launch Dashboard
To explore results interactively:

```bash
streamlit run dashboard.py
```

---

## 🧪 Development & CI/CD

We maintain high standards for code quality:
- **Unit Tests**: `pytest` entries verified on every commit.
- **Linting**: Strict `flake8` and `black` compliance.
- **CI**: Automated GitHub Actions runs on Pull Requests.

---

## 🤝 Contributing

1. Please read our [CONTRIBUTING.md](docs/CONTRIBUTING.md) guide.
2. Check the [CHANGELOG.md](CHANGELOG.md) for version details.
3. Open a Pull Request!

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**[⬆ Back to Top](#ai-testing-)**
