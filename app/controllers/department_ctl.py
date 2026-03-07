from fastapi import HTTPException, status
from pyodbc import Connection
from services.department_service import DepartmentService
from crud.department_crud import DepartmentCRUD
from schemas.department import DepartmentSaveRequest
from loguru import logger
import os

class DepartmentController:
    @staticmethod
    def get_all(db: Connection):
        # Lấy dữ liệu thô từ CRUD và trả về
        return DepartmentCRUD.get_all(db)

    @staticmethod
    def save(db: Connection, data: DepartmentSaveRequest):
        # Dòng này sẽ in ra đường dẫn file mà Python đang thực sự đọc
        logger.info(f"DEBUG: File đang chạy nằm tại: {os.path.abspath(__file__)}")
        # Gọi Service và nhận về bộ (tuple): success, message_text
        success, message_text = DepartmentService.save(db, data)
        logger.info(f"DEBUG: Service trả về -> success={success}, msg={message_text}")
        if not success:
            # Trả về lỗi 400 để AJAX nhảy vào hàm error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail={"message": message_text}
            )
        logger.info(f"messane_text save dept controller: {message_text}")
        # PHẢI dùng biến message_text thay vì ghi chữ "message" trong nháy kép
        return {
            "status": "success" if success else "error", 
            "message": message_text
        }

    @staticmethod
    def delete(db: Connection, dept_id: int):
        success, message_text  = DepartmentService.delete(db, dept_id)
        logger.info(f"messane_text controller: {message_text}")
        if not success:
            # Trả về lỗi 400 để AJAX nhảy vào hàm error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail={"message": message_text}
            )
            
        return {"status": "success" if success else "error", "message": message_text} # Mặc định là 200 OK
