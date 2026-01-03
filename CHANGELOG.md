# Changelog

All notable changes to the AI-Testing project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.2] - 2026-01-04

### Fixed
- **Code Quality**: Removed unused imports (`re`, `json`, `Optional`) from `ai_evaluation/models.py`.
- **Formatting**: Resolved all whitespace and formatting inconsistencies using `black`.

### Changed
- **Documentation**: Updated all `python` commands in `README.md` and `run_evaluation.py` to use the `python -m` module invocation style. This improves script reliability by ensuring correct path resolution.
- **README**: Restructured the Quick Start section into a more user-friendly "Getting Started" guide.

---

## [2.0.1] - 2026-01-03

### Fixed
- **Dependencies**: Removed duplicate entries in `requirements.txt` (tenacity, pytest, pytest-mock, pyyaml)
- **Path Resolution**: Improved config file path handling to work from any directory
- **Error Handling**: Enhanced error messages and graceful degradation when test cases are missing
- **JSON Parsing**: More robust judge response parsing with fallback mechanisms
- **Test Case Parsing**: Better handling of malformed test case files
- **Score Validation**: Added clamping to ensure judge scores stay within 0.0-1.0 range
- **Directory Creation**: Automatic creation of missing directories on initialization
- **PII Scanner**: Added error handling for invalid regex patterns
- **Empty Results**: Proper handling when no test cases are found

### Added
- **Summary Table**: Rich table display of evaluation results in terminal
- **Quick Stats**: Display average score, total cost, and PII warnings after evaluation
- **Better Logging**: More informative console messages throughout evaluation process
- **Help Text**: Improved CLI help with examples
- **Sequential Mode**: Added `--sequential` flag for debugging
- **Persona Validation**: CLI validation for judge persona choices

### Changed
- **Console Output**: Improved formatting and readability of terminal output
- **Export Function**: Better feedback when exporting results
- **Error Messages**: More specific and actionable error messages
- **Test Case Loading**: Better feedback when loading HuggingFace datasets
- **Documentation**: Updated README with clearer examples and troubleshooting

---

## [2.0.0] - 2026-01-03

### Changed
- **Architectural Overhaul**: Major refactoring for modularity. Model-specific logic is now encapsulated in `ai_evaluation/models.py`.
- **Centralized Configuration**: All settings, including pricing, personas, and PII patterns, are now managed in `ai_evaluation/config.yaml`. The evaluation engine is now fully config-driven.
- **CLI Arguments**: The `--models` argument has been standardized to a `provider:model_name` format (e.g., `openai:gpt-4o`, `ollama:llama3`) for clarity and extensibility.

### Added
- **Extensible Model Factory**: A new `get_model` factory function allows for easier integration of new model providers.
- **Formal Contribution Guide**: Added `docs/CONTRIBUTING.md` to standardize the contribution process.
- **Configuration Validation**: Better validation of config.yaml structure

### Fixed
- Improved error handling for model initialization and API failures.
- Standardized token estimation heuristics for local models within the `OllamaModel` class.
- Fixed path resolution issues when running from different directories

---

## [1.1.0] - 2026-01-03

### Added
- **📊 Visual Analytics Engine**: New `analytics.py` module to generate high-resolution performance plots and reports.
- **🕹️ Interactive Dashboard**: Built-in **Streamlit** dashboard for real-time result exploration and response inspection.
- **🏠 Local Model Support**: Integrated **Ollama** allowing you to benchmark local models (Llama, Mistral, etc.) alongside cloud APIs.
- **🛡️ Security & Privacy Suite**:
  - Automated **PII Scanning** to detect leaks of emails, phones, and credit cards in model responses.
  - **Judge Personas**: Specialized judges (`The Critic`, `The Auditor`, `The Helper`) for multi-dimensional evaluation.
- **🧪 Dataset Pipeline**: Integrated **HuggingFace Datasets** loader for benchmarking against industry-standard datasets.
- **🚀 CI/CD Integration**: Automated quality gates via **GitHub Actions** workflows.

### Changed
- **Engine**: Upgraded `run_evaluation` to support `.yaml` schemas with explicit expectations.
- **Test Framework**: Improved test coverage and reliability

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
- **Documentation**: Complete rewrite of user-facing documentation

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

---

## [0.1.0] - 2025-11-01

### Added
- Initial repository structure
- Basic evaluation framework
- Test cases directory
- Results directory
- Basic run_evaluation.py script
- MIT License
- Initial README and documentation

---

## Migration Notes

### Upgrading from 1.x to 2.0

The main breaking change is the model specification format:

**Old (v1.x):**
```bash
python run_evaluation.py --model openai
```

**New (v2.0+):**
```bash
python -m ai_evaluation.run_evaluation --models openai:gpt-4o
```

This change allows you to specify exact model versions and makes it easier to test multiple models simultaneously.

### Upgrading from 0.x to 1.0

Version 1.0 introduced the judge system. Old test cases will continue to work, but you can now add expectations:

```yaml
expectations:
  - "Provide clear explanation"
  - "Include code examples"
```

---

## Future Roadmap

See [GitHub Issues](https://github.com/darshil0/AI-Testing/issues) for planned features and enhancements.
