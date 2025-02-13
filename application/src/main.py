"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .core.config import Settings
from .models.database import init_db
from .services.code_generation import code_generation_router
from .services.requirements import requirements_router
from .services.testing import testing_router
from .services.environment.routes import router as environment_router

settings = Settings()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Driven Software Development Lifecycle Management System",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
# Include API routes with appropriate prefixes
api_prefix = settings.API_V1_STR
# Route configuration
routes = [
    (code_generation_router, "code"),
    (requirements_router, "requirements"),
    (testing_router, "testing"),
    (environment_router, "environment", ["environment"]),
]

# Register routes with appropriate prefixes
for route_info in routes:
    if len(route_info) == 2:
        router, path = route_info
        app.include_router(router, prefix=f"{api_prefix}/{path}")
    else:
        router, path, tags = route_info
        app.include_router(router, prefix=f"{api_prefix}/{path}", tags=tags)


# Initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on application startup."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    init_db(database_url)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Check application health status."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
