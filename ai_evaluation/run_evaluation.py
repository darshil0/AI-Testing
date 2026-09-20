import datetime
import json
import logging
import math
import time
import os
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple, Optional

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


def validate_score(value: object) -> float:
    """Strictly validate a judge score."""
    if isinstance(value, bool):
        raise ValueError("Judge score must be numeric, not boolean")

    if not isinstance(value, (int, float)):
        raise ValueError("Judge score must be numeric")

    score = float(value)

    if not math.isfinite(score):
        raise ValueError("Judge score must be finite")

    if not 0.0 <= score <= 1.0:
        raise ValueError("Judge score must be in [0.0, 1.0]")

    return score


class EvaluationResult(BaseModel):
    test_case_name: str = ""
    category: str = "General"
    difficulty: str = "Medium"
    model_type: str = ""
    prompt: str = ""
    response: str = ""
    duration_seconds: float = 0.0
    tokens_input: int = 0
    tokens_output: int = 0
    estimated_cost: Optional[float] = None
    judge_score: Optional[float] = 0.0
    judge_reasoning: str = ""
    pii_found: bool = False
    pii_types: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    status: str = "success"

    def __init__(self, **data: Any) -> None:
        if "cost" in data and "estimated_cost" not in data:
            data["estimated_cost"] = data.pop("cost")
        if "score" in data and "judge_score" not in data:
            data["judge_score"] = data.pop("score")
        super().__init__(**data)

    @property
    def cost(self) -> Optional[float]:
        return self.estimated_cost

    @property
    def score(self) -> Optional[float]:
        return self.judge_score


def summarize_results(results: List[EvaluationResult]) -> Dict[str, Any]:
    """Compute summary statistics for a list of evaluation results."""
    valid_scores = [r.score for r in results if r.score is not None and r.score >= 0.0]
    failed_judge_count = sum(1 for r in results if r.score is None or r.score < 0.0)
    known_costs = [r.cost for r in results if r.cost is not None]
    unknown_cost_count = sum(1 for r in results if r.cost is None)
    total_cost = sum(known_costs)
    cost_complete = unknown_cost_count == 0

    avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else None

    return {
        "total_cases": len(results),
        "valid_scores_count": len(valid_scores),
        "avg_score": avg_score,
        "failed_judge_count": failed_judge_count,
        "known_total_cost": round(total_cost, 6),
        "unknown_cost_count": unknown_cost_count,
        "cost_complete": cost_complete,
    }


def resolve_config_path(config_arg: Any = None) -> Path:
    """Resolve configuration file path strictly."""
    if config_arg is not None:
        path = Path(config_arg).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        return path

    default_path = Path("ai_evaluation/config.yaml")
    if default_path.is_file():
        return default_path

    alt_path = Path(__file__).parent / "config.yaml"
    if alt_path.is_file():
        return alt_path

    raise FileNotFoundError(f"Configuration file not found: {default_path}")


