# app/models/rbac_md.py

class RBACModel:
    # Tên các bảng
    TABLE_USERS = "dbo.tbl_Users"
    TABLE_ROLES = "dbo.tbl_Roles"
    TABLE_USER_ROLES = "dbo.tbl_UserRoles"
    TABLE_PERMISSION_LIST = "dbo.tbl_PermissionList"
    TABLE_ROLE_PERMISSIONS = "dbo.tbl_RolePermissions"

    # Định nghĩa hằng số Quyền
    PERM_ADMIN = "admin"
    PERM_VIEW_FO = "view_fo"
    PERM_SIGN_FO = "sign_fo"
    PERM_VIEW_HR = "view_hr"

    # --- SQL COMMANDS ---
    # Lấy danh sách Permission
    SQL_SELECT_PERMISSIONS = f"SELECT PermissionCode, PermissionName, ModuleName FROM {TABLE_PERMISSION_LIST}"
    SQL_SELECT_ROLES = f"SELECT RoleCode, RoleName,ModuleName,Description FROM {TABLE_ROLES}"
    
    # Thêm mới Permission
    SQL_INSERT_PERMISSION = f"INSERT INTO {TABLE_PERMISSION_LIST} (PermissionCode, PermissionName, ModuleName, CreatedBy) VALUES (?, ?, ?, ?)"
    
    # Cập nhật INSERT thêm ModuleName
    SQL_INSERT_ROLE = f"""
        INSERT INTO dbo.tbl_Roles (RoleCode, RoleName, ModuleName, Description, CreatedBy, CreatedAt)
        VALUES (?, ?, ?, ?, ?, GETDATE())
    """
    #########################
     # SQL lấy danh sách mã quyền (PermissionCode) mà một Role đang sở hữu
    SQL_GET_PERMISSIONS_BY_ROLE = f"""
        SELECT PermissionCode 
        FROM {TABLE_ROLE_PERMISSIONS} 
        WHERE RoleCode = ?
    """

    # SQL xóa sạch quyền cũ của Role (chuẩn bị cho việc ghi đè mới - Sync)
    SQL_DELETE_ROLE_MAPPING = f"""
        DELETE FROM {TABLE_ROLE_PERMISSIONS} 
        WHERE RoleCode = ?
    """

    # SQL thêm một bản ghi Mapping mới
    SQL_INSERT_ROLE_MAPPING = f"""
        INSERT INTO {TABLE_ROLE_PERMISSIONS} (RoleCode, PermissionCode, CreatedBy, CreatedAt)
        VALUES (?, ?, ?, GETDATE())
    """
    ## phân quyền role cho users
    # SQL lấy User kèm chuỗi Role (ngăn cách bởi dấu phẩy)
    SQL_GET_USERS_WITH_ROLES = """
        SELECT u.Username, u.FullName, u.Department, u.IsActive,
               ISNULL(STRING_AGG(ur.RoleCode, ', '), '') as Roles
        FROM dbo.tbl_Users u
        LEFT JOIN dbo.tbl_UserRoles ur ON u.Username = ur.Username
        GROUP BY u.Username, u.FullName, u.Department, u.IsActive
    """
    # SQL lấy danh sách RoleCode mà một User đang có
    SQL_GET_ROLES_BY_USER = f"SELECT RoleCode FROM {TABLE_USER_ROLES} WHERE Username = ?"

    # SQL xóa sạch Role cũ của User (Cơ chế Sync)
    SQL_DELETE_USER_ROLES = f"DELETE FROM {TABLE_USER_ROLES} WHERE Username = ?"

    # SQL gán một Role mới cho User
    SQL_INSERT_USER_ROLE = f"""
        INSERT INTO {TABLE_USER_ROLES} (Username, RoleCode, CreatedBy, CreatedAt)
        VALUES (?, ?, ?, GETDATE())
    """
    SQL_GET_ROLES_WITH_PERMS = """
        SELECT r.RoleCode, r.RoleName, r.ModuleName,
               ISNULL(STRING_AGG('[' + p.PermissionCode + '] ' + p.PermissionName, ' | '), 'N/A') as PermList
        FROM dbo.tbl_Roles r
        LEFT JOIN dbo.tbl_RolePermissions rp ON r.RoleCode = rp.RoleCode
        LEFT JOIN dbo.tbl_PermissionList p ON rp.PermissionCode = p.PermissionCode
        GROUP BY r.RoleCode, r.RoleName, r.ModuleName
        ORDER BY r.ModuleName, r.RoleName
    """
    