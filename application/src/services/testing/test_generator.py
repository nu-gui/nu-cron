"""AI-powered test generation service using OpenAI models."""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

import openai
import redis
from fastapi import HTTPException


class TestGenerator:
    """Manages test generation, validation, and performance testing using AI."""

    def __init__(self):
        """Initialize test generator with OpenAI client and Redis cache."""
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.redis_client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://redis:6379/0")
        )
        # 1 hour default cache TTL
        self.cache_ttl = int(os.getenv("TEST_GENERATION_CACHE_TTL", "3600"))

    async def generate_tests(
        self,
        code: str,
        language: str,
        test_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate tests based on code using Mistral 7B.

        Args:
            code: Source code to generate tests for
            language: Programming language of the code
            test_type: Type of tests to generate (unit, integration, etc.)
            context: Additional context for test generation

        Returns:
            Dict containing generated tests and metadata
        """
        cache_key = f"test_gen:{hash(code + language + test_type)}"
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)

        try:
            prompt = self._create_test_generation_prompt(
                code, language, test_type, context
            )
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",  # Will use Mistral later
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert test engineer. Generate "
                            "comprehensive tests based on the provided code."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            generated_tests = response.choices[0].message.content
            result = {
                "status": "success",
                "tests": generated_tests,
                "language": language,
                "test_type": test_type,
                "timestamp": datetime.utcnow().isoformat(),
                # Using GPT-4 for now, will switch to Mistral
                "model_used": "gpt-4-turbo-preview",
            }

            # Cache the result
            self.redis_client.setex(
                cache_key, self.cache_ttl, json.dumps(result)
            )

            return result

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise Exception(str(e))

    def _create_test_generation_prompt(
        self,
        code: str,
        language: str,
        test_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a detailed prompt for test generation."""
        framework = self._get_test_framework(language)
        prompt = (
            f"Generate {test_type} tests ({language}):\n\n"
            f"{code}\n\n"
            "Test Requirements:\n"
            f"1. Use appropriate testing framework ({framework})\n"
            "2. Include edge cases and error scenarios\n"
            "3. Follow testing best practices\n"
            "4. Add comprehensive assertions\n"
            "5. Include setup and teardown if needed\n"
        )

        if context:
            context_json = json.dumps(context, indent=2)
            prompt += f"""
Additional Context:
{context_json}
"""

        return prompt

    def _get_test_framework(self, language: str) -> str:
        """Get the appropriate testing framework based on language.

        Args:
            language: Programming language to get framework for

        Returns:
            Name of the recommended testing framework
        """
        frameworks = {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "jest",
            "java": "junit",
            "go": "testing",
        }
        return frameworks.get(language.lower(), "unknown")

    async def validate_tests(
        self, tests: str, code: str, language: str
    ) -> Dict[str, Any]:
        """Validate generated tests for completeness and coverage.

        Args:
            tests: Test code to validate
            code: Source code being tested
            language: Programming language of the code

        Returns:
            Dict containing validation results and metadata
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
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            validation_result = response.choices[0].message.content
            return {
                "status": "success",
                "validation": validation_result,
                "language": language,
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": "gpt-4-turbo-preview",
            }

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise Exception(str(e))

    def _create_test_validation_prompt(
        self, tests: str, code: str, language: str
    ) -> str:
        """Create a detailed prompt for test validation.

        Args:
            tests: Test code to validate
            code: Source code being tested
            language: Programming language of the code

        Returns:
            Formatted prompt string for validation
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
        performance_criteria: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate performance tests for the given code.

        Args:
            code: Source code to generate performance tests for
            language: Programming language of the code
            performance_criteria: Optional performance requirements

        Returns:
            Dict containing generated performance tests and metadata
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
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            performance_tests = response.choices[0].message.content
            return {
                "status": "success",
                "performance_tests": performance_tests,
                "language": language,
                "criteria": performance_criteria,
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": "gpt-4-turbo-preview",
            }

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise Exception(str(e))

    def _create_performance_test_prompt(
        self,
        code: str,
        language: str,
        performance_criteria: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a detailed prompt for performance test generation.

        Args:
            code: Source code to generate performance tests for
            language: Programming language of the code
            performance_criteria: Optional performance requirements and thresholds

        Returns:
            Formatted prompt string for the AI model
        """
        prompt = (
            f"Generate performance tests ({language}):\n\n"
            f"{code}\n\n"
            "Focus on:\n"
            "1. Response time measurements\n"
            "2. Resource utilization tracking\n"
            "3. Load testing scenarios\n"
            "4. Stress testing conditions\n"
            "5. Performance benchmarks\n"
        )

        if performance_criteria:
            criteria_json = json.dumps(performance_criteria, indent=2)
            prompt += f"""
Performance Criteria:
{criteria_json}
"""

        return prompt
