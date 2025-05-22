from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str
    PROJECT_DESCRIPTION: str
    PROJECT_VERSION: str = "1.0.0"
    MONGODB_URL: str = "mongodb://localhost:27017/"
    MONGODB_DATABASE: str = "ecommercedb"
    MONGODB_MAX_CONNECTIONS_COUNT: int = 10
    MONGODB_MIN_CONNECTIONS_COUNT: int = 1

settings = Settings()     