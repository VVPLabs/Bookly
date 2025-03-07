
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM : str= os.getenv("JWT_ALGORITHM", "")
    REDIS_URL:str = "redis://redis_db:6379/0"
    MAIL_USERNAME: str= os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD:SecretStr= SecretStr(os.getenv("MAIL_PASSWORD",""))
    MAIL_FROM:str= os .getenv("MAIL_FROM", "")
    MAIL_PORT:int= int(os.getenv("MAIL_PORT", ""))
    MAIL_SERVER:str= os.getenv("MAIL_SERVER", "") 
    MAIL_STARTTLS:bool= True
    MAIL_SSL_TLS:bool= False
    USE_CREDENTIALS:bool =True
    VALIDATE_CERTS :bool= True
    DOMAIN:str= os.getenv("DOMAIN", "")


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

Config = Settings()


broker_url= Config.REDIS_URL
result_backend= Config.REDIS_URL