@echo off
setlocal
cd /d "C:\SMILE PMS\DOCS_PROJECT\app"

:: Kiểm tra và cài đặt thư viện thiếu (chỉ chạy khi cần)
echo [%date% %time%] Dang kiem tra thu vien FastAPI...
"C:\Program Files\Python312\python.exe" -m pip install fastapi uvicorn jinja2 python-multipart pyodbc pandas openpyxl --user
"C:\Program Files\Python312\python.exe" -m pip install loguru --user
"C:\Program Files\Python312\python.exe" -m pip install "python-jose[cryptography]" --user
:: Khởi động FastAPI với Uvicorn
:: --port 6066: Giữ nguyên cổng cũ để không phải sửa Nginx
:: --workers 4: Chạy đa luồng để xử lý nhanh hơn (tùy số nhân CPU)
echo [%date% %time%] Dang khoi dong FastAPI Server...
"C:\Program Files\Python312\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 6066 --reload --workers 4

pause
