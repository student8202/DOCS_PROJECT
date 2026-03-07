from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pyodbc import Connection
from database import get_db
from controllers.employee_ctl import EmployeeController
from schemas.employee import EmployeeCreate

router = APIRouter(tags=["Nhân viên"])

@router.get("/api/all")
async def get_employees(db: Connection = Depends(get_db)):
    return EmployeeController.get_all(db)

@router.post("/api/save")
async def save_employee(data: EmployeeCreate, db: Connection = Depends(get_db)):
    new_id = EmployeeController.save(db, data)
    return {"status": "success", "id": new_id}

@router.delete("/api/delete/{emp_id}")
async def delete_employee(emp_id: int, db: Connection = Depends(get_db)):
    try:
        success = EmployeeController.delete(db, emp_id)
        if not success:
            raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên để xóa")
        return {"status": "success", "message": f"Đã xóa nhân viên ID: {emp_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/api/export")
async def export_employees(db: Connection = Depends(get_db)):
    file_out = EmployeeController.export_excel(db)
    return StreamingResponse(
        file_out, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Employees.xlsx"}
    )


# API Tải file mẫu
@router.get("/api/template")
async def get_template(db: Connection = Depends(get_db)):
    file_out = EmployeeController.get_template_excel(db)
    return StreamingResponse(
        file_out,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Template_Import.xlsx"}
    )

# API Import dữ liệu từ Excel
@router.post("/api/import")
async def import_employees(
    file: UploadFile = File(...), 
    db: Connection = Depends(get_db)
):
    # Kiểm tra định dạng file
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Vui lòng gửi file Excel (.xlsx)")

    content = await file.read() # Đọc file dưới dạng bytes
    try:
        count = EmployeeController.import_excel(db, content)
        return {"status": "success", "message": f"Đã nhập thành công {count} nhân viên."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
