from fastapi import HTTPException
from services.tpl_sv import TPLService
from loguru import logger

class TPLController:
    @staticmethod
    def get_list(is_custom: int):
        try:
            # Gọi Service để lấy danh sách
            return TPLService.get_list_logic(is_custom)
        except Exception as e:
            logger.error(f"Lỗi lấy danh sách Template: {str(e)}")
            raise HTTPException(status_code=500, detail="Không thể tải danh sách mẫu hồ sơ")

    @staticmethod
    def get_detail(tpl_id: int):
        try:
            data = TPLService.get_detail_logic(tpl_id)
            if not data:
                raise HTTPException(status_code=404, detail="Mẫu hồ sơ không tồn tại")
            return data
        except Exception as e:
            logger.error(f"Lỗi lấy chi tiết Template ID {tpl_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Lỗi hệ thống khi tải chi tiết mẫu")

    @staticmethod
    def save(data: dict):
        try:
            # 1. Kiểm tra các trường bắt buộc
            if not data.get('TemplateCode') or not data.get('TemplateName'):
                raise HTTPException(status_code=400, detail="Mã và Tên mẫu không được để trống")

            # 2. Lấy tên người dùng thực hiện (Giả định bạn dùng username từ session/token)
            # Ở đây tôi tạm để 'Admin' - Bạn có thể thay bằng logic lấy user thực tế
            current_user = "Admin" 

            # 3. Gọi Service để thực hiện Insert/Update
            result = TPLService.save_logic(data, current_user)
            return result
            
        except Exception as e:
            logger.error(f"Lỗi lưu Template: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Lỗi khi lưu mẫu hồ sơ: {str(e)}")
