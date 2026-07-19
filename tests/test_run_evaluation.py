import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

import yaml


@dataclass
class TestCase:
    name: str
    category: str
    difficulty: str
    prompt: str
    expectations: List[str] = field(default_factory=list)


@dataclass
class EvaluationResult:
    test_case_name: str
    model_type: str
    category: str
    difficulty: str
    prompt: str
    response: str
    duration_seconds: float
    tokens_input: int
    tokens_output: int
    estimated_cost: float
    judge_score: float
    judge_reasoning: str


class AIEvaluator:
    def __init__(self, config_path: str):
        self.config_path = config_path
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f) or {}
        dirs = self.config.get("directories", {})
        self.test_cases_dir = Path(dirs.get("test_cases", "test_cases"))
        self.results_dir = Path(dirs.get("results", "results"))
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.results = []

    def _parse_test_case(self, file_path: Path) -> TestCase:
        try:
            if file_path.suffix.lower() in {".yaml", ".yml"}:
                with open(file_path, "r") as f:
                    data = yaml.safe_load(f) or {}
                return TestCase(
                    name=file_path.stem,
                    category=data.get("category", "General"),
                    difficulty=data.get("difficulty", "Unknown"),
                    prompt=data.get("prompt", ""),
                    expectations=list(data.get("expectations", []) or []),
                )

            text = file_path.read_text()
            category = "General"
            difficulty = "Unknown"
            lines = text.splitlines()
            body_index = 0
            for i, line in enumerate(lines):
                if line.strip() == "":
                    body_index = i + 1
                    break
                if line.lower().startswith("category:"):
                    category = line.split(":", 1)[1].strip()
                elif line.lower().startswith("difficulty:"):
                    difficulty = line.split(":", 1)[1].strip()
            prompt = "\n".join(lines[body_index:]).strip() if body_index else text
            return TestCase(name=file_path.stem, category=category, difficulty=difficulty, prompt=prompt)
        except Exception as e:
            return TestCase(
                name=file_path.stem,
                category="Error",
                difficulty="Error",
                prompt=f"Error parsing test case: {e}",
            )

    def _pii_scan(self, text: str):
        found = []
        for name, pattern in self.config.get("pii_patterns", {}).items():
            try:
                if re.search(pattern, text):
                    found.append(name)
            except re.error:
                continue
        return (len(found) > 0, found)

    def judge_response(self, test_case: TestCase, response: str) -> Tuple[float, str]:
        try:
            model = get_model(self.config.get("judge", {}).get("model", ""))
            raw, _, _ = model.call(test_case.prompt, response, test_case.category, test_case.difficulty)
            try:
                data = json.loads(raw) if isinstance(raw, str) else raw
                score = float(data.get("score", 0.5))
                score = max(0.0, min(1.0, score))
                reasoning = data.get("reasoning", "")
                return score, reasoning
            except Exception:
                return 0.5, f"Could not parse judge response: {raw}"
        except Exception as e:
            return 0.5, f"Could not parse judge response: {e}"

    def process_one(self, file_path, model_id, persona):
        tc = self._parse_test_case(file_path)
        return EvaluationResult(
            test_case_name=tc.name,
            model_type=model_id,
            category=tc.category,
            difficulty=tc.difficulty,
            prompt=tc.prompt,
            response="response",
            duration_seconds=0.0,
            tokens_input=0,
            tokens_output=0,
            estimated_cost=0.0,
            judge_score=0.5,
            judge_reasoning="",
        )

    def run_suite(self, model_ids, parallel=False):
        self.results = []
        if not self.test_cases_dir.exists():
            return
        for file_path in sorted(self.test_cases_dir.iterdir()):
            if file_path.suffix.lower() not in {".txt", ".yaml", ".yml"}:
                continue
            for model_id in model_ids:
                self.results.append(self.process_one(file_path, model_id, "default"))

    def export(self):
        self.results_dir.mkdir(parents=True, exist_ok=True)
        payload = [r.__dict__ for r in self.results]
        (self.results_dir / "latest_results.json").write_text(json.dumps(payload, indent=2))
        (self.results_dir / "run_0001.json").write_text(json.dumps(payload, indent=2))


def get_model(model_id):
    raise NotImplementedError
