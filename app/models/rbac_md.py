class RBACModel:
    TBL_USERS = "dbo.tbl_Users"
    TBL_USER_ROLES = "dbo.tbl_UserRoles"
    TBL_ROLE_PERMS = "dbo.tbl_RolePermissions"
    TBL_PERMISSIONS = "dbo.tbl_PermissionList"
    
    # Định nghĩa các hằng số quyền bằng chữ thường
    PERM_VIEW_FO = "view_fo"
    PERM_SIGN_FO = "sign_fo"
    PERM_VIEW_HR = "view_hr"
    PERM_ADMIN   = "admin"