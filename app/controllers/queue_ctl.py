from services.queue_sv import QueueService

class QueueController:
    def __init__(self):
        self.service = QueueService()

    def get_current_device_logic(self, folio: str):
        if not folio:
            return {"status": "error", "message": "Folio không hợp lệ"}
            
        result = self.service.get_current_device_by_folio(folio)
        
        return result