"""Application configuration and environment settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and environment configuration."""
    PROJECT_NAME: str = "AI-SDLC"
    API_V1_STR: str = "/api/v1"
    
    # Environment configuration
    DOCKER_COMPOSE_PATH: str = "docker-compose.yml"
    KUBERNETES_CONFIG_PATH: str = "~/.kube/config"
    
    # Resource defaults
    DEFAULT_CPU_LIMIT: str = "2"
    DEFAULT_MEMORY_LIMIT: str = "4Gi"
    
    # Test environment settings
    TEST_ENV: str = "integration"
    TEST_DB_HOST: str = "test-db"
    
    # Monitoring configuration
    PROMETHEUS_PORT: int = 9090
    GRAFANA_PORT: int = 3000
    
    class Config:
        case_sensitive = True
        env_file = ".env"
