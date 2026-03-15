# app/controllers/rbac_ct.py
from fastapi import HTTPException, status, Request
from fastapi.responses import RedirectResponse
from services.rbac_sv import RBACService
from core.deps import templates  # Import từ deps
from core.exceptions import DuplicateError
from loguru import logger

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
        
    ### xử lý Role Permission
    @staticmethod
    def get_role_config_data(role_code: str):
        """Lấy dữ liệu để hiển thị Modal Răng cưa (Lọc theo Module)"""
        try:
            # Gọi Service để lấy cả list 'tất cả quyền' và 'quyền hiện có'
            data = RBACService.get_perms_by_role_module_logic(role_code)
            return data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi tải cấu hình: {str(e)}")

    @staticmethod
    def save_role_permissions(data, admin_user: str):
        """Xử lý nút Cập nhật cấu hình (Xóa cũ - Ghi mới)"""
        try:
            # data là Schema RolePermissionMap (role_code và list permission_codes)
            RBACService.update_role_mapping_logic(data.role_code, data.permission_codes, admin_user)
            return {"status": "success", "message": "Đã cập nhật quyền thành công"}
        except Exception as e:
            raise HTTPException(status_code=400, detail="Không thể lưu cấu hình quyền")
        
    @staticmethod
    def render_role_permissions(request: Request, role_code: str):
        # 1. Lấy dữ liệu từ Service
        data = RBACService.get_perms_by_role_module_logic(role_code)
        
        # 2. Nhóm dữ liệu ngay trong Python cho Jinja2 dễ đọc
        grouped = {}
        for p in data['all_perms']:
            mod = p['ModuleName'] or 'KHÁC'
            if mod not in grouped: grouped[mod] = []
            grouped[mod].append(p)
        
        # 3. Render đúng mẩu HTML nhỏ này thôi
        return templates.TemplateResponse("admin/rbac_perm_items.html", {
            "request": request,
            "grouped_perms": grouped,
            "current_perms": data['current_perms']
        })
        
    ## gán role cho user
    @staticmethod
    def render_manage_page(request: Request):
        # 1. Lấy danh sách quyền từ Session (đã lưu lúc Login)
        user_perms = request.session.get("permissions", [])
        
        # 2. KIỂM TRA QUYỀN (Sử dụng chữ thường 'admin')
        if "admin" not in [p.lower() for p in user_perms if p]:
            # Nếu không có quyền admin, đá về Dashboard
            return RedirectResponse(url="/dashboard")
            
        # 3. RENDER TRANG (Dùng templates từ deps để có Global Context get_perms)
        return templates.TemplateResponse("admin/rbac_manage.html", {"request": request})

    @staticmethod
    def list_users_with_roles():
        try:
            # Chỉ đơn giản là trả về list dict từ service
            data = RBACService.get_users_with_roles_logic()
            return data
        except Exception as e:
            logger.error(f"Lỗi Controller: {str(e)}")
            raise HTTPException(status_code=500, detail="Lỗi hệ thống")
    
    @staticmethod
    def get_user_current_roles(username: str): # Phải có tham số username ở đây
        try:
            # Gọi hàm lấy quyền của 1 người
            return RBACService.get_user_roles_logic(username)
        except Exception as e:
            logger.error(f"Lỗi lấy quyền user {username}: {str(e)}")
            raise HTTPException(status_code=500, detail="Lỗi tải quyền nhân viên")
     
    @staticmethod
    def render_user_role_config(request: Request, username: str):
        # 1. Lấy dữ liệu từ Service
        all_roles = RBACService.get_roles_with_details_logic()
        my_roles = RBACService.get_user_roles_logic(username) # List ['admin',...]

        # 2. Nhóm Roles theo ModuleName ngay tại Python
        grouped = {}
        for r in all_roles:
            mod = r['ModuleName'] or 'HỆ THỐNG'
            if mod not in grouped: grouped[mod] = []
            grouped[mod].append(r)
        
        # 3. Trả về Fragment HTML
        return templates.TemplateResponse("admin/rbac_user_role_items.html", {
            "request": request,
            "grouped_roles": grouped,
            "my_roles": my_roles
        })
        
    @staticmethod
    def list_roles_detailed():
        """Lấy danh sách Role kèm chuỗi Permission để hiện dạng cây trên UI"""
        try:
            # Gọi Service thực hiện SQL JOIN 3 bảng
            data = RBACService.get_roles_with_details_logic()
            return data
        except Exception as e:
            from fastapi import HTTPException
            from loguru import logger
            logger.error(f"Lỗi lấy danh sách Role chi tiết: {str(e)}")
            raise HTTPException(status_code=500, detail="Lỗi hệ thống khi tải danh mục vai trò")
        
    @staticmethod
    def save_user_roles(data, admin_user: str):
        try:
            # data.username lấy từ Schema UserRoleUpdate
            RBACService.update_user_roles_logic(data.username, data.role_codes, admin_user)
            
            # Trả về kèm username để xác nhận ở Frontend
            return {
                "status": "success", 
                "message": f"Đã cập nhật vai trò cho nhân viên: {data.username}"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @staticmethod
    def bulk_assign_user_roles(data, admin_user: str):
        """Xử lý gán quyền cho danh sách nhiều nhân viên cùng lúc"""
        try:
            # data là Schema BulkRoleAssignRequest chứa 'usernames' và 'role_codes'
            success = RBACService.bulk_update_user_roles_logic(
                data.usernames, 
                data.role_codes, 
                admin_user
            )
            
            if success:
                count = len(data.usernames)
                return {
                    "status": "success", 
                    "message": f"Đã cập nhật vai trò thành công cho {count} nhân viên."
                }
            
            raise Exception("Cập nhật thất bại")
            
        except Exception as e:
            from fastapi import HTTPException
            from loguru import logger
            logger.error(f"Lỗi Gán quyền hàng loạt: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="Lỗi hệ thống khi xử lý gán quyền hàng loạt"
            )
        
