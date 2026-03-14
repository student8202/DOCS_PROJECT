# app/controllers/rbac_ct.py
from fastapi import HTTPException, status, Request
from fastapi.responses import RedirectResponse
from services.rbac_sv import RBACService
from core.deps import templates  # Import từ deps
from core.exceptions import DuplicateError


class RBACController:
    @staticmethod
    def render_setup_page(request: Request):
        # Sử dụng hàm get_perms đã khai báo toàn cục để check
        user_perms = request.session.get("permissions", [])
        if "admin" not in user_perms:
            return RedirectResponse(url="/dashboard")

        return templates.TemplateResponse("admin/rbac_setup.html", {"request": request})

    @staticmethod
    def add_permission(data, admin_user: str):
        try:
            RBACService.create_permission_logic(data, admin_user)
            return {"status": "success", "message": "Đã thêm quyền mới"}
        except DuplicateError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Lỗi hệ thống")

    @staticmethod
    def update_role_mapping(data, admin_user: str):
        try:
            RBACService.map_role_permissions_logic(
                data.role_code, data.permission_codes, admin_user
            )
            return {
                "status": "success",
                "message": "Cập nhật quyền cho Vai trò thành công",
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def list_permissions():
        try:
            return RBACService.get_permissions_logic()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def list_roles():
        try:
            return RBACService.get_roles_logic()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def add_role(data, admin_user: str):
        try:
            RBACService.create_role_logic(data, admin_user)
            return {"status": "success", "message": "Đã thêm vai trò mới thành công"}
        except DuplicateError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Lỗi hệ thống khi thêm vai trò")
