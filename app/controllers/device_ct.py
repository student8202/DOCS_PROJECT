from fastapi import HTTPException, status
from services.device_sv import DeviceService
from loguru import logger

class DeviceController:
    def __init__(self):
        # Khởi tạo Service để sử dụng trong các hàm bên dưới
        self.service = DeviceService()
    # ... các hàm cũ giữ nguyên ...

    def get_online_list(self, module: str):
        try:
            return self.service.get_online_devices_logic(module)
        except Exception as e:
            logger.error(f"Lỗi lấy danh sách thiết bị Online: {str(e)}")
            return []
