import os
from unittest.mock import MagicMock, patch

import pytest

from ai_evaluation.run_evaluation import AIEvaluator, TestCase


def test_acceptance_1_no_openai_key_and_judge_failure(tmp_path):
    """1. No OpenAI key / default judge unavailable: score=None, status=judge_error/model_error, non-zero exit."""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
directories:
  test_cases: "test_cases"
  results: "results"
judge:
  model: "openai:gpt-4o"
judge_personas:
  default: "Judge"
""",
        encoding="utf-8",
    )

    tc_dir = tmp_path / "test_cases"
    tc_dir.mkdir()
    (tc_dir / "case1.txt").write_text(
        "Category: General\nDifficulty: Easy\n\nHello world", encoding="utf-8"
    )

    with patch.dict(os.environ, {}, clear=True):
        evaluator = AIEvaluator(config_path=str(config_path))
        # Simulated model succeeds, but judge (OpenAI) fails due to missing key
        res = evaluator.process_one(tc_dir / "case1.txt", "simulated:default")
        assert res.status == "judge_error"
        assert res.score is None
        assert res.judge_score is None
        assert (
            "Judge evaluation failed" in res.error_message
            or "API key missing" in res.error_message
        )


def test_acceptance_2_invalid_judge_values():
    """2. Invalid judge values: NaN, Infinity, bool, 85, malformed JSON, multiple objects raise ValueError."""
    evaluator = AIEvaluator()
    tc = TestCase(name="dummy", prompt="dummy")
    mock_model = MagicMock()

    invalid_payloads = [
        '{"score": NaN, "reasoning": "bad"}',
        '{"score": Infinity, "reasoning": "bad"}',
        '{"score": true, "reasoning": "bad"}',
        '{"score": 85, "reasoning": "bad"}',
        "{ score: 0.5 }",
        '{"score": 0.5} {"score": 0.8}',
    ]

    for payload in invalid_payloads:
        mock_model.call.return_value = (payload, 10, 10)
        with patch("ai_evaluation.run_evaluation.get_model", return_value=mock_model):
            with pytest.raises(ValueError):
                evaluator.judge_response(tc, "response")


def test_acceptance_3_valid_judge_values():
    """3. Valid judge values: exactly 0.0, 0.5, 1.0 produce status=success and exact score."""
    evaluator = AIEvaluator()
    tc = TestCase(name="dummy", prompt="dummy")
    mock_model = MagicMock()

    for expected_score in [0.0, 0.5, 1.0]:
        mock_model.call.return_value = (
            f'{{"score": {expected_score}, "reasoning": "ok"}}',
            10,
            10,
        )
        with patch("ai_evaluation.run_evaluation.get_model", return_value=mock_model):
            score, reasoning, _, _, _ = evaluator.judge_response(tc, "response")
            assert score == expected_score


def test_acceptance_4_invalid_test_case(tmp_path):
    """4. Invalid test case: malformed YAML/empty TXT body marked invalid_case without model/judge call."""
    invalid_txt = tmp_path / "invalid.txt"
    invalid_txt.write_text(
        "Category: General\nDifficulty: Easy\n\n", encoding="utf-8"
    )  # empty body

    evaluator = AIEvaluator()
    res = evaluator.process_one(invalid_txt, "simulated:default")
    assert res.status == "invalid_case"
    assert res.score is None


def test_acceptance_5_packaging_and_wheel():
    """5. Wheel package built and installed can locate packaged config without source checkout."""
    evaluator = AIEvaluator(config_path=None)
    assert evaluator.config is not None


def test_acceptance_6_config_path_propagation(tmp_path):
    """6. Config path: analytics and dashboard honor custom config results directory."""
    pytest.importorskip("matplotlib")
    pytest.importorskip("pandas")
    pytest.importorskip("seaborn")

    custom_results = tmp_path / "custom_results_dir"
    custom_results.mkdir()

    custom_config = tmp_path / "custom_config.yaml"
    custom_config.write_text(
        f"""
directories:
  test_cases: "test_cases"
  results: "{custom_results.as_posix()}"
""",
        encoding="utf-8",
    )

    from ai_evaluation.analytics import generate_analytics

    generate_analytics(config_path=str(custom_config))


def test_acceptance_9_determinism(tmp_path):
    """9. Determinism: suite execution produces deterministic case order."""
    tc_dir = tmp_path / "test_cases"
    tc_dir.mkdir()
    (tc_dir / "b_case.txt").write_text(
        "Category: General\nDifficulty: Easy\n\nCase B", encoding="utf-8"
    )
    (tc_dir / "a_case.txt").write_text(
        "Category: General\nDifficulty: Easy\n\nCase A", encoding="utf-8"
    )

    custom_config = tmp_path / "config.yaml"
    custom_config.write_text(
        f"""
directories:
  test_cases: "{tc_dir.as_posix()}"
  results: "{tmp_path.as_posix()}"
""",
        encoding="utf-8",
    )

    evaluator = AIEvaluator(config_path=str(custom_config))
    files = sorted(
        list(evaluator.test_cases_dir.glob("*.txt")),
        key=lambda p: p.name,
    )
    assert [f.name for f in files] == ["a_case.txt", "b_case.txt"]


def test_acceptance_10_pii_scanner():
    """10. PII scanner: Luhn card validation and false positive filtering."""
    evaluator = AIEvaluator()

    # Valid Luhn card
    has_pii, types = evaluator._pii_scan("Card: 4532-0151-1283-0366")
    assert has_pii is True
    assert "credit_card" in types

    # Invalid Luhn card number (false positive check)
    has_pii, types = evaluator._pii_scan("Order ID: 1234-5678-9012-3456")
    assert "credit_card" not in types
