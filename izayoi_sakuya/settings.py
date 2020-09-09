import os

from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class Settings(BaseSettings):
    # Directories
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))

    # App basic settings
    DEBUG: bool = Field(True, env="SAKUYA_DEBUG")


settings = Settings()
