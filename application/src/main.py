from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import Settings
from .services.environment.routes import router as environment_router

app = FastAPI(
    title=Settings().PROJECT_NAME,
    openapi_url=f"{Settings().API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    environment_router,
    prefix=f"{Settings().API_V1_STR}/environment",
    tags=["environment"]
)
