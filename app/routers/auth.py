from fastapi import APIRouter, Depends, Form
from controllers.auth_controller import AuthController
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    return AuthController.login(username, password)

@router.post("/sync/{source_type}")
def sync_users(source_type: str, admin_user: str = "admin"): # admin_user sẽ lấy từ Token sau này
    # source_type sẽ nhận: 'FO', 'BO', hoặc 'HR'
    return AuthService.sync_users_from_source(source_type, admin_user)
