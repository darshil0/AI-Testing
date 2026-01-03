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
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.test_cases_dir = Path(self.config["directories"]["test_cases"])
        self.results_dir = Path(self.config["directories"]["results"])
        self.results: List[EvaluationResult] = []

        if not self.results_dir.exists():
            self.results_dir.mkdir(parents=True, exist_ok=True)

    def load_from_hf(self, dataset_name: str, split: str = "test", count: int = 5):
        """Load test cases from HuggingFace datasets."""
        try:
            from datasets import load_dataset

            ds = load_dataset(dataset_name, split=split, streaming=True)
            logger.info(f"Loading {count} cases from HF: {dataset_name}")
            for i, item in enumerate(ds.take(count)):
                prompt = item.get("question") or item.get("prompt") or item.get("text")
                if prompt:
                    path = self.test_cases_dir / f"hf_{i}.txt"
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(f"Category: HuggingFace\nDifficulty: Auto\n\n{prompt}")
        except ImportError:
            logger.error("HuggingFace 'datasets' not installed. pip install datasets.")
        except Exception as e:
            logger.error(f"HF Load failed: {e}")

    def _pii_scan(self, text: str) -> Tuple[bool, List[str]]:
        """Simple regex-based PII scanner."""
        found_types = []
        for p_type, pattern in self.config["pii_patterns"].items():
            if re.search(pattern, text):
                found_types.append(p_type)
        return len(found_types) > 0, found_types

    def judge_response(
        self, test_case: TestCase, response: str, persona: str = "default"
    ) -> Tuple[float, str]:
        judge_model_id = self.config["judge"]["model"]
        persona_prompt = self.config["judge_personas"].get(
            persona, self.config["judge_personas"]["default"]
        )

        try:
            judge_model = get_model(judge_model_id, self.config)
        except ValueError as e:
            return 0.0, f"Judge model error: {e}"

        criteria = (
            ",".join(test_case.expectations)
            if test_case.expectations
            else "overall quality"
        )
        prompt = f'{persona_prompt}\nRate on 0.0-1.0. JSON: {{"score": float, "reasoning": "string"}}\nPROMPT: {test_case.prompt}\nRESPONSE: {response}'

        try:
            raw, _, _ = judge_model.call(prompt)
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
                return float(data.get("score", 0.0)), data.get("reasoning", "")
        except json.JSONDecodeError:
            return 0.0, "Judge returned invalid JSON."
        except Exception as e:
            logger.error(f"Judging failed: {e}")
        return 0.0, "Judging error"

    def _parse_test_case(self, file_path: Path) -> TestCase:
        if file_path.suffix == ".yaml":
            with open(file_path, "r") as f:
                return TestCase(name=file_path.stem, **yaml.safe_load(f))

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            category_match = re.search(r"Category:\s*(.*)", content)
            difficulty_match = re.search(r"Difficulty:\s*(.*)", content)
            category = category_match.group(1).strip() if category_match else "General"
            difficulty = (
                difficulty_match.group(1).strip() if difficulty_match else "Medium"
            )
            return TestCase(
                name=file_path.stem,
                category=category,
                difficulty=difficulty,
                prompt=content,
            )

    def process_one(
        self, file_path: Path, model_id: str, persona: str = "default"
    ) -> EvaluationResult:
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
                judge_score=score,
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
                response=f"Error: {e}",
                duration_seconds=0,
                judge_score=0.0,
                judge_reasoning="Fatal error during processing.",
            )

    def run_suite(
        self, model_ids: List[str], persona: str = "default", parallel: bool = True
    ):
        files = list(self.test_cases_dir.glob("*.txt")) + list(
            self.test_cases_dir.glob("*.yaml")
        )
        tasks = [(file, model_id, persona) for file in files for model_id in model_ids]

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

            if parallel:
                with ThreadPoolExecutor(
                    max_workers=self.config.get("max_workers", 5)
                ) as executor:
                    self.results = list(executor.map(runner, tasks))
            else:
                self.results = [runner(task) for task in tasks]

    def export(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        # Export latest results for dashboard
        latest_path = self.results_dir / "latest_results.json"
        with open(latest_path, "w") as f:
            json.dump([r.model_dump() for r in self.results], f, indent=2)

        # Export a unique file for this run
        run_path = self.results_dir / f"run_{timestamp}.json"
        with open(run_path, "w") as f:
            json.dump([r.model_dump() for r in self.results], f, indent=2)
        logger.info(f"Exported results to {run_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Evaluation Framework")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["simulated:default"],
        help="List of models to evaluate, e.g., 'openai:gpt-4o ollama:llama3'",
    )
    parser.add_argument(
        "--persona", default="default", help="Judge persona to use for evaluation."
    )
    parser.add_argument(
        "--config",
        default="ai_evaluation/config.yaml",
        help="Path to the configuration file.",
    )

    args = parser.parse_args()

    evaluator = AIEvaluator(config_path=args.config)
    console.print(
        Panel.fit(f"🚀 AI Benchmark V2.0 - Persona: {args.persona}", style="bold green")
    )
    evaluator.run_suite(args.models, persona=args.persona)
    evaluator.export()
    console.print(
        "[bold cyan]Done! Run 'python ai_evaluation/analytics.py' for charts.[/]"
    )
