from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from controllers.rbac_ct import RBACController
from controllers.fo_ct import FOController
from services.fo_sv import FOService
from core.deps import templates # Import từ deps
from typing import List

router = APIRouter(prefix="/fo", tags=["FO Bill Management"])

@router.get("/bill-manage", response_class=HTMLResponse)
async def bill_manage_page(request: Request):
    # Bạn có thể lấy danh sách thiết bị từ DB ở đây để đổ vào Dropdown iPad
    # devices = device_sv.get_active_devices(module="FO")
    return templates.TemplateResponse(
        "fo/fo_bill_manage.html", 
        {
            "request": request,
            "title": "Quản lý Bill & Giao dịch",
            # "devices": devices 
        }
    )

