import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Khai báo các biến, không gán giá trị mặc định nhạy cảm ở đây
    PROJECT_NAME: str = "SMILE HR PROFESSIONAL"
    SECRET_KEY: str 
    
    # THÊM 2 DÒNG NÀY ĐỂ KHỚP VỚI FILE .ENV
    DEBUG: bool = True
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    DB_DRIVER: str = "{ODBC Driver 17 for SQL Server}"
    DB_SERVER: str 
    DB_NAME: str 
    DB_USER: str 
    DB_PASSWORD: str 

    @property
    def connection_string(self) -> str:
        return (
            f"DRIVER={self.DB_DRIVER};"
            f"SERVER={self.DB_SERVER};"
            f"DATABASE={self.DB_NAME};"
            f"UID={self.DB_USER};"
            f"PWD={self.DB_PASSWORD};"
            "Trusted_Connection=no;" 
        )

    class Config:
        # Pydantic sẽ tự tìm file .env ở thư mục gốc và map vào các biến trên
        env_file = ".env" 
        case_sensitive = True

settings = Settings()