import os
import datetime

def evaluate_model(test_case_content):
    """
    Simulates an AI model evaluation.
    In a real-world scenario, this function would interact with an AI model.
    For this example, it returns a more realistic response based on the test case.
    """
    if "capital of France" in test_case_content:
        return "Paris is the capital of France."
    elif "factorial" in test_case_content:
        return """
def factorial(n):
    \"\"\"Calculates the factorial of a non-negative integer.\"\"\"
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
"""
    elif "Summarize" in test_case_content:
        return "A quick brown fox jumps over a lazy dog."
    else:
        return "This is a simulated response from the AI model."

def run_evaluation():
    """
    Reads test cases, runs the evaluation, and saves the results.
    """
    test_cases_dir = 'test_cases'
    results_dir = 'results'

    if not os.path.exists(test_cases_dir):
        print(f"Directory not found: {test_cases_dir}")
        return

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    for filename in os.listdir(test_cases_dir):
        test_case_path = os.path.join(test_cases_dir, filename)
        if os.path.isfile(test_case_path):
            with open(test_case_path, 'r') as f:
                test_case_content = f.read()

            model_output = evaluate_model(test_case_content)

            result_filename = f"result_{os.path.splitext(filename)[0]}.txt"
            result_path = os.path.join(results_dir, result_filename)

            with open(result_path, 'w') as f:
                f.write("--- Test Case ---\n")
                f.write(test_case_content)
                f.write("\n\n--- AI Model Output ---\n")
                f.write(model_output)

            print(f"Result for {filename} saved to {result_path}")

if __name__ == "__main__":
    run_evaluation()
