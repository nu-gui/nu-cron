"""Test suite for model environments and configurations."""

import pytest
from unittest.mock import AsyncMock, Mock, patch, DEFAULT
import os

from application.src.services.ai.model_selector import ModelSelector
from application.src.core.config import Settings
from application.tests.utils.model_test_utils import (
    setup_mock_future,
    mock_token_usage,
    create_mock_client,
    setup_model_environment
)


@pytest.fixture
def model_environments():
    """Configure test environments for different models."""
    with patch.dict(os.environ, setup_model_environment()):
        settings = Settings()
        return ModelSelector(settings)


@pytest.mark.asyncio
async def test_model_environment_initialization(model_environments):
    """Test initialization of all model environments."""
    assert "openai" in model_environments.models
    assert "claude" in model_environments.models
    assert "mistral" in model_environments.models
    assert "groq" in model_environments.models

    # Verify model configurations
    assert model_environments.models["openai"]["name"] == "gpt-4-turbo-preview"
    assert model_environments.models["claude"]["name"] == "claude-3-opus-20240229"
    assert model_environments.models["mistral"]["name"] == "mistral-large-latest"
    assert model_environments.models["groq"]["name"] == "mixtral-8x7b-32768"


@pytest.mark.asyncio
async def test_model_token_tracking(model_environments):
    """Test token tracking across different models."""
    test_content = "Test response"
    test_tokens = mock_token_usage(50, 30)

    # Test OpenAI token tracking
    with patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value = create_mock_client("openai")
        mock_openai.return_value.chat.completions.create.return_value = setup_mock_future(
            test_content, test_tokens
        )
        # Test implementation for OpenAI

    # Test Claude token tracking
    with patch("anthropic.Anthropic") as mock_claude:
        mock_claude.return_value = create_mock_client("claude")
        mock_claude.return_value.messages.create.return_value = setup_mock_future(
            test_content, test_tokens
        )
        # Test implementation for Claude

    # Test Mistral token tracking
    with patch("mistralai.Client") as mock_mistral:
        mock_mistral.return_value = create_mock_client("mistral")
        mock_mistral.return_value.chat.completions.create.return_value = setup_mock_future(
            test_content, test_tokens
        )
        # Test implementation for Mistral

    # Test Groq token tracking
    with patch("groq.Groq") as mock_groq:
        mock_groq.return_value = create_mock_client("groq")
        mock_groq.return_value.chat.completions.create.return_value = setup_mock_future(
            test_content, test_tokens
        )
        # Test implementation for Groq


@pytest.mark.asyncio
async def test_model_fallback_chain(model_environments):
    """Test fallback chain across different models."""
    test_content = "Fallback response"
    test_tokens = mock_token_usage(40, 20)

    # Test OpenAI fallback chain
    with patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value = create_mock_client("openai")
        mock_openai.return_value.chat.completions.create.side_effect = [
            Exception("Primary model error"),
            setup_mock_future(test_content, test_tokens)
        ]
        # Verify fallback to gpt-4-0125-preview

    # Test cross-model fallback
    with patch.multiple(
        "",
        openai=DEFAULT,
        anthropic=DEFAULT,
        mistralai=DEFAULT,
        groq=DEFAULT
    ) as mocks:
        # Configure mock responses and errors
        for client in mocks.values():
            client.return_value = create_mock_client(client.__name__)
            client.return_value.chat.completions.create.side_effect = [
                Exception("Model error"),
                setup_mock_future(test_content, test_tokens)
            ]
        # Test implementation for cross-model fallback


@pytest.mark.asyncio
async def test_model_environment_validation(model_environments):
    """Test validation of model environment configurations."""
    # Test invalid model configuration
    invalid_settings = Settings()
    invalid_settings.AI_MODELS["invalid_model"] = {
        "name": "invalid-model",
        "max_tokens": -1,  # Invalid token count
        "temperature": 2.0,  # Invalid temperature
        "priority": 0,  # Invalid priority
    }

    with pytest.raises(ValueError) as exc_info:
        ModelSelector(invalid_settings)
    assert "Invalid model configuration" in str(exc_info.value)


@pytest.mark.asyncio
async def test_model_selection_priority(model_environments):
    """Test model selection based on priority settings."""
    # Test model selection with different priorities
    test_scenarios = [
        {"task": "simple_task", "expected_model": "openai"},
        {"task": "complex_task", "expected_model": "claude"},
        {"task": "fallback_task", "expected_model": "mistral"},
    ]

    for scenario in test_scenarios:
        selected_model = model_environments.select_model(
            scenario["task"],
            context={"complexity": "high" if scenario["task"] == "complex_task" else "low"}
        )
        assert selected_model["name"] == model_environments.models[scenario["expected_model"]]["name"]
