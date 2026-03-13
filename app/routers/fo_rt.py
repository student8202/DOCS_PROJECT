from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from controllers.rbac_ct import RBACController
from models.rbac_md import RBACModel # Import Model
from core.deps import templates # Import từ deps

router = APIRouter(prefix="/fo", tags=["Front Office"])

@router.get("/search", include_in_schema=False)
async def fo_search_page(request: Request):
    # Người gác cổng check quyền
    RBACController.guard(request, RBACModel.PERM_VIEW_FO)
    
    return templates.TemplateResponse("fo_search.html", {"request": request})
