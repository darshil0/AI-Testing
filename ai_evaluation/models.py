import logging
import os
from typing import Any, Dict, Optional, Tuple

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

# Optional imports for real models
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

import warnings

GEMINI_GENAI_AVAILABLE = False
GEMINI_LEGACY_AVAILABLE = False
genai = None
types = None
genai_legacy = None

try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from google import genai
        from google.genai import types

    GEMINI_GENAI_AVAILABLE = True
except Exception:
    GEMINI_GENAI_AVAILABLE = False

try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import google.generativeai as genai_legacy

    GEMINI_LEGACY_AVAILABLE = True
except Exception:
    GEMINI_LEGACY_AVAILABLE = False

GEMINI_AVAILABLE = GEMINI_GENAI_AVAILABLE or GEMINI_LEGACY_AVAILABLE

try:
    import ollama

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

logger = logging.getLogger("rich")


class BaseModel:
    def __init__(self, model_name: str, config: Dict[str, Any]) -> None:
        self.model_name = model_name
        self.config = config

    def call(self, prompt: str) -> Tuple[str, int, int]:
        """Return (response_text, input_tokens, output_tokens)."""
        raise NotImplementedError

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> Optional[float]:
        pricing_config = self.config.get("pricing", {})
        provider_name = getattr(self, "provider_name", "unknown")

        # Key lookup precedence: "provider:model_name", "model_name"
        full_key = f"{provider_name}:{self.model_name}"
        if full_key in pricing_config:
            prices = pricing_config[full_key]
        elif self.model_name in pricing_config:
            prices = pricing_config[self.model_name]
        else:
            if self.model_name != "default" and provider_name != "simulated":
                logger.warning(
                    f"Pricing config missing for provider '{provider_name}', model '{self.model_name}'. Cost set to unknown (None)."
                )
            return None

        if input_tokens is None or output_tokens is None:
            return None

        if not isinstance(prices, dict):
            return None

        input_price = prices.get("input")
        output_price = prices.get("output")
        if input_price is None or output_price is None:
            return None

        return (input_tokens / 1_000_000) * input_price + (
            output_tokens / 1_000_000
        ) * output_price


def is_transient_error(exception: Exception) -> bool:
    """Return True if exception is transient (network timeout, rate limit, 5xx error)."""
    exc_type = type(exception).__name__
    exc_msg = str(exception).lower()

    if any(
        term in exc_msg
        for term in [
            "api_key",
            "unauthorized",
            "authentication",
            "invalid_request",
            "not_found",
            "blocked by safety",
            "safety settings",
        ]
    ):
        return False

    status_code = getattr(exception, "status_code", None) or getattr(
        exception, "code", None
    )
    if isinstance(status_code, int):
        if status_code in [429, 500, 502, 503, 504]:
            return True
        if status_code in [400, 401, 403, 404]:
            return False

    if any(
        term in exc_type.lower()
        for term in ["timeout", "connection", "rate", "server", "unavailable"]
    ):
        return True

    return False


class SimulatedModel(BaseModel):
    provider_name = "simulated"

    def call(self, prompt: str) -> Tuple[str, int, int]:
        # Simple deterministic stub for local/dev runs
        return "Simulated response.", len(prompt) // 4, 5


class OpenAIModel(BaseModel):
    provider_name = "openai"

    def __init__(self, model_name: str, config: Dict[str, Any]) -> None:
        super().__init__(model_name, config)
        api_key = os.getenv("OPENAI_API_KEY")
        if not OPENAI_AVAILABLE or not api_key:
            raise ValueError("OpenAI API key missing or openai not installed.")
        self.client = OpenAI(api_key=api_key)

    @retry(
        retry=retry_if_exception(is_transient_error),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def call(self, prompt: str) -> Tuple[str, int, int]:
        max_tok = self.config.get("default_model_params", {}).get(
            "max_tokens", self.config.get("max_tokens", 2000)
        )
        temp = self.config.get("default_model_params", {}).get(
            "temperature", self.config.get("temperature", 0.7)
        )

        params: Dict[str, Any] = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
        }

        # Handle OpenAI reasoning models (o1, o3-mini) which do not support temperature or max_tokens
        if self.model_name.startswith(("o1", "o3")):
            params["max_completion_tokens"] = max_tok
        else:
            params["max_tokens"] = max_tok
            params["temperature"] = temp

        resp = self.client.chat.completions.create(**params)
        content = resp.choices[0].message.content or ""
        input_tokens = getattr(resp.usage, "prompt_tokens", 0)
        output_tokens = getattr(resp.usage, "completion_tokens", 0)
        return content, input_tokens, output_tokens


