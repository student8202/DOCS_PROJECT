from services.queue_sv import QueueService

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