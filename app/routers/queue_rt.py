from fastapi import APIRouter, Request, Depends,HTTPException
from schemas.queue_sh import QueueSendSchema, QueueSignSchema, DeviceResetSchema
from services.queue_sv import QueueService
from controllers.queue_ctl import QueueController

router = APIRouter(prefix="/api/v1/queue", tags=["Signature Queue"])
service = QueueService()
queue_ctl = QueueController()


@router.post("/send")
async def send_to_tablet(data: QueueSendSchema,request: Request):
    current_user = request.session.get("username")
    """Máy nhân viên gọi API này để đẩy hồ sơ sang iPad"""
    return service.send_to_queue_logic(data, current_user)

@router.get("/check/{device_id}")
async def check_for_tablet(device_id: str):
    """iPad gọi API này mỗi 5 giây để xem có hồ sơ mới không"""
    return service.check_new_doc_logic(device_id)

@router.get("/get-content/{queue_id}")
async def get_queue_content(queue_id: int, svc: QueueService = Depends()):
    """iPad gọi API này để lấy nội dung HTML đã trộn dữ liệu để hiển thị"""
    return svc.get_queue_content_logic(queue_id)

@router.get("/get-current-device/{folio}")
async def get_current_device(folio: str):
    """
    API lấy iPad đang xử lý Folio để chuẩn bị Reset
    """
    result = queue_ctl.get_current_device_logic(folio)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.get("/check-valid/{queue_id}")
async def check_valid(queue_id: int, svc: QueueService = Depends()):
    status = svc.check_queue_valid(queue_id)
    return {"status": status}

@router.post("/reset-device")
async def reset_device_queue(
    data: DeviceResetSchema, 
    svc: QueueService = Depends()
):
    """
    Giải phóng thiết bị: Hủy tất cả hồ sơ đang ở trạng thái Chờ (0) 
    hoặc Đang ký (1) để đưa thiết bị về trạng thái Rảnh.
    """
    # data.DeviceID là chuỗi (str) -> Truyền vào hàm Service đã sửa ở trên
    return svc.reset_device_queue(data.DeviceID)

@router.post("/change-device")
async def change_device(data: dict): # Bạn có thể tạo Schema riêng nếu muốn
    folio = data.get("FolioNum")
    new_device = data.get("NewDeviceID")
    return queue_ctl.change_device_logic(folio, new_device)

@router.post("/force-cancel")
async def force_cancel(data: dict):
    folio = data.get("FolioNum")
    id_add = data.get("IdAddition")
    return queue_ctl.force_cancel_logic(folio, id_add)

