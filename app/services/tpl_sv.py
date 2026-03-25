import json
from loguru import logger
from database.db_connection import get_lv_docs_db, get_smile_fo_db
from schemas.tpl_sh import TemplateCreateSchema, TemplateSystemSaveSchema
import os

class TPLService:
    # Thư mục gốc cố định cho Template hệ thống
    # project_root/app/static/templates
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    TARGET_DIR = os.path.join(BASE_DIR, "app", "static", "templates")
    
    def get_list_logic(self, is_custom: int):
        conn = get_lv_docs_db()
        if not conn:
            raise Exception("Không thể kết nối cơ sở dữ liệu hệ thống")
        
        cursor = conn.cursor()
        try:
            # Lấy danh sách mẫu dựa trên IsCustom (1: CKEditor, 0: Dev)
            sql = """
                SELECT TemplateID, TemplateCode, TemplateName, ModuleName, SubModule, 
                       Category, FilePath, IsActive, CreatedBy, CreatedAt 
                FROM dbo.tbl_Templates 
                WHERE IsCustom = ?
                ORDER BY CreatedAt DESC
            """
            cursor.execute(sql, (is_custom,))
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_detail_logic(self, tpl_id: int):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            sql = "SELECT * FROM dbo.tbl_Templates WHERE TemplateID = ?"
            cursor.execute(sql, (tpl_id,))
            row = cursor.fetchone()
            if not row:
                return None
            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, row))
        finally:
            conn.close()
    
    # 2. Hàm chuyên biệt cho System (Đọc file vật lý nạp vào Monaco)
    def get_system_content_logic(self, file_name: str):
        """Đọc file dựa trên tên file, Backend tự gán Path"""
        full_path = os.path.join(self.TARGET_DIR, file_name)
        if not os.path.exists(full_path):
            return "<!-- Error: File không tồn tại trên hệ thống -->"
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
        
    def save_logic(self, data: TemplateCreateSchema, username: str):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # Kiểm tra trùng mã Code nếu là thêm mới (không có TemplateID)
            if not data.TemplateID:
                cursor.execute("SELECT TemplateID FROM dbo.tbl_Templates WHERE TemplateCode = ?", (data.TemplateCode,))
                if cursor.fetchone():
                    raise Exception(f"Mã mẫu '{data.TemplateCode}' đã tồn tại.")

            if data.TemplateID:
                # 1. Update
                sql = """
                    UPDATE dbo.tbl_Templates SET 
                        TemplateCode=?, TemplateName=?, ModuleName=?, SubModule=?, Category=?,
                        HtmlContent=?, IsActive=?, UpdatedBy=?, UpdatedAt=GETDATE()
                    WHERE TemplateID=?
                """
                cursor.execute(sql, (data.TemplateCode, data.TemplateName, data.ModuleName, 
                                     data.SubModule, data.Category, data.HtmlContent, data.IsActive, 
                                     username, data.TemplateID))
            else:
                # 2. Insert (Mặc định IsCustom = 1 cho người dùng ko biết code)
                sql = """
                    INSERT INTO dbo.tbl_Templates 
                    (TemplateCode, TemplateName, ModuleName, SubModule, Category,IsCustom, HtmlContent, IsActive, CreatedBy, CreatedAt)
                    VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, GETDATE())
                """
                cursor.execute(sql, (data.TemplateCode, data.TemplateName, data.ModuleName, 
                                     data.SubModule, data.Category, data.HtmlContent, data.IsActive, username))
            
            # 3. Ghi Audit Log
            cursor.execute("INSERT INTO dbo.tbl_AuditLogs (Username, ActionName, ModuleName, TargetID, Description) VALUES (?,?,?,?,?)",
                           (username, 'SAVE_TPL', data.ModuleName, data.TemplateCode, f"Lưu mẫu: {data.TemplateName}"))
            
            conn.commit()
            return {"status": "success", "message": "Lưu dữ liệu thành công"}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    def read_file_content(self, file_path: str):
        """Đọc nội dung file HTML từ đường dẫn vật lý"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return "<!-- File không tồn tại hoặc đường dẫn sai -->"
        

    def get_tags_logic(self):
        """Lấy danh sách thẻ động từ DB LV_DOCS"""
        conn = get_lv_docs_db()
        if not conn:
            raise Exception("Không thể kết nối cơ sở dữ liệu hệ thống")
        
        cursor = conn.cursor()
        try:
            sql = "SELECT TagName, TagCode, ModuleName FROM tbl_TemplateTags WHERE IsActive = 1 ORDER BY SortOrder"
            cursor.execute(sql)
            
            # ĐÚNG CHUẨN pyodbc: Lấy tên cột từ phần tử đầu tiên của mỗi tuple trong description
            columns = [column[0] for column in cursor.description]
            
            rows = cursor.fetchall()
            
            # Tạo danh sách các dictionary sạch
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            return result
        except Exception as e:
            logger.error(f"SQL Error tags: {str(e)}")
            raise e
        finally:
            conn.close()
            
    def save_system_tpl_logic(self, data: TemplateSystemSaveSchema, username: str):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # --- BƯỚC 1: XỬ LÝ FILE VẬT LÝ ---
            # Chỉ lấy tên file (VD: confirm.html), bỏ qua mọi đường dẫn linh tinh để bảo mật
            file_name = os.path.basename(data.FilePath) 
            if not file_name.endswith('.html'): 
                file_name += '.html'
            
            # Đường dẫn thực tế để Python ghi file xuống ổ cứng
            full_path = os.path.join(self.TARGET_DIR, file_name)

            # --- BƯỚC 2: CẬP NHẬT DATABASE ---
            # Kiểm tra ID: Nếu ID > 0 thì mới là cập nhật, ngược lại là thêm mới
            if data.TemplateID and data.TemplateID > 0:
                # LOGIC CẬP NHẬT (UPDATE)
                sql = """UPDATE tbl_Templates SET 
                            TemplateCode=?, TemplateName=?, ModuleName=?, SubModule=?, 
                            Category=?, FilePath=?, IsActive=?, UpdatedBy=?, UpdatedAt=GETDATE() 
                         WHERE TemplateID=?"""
                
                params = (
                    data.TemplateCode, data.TemplateName, data.ModuleName, 
                    data.SubModule, data.Category, file_name, data.IsActive,
                    username, data.TemplateID
                )
                cursor.execute(sql, params)
            else:
                # LOGIC THÊM MỚI (INSERT)
                # IsCustom = 0 (dành cho hệ thống), IsActive lấy từ form
                sql = """INSERT INTO tbl_Templates 
                            (TemplateCode, TemplateName, ModuleName, SubModule, Category, 
                             IsCustom, FilePath, IsActive, CreatedBy, CreatedAt) 
                         VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, GETDATE())"""
                
                params = (
                    data.TemplateCode, data.TemplateName, data.ModuleName, 
                    data.SubModule, data.Category, file_name, data.IsActive, 
                    username
                )
                cursor.execute(sql, params)

            # --- BƯỚC 3: GHI NỘI DUNG VÀO FILE ---
            # Đảm bảo thư mục static/templates luôn tồn tại
            os.makedirs(self.TARGET_DIR, exist_ok=True)
            
            # Ghi đè (hoặc tạo mới) nội dung từ Monaco Editor vào file vật lý
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(data.HtmlContent)

            conn.commit()
            return {"status": "success", "message": f"Đã lưu thành công file {file_name}"}
            
        except Exception as e:
            if conn: conn.rollback()
            raise Exception(f"Lỗi hệ thống tập tin hoặc SQL: {str(e)}")
        finally:
            if conn: conn.close()