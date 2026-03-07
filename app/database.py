import pyodbc
from core.config import settings
from fastapi import Request

# 1. Hàm cung cấp connection cho FastAPI (Dependency)
def get_db():
    conn = pyodbc.connect(settings.connection_string)
    try:
        yield conn
    finally:
        conn.close()

def write_system_log(user_name: str, method: str, path: str, status_code: int, ip: str):
    """Ghi log tự động cho mọi request"""
    try:
        # Chỉ ghi log cho các thao tác thay đổi dữ liệu (POST, PUT, DELETE)
        # Hoặc ghi tất cả tùy bạn, ở đây tôi lọc để tránh rác DB
        if method in ["POST", "PUT", "DELETE"] or "api" in path:
            with pyodbc.connect(settings.connection_string) as conn:
                cursor = conn.cursor()
                sql = """
                    INSERT INTO UserLogs (UserID, Action, IPAddress, CreatedAt) 
                    VALUES (?, ?, ?, GETDATE())
                """
                action = f"{method} {path} - Status: {status_code}"
                cursor.execute(sql, (user_name, action, ip))
                conn.commit()
    except Exception as e:
        print(f"❌ Lỗi Middleware Log: {e}")

# 3. Hàm kiểm tra kết nối
def check_db_connection():
    try:
        conn = pyodbc.connect(settings.connection_string, timeout=5)
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Lỗi kết nối Database: {e}")
        return False
