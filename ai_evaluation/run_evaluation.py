import datetime
import yaml
import json
import csv
from pathlib import Path


class AIEvaluator:
    def __init__(self, config_path="config.yaml", test_cases_dir="test_cases", results_dir="results"):
        """
        Initialize the AI Evaluator.

        Args:
            config_path (str|Path): Path to the configuration file.
            test_cases_dir (str|Path): Directory containing test cases.
            results_dir (str|Path): Directory to save results.
        """
        self.config_path = config_path
        self.test_cases_dir = Path(test_cases_dir)
        self.results_dir = Path(results_dir)
        self.results = []

        self.config = self._load_config(self.config_path)

        # Ensure results directory exists
        if not self.results_dir.exists():
            self.results_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path):
        """Load configuration from YAML file."""
        path = Path(config_path)
        if not path.is_absolute():
            # Try finding it relative to the script if not found in cwd
            script_dir = Path(__file__).parent
            potential_path = script_dir / config_path
            if potential_path.exists():
                path = potential_path

        if path.exists():
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        return {}

    def evaluate_model(self, prompt, model_type="simulated"):
        """
        Simulate or perform code evaluation.
        """
        if model_type == "simulated":
            return "This is a simulated response from the AI model."

        # Future implementation for OpenAI/Anthropic could go here
        # utilizing self.config for api keys/params
        return f"Response from {model_type} not implemented."

    def run_evaluation(self, model_type="simulated"):
        """
        Run evaluation on all test cases in the test_cases directory.
        """
        self.results = []  # Reset results

        if not self.test_cases_dir.exists():
            print(f"Directory not found: {self.test_cases_dir}")
            return

        for test_case_path in self.test_cases_dir.glob("*"):
            if test_case_path.is_file():
                try:
                    with open(test_case_path, 'r', encoding='utf-8') as f:
                        test_case_content = f.read()
                except UnicodeDecodeError:
                    print(f"Skipping {test_case_path.name}: not a text file.")
                    continue

                response = self.evaluate_model(test_case_content, model_type)

                result = {
                    "test_case_name": test_case_path.stem,
                    "prompt": test_case_content,
                    "response": response,
                    "metadata": {
                        "model_type": model_type,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                }
                self.results.append(result)

                # Save individual result file (legacy behavior)
                timestamp_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                result_filename = f"result_{test_case_path.stem}_{timestamp_str}.txt"
                result_path = self.results_dir / result_filename

                try:
                    with open(result_path, 'w', encoding='utf-8') as f:
                        f.write("--- Test Case ---\n")
                        f.write(test_case_content)
                        f.write("\n\n--- AI Model Output ---\n")
                        f.write(response)
                    print(f"Result for {test_case_path.name} saved to {result_path}")
                except Exception as e:
                    print(f"Failed to save result for {test_case_path.name}: {e}")

    def export_results(self, format="json"):
        """
        Export results to JSON or CSV.

        Args:
            format (str): 'json' or 'csv'

        Returns:
            str: Path to the exported file.
        """
        timestamp_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        if format == "json":
            filename = f"results_export_{timestamp_str}.json"
            filepath = self.results_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2)
            return str(filepath)

        elif format == "csv":
            filename = f"results_export_{timestamp_str}.csv"
            filepath = self.results_dir / filename

            if not self.results:
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    pass  # Empty file
                return str(filepath)

            # Flatten data for CSV
            csv_data = []
            for r in self.results:
                row = {
                    "test_case_name": r["test_case_name"],
                    "prompt": r["prompt"],
                    "response": r["response"],
                    "model_type": r["metadata"]["model_type"],
                    "timestamp": r["metadata"]["timestamp"]
                }
                csv_data.append(row)

            fieldnames = csv_data[0].keys()
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
            return str(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run AI Evaluation")
    parser.add_argument("--model", default="simulated", help="Model type to evaluate (simulated, openai, anthropic)")
    args = parser.parse_args()

    # Resolve paths relative to the script location
    script_dir = Path(__file__).parent

    config_path = script_dir / "config.yaml"
    test_cases_dir = script_dir / "test_cases"
    results_dir = script_dir / "results"

    evaluator = AIEvaluator(
        config_path=config_path,
        test_cases_dir=test_cases_dir,
        results_dir=results_dir
    )

    print(f"Running evaluation with model: {args.model}")
    evaluator.run_evaluation(model_type=args.model)

    export_path = evaluator.export_results("json")
    print(f"Results exported to: {export_path}")
