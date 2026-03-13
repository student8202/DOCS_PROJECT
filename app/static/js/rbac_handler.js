async function openRoleModal(username) {
    $('#targetUser').text(username);
    // 1. Load danh sách Roles từ API rbac/roles-list
    const res = await fetch('/rbac/roles-list');
    const roles = await res.json();
    
    let html = '';
    roles.forEach(r => {
        html += `<div class="form-check">
            <input class="form-check-input" type="checkbox" value="${r.RoleCode}" id="${r.RoleCode}">
            <label class="form-check-label">${r.RoleName}</label>
        </div>`;
    });
    $('#roleCheckboxGroup').html(html);
    $('#roleModal').modal('show');
}

async function saveRoles() {
    const username = $('#targetUser').text();
    const selectedRoles = [];
    $('#roleCheckboxGroup input:checked').each(function() {
        selectedRoles.push($(this).val());
    });

    const res = await fetch('/rbac/update-roles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username, role_codes: selectedRoles })
    });

    if (res.ok) {
        Swal.fire('Thành công', 'Đã cập nhật quyền!', 'success');
        $('#roleModal').modal('hide');
    }
}
