from fastapi import APIRouter, Depends
from schemas.queue_sh import QueueSendSchema, QueueSignSchema
from services.queue_sv import QueueService

router = APIRouter(prefix="/api/v1/queue", tags=["Signature Queue"])
service = QueueService()

@router.post("/send")
async def send_to_tablet(data: QueueSendSchema):
    """Máy nhân viên gọi API này để đẩy hồ sơ sang iPad"""
    return service.send_to_queue_logic(data)

@router.get("/check/{device_id}")
async def check_for_tablet(device_id: str):
    """iPad gọi API này mỗi 5 giây để xem có hồ sơ mới không"""
    return service.check_new_doc_logic(device_id)
