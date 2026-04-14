from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from schemas.fo_bill_sh import  FolioSearchRequest
from controllers.fo_bill_ctl import FOBillController
from services.fo_bill_svc import FOBillService
from core.deps import templates # Import từ deps
from typing import List
from loguru import logger

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

api_router = APIRouter(prefix="/api/v1/fo/bill", tags=["FO Bill API"])

@api_router.post("/search-folio")
async def api_search_folio(payload: FolioSearchRequest):
    try:
        # Router chỉ nhận payload và chuyển cho Controller xử lý
        return await FOBillController.search_folios_logic(payload.model_dump())
    except Exception as e:
        logger.error(f"RT: Lỗi API cuối cùng - {str(e)}")
        return {"status": "error", "layer": "RT", "msg": str(e)}

@api_router.get("/transactions/{folio}/{tab}")
async def api_get_transactions(folio: str, tab: str):
    try:
        return await FOBillController.get_transactions_logic(folio, tab)
    except Exception as e:
        logger.error(f"RT: Lỗi API cuối cùng - {str(e)}")
        return {"status": "error", "layer": "RT", "msg": str(e)}
    
@api_router.get("/details/{folio}/{id_addition}")
async def api_get_folio_details(folio: str, id_addition: int, show_all: int = 0):
    try:
        # Bạn cần viết thêm logic này trong Controller
        return await FOBillController.get_folio_details_logic(folio, id_addition, show_all)
    except Exception as e:
        logger.error(f"RT: Lỗi lấy chi tiết Folio - {str(e)}")
        return {"status": "error", "layer": "RT", "msg": str(e)}
    
@api_router.get("/tabs/{folio}/{show_all}")
async def api_get_tabs(folio: str, show_all: int):
    """
    Endpoint riêng để load lại danh sách Tab khi toggle nút 'Show All Bal'
    """
    try:
        return await FOBillController.get_tabs(folio, show_all)
    except Exception as e:
        logger.error(f"RT: Lỗi Endpoint lấy danh sách Tab {folio} - {str(e)}")
        return {"status": "error", "layer": "RT", "msg": str(e)}
    
@api_router.get("/check-update/{folio}")
async def api_check_folio_update(folio: str):
    try:
        # Gọi trực tiếp Controller để lấy MaxID
        return await FOBillController.get_max_id_logic(folio)
    except Exception as e:
        logger.error(f"RT Error (CheckUpdate): {str(e)}")
        return {"status": "error", "data": {"MaxTransactionID": 0}}