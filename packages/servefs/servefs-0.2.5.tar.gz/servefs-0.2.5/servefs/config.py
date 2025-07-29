from pathlib import Path
from typing import Union, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = False
    BASIC_AUTH: Optional[str] = None
    ROOT: Path = Path("./files")

    class Config:
        env_prefix = "SERVEFS_"

settings = Settings()