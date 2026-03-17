# app/controllers/fo_ct.py
from fastapi import HTTPException
from services.fo_sv import FOService
from loguru import logger

class FOController:
    @staticmethod
    def get_inhouse_list():
        try:
            # Gọi logic nghiệp vụ từ Service
            data = FOService.get_inhouse_list_logic()
            return data
        except Exception as e:
            logger.error(f"Lỗi Controller FO: {str(e)}")
            raise HTTPException(status_code=500, detail="Lỗi hệ thống khi tải dữ liệu SMILE")
        
    @staticmethod
    def get_inhouse_list_booking():
        try:
            # Gọi logic nghiệp vụ từ Service
            data = FOService.get_inhouse_list_logic_booking()
            return data
        except Exception as e:
            logger.error(f"Lỗi Controller FO: {str(e)}")
            raise HTTPException(status_code=500, detail="Lỗi hệ thống khi tải dữ liệu SMILE")
