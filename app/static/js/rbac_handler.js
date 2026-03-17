$(document).ready(function () {
    // Khởi tạo bảng danh sách nhân sự
    $('#tblUsers').DataTable({
        responsive: true,
        ajax: {
            url: '/rbac/users-roles-data', // Gọi API Controller trả về JSON
            dataSrc: ''
        },
        columns: [
            {
                data: 'Username',
                render: function (data) {
                    return `<input type="checkbox" class="user-checkbox" value="${data}">`;
                }
            },
            { data: 'Username' },
            { data: 'FullName' },
            { data: 'Roles' },
            {
                data: 'Username', // Dùng Username để biết đang gán quyền cho ai
                className: 'text-center', // Căn giữa nút bấm cho đẹp
                render: function (data) {
                    // Trả về đoạn mã HTML của nút "Gán quyền"
                    // Khi nhấn nút này, nó sẽ gọi hàm showAssignRole('tên_user')
                    return `
            <button class="btn btn-sm btn-outline-primary fw-bold" onclick="showAssignRole('${data}')">
                <i class="fas fa-user-edit me-1"></i> Gán quyền
            </button>
            <button class="btn btn-sm btn-outline-warning fw-bold ms-1" onclick="openAdminResetPass('${data}')" title="Đặt lại mật khẩu">
                <i class="fas fa-key"></i> Reset password
            </button>
        `;
                }
            }
        ],
        // BƯỚC 1: TẮT SORT CHO CỘT ĐẦU TIÊN
        columnDefs: [{
            targets: 0,
            orderable: false,
            searchable: false,
            className: 'dt-center', // Ép căn giữa bằng class chuẩn
            width: '40px'
        },
        {
            targets: 4, // Cột Thao tác cũng nên căn giữa cho đẹp
            className: 'dt-center'
        }
        ],
        order: [[1, 'asc']], // Luôn mặc định sắp xếp theo cột Username (Cột 1)
        language: {
        //     url: '/static/js/languages.json' // Để hiện tiếng Việt nếu bạn đã có file này
        }
    });

    // XỬ LÝ NÚT CHECK ALL (Chặn sự kiện nổi bọt)
    $('#checkAll').on('click', function (e) {
        // Ngăn click checkbox kích hoạt sắp xếp cột của DataTable
        e.stopPropagation();

        const isChecked = this.checked;
        $('.user-checkbox').prop('checked', isChecked);
    });
});

// Hàm mở Modal gán quyền cho từng User
async function showAssignRole(username) {
    // 1. Đưa tên User vào tiêu đề
    $('#targetUser').text(username);
    
    // 2. ÉP NÚT LƯU LUÔN GỌI saveUserRoles
    $('#btnSaveRole').attr('onclick', 'saveUserRoles()');

    $('#modalRole').modal('show');
    $('#roleListContainer').html('<div class="text-center py-3"><div class="spinner-border text-primary"></div></div>');

    // Đổi thuộc tính nút Lưu để biết là đang lưu 1 user
    $('#modalRole .btn-primary').attr('onclick', 'saveUserRoles()');

    // 3. Gọi API lấy HTML (Fragment)
    const response = await fetch(`/rbac/user-role-config-html/${username}`);
    const html = await response.text();
    $('#roleListContainer').html(html);
}

// Hàm lưu dữ liệu gán quyền (Xóa cũ - Ghi mới)
async function saveUserRoles() {
    const titleText = $('#targetUser').text().trim();
    // Kiểm tra xem tiêu đề có chữ "nhân viên đã chọn" không
    const isBulk = titleText.includes("nhân viên đã chọn");
    
    const selectedRoles = [];
    // Quét tất cả checkbox TRONG MODAL
    $('#modalRole input.chk-user-role:checked').each(function () {
        selectedRoles.push($(this).val());
    });

    // --- LOGIC BẠN CẦN ---
    if (isBulk && selectedRoles.length === 0) {
        Swal.fire('Chú ý', 'Khi gán hàng loạt, bạn phải chọn ít nhất 1 vai trò!', 'warning');
        return;
    }
    // Nếu không phải Bulk (gán 1 người), mảng rỗng [] vẫn cho qua

    Swal.fire({ title: 'Đang lưu...', allowOutsideClick: false, didOpen: () => { Swal.showLoading(); } });

    // Xác định dữ liệu và URL
    let payload = {};
    let url = isBulk ? '/rbac/users/bulk-save-roles' : '/rbac/users/save-roles';

    if (isBulk) {
        const selectedUsers = [];
        $('.user-checkbox:checked').each(function() { selectedUsers.push($(this).val()); });
        payload = { usernames: selectedUsers, role_codes: selectedRoles };
    } else {
        payload = { username: titleText, role_codes: selectedRoles };
    }

    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res.ok) {
        Swal.fire('Thành công', 'Đã cập nhật quyền!', 'success');
        $('#modalRole').modal('hide');
        $('#tblUsers').DataTable().ajax.reload(null, false);
        $('.user-checkbox, #checkAll').prop('checked', false);
        $('#bulkActionArea').fadeOut();
    } else {
        const err = await res.json();
        Swal.fire('Lỗi', err.detail, 'error');
    }
}


