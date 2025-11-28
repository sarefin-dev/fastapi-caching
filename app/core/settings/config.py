from functools import lru_cache

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated


class BasicSettings(BaseSettings):
    """
    Defines the structure for application settings. 
    Settings are loaded from environment variables or a .env file.
    """

    # The application's name. It uses a default value if not found 
    # in the environment or .env file. It is being used for testing whether the app is getting loaded or not.
    app_name: str = "In case env file is missing"

    database_url: str = "sqlite:///database.db"

    model_config: SettingsConfigDict = SettingsConfigDict(env_file=".env")


@lru_cache
def get_basic_settings():
    """
    Loads and caches the BasicSettings instance.
    
    The @lru_cache decorator ensures that:
    1. The function is called only once per process.
    2. Subsequent calls return the cached result immediately, 
       avoiding file I/O and object creation overhead.
    """
    #Print statement to prove the function is executed only on the first call
    print("I should not be printed twice")
    return BasicSettings()


# Use this dependency whenever a function needs access to the BasicSettings object.
BasicSettingsDep = Annotated[BasicSettings, Depends(get_basic_settings)]
