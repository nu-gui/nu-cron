from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
import os

from .core.ai_assistant import AIAssistant
from .models.database import init_db, User, Project
from .services.auth_service import get_current_user
from .interfaces.rest_api import router as api_router
from .services.code_generation import code_generation_router
from .services.requirements import requirements_router
from .services.testing import testing_router
from .core.config import Settings
from .services.environment.routes import router as environment_router

app = FastAPI(
    title=Settings().PROJECT_NAME,
    description="AI-Driven Software Development Lifecycle Management System",
    version="1.0.0",
    openapi_url=f"{Settings().API_V1_STR}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=Settings().API_V1_STR)
app.include_router(code_generation_router, prefix=f"{Settings().API_V1_STR}/code")
app.include_router(requirements_router, prefix=f"{Settings().API_V1_STR}/requirements")
app.include_router(testing_router, prefix=f"{Settings().API_V1_STR}/testing")
app.include_router(environment_router, prefix=f"{Settings().API_V1_STR}/environment", tags=["environment"])

# Initialize database
@app.on_event("startup")
async def startup_event():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    init_db(database_url)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
