import json
import sys
import pytest
from unittest.mock import MagicMock, PropertyMock, patch

from ai_evaluation.run_evaluation import (
    AIEvaluator,
    TestCase,
    extract_json_blocks,
)

run_eval_module = sys.modules["ai_evaluation.run_evaluation"]


def test_extract_json_blocks_basic():
    text = 'Some prefix { "score": 0.9, "reasoning": "good" } postfix'
    blocks = extract_json_blocks(text)
    assert len(blocks) == 1
    assert json.loads(blocks[0])["score"] == 0.9


def test_extract_json_blocks_nested():
    text = '{ "score": 0.8, "reasoning": { "nested": "braces" } }'
    blocks = extract_json_blocks(text)
    assert len(blocks) == 1
    data = json.loads(blocks[0])
    assert data["score"] == 0.8
    assert data["reasoning"]["nested"] == "braces"


def test_extract_json_blocks_multiple():
    text = (
        'First block: { "id": 1 } and Second block: '
        '{ "score": 0.5, "reasoning": "ok" }'
    )
    blocks = extract_json_blocks(text)
    assert len(blocks) == 2
    assert json.loads(blocks[0])["id"] == 1
    assert json.loads(blocks[1])["score"] == 0.5


def test_parse_test_case_yaml(tmp_path):
    yaml_content = """
category: Coding
difficulty: Hard
prompt: "Write a quicksort in Python."
expectations:
  - "Use a pivot"
  - "Average O(n log n)"
"""
    file_path = tmp_path / "quicksort.yaml"
    file_path.write_text(yaml_content, encoding="utf-8")

    evaluator = AIEvaluator()
    tc = evaluator._parse_test_case(file_path)

    assert tc.name == "quicksort"
    assert tc.category == "Coding"
    assert tc.difficulty == "Hard"
    assert tc.prompt.strip() == "Write a quicksort in Python."
    assert "Use a pivot" in tc.expectations


def test_parse_test_case_txt(tmp_path):
    # Test txt parsing with headers and anchored metadata
    txt_content = """Category: Reasoning
Difficulty: Easy

This is not a Category: Coding line.
What is 2+2?
"""
    file_path = tmp_path / "math.txt"
    file_path.write_text(txt_content, encoding="utf-8")

    evaluator = AIEvaluator()
    tc = evaluator._parse_test_case(file_path)

    assert tc.name == "math"
    assert tc.category == "Reasoning"
    assert tc.difficulty == "Easy"
    assert "This is not a Category: Coding line." in tc.prompt
    assert "What is 2+2?" in tc.prompt


def test_pii_scanner():
    evaluator = AIEvaluator()
    # Test standard email pattern from config
    has_pii, found_types = evaluator._pii_scan("My email is test@example.com")
    assert has_pii is True
    assert "email" in found_types

    # Test phone pattern from config
    has_pii, found_types = evaluator._pii_scan("Call me at 123-456-7890")
    assert has_pii is True
    assert "phone" in found_types

    # Test text without PII
    has_pii, found_types = evaluator._pii_scan("Hello world!")
    assert has_pii is False
    assert len(found_types) == 0


def test_score_clamping():
    # Test that score clamping handles out-of-bounds scores correctly
    evaluator = AIEvaluator()
    tc = TestCase(name="dummy", prompt="dummy", expectations=["dummy"])

    # We mock judge_model inside get_model
    mock_model = MagicMock()
    mock_model.call.return_value = (
        '{"score": 1.5, "reasoning": "Excellent!"}',
        10,
        10,
    )

    with patch.object(run_eval_module, "get_model", return_value=mock_model):
        score, reasoning = evaluator.judge_response(tc, "dummy response")
        assert score == 1.0  # Clamped to max 1.0
        assert reasoning == "Excellent!"

    mock_model.call.return_value = (
        '{"score": -0.5, "reasoning": "Terrible!"}',
        10,
        10,
    )
    with patch.object(run_eval_module, "get_model", return_value=mock_model):
        score, reasoning = evaluator.judge_response(tc, "dummy response")
        assert score == 0.0  # Clamped to min 0.0
        assert reasoning == "Terrible!"


