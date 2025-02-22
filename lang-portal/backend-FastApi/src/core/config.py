from pydantic import BaseModel
from pathlib import Path
from typing import Any, Dict, Optional

class Settings(BaseModel):
    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Language Learning Portal"
    VERSION: str = "0.2.0"
    
    # Database
    DATABASE_URL: str = "sqlite:///./words.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    # Paths
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent.parent
    MIGRATIONS_DIR: Path = ROOT_DIR / "migrations"
    SEEDS_DIR: Path = ROOT_DIR / "seeds"

settings = Settings() 