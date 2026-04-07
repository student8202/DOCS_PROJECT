from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse,HTMLResponse
from controllers.docs_ctl import DocsController 
from services.docs_sv import DocsService
from schemas.docs_sh import ApproveSchema
from core.deps import templates # Import từ deps

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
                        GuestName: str = Form(...), IdAddition: int = Form(...), DocType: str = Form(...)):
    user = request.session.get("username")
    # Gọi Controller
    result = docs_ctl.upload_manual_controller(file, FolioNum, BookingID, GuestName, DocType, IdAddition, user)
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

@router.get("/restore/{doc_guid}")
async def restore_file(doc_guid: str):
    """
    API Khôi phục: http://localhost/api/v1/docs/restore/UUID-CHUOII-DAII
    """
    # Gọi Controller xử lý
    result = docs_ctl.restore_file_controller(doc_guid)
    
    # Trả về kết quả JSON kèm mã trạng thái
    return JSONResponse(status_code=result["status"], content=result)

@router.get("/view-list/{folio}", response_class=HTMLResponse)
async def view_signed_docs_page(request: Request, folio: str):
    """
    API mở trang Pop-up: http://localhost/api/v1/docs/view-list/10349
    """
    # 1. Gọi Controller xử lý dữ liệu
    result = docs_ctl.get_view_list_controller(folio)
    
    # 2. Nếu có lỗi (400, 500), quăng lỗi ra trình duyệt
    if result["status"] != 200:
        raise HTTPException(status_code=result["status"], detail=result["detail"])

    # 3. TRỌNG TÂM: Đổ dữ liệu vào file view_list.html
    # Jinja2 sẽ tự động thay thế {{ docs }} và {{ folio }} bằng dữ liệu thực
    return templates.TemplateResponse("docs/view_list.html", {
        "request": request, 
        "docs": result["docs"], 
        "folio": result["folio"]
    })
