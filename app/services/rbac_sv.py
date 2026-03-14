# app/services/rbac_sv.py
from database.db_connection import get_lv_docs_db
from models.rbac_md import RBACModel
from core.exceptions import DuplicateError  # Giả sử bạn đã định nghĩa lỗi này
from schemas.rbac_sh import PermissionCreate, RoleCreate


class RBACService:
    @staticmethod
    def create_permission_logic(data: PermissionCreate, admin_user: str):
        conn = get_lv_docs_db()
        try:
            cursor = conn.cursor()
            # Kiểm tra trùng Code
            cursor.execute(
                f"SELECT PermissionCode FROM {RBACModel.TABLE_PERMISSION_LIST} WHERE PermissionCode = ?",
                (data.code,),
            )
            if cursor.fetchone():
                raise DuplicateError(f"Quyền '{data.code}' đã tồn tại")

            cursor.execute(
                RBACModel.SQL_INSERT_PERMISSION,
                (data.code, data.name, data.module, admin_user),
            )
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def map_role_permissions_logic(role_code: str, perm_codes: list, admin_user: str):
        conn = get_lv_docs_db()
        try:
            cursor = conn.cursor()
            # Xóa cũ gán mới (Sync)
            cursor.execute(
                f"DELETE FROM {RBACModel.TABLE_ROLE_PERMISSIONS} WHERE RoleCode = ?",
                (role_code,),
            )
            for p_code in perm_codes:
                cursor.execute(
                    RBACModel.SQL_INSERT_ROLE_PERMISSION,
                    (role_code, p_code, admin_user),
                )
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def get_permissions_logic():
        conn = get_lv_docs_db()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(RBACModel.SQL_SELECT_PERMISSIONS)

            # Lấy tên các cột từ cursor
            columns = [column[0] for column in cursor.description]

            # Ép dữ liệu thành List các Dictionary một cách thủ công và sạch sẽ
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            return results
        finally:
            conn.close()

    @staticmethod
    def get_roles_logic():
        conn = get_lv_docs_db()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(RBACModel.SQL_SELECT_ROLES)
            # 1. Lấy danh sách TÊN CỘT sạch sẽ (RoleCode, RoleName, Description)
            columns = [column[0] for column in cursor.description]

            # 2. Ép dữ liệu thành List các Dictionary thuần túy
            results = []
            for row in cursor.fetchall():
                # zip kết nối tên cột với giá trị tương ứng của dòng đó
                results.append(dict(zip(columns, row)))

            return results
        finally:
            conn.close()

    @staticmethod
    def create_role_logic(data: RoleCreate, admin_user: str):
        conn = get_lv_docs_db()
        if not conn: return False
        try:
            cursor = conn.cursor()
            # 1. Kiểm tra xem RoleCode đã tồn tại chưa
            cursor.execute(f"SELECT RoleCode FROM dbo.tbl_Roles WHERE RoleCode = ?", (data.code,))
            if cursor.fetchone():
                raise DuplicateError(f"Vai trò '{data.code}' đã tồn tại trong hệ thống")
            
            # 2. Thực hiện INSERT
            cursor.execute(RBACModel.SQL_INSERT_ROLE, (
                data.code, data.name, data.module_name, data.description, admin_user
            ))
            conn.commit()
            return True
        finally:
            conn.close()
