from crud.auth_crud import AuthCRUD
from core.security import Security

class AuthService:
    @staticmethod
    def authenticate_user(db, username, password):
        # 1. Tìm user từ CRUD
        user = AuthCRUD.get_employee_by_name(db, username)
        
        # 2. Logic kiểm tra mật khẩu
        if not user or not Security.verify_password(password, user.Password):
            return None
            
        # 3. Lấy và format quyền
        perms_list = AuthCRUD.get_permissions_by_employee_id(db, user.ID)
        
        return {
            "id": user.ID,
            "name": user.FullName,
            "perms": ",".join(perms_list)
        }
