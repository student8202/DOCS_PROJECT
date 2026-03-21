from pydantic import BaseModel, Field, field_validator
from typing import Optional

class TemplateCreateSchema(BaseModel):
    TemplateID: Optional[int] = None
    TemplateCode: str = Field(..., pattern="^[A-Z0-9_]+$")
    TemplateName: str = Field(..., min_length=2, max_length=255)
    
    @field_validator('TemplateCode')
    @classmethod
    def normalize_code(cls, v: str):
        return v.upper().strip()

    @field_validator('TemplateName')
    @classmethod
    def normalize_name(cls, v: str):
        return v.strip() # Giữ nguyên Tiếng Việt có dấu
    
    # Ràng buộc các phân hệ hợp lệ
    ModuleName: str = Field(..., pattern="^(FO|POS|BO|HR)$")
    SubModule: str = Field(..., min_length=2)
    Category: str = Field(..., min_length=2)
    
    IsCustom: int = 1
    HtmlContent: Optional[str] = None
    IsActive: bool = True

    class Config:
        from_attributes = True
        
class TemplateSystemSchema(BaseModel):
    TemplateID: Optional[int] = None
    TemplateCode: str = Field(..., pattern="^[a-zA-Z0-9_]+$")
    TemplateName: str = Field(..., min_length=2)
    FilePath: str = Field(..., min_length=5) # Bắt buộc có đường dẫn file
    IsCustom: int = 0 # Fix cứng là 0
    IsActive: bool = True
