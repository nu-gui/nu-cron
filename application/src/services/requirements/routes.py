from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from ...models.database import User
from ...services.auth_service import get_current_user
from ...core.ai_assistant import AIAssistant

router = APIRouter()

@router.post("/analyze")
async def analyze_requirements(
    project_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Analyze project requirements using AI and generate structured documentation
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
):
    """
    Perform risk assessment and feasibility analysis for a project
    """
    try:
        ai_assistant = AIAssistant()
        risk_assessment = await ai_assistant.assess_project_risks(project_id)
        return risk_assessment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