class AIEvaluator:
    def __init__(self, config_path: Any = None) -> None:
        self.config_path = resolve_config_path(config_path)

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        # Resolve paths relative to config location
        config_dir = self.config_path.parent

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
            if len(blocks) != 1:
                raise ValueError(
                    f"Expected exactly 1 JSON block in judge output, found {len(blocks)}. Raw response: {raw}"
                )

            try:
                data = json.loads(blocks[0])
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Judge response contained invalid JSON block: {e}"
                ) from e

            if not isinstance(data, dict) or "score" not in data:
                raise ValueError("JSON is missing the required 'score' key.")

            score = validate_score(data["score"])
            reasoning = data.get("reasoning", "")
            return score, reasoning
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
            expectations: List[str] = []
            idx = 0

            while idx < len(lines):
                stripped = lines[idx].strip()

                if not stripped:
                    idx += 1
                    continue

                cat_m = re.match(r"^Category:\s*(.*)", stripped, re.IGNORECASE)
                diff_m = re.match(r"^Difficulty:\s*(.*)", stripped, re.IGNORECASE)
                exp_m = re.match(r"^Expectations?:\s*(.*)", stripped, re.IGNORECASE)

                if cat_m:
                    val = cat_m.group(1).strip()
                    if val:
                        category = val
                    idx += 1
                    continue

                if diff_m:
                    val = diff_m.group(1).strip()
                    if val:
                        difficulty = val
                    idx += 1
                    continue

                if exp_m:
                    val = exp_m.group(1).strip()
                    if val:
                        expectations.append(val)
                    idx += 1
                    continue

                break

            prompt_body = "\n".join(lines[idx:]).strip()
            if not prompt_body:
                prompt_body = content.strip()

            return TestCase(
                name=file_path.stem,
                category=category,
                difficulty=difficulty,
                prompt=prompt_body,
                expectations=expectations,
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
            estimated_cost = round(cost, 6) if cost is not None else None
            pii_found, pii_types = self._pii_scan(response)

            try:
                score, reason = self.judge_response(tc, response, persona)
                judge_status = "success"
            except Exception as je:
                logger.warning(f"Judging failed for {tc.name}: {je}")
                score, reason = None, f"Judging failed: {str(je)}"
                judge_status = "judge_error"

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
                estimated_cost=estimated_cost,
                judge_score=round(score, 3) if score is not None else None,
                judge_reasoning=reason,
                pii_found=pii_found,
                pii_types=pii_types,
                status=judge_status,
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
                judge_score=None,
                estimated_cost=None,
                judge_reasoning=f"Fatal error during processing: {str(e)}",
                status="model_error",
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
            score_str = (
                f"{result.judge_score:.2f}"
                if result.judge_score is not None and result.judge_score >= 0.0
                else "N/A"
            )
            cost_str = (
                f"${result.estimated_cost:.4f}"
                if result.estimated_cost is not None
                else "N/A"
            )
            table.add_row(
                result.test_case_name[:30],
                result.model_type[:20],
                score_str,
                f"{result.duration_seconds:.2f}s",
                cost_str,
            )

        console.print(table)

        summary = summarize_results(self.results)

        if summary["avg_score"] is not None:
            console.print(f"\n[bold]Average Score:[/] {summary['avg_score']:.3f}")
        else:
            console.print("\n[bold]Average Score:[/] N/A (No valid judge scores)")

        if summary["failed_judge_count"] > 0:
            console.print(
                f"[bold yellow]⚠ Judge Errors:[/] {summary['failed_judge_count']} responses failed judging"
            )

        console.print(f"[bold]Known Total Cost:[/] ${summary['known_total_cost']:.4f}")
        if not summary["cost_complete"]:
            console.print(
                f"[bold yellow]⚠ Cases with Unknown Cost:[/] {summary['unknown_cost_count']}/{summary['total_cases']}"
            )
            console.print("[bold yellow]Cost completeness: incomplete[/]")
        else:
            console.print("[bold green]Cost completeness: complete[/]")

        pii_count = sum(1 for r in self.results if r.pii_found)
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


def main() -> int:
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
        default=None,
        help="Path to configuration file",
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Run evaluations sequentially instead of parallel",
    )
    parser.add_argument(
        "--require-known-costs",
        action="store_true",
        help="Fail evaluation if any model or judge cost is unknown",
    )
    parser.add_argument(
        "--allow-failures",
        action="store_true",
        help="Exit with status 0 even if evaluation test cases fail or judge errors occur",
    )

    args = parser.parse_args()

    try:
        config_path = resolve_config_path(args.config)
        evaluator = AIEvaluator(config_path=config_path)
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

        summary = summarize_results(evaluator.results)

        if args.require_known_costs and not summary["cost_complete"]:
            console.print(
                "[bold red]Error:[/] Unknown cost encountered with --require-known-costs"
            )
            return 1

        if not args.allow_failures and (
            summary["failed_judge_count"] > 0
            or any(
                r.judge_score is None or r.judge_score < 0.0 for r in evaluator.results
            )
        ):
            console.print(
                "[bold red]Error:[/] Evaluation contains judge errors or failures"
            )
            return 1

        console.print("\n[bold cyan]✨ Evaluation complete![/]")
        console.print("[dim]Run 'view-dashboard' for interactive dashboard[/]")
        return 0

    except (FileNotFoundError, OSError, ValueError) as e:
        console.print(f"[bold red]Configuration error:[/] {e}")
        logger.error(f"Configuration error: {e}")
        return 2
    except Exception as e:
        console.print(f"[bold red]Fatal error:[/] {e}")
        logger.exception("Fatal error during evaluation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
