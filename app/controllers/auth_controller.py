from fastapi import HTTPException, Request
from services.auth_service import AuthService
from services.fo_sv import FOService
from core.security import verify_password, create_access_token
from schemas.auth import ChangePasswordRequest
# from database.db_connection import get_lv_docs_db
from loguru import logger
from core.deps import templates 

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
        
        hotel_date = FOService.get_hotel_date() # Hàm "SELECT TOP 1 HotelDate..." bạn đã viết
        request.session["hotel_date"] = hotel_date # Lưu vào Session
        hotel_name = FOService.get_hotel_name() 
        request.session["hotel_name"] = hotel_name
        
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
            "permissions": permissions,
            "hotel_date":hotel_date,
            "hotel_name":hotel_name
        }

    @staticmethod
    def logout(request: Request):
        request.session.clear() # Xóa sạch Username và Quyền trong Session
        return {"status": "success", "message": "Đã đăng xuất"}
    
    #admin reset password
    @staticmethod
    def admin_reset_pass(data, admin_user: str):
        """Controller xử lý việc Admin cưỡng bức đổi mật khẩu cho User"""
        try:
            # data là Schema AdminResetPassRequest (username, new_password)
            AuthService.admin_reset_password_logic(
                data.username, 
                data.new_password, 
                admin_user
            )
            return {
                "status": "success", 
                "message": f"Đã đặt lại mật khẩu cho tài khoản {data.username} thành công."
            }
        except Exception as e:
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail="Lỗi hệ thống khi reset mật khẩu")
        
    # user change password
    @staticmethod
    def user_change_password(username: str, data: ChangePasswordRequest):
        # 1. Kiểm tra khớp mật khẩu mới
        if data.new_password != data.confirm_password:
            raise HTTPException(status_code=400, detail="Mật khẩu xác nhận không khớp")
        
        try:
            # 2. Gọi Service xử lý
            AuthService.change_password_logic(username, data.model_dump())
            return {"status": "success", "message": "Đổi mật khẩu thành công!"}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception:
            raise HTTPException(status_code=500, detail="Lỗi hệ thống")
        
    # dynamic dashboard
    @staticmethod
    def render_dashboard(request: Request):
        user_perms = [p.lower() for p in request.session.get("permissions", []) if p]
        
        # Kiểm tra xem User có quyền ở những phân hệ nào
        dash_modules = {
            "show_fo": "view_fo" in user_perms or "admin" in user_perms,
            "show_bo": "view_bo" in user_perms or "admin" in user_perms,
            "show_hr": "view_hr" in user_perms or "admin" in user_perms
        }
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "full_name": request.session.get("full_name"),
            "dash_modules": dash_modules # Gửi dict chứa các cờ True/False
        })