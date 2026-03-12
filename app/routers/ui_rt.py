import os
from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, Response
from fastapi.templating import Jinja2Templates
from core.security import get_password_hash
from passlib.hash import bcrypt

# Khai báo Router cho giao diện
router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")

# --- ROUTES GIAO DIỆN (UI) ---
def login_required(request: Request):
    # Kiểm tra xem trong kho Session có tên người dùng không
    if "username" not in request.session:
        # Nếu không có, bắt quay lại trang chủ (Login) ngay lập tức
        return False
    return True

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Trang đăng nhập hệ thống"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    if not login_required(request):
        return RedirectResponse(url="/?error=timeout", status_code=303)
        
    # Lấy danh sách quyền đã lưu lúc Login
    user_permissions = request.session.get("permissions", [])
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "full_name": request.session.get("full_name"),
        "user_permissions": user_permissions # Gửi quyền sang HTML
    })

@router.get("/fo", response_class=HTMLResponse)
async def fo_page(request: Request):
    """Trang Tiền sảnh (Search Booking)"""
    return templates.TemplateResponse("fo_search.html", {"request": request})

@router.get('/favicon.ico', include_in_schema=False)
async def favicon():
    file_path = os.path.join("static", "favicon.ico")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    # Trả về phản hồi trống thay vì báo lỗi 500 nếu thiếu file
    return Response(status_code=204) 

# test password
@router.get("/gen_pass/{password}", tags=["Tools"],include_in_schema=False)
async def generate_hash(password: str):
    # Ép kiểu về string và giới hạn độ dài để bảo vệ Bcrypt
    safe_pass = str(password)[:50] 
    
    # Gọi hàm băm từ security.py
    hashed = get_password_hash(safe_pass)
    
    return {
        "project": "LaVie Project",
        "status": "Success",
        "password_plain": safe_pass,
        "password_hash": hashed,
        "sql_command": f"UPDATE dbo.tbl_Users SET Password_Hash = '{hashed}' WHERE Username = 'admin';"
    }