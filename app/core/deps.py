# app/core/deps.py
from fastapi.templating import Jinja2Templates

# Khai báo templates duy nhất tại đây
templates = Jinja2Templates(directory="templates")

# # Đăng ký các hàm/biến toàn cục
templates.env.globals.update(
    # hàm lấy quyền
    get_perms=lambda request: request.session.get("permissions", []),
    # THÊM DÒNG NÀY: Hàm lấy ngày khách sạn từ Session
    get_hotel_date=lambda request: request.session.get("hotel_date", ""),
    
    get_hotel_name=lambda request: request.session.get("hotel_name", "")
)