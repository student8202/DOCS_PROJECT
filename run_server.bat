@echo off
set NGINX_PATH=C:\nginx_fastapi
cd /d "%NGINX_PATH%"

:: Lấy thời gian
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /format:list') do set datetime=%%I
set ts=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%-%datetime:~12,2%

echo [%ts%] Dang kiem tra va khoi dong lai Nginx...

:: 1. Kiểm tra lỗi cú pháp file config trước khi thực hiện
nginx -t
if %errorlevel% neq 0 (
    echo [ERROR] File cấu hình co loi. Vui long kiem tra lai!
    pause
    exit /b
)

:: 2. Tắt triệt để các process cũ (nếu có)
taskkill /f /im nginx.exe 2>nul

:: 3. Khởi động mới Nginx
start nginx
echo [SUCCESS] Nginx da duoc khoi dong lai thanh cong.
pause