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

app = FastAPI(
    title="AI-SDLC System",
    description="AI-Driven Software Development Lifecycle Management System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")
app.include_router(code_generation_router, prefix="/api/v1/code")
app.include_router(requirements_router, prefix="/api/v1/requirements")

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
