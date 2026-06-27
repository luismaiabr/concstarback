from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import json

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

    @field_validator("ALLOW_ORIGINS", mode="before")
    @classmethod
    def parse_allow_origins(cls, v):
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.startswith("[") and v_stripped.endswith("]"):
                try:
                    cleaned = v_stripped.replace("'", '"')
                    return json.loads(cleaned)
                except Exception:
                    v_stripped = v_stripped[1:-1]
            return [x.strip().strip("'\"") for x in v_stripped.split(",") if x.strip()]
        return v

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
settings = Settings()  # type: ignore
