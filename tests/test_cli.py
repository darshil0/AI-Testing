from unittest.mock import MagicMock, patch

from ai_evaluation.run_evaluation import AIEvaluator, main


def test_main_cli_success(tmp_path):
    config_p = tmp_path / "config.yaml"
    tc_p = tmp_path / "test_cases"
    res_p = tmp_path / "results"
    tc_p.mkdir()
    res_p.mkdir()

    config_p.write_text(
        f"""
directories:
  test_cases: "{tc_p.as_posix()}"
  results: "{res_p.as_posix()}"
""",
        encoding="utf-8",
    )

    (tc_p / "case.txt").write_text(
        "Category: General\nDifficulty: Easy\n\nPrompt content", encoding="utf-8"
    )

    test_args = [
        "run-evaluation",
        "--config",
        str(config_p),
        "--models",
        "simulated:default",
    ]
    with (
        patch("sys.argv", test_args),
        patch.object(
            AIEvaluator,
            "judge_response",
            return_value=(0.95, "Good response", 10, 5, 0.0001),
        ),
    ):
        main()


def test_main_cli_missing_config():
    test_args = ["run-evaluation", "--config", "non_existent_config.yaml"]
    with patch("sys.argv", test_args):
        exit_code = main()
        assert exit_code == 2


def test_load_from_hf(tmp_path):
    evaluator = AIEvaluator()
    evaluator.test_cases_dir = tmp_path

    mock_item = {"question": "What is 2+2?"}
    mock_ds = MagicMock()
    mock_ds.take.return_value = [mock_item]

    with (
        patch.dict("sys.modules", {"datasets": MagicMock()}),
        patch("datasets.load_dataset", return_value=mock_ds, create=True),
    ):
        written_count = evaluator.load_from_hf("test_ds", count=1)
        mock_ds.take.assert_called_once_with(1)
        written = list(tmp_path.glob("hf_*.txt"))
        assert len(written) == 1
        assert written_count == 1
