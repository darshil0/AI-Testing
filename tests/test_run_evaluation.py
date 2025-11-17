import pytest
import os
import json
import csv
from pathlib import Path
from ai_evaluation.run_evaluation import AIEvaluator
from pathlib import Path
from unittest.mock import MagicMock


@pytest.fixture
def evaluator(mocker):
    """A fixture that provides a mocked AIEvaluator instance."""
    mocker.patch("pathlib.Path.mkdir")
    mocker.patch("yaml.safe_load", return_value={
        "max_tokens": 2000,
        "temperature": 0.7,
        "timeout_seconds": 60,
    })
    mocker.patch("builtins.open", mocker.mock_open())
    return AIEvaluator()


def test_aievaluator_initialization(evaluator):
    """Test that the AIEvaluator class can be initialized."""
    assert evaluator is not None

def test_export_results(tmp_path):
    """Test exporting results to CSV and JSON formats."""
    # Setup temporary directories
    test_cases_dir = tmp_path / "test_cases"
    results_dir = tmp_path / "results"
    test_cases_dir.mkdir()
    results_dir.mkdir()

    # Create a dummy test case
    (test_cases_dir / "test1.txt").write_text("What is 2+2?")

    # Initialize evaluator and run evaluation
    evaluator = AIEvaluator(
        test_cases_dir=str(test_cases_dir),
        results_dir=str(results_dir),
    )
    evaluator.run_evaluation(model_type="simulated")

    # Test JSON export
    json_export_path_str = evaluator.export_results("json")
    assert json_export_path_str is not None
    json_export_path = Path(json_export_path_str)
    assert json_export_path.exists()
    with open(json_export_path, "r") as f:
        json_data = json.load(f)
    assert len(json_data) == 1
    assert json_data[0]["test_case_name"] == "test1"
    assert "simulated" in json_data[0]["metadata"]["model_type"]

    # Test CSV export
    csv_export_path_str = evaluator.export_results("csv")
    assert csv_export_path_str is not None
    csv_export_path = Path(csv_export_path_str)
    assert csv_export_path.exists()
    with open(csv_export_path, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert "test_case_name" in header
        assert "response" in header
        data = list(reader)
    assert len(data) == 1
    assert "test1" in data[0]
