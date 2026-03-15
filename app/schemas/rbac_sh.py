# app/schemas/rbac_sh.py
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class PermissionCreate(BaseModel):
    # Field(...) bắt buộc phải có, pattern đảm bảo chỉ dùng chữ thường, số và gạch dưới
    code: str = Field(..., pattern=r"^[a-zA-Z0-9_]+$") 
    name: str
    module: str # FO, BO, HR, SYSTEM

    @field_validator('code')
    @classmethod
    def force_lower(cls, v: str) -> str:
        return v.lower()

class RoleCreate(BaseModel):
    code: str = Field(..., pattern=r"^[a-zA-Z0-9_]+$")
    name: str
    module_name: str # FO, BO, HR hoặc SYSTEM
    description: Optional[str] = None

class RoleRead(BaseModel):
    RoleCode: str
    RoleName: Optional[str] = None
    ModuleName: Optional[str] = None
    Description: Optional[str] = None
    
# Schema dùng để gán danh sách Quyền vào 1 Vai trò (LỖI Ở ĐÂY)
class RolePermissionMap(BaseModel):
    role_code: str
    permission_codes: List[str]  # Danh sách các mã quyền (chữ thường) được tích chọn

# Schema dùng để gán Role cho User (Để dùng cho rbac_manage.html)
class UserRoleUpdate(BaseModel):
    username: str
    role_codes: List[str]

# Schema trả về dữ liệu cho DataTables
class UserWithRolesRead(BaseModel):
    Username: str
    FullName: Optional[str]
    Roles: str

class PermissionRead(BaseModel):
    PermissionCode: str
    PermissionName: str
    ModuleName: str

class RoleWithPermsRead(BaseModel):
    RoleCode: str
    RoleName: Optional[str] = None
    ModuleName: Optional[str] = None
    PermList: Optional[str] = "N/A"

class BulkRoleAssignRequest(BaseModel):
    usernames: List[str]  # Danh sách các User được chọn
    role_codes: List[str] # Các Role muốn gán cho nhóm này
