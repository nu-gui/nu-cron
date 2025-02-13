"""Model selection service for AI operations."""

import logging
from typing import Dict, Optional

from application.src.core.config import Settings

logger = logging.getLogger(__name__)


class ModelSelector:
    """Handles dynamic model selection and fallback strategies."""

    def __init__(self, settings: Settings):
        """Initialize model selector with configuration."""
        self.settings = settings
        self.models = settings.OPENAI_MODELS
        self._validate_models()

    def _validate_models(self) -> None:
        """Validate model configuration."""
        if not self.models:
            raise ValueError("No models configured")
        for model_id, config in self.models.items():
            required_fields = ["name", "max_tokens", "temperature", "priority"]
            missing = [f for f in required_fields if f not in config]
            if missing:
                raise ValueError(
                    f"Model {model_id} missing required fields: {', '.join(missing)}"
                )

    def select_model(
        self,
        task_type: str,
        token_estimate: Optional[int] = None,
        context: Optional[Dict] = None,
    ) -> Dict:
        """
        Select the most appropriate model based on task requirements.

        Args:
            task_type: Type of task (e.g., 'code_generation', 'test_generation')
            token_estimate: Estimated tokens needed for the task
            context: Additional context for model selection

        Returns:
            Dict containing model configuration
        """
        available_models = sorted(
            self.models.items(), key=lambda x: x[1]["priority"]
        )

        # Select model based on token requirements
        if token_estimate:
            available_models = [
                (model_id, config)
                for model_id, config in available_models
                if config["max_tokens"] >= token_estimate
            ]

        # If no models meet token requirements, use the model with highest max_tokens
        if not available_models:
            logger.warning(
                "No models meet token requirements, using fallback model"
            )
            return max(self.models.items(), key=lambda x: x[1]["max_tokens"])[
                1
            ]

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
        current_priority = None
        for model_id, config in self.models.items():
            if config["name"] == current_model:
                current_priority = config["priority"]
                break

        if current_priority is None:
            logger.warning(f"Unknown model: {current_model}")
            return None

        # Find next model with higher priority number
        fallback_models = [
            config
            for config in self.models.values()
            if config["priority"] > current_priority
        ]

        if not fallback_models:
            logger.warning("No fallback models available")
            return None

        return min(fallback_models, key=lambda x: x["priority"])
