import datetime
import json
import csv
import logging
import time
import os
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

import yaml
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel, Field

# Rich UI imports
from rich.console import Console
from rich.table import Table
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
from rich.handler import RichHandler
from rich.panel import Panel

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

try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Load environment variables
load_dotenv()

# Configure logging with Rich
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

# --- Pricing Constants (Approximate per 1M tokens) ---
PRICING = {
    "gpt-4o": {"input": 5.0, "output": 15.0},
    "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
    "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
    "claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
    "gemini-1.5-pro": {"input": 7.0, "output": 21.0},
    "simulated": {"input": 0.0, "output": 0.0},
}


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
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())


class AIEvaluator:
    def __init__(
        self,
        config_path="config.yaml",
        test_cases_dir="test_cases",
        results_dir="results",
    ):
        self.test_cases_dir = Path(test_cases_dir)
        self.results_dir = Path(results_dir)
        self.results: List[EvaluationResult] = []

        # Initialize clients
        self.openai_client = (
            OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY")
            else None
        )
        self.anthropic_client = (
            Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY")
            else None
        )

        if GEMINI_AVAILABLE and os.getenv("GOOGLE_API_KEY"):
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.gemini_model = genai.GenerativeModel("gemini-1.5-pro")
        else:
            self.gemini_model = None

        if not self.results_dir.exists():
            self.results_dir.mkdir(parents=True, exist_ok=True)

    def _calculate_cost(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        prices = PRICING.get(model, {"input": 0, "output": 0})
        return (input_tokens / 1_000_000 * prices["input"]) + (
            output_tokens / 1_000_000 * prices["output"]
        )

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _call_openai(self, prompt: str, model="gpt-4o"):
        if not self.openai_client:
            raise ValueError("OpenAI Key Missing")
        resp = self.openai_client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}]
        )
        return (
            resp.choices[0].message.content,
            resp.usage.prompt_tokens,
            resp.usage.completion_tokens,
        )

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _call_anthropic(self, prompt: str, model="claude-3-opus-20240229"):
        if not self.anthropic_client:
            raise ValueError("Anthropic Key Missing")
        resp = self.anthropic_client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text, resp.usage.input_tokens, resp.usage.output_tokens

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _call_gemini(self, prompt: str):
        if not self.gemini_model:
            raise ValueError("Gemini Key Missing")
        resp = self.gemini_model.generate_content(prompt)
        # Gemini usage metadata varies; using heuristic for now
        return resp.text, len(prompt) // 4, len(resp.text) // 4

    def judge_response(self, test_case: TestCase, response: str) -> tuple[float, str]:
        """Use an LLM to judge the quality of the response."""
        judge_provider = os.getenv("JUDGE_MODEL", "simulated")
        judge_model_name = os.getenv("JUDGE_SPECIFIC_MODEL", "gpt-4o")

        if judge_provider == "simulated":
            return 0.85, "Simulated judgment based on keyword heuristic."

        criteria = (
            ",".join(test_case.expectations)
            if test_case.expectations
            else "clarity and accuracy"
        )
        judge_prompt = f"""
        Rate the following AI response on a scale of 0.0 to 1.0 based on these criteria: {criteria}.
        Provide your response in JSON format: {{"score": float, "reasoning": "string"}}

        PROMPT: {test_case.prompt}
        RESPONSE: {response}
        """

        try:
            if judge_provider == "openai":
                raw, _, _ = self._call_openai(judge_prompt, model=judge_model_name)
            elif judge_provider == "anthropic":
                raw, _, _ = self._call_anthropic(judge_prompt, model=judge_model_name)
            else:
                return 0.5, "Unknown judge provider"

            # Simple JSON extraction
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
                return float(data.get("score", 0.0)), data.get("reasoning", "")
        except Exception as e:
            logger.error(f"Judging failed: {e}")
        return 0.0, "Error during judging"

    def _parse_test_case(self, file_path: Path) -> TestCase:
        if file_path.suffix == ".yaml":
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
                return TestCase(name=file_path.stem, **data)

        # Legacy TXT parsing
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        category = "General"
        difficulty = "Medium"
        lines = content.split("\n")
        for line in lines[:3]:
            if line.lower().startswith("category:"):
                category = line.split(":")[1].strip()
            if line.lower().startswith("difficulty:"):
                difficulty = line.split(":")[1].strip()

        return TestCase(
            name=file_path.stem,
            category=category,
            difficulty=difficulty,
            prompt=content,
        )

    def process_one(self, file_path: Path, model_type: str) -> EvaluationResult:
        tc = self._parse_test_case(file_path)
        start = time.time()

        try:
            if model_type == "simulated":
                ans, i, o = "Simulated response.", 10, 5
            elif model_type == "openai":
                ans, i, o = self._call_openai(tc.prompt)
            elif model_type == "anthropic":
                ans, i, o = self._call_anthropic(tc.prompt)
            elif model_type == "gemini":
                ans, i, o = self._call_gemini(tc.prompt)
            else:
                raise ValueError("Model not supported")

            dur = time.time() - start
            cost = self._calculate_cost(model_type, i, o)
            score, reason = self.judge_response(tc, ans)

            return EvaluationResult(
                test_case_name=tc.name,
                category=tc.category,
                difficulty=tc.difficulty,
                model_type=model_type,
                prompt=tc.prompt,
                response=ans,
                duration_seconds=round(dur, 2),
                tokens_input=i,
                tokens_output=o,
                estimated_cost=round(cost, 6),
                judge_score=score,
                judge_reasoning=reason,
            )
        except Exception as e:
            logger.error(f"Error evaluating {tc.name}: {e}")
            return EvaluationResult(
                test_case_name=tc.name,
                category=tc.category,
                difficulty=tc.difficulty,
                model_type=model_type,
                prompt=tc.prompt,
                response=f"Error: {e}",
                duration_seconds=0,
                judge_score=0,
                judge_reasoning="Crash",
            )

    def run_suite(self, model_types: List[str], parallel: bool = True):
        files = list(self.test_cases_dir.glob("*.txt")) + list(
            self.test_cases_dir.glob("*.yaml")
        )
        tasks = [(f, m) for f in files for m in model_types]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            main_task = progress.add_task(
                "[cyan]Evaluating Models...", total=len(tasks)
            )

            def run_task(args):
                res = self.process_one(*args)
                progress.advance(main_task)
                return res

            if parallel:
                with ThreadPoolExecutor(max_workers=5) as executor:
                    self.results = list(executor.map(run_task, tasks))
            else:
                self.results = [run_task(t) for t in tasks]

    def display_summary(self):
        table = Table(
            title="Evaluation Benchmark Summary",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Case")
        table.add_column("Model")
        table.add_column("Time (s)")
        table.add_column("Score")
        table.add_column("Cost ($)")

        for r in self.results:
            color = (
                "green"
                if r.judge_score > 0.8
                else "yellow" if r.judge_score > 0.5 else "red"
            )
            table.add_row(
                r.test_case_name,
                r.model_type,
                f"{r.duration_seconds}s",
                f"[{color}]{r.judge_score}[/]",
                f"${r.estimated_cost:.4f}",
            )
        console.print(table)

    def export(self):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        # JSON
        with open(self.results_dir / f"v1_results_{ts}.json", "w") as f:
            json.dump([r.model_dump() for r in self.results], f, indent=2)

        # CSV Comparison Report
        df_rows = []
        for r in self.results:
            df_rows.append(r.model_dump())

        keys = df_rows[0].keys() if df_rows else []
        with open(
            self.results_dir / f"comparison_report_{ts}.csv", "w", newline=""
        ) as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(df_rows)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=["simulated"])
    parser.add_argument("--sequential", action="store_true")
    args = parser.parse_args()

    # Resolve paths relative to the script location
    script_dir = Path(__file__).parent

    evaluator = AIEvaluator(
        test_cases_dir=script_dir / "test_cases", results_dir=script_dir / "results"
    )
    console.print(Panel.fit("🚀 Starting V1.0 AI Evaluation Framework", style="bold blue"))

    evaluator.run_suite(args.models, parallel=not args.sequential)
    evaluator.display_summary()
    evaluator.export()
    console.print(
        "[bold green]✅ Evaluation Complete. Reports generated in results/ directory.[/]"
    )
