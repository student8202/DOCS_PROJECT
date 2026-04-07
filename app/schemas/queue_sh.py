from pydantic import BaseModel
from typing import Optional

# Dành cho nhân viên gửi hồ sơ
class QueueSendSchema(BaseModel):
    ModuleName: str
    RefType: str
    RefID: str
    DeviceID: str
    TemplateID: int
    
    # Cho phép null/thiếu khi gửi từ JS, Backend sẽ tự điền vào sau
    RenderedHtml: Optional[str] = None 
    CreatedBy: Optional[str] = None
    
    # Các trường mở rộng cho SMILE
    ConfirmNum: Optional[str] = None
    FolioNum: Optional[str] = None
    GroupCode: Optional[str] = None
    IdAddition: Optional[int] = None

# Dành cho kết quả ký từ Tablet gửi về
class QueueSignSchema(BaseModel):
    QueueID: int
    Signature_Base64: str
    
class DeviceResetSchema(BaseModel):
    DeviceID: str
    
class QueueCompleteSchema(BaseModel):
    QueueID: int
    Guest_Signature: str      # Chuỗi ảnh Base64 của khách
    Reception_Signature: str  # Chuỗi ảnh Base64 của lễ tân (có thể rỗng)
