from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    PROJECT_NAME: str = "AI-SDLC"
    API_V1_STR: str = "/api/v1"

    # OpenAI configuration
    OPENAI_MAX_RETRIES: int = 3
    OPENAI_TIMEOUT: float = 30.0
    OPENAI_DEFAULT_HEADERS: dict = {"X-Custom-Header": "nu-cron"}

    # Helicone configuration
    HELICONE_API_KEY: str = ""  # Set via environment variable
    HELICONE_CACHE_ENABLED: bool = True
    HELICONE_CACHE_TTL: int = 3600  # 1 hour
    HELICONE_RETRY_ENABLED: bool = True
    HELICONE_RATE_LIMIT_POLICY: str = "throttle"

    # Model configuration
    AI_MODELS: dict[str, dict[str, Any]] = {
        "openai": {
            "name": "gpt-4-turbo-preview",
            "max_tokens": 4096,
            "temperature": 0.7,
            "priority": 1,
            "fallback_chain": ["gpt-4-0125-preview", "gpt-4"]
        },
        "claude": {
            "name": "claude-3-opus-20240229",
            "max_tokens": 4096,
            "temperature": 0.7,
            "priority": 2,
            "fallback_chain": []
        },
        "mistral": {
            "name": "mistral-large-latest",
            "max_tokens": 4096,
            "temperature": 0.7,
            "priority": 3,
            "fallback_chain": []
        },
        "groq": {
            "name": "mixtral-8x7b-32768",
            "max_tokens": 4096,
            "temperature": 0.7,
            "priority": 4,
            "fallback_chain": []
        }
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
