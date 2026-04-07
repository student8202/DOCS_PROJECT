from database.db_connection import get_lv_docs_db
from models.signed_doc_md import SignedDocumentModel
from datetime import datetime
from loguru import logger
import shutil
import os, uuid


class DocsService:
    def save_manual_upload(self, file, folio, booking_id, guest_name, doc_type, idAddition, username):
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
                (Booking_ID, Folio_Num, Doc_Type, IdAddtion, Source_Type, Guest_Name_SS, 
                FilePath, File_Extension, Status, Version, IsCurrent, CreatedBy, CreatedAt)
                VALUES (?, ?, ?, ?, 'SCAN', ?, ?, ?, 3, ?, 1, ?, GETDATE())
            """
            cursor.execute(sql_insert, (booking_id, folio, doc_type, idAddition, guest_name, 
                                    db_file_path, file_ext, new_version, username))
                
            conn.commit()
            return True
        finally:
            conn.close()
     
    def save_manual_upload(self, file, folio, booking_id, guest_name, doc_type, id_addition, username):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # --- BƯỚC 1: XỬ LÝ VERSION & ISCURRENT ---
            # Xác định trục xoay: RegCard thì kèm IdAddition, các loại khác chỉ cần Folio
            where_clause = "Folio_Num = ? AND Doc_Type = ? AND IsDeleted = 0"
            params_v = [folio, doc_type]
            
            if doc_type == 'REG_CARD' and id_addition:
                where_clause += " AND IdAddition = ?"
                params_v.append(id_addition)

            # Tìm Version lớn nhất
            sql_check = f"SELECT ISNULL(MAX(Version), 0) FROM dbo.tbl_SignedDocuments WHERE {where_clause}"
            cursor.execute(sql_check, params_v)
            new_version = cursor.fetchone()[0] + 1

            # Vô hiệu hóa các bản cũ của đúng đối tượng này
            sql_update_old = f"UPDATE dbo.tbl_SignedDocuments SET IsCurrent = 0 WHERE {where_clause}"
            cursor.execute(sql_update_old, params_v)

            # --- BƯỚC 2: LƯU FILE VẬT LÝ ---
            now = datetime.now()
            sub_path = os.path.join(str(now.year), f"{now.month:02d}", f"{now.day:02d}")
            base_dir = os.path.join("static", "storage", "signed_docs", sub_path)
            os.makedirs(base_dir, exist_ok=True)

            file_ext = os.path.splitext(file.filename)[1]
            # Tên file có Version và IdAddition để tránh trùng: 10349_REG_CARD_454_v1.pdf
            file_name = f"{folio}_{doc_type}_{id_addition}_v{new_version}{file_ext}".replace(" ", "_")
            full_physical_path = os.path.join(os.getcwd(), base_dir, file_name)
            db_web_path = f"/static/storage/signed_docs/{sub_path}/{file_name}".replace("\\", "/")

            # Ghi file vật lý
            with open(full_physical_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # --- BƯỚC 3: LƯU VÀO DATABASE VẬN HÀNH (LV_DOCS) ---
            doc_guid = uuid.uuid4()
            # Sử dụng chung Model SQL_INSERT_NEW để thống nhất
            params_main = (
                doc_guid,            # 1. Doc_GUID
                str(booking_id),     # 2. Booking_ID
                str(folio),          # 3. Folio_Num
                None,                # 4. Group_Code (Nếu có thì truyền vào)
                id_addition,         # 5. IdAddition
                doc_type,            # 6. Doc_Type
                'SCAN',              # 7. Source_Type (Hàng Upload)
                'FO',                # 8. Owner_Dept
                guest_name,          # 9. Guest_Name_SS
                None,                # 10. Data_JSON_Full_SS (Upload tay nên không có Snapshot)
                db_web_path,         # 11. FilePath
                None,                # 12. Signature_Base64
                file_ext,            # 13. File_Extension
                new_version,         # 14. Version
                username             # 15. CreatedBy
            )
            cursor.execute(SignedDocumentModel.SQL_INSERT_NEW, params_main)

            # --- BƯỚC 4: LƯU VÀO DATABASE ARCHIVE (LV_DOCS_ARCHIVE) ---
            # Đọc lại chính cái file vừa lưu ở trên để đưa vào DB Archive
            with open(full_physical_path, "rb") as f:
                file_binary = f.read()

            sql_archive = """
                INSERT INTO LV_DOCS_ARCHIVE.dbo.tbl_SignedDocuments_Archive 
                (Doc_GUID, Booking_ID, Folio_Num, Doc_Type, FileBinary, FileName_Original, CreatedBy)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql_archive, (doc_guid, booking_id, folio, doc_type, 
                                         file_binary, file_name, username))
                
            conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi Upload: {str(e)}")
            raise e
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
            
    def restore_file_from_archive_service(self, doc_guid: str):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # 1. Truy vấn nội dung nhị phân và đường dẫn mong muốn
            sql = """
                SELECT a.FileBinary, d.FilePath 
                FROM LV_DOCS_ARCHIVE.dbo.tbl_SignedDocuments_Archive a
                JOIN dbo.tbl_SignedDocuments d ON a.Doc_GUID = d.Doc_GUID
                WHERE a.Doc_GUID = ?
            """
            cursor.execute(sql, (doc_guid,))
            row = cursor.fetchone()
            
            if not row:
                raise ValueError(f"Không tìm thấy bản sao Archive cho GUID: {doc_guid}")

            file_binary, db_file_path = row
            
            # 2. Xác định đường dẫn vật lý đầy đủ trên Server Windows
            # db_file_path: /static/storage/signed_docs/2026/04/06/file_v1.pdf
            clean_path = db_file_path.lstrip('/')
            full_physical_path = os.path.join(os.getcwd(), clean_path)
            
            # 3. Tự động tạo lại thư mục YYYY/MM/DD nếu đã bị xóa mất
            dir_path = os.path.dirname(full_physical_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

            # 4. Ghi ngược dữ liệu nhị phân từ DB ra file vật lý
            with open(full_physical_path, "wb") as f:
                f.write(file_binary)
            
            return full_physical_path
        finally:
            conn.close()
            
    def get_signed_docs_with_history_service(self, folio: str):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # BƯỚC 1: Lấy danh sách các bản ghi ĐANG HIỆN HÀNH (IsCurrent = 1)
            # Đây là những tấm hình sẽ hiện ra đầu tiên
            sql_current = """
                SELECT Doc_GUID, IdAddition, Doc_Type, FilePath, Version, CreatedBy,
                       FORMAT(CreatedAt, 'dd/MM/yyyy HH:mm') as CreatedAt
                FROM dbo.tbl_SignedDocuments
                WHERE Folio_Num = ? AND IsDeleted = 0 AND IsCurrent = 1
                ORDER BY IdAddition ASC, Doc_Type ASC
            """
            cursor.execute(sql_current, (folio,))
            columns = [column[0] for column in cursor.description]
            current_docs = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # BƯỚC 2: Lấy toàn bộ LỊCH SỬ của các bản ghi cũ (IsCurrent = 0)
            sql_history = """
                SELECT Doc_GUID, IdAddition, Doc_Type, FilePath, Version,
                       FORMAT(CreatedAt, 'dd/MM/yyyy HH:mm') as CreatedAt
                FROM dbo.tbl_SignedDocuments
                WHERE Folio_Num = ? AND IsDeleted = 0 AND IsCurrent = 0
                ORDER BY Version DESC
            """
            cursor.execute(sql_history, (folio,))
            history_rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # BƯỚC 3: Ghép lịch sử vào đúng bản ghi hiện hành (Dựa trên Doc_Type và IdAddition)
            for doc in current_docs:
                doc['history_list'] = [
                    h for h in history_rows 
                    if h['Doc_Type'] == doc['Doc_Type'] and h['IdAddition'] == doc['IdAddition']
                ]

            return current_docs
        finally:
            conn.close()
