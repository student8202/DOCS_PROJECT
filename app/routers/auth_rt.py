from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pyodbc import Connection

from database import get_db
from controllers.auth_ctl import AuthController
from schemas.auth import LoginRequest

router = APIRouter(prefix="/auth", tags=["Xác thực"])
templates = Jinja2Templates(directory="templates")

# 1. Trang hiển thị Login
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})

# 2. API Login - Router chỉ điều hướng và quản lý Session
@router.post("/api/login")
async def api_login(
    request: Request, 
    data: LoginRequest, 
    db: Connection = Depends(get_db)
):
    # Router gọi Controller để lấy kết quả xử lý
    result = AuthController.login(db, data.username, data.password)
    
    # Nếu thành công, Router thực hiện hành động liên quan đến HTTP (ghi Session)
    if result["status"] == "success":
        user_data = result["user"]
        request.session.update({
            "user_id": user_data["id"],
            "user_name": user_data["name"],
            "permissions": user_data["perms"]
        })
        
    return result

# 3. API Đăng xuất
@router.get("/api/logout")
async def api_logout(request: Request):
    request.session.clear()
    return {"status": "success"}