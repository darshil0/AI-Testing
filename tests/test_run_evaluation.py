import pytest
import json
from pathlib import Path
import yaml
from ai_evaluation.run_evaluation import AIEvaluator, EvaluationResult, TestCase
from unittest.mock import call, mock_open, MagicMock, patch

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
    
    # Write config to file
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    
    evaluator_instance = AIEvaluator(config_path=str(config_path))

    # Mock the process_one method to return a valid result based on the model
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


def test_aievaluator_initialization(evaluator, mock_config):
    """Test that the AIEvaluator class can be initialized correctly."""
    evaluator_instance, test_cases_dir, results_dir = evaluator
    config, _, _ = mock_config
    
    assert evaluator_instance is not None
    assert evaluator_instance.config == config
    assert evaluator_instance.test_cases_dir.name == test_cases_dir.name


def test_parse_test_case_txt(evaluator):
    """Test parsing a .txt test case file."""
    evaluator_instance, test_cases_dir, _ = evaluator
    
    # Create a test case file
    test_file = test_cases_dir / "test1.txt"
    test_file.write_text("Category: Reasoning\nDifficulty: Hard\n\nWhat is 2+2?")
    
    test_case = evaluator_instance._parse_test_case(test_file)
    
    assert test_case.name == "test1"
    assert test_case.category == "Reasoning"
    assert test_case.difficulty == "Hard"
    assert "What is 2+2?" in test_case.prompt


def test_parse_test_case_yaml(evaluator):
    """Test parsing a .yaml test case file."""
    evaluator_instance, test_cases_dir, _ = evaluator
    
    # Create a YAML test case file
    test_file = test_cases_dir / "test2.yaml"
    yaml_content = {
        "category": "Coding",
        "difficulty": "Medium",
        "prompt": "Write a function to reverse a string",
        "expectations": ["Correct implementation", "Handle edge cases"]
    }
    with open(test_file, "w") as f:
        yaml.dump(yaml_content, f)
    
    test_case = evaluator_instance._parse_test_case(test_file)
    
    assert test_case.name == "test2"
    assert test_case.category == "Coding"
    assert test_case.difficulty == "Medium"
    assert "reverse" in test_case.prompt.lower()
    assert len(test_case.expectations) == 2


def test_pii_scanner(evaluator):
    """Test PII detection functionality."""
    evaluator_instance, _, _ = evaluator
    
    # Test with email
    text_with_email = "Contact me at john.doe@example.com for details"
    found, types = evaluator_instance._pii_scan(text_with_email)
    assert found == True
    assert "email" in types
    
    # Test without PII
    text_clean = "This is a clean text without any personal information"
    found, types = evaluator_instance._pii_scan(text_clean)
    assert found == False
    assert len(types) == 0


def test_run_suite_and_export(evaluator, mock_config, mocker):
    """Test running an evaluation suite and properly exporting the results."""
    evaluator_instance, test_cases_dir, results_dir = evaluator
    config, _, _ = mock_config
    
    # Create a test case file
    test_file = test_cases_dir / "test1.txt"
    test_file.write_text("Category: General\nDifficulty: Easy\n\nWhat is 2+2?")
    
    # Run the suite
    evaluator_instance.run_suite(model_ids=["simulated:default"], parallel=False)
    
    # Verify results
    assert len(evaluator_instance.results) == 1
    result = evaluator_instance.results[0]
    assert result.test_case_name == "test1"
    assert result.model_type == "simulated:default"
    assert result.judge_score == 0.9
    
    # Test export
    evaluator_instance.export()
    
    # Check that files were created
    latest_file = results_dir / "latest_results.json"
    assert latest_file.exists()
    
    # Verify content
    with open(latest_file, "r") as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["test_case_name"] == "test1"


