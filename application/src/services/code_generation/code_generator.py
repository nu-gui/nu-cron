from typing import Dict, Any, List, Optional
import openai
import os
from datetime import datetime
import json
import redis
from fastapi import HTTPException


class CodeGenerator:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.redis_client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://redis:6379/0")
        )
        # 1 hour default
        self.cache_ttl = int(os.getenv("CODE_GENERATION_CACHE_TTL", "3600"))

    async def generate_code(
        self,
        requirements: Dict[str, Any],
        language: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate code based on requirements using GPT-4 Turbo
        """
        cache_key = f"code_gen:{hash(json.dumps(requirements))}"
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)

        try:
            prompt = self._create_code_generation_prompt(
                requirements, language, context
            )
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert software developer. Generate "
                            "high-quality, secure, and efficient code."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            generated_code = response.choices[0].message.content
            result = {
                "status": "success",
                "code": generated_code,
                "language": language,
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": "gpt-4-turbo-preview",
            }

            # Cache the result
            self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(result))

            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def _create_code_generation_prompt(
        self,
        requirements: Dict[str, Any],
        language: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a detailed prompt for code generation
        """
        prompt = (
            f"Generate {language} code based on requirements:\n\n"
            f"Requirements:\n{json.dumps(requirements, indent=2)}\n\n"
            f"Language: {language}\n"
        )

        if context:
            prompt += "\nAdditional Context:\n" f"{json.dumps(context, indent=2)}\n"

        prompt += (
            "\nPlease provide:\n"
            "1. Implementation following best practices\n"
            "2. Error handling and input validation\n"
            "3. Comments explaining complex logic\n"
            "4. Type hints (if applicable)\n"
            "5. Security considerations\n"
        )

        return prompt

    async def review_code(
        self, code: str, language: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Review code using Claude 3 for better analysis
        """
        try:
            prompt = self._create_code_review_prompt(code, language, context)
            # Note: Claude integration will be added here
            # For now, using GPT-4 as a placeholder
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Expert code reviewer: analyze code for "
                            "quality, security, and performance."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            review_result = response.choices[0].message.content
            return {
                "status": "success",
                "review": review_result,
                "language": language,
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": "gpt-4-turbo-preview",
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def _create_code_review_prompt(
        self, code: str, language: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a detailed prompt for code review
        """
        prompt = f"""Review the following {language} code:

{code}

Please analyze for:
1. Code quality and best practices
2. Security vulnerabilities
3. Performance optimizations
4. Error handling
5. Documentation completeness
"""

        if context:
            prompt += f"""
Additional Context:
{json.dumps(context, indent=2)}
"""

        return prompt

    async def optimize_code(
        self, code: str, language: str, optimization_goals: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Optimize code for performance and efficiency
        """
        try:
            prompt = self._create_optimization_prompt(
                code, language, optimization_goals
            )
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Expert optimizer: improve code for "
                            "better performance and efficiency."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            optimized_code = response.choices[0].message.content
            return {
                "status": "success",
                "optimized_code": optimized_code,
                "language": language,
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": "gpt-4-turbo-preview",
                "optimization_goals": optimization_goals,
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def _create_optimization_prompt(
        self, code: str, language: str, optimization_goals: Optional[List[str]] = None
    ) -> str:
        """
        Create a detailed prompt for code optimization
        """
        prompt = f"""Optimize the following {language} code:

{code}

Focus on:
1. Time complexity
2. Space efficiency
3. Resource utilization
4. Algorithm improvements
5. Memory management
"""

        if optimization_goals:
            prompt += f"""
Specific Optimization Goals:
{json.dumps(optimization_goals, indent=2)}
"""

        return prompt
