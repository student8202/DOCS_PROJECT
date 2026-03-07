// Functions for Department
function openDeptModal() {
    $('#deptId').val(''); $('#deptModal').modal('show');
    applyLanguage(); // Đảm bảo các label trong Modal được dịch
}
function saveDept() {
    $.ajax({
        url: '/departments/api/save', type: 'POST', contentType: 'application/json',
        data: JSON.stringify({ DeptName: $('#deptName').val() }),
        success: () => { $('#deptModal').modal('hide'); deptTable.ajax.reload(); loadDeptsToDropdown(); }
    });
}
// function delDept(id) {
//     if (confirm('Xóa?')) $.ajax({ url: `/departments/api/delete/${id}`, type: 'DELETE', success: () => deptTable.ajax.reload() });
// }
function delDept(row) {
    Swal.fire({
        title: 'Xác nhận xóa bộ phận?',
        html: `Bạn muốn xóa bộ phận: <b>${row.DeptName}</b>?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        confirmButtonText: 'Đồng ý xóa',
        cancelButtonText: 'Hủy'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: `/departments/api/delete/${row.DeptID}`,
                type: 'DELETE',
                success: function (response) {
                    deptTable.ajax.reload();
                    loadDeptsToDropdown();
                    Swal.fire({
                        title: 'Đã xóa!',
                        text: response.message,
                        icon: 'success',
                        timer: 2000, // <--- Tự đóng sau 2000ms
                        timerProgressBar: true, // Hiện thanh đếm ngược cho đẹp
                        showConfirmButton: true // Ẩn nút "OK" vì nó tự đóng rồi
                    }) 
                },
                error: function (xhr) {
                    // Lấy tin nhắn lỗi từ server (Ví dụ: "Không thể xóa! Đang có 5 nhân viên...")
                    const errorMsg = xhr.responseJSON ? xhr.responseJSON.detail.message : 'Lỗi hệ thống!';
                    Swal.fire({
                        title: 'Cảnh báo!',
                        text: errorMsg,
                        icon: 'error',
                        confirmButtonColor: '#3085d6'
                    });
                }
            });
        }
    });
}
// cập nhật
function editDept(row) {
    $('#deptId').val(row.DeptID); // Gán ID vào hidden input
    $('#deptName').val(row.DeptName);
    $('#deptModal').modal('show');
}

function saveDept() {
    const rawId = $('#deptId').val();
    const data = {
        // Nếu ID rỗng (thêm mới) thì gửi 0, nếu có thì ép kiểu sang số nguyên
        DeptID: rawId ? parseInt(rawId) : 0, 
        DeptName: $('#deptName').val().trim()
    };

    if (!data.DeptName) {
        Swal.fire('!', t('please_enter_name'), 'warning');
        return;
    }

    $.ajax({
        url: '/departments/api/save',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function (res) {
            $('#deptModal').modal('hide');
            deptTable.ajax.reload();
            loadDeptsToDropdown(); // Cập nhật dropdown bên tab nhân viên
            console.log(res)
            Swal.fire({
                        title: 'Đã Lưu!',
                        text: t(res.message),
                        icon: 'success',
                        timer: 2000, // <--- Tự đóng sau 2000ms
                        timerProgressBar: true, // Hiện thanh đếm ngược cho đẹp
                        showConfirmButton: true // Ẩn nút "OK" vì nó tự đóng rồi
                    }) 
        },
        error: function (xhr) {
            // Lấy mã lỗi (ví dụ: 'err_dept_exists') và dịch qua hàm t()
            const errorKey = xhr.responseJSON ? xhr.responseJSON.detail.message : t('err_dept_exists');
            Swal.fire(t(errorKey), '', 'error');
        }
    });
}