from services.rbac_sv import RBACService
from fastapi import HTTPException, Request, status


class RBACController:
    @staticmethod
    def get_my_permissions(username: str):
        # Chỉ gọi Service và trả về kết quả
        perms = RBACService.get_user_permissions_logic(username)
        return {"username": username, "permissions": perms}

    @staticmethod
    def guard(request: Request, required_perm: str):
        # Controller chỉ điều phối và ném lỗi HTTP
        if not RBACService.check_permission_logic(request, required_perm):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bạn không có quyền: {required_perm.lower()}",
            )
        return True

    @staticmethod
    def get_roles_list():
        return RBACService.get_all_roles_logic()

    @staticmethod
    def apply_user_roles(data, admin_user: str):
        try:
            RBACService.update_user_roles_logic(
                data.username, data.role_codes, admin_user
            )
            return {"status": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
