from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PLYRA_",
        env_file=".env",
        extra="ignore",
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 7700
    env: Literal["local", "staging", "production"] = "local"
    debug: bool = False

    # Auth
    admin_api_key: str = "plm_admin_changeme"
    # Admin key is used to create/revoke workspace keys via /admin/keys
    # Set this to a strong random value in production

    # Key store — where API keys are stored
    # default: SQLite at ~/.plyra/keys.db
    # set to postgres://... for multi-node deployments
    key_store_url: str = "~/.plyra/keys.db"

    # Memory storage (passed through to plyra-memory)
    store_url: str = "~/.plyra/memory.db"
    vectors_url: str = "~/.plyra/memory.index"
    embed_model: str = "all-MiniLM-L6-v2"

    # Optional: Postgres for memory storage
    # database_url: str | None = None

    # Optional: LLM for extraction + summarization
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None

    # Rate limiting (requests per minute per API key)
    rate_limit_rpm: int = 600

    # CORS
    cors_origins: list[str] = ["*"]

    @classmethod
    def default(cls) -> "ServerConfig":
        return cls()
