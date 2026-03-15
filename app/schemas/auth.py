from pydantic import BaseModel, ConfigDict,Field
from typing import List, Optional
from datetime import datetime

# Schema cho dữ liệu Login gửi lên
class LoginRequest(BaseModel):
    username: str
    password: str

# Schema cho dữ liệu User trả về (Mapping từ Database)
class UserInDB(BaseModel):
    Username: str
    FullName: Optional[str] = None
    IsActive: bool
    Source_Map: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True) # Thay cho class Config cũ

# Schema trả về cho Client sau khi Login thành công
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    full_name: str
    permissions: List[str] = []

# user change password   
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)
    confirm_password: str