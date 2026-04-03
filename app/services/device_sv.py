from database.db_connection import get_lv_docs_db
from schemas.device_sh import DeviceRegisterSchema, DevicePingSchema
import datetime
from fastapi import HTTPException


class DeviceService:
    def register_device_logic(self, data: DeviceRegisterSchema):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # 1. KIỂM TRA: Thiết bị có tồn tại trong danh mục không?
            cursor.execute(
                "SELECT DeviceID FROM dbo.tbl_Devices WHERE DeviceID = ?",
                (data.DeviceID,),
            )
            exists = cursor.fetchone()

            if not exists:
                # Nếu không thấy FO03 -> Chặn đứng và trả về lỗi 400 ngay lập tức
                raise HTTPException(
                    status_code=400,
                    detail=f"Mã quầy '{data.DeviceID}' chưa được khai báo. Vui lòng liên hệ Admin!",
                )

            # 2. NẾU TỒN TẠI: Chỉ thực hiện UPDATE (Chiếm quyền)
            # Chúng ta KHÔNG dùng INSERT ở đây để tránh tạo rác dữ liệu
            sql = """
                UPDATE dbo.tbl_Devices 
                SET ConnectionID = ?, 
                    LastActive = GETDATE(), 
                    DeviceType = ?, 
                    ModuleName = ?
                WHERE DeviceID = ?
            """
            cursor.execute(
                sql,
                (data.ConnectionID, data.DeviceType, data.ModuleName, data.DeviceID),
            )

            conn.commit()
            return {
                "status": "success",
                "message": "Đã chiếm quyền điều khiển quầy thành công",
            }

        except HTTPException as he:
            # Nếu là lỗi do mình chủ động raise (400) thì ném tiếp ra ngoài
            raise he
        except Exception as e:
            # Các lỗi hệ thống khác (SQL, kết nối...)
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()

    def ping_logic(self, data: DevicePingSchema):
        conn = get_lv_docs_db()
        cursor = conn.cursor()
        try:
            # 1. Lấy ConnectionID hiện tại của quầy này trong DB
            cursor.execute(
                "SELECT ConnectionID FROM dbo.tbl_Devices WHERE DeviceID = ?",
                (data.DeviceID,),
            )
            row = cursor.fetchone()

            if not row:
                return {"status": "not_found"}

            db_conn_id = row[0]

            # 2. SO SÁNH: Nếu ConnectionID gửi lên khác với DB -> Máy này đã bị "đá" ra
            if db_conn_id != data.ConnectionID:
                return {
                    "status": "conflict",
                    "message": "Another device took over this ID",
                }

            # 3. NẾU KHỚP: Cập nhật LastActive để giữ trạng thái IsOnline = 1
            cursor.execute(
                "UPDATE dbo.tbl_Devices SET LastActive = GETDATE() WHERE DeviceID = ?",
                (data.DeviceID,),
            )
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
                SELECT 
                d.DeviceID, 
                d.DeviceName, 
                d.DeviceType, 
                d.ModuleName,
                CASE 
                    WHEN EXISTS (
                        SELECT 1 FROM dbo.tbl_SignatureQueue q 
                        WHERE q.DeviceID = d.DeviceID AND q.Status IN (0, 1)
                    ) THEN 1 ELSE 0 
                END AS IsBusy
            FROM dbo.tbl_Devices d
            WHERE d.ModuleName = ? AND d.IsOnline = 1
            ORDER BY d.DeviceID ASC
            """
            cursor.execute(sql, (module,))
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            conn.close()
