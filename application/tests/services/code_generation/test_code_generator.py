"""Test suite for the CodeGenerator class."""

import json
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from application.src.services.code_generation.code_generator import (
    CodeGenerator,
)


@pytest.fixture
def code_generator():
    """Create a CodeGenerator instance with mocked dependencies."""
    with patch("redis.Redis.from_url") as mock_redis, patch("openai.api_key"):
        mock_redis.return_value = Mock()
        yield CodeGenerator()


@pytest.mark.asyncio
async def test_generate_code_success(code_generator):
    """Test successful code generation with OpenAI."""
    # Mock data
    requirements = {"feature": "user authentication", "language": "python"}
    language = "python"
    mock_response = Mock()
    mock_response.choices = [
        Mock(message=Mock(content="def authenticate_user(): pass"))
    ]
    code_generator.openai_client.chat.completions.create = Mock(
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
    mock_response.choices = [
        Mock(message=Mock(content="Code review: Looks good"))
    ]
    code_generator.openai_client.chat.completions.create = Mock(
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
    mock_response.choices = [
        Mock(message=Mock(content="Optimized code: def fast_function(): pass"))
    ]
    code_generator.openai_client.chat.completions.create = Mock(
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
    code_generator.openai_client.chat.completions.create = Mock(
        side_effect=Exception("API Error")
    )

    # Test
    with pytest.raises(Exception) as exc_info:
        await code_generator.generate_code(requirements, language)

    assert str(exc_info.value) == "API Error"
