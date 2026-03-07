from pyodbc import Connection
from typing import List

class PermissionController:
    @staticmethod
    def get_all_with_view_rights(db: Connection):
        cursor = db.cursor()
        # Giữ nguyên câu lệnh STUFF FOR XML PATH cực hay của bạn cho SQL Server
        sql = """
            SELECT e.ID, e.FullName, 
            STUFF((SELECT ', ' + d.DeptName 
                   FROM EmployeeViewRights evr 
                   JOIN Departments d ON evr.DeptID = d.DeptID 
                   WHERE evr.EmployeeID = e.ID 
                   FOR XML PATH('')), 1, 2, '') AS ViewDepts
            FROM Employees e
        """
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def get_view_rights_by_emp(db: Connection, emp_id: int):
        cursor = db.cursor()
        cursor.execute("SELECT DeptID FROM EmployeeViewRights WHERE EmployeeID = ?", (emp_id,))
        return [row[0] for row in cursor.fetchall()] 

    @staticmethod
    def save_view_rights(db: Connection, emp_id: int, dept_ids: List[int]):
        cursor = db.cursor()
        try:
            # 1. Xóa toàn bộ quyền cũ
            cursor.execute("DELETE FROM EmployeeViewRights WHERE EmployeeID = ?", (emp_id,))
            
            # 2. Thêm mới hàng loạt (Bulk Insert)
            if dept_ids:
                params = [(emp_id, d_id) for d_id in dept_ids]
                cursor.executemany("INSERT INTO EmployeeViewRights (EmployeeID, DeptID) VALUES (?, ?)", params)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
