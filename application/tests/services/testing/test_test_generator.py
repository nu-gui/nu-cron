"""Test suite for the TestGenerator class."""

import json
import os
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from application.src.services.testing.test_generator import TestGenerator


@pytest.fixture
def test_generator():
    """Create a TestGenerator instance with mocked dependencies."""
    with patch("redis.Redis.from_url") as mock_redis, patch(
        "openai.OpenAI"
    ) as mock_openai, patch(
        "application.src.services.ai.model_selector" ".ModelSelector"
    ) as mock_selector, patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "test-key",
            "HELICONE_API_KEY": "test-helicone-key",
        },
    ):
        # Mock Redis
        mock_redis_client = Mock()
        mock_redis_client.get.return_value = None
        mock_redis.return_value = mock_redis_client

        # Mock OpenAI
        mock_openai.return_value = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = {
            "content": "Generated test content"
        }
        mock_openai.return_value.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        # Mock ModelSelector
        mock_selector.return_value = Mock()
        mock_selector.return_value.select_model.return_value = {
            "name": "gpt-4-turbo-preview",
            "max_tokens": 4096,
            "temperature": 0.7,
            "priority": 1,
        }
        mock_selector.return_value.get_fallback_model.return_value = {
            "name": "gpt-4-0125-preview",
            "max_tokens": 4096,
            "temperature": 0.7,
            "priority": 2,
        }

        yield TestGenerator()


@pytest.mark.asyncio
async def test_generate_tests_success(test_generator):
    """Test successful test generation with OpenAI."""
    # Mock data
    code = "def add(a, b): return a + b"
    language = "python"
    test_type = "unit"
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = {
        "content": "def test_add(): assert add(1, 2) == 3"
    }
    test_generator.openai_client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    # Test
    result = await test_generator.generate_tests(code, language, test_type)

    # Assertions
    assert result["status"] == "success"
    assert "tests" in result
    assert result["language"] == "python"
    assert result["test_type"] == "unit"
    assert result["model_used"] == "gpt-4-turbo-preview"


@pytest.mark.asyncio
async def test_generate_tests_with_cache(test_generator):
    """Test test generation with Redis cache hit."""
    # Mock data
    code = "def add(a, b): return a + b"
    language = "python"
    test_type = "unit"
    cached_result = {
        "status": "success",
        "tests": "def test_add(): assert add(1, 2) == 3",
        "language": "python",
        "test_type": "unit",
        "timestamp": datetime.utcnow().isoformat(),
        "model_used": "gpt-4-turbo-preview",
    }
    test_generator.redis_client.get.return_value = json.dumps(
        cached_result
    ).encode()

    # Test
    result = await test_generator.generate_tests(code, language, test_type)

    # Assertions
    assert result == cached_result
    test_generator.openai_client.chat.completions.create.assert_not_called()


@pytest.mark.asyncio
async def test_validate_tests_success(test_generator):
    """Test successful test validation with OpenAI."""
    # Mock data
    tests = "def test_add(): assert add(1, 2) == 3"
    code = "def add(a, b): return a + b"
    language = "python"
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = {
        "content": "Test validation: Good coverage"
    }
    test_generator.openai_client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    # Test
    result = await test_generator.validate_tests(tests, code, language)

    # Assertions
    assert result["status"] == "success"
    assert "validation" in result
    assert result["language"] == "python"
    assert result["model_used"] == "gpt-4-turbo-preview"


@pytest.mark.asyncio
async def test_generate_performance_tests_success(test_generator):
    """Test successful performance test generation with OpenAI."""
    # Mock data
    code = "def process_data(): pass"
    language = "python"
    performance_criteria = {"response_time": "100ms", "throughput": "1000rps"}
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = {
        "content": "Performance test: measure response time"
    }
    test_generator.openai_client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    # Test
    result = await test_generator.generate_performance_tests(
        code, language, performance_criteria
    )

    # Assertions
    assert result["status"] == "success"
    assert "performance_tests" in result
    assert result["language"] == "python"
    assert result["criteria"] == performance_criteria
    assert result["model_used"] == "gpt-4-turbo-preview"


@pytest.mark.asyncio
async def test_generate_tests_error_handling(test_generator):
    """Test error handling in test generation."""
    # Mock data
    code = "invalid code"
    language = "unknown"
    test_type = "invalid"
    test_generator.openai_client.chat.completions.create = AsyncMock(
        side_effect=Exception("API Error")
    )

    # Test
    with pytest.raises(Exception) as exc_info:
        await test_generator.generate_tests(code, language, test_type)

    assert str(exc_info.value) == "API Error"
