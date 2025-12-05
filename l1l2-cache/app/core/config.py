from async_lru import alru_cache  # async version of alru_cache
from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated


class AppSettings(BaseSettings):
    app_name: str = "L1 & L2 Cache Example in FastAPI (Fallback)"

    model_config = SettingsConfigDict(env_file=".env")


@alru_cache
async def get_config():
    return AppSettings()


ConfigDep = Annotated[AppSettings, Depends(get_config)]
