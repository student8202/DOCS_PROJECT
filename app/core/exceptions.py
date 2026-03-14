class LaVieError(Exception):
    """Lỗi cơ sở cho dự án LaVie"""
    def __init__(self, message: str):
        self.message = message

class RoleAlreadyAssignedError(LaVieError):
    """Lỗi khi gán trùng Role đã có"""
    pass

class UserNotFoundError(LaVieError):
    """Lỗi không tìm thấy User trong hệ thống"""
    pass

class DuplicateError(LaVieError):
    """Lỗi khi dữ liệu (Username, RoleCode, PermissionCode) đã tồn tại"""
    pass

class DatabaseError(LaVieError):
    """Lỗi kết nối hoặc thao tác Database thất bại"""
    pass