"""
Concrete LLM provider implementations.
"""

import time
from typing import Any, Dict

from ..base.provider import LLMProvider
from ..utils.token_costs import get_token_costs
from ..utils.tool_call_parser import extract_anthropic_response_with_tools


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider implementation."""

    def __init__(self):
        super().__init__(
            name="openai", response_extractor=self._extract_openai_response
        )

    def parse_tokens(self, response_data: Dict[str, Any]) -> Dict[str, int]:
        """Parse tokens from OpenAI response."""
        usage = response_data.get("usage", {})
        return {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }

    def calculate_cost(
        self, tokens_data: Dict[str, int], model_name: str
    ) -> Dict[str, float]:
        """Calculate cost for OpenAI model."""
        try:
            model_pricing = get_token_costs(model_name, self.name)
            prompt_tokens = tokens_data.get("prompt_tokens", 0)
            completion_tokens = tokens_data.get("completion_tokens", 0)

            input_price = prompt_tokens * model_pricing["input_cost_per_token"]
            output_price = (
                completion_tokens * model_pricing["output_cost_per_token"]
            )
            total_price = input_price + output_price

            return {
                "input": input_price,
                "output": output_price,
                "total": total_price,
            }
        except ValueError as e:
            raise e

    def get_completion_start_time(self, response_data: Dict[str, Any]) -> float:
        """Extract completion start time from OpenAI response."""
        return response_data.get("created", time.time())

    def _extract_openai_response(self, data: Dict[str, Any]) -> str:
        """Extract response content from OpenAI response."""
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        return ""


class AnthropicProvider(LLMProvider):
    """Anthropic LLM provider implementation."""

    def __init__(self):
        super().__init__(
            name="anthropic",
            response_extractor=extract_anthropic_response_with_tools,
        )

    def parse_tokens(self, response_data: Dict[str, Any]) -> Dict[str, int]:
        """Parse tokens from Anthropic response."""
        usage = response_data.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        cache_creation_input_tokens = usage.get(
            "cache_creation_input_tokens", 0
        )
        cache_read_input_tokens = usage.get("cache_read_input_tokens", 0)

        return {
            "prompt_tokens": input_tokens,
            "completion_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cache_creation_input_tokens": cache_creation_input_tokens,
            "cache_read_input_tokens": cache_read_input_tokens,
        }

    def calculate_cost(
        self, tokens_data: Dict[str, int], model_name: str
    ) -> Dict[str, float]:
        """Calculate cost for Anthropic model."""
        try:
            model_pricing = get_token_costs(model_name, self.name)
            prompt_tokens = tokens_data.get("prompt_tokens", 0)
            completion_tokens = tokens_data.get("completion_tokens", 0)
            cache_creation_input_tokens = tokens_data.get(
                "cache_creation_input_tokens", 0
            )
            cache_read_input_tokens = tokens_data.get(
                "cache_read_input_tokens", 0
            )

            input_price = prompt_tokens * model_pricing["input_cost_per_token"]
            output_price = (
                completion_tokens * model_pricing["output_cost_per_token"]
            )

            # Calculate cache-related costs
            cache_creation_price = 0.0
            cache_read_price = 0.0

            if (
                cache_creation_input_tokens > 0
                and "cache_creation_input_token_cost" in model_pricing
            ):
                cache_creation_price = (
                    cache_creation_input_tokens
                    * model_pricing["cache_creation_input_token_cost"]
                )

            if (
                cache_read_input_tokens > 0
                and "cache_read_input_token_cost" in model_pricing
            ):
                cache_read_price = (
                    cache_read_input_tokens
                    * model_pricing["cache_read_input_token_cost"]
                )

            total_price = (
                input_price
                + output_price
                + cache_creation_price
                + cache_read_price
            )

            return {
                "input": input_price,
                "output": output_price,
                "cache_creation": cache_creation_price,
                "cache_read": cache_read_price,
                "total": total_price,
            }
        except ValueError as e:
            raise e

    def get_completion_start_time(self, response_data: Dict[str, Any]) -> float:
        """Extract completion start time from Anthropic response."""
        return response_data.get("started_at", time.time())


class GroqProvider(LLMProvider):
    """Groq LLM provider implementation."""

    def __init__(self):
        super().__init__(
            name="groq", response_extractor=self._extract_groq_response
        )

    def parse_tokens(self, response_data: Dict[str, Any]) -> Dict[str, int]:
        """Parse tokens from Groq response."""
        usage = response_data.get("usage", {})
        return {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }

    def calculate_cost(
        self, tokens_data: Dict[str, int], model_name: str
    ) -> Dict[str, float]:
        """Calculate cost for Groq model."""
        try:
            model_pricing = get_token_costs(model_name, self.name)
            prompt_tokens = tokens_data.get("prompt_tokens", 0)
            completion_tokens = tokens_data.get("completion_tokens", 0)

            input_price = prompt_tokens * model_pricing["input_cost_per_token"]
            output_price = (
                completion_tokens * model_pricing["output_cost_per_token"]
            )
            total_price = input_price + output_price

            return {
                "input": input_price,
                "output": output_price,
                "total": total_price,
            }
        except ValueError as e:
            raise e

    def get_completion_start_time(self, response_data: Dict[str, Any]) -> float:
        """Extract completion start time from Groq response."""
        return response_data.get("created", time.time())

    def _extract_groq_response(self, data: Dict[str, Any]) -> str:
        """Extract response content from Groq response."""
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        return ""
