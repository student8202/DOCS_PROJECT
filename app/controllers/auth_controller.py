from fastapi import HTTPException, status
from services.auth_service import AuthService
from core.security import verify_password, create_access_token
from database.db_connection import get_lv_docs_db

class AuthController:
    @staticmethod
    def login(username, password):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        
        # 1. Tìm User trong LaVie Docs (Độc lập hoàn toàn)
        cursor.execute("SELECT Username, Password_Hash, IsActive, FullName FROM dbo.tbl_Users WHERE Username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            raise HTTPException(status_code=401, detail="Tài khoản không tồn tại trong LaVie")
        
        if not user.IsActive:
            raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")

        # 2. Kiểm tra mật khẩu băm
        if not verify_password(password, user.Password_Hash):
            raise HTTPException(status_code=401, detail="Mật khẩu không chính xác")

        # 3. Tạo Token kèm thông tin Username để lưu vết CreatedBy/UpdatedBy sau này
        access_token = create_access_token(data={"sub": user.Username, "name": user.FullName})
        
        return {
            "access_token": access_token, 
            "token_type": "bearer", 
            "username": user.Username,
            "full_name": user.FullName
        }
