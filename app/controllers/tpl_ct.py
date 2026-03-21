from fastapi import HTTPException, status
from services.tpl_sv import TPLService
from schemas.tpl_sh import TemplateCreateSchema
from loguru import logger

class TPLController:
    def __init__(self):
        # Khởi tạo Service để sử dụng trong các hàm bên dưới
        self.service = TPLService()

    def get_list(self, is_custom: int):
        try:
            # Controller chỉ gọi Service, không xử lý logic dữ liệu
            return self.service.get_list_logic(is_custom)
        except Exception as e:
            logger.error(f"Lỗi Controller get_list: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Không thể tải danh sách mẫu hồ sơ"
            )

    def get_detail(self, tpl_id: int):
        try:
            data = self.service.get_detail_logic(tpl_id)
            if not data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Mẫu hồ sơ không tồn tại"
                )
            return data
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.error(f"Lỗi Controller get_detail ID {tpl_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Lỗi hệ thống khi tải chi tiết mẫu"
            )

    def save(self, data: TemplateCreateSchema, username: str): # Nhận thêm username
        try:
            # Chuyển username xuống Service để ghi vào CreatedBy/UpdatedBy
            result = self.service.save_logic(data, username)
            return result
        except Exception as e:
            logger.error(f"Lỗi Controller save: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        
    def get_tags(self):
        try:
            # Gọi service lấy danh sách tags
            return self.service.get_tags_logic()
        except Exception as e:
            logger.error(f"Lỗi lấy Tags: {str(e)}")
            raise HTTPException(status_code=500, detail="Không thể tải danh sách thẻ động")
