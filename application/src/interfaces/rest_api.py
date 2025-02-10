from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, TypedDict
from datetime import datetime

class ProjectResponse(TypedDict):
    id: int
    name: str
    description: str
    requirements: Dict[str, Any]
    created_at: str

class ProjectListResponse(TypedDict):
    status: str
    projects: List[ProjectResponse]

from ..models.database import User, Project
from ..services.auth_service import get_current_user

router = APIRouter()

@router.post("/projects/")
async def create_project(
    project_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create a new project with requirements for analysis
    """
    try:
        project = Project(
            name=project_data["name"],
            description=project_data["description"],
            requirements=project_data.get("requirements", {}),
            created_by_id=current_user.id,
            created_at=datetime.utcnow()
        )
        # Note: In a real implementation, we would save to database here
        return {
            "status": "success",
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "requirements": project.requirements,
                "created_at": project.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}")
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get project details by ID
    """
    # Note: In a real implementation, we would fetch from database
    project = Project(
        id=project_id,
        name="Test Project",
        description="Test Description",
        requirements={},
        created_by_id=current_user.id,
        created_at=datetime.utcnow()
    )
    return {
        "status": "success",
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "requirements": project.requirements,
            "created_at": project.created_at.isoformat()
        }
    }

@router.get("/projects/")
async def list_projects(
    current_user: User = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """
    List all projects for the current user
    """
    # Note: In a real implementation, we would fetch from database
    projects = [
        Project(
            id=1,
            name="Test Project 1",
            description="Test Description 1",
            requirements={},
            created_by_id=current_user.id,
            created_at=datetime.utcnow()
        )
    ]
    return ProjectListResponse(
        status="success",
        projects=[
            ProjectResponse(
                id=project.id,
                name=project.name,
                description=project.description,
                requirements=project.requirements,
                created_at=project.created_at.isoformat()
            )
            for project in projects
        ]
    )

@router.put("/projects/{project_id}")
async def update_project(
    project_id: int,
    project_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update project details and requirements
    """
    try:
        # Note: In a real implementation, we would update in database
        project = Project(
            id=project_id,
            name=project_data.get("name", ""),
            description=project_data.get("description", ""),
            requirements=project_data.get("requirements", {}),
            created_by_id=current_user.id,
            created_at=datetime.utcnow()
        )
        return {
            "status": "success",
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "requirements": project.requirements,
                "created_at": project.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
