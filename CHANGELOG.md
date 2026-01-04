# Changelog

All notable changes to the AI-Testing project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-01-04

### Added
- **Project Packaging**: Introduced `pyproject.toml` to define the project as an installable package.
- **Console Scripts**: Created `run-evaluation` and `view-dashboard` entry points for easier execution.

### Changed
- **Project Structure**: Consolidated all source code into the `ai_evaluation` directory by moving `dashboard.py`.
- **Documentation**: Overhauled `README.md` with a modern structure, clearer installation instructions (`pip install -e .`), and usage examples for new console scripts.
- **Code Quality**: Standardized script execution to use `python -m` for better path resolution and resolved linting issues.

### Fixed
- **Testing**: Corrected a `unittest.mock.patch` targeting error and improved mocking strategy in `tests/test_run_evaluation.py` to ensure test reliability.

---

## [2.0.1] - 2026-01-03

### Fixed
- **Dependencies**: Removed duplicate entries in `requirements.txt` (tenacity, pytest, pytest-mock, pyyaml).
- **Path Resolution**: Improved config file path handling to work from any execution directory.
- **Error Handling**: Enhanced error messages and graceful degradation when test cases are missing.
- **JSON Parsing**: Robust judge response parsing with fallback mechanisms.
- **Score Validation**: Added clamping to ensure judge scores stay strictly within the 0.0-1.0 range.
- **PII Scanner**: Added validation for invalid regex patterns.

### Added
- **Summary Table**: Rich terminal display of evaluation results.
- **Quick Stats**: Display average score, total cost, and PII warnings post-evaluation.
- **Sequential Mode**: Added `--sequential` flag to assist with debugging.
- **Persona Validation**: CLI validation for judge persona choices.

---

## [2.0.0] - 2026-01-03

### Changed
- **Architectural Overhaul**: Major refactoring for modularity; model-specific logic is now encapsulated in `ai_evaluation/models.py`.
- **Centralized Configuration**: All settings (pricing, personas, PII patterns) are now managed in `ai_evaluation/config.yaml`.
- **CLI Arguments**: Standardized the `--models` argument to `provider:model_name` format (e.g., `openai:gpt-4o`).

### Added
- **Extensible Model Factory**: New `get_model` factory function for easier integration of new providers.
- **Formal Contribution Guide**: Added `docs/CONTRIBUTING.md`.

---

## [1.1.0] - 2026-01-03

### Added
- **📊 Visual Analytics Engine**: New `analytics.py` module to generate high-resolution performance plots.
- **🕹️ Interactive Dashboard**: Built-in **Streamlit** dashboard for real-time result exploration.
- **🏠 Local Model Support**: Integrated **Ollama** for benchmarking local models like Llama and Mistral.
- **🛡️ Security & Privacy Suite**: Automated **PII Scanning** and specialized **Judge Personas**.
- **🚀 CI/CD Integration**: Automated quality gates via GitHub Actions.

---

## [1.0.0] - 2026-01-03

### Added
- **🌐 Model Expansion**: Official support for Google Gemini 1.5 Pro.
- **⚖️ LLM-as-a-Judge**: Automated scoring system using high-capability models.
- **✨ Rich CLI**: Premium terminal interface with progress bars and status updates.
- **💰 Token & Cost Tracking**: Real-time calculation of API costs.
- **🛠️ Advanced Test Schemas**: Support for `.yaml` based test cases with metadata.

---

## [0.1.0] - 2025-11-01

### Added
- Initial repository structure and basic evaluation framework.
- MIT License.
