from unittest.mock import MagicMock, patch

from ai_evaluation.models import GeminiModel, OllamaModel, OpenAIModel


def test_models_additional_coverage():
    config = {
        "pricing": {
            "openai:gpt-4o": {"input": 2.5, "output": 10.0},
            "anthropic:claude-3-5-sonnet": {"input": 3.0, "output": 15.0},
        }
    }

    # OpenAI o1/o3 model call
    with (
        patch("ai_evaluation.models.OPENAI_AVAILABLE", True),
        patch("os.getenv", return_value="fake_key"),
    ):
        model = OpenAIModel("o1-preview", config)
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock()]
        mock_resp.choices[0].message.content = "Reasoning answer"
        mock_resp.usage.prompt_tokens = 15
        mock_resp.usage.completion_tokens = 25
        model.client.chat.completions.create = MagicMock(return_value=mock_resp)

        content, in_tok, out_tok = model.call("Think step by step")
        assert content == "Reasoning answer"
        assert in_tok == 15
        assert out_tok == 25

    # Gemini model with new SDK
    mock_genai_module = MagicMock()
    mock_client_cls = MagicMock()
    mock_genai_module.Client = mock_client_cls
    mock_types = MagicMock()

    with (
        patch("ai_evaluation.models.GEMINI_AVAILABLE", True),
        patch("ai_evaluation.models.GEMINI_GENAI_AVAILABLE", True),
        patch("ai_evaluation.models.types", mock_types, create=True),
        patch.dict("sys.modules", {"google.genai": mock_genai_module}),
        patch("ai_evaluation.models.genai", mock_genai_module, create=True),
        patch("os.getenv", return_value="fake_key"),
    ):
        mock_client = MagicMock()
        mock_gen_resp = MagicMock()
        mock_gen_resp.text = "Gemini new response"
        mock_gen_resp.usage_metadata.prompt_token_count = 12
        mock_gen_resp.usage_metadata.candidates_token_count = 18
        mock_client.models.generate_content.return_value = mock_gen_resp
        mock_client_cls.return_value = mock_client

        model = GeminiModel("gemini-2.0-flash", config)
        text, in_tok, out_tok = model.call("Hello Gemini")
        assert text == "Gemini new response"
        assert in_tok == 12
        assert out_tok == 18

    # Ollama model object response
    with (
        patch("ai_evaluation.models.OLLAMA_AVAILABLE", True),
        patch("ollama.chat", create=True) as mock_ollama_chat,
    ):
        mock_resp_obj = MagicMock()
        mock_resp_obj.message.content = "Ollama obj reply"
        mock_resp_obj.prompt_eval_count = 8
        mock_resp_obj.eval_count = 14
        mock_ollama_chat.return_value = mock_resp_obj

        model = OllamaModel("llama3", config)
        text, in_tok, out_tok = model.call("Hello Ollama")
        assert text == "Ollama obj reply"
        assert in_tok == 8
        assert out_tok == 14
