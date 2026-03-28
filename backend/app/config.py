"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """TakiOS application settings.

    All values can be overridden via environment variables or .env file.
    """

    # Application
    app_name: str = "TakiOS"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Auth
    secret_key: str = "change-me-to-a-random-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database
    database_url: str = "postgresql+asyncpg://takios:takios@localhost:5432/takios"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "takios"
    max_artifact_upload_size_bytes: int = 10 * 1024 * 1024

    # AI
    ai_provider: str = "anthropic"
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Agent Team — Multi-Model Routing
    model_routing_profile: str = "balanced"  # quality | balanced | budget | inherit
    opus_model: str = "claude-opus-4-20250514"
    sonnet_model: str = "claude-sonnet-4-20250514"
    haiku_model: str = "claude-haiku-3-20250414"

    # Agent Team — AutoDream Motor
    dream_interval_hours: int = 12
    dream_session_threshold: int = 50
    max_index_lines: int = 200

    model_config = {"env_file": "../.env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