def test_judge_response(evaluator, mocker):
    """Test the judge_response functionality."""
    evaluator_instance, _, _ = evaluator
    
    # Create a test case
    test_case = TestCase(
        name="test_judge",
        category="General",
        difficulty="Easy",
        prompt="What is the capital of France?",
        expectations=["Mention Paris", "Be accurate"]
    )
    
    # Mock the judge model's response
    mock_judge_response = '{"score": 0.95, "reasoning": "Excellent answer, mentions Paris correctly"}'
    
    # Patch where the function is LOOKED UP, not where it is defined.
    with patch('ai_evaluation.run_evaluation.get_model') as mock_get_model:
        mock_model = MagicMock()
        mock_model.call.return_value = (mock_judge_response, 10, 20)
        mock_get_model.return_value = mock_model
        
        score, reasoning = evaluator_instance.judge_response(
            test_case,
            "The capital of France is Paris",
            persona="default"
        )
        
        assert score == 0.95
        assert "Paris" in reasoning


def test_empty_test_cases_directory(evaluator, mocker, capsys):
    """Test handling of empty test cases directory."""
    evaluator_instance, test_cases_dir, _ = evaluator
    
    # Ensure directory is empty
    for file in test_cases_dir.iterdir():
        file.unlink()
    
    # Mock console.print to avoid actual output
    mock_console = mocker.patch('ai_evaluation.run_evaluation.console')
    
    # Run suite should handle gracefully
    evaluator_instance.run_suite(model_ids=["simulated:default"], parallel=False)
    
    # Should have printed a warning
    mock_console.print.assert_called()
    assert len(evaluator_instance.results) == 0


def test_score_clamping(evaluator, mocker):
    """Test that judge scores are clamped to 0.0-1.0 range."""
    evaluator_instance, _, _ = evaluator
    
    test_case = TestCase(
        name="test_clamp",
        category="General",
        difficulty="Easy",
        prompt="Test prompt"
    )
    
    # Mock judge returning out-of-range scores
    with patch('ai_evaluation.models.get_model') as mock_get_model:
        mock_model = MagicMock()
        
        # Test score > 1.0
        mock_model.call.return_value = ('{"score": 1.5, "reasoning": "Test"}', 10, 20)
        mock_get_model.return_value = mock_model
        
        score, _ = evaluator_instance.judge_response(test_case, "response")
        assert score <= 1.0
        
        # Test score < 0.0
        mock_model.call.return_value = ('{"score": -0.5, "reasoning": "Test"}', 10, 20)
        score, _ = evaluator_instance.judge_response(test_case, "response")
        assert score >= 0.0


def test_malformed_test_case(evaluator):
    """Test handling of malformed test case files."""
    evaluator_instance, test_cases_dir, _ = evaluator
    
    # Create a malformed test case
    test_file = test_cases_dir / "malformed.txt"
    test_file.write_text("This is malformed\nNo proper structure")
    
    # Should not crash, should return a valid TestCase
    test_case = evaluator_instance._parse_test_case(test_file)
    
    assert test_case.name == "malformed"
    assert test_case.prompt is not None


def test_multiple_models(evaluator):
    """Test running evaluation with multiple models."""
    evaluator_instance, test_cases_dir, _ = evaluator
    
    # Create test case
    test_file = test_cases_dir / "multi_test.txt"
    test_file.write_text("Category: General\nDifficulty: Easy\n\nTest prompt")
    
    # Run with multiple models
    evaluator_instance.run_suite(
        model_ids=["simulated:default", "simulated:model2"],
        parallel=False
    )
    
    # Should have results for both models
    assert len(evaluator_instance.results) == 2
    model_types = [r.model_type for r in evaluator_instance.results]
    assert "simulated:default" in model_types
    assert "simulated:model2" in model_types


def test_export_creates_timestamped_file(evaluator):
    """Test that export creates a timestamped file."""
    evaluator_instance, test_cases_dir, results_dir = evaluator
    
    # Create dummy result
    evaluator_instance.results = [
        EvaluationResult(
            test_case_name="test",
            category="General",
            difficulty="Easy",
            model_type="simulated:default",
            prompt="test",
            response="response",
            duration_seconds=1.0
        )
    ]
    
    # Export
    evaluator_instance.export()
    
    # Check timestamped files exist (should start with "run_")
    run_files = list(results_dir.glob("run_*.json"))
    assert len(run_files) >= 1
    assert (results_dir / "latest_results.json").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
