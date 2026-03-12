import bcrypt
from datetime import datetime
from database.db_connection import (
    get_lv_docs_db, get_smile_fo_db, get_smile_bo_db, get_smile_hr_db
)

DEFAULT_PASSWORD = "Lavie@123" # Mật khẩu mặc định cho lần đầu Sync

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def sync_users_from_source(source_type: str, current_admin: str):
        """
        Đồng bộ nhân sự từ SMILE (FO/BO/HR) dựa trên bảng Clerk
        """
        # 1. Chọn kết nối nguồn
        if source_type == 'FO':
            conn_source = get_smile_fo_db()
        elif source_type == 'BO':
            conn_source = get_smile_bo_db()
        else:
            conn_source = get_smile_hr_db()
            
        conn_lv = get_lv_docs_db()
        
        try:
            cursor_src = conn_source.cursor()
            cursor_lv = conn_lv.cursor()

            # 2. Truy vấn đúng tên cột bạn vừa cung cấp
            # ClerkID -> Username, LastName -> FullName, DisabledFlag -> IsActive
            cursor_src.execute("SELECT ClerkID, LastName, DisabledFlag FROM dbo.Clerk")
            src_users = cursor_src.fetchall()

            hashed_default = AuthService.hash_password(DEFAULT_PASSWORD)

            for row in src_users:
                username = row.ClerkID.strip() if row.ClerkID else None
                fullname = row.LastName.strip() if row.LastName else ""
                # SMILE: DisabledFlag thường là 1 (Bị khóa) hoặc 0 (Hoạt động)
                is_disabled = row.DisabledFlag 

                if not username: continue

                # 3. Kiểm tra tồn tại trong LV_DOCS
                cursor_lv.execute("SELECT Username, Source_Map FROM dbo.tbl_Users WHERE Username = ?", (username,))
                exists = cursor_lv.fetchone()

                if not exists:
                    # TẠO MỚI (Snapshot dữ liệu SMILE sang LV_DOCS)
                    sql_ins = """
                        INSERT INTO dbo.tbl_Users (
                            Username, Password_Hash, FullName, IsActive, 
                            Source_Map, CreatedBy, CreatedAt
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """
                    cursor_lv.execute(sql_ins, (
                        username, hashed_default, fullname, 
                        0 if is_disabled else 1, 
                        source_type, current_admin, datetime.now()
                    ))
                else:
                    # ĐỒNG BỘ TRẠNG THÁI (Nếu SMILE khóa thì LaVie khóa)
                    current_map = exists.Source_Map or ""
                    new_map = current_map
                    if source_type not in current_map:
                        new_map = f"{current_map},{source_type}".strip(',')

                    sql_upd = """
                        UPDATE dbo.tbl_Users 
                        SET Source_Map = ?, FullName = ?, 
                            IsActive = ?, UpdatedBy = ?, UpdatedAt = ?
                        WHERE Username = ?
                    """
                    cursor_lv.execute(sql_upd, (
                        new_map, fullname, 
                        0 if is_disabled else 1, 
                        current_admin, datetime.now(), username
                    ))

            conn_lv.commit()
            return {"status": "success", "message": f"Đã đồng bộ {len(src_users)} nhân sự từ {source_type}"}
        
        finally:
            conn_source.close()
            conn_lv.close()

    @staticmethod
    def get_user_by_username(username: str):
        """Lấy thông tin User từ Database"""
        conn = get_lv_docs_db()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Username, Password_Hash, IsActive, FullName FROM dbo.tbl_Users WHERE Username = ?", (username,))
            return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_user_permissions(username: str):
        """Lấy danh sách quyền (RBAC) của User"""
        conn = get_lv_docs_db()
        if not conn: return []
        try:
            cursor = conn.cursor()
            sql = """
                SELECT DISTINCT PermissionCode 
                FROM dbo.tbl_RolePermissions 
                WHERE RoleCode IN (SELECT RoleCode FROM dbo.tbl_UserRoles WHERE Username = ?)
            """
            cursor.execute(sql, (username,))
            # .lower() để biến tất cả 'ADMIN', 'Admin' thành 'admin'
            return [str(row[0]).strip().lower() for row in cursor.fetchall()]
        finally:
            conn.close()
