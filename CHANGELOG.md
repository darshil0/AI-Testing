# Changelog

All notable changes to the AI-Testing project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-03

### Changed
- **Architectural Overhaul**: Major refactoring for modularity. Model-specific logic is now encapsulated in `ai_evaluation/models.py`.
- **Centralized Configuration**: All settings, including pricing, personas, and PII patterns, are now managed in `ai_evaluation/config.yaml`. The evaluation engine is now fully config-driven.
- **CLI Arguments**: The `--models` argument has been standardized to a `provider:model_name` format (e.g., `openai:gpt-4o`, `ollama:llama3`) for clarity and extensibility.

### Added
- **Extensible Model Factory**: A new `get_model` factory function allows for easier integration of new model providers.
- **Formal Contribution Guide**: Added `docs/CONTRIBUTING.md` to standardize the contribution process.

### Fixed
- Improved error handling for model initialization and API failures.
- Standardized token estimation heuristics for local models within the `OllamaModel` class.

---

## [1.1.0] - 2026-01-03

### Added
- **📊 Visual Analytics Engine**: New `analytics.py` module to generate high-resolution performance plots and reports.
- **🕹️ Interactive Dashboard**: Built-in **Streamlit** dashboard for real-time result exploration and response inspection.
- **🏠 Local Model Support**: Integrated **Ollama** allowing you to benchmark local models (Llama, Mistral, etc.) alongside cloud APIs.
- **🛡️ Security & Privacy Suite**:
  - Automated **PII Scanning** to detect leaks of emails, phones, and credit cards in model responses.
  *   **Judge Personas**: Specialized judges (`The Critic`, `The Auditor`, `The Helper`) for multi-dimensional evaluation.
- **🧪 Dataset Pipeline**: Integrated **HuggingFace Datasets** loader for benchmarking against industry-standard datasets.
- **🚀 CI/CD Integration**: Automated quality gates via **GitHub Actions** workflows.

### Changed
- **Engine**: Upgraded `run_evaluation` to support `.yaml` schemas with explicit expectations.

---

## [1.0.0] - 2026-01-03

### Added
- **🌐 Model Expansion**: Official support for **Google Gemini 1.5 Pro** via `google-generativeai`.
- **⚖️ LLM-as-a-Judge**: Automated scoring system where high-capability models evaluate response quality based on criteria.
- **✨ Rich CLI**: Premium terminal interface with progress bars, status updates, and beautiful summary tables (`rich`).
- **🐳 Containerization**: Added `Dockerfile` and `docker-compose.yml` for isolated cross-platform execution.
- **💰 Token & Cost Tracking**: Real-time calculation of token usage and estimated API costs for all major providers.
- **🛠️ Advanced Test Schemas**: Added support for `.yaml` based test cases with built-in expectations and metadata.
- **📈 Comprehensive Reporting**: New `comparison_report.csv` for side-by-side benchmarking of multiple models.

### Changed
- **Architecture**: Overhauled `AIEvaluator` with Pydantic for strict data validation and type safety.
- **Parallelism**: Defaults to multi-threaded execution for high throughput.

---

## [0.8.0] - 2026-01-03

### Added
- **Real Model Integration**: Native support for OpenAI (GPT) and Anthropic (Claude) APIs.
- **Parallel Computing**: Implemented `ThreadPoolExecutor` to run evaluations concurrently, drastically reducing execution time for large test suites.
- **Robustness Suite**: 
  - Integrated `tenacity` for exponential backoff and automatic retries on API failure.
  - Added `python-dotenv` for secure management of API keys and configuration.
- **Logging System**: Full Python `logging` integration with support for file logging (`evaluation.log`) and configurable levels.
- **Advanced Metadata**: 
  - Automated tracking of request duration (latency).
  - Basic scoring mechanism for automated evaluation.
- **Batch Export**: Automatically exports both JSON and CSV summaries on every run.

### Changed
- **CLI Upgrades**: New `--sequential` flag to disable parallel processing if needed.
- **Improved AIEvaluator**: Internal refactor for better thread-safety and error isolation.

---

## [0.7.0] - 2026-01-03

### Added
- **CLI Support**: `run_evaluation.py` now accepts `--model` arguments for easy switching between model providers.
- **Export Functionality**: Results can now be exported to JSON and CSV formats.
- **Test Standardization**: All test cases are now in `.txt` format with standardized `Category` and `Difficulty` headers.
- **Unit Testing**: Comprehensive test suite using `pytest` and `pytest-mock` to ensure stability.
- **Linting**: Added `flake8` configuration and resolved all code style issues.
- **Documentation**: Completely overhauled `README.md`, added `SETUP.md`, `QUICK_REFERENCE.md`, and `CONTRIBUTING.md`.

### Changed
- **Refactoring**: Converted `run_evaluation.py` from a script to a modular `AIEvaluator` class.
- **Dependency Management**: Updated `requirements.txt` with strict versioning and testing dependencies.
- **Path Handling**: Improved relative path resolution to allow running scripts from the project root.

### Fixed
- Resolved relative path issues preventing execution from root directory.
- Fixed header formatting in legacy test cases.
- Corrected boolean logic and error handling in file operations.

## [0.1.0] - 2025-11-01

### Added
- Initial repository structure
- Basic evaluation framework
- Test cases directory
- Results directory
- Basic run_evaluation.py script

---
