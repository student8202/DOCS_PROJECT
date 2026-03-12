from fastapi import HTTPException, Request
from services.auth_service import AuthService
from core.security import verify_password, create_access_token
# from database.db_connection import get_lv_docs_db
from loguru import logger

class AuthController:
    @staticmethod
    def login(request: Request, username, password):
        # 1. Gọi Service lấy dữ liệu
        user = AuthService.get_user_by_username(username)
        
        if not user:
            raise HTTPException(status_code=401, detail="Tài khoản không tồn tại")
        
        # user[1] là Password_Hash, user[2] là IsActive
        if not user[2]:
            raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")

        if not verify_password(password, user[1]):
            raise HTTPException(status_code=401, detail="Sai mật khẩu")

        # 2. Lấy quyền và ghi vào Session để lưu Log/Audit sau này
        permissions = AuthService.get_user_permissions(username)
        
        request.session["username"] = user[0]
        request.session["full_name"] = user[3]
        request.session["permissions"] = permissions

        # 3. Trả về Token (nếu cần dùng cho API/Mobile)
        token = create_access_token(data={"sub": user[0], "name": user[3]})
        
        logger.info(f"User {username} logged in successfully with {len(permissions)} perms")
        
        return {
            "access_token": token,
            "username": user[0],
            "full_name": user[3],
            "permissions": permissions
        }

    @staticmethod
    def logout(request: Request):
        request.session.clear() # Xóa sạch Username và Quyền trong Session
        return {"status": "success", "message": "Đã đăng xuất"}