"""Routes for AI-driven requirements analysis and risk assessment."""

from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException

from ...core.ai_assistant import AIAssistant
from ...models.database import User
from ...services.auth_service import get_current_user


router = APIRouter()


@router.post("/analyze")
async def analyze_requirements(
    project_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Analyze project requirements using AI.

    Args:
        project_data: Project requirements and metadata
        current_user: Authenticated user making the request

    Returns:
        Dict containing structured documentation and analysis
    """
    try:
        ai_assistant = AIAssistant()
        analysis_result = await ai_assistant.analyze_requirements(project_data)
        return analysis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk-assessment")
async def assess_risks(
    project_id: int,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Perform risk assessment and feasibility analysis.

    Args:
        project_id: ID of the project to analyze
        current_user: Authenticated user making the request

    Returns:
        Dict containing risk assessment and recommendations
    """
    try:
        ai_assistant = AIAssistant()
        risk_assessment = await ai_assistant.assess_project_risks(project_id)
        return risk_assessment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
