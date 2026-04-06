from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from controllers.docs_ctl import DocsController 
from services.docs_sv import DocsService
from schemas.docs_sh import ApproveSchema

router = APIRouter(
    prefix="/api/v1/docs",
    tags=["Documents Management"]
)

# Khởi tạo Service
docs_svc = DocsService()
docs_ctl = DocsController() # Khởi tạo Controller

@router.post("/upload-manual")
async def upload_manual(request: Request, file: UploadFile = File(...), 
                        FolioNum: str = Form(...), BookingID: str = Form(...), 
                        GuestName: str = Form(...), DocType: str = Form(...)):
    user = request.session.get("username")
    # Gọi Controller
    result = docs_ctl.upload_manual_controller(file, FolioNum, BookingID, GuestName, DocType, user)
    return JSONResponse(status_code=result["status"], content=result)
    # raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_categories(module: str = "FO"):
    """
    API: http://localhost/api/v1/docs/categories?module=FO
    Dùng để nạp danh sách vào Selectbox ở Frontend
    """
    try:
        # Gọi sang Controller để lấy dữ liệu
        result = docs_ctl.get_categories_logic(module)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/approve")
async def approve_signature(request: Request, data: ApproveSchema):
    # 1. Lấy user từ session
    user = request.session.get("username")
    
    # 2. Gọi Controller và nhận kết quả "đã đóng gói"
    result = docs_ctl.approve_signature_controller(data.QueueID, user)
    
    # 3. Trả về đúng mã trạng thái mà Controller đã định đoạt
    return JSONResponse(status_code=result["status"], content=result)
