# AI-Testing Codebase Fixes - Summary

## Overview
This document provides a comprehensive history of the issues identified, refactored, and resolved in the AI-Testing codebase, tracking the evolution of the framework from its early versions up to **Version 2.1.6**.

---

## 🚀 Critical Fixes in Version 2.1.6

### 1. Robust Simulated Cost Tracking and Warnings
* **Problem**: When using the simulated model name `"default"` (i.e. `simulated:default`), pricing is not explicitly configured in `config.yaml` for `"default"`. Calculating costs triggered a pricing warning: `Pricing config is missing for model 'default'. Cost will be set to $0.0.`. This cluttered output for standard local-only evaluations and broke test assertions.
* **Fix**: Suppressed pricing warnings for the simulated model `"default"`.
* **Impact**: Cleaner logs and reliable simulated test runs.

## 🚀 Critical Fixes in Version 2.1.5

### 1. Robust Judge JSON Extraction via Balanced Braces
* **Problem**: Extracting the judge's JSON scores via basic regular expressions was highly fragile. If a judge outputted JSON containing nested braces (such as code blocks, JSON snippets, or complex punctuation inside the `reasoning` block), the parser would fail or crash.
* **Fix**: Replaced the fragile regex search with a robust balanced brace-matching algorithm (`extract_json_blocks`) to locate and extract complete JSON objects. Added rigorous schema key validation.
* **Resilience**: If JSON parsing fails, the system propagates clear warnings, preserves the raw model response, and assigns a sentinel score of `-1.0` to explicitly flag the evaluation failure rather than silently defaulting to `0.0` or crashing.

### 2. Lazy Loading of Streamlit (Lazy Imports)
* **Problem**: Standard package initialization eagerly imported the Streamlit package. This caused immediate startup and execution errors on systems or CI/CD pipelines where Streamlit was not installed or required (e.g., headless test runs).
* **Fix**: Encapsulated the Streamlit dashboard imports within a delayed functional wrapper (`run_dashboard()`) inside `ai_evaluation/__init__.py`.
* **Impact**: CLI tools can be run and tests can execute flawlessly without any Streamlit package dependencies being loaded upfront.

### 3. Pytest Mocking Target Resolving
* **Problem**: Mocking `get_model` inside `tests/test_run_evaluation.py` via string patching (e.g., `ai_evaluation.run_evaluation.get_model`) raised `AttributeError` on certain Python runtimes. This occurred because `ai_evaluation`'s package initialization overrode `run_evaluation` with its imported main function.
* **Fix**: Retrieved the target module object directly from `sys.modules['ai_evaluation.run_evaluation']` and patched using standard `unittest.mock.patch.object` on that module.
* **Impact**: Completely resolved testing failures across diverse environments.

### 4. Docker Layer Caching & Build Optimization
* **Problem**: The Docker build process was inefficient, rebuilds were slow, and packaging structure failed due to copy orders.
* **Fix**: Restructured the `Dockerfile` to copy `pyproject.toml` and the package source directory `ai_evaluation/` before executing the project setup `pip install -e .`.
* **Impact**: Faster rebuilds with Docker layer caching and consistent container builds.

---

## 🔧 Critical Fixes in Version 2.1.4

### 1. Streamlit Dashboard Model Selection
* **Problem**: In the "Individual Response View" of the Streamlit dashboard, only the first model's evaluation response was displayed.
* **Fix**: Added an explicit model selection dropdown, allowing the user to select and inspect the detailed prompt, response, and scoring for any model evaluated in the suite.

### 2. Elimination of Hardcoded Result Directory Paths
* **Problem**: Both `analytics.py` and `dashboard.py` had hardcoded `results` paths, which caused them to miss runs if the user customized directory paths in their configuration.
* **Fix**: Refactored both modules to dynamically read the `directories.results` configuration property from `config.yaml`.

### 3. Graceful Crash Protection for JSON and Empty Runs
* **Problem**: If an evaluation run failed or was interrupted, it could write an empty or malformed JSON file to the results folder. Selecting this corrupted run would crash the Streamlit dashboard.
* **Fix**:
  - Implemented `try/except` handlers for `json.JSONDecodeError` to prevent corrupted files from crashing the application.
  - Added strict checks for `df.empty` to halt rendering and display an informative warning instead of raising a fatal `KeyError`.

