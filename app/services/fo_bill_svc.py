from database.db_connection import get_smile_fo_db # Import hàm của bạn
from loguru import logger
from core.utils import tcvn3_to_unicode_cmt, tcvn3_to_unicode

class FOBillService:
    @staticmethod
    def _to_dict(cursor, row):
        """Helper biến row SQL thành dictionary"""
        if not row: return None
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))

    @staticmethod
    def search_folios(f: dict):
        """Thực thi spSearchFolioTransaction với logic skip result sets đã thành công"""
        conn = get_smile_fo_db()
        if not conn: return []
        
        try:
            cursor = conn.cursor()
            # 1. Chống lỗi thông báo rác
            cursor.execute("SET NOCOUNT ON")
            
            query = "{CALL spSearchFolioTransaction (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)}"
            params = (
                f.get('noShow', 0), f.get('reserved', 0), f.get('canceled', 0), f.get('inHouse', 1),
                f.get('arrivalToday', 0), f.get('checkOutToday', 0), f.get('checkOut', 0),
                f.get('sNumInfo', ''), f.get('name', ''), f.get('firstName', ''), f.get('lastName', ''),
                f.get('companyID', ''), f.get('groupID', ''), f.get('countryID', ''), f.get('roomCode', ''),
                f.get('arrivalDateFrom', ''), f.get('arrivalDateTo', ''), 
                f.get('departureDateFrom', ''), f.get('departureDateTo', ''),
                f.get('hotelDate', ''), f.get('exactly', 0), f.get('includePf', 0),
                f.get('sTAorARNum', ''), f.get('isNotBalance', 0), f.get('cruiseCode', '')
            )
            # TẠO CÂU LỆNH SQL DẠNG "EXEC" RIÊNG ĐỂ LOG (Dễ copy chạy trong SQL nhất)
            # Dùng "EXEC" thay vì "{CALL}" cho câu log
            sql_log_template = "EXEC spSearchFolioTransaction " + ", ".join(["{}"] * 25)
            formatted_params = [f"'{p}'" if isinstance(p, str) else str(p) for p in params]
            full_sql_log = sql_log_template.format(*formatted_params)

            # In ra log
            logger.debug(f"SVC: SQL DEBUG (Copy to SQL Studio): {full_sql_log}")
            # 2. Gọi Store
            cursor.execute(query, params)

            # 3. LẶP CHO ĐẾN KHI CHẠM DỮ LIỆU THẬT (Giống code mẫu của bạn)
            while cursor.description is None:
                if not cursor.nextset(): 
                    break
            
            # 4. Nếu vẫn không thấy description thì trả về rỗng
            if cursor.description is None: 
                return []

            # 5. Map dữ liệu
            columns = [col[0] for col in cursor.description] 
            rows = cursor.fetchall()
            
            # Chuyển đổi Unicode nếu cần (giống code cũ của bạn dùng tcvn3_to_unicode)
            results = [dict(zip(columns, row)) for row in rows]
            
            # Xử lý tiếng Việt TCVN3 cho TẤT CẢ các trường có kiểu chuỗi (String)
            for g in results:
                for key, value in g.items():
                    if isinstance(value, str):
                        g[key] = tcvn3_to_unicode_cmt(value)
            
            return results

        except Exception as e:
            logger.error(f"SVC Error: {str(e)}")
            raise e # Ném lỗi lên tầng trên (Controller)
        finally:
            conn.close()

    @staticmethod
    def get_folio_summary(folio_num: str, id_addition: int, show_all: int):
        """Gom nhóm thông tin Header khách hàng"""
        conn = get_smile_fo_db()
        if not conn: return None
        
        try:
            cursor = conn.cursor()
            # 1. Lấy thông tin Header (Dùng SQL Query thuần thường không bị lỗi nextset)
            sql = """
                SELECT F.FolioExRate, F.FolioNum, A.FirstName, A.LastName, RoomCode, 
                    A.ArrivalTime, A.DepartureTime, A.AdtStatus, RateAmount, F.Notice, 
                    F.TravelAgent1Code, COALESCE(NoPostFlag, 0) AS NoPost, C.NoOfDec
                FROM Folio F
                JOIN AdditionalName A ON F.FolioNum = A.FolioNum
                JOIN CurrencyDef C ON F.FolioCurrencyCode = C.CurrencyCode
                WHERE A.FolioNum = ? AND A.IdAddition = ?
            """
            cursor.execute(sql, (folio_num, id_addition))
            row = cursor.fetchone()
            header = FOBillService._to_dict(cursor, row) if row else None
            
            if header:
                # --- MỚI: Lấy thông tin Company Name ---
                if header.get('TravelAgent1Code'):
                    sql_company = "SELECT ClientName FROM CLIENT WHERE ClientFolioNum = ?"
                    cursor.execute(sql_company, (header['TravelAgent1Code'],))
                    company_row = cursor.fetchone()
                    if company_row:
                        # Lưu ý: Giải mã TCVN3 cho tên công ty luôn
                        header['CompanyName'] = tcvn3_to_unicode_cmt(company_row[0])
                    else:
                        header['CompanyName'] = ""
                else:
                    header['CompanyName'] = ""
                    
                # Xử lý tiếng Việt cho Header (FirstName, LastName, Notice...)
                for key, value in header.items():
                    if isinstance(value, str) and key != 'CompanyName':
                        header[key] = tcvn3_to_unicode_cmt(value)

                # 2. Lấy danh sách Tab (Dùng CALL Store Procedure nên CẦN nextset)
                cursor.execute("{CALL CHGetFolioBalanceCode (?, ?)}", (folio_num, show_all))
                
                # --- ÁP DỤNG LOGIC AN TOÀN CỦA BẠN ---
                while cursor.description is None:
                    if not cursor.nextset(): 
                        break
                
                if cursor.description:
                    # Lấy danh sách tab, thường là cột đầu tiên [0]
                    header['Tabs'] = [r[0].strip() for r in cursor.fetchall() if r[0]]
                else:
                    header['Tabs'] = []

            return header

        except Exception as e:
            logger.error(f"SVC: Lỗi SQL Server (GetSummary) - {str(e)}")
            raise e 
        finally:
            conn.close()

    @staticmethod
    def get_transactions(folio_num: str, tab: str):
        """Thực thi CHGetFolioTransactionNew lấy Tầng 2"""
        conn = get_smile_fo_db()
        if not conn: return []
        
        try:
            cursor = conn.cursor()
            # SMILE cần tab có khoảng trắng kiểu 'A '
            cursor.execute("{CALL CHGetFolioTransactionNew (?, ?, 1)}", (folio_num, f"{tab} "))
            # --- PHẦN SỬA ĐỔI: Bỏ qua các tập kết quả trống (None) ---
            while cursor.description is None:
                if not cursor.nextset():
                    break
            
            # Sau khi thoát vòng lặp, kiểm tra nếu có dữ liệu thì fetch
            if cursor.description:
                rows = cursor.fetchall()
                return [FOBillService._to_dict(cursor, r) for r in rows]
            
            return [] # Trả về list rỗng nếu không có dữ liệu sau khi duyệt hết
        except Exception as e:
            logger.error(f"SVC: Lỗi SQL Server - {str(e)}") # Biết ngay lỗi do DB
            raise e # Ném lỗi lên tầng trên (Controller)
        finally:
            conn.close()

    @staticmethod
    def get_max_transaction_id(folio_num: str):
        """Lấy TransactionID lớn nhất hiện tại để theo dõi thay đổi"""
        conn = get_smile_fo_db()
        if not conn: return 0
        try:
            cursor = conn.cursor()
            sql = "SELECT MAX(TransactionID) FROM FolioTransaction WHERE FolioNum = ?"
            cursor.execute(sql, (folio_num,))
            row = cursor.fetchone()
            return row[0] if row and row[0] else 0
        except Exception as e:
            logger.error(f"SVC Error (MaxID): {e}")
            return 0
        finally:
            conn.close()
            
    @staticmethod
    def get_available_tabs(folio_num: str, show_all: int):
        """Thực thi CHGetFolioBalanceCode để lấy danh sách mã Tab"""
        conn = get_smile_fo_db()
        if not conn: return []
        
        try:
            cursor = conn.cursor()
            # Thực thi Procedure
            cursor.execute("{CALL CHGetFolioBalanceCode (?, ?)}", (folio_num, show_all))
            
            # Bỏ qua các tập kết quả trống (None description)
            while cursor.description is None:
                if not cursor.nextset():
                    break
            
            if cursor.description:
                rows = cursor.fetchall()
                # row[0] là mã Tab (ví dụ: 'A ', 'B ', 'V ')
                return [row[0].strip() for row in rows if row[0]]
            
            return []
        except Exception as e:
            logger.error(f"Service Error (get_available_tabs): {str(e)}")
            raise e
        finally:
            conn.close()
        
    @staticmethod
    def get_client_name(client_folio_num: int):
        """Lấy tên Travel Agent / Company từ ClientFolioNum"""
        conn = get_smile_fo_db()
        if not conn: return ""
        try:
            cursor = conn.cursor()
            sql = "SELECT ClientName FROM CLIENT WHERE ClientFolioNum = ?"
            cursor.execute(sql, (client_folio_num,))
            row = cursor.fetchone()
            return row[0] if row else ""
        except Exception as e:
            logger.error(f"SVC Error (ClientName): {e}")
            return ""
        finally:
            conn.close()