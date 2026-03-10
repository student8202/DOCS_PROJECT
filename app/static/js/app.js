$(document).ready(function () {
    // Hiển thị tên người dùng trên Header
    const fullName = localStorage.getItem('full_name');
    if (fullName) {
        $('#user_display_name').text(fullName);
    }

    // Cập nhật năm ở Footer
    $('#footer_year').text(new Date().getFullYear());
});

// Hàm xử lý 3 nút Smart Sync (FO, BO, HR)
async function handleSync(type) {
    const result = await Swal.fire({
        title: `Đồng bộ SMILE_${type}?`,
        text: `Hệ thống sẽ cập nhật nhân sự từ nguồn này vào LV_DOCS.`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Bắt đầu',
        cancelButtonText: 'Hủy'
    });

    if (result.isConfirmed) {
        Swal.fire({ 
            title: 'Đang đồng bộ...', 
            allowOutsideClick: false, 
            didOpen: () => { Swal.showLoading(); } 
        });

        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`/auth/sync/${type}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await response.json();

            if (response.ok) {
                Swal.fire('Thành công', data.message, 'success');
            } else {
                Swal.fire('Thất bại', data.detail || 'Lỗi xử lý', 'error');
            }
        } catch (err) {
            Swal.fire('Lỗi', 'Không thể kết nối API', 'error');
        }
    }
}
