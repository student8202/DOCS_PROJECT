from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from core.deps import templates

router = APIRouter(prefix="/sign", tags=["Sign Views"])

# 1. Trang Chờ (Dành cho iPad để ở quầy)
@router.get("/waiting", response_class=HTMLResponse)
async def waiting_page(request: Request):
    return templates.TemplateResponse("sign/waiting_screen.html", {"request": request})

# 2. Trang Ký (Khi có hồ sơ đổ về)
@router.get("/process/{queue_id}", response_class=HTMLResponse)
async def sign_page(request: Request, queue_id: int):
    return templates.TemplateResponse("sign/sign_process.html", {
        "request": request, 
        "queue_id": queue_id
    })
