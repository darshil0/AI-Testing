# Changelog

All notable changes to the AI-Testing project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [0.1.0] - 2025-12-30

### Added
- Initial repository structure
- Basic evaluation framework
- Test cases directory
- Results directory
- Basic run_evaluation.py script

---

