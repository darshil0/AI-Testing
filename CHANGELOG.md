# Changelog

All notable changes to the AI-Testing project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

