from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    PROJECT_NAME: str = "AI-SDLC"
    API_V1_STR: str = "/api/v1"

    # OpenAI configuration
    OPENAI_MAX_RETRIES: int = 3
    OPENAI_TIMEOUT: float = 30.0
    OPENAI_DEFAULT_HEADERS: dict = {"X-Custom-Header": "nu-cron"}

    # Model configuration
    OPENAI_MODELS = {
        "gpt-4-turbo": {
            "name": "gpt-4-turbo-preview",
            "max_tokens": 4096,
            "temperature": 0.7,
            "priority": 1,  # Default model
        },
        "gpt-4-mini": {
            "name": "gpt-4-0125-preview",
            "max_tokens": 4096,
            "temperature": 0.7,
            "priority": 2,  # Fallback model
        },
        "gpt-4": {
            "name": "gpt-4",
            "max_tokens": 8192,
            "temperature": 0.7,
            "priority": 3,  # Last resort
        },
    }

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
