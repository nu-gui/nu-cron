"""Shared utilities for AI model testing."""

import asyncio
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, Mock


def create_mock_completion(
    content: str, tokens: Optional[Dict[str, int]] = None
) -> Mock:
    """Create mock completion response for AI models.

    Args:
        content: The response content
        tokens: Optional token usage statistics

    Returns:
        Mock object simulating model response
    """
    mock_response = AsyncMock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = {"content": content}
    if tokens:
        # Create a class to hold token values
        class Usage:
            def __init__(self, tokens):
                self.prompt_tokens = tokens["prompt_tokens"]
                self.completion_tokens = tokens["completion_tokens"]
                self.total_tokens = tokens["total_tokens"]
        # Create usage instance with actual values
        mock_response.usage = Usage(tokens)
    return mock_response


def setup_mock_future(
    content: str, tokens: Optional[Dict[str, int]] = None
) -> asyncio.Future:
    """Setup asyncio.Future with mock response.

    Args:
        content: The response content
        tokens: Optional token usage statistics

    Returns:
        Future containing mock response
    """
    mock_response = create_mock_completion(content, tokens)
    if asyncio.get_event_loop().is_running():
        future = asyncio.Future()
        future.set_result(mock_response)
        return mock_response  # Return mock response directly for async tests
    return mock_response


def mock_token_usage(
    prompt_tokens: int, completion_tokens: int
) -> Dict[str, int]:
    """Create token usage dictionary.

    Args:
        prompt_tokens: Number of tokens in prompt
        completion_tokens: Number of tokens in completion

    Returns:
        Dictionary with token usage statistics
    """
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
    }


def create_mock_client(provider: str) -> Mock:
    """Create mock client for different AI models.

    Args:
        provider: The provider name ('openai', 'claude', 'mistral', 'groq')

    Returns:
        Mock client object
    """
    mock_client = Mock()
    mock_client.name = provider  # Add name attribute for mock identification
    mock_client.default_headers = {
        "Helicone-Auth": "test-key",
        "Helicone-Cache-Enabled": "true",
        "Helicone-Cache-TTL": "3600",
    }

    if provider == "openai":
        mock_client.chat.completions.create = AsyncMock()
        mock_client.chat.completions.create.return_value = create_mock_completion("Test response")
    elif provider in ["claude", "anthropic"]:
        mock_client.messages.create = AsyncMock()
        mock_client.messages.create.return_value = create_mock_completion("Test response")
    elif provider == "mistral":
        mock_client.chat.completions.create = AsyncMock()
        mock_client.chat.completions.create.return_value = create_mock_completion("Test response")
        mock_client.client = AsyncMock()  # Add client attribute for MistralClient
    elif provider == "groq":
        mock_client.chat.completions.create = AsyncMock()
        mock_client.chat.completions.create.return_value = create_mock_completion("Test response")

    return mock_client


def setup_model_environment() -> Dict[str, Any]:
    """Setup test environment variables for all models.

    Returns:
        Dictionary of test environment variables
    """
    return {
        "OPENAI_API_KEY": "test-openai-key",
        "ANTHROPIC_API_KEY": "test-claude-key",
        "GROQ_API_KEY": "test-groq-key",
        "MISTRAL_API_KEY": "test-mistral-key",
        "HELICONE_API_KEY": "test-helicone-key",
    }
