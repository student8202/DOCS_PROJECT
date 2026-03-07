from pyodbc import Connection
from crud.department_crud import DepartmentCRUD
from schemas.department import DepartmentSaveRequest
from loguru import logger

class DepartmentService:
    @staticmethod
    def save(db: Connection, data: DepartmentSaveRequest):
        dept_name = data.DeptName.strip()
        dept_id = data.DeptID

        # Logic 1: Kiểm tra trùng tên
        if DepartmentCRUD.check_exists_name(db, dept_name, dept_id):
            return False, "Tên phòng ban đã tồn tại!"

        # Logic 2: Thực hiện lưu
        try:
            if dept_id:
                DepartmentCRUD.update(db, dept_id, dept_name)
            else:
                DepartmentCRUD.insert(db, dept_name)
            db.commit()
            return True, "Lưu thành công"
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def delete(db: Connection, dept_id: int):
        logger.info(f"Đang xử lý: {dept_id}")
        # Lấy kết quả từ CRUD
        emp_count = DepartmentCRUD.check_employee_relation(db, dept_id)    
        logger.info(f"Employee count: {emp_count}")
        if emp_count > 0:
            return False, f"Không thể xóa! Đang có {emp_count} nhân viên thuộc bộ phận này."
        
        # Logic 2: Thực hiện xóa
        try:
            DepartmentCRUD.delete(db, dept_id)
            db.commit()
            return True, "Xóa bộ phận thành công."
        except Exception as e:
            db.rollback()
            raise e
