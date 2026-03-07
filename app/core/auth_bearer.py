from fastapi import Request, HTTPException, status

async def verify_admin(request: Request):
    """Dependency kiểm tra quyền admin nhanh"""
    perms = request.session.get("permissions", "").split(",")
    if "admin" not in perms:
        raise HTTPException(status_code=403, detail="Bạn không có quyền quản trị")
    return True