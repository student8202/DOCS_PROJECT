import os
import uvicorn
import sys
import io
from loguru import logger
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from database import write_system_log

from core.config import settings
from routers.auth_rt import router as auth_router
from routers.employee_rt import router as employee_router
from routers.department_rt import router as department_router
from routers.permission_rt import router as perm_router

from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

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

# Tạo lại route docs nhưng có bảo vệ
@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(get_current_username)):
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")

@app.get("/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(get_current_username)):
    from fastapi.openapi.utils import get_openapi
    return get_openapi(title="HR Project API", version="1.0.0", routes=app.routes)

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
# --- QUAN TRỌNG: THỨ TỰ MIDDLEWARE ---
# --- CẤU HÌNH MIDDLEWARE ---
# 2. Khai báo SessionMiddleware SAU (Nó nằm gần Router hơn)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# 1. Khai báo Log Middleware TRƯỚC (Nó sẽ bọc ngoài cùng)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Cho request đi qua
    response = await call_next(request)
    
    try:
        # Kiểm tra xem 'session' có trong scope không trước khi truy cập
        if "session" in request.scope:
            user_name = request.session.get("user_name", "Anonymous")
            path = request.url.path
            method = request.method
            ip = request.client.host
            write_system_log(user_name, method, path, response.status_code, ip)
    except Exception as e:
        # Ghi log lỗi ra console để debug nếu cần, nhưng không làm sập app
        print(f"Log Middleware Error: {e}")
        # Tuyệt đối không để lỗi log làm sập ứng dụng
        pass
    return response

# --- CẤU HÌNH STATIC & TEMPLATES ---
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 3. Route Gốc
@app.get("/")
async def index(request: Request):
    if 'user_id' not in request.session:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request})

# 4. Đăng ký Routers
app.include_router(auth_router, include_in_schema=False)
app.include_router(employee_router, prefix="/employees", tags=["Nhân viên"])
app.include_router(department_router, prefix="/departments", tags=["Phòng ban"])
app.include_router(perm_router, prefix="/permissions", tags=["Phân quyền"])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6066))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
