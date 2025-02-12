import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime
import json

from application.src.services.code_generation.code_generator import CodeGenerator

@pytest.fixture
def code_generator():
    with patch('redis.Redis.from_url') as mock_redis, \
         patch('openai.Completion.create') as mock_openai_create:
        mock_redis.return_value = Mock()
        mock_redis.return_value.get.return_value = None  # Default to cache miss
        yield CodeGenerator(), mock_openai_create

@pytest.mark.asyncio
async def test_generate_code_success(code_generator):
    code_generator, mock_openai_create = code_generator
    # Mock data
    requirements = {"feature": "user authentication", "language": "python"}
    language = "python"
    mock_response = Mock()
    mock_response.choices = [Mock(text="def authenticate_user(): pass")]
    future = asyncio.Future()
    future.set_result(mock_response)
    mock_openai_create.return_value = future
    
    # Test
    result = await code_generator.generate_code(requirements, language)
    
    # Assertions
    assert result["status"] == "success"
    assert "code" in result
    assert result["language"] == "python"
    assert result["model_used"] == "gpt-4-turbo-preview"

@pytest.mark.asyncio
async def test_generate_code_with_cache(code_generator):
    code_generator, mock_openai_create = code_generator
    # Mock data
    requirements = {"feature": "user authentication", "language": "python"}
    language = "python"
    cached_result = {
        "status": "success",
        "code": "def authenticate_user(): pass",
        "language": "python",
        "timestamp": datetime.utcnow().isoformat(),
        "model_used": "gpt-4-turbo-preview"
    }
    code_generator.redis_client.get.return_value = json.dumps(cached_result).encode()
    
    # Test
    result = await code_generator.generate_code(requirements, language)
    
    # Assertions
    assert result == cached_result
    mock_openai_create.assert_not_called()

@pytest.mark.asyncio
async def test_review_code_success(code_generator):
    code_generator, mock_openai_create = code_generator
    # Mock data
    code = "def authenticate_user(): pass"
    language = "python"
    mock_response = Mock()
    mock_response.choices = [Mock(text="Code review: Looks good")]
    future = asyncio.Future()
    future.set_result(mock_response)
    mock_openai_create.return_value = future
    
    # Test
    result = await code_generator.review_code(code, language)
    
    # Assertions
    assert result["status"] == "success"
    assert "review" in result
    assert result["language"] == "python"
    assert result["model_used"] == "gpt-4-turbo-preview"

@pytest.mark.asyncio
async def test_optimize_code_success(code_generator):
    code_generator, mock_openai_create = code_generator
    # Mock data
    code = "def slow_function(): pass"
    language = "python"
    optimization_goals = ["performance", "memory"]
    mock_response = Mock()
    mock_response.choices = [Mock(text="Optimized code: def fast_function(): pass")]
    future = asyncio.Future()
    future.set_result(mock_response)
    mock_openai_create.return_value = future
    
    # Test
    result = await code_generator.optimize_code(code, language, optimization_goals)
    
    # Assertions
    assert result["status"] == "success"
    assert "optimized_code" in result
    assert result["language"] == "python"
    assert result["model_used"] == "gpt-4-turbo-preview"
    assert result["optimization_goals"] == optimization_goals

@pytest.mark.asyncio
async def test_generate_code_error_handling(code_generator):
    code_generator, mock_openai_create = code_generator
    # Mock data
    requirements = {"feature": "invalid"}
    language = "unknown"
    mock_openai_create.side_effect = Exception("API Error")
    
    # Test
    with pytest.raises(Exception) as exc_info:
        await code_generator.generate_code(requirements, language)
    
    assert str(exc_info.value) == "API Error"
