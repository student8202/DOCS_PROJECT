from schemas.queue_sh import QueueSendSchema
from database.db_connection import get_lv_docs_db
from fastapi import HTTPException
from loguru import logger
import traceback
import os

class QueueService:
    # 1. NHÂN VIÊN GỬI HỒ SƠ VÀO HÀNG ĐỢI
    # def send_to_queue_logic(self, data: QueueSendSchema, username: str):
    #     conn = get_lv_docs_db()
    #     cursor = conn.cursor()
    #     try:
    #         # 1. KIỂM TRA TRẠNG THÁI THIẾT BỊ: Có hồ sơ nào chưa hoàn tất không?
    #         # Status 0: Waiting, Status 1: Processing
    #         cursor.execute("""
    #             SELECT TOP 1 QueueID, RefID 
    #             FROM dbo.tbl_SignatureQueue 
    #             WHERE DeviceID = ? AND Status IN (0, 1)
    #         """, (data.DeviceID,))
    #         busy_doc = cursor.fetchone()

    #         if busy_doc:
    #             # NẾU ĐANG BẬN: Chặn đứng và báo lỗi về Dashboard
    #             raise Exception(f"Thiết bị {data.DeviceID} đang bận xử lý hồ sơ {busy_doc[1]}. "
    #                             f"Vui lòng đợi khách ký xong hoặc hủy hồ sơ cũ.")
            
    #         # 1. LOGIC TRỘN DỮ LIỆU (RENDER)
    #         # Giả sử bạn đã có hàm render_tpl(template_id, folio, group, id_add)
    #         # Nếu chưa có, tạm thời lấy HtmlContent gốc của Template
    #         cursor.execute("SELECT HtmlContent FROM tbl_Templates WHERE TemplateID = ?", (data.TemplateID,))
    #         tpl_row = cursor.fetchone()
            
    #         if not tpl_row:
    #             return {"status": "error", "message": "Không tìm thấy mẫu"}

    #         html_final = tpl_row[0] # Lấy chuỗi HTML từ Tuple
    #         # Thay thế thẻ đánh dấu bằng một thẻ img có ID cụ thể
    #         # Cấy vùng chứa cho Khách
    #         html_final = html_final.replace("{{GuestSignatureImg}}", 
    #             '<div class="sig-placeholder" onclick="SIGN.actions.openPad(\'guest\')">'
    #             '<img id="img-guest-sig" src="" style="display:none; max-height:80px;" />'
    #             '<span class="placeholder-text">Chạm để ký / Touch to sign</span>'
    #             '</div>')

    #         # Cấy vùng chứa cho Lễ tân
    #         html_final = html_final.replace("{{ReceptionSignatureImg}}", 
    #             '<div class="sig-placeholder" onclick="SIGN.actions.openPad(\'reception\')">'
    #             '<img id="img-recep-sig" src="" style="display:none; max-height:120px;" />'
    #             '<span class="placeholder-text">Chạm để ký / Staff Sign</span>'
    #             '</div>')

    #         # 2. Hủy hồ sơ cũ của thiết bị
    #         cursor.execute("UPDATE dbo.tbl_SignatureQueue SET Status = 4 WHERE DeviceID = ? AND Status = 0", (data.DeviceID,))
            
    #         # 3. Insert với đầy đủ thông tin
    #         sql = """
    #             INSERT INTO dbo.tbl_SignatureQueue 
    #             (ModuleName, RefType, RefID, DeviceID, TemplateID, RenderedHtml, Status, CreatedBy, CreatedAt)
    #             VALUES (?, ?, ?, ?, ?, ?, 0, ?, GETDATE())
    #         """
    #         cursor.execute(sql, (
    #             data.ModuleName, data.RefType, data.RefID, data.DeviceID, 
    #             data.TemplateID, html_final, username
    #         ))
            
    #         conn.commit()
    #         return {"status": "success"}
    #     except Exception as e:
    #         # Các lỗi hệ thống khác (SQL, kết nối...)
    #         raise HTTPException(status_code=500, detail=str(e))
    #     finally:
    #         conn.close()

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
            # 1. Kiểm tra thiết bị bận
            cursor.execute("SELECT QueueID FROM dbo.tbl_SignatureQueue WHERE DeviceID = ? AND Status IN (0, 1)", (data.DeviceID,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail=f"Thiết bị {data.DeviceID} đang bận.")

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
