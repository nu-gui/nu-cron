"""Test suite for token usage monitoring across different AI models."""

import pytest
import os
from unittest.mock import Mock, patch

from application.src.services.ai.model_selector import ModelSelector
from application.src.core.config import Settings
from application.tests.utils.model_test_utils import (
    setup_mock_future,
    mock_token_usage,
    create_mock_client,
    setup_model_environment,
)


@pytest.fixture
def model_selector():
    """Create ModelSelector instance with test configuration."""
    with patch.dict(os.environ, setup_model_environment()):
        settings = Settings()
        return ModelSelector(settings)


@pytest.mark.asyncio
async def test_openai_token_monitoring(model_selector):
    """Test OpenAI token monitoring via Helicone."""
    test_content = "OpenAI test response"
    test_tokens = mock_token_usage(50, 30)

    with patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value = create_mock_client("openai")
        mock_openai.return_value.chat.completions.create.return_value = (
            setup_mock_future(test_content, test_tokens)
        )

        # Test token tracking
        response = await model_selector.generate_completion(
            "test prompt", model="openai"
        )

        assert response.usage.prompt_tokens == test_tokens["prompt_tokens"]
        assert (
            response.usage.completion_tokens
            == test_tokens["completion_tokens"]
        )
        assert response.usage.total_tokens == test_tokens["total_tokens"]

        # Verify Helicone headers
        mock_openai.assert_called_once()
        client = mock_openai.return_value
        assert "Helicone-Auth" in client.default_headers
        assert "Helicone-Cache-Enabled" in client.default_headers
        assert "Helicone-Cache-TTL" in client.default_headers


@pytest.mark.asyncio
async def test_claude_token_monitoring(model_selector):
    """Test Claude token monitoring."""
    test_content = "Claude test response"
    test_tokens = mock_token_usage(45, 25)

    with patch("anthropic.Anthropic") as mock_claude:
        mock_claude.return_value = create_mock_client("claude")
        mock_claude.return_value.messages.create.return_value = (
            setup_mock_future(test_content, test_tokens)
        )

        # Test token tracking
        response = await model_selector.generate_completion(
            "test prompt", model="claude"
        )

        assert response.usage.prompt_tokens == test_tokens["prompt_tokens"]
        assert (
            response.usage.completion_tokens
            == test_tokens["completion_tokens"]
        )
        assert response.usage.total_tokens == test_tokens["total_tokens"]


@pytest.mark.asyncio
async def test_mistral_token_monitoring(model_selector):
    """Test Mistral token monitoring."""
    test_content = "Mistral test response"
    test_tokens = mock_token_usage(40, 20)

    with patch("mistralai.Client") as mock_mistral:
        mock_mistral.return_value = create_mock_client("mistral")
        mock_mistral.return_value.chat.completions.create.return_value = (
            setup_mock_future(test_content, test_tokens)
        )

        # Test token tracking
        response = await model_selector.generate_completion(
            "test prompt", model="mistral"
        )

        assert response.usage.prompt_tokens == test_tokens["prompt_tokens"]
        assert (
            response.usage.completion_tokens
            == test_tokens["completion_tokens"]
        )
        assert response.usage.total_tokens == test_tokens["total_tokens"]


@pytest.mark.asyncio
async def test_groq_token_monitoring(model_selector):
    """Test Groq token monitoring."""
    test_content = "Groq test response"
    test_tokens = mock_token_usage(35, 15)

    with patch("groq.Groq") as mock_groq:
        mock_groq.return_value = create_mock_client("groq")
        mock_groq.return_value.chat.completions.create.return_value = (
            setup_mock_future(test_content, test_tokens)
        )

        # Test token tracking
        response = await model_selector.generate_completion(
            "test prompt", model="groq"
        )

        assert response.usage.prompt_tokens == test_tokens["prompt_tokens"]
        assert (
            response.usage.completion_tokens
            == test_tokens["completion_tokens"]
        )
        assert response.usage.total_tokens == test_tokens["total_tokens"]


@pytest.mark.asyncio
async def test_token_monitoring_with_cache(model_selector):
    """Test token monitoring with caching enabled."""
    test_content = "Cached response"
    test_tokens = mock_token_usage(30, 10)

    with patch("redis.Redis.from_url") as mock_redis:
        # Setup Redis mock
        mock_redis_client = Mock()
        mock_redis_client.get.return_value = None
        mock_redis.return_value = mock_redis_client

        # Test caching behavior
        with patch("openai.OpenAI") as mock_openai:
            mock_openai.return_value = create_mock_client("openai")
            mock_openai.return_value.chat.completions.create.return_value = (
                setup_mock_future(test_content, test_tokens)
            )

            # First call - should use API
            response1 = await model_selector.generate_completion(
                "test prompt", model="openai"
            )

            # Second call - should use cache
            mock_redis_client.get.return_value = response1
            response2 = await model_selector.generate_completion(
                "test prompt", model="openai"
            )

            assert response1.usage.total_tokens == response2.usage.total_tokens
            (
                mock_openai.return_value.chat.completions.create.assert_called_once()
            )


@pytest.mark.asyncio
async def test_token_monitoring_error_handling(model_selector):
    """Test token monitoring error handling."""
    with patch("openai.OpenAI") as mock_openai:
        mock_openai.return_value = create_mock_client("openai")
        mock_openai.return_value.chat.completions.create.side_effect = (
            Exception("Token limit exceeded")
        )

        with pytest.raises(Exception) as exc_info:
            await model_selector.generate_completion(
                "test prompt", model="openai"
            )
        assert "Token limit exceeded" in str(exc_info.value)
