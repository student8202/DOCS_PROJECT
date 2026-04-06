# app/services/fo_sv.py
from models.fo_md import FOModel
from database.db_connection import get_smile_fo_db
from loguru import logger
from core.utils import tcvn3_to_unicode

class FOService:
    @staticmethod
    def get_hotel_date():
        conn = get_smile_fo_db()
        if not conn: return None
        try:
            cursor = conn.cursor()
            # 1. Truy vấn lấy ngày khách sạn
            cursor.execute(FOModel.SQL_GET_HOTEL_DATE)
            row = cursor.fetchone()
            
            # 2. KIỂM TRA AN TOÀN: Nếu có dòng dữ liệu và giá trị không NULL
            if row and row[0]:
                # Ép kiểu datetime sang string định dạng MM/DD/YYYY
                return row[0].strftime('%m/%d/%Y') 
            
            return None
        except Exception as e:
            logger.error(f"Lỗi lấy HotelDate: {str(e)}")
            return None
        finally:
            conn.close()
            
    @staticmethod
    def get_hotel_name():
        conn = get_smile_fo_db()
        if not conn: return None
        try:
            cursor = conn.cursor()
            # 1. Truy vấn lấy ngày khách sạn
            cursor.execute(FOModel.SQL_GET_HOTEL_NAME)
            row = cursor.fetchone()
            
            # 2. KIỂM TRA AN TOÀN: Nếu có dòng dữ liệu và giá trị không NULL
            if row and row[0]:
                return row[0]
            
            return None
        except Exception as e:
            logger.error(f"Lỗi lấy HotelDate: {str(e)}")
            return None
        finally:
            conn.close()
        
    @staticmethod
    def get_guest_list_logic(mode: int):
        hotel_date = FOService.get_hotel_date()
        if not hotel_date: return []

        conn = get_smile_fo_db()
        try:
            cursor = conn.cursor()
            cursor.execute("SET NOCOUNT ON")
            
            if mode == 0:
                sql = FOModel.SQL_SEARCH_RS_IH
            elif mode == 1:
                sql = FOModel.SQL_SEARCH_RS
            elif mode == 2:
                sql = FOModel.SQL_SEARCH_INHOUSE
            
            # 1. Gọi Store Procedure SMILE
            cursor.execute(sql, (hotel_date,))
            while cursor.description is None:
                if not cursor.nextset(): break
                
            if cursor.description is None: return []

            columns = [col[0] for col in cursor.description] 
            guests = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # 2. LỌC DANH SÁCH FOLIONUM TỪ KẾT QUẢ SP (Điều kiện: IdAddition = 0)
            # Chúng ta chỉ đi tìm Specials/Notice cho những Folio chính này
            main_folios = [str(g['FolioNum']) for g in guests if g.get('IdAddition') == 0 and g.get('FolioNum')]
            
            if main_folios:
                folio_ids_str = ",".join(main_folios)
                
                # 3. Lấy Specials (Nối chuỗi) dựa trên FolioNum
                sql_spec = f"""
                    SELECT FolioNum, STRING_AGG(SpecialCode, ', ') as SpecialService 
                    FROM SMILE_FO.dbo.Folio_Special 
                    WHERE FolioNum IN ({folio_ids_str})
                    GROUP BY FolioNum
                """
                cursor.execute(sql_spec)
                spec_map = {row[0]: row[1] for row in cursor.fetchall()}

                # 4. Lấy Notice dựa trên FolioNum
                sql_notc = f"""
                    SELECT FolioNum, Notice 
                    FROM SMILE_FO.dbo.Folio 
                    WHERE FolioNum IN ({folio_ids_str})
                """
                cursor.execute(sql_notc)
                notc_map = {row[0]: row[1] for row in cursor.fetchall()}

                for g in guests:
                    f_id = g.get('FolioNum')
                    is_main = g.get('IdAddition') == 0
                    
                    # Chỉ gán dữ liệu bổ sung nếu là Folio chính (IdAddition = 0 từ SP)
                    if is_main:
                        g['SpecialService'] = spec_map.get(f_id, "")
                        g['Notice'] = notc_map.get(f_id, "")
                    else:
                        g['SpecialService'] = ""
                        g['Notice'] = ""
                        
                    # 1. Tạo bản đồ ánh xạ nhanh
                    # 1. TẠO BẢN ĐỒ ÁNH XẠ DỰA TRÊN FFOLIONUM
                    # Chúng ta tìm xem trong mỗi nhóm FFolioNum, dòng nào (thường là IdAddition=0) có chứa Group/Company
                    group_map = {}
                    company_map = {}

                    for g in guests:
                        f_folio = g.get('FFolioNum')
                        # Nếu dòng này có GroupCode hoặc CompanyName thì lưu lại làm "mẫu" cho cả nhóm FFolioNum đó
                        if f_folio:
                            if g.get('GroupCode') and f_folio not in group_map:
                                group_map[f_folio] = g.get('GroupCode')
                            if g.get('CompanyName') and f_folio not in company_map:
                                company_map[f_folio] = g.get('CompanyName')

                    # 2. BƠM DỮ LIỆU VÀO TẤT CẢ CÁC RECORD TRONG NHÓM
                    for g in guests:
                        f_folio = g.get('FFolioNum')
                        if f_folio in group_map:
                            # Gán dữ liệu vào cột ẩn chuyên dùng để SORT
                            g['SortGroup'] = group_map[f_folio]
                        else:
                            g['SortGroup'] = g.get('GroupCode', '')

                        if f_folio in company_map:
                            # Gán dữ liệu vào cột ẩn chuyên dùng để SORT
                            g['SortCompany'] = company_map[f_folio]
                        else:
                            g['SortCompany'] = g.get('CompanyName', '')
  
                   # Xử lý tiếng Việt TCVN3 cho TẤT CẢ các trường có kiểu chuỗi (String)
                    for g in guests:
                        for key, value in g.items():
                            if isinstance(value, str):
                                g[key] = tcvn3_to_unicode(value)
                    # GỌI HÀM TÁCH RIÊNG ĐỂ BƠM TRẠNG THÁI KÝ
                    guests = FOService._check_sign_status_internal(guests, cursor)
            return guests
        except Exception as e:
            print(f"Error: {str(e)}")
            return []
        finally:
            conn.close()
            
    @staticmethod
    def get_guest_list_logic_booking(mode: int):
        hotel_date = FOService.get_hotel_date()
        if not hotel_date: return []

        conn = get_smile_fo_db()
        try:
            cursor = conn.cursor()
            cursor.execute("SET NOCOUNT ON")
            
            if mode == 0:
                sql = FOModel.SQL_SEARCH_RS_IH
            elif mode == 1:
                sql = FOModel.SQL_SEARCH_RS
            elif mode == 2:
                sql = FOModel.SQL_SEARCH_INHOUSE
                
            # 1. Gọi Store Procedure SMILE
            cursor.execute(sql, (hotel_date,))
            while cursor.description is None:
                if not cursor.nextset(): break
                
            if cursor.description is None: return []

            columns = [col[0] for col in cursor.description] 
            guests = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # 2. LẤY SPECIALS & NOTICE (Chỉ cho Folio chính IdAddition = 0)
            main_folios = [str(g['FolioNum']) for g in guests if g.get('IdAddition') == 0 and g.get('FolioNum')]
            spec_map = {}
            notc_map = {}
            
            if main_folios:
                folio_ids_str = ",".join(main_folios)
                # Lấy Specials
                cursor.execute(f"SELECT FolioNum, STRING_AGG(SpecialCode, ', ') FROM SMILE_FO.dbo.Folio_Special WHERE FolioNum IN ({folio_ids_str}) GROUP BY FolioNum")
                spec_map = {row[0]: row[1] for row in cursor.fetchall()}
                # Lấy Notice
                cursor.execute(f"SELECT FolioNum, Notice FROM SMILE_FO.dbo.Folio WHERE FolioNum IN ({folio_ids_str})")
                notc_map = {row[0]: row[1] for row in cursor.fetchall()}

            # Gán dữ liệu Specials/Notice vào dòng chính trước khi điều chuyển
            for g in guests:
                if g.get('IdAddition') == 0:
                    f_id = g.get('FolioNum')
                    g['SpecialService'] = spec_map.get(f_id, "")
                    g['Notice'] = notc_map.get(f_id, "")
                    # 1. TẠO BẢN ĐỒ ÁNH XẠ DỰA TRÊN FFOLIONUM
                    # Chúng ta tìm xem trong mỗi nhóm FFolioNum, dòng nào (thường là IdAddition=0) có chứa Group/Company
                    group_map = {}
                    company_map = {}

                    for g in guests:
                        f_folio = g.get('FFolioNum')
                        # Nếu dòng này có GroupCode hoặc CompanyName thì lưu lại làm "mẫu" cho cả nhóm FFolioNum đó
                        if f_folio:
                            if g.get('GroupCode') and f_folio not in group_map:
                                group_map[f_folio] = g.get('GroupCode')
                            if g.get('CompanyName') and f_folio not in company_map:
                                company_map[f_folio] = g.get('CompanyName')

                    # 2. BƠM DỮ LIỆU VÀO TẤT CẢ CÁC RECORD TRONG NHÓM
                    for g in guests:
                        f_folio = g.get('FFolioNum')
                        if f_folio in group_map:
                            # Gán dữ liệu vào cột ẩn chuyên dùng để SORT
                            g['SortGroup'] = group_map[f_folio]
                        else:
                            g['SortGroup'] = g.get('GroupCode', '')

                        if f_folio in company_map:
                            # Gán dữ liệu vào cột ẩn chuyên dùng để SORT
                            g['SortCompany'] = company_map[f_folio]
                        else:
                            g['SortCompany'] = g.get('CompanyName', '')
            # 3. LOGIC ĐIỀU CHUYỂN DỮ LIỆU & GOM NHÓM (FFOLIONUM)
            from collections import defaultdict
            groups = defaultdict(list)
            for g in guests:
                groups[g['FFolioNum']].append(g)

            final_guests = []
            for f_folio, members in groups.items():
                # Tìm dòng Reservation (IdAddition = 0)
                res_row = next((m for m in members if m.get('IdAddition') == 0), None)
                
                # Tìm các dòng khách (IdAddition > 0), sắp xếp để tìm dòng đầu tiên
                guest_rows = sorted([m for m in members if m.get('IdAddition') > 0], 
                                    key=lambda x: x.get('IdAddition', 0))

                if res_row and guest_rows:
                    first_guest = guest_rows[0]
                    
                    # Copy TẤT CẢ các cột từ dòng IdAddition=0 sang dòng khách đầu tiên
                    # Trừ cột IdAddition để không làm hỏng định danh của dòng khách
                    for key, value in res_row.items():
                        if key != 'IdAddition':
                            first_guest[key] = value
                    
                    # Thêm các dòng khách vào danh sách cuối cùng (bỏ dòng res_row)
                    final_guests.extend(guest_rows)
                else:
                    # Nếu nhóm không có khách (chỉ có res) hoặc ngược lại, giữ nguyên để tránh mất data
                    final_guests.extend(members)
                    
                    
            # 4. CHUYỂN ĐỔI TCVN3 -> UNICODE CHO TẤT CẢ DỮ LIỆU CUỐI CÙNG
            for g in final_guests:
                for key, value in g.items():
                    if isinstance(value, str):
                        g[key] = tcvn3_to_unicode(value)
            # GỌI HÀM TÁCH RIÊNG ĐỂ BƠM TRẠNG THÁI KÝ
            final_guests = FOService._check_sign_status_internal(final_guests, cursor)
            
            return final_guests

        except Exception as e:
            logger.error(f"Error: {str(e)}")
            print(f"Error: {str(e)}")
            return []
        finally:
            conn.close()
    
    @staticmethod       
    def _check_sign_status_internal(guests_list, cursor):
        """
        Tách riêng logic kiểm tra trạng thái ký từ 2 bảng: Queue và SignedDocuments
        """
        logger.info(f"DEBUG: Checking status for {len(guests_list)} guests") # <-- Thêm dòng này
        if not guests_list: return guests_list

        # 1. Thu thập danh sách Folio để query 1 lần
        all_folios = list(set([f"'{g['FolioNum']}'" for g in guests_list if g.get('FolioNum')]))
        folios_str = ",".join(all_folios)
        
        # Bản đồ lưu trạng thái: { 'Folio123': {'REG_CARD', 'CONFIRM'} }
        status_map = {}

        if folios_str:
            # 2. TRUY VẤN BẢNG QUEUE (Những bản khách VỪA KÝ XONG - Status 2)
            sql_queue = f"""
                SELECT q.RefID, t.Category
                FROM LV_DOCS.dbo.tbl_SignatureQueue q
                INNER JOIN LV_DOCS.dbo.tbl_Templates t ON q.TemplateID = t.TemplateID
                WHERE q.RefID IN ({folios_str}) AND q.Status = 2
            """
            cursor.execute(sql_queue)
            for r in cursor.fetchall():
                f_id, cat = r[0], r[1].upper()
                status_map.setdefault(f_id, set()).add(cat)

            # 3. TRUY VẤN BẢNG SIGNED_DOCS (Những bản ĐÃ DUYỆT XONG - Status 3)
            sql_signed = f"""
                SELECT Folio_Num, Doc_Type 
                FROM LV_DOCS.dbo.tbl_SignedDocuments 
                WHERE Folio_Num IN ({folios_str}) AND Status = 3 AND IsDeleted = 0
            """
            cursor.execute(sql_signed)
            for r in cursor.fetchall():
                f_id, cat = r[0], r[1].upper() # Doc_Type lưu REG_CARD hoặc CONFIRM
                status_map.setdefault(f_id, set()).add(cat)

        # 4. BƠM DỮ LIỆU VÀO DANH SÁCH KHÁCH
        for g in guests_list:
            f_id = g['FolioNum']
            ff_id = g['FFolioNum']
            
            # Check cả Folio lẻ (thường cho RegCard) và Folio tổng (thường cho Confirm)
            signed = status_map.get(f_id, set()) | status_map.get(ff_id, set())
            
            has_reg = "REG_CARD" in signed
            has_conf = "CONFIRM" in signed

            if has_reg and has_conf: g['SignMode'] = 'FULL'
            elif has_reg: g['SignMode'] = 'REG_ONLY'
            elif has_conf: g['SignMode'] = 'CONF_ONLY'
            else: g['SignMode'] = 'NONE'

            # logger.info(f"DEBUG: Sample SignMode: {guests_list[0].get('SignMode')}") 
        return guests_list


    