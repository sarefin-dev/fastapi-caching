import asyncio
#from functools import lru_cache
from async_lru import alru_cache
from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated


class AppSettings(BaseSettings):
    app_name: str = "My App"

    model_config = SettingsConfigDict(env_file=".env")


@alru_cache(maxsize=1)
async def get_app_config():
    return AppSettings()


ConfigDep = Annotated[AppSettings, Depends(get_app_config)]
