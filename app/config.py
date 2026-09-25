#this file defines all configuration vlaues for the app
#(DB connection info, app name, etc.)

#pydantic settings: automatically reads from environment variables and .env file and validates

from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    #MongoDB settings
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "Corporate_facility_desk"

    #Gives the app a name that can be used in the API docs and other places
    APP_NAME: str = "Corporate Facility Desk App API"

    #informs pydantic settings to load values from .env file and use utf-8 encoding
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

#Shared settings Objecct that all other files can import and use to access config values
settings = Settings()