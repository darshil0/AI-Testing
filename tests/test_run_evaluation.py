import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys
import yaml
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
        "max_workers": 2,
        "pii_patterns": {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "phone": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "social_security": r"\b\d{3}-\d{2}-\d{4}\b",
        },
        "judge": {"model": "simulated:default"},
        "judge_personas": {
            "default": "You are a default judge.",
            "critic": "You are a critical judge.",
            "auditor": "You are a safety auditor.",
        },
        "pricing": {"simulated": {"input": 0.0, "output": 0.0}},
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
            judge_reasoning="Good response, correct answer.",
        )

    mocker.patch.object(evaluator_instance, "process_one", side_effect=mock_process_one)
    return evaluator_instance, test_cases_dir, results_dir


# --- Initialization Tests ---


def test_aievaluator_initialization(evaluator, mock_config):
    evaluator_instance, test_cases_dir, _ = evaluator
    config, _, _ = mock_config

    assert evaluator_instance is not None
    assert evaluator_instance.config["max_workers"] == 2
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
        "expectations": ["Correct implementation"],
    }
    with open(test_file, "w") as f:
        yaml.dump(yaml_content, f)

    test_case = evaluator_instance._parse_test_case(test_file)
    assert test_case.category == "Coding"
    assert len(test_case.expectations) == 1


def test_parse_test_case_yml(evaluator):
    evaluator_instance, test_cases_dir, _ = evaluator
    test_file = test_cases_dir / "test3.yml"
    yaml_content = {
        "category": "Writing",
        "difficulty": "Easy",
        "prompt": "Write a poem",
        "expectations": ["Rhyming"],
    }
    with open(test_file, "w") as f:
        yaml.dump(yaml_content, f)

    test_case = evaluator_instance._parse_test_case(test_file)
    assert test_case.category == "Writing"
    assert len(test_case.expectations) == 1


def test_parse_test_case_invalid_yaml(evaluator):
    evaluator_instance, test_cases_dir, _ = evaluator
    test_file = test_cases_dir / "test_invalid.yaml"
    # Write corrupt YAML syntax
    test_file.write_text("category: : : [corrupt yaml")

    test_case = evaluator_instance._parse_test_case(test_file)
    assert test_case.name == "test_invalid"
    assert test_case.category == "Error"
    assert "Error parsing test case" in test_case.prompt


# --- Logic, Security & PII Tests ---


def test_pii_scanner_all_patterns(evaluator):
    evaluator_instance, _, _ = evaluator

    # Email
    found, types = evaluator_instance._pii_scan("Contact john@demo.com")
    assert found is True
    assert "email" in types

    # Phone
    found, types = evaluator_instance._pii_scan("Call me at 555-123-4567")
    assert found is True
    assert "phone" in types

    # CC
    found, types = evaluator_instance._pii_scan("Card: 1234-5678-9012-3456")
    assert found is True
    assert "credit_card" in types

    # SSN
    found, types = evaluator_instance._pii_scan("SSN: 000-12-3456")
    assert found is True
    assert "social_security" in types

    # Safe text
    found, types = evaluator_instance._pii_scan(
        "This is a safe sentence without any private details."
    )
    assert found is False
    assert len(types) == 0


def test_pii_scanner_invalid_regex(evaluator):
    evaluator_instance, _, _ = evaluator
    # Artificially inject an invalid pattern in configuration
    evaluator_instance.config["pii_patterns"]["invalid"] = "[["

    # Should handle re.error gracefully and not crash
    found, types = evaluator_instance._pii_scan("test")
    assert found is False


def test_score_clamping(evaluator, mocker):
    """Ensure scores outside 0-1 range are normalized."""
    evaluator_instance, _, _ = evaluator
    test_case = TestCase(name="clamp", category="G", difficulty="E", prompt="P")

    # Target the get_model function where it is looked up in run_evaluation
    target_module = sys.modules["ai_evaluation.run_evaluation"]
    with patch.object(target_module, "get_model") as mock_get_model:
        mock_model = MagicMock()
        mock_get_model.return_value = mock_model

        # Test upper bound
        mock_model.call.return_value = (
            '{"score": 1.5, "reasoning": "High"}',
            1,
            1,
        )
        score, _ = evaluator_instance.judge_response(test_case, "resp")
        assert score == 1.0

        # Test lower bound
        mock_model.call.return_value = (
            '{"score": -0.5, "reasoning": "Low"}',
            1,
            1,
        )
        score, _ = evaluator_instance.judge_response(test_case, "resp")
        assert score == 0.0


def test_judge_response_malformed_json(evaluator, mocker):
    evaluator_instance, _, _ = evaluator
    test_case = TestCase(name="malformed", category="G", difficulty="E", prompt="P")

    target_module = sys.modules["ai_evaluation.run_evaluation"]
    with patch.object(target_module, "get_model") as mock_get_model:
        mock_model = MagicMock()
        mock_get_model.return_value = mock_model

        # Completely malformed response
        mock_model.call.value = ("this is not json at all", 1, 1)
        # Using mock_model.call.side_effect/return_value
        mock_model.call.return_value = ("this is not json at all", 1, 1)
        score, reasoning = evaluator_instance.judge_response(test_case, "resp")
        assert score == 0.5
        assert "Could not parse judge response" in reasoning


# --- System Integration & Suite Tests ---


def test_run_suite_and_export(evaluator):
    evaluator_instance, test_cases_dir, results_dir = evaluator
    test_file = test_cases_dir / "test1.txt"
    test_file.write_text("Category: G\nDifficulty: E\n\nPrompt")

    evaluator_instance.run_suite(model_ids=["simulated:default"], parallel=False)
    evaluator_instance.export()

    assert (results_dir / "latest_results.json").exists()
    assert len(list(results_dir.glob("run_*.json"))) >= 1


def test_run_suite_empty_directory(evaluator):
    evaluator_instance, test_cases_dir, _ = evaluator
    # Ensure directory is empty
    for f in test_cases_dir.glob("*"):
        f.unlink()

    # Running suite on empty directory should not crash
    evaluator_instance.run_suite(model_ids=["simulated:default"], parallel=False)
    assert len(evaluator_instance.results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
