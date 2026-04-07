import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "LaVie Project - Digital Archive" 
    
    # LV_DOCS
    LV_DOCS_SERVER: str
    LV_DOCS_DB: str
    LV_DOCS_UID: str
    LV_DOCS_PWD: str
    
    # LV_DOCS
    LV_DOCS_AR_SERVER: str
    LV_DOCS_AR_DB: str
    LV_DOCS_AR_UID: str
    LV_DOCS_AR_PWD: str
    
    # SMILE_FO
    SMILE_FO_SERVER: str
    SMILE_FO_DB: str
    SMILE_FO_UID: str
    SMILE_FO_PWD: str
    
    # SMILE_BO
    SMILE_BO_SERVER: str
    SMILE_BO_DB: str
    SMILE_BO_UID: str
    SMILE_BO_PWD: str
    
    # SMILE_HR
    SMILE_HR_SERVER: str
    SMILE_HR_DB: str
    SMILE_HR_UID: str
    SMILE_HR_PWD: str
    
    # Auth
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Cấu hình nạp file .env
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
