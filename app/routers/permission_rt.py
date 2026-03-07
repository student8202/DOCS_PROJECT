from fastapi import APIRouter, Request, Body, HTTPException, BackgroundTasks, Depends
from pyodbc import Connection
from database import get_db
from controllers.permission_ctl import PermissionController

router = APIRouter( tags=["Phân Quyền"])

@router.get("/api/view-list")
async def get_view_list(request: Request, db: Connection = Depends(get_db)):
    # Kiểm tra quyền admin từ session
    if not request.session.get("user_id"):
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")
    
    # Truyền 'db' vào Controller
    return PermissionController.get_all_with_view_rights(db)

@router.get("/api/view-rights/{emp_id}")
async def get_emp_rights(emp_id: int, db: Connection = Depends(get_db)):
    return PermissionController.get_view_rights_by_emp(db, emp_id)

@router.post("/api/save-view-rights")
async def save_rights(
    request: Request, 
    background_tasks: BackgroundTasks,
    db: Connection = Depends(get_db),
    data: dict = Body(...)
):
    emp_id = data.get('employee_id')
    dept_ids = data.get('dept_ids', [])
    
    if not emp_id:
        raise HTTPException(status_code=400, detail="Thiếu mã nhân viên")

    # 1. Thực hiện lưu vào Database (truyền db)
    PermissionController.save_view_rights(db, emp_id, dept_ids)
    
    # # không cần vì đã có middleware lưu log
    # # 2. Ghi Log bảo mật
    # user_id = request.session.get("user_id", "System")
    # log_msg = f"Cập nhật quyền xem cho NV ID: {emp_id}. Số lượng: {len(dept_ids)}"
    
    # # Lưu ý: write_user_log cần được gọi đúng cách trong background_tasks
    # background_tasks.add_task(write_user_log, user_id, log_msg)
    
    return {"status": "success", "message": "Cập nhật quyền thành công"}
