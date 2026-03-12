$(document).ready(function () {
    const loginForm = $('#loginForm');
    if (loginForm.length > 0) {
        loginForm.on('submit', async function (e) {
            e.preventDefault();
            const $btn = $('#btnLogin');
            const $alert = $('#loginAlert');

            $btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2"></span>Đang kiểm tra...');
            $alert.addClass('d-none');

            const formData = new FormData(this);

            try {
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (response.ok) {
                    localStorage.setItem('access_token', result.access_token);
                    localStorage.setItem('username', result.username);
                    localStorage.setItem('full_name', result.full_name);

                    Swal.fire({
                        icon: 'success',
                        title: 'Thành công',
                        text: `Chào mừng ${result.full_name}`,
                        timer: 1000,
                        showConfirmButton: false
                    }).then(() => {
                        window.location.href = '/dashboard';
                    });
                } else {
                    $alert.text(result.detail || 'Lỗi xác thực').removeClass('d-none');
                    $btn.prop('disabled', false).text('ĐĂNG NHẬP');
                }
            } catch (err) {
                $alert.text('Lỗi kết nối máy chủ').removeClass('d-none');
                $btn.prop('disabled', false).text('ĐĂNG NHẬP');
            }
        });
    }
});

// Hàm đăng xuất dùng chung
// Thêm async ở đầu hàm
async function logout() {
    // Chờ người dùng nhấn xác nhận từ SweetAlert2
    const result = await Swal.fire({
        title: 'Đăng xuất?',
        text: "Bạn muốn thoát khỏi LaVie Project?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3c4b64',
        confirmButtonText: 'Đồng ý',
        cancelButtonText: 'Hủy'
    });

    // Nếu người dùng đồng ý
    if (result.isConfirmed) {
        try {
            // 1. Gọi Server xóa Session (Bắt buộc để xóa thẻ bài ở Backend)
            await fetch('/auth/logout', { method: 'POST' });

            // 2. Xóa dữ liệu ở trình duyệt
            localStorage.clear();

            // 3. Chuyển về trang chủ
            window.location.href = '/';
        } catch (error) {
            console.error("Lỗi đăng xuất:", error);
            // Vẫn cho về trang chủ nếu lỗi mạng để đảm bảo thoát được giao diện
            window.location.href = '/';
        }
    }
}
