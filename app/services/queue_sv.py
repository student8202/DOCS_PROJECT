from schemas.queue_sh import QueueSendSchema
from database.db_connection import get_lv_docs_db

class QueueService:
    # 1. NHÂN VIÊN GỬI HỒ SƠ VÀO HÀNG ĐỢI
    def send_to_queue_logic(self, data: QueueSendSchema, username: str):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # 1. LOGIC TRỘN DỮ LIỆU (RENDER)
            # Giả sử bạn đã có hàm render_tpl(template_id, folio, group, id_add)
            # Nếu chưa có, tạm thời lấy HtmlContent gốc của Template
            cursor.execute("SELECT HtmlContent FROM tbl_Templates WHERE TemplateID = ?", (data.TemplateID,))
            tpl_row = cursor.fetchone()
            html_final = tpl_row[0] if tpl_row else "Template Error"

            # 2. Hủy hồ sơ cũ của thiết bị
            cursor.execute("UPDATE dbo.tbl_SignatureQueue SET Status = 4 WHERE DeviceID = ? AND Status = 0", (data.DeviceID,))
            
            # 3. Insert với đầy đủ thông tin
            sql = """
                INSERT INTO dbo.tbl_SignatureQueue 
                (ModuleName, RefType, RefID, DeviceID, TemplateID, RenderedHtml, Status, CreatedBy, CreatedAt)
                VALUES (?, ?, ?, ?, ?, ?, 0, ?, GETDATE())
            """
            cursor.execute(sql, (
                data.ModuleName, data.RefType, data.RefID, data.DeviceID, 
                data.TemplateID, html_final, username
            ))
            
            conn.commit()
            return {"status": "success"}
        finally:
            conn.close()

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
