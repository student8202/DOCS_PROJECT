import bcrypt
from datetime import datetime
from database.db_connection import (
    get_lv_docs_db,
    get_smile_fo_db,
    get_smile_bo_db,
    get_smile_hr_db,
)
from models.rbac_md import RBACModel
from core.security import verify_password, get_password_hash  # Hàm băm bạn đã có
from core.utils import tcvn3_to_unicode

DEFAULT_PASSWORD = "Lavie@123"  # Mật khẩu mặc định cho lần đầu Sync


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def sync_users_from_source(source_type: str, current_admin: str):
        """
        Đồng bộ nhân sự từ SMILE (FO/BO/HR) dựa trên bảng Clerk
        """
        # 1. Chọn kết nối nguồn
        if source_type == "FO":
            conn_source = get_smile_fo_db()
        elif source_type == "BO":
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
                fullname_raw = row.LastName.strip() if row.LastName else ""
                # CHUYỂN ĐỔI SANG UNICODE
                fullname_unicode = tcvn3_to_unicode(fullname_raw)
                # SMILE: DisabledFlag thường là 1 (Bị khóa) hoặc 0 (Hoạt động)
                is_disabled = row.DisabledFlag

                if not username:
                    continue

                # 3. Kiểm tra tồn tại trong LV_DOCS
                cursor_lv.execute(
                    "SELECT Username, Source_Map FROM dbo.tbl_Users WHERE Username = ?",
                    (username,),
                )
                exists = cursor_lv.fetchone()

                if not exists:
                    # TẠO MỚI (Snapshot dữ liệu SMILE sang LV_DOCS)
                    sql_ins = """
                        INSERT INTO dbo.tbl_Users (
                            Username, Password_Hash, FullName, IsActive, 
                            Source_Map, CreatedBy, CreatedAt
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """
                    cursor_lv.execute(
                        sql_ins,
                        (
                            username,
                            hashed_default,
                            fullname_unicode,
                            0 if is_disabled else 1,
                            source_type,
                            current_admin,
                            datetime.now(),
                        ),
                    )
                else:
                    # ĐỒNG BỘ TRẠNG THÁI (Nếu SMILE khóa thì LaVie khóa)
                    current_map = exists.Source_Map or ""
                    new_map = current_map
                    if source_type not in current_map:
                        new_map = f"{current_map},{source_type}".strip(",")

                    sql_upd = """
                        UPDATE dbo.tbl_Users 
                        SET Source_Map = ?, FullName = ?, 
                            IsActive = ?, UpdatedBy = ?, UpdatedAt = ?
                        WHERE Username = ?
                    """
                    cursor_lv.execute(
                        sql_upd,
                        (
                            new_map,
                            fullname_unicode,
                            0 if is_disabled else 1,
                            current_admin,
                            datetime.now(),
                            username,
                        ),
                    )

            conn_lv.commit()
            return {
                "status": "success",
                "message": f"Đã đồng bộ {len(src_users)} nhân sự từ {source_type}",
            }

        finally:
            conn_source.close()
            conn_lv.close()

    @staticmethod
    def get_user_by_username(username: str):
        """Lấy thông tin User từ Database"""
        conn = get_lv_docs_db()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Username, Password_Hash, IsActive, FullName FROM dbo.tbl_Users WHERE Username = ?",
                (username,),
            )
            return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_user_permissions(username: str):
        """Lấy 'Chùm chìa khóa' (Code + Action + Module)"""
        conn = get_lv_docs_db()
        try:
            cursor = conn.cursor()
            sql = """
                SELECT DISTINCT P.PermissionCode, P.Action_Type, P.ModuleName
                FROM dbo.tbl_PermissionList P
                JOIN dbo.tbl_RolePermissions RP ON P.PermissionCode = RP.PermissionCode
                JOIN dbo.tbl_UserRoles UR ON RP.RoleCode = UR.RoleCode
                WHERE UR.Username = ?
            """
            cursor.execute(sql, (username,))
            rows = cursor.fetchall()
            # Trả về mảng các Dictionary để Backend sau này lọc SQL cực nhanh
            return [
                {
                    "code": str(r[0]).strip().lower() if r[0] else "",
                    "action": str(r[1]).strip().upper() if r[1] else "VIEW",
                    "module": str(r[2]).strip().upper() if r[2] else "FO",
                }
                for r in rows
            ]
        finally:
            conn.close()

    # admin reset pass
    @staticmethod
    def admin_reset_password_logic(username: str, new_pass: str, admin_user: str):
        conn = get_lv_docs_db()
        try:
            cursor = conn.cursor()
            # 1. Băm mật khẩu mới
            hashed_password = get_password_hash(new_pass)

            # 2. Cập nhật vào DB
            cursor.execute(
                RBACModel.SQL_ADMIN_RESET_PASSWORD,
                (hashed_password, admin_user, username),
            )
            conn.commit()
            return True
        finally:
            conn.close()

    # user change password
    @staticmethod
    def change_password_logic(username: str, data: dict):
        conn = get_lv_docs_db()
        try:
            cursor = conn.cursor()
            # 1. Lấy mật khẩu cũ từ Database
            cursor.execute(RBACModel.SQL_GET_USER_PASSWORD_HASH, (username,))
            user = cursor.fetchone()

            if not user:
                raise ValueError("Người dùng không tồn tại")

            # 2. Kiểm tra mật khẩu cũ (verify_password là hàm băm của bạn)
            if not verify_password(data["old_password"], user.Password_Hash):
                raise ValueError("Mật khẩu cũ không chính xác")

            # 3. Băm mật khẩu mới và cập nhật
            new_hash = get_password_hash(data["new_password"])
            cursor.execute(RBACModel.SQL_UPDATE_USER_PASSWORD, (new_hash, username))
            conn.commit()
            return True
        finally:
            conn.close()
