import asyncio
"""Model selection service for AI operations."""

import logging
import os
from typing import Any, Dict, List, Optional

import anthropic
import groq
import mistralai
import openai

from application.src.core.config import Settings

logger = logging.getLogger(__name__)


class ModelSelector:
    """Handles dynamic model selection and fallback strategies."""

    def __init__(self, settings: Settings):
        """Initialize model selector with configuration."""
        self.settings = settings
        self.models = settings.AI_MODELS
        self._validate_models()

    def _validate_models(self) -> None:
        """Validate model configuration."""
        if not self.models:
            raise ValueError("No models configured")
        for model_id, config in self.models.items():
            # Check required fields
            fields = ["name", "max_tokens", "temperature", "priority"]
            missing = [f for f in fields if f not in config]
            if missing:
                msg = ", ".join(missing)
                raise ValueError(f"Model {model_id} missing fields: {msg}")
            
            # Validate field values
            if config["max_tokens"] <= 0:
                raise ValueError("Invalid model configuration")
            if not 0 <= config["temperature"] <= 2:
                raise ValueError("Invalid model configuration")
            if config["priority"] <= 0:
                raise ValueError("Invalid model configuration")

    def select_model(
        self,
        task_type: str,
        token_estimate: Optional[int] = None,
        context: Optional[Dict] = None,
    ) -> Dict:
        """Select the most appropriate model based on task requirements.

        Args:
            task_type: Type of task (e.g., 'code_generation')
            token_estimate: Estimated tokens needed
            context: Additional context for selection

        Returns:
            Dict containing model configuration
        """
        models = self.models.items()
        available_models = sorted(models, key=lambda x: x[1]["priority"])

        # Filter models by token limit
        if token_estimate:
            available_models = [
                m
                for m in available_models
                if m[1]["max_tokens"] >= token_estimate
            ]

        # Use model with highest max_tokens if no models meet requirements
        if not available_models:
            logger.warning("No models meet requirements")
            models = self.models.items()
            return max(models, key=lambda x: x[1]["max_tokens"])[1]

        # Select model based on task type and context
        task_model_map = {
            "simple_task": "openai",
            "complex_task": "claude",
            "fallback_task": "mistral"
        }

        if task_type in task_model_map:
            target_provider = task_model_map[task_type]
            for model in available_models:
                if model[0] == target_provider:
                    return model[1]

        # Return the highest priority model that meets requirements
        return available_models[0][1]

    def get_fallback_model(self, current_model: str) -> Optional[Dict]:
        """
        Get the next fallback model when current model fails.

        Args:
            current_model: Name of the current model that failed

        Returns:
            Next model configuration or None if no fallbacks available
        """
        # Map model names to their configurations
        model_map = {
            "gpt-4-turbo-preview": self.models["openai"],
            "gpt-4-0125-preview": self.models["openai"],
            "claude-3-opus-20240229": self.models["claude"],
            "mistral-large-latest": self.models["mistral"],
            "mixtral-8x7b-32768": self.models["groq"]
        }

        # Define fallback chain
        fallback_chain = {
            "gpt-4-turbo-preview": "claude-3-opus-20240229",
            "gpt-4-0125-preview": "mistral-large-latest",
            "claude-3-opus-20240229": "mistral-large-latest",
            "mistral-large-latest": "mixtral-8x7b-32768"
        }

        if current_model not in model_map:
            logger.warning(f"Unknown model: {current_model}")
            return None

        next_model = fallback_chain.get(current_model)
        return model_map[next_model] if next_model else None

    async def generate_completion(
        self,
        prompt: str,
        model: str,
        fallback_providers: Optional[List[str]] = None,
    ) -> Any:
        """Generate completion using specified model with fallback support.

        Args:
            prompt: Input prompt for completion
            model: Model provider to use ('openai', 'claude', etc.)
            fallback_providers: Optional list of fallback providers

        Returns:
            Completion response with standardized format
        """
        # Map provider aliases
        provider_map = {
            "anthropic": "claude",
            "claude": "claude"
        }
        model_key = provider_map.get(model, model)

        if model_key not in self.models:
            raise ValueError(f"Unknown model provider: {model}")

        current_model = self.models[model_key]
        # Map provider for _generate_with_provider
        provider = "claude" if model in ["claude", "anthropic"] else model
        try:
            # Map provider for _generate_with_provider
            provider = "claude" if model in ["claude", "anthropic"] else model
            response = await self._generate_with_provider(
                prompt, provider, current_model
            )
            # Check if response is empty (tokenization only)
            if not response.choices[0].message["content"]:
                raise ValueError("Empty response")
            return response
        except Exception as e:
            # Try fallback models within same provider
            if current_model.get("fallback_chain"):
                for fallback_name in current_model["fallback_chain"]:
                    try:
                        fallback_response = await self._generate_with_provider(
                            prompt, provider, {"name": fallback_name}
                        )
                        if fallback_response.choices[0].message["content"]:
                            return fallback_response
                    except Exception:
                        continue

            # Try cross-provider fallback
            if fallback_providers:
                for fallback_provider in fallback_providers:
                    # Map provider aliases for fallback
                    provider_key = "claude" if fallback_provider in ["claude", "anthropic"] else fallback_provider
                    if provider_key in self.models:
                        try:
                            return await self._generate_with_provider(
                                prompt,
                                fallback_provider,
                                self.models[provider_key],
                            )
                        except Exception:
                            continue

            # Re-raise original error if all fallbacks fail
            raise

    async def _generate_with_provider(
        self, prompt: str, provider: str, model_config: Dict[str, Any]
    ) -> Any:
        """Generate completion using specific provider.

        Args:
            prompt: Input prompt
            provider: Provider name
            model_config: Model configuration

        Returns:
            Provider-specific completion response
        """
        try:
            response = None
            if provider == "openai":
                client = openai.OpenAI(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    base_url="https://api.helicone.ai/v1/openai",
                    default_headers={
                        "Helicone-Auth": f"Bearer {os.getenv('HELICONE_API_KEY')}",
                        "Helicone-Cache-Enabled": "true",
                        "Helicone-Cache-TTL": "3600",
                    },
                )
                response = await client.chat.completions.create(
                    model=model_config["name"],
                    messages=[{"role": "user", "content": prompt}],
                    temperature=model_config.get("temperature", 0.7),
                    max_tokens=model_config.get("max_tokens", 4096),
                )
            elif provider == "claude" or provider == "anthropic":
                client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                response = await client.messages.create(
                    model=model_config["name"],
                    max_tokens=model_config.get("max_tokens", 4096),
                    messages=[{"role": "user", "content": prompt}],
                )
            elif provider == "mistral":
                client = mistralai.client.MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))
                response = await client.chat.completions.create(
                    model=model_config["name"],
                    messages=[{"role": "user", "content": prompt}],
                    temperature=model_config.get("temperature", 0.7),
                    max_tokens=model_config.get("max_tokens", 4096),
                )
            elif provider == "groq":
                client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
                response = await client.chat.completions.create(
                    model=model_config["name"],
                    messages=[{"role": "user", "content": prompt}],
                    temperature=model_config.get("temperature", 0.7),
                    max_tokens=model_config.get("max_tokens", 4096),
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            # Handle async response
            if asyncio.isfuture(response):
                response = await response
            return response
        except Exception as e:
            logger.error(f"Error generating completion with {provider}: {e}")
            raise
