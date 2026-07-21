# Changelog

All notable changes to the AI-Testing project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.6] - 2026-07-20

### Fixed

- **Pricing warning omission**: Suppressed missing pricing warning for standard simulated model named `"default"`.
- **Version synchronization**: Upgraded and standardized version reference to `2.1.6` across the package, configuration, tests, and all documentation guides.

## [2.1.5] - 2026-07-15

### Added

- **Version Synchronization**: Synchronized and standardized all package and CLI version references to `2.1.5` across `pyproject.toml`, `ai_evaluation/__init__.py`, `tests/__init__.py`, `ai_evaluation/run_evaluation.py`, and `ai_evaluation/dashboard.py`.
- **Documentation Polishing**: Overhauled `docs/CONTRIBUTING.md` and `README.md` to ensure instructions align with standard development setups.
- **Lazy Dashboard Loading**: Added lazy import wrapper `run_dashboard()` inside package initialization to prevent eager importing of Streamlit when calling other parts of the package.
- **Execution Entry Points**: Created package entry point `ai_evaluation/__main__.py` to support running the evaluation via `python -m ai_evaluation` cleanly.

### Fixed

- **Test Discovery & CI failures**: Replaced tests scaffolding in `tests/test_run_evaluation.py` with 12 deterministic and comprehensive unit tests. Resolved pytest collection warning on `TestCase`.
- **Hardened JSON parsing**: Replaced fragile judge response regex with balanced brace block parsing (`extract_json_blocks`), validated parsing and expected schema keys, and replaced silent failures with warning/error propagation. Modified `process_one` to cleanly catch judge exceptions and retain raw model responses.
- **Docker Layer Caching & Package build**: Modified `Dockerfile` to copy `pyproject.toml` and package source directory `ai_evaluation/` before executing `pip install -e .` to resolve packaging build failure while preserving caching.
- **CLI Usage Documentation**: Realigned all docs to prefer standardized module-entry invocations (`python -m ai_evaluation.run_evaluation` and `python -m ai_evaluation`).
- **Dependency Drift Resolved**: Cleaned up package drift by removing redundant `requirements.txt` and establishing `pyproject.toml` as single source of truth.
- **Accuracy & Correctness Polishing**: Anchored plain text test-case headers strictly to line starts. Added missing pricing warnings in `models.py` and retry logic to `OllamaModel.call`.
- **Environment Minimalization**: Cleaned up unused, dead environment variables in `.env.example`.
- **Documentation Realignment**: Realigned documentation to match actual feature implementations by removing unsupported expected answer claims.

## [2.1.4] - 2026-07-14

### Fixed

- **Dashboard Model Selection**: Fixed a bug in the Individual Response View where only the first model's response was shown. Added a dropdown to explicitly select which model's output to inspect.
- **Hardcoded Results Paths**: `analytics.py` and `dashboard.py` previously hardcoded the `results` directory. They now dynamically read `directories.results` from `config.yaml`.
- **Dashboard JSON Crashes**: Added a `try/except` block for `json.JSONDecodeError` to prevent the Streamlit dashboard from crashing entirely when a corrupted JSON run file is selected.
- **Empty DataFrame KeyErrors**: Added a check for `df.empty` in the dashboard to immediately halt execution and display a warning instead of raising a fatal `KeyError` when loading empty evaluation runs.
- **`AnthropicModel` Temperature Config**: The Anthropic API integration now correctly reads and passes the `temperature` parameter from `config.yaml`, instead of ignoring it.
- **Missing `.yml` Support**: The test case glob discovery in `run_suite` now successfully collects `.yml` files in addition to `.yaml` and `.txt`.

## [2.1.3] - 2026-07-14

### Fixed

