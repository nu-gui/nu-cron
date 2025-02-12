from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional

from ...models.database import User
from ...services.auth_service import get_current_user
from .test_generator import TestGenerator

router = APIRouter()
test_generator = TestGenerator()


@router.post("/generate")
async def generate_tests(
    code: str,
    language: str,
    test_type: str,
    context: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Generate tests based on code using Mistral 7B
    """
    try:
        result = await test_generator.generate_tests(code, language, test_type, context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_tests(
    tests: str, code: str, language: str, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Validate generated tests for completeness and coverage
    """
    try:
        result = await test_generator.validate_tests(tests, code, language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/performance")
async def generate_performance_tests(
    code: str,
    language: str,
    performance_criteria: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Generate performance tests for the code
    """
    try:
        result = await test_generator.generate_performance_tests(
            code, language, performance_criteria
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
