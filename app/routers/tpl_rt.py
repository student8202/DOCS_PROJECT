from fastapi import APIRouter, Request, Query, Depends
from controllers.tpl_ct import TPLController
from schemas.tpl_sh import TemplateCreateSchema, TemplateSystemSaveSchema # Import Schema để validate
from core.deps import templates

router = APIRouter(prefix="/fo/templates", tags=["Template Management"])

# 1. ROUTES HIỂN THỊ GIAO DIỆN (RENDER HTML)
@router.get("/custom-view")
async def tpl_custom_page(request: Request):
    return templates.TemplateResponse("admin/tpl_custom.html", {"request": request})

@router.get("/system-view")
async def tpl_system_page(request: Request):
    return templates.TemplateResponse("admin/tpl_system.html", {"request": request})

# 2. ROUTES API (XỬ LÝ DỮ LIỆU) - SỬ DỤNG DEPENDS
@router.get("/list")
async def get_tpl_list(
    is_custom: int = Query(1),
    controller: TPLController = Depends(TPLController) # Tiêm Controller vào đây
):
    # Không gọi TPLController.get_list() (static) mà gọi qua instance 'controller'
    return controller.get_list(is_custom)

@router.get("/detail/{tpl_id}")
async def get_tpl_detail(
    tpl_id: int,
    controller: TPLController = Depends(TPLController)
):
    return controller.get_detail(tpl_id)

@router.get("/system-detail/{tpl_id}")
async def get_system_detail(tpl_id: int, controller: TPLController = Depends(TPLController)):
    return controller.get_system_detail(tpl_id)

@router.get("/tags")
async def get_tags(controller: TPLController = Depends(TPLController)):
    """API trả về danh sách thẻ động cho Sidebar"""
    return controller.get_tags()

@router.post("/save")
async def save_tpl(
    request: Request, # Thêm request để đọc session
    data: TemplateCreateSchema,
    controller: TPLController = Depends(TPLController)
):
    # Lấy user từ session (đã được gán lúc login thành công)
    current_user = request.session.get("username")
    if not current_user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Phiên làm việc hết hạn")
        
    return controller.save(data, current_user)

@router.post("/save-system")
async def save_system_tpl(
    request: Request,
    data: TemplateSystemSaveSchema,
    controller: TPLController = Depends(TPLController)
):
    username = request.session.get("username", "DevAdmin")
    return controller.save_system(data, username)