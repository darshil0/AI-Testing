# models.py

import os
import re
import json
import logging
from typing import Tuple, Dict, Any, Optional

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
    def __init__(self, model_name: str, config: Dict[str, Any]):
        self.model_name = model_name
        self.config = config

    def call(self, prompt: str) -> Tuple[str, int, int]:
        raise NotImplementedError

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        prices = self.config.get("pricing", {}).get(
            self.model_name, {"input": 0.0, "output": 0.0}
        )
        return (input_tokens / 1_000_000 * prices["input"]) + (
            output_tokens / 1_000_000 * prices["output"]
        )


class SimulatedModel(BaseModel):
    def call(self, prompt: str) -> Tuple[str, int, int]:
        return "Simulated response.", 10, 5


class OpenAIModel(BaseModel):
    def __init__(self, model_name: str, config: Dict[str, Any]):
        super().__init__(model_name, config)
        if not OPENAI_AVAILABLE or not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OpenAI API key missing or openai not installed.")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def call(self, prompt: str) -> Tuple[str, int, int]:
        resp = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.config.get("max_tokens", 2000),
            temperature=self.config.get("temperature", 0.7),
        )
        return (
            resp.choices[0].message.content,
            resp.usage.prompt_tokens,
            resp.usage.completion_tokens,
        )


class AnthropicModel(BaseModel):
    def __init__(self, model_name: str, config: Dict[str, Any]):
        super().__init__(model_name, config)
        if not ANTHROPIC_AVAILABLE or not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("Anthropic API key missing or anthropic not installed.")
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def call(self, prompt: str) -> Tuple[str, int, int]:
        resp = self.client.messages.create(
            model=self.model_name,
            max_tokens=self.config.get("max_tokens", 2000),
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text, resp.usage.input_tokens, resp.usage.output_tokens


class GeminiModel(BaseModel):
    def __init__(self, model_name: str, config: Dict[str, Any]):
        super().__init__(model_name, config)
        if not GEMINI_AVAILABLE or not os.getenv("GOOGLE_API_KEY"):
            raise ValueError(
                "Google API key missing or google-generativeai not installed."
            )
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.client = genai.GenerativeModel(self.model_name)

    def call(self, prompt: str) -> Tuple[str, int, int]:
        resp = self.client.generate_content(prompt)
        # Gemini does not return token counts directly in the same way
        # Heuristic:
        input_tokens = len(prompt) // 4
        output_tokens = len(resp.text) // 4
        return resp.text, input_tokens, output_tokens


class OllamaModel(BaseModel):
    def __init__(self, model_name: str, config: Dict[str, Any]):
        super().__init__(model_name, config)
        if not OLLAMA_AVAILABLE:
            raise ValueError("Ollama not installed.")

    def call(self, prompt: str) -> Tuple[str, int, int]:
        resp = ollama.chat(
            model=self.model_name, messages=[{"role": "user", "content": prompt}]
        )
        content = resp["message"]["content"]
        # Heuristic for local models
        return content, len(prompt) // 4, len(content) // 4


def get_model(model_identifier: str, config: Dict[str, Any]) -> BaseModel:
    """Factory function to get a model instance."""
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
