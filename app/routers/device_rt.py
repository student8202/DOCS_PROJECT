from fastapi import APIRouter, Depends
from schemas.device_sh import DeviceRegisterSchema, DevicePingSchema
from services.device_sv import DeviceService

router = APIRouter(prefix="/api/v1/devices", tags=["Devices Management"])
service = DeviceService()

@router.post("/register")
async def register_device(data: DeviceRegisterSchema):
    # Tablet gọi cái này khi nhấn nút "Xác nhận chiếm quyền"
    return service.register_device_logic(data)

@router.post("/ping")
async def ping_device(data: DevicePingSchema):
    # Tablet gọi cái này định kỳ mỗi 10 giây (Heartbeat)
    return service.ping_logic(data)

@router.get("/online-list")
async def get_online_list(
    module: str = "FO", 
    svc: DeviceService = Depends()
):
    """API trả về danh sách iPad đang sẵn sàng nhận hồ sơ"""
    return svc.get_online_devices_logic(module)