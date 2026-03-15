# app/services/fo_sv.py
from models.fo_md import FOModel
from database.db_connection import get_smile_fo_db

class FOService:
    @staticmethod
    def get_hotel_date():
        conn = get_smile_fo_db()
        try:
            cursor = conn.cursor()
            cursor.execute(FOModel.SQL_GET_HOTEL_DATE)
            row = cursor.fetchone()
            # Trả về định dạng MM/DD/YYYY để SP SMILE hiểu
            return row.HotelDate.strftime('%m/%d/%Y') if row else None
        finally:
            conn.close()

    @staticmethod
    def get_inhouse_list_logic():
        hotel_date = FOService.get_hotel_date()
        if not hotel_date: return []
        
        conn = get_smile_fo_db()
        try:
            cursor = conn.cursor()
            # Gọi SP với tham số HotelDate vừa lấy được
            cursor.execute(FOModel.SQL_GET_INHOUSE_GUESTS, (hotel_date,))
            columns = [col for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            conn.close()
