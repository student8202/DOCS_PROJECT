from schemas.queue_sh import QueueSendSchema, QueueCompleteSchema
from models.signed_doc_md import SignedDocumentModel
from database.db_connection import get_lv_docs_db
from fastapi import HTTPException
from loguru import logger
from datetime import datetime
from weasyprint import HTML
import traceback
import os,io
import pdfkit, json

class QueueService:

    # 2. TABLET KIỂM TRA HỒ SƠ MỚI (Polling)
    def check_new_doc_logic(self, device_id: str):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # Chỉ lấy hồ sơ mới nhất đang ở trạng thái 0 (Waiting)
            sql = """
                SELECT TOP 1 QueueID, RenderedHtml, RefID 
                FROM dbo.tbl_SignatureQueue 
                WHERE DeviceID = ? AND Status = 0 
                ORDER BY CreatedAt DESC
            """
            cursor.execute(sql, (device_id,))
            row = cursor.fetchone()
            if row:
                # Khi Tablet đã "bốc" hồ sơ này, chuyển trạng thái sang 1 (Processing - Đang xem)
                cursor.execute("UPDATE dbo.tbl_SignatureQueue SET Status = 1 WHERE QueueID = ?", (row[0],))
                conn.commit()
                return {"QueueID": row[0], "Html": row[1], "RefID": row[2]}
            return None
        finally:
            conn.close()

