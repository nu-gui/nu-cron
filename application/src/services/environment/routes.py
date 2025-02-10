from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from .environment_manager import EnvironmentManager
from ...core.config import Settings

router = APIRouter()
settings = Settings()

@router.post("/create")
async def create_environment(env_name: str, env_type: str) -> Dict[str, Any]:
    """Create a new development environment."""
    manager = EnvironmentManager(settings.DOCKER_COMPOSE_PATH)
    success = manager.create_environment(env_name, env_type)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create environment")
    return {"message": f"Environment {env_name} created successfully"}

@router.delete("/destroy")
async def destroy_environment(env_name: str, env_type: str) -> Dict[str, Any]:
    """Destroy a development environment."""
    manager = EnvironmentManager(settings.DOCKER_COMPOSE_PATH)
    success = manager.destroy_environment(env_name, env_type)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to destroy environment")
    return {"message": f"Environment {env_name} destroyed successfully"}

@router.post("/scale")
async def scale_environment(env_name: str, service: str, replicas: int) -> Dict[str, Any]:
    """Scale services in an environment."""
    manager = EnvironmentManager(settings.DOCKER_COMPOSE_PATH)
    success = manager.scale_environment(env_name, service, replicas)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to scale environment")
    return {"message": f"Service {service} scaled to {replicas} replicas"}
