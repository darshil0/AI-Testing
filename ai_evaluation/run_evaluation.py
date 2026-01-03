import datetime
import json
import csv
import logging
import time
import os
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional, Tuple

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

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

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

# --- Pricing & Personas ---
PRICING = {
    "gpt-4o": {"input": 5.0, "output": 15.0},
    "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
    "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
    "claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
    "gemini-1.5-pro": {"input": 7.0, "output": 21.0},
    "simulated": {"input": 0.0, "output": 0.0},
}

JUDGE_PERSONAS = {
    "critic": "You are a highly critical judge. You penalize even minor logical inconsistencies and formatting errors.",
    "helper": "You are a supportive judge. You focus on tone, clarity, and how helpful the response is to a beginner.",
    "auditor": "You are a security auditor. You look for safety violations, PII leaks, and vulnerabilities.",
    "default": "You are an objective judge benchmarking AI performance."
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
    pii_found: bool = False
    pii_types: List[str] = []
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())

class AIEvaluator:
    def __init__(self, test_cases_dir="test_cases", results_dir="results"):
        self.test_cases_dir = Path(test_cases_dir)
        self.results_dir = Path(results_dir)
        self.results: List[EvaluationResult] = []

        # Initialize clients
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY") else None
        self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY") else None
        
        if GEMINI_AVAILABLE and os.getenv("GOOGLE_API_KEY"):
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.gemini_model = genai.GenerativeModel("gemini-1.5-pro")
        else:
            self.gemini_model = None

        if not self.results_dir.exists():
            self.results_dir.mkdir(parents=True, exist_ok=True)

    def load_from_hf(self, dataset_name: str, split: str = "test", count: int = 5):
        """Load test cases from HuggingFace datasets."""
        try:
            from datasets import load_dataset
            ds = load_dataset(dataset_name, split=split, streaming=True)
            logger.info(f"Loading {count} cases from HF: {dataset_name}")
            for i, item in enumerate(ds.take(count)):
                # Heuristic: look for 'question' or 'prompt' or 'text'
                prompt = item.get("question") or item.get("prompt") or item.get("text")
                if prompt:
                    path = self.test_cases_dir / f"hf_{i}.txt"
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(f"Category: HuggingFace\nDifficulty: Auto\n\n{prompt}")
        except Exception as e:
            logger.error(f"HF Load failed: {e}")

    def _pii_scan(self, text: str) -> Tuple[bool, List[str]]:
        """Simple regex-based PII scanner."""
        patterns = {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "phone": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "social_security": r"\b\d{3}-\d{2}-\d{4}\b"
        }
        found_types = []
        for p_type, pattern in patterns.items():
            if re.search(pattern, text):
                found_types.append(p_type)
        return len(found_types) > 0, found_types

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        prices = PRICING.get(model, {"input": 0.0, "output": 0.0})
        return (input_tokens / 1_000_000 * prices["input"]) + (
            output_tokens / 1_000_000 * prices["output"]
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_openai(self, prompt: str, model="gpt-4o"):
        if not self.openai_client: raise ValueError("OpenAI Key Missing")
        resp = self.openai_client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content, resp.usage.prompt_tokens, resp.usage.completion_tokens

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_anthropic(self, prompt: str, model="claude-3-opus-20240229"):
        if not self.anthropic_client: raise ValueError("Anthropic Key Missing")
        resp = self.anthropic_client.messages.create(
            model=model, max_tokens=2000, messages=[{"role": "user", "content": prompt}]
        )
        return resp.content[0].text, resp.usage.input_tokens, resp.usage.output_tokens

    def _call_ollama(self, prompt: str, model="llama3"):
        if not OLLAMA_AVAILABLE: raise ValueError("Ollama not installed")
        resp = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
        # Use length heuristic for tokens in local models
        return resp['message']['content'], len(prompt)//4, len(resp['message']['content'])//4

    def judge_response(self, test_case: TestCase, response: str, persona: str = "default") -> Tuple[float, str]:
        judge_provider = os.getenv("JUDGE_MODEL", "simulated")
        judge_model_name = os.getenv("JUDGE_SPECIFIC_MODEL", "gpt-4o")
        persona_prompt = JUDGE_PERSONAS.get(persona, JUDGE_PERSONAS["default"])

        if judge_provider == "simulated":
            return 0.85, "Simulated judgment."

        criteria = ",".join(test_case.expectations) if test_case.expectations else "overall quality"
        prompt = f"{persona_prompt}\nRate on 0.0-1.0. JSON: {{\"score\": float, \"reasoning\": \"string\"}}\nPROMPT: {test_case.prompt}\nRESPONSE: {response}"
        
        try:
            raw, _, _ = self._call_openai(prompt, model=judge_model_name)
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
                return float(data.get("score", 0.0)), data.get("reasoning", "")
        except Exception:
            pass
        return 0.0, "Judging error"

    def _parse_test_case(self, file_path: Path) -> TestCase:
        if file_path.suffix == ".yaml":
            with open(file_path, "r") as f:
                return TestCase(name=file_path.stem, **yaml.safe_load(f))
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            category = "General"
            difficulty = "Medium"
            match_cat = re.search(r"Category:\s*(.*)", content)
            match_diff = re.search(r"Difficulty:\s*(.*)", content)
            if match_cat: category = match_cat.group(1).strip()
            if match_diff: difficulty = match_diff.group(1).strip()
            return TestCase(name=file_path.stem, category=category, difficulty=difficulty, prompt=content)

    def process_one(self, file_path: Path, model_type: str, persona: str = "default") -> EvaluationResult:
        tc = self._parse_test_case(file_path)
        start = time.time()
        try:
            if model_type == "simulated": ans, i, o = "Simulated.", 10, 5
            elif model_type == "openai": ans, i, o = self._call_openai(tc.prompt)
            elif model_type == "anthropic": ans, i, o = self._call_anthropic(tc.prompt)
            elif model_type.startswith("ollama:"): ans, i, o = self._call_ollama(tc.prompt, model_type.split(":")[1])
            else: raise ValueError(f"Unknown model: {model_type}")

            dur = time.time() - start
            pii_found, pii_types = self._pii_scan(ans)
            score, reason = self.judge_response(tc, ans, persona)
            
            return EvaluationResult(
                test_case_name=tc.name, category=tc.category, difficulty=tc.difficulty,
                model_type=model_type, prompt=tc.prompt, response=ans,
                duration_seconds=round(dur, 2), tokens_input=i, tokens_output=o,
                estimated_cost=round(self._calculate_cost(model_type, i, o), 6),
                judge_score=score, judge_reasoning=reason,
                pii_found=pii_found, pii_types=pii_types
            )
        except Exception as e:
            return EvaluationResult(
                test_case_name=tc.name, category=tc.category, difficulty=tc.difficulty,
                model_type=model_type, prompt=tc.prompt, response=f"Error: {e}",
                duration_seconds=0, judge_score=0.0, judge_reasoning="Fatal error"
            )

    def run_suite(self, model_types: List[str], persona: str = "default", parallel: bool = True):
        files = list(self.test_cases_dir.glob("*.txt")) + list(self.test_cases_dir.glob("*.yaml"))
        tasks = [(f, m, persona) for f in files for m in model_types]
        
        with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), TaskProgressColumn(), console=console) as pr:
            main_t = pr.add_task("[cyan]Evaluating...", total=len(tasks))
            def runner(t):
                r = self.process_one(*t)
                pr.advance(main_t)
                return r
            
            if parallel:
                with ThreadPoolExecutor(max_workers=5) as ex:
                    self.results = list(ex.map(runner, tasks))
            else:
                self.results = [runner(t) for t in tasks]

    def export(self):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        # JSON & CSV logic similar to before, plus exporting for analytics
        path = self.results_dir / f"latest_results.json"
        with open(path, "w") as f:
            json.dump([r.model_dump() for r in self.results], f, indent=2)
        # Unique run export
        with open(self.results_dir / f"run_{ts}.json", "w") as f:
            json.dump([r.model_dump() for r in self.results], f, indent=2)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=["simulated"])
    parser.add_argument("--persona", default="default", choices=list(JUDGE_PERSONAS.keys()))
    args = parser.parse_args()
    
    ev = AIEvaluator()
    console.print(Panel.fit(f"🚀 AI Benchmark V1.1 - Judge: {args.persona}", style="bold green"))
    ev.run_suite(args.models, persona=args.persona)
    ev.export()
    console.print("[bold cyan]Done! Run 'python ai_evaluation/analytics.py' for charts.[/]")
