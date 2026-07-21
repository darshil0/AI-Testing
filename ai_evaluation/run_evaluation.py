import datetime
import json
import logging
import time
import os
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple

import sys
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Reconfigure sys.stdout and sys.stderr to use utf-8 on Windows
if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

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
        logging.FileHandler(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", "evaluation.log"
            )
        ),
    ],
)
logger = logging.getLogger("rich")
console = Console()


def extract_json_blocks(text: str) -> List[str]:
    """Find all potential JSON object blocks in text using balanced braces, ignoring braces inside strings."""
    blocks = []
    i = 0
    n = len(text)
    while i < n:
        start_idx = text.find("{", i)
        if start_idx == -1:
            break

        count = 0
        in_string = False
        escaped = False
        end_idx = -1
        for j in range(start_idx, n):
            char = text[j]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
            else:
                if char == '"':
                    in_string = True
                elif char == "{":
                    count += 1
                elif char == "}":
                    count -= 1
                    if count == 0:
                        end_idx = j
                        break
        if end_idx != -1:
            blocks.append(text[start_idx : end_idx + 1])
            i = end_idx + 1
        else:
            i = start_idx + 1
    return blocks


class TestCase(BaseModel):
    __test__ = False
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
    pii_types: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())


class AIEvaluator:
    def __init__(self, config_path: str = "ai_evaluation/config.yaml") -> None:
        # Handle relative paths from project root
        if not Path(config_path).exists():
            alt_path = Path(__file__).parent / "config.yaml"
            if alt_path.exists():
                config_path = str(alt_path)
            else:
                raise FileNotFoundError(f"Config file not found at {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        # Resolve paths relative to config location
        config_dir = Path(config_path).parent

        directories = self.config.get("directories", {})
        test_cases_path = directories.get("test_cases", "test_cases")
        results_path = directories.get("results", "results")

        self.test_cases_dir = Path(test_cases_path)
        if not self.test_cases_dir.is_absolute():
            self.test_cases_dir = config_dir / self.test_cases_dir

        self.results_dir = Path(results_path)
        if not self.results_dir.is_absolute():
            self.results_dir = config_dir / self.results_dir

        self.results: List[EvaluationResult] = []

        # Ensure directories exist
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.test_cases_dir.mkdir(parents=True, exist_ok=True)

    def load_from_hf(
        self, dataset_name: str, split: str = "test", count: int = 5
    ) -> None:
        """Load test cases from HuggingFace datasets."""
        try:
            from datasets import load_dataset

            ds = load_dataset(dataset_name, split=split, streaming=True)
            logger.info(f"Loading {count} cases from HF: {dataset_name}")
            written_count = 0
            for i, item in enumerate(ds.take(count)):
                prompt = item.get("question") or item.get("prompt") or item.get("text")
                if prompt:
                    path = (
                        self.test_cases_dir
                        / f"hf_{dataset_name.replace('/', '_')}_{i}.txt"
                    )
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(f"Category: HuggingFace\nDifficulty: Auto\n\n{prompt}")
                    written_count += 1
            logger.info(
                f"Successfully loaded {written_count} test cases from {dataset_name}"
            )
        except ImportError:
            logger.error(
                "HuggingFace 'datasets' not installed. Install with: pip install datasets"
            )
        except Exception as e:
            logger.error(f"HF Load failed: {e}")

    def _pii_scan(self, text: str) -> Tuple[bool, List[str]]:
        """Simple regex-based PII scanner."""
        found_types: List[str] = []
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
            return -1.0, f"Judge model error: {e}"

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
            blocks = extract_json_blocks(raw)
            parsed_data = None
            for block in blocks:
                try:
                    data = json.loads(block)
                    if isinstance(data, dict) and "score" in data:
                        parsed_data = data
                        break
                except json.JSONDecodeError:
                    continue

            if parsed_data is not None:
                # Validate JSON/fields
                if "score" not in parsed_data:
                    raise ValueError("JSON is missing the required 'score' key.")

                try:
                    score = float(parsed_data["score"])
                except (TypeError, ValueError) as e:
                    raise ValueError(
                        f"Score is not a valid float: {parsed_data['score']}"
                    ) from e

                # Clamp score to valid range
                score = max(0.0, min(1.0, score))
                reasoning = parsed_data.get("reasoning", "")
                return score, reasoning
            else:
                logger.warning(
                    f"Judge response did not contain valid JSON: {raw[:100]}"
                )
                raise ValueError(
                    f"Judge response did not contain valid JSON with score. Raw response: {raw}"
                )
        except Exception as e:
            logger.error(f"Judging failed: {e}")
            raise e

    def _parse_test_case(self, file_path: Path) -> TestCase:
        """Parse a test case from a file."""
        try:
            if file_path.suffix in (".yaml", ".yml"):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    if "name" not in data:
                        data["name"] = file_path.stem
                    return TestCase(**data)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.splitlines()
            category = "General"
            difficulty = "Medium"
            header_line_count = 0

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    if header_line_count > 0:
                        header_line_count += 1
                        break
                    else:
                        header_line_count += 1
                        continue

                cat_m = re.match(r"^Category:\s*(.*)", stripped, re.IGNORECASE)
                diff_m = re.match(r"^Difficulty:\s*(.*)", stripped, re.IGNORECASE)

                if cat_m:
                    category = cat_m.group(1).strip()
                    header_line_count += 1
                elif diff_m:
                    difficulty = diff_m.group(1).strip()
                    header_line_count += 1
                else:
                    break

            prompt_body = "\n".join(lines[header_line_count:]).strip()
            if not prompt_body:
                prompt_body = content.strip()

            return TestCase(
                name=file_path.stem,
                category=category,
                difficulty=difficulty,
                prompt=prompt_body,
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
            try:
                score, reason = self.judge_response(tc, response, persona)
            except Exception as je:
                logger.warning(f"Judging failed for {tc.name}: {je}")
                score, reason = -1.0, f"Judging failed: {str(je)}"

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
                duration_seconds=0.0,
                judge_score=0.0,
                judge_reasoning=f"Fatal error during processing: {str(e)}",
            )

    def run_suite(
        self, model_ids: List[str], persona: str = "default", parallel: bool = True
    ) -> None:
        """Run evaluation suite across all test cases and models."""
        files = (
            list(self.test_cases_dir.glob("*.txt"))
            + list(self.test_cases_dir.glob("*.yaml"))
            + list(self.test_cases_dir.glob("*.yml"))
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
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            main_task = progress.add_task("[cyan]Evaluating...", total=len(tasks))

            def runner(task_data: Tuple[Path, str, str]) -> EvaluationResult:
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

    def print_summary(self) -> None:
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

        # Summary stats - filter out sentinel error scores (< 0.0) for avg_score
        valid_scores = [r.judge_score for r in self.results if r.judge_score >= 0.0]
        failed_judge_count = sum(1 for r in self.results if r.judge_score < 0.0)

        if valid_scores:
            avg_score = sum(valid_scores) / len(valid_scores)
            console.print(f"\n[bold]Average Score:[/] {avg_score:.3f}")
        else:
            console.print("\n[bold]Average Score:[/] N/A (No valid judge scores)")

        if failed_judge_count > 0:
            console.print(
                f"[bold yellow]⚠ Judge Errors:[/] {failed_judge_count} responses failed judging"
            )

        total_cost = sum(r.estimated_cost for r in self.results)
        pii_count = sum(1 for r in self.results if r.pii_found)

        console.print(f"[bold]Total Cost:[/] ${total_cost:.4f}")
        if pii_count > 0:
            console.print(f"[bold red]⚠ PII Warnings:[/] {pii_count} responses")

    def export(self, export_format: str = "json") -> None:
        """Export results to files."""
        if not self.results:
            logger.warning("No results to export")
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Export latest results for dashboard (always JSON so dashboard is compatible)
        latest_path = self.results_dir / "latest_results.json"
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump([r.model_dump() for r in self.results], f, indent=2)

        # Export a unique file for this run
        if export_format.lower() == "csv":
            import csv

            run_path = self.results_dir / f"run_{timestamp}.csv"
            if self.results:
                first_dict = self.results[0].model_dump()
                fieldnames = list(first_dict.keys())
                with open(run_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for r in self.results:
                        row = r.model_dump()
                        for k, v in row.items():
                            if isinstance(v, (list, dict)):
                                row[k] = json.dumps(v)
                        writer.writerow(row)
        else:
            run_path = self.results_dir / f"run_{timestamp}.json"
            with open(run_path, "w", encoding="utf-8") as f:
                json.dump([r.model_dump() for r in self.results], f, indent=2)

        logger.info(f"Results exported to {run_path}")
        console.print(f"[green]✓[/] Results saved to: {run_path.name}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Evaluation Framework V2.1.7",
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
        "--export-format",
        default="json",
        choices=["json", "csv"],
        help="Format to export results (json or csv)",
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
                f"🤖 AI Benchmark V2.1.7\nPersona: {args.persona}\nModels: {', '.join(args.models)}",
                style="bold green",
            )
        )

        evaluator.run_suite(
            args.models, persona=args.persona, parallel=not args.sequential
        )

        evaluator.print_summary()
        evaluator.export(export_format=args.export_format)

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
