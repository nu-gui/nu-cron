"""Test suite for the CodeGenerator class."""

import os
import json
from datetime import datetime
import asyncio
from unittest.mock import Mock, patch, AsyncMock

import pytest

from application.src.services.code_generation.code_generator import (
    CodeGenerator,
)


@pytest.fixture
def code_generator():
    """Create a CodeGenerator instance with mocked dependencies."""
    with patch("redis.Redis.from_url") as mock_redis, \
         patch("openai.OpenAI") as mock_openai, \
         patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        mock_redis_client = Mock()
        mock_redis_client.get.return_value = None
        mock_redis.return_value = mock_redis_client
        mock_openai.return_value = Mock()
        
        # Set up async response mock
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = {"content": "Generated code content"}
        mock_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
        yield CodeGenerator()


@pytest.mark.asyncio
async def test_generate_code_success(code_generator):
    """Test successful code generation with OpenAI."""
    # Mock data
    requirements = {"feature": "user authentication", "language": "python"}
    language = "python"
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = {"content": "def authenticate_user(): pass"}
    code_generator.openai_client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    # Test
    result = await code_generator.generate_code(requirements, language)

    # Assertions
    assert result["status"] == "success"
    assert "code" in result
    assert result["language"] == "python"
    assert result["model_used"] == "gpt-4-turbo-preview"


@pytest.mark.asyncio
async def test_generate_code_with_cache(code_generator):
    """Test code generation with Redis cache hit."""
    # Mock data
    requirements = {"feature": "user authentication", "language": "python"}
    language = "python"
    cached_result = {
        "status": "success",
        "code": "def authenticate_user(): pass",
        "language": "python",
        "timestamp": datetime.utcnow().isoformat(),
        "model_used": "gpt-4-turbo-preview",
    }
    code_generator.redis_client.get.return_value = json.dumps(
        cached_result
    ).encode()

    # Test
    result = await code_generator.generate_code(requirements, language)

    # Assertions
    assert result == cached_result
    code_generator.openai_client.chat.completions.create.assert_not_called()


@pytest.mark.asyncio
async def test_review_code_success(code_generator):
    """Test successful code review with OpenAI."""
    # Mock data
    code = "def authenticate_user(): pass"
    language = "python"
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = {"content": "Code review: Looks good"}
    code_generator.openai_client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    # Test
    result = await code_generator.review_code(code, language)

    # Assertions
    assert result["status"] == "success"
    assert "review" in result
    assert result["language"] == "python"
    assert result["model_used"] == "gpt-4-turbo-preview"


@pytest.mark.asyncio
async def test_optimize_code_success(code_generator):
    """Test successful code optimization with OpenAI."""
    # Mock data
    code = "def slow_function(): pass"
    language = "python"
    optimization_goals = ["performance", "memory"]
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = {"content": "Optimized code: def fast_function(): pass"}
    code_generator.openai_client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    # Test
    result = await code_generator.optimize_code(
        code, language, optimization_goals
    )

    # Assertions
    assert result["status"] == "success"
    assert "optimized_code" in result
    assert result["language"] == "python"
    assert result["model_used"] == "gpt-4-turbo-preview"
    assert result["optimization_goals"] == optimization_goals


@pytest.mark.asyncio
async def test_generate_code_error_handling(code_generator):
    """Test error handling in code generation."""
    # Mock data
    requirements = {"feature": "invalid"}
    language = "unknown"
    code_generator.openai_client.chat.completions.create = AsyncMock(
        side_effect=Exception("API Error")
    )

    # Test
    with pytest.raises(Exception) as exc_info:
        await code_generator.generate_code(requirements, language)

    assert str(exc_info.value) == "500: API Error"
