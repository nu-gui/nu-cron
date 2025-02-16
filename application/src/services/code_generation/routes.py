"""Routes for code generation and optimization using AI models."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException

from application.src.models.database import User
from application.src.services.auth_service import get_current_user

from .code_generator import CodeGenerator

router = APIRouter()
code_generator = None  # Initialize lazily


def get_code_generator():
    global code_generator
    if code_generator is None:
        code_generator = CodeGenerator()
    return code_generator


@router.post("/generate")
async def generate_code(
    requirements: Dict[str, Any],
    language: str,
    context: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Generate code based on requirements using GPT-4 Turbo
    """
    try:
        result = await get_code_generator().generate_code(
            requirements, language, context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review")
async def review_code(
    code: str,
    language: str,
    context: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Review code using Claude 3 for better analysis
    """
    try:
        result = await get_code_generator().review_code(
            code, language, context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize")
async def optimize_code(
    code: str,
    language: str,
    optimization_goals: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Optimize code for performance and efficiency
    """
    try:
        result = await get_code_generator().optimize_code(
            code, language, optimization_goals
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
