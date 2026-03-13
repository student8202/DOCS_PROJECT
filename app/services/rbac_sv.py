from database.db_connection import get_lv_docs_db
from fastapi import HTTPException, Request
from models.rbac_md import RBACModel # Gọi Model vào đây

class RBACService:
    @staticmethod
    def get_user_permissions_logic(username: str):
        conn = get_lv_docs_db()
        if not conn: return []
        try:
            cursor = conn.cursor()
            # Truy vấn gộp từ bảng gán Role sang bảng danh sách Quyền
            sql = """
                SELECT DISTINCT PermissionCode 
                FROM dbo.tbl_RolePermissions 
                WHERE RoleCode IN (SELECT RoleCode FROM dbo.tbl_UserRoles WHERE Username = ?)
            """
            cursor.execute(sql, (username,))
            # Trả về list phẳng: ['VIEW_FO', 'SIGN_FO', ...]
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def has_permission(request: Request, required_perm: str) -> bool:
        """
        Kiểm tra xem User có quyền cụ thể không.
        Quyền ADMIN luôn được thông qua mọi cửa.
        """
        user_perms = request.session.get("permissions", [])
        
        # Nếu có quyền cụ thể hoặc là đại ca ADMIN thì cho qua
        if required_perm in user_perms or RBACModel.PERM_ADMIN in user_perms:
            return True
        return False
    
    @staticmethod
    def check_permission_logic(request: Request, required_perm: str) -> bool:
        # Lấy list quyền từ Session (đã được lưu lúc Login)
        user_perms = request.session.get("permissions", [])
        
        # Ép kiểu an toàn và kiểm tra (Quyền admin hoặc quyền cụ thể)
        perms_lower = [p.lower() for p in user_perms if p]
        
        if required_perm.lower() in perms_lower or RBACModel.PERM_ADMIN in perms_lower:
            return True
        return False