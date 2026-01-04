import datetime
import json
import logging
import time
import os
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Rich UI imports
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table

# Local imports
from .models import get_model

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(rich_tracebacks=True),
        logging.FileHandler("evaluation.log"),
    ],
)
logger = logging.getLogger("rich")
console = Console()


class TestCase(BaseModel):
    name: str
    category: str = "General"
    difficulty: str = "Medium"
    prompt: str
    expectations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvaluationResult(BaseModel):
    test_case_name: str
    category: str
    difficulty: str
    model_type: str
    prompt: str
    response: str
    duration_seconds: float
    tokens_input: int = 0
    tokens_output: int = 0
    estimated_cost: float = 0.0
    judge_score: float = 0.0
    judge_reasoning: str = ""
    pii_found: bool = False
    pii_types: List[str] = []
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())


class AIEvaluator:
    def __init__(self, config_path="ai_evaluation/config.yaml"):
        # Handle relative paths from project root
        if not Path(config_path).exists():
            alt_path = Path(__file__).parent / "config.yaml"
            if alt_path.exists():
                config_path = str(alt_path)
            else:
                raise FileNotFoundError(f"Config file not found at {config_path}")

        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Resolve paths relative to config location
        config_dir = Path(config_path).parent

        self.test_cases_dir = Path(self.config["directories"]["test_cases"])
        if not self.test_cases_dir.is_absolute():
            self.test_cases_dir = config_dir / self.test_cases_dir

        self.results_dir = Path(self.config["directories"]["results"])
        if not self.results_dir.is_absolute():
            self.results_dir = config_dir / self.results_dir

        self.results: List[EvaluationResult] = []

        # Ensure directories exist
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.test_cases_dir.mkdir(parents=True, exist_ok=True)

    def load_from_hf(self, dataset_name: str, split: str = "test", count: int = 5):
        """Load test cases from HuggingFace datasets."""
        try:
            from datasets import load_dataset

            ds = load_dataset(dataset_name, split=split, streaming=True)
            logger.info(f"Loading {count} cases from HF: {dataset_name}")
            for i, item in enumerate(ds.take(count)):
                prompt = item.get("question") or item.get("prompt") or item.get("text")
                if prompt:
                    path = (
                        self.test_cases_dir
                        / f"hf_{dataset_name.replace('/', '_')}_{i}.txt"
                    )
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(f"Category: HuggingFace\nDifficulty: Auto\n\n{prompt}")
            logger.info(f"Successfully loaded {count} test cases from {dataset_name}")
        except ImportError:
            logger.error(
                "HuggingFace 'datasets' not installed. Install with: pip install datasets"
            )
        except Exception as e:
            logger.error(f"HF Load failed: {e}")

    def _pii_scan(self, text: str) -> Tuple[bool, List[str]]:
        """Simple regex-based PII scanner."""
        found_types = []
        for p_type, pattern in self.config.get("pii_patterns", {}).items():
            try:
                if re.search(pattern, text):
                    found_types.append(p_type)
            except re.error as e:
                logger.warning(f"Invalid regex pattern for {p_type}: {e}")
        return len(found_types) > 0, found_types

    def judge_response(
        self, test_case: TestCase, response: str, persona: str = "default"
    ) -> Tuple[float, str]:
        """Judge a model response using an LLM judge."""
        judge_model_id = self.config["judge"]["model"]
        persona_prompt = self.config["judge_personas"].get(
            persona, self.config["judge_personas"]["default"]
        )

        try:
            judge_model = get_model(judge_model_id, self.config)
        except ValueError as e:
            logger.warning(f"Judge model error: {e}")
            return 0.0, f"Judge model error: {e}"

        criteria = (
            ", ".join(test_case.expectations)
            if test_case.expectations
            else "overall quality"
        )

        prompt = f"""{persona_prompt}

Rate the following response on a scale of 0.0-1.0 based on: {criteria}

Return your evaluation as JSON in this exact format:
{{"score": <float between 0.0 and 1.0>, "reasoning": "<your explanation>"}}

ORIGINAL PROMPT: {test_case.prompt}

MODEL RESPONSE: {response}"""

        try:
            raw, _, _ = judge_model.call(prompt)
            # Try to extract JSON from the response
            match = re.search(r'\{[^}]*"score"[^}]*\}', raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
                score = float(data.get("score", 0.0))
                # Clamp score to valid range
                score = max(0.0, min(1.0, score))
                reasoning = data.get("reasoning", "")
                return score, reasoning
            else:
                logger.warning(
                    f"Judge response did not contain valid JSON: {raw[:100]}"
                )
                return 0.5, "Could not parse judge response"
        except json.JSONDecodeError as e:
            logger.error(f"Judge returned invalid JSON: {e}")
            return 0.0, "Judge returned invalid JSON"
        except Exception as e:
            logger.error(f"Judging failed: {e}")
            return 0.0, f"Judging error: {str(e)}"

    def _parse_test_case(self, file_path: Path) -> TestCase:
        """Parse a test case from a file."""
        try:
            if file_path.suffix == ".yaml":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    return TestCase(name=file_path.stem, **data)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse headers
            category_match = re.search(r"Category:\s*(.*)", content, re.IGNORECASE)
            difficulty_match = re.search(r"Difficulty:\s*(.*)", content, re.IGNORECASE)

            category = category_match.group(1).strip() if category_match else "General"
            difficulty = (
                difficulty_match.group(1).strip() if difficulty_match else "Medium"
            )

            return TestCase(
                name=file_path.stem,
                category=category,
                difficulty=difficulty,
                prompt=content.strip(),
            )
        except Exception as e:
            logger.error(f"Error parsing test case {file_path}: {e}")
            # Return a minimal valid test case
            return TestCase(
                name=file_path.stem,
                category="Error",
                difficulty="Unknown",
                prompt=f"Error parsing test case: {e}",
            )

    def process_one(
        self, file_path: Path, model_id: str, persona: str = "default"
    ) -> EvaluationResult:
        """Process a single test case with a given model."""
        tc = self._parse_test_case(file_path)
        start_time = time.time()

        try:
            model = get_model(model_id, self.config)
            response, input_tokens, output_tokens = model.call(tc.prompt)

            duration = time.time() - start_time
            cost = model._calculate_cost(input_tokens, output_tokens)
            pii_found, pii_types = self._pii_scan(response)
            score, reason = self.judge_response(tc, response, persona)

            return EvaluationResult(
                test_case_name=tc.name,
                category=tc.category,
                difficulty=tc.difficulty,
                model_type=model_id,
                prompt=tc.prompt,
                response=response,
                duration_seconds=round(duration, 2),
                tokens_input=input_tokens,
                tokens_output=output_tokens,
                estimated_cost=round(cost, 6),
                judge_score=round(score, 3),
                judge_reasoning=reason,
                pii_found=pii_found,
                pii_types=pii_types,
            )
        except Exception as e:
            logger.error(f"Error processing {tc.name} with {model_id}: {e}")
            return EvaluationResult(
                test_case_name=tc.name,
                category=tc.category,
                difficulty=tc.difficulty,
                model_type=model_id,
                prompt=tc.prompt,
                response=f"Error: {str(e)}",
                duration_seconds=0,
                judge_score=0.0,
                judge_reasoning=f"Fatal error during processing: {str(e)}",
            )

    def run_suite(
        self, model_ids: List[str], persona: str = "default", parallel: bool = True
    ):
        """Run evaluation suite across all test cases and models."""
        files = list(self.test_cases_dir.glob("*.txt")) + list(
            self.test_cases_dir.glob("*.yaml")
        )

        if not files:
            logger.warning(f"No test cases found in {self.test_cases_dir}")
            console.print(
                "[yellow]⚠ No test cases found. Add .txt or .yaml files to test_cases directory.[/]"
            )
            return

        tasks = [(file, model_id, persona) for file in files for model_id in model_ids]

        console.print(
            f"[cyan]Found {len(files)} test cases, running with {len(model_ids)} model(s)[/]"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            main_task = progress.add_task("[cyan]Evaluating...", total=len(tasks))

            def runner(task_data):
                result = self.process_one(*task_data)
                progress.advance(main_task)
                return result

            if parallel and len(tasks) > 1:
                with ThreadPoolExecutor(
                    max_workers=self.config.get("max_workers", 5)
                ) as executor:
                    self.results = list(executor.map(runner, tasks))
            else:
                self.results = [runner(task) for task in tasks]

    def print_summary(self):
        """Print a summary table of results."""
        if not self.results:
            console.print("[yellow]No results to display[/]")
            return

        table = Table(title="Evaluation Summary")
        table.add_column("Test Case", style="cyan")
        table.add_column("Model", style="magenta")
        table.add_column("Score", style="green")
        table.add_column("Duration", style="yellow")
        table.add_column("Cost", style="red")

        for result in self.results:
            table.add_row(
                result.test_case_name[:30],
                result.model_type[:20],
                f"{result.judge_score:.2f}",
                f"{result.duration_seconds:.2f}s",
                f"${result.estimated_cost:.4f}",
            )

        console.print(table)

        # Summary stats
        avg_score = sum(r.judge_score for r in self.results) / len(self.results)
        total_cost = sum(r.estimated_cost for r in self.results)
        pii_count = sum(1 for r in self.results if r.pii_found)

        console.print(f"\n[bold]Average Score:[/] {avg_score:.3f}")
        console.print(f"[bold]Total Cost:[/] ${total_cost:.4f}")
        if pii_count > 0:
            console.print(f"[bold red]⚠ PII Warnings:[/] {pii_count} responses")

    def export(self):
        """Export results to JSON files."""
        if not self.results:
            logger.warning("No results to export")
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Export latest results for dashboard
        latest_path = self.results_dir / "latest_results.json"
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump([r.model_dump() for r in self.results], f, indent=2)

        # Export a unique file for this run
        run_path = self.results_dir / f"run_{timestamp}.json"
        with open(run_path, "w", encoding="utf-8") as f:
            json.dump([r.model_dump() for r in self.results], f, indent=2)

        logger.info(f"Results exported to {run_path}")
        console.print(f"[green]✓[/] Results saved to: {run_path.name}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Evaluation Framework V2.0.2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  run-evaluation --models simulated:default
  run-evaluation --models openai:gpt-4o anthropic:claude-sonnet-4-20250514
  run-evaluation --models ollama:llama3 --persona critic
        """,
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=["simulated:default"],
        help="List of models (format: provider:model_name)",
    )
    parser.add_argument(
        "--persona",
        default="default",
        choices=["default", "critic", "helper", "auditor"],
        help="Judge persona for evaluation",
    )
    parser.add_argument(
        "--config",
        default="ai_evaluation/config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Run evaluations sequentially instead of parallel",
    )

    args = parser.parse_args()

    try:
        evaluator = AIEvaluator(config_path=args.config)
        console.print(
            Panel.fit(
                f"🤖 AI Benchmark V2.1.0\nPersona: {args.persona}\nModels: {', '.join(args.models)}",
                style="bold green",
            )
        )

        evaluator.run_suite(
            args.models, persona=args.persona, parallel=not args.sequential
        )

        evaluator.print_summary()
        evaluator.export()

        console.print("\n[bold cyan]✨ Evaluation complete![/]")
        console.print("[dim]Run 'view-dashboard' for interactive dashboard[/]")

    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/] {e}")
        console.print(
            "[yellow]Make sure config.yaml exists and test cases are present[/]"
        )
    except Exception as e:
        console.print(f"[bold red]Fatal error:[/] {e}")
        logger.exception("Fatal error during evaluation")


if __name__ == "__main__":
    main()
