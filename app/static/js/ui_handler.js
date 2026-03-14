// Đảm bảo CoreUI Navigation khởi tạo đúng
$(document).ready(function() {
    // tính năng Dropdown (đóng/mở menu con) hoạt động
    const nav = document.querySelectorAll('.sidebar-nav');
    nav.forEach(el => {
        const navigation = coreui.Navigation.getInstance(el);
    });
    // Tự động mở menu cha nếu có menu con đang active
    $('.nav-group-items .nav-link.active').closest('.nav-group').addClass('show');
    
    // Giữ trạng thái khi nhấn expand menu trái
    const sidebarEl = document.querySelector('#sidebar');
    if (!sidebarEl) return;

    // 1. KHI LOAD TRANG: Kiểm tra trạng thái đã lưu
    const isUnfoldable = localStorage.getItem('sidebar_unfoldable') === 'true';
    
    if (isUnfoldable) {
        sidebarEl.classList.add('sidebar-narrow-unfoldable');
        // Thêm class này để đảm bảo icon và text hiển thị đúng chế độ thu nhỏ của v5
        //sidebarEl.classList.add('sidebar-narrow'); 
    }

    // 2. BẮT SỰ KIỆN: Khi người dùng nhấn nút Toggler ở chân Sidebar
    const toggler = document.querySelector('.sidebar-toggler');
    if (toggler) {
        toggler.addEventListener('click', function() {
            // Đợi một chút để CoreUI thực hiện xong việc toggle class
            setTimeout(() => {
                const currentStatus = sidebarEl.classList.contains('sidebar-narrow-unfoldable');
                localStorage.setItem('sidebar_unfoldable', currentStatus);
            }, 100);
        });
    }
});
