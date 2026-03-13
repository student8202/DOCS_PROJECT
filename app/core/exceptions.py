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