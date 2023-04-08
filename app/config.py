from pydantic import BaseSettings, EmailStr

class Settings(BaseSettings):
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str
    MONGO_INITDB_DATABASE:str

    EMAIL_HOST: str
    EMAIL_PORT: str
    EMAIL_USERNAME: str
    EMAIL_PASSWORD:str
    EMAIL_FROM:EmailStr

    DATABASE_URL: str
    CLIENT_ORIGIN: str

    # https://fastapi.tiangolo.com/advanced/settings/
    class Config:
        env_file = './.env'

settings = Settings()