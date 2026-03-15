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
            
################### xử lý Role Permission
    @staticmethod
    def get_perms_by_role_module_logic(role_code: str):
        conn = get_lv_docs_db()
        try:
            cursor = conn.cursor()
            # 1. Lấy Module của Role
            cursor.execute("SELECT ModuleName FROM dbo.tbl_Roles WHERE RoleCode = ?", (role_code,))
            row = cursor.fetchone()
            role_module = row[0] if row and row[0] else None

            # 2. Lấy Permission (Thêm ORDER BY PermissionCode để xếp A-Z)
            if role_module:
                sql = "SELECT PermissionCode, PermissionName, ModuleName FROM dbo.tbl_PermissionList WHERE ModuleName = ? ORDER BY PermissionCode ASC"
                cursor.execute(sql, (role_module,))
            else:
                sql = "SELECT PermissionCode, PermissionName, ModuleName FROM dbo.tbl_PermissionList ORDER BY ModuleName, PermissionCode ASC"
                cursor.execute(sql)
                
            all_perms = [dict(zip([col[0] for col in cursor.description], r)) for r in cursor.fetchall()]
            
            # 3. Lấy quyền hiện có
            cursor.execute("SELECT PermissionCode FROM dbo.tbl_RolePermissions WHERE RoleCode = ?", (role_code,))
            current_perms = [r[0] for r in cursor.fetchall()]
            
            return {"all_perms": all_perms, "current_perms": current_perms}
        finally:
            conn.close()

    @staticmethod
    def update_role_mapping_logic(role_code: str, perm_codes: list, admin: str):
        """Thực hiện Xóa sạch cũ - Ghi mới (Cơ chế Sync)"""
        conn = get_lv_docs_db()
        try:
            cursor = conn.cursor()
            # Xóa toàn bộ mapping cũ của Role này
            cursor.execute("DELETE FROM dbo.tbl_RolePermissions WHERE RoleCode = ?", (role_code,))
            # Ghi mới các quyền đã tích
            for p_code in perm_codes:
                cursor.execute(
                    "INSERT INTO dbo.tbl_RolePermissions (RoleCode, PermissionCode, CreatedBy) VALUES (?, ?, ?)",
                    (role_code, p_code, admin)
                )
            conn.commit()
            return True
        finally:
            conn.close()
            
    ## gán role cho user
    @staticmethod
    def get_users_with_roles_logic():
        conn = get_lv_docs_db()
        if not conn: 
            return []
        try:
            cursor = conn.cursor()
            # Gọi câu SQL từ Model
            cursor.execute(RBACModel.SQL_GET_USERS_WITH_ROLES)
            
            # LỖI TẠI ĐÂY: Phải lấy column[0] để lấy tên cột dạng chuỗi
            columns = [column[0] for column in cursor.description]
            
            results = []
            for row in cursor.fetchall():
                # Ép kiểu Row thành Dictionary sạch
                results.append(dict(zip(columns, row)))
                
            return results
        finally:
            conn.close()
            
    @staticmethod
    def get_user_roles_logic(username: str):
        conn = get_lv_docs_db()
        try:
            cursor = conn.cursor()
            cursor.execute(RBACModel.SQL_GET_ROLES_BY_USER, (username,))
            # Trả về mảng phẳng để JS dễ kiểm tra .includes()
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
         
    @staticmethod
    def update_user_roles_logic(username: str, role_codes: list, admin_user: str):
        conn = get_lv_docs_db()
        try:
            cursor = conn.cursor()
            # 1. Xóa sạch vai trò cũ
            cursor.execute(RBACModel.SQL_DELETE_USER_ROLES, (username,))
            # 2. Ghi mới danh sách vai trò
            for r_code in role_codes:
                cursor.execute(RBACModel.SQL_INSERT_USER_ROLE, (username, r_code, admin_user))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback() # Nếu lỗi thì trả lại trạng thái cũ
            raise e
        finally:
            conn.close()
            
    @staticmethod
    def get_roles_with_details_logic():
        conn = get_lv_docs_db()
        if not conn: return []
        try:
            cursor = conn.cursor()
            # Gọi SQL JOIN từ Model
            cursor.execute(RBACModel.SQL_GET_ROLES_WITH_PERMS)
            
            # 1. Lấy danh sách tên cột sạch sẽ (RoleCode, RoleName, ModuleName, PermList)
            columns = [column[0] for column in cursor.description]
            
            # 2. Ép dữ liệu thành List các Dictionary thuần túy
            results = []
            for row in cursor.fetchall():
                # zip kết nối tên cột với giá trị thực tế của dòng đó
                results.append(dict(zip(columns, row)))
                
            return results
        finally:
            conn.close()
            
        # gán quyền hàng loạt
    @staticmethod
    def bulk_update_user_roles_logic(usernames: list, role_codes: list, admin_user: str):
            conn = get_lv_docs_db()
            try:
                cursor = conn.cursor()
                for user in usernames:
                    # Xóa cũ gán mới cho từng người trong danh sách
                    cursor.execute("DELETE FROM dbo.tbl_UserRoles WHERE Username = ?", (user,))
                    for r_code in role_codes:
                        cursor.execute(
                            "INSERT INTO dbo.tbl_UserRoles (Username, RoleCode, CreatedBy) VALUES (?, ?, ?)",
                            (user, r_code, admin_user)
                        )
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()   
            
    