# Cơ chế Độc quyền (Exclusive Waiting): Khi nhân viên gửi hồ sơ mới, lệnh UPDATE Status = 4 sẽ hủy bỏ các hồ sơ cũ mà khách chưa kịp ký. Điều này giúp Tablet luôn hiển thị đúng và duy nhất hồ sơ hiện tại.
# Chuyển trạng thái (State Machine): Ngay khi Tablet lấy được dữ liệu (check_new_doc), nó chuyển Status từ 0 sang 1. Nhân viên ở máy tính nhìn vào bảng Queue sẽ thấy ngay trạng thái: "Khách đang xem hồ sơ".
# Dữ liệu đóng gói (Self-contained): RenderedHtml đã được trộn sẵn dữ liệu ở máy nhân viên. Tablet chỉ việc "đổ" nó ra màn hình, không cần query lại SQL phức tạp, giúp tốc độ phản hồi cực nhanh.

    def get_queue_content_logic(self, queue_id: int):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # Lấy nội dung HTML đã trộn và RefID (Số Folio)
            sql = "SELECT RenderedHtml, RefID FROM dbo.tbl_SignatureQueue WHERE QueueID = ?"
            cursor.execute(sql, (queue_id,))
            row = cursor.fetchone()
            
            if row:
                # Trả về đúng định dạng mà JS (sign_handler.js) đang chờ
                return {
                    "Html": row[0], 
                    "RefID": row[1]
                }
            return {"Html": "Không tìm thấy nội dung hồ sơ", "RefID": ""}
        finally:
            conn.close()
            
    def reset_device_queue(self, device_id: str):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # Hủy tất cả hồ sơ đang ở trạng thái Chờ (0) hoặc Đang ký (1)
            cursor.execute("""
                UPDATE dbo.tbl_SignatureQueue 
                SET Status = 4 
                WHERE DeviceID = ? AND Status IN (0, 1)
            """, (device_id,))
            conn.commit()
            return {"status": "success", "device": device_id}
        finally:
            conn.close()
            
    def check_queue_valid(self, queue_id: int):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # Kiểm tra trạng thái hiện tại
            cursor.execute("SELECT Status FROM dbo.tbl_SignatureQueue WHERE QueueID = ?", (queue_id,))
            row = cursor.fetchone()
            # Nếu Status = 4 (Hủy) hoặc không tìm thấy
            if not row or row[0] == 4:
                return "cancelled"
            return "active"
        finally:
            conn.close()
                
    def get_current_device_by_folio(self, folio: str):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # Tìm DeviceID của hồ sơ mới nhất đang ở trạng thái Chờ (0) hoặc Đang ký (1)
            sql = """
                SELECT TOP 1 DeviceID 
                FROM dbo.tbl_SignatureQueue 
                WHERE RefID = ? AND Status IN (0, 1) 
                ORDER BY CreatedAt DESC
            """
            cursor.execute(sql, (folio,))
            row = cursor.fetchone()
            
            if row:
                # CHỐT HẠ: Phải lấy row[0] để lấy chuỗi 'FO01'
                device_id = row[0] 
                return {"status": "success", "DeviceID": device_id}
            
            return {"status": "success", "DeviceID": None}
        except Exception as e:
            logger.error(f"Lỗi lấy DeviceID từ Folio {folio}: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            conn.close()
            
    def update_queue_device(self, folio: str, new_device_id: str):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # Tìm bản ghi đang chờ (0) hoặc đang ký (1) để đổi máy
            sql = """
                UPDATE dbo.tbl_SignatureQueue 
                SET DeviceID = ?, UpdatedAt = GETDATE()
                WHERE RefID = ? AND Status IN (0, 1)
            """
            cursor.execute(sql, (new_device_id, folio))
            conn.commit()
            return cursor.rowcount > 0 # Trả về True nếu có dòng được update
        finally:
            conn.close()   
            
    def cancel_queue_by_folio(self, folio: str, id_add: int):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # Chuyển trạng thái sang 4 (Hủy) cho các bản ghi chưa hoàn tất (0, 1, 2)
            sql = """
                UPDATE dbo.tbl_SignatureQueue 
                SET Status = 4, ExpiredAt = GETDATE()
                WHERE RefID = ? AND Status IN (0, 1, 2)
            """
            # Nếu nghiệp vụ của bạn yêu cầu hủy chính xác theo cả IdAddition thì thêm vào WHERE
            cursor.execute(sql, (folio,)) 
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
             
    #  Dual-Source (đọc từ File hoặc DB), nên tách thành 3 hàm nhỏ   
    def _get_template_content(self, template_id: int):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT IsCustom, HtmlContent, FilePath FROM tbl_Templates WHERE TemplateID = ?", (template_id,))
            row = cursor.fetchone()
            if not row: return None

            if row.IsCustom:
                return row.HtmlContent
            else:
                # FilePath chỉ lưu tên file, ví dụ: "reg_card.html"
                # Đường dẫn đầy đủ: app/static/templates/reg_card.html
                base_path = os.path.join("app", "static", "templates")
                full_path = os.path.join(base_path, row.FilePath)
                
                if os.path.exists(full_path):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        return f.read()
                return f"<!-- Error: File {row.FilePath} not found -->"
        finally:
            conn.close()
    # Hàm này lo việc thay thế các tag {{...}} và cấy các vùng ký.
    def _render_final_html(self, raw_html: str, snapshot_data: dict):
        html = raw_html
        
        # 1. Mapping dữ liệu từ SMILE
        for key, value in snapshot_data.items():
            val_str = str(value if value is not None else "")
            html = html.replace("{{" + key + "}}", val_str)
            html = html.replace("{{ " + key + " }}", val_str)

        # 2. Cấy vùng ký Khách & Lễ tân
        html = html.replace("{{GuestSignatureImg}}", 
            '<div class="sig-placeholder" onclick="SIGN.actions.openPad(\'guest\')">'
            '<img id="img-guest-sig" src="" style="display:none; max-height:80px;" />'
            '<span class="placeholder-text">Chạm để ký / Touch to sign</span></div>')

        html = html.replace("{{ReceptionSignatureImg}}", 
            '<div class="sig-placeholder" onclick="SIGN.actions.openPad(\'reception\')">'
            '<img id="img-recep-sig" src="" style="display:none; max-height:120px;" />'
            '<span class="placeholder-text">Chạm để ký / Staff Sign</span></div>')
            
        return html
    
    def _get_smile_snapshot(self, folio: str, group: str, id_add: int):
        # 
        return {
            "LastName": "NGUYEN",
            "FirstName": "ANH QUYET",
            "ArrivalDate": "02/04/2026",
            "DepartureDate": "05/04/2026",
            "RoomCode": "1001",
            "RoomType": "DELUXE"
        }
        
    def send_to_queue_logic(self, data: QueueSendSchema, username: str):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
             # 1. Gọi hàm tách riêng để kiểm tra bận (Dùng self._)
            busy_ref_id = self.is_device_busy(data.DeviceID, cursor)
            
            if busy_ref_id:
                logger.warning(f"Thiết bị {data.DeviceID} đang bận hồ sơ {busy_ref_id}")
                # CHỈ RAISE EXCEPTION - Không dùng HTTPException ở Service
                raise ValueError(f"Thiết bị {data.DeviceID} đang bận xử lý hồ sơ {busy_ref_id}.")

            # 2. Lấy HTML thô (Từ File hoặc DB)
            raw_html = self._get_template_content(data.TemplateID)
            if not raw_html:
                raise HTTPException(status_code=404, detail="Không tìm thấy mẫu.")

            # 3. Lấy dữ liệu thực & Trộn (Render)
            # Giả sử bạn đã có hàm lấy snapshot từ SMILE
            snapshot = self._get_smile_snapshot(data.FolioNum, data.GroupCode, data.IdAddition)
            html_final = self._render_final_html(raw_html, snapshot)

            # 4. Lưu vào Queue
            sql = """INSERT INTO dbo.tbl_SignatureQueue 
                    (ModuleName, RefType, RefID, DeviceID, TemplateID, RenderedHtml, Status, CreatedBy, CreatedAt)
                    VALUES (?, ?, ?, ?, ?, ?, 0, ?, GETDATE())"""
            cursor.execute(sql, (data.ModuleName, data.RefType, data.RefID, data.DeviceID, 
                                data.TemplateID, html_final, username))
            conn.commit()
            return {"status": "success"}
        except Exception as e:
            logger.info(traceback.format_exc()) # In toàn bộ vết lỗi (dòng mấy, file nào) ra màn hình đen (Console)
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()
    
    def is_device_busy(self, device_id: str, cursor):
        """
        Hàm bổ trợ: Kiểm tra thiết bị có hồ sơ chưa hoàn tất (Status 0, 1) không.
        Truyền cursor vào để dùng chung kết nối với hàm gọi nó.
        """
        sql = """
            SELECT TOP 1 RefID 
            FROM dbo.tbl_SignatureQueue 
            WHERE LTRIM(RTRIM(DeviceID)) = LTRIM(RTRIM(?)) 
            AND Status IN (0, 1)
        """
        cursor.execute(sql, (device_id,))
        row = cursor.fetchone()
        
        # Nếu có row nghĩa là bận, trả về RefID đó. Nếu không bận trả về None.
        return row[0] if row else None

    def _export_html_to_pdf(self, html_content: str, save_path: str):
        """
        Hàm chuyên biệt để xuất file PDF từ chuỗi HTML.
        """
        # 1. Cấu hình đường dẫn thực thi wkhtmltopdf
        path_wkhtmlto = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmlto)
        
        # 2. Thiết lập Options tối ưu: Tắt JS, cho phép truy cập file nội bộ để tăng tốc
        options = {
            'encoding': "UTF-8",
            'quiet': '',                       # Không in log ra console để đỡ tốn tài nguyên
            'no-outline': None,                # Tắt mục lục
            'disable-javascript': None,        # TẮT JS: Đây là nguyên nhân gây chậm nhất
            'enable-local-file-access': None,  # Chỉ cho phép đọc file trên ổ cứng (ảnh chữ ký)
            'disable-external-links': None,    # CẤM kết nối ra ngoài (Internet)
            'page-size': 'A4',
            'margin-top': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
            'margin-left': '10mm',
        }

        try:
            # Thực hiện chuyển đổi
            try:
                pdfkit.from_string(html_content, save_path, configuration=config, options=options)
                return True
            except OSError as e:
                # Nếu lỗi chứa "Exit with code 1" nhưng file vẫn tồn tại thì coi như thành công
                if 'code 1' in str(e) and os.path.exists(save_path):
                    pass 
                else:
                    raise e
        except Exception as e:
            logger.error(f"Lỗi PDFKit nội bộ: {str(e)}")
            raise Exception(f"Không thể tạo file PDF: {str(e)}")
     
    def _export_html_to_pdf_WS(self, html_content: str, save_path: str):
        """
        Sử dụng WeasyPrint để xuất PDF (Không cần wkhtmltopdf).
        """
        try:
            # Chuyển đổi trực tiếp từ chuỗi HTML sang file PDF
            HTML(string=html_content).write_pdf(save_path)
            return True
        except Exception as e:
            print(f"Lỗi WeasyPrint: {e}")
            return False

       
    def complete_and_archive_service(self, data, username):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # 1. Lấy dữ liệu từ Queue và Template
            sql_select = """
                SELECT q.RefID, q.RenderedHtml, t.Category, q.ModuleName
                FROM dbo.tbl_SignatureQueue q
                JOIN dbo.tbl_Templates t ON q.TemplateID = t.TemplateID
                WHERE q.QueueID = ?
            """
            cursor.execute(sql_select, (data.QueueID,))
            row = cursor.fetchone()
            if not row: 
                raise ValueError(f"Không tìm thấy hồ sơ ID {data.QueueID}")
            
            folio, html_raw, category, module = row[0], row[1], row[2], row[3]

            # 2. Chèn chữ ký Base64 vào HTML
            html_signed = html_raw
            if data.Guest_Signature:
                html_signed = html_signed.replace('id="img-guest-sig" src=""', f'id="img-guest-sig" src="{data.Guest_Signature}" style="display:block; max-height:100px;"')
            if data.Reception_Signature:
                html_signed = html_signed.replace('id="img-recep-sig" src=""', f'id="img-recep-sig" src="{data.Reception_Signature}" style="display:block; max-height:100px;"')

            # 3. Tạo cấu trúc thư mục lưu trữ YYYY/MM/DD
            now = datetime.now()
            sub_path = os.path.join(str(now.year), f"{now.month:02d}", f"{now.day:02d}")
            dir_path = os.path.join("static", "storage", "signed_docs", sub_path)
            os.makedirs(dir_path, exist_ok=True)

            file_name = f"{folio}_{category}.pdf".replace(" ", "_")
            full_physical_path = os.path.join(dir_path, file_name)
            db_web_path = f"/static/storage/signed_docs/{sub_path}/{file_name}".replace("\\", "/")

            # 4. XUẤT PDF (Đã thêm configuration và options)
            self._export_html_to_pdf_WS(html_signed, full_physical_path)

            # 5. Lấy Snapshot dữ liệu SMILE
            snapshot = self._get_smile_snapshot(folio, None, 0) 
            json_snapshot = json.dumps(snapshot, ensure_ascii=False)

            # 6. Lưu vào kho hồ sơ vĩnh viễn (Sử dụng Model SQL đã bàn ở trên cho sạch)
            
            params = (
                None,                # Doc_Group_ID
                str(folio),          # Booking_ID (ConfirmNum)
                str(folio),          # Folio_Num
                None,                # Group_Code
                str(category),       # Doc_Type
                'DIGITAL',           # Source_Type
                str(module),         # Owner_Dept
                str(snapshot.get('LastName', '')), # Guest_Name_SS
                json_snapshot,       # Data_JSON_Full_SS
                db_web_path,         # FilePath
                data.Guest_Signature,# Signature_Base64
                '.pdf',              # File_Extension
                username             # CreatedBy
            )
            cursor.execute(SignedDocumentModel.SQL_INSERT, params)

            # 7. Cập nhật Queue sang trạng thái 2
            cursor.execute("UPDATE dbo.tbl_SignatureQueue SET Status = 2 WHERE QueueID = ?", (data.QueueID,))
            
            conn.commit()
            return True
            
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            raise e
        finally:
            conn.close()

    