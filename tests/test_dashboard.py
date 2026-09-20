import json
from unittest.mock import MagicMock, patch

import pytest

from ai_evaluation.dashboard import show_dashboard

pytest.importorskip("streamlit")
pytest.importorskip("pandas")


def test_dashboard_flow(tmp_path):
    results_dir = tmp_path / "results"
    results_dir.mkdir()

    run_file = results_dir / "run_20260101_120000.json"
    sample_data = [
        {
            "test_case_name": "tc1",
            "category": "General",
            "difficulty": "Easy",
            "model_type": "simulated:default",
            "prompt": "Hello",
            "response": "Hi",
            "status": "success",
            "score": 0.9,
            "duration_seconds": 0.5,
            "estimated_cost": 0.001,
            "judge_reasoning": "Good",
            "pii_found": False,
            "pii_types": [],
        }
    ]
    run_file.write_text(json.dumps(sample_data), encoding="utf-8")

    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        f"""
directories:
  results: "{results_dir.as_posix()}"
""",
        encoding="utf-8",
    )

    mock_st = MagicMock()
    mock_st.sidebar.selectbox.return_value = str(run_file)
    mock_st.sidebar.text_input.return_value = str(config_file)
    mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]
    mock_st.columns.side_effect = lambda n: [
        MagicMock() for _ in range(n if isinstance(n, int) else len(n))
    ]
    mock_st.radio.return_value = "Avg Score"

    with (
        patch("streamlit.set_page_config"),
        patch("streamlit.title"),
        patch("streamlit.markdown"),
        patch("streamlit.sidebar", mock_st.sidebar),
        patch("streamlit.stop"),
        patch("streamlit.columns", mock_st.columns),
        patch("streamlit.tabs", mock_st.tabs),
        patch("streamlit.subheader"),
        patch("streamlit.dataframe"),
        patch("streamlit.divider"),
        patch("streamlit.selectbox", side_effect=["tc1", "simulated:default"]),
        patch("streamlit.info"),
        patch("streamlit.code"),
        patch("streamlit.success"),
        patch("streamlit.warning"),
        patch("streamlit.radio", mock_st.radio),
        patch("streamlit.bar_chart"),
    ):
        show_dashboard()
