from fastapi import APIRouter, Request
from schemas.rbac_sh import UserPermissionsRead
from controllers.rbac_ct import RBACController
from core.deps import templates # Import từ deps

router = APIRouter(prefix="/rbac", tags=["RBAC"])


@router.get("/my-permissions", response_model=UserPermissionsRead)
async def get_permissions(request: Request):
    username = request.session.get("username")
    return RBACController.get_my_permissions(username)


@router.get("/roles-list", include_in_schema=False)
async def roles_list():
    return RBACController.get_roles_list()


@router.post("/update-roles")
async def update_roles(request: Request, data: UserRoleUpdate):
    admin = request.session.get("username", "SYSTEM")
    return RBACController.apply_user_roles(data, admin)

@router.get("/manage", include_in_schema=False)
async def rbac_manage_page(request: Request):
    # Router gọi trực tiếp sang Controller để xử lý render
    return RBACController.render_manage_page(request)

