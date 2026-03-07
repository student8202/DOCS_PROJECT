from pydantic import BaseModel
from typing import List, Optional

class EmployeeBase(BaseModel):
    FullName: str
    IdDepartment: int

class EmployeeCreate(EmployeeBase):
    ID: Optional[int] = None  # Nếu có ID là Update, không có là Insert

class EmployeeResponse(EmployeeBase):
    ID: int
    DeptName: Optional[str] = None

class EmployeeSaveRequest(BaseModel):
    ID: Optional[int] = None
    FullName: str
    IdDepartment: int
    Password: Optional[str] = None  # Chỉ nhập khi tạo mới hoặc đổi pass
    
    class Config:
        from_attributes = True
