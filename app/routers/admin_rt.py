from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from controllers.rbac_ct import RBACController
from models.rbac_md import RBACModel # Import Model
from core.deps import templates # Import từ deps

# Khai báo lại đường dẫn templates tương đối từ thư mục app
# templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/admin", tags=["Config"])


@router.get("/sync-users", include_in_schema=False)
async def sync_users_page(request: Request):
    # Kiểm tra quyền 'admin' trong session trước khi cho vào
    user_perms = request.session.get("permissions", [])
    if "admin" not in user_perms:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/dashboard")
        
    return templates.TemplateResponse("admin/sync_users.html", {"request": request})
