import pytest
import json
import yaml
from pathlib import Path
from unittest.mock import MagicMock, patch
from ai_evaluation.run_evaluation import AIEvaluator, EvaluationResult, TestCase

@pytest.fixture
def mock_config(tmp_path):
    """Provides a mock configuration dictionary and creates necessary directories."""
    test_cases_dir = tmp_path / "test_cases"
    results_dir = tmp_path / "results"
    test_cases_dir.mkdir()
    results_dir.mkdir()

    config = {
        "directories": {
            "test_cases": str(test_cases_dir),
            "results": str(results_dir),
        },
        "max_workers": 1,
        "pii_patterns": {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        },
        "judge": {"model": "simulated:default"},
        "judge_personas": {
            "default": "You are a default judge.",
            "critic": "You are a critical judge.",
        },
        "pricing": {
            "simulated": {"input": 0.0, "output": 0.0}
        },
    }
    return config, test_cases_dir, results_dir


@pytest.fixture
def evaluator(mocker, mock_config):
    """A fixture that provides a properly mocked AIEvaluator instance."""
    config, test_cases_dir, results_dir = mock_config
    config_path = test_cases_dir.parent / "config.yaml"
    
    # Write config to file using safe YAML dump
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    
    # Mocking the directory paths in the instance to use our tmp_path
    evaluator_instance = AIEvaluator(config_path=str(config_path))

    # Mock the process_one method to avoid hitting real APIs or models during logic tests
    def mock_process_one(file_path, model_id, persona):
        return EvaluationResult(
            test_case_name=file_path.stem,
            model_type=model_id,
            category="General",
            difficulty="Easy",
            prompt="What is 2+2?",
            response="Simulated response: 4",
            duration_seconds=0.1,
            tokens_input=5,
            tokens_output=10,
            estimated_cost=0.0,
            judge_score=0.9,
            judge_reasoning="Good response, correct answer."
        )

    mocker.patch.object(evaluator_instance, 'process_one', side_effect=mock_process_one)
    return evaluator_instance, test_cases_dir, results_dir


# --- Initialization Tests ---

def test_aievaluator_initialization(evaluator, mock_config):
    evaluator_instance, test_cases_dir, _ = evaluator
    config, _, _ = mock_config
    
    assert evaluator_instance is not None
    assert evaluator_instance.config["max_workers"] == 1
    assert Path(evaluator_instance.test_cases_dir).name == test_cases_dir.name


# --- Parsing Tests ---

def test_parse_test_case_txt(evaluator):
    evaluator_instance, test_cases_dir, _ = evaluator
    test_file = test_cases_dir / "test1.txt"
    test_file.write_text("Category: Reasoning\nDifficulty: Hard\n\nWhat is 2+2?")
    
    test_case = evaluator_instance._parse_test_case(test_file)
    
    assert test_case.name == "test1"
    assert test_case.category == "Reasoning"
    assert "What is 2+2?" in test_case.prompt


def test_parse_test_case_yaml(evaluator):
    evaluator_instance, test_cases_dir, _ = evaluator
    test_file = test_cases_dir / "test2.yaml"
    yaml_content = {
        "category": "Coding",
        "difficulty": "Medium",
        "prompt": "Write a function to reverse a string",
        "expectations": ["Correct implementation"]
    }
    with open(test_file, "w") as f:
        yaml.dump(yaml_content, f)
    
    test_case = evaluator_instance._parse_test_case(test_file)
    assert test_case.category == "Coding"
    assert len(test_case.expectations) == 1


# --- Logic & Security Tests ---

def test_pii_scanner(evaluator):
    evaluator_instance, _, _ = evaluator
    text_with_email = "Contact me at john.doe@example.com"
    found, types = evaluator_instance._pii_scan(text_with_email)
    assert found is True
    assert "email" in types


def test_score_clamping(evaluator, mocker):
    """Ensure scores outside 0-1 range are normalized."""
    evaluator_instance, _, _ = evaluator
    test_case = TestCase(name="clamp", category="G", difficulty="E", prompt="P")
    
    # Target the get_model function in the models module
    with patch('ai_evaluation.models.get_model') as mock_get_model:
        mock_model = MagicMock()
        mock_get_model.return_value = mock_model
        
        # Test upper bound
        mock_model.call.return_value = ('{"score": 1.5, "reasoning": "High"}', 1, 1)
        score, _ = evaluator_instance.judge_response(test_case, "resp")
        assert score == 1.0
        
        # Test lower bound
        mock_model.call.return_value = ('{"score": -0.5, "reasoning": "Low"}', 1, 1)
        score, _ = evaluator_instance.judge_response(test_case, "resp")
        assert score == 0.0


# --- System Integration Tests ---

def test_run_suite_and_export(evaluator, results_dir, test_cases_dir):
    evaluator_instance, _, _ = evaluator
    test_file = test_cases_dir / "test1.txt"
    test_file.write_text("Category: G\nDifficulty: E\n\nPrompt")
    
    evaluator_instance.run_suite(model_ids=["simulated:default"], parallel=False)
    evaluator_instance.export()
    
    assert (results_dir / "latest_results.json").exists()
    assert len(list(results_dir.glob("run_*.json"))) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
