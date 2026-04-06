from services.docs_sv import DocsService
from loguru import logger
import traceback

class DocsController:
    def __init__(self):
        self.service = DocsService()

    def get_categories_logic(self, module: str):
        """Logic kiểm tra trước khi lấy danh sách Category"""
        if not module:
            return []
        
        # Gọi xuống Service để lấy dữ liệu từ Database
        categories = self.service.get_all_categories(module)
        
        # Trả về danh sách (Ví dụ: ["REG_CARD", "CONFIRM"])
        return categories
    
    def upload_manual_controller(self, file, folio, booking_id, guest_name, doc_type, username):
        try:
            # Gọi Service thực hiện logic "đè" phiên bản
            self.service.save_manual_upload(file, folio, booking_id, guest_name, doc_type, username)
            return {"status": 200, "message": "Cập nhật hồ sơ thành công"}
        except Exception as e:
            logger.error(f"Lỗi Upload: {str(e)}")
            return {"status": 500, "detail": "Lỗi hệ thống khi xử lý phiên bản"}
    
    def approve_signature_controller(self, queue_id: int, username: str):
        try:
            # Gọi Service xử lý nghiệp vụ
            self.service.approve_signature_service(queue_id, username)
            return {"status": 200, "message": "Duyệt thành công"}
            
        except ValueError as ve:
            # Lỗi nghiệp vụ (Sai ID, thiếu dữ liệu) -> Trả về 400
            return {"status": 400, "detail": str(ve)}
            
        except Exception as e:
            # Lỗi hệ thống (Sập DB, lỗi code) -> Trả về 500
            # Ở đây ta có thể dùng traceback để biết chính xác dòng bị lỗi
            logger.error(traceback.format_exc()) 
            return {"status": 500, "detail": "Lỗi hệ thống server"}