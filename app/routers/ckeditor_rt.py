import os
import shutil
from fastapi import APIRouter, File, UploadFile, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from core.deps import templates

router = APIRouter(prefix="/admin/ckeditor", tags=["CKEditor"])

UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/browser", response_class=HTMLResponse)
async def file_browser(request: Request):
    file_list = []
    if UPLOAD_DIR.exists():
        for f in os.listdir(UPLOAD_DIR):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                path = UPLOAD_DIR / f
                file_list.append({
                    "name": f,
                    "size": round(os.path.getsize(path) / 1024, 1) # KB
                })
                
    return templates.TemplateResponse("admin/ck_file_browser.html", {
        "request": request, 
        "files": file_list
    })

@router.post("/upload")
async def quick_upload(upload: UploadFile = File(...)):
    try:
        # Làm sạch tên file để tránh lỗi path
        clean_name = upload.filename.replace(" ", "_")
        file_path = UPLOAD_DIR / clean_name
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload.file, buffer)
        
        return {
            "uploaded": 1,
            "fileName": clean_name,
            "url": f"/static/uploads/{clean_name}"
        }
    except Exception as e:
        return {"uploaded": 0, "error": {"message": str(e)}}
