
# pydantic v2 moved BaseSettings into a separate package named
# `pydantic-settings`.  If you see a `ModuleNotFoundError` when
# importing below it's because the dependency hasn't been installed.
# The requirements.txt already lists `pydantic-settings`, so make
# sure you've run `pip install -r requirements.txt` in the
# virtual environment.  We also catch the error here and raise a
# clearer message.
try:
    from pydantic_settings import BaseSettings
except ImportError as exc:
    raise ImportError(
        "Missing dependency 'pydantic-settings'. "
        "Install it with `pip install pydantic-settings` or "
        "`pip install -r requirements.txt`."
    ) from exc

from pydantic import field_validator
from typing import Optional, List

class Settings(BaseSettings):
    # App settings
    app_name: str = "Face Recognition Campus Monitoring API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database
    database_url: str = "mysql+mysql.connector://root:@localhost:3306/face_recognition_system"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = [
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://192.168.1.100:8000",
        "*",
    ]
    
    # Face Recognition Settings
    face_embeddings_threshold: float = 0.6
    
    @field_validator('debug', mode='before')
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