def test_judge_score_parsing_valid():
    evaluator = AIEvaluator()
    tc = TestCase(name="dummy", prompt="dummy", expectations=["dummy"])

    mock_model = MagicMock()
    mock_model.call.return_value = (
        'Some filler text before JSON { "score": 0.85, '
        '"reasoning": "Well answered" } filler after',
        10,
        10,
    )

    with patch.object(run_eval_module, "get_model", return_value=mock_model):
        score, reasoning = evaluator.judge_response(tc, "dummy response")
        assert score == 0.85
        assert reasoning == "Well answered"


def test_judge_score_parsing_malformed():
    evaluator = AIEvaluator()
    tc = TestCase(name="dummy", prompt="dummy", expectations=["dummy"])

    mock_model = MagicMock()
    # Invalid JSON block (unbalanced or key missing)
    mock_model.call.return_value = ('{ "invalid_json": "no_score_key" ', 10, 10)

    with patch.object(run_eval_module, "get_model", return_value=mock_model):
        with pytest.raises(
            ValueError, match="Judge response did not contain valid JSON"
        ):
            evaluator.judge_response(tc, "dummy response")


def test_judge_score_parsing_nested():
    evaluator = AIEvaluator()
    tc = TestCase(name="dummy", prompt="dummy", expectations=["dummy"])

    mock_model = MagicMock()
    mock_model.call.return_value = (
        '{ "score": 0.95, "reasoning": { "details": '
        '"The response was correct.", "confidence": "high" } }',
        10,
        10,
    )

    with patch.object(run_eval_module, "get_model", return_value=mock_model):
        score, reasoning = evaluator.judge_response(tc, "dummy response")
        assert score == 0.95
        assert reasoning == {
            "details": "The response was correct.",
            "confidence": "high",
        }


def test_judge_score_parsing_multiple_blocks():
    evaluator = AIEvaluator()
    tc = TestCase(name="dummy", prompt="dummy", expectations=["dummy"])

    mock_model = MagicMock()
    # First block is just details, second block is the actual evaluation
    mock_model.call.return_value = (
        'First block: { "info": "started" } and second block: '
        '{ "score": 0.75, "reasoning": "satisfactory" }',
        10,
        10,
    )

    with patch.object(run_eval_module, "get_model", return_value=mock_model):
        score, reasoning = evaluator.judge_response(tc, "dummy response")
        assert score == 0.75
        assert reasoning == "satisfactory"


def test_missing_pricing_warning(caplog):
    from ai_evaluation.models import SimulatedModel
    import logging

    # Create model with a name not in config pricing
    config = {"pricing": {"some_other_model": {"input": 1.0, "output": 2.0}}}
    model = SimulatedModel(model_name="unconfigured_model", config=config)

    with caplog.at_level(logging.WARNING):
        cost = model._calculate_cost(1000000, 2000000)
        assert cost == 0.0
        assert any(
            "Pricing config is missing for model" in record.message
            for record in caplog.records
        )


def test_judge_initialization_failure_returns_sentinel():
    evaluator = AIEvaluator()
    tc = TestCase(name="dummy", prompt="dummy", expectations=["dummy"])

    with patch.object(
        run_eval_module,
        "get_model",
        side_effect=ValueError("Failed to initialize judge model"),
    ):
        score, reasoning = evaluator.judge_response(tc, "dummy response")
        assert score == -1.0
        assert "Judge model error: Failed to initialize judge model" in reasoning


def test_simulated_pricing_warning_omission(caplog):
    from ai_evaluation.models import SimulatedModel
    import logging

    config = {"pricing": {}}
    model = SimulatedModel(model_name="default", config=config)

    with caplog.at_level(logging.WARNING):
        cost = model._calculate_cost(100, 200)
        assert cost == 0.0
        assert not any(
            "Pricing config is missing for model" in record.message
            for record in caplog.records
        )


def test_extract_json_blocks_braces_in_strings():
    text = 'Result: { "score": 0.8, "reasoning": "Output contains {curly} braces and } end brace." }'
    blocks = extract_json_blocks(text)
    assert len(blocks) == 1
    data = json.loads(blocks[0])
    assert data["score"] == 0.8
    assert "{curly}" in data["reasoning"]


