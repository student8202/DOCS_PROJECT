from database.db_connection import get_lv_docs_db
from schemas.device_sh import DeviceRegisterSchema,DevicePingSchema
import datetime

class DeviceService:
    def register_device_logic(self, data: DeviceRegisterSchema):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # 1. Kiểm tra xem DeviceID (quầy) này đã tồn tại trong DB chưa
            cursor.execute("SELECT DeviceID FROM dbo.tbl_Devices WHERE DeviceID = ?", (data.DeviceID,))
            exists = cursor.fetchone()

            if exists:
                # CHIẾM QUYỀN: Ghi đè ConnectionID mới và cập nhật LastActive
                sql = """
                    UPDATE dbo.tbl_Devices 
                    SET ConnectionID = ?, LastActive = GETDATE(), DeviceType = ?, ModuleName = ?
                    WHERE DeviceID = ?
                """
                cursor.execute(sql, (data.ConnectionID, data.DeviceType, data.ModuleName, data.DeviceID))
            else:
                # ĐĂNG KÝ MỚI: Nếu quầy này chưa có trong danh sách quầy
                sql = """
                    INSERT INTO dbo.tbl_Devices (DeviceID, ConnectionID, DeviceType, ModuleName, LastActive)
                    VALUES (?, ?, ?, ?, GETDATE())
                """
                cursor.execute(sql, (data.DeviceID, data.ConnectionID, data.DeviceType, data.ModuleName))
            
            conn.commit()
            return {"status": "success", "message": "Registered/Taken over successfully"}
        finally:
            conn.close()

    def ping_logic(self, data: DevicePingSchema):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # 1. Lấy ConnectionID hiện tại của quầy này trong DB
            cursor.execute("SELECT ConnectionID FROM dbo.tbl_Devices WHERE DeviceID = ?", (data.DeviceID,))
            row = cursor.fetchone()
            
            if not row:
                return {"status": "not_found"}
            
            db_conn_id = row[0]

            # 2. SO SÁNH: Nếu ConnectionID gửi lên khác với DB -> Máy này đã bị "đá" ra
            if db_conn_id != data.ConnectionID:
                return {"status": "conflict", "message": "Another device took over this ID"}

            # 3. NẾU KHỚP: Cập nhật LastActive để giữ trạng thái IsOnline = 1
            cursor.execute("UPDATE dbo.tbl_Devices SET LastActive = GETDATE() WHERE DeviceID = ?", (data.DeviceID,))
            conn.commit()
            
            return {"status": "online"}
        finally:
            conn.close()
            
    def get_online_devices_logic(self, module: str):
        """Lấy danh sách các quầy đang Online thuộc phân hệ (FO/POS...)"""
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # Lọc theo Module và trạng thái IsOnline = 1 (Computed column trong SQL)
            sql = """
                SELECT DeviceID, DeviceName, DeviceType, ModuleName 
                FROM dbo.tbl_Devices 
                WHERE ModuleName = ? AND IsOnline = 1
                ORDER BY DeviceID ASC
            """
            cursor.execute(sql, (module,))
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            conn.close()
