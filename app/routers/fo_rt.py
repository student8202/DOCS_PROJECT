from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from controllers.rbac_ct import RBACController
from controllers.fo_ct import FOController
from services.fo_sv import FOService
from models.rbac_md import RBACModel # Import Model
from core.deps import templates # Import từ deps
from schemas.fo_sh import InHouseRead
from typing import List

router = APIRouter(prefix="/fo", tags=["Front Office"])

# @router.get("/search", include_in_schema=False)
# async def fo_search_page(request: Request):
#     # Người gác cổng check quyền
#     RBACController.guard(request, RBACModel.PERM_VIEW_FO)
    
#     return templates.TemplateResponse("fo_search.html", {"request": request})

# @router.get("/inhouse-list", response_model=List[InHouseRead])
# async def api_inhouse_list(request: Request):
#     # Kiểm tra Session hoặc Quyền view_fo nếu cần tại đây
#     return FOController.get_inhouse_list()
@router.get("/inhouse-list")
async def api_inhouse_list(request: Request):
    # Kiểm tra Session hoặc Quyền view_fo nếu cần tại đây
    return FOController.get_inhouse_list()

@router.get("/inhouse-list2")
async def api_inhouse_list(request: Request):
    # Kiểm tra Session hoặc Quyền view_fo nếu cần tại đây
    return FOController.get_inhouse_list_booking()