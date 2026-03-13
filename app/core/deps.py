# app/core/deps.py
from fastapi.templating import Jinja2Templates

# Khai báo templates duy nhất tại đây
templates = Jinja2Templates(directory="templates")

# Đăng ký hàm get_perms toàn cục ngay tại đây
templates.env.globals.update(
    get_perms=lambda request: request.session.get("permissions", [])
)