- **Prompt Contamination**: `_parse_test_case` for `.txt` files was passing the entire raw file content — including `Category:` and `Difficulty:` metadata header lines — as the AI prompt. Added a regex strip so only the body text after the headers is sent to the model.
- **Mutable Pydantic Default**: `EvaluationResult.pii_types` was declared as `List[str] = []`, a mutable default incompatible with Pydantic v2. Changed to `Field(default_factory=list)`.
- **Fragile Judge JSON Regex**: The regex `r'\{[^}]*"score"[^}]*\}'` used to extract the judge's JSON response broke silently whenever the `reasoning` value contained a `}` character (e.g. in code snippets). Changed to a non-greedy DOTALL match.
- **`OllamaModel` Dict-Style Access**: `resp["message"]["content"]` crashed at runtime because the `ollama` library returns an object, not a dict. Changed to `resp.message.content`.
- **Missing `@retry` on `GeminiModel`**: Unlike `OpenAIModel` and `AnthropicModel`, `GeminiModel.call` had no retry decorator, making it brittle against transient rate-limit errors. Added `@retry(stop=stop_after_attempt(3), ...)`.
- **`default_model_params` Never Read**: `config.yaml` defined `default_model_params.max_tokens` and `default_model_params.temperature`, but all model classes read top-level keys that didn't exist. Updated all model classes to check `default_model_params` first and added top-level alias keys to `config.yaml`.
- **`FileHandler` Relative Path**: `logging.FileHandler("evaluation.log")` wrote the log to whatever the process's current working directory happened to be. Changed to an absolute path anchored at the project root via `__file__`.
- **`load_from_hf` Inaccurate Count Log**: The success log always reported the original `count` argument, even if fewer items had a usable prompt field. Worse, `i` would be undefined if the dataset was empty, causing a `NameError`. Introduced a `written_count` variable incremented only when a file is actually written.
- **`TextColumn` Format String**: `TextColumn("{task.description}")` skipped Rich's canonical `progress.description` style. Changed to `TextColumn("[progress.description]{task.description}")`.
- **`subprocess.run` Missing `check=True`**: `dashboard.py`'s `main()` called `subprocess.run(...)` without `check=True`, silently swallowing failures (e.g. Streamlit not installed). Added `check=True`.
- **`__init__.py` CRLF Line Endings**: The file used Windows-style `\r\n` line endings inconsistently with the rest of the project. Converted to LF.
- **Version String Mismatch**: `argparse` description said `"AI Evaluation Framework V2.0.2"` while the package and startup banner both reported `V2.1.0`. Aligned to `V2.1.0`.
- **Missing `encoding="utf-8"`**: Added the explicit encoding argument to `open()` calls in `dashboard.py` and two locations in `tests/test_run_evaluation.py` to prevent `UnicodeDecodeError` / `UnicodeEncodeError` on Windows.
- **`requirements.txt` Version Conflict**: `pandas>=2.1.0` conflicted with `pandas>=2.0.0` in `pyproject.toml`. Aligned both to `>=2.0.0`.

---

## [2.1.2] - 2026-07-13

### Fixed
- **CI/CD Pipeline**: Standardized simulated evaluation execution using the `run-evaluation` console script command and fixed the model format argument to `simulated:default`. Installed the package editably in the GitHub Actions workflow.
- **Directory Path Resolution**: Corrected configuration paths in `config.yaml` to ensure test cases and results resolve cleanly relative to the package workspace.
- **Test Case YAML Parsing**: Resolved a keyword collision on `name` when parsing YAML test case files.

## [2.1.1] - 2026-01-05

### Added
- **Dashboard Entry Point**: Introduced a standard `main()` function in `ai_evaluation/dashboard.py` to support CLI execution and packaging entry points.

### Changed
- **Packaging Alignment**: Standardized `pyproject.toml` configuration to route `view-dashboard` script command to the correct `main()` entry point of the dashboard.
- **Improved Code Quality**: Run `black` code formatter on modified and core package modules.

### Fixed
- **Testing Imports**: Cleaned up package and test `__init__.py` namespaces to avoid test runner compilation errors and namespace pollution.
- **Score Clamping Test Mocking**: Fixed a mocking error in unit tests by targeting `get_model` within the namespace of `ai_evaluation.run_evaluation` where it is actually looked up.

---

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
