# AI-Testing

**Version: 1.3**

A comprehensive repository containing test cases and evaluation frameworks for assessing various AI models' performance, capabilities, and limitations.

## Overview

This repository provides a structured approach to AI model evaluation through:
- Standardized test cases covering different AI capabilities
- Automated evaluation pipeline with a keyword-based scoring system
- Result tracking and comparison across models

## AI Evaluation Framework

The evaluation framework is located in the `ai_evaluation` directory and consists of the following components:

### Directory Structure

```
ai_evaluation/
├── test_cases/        # Test case definitions in YAML format
├── results/           # Evaluation outputs and metrics (auto-generated, gitignored)
├── config.yaml        # Configuration for the evaluation script
└── run_evaluation.py  # Main evaluation script
```

### Components

- **`test_cases/`**: Contains YAML test case files for evaluating AI models. Each test case includes a `prompt` and a list of `expected_keywords` for automated scoring.

- **`results/`**: Stores evaluation results with timestamps. This directory is created automatically. Each result file includes the original test case, the model's response, the calculated score, and other metadata.

- **`config.yaml`**: Configuration file for the evaluation script. It allows you to set parameters like `max_tokens`, `temperature`, and API timeouts.

- **`run_evaluation.py`**: The main evaluation script that reads test cases, interfaces with AI models, scores the responses, and saves the results.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required dependencies (install via `pip install -r requirements.txt`)

### Usage

1. **Add Test Cases**
   
   Create new YAML files in the `ai_evaluation/test_cases` directory. Each file should have the following structure:
   ```yaml
   prompt: "Your test prompt here. For example, what is the capital of France?"
   expected_keywords:
     - "Paris"
   ```

2. **Run the Evaluation**
   
   Navigate to the `ai_evaluation` directory and execute:
   ```bash
   cd ai_evaluation
   python3 run_evaluation.py
   ```

   To export all results to a single file, use the `--export-format` argument:
   ```bash
   python3 run_evaluation.py --export-format csv
   ```
   This will create an `export_YYYYMMDD_HHMMSS.csv` file in the `results` directory.

3. **View Results**
   
   Evaluation results, including the score, are saved in `ai_evaluation/results/` in JSON format.

## Test Case Guidelines

When creating test cases:
- Use clear and unambiguous instructions in the `prompt`.
- Provide a list of `expected_keywords` that are likely to appear in a correct response. The more comprehensive the list, the more accurate the score.
- Consider edge cases, safety, and ethical considerations.

## Contributing

Contributions are welcome! To add new test cases or improve the framework:
1. Fork the repository
2. Create a feature branch
3. Add your test cases or improvements
4. Submit a pull request with a clear description

## Roadmap

Potential future enhancements:
- [ ] Support for multiple AI model APIs (OpenAI, Anthropic, etc.)
- [x] Automated scoring and comparison metrics (keyword-based implemented)
- [ ] Web interface for viewing results
- [ ] Batch evaluation capabilities
- [x] Export results to CSV/JSON for analysis

## License

MIT

## Contact

For questions or suggestions, please open an issue in this repository.
