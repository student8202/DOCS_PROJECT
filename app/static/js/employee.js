// Functions for Employee
function openEmpModal() {
    $('#empId').val(''); $('#empModal').modal('show');
    applyLanguage(); // Đảm bảo các label trong Modal được dịch
}
function saveEmp() {
    $.ajax({
        url: '/employees/api/save', type: 'POST', contentType: 'application/json',
        data: JSON.stringify({ FullName: $('#empName').val(), IdDepartment: $('#empDeptSelect').val() }),
        success: () => { $('#empModal').modal('hide'); empTable.ajax.reload(); Swal.fire('Xong!', '', 'success'); }
    });
}
function delEmp(id) {
    if (confirm('Xóa?')) $.ajax({ url: `/employees/api/delete/${id}`, type: 'DELETE', success: () => empTable.ajax.reload() });
}
function delEmp(row) {
    Swal.fire({
        title: t('confirm_delete'),
        html: t('confirm_delete_emp', { name: row.FullName }),
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        confirmButtonText: t('btn_yes'),
        cancelButtonText: t('btn_cancel'),
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: `/employees/api/delete/${row.ID}`,
                type: 'DELETE',
                success: function () {
                    // Reload và giữ nguyên paging (false)
                    empTable.ajax.reload(function (json) {
                        const info = empTable.page.info();
                        // Nếu trang hiện tại không còn dòng nào (do vừa xóa dòng cuối của trang)
                        // và chúng ta không ở trang đầu tiên (info.page > 0)
                        if (info.recordsDisplay > 0 && info.start >= info.recordsDisplay && info.page > 0) {
                            empTable.page('previous').draw('page');
                        }
                    }, false);
                    Swal.fire('Đã xóa!', `Nhân viên <b>${row.FullName}</b> đã bị xóa.`, 'success');
                },
                error: () => Swal.fire('Lỗi', 'Không thể xóa dữ liệu', 'error')
            });
        }
    });
}
// --- HÀM XỬ LÝ SỬA (EDIT) ---

function editEmp(row) {
    $('#empId').val(row.ID); // Gán ID vào hidden input
    $('#empName').val(row.FullName);
    // Cập nhật Select2
    $('#empDeptSelect').val(row.IdDepartment).trigger('change');
    $('#empModal').modal('show');
}

// --- CẬP NHẬT HÀM SAVE (Để gửi cả ID khi sửa) ---

function saveEmp() {
    // 1. Lấy dữ liệu từ Form
    const empId = $('#empId').val();
    const payload = {
        // Ép kiểu ID về số nguyên, nếu rỗng thì để là 0 hoặc null
        ID: empId ? parseInt(empId) : 0,
        FullName: $('#empName').val().trim(),
        IdDepartment: parseInt($('#empDeptSelect').val())
    };

    // 2. Kiểm tra dữ liệu (Validate)
    if (!payload.FullName) {
        Swal.fire(t('msg_err') || 'Lỗi!', t('err_name_empty') || 'Vui lòng nhập họ tên', 'error');
        return;
    }
    if (!payload.IdDepartment) {
        Swal.fire(t('msg_err') || 'Lỗi!', t('err_dept_empty') || 'Vui lòng chọn bộ phận', 'error');
        return;
    }

    $.ajax({
        url: '/employees/api/save',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(payload),
        success: function (response) {
            // Ưu tiên lấy ID từ response (thêm mới), nếu không có thì lấy từ biến empId (sửa)
            const targetId = response.id || $('#empId').val();

            $('#empModal').modal('hide');

            // Reload bảng và thực hiện callback
            empTable.ajax.reload(function () {
                if (targetId) {
                    // 1. Tìm index của dòng dựa trên ID trong toàn bộ dữ liệu
                    let foundIndex = -1;
                    empTable.rows().every(function (idx) {
                        if (Number(this.data().ID) === Number(targetId)) {
                            foundIndex = idx;
                            return false; // Dừng vòng lặp khi tìm thấy
                        }
                    });

                    // 2. Nếu tìm thấy dòng (index >= 0)
                    if (foundIndex !== -1) {
                        const pageInfo = empTable.page.info();

                        // 3. Tính toán trang và nhảy đến trang đó
                        const pageToJump = Math.floor(foundIndex / pageInfo.length);
                        empTable.page(pageToJump).draw(false);

                        // 4. Đợi DOM render rồi mới Scroll và Highlight
                        setTimeout(() => {
                            const rowNode = empTable.row(foundIndex).node();
                            if (rowNode) {
                                rowNode.scrollIntoView({ behavior: 'smooth', block: 'center' });

                                $(rowNode).addClass('table-success');
                                setTimeout(() => $(rowNode).removeClass('table-success'), 2000);
                            }
                        }, 300);
                    }
                }
            }, false); // Quan trọng: false để không reset về trang 1 ngay lập tức

            Swal.fire(t('msg_success') || 'Thành công!', t('save_success') || 'Dữ liệu đã được cập nhật', 'success');
        },
        error: function (err) {
            // Hiển thị chi tiết lỗi 422 từ FastAPI
            const errorDetail = err.responseJSON?.detail;
            const msg = typeof errorDetail === 'object' ? JSON.stringify(errorDetail) : errorDetail;
            Swal.fire('Lỗi dữ liệu', msg || 'Lỗi kết nối server', 'error');
        }
    });
}
// -----------------------
// --- HÀM TẢI FILE MẪU (TEMPLATE) ---
function downloadEmpTemplate() {
    // Chuyển hướng trực tiếp để trình duyệt tự tải file về
    window.location.href = '/employees/api/template';
}

// --- HÀM XUẤT EXCEL (EXPORT) ---
function exportEmpExcel() {
    Swal.fire({
        title: 'Đang chuẩn bị dữ liệu...',
        allowOutsideClick: false,
        didOpen: () => { Swal.showLoading(); }
    });

    // Tải file về
    window.location.href = '/employees/api/export';

    // Đóng loading sau 1 giây
    setTimeout(() => { Swal.close(); }, 1500);
}

// --- HÀM NHẬP EXCEL (IMPORT) ---
function handleImportEmp(input) {
    const file = input.files[0];
    if (!file) return;

    // Kiểm tra định dạng file nhanh ở client
    const ext = file.name.split('.').pop().toLowerCase();
    if (ext !== 'xlsx' && ext !== 'xls') {
        Swal.fire('Lỗi', 'Vui lòng chọn file Excel (.xlsx hoặc .xls)', 'error');
        input.value = '';
        return;
    }

    Swal.fire({
        title: 'Đang xử lý dữ liệu...',
        text: 'Vui lòng chờ trong giây lát',
        allowOutsideClick: false,
        didOpen: () => { Swal.showLoading(); }
    });

    const formData = new FormData();
    formData.append('file', file);

    $.ajax({
        url: '/employees/api/import',
        type: 'POST',
        data: formData,
        processData: false, // Quan trọng: không xử lý dữ liệu
        contentType: false, // Quan trọng: không set contentType mặc định
        success: function (response) {
            input.value = ''; // Reset input để có thể chọn lại file cũ nếu muốn
            empTable.ajax.reload(); // Load lại DataTables
            Swal.fire('Thành công!', response.message, 'success');
        },
        error: function (xhr) {
            input.value = '';
            const msg = xhr.responseJSON ? xhr.responseJSON.error : 'Lỗi kết nối server';
            Swal.fire('Thất bại', msg, 'error');
        }
    });
}