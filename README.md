# AI-Testing

A comprehensive repository for evaluating AI models using a structured testing framework. This project includes a standardized test suite, an extensible evaluation script, and tools for analyzing model performance.

## 🚀 Features

- **Multi-Model Support**: interface for OpenAI, Anthropic, and simulated models.
- **Standardized Test Cases**: categorized by domain (Reasoning, Creativity, Coding, etc.) and difficulty.
- **Flexible Reporting**: Export results to JSON or CSV formats.
- **Robustness**: Typesafe implementation with unit tests and linting.

## 📋 Prerequisites

- Python 3.8+
- pip (Python package installer)

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/darshil0/AI-Testing.git
    cd AI-Testing
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    - Copy `.env.example` to `.env`.
    - Add your API keys (OpenAI, Anthropic) if you intend to use real models.
    ```bash
    cp .env.example .env
    ```

## 💻 Usage

The core evaluation script can be run from the command line.

### Basic Run (Simulated Mode)
Runs evaluation using a mock responder (no API keys required).
```bash
python ai_evaluation/run_evaluation.py
```

### Specify Model
Choose between `simulated`, `openai`, or `anthropic`.
```bash
python ai_evaluation/run_evaluation.py --model openai
```

*(Note: Real model usage requires valid API keys in `.env`)*

### Output
Results are saved to `ai_evaluation/results/` in both JSON and text formats.

## 🧪 Development

### Running Tests
This project uses `pytest` for unit testing.
```bash
pytest
```

### Linting
Ensure code quality with `flake8`.
```bash
flake8 .
```

## 📝 Creating Test Cases

Test cases are located in `ai_evaluation/test_cases/`. To add a new test:

1. Create a `.txt` file.
2. Add metadata headers (`Category`, `Difficulty`).
3. Add your prompt.

**Example:**
```text
Category: Reasoning
Difficulty: Hard

Explain the relationship between quantum mechanics and general relativity.
```

## 📄 License

This project is licensed under the MIT License. See `LICENSE` for details.
