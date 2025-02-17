"""Test suite for model fallback scenarios."""

import os
from unittest.mock import patch

import pytest

from application.src.core.config import Settings
from application.src.services.ai.model_selector import ModelSelector
from application.tests.utils.model_test_utils import (
    create_mock_client,
    mock_token_usage,
    setup_mock_future,
    setup_model_environment,
)


@pytest.fixture
def model_selector():
    """Create ModelSelector instance with test configuration."""
    with patch.dict(os.environ, setup_model_environment()):
        settings = Settings()
        return ModelSelector(settings)


@pytest.mark.asyncio
async def test_openai_fallback_chain(model_selector):
    """Test OpenAI model fallback chain."""
    test_content = "Fallback response"
    test_tokens = mock_token_usage(40, 20)

    with patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value = create_mock_client("openai")

        # Configure mock to fail with primary model and succeed with fallback
        mock_openai.return_value.chat.completions.create.side_effect = [
            Exception("Primary model error"),  # gpt-4-turbo-preview fails
            setup_mock_future(test_content, test_tokens)  # gpt-4-0125-preview succeeds
        ]

        # Test fallback
        response = await model_selector.generate_completion(
            "test prompt", model="openai"
        )

        assert response.choices[0].message["content"] == test_content
        assert response.usage.total_tokens == test_tokens["total_tokens"]
        assert mock_openai.return_value.chat.completions.create.call_count == 2


@pytest.mark.asyncio
async def test_openai_complete_fallback_chain(model_selector):
    """Test complete OpenAI fallback chain through all models."""
    test_content = "Last resort response"
    test_tokens = mock_token_usage(35, 15)

    with patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value = create_mock_client("openai")

        # Configure mock to fail twice and succeed with last resort
        mock_openai.return_value.chat.completions.create.side_effect = [
            Exception("Primary model error"),  # gpt-4-turbo-preview fails
            Exception("Fallback model error"),  # gpt-4-0125-preview fails
            setup_mock_future(test_content, test_tokens)  # gpt-4 succeeds
        ]

        # Test complete fallback chain
        response = await model_selector.generate_completion(
            "test prompt", model="openai"
        )

        assert response.choices[0].message["content"] == test_content
        assert response.usage.total_tokens == test_tokens["total_tokens"]
        assert mock_openai.return_value.chat.completions.create.call_count == 3


@pytest.mark.asyncio
async def test_cross_model_fallback(model_selector):
    """Test fallback between different model providers."""
    test_content = "Cross-model fallback response"
    test_tokens = mock_token_usage(45, 25)

    # Mock all model clients
    with patch("openai.OpenAI") as mock_openai, \
         patch("anthropic.Anthropic") as mock_anthropic, \
         patch("mistralai.client.MistralClient") as mock_mistral, \
         patch("groq.Groq") as mock_groq:
        mocks = {
            "openai": mock_openai,
            "anthropic": mock_anthropic,
            "mistral": mock_mistral,
            "groq": mock_groq
        }
        # Configure mock clients
        for name, mock in mocks.items():
            mock.return_value = create_mock_client(name)
            if name == "openai":
                # OpenAI fails completely
                mock.return_value.chat.completions.create.side_effect = [
                    Exception("Primary model error"),
                    Exception("Fallback model error"),
                    Exception("Last resort error"),
                ]
            elif name == "anthropic":
                # Anthropic succeeds
                mock_response = setup_mock_future(test_content, test_tokens)
                mock.return_value.messages.create.return_value = mock_response
            else:
                # Other models not used
                mock.return_value.chat.completions.create.side_effect = Exception("Should not be called")

        # Test cross-model fallback
        response = await model_selector.generate_completion(
            "test prompt",
            model="openai",
            fallback_providers=["anthropic", "mistral", "groq"],
        )

        assert response.choices[0].message["content"] == test_content
        assert response.usage.total_tokens == test_tokens["total_tokens"]

        # Verify OpenAI attempts and Claude success
        assert (
            mocks["openai"].return_value.chat.completions.create.call_count
            == 3
        )
        assert mocks["anthropic"].return_value.messages.create.call_count == 1

        # Verify other models weren't called
        assert (
            mocks["mistral"].return_value.chat.completions.create.call_count
            == 0
        )
        assert (
            mocks["groq"].return_value.chat.completions.create.call_count == 0
        )


@pytest.mark.asyncio
async def test_fallback_with_token_monitoring(model_selector):
    """Test token monitoring during fallback scenarios."""
    primary_tokens = mock_token_usage(
        50, 0
    )  # Only prompt tokens for failed request
    fallback_tokens = mock_token_usage(
        50, 30
    )  # Full tokens for successful fallback

    with patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value = create_mock_client("openai")

        # Configure mock to fail with primary model and succeed with fallback
        mock_openai.return_value.chat.completions.create.side_effect = [
            setup_mock_future("", primary_tokens),  # Primary model fails after tokenizing
            setup_mock_future("Fallback response", fallback_tokens)  # Fallback succeeds
        ]

        # Test fallback with token monitoring
        response = await model_selector.generate_completion(
            "test prompt", model="openai"
        )

        assert response.usage.prompt_tokens == fallback_tokens["prompt_tokens"]
        assert (
            response.usage.completion_tokens
            == fallback_tokens["completion_tokens"]
        )
        assert response.usage.total_tokens == fallback_tokens["total_tokens"]


@pytest.mark.asyncio
async def test_fallback_error_handling(model_selector):
    """Test error handling when all fallbacks fail."""
    with patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value = create_mock_client("openai")

        # Configure all attempts to fail
        mock_openai.return_value.chat.completions.create.side_effect = (
            Exception("Model error")
        )

        # Test error handling when all fallbacks fail
        with pytest.raises(Exception) as exc_info:
            await model_selector.generate_completion(
                "test prompt", model="openai"
            )

        assert "Model error" in str(exc_info.value)
        assert mock_openai.return_value.chat.completions.create.call_count == 3
