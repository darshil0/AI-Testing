# AI-Testing
This is a repository containing all the testcases for Evaluating the various AI Models.

## AI Evaluation Framework

This repository includes a simple framework for evaluating AI models. The framework is located in the `ai_evaluation` directory and consists of the following components:

- `test_cases/`: A directory containing test cases for the AI models. Each test case is a text file with instructions for the model.
- `results/`: A directory where the evaluation results are stored. Each result file contains the original test case and the model's output.
- `run_evaluation.py`: A Python script that runs the evaluation. It reads the test cases, simulates an AI model's response, and saves the results to the `results` directory.

### How to Use

1.  **Add Test Cases:** Create new text files in the `ai_evaluation/test_cases` directory. Each file should contain a specific test case for the AI model.

2.  **Run the Evaluation:** Navigate to the `ai_evaluation` directory and run the following command:

    ```bash
    python3 run_evaluation.py
    ```

3.  **View the Results:** The evaluation results will be saved in the `ai_evaluation/results` directory. Each result file will be named with the original test case name and a timestamp.