// Hàm xử lý nhấn nút "Gán quyền hàng loạt" (Nút này bạn đặt trên đầu bảng)
async function showBulkAssignRole() {
    const selectedUsers = [];
    $('.user-checkbox:checked').each(function () {
        selectedUsers.push($(this).val());
    });

    if (selectedUsers.length === 0) {
        Swal.fire('Chú ý', 'Vui lòng chọn ít nhất một nhân viên!', 'warning');
        return;
    }

    // 1. Đưa thông báo số lượng vào tiêu đề để hàm Lưu biết là đang gán hàng loạt
    $('#targetUser').text(`${selectedUsers.length} nhân viên đã chọn`);
    
    // 2. VẪN GỌI saveUserRoles (Không gọi hàm Bulk nữa)
    $('#btnSaveRole').attr('onclick', 'saveUserRoles()');

    $('#modalRole').modal('show');
    $('#roleListContainer').html('<div class="text-center py-3"><div class="spinner-border text-primary"></div></div>');

    // 3. Gọi API lấy HTML trắng (hoặc của người đầu tiên) để hiện danh sách Role
    const response = await fetch(`/rbac/user-role-config-html/dummy`); // Hoặc một user mẫu
    const html = await response.text();
    $('#roleListContainer').html(html);
}


// gán quyền hàng loạt
$('#tblUsers tbody').on('change', '.user-checkbox', function () {
    updateBulkButton();
});

$('#checkAll').on('change', function () {
    updateBulkButton();
});

function updateBulkButton() {
    const selectedCount = $('.user-checkbox:checked').length;
    if (selectedCount > 0) {
        $('#selectedCount').text(selectedCount);
        $('#bulkActionArea').fadeIn();
    } else {
        $('#bulkActionArea').fadeOut();
    }
}

// Hàm mở Modal gán quyền hàng loạt
async function openBulkRoleModal() {
    const selectedUsers = [];
    $('.user-checkbox:checked').each(function () {
        selectedUsers.push($(this).val());
    });

    // Tận dụng lại cái Modal cũ nhưng đổi tiêu đề
    $('#targetUser').text(selectedUsers.length + " nhân viên đã chọn");
    $('#modalRole').modal('show');

    // Đổi lệnh onclick của nút Lưu trong Modal thành hàm lưu hàng loạt
    $('#modalRole .btn-primary').attr('onclick', 'saveBulkUserRoles()');

    // Load danh sách Role (giống hàm đơn lẻ)
    const res = await fetch('/rbac/roles-list');
    const roles = await res.json();
    let html = '';
    roles.forEach(r => {
        html += `
            <div class="form-check p-2 border rounded-2 mb-2">
                <input class="form-check-input ms-1 chk-bulk-role" type="checkbox" value="${r.RoleCode}" id="br_${r.RoleCode}">
                <label class="form-check-label ms-3 fw-bold" for="br_${r.RoleCode}">${r.RoleName}</label>
            </div>`;
    });
    $('#roleListContainer').html(html);
}

async function saveBulkUserRoles() {
    const selectedUsers = [];
    $('.user-checkbox:checked').each(function () { selectedUsers.push($(this).val()); });

    const selectedRoles = [];
    $('.chk-bulk-role:checked').each(function () { selectedRoles.push($(this).val()); });

    if (selectedRoles.length === 0) {
        Swal.fire('Chú ý', 'Vui lòng chọn ít nhất một vai trò!', 'warning');
        return;
    }

    const res = await fetch('/rbac/users/bulk-save-roles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            usernames: selectedUsers,
            role_codes: selectedRoles
        })
    });

    if (res.ok) {
        Swal.fire('Thành công', 'Đã cập nhật quyền!', 'success');
        $('#modalRole').modal('hide');

        // --- BƯỚC QUAN TRỌNG: RESET TRẠNG THÁI ---
        // 1. Bỏ tích nút CheckAll trên đầu bảng
        $('#checkAll').prop('checked', false);

        // 2. Ẩn nút "Gán quyền hàng loạt" (nếu có)
        $('#bulkActionArea').fadeOut();

        // 3. Tải lại dữ liệu mới từ Server
        $('#tblUsers').DataTable().ajax.reload(null, false);
        // null, false: Giúp giữ nguyên trang (pagination) đang xem
    }
}
// ADMIN RESET PASS
function openAdminResetPass(username) {
    $('#resetTargetUser').text(username);
    $('#admin_new_pass').val('');
    $('#modalAdminResetPass').modal('show');
}

async function submitAdminResetPass() {
    const username = $('#resetTargetUser').text();
    const newPass = $('#admin_new_pass').val();

    if (newPass.length < 6) {
        Swal.fire('Chú ý', 'Mật khẩu phải từ 6 ký tự trở lên', 'warning');
        return;
    }

    const res = await fetch('/rbac/users/admin-reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username, new_password: newPass })
    });

    if (res.ok) {
        Swal.fire('Thành công', 'Mật khẩu đã được đặt lại!', 'success');
        $('#modalAdminResetPass').modal('hide');
    }
}