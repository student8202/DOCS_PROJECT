# app/controllers/fo_ct.py
from fastapi import HTTPException
from services.fo_sv import FOService
from loguru import logger

class FOController:
    @staticmethod
    def get_guest_list(mode: int):
        try:
            # Gọi logic nghiệp vụ từ Service
            data = FOService.get_guest_list_logic(mode)
            return data
        except Exception as e:
            logger.error(f"Lỗi Controller FO: {str(e)}")
            raise HTTPException(status_code=500, detail="Lỗi hệ thống khi tải dữ liệu SMILE")
        
    @staticmethod
    def get_guest_list_booking(mode: int):
        try:
            # Gọi logic nghiệp vụ từ Service
            data = FOService.get_guest_list_logic_booking(mode)
            return data
        except Exception as e:
            logger.error(f"Lỗi Controller FO: {str(e)}")
            raise HTTPException(status_code=500, detail="Lỗi hệ thống khi tải dữ liệu SMILE")
