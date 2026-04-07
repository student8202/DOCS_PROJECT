import pyodbc
from loguru import logger
from core.config import settings # Sửa import từ 'app.core' thành 'core'

def create_conn(server, db, uid, pwd, name="Database"):
    # Kiểm tra nếu cấu hình trống (phòng lỗi .env chưa nạp)
    if not server or not db:
        logger.error(f"Thanh phan cau hinh {name} bi trong!")
        return None

    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={db};"
        f"UID={uid};"
        f"PWD={pwd};"
        "MARS_Connection=Yes;"
        "Connection Timeout=5;" # Ràng buộc timeout ở mức Driver
    )
    
    try:
        # timeout=5 ở đây là timeout của pyodbc
        return pyodbc.connect(conn_str, timeout=5)
    except pyodbc.Error as e:
        # Ghi log lỗi để Admin biết DB nào đang rớt mạng
        logger.error(f"Loi ket noi den {name} ({server}): {e}")
        return None

# --- CÁC HÀM KẾT NỐI ĐỘC LẬP ---

def get_lv_docs_db():
    """Hệ thống chính - Bắt buộc phải có"""
    return create_conn(settings.LV_DOCS_SERVER, settings.LV_DOCS_DB, 
                       settings.LV_DOCS_UID, settings.LV_DOCS_PWD, "LV_DOCS")

def get_smile_fo_db():
    """Nguồn Tiền sảnh - Có thể rớt mạng"""
    return create_conn(settings.SMILE_FO_SERVER, settings.SMILE_FO_DB, 
                       settings.SMILE_FO_UID, settings.SMILE_FO_PWD, "SMILE_FO")

def get_smile_bo_db():
    """Nguồn Kế toán - Có thể rớt mạng"""
    return create_conn(settings.SMILE_BO_SERVER, settings.SMILE_BO_DB, 
                       settings.SMILE_BO_UID, settings.SMILE_BO_PWD, "SMILE_BO")

def get_smile_hr_db():
    """Nguồn Nhân sự - Có thể rớt mạng"""
    return create_conn(settings.SMILE_HR_SERVER, settings.SMILE_HR_DB, 
                       settings.SMILE_HR_UID, settings.SMILE_HR_PWD, "SMILE_HR")
    
def get_lv_docs_ar_db():
    """Lưu trữ hồ sơ"""
    return create_conn(settings.LV_DOCS_AR_SERVER, settings.LV_DOCS_AR_DB, 
                       settings.LV_DOCS_AR_UID, settings.LV_DOCS_AR_PWD, "LV_DOCS_ARCHIVE")