### 4. API Adapter Polishing
* **Problem**: The Anthropic model adapter ignored the `temperature` parameter configured in `config.yaml`.
* **Fix**: Updated `AnthropicModel` to parse and pass the configured `temperature` parameter into its API requests.

### 5. Multi-Extension Globbing Support
* **Problem**: Test case discovery was limited strictly to `.yaml` and `.txt`.
* **Fix**: Added support for `.yml` file extension globbing alongside `.yaml` in `run_suite`.

---

## 🛡️ Critical Fixes in Version 2.1.3

### 1. Prompt Contamination Stripping
* **Problem**: Metadata headers in `.txt` test cases (e.g., `Category: Reasoning` and `Difficulty: Hard`) were being sent to the evaluated model as part of the prompt, contaminating the model's response context.
* **Fix**: Implemented strict line-start anchored regexes (`^Category:` and `^Difficulty:`) with multiline flags to extract, parse, and completely strip these metadata headers from the prompt text before execution.

### 2. Mutable Pydantic Default Values
* **Problem**: `EvaluationResult.pii_types` was declared as `List[str] = []`, which is a mutable default value incompatible with Pydantic v2's validation model.
* **Fix**: Replaced with Pydantic's safe default factory declaration: `Field(default_factory=list)`.

### 3. Ollama Model Response Attribute Access
* **Problem**: The Ollama integration crashed at runtime because it attempted dictionary-style access (`resp["message"]["content"]`) on the Ollama API client response, which is a typed object.
* **Fix**: Refactored Ollama response parsing to use attribute-style access: `resp.message.content`.

### 4. Gemini Model Resilience
* **Problem**: Unlike cloud model adapters for OpenAI and Anthropic, the `GeminiModel` lacked retry logic, causing it to fail immediately on transient network hiccups or rate limits.
* **Fix**: Decorated `GeminiModel.call` with the `@retry` decorator configured with exponential backoff.

### 5. Path Resolvers and File Encodings
* **Problem**: Logging to `evaluation.log` defaulted to the process's current working directory instead of a fixed, consistent location. Additionally, opening text files on Windows occasionally raised encoding errors.
* **Fix**:
  - Anchored `evaluation.log` to an absolute path at the project root.
  - Added explicit `encoding="utf-8"` arguments to all file `open` operations.

---

## 🐛 Critical Fixes in Version 2.0.1

### 1. Duplicate Dependencies Resolved
* **Problem**: `requirements.txt` contained duplicates of core testing and utility packages (e.g., `tenacity`, `pytest`, `pytest-mock`, `pyyaml`).
* **Fix**: Consolidated the dependencies, and later aligned everything into `pyproject.toml` as the single source of truth.

### 2. Empty Test Directory Handling
* **Problem**: Executing evaluations when the `test_cases` directory was empty triggered unhandled execution crashes.
* **Fix**: Added an early-exit check that logs warning messages and alerts the user gracefully.

### 3. Score Clamping
* **Problem**: Occasionally, LLM judges returned scores outside the expected `0.0 - 1.0` range (e.g., `1.5` or `-0.5`).
* **Fix**: Implemented score clamping to guarantee all scores stay strictly in the valid range of `[0.0, 1.0]`.

---

## 📈 Summary of Documentation and Architectural Changes

- **Version 1.0.0**: Basic LLM-as-a-Judge and initial CLI progress metrics.
- **Version 2.0.0**: Architectural overhaul isolating models to `models.py` and centralizing configurations into `config.yaml`.
- **Version 2.1.0**: Python packaging conversion, adding console entry scripts (`run-evaluation`, `view-dashboard`).
- **Version 2.1.6**: Suppressed pricing config warning for `default` simulated model name, synchronized package and documentation version strings to 2.1.6.
- **Version 2.1.5**: Version synchronization, brace JSON parsing, lazy-loaded dashboard, robust testing, and optimized docker builds.
