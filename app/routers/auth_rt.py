from fastapi import APIRouter, Depends, Form, HTTPException, Request, status # Thêm Request, status
from controllers.auth_controller import AuthController
from services.auth_service import AuthService
from core.deps import templates # Import từ deps

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    return AuthController.login(request, username, password)

@router.post("/sync/{source_type}")
async def sync_users(source_type: str, request: Request): # Thêm request vào đây
    # 1. Lấy danh sách quyền từ Session
    user_perms = request.session.get("permissions", [])
    
    # 2. Kiểm tra quyền ADMIN
    if "admin" not in user_perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Bạn không có quyền thực hiện lệnh này"
        )
    
    # 3. Lấy username của người đang thực hiện để lưu log CreatedBy
    admin_user = request.session.get("username", "admin")
    
    # Gọi sang Service xử lý
    return AuthService.sync_users_from_source(source_type, admin_user)

@router.post("/logout")
async def logout(request: Request):
    """API xóa Session từ Backend"""
    return AuthController.logout(request)