SELECT Username, Password_Hash, IsActive, FullName FROM dbo.tbl_Users WHERE Username ='admin'

UPDATE dbo.tbl_Users 
SET Password_Hash = '$2b$12$rf1QMKqXMU76UB5L3dq2QOC3U4lC7EQ8DBswp6adC5gYuvuUUyIFW' 
WHERE Username = 'admin';

SELECT * FROM dbo.tbl_Users WHERE Username = 'sml'

delete tbl_Users WHERE Username <> 'admin'

SELECT * FROM dbo.tbl_PermissionList
SELECT * FROM dbo.tbl_RolePermissions
SELECT * FROM dbo.tbl_Roles

INSERT INTO dbo.tbl_PermissionList (PermissionCode, PermissionName, ModuleName, CreatedBy)
VALUES 
('admin', N'Quản trị', 'FO,POS,HR', 'SYSTEM')

INSERT INTO dbo.tbl_Roles (RoleCode, RoleName, CreatedBy)
VALUES ('ADMIN', N'Quản trị hệ thống', 'SYSTEM');

INSERT INTO dbo.tbl_RolePermissions (RoleCode, PermissionCode, CreatedBy)
SELECT 'ADMIN', PermissionCode, 'SYSTEM' FROM dbo.tbl_PermissionList;

INSERT INTO tbl_RolePermissions ([RoleCode], [PermissionCode], [CreatedBy], [CreatedAt], [UpdatedBy], [UpdatedAt])
VALUES
( N'ADMIN', N'admin', N'SYSTEM', N'2026-03-10T21:25:08.833', NULL, NULL )

SELECT DISTINCT PermissionCode 
                FROM dbo.tbl_RolePermissions 
                WHERE RoleCode IN (SELECT RoleCode FROM dbo.tbl_UserRoles WHERE Username = 'admin')