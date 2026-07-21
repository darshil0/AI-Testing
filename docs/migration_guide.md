# Migration Guide: Upgrading to AI-Testing Version 2.1.7

## Introduction
This guide provides instructions and details for upgrading your AI-Testing environment from previous legacy releases (such as `v2.0.0` or `v2.1.0`) to the latest enterprise-ready **Version 2.1.7**.

---

## ⚡ Quick Upgrade Checklist

If you are an existing user looking to upgrade quickly, run the following commands in your terminal:

```bash
# 1. Pull the latest repository updates
git pull origin main

# 2. Activate your virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Perform an editable installation of the package along with developer tools
pip install -e ".[dev]"

# 4. Clear any cached test outputs (Optional but recommended)
rm -rf .pytest_cache/

# 5. Run unit tests to verify installation
python -m pytest
```

---

## 🚀 Key Evolutionary Milestones (What's New in v2.1.7)

### 1. Unified Packaging & Console Scripts
* **Legacy Behavior**: Invocations required executing scripts directly by path (e.g., `python ai_evaluation/run_evaluation.py`).
* **Modern Behavior**: The project is structured as a compliant Python package defined in `pyproject.toml`.
  - Run evaluations globally via the entry point command: **`run-evaluation`**
  - Launch the web dashboard globally via: **`view-dashboard`**
  - Alternatively, execute the modules directly as packages:
    ```bash
    python -m ai_evaluation
    python -m ai_evaluation.dashboard
    ```

### 2. Export Format Options
You can now consolidate your run output files into a single unified output using the `--export-format` command-line flag:
```bash
# Export consolidated results as a CSV spreadsheet
run-evaluation --models simulated:default --export-format csv

# Export consolidated results as a structured JSON file
run-evaluation --models simulated:default --export-format json
```

### 3. Streamlit Lazy Loading
Previously, running any evaluation or test on a machine without the Streamlit library installed resulted in immediate crashes during package import. In Version 2.1.7, Streamlit is lazily loaded upon execution of `view-dashboard`. Standard evaluation commands run flawlessly even in minimalist environments without Streamlit.

---

## 💻 Code and CLI Invocation Comparison

| Feature / Action | Legacy Syntax (v2.0.0) | Modern Syntax (v2.1.7) |
| :--- | :--- | :--- |
| **Local Installation** | `pip install -r requirements.txt` | `pip install -e .` or `pip install -e ".[dev]"` |
| **Run Default Simulated Suite** | `python run_evaluation.py --models simulated:default` | `run-evaluation --models simulated:default` |
| **Run Module directly** | `python -m ai_evaluation.run_evaluation` | `python -m ai_evaluation` |
| **Start Streamlit Dashboard** | `streamlit run dashboard.py` | `view-dashboard` |
| **Debugging (Sequential Mode)** | *Not Supported* | `run-evaluation --models simulated:default --sequential` |
| **Export Results Formats** | *JSON files only* | `--export-format json` or `--export-format csv` |

---

## 🛠️ Model Prefix Reference Sheet

Ensure your model arguments match the required `provider:model_name` syntax:

* **Simulated**: `simulated:default` (Requires no API keys or internet connection)
* **OpenAI**: `openai:gpt-4o` or `openai:gpt-3.5-turbo`
* **Anthropic**: `anthropic:claude-3-5-sonnet-20241022` or `anthropic:claude-3-opus-20240229`
* **Google**: `gemini:gemini-1.5-pro`
* **Ollama**: `ollama:llama3` or `ollama:mistral`

---

## ⚙️ Configuration & Test Case Compatibility

### 1. Config.yaml Settings
Your existing `config.yaml` file remains **100% backward compatible**. The evaluator now resolves the test cases and results paths relative to the configuration file's parent folder. Ensure your paths in `config.yaml` are clean:

```yaml
directories:
  test_cases: "test_cases"
  results: "results"
```

### 2. Test Cases Extensions
The evaluation suite now supports `.yml` alongside `.yaml` and `.txt`.
```bash
# You can use any of these filenames inside the test_cases directory:
code_optimization.yaml
data_cleaning.yml
factual_accuracy.txt
```

---

## 🩺 Troubleshooting Upgrade Hurdles

### Issue 1: `ModuleNotFoundError: No module named 'yaml'` or `run-evaluation: command not found`
* **Cause**: Your Python environment does not have the package installed editably, or you are running in a shell where the virtual environment is inactive.
* **Resolution**:
  ```bash
  source venv/bin/activate
  pip install -e .
  ```

### Issue 2: Streamlit Dashboard Crashes on Interrupted Runs
* **Cause**: Interrupted runs can sometimes write empty or incomplete JSON runs to your results folder.
* **Resolution**: In Version 2.1.7, the dashboard is resilient and ignores corrupted files. If you are on an older version, remove any empty or corrupted files in your results directory:
  ```bash
  find ai_evaluation/results/ -size 0 -delete
  ```

### Issue 3: Duplicate Package Warnings in Older Environments
* **Cause**: Leftover packages from old `requirements.txt` runs.
* **Resolution**: Recreate a clean virtual environment:
  ```bash
  deactivate
  rm -rf venv/
  python3 -m venv venv
  source venv/bin/activate
  pip install -e ".[dev]"
  ```
