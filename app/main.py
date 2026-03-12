import os
import uvicorn
import sys
import io
import secrets
import time
from loguru import logger
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# from starlette.middleware.sessions import SessionMiddleware
# from database import write_system_log

from core.config import settings
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from routers import auth_rt, ui_rt  # Import các router đã bàn
from core.security import get_password_hash
#swagger
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from fastapi.responses import FileResponse,Response
from starlette.middleware.sessions import SessionMiddleware
from core.config import settings

# Gộp tất cả cấu hình vào một nơi
app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=None,   # Tắt Swagger mặc định để tự tạo route bảo vệ
    redoc_url=None   # Tắt ReDoc mặc định
)

# Thêm Middleware này ngay sau khi khởi tạo app = FastAPI(...)
app.add_middleware(
    SessionMiddleware, 
    secret_key=settings.SECRET_KEY, # Dùng key trong .env để mã hóa cookie session
    session_cookie="lavie_session",
    max_age=28800 # 8 tiếng làm việc (giây)
)

# Swagger
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

# 2. Tạo Route riêng có yêu cầu đăng nhập Basic Auth
@app.get("/admin/api-docs", include_in_schema=False)
async def get_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(
        openapi_url="/admin/openapi.json",
        title="LaVie Project - API Schema"
    )

@app.get("/admin/openapi.json", include_in_schema=False)
async def openapi_endpoint(username: str = Depends(get_current_username)):
    return get_openapi(
        title="LaVie Project",
        version="1.0.0",
        routes=app.routes,
    )
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
####
# --- LOGGING MIDDLEWARE ---
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    # 1. Bắt đầu đo thời gian và xác định vị trí truy cập
    start_time = time.time()
    path = request.url.path
    method = request.method
    client_ip = request.client.host

    logger.info(f"START | {method} {path} | IP: {client_ip}")

    try:
        # 2. Cho phép request đi tiếp vào Controller/Router
        response = await call_next(request)
        
        # 3. Tính toán thời gian xử lý xong
        process_time = (time.time() - start_time) * 1000
        formatted_process_time = "{0:.2f}".format(process_time)
        
        logger.info(f"END   | {method} {path} | Status: {response.status_code} | Time: {formatted_process_time}ms")
        
        return response

    except Exception as e:
        # 4. Nếu có lỗi sập nguồn ở bất kỳ đâu, Middleware sẽ bắt được và ghi log
        process_time = (time.time() - start_time) * 1000
        logger.error(f"FAIL  | {method} {path} | Error: {str(e)} | Time: {process_time:.2f}ms")
        raise e

# 1. Cấu hình thư mục chứa file vật lý (JS, CSS, PDF)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Cấu hình Jinja2 để render HTML
templates = Jinja2Templates(directory="templates")

# 3. Đăng ký các API Routers
app.include_router(auth_rt.router,include_in_schema=False)
# 3. Kết nối các "Mảnh ghép" Router
app.include_router(ui_rt.router)   # Router Giao diện (HTML)
# app.include_router(fo.router) # Mở ra khi làm module FO

# Middleware xử lý lỗi 404 (Nếu gõ sai link)
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6066))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
