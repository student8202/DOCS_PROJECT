from fastapi import APIRouter, Request, Query
from controllers.tpl_ct import TPLController
from core.deps import templates

router = APIRouter(prefix="/fo/templates", tags=["Template Management"])

# 1. Route hiển thị trang giao diện chính
@router.get("/custom-view")
async def tpl_custom_page(request: Request):
    # Bạn có thể thêm guard check quyền ở đây nếu muốn
    # RBACController.guard(request, "PERM_SYSTEM_SETTING")
    return templates.TemplateResponse("admin/tpl_custom.html", {"request": request})

@router.get("/system-view")
async def tpl_system_page(request: Request):
    return templates.TemplateResponse("admin/tpl_system.html", {"request": request})

@router.get("/list")
async def get_tpl_list(is_custom: int = Query(1)):
    return TPLController.get_list(is_custom)

@router.get("/detail/{tpl_id}")
async def get_tpl_detail(tpl_id: int):
    return TPLController.get_detail(tpl_id)

@router.post("/save")
async def save_tpl(request: Request):
    data = await request.json()
    return TPLController.save(data)
