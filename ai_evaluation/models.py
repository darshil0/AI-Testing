import logging
import os
from typing import Tuple, Dict, Any

from tenacity import retry, stop_after_attempt, wait_exponential

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

try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

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

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing_config = self.config.get("pricing", {})
        if self.model_name not in pricing_config:
            if self.model_name != "default":
                logger.warning(
                    f"Pricing config is missing for model '{self.model_name}'. Cost will be set to $0.0."
                )
            prices = {"input": 0.0, "output": 0.0}
        else:
            prices = pricing_config[self.model_name]

        input_price = prices.get("input", 0.0) if isinstance(prices, dict) else 0.0
        output_price = prices.get("output", 0.0) if isinstance(prices, dict) else 0.0

        return (input_tokens / 1_000_000 * input_price) + (
            output_tokens / 1_000_000 * output_price
        )


class SimulatedModel(BaseModel):
    def call(self, prompt: str) -> Tuple[str, int, int]:
        # Simple deterministic stub for local/dev runs
        return "Simulated response.", 10, 5


class OpenAIModel(BaseModel):
    def __init__(self, model_name: str, config: Dict[str, Any]) -> None:
        super().__init__(model_name, config)
        api_key = os.getenv("OPENAI_API_KEY")
        if not OPENAI_AVAILABLE or not api_key:
            raise ValueError("OpenAI API key missing or openai not installed.")
        self.client = OpenAI(api_key=api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    def call(self, prompt: str) -> Tuple[str, int, int]:
        resp = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.config.get("default_model_params", {}).get(
                "max_tokens", self.config.get("max_tokens", 2000)
            ),
            temperature=self.config.get("default_model_params", {}).get(
                "temperature", self.config.get("temperature", 0.7)
            ),
        )
        content = resp.choices[0].message.content or ""
        input_tokens = getattr(resp.usage, "prompt_tokens", 0)
        output_tokens = getattr(resp.usage, "completion_tokens", 0)
        return content, input_tokens, output_tokens


class AnthropicModel(BaseModel):
    def __init__(self, model_name: str, config: Dict[str, Any]) -> None:
        super().__init__(model_name, config)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not ANTHROPIC_AVAILABLE or not api_key:
            raise ValueError("Anthropic API key missing or anthropic not installed.")
        self.client = Anthropic(api_key=api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
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
    def __init__(self, model_name: str, config: Dict[str, Any]) -> None:
        super().__init__(model_name, config)
        api_key = os.getenv("GOOGLE_API_KEY")
        if not GEMINI_AVAILABLE or not api_key:
            raise ValueError(
                "Google API key missing or google-generativeai not installed."
            )
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.model_name)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    def call(self, prompt: str) -> Tuple[str, int, int]:
        resp = self.client.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": self.config.get("default_model_params", {}).get(
                    "max_tokens", self.config.get("max_tokens", 2000)
                ),
                "temperature": self.config.get("default_model_params", {}).get(
                    "temperature", self.config.get("temperature", 0.7)
                ),
            },
        )
        try:
            text = getattr(resp, "text", "") or ""
        except ValueError as ve:
            logger.warning(f"Gemini response text unavailable (safety or empty): {ve}")
            text = "Response blocked or empty due to safety settings."

        usage = getattr(resp, "usage_metadata", None)
        if usage is not None:
            input_tokens = getattr(usage, "prompt_token_count", 0)
            output_tokens = getattr(usage, "candidates_token_count", 0)
        else:
            # Fallback heuristic
            input_tokens = len(prompt) // 4
            output_tokens = len(text) // 4
        return text, input_tokens, output_tokens


class OllamaModel(BaseModel):
    def __init__(self, model_name: str, config: Dict[str, Any]) -> None:
        super().__init__(model_name, config)
        if not OLLAMA_AVAILABLE:
            raise ValueError("Ollama not installed.")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    def call(self, prompt: str) -> Tuple[str, int, int]:
        resp = ollama.chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
        )
        if isinstance(resp, dict):
            content = resp.get("message", {}).get("content", "")
        else:
            msg = getattr(resp, "message", None)
            if isinstance(msg, dict):
                content = msg.get("content", "")
            else:
                content = getattr(msg, "content", "") or ""
        # Heuristic for local models
        return content, len(prompt) // 4, len(content) // 4


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
