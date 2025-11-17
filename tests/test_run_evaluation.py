import pytest
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
    assert evaluator.max_tokens == 2000
    assert evaluator.temperature == 0.7


def test_load_test_cases(mocker, evaluator):
    """Test that test cases are loaded correctly."""
    mocker.patch("builtins.open", mocker.mock_open(read_data="Test case content"))
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.glob", return_value=[Path("test_cases/test_case.txt")])

    test_cases = evaluator.load_test_cases()

    assert len(test_cases) == 1
    assert test_cases[0]["name"] == "test_case"
    assert test_cases[0]["content"] == "Test case content"


def test_save_result(mocker, evaluator):
    """Test that results are saved correctly."""
    mocked_open = mocker.patch("builtins.open", mocker.mock_open())

    evaluator.save_result("test_case", "Test content", "Test response")

    mocked_open.assert_called_once()


def test_call_openai(mocker, evaluator):
    """Test the OpenAI API call."""
    mocker.patch("os.getenv", return_value="fake_api_key")
    mock_openai_module = mocker.MagicMock()

    # Create a MagicMock for the choice object
    mock_choice = MagicMock()
    mock_choice.message.content = "Test response"

    mock_openai_module.ChatCompletion.create.return_value.choices = [mock_choice]
    mock_openai_module.APIError = Exception
    mocker.patch.dict("sys.modules", {"openai": mock_openai_module})

    response = evaluator.call_openai("Test case")

    assert response == "Test response"


def test_call_anthropic(mocker, evaluator):
    """Test the Anthropic API call."""
    mocker.patch("os.getenv", return_value="fake_api_key")
    mock_anthropic_module = mocker.MagicMock()
    mock_anthropic_client = mock_anthropic_module.Anthropic.return_value
    mock_anthropic_client.messages.create.return_value.content = [mocker.Mock(text="Test response")]
    mock_anthropic_module.APIError = Exception
    mocker.patch.dict("sys.modules", {"anthropic": mock_anthropic_module})

    response = evaluator.call_anthropic("Test case")

    assert response == "Test response"
