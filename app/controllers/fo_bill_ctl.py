from services.fo_bill_svc import FOBillService
from loguru import logger

class FOBillController:
    @staticmethod
    async def search_folios_logic(payload: dict):
        # --- DEBUG: Log đầu vào tại Controller ---
        logger.debug(f"CTL: Bắt đầu xử lý Search cho: {payload.get('sNumInfo')}")
        
        try:
            # 1. Gọi Service (Service đang dùng pyodbc nên gọi trực tiếp)
            data = FOBillService.search_folios(payload)
            
            # 2. Xử lý dữ liệu thô
            if data:
                for row in data:
                    # Ép kiểu an toàn: Nếu Balance là None thì trả về 0
                    val = row.get('Balance')
                    row['Balance'] = float(val) if val is not None else 0.0
                    
                    # Format ngày tháng nếu cần (SMILE đôi khi trả về đối tượng datetime)
                    # row['Arrival'] = row['Arrival'].strftime('%d/%m/%Y') if ...
            
            return {
                "status": "success", 
                "data": data,
                "layer": "CTL" # Đánh dấu đã qua tầng Controller thành công
            }
            
        except Exception as e:
            # Ghi log lỗi chi tiết kèm nội dung Exception
            logger.error(f"CTL Error (Search): {str(e)}")
            return {
                "status": "error", 
                "message": "Lỗi tại Controller khi xử lý dữ liệu", 
                "detail": str(e),
                "layer": "CTL"
            }
    @staticmethod
    async def get_folio_details_logic(folio: str, id_addition: int):
        """MỚI: Xử lý gộp dữ liệu Summary bên trái và cấu hình ban đầu"""
        logger.debug(f"CTL: Lấy thông tin Header Folio {folio}")
        try:
            # 1. Gọi Service lấy Header, Company Name và Tabs
            header = FOBillService.get_folio_summary(folio, id_addition)
            
            if not header:
                return {"status": "error", "message": "Không tìm thấy thông tin khách"}

            # 2. Lấy thêm Max ID hiện tại để JS theo dõi
            max_id = FOBillService.get_max_transaction_id(folio)
            header['MaxTransactionID'] = max_id

            return {
                "status": "success",
                "data": header,
                "layer": "CTL"
            }
        except Exception as e:
            logger.error(f"CTL Error (Details): {str(e)}")
            return {"status": "error", "message": str(e), "layer": "CTL"}
        
    @staticmethod
    async def get_transactions_logic(folio: str, tab: str):
        logger.debug(f"CTL: Lấy giao dịch Folio {folio}, Tab {tab}")
        try:
            data = FOBillService.get_transactions(folio, tab)
            
            # Ép kiểu an toàn từng dòng và tính tổng
            tab_balance = 0.0
            for row in data:
                val = row.get('Amount', 0)
                # Chống lỗi nếu Amount là None
                row['Amount'] = float(val) if val is not None else 0.0
                tab_balance += row['Amount']
            
            return {
                "status": "success", 
                "data": data,
                "tab_balance": tab_balance,
                "layer": "CTL"
            }
        except Exception as e:
            logger.error(f"CTL Error (Trans): {str(e)}")
            return {"status": "error", "message": str(e), "layer": "CTL"}
