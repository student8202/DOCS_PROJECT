from services.queue_sv import QueueService, QueueCompleteSchema
import traceback
from loguru import logger

class QueueController:
    def __init__(self):
        self.service = QueueService()

    def get_current_device_logic(self, folio: str):
        if not folio:
            return {"status": "error", "message": "Folio không hợp lệ"}
            
        result = self.service.get_current_device_by_folio(folio)
        
        return result
    
    def change_device_logic(self, folio: str, new_device_id: str):
        success = self.service.update_queue_device(folio, new_device_id)
        if success:
            return {"status": "success", "message": "Đã chuyển thiết bị"}
        return {"status": "error", "message": "Không tìm thấy hồ sơ đang treo để chuyển"}

    def force_cancel_logic(self, folio: str, id_add: int):
        if not folio:
            return {"status": "error", "message": "Dữ liệu không hợp lệ"}
            
        success = self.service.cancel_queue_by_folio(folio, id_add)
        if success:
            return {"status": "success", "message": "Đã hủy yêu cầu"}
        return {"status": "error", "message": "Không tìm thấy hồ sơ đang treo để hủy"}
    
        
    def complete_and_archive_controller(self, data, username):
        try:
            # Gọi Service xử lý toàn bộ quy trình
            self.service.complete_and_archive_service(data, username)
            return {"status": 200, "message": "Hồ sơ đã được ký và tạo file PDF thành công"}
        except ValueError as ve:
            return {"status": 400, "detail": str(ve)}
        except Exception as e:
            logger.error(traceback.format_exc())
            return {"status": 500, "detail": "Lỗi hệ thống khi tạo file PDF"}