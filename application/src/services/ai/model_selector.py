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
        self.models = settings.AI_MODELS
        self._validate_models()

    def _validate_models(self) -> None:
        """Validate model configuration."""
        if not self.models:
            raise ValueError("No models configured")
        for model_id, config in self.models.items():
            fields = ["name", "max_tokens", "temperature", "priority"]
            missing = [f for f in fields if f not in config]
            if missing:
                msg = ", ".join(missing)
                raise ValueError(f"Model {model_id} missing fields: {msg}")

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
