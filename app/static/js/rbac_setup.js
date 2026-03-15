$(document).ready(function () {
    // 1. Load Bảng Quyền (Permissions)
    $('#tblPermissions').DataTable({
        ajax: {
            url: '/rbac/permissions-list',
            dataSrc: ''
        },
        columns: [
            { data: 'PermissionCode' },
            { data: 'PermissionName' },
            { data: 'ModuleName' }
        ],
        language: { url: '/static/js/languages.json' } // Nếu bạn có file ngôn ngữ tiếng Việt
    });

    $('#tblRoles').DataTable({
        ajax: {
            url: '/rbac/roles-list',
            dataSrc: ''
        },
        columns: [
            { data: 'RoleCode' },
            { data: 'RoleName' },
            { data: 'ModuleName' }, // Cột số 2 (index từ 0) - Đây là nơi gây lỗi nếu Backend ko trả về
            {
                data: 'RoleCode', // Cột số 3 (Thao tác)
                className: 'text-center',
                render: function (data) {
                    // ĐÂY LÀ NÚT RĂNG CƯA (Icon cog) để bạn nhấn vào cấu hình quyền
                    return `<button class="btn btn-sm btn-outline-warning" onclick="openConfigRole('${data}')" title="Cấu hình quyền">
                            <i class="fas fa-cog"></i>
                        </button>`;
                }
            }
        ]
    });
});

// Permission List
async function openAddPermModal() {
    $('#modalAddPerm').modal('show');
}

$('#formAddPerm').on('submit', async function (e) {
    e.preventDefault();
    const formData = new Object();
    $(this).serializeArray().forEach(item => formData[item.name] = item.value);

    const res = await fetch('/rbac/permissions/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    });

    if (res.ok) {
        Swal.fire('Thành công', 'Đã thêm quyền mới vào di sản!', 'success');
        $('#modalAddPerm').modal('hide');
        // Reload lại bảng Permissions...
        // 2. Reset Form để lần sau mở ra nó trắng tinh
        $(this).trigger("reset");

        // 3. LỆNH QUAN TRỌNG: Reload dữ liệu bảng mà không load lại trang
        $('#tblPermissions').DataTable().ajax.reload();
    } else {
        const error = await res.json();
        Swal.fire('Lỗi', error.detail, 'error');
    }
});

// Role List

// --- PHẦN XỬ LÝ ROLE ---
async function openAddRoleModal() {
    $('#modalAddRole').modal('show');
}

// Sửa ID Form thành #formAddRole để không bị trùng với Permission
$('#formAddRole').on('submit', async function (e) {
    e.preventDefault();
    const formData = {};
    $(this).serializeArray().forEach(item => formData[item.name] = item.value);

    const res = await fetch('/rbac/roles/add', { // Sửa API endpoint đúng cho Role
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    });

    if (res.ok) {
        Swal.fire('Thành công', 'Đã thêm vai trò mới!', 'success');
        $('#modalAddRole').modal('hide');
        $(this).trigger("reset");
        $('#tblRoles').DataTable().ajax.reload();
    } else {
        const error = await res.json();
        Swal.fire('Lỗi', error.detail, 'error');
    }
});
// phần cấu hình quyền cho role
// 1. Hàm mở Modal và load dữ liệu (Lọc theo Module từ Backend)
async function openConfigRole(roleCode) {
    $('#configRoleTitle').text(roleCode);
    $('#modalConfigRole').modal('show');
    
    // JS chỉ việc "đi lấy mẩu HTML" đã nấu sẵn về và dán vào
    const response = await fetch(`/rbac/role-config-html/${roleCode}`);
    const html = await response.text();
    
    $('#permCheckboxContainer').html(html);
}

// 2. Hàm lưu dữ liệu (Xóa cũ - Ghi mới)
async function saveRoleMapping() {
    const roleCode = $('#configRoleTitle').text();
    const selectedPerms = [];
    
    // Thu thập tất cả các quyền đã được tích
    $('.chk-role-perm:checked').each(function() {
        selectedPerms.push($(this).val());
    });

    const res = await fetch('/rbac/roles/save-permissions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            role_code: roleCode, 
            permission_codes: selectedPerms 
        })
    });

    if (res.ok) {
        Swal.fire('Thành công', `Đã cập nhật quyền cho nhóm ${roleCode}!`, 'success');
        $('#modalConfigRole').modal('hide');
    } else {
        Swal.fire('Lỗi', 'Không thể lưu cấu hình quyền', 'error');
    }
}
