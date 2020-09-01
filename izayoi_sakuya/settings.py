from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class Settings(BaseSettings):
    # App basic settings
    DEBUG: bool = Field(True, env="SAKUYA_DEBUG")

settings = Settings()
