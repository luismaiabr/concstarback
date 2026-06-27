from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    JWT_SECRET_KEY: str
    JWT_TOKEN_EXPIRATION_IN_MINUTES: int
    BACK_END_PORT: int = 8000
    ALLOW_ORIGINS: list[str] = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "https://concstarfront.vercel.app"
    ]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
settings = Settings()  # type: ignore
