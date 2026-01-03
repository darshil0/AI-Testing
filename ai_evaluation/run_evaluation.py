import datetime
import json
import csv
import logging
import time
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import yaml
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Optional imports for real models
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv("LOG_FILE", "evaluation.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AIEvaluator:
    def __init__(self, config_path="config.yaml", test_cases_dir="test_cases", results_dir="results"):
        """
        Initialize the AI Evaluator.
        """
        self.config_path = config_path
        self.test_cases_dir = Path(test_cases_dir)
        self.results_dir = Path(results_dir)
        self.results = []

        self.config = self._load_config(self.config_path)

        # Clients initialization
        self.openai_client = None
        self.anthropic_client = None

        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Ensure results directory exists
        if not self.results_dir.exists():
            self.results_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path):
        """Load configuration from YAML file."""
        path = Path(config_path)
        if not path.is_absolute():
            script_dir = Path(__file__).parent
            potential_path = script_dir / config_path
            if potential_path.exists():
                path = potential_path

        if path.exists():
            try:
                with open(path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.error(f"Failed to load config at {path}: {e}")
        return {}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_openai(self, prompt):
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized. Check API key.")
        
        response = self.openai_client.chat.completions.create(
            model=self.config.get("openai_model", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.config.get("max_tokens", 2000),
            temperature=self.config.get("temperature", 0.7)
        )
        return response.choices[0].message.content

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_anthropic(self, prompt):
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized. Check API key.")
        
        response = self.anthropic_client.messages.create(
            model=self.config.get("anthropic_model", "claude-3-opus-20240229"),
            max_tokens=self.config.get("max_tokens", 2000),
            temperature=self.config.get("temperature", 0.7),
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    def evaluate_model(self, prompt, model_type="simulated"):
        """
        Perform model evaluation using the specified provider.
        """
        try:
            if model_type == "simulated":
                return "This is a simulated response from the AI model."
            elif model_type == "openai":
                return self._call_openai(prompt)
            elif model_type == "anthropic":
                return self._call_anthropic(prompt)
            else:
                return f"Response from {model_type} not implemented."
        except Exception as e:
            logger.error(f"Error calling {model_type}: {e}")
            return f"Error: {str(e)}"

    def _process_test_case(self, test_case_path, model_type):
        """Internal helper to process a single test case (for threading)."""
        if not test_case_path.is_file():
            return None

        try:
            with open(test_case_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract headers if present (Legacy support)
            lines = content.split('\n')
            category = "General"
            difficulty = "Medium"
            prompt_content = content
            
            for line in lines[:5]:
                if line.lower().startswith("category:"):
                    category = line.split(":", 1)[1].strip()
                elif line.lower().startswith("difficulty:"):
                    difficulty = line.split(":", 1)[1].strip()

            logger.info(f"Evaluating {test_case_path.name} with {model_type}...")
            
            start_time = time.time()
            response = self.evaluate_model(content, model_type)
            duration = time.time() - start_time

            result = {
                "test_case_name": test_case_path.stem,
                "category": category,
                "difficulty": difficulty,
                "prompt": content,
                "response": response,
                "metadata": {
                    "model_type": model_type,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "duration_seconds": round(duration, 2)
                }
            }
            
            # Simple scoring (place holder for more complex logic)
            # In a real tool, this would be LLM-based or exact match
            result["score"] = 1.0 if "error" not in response.lower() else 0.0

            # Save individual text result
            self._save_individual_result(test_case_path.stem, content, response)
            
            return result
        except Exception as e:
            logger.error(f"Failed to process {test_case_path.name}: {e}")
            return None

    def _save_individual_result(self, name, prompt, response):
        timestamp_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        result_filename = f"result_{name}_{timestamp_str}.txt"
        result_path = self.results_dir / result_filename
        try:
            with open(result_path, 'w', encoding='utf-8') as f:
                f.write(f"--- Test Case: {name} ---\n")
                f.write(prompt)
                f.write("\n\n--- AI Model Output ---\n")
                f.write(response)
        except Exception as e:
            logger.error(f"Failed to save result file for {name}: {e}")

    def run_evaluation(self, model_type="simulated", parallel=True):
        """
        Run evaluation on all test cases in the test_cases directory.
        """
        self.results = []
        
        if not self.test_cases_dir.exists():
            logger.error(f"Directory not found: {self.test_cases_dir}")
            return

        test_case_paths = list(self.test_cases_dir.glob("*.txt"))
        
        if parallel and len(test_case_paths) > 1:
            logger.info(f"Running {len(test_case_paths)} test cases in parallel...")
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(self._process_test_case, p, model_type) for p in test_case_paths]
                for future in futures:
                    res = future.result()
                    if res:
                        self.results.append(res)
        else:
            for path in test_case_paths:
                res = self._process_test_case(path, model_type)
                if res:
                    self.results.append(res)

        logger.info(f"Evaluation complete. Processed {len(self.results)} cases.")

    def export_results(self, format="json"):
        """
        Export results to JSON or CSV.
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
                    pass
                return str(filepath)
            
            csv_data = []
            for r in self.results:
                row = {
                    "test_case_name": r["test_case_name"],
                    "category": r.get("category", "N/A"),
                    "difficulty": r.get("difficulty", "N/A"),
                    "response": r["response"][:100] + "...", # Truncate for CSV
                    "model_type": r["metadata"]["model_type"],
                    "duration": r["metadata"]["duration_seconds"],
                    "score": r.get("score", 0.0),
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
    
    parser = argparse.ArgumentParser(description="Run AI Evaluation Batch")
    parser.add_argument("--model", default="simulated", help="Model: simulated, openai, anthropic")
    parser.add_argument("--sequential", action="store_true", help="Disable parallel execution")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    
    evaluator = AIEvaluator(
        config_path=script_dir / "config.yaml",
        test_cases_dir=script_dir / "test_cases",
        results_dir=script_dir / "results"
    )
    
    logger.info(f"--- Starting Evaluation (Model: {args.model}) ---")
    evaluator.run_evaluation(model_type=args.model, parallel=not args.sequential)
    
    json_path = evaluator.export_results("json")
    csv_path = evaluator.export_results("csv")
    
    logger.info(f"Results exported to:\n - {json_path}\n - {csv_path}")
