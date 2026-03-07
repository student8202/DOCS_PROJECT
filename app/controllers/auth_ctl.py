from services.auth_service import AuthService

class AuthController:
    @staticmethod
    def login(db, username, password):
        user_data = AuthService.authenticate_user(db, username, password)
        
        if user_data:
            return {
                "status": "success",
                "user": user_data
            }
            
        return {
            "status": "error", 
            "message": "Tài khoản hoặc mật khẩu không đúng!"
        }
