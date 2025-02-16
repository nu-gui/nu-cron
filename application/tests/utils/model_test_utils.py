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
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = {"content": content}
    if tokens:
        mock_response.usage = tokens
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
    future = asyncio.Future()
    future.set_result(create_mock_completion(content, tokens))
    return future


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


def create_mock_client(model: str) -> Mock:
    """Create mock client for different AI models.

    Args:
        model: The model type ('openai', 'claude', 'mistral', 'groq')

    Returns:
        Mock client object
    """
    mock_client = Mock()

    if model == "openai":
        mock_client.chat.completions.create = AsyncMock()
    elif model == "claude":
        mock_client.messages.create = AsyncMock()
    elif model == "mistral":
        mock_client.chat.completions.create = AsyncMock()
    elif model == "groq":
        mock_client.chat.completions.create = AsyncMock()

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
