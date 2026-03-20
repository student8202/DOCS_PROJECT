from database.db_connection import get_lv_docs_db
from datetime import datetime

class TPLService:
    @staticmethod
    def get_list_logic(is_custom: int):
        conn = get_lv_docs_db()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT TemplateID, TemplateCode, TemplateName, IsActive, CreatedBy FROM FO.tbl_Templates WHERE IsCustom = ?", (is_custom,))
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally: conn.close()

    @staticmethod
    def get_detail_logic(tpl_id: int):
        conn = get_lv_docs_db()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM FO.tbl_Templates WHERE TemplateID = ?", (tpl_id,))
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
            return None
        finally: conn.close()

    @staticmethod
    def save_logic(data: dict, user_name: str):
        conn = get_lv_docs_db()
        try:
            cursor = conn.cursor()
            tpl_id = data.get('TemplateID')
            
            if tpl_id: # UPDATE
                sql = """UPDATE FO.tbl_Templates SET TemplateCode=?, TemplateName=?, IsCustom=?, 
                         HtmlContent=?, FilePath=?, UpdatedBy=?, UpdatedAt=? WHERE TemplateID=?"""
                cursor.execute(sql, (data['TemplateCode'], data['TemplateName'], data['IsCustom'], 
                                     data['HtmlContent'], data['FilePath'], user_name, datetime.now(), tpl_id))
            else: # INSERT
                sql = """INSERT INTO FO.tbl_Templates (TemplateCode, TemplateName, IsCustom, HtmlContent, FilePath, CreatedBy) 
                         VALUES (?, ?, ?, ?, ?, ?)"""
                cursor.execute(sql, (data['TemplateCode'], data['TemplateName'], data['IsCustom'], 
                                     data['HtmlContent'], data['FilePath'], user_name))
            conn.commit()
            return {"status": "success"}
        finally: conn.close()
