from fastapi import APIRouter, Request, Depends
from schemas.queue_sh import QueueSendSchema, QueueSignSchema
from services.queue_sv import QueueService

router = APIRouter(prefix="/api/v1/queue", tags=["Signature Queue"])
service = QueueService()


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
