from database.db_connection import get_lv_docs_db
import os
from datetime import datetime
import shutil
from loguru import logger

class DocsService:
    def save_manual_upload(self, file, folio, booking_id, guest_name, doc_type, username):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # 1. Tìm Version lớn nhất hiện tại của Folio + Loại hồ sơ này
            sql_check = """
                SELECT MAX(Version) FROM dbo.tbl_SignedDocuments 
                WHERE Folio_Num = ? AND Doc_Type = ? AND IsDeleted = 0
            """
            cursor.execute(sql_check, (folio, doc_type))
            current_max_version = cursor.fetchone()[0] or 0
            new_version = current_max_version + 1

            # 2. Vô hiệu hóa tất cả bản cũ (Set IsCurrent = 0)
            sql_update_old = """
                UPDATE dbo.tbl_SignedDocuments 
                SET IsCurrent = 0 
                WHERE Folio_Num = ? AND Doc_Type = ?
            """
            cursor.execute(sql_update_old, (folio, doc_type))

            # 3. (Logic tạo thư mục và lưu file vật lý giữ nguyên như cũ)
            now = datetime.now()
            # Tạo cấu trúc: 2026/04/04
            sub_path = os.path.join(str(now.year), f"{now.month:02d}", f"{now.day:02d}")
            base_dir = os.path.join("static", "storage", "signed_docs", sub_path)
            
            # Tạo thư mục nếu chưa có
            if not os.path.exists(base_dir):
                os.makedirs(base_dir, exist_ok=True)

            # Lấy đuôi file (ví dụ: .pdf)
            file_ext = os.path.splitext(file.filename)[1]

            # QUAN TRỌNG: Đặt tên file kèm theo Version để không bị ghi đè
            # Ví dụ: 10349_REG_CARD_v1.pdf, 10349_REG_CARD_v2.pdf
            file_name = f"{folio}_{doc_type}_v{new_version}{file_ext}".replace(" ", "_")
            
            # Đường dẫn đầy đủ để lưu file vật lý trên ổ cứng
            full_physical_path = os.path.join(os.getcwd(), base_dir, file_name)
            
            # Đường dẫn thân thiện để lưu vào Database (để Web có thể mở được)
            db_file_path = f"/static/storage/signed_docs/{sub_path}/{file_name}".replace("\\", "/")

            # Thực hiện ghi file vật lý vào ổ cứng
            with open(full_physical_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # 4. Insert bản mới với Version mới và IsCurrent = 1
            sql_insert = """
                INSERT INTO dbo.tbl_SignedDocuments 
                (Booking_ID, Folio_Num, Doc_Type, Source_Type, Guest_Name_SS, 
                FilePath, File_Extension, Status, Version, IsCurrent, CreatedBy, CreatedAt)
                VALUES (?, ?, ?, 'SCAN', ?, ?, ?, 3, ?, 1, ?, GETDATE())
            """
            cursor.execute(sql_insert, (booking_id, folio, doc_type, guest_name, 
                                    db_file_path, file_ext, new_version, username))
                
            conn.commit()
            return True
        finally:
            conn.close()
            
    def get_all_categories(self, module: str):
        """Lấy danh sách các loại hồ sơ (Category) không trùng nhau từ bảng Templates"""
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # Lấy các Category duy nhất (DISTINCT) đang hoạt động (IsActive = 1)
            sql = """
                SELECT DISTINCT Category 
                FROM dbo.tbl_Templates 
                WHERE ModuleName = ? AND IsActive = 1 AND Category IS NOT NULL
            """
            cursor.execute(sql, (module,))
            
            # Chuyển kết quả từ List of Tuples thành List of Strings
            # Ví dụ: [('REG_CARD',), ('CONFIRM',)] -> ['REG_CARD', 'CONFIRM']
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        finally:
            conn.close()
            
    def approve_signature_service(self, queue_id: int, username: str):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # 1. Lấy dữ liệu từ Queue
            cursor.execute("SELECT RefID, RenderedHtml, TemplateID FROM tbl_SignatureQueue WHERE QueueID = ?", (queue_id,))
            row = cursor.fetchone()
            
            if not row:
                # Ghi log để Admin debug trong Terminal
                logger.error(f"Approve thất bại: Không tìm thấy QueueID {queue_id}")
                raise ValueError(f"Hồ sơ số {queue_id} không tồn tại hoặc đã bị xóa.")

            # ... (Logic đóng gói PDF, Insert vào tbl_SignedDocuments) ...
            # Nếu SQL lỗi ở đây, Python tự động quăng Exception lên Controller
            
            conn.commit()
            return True
        finally:
            conn.close()
