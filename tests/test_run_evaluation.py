import pytest
import json
from pathlib import Path
import yaml
from ai_evaluation.run_evaluation import AIEvaluator, EvaluationResult
from unittest.mock import call, mock_open

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
        "pii_patterns": {"email": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"},
        "judge": {"model": "simulated:default"},
        "judge_personas": {"default": "You are a default judge."},
        "pricing": {},
    }
    return config

@pytest.fixture
def evaluator(mocker, mock_config):
    """A fixture that provides a properly mocked AIEvaluator instance."""
    config_path = Path("dummy_config.yaml")

    mocker.patch("builtins.open", mock_open(read_data=yaml.dump(mock_config)))
    mocker.patch("yaml.safe_load", return_value=mock_config)

    evaluator_instance = AIEvaluator(config_path=str(config_path))

    mock_result = EvaluationResult(
        test_case_name="test1",
        category="General",
        difficulty="Easy",
        model_type="simulated:default",
        prompt="What is 2+2?",
        response="Simulated response.",
        duration_seconds=0.1,
        tokens_input=5,
        tokens_output=10,
        estimated_cost=0.0,
        judge_score=0.9,
        judge_reasoning="Good response."
    )
    mocker.patch.object(evaluator_instance, 'process_one', return_value=mock_result)

    return evaluator_instance

def test_aievaluator_initialization(evaluator, mock_config):
    """Test that the AIEvaluator class can be initialized correctly."""
    assert evaluator is not None
    assert evaluator.config == mock_config
    assert str(evaluator.test_cases_dir) == mock_config["directories"]["test_cases"]

def test_run_suite_and_export(evaluator, mock_config, mocker):
    """Test running an evaluation suite and properly exporting the results."""
    test_cases_dir = Path(mock_config["directories"]["test_cases"])
    (test_cases_dir / "test1.txt").write_text("Category: General\nDifficulty: Easy\n\nWhat is 2+2?")

    evaluator.run_suite(model_ids=["simulated:default"], parallel=False)

    assert len(evaluator.results) == 1
    result_data = [r.model_dump() for r in evaluator.results]
    assert result_data[0]["test_case_name"] == "test1"

    # Mock the file writing to verify the export method's behavior
    mock_file = mock_open()
    mocker.patch("builtins.open", mock_file)
    mock_json_dump = mocker.patch("json.dump")

    evaluator.export()

    # Verify that `open` was called for both the latest and the timestamped report
    results_dir = Path(mock_config["directories"]["results"])
    latest_path = results_dir / "latest_results.json"

    # Check that the file handles were opened for writing
    assert any(c == call(latest_path, "w") for c in mock_file.call_args_list)
    assert any("run_" in str(c.args[0]) and c.args[1] == "w" for c in mock_file.call_args_list)

    # Verify that `json.dump` was called with the correct data
    mock_json_dump.assert_any_call(result_data, mock_file(), indent=2)
