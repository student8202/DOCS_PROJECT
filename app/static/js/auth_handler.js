const Auth = {
    // --- HÀM ĐĂNG NHẬP (Chuyển từ login.html sang đây) ---
    doLogin: async function (event) {
        if (event) event.preventDefault(); // Chặn đứng việc load lại trang

        // 1. Reset lại thông báo lỗi trước khi bấm
        $('#error-msg').addClass('d-none').text("");
        
        const username = $('#user').val();
        const password = $('#pass').val();

        if (!username || !password) {
            // Thay vì alert() trình duyệt xấu xí, dùng ngay div error của bạn
            $('#error-msg').text("Vui lòng nhập tài khoản và mật khẩu").removeClass('d-none');
            return;
        }

        try {
            const res = await fetch('/auth/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            console.log(data)
            if (data.status === "success") {
                // Lưu mọi thứ vào trình duyệt
                localStorage.setItem('userName', data.user.name);
                localStorage.setItem('userPerms', data.user.perms);
                // Chuyển hướng
                window.location.href = '/';
            } else {
                // Hiển thị lỗi từ server
                $('#error-msg').text(data.message).removeClass('d-none');
            }
        } catch (error) {
            console.error("Login Error:", error);
            $('#error-msg').text("Lỗi kết nối hệ thống!").removeClass('d-none');
        }
    },

    // --- HÀM LẤY QUYỀN ---
    getPerms: () => (localStorage.getItem('userPerms') || "").split(','),

    // --- KIỂM TRA QUYỀN ---
    has: (p) => Auth.getPerms().includes(p),

    // --- ĐĂNG XUẤT ---
    logout: () => {
        fetch('auth/api/logout')
            .catch(err => console.error("Logout Error:", err))
            .finally(() => {
                // KHÔNG dùng localStorage.clear();

                // Chỉ xóa thông tin đăng nhập
                localStorage.removeItem('userPerms');
                localStorage.removeItem('userName');

                // Giữ nguyên localStorage.getItem('appLang')

                window.location.replace('auth/login');
            });
    }
};

