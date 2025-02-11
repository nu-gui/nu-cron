"""Test generator module for AI-driven code."""

from typing import Dict, Any, Optional
import os
from datetime import datetime
import json
import redis
from fastapi import HTTPException
import openai


class TestGenerator:
    def __init__(self):
        self.openai_client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.redis_client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://redis:6379/0")
        )
        # 1 hour default
        self.cache_ttl = int(os.getenv("TEST_GENERATION_CACHE_TTL", "3600"))

    async def generate_tests(
        self,
        code: str,
        language: str,
        test_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate tests based on code using Mistral 7B.

        Currently using GPT-4 as placeholder.
        """
        cache_key = (
            f"test_gen:{hash(code + language + test_type)}"
        )
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)

        try:
            prompt = self._create_test_generation_prompt(
                code, language, test_type, context
            )
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",  # Will be replaced with Mistral 7B
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert test engineer. Generate "
                            "comprehensive tests based on the provided code."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            generated_tests = response.choices[0].message.content
            result = {
                "status": "success",
                "tests": generated_tests,
                "language": language,
                "test_type": test_type,
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": "gpt-4-turbo-preview"  # Will be replaced with Mistral 7B
            }
            
            # Cache the result
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(result)
            )
            
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def _create_test_generation_prompt(
        self,
        code: str,
        language: str,
        test_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a detailed prompt for test generation
        """
        prompt = f"""Generate {test_type} tests for the following {language} code:

{code}

Test Requirements:
1. Use appropriate testing framework ({self._get_test_framework(language)})
2. Include edge cases and error scenarios
3. Follow testing best practices
4. Add comprehensive assertions
5. Include setup and teardown if needed
"""

        if context:
            prompt += f"""
Additional Context:
{json.dumps(context, indent=2)}
"""

        return prompt

    def _get_test_framework(self, language: str) -> str:
        """
        Get the appropriate testing framework based on language
        """
        frameworks = {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "jest",
            "java": "junit",
            "go": "testing"
        }
        return frameworks.get(language.lower(), "unknown")

    async def validate_tests(
        self,
        tests: str,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Validate generated tests for completeness and coverage
        """
        try:
            prompt = self._create_test_validation_prompt(tests, code, language)
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert test validator. Analyze tests "
                            "for completeness and coverage."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            validation_result = response.choices[0].message.content
            return {
                "status": "success",
                "validation": validation_result,
                "language": language,
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": "gpt-4-turbo-preview"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def _create_test_validation_prompt(
        self,
        tests: str,
        code: str,
        language: str
    ) -> str:
        """
        Create a detailed prompt for test validation
        """
        return f"""Validate the following {language} tests against the code:

Code:
{code}

Tests:
{tests}

Please analyze:
1. Test coverage and completeness
2. Edge case handling
3. Error scenario coverage
4. Assertion quality
5. Test maintainability
"""

    async def generate_performance_tests(
        self,
        code: str,
        language: str,
        performance_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate performance tests for the code
        """
        try:
            prompt = self._create_performance_test_prompt(
                code, language, performance_criteria
            )
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert in performance testing. "
                            "Generate comprehensive performance tests."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            performance_tests = response.choices[0].message.content
            return {
                "status": "success",
                "performance_tests": performance_tests,
                "language": language,
                "criteria": performance_criteria,
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": "gpt-4-turbo-preview"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def _create_performance_test_prompt(
        self,
        code: str,
        language: str,
        performance_criteria: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a detailed prompt for performance test generation
        """
        prompt = f"""Generate performance tests for the following {language} code:

{code}

Focus on:
1. Response time measurements
2. Resource utilization tracking
3. Load testing scenarios
4. Stress testing conditions
5. Performance benchmarks
"""

        if performance_criteria:
            prompt += f"""
Performance Criteria:
{json.dumps(performance_criteria, indent=2)}
"""

        return prompt
