# app/core/deps.py
from fastapi import Request, HTTPException, status
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

def require_permission(target_code: str, target_action: str, target_module: str):
    """
    Bắt buộc phải khớp cả 3: Code + Action + Module
    Ví dụ: require_permission("edit_fo", "EDIT", "FO")
    """
    async def permission_dependency(request: Request):
        # 1. Lấy danh sách từ Session
        permissions = request.session.get("permissions", [])
        
        # Chuẩn hóa dữ liệu đầu vào để so sánh
        t_code = target_code.strip().lower()
        t_action = target_action.strip().upper()
        t_module = target_module.strip().upper()

        # 2. Duyệt tìm xem có 'chìa khóa' nào khớp hoàn toàn không
        for p in permissions:
            p_code = str(p.get("code", "")).strip().lower()
            p_action = str(p.get("action", "")).strip().upper()
            # Tách chuỗi module "FO,POS,HR" thành list ["FO", "POS", "HR"]
            p_modules = [m.strip().upper() for m in str(p.get("module", "")).split(",")]

            # KIỂM TRA ĐIỀU KIỆN: Khớp Code + Khớp Action + Module nằm trong danh sách cho phép
            if p_code == t_code and p_action == t_action and t_module in p_modules:
                return True # Tìm thấy quyền khớp, cho phép đi tiếp
        
        # 3. Nếu không tìm thấy quyền nào thỏa mãn
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Từ chối: Bạn không có quyền {t_action} trên {t_module} với mã {t_code}"
        )
            
    return permission_dependency