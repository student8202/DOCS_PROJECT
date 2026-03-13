from pydantic import BaseModel
from typing import List

class UserPermissionsRead(BaseModel):
    username: str
    permissions: List[str]
    
class PermissionErrorResponse(BaseModel):
    detail: str = "Bạn không có quyền truy cập chức năng này"
    
class PermissionCheck(BaseModel):
    username: str
    has_access: bool

class UserRoleUpdate(BaseModel):
    username: str
    role_codes: List[str]

class RoleRead(BaseModel):
    RoleCode: str
    RoleName: str