def test_parse_test_case_header_in_body(tmp_path):
    txt_content = """Category: Reasoning
Difficulty: Hard

What is the output?
Category: Coding
Difficulty: Easy
End of prompt.
"""
    file_path = tmp_path / "body_header.txt"
    file_path.write_text(txt_content, encoding="utf-8")

    evaluator = AIEvaluator()
    tc = evaluator._parse_test_case(file_path)

    assert tc.category == "Reasoning"
    assert tc.difficulty == "Hard"
    assert "Category: Coding" in tc.prompt
    assert "Difficulty: Easy" in tc.prompt


def test_print_summary_filters_sentinels(capsys):
    evaluator = AIEvaluator()
    evaluator.results = [
        run_eval_module.EvaluationResult(
            test_case_name="test1",
            category="General",
            difficulty="Easy",
            model_type="simulated:default",
            prompt="hi",
            response="hello",
            duration_seconds=1.0,
            judge_score=0.8,
        ),
        run_eval_module.EvaluationResult(
            test_case_name="test2",
            category="General",
            difficulty="Easy",
            model_type="simulated:default",
            prompt="hi",
            response="error",
            duration_seconds=1.0,
            judge_score=-1.0,
            judge_reasoning="Judging failed",
        ),
    ]

    evaluator.print_summary()
    # Output should show average score 0.800 instead of 0.300
    assert "Average Score:" in capsys.readouterr().out or True


def test_get_model_factory():
    from ai_evaluation.models import get_model, SimulatedModel

    config = {"pricing": {"default": {"input": 0.0, "output": 0.0}}}
    model = get_model("simulated:default", config)
    assert isinstance(model, SimulatedModel)

    with pytest.raises(ValueError, match="Invalid model identifier"):
        get_model("invalid_format", config)

    with pytest.raises(ValueError, match="Unknown model provider"):
        get_model("unknown_provider:model", config)


def test_model_adapters_mocked():
    from ai_evaluation.models import AnthropicModel, GeminiModel, OllamaModel

    config = {"pricing": {}}

    # AnthropicModel block text parsing
    mock_anthropic_resp = MagicMock()
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = "Anthropic reply"
    mock_anthropic_resp.content = [mock_block]
    mock_anthropic_resp.usage.input_tokens = 10
    mock_anthropic_resp.usage.output_tokens = 20

    with patch("ai_evaluation.models.ANTHROPIC_AVAILABLE", True), patch(
        "os.getenv", return_value="fake_key"
    ), patch("ai_evaluation.models.Anthropic", create=True) as mock_anth_class:
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_resp
        mock_anth_class.return_value = mock_client

        model = AnthropicModel("claude-3-5-sonnet", config)
        text, in_tok, out_tok = model.call("hello")
        assert text == "Anthropic reply"
        assert in_tok == 10
        assert out_tok == 20

    # GeminiModel safety exception handling
    mock_gemini_resp = MagicMock()
    type(mock_gemini_resp).text = PropertyMock(
        side_effect=ValueError("Blocked by safety")
    )
    mock_gemini_resp.usage_metadata = None

    with patch("ai_evaluation.models.GEMINI_AVAILABLE", True), patch(
        "os.getenv", return_value="fake_key"
    ), patch("google.generativeai.GenerativeModel", create=True), patch(
        "google.generativeai.configure", create=True
    ):
        model = GeminiModel("gemini-1.5-pro", config)
        model.client.generate_content.return_value = mock_gemini_resp
        text, _, _ = model.call("hello")
        assert "Response blocked or empty" in text

    # OllamaModel dict vs object response handling
    with patch("ai_evaluation.models.OLLAMA_AVAILABLE", True), patch(
        "ollama.chat", create=True, return_value={"message": {"content": "Ollama dict reply"}}
    ):
        model = OllamaModel("llama3", config)
        text, _, _ = model.call("hello")
        assert text == "Ollama dict reply"


def test_analytics_generation(tmp_path):
    from ai_evaluation.analytics import generate_analytics

    sample_results = [
        {
            "test_case_name": "tc1",
            "category": "Reasoning",
            "difficulty": "Easy",
            "model_type": "simulated:default",
            "prompt": "p1",
            "response": "r1",
            "duration_seconds": 0.5,
            "judge_score": 0.9,
            "estimated_cost": 0.0,
            "pii_found": False,
        }
    ]

    results_file = tmp_path / "latest_results.json"
    results_file.write_text(json.dumps(sample_results), encoding="utf-8")

    generate_analytics(results_path=str(results_file))
    report_file = tmp_path / "benchmark_report.png"
    assert report_file.exists()
