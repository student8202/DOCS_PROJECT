# app/routers/rbac_rt.py
from fastapi import APIRouter, Request
from schemas.rbac_sh import PermissionCreate, RolePermissionMap
from controllers.rbac_ct import RBACController
from schemas.rbac_sh import PermissionRead, RoleRead, RoleCreate
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
