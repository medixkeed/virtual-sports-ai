from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Virtual Sports AI"
    database_url: str = "sqlite:///./virtual_sports_ai.db"
    secret_key: str = "dev-change-me-in-production-use-long-random-string"
    access_token_expire_minutes: int = 60 * 24 * 7
    refresh_interval_minutes: int = 5
    rebuild_sports_data_on_startup: bool = True
    historical_season_count: int = 9
    free_prediction_limit: int = 5
    data_provider: str = "betpawa"
    betpawa_base_url: str = "https://www.betpawa.ug"
    betpawa_timeout_seconds: float = 10.0
    betpawa_user_agent: str = "VirtualSportsAI/1.0 (+public-data-client)"
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"


settings = Settings()
