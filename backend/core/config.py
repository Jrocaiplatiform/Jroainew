from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "J-ROC AI Platform"
    environment: str = "development"
    allowed_hosts: str = "localhost,127.0.0.1"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    rate_limit_per_minute: int = 120
    require_https: bool = False
    database_url: str = "sqlite:///./jroc.db"
    jwt_secret: str = "CHANGE-ME-IN-PRODUCTION"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    brain_enabled: bool = False
    openai_api_key: str = ""
    openai_model: str = "gpt-5.6"
    openrouter_api_key: str = ""
    groq_api_key: str = ""
    google_api_key: str = ""
    mistral_api_key: str = ""
    cloudflare_api_token: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_host_list(self) -> list[str]:
        return [h.strip() for h in self.allowed_hosts.split(",") if h.strip()]

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def validate_runtime(self) -> None:
        if self.rate_limit_per_minute < 1:
            raise ValueError("RATE_LIMIT_PER_MINUTE must be positive")
        if self.environment.lower() in {"production", "prod"}:
            if len(self.jwt_secret) < 32 or self.jwt_secret == "CHANGE-ME-IN-PRODUCTION":
                raise ValueError("Production JWT_SECRET must be at least 32 characters")
            if not self.require_https:
                raise ValueError("Production requires HTTPS")
            if not self.allowed_host_list or "*" in self.allowed_host_list:
                raise ValueError("Production requires an explicit allowed host list")
            if not self.cors_origin_list or "*" in self.cors_origin_list:
                raise ValueError("Production requires explicit CORS origins")


settings = Settings()
