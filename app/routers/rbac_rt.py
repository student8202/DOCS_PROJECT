# app/routers/rbac_rt.py
from fastapi import APIRouter, Request
from controllers.rbac_ct import RBACController
from schemas.rbac_sh import (PermissionCreate, RolePermissionMap,PermissionRead, 
                             RoleRead, RoleCreate,UserRoleUpdate,RoleWithPermsRead,BulkRoleAssignRequest)
from typing import List  

router = APIRouter(prefix="/rbac", tags=["RBAC"])

@router.post("/permissions/add")
async def api_add_permission(request: Request, data: PermissionCreate):
    admin = request.session.get("username", "SYSTEM")
    return RBACController.add_permission(data, admin)

@router.post("/roles/map-permissions")
async def api_map_permissions(request: Request, data: RolePermissionMap):
    admin = request.session.get("username", "SYSTEM")
    return RBACController.update_role_mapping(data, admin)

@router.get("/manage", include_in_schema=False)
async def rbac_manage_page(request: Request):
    """Lộ trình mở trang Quản lý User & Role"""
    return RBACController.render_manage_page(request)

@router.get("/users-roles-data", include_in_schema=False)
async def get_users_roles_data():
    return RBACController.list_users_with_roles()

@router.get("/setup", include_in_schema=False)
async def rbac_setup_page(request: Request):
    # Gọi Controller để kiểm tra quyền admin trước khi render
    return RBACController.render_setup_page(request)

@router.get("/permissions-list", response_model=List[PermissionRead])
async def get_permissions():
    return RBACController.list_permissions()

@router.get("/roles-list", response_model=List[RoleRead])
async def get_roles():
    return RBACController.list_roles()

@router.post("/roles/add") # ĐÂY LÀ ĐIỀU HƯỚNG BẠN ĐANG THIẾU
async def api_add_role(request: Request, data: RoleCreate):
    # Lấy admin từ session để ghi log CreatedBy
    admin_user = request.session.get("username", "SYSTEM")
    return RBACController.add_role(data, admin_user)

### Role Permission
# Route 1: Lấy dữ liệu để đổ vào Modal khi nhấn Răng cưa
@router.get("/role-config/{role_code}")
async def api_get_role_config(role_code: str):
    return RBACController.get_role_config_data(role_code)

# Route 2: Nhận dữ liệu từ Modal gửi lên để lưu vào Database
@router.post("/roles/save-permissions")
async def api_save_role_perms(request: Request, data: RolePermissionMap):
    # Lấy admin từ session để ghi log di sản CreatedBy
    admin_user = request.session.get("username", "SYSTEM")
    return RBACController.save_role_permissions(data, admin_user)

@router.get("/role-config-html/{role_code}", include_in_schema=False)
async def api_get_role_config_html(request: Request, role_code: str):
    # Router gọi Controller để render mẩu HTML (Fragment)
    return RBACController.render_role_permissions(request, role_code)

## gán role cho user
@router.get("/user-roles/{username}", response_model=List[str])
async def get_user_roles(username: str):
    return RBACController.get_user_current_roles(username)

@router.get("/roles-detailed-list", response_model=List[RoleWithPermsRead])
async def get_roles_detailed():
    # Router mỏng, chỉ gọi Controller
    return RBACController.list_roles_detailed()

@router.get("/user-role-config-html/{username}", include_in_schema=False)
async def api_get_user_role_html(request: Request, username: str):
    return RBACController.render_user_role_config(request, username)

@router.post("/users/save-roles")
async def api_save_user_roles(request: Request, data: UserRoleUpdate):
    # Lấy admin từ session để ghi log di sản
    admin_user = request.session.get("username", "SYSTEM")
    return RBACController.save_user_roles(data, admin_user)

@router.post("/users/bulk-save-roles")
async def api_bulk_save_roles(request: Request, data: BulkRoleAssignRequest):
    # Lấy admin từ session để ghi log Audit cho từng dòng bản ghi
    admin_user = request.session.get("username", "SYSTEM")
    
    # Router mỏng, chỉ chuyển tiếp sang Controller
    return RBACController.bulk_assign_user_roles(data, admin_user)
