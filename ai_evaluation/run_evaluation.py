#!/usr/bin/env python3
"""
AI Model Evaluation Script

This script runs test cases against AI models and saves the results.
It supports multiple AI providers and can be extended for custom models.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AIEvaluator:
    """Main class for evaluating AI models with test cases."""
    
    def __init__(self, test_cases_dir: str = "test_cases", 
                 results_dir: str = "results"):
        """
        Initialize the evaluator.
        
        Args:
            test_cases_dir: Directory containing test case files
            results_dir: Directory to save evaluation results
        """
        self.test_cases_dir = Path(test_cases_dir)
        self.results_dir = Path(results_dir)
        
        # Create directories if they don't exist
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration from environment
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.timeout = int(os.getenv("TIMEOUT_SECONDS", "60"))
        
    def load_test_cases(self) -> List[Dict[str, str]]:
        """
        Load all test cases from the test_cases directory.
        
        Returns:
            List of dictionaries containing test case information
        """
        test_cases = []
        
        if not self.test_cases_dir.exists():
            print(f"Warning: Test cases directory '{self.test_cases_dir}' not found")
            return test_cases
        
        for file_path in self.test_cases_dir.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                test_cases.append({
                    "name": file_path.stem,
                    "content": content,
                    "file_path": str(file_path)
                })
                print(f"Loaded test case: {file_path.name}")
            except Exception as e:
                print(f"Error loading {file_path.name}: {e}")
        
        return test_cases
    
    def simulate_ai_response(self, test_case: str) -> str:
        """
        Simulate an AI model's response to a test case.
        
        In production, this would call actual AI model APIs.
        Replace this with real API calls to OpenAI, Anthropic, etc.
        
        Args:
            test_case: The test case content
            
        Returns:
            Simulated AI response
        """
        # This is a placeholder. Replace with actual API calls:
        # - OpenAI: openai.ChatCompletion.create()
        # - Anthropic: anthropic.messages.create()
        # - etc.
        
        return (
            f"[SIMULATED RESPONSE]\n\n"
            f"This is a simulated response for testing purposes.\n"
            f"In production, this would be replaced with an actual AI model response.\n\n"
            f"Test case received with {len(test_case)} characters."
        )
    
    def call_openai(self, test_case: str, model: str = "gpt-4") -> Optional[str]:
        """
        Call OpenAI API with a test case.
        
        Args:
            test_case: The test case content
            model: OpenAI model to use
            
        Returns:
            Model response or None if error
        """
        try:
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY")
            
            if not openai.api_key:
                print("Warning: OPENAI_API_KEY not set")
                return None
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": test_case}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout
            )
            
            return response.choices[0].message.content
            
        except ImportError:
            print("OpenAI library not installed. Install with: pip install openai")
            return None
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None
    
    def call_anthropic(self, test_case: str, 
                       model: str = "claude-sonnet-4-20250514") -> Optional[str]:
        """
        Call Anthropic API with a test case.
        
        Args:
            test_case: The test case content
            model: Anthropic model to use
            
        Returns:
            Model response or None if error
        """
        try:
            import anthropic
            
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("Warning: ANTHROPIC_API_KEY not set")
                return None
            
            client = anthropic.Anthropic(api_key=api_key)
            
            message = client.messages.create(
                model=model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": test_case}]
            )
            
            return message.content[0].text
            
        except ImportError:
            print("Anthropic library not installed. Install with: pip install anthropic")
            return None
        except Exception as e:
            print(f"Error calling Anthropic API: {e}")
            return None
    
    def save_result(self, test_case_name: str, test_case_content: str, 
                    response: str, metadata: Optional[Dict] = None) -> str:
        """
        Save evaluation result to a JSON file.
        
        Args:
            test_case_name: Name of the test case
            test_case_content: Original test case content
            response: AI model's response
            metadata: Additional metadata to include
            
        Returns:
            Path to the saved result file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_filename = f"{test_case_name}_{timestamp}.json"
        result_path = self.results_dir / result_filename
        
        result_data = {
            "test_case_name": test_case_name,
            "timestamp": datetime.now().isoformat(),
            "test_case": test_case_content,
            "response": response,
            "metadata": metadata or {}
        }
        
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"Result saved: {result_path}")
        return str(result_path)
    
    def run_evaluation(self, model_type: str = "simulated") -> None:
        """
        Run evaluation on all test cases.
        
        Args:
            model_type: Type of model to evaluate ("simulated", "openai", "anthropic")
        """
        print(f"\n{'='*60}")
        print(f"Starting AI Model Evaluation - {model_type.upper()}")
        print(f"{'='*60}\n")
        
        test_cases = self.load_test_cases()
        
        if not test_cases:
            print("No test cases found. Please add test cases to the test_cases directory.")
            return
        
        print(f"Found {len(test_cases)} test case(s)\n")
        
        for idx, test_case in enumerate(test_cases, 1):
            print(f"\n[{idx}/{len(test_cases)}] Processing: {test_case['name']}")
            print("-" * 60)
            
            # Get response based on model type
            if model_type == "openai":
                response = self.call_openai(test_case['content'])
            elif model_type == "anthropic":
                response = self.call_anthropic(test_case['content'])
            else:
                response = self.simulate_ai_response(test_case['content'])
            
            if response is None:
                response = "[ERROR] Failed to get response from model"
            
            # Save result
            metadata = {
                "model_type": model_type,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            self.save_result(
                test_case['name'],
                test_case['content'],
                response,
                metadata
            )
            
            # Small delay to avoid rate limiting
            time.sleep(1)
        
        print(f"\n{'='*60}")
        print(f"Evaluation Complete! Results saved to: {self.results_dir}")
        print(f"{'='*60}\n")


def main():
    """Main entry point for the evaluation script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run AI model evaluation with test cases"
    )
    parser.add_argument(
        "--model",
        choices=["simulated", "openai", "anthropic"],
        default="simulated",
        help="Model type to evaluate (default: simulated)"
    )
    parser.add_argument(
        "--test-cases-dir",
        default="test_cases",
        help="Directory containing test cases (default: test_cases)"
    )
    parser.add_argument(
        "--results-dir",
        default="results",
        help="Directory to save results (default: results)"
    )
    
    args = parser.parse_args()
    
    evaluator = AIEvaluator(
        test_cases_dir=args.test_cases_dir,
        results_dir=args.results_dir
    )
    
    evaluator.run_evaluation(model_type=args.model)


if __name__ == "__main__":
    main()