class AnthropicModel(BaseModel):
    provider_name = "anthropic"

    def __init__(self, model_name: str, config: Dict[str, Any]) -> None:
        super().__init__(model_name, config)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not ANTHROPIC_AVAILABLE or not api_key:
            raise ValueError("Anthropic API key missing or anthropic not installed.")
        self.client = Anthropic(api_key=api_key)

    @retry(
        retry=retry_if_exception(is_transient_error),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def call(self, prompt: str) -> Tuple[str, int, int]:
        resp = self.client.messages.create(
            model=self.model_name,
            max_tokens=self.config.get("default_model_params", {}).get(
                "max_tokens", self.config.get("max_tokens", 2000)
            ),
            temperature=self.config.get("default_model_params", {}).get(
                "temperature", self.config.get("temperature", 0.7)
            ),
            messages=[{"role": "user", "content": prompt}],
        )
        text = ""
        if hasattr(resp, "content") and resp.content:
            text_blocks = []
            for block in resp.content:
                if getattr(block, "type", "text") == "text" and hasattr(block, "text"):
                    text_blocks.append(block.text)
                elif isinstance(block, str):
                    text_blocks.append(block)
            text = "".join(text_blocks)
        input_tokens = getattr(resp.usage, "input_tokens", 0)
        output_tokens = getattr(resp.usage, "output_tokens", 0)
        return text, input_tokens, output_tokens


class GeminiModel(BaseModel):
    provider_name = "gemini"

    def __init__(self, model_name: str, config: Dict[str, Any]) -> None:
        super().__init__(model_name, config)
        if not GEMINI_AVAILABLE:
            raise ValueError(
                "Google GenAI SDK is not installed. Install with: pip install 'ai-evaluation-framework[gemini]'"
            )
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is missing.")
        if GEMINI_GENAI_AVAILABLE:
            target_genai = genai
            if target_genai is None:
                from google import genai as target_genai
            self.client = target_genai.Client(api_key=api_key)
            self.use_new_sdk = True
        else:
            target_legacy = genai_legacy
            if target_legacy is None:
                import google.generativeai as target_legacy
            target_legacy.configure(api_key=api_key)
            self.client = target_legacy.GenerativeModel(self.model_name)
            self.use_new_sdk = False

    @retry(
        retry=retry_if_exception(is_transient_error),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def call(self, prompt: str) -> Tuple[str, int, int]:
        max_tok = self.config.get("default_model_params", {}).get(
            "max_tokens", self.config.get("max_tokens", 2000)
        )
        temp = self.config.get("default_model_params", {}).get(
            "temperature", self.config.get("temperature", 0.7)
        )

        if self.use_new_sdk:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tok,
                    temperature=temp,
                ),
            )
            # Check for safety block or empty response
            text = getattr(response, "text", "") or ""
            if not text:
                candidates = getattr(response, "candidates", [])
                if candidates and getattr(candidates[0], "finish_reason", None) in [
                    "SAFETY",
                    "BLOCKLIST",
                    "PROHIBITED_CONTENT",
                ]:
                    raise ValueError(
                        f"Gemini output blocked by safety settings: {candidates[0].finish_reason}"
                    )
                raise ValueError("Gemini returned empty or blocked response")

            usage = getattr(response, "usage_metadata", None)
            in_tok = (
                getattr(usage, "prompt_token_count", 0) if usage else len(prompt) // 4
            )
            out_tok = (
                getattr(usage, "candidates_token_count", 0) if usage else len(text) // 4
            )
            return text, in_tok, out_tok
        else:
            resp = self.client.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tok,
                    "temperature": temp,
                },
            )
            try:
                text = getattr(resp, "text", "") or ""
            except ValueError as ve:
                raise ValueError(
                    f"Gemini response blocked by safety settings: {ve}"
                ) from ve

            if not text:
                raise ValueError("Gemini returned empty response")

            usage = getattr(resp, "usage_metadata", None)
            in_tok = (
                getattr(usage, "prompt_token_count", 0) if usage else len(prompt) // 4
            )
            out_tok = (
                getattr(usage, "candidates_token_count", 0) if usage else len(text) // 4
            )
            return text, in_tok, out_tok


class OllamaModel(BaseModel):
    provider_name = "ollama"

    def __init__(self, model_name: str, config: Dict[str, Any]) -> None:
        super().__init__(model_name, config)
        if not OLLAMA_AVAILABLE:
            raise ValueError("Ollama not installed.")

    @retry(
        retry=retry_if_exception(is_transient_error),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def call(self, prompt: str) -> Tuple[str, int, int]:
        max_tok = self.config.get("default_model_params", {}).get(
            "max_tokens", self.config.get("max_tokens", 2000)
        )
        temp = self.config.get("default_model_params", {}).get(
            "temperature", self.config.get("temperature", 0.7)
        )

        resp = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            options={
                "num_predict": max_tok,
                "temperature": temp,
            },
        )
        if isinstance(resp, dict):
            content = resp.get("message", {}).get("content", "")
            in_tok = resp.get("prompt_eval_count", len(prompt) // 4)
            out_tok = resp.get("eval_count", len(content) // 4)
        else:
            msg = getattr(resp, "message", None)
            if isinstance(msg, dict):
                content = msg.get("content", "")
            else:
                content = getattr(msg, "content", "") or ""
            in_tok = getattr(resp, "prompt_eval_count", len(prompt) // 4)
            out_tok = getattr(resp, "eval_count", len(content) // 4)
        return content, in_tok, out_tok


def get_model(model_identifier: str, config: Dict[str, Any]) -> BaseModel:
    """Factory function to get a model instance.

    model_identifier format: "<provider>:<model_name>", e.g. "openai:gpt-4o".
    """
    if ":" not in model_identifier:
        raise ValueError(
            f"Invalid model identifier '{model_identifier}'. Expected '<provider>:<model_name>'."
        )

    provider, model_name = model_identifier.split(":", 1)

    if provider == "openai":
        return OpenAIModel(model_name, config)
    if provider == "anthropic":
        return AnthropicModel(model_name, config)
    if provider == "gemini":
        return GeminiModel(model_name, config)
    if provider == "ollama":
        return OllamaModel(model_name, config)
    if provider == "simulated":
        return SimulatedModel(model_name, config)

    raise ValueError(f"Unknown model provider: {provider}")
