"""Test suite for the ModelSelector class."""

import pytest

from application.src.core.config import Settings
from application.src.services.ai.model_selector import ModelSelector


@pytest.fixture
def model_selector():
    """Create a ModelSelector instance with test configuration."""
    settings = Settings()
    return ModelSelector(settings)


def test_model_selector_initialization(model_selector):
    """Test successful initialization of ModelSelector."""
    assert model_selector.models == Settings().AI_MODELS
    assert len(model_selector.models) > 0


def test_select_model_default(model_selector):
    """Test model selection with default parameters."""
    model = model_selector.select_model("test_generation")
    assert model["name"] == "gpt-4-turbo-preview"
    assert model["priority"] == 1


def test_select_model_with_token_estimate(model_selector):
    """Test model selection with token requirements."""
    model = model_selector.select_model("test_generation", token_estimate=5000)
    assert (
        model["name"] == "gpt-4-turbo-preview"
    )  # Should select model with highest max_tokens
    assert model["max_tokens"] == 4096


def test_select_model_with_context(model_selector):
    """Test model selection with context."""
    model = model_selector.select_model(
        "test_generation", context={"test_type": "unit"}
    )
    assert model["name"] == "gpt-4-turbo-preview"
    assert model["priority"] == 1


def test_get_fallback_model(model_selector):
    """Test fallback model selection."""
    fallback = model_selector.get_fallback_model("gpt-4-turbo-preview")
    assert fallback["name"] == "claude-3-opus-20240229"
    assert fallback["priority"] == 2


def test_get_fallback_model_last_resort(model_selector):
    """Test fallback to last resort model."""
    fallback = model_selector.get_fallback_model("gpt-4-0125-preview")
    assert fallback["name"] == "mistral-large-latest"
    assert fallback["priority"] == 3


def test_get_fallback_model_none_available(model_selector):
    """Test when no fallback models are available."""
    fallback = model_selector.get_fallback_model("gpt-4")
    assert fallback is None


def test_validate_models_missing_fields():
    """Test validation of model configuration with missing fields."""
    settings = Settings()
    settings.AI_MODELS = {
        "test-model": {
            "name": "test",
            # Missing required fields
        }
    }
    with pytest.raises(ValueError) as exc_info:
        ModelSelector(settings)
    assert "missing fields" in str(exc_info.value)


def test_validate_models_empty_config():
    """Test validation with empty model configuration."""
    settings = Settings()
    settings.AI_MODELS = {}
    with pytest.raises(ValueError) as exc_info:
        ModelSelector(settings)
    assert "No models configured" in str(exc_info.value)
