import os
import uvicorn
import sys
import io
import secrets
from loguru import logger
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# from starlette.middleware.sessions import SessionMiddleware
# from database import write_system_log

from core.config import settings
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from routers import auth  # Import các router đã bàn

# Gộp tất cả cấu hình vào một nơi
app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=None,   # Tắt Swagger mặc định để tự tạo route bảo vệ
    redoc_url=None   # Tắt ReDoc mặc định
)

security = HTTPBasic()
def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    # Thay 'admin' và 'secret_key' bằng thông tin bạn muốn
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "project")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không có quyền truy cập tài liệu",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Ép terminal dùng UTF-8 để hiện tiếng Việt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# Xóa cấu hình mặc định và thêm cấu hình hỗ trợ UTF-8 cho Terminal
# Xóa cấu hình mặc định
logger.remove()

# Thêm lại cấu hình với dấu ngoặc nhọn chuẩn {}
logger.add(
    sys.stderr, 
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>", 
    colorize=True, 
    backtrace=True, 
    diagnose=True
)

# Ghi ra file (đảm bảo encoding utf-8 để không lỗi font tiếng Việt)
logger.add(
    "logs/app.log", 
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    encoding="utf-8", 
    rotation="10 MB",
    retention="10 days"
)

# 1. Cấu hình thư mục chứa file vật lý (JS, CSS, PDF)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Cấu hình Jinja2 để render HTML
templates = Jinja2Templates(directory="templates")

# 3. Đăng ký các API Routers
app.include_router(auth.router)
# app.include_router(fo.router) # Mở ra khi làm module FO

# --- ROUTES GIAO DIỆN (UI) ---

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Trang đăng nhập hệ thống"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Trang chủ Dashboard với 3 nút Sync"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/fo", response_class=HTMLResponse)
async def fo_page(request: Request):
    """Trang Tiền sảnh (Search Booking)"""
    return templates.TemplateResponse("fo_search.html", {"request": request})

# Middleware xử lý lỗi 404 (Nếu gõ sai link)
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6066))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
